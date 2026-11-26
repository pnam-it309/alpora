"""Native image file chooser backends (kdialog, zenity, yad) run through SafeRunner."""
from pathlib import Path

from ..adapters.base import SafeRunner
from .local_images import IMAGE_EXTENSIONS

PICK_TIMEOUT = 300.0
_GLOB = ' '.join(f'*{ext} *{ext.upper()}' for ext in IMAGE_EXTENSIONS)
_FILTER = 'Images (' + _GLOB + ')'
_TITLE = 'Choose wallpaper'


def picker_commands(start):
    start_dir = str(start) + '/'
    return [
        ['kdialog', '--title', _TITLE, '--getopenfilename', start_dir, _GLOB],
        ['zenity', '--file-selection', '--title', _TITLE, '--filename', start_dir,
         '--file-filter', _FILTER],
        ['yad', '--file', '--title', _TITLE, '--filename', start_dir, '--file-filter', _FILTER],
    ]


def pick_image(start=None):
    """Return {'path': str, 'backend': name}; path empty when cancelled or no picker is available."""
    start = Path(start).expanduser() if start else Path.home() / 'Pictures'
    if not start.is_dir():
        start = Path.home()
    for cmd in picker_commands(start):
        if not SafeRunner.is_available(cmd[0]):
            continue
        result = SafeRunner.run(cmd, timeout=PICK_TIMEOUT, use_circuit_breaker=False)
        if result.returncode == 127:
            continue
        lines = (result.stdout or '').strip().splitlines()
        chosen = lines[0].strip() if lines else ''
        if result.returncode == 0 and chosen:
            path = Path(chosen).expanduser()
            if path.suffix.lower() in IMAGE_EXTENSIONS and path.is_file():
                return {'path': str(path), 'backend': cmd[0], 'unavailable': False}
            return {'path': '', 'backend': cmd[0], 'unavailable': False, 'invalid': True}
        return {'path': '', 'backend': cmd[0], 'unavailable': False, 'cancelled': True}
    return {'path': '', 'backend': '', 'unavailable': True,
            'error': 'No file picker found (install kdialog, zenity or yad)'}
