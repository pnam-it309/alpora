"""Unit tests for ALPORA OS Update Center and OTA patch service."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import MagicMock, patch

from poly_shell.commands.parser import build_parser
from poly_shell.commands.update_cmd import UpdateCenterTUI, handle_update
from poly_shell.core.state import Paths
from poly_shell.services.update_service import UpdateService, parse_semver


class UpdateServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.paths = Paths(root / "config", root / "state", root / "runtime")
        self.service = UpdateService(paths=self.paths)

    def test_semver_parsing(self):
        self.assertEqual(parse_semver("v1.0.0"), (1, 0, 0))
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3))
        self.assertTrue(parse_semver("v1.1.0") > parse_semver("v1.0.0"))
        self.assertTrue(parse_semver("2.0.0") > parse_semver("1.9.9"))

    def test_parser_update_flags_and_subcommands(self):
        parser = build_parser("1.0.0")

        args_top_json = parser.parse_args(["update", "--json"])
        self.assertIsNone(args_top_json.update_action)
        self.assertTrue(args_top_json.json)
        self.assertFalse(args_top_json.tui)

        args_top_tui = parser.parse_args(["update", "--tui"])
        self.assertIsNone(args_top_tui.update_action)
        self.assertTrue(args_top_tui.tui)

        args_check_json = parser.parse_args(["update", "check", "--json"])
        self.assertEqual(args_check_json.update_action, "check")
        self.assertTrue(args_check_json.json)

        args_apply = parser.parse_args(["update", "apply", "--branch", "dev", "--hold"])
        self.assertEqual(args_apply.update_action, "apply")
        self.assertEqual(args_apply.branch, "dev")
        self.assertTrue(args_apply.hold)

        args_status_json = parser.parse_args(["update", "status", "--json"])
        self.assertEqual(args_status_json.update_action, "status")
        self.assertTrue(args_status_json.json)

        args_tui = parser.parse_args(["update", "tui", "--branch", "beta", "--auto-apply"])
        self.assertEqual(args_tui.update_action, "tui")
        self.assertEqual(args_tui.branch, "beta")
        self.assertTrue(args_tui.auto_apply)

    @patch("urllib.request.urlopen")
    def test_check_update_with_newer_release(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"""{
            "tag_name": "v1.2.0",
            "name": "ALPORA OS v1.2.0 Release",
            "body": "- Added Game Mode\\n- Added Phone Connect",
            "published_at": "2026-11-03T12:00:00Z",
            "html_url": "https://github.com/pnam-it309/alpora/releases/tag/v1.2.0",
            "assets": [
                {"name": "alpora-archlinux-2026.11.iso", "browser_download_url": "https://example.com/alpora.iso"}
            ]
        }"""
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch.object(self.service, "get_current_version", return_value="1.0.0"):
            res = self.service.check_update(force=True)
            self.assertTrue(res["has_update"])
            self.assertEqual(res["latest_version"], "v1.2.0")
            self.assertEqual(res["iso_download_url"], "https://example.com/alpora.iso")

    @patch("urllib.request.urlopen")
    def test_check_update_up_to_date(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"""{
            "tag_name": "v1.0.0",
            "name": "ALPORA OS v1.0.0",
            "body": "Initial Release"
        }"""
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch.object(self.service, "get_current_version", return_value="1.0.0"):
            res = self.service.check_update(force=True)
            self.assertFalse(res["has_update"])

    @patch("subprocess.run")
    def test_apply_update_git_failure_handling(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="Connection error")
        res = self.service.apply_update()
        self.assertFalse(res["success"])

    @patch.object(UpdateService, "get_current_version", return_value="1.0.0")
    @patch.object(UpdateService, "check_update")
    def test_cli_update_handlers(self, mock_check, _mock_ver):
        mock_check.return_value = {
            "has_update": False,
            "current_version": "1.0.0",
            "latest_version": "1.0.0",
            "release_title": "Up to date",
            "release_notes": "",
            "published_at": "",
            "html_url": "",
            "iso_download_url": None,
        }

        out_check = io.StringIO()
        with redirect_stdout(out_check):
            args_check = MagicMock(update_action="check", json=False)
            self.assertEqual(handle_update(args_check), 0)
        rendered_check = out_check.getvalue()
        self.assertIn("╭", rendered_check)
        self.assertIn("U P D A T E   C E N T E R", rendered_check)
        self.assertIn("Đang ở phiên bản mới nhất", rendered_check)

        out_status = io.StringIO()
        with redirect_stdout(out_status):
            args_status = MagicMock(update_action="status", json=False)
            self.assertEqual(handle_update(args_status), 0)
        self.assertIn("ALPORA OS Version: 1.0.0", out_status.getvalue())

        out_status_json = io.StringIO()
        with redirect_stdout(out_status_json):
            args_status_json = MagicMock(update_action="status", json=True)
            self.assertEqual(handle_update(args_status_json), 0)
        self.assertEqual(json.loads(out_status_json.getvalue()), {"version": "1.0.0"})

    @patch.object(UpdateService, "check_update")
    def test_cli_update_tui_non_interactive(self, mock_check):
        mock_check.return_value = {
            "has_update": True,
            "current_version": "1.0.0",
            "latest_version": "v1.3.0",
            "release_title": "ALPORA v1.3.0",
            "release_notes": "- New TUI Update Center\n- Theme integration",
            "published_at": "2026-11-26T00:00:00Z",
            "html_url": "https://github.com/pnam-it309/alpora/releases/tag/v1.3.0",
            "iso_download_url": "https://example.com/alpora-v1.3.0.iso",
        }

        buf = io.StringIO()
        with patch("sys.stdin.isatty", return_value=False), redirect_stdout(buf):
            args_tui = MagicMock(update_action="tui", branch="main", auto_apply=False, hold=False, json=False)
            self.assertEqual(handle_update(args_tui), 0)

        output = buf.getvalue()
        self.assertIn("╭", output)
        self.assertIn("╰", output)
        self.assertIn("ĐÃ TÌM THẤY BẢN CẬP NHẬT MỚI!", output)
        self.assertIn("New TUI Update Center", output)
        self.assertIn("https://example.com/alpora-v1.3.0.iso", output)

        # Also test update_action=None defaults to TUI
        buf_default = io.StringIO()
        with patch("sys.stdin.isatty", return_value=False), redirect_stdout(buf_default):
            args_none = MagicMock(update_action=None, branch="main", auto_apply=False, hold=False, json=False, tui=True)
            self.assertEqual(handle_update(args_none), 0)
        self.assertIn("U P D A T E   C E N T E R", buf_default.getvalue())

    @patch("subprocess.run")
    @patch.object(UpdateService, "apply_update")
    def test_cli_update_apply_success_and_failure(self, mock_apply, mock_subproc):
        mock_apply.return_value = {
            "success": True,
            "message": "ALPORA updated successfully to latest main commit.",
            "backup_path": "/tmp/alpora-backup",
        }

        buf = io.StringIO()
        with redirect_stdout(buf):
            args_ok = MagicMock(update_action="apply", branch="main", hold=False)
            self.assertEqual(handle_update(args_ok), 0)

        mock_apply.assert_called_once_with(branch="main")
        mock_subproc.assert_called_once_with(["systemctl", "--user", "restart", "poly-shell.service"], check=False)
        out = buf.getvalue()
        self.assertIn("[1/5]", out)
        self.assertIn("[5/5]", out)
        self.assertIn("100%", out)
        self.assertIn("[THÀNH CÔNG]", out)
        self.assertIn("/tmp/alpora-backup", out)

        # Failure path: exit code 1, stderr output, systemctl NOT called
        mock_apply.reset_mock()
        mock_subproc.reset_mock()
        mock_apply.return_value = {"success": False, "error": "Network timeout"}

        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            args_fail = MagicMock(update_action="apply", branch="dev", hold=False)
            self.assertEqual(handle_update(args_fail), 1)

        mock_apply.assert_called_once_with(branch="dev")
        mock_subproc.assert_not_called()
        self.assertIn("[LỖI]", err_buf.getvalue())
        self.assertIn("Network timeout", err_buf.getvalue())

    def test_tui_truecolor_rendering(self):
        tui = UpdateCenterTUI(
            theme_label="Alpine",
            palette={"accent": "#b8cba1", "border": "#59655c", "text": "#edf0e5"},
            color=True,
        )
        rendered = tui.render_check(
            {
                "has_update": False,
                "current_version": "1.0.0",
                "latest_version": "1.0.0",
            }
        )
        self.assertIn("\033[38;2;", rendered)


if __name__ == "__main__":
    unittest.main()
