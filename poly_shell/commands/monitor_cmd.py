"""Command handler for multi-monitor configuration, interactive layout and persistence."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from ..adapters.hyprland import HyprlandAdapter
from ..core.state import ConfigError, Paths
from ..services.monitor_service import MonitorService


def handle_monitor(paths: Paths, args: argparse.Namespace) -> int:
    """Handle `poly-shell monitor` subcommands."""
    service = MonitorService(paths)
    action = getattr(args, "action", "list")

    if action == "list":
        monitors = HyprlandAdapter.get_monitors()
        print(json.dumps(monitors, indent=2, ensure_ascii=False))
        return 0

    if action in ("apply", "persist"):
        raw_payload = getattr(args, "payload", "[]")
        try:
            payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
        except ValueError as exc:
            raise ConfigError("Invalid monitor JSON payload") from exc

        result = service.apply_and_persist(payload)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("success") else 1

    raise ConfigError(f"Unknown monitor action: {action}")
