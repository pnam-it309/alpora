from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch

from poly_shell.state import Paths
from poly_shell.toolkit_refresh import refresh


class ToolkitRefreshTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.paths = Paths(root / 'config/poly-shell', root / 'state', root / 'runtime')
        css = self.paths.config.parent / 'gtk-4.0/poly-palette.css'
        css.parent.mkdir(parents=True)
        css.write_text('window { background: #123456; }')

    def reply(self, owner=True, busy=False):
        def run(command, **kwargs):
            if 'NameHasOwner' in command[-2]:
                return CompletedProcess(command, 0, '(true,)' if owner else '(false,)')
            if command[-1] == 'Busy':
                return CompletedProcess(command, 0, '(<true>,)' if busy else '(<false>,)')
            if command[-1] == 'OpenLocations':
                return CompletedProcess(command, 0, "(<['file:///home/user/a%20b', 'file:///home/user/project']>,)")
            return CompletedProcess(command, 255, '')  # Quit can outlive its D-Bus reply.
        return run

    def test_absent_file_manager_is_not_started(self):
        with patch('poly_shell.toolkit_refresh.subprocess.run', side_effect=self.reply(owner=False)), patch('poly_shell.toolkit_refresh.subprocess.Popen') as launch:
            self.assertFalse(refresh(self.paths)['refreshed'])
            launch.assert_not_called()

    def test_busy_file_operations_are_not_interrupted(self):
        with patch('poly_shell.toolkit_refresh.subprocess.run', side_effect=self.reply(busy=True)) as run, patch('poly_shell.toolkit_refresh.subprocess.Popen') as launch:
            self.assertTrue(refresh(self.paths)['deferred'])
            self.assertFalse(any(command.args[0][0] == 'nautilus' for command in run.call_args_list))
            launch.assert_not_called()
            self.assertFalse((self.paths.state / 'toolkit-refresh.json').exists())

    def test_refresh_restores_locations_and_unchanged_palette_does_not_restart(self):
        with patch('poly_shell.toolkit_refresh.subprocess.run', side_effect=self.reply()), patch('poly_shell.toolkit_refresh.subprocess.Popen') as launch, patch('poly_shell.toolkit_refresh.time.sleep'):
            self.assertTrue(refresh(self.paths)['refreshed'])
            self.assertEqual(launch.call_args.args[0], ['nautilus', '--new-window', '--', 'file:///home/user/a%20b', 'file:///home/user/project'])
            self.assertFalse(refresh(self.paths)['refreshed'])
            self.assertEqual(launch.call_count, 1)
