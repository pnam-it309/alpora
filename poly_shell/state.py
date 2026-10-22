"""Validated settings and atomic, serialized profile changes (standard library only)."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODES = ("work", "vibe")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Paths:
    config: Path
    state: Path
    runtime: Path

    @classmethod
    def current(cls):
        home = Path.home()
        return cls(
            Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "poly-shell",
            Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")) / "poly-shell",
            Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")) / "poly-shell",
        )

    @property
    def session(self):
        return self.state / "session.json"


def read_object(path):
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigError(f"Expected a JSON object in {path}")
    return value


def atomic_json(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def defaults():
    return {
        "schemaVersion": 1,
        "apps": {
            "terminal": ["foot" if shutil.which("foot") else "kitty"],
            "launcher": ["fuzzel"],
            "audio": ["pavucontrol"],
            "lock": ["hyprlock"],
            "network": ["nm-connection-editor"],
        },
        "bar": {"height": 40, "workspaceCount": 4, "fontFamily": "Noto Sans", "fontSize": 13,
                "margin": 20, "top": 12},
        "reducedMotion": False,
    }


def integer(value, minimum, maximum, name):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ConfigError(f"{name} must be an integer between {minimum} and {maximum}")


def settings_for(paths):
    target = paths.config / "settings.json"
    if not target.exists():
        atomic_json(target, defaults())
    data = merge(defaults(), read_object(target))
    if data.get("schemaVersion") != 1:
        raise ConfigError("Unsupported settings schemaVersion")
    apps = data.get("apps")
    if not isinstance(apps, dict):
        raise ConfigError("apps must be an object")
    for key in ("terminal", "launcher", "audio", "lock"):
        command = apps.get(key)
        if not isinstance(command, list) or not command or any(
            not isinstance(part, str) or not part or "\0" in part for part in command
        ):
            raise ConfigError(f"apps.{key} must be a nonempty array of command arguments")
    bar = data.get("bar")
    if not isinstance(bar, dict):
        raise ConfigError("bar must be an object")
    integer(bar.get("height"), 32, 80, "bar.height")
    integer(bar.get("workspaceCount"), 1, 10, "bar.workspaceCount")
    integer(bar.get("fontSize"), 10, 24, "bar.fontSize")
    integer(bar.get("margin"), 0, 64, "bar.margin")
    integer(bar.get("top"), 0, 64, "bar.top")
    if not isinstance(bar.get("fontFamily"), str) or not bar["fontFamily"].strip():
        raise ConfigError("bar.fontFamily must be a nonempty string")
    if type(data.get("reducedMotion")) is not bool:
        raise ConfigError("reducedMotion must be true or false")
    return data


def profile_for(paths, mode):
    if mode not in MODES:
        raise ConfigError(f"Unknown mode: {mode}")
    data = read_object(ROOT / "profiles" / f"{mode}.json")
    override = paths.config / "profiles" / f"{mode}.json"
    if override.exists():
        data = merge(data, read_object(override))
    if not isinstance(data.get("label"), str) or not data["label"].strip():
        raise ConfigError("profile.label must be a nonempty string")
    palette = data.get("palette")
    if not isinstance(palette, dict):
        raise ConfigError("profile.palette must be an object")
    for key in ("background", "surface", "text", "muted", "accent"):
        if not isinstance(palette.get(key), str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", palette[key]):
            raise ConfigError(f"palette.{key} must be a #RRGGBB color")
    integer(data.get("motionMs"), 0, 300, "profile.motionMs")
    return data


@contextmanager
def state_lock(paths):
    paths.state.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (paths.state / "state.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def current_mode(paths):
    if not paths.session.exists():
        return "work"
    data = read_object(paths.session)
    if data.get("schemaVersion") != 1 or data.get("mode") not in MODES:
        raise ConfigError(f"Invalid saved session in {paths.session}; preserved for recovery")
    return data["mode"]


def appearance_for(paths):
    """Resolve visual assets separately from behavior modes, with safe fallback."""
    from .themes import resolve_appearance
    return resolve_appearance(paths)


def update_session(paths, requested=None):
    from .visual import visual_for
    with state_lock(paths):
        old = current_mode(paths)
        mode = ("vibe" if old == "work" else "work") if requested == "toggle" else (requested or old)
        snapshot = {
            "schemaVersion": 1,
            "mode": mode,
            "profile": profile_for(paths, mode),
            "settings": settings_for(paths),
            "appearance": appearance_for(paths),
            "visual": visual_for(paths),
        }
        atomic_json(paths.session, snapshot)
        return snapshot
