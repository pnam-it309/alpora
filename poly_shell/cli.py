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

from . import __version__
from .adapters.base import SafeRunner
from .system.integration import fallback_panel, install, patch_autostart, restore_autostart
from .core.state import ConfigError, MODES, Paths, ROOT, current_mode, update_session
from .system.desktop import control, wallpaper, restore_desktop
from .services.organizer import organizer
from .system.indicators import show_indicator, sync_notifications
from .system.lockscreen import lock_date, sync_lockscreen
from .theming.appearance import appearance_control, sync as sync_appearance
from .theming.themes import theme_control
from .theming.timeline import timeline_control
from .system.widgets import widgets_control
from .services.shortcuts import shortcuts_control
from .system.programs import inventory
from . import commands


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

        environment = dict(
            os.environ,
            POLY_SHELL_ROOT=str(ROOT),
            POLY_SHELL_STATE=str(paths.session),
            POLY_SHELL_READY=str(ready),
            POLY_SHELL_CTL=str(ROOT / "bin/poly-shell"),
            POLY_SHELL_ASSETS=str(ROOT / "assets"),
            POLY_SHELL_SOCK=daemon.ipc_server.endpoint_address,
            PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}".rstrip(":"),
            PATH=f"{ROOT / 'bin'}:{Path.home() / '.local/bin'}:{os.environ.get('PATH', '')}".rstrip(":"),
        )
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
        from .system.diagnostics import collect_diagnostic_bundle
        archive = collect_diagnostic_bundle(paths, output_dir)
        print(f"Diagnostic bundle written to: {archive}")
        return 0
    ok = True
    print(f"Poly Shell {__version__}\nProject: {ROOT}")
    for item in inventory():
        status = "OK" if item['available'] else "MISSING" if item['required'] else "OPTIONAL MISSING"
        missing = [name for name, value in item['tools'].items() if not value]
        print(f"{status} {item['name']} [{item['package']}]: {item['purpose']}" + ("; missing: " + ", ".join(missing) if missing else ""))
        if item['required'] and not item['available']:
            ok = False
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
        if fcntl is not None:
            fcntl.flock(lock, fcntl.LOCK_EX)
        if subprocess.run(ipc, capture_output=True, text=True, timeout=3).returncode == 0:
            return
        update_session(paths)
        # A separate user unit keeps the settings app alive across bar restarts.
        environment = {name: os.environ[name] for name in (
            "WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE",
            "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_CONFIG_HOME", "XDG_STATE_HOME",
            "XDG_DATA_HOME") if os.environ.get(name)}
        environment.update(
            POLY_SHELL_ROOT=str(ROOT),
            POLY_SHELL_STATE=str(paths.session),
            POLY_SHELL_CTL=str(ROOT / "bin/poly-shell"),
            POLY_SHELL_ASSETS=str(ROOT / "assets"),
            PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}".rstrip(":"),
            PATH=f"{ROOT / 'bin'}:{Path.home() / '.local/bin'}:{os.environ.get('PATH', '')}".rstrip(":"),
        )
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
    from .commands.tasks_cmd import open_task_manager as _open_tm
    return _open_tm(paths, runtime_check_fn=runtime_check)


def main(argv=None):
    from .commands.parser import build_parser
    parser = build_parser(__version__)
    args = parser.parse_args(argv)
    paths = Paths.current()

    # Route subcommands to dedicated handlers in poly_shell.commands
    COMMAND_HANDLERS = {
        "doctor": lambda: doctor(paths, bundle=args.bundle, output_dir=args.output),
        "preflight": lambda: commands.handle_preflight(paths, args),
        "task-manager": lambda: commands.handle_task_manager(paths, args, runtime_check),
        "tasks": lambda: commands.handle_tasks(paths, args),
        "wellbeing": lambda: commands.handle_wellbeing(paths, args),
        "shortcuts": lambda: commands.handle_shortcuts(paths, args),
        "organizer": lambda: commands.handle_organizer(paths, args),
        "control": lambda: commands.handle_control(paths, args),
        "wallpaper": lambda: commands.handle_wallpaper(paths, args),
        "project": lambda: commands.handle_project(paths, args),
        "dotfiles": lambda: commands.handle_dotfiles(paths, args),
        "windows-drives": lambda: commands.handle_windows_drives(paths, args),
        "osd": lambda: commands.handle_osd(paths, args),
        "lock-date": lambda: commands.handle_lock_date(paths, args),
        "lock-media": lambda: commands.handle_lock_media(paths, args),
        "theme": lambda: commands.handle_theme(paths, args),
        "timeline": lambda: commands.handle_timeline(paths, args),
        "widgets": lambda: commands.handle_widgets(paths, args),
        "appearance": lambda: commands.handle_appearance(paths, args),
        "palette-extract": lambda: commands.handle_palette_extract(paths, args),
        "assets": lambda: commands.handle_assets(paths, args),
        "toolkit-refresh": lambda: commands.handle_toolkit_refresh(paths, args),
        "screen": lambda: commands.handle_screen(args),
        "pip": lambda: commands.handle_pip(args),
        "exe": lambda: commands.handle_exe(args),
        "demo": lambda: commands.handle_demo(paths, args),
        "launcher": lambda: commands.handle_launcher(paths, args),
        "quick-settings": lambda: commands.handle_quick_settings(paths, args),
        "notifications": lambda: commands.handle_notifications(paths, args),
        "clipboard": lambda: commands.handle_clipboard(paths, args),
        "overview": lambda: commands.handle_overview(paths, args),
        "power-menu": lambda: commands.handle_power_menu(paths, args),
        "toggle-mode": lambda: commands.handle_toggle_mode(paths, args),
        "display-project": lambda: commands.handle_display_project(paths, args),
        "video-pip": lambda: commands.handle_pip(args),
        "game": lambda: commands.handle_game(args),
        "phone": lambda: commands.handle_phone(args),
        "update": lambda: commands.handle_update(args),
        "security": lambda: commands.handle_security(args),
        "storage": lambda: commands.handle_storage(args),
        "memory": lambda: commands.handle_memory(args),
        "mem": lambda: commands.handle_memory(args),
        "dev": lambda: commands.handle_dev(args),
        "properties": lambda: commands.handle_properties(args),
        "snapshot": lambda: commands.handle_snapshot(args),
        "privacy": lambda: commands.handle_privacy(args),
        "welcome": lambda: commands.handle_welcome(paths, args, runtime_check),
        "monitor": lambda: commands.handle_monitor(paths, args),
        "arcade": lambda: commands.handle_arcade(paths, args),
        "running-apps": lambda: commands.handle_running_apps(args),
        "clipboard-serve": lambda: commands.handle_clipboard_serve(),
        "service": lambda: commands.handle_service(paths, args),
        "watchdog": lambda: commands.handle_watchdog(paths, args),
    }

    try:
        if args.command in COMMAND_HANDLERS:
            result = COMMAND_HANDLERS[args.command]()
            return result if result is not None else 0

        # Session lifecycle commands
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
