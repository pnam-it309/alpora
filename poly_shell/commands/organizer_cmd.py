"""Command handler for local calendar, tasks, notes, and focus timer."""
import json
from ..organizer import organizer
from ..state import ConfigError


def handle_organizer(paths, args) -> int:
    try:
        payload = json.loads(args.payload)
    except ValueError as exc:
        raise ConfigError("Invalid organizer JSON") from exc
    print(json.dumps(organizer(paths, args.action, payload), ensure_ascii=False))
    return 0

