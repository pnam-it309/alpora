"""Tests for 1-click .alpora-rice packaging and CLI."""
import argparse
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from poly_shell.commands.rice_cmd import handle_rice
from poly_shell.core.rice_package import export_rice, import_rice, inspect_rice
from poly_shell.core.state import Paths


class TestRicePackage(unittest.TestCase):
    """Test rice bundle export, inspection, and application."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.paths = Paths(
            self.root / "config",
            self.root / "state",
            self.root / "runtime",
        )
        self.paths.config.mkdir(parents=True, exist_ok=True)
        self.paths.state.mkdir(parents=True, exist_ok=True)
        self.paths.runtime.mkdir(parents=True, exist_ok=True)

        # Seed theme and wallpaper
        (self.paths.config / "theme.json").write_text(json.dumps({"theme": "nord"}), encoding="utf-8")
        fake_wp = self.root / "sample-wallpaper.png"
        fake_wp.write_bytes(b"FAKE_PNG_BYTES")
        (self.paths.state / "wallpaper.json").write_text(json.dumps({"path": str(fake_wp)}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_and_inspect_rice(self):
        out_file = self.root / "nord-rice.alpora-rice"
        exported = export_rice(
            self.paths,
            out_file,
            name="Nord Frost",
            author="TestAuthor",
            description="Clean arctic theme",
        )
        self.assertTrue(exported.exists())
        self.assertTrue(exported.is_file())

        manifest = inspect_rice(exported)
        self.assertEqual(manifest["name"], "Nord Frost")
        self.assertEqual(manifest["author"], "TestAuthor")
        self.assertEqual(manifest["theme"], "nord")
        self.assertTrue(manifest["has_wallpaper"])
        self.assertIn("theme.json", manifest["files"])
        self.assertGreater(manifest["archive_size_bytes"], 0)

    def test_import_rice_preview_and_apply(self):
        out_file = self.root / "test-rice.alpora-rice"
        export_rice(self.paths, out_file, name="Preview Rice")

        # Create new target environment
        target_tmp = tempfile.TemporaryDirectory()
        try:
            target_root = Path(target_tmp.name)
            target_paths = Paths(
                target_root / "config",
                target_root / "state",
                target_root / "runtime",
            )

            # Preview
            preview_res = import_rice(target_paths, out_file, apply=False)
            self.assertEqual(preview_res["status"], "preview")
            self.assertFalse((target_paths.config / "theme.json").exists())

            # Apply
            apply_res = import_rice(target_paths, out_file, apply=True)
            self.assertEqual(apply_res["status"], "applied")
            self.assertTrue((target_paths.config / "theme.json").exists())
            self.assertTrue((target_paths.state / "wallpaper.json").exists())
        finally:
            target_tmp.cleanup()

    def test_handle_rice_cli(self):
        out_file = self.root / "cli-rice.alpora-rice"

        # Test CLI export
        args_export = argparse.Namespace(
            action="export",
            output=str(out_file),
            name="CLI Rice",
            author="CLI Tester",
            desc="CLI Description",
        )
        code = handle_rice(self.paths, args_export)
        self.assertEqual(code, 0)
        self.assertTrue(out_file.exists())

        # Test CLI inspect
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            args_inspect = argparse.Namespace(
                action="inspect",
                file=str(out_file),
                json=True,
            )
            code = handle_rice(self.paths, args_inspect)
            self.assertEqual(code, 0)
            data = json.loads(fake_out.getvalue())
            self.assertEqual(data["name"], "CLI Rice")

        # Test CLI import preview
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            args_import = argparse.Namespace(
                action="import",
                file=str(out_file),
                preview=True,
            )
            code = handle_rice(self.paths, args_import)
            self.assertEqual(code, 0)
            self.assertIn("Rice Package Preview", fake_out.getvalue())


if __name__ == "__main__":
    unittest.main()
