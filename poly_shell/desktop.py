"""Small adapters for desktop tools without QML service bindings."""
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time
import uuid
import math

from .state import ConfigError, ROOT, atomic_json, read_object, state_lock
from .radios_power import power_status, radio_status, set_airplane, set_profile


def command(args, *, check=True):
    result = subprocess.run(args, capture_output=True, text=True, timeout=5)
    if check and result.returncode:
        raise ConfigError((result.stderr or result.stdout).strip() or f"{args[0]} failed")
    return result


def backlight_device(root=Path('/sys/class/backlight')):
    for path in sorted(root.iterdir()) if root.exists() else []:
        try:
            maximum = int((path / 'max_brightness').read_text())
            current = int((path / 'brightness').read_text())
            if maximum > 0:
                return path.name, max(0, min(100, round(current / maximum * 100)))
        except (OSError, ValueError):
            continue
    return None, 0


def status(paths):
    device, brightness = backlight_device()
    dnd = command(['makoctl', 'mode'], check=False) if shutil.which('makoctl') else None
    preference = paths.state / 'desktop.json'
    saved = read_object(preference) if preference.exists() else {}
    return {
        'brightnessAvailable': bool(device and shutil.which('brightnessctl')),
        'brightness': brightness,
        'dndAvailable': bool(dnd and dnd.returncode == 0),
        'dnd': bool(dnd and 'do-not-disturb' in dnd.stdout.split()),
        'nightLightAvailable': bool(shutil.which('hyprsunset')),
        'nightLight': bool(saved.get('nightLight', False)),
        **power_status(command),
        **radio_status(),
        'airplaneManaged': (paths.state / 'airplane-restore.json').exists(),
    }


def set_night_light(paths, enabled):
    if not shutil.which('hyprsunset'):
        raise ConfigError('Night Light requires hyprsunset')
    # The process starts with identity colors. Its IPC can then change temperature.
    alive = command(['pgrep', '-u', str(os.getuid()), '-x', 'hyprsunset'], check=False)
    if alive.returncode:
        paths.state.mkdir(parents=True, exist_ok=True)
        with (paths.state / 'hyprsunset.log').open('a') as log:
            subprocess.Popen(['hyprsunset', '--identity'], stdout=log, stderr=log, start_new_session=True)
        for _ in range(25):
            response = command(['hyprctl', 'hyprsunset', 'profile'], check=False)
            if response.returncode == 0 and 'error' not in response.stdout.lower():
                break
            time.sleep(.05)
    args = ['hyprctl', 'hyprsunset', 'temperature', '4500'] if enabled else ['hyprctl', 'hyprsunset', 'identity']
    response = command(args)
    if any(word in response.stdout.lower() for word in ('error', 'not found', "couldn't")):
        raise ConfigError(response.stdout.strip())
    atomic_json(paths.state / 'desktop.json', {'nightLight': enabled})


def restore_desktop(paths):
    """Reapply our saved Night Light preference when the shell starts."""
    preference = paths.state / 'desktop.json'
    if preference.exists() and read_object(preference).get('nightLight') is True:
        with state_lock(paths):
            set_night_light(paths, True)


def control(paths, action, value=None):
    if action == 'status':
        return status(paths)
    if action == 'brightness':
        try:
            percentage = int(value)
        except (ValueError, TypeError) as exc:
            raise ConfigError('Brightness must be an integer') from exc
        if not 5 <= percentage <= 100:
            raise ConfigError('Brightness must be between 5 and 100')
        device, _ = backlight_device()
        if not device:
            raise ConfigError('No controllable display backlight found')
        command(['brightnessctl', '-d', device, 'set', f'{percentage}%'])
    elif action == 'bluetooth':
        if value not in ('on', 'off'):
            raise ConfigError('Bluetooth state must be on or off')
        if value == 'on':
            command(['rfkill', 'unblock', 'bluetooth'])
        command(['bluetoothctl', '--timeout', '3', 'power', value])
        if value == 'off':
            command(['rfkill', 'block', 'bluetooth'])
    elif action == 'dnd':
        command(['makoctl', 'mode', '-t', 'do-not-disturb'])
    elif action == 'nightlight':
        with state_lock(paths):
            set_night_light(paths, not status(paths)['nightLight'])
    elif action == 'power-profile':
        set_profile(value, command)
    elif action == 'airplane':
        set_airplane(paths, value, command)
    else:
        raise ConfigError('Unsupported desktop action')
    return status(paths)


def wallpaper(paths, image=None, *, reset=False):
    with state_lock(paths):
        return _wallpaper(paths, image, reset=reset)


