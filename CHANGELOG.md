# Changelog

## [v1.2.0] — 2026-11-28 — Interactive Displays, iCal Sync, GameMode & Desktop Arcade Release

### Key Highlights & Superpowers

#### Interactive Display Management (Settings Monitors Page)
- **Interactive Spatial Arrangement**: Real-time canvas in `SettingsMonitorsPage.qml` allowing drag-and-drop repositioning of displays with edge snapping.
- **Quick Alignment Presets**: One-click spatial arrangements (Primary Left/Right, Secondary Top/Bottom).
- **Per-Monitor Controls**: Dedicated display scaling (1.0x, 1.25x, 1.5x, 1.75x, 2.0x) and refresh rate mode selectors per connected monitor.
- **Safe Persistence Engine**: `poly-shell monitor apply` dispatches sanitized `hyprctl keyword monitor` commands and atomically writes persistent configs to `~/.config/hypr/config/monitors.lua` and `dotfiles/hypr/.config/hypr/hyprland.conf`.

#### CalDAV / iCalendar (.ics) Sync & Export for My Day Planner
- **RFC 5545 iCalendar Engine**: Self-contained parser and generator in `poly_shell/services/ical_sync.py` with zero external dependencies.
- **Planner Import & Export**: Import external calendar `.ics` files and export daily tasks and scheduled events via `poly-shell organizer import <file>` and `poly-shell organizer export <file>`.
- **UI Integration**: Action buttons in `shell/panels/DayPanel.qml` with native desktop notifications via `notify-send`.

#### GameMode & Gaming Performance HUD/Tuning
- **Governor & Sysfs Control with Restore Hooks**: Automatic CPU governor elevation (`cpupower`, `powerprofilesctl`, or sysfs `scaling_governor`) to `performance` on game launch with reliable state restoration hooks ensuring pre-game governor and power profiles are restored on process termination or exit.
- **Process Renicing**: Automatic detection and priority elevation (nice -5) for game processes and Wine/Proton render threads.
- **Distraction-Free Gaming**: Automatic notification suppression via DND during gameplay with seamless restoration.
- **Quick Settings HUD**: Dedicated `QuickGameModeSubpage.qml` and quick action tile in the control center with live optimization status feedback.

#### ALPORA Desktop Arcade Engine, Pet Catch & Fishing Mini-Games
- **Native Arcade Overlay & Multi-Game Hub**: Immersive overlay (`shell/widgets/ArcadeOverlay.qml`) accessible via `Super + G`, dedicated TopBar gamepad button (`shell/components/TopBarArcadeButton.qml`), or CLI `poly-shell arcade toggle`.
- **Pet Catch Interactive Mini-Game**: Interactive ball toss mini-game (`shell/widgets/ArcadeCatchGame.qml`) directly linked with Desktop Companion (`DesktopCompanion.qml`), featuring real-time collision detection, dynamic catch animations, physics trajectories, squash-and-stretch, and combo scoring.
- **Desktop Fishing Mini-Game**: Relaxing pond fishing simulation (`shell/widgets/ArcadeFishingGame.qml`, `FishingPondView.qml`) with rod casting, bobber ripples, fish bite detection, reel tension gauge mini-game, species catalog (Carp, Salmon, Mythic Golden Koi), length/weight measurements, and score celebration.
- **Persistent High Scores & CLI Hub**: High scores saved to `~/.config/poly-shell/arcade.json`, queryable and manageable via `poly-shell arcade status/scores/reset-scores/record`.

#### Windows-Style Free-Float Mode & Cascade Window Placement
- **Smart Free-Float Toggle**: New `poly-shell control float-toggle` and keybinding `Super + Shift + F` to easily toggle floating with comfortable 1080x700 window sizing.
- **Cascade Window Arrangement**: New `poly-shell control cascade` and keybinding `Super + Shift + C` to arrange all floating windows on the workspace in a clean staircase cascade.

#### Omni-Search in Application Launcher
- **Instant Calculator & Math Evaluation**: Instant calculation for math formulas (`= 1024 * 768 / 60`, sqrt, sin, cos) with one-click copy to clipboard.
- **Direct Terminal Runner**: Prefix `>` or `$` to execute commands directly in terminal.
- **Direct Folder Location Opening**: Typing `~/` or `/` presents an instant card to open the path directly in file manager.

