"""Wallpaper collections, deterministic palettes and reversible coordinated themes."""
from copy import deepcopy
from datetime import datetime
import colorsys
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from ..core.state import (ConfigError, ROOT, Paths, atomic_json, read_object, state_lock,
                    current_mode, profile_for, settings_for, merge)
from .appearance import atomic_text
from .visual import visual_for
from .landscapes import landscape_assets
from .local_images import IMAGE_EXTENSIONS, discover_image_folders, discover_local_images
from .toolkit_theme import (
    HEX,
    KEYS,
    border_lua,
    ini_settings,
    map_color,
    mix,
    rgb,
    toolkit_files,
    toolkit_theme_name,
    toolkit_theme_root,
    validate_palette,
)

IDS = ('alpine', 'moon-lake', 'forest-mist', 'warm-desert', 'northern-lights', 'rose-sunset', 'timeline')


def data_root(paths):
    # Keep private imported images out of the source repository.
    return paths.config / 'wallpapers'


def theme_image(paths, document):
    value = document.get('wallpaper')
    if not isinstance(value, str):
        raise ConfigError('Missing wallpaper for theme')
    path = (ROOT / 'assets' / value).resolve()
    if not (path.is_relative_to((ROOT / 'assets/wallpapers').resolve()) or
            path.is_relative_to(data_root(paths).resolve())):
        raise ConfigError('Image must belong to collection')
    if path.suffix.lower() not in IMAGE_EXTENSIONS or not path.is_file():
        raise ConfigError('Theme wallpaper image not found')
    return path


def load_theme(paths, ident):
    if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9_-]{1,80}', ident):
        raise ConfigError('Invalid theme name')
    path = ROOT / 'assets/themes' / (ident + '.json') if ident in IDS else paths.config / 'themes' / (ident + '.json')
    doc = read_object(path)
    if doc.get('id') != ident:
        raise ConfigError('Invalid theme file')
    theme_image(paths, doc)
    if ident == 'timeline':
        from .timeline import assets
        assets()
    palette = validate_palette(doc.get('themePalette', doc.get('palette')))
    if not isinstance(doc.get('swatches'), list) or len(doc['swatches']) != 5 or any(not isinstance(c, str) or not HEX.fullmatch(c) for c in doc['swatches']):
        raise ConfigError('Invalid theme color swatches')
    return doc | {'palette': palette}


def resolve_appearance(paths):
    base = read_object(ROOT / 'assets/themes/alpine.json')
    selection = paths.config / 'appearance.json'
    try:
        selected = read_object(selection) if selection.exists() else {}
        ident = selected.get('theme', 'alpine')
        if ident == 'alpine' and not selected.get('palette'):
            return base
        doc = load_theme(paths, ident)
        result = merge(base, doc)
        result['label'] = doc.get('collectionLabel', doc['label'])
        if selected.get('palette'):
            result['palette'] = validate_palette(selected['palette'])
        result['colorsFromWallpaper'] = selected.get('colorsFromWallpaper', True)
        if ident == 'timeline' and result['colorsFromWallpaper']:
            from .timeline import palette_for, saved_minute
            result['palette'] = palette_for(saved_minute(paths))
        visuals, assets = landscape_assets(paths, ident, result['palette'])
        if all(path.is_file() for path in assets): result.update(visuals)
        return result
    except (ConfigError, OSError, TypeError):
        return base



def catalog(paths, folder=None):
    docs = []
    for ident in list(IDS) + sorted(p.stem for p in (paths.config / 'themes').glob('custom-*.json')):
        try:
            doc = load_theme(paths, ident)
            docs.append({'id': ident, 'label': doc.get('collectionLabel', doc['label']),
                         'image': str(timeline_frame(paths) if ident == 'timeline' else theme_image(paths, doc)), 'palette': doc['palette'],
                         'swatches': doc['swatches'], 'custom': ident.startswith('custom-')})
        except (ConfigError, OSError):
            continue
    saved = read_object(paths.config / 'appearance.json') if (paths.config / 'appearance.json').exists() else {}
    folder_value = str(folder).strip() if folder is not None else ''
    active_folder = str(Path(folder_value).expanduser()) if folder_value else ''
    return {'items': docs, 'selected': saved.get('theme', 'alpine'),
            'colorsFromWallpaper': saved.get('colorsFromWallpaper', True),
            'localFolders': discover_image_folders(),
            'localImages': discover_local_images(folder),
            'activeFolder': active_folder}



