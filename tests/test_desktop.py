from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from poly_shell.desktop import backlight_device, control, restore_desktop
from poly_shell.state import ConfigError, Paths, atomic_json


class DesktopTests(unittest.TestCase):
    def test_backlight_conversion_and_missing_device(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(backlight_device(root), (None, 0))
            device = root / 'display'
            device.mkdir()
            (device / 'max_brightness').write_text('255')
            (device / 'brightness').write_text('128')
            self.assertEqual(backlight_device(root), ('display', 50))
            (device / 'max_brightness').write_text('0')
            self.assertEqual(backlight_device(root), (None, 0))

    def test_invalid_brightness_never_reaches_the_hardware_command(self):
        paths = Paths(Path('/unused'), Path('/unused'), Path('/unused'))
        for value in ('0', '-1', '101', '50; reboot', None):
            with self.subTest(value=value), patch('poly_shell.desktop.command') as run:
                with self.assertRaises(ConfigError):
                    control(paths, 'brightness', value)
                run.assert_not_called()

    def test_bluetooth_unblocks_before_enabling_and_blocks_after_disabling(self):
        paths = Paths(Path('/unused'), Path('/unused'), Path('/unused'))
        with patch('poly_shell.desktop.command') as run, patch('poly_shell.desktop.status', return_value={}):
            control(paths, 'bluetooth', 'on')
            self.assertEqual([c.args[0] for c in run.call_args_list], [
                ['rfkill', 'unblock', 'bluetooth'], ['bluetoothctl', '--timeout', '3', 'power', 'on']])
            run.reset_mock()
            control(paths, 'bluetooth', 'off')
            self.assertEqual([c.args[0] for c in run.call_args_list], [
                ['bluetoothctl', '--timeout', '3', 'power', 'off'], ['rfkill', 'block', 'bluetooth']])
            run.reset_mock()
            with self.assertRaises(ConfigError):
                control(paths, 'bluetooth', 'invalid')
            run.assert_not_called()

    def test_night_light_preference_is_reapplied_on_start(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = Paths(root / 'config', root / 'state', root / 'runtime')
            atomic_json(paths.state / 'desktop.json', {'nightLight': True})
            with patch('poly_shell.desktop.set_night_light') as apply:
                restore_desktop(paths)
                apply.assert_called_once_with(paths, True)

    def test_unsupported_action_raises_config_error(self):
        paths = Paths(Path('/unused'), Path('/unused'), Path('/unused'))
        with self.assertRaises(ConfigError):
            control(paths, 'invalid_action')

    def test_invalid_power_profile_raises_config_error(self):
        paths = Paths(Path('/unused'), Path('/unused'), Path('/unused'))
        with self.assertRaises(ConfigError):
            control(paths, 'power-profile', 'ultra-overclock')

    def test_invalid_airplane_value_raises_config_error(self):
        paths = Paths(Path('/unused'), Path('/unused'), Path('/unused'))
        with patch('poly_shell.desktop.set_airplane', side_effect=ConfigError('State must be on or off')):
            with self.assertRaises(ConfigError):
                control(paths, 'airplane', 'invalid')


if __name__ == '__main__':
    unittest.main()
