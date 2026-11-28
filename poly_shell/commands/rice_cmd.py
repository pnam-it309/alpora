"""CLI command handler for .alpora-rice export, import, and inspect."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from ..core.rice_package import export_rice, import_rice, inspect_rice
from ..core.state import Paths


def handle_rice(paths: Paths, args: argparse.Namespace) -> int:
    """Handle `poly-shell rice` subcommands."""
    action = getattr(args, "action", "export") or "export"

    if action == "export":
        out_target = getattr(args, "output", "") or "my-desktop.alpora-rice"
        name = getattr(args, "name", "") or Path(out_target).stem
        author = getattr(args, "author", "") or "ALPORA User"
        description = getattr(args, "desc", "") or "ALPORA Desktop Rice"

        try:
            exported = export_rice(paths, out_target, name=name, author=author, description=description)
            print(f"Successfully exported rice package to: {exported}")
            return 0
        except Exception as exc:
            print(f"Error exporting rice package: {exc}", file=sys.stderr)
            return 1

    if action in ("import", "apply"):
        file_target = getattr(args, "file", None)
        if not file_target:
            print("Error: Specify a rice package file to import.", file=sys.stderr)
            return 1

        apply = not getattr(args, "preview", False)
        try:
            res = import_rice(paths, file_target, apply=apply)
            manifest = res.get("manifest", {})
            if apply:
                print(f"Successfully applied rice package: {manifest.get('name', 'Unknown')}")
                print(f"  Theme: {manifest.get('theme')}")
                print(f"  Wallpaper: {manifest.get('wallpaper_file', 'None')}")
            else:
                print(f"Rice Package Preview: {manifest.get('name', 'Unknown')}")
                print(json.dumps(manifest, indent=2))
            return 0
        except Exception as exc:
            print(f"Error importing rice package: {exc}", file=sys.stderr)
            return 1

    if action == "inspect":
        file_target = getattr(args, "file", None)
        if not file_target:
            print("Error: Specify a rice package file to inspect.", file=sys.stderr)
            return 1

        try:
            manifest = inspect_rice(file_target)
            if getattr(args, "json", False):
                print(json.dumps(manifest, indent=2))
            else:
                print(f"Package: {manifest.get('name', 'Unknown')}")
                print(f"Author: {manifest.get('author', 'Unknown')}")
                print(f"Description: {manifest.get('description', '')}")
                print(f"Theme: {manifest.get('theme', 'default')}")
                print(f"Has Wallpaper: {manifest.get('has_wallpaper', False)}")
                print(f"Assets: {', '.join(manifest.get('files', []))}")
            return 0
        except Exception as exc:
            print(f"Error inspecting rice package: {exc}", file=sys.stderr)
            return 1

    print(f"Unknown rice action: {action}", file=sys.stderr)
    return 1
