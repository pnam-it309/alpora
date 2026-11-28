"""Widget SDK manager for discovering, validating, and managing ALPORA desktop widgets."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple
import zipfile

WIDGET_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\.\-]+$")
DEFAULT_USER_WIDGETS_DIR = Path.home() / ".config" / "poly-shell" / "widgets"
DEFAULT_SYSTEM_WIDGETS_DIRS = [
    Path("/usr/share/poly-shell/widgets"),
    Path("/usr/local/share/poly-shell/widgets"),
]


class WidgetValidationError(ValueError):
    """Raised when widget manifest or structure fails validation."""


class WidgetManager:
    """Manages ALPORA external widget scanning, validation, installation and scaffolding."""

    def __init__(
        self,
        user_dir: Optional[Path] = None,
        system_dirs: Optional[List[Path]] = None,
    ):
        if user_dir is not None:
            self.user_dir = Path(user_dir)
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            base = Path(xdg_config) if xdg_config else (Path.home() / ".config")
            self.user_dir = base / "poly-shell" / "widgets"

        if system_dirs is not None:
            self.system_dirs = [Path(d) for d in system_dirs]
        else:
            self.system_dirs = list(DEFAULT_SYSTEM_WIDGETS_DIRS)

    def validate_manifest(
        self, manifest: Dict[str, Any], widget_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Validate widget manifest dictionary and return normalized manifest.

        Raises WidgetValidationError if invalid.
        """
        if not isinstance(manifest, dict):
            raise WidgetValidationError("Manifest must be a JSON object")

        # Validate 'id'
        widget_id = manifest.get("id")
        if not widget_id or not isinstance(widget_id, str):
            raise WidgetValidationError("Widget manifest must have a non-empty string 'id'")
        if not WIDGET_ID_PATTERN.match(widget_id):
            raise WidgetValidationError(
                f"Widget id '{widget_id}' contains invalid characters (must match {WIDGET_ID_PATTERN.pattern})"
            )

        # Validate 'name'
        name = manifest.get("name")
        if not name or not isinstance(name, str):
            raise WidgetValidationError("Widget manifest must have a non-empty string 'name'")

        # Validate 'version'
        version = manifest.get("version", "1.0.0")
        if not isinstance(version, str):
            raise WidgetValidationError("Widget version must be a string")

        # Validate 'entry'
        entry = manifest.get("entry", "Main.qml")
        if not entry or not isinstance(entry, str):
            raise WidgetValidationError("Widget entry must be a non-empty string")

        if widget_dir is not None:
            entry_file = (Path(widget_dir) / entry).resolve()
            try:
                # Ensure entry file doesn't escape widget_dir
                entry_file.relative_to(Path(widget_dir).resolve())
            except ValueError:
                raise WidgetValidationError("Widget entry points outside the widget directory")
            if not entry_file.is_file():
                raise WidgetValidationError(f"Entry file '{entry}' does not exist in widget directory")

        # Validate dimensions
        width = manifest.get("width", 300)
        if not isinstance(width, (int, float)) or width <= 0:
            raise WidgetValidationError("Widget width must be a positive number")

        height = manifest.get("height", 200)
        if not isinstance(height, (int, float)) or height <= 0:
            raise WidgetValidationError("Widget height must be a positive number")

        # Validate enabled
        enabled = manifest.get("enabled", True)
        if not isinstance(enabled, bool):
            raise WidgetValidationError("Widget enabled must be a boolean")

        # Validate defaultPosition
        default_pos = manifest.get("defaultPosition")
        if default_pos is not None:
            if not isinstance(default_pos, dict):
                raise WidgetValidationError("defaultPosition must be an object with 'x' and 'y'")
            if "x" in default_pos and not isinstance(default_pos["x"], (int, float)):
                raise WidgetValidationError("defaultPosition.x must be a number")
            if "y" in default_pos and not isinstance(default_pos["y"], (int, float)):
                raise WidgetValidationError("defaultPosition.y must be a number")

        normalized = {
            "id": widget_id,
            "name": name,
            "version": version,
            "entry": entry,
            "description": str(manifest.get("description", "")),
            "author": str(manifest.get("author", "")),
            "license": str(manifest.get("license", "")),
            "enabled": enabled,
            "width": int(width),
            "height": int(height),
            "defaultPosition": default_pos or {"x": 50, "y": 50},
        }
        return normalized

    def scan_widgets(self, include_invalid: bool = False) -> List[Dict[str, Any]]:
        """Scan system and user widget directories for installed widgets.

        User widgets override system widgets with the same id.
        """
        widgets_by_id: Dict[str, Dict[str, Any]] = {}

        # 1. System widgets
        for sys_dir in self.system_dirs:
            if not sys_dir.is_dir():
                continue
            for item in sorted(sys_dir.iterdir()):
                if item.is_dir():
                    info = self._load_widget_from_dir(item, is_system=True)
                    if info:
                        if info.get("valid") or include_invalid:
                            widgets_by_id[info["id"]] = info

        # 2. User widgets (override system widgets)
        if self.user_dir.is_dir():
            for item in sorted(self.user_dir.iterdir()):
                if item.is_dir():
                    info = self._load_widget_from_dir(item, is_system=False)
                    if info:
                        if info.get("valid") or include_invalid:
                            widgets_by_id[info["id"]] = info

        return sorted(widgets_by_id.values(), key=lambda w: w["name"].lower())

    def _load_widget_from_dir(self, directory: Path, is_system: bool) -> Optional[Dict[str, Any]]:
        manifest_file = directory / "widget.json"
        if not manifest_file.is_file():
            return None

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            data = self.validate_manifest(raw, widget_dir=directory)
            data["path"] = str(directory.resolve())
            data["entry_path"] = str((directory / data["entry"]).resolve())
            data["is_system"] = is_system
            data["valid"] = True
            return data
        except Exception as exc:
            widget_id = directory.name
            return {
                "id": widget_id,
                "name": widget_id,
                "version": "unknown",
                "entry": "Main.qml",
                "path": str(directory.resolve()),
                "entry_path": "",
                "is_system": is_system,
                "valid": False,
                "error": str(exc),
            }

    def get_widget(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get widget info by id."""
        for widget in self.scan_widgets(include_invalid=True):
            if widget["id"] == widget_id:
                return widget
        return None

    def create_widget(
        self, widget_id: str, name: str = "", target_dir: Optional[Path] = None
    ) -> Path:
        """Scaffold a new widget directory with valid widget.json and template Main.qml."""
        if not WIDGET_ID_PATTERN.match(widget_id):
            raise WidgetValidationError(f"Invalid widget id '{widget_id}'")

        dest_dir = (target_dir or self.user_dir) / widget_id
        if dest_dir.exists():
            raise FileExistsError(f"Widget directory already exists: {dest_dir}")

        dest_dir.mkdir(parents=True, exist_ok=True)
        display_name = name.strip() or widget_id.replace("-", " ").replace("_", " ").title()

        manifest = {
            "id": widget_id,
            "name": display_name,
            "version": "1.0.0",
            "description": f"Custom {display_name} desktop widget",
            "author": os.environ.get("USER", "Developer"),
            "entry": "Main.qml",
            "enabled": True,
            "width": 320,
            "height": 180,
            "defaultPosition": {"x": 50, "y": 50},
        }
        with open(dest_dir / "widget.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        main_qml = f"""pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts

Rectangle {{
    id: root
    implicitWidth: 320
    implicitHeight: 180
    radius: (typeof Session !== "undefined" && Session.visual) ? Session.visual.widgetRadius : 16
    color: (typeof Glass !== "undefined") ? Glass.materialTop(0.85) : "#202020"
    border.width: (typeof Session !== "undefined" && Session.visual) ? Session.visual.widgetBorder : 1
    border.color: (typeof Glass !== "undefined" && typeof Session !== "undefined") ? Glass.tint(Session.foreground, 0.22) : "#404040"

    ColumnLayout {{
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        RowLayout {{
            Layout.fillWidth: true
            spacing: 8

            Text {{
                text: "{display_name}"
                color: (typeof Session !== "undefined") ? Session.foreground : "#ffffff"
                font.family: (typeof Session !== "undefined") ? Session.fontFamily : "sans-serif"
                font.pixelSize: 14
                font.bold: true
                Layout.fillWidth: true
                elide: Text.ElideRight
            }}

            Text {{
                text: "v1.0"
                color: (typeof Session !== "undefined") ? Session.muted : "#888888"
                font.family: (typeof Session !== "undefined") ? Session.fontFamily : "sans-serif"
                font.pixelSize: 10
            }}
        }}

        Rectangle {{
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: (typeof Glass !== "undefined" && typeof Session !== "undefined") ? Glass.tint(Session.foreground, 0.1) : "#303030"
        }}

        Text {{
            text: "ALPORA Desktop Widget SDK"
            color: (typeof Session !== "undefined") ? Session.muted : "#aaaaaa"
            font.family: (typeof Session !== "undefined") ? Session.fontFamily : "sans-serif"
            font.pixelSize: 12
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }}

        Item {{ Layout.fillHeight: true }}
    }}
}}
"""
        with open(dest_dir / "Main.qml", "w", encoding="utf-8") as f:
            f.write(main_qml)

        return dest_dir

    def install_widget(
        self, source: Path | str, target_dir: Optional[Path] = None, force: bool = False
    ) -> Dict[str, Any]:
        """Install a widget from directory or zip archive into the user widgets directory."""
        source_path = Path(source).resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Source widget path does not exist: {source_path}")

        install_base = target_dir or self.user_dir
        install_base.mkdir(parents=True, exist_ok=True)

        if source_path.is_file() and zipfile.is_zipfile(source_path):
            return self._install_from_zip(source_path, install_base, force)
        elif source_path.is_dir():
            return self._install_from_dir(source_path, install_base, force)
        else:
            raise WidgetValidationError(f"Source must be a widget directory or zip archive: {source_path}")

    def _install_from_dir(self, source_dir: Path, install_base: Path, force: bool) -> Dict[str, Any]:
        manifest_file = source_dir / "widget.json"
        if not manifest_file.is_file():
            raise WidgetValidationError(f"Missing widget.json in {source_dir}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        manifest = self.validate_manifest(raw, widget_dir=source_dir)

        dest = install_base / manifest["id"]
        if dest.exists():
            if not force:
                raise FileExistsError(f"Widget '{manifest['id']}' already exists at {dest}. Use force=True to overwrite.")
            shutil.rmtree(dest)

        shutil.copytree(source_dir, dest)
        return self.validate_manifest(manifest, widget_dir=dest) | {
            "path": str(dest.resolve()),
            "entry_path": str((dest / manifest["entry"]).resolve()),
            "is_system": False,
            "valid": True,
        }

    def _install_from_zip(self, zip_path: Path, install_base: Path, force: bool) -> Dict[str, Any]:
        temp_dir = install_base / f".tmp_install_{os.getpid()}_{zip_path.stem}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(temp_dir)

            # Check if contents are nested under a single directory
            contents = list(temp_dir.iterdir())
            candidate_dir = temp_dir
            if len(contents) == 1 and contents[0].is_dir():
                candidate_dir = contents[0]

            return self._install_from_dir(candidate_dir, install_base, force)
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def remove_widget(self, widget_id: str, target_dir: Optional[Path] = None) -> bool:
        """Remove an installed user widget by id."""
        user_widgets_dir = target_dir or self.user_dir
        dest = user_widgets_dir / widget_id
        if not dest.exists():
            # Check if it's a system widget
            for sys_dir in self.system_dirs:
                if (sys_dir / widget_id).exists():
                    raise PermissionError(f"Cannot remove system widget '{widget_id}'")
            raise FileNotFoundError(f"Widget '{widget_id}' not found in user directory")

        if not dest.is_dir():
            raise WidgetValidationError(f"Target path {dest} is not a directory")

        shutil.rmtree(dest)
        return True

    def dump_manifests_cache(self, output_path: Path) -> None:
        """Write current valid manifests to a JSON cache file."""
        widgets = [w for w in self.scan_widgets() if w.get("valid")]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = output_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(widgets, f, indent=2)
        temp_path.replace(output_path)
