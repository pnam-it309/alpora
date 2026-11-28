"""Command handler for local calendar, tasks, notes, and focus timer."""
import json
from ..services.organizer import organizer
from ..core.state import ConfigError


def handle_organizer(paths, args) -> int:
    raw = getattr(args, "payload", "{}") or "{}"
    if args.action in ("import", "export") and not raw.strip().startswith("{"):
        payload = {"file": raw.strip()}
    else:
        try:
            payload = json.loads(raw)
        except ValueError as exc:
            raise ConfigError("Invalid organizer JSON") from exc
    result = organizer(paths, args.action, payload)
    print(json.dumps(result, ensure_ascii=False))
    return 0

