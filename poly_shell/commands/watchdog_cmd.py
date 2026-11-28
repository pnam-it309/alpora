"""CLI command handler for ALPORA runtime watchdog and health monitoring."""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import signal
import socket
import sys
import time
from typing import Any, Dict, Optional

from ..core.state import Paths
from ..core.watchdog import CrashReporter, HeartbeatWatchdog, ProcessMonitor

logger = logging.getLogger(__name__)


def _ping_ipc_socket(socket_path: Path, timeout: float = 2.0) -> Dict[str, Any]:
    """Send ping to the Unix Domain Socket IPC server and return response dict."""
    if not socket_path.exists():
        return {"ok": False, "error": f"Socket does not exist: {socket_path}"}

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(str(socket_path))
        payload = json.dumps({"id": 1, "action": "ping", "params": {}}) + "\n"
        sock.sendall(payload.encode("utf-8"))
        raw = sock.recv(4096).decode("utf-8", errors="replace")
        resp = json.loads(raw.strip())
        return {"ok": bool(resp.get("success")), "data": resp.get("data", {})}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        try:
            sock.close()
        except OSError:
            pass


def handle_watchdog(paths: Paths, args: argparse.Namespace) -> int:
    """Handle `poly-shell watchdog` CLI commands."""
    action = getattr(args, "action", "run") or "run"
    runtime_dir = paths.runtime if hasattr(paths, "runtime") and paths.runtime else (
        Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "poly-shell"
    )
    socket_path = runtime_dir / "ipc.sock"

    if action in ("check", "status"):
        metrics = ProcessMonitor.get_process_metrics()
        ipc_res = _ping_ipc_socket(socket_path)
        status_report = {
            "status": "healthy" if ipc_res.get("ok") else "degraded",
            "ipc_socket": {
                "path": str(socket_path),
                "responsive": ipc_res.get("ok", False),
                "error": ipc_res.get("error"),
            },
            "metrics": {
                "rss_mb": metrics.rss_mb if metrics else None,
                "threads": metrics.threads_count if metrics else None,
                "uptime_seconds": metrics.uptime_seconds if metrics else None,
            } if metrics else None,
            "timestamp": time.time(),
        }
        print(json.dumps(status_report, indent=2))
        return 0 if ipc_res.get("ok") else 1

    if action == "metrics":
        metrics = ProcessMonitor.get_process_metrics()
        if metrics:
            print(json.dumps({
                "pid": metrics.pid,
                "name": metrics.name,
                "rss_mb": metrics.rss_mb,
                "threads_count": metrics.threads_count,
                "status": metrics.status,
                "uptime_seconds": metrics.uptime_seconds,
            }, indent=2))
            return 0
        print(json.dumps({"error": "Unable to read process metrics"}), file=sys.stderr)
        return 1

    if action == "run":
        interval = getattr(args, "interval", 5.0) or 5.0
        stall_timeout = getattr(args, "timeout", 15.0) or 15.0
        once = getattr(args, "once", False)

        watchdog = HeartbeatWatchdog(heartbeat_timeout=stall_timeout)
        running = True

        def _sig_handler(sig, frame):
            nonlocal running
            running = False

        try:
            signal.signal(signal.SIGINT, _sig_handler)
            signal.signal(signal.SIGTERM, _sig_handler)
        except (ValueError, AttributeError):
            pass

        print(f"ALPORA Watchdog started (interval={interval}s, timeout={stall_timeout}s, socket={socket_path})")

        consecutive_stalls = 0
        while running:
            res = _ping_ipc_socket(socket_path, timeout=min(2.0, interval))
            if res.get("ok"):
                watchdog.beat()
                consecutive_stalls = 0
            else:
                if watchdog.is_stalled():
                    consecutive_stalls += 1
                    logger.warning("ALPORA Shell watchdog detected stall (%d consecutive checks)", consecutive_stalls)

            if once:
                break

            time.sleep(interval)

        return 0

    print(f"Unknown watchdog action: {action}", file=sys.stderr)
    return 1