def extract_palette_from_image(source_path):
    """Extract deterministic semantic palette from an image file using Pillow."""
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise ConfigError('Select an image file')
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise ConfigError('Pillow (python-pillow) is required for palette extraction')
    try:
        with Image.open(source) as original:
            if original.format not in ('PNG', 'JPEG', 'WEBP'):
                raise ConfigError('Supported formats: PNG, JPEG, and WebP')
            original.load()
            sample = ImageOps.exif_transpose(original).convert('RGB')
            sample.thumbnail((96, 96))
            quantized = sample.quantize(colors=12)
            table = quantized.getpalette()
            counts = sorted(quantized.getcolors(), reverse=True)
    except (OSError, ValueError) as exc:
        raise ConfigError('Failed to read image') from exc
    candidates = []
    for count, index in counts:
        color = tuple(c / 255 for c in table[index*3:index*3+3])
        h, sat, val = colorsys.rgb_to_hsv(*color)
        candidates.append((count * (0.2 + sat) * (0.3 + val), h, sat, val, color))
    _, hue, sat, val, _ = max(candidates)
    def hsv(h, s, v):
        return '#' + ''.join(f'{round(x*255):02x}' for x in colorsys.hsv_to_rgb(h % 1, s, v))
    return {
        'background': hsv(hue, min(.48, max(.15, sat)), .15),
        'surface': hsv(hue, min(.40, max(.12, sat*.65)), .24),
        'text': hsv(hue, .035, .96),
        'muted': hsv(hue, .13, .77),
        'accent': hsv(hue, min(.42, max(.18, sat*.65)), .88),
        'secondary': hsv(hue+.12, .29, .88),
        'cool': hsv(hue-.10, .28, .80),
        'border': hsv(hue, .18, .40),
    }

def import_wallpaper(paths, value):
    if not isinstance(value, str) or not value.strip():
        raise ConfigError('Select an image for wallpaper')
    source = Path(value).expanduser().resolve()
    if not source.is_file():
        raise ConfigError('Select an image for wallpaper')
    palette = extract_palette_from_image(source)
    ident = 'custom-' + hashlib.sha256(source.read_bytes()).hexdigest()[:20]
    suffix = '.jpg' if source.suffix.lower() in ('.jpg', '.jpeg') else source.suffix.lower()
    if suffix not in ('.png', '.jpg', '.webp'):
        suffix = '.png'  # Actual decoder format, not an arbitrary source suffix.
        raise ConfigError('Save image with PNG, JPG or WebP extension')
    destination = data_root(paths) / (ident + suffix)
    label = re.sub(r'[\x00-\x1f$#{}<>]', '', source.stem).strip()[:50] or 'Custom Wallpaper'
    doc = {'id': ident, 'label': label, 'wallpaper': str(destination), 'palette': palette,
           'swatches': [palette[k] for k in ('background', 'surface', 'cool', 'accent', 'secondary')]}
    with state_lock(paths):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            temporary = destination.with_suffix(destination.suffix + '.tmp')
            try:
                shutil.copyfile(source, temporary)
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
        atomic_json(paths.config / 'themes' / (ident + '.json'), doc)
    return catalog(paths) | {'imported': ident}