def validate_transition(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {'x', 'y'}:
        raise ConfigError('Неверная точка появления обоев')
    for coordinate in value.values():
        if type(coordinate) not in (int, float) or not math.isfinite(coordinate) or not 0 <= coordinate <= 1:
            raise ConfigError('Точка появления обоев должна быть внутри экрана')
    return value


def _animated_wallpaper(paths, image, saved, transition, seed=None):
    def executable(name):
        local = Path.home() / '.local/bin' / name
        return shutil.which(name) or (str(local) if local.is_file() else None)
    client = executable('awww') or executable('swww')
    daemon = executable('awww-daemon') or executable('swww-daemon')
    if not client or not daemon:
        raise ConfigError('Для анимации обоев требуется awww (или swww)')
    def send(image_path, origin=None):
        args = [client, 'img', str(image_path), '--resize', 'crop',
                '--transition-type', 'grow' if origin else 'none']
        if origin:
            # Explicit decimals distinguish relative coordinates from pixel values.
            args += ['--transition-pos', f"{origin['x']:.6f},{origin['y']:.6f}", '--invert-y',
                     '--transition-duration', '1.4', '--transition-fps', '60',
                     '--transition-bezier', '0.22,0.8,0.22,1']
        command(args)
    started = False
    if command([client, 'query'], check=False).returncode:
        launch = ['systemd-run', '--user', '--quiet', '--collect',
                  '--unit=poly-shell-animated-wallpaper', '--service-type=exec']
        for name in ('WAYLAND_DISPLAY', 'DISPLAY', 'XDG_RUNTIME_DIR'):
            if os.environ.get(name):
                launch.append('--setenv=' + name + '=' + os.environ[name])
        command(launch + [daemon, '--no-cache'])
        started = True
        for _ in range(40):
            if not command([client, 'query'], check=False).returncode:
                break
            time.sleep(.05)
        else:
            command(['systemctl', '--user', 'stop', 'poly-shell-animated-wallpaper'], check=False)
            raise ConfigError('Не удалось запустить анимацию обоев')
    old_image = seed or saved.get('image')
    previous = command(['pgrep', '-u', str(os.getuid()), '-x', 'swaybg'], check=False)
    try:
        if (started or seed is not None) and old_image and Path(old_image).is_file():
            send(old_image)
        send(image, transition)
        atomic_json(paths.config / 'wallpaper.json', {'image': str(image), 'renderer': 'animated'})
    except Exception:
        if started:
            command(['systemctl', '--user', 'stop', 'poly-shell-animated-wallpaper'], check=False)
        elif old_image and Path(old_image).is_file():
            send(old_image)
        raise
    for value in previous.stdout.split():
        try:
            os.kill(int(value), signal.SIGTERM)
        except ProcessLookupError:
            pass


def _wallpaper(paths, image=None, *, reset=False, quiet=False, transition=None, seed=None):
    transition = validate_transition(transition)
    preference = paths.config / 'wallpaper.json'
    previous_saved = read_object(preference) if preference.exists() else {}
    saved = read_object(preference) if preference.exists() and not reset and image is None else {}
    image = Path(image or saved.get('image') or ROOT / 'assets/wallpapers/alpine-dawn.png').expanduser().resolve()
    if image.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp') or not image.is_file():
        raise ConfigError('Выбери существующее изображение PNG, JPG или WebP')
    if not image.exists():
        raise ConfigError(f'Wallpaper is missing: {image}')
    if transition is not None or previous_saved.get('renderer') == 'animated':
        from .state import settings_for
        if settings_for(paths).get('reducedMotion'):
            transition = None
        _animated_wallpaper(paths, image, previous_saved, transition, seed)
        return
    previous = command(['pgrep', '-u', str(os.getuid()), '-x', 'swaybg'], check=False)
    # A detached child still belongs to the settings service's cgroup. Give the
    # renderer its own user unit so closing/restarting settings cannot kill it.
    unit = 'poly-shell-wallpaper-' + uuid.uuid4().hex
    launch = ['systemd-run', '--user', '--quiet', '--collect',
              '--unit=' + unit, '--service-type=exec',
              '--description=Poly Shell Wallpaper']
    for name in ('WAYLAND_DISPLAY', 'DISPLAY', 'XDG_RUNTIME_DIR'):
        if os.environ.get(name):
            launch.append('--setenv=' + name + '=' + os.environ[name])
    launch += ['swaybg', '-i', str(image), '-m', 'fill']
    command(launch)
    try:
        time.sleep(.25)
        active = command(['systemctl', '--user', 'is-active', '--quiet', unit], check=False)
        if active.returncode:
            raise ConfigError('Не удалось запустить обои; предыдущий фон сохранён. '
                              'Подробности: journalctl --user -u ' + unit)
        atomic_json(preference, {'image': str(image)})
    except Exception:
        command(['systemctl', '--user', 'stop', unit], check=False)
        raise
    for value in previous.stdout.split():
        try:
            os.kill(int(value), signal.SIGTERM)
        except ProcessLookupError:
            pass
    if not quiet: print(f'Static wallpaper: {image}')
