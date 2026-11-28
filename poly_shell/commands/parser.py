"""Argument parser definition for ALPORA Poly Shell CLI."""
from __future__ import annotations

import argparse

from ..core.state import MODES


def build_parser(version: str) -> argparse.ArgumentParser:
    """Build and return the top-level CLI ArgumentParser."""
    parser = argparse.ArgumentParser(description="Poly Shell foundation preview")
    parser.add_argument("--version", action="version", version=version)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in (
        "init",
        "refresh",
        "install",
        "run",
        "start",
        "stop",
        "restart",
        "status",
        "logs",
        "activate",
        "deactivate",
        "settings",
    ):
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
    tasks_parser.add_argument(
        "--tab",
        choices=("processes", "performance", "startup", "users", "details", "services"),
        default="processes",
    )
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
    control_parser.add_argument(
        "action",
        choices=(
            "status",
            "brightness",
            "dnd",
            "nightlight",
            "bluetooth",
            "power-profile",
            "airplane",
            "hotspot",
            "wifi-connect",
            "ui-scale",
            "touchpad",
            "font",
            "caffeine",
            "gamemode",
            "phone",
            "locale",
        ),
    )
    control_parser.add_argument("value", nargs="?")
    theme_parser = sub.add_parser("theme", help="wallpaper-derived color themes")
    theme_parser.add_argument("action", choices=("list", "apply", "import", "remove", "pick",
                              "slideshow-get", "slideshow-set", "slideshow-next"))
    theme_parser.add_argument("payload", nargs="?", default="{}")
    timeline_parser = sub.add_parser("timeline", help="saved time of day for the Timeline theme")
    timeline_parser.add_argument("action", choices=("get", "set", "ready", "sync-clock"))
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
    screen_parser.add_argument(
        "action",
        choices=("region", "full", "window", "satty", "ocr", "qr", "record", "stop-record"),
        default="region",
        nargs="?",
    )
    screen_parser.add_argument("--with-audio", action="store_true", help="record screen with audio")
    wellbeing_parser = sub.add_parser("wellbeing", help="display digital wellbeing and application usage statistics")
    wellbeing_parser.add_argument("--date", help="specific date YYYY-MM-DD")
    wellbeing_parser.add_argument("--json", action="store_true", help="output JSON")
    appearance_parser = sub.add_parser("appearance", help="validated desktop appearance controls")
    appearance_parser.add_argument("action", choices=("get", "apply", "reset", "install"))
    appearance_parser.add_argument("payload", nargs="?", default="{}")
    organizer_parser = sub.add_parser("organizer", help="local calendar, tasks, notes and focus timer")
    organizer_parser.add_argument(
        "action",
        choices=(
            "get",
            "task-add",
            "event-add",
            "task-toggle",
            "item-remove",
            "note",
            "timer-start",
            "timer-pause",
            "timer-reset",
            "timer-duration",
            "import",
            "export",
        ),
    )
    organizer_parser.add_argument("payload", nargs="?", default="{}")
    windows_fs_parser = sub.add_parser("windows-drives", help="discover and mount Windows partitions")
    windows_fs_parser.add_argument("action", choices=("list", "mount", "unmount", "normalize-path"))
    windows_fs_parser.add_argument("target", nargs="?", default="")
    dotfiles_parser = sub.add_parser("dotfiles", help="manage dotfile symlinks (Stow / Chezmoi compatible)")
    dotfiles_parser.add_argument(
        "action",
        choices=("status", "check", "link", "stow", "apply", "unlink", "unstow", "delete", "restow"),
        nargs="?",
        default="status",
    )
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
    demo_parser = sub.add_parser("demo", help="ALPORA interactive design lab, motion studies and shell simulator")
    demo_parser.add_argument("mode", choices=("web", "native", "server"), default="web", nargs="?", help="demo mode: web (browser), native (Quickshell window), or server only")
    demo_parser.add_argument("--port", type=int, default=8080, help="port for the demo HTTP server (default: 8080)")
    demo_parser.add_argument("--no-browser", action="store_true", help="do not auto-open default web browser")

    # Game performance mode & Hoyoverse tweaks
    game_parser = sub.add_parser("game", help="game performance mode and Hoyoverse gaming optimizations (Honkai, ZZZ)")
    game_sub = game_parser.add_subparsers(dest="game_action")
    game_on = game_sub.add_parser("on", help="activate Game Mode (reduce Hyprland load, set performance governor)")
    game_on.add_argument("game", nargs="?", default="", help="optional target game name")
    game_sub.add_parser("off", help="deactivate Game Mode and restore balanced compositor state")
    game_toggle = game_sub.add_parser("toggle", help="toggle Game Mode on or off")
    game_toggle.add_argument("game", nargs="?", default="", help="optional target game name")
    game_status = game_sub.add_parser("status", help="check Game Mode status, CPU governor and applied tweaks")
    game_status.add_argument("--json", action="store_true", help="output status in JSON format")
    game_hoyo = game_sub.add_parser("hoyo", help="view Hoyoverse gaming profile and recommended env vars (ZZZ, Honkai Star Rail)")
    game_hoyo.add_argument("target", nargs="?", default="zzz", choices=("zzz", "honkai", "starrail", "genshin"), help="Hoyoverse game title (zzz, honkai, starrail, genshin)")
    game_launch = game_sub.add_parser("launch", help="launch a game wrapped inside ALPORA Game Mode")
    game_launch.add_argument("--game", help="game title preset to apply")
    game_launch.add_argument("command", nargs="+", help="command or executable path to execute")

    # Phone Ecosystem (KDE Connect integration)
    phone_parser = sub.add_parser("phone", help="phone ecosystem and connectivity integration (KDE Connect)")
    phone_sub = phone_parser.add_subparsers(dest="phone_action")
    phone_list = phone_sub.add_parser("list", help="list paired and reachable phone devices")
    phone_list.add_argument("--json", action="store_true", help="output devices in JSON format")
    phone_status = phone_sub.add_parser("status", help="check phone ecosystem connectivity status")
    phone_status.add_argument("--json", action="store_true", help="output status in JSON format")
    phone_ring = phone_sub.add_parser("ring", help="ring phone to find it")
    phone_ring.add_argument("device_id", nargs="?", help="optional device ID")
    phone_ping = phone_sub.add_parser("ping", help="send ping test notification to phone")
    phone_ping.add_argument("device_id", nargs="?", help="optional device ID")
    phone_ping.add_argument("--message", default="ALPORA Ecosystem Connected", help="custom ping message")
    phone_clip = phone_sub.add_parser("share-clipboard", help="sync clipboard text to phone")
    phone_clip.add_argument("text", nargs="?", help="text to share (defaults to current desktop clipboard)")
    phone_clip.add_argument("--device", dest="device_id", help="optional target device ID")
    phone_file = phone_sub.add_parser("send-file", help="send a file wirelessly to phone")
    phone_file.add_argument("file", help="path to local file")
    phone_file.add_argument("--device", dest="device_id", help="optional target device ID")

    # System Update Center (Windows Update style OTA updater)
    update_parser = sub.add_parser("update", help="check, download, and apply ALPORA OS updates")
    update_parser.add_argument("--json", action="store_true", help="output update info in JSON")
    update_parser.add_argument("--tui", action="store_true", help="open interactive TrueColor TUI Update Center")
    update_sub = update_parser.add_subparsers(dest="update_action")
    update_check = update_sub.add_parser("check", help="check for new ALPORA OS releases on GitHub")
    update_check.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="output update info in JSON")
    update_apply = update_sub.add_parser("apply", help="download and apply latest ALPORA OS update")
    update_apply.add_argument("--branch", default="main", help="target git branch to update from")
    update_apply.add_argument("--hold", action="store_true", help="keep terminal window open after update completes")
    update_status = update_sub.add_parser("status", help="show current ALPORA OS version and update state")
    update_status.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="output update status in JSON")
    update_tui = update_sub.add_parser("tui", help="open interactive TrueColor TUI Update Center")
    update_tui.add_argument("--branch", default="main", help="target git branch to update from")
    update_tui.add_argument("--auto-apply", action="store_true", help="automatically apply available update")

    # System Security and Hardening Audit
    sec_parser = sub.add_parser("security", help="audit Linux security posture and apply kernel hardening")
    sec_sub = sec_parser.add_subparsers(dest="security_action")
    sec_sub.add_parser("status", help="check system security score and active protections")
    sec_sub.add_parser("audit", help="run comprehensive security & performance assessment")
    sec_sub.add_parser("harden", help="view recommended commands to harden Arch Linux and UFW")
    sec_sub.add_parser("sysctl", help="output hardened sysctl.d configurations")

    # Storage Guard & Anti-Bloat CleanGuard
    storage_parser = sub.add_parser("storage", help="storage management, Btrfs subvolumes, and anti-bloat clean")
    storage_sub = storage_parser.add_subparsers(dest="storage_action")
    storage_sub.add_parser("status", help="overview of disk usage, Btrfs subvolumes, and cleanable caches")
    storage_sub.add_parser("overview", help="detailed partition metrics and cleanable sizes")
    storage_sub.add_parser("clean", help="reclaim disk space by safely clearing redundant caches")
    storage_move = storage_sub.add_parser("move", help="move heavy data folder to secondary disk and symlink")
    storage_move.add_argument("source", help="source directory path to move")
    storage_move.add_argument("target", help="target parent directory on another partition/drive")

    # Memory Shield & Anti-Thrashing Drop-RAM Engine
    mem_parser = sub.add_parser("memory", aliases=["mem"], help="RAM shield, zRAM compression, and anti-thrashing workspace optimizer")
    mem_sub = mem_parser.add_subparsers(dest="action")
    mem_sub.add_parser("status", help="view RAM, zRAM compression ratio, PSI stall pressure, and workspace allocation")
    mem_sub.add_parser("drop", help="drop caches, compact memory pages, and reclaim free RAM")
    mem_sub.add_parser("clean", help="alias for drop")
    mem_sub.add_parser("eco", help="throttle background workspace apps to prevent memory and CPU lag")
    mem_sub.add_parser("setup-zram", help="setup Zstandard compressed RAM swap and systemd-oomd")

    # Developer CLI Hub & Isolated Toolchain Hub
    dev_parser = sub.add_parser("dev", help="developer CLI toolchain hub and isolated binary management")
    dev_sub = dev_parser.add_subparsers(dest="dev_action")
    dev_sub.add_parser("list", help="list managed developer CLI tools and status")
    dev_inst = dev_sub.add_parser("install", help="install/link a CLI tool into ~/.alpora/dev/bin without sudo")
    dev_inst.add_argument("tool", help="name of CLI tool to install (lazygit, uv, bun, ripgrep, etc.)")
    dev_rem = dev_sub.add_parser("remove", help="cleanly remove a developer CLI tool")
    dev_rem.add_argument("tool", help="name of CLI tool to remove")
    dev_sub.add_parser("doctor", help="diagnose $PATH health and clean broken symlinks")
    dev_exp = dev_sub.add_parser("export", help="export installed developer tools profile to JSON")
    dev_exp.add_argument("--out", default="alpora-dev-stack.json", help="output profile JSON path")
    dev_imp = dev_sub.add_parser("import", help="import developer tools profile JSON")
    dev_imp.add_argument("file", help="profile JSON file to import")
    dev_clone = dev_sub.add_parser("clone", help="clone directory or file using Btrfs CoW reflink (0 bytes extra)")
    dev_clone.add_argument("source", help="source path")
    dev_clone.add_argument("destination", help="destination path")

    # File and Folder Properties Inspector
    prop_parser = sub.add_parser("properties", help="comprehensive file properties, sizes, and integrity hashes")
    prop_parser.add_argument("target", help="path to file or directory to inspect")

    # Instant System Rollback & Btrfs Snapshots
    snap_parser = sub.add_parser("snapshot", help="instant Btrfs system recovery snapshots and bootloader rollbacks")
    snap_sub = snap_parser.add_subparsers(dest="snapshot_action")
    snap_sub.add_parser("list", help="list available rollback snapshots")
    snap_create = snap_sub.add_parser("create", help="create instant rollback snapshot")
    snap_create.add_argument("description", nargs="?", default="Manual ALPORA Backup", help="snapshot description")
    snap_del = snap_sub.add_parser("delete", help="delete snapshot by ID")
    snap_del.add_argument("id", type=int, help="snapshot ID")

    # Application Privacy & Sandboxing Matrix
    priv_parser = sub.add_parser("privacy", help="application sandbox permissions and privacy control center")
    priv_sub = priv_parser.add_subparsers(dest="privacy_action")
    priv_sub.add_parser("status", help="audit application sandbox permissions")
    priv_iso = priv_sub.add_parser("isolate", help="isolate app from reading ~/.ssh or user home")
    priv_iso.add_argument("app", help="app ID (e.g. com.discordapp.Discord)")
    priv_allow = priv_sub.add_parser("allow", help="allow specific app permission (mic, camera, network)")
    priv_allow.add_argument("app", help="app ID")
    priv_allow.add_argument("permission", choices=("mic", "camera", "network"), help="permission name")
    priv_rev = priv_sub.add_parser("revoke", help="revoke specific app permission")
    priv_rev.add_argument("app", help="app ID")
    priv_rev.add_argument("permission", choices=("mic", "camera", "network"), help="permission name")

    # Panel, workspace and desktop shortcuts dispatchers
    sub.add_parser("launcher", help="toggle application launcher and omni-bar")
    sub.add_parser("quick-settings", help="toggle quick settings control center")
    sub.add_parser("notifications", help="toggle notifications flyout panel")
    sub.add_parser("clipboard", help="toggle clipboard history panel")
    sub.add_parser("overview", help="toggle workspaces and windows overview")
    sub.add_parser("power-menu", help="toggle session and power menu")
    sub.add_parser("toggle-mode", help="toggle between Work and Vibe modes")
    sub.add_parser("display-project", help="toggle display projection menu")
    sub.add_parser("video-pip", help="alias for floating video picture-in-picture player")
    sub.add_parser("welcome", help="open ALPORA first-run welcome wizard")
    running_apps_parser = sub.add_parser("running-apps", help="ALPORA process manager helper")
    running_apps_parser.add_argument("action", nargs="?", default="snapshot", choices=["snapshot", "signal"])
    running_apps_parser.add_argument("args", nargs="*", help="arguments for snapshot or signal")
    sub.add_parser("clipboard-serve", help="run clipboard history service")
    monitor_parser = sub.add_parser("monitor", help="interactive display management and layout persistence")
    monitor_parser.add_argument("action", nargs="?", default="list", choices=("list", "apply", "persist"))
    monitor_parser.add_argument("payload", nargs="?", default="[]")

    arcade_parser = sub.add_parser("arcade", help="ALPORA Desktop Arcade Engine mini-games")
    arcade_parser.add_argument("action", nargs="?", default="toggle", choices=("toggle", "open", "close", "play", "status", "scores", "reset-scores", "record"))
    arcade_parser.add_argument("game", nargs="?", default="catch", help="game identifier (e.g. catch)")
    arcade_parser.add_argument("score", type=int, nargs="?", default=0, help="score value to record")

    return parser