def runtime_border(p):
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        result = subprocess.run(['hyprctl', 'eval', border_lua(p)], capture_output=True, text=True, timeout=5)
        if result.returncode or result.stdout.strip() != 'ok':
            # Fallback to standard Hyprland keyword syntax
            active = f"rgba({p['accent'][1:]}e6) rgba({p['secondary'][1:]}cc) 45deg"
            inactive = f"rgba({p['border'][1:]}b3)"
            res1 = subprocess.run(['hyprctl', 'keyword', 'general:col.active_border', active], capture_output=True, text=True, timeout=5)
            res2 = subprocess.run(['hyprctl', 'keyword', 'general:col.inactive_border', inactive], capture_output=True, text=True, timeout=5)
            if res1.returncode != 0 and res2.returncode != 0:
                raise ConfigError('Cannot apply Hyprland border colors')


def notify_toolkit(paths, palette, icon_name):
    warnings = []
    if paths.config != Paths.current().config:
        return warnings
    for key, value in (('gtk-theme', toolkit_theme_name(palette)), ('icon-theme', icon_name)):
        try:
            result = subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', key, value], capture_output=True, text=True, timeout=3)
            if result.returncode: warnings.append('Cannot update system setting ' + key)
        except (OSError, subprocess.SubprocessError):
            warnings.append('Cannot update system setting ' + key)
    from .terminal_colors import refresh
    if refresh(palette):
        warnings.append('Cannot update colors for some open terminals')
    try:
        from .toolkit_refresh import schedule
        schedule(paths)
    except (OSError, subprocess.SubprocessError):
        warnings.append('Restart file manager to refresh its palette')
    return warnings


def apply_timeline_palette(paths, minute, palette, selection):
    """Called under state_lock: publish palette/time together, without wallpaper work."""
    from ..system.indicators import mako_style
    from ..system.lockscreen import lock_style
    p = validate_palette(palette)
    old_palette = validate_palette(selection.get('palette') or load_theme(paths, 'timeline')['palette'])
    doc = load_theme(paths, 'timeline')
    resolved = merge(read_object(ROOT / 'assets/themes/alpine.json'), doc)
    resolved.update(label=doc.get('collectionLabel', doc['label']), palette=p, colorsFromWallpaper=True)
    snapshot = {'schemaVersion': 1, 'mode': current_mode(paths),
                'profile': profile_for(paths, current_mode(paths)), 'settings': settings_for(paths),
                'visual': visual_for(paths), 'appearance': resolved}
    files = toolkit_files(paths, p, resolved.get('iconTheme', 'Poly-Alpine'))
    files[paths.state/'mako-theme.conf'] = mako_style(snapshot)
    files[paths.state/'hyprlock-theme.conf'] = lock_style(snapshot, paths)
    files[paths.config.parent/'hypr/poly-shell-theme.lua'] = border_lua(p)
    visuals, images = landscape_assets(paths, 'timeline', p)
    files.update(images); resolved.update(visuals)
    files[paths.config/'appearance.json'] = json.dumps(selection | {'palette': p}, ensure_ascii=False, indent=2)+'\n'
    files[paths.config/'timeline.json'] = json.dumps({'schemaVersion': 1, 'minute': minute})+'\n'
    files[paths.session] = json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n'
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in files}
    border_changed = False
    try:
        for path, text in files.items():
            if path != paths.session and originals[path] != text: atomic_text(path, text)
        border_changed = True; runtime_border(p)
        atomic_text(paths.session, files[paths.session])
    except (ConfigError, OSError, ValueError, subprocess.SubprocessError) as failure:
        errors = []
        for path, old in originals.items():
            try:
                if old is None: path.unlink(missing_ok=True)
                elif not path.exists() or path.read_text(encoding="utf-8") != old: atomic_text(path, old)
            except OSError as exc: errors.append(str(exc))
        if border_changed:
            try: runtime_border(old_palette)
            except (ConfigError, OSError, subprocess.SubprocessError) as exc: errors.append(str(exc))
        raise ConfigError('Timeline colors not saved: '+str(failure)+('; Restored: '+'; '.join(errors) if errors else '')) from failure
    notify_toolkit(paths, p, resolved.get('iconTheme', 'Poly-Alpine'))
    if paths.config == Paths.current().config:
        try: subprocess.run(['makoctl', 'reload'], capture_output=True, timeout=3, check=False)
        except (OSError, subprocess.SubprocessError): pass


