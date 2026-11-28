"""Unit tests for ALPORA Desktop Widget SDK manager and CLI commands."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

from poly_shell.commands.parser import build_parser
from poly_shell.commands.widget_cmd import handle_widget
from poly_shell.core.state import Paths
from poly_shell.core.widget_manager import (
    WidgetManager,
    WidgetValidationError,
)


class WidgetManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base = Path(self.temp_dir.name)
        self.user_dir = self.base / "user_widgets"
        self.system_dir = self.base / "system_widgets"
        self.user_dir.mkdir(parents=True)
        self.system_dir.mkdir(parents=True)
        self.manager = WidgetManager(user_dir=self.user_dir, system_dirs=[self.system_dir])

    def test_validate_manifest_valid(self):
        raw = {
            "id": "test-widget",
            "name": "Test Widget",
            "version": "1.2.3",
            "entry": "Main.qml",
            "width": 400,
            "height": 250,
            "enabled": True,
            "defaultPosition": {"x": 20, "y": 30},
        }
        normalized = self.manager.validate_manifest(raw)
        self.assertEqual(normalized["id"], "test-widget")
        self.assertEqual(normalized["name"], "Test Widget")
        self.assertEqual(normalized["version"], "1.2.3")
        self.assertEqual(normalized["width"], 400)
        self.assertEqual(normalized["height"], 250)
        self.assertTrue(normalized["enabled"])
        self.assertEqual(normalized["defaultPosition"], {"x": 20, "y": 30})

    def test_validate_manifest_errors(self):
        # Must be dict
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest("not-a-dict")  # type: ignore

        # Missing or bad id
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"name": "No ID"})
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "bad/id!@#", "name": "Bad ID"})

        # Missing or bad name
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "good-id", "name": ""})

        # Bad dimensions
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "w", "name": "W", "width": -10})
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "w", "name": "W", "height": "bad"})  # type: ignore

        # Bad defaultPosition
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "w", "name": "W", "defaultPosition": "bad"})  # type: ignore
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest({"id": "w", "name": "W", "defaultPosition": {"x": "bad"}})

    def test_validate_manifest_with_directory_and_entry_check(self):
        w_dir = self.base / "check_dir"
        w_dir.mkdir()
        (w_dir / "Main.qml").write_text("// entry", encoding="utf-8")

        manifest = {"id": "my-w", "name": "My W", "entry": "Main.qml"}
        res = self.manager.validate_manifest(manifest, widget_dir=w_dir)
        self.assertEqual(res["id"], "my-w")

        # Non-existent entry file
        bad_manifest = {"id": "my-w", "name": "My W", "entry": "Missing.qml"}
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest(bad_manifest, widget_dir=w_dir)

        # Path traversal
        traversal = {"id": "my-w", "name": "My W", "entry": "../escaped.qml"}
        with self.assertRaises(WidgetValidationError):
            self.manager.validate_manifest(traversal, widget_dir=w_dir)

    def test_create_widget(self):
        created_path = self.manager.create_widget("clock-widget", name="My Clock")
        self.assertTrue(created_path.is_dir())
        self.assertTrue((created_path / "widget.json").is_file())
        self.assertTrue((created_path / "Main.qml").is_file())

        with open(created_path / "widget.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["id"], "clock-widget")
        self.assertEqual(data["name"], "My Clock")

        # Duplicate creation raises FileExistsError
        with self.assertRaises(FileExistsError):
            self.manager.create_widget("clock-widget")

        # Invalid id raises WidgetValidationError
        with self.assertRaises(WidgetValidationError):
            self.manager.create_widget("invalid name with spaces!")

    def test_scan_widgets_system_and_user_precedence(self):
        # Create system widget
        sys_w = self.system_dir / "system-widget"
        sys_w.mkdir()
        (sys_w / "widget.json").write_text(
            json.dumps({"id": "system-widget", "name": "System Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (sys_w / "Main.qml").write_text("// sys", encoding="utf-8")

        # Create user widget with different id
        user_w = self.user_dir / "user-widget"
        user_w.mkdir()
        (user_w / "widget.json").write_text(
            json.dumps({"id": "user-widget", "name": "User Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (user_w / "Main.qml").write_text("// user", encoding="utf-8")

        scanned = self.manager.scan_widgets()
        self.assertEqual(len(scanned), 2)
        ids = {w["id"] for w in scanned}
        self.assertEqual(ids, {"system-widget", "user-widget"})

        # Override system widget with same id in user directory
        override_w = self.user_dir / "system-widget"
        override_w.mkdir()
        (override_w / "widget.json").write_text(
            json.dumps({"id": "system-widget", "name": "Overridden System Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (override_w / "Main.qml").write_text("// overridden", encoding="utf-8")

        scanned_override = self.manager.scan_widgets()
        self.assertEqual(len(scanned_override), 2)
        overridden = [w for w in scanned_override if w["id"] == "system-widget"][0]
        self.assertEqual(overridden["name"], "Overridden System Widget")
        self.assertFalse(overridden["is_system"])

    def test_install_widget_from_directory_and_zip(self):
        # Prepare source directory
        src_dir = self.base / "source_widget"
        src_dir.mkdir()
        (src_dir / "widget.json").write_text(
            json.dumps({"id": "src-widget", "name": "Source Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (src_dir / "Main.qml").write_text("// source", encoding="utf-8")

        # Install from dir
        installed = self.manager.install_widget(src_dir)
        self.assertEqual(installed["id"], "src-widget")
        self.assertTrue((self.user_dir / "src-widget" / "widget.json").is_file())

        # Duplicate without force raises FileExistsError
        with self.assertRaises(FileExistsError):
            self.manager.install_widget(src_dir, force=False)

        # Overwrite with force
        installed_forced = self.manager.install_widget(src_dir, force=True)
        self.assertEqual(installed_forced["id"], "src-widget")

        # Install from zip archive
        zip_path = self.base / "packaged_widget.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("widget.json", json.dumps({"id": "zip-widget", "name": "Zip Widget", "entry": "Main.qml"}))
            zf.writestr("Main.qml", "// zip entry")

        installed_zip = self.manager.install_widget(zip_path)
        self.assertEqual(installed_zip["id"], "zip-widget")
        self.assertTrue((self.user_dir / "zip-widget" / "widget.json").is_file())

    def test_remove_widget_and_protect_system_widgets(self):
        # Create user widget and remove it
        self.manager.create_widget("to-remove")
        self.assertTrue((self.user_dir / "to-remove").exists())
        self.assertTrue(self.manager.remove_widget("to-remove"))
        self.assertFalse((self.user_dir / "to-remove").exists())

        # Removing non-existent raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.manager.remove_widget("does-not-exist")

        # Protecting system widget from removal
        sys_w = self.system_dir / "core-widget"
        sys_w.mkdir()
        (sys_w / "widget.json").write_text(
            json.dumps({"id": "core-widget", "name": "Core Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (sys_w / "Main.qml").write_text("// core", encoding="utf-8")

        with self.assertRaises(PermissionError):
            self.manager.remove_widget("core-widget")

    def test_dump_manifests_cache(self):
        self.manager.create_widget("cache-test", name="Cache Test")
        cache_file = self.base / "cache" / "manifests.json"
        self.manager.dump_manifests_cache(cache_file)
        self.assertTrue(cache_file.is_file())
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "cache-test")


class WidgetCliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base = Path(self.temp_dir.name)
        self.paths = Paths(config=self.base / "config", state=self.base / "state", runtime=self.base / "runtime")
        self.paths.config.mkdir(parents=True)
        self.paths.state.mkdir(parents=True)
        self.paths.runtime.mkdir(parents=True)

    def test_cli_create_and_list(self):
        args_create = argparse.Namespace(widget_action="create", id="hello-widget", name="Hello World", dir=None)
        ret = handle_widget(self.paths, args_create)
        self.assertEqual(ret, 0)
        self.assertTrue((self.paths.config / "widgets" / "hello-widget" / "widget.json").is_file())

        # List in text mode
        buf = io.StringIO()
        args_list = argparse.Namespace(widget_action="list", json=False)
        with patch("sys.stdout", buf):
            ret_list = handle_widget(self.paths, args_list)
        self.assertEqual(ret_list, 0)
        self.assertIn("hello-widget", buf.getvalue())
        self.assertIn("Hello World", buf.getvalue())

        # List in JSON mode
        buf_json = io.StringIO()
        args_json = argparse.Namespace(widget_action="list", json=True)
        with patch("sys.stdout", buf_json):
            ret_json = handle_widget(self.paths, args_json)
        self.assertEqual(ret_json, 0)
        parsed = json.loads(buf_json.getvalue())
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], "hello-widget")

    def test_cli_install_and_remove(self):
        # Create a widget in a foreign location
        foreign_dir = self.base / "foreign" / "foreign-widget"
        foreign_dir.mkdir(parents=True)
        (foreign_dir / "widget.json").write_text(
            json.dumps({"id": "foreign-widget", "name": "Foreign Widget", "entry": "Main.qml"}),
            encoding="utf-8",
        )
        (foreign_dir / "Main.qml").write_text("// foreign", encoding="utf-8")

        # Install via CLI
        args_install = argparse.Namespace(widget_action="install", path=str(foreign_dir), force=False)
        ret_inst = handle_widget(self.paths, args_install)
        self.assertEqual(ret_inst, 0)
        self.assertTrue((self.paths.config / "widgets" / "foreign-widget").is_dir())

        # Remove via CLI
        args_remove = argparse.Namespace(widget_action="remove", id="foreign-widget")
        ret_rem = handle_widget(self.paths, args_remove)
        self.assertEqual(ret_rem, 0)
        self.assertFalse((self.paths.config / "widgets" / "foreign-widget").exists())

    def test_cli_errors(self):
        # Missing path for install
        args_inst_bad = argparse.Namespace(widget_action="install", path=None)
        ret = handle_widget(self.paths, args_inst_bad)
        self.assertEqual(ret, 1)

        # Missing id for remove
        args_rem_bad = argparse.Namespace(widget_action="remove", id=None)
        ret = handle_widget(self.paths, args_rem_bad)
        self.assertEqual(ret, 1)

        # Missing id for create
        args_create_bad = argparse.Namespace(widget_action="create", id=None)
        ret = handle_widget(self.paths, args_create_bad)
        self.assertEqual(ret, 1)

        # Unknown action
        args_unknown = argparse.Namespace(widget_action="unknown_action")
        ret = handle_widget(self.paths, args_unknown)
        self.assertEqual(ret, 1)


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser("1.2.0")

    def test_parser_widget_subcommands(self):
        args1 = self.parser.parse_args(["widget", "list", "--json"])
        self.assertEqual(args1.command, "widget")
        self.assertEqual(args1.widget_action, "list")
        self.assertTrue(args1.json)

        args2 = self.parser.parse_args(["widget", "install", "/path/to/pkg.zip", "--force"])
        self.assertEqual(args2.command, "widget")
        self.assertEqual(args2.widget_action, "install")
        self.assertEqual(args2.path, "/path/to/pkg.zip")
        self.assertTrue(args2.force)

        args3 = self.parser.parse_args(["widget", "remove", "clock-card"])
        self.assertEqual(args3.command, "widget")
        self.assertEqual(args3.widget_action, "remove")
        self.assertEqual(args3.id, "clock-card")

        args4 = self.parser.parse_args(["widget", "create", "demo-card", "--name", "Demo Card"])
        self.assertEqual(args4.command, "widget")
        self.assertEqual(args4.widget_action, "create")
        self.assertEqual(args4.id, "demo-card")
        self.assertEqual(args4.name, "Demo Card")


if __name__ == "__main__":
    unittest.main()
