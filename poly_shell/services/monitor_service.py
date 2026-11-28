"""Monitor layout management and persistence service for Hyprland."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base import SafeRunner
from ..core.state import ConfigError, Paths, ROOT

logger = logging.getLogger(__name__)

SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_monitor_spec(m: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize a single monitor specification."""
    if not isinstance(m, dict):
        raise ConfigError("Monitor spec must be a dictionary")
    name = str(m.get("name", "")).strip()
    if not name or not SAFE_NAME_RE.match(name):
        raise ConfigError(f"Invalid monitor name: {name}")

    try:
        width = int(m.get("width", 1920))
        height = int(m.get("height", 1080))
        if width <= 0 or height <= 0 or width > 16384 or height > 16384:
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigError(f"Invalid resolution for monitor {name}")

    try:
        raw_hz = m.get("refreshRate", m.get("refresh_rate", 60.0))
        refresh_rate = round(float(raw_hz), 2)
        if refresh_rate <= 0 or refresh_rate > 500:
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigError(f"Invalid refresh rate for monitor {name}")

    try:
        x = int(m.get("x", 0))
        y = int(m.get("y", 0))
        if abs(x) > 65536 or abs(y) > 65536:
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigError(f"Invalid position for monitor {name}")

    try:
        scale = round(float(m.get("scale", 1.0)), 2)
        if scale < 0.25 or scale > 5.0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ConfigError(f"Invalid scale for monitor {name}")

    disabled = bool(m.get("disabled", False))
    return {
        "name": name,
        "width": width,
        "height": height,
        "refresh_rate": refresh_rate,
        "x": x,
        "y": y,
        "scale": scale,
        "disabled": disabled,
    }


class MonitorService:
    """Service to arrange, apply, and persist multi-monitor configurations."""

    def __init__(self, paths: Optional[Paths] = None):
        self.paths = paths or Paths.current()

    def apply_and_persist(self, monitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply monitor layout dynamically via hyprctl and persist to config files."""
        if not isinstance(monitors, list) or not monitors:
            raise ConfigError("Monitors list cannot be empty")

        validated = [validate_monitor_spec(m) for m in monitors]
        commands_run: List[str] = []

        # 1. Apply to running Hyprland compositor
        for m in validated:
            if m["disabled"]:
                arg = f"{m['name']},disable"
            else:
                arg = f"{m['name']},{m['width']}x{m['height']}@{m['refresh_rate']},{m['x']}x{m['y']},{m['scale']}"
            cmd = ["hyprctl", "keyword", "monitor", arg]
            SafeRunner.run(cmd, timeout=3.0)
            commands_run.append(f"hyprctl keyword monitor {arg}")

        # 2. Persist to files
        persisted_files = self.persist_configs(validated)

        return {
            "success": True,
            "applied_count": len(validated),
            "commands": commands_run,
            "persisted_files": persisted_files,
            "message": f"Successfully applied and persisted {len(validated)} display(s).",
        }

    def persist_configs(self, monitors: List[Dict[str, Any]]) -> List[str]:
        """Write monitor configurations to Lua and Hyprland config files."""
        persisted: List[str] = []

        # A. ~/.config/hypr/config/monitors.lua
        lua_target = Path.home() / ".config/hypr/config/monitors.lua"
        try:
            lua_target.parent.mkdir(parents=True, exist_ok=True)
            lua_lines = ["-- ALPORA Monitor Configuration (Auto-generated)\n"]
            for m in monitors:
                if m["disabled"]:
                    lua_lines.append(f'hl.monitor({{ output = "{m["name"]}", mode = "disable" }})\n')
                else:
                    lua_lines.append(
                        f'hl.monitor({{\n'
                        f'  output = "{m["name"]}",\n'
                        f'  mode = "{m["width"]}x{m["height"]}@{m["refresh_rate"]}Hz",\n'
                        f'  position = "{m["x"]}x{m["y"]}",\n'
                        f'  scale = {m["scale"]},\n'
                        f'}})\n'
                    )
            lua_target.write_text("".join(lua_lines), encoding="utf-8")
            persisted.append(str(lua_target))
        except OSError as exc:
            logger.warning("Failed to write monitors.lua: %s", exc)

        # B. dotfiles/hypr/.config/hypr/hyprland.conf & ~/.config/hypr/hyprland.conf
        conf_targets = [
            ROOT / "dotfiles/hypr/.config/hypr/hyprland.conf",
            Path.home() / ".config/hypr/hyprland.conf",
        ]
        conf_monitor_lines = []
        for m in monitors:
            if m["disabled"]:
                conf_monitor_lines.append(f"monitor = {m['name']}, disable\n")
            else:
                conf_monitor_lines.append(
                    f"monitor = {m['name']}, {m['width']}x{m['height']}@{m['refresh_rate']}, {m['x']}x{m['y']}, {m['scale']}\n"
                )

        for conf_file in conf_targets:
            if conf_file.exists():
                try:
                    content = conf_file.read_text(encoding="utf-8")
                    # Replace existing monitor lines or append if none
                    lines = content.splitlines(keepends=True)
                    new_lines = []
                    inserted = False
                    for line in lines:
                        if line.strip().startswith("monitor = ") or line.strip().startswith("monitor="):
                            if not inserted:
                                new_lines.extend(conf_monitor_lines)
                                inserted = True
                        else:
                            new_lines.append(line)
                    if not inserted:
                        new_lines.append("\n# ALPORA Display Configuration\n")
                        new_lines.extend(conf_monitor_lines)
                    conf_file.write_text("".join(new_lines), encoding="utf-8")
                    persisted.append(str(conf_file))
                except OSError as exc:
                    logger.warning("Failed to update %s: %s", conf_file, exc)

        return persisted
