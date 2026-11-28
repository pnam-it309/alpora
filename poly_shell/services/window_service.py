"""Window layout service for ALPORA: Free-Float mode and Cascade window positioning."""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

from ..adapters.base import SafeRunner


def _run_hyprctl(args: list[str]) -> str:
    """Safely run hyprctl command and return stdout."""
    hyprctl = shutil.which("hyprctl")
    if not hyprctl:
        return ""
    res = SafeRunner.run([hyprctl, *args], timeout=2.0)
    return res.stdout if res.returncode == 0 else ""


def get_active_workspace() -> int:
    """Get currently focused workspace ID."""
    out = _run_hyprctl(["activeworkspace", "-j"])
    if out:
        try:
            data = json.loads(out)
            return int(data.get("id", 1))
        except (json.JSONDecodeError, ValueError):
            pass
    return 1


def get_clients() -> list[dict[str, Any]]:
    """Return all Hyprland toplevel clients."""
    out = _run_hyprctl(["clients", "-j"])
    if not out:
        return []
    try:
        data = json.loads(out)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def get_active_window() -> dict[str, Any] | None:
    """Return details of currently focused window."""
    out = _run_hyprctl(["activewindow", "-j"])
    if not out:
        return None
    try:
        data = json.loads(out)
        return data if isinstance(data, dict) and data.get("address") else None
    except json.JSONDecodeError:
        return None


def cascade_floating_windows(workspace_id: int | None = None) -> int:
    """Arrange all floating windows on the workspace in a clean cascade staircase."""
    ws = workspace_id if workspace_id is not None else get_active_workspace()
    clients = [c for c in get_clients() if c.get("floating") and c.get("workspace", {}).get("id") == ws]
    if not clients:
        return 0

    start_x = 90
    start_y = 70
    offset_step = 38
    default_w = 1080
    default_h = 700

    count = 0
    for idx, client in enumerate(clients):
        addr = client.get("address", "")
        if not addr:
            continue
        cycle = idx % 8
        set_num = idx // 8
        cx = start_x + (cycle * offset_step) + (set_num * 100)
        cy = start_y + (cycle * offset_step)

        if client.get("fullscreen"):
            _run_hyprctl(["dispatch", "fullscreen", f"0,address:{addr}"])

        # Dispatch resize and move
        _run_hyprctl(["dispatch", "resizewindowpixel", f"exact {default_w} {default_h},address:{addr}"])
        _run_hyprctl(["dispatch", "movewindowpixel", f"exact {cx} {cy},address:{addr}"])
        count += 1

    return count


def toggle_floating_smart() -> bool:
    """Toggle floating on the active window with smart Windows-style sizing."""
    active = get_active_window()
    if not active:
        # Default fallback toggle
        _run_hyprctl(["dispatch", "togglefloating"])
        return True

    addr = active.get("address", "")
    is_floating = active.get("floating", False)

    if not is_floating:
        if active.get("fullscreen"):
            _run_hyprctl(["dispatch", "fullscreen", f"0,address:{addr}"])
        # Switch to floating and apply comfortable default dimensions
        _run_hyprctl(["dispatch", "togglefloating", f"address:{addr}"])
        _run_hyprctl(["dispatch", "resizewindowpixel", f"exact 1080 700,address:{addr}"])
        _run_hyprctl(["dispatch", "centerwindow"])
    else:
        # Switch back to tiled
        _run_hyprctl(["dispatch", "togglefloating", f"address:{addr}"])

    return True
