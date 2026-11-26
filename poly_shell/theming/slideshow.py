"""Wallpaper slideshow: config, ordering and advancing to the next folder image."""
from pathlib import Path
import random

from ..core.state import ConfigError, atomic_json, read_object, state_lock
from .local_images import IMAGE_EXTENSIONS, discover_image_folders

INTERVALS = (5, 15, 30, 60)
DEFAULTS = {'enabled': False, 'folder': '', 'intervalMinutes': 15, 'shuffle': False}


def _config_path(paths):
    return paths.config / 'slideshow.json'


def _state_path(paths):
    return paths.state / 'slideshow-state.json'


def _safe_read(path):
    try:
        return read_object(path) if path.exists() else {}
    except (ConfigError, OSError):
        return {}


def get_config(paths):
    raw = _safe_read(_config_path(paths))
    interval = raw.get('intervalMinutes')
    return {
        'enabled': raw.get('enabled') is True,
        'folder': raw.get('folder') if isinstance(raw.get('folder'), str) else '',
        'intervalMinutes': interval if interval in INTERVALS else DEFAULTS['intervalMinutes'],
        'shuffle': raw.get('shuffle') is True,
    }


def set_config(paths, payload):
    config = get_config(paths)
    if 'enabled' in payload:
        if not isinstance(payload['enabled'], bool):
            raise ConfigError('Invalid slideshow enabled flag')
        config['enabled'] = payload['enabled']
    if 'shuffle' in payload:
        if not isinstance(payload['shuffle'], bool):
            raise ConfigError('Invalid slideshow shuffle flag')
        config['shuffle'] = payload['shuffle']
    if 'intervalMinutes' in payload:
        if payload['intervalMinutes'] not in INTERVALS or isinstance(payload['intervalMinutes'], bool):
            raise ConfigError('Slideshow interval must be 5, 15, 30 or 60 minutes')
        config['intervalMinutes'] = payload['intervalMinutes']
    if 'folder' in payload:
        folder = payload['folder']
        if not isinstance(folder, str):
            raise ConfigError('Invalid slideshow folder')
        folder = folder.strip()
        if folder and not Path(folder).expanduser().is_dir():
            raise ConfigError('Slideshow folder does not exist')
        config['folder'] = str(Path(folder).expanduser()) if folder else ''
    with state_lock(paths):
        atomic_json(_config_path(paths), config)
    return config


def effective_folder(config):
    if config['folder']:
        return Path(config['folder']).expanduser()
    for entry in discover_image_folders():
        if entry['label'] != 'Screenshots':
            return Path(entry['path'])
    return None


def folder_images(folder):
    if folder is None:
        return []
    try:
        return sorted((str(p) for p in folder.iterdir()
                       if p.suffix.lower() in IMAGE_EXTENSIONS and p.is_file()), key=str.lower)
    except OSError:
        return []


def next_image(paths, rng=random):
    """Pick and import the next image, apply it, and remember the index."""
    from .themes import apply_theme, import_wallpaper
    config = get_config(paths)
    folder = effective_folder(config)
    images = folder_images(folder)
    if not images:
        raise ConfigError('Slideshow folder has no images')
    state = _safe_read(_state_path(paths))
    last = state.get('index') if isinstance(state.get('index'), int) and state.get('folder') == str(folder) else -1
    if config['shuffle'] and len(images) > 1:
        index = rng.choice([i for i in range(len(images)) if i != last])
    else:
        index = (last + 1) % len(images)
    imported = import_wallpaper(paths, images[index])['imported']
    saved = _safe_read(paths.config / 'appearance.json')
    result = apply_theme(paths, imported, saved.get('colorsFromWallpaper', True), None)
    with state_lock(paths):
        atomic_json(_state_path(paths), {'folder': str(folder), 'index': index, 'image': images[index]})
    return result | {'imported': imported, 'slideshow': config | {'index': index}}


def slideshow_control(paths, action, payload):
    if action == 'slideshow-get':
        config = get_config(paths)
        return config | {'effectiveFolder': str(effective_folder(config) or '')}
    if action == 'slideshow-set':
        config = set_config(paths, payload)
        return config | {'effectiveFolder': str(effective_folder(config) or '')}
    if action == 'slideshow-next':
        return next_image(paths)
    raise ConfigError('Unknown theme action')
