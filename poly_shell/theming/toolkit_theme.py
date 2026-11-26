"""GTK3/GTK4 and Hyprland border theme generators for ALPORA."""
from __future__ import annotations

import colorsys
import hashlib
import json
import os
from pathlib import Path
import re

from ..core.state import ConfigError, Paths, ROOT

HEX = re.compile(r'#[0-9a-fA-F]{6}')
KEYS = ('background', 'surface', 'text', 'muted', 'accent', 'secondary', 'cool', 'border')


def validate_palette(value):
    if not isinstance(value, dict):
        raise ConfigError('Invalid theme palette')
    for key in ('background', 'surface', 'text', 'muted', 'accent'):
        if not isinstance(value.get(key), str) or not HEX.fullmatch(value[key]):
            raise ConfigError('Invalid theme color: ' + key)
    result = {}
    for key in KEYS:
        color = value.get(key, value['accent'] if key in ('secondary', 'cool') else value['muted'])
        if not isinstance(color, str) or not HEX.fullmatch(color):
            raise ConfigError('Invalid theme color: ' + key)
        result[key] = color
    return result


def rgb(value):
    return tuple(int(value[i:i+2], 16) / 255 for i in (1, 3, 5))


def mix(a, b, amount):
    return '#' + ''.join(f'{round(x * (1-amount) * 255 + y * amount * 255):02x}' for x, y in zip(rgb(a), rgb(b)))


def map_color(value, p):
    """Recolor the owned toolkit templates; keep semantic red/warning colors."""
    roles = {'#202729': 'background', '#272d2d': 'background',
             '#2e3734': 'surface', '#343d38': 'surface',
             '#293230': 'surface', '#2b3430': 'surface',
             '#e7e9e5': 'text', '#a9b99a': 'accent', '#bfd0ad': 'accent'}
    if value.lower() in roles:
        return p[roles[value.lower()]]
    r, g, b = rgb(value)
    h, s, _v = colorsys.rgb_to_hsv(r, g, b)
    light = (r + g + b) / 3
    if s > .18 and h < .045:
        return value
    if s > .10 and light > .48:
        base = p['secondary'] if .045 <= h < .17 else p['cool'] if .43 < h < .65 else p['accent']
        return mix(base, p['background'], max(0, .68-light)*.65)
    if light > .80:
        return p['text']
    if light > .54:
        return p['muted']
    if light > .33:
        return mix(p['surface'], p['accent'], min(.4, .12+light-.33))
    if light > .19:
        return mix(p['background'], p['surface'], min(.95, .35+(light-.19)*4))
    if light > .13:
        return mix(p['background'], p['surface'], (light-.13)*3)
    return mix(p['background'], '#000000', .18)


def toolkit_theme_name(p):
    # Include the renderer revision so existing GTK processes reload revised CSS.
    digest = hashlib.sha256(('2:'+json.dumps(validate_palette(p), sort_keys=True)).encode()).hexdigest()[:12]
    return "PolyShell-Palette-" + digest


def toolkit_theme_root(paths):
    if paths.config == Paths.current().config:
        return Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'themes'
    return paths.config.parent / 'toolkit-themes'


def ini_settings(text, values, section_name="Settings"):
    """Update only owned GTK keys; preserve comments and unrelated sections."""
    heading = '['+section_name+']'
    match = re.search(r'(?m)^'+re.escape(heading)+r'\s*$', text)
    if not match:
        return text.rstrip() + '\n'+heading+'\n' + ''.join(key+'='+value+'\n' for key, value in values.items())
    start = match.end()
    next_section = re.search(r'(?m)^\[', text[start:])
    end = start + next_section.start() if next_section else len(text)
    section = text[start:end]
    for key, value in values.items():
        pattern = r'(?m)^' + re.escape(key) + r'\s*=.*$'
        if re.search(pattern, section): section = re.sub(pattern, key+'='+value, section)
        else: section = section.rstrip()+'\n'+key+'='+value+'\n'
    return text[:start] + section + text[end:]


def toolkit_files(paths, p, icon_name=None):
    result = {}
    config = paths.config.parent
    name = toolkit_theme_name(p)
    for version in ('3', '4'):
        template = (ROOT / 'assets/theme-templates' / ('gtk' + version + '.css')).read_text()
        body = template.split('\n', 1)[1] if version == '3' else template
        colors = sorted(set(HEX.findall(body)))
        symbols = ''.join('@define-color poly_c_' + color[1:] + ' ' + map_color(color, p) + ';\n' for color in colors)
        base = '@import url("resource:///org/gtk/libgtk/theme/' + ('Adwaita/gtk-contained-dark.css' if version == '3' else 'Default/gtk-dark.css') + '");\n'
        theme_css = base + symbols + HEX.sub(lambda m: map_color(m[0], p), body)
        theme_dir = toolkit_theme_root(paths) / name / ('gtk-' + version + '.0')
        result[theme_dir / 'gtk.css'] = theme_css
        result[theme_dir / 'gtk-dark.css'] = theme_css
        # The user provider is loaded once by GTK. Keep it palette-independent:
        # its symbolic colors resolve against the newly selected named theme.
        bridge = '/* Poly Shell: live symbolic colors supplied by the selected GTK theme. */\n'
        bridge += (HEX.sub(lambda m: '@poly_c_' + m[0][1:], body) if version == '3'
                   else HEX.sub(lambda m: map_color(m[0], p), body))
        if version == '4':
            # Libadwaita forces Adwaita-empty and cannot resolve named-theme symbols.
            bridge += '\nwindow.background { background-color: @window_bg_color; color: @window_fg_color; }\n'
        css = config / ('gtk-' + version + '.0') / 'poly-palette.css'
        result[css] = bridge
        entry = config / ('gtk-' + version + '.0') / 'gtk.css'
        if entry.is_symlink(): entry = entry.resolve()
        original = entry.read_text() if entry.exists() else ''
        marker = '@import url("' + str(css) + '");' if entry.parent != css.parent else '@import url("poly-palette.css");'
        if marker not in original: original = original.rstrip() + '\n' + marker + '\n'
        result[entry] = original
        settings = config / ('gtk-' + version + '.0') / 'settings.ini'
        if settings.is_symlink(): settings = settings.resolve()
        values = {'gtk-theme-name': name}
        if icon_name: values['gtk-icon-theme-name'] = icon_name
        result[settings] = ini_settings(settings.read_text() if settings.exists() else '', values)
    from .terminal_colors import config_files
    result.update(config_files(config, p))
    return result


def border_lua(p):
    return ('hl.config({ general = { col = { active_border = { colors = { "rgba('+p['accent'][1:]+'e6)", '
            '"rgba('+p['secondary'][1:]+'cc)" }, angle = 45 }, inactive_border = "rgba('+p['border'][1:]+'b3)" } } })\n')
