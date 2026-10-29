"""Lifecycle CLI. No shell interpolation and no system-wide package changes."""
import argparse
try:
    import fcntl
except ImportError:
    fcntl = None
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import re

from . import __version__
from .adapters.base import SafeRunner
from .integration import fallback_panel, install, patch_autostart, restore_autostart
from .state import ConfigError, MODES, Paths, ROOT, current_mode, update_session
from .desktop import control, wallpaper, restore_desktop
from .organizer import organizer
from .indicators import show_indicator, sync_notifications
from .lockscreen import lock_date, sync_lockscreen
from .appearance import appearance_control, sync as sync_appearance
from .themes import theme_control
from .timeline import timeline_control
from .widgets import widgets_control
from .shortcuts import shortcuts_control
from .programs import inventory


ALLOWED_SYSTEMCTL_SUBCOMMANDS = {
    'start', 'stop', 'restart', 'status', 'is-active', 'is-failed',
    'reset-failed', 'daemon-reload', 'import-environment'
}


def systemctl(*arguments, check=True, capture=False):
    if not arguments or arguments[0] not in ALLOWED_SYSTEMCTL_SUBCOMMANDS:
        raise ConfigError(f"Unauthorized systemctl action: {arguments[0] if arguments else None}")
    clean_arguments = [str(arg) for arg in arguments]
    for arg in clean_arguments:
        if any(c in arg for c in ("\x00", "\n", "\r")):
            raise ConfigError("Invalid character in systemctl argument")
    return subprocess.run(["systemctl", "--user", *clean_arguments], check=check,
                          capture_output=capture, text=True)


