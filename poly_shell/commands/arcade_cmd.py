"""CLI command handler for ALPORA Desktop Arcade Engine."""
from __future__ import annotations

import json
import sys

from ..core.state import Paths
from ..services.arcade_service import (
    get_arcade_data,
    record_score,
    reset_scores,
)
from .panel_cmd import call_shell_ipc


def handle_arcade(paths: Paths, args) -> int:
    """Handle `poly-shell arcade` CLI invocations."""
    action = getattr(args, "action", "toggle")
    game = getattr(args, "game", "catch") or "catch"

    if action == "toggle":
        if not call_shell_ipc("toggleArcade"):
            # Quickshell may not be active; report clean fallback
            print("Arcade toggle requested via IPC", file=sys.stderr)
        return 0

    if action in ("open", "play"):
        if not call_shell_ipc("openArcade", game):
            print(f"Arcade launch requested for '{game}' via IPC", file=sys.stderr)
        return 0

    if action == "close":
        if not call_shell_ipc("closeArcade"):
            print("Arcade close requested via IPC", file=sys.stderr)
        return 0

    if action == "status":
        data = get_arcade_data(paths)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if action == "scores":
        data = get_arcade_data(paths)
        scores = data.get("high_scores", {})
        print("ALPORA Desktop Arcade — High Scores:")
        for g_name, val in scores.items():
            print(f"  • {g_name.capitalize()}: {val} pts")
        return 0

    if action == "reset-scores":
        reset_scores(paths)
        print("Arcade high scores reset to 0.")
        return 0

    if action == "record":
        score_val = getattr(args, "score", 0)
        is_new, high = record_score(paths, game, score_val)
        if is_new:
            print(f"★ NEW HIGH SCORE for {game}: {high} pts!")
        else:
            print(f"Score recorded: {score_val} pts (High score: {high} pts)")
        return 0

    print(f"Unknown arcade action: {action}", file=sys.stderr)
    return 1