#### Core Clarity, Reliability & Code Modularization
- **Modularized Running Apps, Launcher & Video PiP**: Extracted `DesktopProcessRow.qml`, `LauncherInstantSection.qml`, and `VideoPipPlaybackBar.qml`, keeping all source files comfortably under the strict 500-line budget (`Launcher.qml` 453 lines, `VideoPipOverlay.qml` 428 lines).
- **Strict QML Linting Passed**: Resolved `duplicate-property-binding` on `squashX`/`squashY` in `ArcadeCatchGame.qml` and connected `ArcadePhysics.js` directly for shared velocity and restitution calculations.
- **Semantic Palette Compliance**: Replaced baked hex colors in `VideoPipOverlay.qml` with dynamic semantic palette tokens (`Session.background`).
- **Hyprland Shortcut Collision Fixed**: Resolved keybinding conflict where `Super + M` mapped to both notifications and window minimize; allocated Windows-standard `Super + D` / `Super + Shift + D` for minimize to special workspace while preserving `Super + M` for notifications.
- **Hardened Omni-Search Calculator**: Fixed math evaluation regex in `LauncherQuery.js` to prevent code injection, added support for functions (`sqrt`, `sin`, `cos`, `abs`, `round`, `floor`, `ceil`) and power operator (`^`), verified with dedicated test suite in `tests/test_launcher_query.py`.
- **Enhanced Float Cascade & Multi-Monitor**: Improved `window_service.py` with cascade cycle wrapping for workspaces with many windows, automatic fullscreen unmapping, and expanded unit tests (444 tests passing).

## [v1.1.0] — 2026-11-28 — Feature & Architecture Release

### Key Highlights & Superpowers

#### TrueColor Update Center (TUI & GUI)
- **Interactive TUI**: 24-bit TrueColor Update Center (`poly-shell update tui`) with theme-adaptive palette, box-drawing layout, 5-stage progress animation, and keyboard shortcuts (`a` to apply, `q` to quit).
- **Settings Integration**: Dedicated Update & About settings page (`SettingsUpdateAbout.qml`) displaying current vs upstream version, changelog viewer, and 1-click update trigger.
- **OTA Infrastructure**: Semver parsing, cache validation, and safe Git pull with automated snapshot rollbacks on failure.

#### Personal Wallpapers & Slideshow Engine
- **Local Image Discovery**: Automatic scanning across `~/Pictures`, `~/Downloads`, `~/Pictures/Screenshots`, `/usr/share/backgrounds`, or any user-defined folder.
- **Color Extraction & Sync**: Automatic palette extraction for GTK, Hyprland, Terminal, and Lockscreen directly from custom wallpapers.
- **Fixed Lockscreen Sandbox**: Eliminated path restrictions in `lockscreen.py` allowing custom wallpaper rendering on Hyprlock without rollbacks.
- **Wallpaper Slideshow**: Configurable rotation timer (`slideshow.py`, `ThemeSlideshowCard.qml`) supporting 5/15/30/60 minute intervals, random shuffle, and folder targeting.
- **Native File Picker**: Bridge to system file dialogs (`kdialog`, `zenity`, `yad`) with graceful fallback to path selector.

#### Calendar, Weather & Schedule Integration
- **Open-Meteo Weather Outlook**: Integrated 7-day weather outlook card (`DayWeatherCard.qml`) into the topbar calendar panel showing current temp, humidity, daily high/low, and rain probability.
- **Interactive Schedule Reminders**: Schedule events with customizable notification reminders (exact time, 5/15/30/60 mins, or 1 day before) dispatched through `notify-send`.
- **Date Sync**: Tapping any day tile in the weather forecast immediately centers and selects that day in the calendar.

