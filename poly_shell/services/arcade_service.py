"""ALPORA Desktop Arcade Engine backend service and high-score persistence."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..core.state import ConfigError, Paths

def _default_arcade_state() -> dict[str, Any]:
    return {
        "version": 1,
        "high_scores": {
            "catch": 0,
            "fishing": 0,
        },
        "sound_fx": True,
        "last_game": "catch",
    }


DEFAULT_ARCADE_STATE: dict[str, Any] = _default_arcade_state()


def _arcade_path(paths: Paths) -> Path:
    """Return the configuration file path for arcade state."""
    config_dir = paths.config if hasattr(paths, "config") else Path.home() / ".config/poly-shell"
    return config_dir / "arcade.json"


def get_arcade_data(paths: Paths) -> dict[str, Any]:
    """Read and validate the arcade scores and preferences."""
    path = _arcade_path(paths)
    if not path.is_file():
        return _default_arcade_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return _default_arcade_state()
        if "high_scores" not in data or not isinstance(data["high_scores"], dict):
            data["high_scores"] = dict(_default_arcade_state()["high_scores"])
        else:
            for k, v in _default_arcade_state()["high_scores"].items():
                if k not in data["high_scores"]:
                    data["high_scores"][k] = v
        if "sound_fx" not in data:
            data["sound_fx"] = True
        if "last_game" not in data:
            data["last_game"] = "catch"
        return data
    except (json.JSONDecodeError, OSError):
        return _default_arcade_state()


def save_arcade_data(paths: Paths, data: dict[str, Any]) -> None:
    """Atomically write the arcade data to disk."""
    path = _arcade_path(paths)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp_path = path.with_suffix(".tmp")
    try:
        temp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_path.replace(path)
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise ConfigError(f"Failed to save arcade data: {exc}") from exc


def record_score(paths: Paths, game: str, score: int) -> tuple[bool, int]:
    """Record a score for a game; returns (is_new_high_score, current_high_score)."""
    if score < 0:
        score = 0
    data = get_arcade_data(paths)
    current_high = data["high_scores"].get(game, 0)
    is_new = score > current_high
    if is_new:
        data["high_scores"][game] = score
        data["last_game"] = game
        save_arcade_data(paths, data)
        return True, score
    return False, current_high


def reset_scores(paths: Paths) -> None:
    """Reset all high scores to zero."""
    data = get_arcade_data(paths)
    data["high_scores"] = {k: 0 for k in data["high_scores"]}
    save_arcade_data(paths, data)
