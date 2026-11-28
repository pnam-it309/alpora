"""CLI command handler for poly-shell systemd user service."""
from __future__ import annotations

import argparse
import subprocess
import sys

from ..core.state import Paths

SERVICE_UNIT = "poly-shell.service"
VALID_ACTIONS = ("status", "start", "stop", "restart", "logs", "enable", "disable")


def handle_service(paths: Paths, args: argparse.Namespace) -> int:
    """Handle `poly-shell service` CLI invocations.

    Supports actions: status, start, stop, restart, logs, enable, disable.
    """
    action = getattr(args, "action", "status") or "status"
    unit = getattr(args, "unit", SERVICE_UNIT) or SERVICE_UNIT

    if action not in VALID_ACTIONS:
        print(f"Unknown service action: {action}. Expected one of: {', '.join(VALID_ACTIONS)}", file=sys.stderr)
        return 1

    try:
        if action == "status":
            cmd = ["systemctl", "--user", "status", "--no-pager", unit]
            return subprocess.run(cmd).returncode

        if action in ("start", "stop", "restart", "enable", "disable"):
            cmd = ["systemctl", "--user", action, unit]
            return subprocess.run(cmd).returncode

        if action == "logs":
            lines = getattr(args, "lines", None) or 80
            cmd = ["journalctl", "--user", "-u", unit, "-n", str(lines)]
            if getattr(args, "follow", False):
                cmd.append("-f")
            else:
                cmd.append("--no-pager")
            return subprocess.run(cmd).returncode

    except (OSError, subprocess.SubprocessError) as exc:
        print(f"poly-shell service: {exc}", file=sys.stderr)
        return 1

    return 0