def timeline_frame(paths):
    try:
        from PIL import Image
    except ImportError:
        Image = None
    from .timeline import assets, saved_minute
    stops = assets()
    minute = saved_minute(paths)
    path = paths.state / ('timeline-frame-' + str(minute) + '.png')
    if path.is_file() and path.stat().st_mtime >= max(Path(stop['image']).stat().st_mtime for stop in stops):
        return path
    extended = stops + [dict(stops[0], minute=1440)]
    lower, upper = next((a, b) for a, b in zip(extended, extended[1:]) if a['minute'] <= minute < b['minute'])
    if Image is None:
        nearest = lower if (minute - lower['minute']) <= (upper['minute'] - minute) else upper
        return Path(nearest['image'])
    t = (minute - lower['minute']) / (upper['minute'] - lower['minute'])
    t = t * t * (3 - 2 * t)
    path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(lower['image']) as a, Image.open(upper['image']) as b:
        Image.blend(a.convert('RGB'), b.convert('RGB'), t).save(path)
    return path


def apply_theme(paths, ident, automatic=True, transition=None, *, activate=True):
    from ..system.desktop import _wallpaper
    from ..system.desktop import validate_transition
    from ..system.indicators import mako_style
    from ..system.lockscreen import lock_style
    from ..core.state import appearance_for
    if type(automatic) is not bool:
        raise ConfigError('Invalid palette mode')
    transition = validate_transition(transition)
    if not activate and transition is not None:
        raise ConfigError('A prepared theme cannot start a live transition')
    with state_lock(paths):
        doc = load_theme(paths, ident)
        mode = current_mode(paths)
        previous = appearance_for(paths)
        old_palette = validate_palette(previous.get('palette') or profile_for(paths, mode)['palette'])
        p = doc['palette'] if automatic else old_palette
        if ident == 'timeline' and automatic:
            from .timeline import palette_for, saved_minute
            p = palette_for(saved_minute(paths))
        resolved = merge(read_object(ROOT / 'assets/themes/alpine.json'), doc)
        resolved.update(label=doc.get('collectionLabel', doc['label']), palette=p, colorsFromWallpaper=automatic)
        snapshot = {'schemaVersion': 1, 'mode': mode, 'profile': profile_for(paths, mode),
                    'settings': settings_for(paths), 'visual': visual_for(paths), 'appearance': resolved}
        selection = {'schemaVersion': 1, 'theme': ident, 'palette': p, 'colorsFromWallpaper': automatic}
        files = toolkit_files(paths, p, resolved.get("iconTheme", "Poly-Alpine"))
        files[paths.state / 'mako-theme.conf'] = mako_style(snapshot)
        files[paths.state / 'hyprlock-theme.conf'] = lock_style(snapshot, paths)
        files[paths.config.parent / 'hypr/poly-shell-theme.lua'] = border_lua(p)
        visuals, assets = landscape_assets(paths, ident, p)
        files.update(assets)
        # Retain the old file for recovery tools; displayed images use immutable
        # palette-specific URLs rather than a mutable Qt image-cache key.
        files[paths.state / 'theme-ridge.svg'] = assets[Path(visuals['ridge'])]
        resolved.update(visuals)
        files[paths.config / 'appearance.json'] = json.dumps(selection, ensure_ascii=False, indent=2)+'\n'
        files[paths.session] = json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n'
        wallpaper_config = paths.config / 'wallpaper.json'
        originals = {f: f.read_text(encoding="utf-8") if f.exists() else None for f in (*files, wallpaper_config)}
        old_image = read_object(wallpaper_config).get('image') if wallpaper_config.exists() else str(ROOT / 'assets/wallpapers/alpine-dawn.png')
        backup = paths.state / 'backups' / ('theme-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        changed_wallpaper = False
        try:
            # Start the drop reveal before durable backups, toolkit writes or
            # compositor calls. All text and the previous state are already
            # validated in memory; the same rollback covers every later step.
            if transition is not None:
                target = timeline_frame(paths) if ident == 'timeline' else theme_image(paths, doc)
                seed = timeline_frame(paths) if previous.get('id') == 'timeline' else None
                _wallpaper(paths, str(target), quiet=True, transition=transition, seed=seed)
                changed_wallpaper = True
            atomic_json(backup / 'manifest.json', {'files': [{'path': str(f), 'backup': str(i)+'-'+f.name if content is not None else None} for i, (f, content) in enumerate(originals.items())]})
            for i, (f, content) in enumerate(originals.items()):
                if content is not None: atomic_text(backup / (str(i)+'-'+f.name), content)
            for f, text in files.items():
                if f != paths.session: atomic_text(f, text)
            if activate: runtime_border(p)
            if activate and transition is None:
                _wallpaper(paths, str(theme_image(paths, doc)), quiet=True)
                changed_wallpaper = True
            elif not activate:
                target = timeline_frame(paths) if ident == 'timeline' else theme_image(paths, doc)
                atomic_json(wallpaper_config, {'image': str(target)})
            atomic_text(paths.session, files[paths.session])
        except (ConfigError, OSError, ValueError, subprocess.SubprocessError) as failure:
            errors = []
            for f, original in originals.items():
                try:
                    if original is None: f.unlink(missing_ok=True)
                    else: atomic_text(f, original)
                except OSError as exc: errors.append(str(exc))
            try:
                if activate: runtime_border(old_palette)
                if changed_wallpaper: _wallpaper(paths, old_image, quiet=True)
            except (ConfigError, OSError, ValueError, subprocess.SubprocessError) as exc: errors.append(str(exc))
            raise ConfigError('Theme not applied: '+str(failure)+('; Restored: '+'; '.join(errors) if errors else '')) from failure
    if not activate:
        return catalog(paths) | {'saved': True, 'prepared': True, 'warnings': []}
    try:
        subprocess.run(['makoctl', 'reload'], capture_output=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired):
        pass
    warnings = notify_toolkit(paths, p, resolved.get('iconTheme', 'Poly-Alpine'))
    return catalog(paths) | {'saved': True, 'warnings': warnings}


def delete_custom_theme(paths, ident):
    """Remove an imported custom wallpaper theme and revert to alpine if active."""
    if not isinstance(ident, str) or not re.fullmatch(r'custom-[a-f0-9]{20}', ident):
        raise ConfigError('Can only remove custom imported wallpapers')
    with state_lock(paths):
        selection = paths.config / 'appearance.json'
        active = False
        if selection.exists():
            try:
                active = read_object(selection).get('theme') == ident
            except ConfigError:
                active = False
        (paths.config / 'themes' / (ident + '.json')).unlink(missing_ok=True)
        for image_path in data_root(paths).glob(ident + '.*'):
            if image_path.is_file():
                image_path.unlink(missing_ok=True)
        if active:
            apply_theme(paths, 'alpine', True)
    return catalog(paths)


def theme_control(paths, action, payload):
    if not isinstance(payload, dict):
        raise ConfigError('Invalid theme request')
    if action == 'list':
        return catalog(paths, folder=payload.get('folder'))
    if action == 'import':
        imported_res = import_wallpaper(paths, payload.get('image'))
        if payload.get('apply') is True:
            applied_res = apply_theme(
                paths,
                imported_res['imported'],
                payload.get('colorsFromWallpaper', True),
                payload.get('transition'),
            )
            return applied_res | {'imported': imported_res['imported']}
        return imported_res
    if action == 'pick':
        from .file_picker import pick_image
        return pick_image()
    if action.startswith('slideshow-'):
        from . import slideshow
        return slideshow.slideshow_control(paths, action, payload)
    if action == 'apply':
        return apply_theme(paths, payload.get('id'), payload.get('colorsFromWallpaper', True), payload.get('transition'))
    if action == 'remove':
        return delete_custom_theme(paths, payload.get('id'))
    raise ConfigError('Unknown theme action')
