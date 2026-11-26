"""NetworkManager Wi-Fi connection and Mobile Hotspot controls for ALPORA."""
from __future__ import annotations

import json

from ..core.state import ConfigError, read_object


def hotspot_config(paths):
    target = paths.config / 'hotspot.json'
    if target.exists():
        try:
            data = read_object(target)
            if isinstance(data, dict):
                return {
                    'ssid': str(data.get('ssid', 'Alpora-Hotspot')),
                    'password': str(data.get('password', 'alporapassword')),
                }
        except Exception:
            pass
    return {'ssid': 'Alpora-Hotspot', 'password': 'alporapassword'}


def hotspot_status(paths):
    from . import desktop
    if not desktop.shutil.which('nmcli'):
        return {
            'hotspotAvailable': False,
            'hotspot': False,
            'hotspotSsid': 'Alpora-Hotspot',
            'hotspotPassword': 'alporapassword',
            'hotspotClients': 0,
        }
    cfg = hotspot_config(paths)
    is_active = False
    active_device = None
    try:
        res = desktop.command(['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'], check=False)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.strip().split(':')
                if len(parts) >= 3 and parts[1] in ('802-11-wireless', 'wifi'):
                    cname = parts[0]
                    if cname in ('Hotspot', cfg['ssid']):
                        is_active = True
                        active_device = parts[2]
                        break
                    mode_res = desktop.command(['nmcli', '-t', '-f', '802-11-wireless.mode', 'connection', 'show', cname], check=False)
                    if mode_res.returncode == 0 and 'ap' in mode_res.stdout.lower():
                        is_active = True
                        active_device = parts[2]
                        break
    except Exception:
        pass

    clients = 0
    if is_active and active_device:
        try:
            neigh = desktop.command(['ip', 'neigh', 'show', 'dev', active_device], check=False)
            if neigh.returncode == 0:
                clients = len([
                    entry for entry in neigh.stdout.splitlines()
                    if any(k in entry for k in ('REACHABLE', 'STALE', 'DELAY'))
                ])
        except (ConfigError, OSError):
            pass

    return {
        'hotspotAvailable': True,
        'hotspot': is_active,
        'hotspotSsid': cfg['ssid'],
        'hotspotPassword': cfg['password'],
        'hotspotClients': clients,
    }


