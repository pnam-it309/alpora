"""Generic wlroots and Sway compositor communication adapter."""
from __future__ import annotations

import json
import os
from typing import Any, Sequence

from .base import SafeRunner
from .compositor_base import BaseCompositorAdapter


class GenericWlrootsAdapter(BaseCompositorAdapter):
    """Encapsulates interaction with generic wlroots / Sway compositors."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if swaymsg or wlr-randr is available and session matches."""
        current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "sway" in current_desktop or "wlroots" in current_desktop or "niri" in current_desktop:
            return True
        return SafeRunner.is_available("swaymsg")

    @classmethod
    def swaymsg(cls, args: Sequence[str], timeout: float = 3.0, check: bool = False) -> str:
        """Execute a swaymsg command."""
        cmd = ["swaymsg", *args]
        proc = SafeRunner.run(cmd, timeout=timeout, check=check)
        return proc.stdout.strip()

    @classmethod
    def get_monitors(cls) -> list[dict[str, Any]]:
        """Return list of active displays via swaymsg -t get_outputs."""
        if not SafeRunner.is_available("swaymsg"):
            return []
        output = cls.swaymsg(["-t", "get_outputs"], timeout=3.0)
        if not output:
            return []
        try:
            parsed = json.loads(output)
            if not isinstance(parsed, list):
                return []
            monitors = []
            for item in parsed:
                monitors.append({
                    "id": item.get("id", 0),
                    "name": item.get("name", "Unknown"),
                    "width": item.get("current_mode", {}).get("width", 1920),
                    "height": item.get("current_mode", {}).get("height", 1080),
                    "refreshRate": float(item.get("current_mode", {}).get("refresh", 60000)) / 1000.0,
                    "focused": bool(item.get("focused", False)),
                })
            return monitors
        except (ValueError, TypeError):
            return []

    @classmethod
    def get_workspaces(cls) -> list[dict[str, Any]]:
        """Return list of active workspaces via swaymsg -t get_workspaces."""
        if not SafeRunner.is_available("swaymsg"):
            return []
        output = cls.swaymsg(["-t", "get_workspaces"], timeout=3.0)
        if not output:
            return []
        try:
            parsed = json.loads(output)
            if not isinstance(parsed, list):
                return []
            workspaces = []
            for item in parsed:
                workspaces.append({
                    "id": item.get("num", item.get("id", 1)),
                    "name": item.get("name", str(item.get("num", 1))),
                    "monitor": item.get("output", ""),
                    "active": bool(item.get("focused", False)),
                    "urgent": bool(item.get("urgent", False)),
                })
            return workspaces
        except (ValueError, TypeError):
            return []

    @classmethod
    def get_clients(cls) -> list[dict[str, Any]]:
        """Return list of open client windows via swaymsg -t get_tree."""
        if not SafeRunner.is_available("swaymsg"):
            return []
        output = cls.swaymsg(["-t", "get_tree"], timeout=3.0)
        if not output:
            return []
        try:
            tree = json.loads(output)
            windows: list[dict[str, Any]] = []

            def _walk(node: dict[str, Any]) -> None:
                if node.get("type") in ("con", "floating_con") and node.get("name"):
                    windows.append({
                        "address": str(node.get("id", "")),
                        "title": node.get("name", ""),
                        "class_name": node.get("app_id") or node.get("window_properties", {}).get("class", ""),
                        "workspace_id": node.get("workspace_id", 0),
                        "floating": node.get("type") == "floating_con",
                        "focused": bool(node.get("focused", False)),
                    })
                for child in node.get("nodes", []) + node.get("floating_nodes", []):
                    if isinstance(child, dict):
                        _walk(child)

            if isinstance(tree, dict):
                _walk(tree)
            return windows
        except (ValueError, TypeError):
            return []

    @classmethod
    def dispatch(cls, command: str, arg: str = "") -> bool:
        """Call swaymsg dispatcher or generic action."""
        if not SafeRunner.is_available("swaymsg"):
            return False
        cmd = [command]
        if arg:
            cmd.append(arg)
        proc = SafeRunner.run(["swaymsg", *cmd], timeout=3.0)
        return proc.returncode == 0
