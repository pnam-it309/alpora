"""Unit tests for poly-shell service command, parser, and systemd unit config."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from poly_shell.commands.parser import build_parser
from poly_shell.commands.service_cmd import handle_service, SERVICE_UNIT, VALID_ACTIONS
from poly_shell.core.state import Paths, ROOT
from poly_shell.system.integration import unit_text


class ServiceCmdTests(unittest.TestCase):
    def setUp(self):
        self.paths = MagicMock(spec=Paths)

    @patch("subprocess.run")
    def test_service_status(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        args = argparse.Namespace(action="status")
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 0)
        mock_run.assert_called_once_with(["systemctl", "--user", "status", "--no-pager", SERVICE_UNIT])

    @patch("subprocess.run")
    def test_service_lifecycle_actions(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        for act in ("start", "stop", "restart", "enable", "disable"):
            with self.subTest(action=act):
                mock_run.reset_mock()
                args = argparse.Namespace(action=act)
                ret = handle_service(self.paths, args)
                self.assertEqual(ret, 0)
                mock_run.assert_called_once_with(["systemctl", "--user", act, SERVICE_UNIT])

    @patch("subprocess.run")
    def test_service_logs_default(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        args = argparse.Namespace(action="logs")
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 0)
        mock_run.assert_called_once_with(
            ["journalctl", "--user", "-u", SERVICE_UNIT, "-n", "80", "--no-pager"]
        )

    @patch("subprocess.run")
    def test_service_logs_custom_options(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        args = argparse.Namespace(action="logs", lines=50, follow=True)
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 0)
        mock_run.assert_called_once_with(
            ["journalctl", "--user", "-u", SERVICE_UNIT, "-n", "50", "-f"]
        )

    @patch("subprocess.run")
    def test_service_custom_unit(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        args = argparse.Namespace(action="restart", unit="custom.service")
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 0)
        mock_run.assert_called_once_with(["systemctl", "--user", "restart", "custom.service"])

    def test_service_unknown_action(self):
        args = argparse.Namespace(action="unknown_action")
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 1)

    @patch("subprocess.run", side_effect=OSError("systemctl not found"))
    def test_service_subprocess_error(self, mock_run):
        args = argparse.Namespace(action="status")
        ret = handle_service(self.paths, args)
        self.assertEqual(ret, 1)

    def test_parser_service_command(self):
        parser = build_parser("1.0.0")

        # Default action should be "status"
        args = parser.parse_args(["service"])
        self.assertEqual(args.command, "service")
        self.assertEqual(args.action, "status")
        self.assertEqual(args.lines, 80)
        self.assertFalse(args.follow)

        # All supported actions
        for act in VALID_ACTIONS:
            args = parser.parse_args(["service", act])
            self.assertEqual(args.command, "service")
            self.assertEqual(args.action, act)

        # Flags for logs
        args = parser.parse_args(["service", "logs", "-n", "100", "-f"])
        self.assertEqual(args.action, "logs")
        self.assertEqual(args.lines, 100)
        self.assertTrue(args.follow)

    @patch("poly_shell.commands.handle_service")
    def test_cli_dispatch_service(self, mock_handle):
        mock_handle.return_value = 0
        from poly_shell.cli import main
        ret = main(["service", "restart"])
        self.assertEqual(ret, 0)
        self.assertTrue(mock_handle.called)

    def test_unit_text_systemd_properties(self):
        text = unit_text(Path("/usr/bin/poly-shell"))
        self.assertIn("Restart=on-failure", text)
        self.assertIn("RestartSec=2", text)
        self.assertIn("StartLimitBurst=3", text)

    def test_dotfiles_service_systemd_properties(self):
        service_file = ROOT / "dotfiles/systemd/.config/systemd/user/poly-shell.service"
        self.assertTrue(service_file.exists(), f"Missing {service_file}")
        content = service_file.read_text(encoding="utf-8")
        self.assertIn("Restart=on-failure", content)
        self.assertIn("RestartSec=2", content)
        self.assertIn("StartLimitBurst=3", content)


if __name__ == "__main__":
    unittest.main()