def set_hotspot(paths, value):
    from . import desktop
    if not desktop.shutil.which('nmcli'):
        raise ConfigError('NetworkManager (nmcli) is required for Mobile Hotspot')
    cfg = hotspot_config(paths)

    if value and str(value).strip().startswith('{'):
        try:
            payload = json.loads(value)
            if not isinstance(payload, dict):
                raise ValueError
        except Exception as exc:
            raise ConfigError('Invalid hotspot configuration JSON') from exc

        if 'ssid' in payload:
            ssid = str(payload['ssid']).strip()
            if not ssid:
                raise ConfigError('Hotspot SSID cannot be empty')
            cfg['ssid'] = ssid
        if 'password' in payload:
            pwd = str(payload['password']).strip()
            if len(pwd) < 8:
                raise ConfigError('Hotspot password must be at least 8 characters')
            cfg['password'] = pwd
        desktop.atomic_json(paths.config / 'hotspot.json', cfg)
        if payload.get('active') is False:
            value = 'off'
        elif payload.get('active') is True:
            value = 'on'
        else:
            return

    current = desktop.hotspot_status(paths)
    if value in ('toggle', None, ''):
        value = 'off' if current['hotspot'] else 'on'

    if value not in ('on', 'off'):
        raise ConfigError("Hotspot value must be 'on', 'off', or configuration JSON")

    if value == 'on':
        desktop.command(['nmcli', 'radio', 'wifi', 'on'], check=False)
        chk = desktop.command(['nmcli', '-t', '-f', 'NAME', 'connection', 'show'], check=False)
        existing = [entry.strip() for entry in chk.stdout.splitlines() if entry.strip()]
        if 'Hotspot' in existing:
            desktop.command(['nmcli', 'connection', 'modify', 'Hotspot',
                     '802-11-wireless.ssid', cfg['ssid'],
                     '802-11-wireless-security.key-mgmt', 'wpa-psk',
                     '802-11-wireless-security.psk', cfg['password'],
                     '802-11-wireless.mode', 'ap',
                     '802-11-wireless.band', 'bg',
                     'ipv4.method', 'shared'])
            desktop.command(['nmcli', 'connection', 'up', 'Hotspot'])
        else:
            try:
                desktop.command(['nmcli', 'device', 'wifi', 'hotspot', 'ssid', cfg['ssid'], 'password', cfg['password']])
            except ConfigError:
                desktop.command(['nmcli', 'connection', 'add', 'type', 'wifi', 'con-name', 'Hotspot',
                         'autoconnect', 'no', 'ssid', cfg['ssid'],
                         '802-11-wireless.mode', 'ap', '802-11-wireless.band', 'bg',
                         'ipv4.method', 'shared',
                         'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', cfg['password']])
                desktop.command(['nmcli', 'connection', 'up', 'Hotspot'])
    elif value == 'off':
        chk = desktop.command(['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'], check=False)
        if chk.returncode == 0:
            for entry in chk.stdout.splitlines():
                parts = entry.strip().split(':')
                if len(parts) >= 2 and parts[1] in ('802-11-wireless', 'wifi'):
                    cname = parts[0]
                    if cname in ('Hotspot', cfg['ssid']):
                        desktop.command(['nmcli', 'connection', 'down', cname], check=False)
                    else:
                        mode_res = desktop.command(['nmcli', '-t', '-f', '802-11-wireless.mode', 'connection', 'show', cname], check=False)
                        if mode_res.returncode == 0 and 'ap' in mode_res.stdout.lower():
                            desktop.command(['nmcli', 'connection', 'down', cname], check=False)


def connect_wifi(value):
    from . import desktop
    if not desktop.shutil.which('nmcli'):
        raise ConfigError('NetworkManager (nmcli) is required to connect to Wi-Fi')
    try:
        payload = json.loads(value) if isinstance(value, str) else value
        if not isinstance(payload, dict):
            raise ValueError
    except Exception as exc:
        raise ConfigError('Invalid Wi-Fi connect JSON payload') from exc

    ssid = payload.get('ssid')
    if not ssid or not isinstance(ssid, str):
        raise ConfigError('SSID is required')
    if ssid.startswith('-') or any(c in ssid for c in ('\x00', '\r', '\n')):
        raise ConfigError('Invalid characters in SSID')
    password = payload.get('password', '')
    identity = payload.get('identity')
    hidden = payload.get('hidden', False)

    if identity:
        chk = desktop.command(['nmcli', '-t', '-f', 'NAME', 'connection', 'show'], check=False)
        existing = [entry.strip() for entry in chk.stdout.splitlines() if entry.strip()]
        if ssid in existing:
            desktop.command(['nmcli', 'connection', 'modify', ssid,
                     '802-1x.eap', 'peap',
                     '802-1x.phase2-auth', 'mschapv2',
                     '802-1x.identity', str(identity),
                     '802-1x.password', str(password)])
        else:
            args = ['nmcli', 'connection', 'add', 'type', 'wifi',
                    'con-name', ssid, 'ssid', ssid,
                    'wifi-sec.key-mgmt', 'wpa-eap',
                    '802-1x.eap', 'peap',
                    '802-1x.phase2-auth', 'mschapv2',
                    '802-1x.identity', str(identity),
                    '802-1x.password', str(password)]
            desktop.command(args)
        desktop.command(['nmcli', 'connection', 'up', ssid])
        return {'success': True, 'ssid': ssid}

    args = ['nmcli', 'device', 'wifi', 'connect', ssid]
    if password:
        args += ['password', str(password)]
    if hidden:
        args += ['hidden', 'yes']
    desktop.command(args)
    return {'success': True, 'ssid': ssid}
