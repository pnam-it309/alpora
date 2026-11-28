import unittest
from unittest.mock import patch

from poly_shell.services.window_service import (
    cascade_floating_windows,
    get_active_window,
    get_active_workspace,
    get_clients,
    toggle_floating_smart,
)


class WindowServiceTests(unittest.TestCase):
    @patch("poly_shell.services.window_service._run_hyprctl")
    def test_get_active_workspace(self, mock_hyprctl):
        mock_hyprctl.return_value = '{"id": 3, "name": "3"}'
        ws = get_active_workspace()
        self.assertEqual(ws, 3)

        mock_hyprctl.return_value = "invalid json"
        self.assertEqual(get_active_workspace(), 1)

    @patch("poly_shell.services.window_service._run_hyprctl")
    def test_get_clients(self, mock_hyprctl):
        mock_hyprctl.return_value = '[{"address": "0x123", "floating": true, "workspace": {"id": 1}}]'
        clients = get_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]["address"], "0x123")

    @patch("poly_shell.services.window_service.get_clients")
    @patch("poly_shell.services.window_service._run_hyprctl")
    def test_cascade_floating_windows(self, mock_hyprctl, mock_clients):
        mock_clients.return_value = [
            {"address": "0x1", "floating": True, "workspace": {"id": 1}},
            {"address": "0x2", "floating": True, "workspace": {"id": 1}},
            {"address": "0x3", "floating": False, "workspace": {"id": 1}},
            {"address": "0x4", "floating": True, "workspace": {"id": 2}},
        ]
        count = cascade_floating_windows(workspace_id=1)
        self.assertEqual(count, 2)
        # Verify resize and move commands were dispatched for both windows
        self.assertGreaterEqual(mock_hyprctl.call_count, 4)

    @patch("poly_shell.services.window_service.get_active_window")
    @patch("poly_shell.services.window_service._run_hyprctl")
    def test_toggle_floating_smart(self, mock_hyprctl, mock_active):
        mock_active.return_value = {"address": "0xabc", "floating": False}
        res = toggle_floating_smart()
        self.assertTrue(res)
        # Should call togglefloating, resizewindowpixel, centerwindow
        self.assertEqual(mock_hyprctl.call_count, 3)

    @patch("poly_shell.services.window_service.get_active_window")
    @patch("poly_shell.services.window_service._run_hyprctl")
    def test_toggle_floating_smart_already_floating_or_fullscreen(self, mock_hyprctl, mock_active):
        # Already floating -> tile
        mock_active.return_value = {"address": "0xabc", "floating": True}
        self.assertTrue(toggle_floating_smart())
        self.assertEqual(mock_hyprctl.call_count, 1)

        # Fullscreen -> unfullscreen then float
        mock_hyprctl.reset_mock()
        mock_active.return_value = {"address": "0xabc", "floating": False, "fullscreen": True}
        self.assertTrue(toggle_floating_smart())
        self.assertEqual(mock_hyprctl.call_count, 4)

        # No active window -> fallback
        mock_hyprctl.reset_mock()
        mock_active.return_value = None
        self.assertTrue(toggle_floating_smart())
        self.assertEqual(mock_hyprctl.call_count, 1)


if __name__ == "__main__":
    unittest.main()
