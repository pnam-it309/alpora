"""Tests for BluetoothService discovery, status, pairing, and connection management."""
import unittest
from unittest.mock import MagicMock, patch

from poly_shell.services.bluetooth_service import BluetoothService


class TestBluetoothService(unittest.TestCase):
    """Verify BluetoothService operations and command parsing."""

    @patch("poly_shell.adapters.base.SafeRunner.is_available")
    def test_status_when_unavailable(self, mock_avail):
        mock_avail.return_value = False
        status = BluetoothService.get_status()
        self.assertFalse(status["available"])
        self.assertFalse(status["powered"])

    @patch("poly_shell.adapters.base.SafeRunner.run")
    @patch("poly_shell.adapters.base.SafeRunner.is_available")
    def test_status_when_powered_on(self, mock_avail, mock_run):
        mock_avail.return_value = True
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = """
Controller 00:1A:7D:DA:71:13 (public)
\tName: ALPORA-Host
\tAlias: ALPORA-Host
\tClass: 0x006c010c
\tPowered: yes
\tPowerState: on
\tDiscoverable: yes
\tDiscovering: no
"""
        mock_run.return_value = mock_proc

        status = BluetoothService.get_status()
        self.assertTrue(status["available"])
        self.assertTrue(status["powered"])
        self.assertTrue(status["discoverable"])
        self.assertFalse(status["discovering"])

    @patch("poly_shell.adapters.base.SafeRunner.run")
    @patch("poly_shell.adapters.base.SafeRunner.is_available")
    def test_list_devices(self, mock_avail, mock_run):
        mock_avail.return_value = True
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = """
Device 88:C9:E8:12:34:56 Sony WH-1000XM4
Device 00:1B:66:AA:BB:CC Keychron K2
"""
        mock_run.return_value = mock_proc

        devices = BluetoothService.list_devices()
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["mac"], "88:C9:E8:12:34:56")
        self.assertEqual(devices[0]["name"], "Sony WH-1000XM4")
        self.assertEqual(devices[1]["name"], "Keychron K2")

    @patch("poly_shell.adapters.base.SafeRunner.run")
    @patch("poly_shell.adapters.base.SafeRunner.is_available")
    def test_pair_and_connect(self, mock_avail, mock_run):
        mock_avail.return_value = True
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Pairing successful"
        mock_run.return_value = mock_proc

        pair_res = BluetoothService.pair("88:C9:E8:12:34:56")
        self.assertTrue(pair_res["success"])

        conn_res = BluetoothService.connect("88:C9:E8:12:34:56")
        self.assertTrue(conn_res)

        disconn_res = BluetoothService.disconnect("88:C9:E8:12:34:56")
        self.assertTrue(disconn_res)


if __name__ == "__main__":
    unittest.main()