def runtime_check():
    if not shutil.which("quickshell"):
        raise ConfigError("quickshell is missing; install it using your package manager")
    result = subprocess.run(["quickshell", "--version"], capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise ConfigError(
            "Quickshell cannot start. On Arch, complete sudo pacman -Syu first.\n"
            + (result.stderr or result.stdout).strip()
        )
    return result.stdout.strip() or result.stderr.strip()


def run(paths):
    runtime_check()
    if not os.environ.get("WAYLAND_DISPLAY"):
        raise ConfigError("Run inside a Wayland session")
    update_session(paths)
    sync_appearance(paths)
    sync_notifications(paths)
    sync_lockscreen(paths)
    paths.runtime.mkdir(mode=0o700, parents=True, exist_ok=True)
    ready = paths.runtime / "ready"
    with (paths.runtime / "instance.lock").open("a") as lock:
        try:
            if fcntl is not None:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ConfigError("Poly Shell is already running") from exc
        ready.unlink(missing_ok=True)
        try:
            restore_desktop(paths)
        except (ConfigError, OSError, subprocess.SubprocessError) as exc:
            print(f"Night Light restore failed: {exc}", file=sys.stderr)
        from .core.daemon import PolyShellDaemon
        daemon = PolyShellDaemon(socket_path=paths.runtime / "ipc.sock")
        try:
            daemon.start()
        except Exception as exc:
            print(f"Warning: Failed to start IPC daemon: {exc}", file=sys.stderr)

        environment = dict(os.environ, POLY_SHELL_STATE=str(paths.session),
                           POLY_SHELL_READY=str(ready), POLY_SHELL_CTL=str(ROOT / "bin/poly-shell"),
                           POLY_SHELL_ASSETS=str(ROOT / "assets"),
                           POLY_SHELL_SOCK=daemon.ipc_server.endpoint_address)
        process = subprocess.Popen(["quickshell", "--path", str(ROOT / "shell")], env=environment)
        stopping = False

        def stop(_signum, _frame):
            nonlocal stopping
            stopping = True
            if process.poll() is None:
                process.terminate()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        try:
            result = process.wait()
            return 0 if stopping else result
        finally:
            daemon.stop()
            ready.unlink(missing_ok=True)


def start(paths):
    runtime_check()
    ready = paths.runtime / "ready"
    already_active = systemctl("is-active", "--quiet", "poly-shell.service", check=False).returncode == 0
    if not already_active:
        ready.unlink(missing_ok=True)
    # Whitelist session variables: never import arbitrary environment secrets.
    names = [name for name in ("WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE",
                              "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_CONFIG_HOME",
                              "XDG_STATE_HOME") if os.environ.get(name)]
    systemctl("import-environment", *names)
    systemctl("daemon-reload")
    systemctl("reset-failed", "poly-shell.service", check=False, capture=True)
    systemctl("start", "poly-shell.service")
    for _ in range(50):
        if ready.exists() and systemctl("is-active", "--quiet", "poly-shell.service", check=False).returncode == 0:
            print("Poly Shell is ready")
            return
        if systemctl("is-failed", "--quiet", "poly-shell.service", check=False).returncode == 0:
            break
        time.sleep(0.1)
    systemctl("stop", "poly-shell.service", check=False)
    raise ConfigError("Shell did not become ready; existing panel kept. See poly-shell logs")


def send_ipc_request(endpoint: str, action: str, params: dict | None = None) -> dict:
    if not endpoint:
        raise ConfigError("No IPC endpoint specified")
    params = params or {}
    sock = socket.socket(
        socket.AF_UNIX if hasattr(socket, "AF_UNIX") and ":" not in endpoint else socket.AF_INET,
        socket.SOCK_STREAM,
    )
    sock.settimeout(3.0)
    try:
        if hasattr(socket, "AF_UNIX") and ":" not in endpoint:
            sock.connect(endpoint)
        else:
            host, port = endpoint.split(":")
            sock.connect((host, int(port)))
        req = json.dumps({"id": "cli", "action": action, "params": params}) + "\n"
        sock.sendall(req.encode("utf-8"))
        resp_line = sock.makefile("r").readline()
        if not resp_line:
            raise ConfigError("Empty response from Poly Shell IPC server")
        return json.loads(resp_line)
    except OSError as exc:
        raise ConfigError(f"Cannot connect to Poly Shell daemon ({endpoint}): {exc}") from exc
    finally:
        sock.close()


def doctor(paths, bundle=False, output_dir=None):
    if bundle:
        from .diagnostics import collect_diagnostic_bundle
        archive = collect_diagnostic_bundle(paths, output_dir)
        print(f"Diagnostic bundle written to: {archive}")
        return 0
    ok = True
    print(f"Poly Shell {__version__}\nProject: {ROOT}")
    for item in inventory():
        status = "OK" if item['available'] else "MISSING" if item['required'] else "OPTIONAL MISSING"
        missing = [name for name,value in item['tools'].items() if not value]
        print(f"{status} {item['name']} [{item['package']}]: {item['purpose']}" + ("; missing: " + ", ".join(missing) if missing else ""))
        if item['required'] and not item['available']: ok = False
    if not shutil.which("foot") and not shutil.which("kitty"):
        print("OPTIONAL MISSING terminal: install foot or kitty, or configure apps.terminal")
    try:
        print("OK " + runtime_check())
    except ConfigError as exc:
        print("BLOCKED " + str(exc))
        ok = False
    print(f"Settings: {paths.config / 'settings.json'}")
    print(f"Saved session: {paths.session}")
    print(f"Wayland: {os.environ.get('WAYLAND_DISPLAY', 'not set')}")
    return 0 if ok else 1


def open_settings(paths):
    runtime_check()
    if not os.environ.get("WAYLAND_DISPLAY"):
        raise ConfigError("Open settings inside Wayland session")
    entry = ROOT / "shell/settings.qml"
    ipc = ["quickshell", "ipc", "--path", str(entry), "call", "settings-app", "raiseWindow"]
    paths.runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (paths.runtime / "settings-start.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if subprocess.run(ipc, capture_output=True, text=True, timeout=3).returncode == 0:
            return
        update_session(paths)
        # A separate user unit keeps the settings app alive across bar restarts.
        environment = {name: os.environ[name] for name in (
            "WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE",
            "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_CONFIG_HOME", "XDG_STATE_HOME",
            "XDG_DATA_HOME") if os.environ.get(name)}
        environment.update(POLY_SHELL_STATE=str(paths.session),
                           POLY_SHELL_CTL=str(ROOT / "bin/poly-shell"),
                           POLY_SHELL_ASSETS=str(ROOT / "assets"))
        active = systemctl("is-active", "--quiet", "poly-shell-settings.service", check=False, capture=True)
        if active.returncode:
            command = ["systemd-run", "--user", "--quiet", "--collect",
                       "--unit=poly-shell-settings", "--service-type=exec",
                       "--description=Poly Shell Settings"]
            command += ["--setenv=" + name + "=" + value for name, value in environment.items()]
            result = subprocess.run(command + ["quickshell", "--path", str(entry), "--no-duplicate"],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode:
                raise ConfigError("Cannot open settings: " + result.stderr.strip())
        for _ in range(60):
            if subprocess.run(ipc, capture_output=True, text=True, timeout=2).returncode == 0:
                return
            time.sleep(.1)
        raise ConfigError("Settings window failed to start. See journalctl --user -u poly-shell-settings")


def open_task_manager(paths):
    runtime_check()
    if not os.environ.get("WAYLAND_DISPLAY"):
        raise ConfigError("Open task manager inside Wayland session")
    entry = ROOT / "shell/task_manager.qml"
    ipc = ["quickshell", "ipc", "--path", str(entry), "call", "task-manager-app", "raiseWindow"]
    paths.runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    if SafeRunner.run(ipc, timeout=2.0).returncode == 0:
        return
    update_session(paths)
    environment = {name: os.environ[name] for name in (
        "WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE",
        "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_CONFIG_HOME", "XDG_STATE_HOME",
        "XDG_DATA_HOME") if os.environ.get(name)}
    environment.update(
        POLY_SHELL_STATE=str(paths.session),
        POLY_SHELL_CTL=str(ROOT / "bin/poly-shell"),
        POLY_SHELL_ASSETS=str(ROOT / "assets")
    )
    if SafeRunner.is_available("systemd-run"):
        cmd = ["systemd-run", "--user", "--quiet", "--collect",
               "--unit=poly-shell-task-manager", "--service-type=exec",
               "--description=ALPORA Task Manager"]
        cmd += ["--setenv=" + name + "=" + value for name, value in environment.items()]
        SafeRunner.run(cmd + ["quickshell", "--path", str(entry), "--no-duplicate"], timeout=8.0)
    else:
        env_copy = os.environ.copy()
        env_copy.update(environment)
        subprocess.Popen(["quickshell", "--path", str(entry), "--no-duplicate"], env=env_copy, start_new_session=True)

    for _ in range(50):
        if SafeRunner.run(ipc, timeout=1.5).returncode == 0:
            return
        time.sleep(.1)
    raise ConfigError("Task manager window failed to start.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Poly Shell foundation preview")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "refresh", "install", "run", "start", "stop", "restart", "status", "logs", "activate", "deactivate", "settings"):
        sub.add_parser(command)
    sub.add_parser("daemon", help="run core background services daemon")
    ipc_parser = sub.add_parser("ipc", help="send request to running Poly Shell daemon")
    ipc_parser.add_argument("action", help="IPC action name (e.g. ping, compositor.workspaces, audio.state)")
    ipc_parser.add_argument("payload", nargs="?", default="{}", help="JSON params payload")
    doctor_parser = sub.add_parser("doctor", help="check runtime dependencies and system health")
    doctor_parser.add_argument("--bundle", action="store_true", help="export diagnostic bundle archive for tester triage")
    doctor_parser.add_argument("--output", help="output directory for the diagnostic bundle archive")
    preflight_parser = sub.add_parser("preflight", help="inspect environment readiness before installation")
    preflight_parser.add_argument("--json", action="store_true", help="output preflight report as JSON")
    sub.add_parser("task-manager", help="open or raise ALPORA Mini Task Manager")
    tasks_parser = sub.add_parser("tasks", help="task manager data queries and control")
    tasks_parser.add_argument("--tab", choices=("processes", "performance", "startup", "users", "details", "services"), default="processes")
    tasks_parser.add_argument("--kill", type=int, help="kill process by PID")
    tasks_parser.add_argument("--sig", type=int, default=15, help="signal number to send with kill (default 15)")
    tasks_parser.add_argument("--service", nargs=2, metavar=("NAME", "ACTION"), help="control systemd service (e.g. name restart)")
    tasks_parser.add_argument("--startup-toggle", nargs=2, metavar=("NAME", "STATE"), help="toggle startup item (name on/off)")
    wallpaper_parser = sub.add_parser("wallpaper", help="apply and remember a static wallpaper")
    wallpaper_parser.add_argument("image", nargs="?")
    wallpaper_parser.add_argument("--reset", action="store_true")
    mode_parser = sub.add_parser("mode", help="read, set, or toggle the saved mode")
    mode_parser.add_argument("mode", nargs="?", choices=(*MODES, "toggle"))
    mode_parser.add_argument("--json", action="store_true")
    control_parser = sub.add_parser("control", help="desktop adapters for the quick settings panel")
    control_parser.add_argument("action", choices=("status", "brightness", "dnd", "nightlight", "bluetooth", "power-profile", "airplane", "hotspot", "wifi-connect", "ui-scale", "touchpad", "font", "caffeine"))
    control_parser.add_argument("value", nargs="?")
    theme_parser = sub.add_parser("theme", help="wallpaper-derived color themes")
    theme_parser.add_argument("action", choices=("list", "apply", "import"))
    theme_parser.add_argument("payload", nargs="?", default="{}")
    timeline_parser = sub.add_parser("timeline", help="saved time of day for the Timeline theme")
    timeline_parser.add_argument("action", choices=("get", "set", "ready"))
    timeline_parser.add_argument("payload", nargs="?", default="{}")
    widgets_parser = sub.add_parser("widgets", help="desktop widgets, layout and weather")
    widgets_parser.add_argument("action", choices=("get", "apply", "weather", "search", "metrics"))
    widgets_parser.add_argument("payload", nargs="?", default="{}")
    shortcuts_parser = sub.add_parser("shortcuts", help="edit persistent Hyprland keyboard shortcuts")
    shortcuts_parser.add_argument("action", choices=("get", "apply"))
    shortcuts_parser.add_argument("payload", nargs="?", default="{}")
    assets_parser = sub.add_parser("assets", help="install pinned ALPORA icon and cursor themes")
    assets_parser.add_argument("action", choices=("install", "apply"))
    osd_parser = sub.add_parser("osd", help="show the current system value without changing it")
    osd_parser.add_argument("kind", choices=("volume", "microphone", "brightness", "capslock", "numlock", "airplane"))
    osd_parser.add_argument("--state", choices=("on", "off"), default="on", help="toggle state for indicator")
    sub.add_parser("lock-date", help="localized lockscreen date, without system locale dependencies")
    lock_media_parser = sub.add_parser("lock-media", help="hyprlock media player album art, metadata, and controls")
    lock_media_parser.add_argument("field", choices=("art", "title", "artist", "controls", "status", "summary"), nargs="?", default="summary")
    sub.add_parser("toolkit-refresh", help="refresh a cached file-manager palette after a theme change")
    screen_parser = sub.add_parser("screen", help="screen capture, recording, OCR and QR tools")
    screen_parser.add_argument("action", choices=("region", "full", "window", "satty", "ocr", "qr", "record", "stop-record"), default="region", nargs="?")
    screen_parser.add_argument("--with-audio", action="store_true", help="record screen with audio")
    wellbeing_parser = sub.add_parser("wellbeing", help="display digital wellbeing and application usage statistics")
    wellbeing_parser.add_argument("--date", help="specific date YYYY-MM-DD")
    wellbeing_parser.add_argument("--json", action="store_true", help="output JSON")
    appearance_parser = sub.add_parser("appearance", help="validated desktop appearance controls")
    appearance_parser.add_argument("action", choices=("get", "apply", "reset", "install"))
    appearance_parser.add_argument("payload", nargs="?", default="{}")
    organizer_parser = sub.add_parser("organizer", help="local calendar, tasks, notes and focus timer")
    organizer_parser.add_argument("action", choices=("get", "task-add", "event-add", "task-toggle", "item-remove", "note", "timer-start", "timer-pause", "timer-reset", "timer-duration"))
    organizer_parser.add_argument("payload", nargs="?", default="{}")
    windows_fs_parser = sub.add_parser("windows-drives", help="discover and mount Windows partitions")
    windows_fs_parser.add_argument("action", choices=("list", "mount", "unmount", "normalize-path"))
    windows_fs_parser.add_argument("target", nargs="?", default="")
    dotfiles_parser = sub.add_parser("dotfiles", help="manage dotfile symlinks (Stow / Chezmoi compatible)")
    dotfiles_parser.add_argument("action", choices=("status", "check", "link", "stow", "apply", "unlink", "unstow", "delete", "restow"), nargs="?", default="status")
    project_parser = sub.add_parser("project", help="multi-monitor projection modes (internal, mirror, extend, external)")
    project_parser.add_argument("mode", choices=("toggle", "open", "close", "internal", "mirror", "extend", "external"), nargs="?", default="toggle")
    palette_parser = sub.add_parser("palette-extract", help="extract dominant palette from any image")
    palette_parser.add_argument("image", help="path to image file")
    exe_parser = sub.add_parser("exe", help="Windows .EXE runner, downloader, and installer (Zalo, etc.)")
    exe_sub = exe_parser.add_subparsers(dest="exe_action", required=True)
    exe_run = exe_sub.add_parser("run", help="run a .exe with Wine and Vietnamese font fixes")
    exe_run.add_argument("path", help="path to .exe file")
    exe_run.add_argument("--prefix", help="optional custom Wine prefix path")
    exe_run.add_argument("extra_args", nargs="*", help="arguments passed to the Windows program")
    exe_dl = exe_sub.add_parser("download", help="download a Windows application .exe (zalo, ultraviewer, notepadpp)")
    exe_dl.add_argument("target", help="app preset name (zalo, ultraviewer, notepadpp) or direct URL")
    exe_dl.add_argument("--output", help="destination directory (defaults to ~/Downloads)")
    exe_inst = exe_sub.add_parser("install", help="install a Windows application and create ALPORA Launcher entry")
    exe_inst.add_argument("target", help="app preset name (e.g. zalo) or path to downloaded setup.exe")
    exe_inst.add_argument("--name", help="display name of the application")
    exe_zalo = exe_sub.add_parser("zalo", help="1-click installer for Zalo on Linux")
    exe_zalo.add_argument("--aur", action="store_true", help="prefer native AUR package if available")
    exe_sub.add_parser("list", help="list known Windows application presets")
    exe_sub.add_parser("register-mime", help="associate .exe files with ALPORA Wine Runner")
    pip_parser = sub.add_parser("pip", help="floating video Picture-in-Picture player (TikTok, Shorts, YouTube)")
    pip_parser.add_argument("target", nargs="?", default="tiktok", help="video platform preset (tiktok, shorts, youtube) or URL")
    pip_parser.add_argument("--mode", choices=("vertical", "landscape"), help="aspect ratio mode")
    pip_parser.add_argument("--width", type=int, help="custom window width")
    pip_parser.add_argument("--height", type=int, help="custom window height")
    args = parser.parse_args(argv)
    paths = Paths.current()
    try:
        if args.command in ("init", "refresh"):
            snapshot = update_session(paths)
            sync_appearance(paths)
            sync_notifications(paths)
            sync_lockscreen(paths)
            print(f"Session ready: {snapshot['mode']} ({paths.session})")
        elif args.command == "mode":
            if args.mode or args.json:
                snapshot = update_session(paths, args.mode)
                sync_notifications(paths)
                sync_lockscreen(paths)
                print(json.dumps(snapshot, ensure_ascii=False) if args.json else snapshot["mode"])
            else:
                print(current_mode(paths))
        elif args.command == "doctor":
            return doctor(paths, bundle=args.bundle, output_dir=args.output)
        elif args.command == "preflight":
            from .preflight import run_preflight, format_preflight_report
            report = run_preflight(paths)
            if getattr(args, "json", False):
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print(format_preflight_report(report))
            return 0 if report["ready"] else 1
        elif args.command == "task-manager":
            open_task_manager(paths)
        elif args.command == "wellbeing":
            from .commands.wellbeing_cmd import handle_wellbeing
            return handle_wellbeing(paths, args)
        elif args.command == "tasks":
            from . import task_manager
            if args.kill:
                task_manager.kill_process(args.kill, sig=args.sig)
                print(json.dumps({"success": True, "killed": args.kill}))
            elif args.service:
                name, act = args.service
                task_manager.control_service(name, act)
                print(json.dumps({"success": True, "service": name, "action": act}))
            elif args.startup_toggle:
                name, state = args.startup_toggle
                enabled = state.lower() in ("on", "true", "1", "yes")
                task_manager.toggle_startup_item(name, enabled)
                print(json.dumps({"success": True, "item": name, "enabled": enabled}))
            else:
                tab = args.tab
                if tab == "processes":
                    data = task_manager.get_processes()
                elif tab == "performance":
                    data = task_manager.get_performance_data()
                elif tab == "startup":
                    data = task_manager.get_startup_items()
                elif tab == "users":
                    data = task_manager.get_user_sessions()
                elif tab == "details":
                    data = task_manager.get_process_details()
                elif tab == "services":
                    data = task_manager.get_services()
                else:
                    data = {}
                print(json.dumps(data, ensure_ascii=False))
        elif args.command == "control":
            CONTROL_ACTIONS = {
                "status": "status", "brightness": "brightness", "dnd": "dnd",
                "nightlight": "nightlight", "bluetooth": "bluetooth",
                "power-profile": "power-profile", "airplane": "airplane",
                "hotspot": "hotspot", "wifi-connect": "wifi-connect",
                "ui-scale": "ui-scale", "touchpad": "touchpad", "font": "font"
            }
            safe_action = CONTROL_ACTIONS.get(args.action)
            if not safe_action:
                raise ConfigError(f"Unknown control action: {args.action}")
            print(json.dumps(control(paths, safe_action, args.value)))
        elif args.command == "theme":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid theme JSON") from exc
            print(json.dumps(theme_control(paths, args.action, payload), ensure_ascii=False))
        elif args.command == "timeline":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid Timeline JSON") from exc
            print(json.dumps(timeline_control(paths, args.action, payload), ensure_ascii=False))
        elif args.command == "widgets":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid widgets JSON") from exc
            if not isinstance(payload, dict): raise ConfigError("Invalid widgets request")
            print(json.dumps(widgets_control(paths, args.action, payload), ensure_ascii=False))
        elif args.command == "shortcuts":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid shortcuts JSON") from exc
            print(json.dumps(shortcuts_control(paths,args.action,payload),ensure_ascii=False))
        elif args.command == "assets":
            from .desktop_assets import install as install_assets, apply as apply_assets
            result = install_assets(paths) if args.action == "install" else apply_assets(paths)
            print(json.dumps(result, ensure_ascii=False))
        elif args.command == "osd":
            if args.kind in ("capslock", "numlock", "airplane"):
                state_val = getattr(args, 'state', 'on') == 'on'
                SafeRunner.run(['quickshell', 'ipc', '--path', str(ROOT / 'shell'), 'call', 'shell', 'showToggleOsd', args.kind, "true" if state_val else "false"], timeout=3.0)
            else:
                OSD_MAP = {'brightness': 'brightness', 'volume': 'volume', 'microphone': 'microphone'}
                safe_kind = OSD_MAP.get(args.kind)
                if not safe_kind:
                    raise ConfigError(f"Invalid OSD indicator: {args.kind}")
                show_indicator(safe_kind)
        elif args.command == "lock-date":
            print(lock_date())
        elif args.command == "lock-media":
            from .lock_media import handle_cli
            handle_cli(args.field)
        elif args.command == "toolkit-refresh":
            from .toolkit_refresh import refresh, schedule
            result = refresh(paths)
            if result.get('busy'):
                schedule(paths)
            print(json.dumps(result))
        elif args.command == "organizer":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid organizer JSON") from exc
            print(json.dumps(organizer(paths, args.action, payload), ensure_ascii=False))
        elif args.command == "screen":
            from .commands.screen_cmd import handle_screen
            return handle_screen(args)
        elif args.command == "appearance":
            try: payload = json.loads(args.payload)
            except ValueError as exc: raise ConfigError("Invalid appearance JSON") from exc
            print(json.dumps(appearance_control(paths, args.action, payload), ensure_ascii=False))
        elif args.command == "windows-drives":
            from .windows_fs import detect_windows_drives, mount_drive, unmount_drive, normalize_windows_path
            if args.action == "list":
                print(json.dumps(detect_windows_drives(), ensure_ascii=False))
            elif args.action == "mount":
                print(json.dumps({"mountpoint": mount_drive(args.target)}, ensure_ascii=False))
            elif args.action == "unmount":
                print(json.dumps({"success": unmount_drive(args.target)}, ensure_ascii=False))
            elif args.action == "normalize-path":
                print(normalize_windows_path(args.target))
        elif args.command == "dotfiles":
            script = (ROOT / "scripts/stow-dotfiles.sh").resolve()
            if args.action in ("status", "check"):
                cmd_action = "status"
            elif args.action in ("link", "stow", "apply"):
                cmd_action = "link"
            elif args.action in ("unlink", "unstow", "delete"):
                cmd_action = "unlink"
            elif args.action == "restow":
                cmd_action = "restow"
            else:
                raise ConfigError(f"Invalid dotfiles action: {args.action}")
            return subprocess.run(["bash", "--", str(script), cmd_action], check=False).returncode  # NOSONAR
        elif args.command == "project":
            entry = ROOT / "shell/shell.qml"
            ALLOWED_MODES = {
                "toggle": "toggle", "open": "open", "close": "close",
                "internal": "internal", "mirror": "mirror",
                "extend": "extend", "external": "external"
            }
            safe_mode = ALLOWED_MODES.get(args.mode, "toggle")
            if safe_mode in ("toggle", "open", "close"):
                cmd = ["quickshell", "ipc", "--path", str(entry), "call", "display-project", safe_mode]
            else:
                cmd = ["quickshell", "ipc", "--path", str(entry), "call", "display-project", "setMode", safe_mode]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)  # NOSONAR
            if res.returncode == 0:
                print(f"Display projection: {safe_mode}")
            else:
                raise ConfigError("Cannot connect to running Poly Shell for display projection")
        elif args.command == "pip":
            from .commands.pip_cmd import handle_pip
            return handle_pip(args)
        elif args.command == "exe":
            from .commands.exe_cmd import handle_exe
            return handle_exe(args)
        elif args.command == "palette-extract":
            from .themes import extract_palette_from_image
            palette = extract_palette_from_image(args.image)
            print(json.dumps(palette, indent=2))
        elif args.command == "wallpaper":
            if args.image and (str(args.image).startswith('-') or any(c in str(args.image) for c in ('\x00', '\r', '\n'))):
                raise ConfigError("Invalid wallpaper argument")
            wallpaper(paths, args.image, reset=args.reset)
        elif args.command == "settings":
            open_settings(paths)
        elif args.command == "install":
            update_session(paths)
            install(paths)
        elif args.command == "daemon":
            from .core.daemon import PolyShellDaemon
            daemon = PolyShellDaemon(socket_path=paths.runtime / "ipc.sock")
            daemon.start()
            print(f"Poly Shell daemon listening on {daemon.ipc_server.endpoint_address}")
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                pass
            finally:
                daemon.stop()
            return 0
        elif args.command == "ipc":
            sock_path = str(paths.runtime / "ipc.sock")
            endpoint = os.environ.get("POLY_SHELL_SOCK") or sock_path
            try:
                params = json.loads(args.payload)
            except ValueError as exc:
                raise ConfigError("Invalid IPC JSON payload") from exc
            resp = send_ipc_request(endpoint, args.action, params)
            print(json.dumps(resp, indent=2, ensure_ascii=False))
            return 0 if resp.get("success") else 1
        elif args.command == "run":
            return run(paths)
        elif args.command == "start":
            start(paths)
        elif args.command == "restart":
            systemctl("stop", "poly-shell.service")
            start(paths)
        elif args.command == "stop":
            systemctl("stop", "poly-shell.service")
        elif args.command == "status":
            return systemctl("status", "--no-pager", "poly-shell.service", check=False).returncode
        elif args.command == "logs":
            return subprocess.run(["journalctl", "--user", "-u", "poly-shell.service", "-n", "80", "--no-pager"]).returncode
        elif args.command == "activate":
            install(paths)
            try:
                start(paths)
                patch_autostart(paths)
            except Exception:
                systemctl("stop", "poly-shell.service", check=False)
                raise
            subprocess.run(["pkill", "-u", str(os.getuid()), "-x", "waybar"], check=False)
            print("Poly Shell active; use poly-shell deactivate to return to Waybar")
        elif args.command == "deactivate":
            restore_autostart(paths)
            systemctl("stop", "poly-shell.service", check=False)
            fallback_panel(paths)
            print("Waybar restored")
        return 0
    except (ConfigError, OSError, subprocess.SubprocessError) as exc:
        print(f"poly-shell: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
