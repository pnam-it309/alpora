# `poly_shell/system/` — System & Desktop Integration Helpers

This package contains **stateless OS integration utilities, one-shot hardware/session scripts, and lifecycle helpers** invoked directly by the CLI or Quickshell `Process` adapters.

## Responsibilities
- **`desktop.py` & `network_controls.py` & `radios_power.py`**: One-shot desktop controls (`poly-shell control ...`), wallpaper process management (`swaybg` / `awww`), Wi-Fi/Hotspot CLI adapters, and backlight/Night Light helpers.
- **`bootstrap.py` & `integration.py` & `preflight.py` & `installer_ui.py`**: Installation, autostart patching, Waybar fallback, and system environment readiness checks.
- **`indicators.py` & `lockscreen.py` & `lock_media.py`**: Mako notification config generation, Hyprlock config syncing, and OSD indicators.
- **`widgets.py` & `running_apps.py` & `programs.py`**: Desktop widget state persistence, process snapshots, and installed desktop application inventory.
- **`windows_fs.py` & `wine_apps.py` & `diagnostics.py`**: NTFS/FAT32 partition mounting, Wine `.exe` prefix automation, and diagnostic bundle generation.

## Architectural Boundary (`system/` vs `services/`)
- Place **one-shot CLI/OS integration functions** and file/config generators in `poly_shell/system/`.
- Place **stateful domain services** that register with `ServiceRegistry` and expose RPC endpoints through `PolyShellDaemon` (`ipc.sock`) in `poly_shell/services/`.
