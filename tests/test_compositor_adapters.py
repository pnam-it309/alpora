"""Tests for multi-compositor adapters (Hyprland and Generic wlroots)."""
import os
import unittest
from unittest.mock import MagicMock, patch

from poly_shell.adapters import (
    BaseCompositorAdapter,
    GenericWlrootsAdapter,
    HyprlandAdapter,
    get_compositor_adapter,
)


class TestCompositorAdapters(unittest.TestCase):
    """Verify compositor adapter detection, queries, and dispatch actions."""

    def test_hyprland_adapter_interface(self):
        self.assertTrue(issubclass(HyprlandAdapter, BaseCompositorAdapter))

    @patch("poly_shell.adapters.base.SafeRunner.run")
    def test_hyprland_adapter_get_monitors(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = '[{"id": 0, "name": "eDP-1", "width": 1920, "height": 1080}]'
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        monitors = HyprlandAdapter.get_monitors()
        self.assertEqual(len(monitors), 1)
        self.assertEqual(monitors[0]["name"], "eDP-1")

    @patch("poly_shell.adapters.base.SafeRunner.run")
    def test_generic_wlroots_get_monitors(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = '[{"id": 1, "name": "DP-1", "current_mode": {"width": 2560, "height": 1440, "refresh": 144000}, "focused": true}]'
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        with patch("poly_shell.adapters.base.SafeRunner.is_available", return_value=True):
            monitors = GenericWlrootsAdapter.get_monitors()
            self.assertEqual(len(monitors), 1)
            self.assertEqual(monitors[0]["name"], "DP-1")
            self.assertEqual(monitors[0]["width"], 2560)
            self.assertEqual(monitors[0]["refreshRate"], 144.0)

    @patch("poly_shell.adapters.base.SafeRunner.run")
    def test_generic_wlroots_get_workspaces(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = '[{"num": 2, "name": "2", "output": "DP-1", "focused": true, "urgent": false}]'
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        with patch("poly_shell.adapters.base.SafeRunner.is_available", return_value=True):
            workspaces = GenericWlrootsAdapter.get_workspaces()
            self.assertEqual(len(workspaces), 1)
            self.assertEqual(workspaces[0]["id"], 2)
            self.assertTrue(workspaces[0]["active"])

    @patch("poly_shell.adapters.base.SafeRunner.run")
    def test_generic_wlroots_get_clients(self, mock_run):
        tree = {
            "type": "root",
            "nodes": [
                {
                    "type": "output",
                    "nodes": [
                        {
                            "type": "con",
                            "name": "Firefox",
                            "app_id": "firefox",
                            "id": 42,
                            "workspace_id": 1,
                            "focused": True,
                        }
                    ]
                }
            ]
        }
        import json
        mock_proc = MagicMock()
        mock_proc.stdout = json.dumps(tree)
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        with patch("poly_shell.adapters.base.SafeRunner.is_available", return_value=True):
            clients = GenericWlrootsAdapter.get_clients()
            self.assertEqual(len(clients), 1)
            self.assertEqual(clients[0]["title"], "Firefox")
            self.assertEqual(clients[0]["class_name"], "firefox")

    def test_get_compositor_adapter_resolution(self):
        with patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "Hyprland"}):
            adapter = get_compositor_adapter()
            self.assertEqual(adapter, HyprlandAdapter)

        with patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "sway"}), \
             patch("poly_shell.adapters.hyprland.HyprlandAdapter.is_available", return_value=False), \
             patch("poly_shell.adapters.generic_wlroots.GenericWlrootsAdapter.is_available", return_value=True):
            adapter = get_compositor_adapter()
            self.assertEqual(adapter, GenericWlrootsAdapter)


if __name__ == "__main__":
    unittest.main()