#### Codebase Modularization & Maintainability
- **Large File Breakdown**: Refactored all monolithic files (`SettingsDetails.qml`, `QuickSettingsSubpages.qml`, `welcome.qml`, `Launcher.qml`, `task_manager.qml`, `themes.py`) to strictly under 500 lines.
- **Automated Guardrails**: Added `test_file_budget.py` unit test to prevent future file bloat in CI.
- **Maintenance Handbook**: Comprehensive [MAINTAINING.md](file:///home/pnam/code/alpora/docs/MAINTAINING.md), GitHub `CODEOWNERS`, `dependabot.yml`, and `SECURITY.md`.

## [v1.0.0] — 2026-11-03 — Official First Release

The first production-ready release of **ALPORA OS**: a coordinated, fluid Wayland desktop operating environment built on Arch Linux, Hyprland, and Quickshell.

### Key Highlights & Superpowers

#### Security Shield & System Hardening (Windows Defender Equivalent)
- **Visual Security Hub**: Integrated `SecurityShieldCard.qml` into Quick Settings with 1-click audit action.
- **Kernel & Network Hardening**: Built-in sysctl security profile (`99-alpora-security.conf`) enabling ASLR, BPF JIT, TCP SYN cookies, and UFW firewall enforcement.
- **Gaming & Low Latency Optimization**: Kernel tuning (`99-alpora-performance.conf`) optimizing `vm.max_map_count` for Steam Proton and irqbalance for smooth multitasking.
- **Application Privacy Sandbox**: Flatpak permission manager (`poly-shell privacy status/isolate/allow/revoke`) to control camera, microphone, and filesystem access.

#### Storage Guard & Seamless Drive Mental Model ("C: vs D: Drive")
- **Transparent Compression**: Btrfs ZSTD level 3 filesystem compression saving 20-35% disk space automatically.
- **Non-Breaking Data Moves**: Move games, code, and downloads across disks (`poly-shell storage move`) without breaking shortcuts, configs, or application paths.
- **File Properties Inspector**: Native `poly-shell properties <path>` revealing allocated vs logical disk size, permissions, and SHA-256/MD5 integrity checksums.
- **Storage Maintenance**: Automated journald log capping (`150M`) and one-click cleanup (`poly-shell storage clean`).

#### Instant System Recovery (5-Second Rollback)
- **Btrfs Snapper Snapshots**: Integrated `snapper` and `snap-pac` (`poly-shell snapshot list/create/delete`).
- **Bootloader Recovery**: Automatic snapshot creation before and after any package update, allowing 5-second boot rollback if an update ever fails.

#### Centralized Developer CLI Hub
- **Isolated User Space**: Managed developer tools in `~/.alpora/dev/bin` without sudo requirements or global PATH pollution.
- **Tool Management**: Standardized catalog (`uv`, `bun`, `pnpm`, `lazygit`, `ripgrep`, etc.) via `poly-shell dev list/install/remove/doctor/export/import`.
- **Reflink CoW Cloning**: Instant 0-byte project duplication (`poly-shell dev clone <src> <dst>`) on Btrfs.

#### OTA Update Center & Distribution
- **Windows-Style Update Flow**: `poly-shell update check/status/apply` with GitHub Releases integration.
- **Cloud ISO Builder**: Automated GitHub Actions workflow compiling official bootable Arch Linux Live ISO images with offline `alpora-install`.
- **Vietnamese IME & Windows App Compatibility**: Native Fcitx5 Bamboo and Wine presets (Zalo, UltraViewer, Notepad++).

---

## [0.1.0-dev] — Development Preview

- Added `--ui-only` standalone UI mode to `install.sh` and `bootstrap.py`: installs the ALPORA shell panel, widgets, and themes without altering existing Hyprland configurations or requiring Arch package management.
- Broadened installer platform support to Arch-based distributions (EndeavourOS, CachyOS, Manjaro, Garuda, Artix, ArcoLinux, Archcraft) and custom kernels via `ID_LIKE` and derivative detection.
- Added `--core-only` flag to `install.sh` separating core compositor/shell packages from optional bundled applications (Firefox, Nautilus, Kitty, Foot, Fuzzel, Pavucontrol).
- Added `uninstall.sh` with `--dry-run`, `--restore-config`, and `--purge` flags to cleanly stop user units, remove installed links/files, and restore previous Hyprland configuration backups.
- Added lightweight internationalisation (i18n) framework supporting English (system baseline), Vietnamese, and Russian with dynamic runtime switching, zero-cost memory table lookups, and JSON locale files in `assets/locales/`.
- Optimized desktop widget and companion CPU consumption: eliminated external `hyprctl` process spawning via in-memory `Hyprland.toplevels` tracking, added immediate occlusion on fullscreen windows and overview, throttled clock second sweep to rest 78% of each second, made weather particle timers conditional on active effects, and introduced adaptive tick rates for companion resting states.
- Validated production configuration in isolated UID 1000/1001 profiles, real asset downloads, spaced paths, repeat setup and a separate software Wayland display; documented the remaining clean-OS gate.
- Fixed first-start QIcon worker loading in launcher/dock, enabling active-but-disabled network/Bluetooth services, and preflighting settings-launcher conflicts before installation writes.

- Added ALPORA Fetch: a faceted terminal system card that follows active/custom/Timeline palettes, supports snapshots and restores terminal state on exit.
- Refreshed the working-desktop screenshots and native theme-switching video with the live system card.
- Included `alpora-fetch` in both installation methods, verified its installed link and QML/service files, and added the missing `xdg-user-dirs` screenshot dependency.
- Updated both README languages, installed-file map, application inventory and first-login commands.

- Reworked the English/Russian README around a working-desktop hero, six landscape palettes, a real theme-switching recording and direct installation guidance.

- Added a guided terminal installer with theme selection, real phase timing, private logs and next-login file verification.
- Added a versioned ALPORA reference preset for missing preferences, preserving existing user data.

- Added pinned Papirus/Bibata installation, consistent GTK/compositor cursor settings and theme-aware folder overlays.
- Added an Arch install.sh preview with package installation, backed-up session defaults and offline theme preparation. Clean-OS validation is pending.

- Introduced ALPORA as the public name, retaining `poly-shell` command and data compatibility.
- Added a landscape banner, English/Russian project pages and current desktop screenshots.
- Added installation/recovery documentation, contribution guidance and third-party notices.
- Existing desktop includes coordinated themes and Timeline, panel controls, launcher,
  dock, workspace overview, organiser, clipboard history and desktop widgets.
- Added settings management of supported Lua hotkeys and robot visibility/flight preferences.
- Fixed robot pausing when bar panels open; changed joint smoothing to use its existing clock.
- Latest local baseline: 197 tests and strict QML lint; known performance and hardware
  validation limits remain documented. No stable release has been published.
