"""1-Click Rice package creation, inspection, and application (.alpora-rice)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tarfile
import time
from typing import Any, Dict

from .state import Paths

RICE_SCHEMA_VERSION = 1


def export_rice(
    paths: Paths,
    output_path: Path | str,
    name: str = "custom-rice",
    author: str = "ALPORA User",
    description: str = "ALPORA Desktop Rice Package",
) -> Path:
    """Bundle active theme, wallpaper, and configuration into an .alpora-rice archive."""
    out = Path(output_path)
    if not out.name.endswith(".alpora-rice") and not out.name.endswith(".tar.gz"):
        out = out.with_suffix(".alpora-rice")

    out.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = paths.runtime / f"rice-export-{int(time.time() * 1000)}" if hasattr(paths, "runtime") and paths.runtime else Path("/tmp") / f"rice-export-{int(time.time())}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        manifest: Dict[str, Any] = {
            "schemaVersion": RICE_SCHEMA_VERSION,
            "name": name,
            "author": author,
            "description": description,
            "timestamp": int(time.time()),
            "has_wallpaper": False,
            "theme": "alpine",
            "files": [],
        }

        # Check theme setting
        theme_file = paths.config / "theme.json" if hasattr(paths, "config") else None
        if theme_file and theme_file.exists():
            try:
                theme_data = json.loads(theme_file.read_text(encoding="utf-8"))
                manifest["theme"] = theme_data.get("theme", "alpine")
                shutil.copy2(theme_file, temp_dir / "theme.json")
                manifest["files"].append("theme.json")
            except (json.JSONDecodeError, OSError):
                pass

        # Check wallpaper setting
        wallpaper_file = paths.state / "wallpaper.json" if hasattr(paths, "state") else None
        if wallpaper_file and wallpaper_file.exists():
            try:
                wp_data = json.loads(wallpaper_file.read_text(encoding="utf-8"))
                current_wp = Path(wp_data.get("path", ""))
                if current_wp.exists() and current_wp.is_file():
                    target_wp = temp_dir / f"wallpaper{current_wp.suffix}"
                    shutil.copy2(current_wp, target_wp)
                    manifest["has_wallpaper"] = True
                    manifest["wallpaper_file"] = target_wp.name
                    manifest["files"].append(target_wp.name)
            except (json.JSONDecodeError, OSError):
                pass

        # Write manifest
        (temp_dir / "rice.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        # Create tarball
        with tarfile.open(out, "w:gz") as tar:
            for item in temp_dir.iterdir():
                tar.add(item, arcname=item.name)

        return out
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def inspect_rice(archive_path: Path | str) -> Dict[str, Any]:
    """Inspect and return manifest data of an .alpora-rice bundle."""
    archive = Path(archive_path)
    if not archive.exists():
        raise FileNotFoundError(f"Rice archive not found: {archive}")

    with tarfile.open(archive, "r:gz") as tar:
        try:
            member = tar.getmember("rice.json")
        except KeyError:
            raise ValueError("Corrupt archive: missing rice.json manifest")

        f = tar.extractfile(member)
        if not f:
            raise ValueError("Unable to read rice.json from archive")
        manifest = json.loads(f.read().decode("utf-8"))
        manifest["archive_size_bytes"] = archive.stat().st_size
        return manifest


def import_rice(paths: Paths, archive_path: Path | str, apply: bool = True) -> Dict[str, Any]:
    """Extract and optionally apply a rice archive."""
    manifest = inspect_rice(archive_path)
    archive = Path(archive_path)

    if not apply:
        return {"status": "preview", "manifest": manifest}

    paths.config.mkdir(parents=True, exist_ok=True)
    paths.state.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive, "r:gz") as tar:
        # Extract theme
        try:
            theme_member = tar.getmember("theme.json")
            f = tar.extractfile(theme_member)
            if f:
                (paths.config / "theme.json").write_bytes(f.read())
        except KeyError:
            pass

        # Extract wallpaper
        wp_name = manifest.get("wallpaper_file")
        if wp_name:
            try:
                wp_member = tar.getmember(wp_name)
                f = tar.extractfile(wp_member)
                if f:
                    wp_dir = paths.state / "wallpapers"
                    wp_dir.mkdir(parents=True, exist_ok=True)
                    dest_wp = wp_dir / wp_name
                    dest_wp.write_bytes(f.read())
                    # Update state
                    (paths.state / "wallpaper.json").write_text(
                        json.dumps({"path": str(dest_wp)}), encoding="utf-8"
                    )
            except KeyError:
                pass

    return {"status": "applied", "manifest": manifest}
