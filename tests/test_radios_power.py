from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from poly_shell.radios_power import power_status, radio_status, radios, restore, set_airplane, set_profile
from poly_shell.state import ConfigError, Paths


class RadioSystem:
    def __init__(self, bluetooth=False):
        self.devices = [{"id": "0", "type": "wlan", "name": "wifi", "soft": False, "hard": False},
                        {"id": "1", "type": "bluetooth", "name": "hci0", "soft": not bluetooth, "hard": False}]
        self.nm = {"wifi": True, "wwan": True}
        self.bluetooth = bluetooth
        self.calls = []
        self.fail_block = False
        self.fail_restore = False

    def run(self, args, **_):
        self.calls.append(args)
        output = ""
        if args[:2] == ["nmcli", "-t"]:
            output = ":".join("enabled" if self.nm[key] else "disabled" for key in ("wifi", "wwan"))
        elif args[:2] == ["nmcli", "radio"]:
            kinds = ("wifi", "wwan") if args[2] == "all" else (args[2],)
            for kind in kinds: self.nm[kind] = args[3] == "on"
        elif args[0] == "rfkill":
            if args[2] == "all":
                for item in self.devices: item["soft"] = args[1] == "block"
                self.bluetooth = False
                if self.fail_block: raise ConfigError("radio write failed")
            else:
                if self.fail_restore: raise ConfigError("restore failed")
                for item in self.devices:
                    if item["id"] == args[2]: item["soft"] = args[1] == "block"
        elif args[-1] == "show": output = "Powered: yes" if self.bluetooth else "Powered: no"
        elif args[-2:] == ["power", "on"]: self.bluetooth = True
        return SimpleNamespace(returncode=0, stdout=output, stderr="")


class RadioPowerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name); self.paths = Paths(root / "config", root / "state", root / "runtime")
        self.system = RadioSystem()
        patcher = patch("poly_shell.radios_power.radios", side_effect=lambda: deepcopy(self.system.devices))
        patcher.start(); self.addCleanup(patcher.stop)
        patcher = patch("poly_shell.radios_power.shutil.which", side_effect=lambda name: name)
        patcher.start(); self.addCleanup(patcher.stop)

    def test_roundtrip_preserves_wifi_on_bluetooth_off(self):
        devices = deepcopy(self.system.devices); nm = deepcopy(self.system.nm)
        set_airplane(self.paths, "on", self.system.run)
        self.assertTrue(radio_status()["airplane"])
        self.assertTrue((self.paths.state / "airplane-restore.json").exists())
        set_airplane(self.paths, "off", self.system.run)
        self.assertEqual(self.system.devices, devices)
        self.assertEqual(self.system.nm, nm)
        self.assertFalse(self.system.bluetooth)
        self.assertFalse((self.paths.state / "airplane-restore.json").exists())

    def test_bluetooth_power_is_restored_only_when_previously_on(self):
        self.system = RadioSystem(bluetooth=True)
        set_airplane(self.paths, "on", self.system.run)
        set_airplane(self.paths, "off", self.system.run)
        self.assertTrue(self.system.bluetooth)

    def test_partial_failure_rolls_back_and_failed_recovery_keeps_snapshot(self):
        original = deepcopy(self.system.devices)
        self.system.fail_block = True
        with self.assertRaises(ConfigError): set_airplane(self.paths, "on", self.system.run)
        self.assertEqual(self.system.devices, original)
        self.assertFalse((self.paths.state / "airplane-restore.json").exists())
        self.system.fail_restore = True
        with self.assertRaises(ConfigError): set_airplane(self.paths, "on", self.system.run)
        self.assertTrue((self.paths.state / "airplane-restore.json").exists())
        self.system.fail_restore = False
        set_airplane(self.paths, "off", self.system.run)
        self.assertEqual(self.system.devices, original)

    def test_invalid_and_repeated_off_do_not_change_hardware(self):
        with self.assertRaises(ConfigError): set_airplane(self.paths, "toggle", self.system.run)
        set_airplane(self.paths, "off", self.system.run)
        self.assertEqual(self.system.calls, [])

    def test_restore_does_not_address_reused_device_id(self):
        saved = {"schemaVersion": 1, "radios": deepcopy(self.system.devices), "networkManager": None, "bluetoothPowered": False}
        self.system.devices[0]["name"] = "new radio"
        restore(saved, self.system.run)
        self.assertNotIn(["rfkill", "unblock", "0"], self.system.calls)

    def test_power_profiles_parse_availability_and_validate_before_setting(self):
        listing = "* performance:\n    Degraded: yes (high-operating-temperature)\n  balanced:\n  power-saver:\n"
        run = Mock(return_value=SimpleNamespace(returncode=0, stdout=listing))
        data = power_status(run)
        self.assertEqual(data["powerProfile"], "performance")
        self.assertIn("high-operating-temperature", data["powerDegraded"])
        set_profile("balanced", run)
        self.assertEqual(run.call_args.args[0], ["powerprofilesctl", "set", "balanced"])
        run.reset_mock()
        with self.assertRaises(ConfigError): set_profile("turbo; reboot", run)
        run.assert_not_called()
        run.return_value = SimpleNamespace(returncode=0, stdout="* balanced:\n  power-saver:\n")
        with self.assertRaises(ConfigError): set_profile("performance", run)
        self.assertNotIn(["powerprofilesctl", "set", "performance"], [call.args[0] for call in run.call_args_list])

    def test_hardware_blocks_are_reported(self):
        for item in self.system.devices: item.update(hard=True, soft=False)
        self.assertTrue(radio_status()["airplane"])
        self.assertTrue(radio_status()["airplaneHardwareBlocked"])


if __name__ == "__main__": unittest.main()
