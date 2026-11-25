# ALPORA Live Desktop Integration Checks (`scripts/checks/`)

This directory contains interactive integration check scripts intended to be run inside an active Wayland / Hyprland session with live UI panels:

* `check-bar-panels`: Exercises real desktop panels (Bar popups, dock reveals).
* `check-render-load`: Measures idle and active CPU/GPU render load.
* `check-companion-travel`: Verifies robot companion pathfinding and landing surfaces.
* `check-living-landscape`: Tests wallpaper transitions and solar timeline math.
* `check-overview-swipe`: Exercises workspace gesture swipe tracking.
* `check-launcher-unfold`: Tests launcher animation curves and keyboard navigation.

## Usage
Most checks require the `--live` flag to prevent accidental invocation outside a desktop session:
```bash
./scripts/checks/check-bar-panels --live
./scripts/checks/check-render-load --seconds 5
```
