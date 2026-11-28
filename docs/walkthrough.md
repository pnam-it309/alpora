# ALPORA OS — v1.2.0 Feature Walkthrough

This guide provides an end-to-end walkthrough of the major desktop superpowers introduced in **ALPORA OS v1.2.0**:
1. [Interactive Monitor Canvas & Multi-Display Management](#1-interactive-monitor-canvas--multi-display-management)
2. [iCalendar (.ics) Sync & Daily Planner](#2-icalendar-ics-sync--daily-planner)
3. [GameMode & Low-Latency Gaming Tuning with Restore Hooks](#3-gamemode--low-latency-gaming-tuning-with-restore-hooks)
4. [ALPORA Desktop Arcade Engine & Pet Catch](#4-alpora-desktop-arcade-engine--pet-catch)

---

## 1. Interactive Monitor Canvas & Multi-Display Management

ALPORA v1.2.0 replaces static display configuration with a dynamic, real-time spatial monitor canvas integrated directly into the Settings hub.

### Key Capabilities
- **Spatial Drag-and-Drop Canvas**: Visually position displays relative to one another in [SettingsMonitorsPage.qml](file:///home/pnam/code/alpora/shell/settings/SettingsMonitorsPage.qml). Displays snap cleanly to adjacent monitor edges.
- **Alignment Presets**: Quick-align buttons for instant primary/secondary positioning:
  - Primary Left / Secondary Right
  - Primary Right / Secondary Left
  - Secondary Above Primary
  - Secondary Below Primary
- **Per-Monitor Scaling & Refresh Rates**: Dedicated dropdowns to adjust display scale factor (`1.0x`, `1.25x`, `1.5x`, `1.75x`, `2.0x`) and display refresh rates per output.
- **Safe Persistence Engine**: Settings are safely dispatched live to Hyprland via `hyprctl keyword monitor` and atomically persisted to `~/.config/hypr/config/monitors.lua` and `dotfiles/hypr/.config/hypr/hyprland.conf`.

### CLI Commands
Inspect and apply monitor layouts programmatically:
```bash
# List detected monitors and current layout
poly-shell monitor list

# Apply custom geometry and scale dynamically
poly-shell monitor apply '[{"name": "DP-1", "x": 0, "y": 0, "width": 2560, "height": 1440, "scale": 1.0, "refresh_rate": 165}, {"name": "HDMI-A-1", "x": 2560, "y": 0, "width": 1920, "height": 1080, "scale": 1.0, "refresh_rate": 60}]'
```

---

## 2. iCalendar (.ics) Sync & Daily Planner

The My Day Planner panel now features bidirectional iCalendar / CalDAV RFC 5545 calendar synchronization with zero external dependencies.

### Key Capabilities
- **Zero-Dependency RFC 5545 Engine**: Implemented in [ical_sync.py](file:///home/pnam/code/alpora/poly_shell/services/ical_sync.py) with comprehensive support for `VEVENT`, `VTODO`, recurrence rules, timezones, alarms, and timestamps.
- **Seamless UI Integration**: Dedicated Import and Export buttons located in the top bar calendar panel header ([DayPanel.qml](file:///home/pnam/code/alpora/shell/panels/DayPanel.qml)).
- **Scheduled Reminders**: Imported events automatically sync with ALPORA's background notification scheduler, dispatching native desktop alerts via `notify-send`.

### CLI Commands
Import and export calendar schedules directly from terminal workflows:
```bash
# Export all current tasks and scheduled events to an RFC 5545 .ics file
poly-shell organizer export ~/calendar_backup.ics

# Import an external .ics file (e.g., Google Calendar, Apple Calendar, Thunderbird)
poly-shell organizer import ~/work_schedule.ics
```

---

## 3. GameMode & Low-Latency Gaming Tuning with Restore Hooks

The enhanced GameMode service elevates system performance for modern gaming (native Wayland, Wine, Steam Proton) while guaranteeing clean restoration when games exit.

### Key Capabilities
- **Automatic CPU Governor Tuning**: Dynamically escalates CPU governor across all cores to `performance` via `cpupower`, `powerprofilesctl`, or direct sysfs (`/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`).
- **State Restore Hooks**: Pre-gaming governor and power profiles are cached in-memory and on disk; state restoration hooks guarantee rollback to the previous power state on game exit, process termination, or unexpected signals.
- **Process Renicing & Priority**: Automatically detects running game executables and render threads, elevating process scheduling priority (`nice -5`).
- **Distraction-Free Gaming (DND)**: Automatically silences desktop notification popups during gameplay and restores notification delivery when gaming stops.
- **Control Center HUD**: Quick action tile in [QuickSettings.qml](file:///home/pnam/code/alpora/shell/panels/QuickSettings.qml) and dedicated subpage in [QuickGameModeSubpage.qml](file:///home/pnam/code/alpora/shell/panels/QuickGameModeSubpage.qml) displaying active optimizations.

### CLI Commands
Control GameMode manually or wrap games:
```bash
# Query active GameMode status
poly-shell game-mode status

# Toggle or trigger optimizations
poly-shell game-mode toggle
```

---

## 4. ALPORA Desktop Arcade Engine & Pet Catch

A built-in desktop arcade and mini-game platform that integrates directly with ALPORA's interactive desktop pet companion.

### Key Capabilities
- **Quick Access Shortcuts**:
  - Global shortcut: `Super + G`
  - TopBar gamepad icon button ([TopBarArcadeButton.qml](file:///home/pnam/code/alpora/shell/components/TopBarArcadeButton.qml))
  - Desktop Companion interaction
  - CLI command: `poly-shell arcade toggle`
- **Pet Catch Mini-Game**:
  - Interactive ball toss mechanics where the player launches balls across the desktop screen.
  - Real-time physics, bounce detection, and trajectory calculation.
  - Desktop Companion ([DesktopCompanion.qml](file:///home/pnam/code/alpora/shell/widgets/DesktopCompanion.qml)) autonomously reacts, runs to intercept the ball, and plays celebratory catch animations.
  - Combo scoring multiplier rewarding consecutive successful catches.
- **Persistent High Scores**: Scores are saved to `~/.config/alpora/arcade_scores.json` and persist across sessions.
- **Theme-Adaptive Retro HUD**: CRT scanline filter, glass score HUD, and full localization support for English, Vietnamese, Russian, and Spanish.

### CLI Commands
Manage the arcade engine and query high scores:
```bash
# Toggle arcade overlay
poly-shell arcade toggle

# Check arcade engine status (JSON)
poly-shell arcade status

# View leaderboard high scores
poly-shell arcade scores

# Reset high scores
poly-shell arcade reset-scores
```
