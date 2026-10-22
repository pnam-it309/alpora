# Preview limitations

ALPORA is a development preview. The current local baseline is Arch Linux,
Hyprland 0.56.2, Quickshell 0.3.2 and Qt 6.12.0 on a single 1920×1080 monitor.

- **Performance:** exposed animated widgets still produce about 38–40% of one
  CPU core for the whole shell in short local samples. Robot smoothing reduced
  load with widgets occluded, but does not solve every desktop animation cost.
- **Hardware coverage:** physical suspend/resume, monitor hotplug, fractional
  scaling and new network/Bluetooth devices were not exhaustively exercised.
  A clean OS installation is still pending.
- **Installation:** the full `install.sh` installs Arch dependencies and prepares
  a complete session; clean-OS installation and first login remain unvalidated.
  The component installer does not install packages. Optional Waybar handover
  expects a recognised `autostart.sh` layout. There is no automatic uninstall
  command or installer for other distributions.
- **Input:** the shortcut editor imports supported `hyprland.lua` bindings.
  Unsupported callbacks, submaps and mouse gestures remain external.
- **System settings:** Bluetooth pairing uses Bluetoothctl in a terminal.
  Enterprise Wi-Fi uses Nmtui. Monitor layout editing is not implemented.
  Hardware-dependent controls need the relevant service and permissions.
- **Language:** the live interface is primarily Russian; full localisation is pending.
- **Diagnostics:** Qt SVG, Wayland text-input and portal warnings remain. Old
  duplicate watcher processes were cleared by restarting; a long soak test has
  not established whether the underlying duplication can recur.

The last local full check passed 197 tests and strict QML lint. This is a local
validation record, not a hosted CI badge or a guarantee of every configuration.
See the [audit](code-audit-2026-10-22.md) and
[performance evidence](performance-evidence/companion-tween-2026-10-22/README.md).

Report reproducible failures with component, trigger, expected/actual behaviour,
versions and relevant redacted logs. Do not post Wi-Fi passwords, clipboard
contents, personal notes or entire unreviewed configuration directories.
