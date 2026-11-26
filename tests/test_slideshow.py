"""File picker backends and wallpaper slideshow."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from poly_shell.core.state import ConfigError, Paths, read_object, update_session
from poly_shell.theming import file_picker, slideshow, themes


def done(code=0, out=''):
    return subprocess.CompletedProcess([], code, stdout=out, stderr='')


class PickerTests(unittest.TestCase):
    def test_no_backend_reports_unavailable(self):
        with patch.object(file_picker.SafeRunner, 'is_available', return_value=False):
            result = file_picker.pick_image()
        self.assertTrue(result['unavailable']); self.assertEqual(result['path'], '')

    def test_first_available_backend_wins_and_is_not_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'a.png'; image.write_bytes(b'x')
            with patch.object(file_picker.SafeRunner, 'is_available', side_effect=lambda b: b == 'zenity'), \
                 patch.object(file_picker.SafeRunner, 'run', return_value=done(0, str(image) + '\n')) as run:
                result = file_picker.pick_image(tmp)
        self.assertEqual(result['path'], str(image)); self.assertEqual(result['backend'], 'zenity')
        self.assertIsInstance(run.call_args.args[0], list)

    def test_cancel_and_non_image_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = Path(tmp) / 'a.txt'; text.write_text('x')
            with patch.object(file_picker.SafeRunner, 'is_available', return_value=True):
                with patch.object(file_picker.SafeRunner, 'run', return_value=done(1, '')):
                    self.assertTrue(file_picker.pick_image(tmp)['cancelled'])
                with patch.object(file_picker.SafeRunner, 'run', return_value=done(0, str(text))):
                    self.assertEqual(file_picker.pick_image(tmp)['path'], '')

    def test_theme_control_pick(self):
        with patch('poly_shell.theming.file_picker.pick_image', return_value={'path': ''}):
            self.assertEqual(themes.theme_control(None, 'pick', {}), {'path': ''})


class SlideshowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.paths = Paths(root / 'config/poly-shell', root / 'state', root / 'runtime')
        update_session(self.paths)
        self.folder = root / 'pics'; self.folder.mkdir()
        for name in ('b.png', 'a.jpg', 'c.webp', 'note.txt'):
            (self.folder / name).write_bytes(b'x')

    def test_config_defaults_and_validation(self):
        self.assertEqual(slideshow.get_config(self.paths),
                         {'enabled': False, 'folder': '', 'intervalMinutes': 15, 'shuffle': False})
        cfg = slideshow.set_config(self.paths, {'enabled': True, 'intervalMinutes': 30, 'folder': str(self.folder)})
        self.assertEqual((cfg['enabled'], cfg['intervalMinutes'], cfg['folder']), (True, 30, str(self.folder)))
        self.assertEqual(read_object(self.paths.config / 'slideshow.json')['intervalMinutes'], 30)
        for bad in ({'intervalMinutes': 7}, {'enabled': 'yes'}, {'folder': '/nonexistent/zz'}, {'shuffle': 1}):
            with self.assertRaises(ConfigError): slideshow.set_config(self.paths, bad)

    def test_next_cycles_in_order_and_remembers_index(self):
        slideshow.set_config(self.paths, {'folder': str(self.folder)})
        seen = []
        with patch.object(themes, 'import_wallpaper', side_effect=lambda p, v: seen.append(Path(v).name) or {'imported': 'custom-x'}), \
             patch.object(themes, 'apply_theme', return_value={'selected': 'custom-x'}):
            for _ in range(4): slideshow.next_image(self.paths)
        self.assertEqual(seen, ['a.jpg', 'b.png', 'c.webp', 'a.jpg'])
        self.assertEqual(read_object(self.paths.state / 'slideshow-state.json')['index'], 0)

    def test_shuffle_never_repeats_and_empty_folder_errors(self):
        slideshow.set_config(self.paths, {'folder': str(self.folder), 'shuffle': True})
        seen = []
        with patch.object(themes, 'import_wallpaper', side_effect=lambda p, v: seen.append(v) or {'imported': 'c'}), \
             patch.object(themes, 'apply_theme', return_value={}):
            for _ in range(6): slideshow.next_image(self.paths)
        self.assertTrue(all(a != b for a, b in zip(seen, seen[1:])))
        empty = self.folder.parent / 'empty'; empty.mkdir()
        slideshow.set_config(self.paths, {'folder': str(empty)})
        with self.assertRaises(ConfigError): slideshow.next_image(self.paths)

    def test_theme_control_dispatch(self):
        got = themes.theme_control(self.paths, 'slideshow-set', {'enabled': True})
        self.assertTrue(got['enabled'])
        self.assertTrue(themes.theme_control(self.paths, 'slideshow-get', {})['enabled'])


if __name__ == '__main__':
    unittest.main()
