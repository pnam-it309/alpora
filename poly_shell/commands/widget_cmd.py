"""CLI command handler for ALPORA Desktop Widget SDK."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from ..core.state import Paths
from ..core.widget_manager import WidgetManager, WidgetValidationError


def handle_widget(paths: Paths, args: argparse.Namespace) -> int:
    """Handle `poly-shell widget [list|install|remove|create]` CLI commands."""
    action = getattr(args, "widget_action", None) or getattr(args, "action", "list") or "list"
    manager = WidgetManager(user_dir=paths.config / "widgets")

    if action == "list":
        widgets = manager.scan_widgets(include_invalid=False)
        as_json = getattr(args, "json", False)
        if as_json:
            print(json.dumps(widgets, indent=2, ensure_ascii=False))
            return 0

        if not widgets:
            print("No desktop widgets installed.")
            return 0

        print(f"Installed Desktop Widgets ({len(widgets)}):")
        for w in widgets:
            scope = "system" if w.get("is_system") else "user"
            status = "enabled" if w.get("enabled", True) else "disabled"
            ver = w.get("version", "1.0.0")
            print(f"  • {w['id']} (v{ver}) [{scope}, {status}] — {w['name']}")
            if w.get("description"):
                print(f"      {w['description']}")
            print(f"      Path: {w.get('path', '')}")
        return 0

    if action == "install":
        target = getattr(args, "path", None)
        if not target:
            print("Error: path to widget directory or .zip archive is required", file=sys.stderr)
            return 1

        force = getattr(args, "force", False)
        try:
            info = manager.install_widget(target, force=force)
            print(f"Successfully installed widget '{info['id']}' to {info['path']}")
            return 0
        except (WidgetValidationError, FileNotFoundError, FileExistsError, OSError) as exc:
            print(f"Failed to install widget: {exc}", file=sys.stderr)
            return 1

    if action == "remove":
        widget_id = getattr(args, "id", None)
        if not widget_id:
            print("Error: widget id is required for removal", file=sys.stderr)
            return 1

        try:
            manager.remove_widget(widget_id)
            print(f"Successfully removed widget '{widget_id}'")
            return 0
        except (WidgetValidationError, FileNotFoundError, PermissionError, OSError) as exc:
            print(f"Failed to remove widget: {exc}", file=sys.stderr)
            return 1

    if action == "create":
        widget_id = getattr(args, "id", None)
        if not widget_id:
            print("Error: widget id is required for creation", file=sys.stderr)
            return 1

        name = getattr(args, "name", "") or ""
        target_dir = getattr(args, "dir", None)
        target_path = Path(target_dir) if target_dir else None

        try:
            created_dir = manager.create_widget(widget_id, name=name, target_dir=target_path)
            print(f"Created new widget scaffold at {created_dir}")
            return 0
        except (WidgetValidationError, FileExistsError, OSError) as exc:
            print(f"Failed to create widget: {exc}", file=sys.stderr)
            return 1

    print(f"Unknown widget action: '{action}'. Expected list, install, remove, or create.", file=sys.stderr)
    return 1
