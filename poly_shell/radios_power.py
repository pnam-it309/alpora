"""Power profiles and reversible radio blocking through installed system tools."""
import re
import shutil
import subprocess
from pathlib import Path

from .state import ConfigError, atomic_json, read_object, state_lock

PROFILES = ("power-saver", "balanced", "performance")


def power_status(run):
    data = {"powerProfilesAvailable": False, "powerProfiles": [], "powerProfile": "", "powerDegraded": ""}
    if not shutil.which("powerprofilesctl"):
        return data
    result = run(["powerprofilesctl", "list"], check=False)
    if result.returncode:
        return data
    for line in result.stdout.splitlines():
        match = re.fullmatch(r"\s*(\*)?\s*(power-saver|balanced|performance):\s*", line)
        if match:
            data["powerProfiles"].append(match[2])
            if match[1]: data["powerProfile"] = match[2]
        if line.strip().startswith("Degraded:"):
            reason = line.split(":", 1)[1].strip()
            if reason != "no": data["powerDegraded"] = reason
    data["powerProfilesAvailable"] = bool(data["powerProfile"] and data["powerProfiles"])
    return data


def set_profile(value, run):
    if value not in PROFILES:
        raise ConfigError("Неизвестный режим питания")
    available = power_status(run)
    if not available["powerProfilesAvailable"]:
        raise ConfigError("Служба power-profiles-daemon недоступна")
    if value not in available["powerProfiles"]:
        raise ConfigError("Этот режим не поддерживается устройством")
    run(["powerprofilesctl", "set", value])


def radios(root=Path("/sys/class/rfkill")):
    result = []
    for path in sorted(root.glob("rfkill*")):
        identifier = path.name.removeprefix("rfkill")
        if not identifier.isdigit(): continue
        try:
            result.append({"id": identifier, "type": (path / "type").read_text().strip(),
                           "name": (path / "name").read_text().strip(),
                           "soft": (path / "soft").read_text().strip() == "1",
                           "hard": (path / "hard").read_text().strip() == "1"})
        except OSError:
            continue  # A radio may disappear while the directory is being read.
    return result


def radio_status():
    devices = radios()
    return {"airplaneAvailable": bool(devices and shutil.which("rfkill")),
            "airplane": bool(devices) and all(item["soft"] or item["hard"] for item in devices),
            "airplaneHardwareBlocked": any(item["hard"] for item in devices)}


def snapshot(run):
    devices = radios()
    if not devices or not shutil.which("rfkill"):
        raise ConfigError("Радиомодули недоступны")
    nm = None
    if shutil.which("nmcli"):
        response = run(["nmcli", "-t", "-f", "WIFI,WWAN", "radio"], check=False)
        values = response.stdout.strip().split(":")
        if response.returncode == 0 and len(values) == 2 and all(value in ("enabled", "disabled") for value in values):
            nm = {"wifi": values[0] == "enabled", "wwan": values[1] == "enabled"}
    bluetooth = False
    if any(item["type"] == "bluetooth" and not item["soft"] and not item["hard"] for item in devices) and shutil.which("bluetoothctl"):
        result = run(["bluetoothctl", "--timeout", "3", "show"], check=False)
        bluetooth = result.returncode == 0 and bool(re.search(r"Powered:\s+yes", result.stdout))
    return {"schemaVersion": 1, "radios": devices, "networkManager": nm, "bluetoothPowered": bluetooth}


def valid_snapshot(data):
    if data.get("schemaVersion") != 1 or not isinstance(data.get("radios"), list):
        raise ConfigError("Повреждена сохранённая конфигурация радиомодулей; файл сохранён")
    for item in data["radios"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].isdigit() or not isinstance(item.get("type"), str) or not isinstance(item.get("name"), str) or type(item.get("soft")) is not bool:
            raise ConfigError("Повреждена запись радиомодуля; файл сохранён")
    nm = data.get("networkManager")
    if nm is not None and (not isinstance(nm, dict) or any(type(nm.get(key)) is not bool for key in ("wifi", "wwan"))):
        raise ConfigError("Повреждена конфигурация сети; файл сохранён")
    if type(data.get("bluetoothPowered")) is not bool:
        raise ConfigError("Повреждена конфигурация Bluetooth; файл сохранён")
    return data


def restore(data, run):
    """Restore by identity instead of treating a reused rfkill id as an old device."""
    valid_snapshot(data)
    failures = []
    def apply(args):
        try: run(args)
        except (ConfigError, OSError, subprocess.SubprocessError) as exc: failures.append(str(exc))
    current = {(item["id"], item["type"], item["name"]) for item in radios()}
    # NM may alter rfkill state, so restore exact kernel soft blocks afterward.
    if data["networkManager"] is not None:
        for kind in ("wifi", "wwan"):
            enabled = data["networkManager"][kind]
            apply(["nmcli", "radio", kind, "on" if enabled else "off"])
    for item in data["radios"]:
        if (item["id"], item["type"], item["name"]) in current:
            apply(["rfkill", "block" if item["soft"] else "unblock", item["id"]])
    if data["bluetoothPowered"] and any(item["type"] == "bluetooth" and not item["soft"] and (item["id"], item["type"], item["name"]) in current for item in data["radios"]):
        apply(["bluetoothctl", "--timeout", "3", "power", "on"])
    if failures:
        raise ConfigError("Не удалось полностью восстановить радиомодули: " + "; ".join(failures))


def set_airplane(paths, value, run):
    if value not in ("on", "off"):
        raise ConfigError("Авиарежим: допустимы on и off")
    target = paths.state / "airplane-restore.json"
    with state_lock(paths):
        if value == "on":
            if radio_status()["airplane"]: return
            data = snapshot(run)
            atomic_json(target, data)  # Recovery state exists before any radios change.
            try:
                if data["networkManager"] is not None:
                    run(["nmcli", "radio", "all", "off"])
                run(["rfkill", "block", "all"])
                if not radio_status()["airplane"]:
                    raise ConfigError("Не все радиомодули удалось отключить")
            except Exception:
                try:
                    restore(data, run)
                    target.unlink(missing_ok=True)
                except Exception:
                    pass  # Keep the snapshot so an off request can retry recovery.
                raise
        else:
            if target.exists():
                restore(read_object(target), run)
                target.unlink()
            else:
                # Mode may have been enabled outside this shell: no prior state.
                if not radio_status()["airplaneAvailable"]:
                    raise ConfigError("Радиомодули недоступны")
                if not radio_status()["airplane"]: return
                run(["rfkill", "unblock", "all"])
                if shutil.which("nmcli"): run(["nmcli", "radio", "all", "on"])
