"""Persistent ring buffer and IPC event dispatcher for notification history."""
from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
import json
import logging
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional, Set, Union

from ..contracts.base import BaseDTO, ShellEventEnvelope
from .state import Paths

logger = logging.getLogger(__name__)


@dataclass
class NotificationItem(BaseDTO):
    """Standardized representation of an individual notification record."""

    id: Union[str, int]
    app_name: str = "System"
    summary: str = ""
    body: str = ""
    urgency: str = "normal"  # "low", "normal", "critical"
    timestamp: float = field(default_factory=time.time)
    app_icon: str = ""
    category: str = ""
    actions: Dict[str, str] = field(default_factory=dict)
    read: bool = False
    archived: bool = True

    @classmethod
    def sanitize(cls, data: Dict[str, Any]) -> "NotificationItem":
        """Instantiate item ensuring safe defaults and string conversions."""
        raw_id = data.get("id")
        if raw_id is None or str(raw_id).strip() == "":
            raw_id = f"notif_{int(time.time() * 1000)}_{os.getpid()}"

        urgency = str(data.get("urgency", "normal")).lower()
        if urgency not in ("low", "normal", "critical"):
            urgency = "normal"

        actions = data.get("actions", {})
        if not isinstance(actions, dict):
            actions = {}

        return cls(
            id=raw_id,
            app_name=str(data.get("app_name") or data.get("appName") or "System"),
            summary=str(data.get("summary") or ""),
            body=str(data.get("body") or ""),
            urgency=urgency,
            timestamp=float(data.get("timestamp") or time.time()),
            app_icon=str(data.get("app_icon") or data.get("appIcon") or ""),
            category=str(data.get("category") or ""),
            actions=actions,
            read=bool(data.get("read", False)),
            archived=bool(data.get("archived", True)),
        )


class NotificationHistory:
    """Thread-safe ring buffer with disk persistence and IPC event broadcasting."""

    DEFAULT_MAX_SIZE = 100

    def __init__(
        self,
        storage_path: Optional[Union[str, Path]] = None,
        max_size: int = DEFAULT_MAX_SIZE,
        ipc_server: Optional[Any] = None,
    ) -> None:
        self.max_size = max(1, int(max_size))
        self.storage_path = Path(storage_path) if storage_path else (Paths.current().state / "notification-history.json")
        self.ipc_server = ipc_server
        self._lock = threading.RLock()
        self._buffer: deque[Dict[str, Any]] = deque(maxlen=self.max_size)
        self._hidden_ids: Set[str] = set()
        self.load()

    def load(self) -> None:
        """Load history from disk, migrating older hidden ID maps if present."""
        with self._lock:
            self._buffer.clear()
            self._hidden_ids.clear()
            if not self.storage_path.exists():
                return
            try:
                content = self.storage_path.read_text(encoding="utf-8")
                if not content.strip():
                    return
                data = json.loads(content)
                if isinstance(data, dict):
                    raw_hidden = data.get("hidden", [])
                    if isinstance(raw_hidden, list):
                        self._hidden_ids = {str(item) for item in raw_hidden}

                    raw_items = data.get("items", [])
                    if isinstance(raw_items, list):
                        for item_data in raw_items:
                            if isinstance(item_data, dict):
                                sanitized = NotificationItem.sanitize(item_data).to_dict()
                                self._buffer.append(sanitized)
                elif isinstance(data, list):
                    for item_data in data:
                        if isinstance(item_data, dict):
                            sanitized = NotificationItem.sanitize(item_data).to_dict()
                            self._buffer.append(sanitized)
            except Exception as exc:
                logger.warning("Failed loading notification history from %s: %s", self.storage_path, exc)

    def save(self) -> bool:
        """Atomically persist ring buffer and hidden IDs to disk."""
        with self._lock:
            try:
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                payload = {
                    "version": 1,
                    "max_size": self.max_size,
                    "updated_at": time.time(),
                    "hidden": sorted(list(self._hidden_ids)),
                    "items": list(self._buffer),
                }
                serialized = json.dumps(payload, indent=2, ensure_ascii=False)
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w",
                    dir=str(self.storage_path.parent),
                    delete=False,
                    encoding="utf-8",
                )
                try:
                    temp_file.write(serialized)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                    temp_file.close()
                    os.replace(temp_file.name, str(self.storage_path))
                    return True
                except Exception:
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    raise
            except Exception as exc:
                logger.error("Failed saving notification history to %s: %s", self.storage_path, exc)
                return False

    def add(self, notification: Union[NotificationItem, Dict[str, Any]]) -> Dict[str, Any]:
        """Add notification to ring buffer, evicting oldest if max_size is exceeded."""
        with self._lock:
            raw_dict = notification.to_dict() if isinstance(notification, NotificationItem) else notification
            sanitized = NotificationItem.sanitize(raw_dict).to_dict()
            str_id = str(sanitized["id"])

            # Deduplicate by removing existing notification with identical ID
            self._buffer = deque(
                [item for item in self._buffer if str(item.get("id")) != str_id],
                maxlen=self.max_size,
            )
            self._buffer.append(sanitized)
            self.save()

            self._broadcast(
                "add",
                {"item": sanitized, "summary": self.get_summary()},
            )
            return sanitized

    def get_history(
        self,
        limit: Optional[int] = None,
        app: Optional[str] = None,
        unread_only: bool = False,
        query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent notifications ordered newest first, with optional filters."""
        with self._lock:
            items = list(reversed(self._buffer))
            if app:
                target_app = app.strip().lower()
                items = [i for i in items if i.get("app_name", "").lower() == target_app]
            if unread_only:
                items = [i for i in items if not i.get("read", False)]
            if query:
                q = query.strip().lower()
                items = [
                    i for i in items
                    if q in i.get("summary", "").lower()
                    or q in i.get("body", "").lower()
                    or q in i.get("app_name", "").lower()
                    or q in str(i.get("id", "")).lower()
                ]
            if limit is not None and limit > 0:
                items = items[:limit]
            return items

    def get_grouped_by_app(self, limit_per_app: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Group notifications by application name, ordered newest first."""
        with self._lock:
            groups: Dict[str, List[Dict[str, Any]]] = {}
            for item in reversed(self._buffer):
                app = item.get("app_name") or "System"
                if app not in groups:
                    groups[app] = []
                if limit_per_app is None or len(groups[app]) < limit_per_app:
                    groups[app].append(item)
            return groups

    def clear(self, app: Optional[str] = None) -> int:
        """Clear all notifications or only those originating from a specific application."""
        with self._lock:
            initial_count = len(self._buffer)
            if app is None:
                self._buffer.clear()
                cleared_count = initial_count
            else:
                target_app = app.strip().lower()
                retained = deque(
                    [i for i in self._buffer if i.get("app_name", "").lower() != target_app],
                    maxlen=self.max_size,
                )
                cleared_count = initial_count - len(retained)
                self._buffer = retained

            self.save()
            self._broadcast(
                "clear",
                {"app": app, "cleared_count": cleared_count, "summary": self.get_summary()},
            )
            return cleared_count

    def dismiss(self, notification_id: Union[str, int]) -> bool:
        """Dismiss single notification from history by ID."""
        with self._lock:
            str_id = str(notification_id)
            initial_count = len(self._buffer)
            self._buffer = deque(
                [i for i in self._buffer if str(i.get("id")) != str_id],
                maxlen=self.max_size,
            )
            removed = len(self._buffer) < initial_count
            if removed:
                self._hidden_ids.add(str_id)
                self.save()
                self._broadcast(
                    "dismiss",
                    {"id": notification_id, "summary": self.get_summary()},
                )
            return removed

    def mark_as_read(
        self,
        notification_id: Optional[Union[str, int]] = None,
        app: Optional[str] = None,
    ) -> int:
        """Mark single, per-app, or all notifications as read."""
        with self._lock:
            str_id = str(notification_id) if notification_id is not None else None
            app_lower = app.strip().lower() if app else None
            updated = 0
            for item in self._buffer:
                matches_id = str_id is None or str(item.get("id")) == str_id
                matches_app = app_lower is None or item.get("app_name", "").lower() == app_lower
                if matches_id and matches_app and not item.get("read", False):
                    item["read"] = True
                    updated += 1
            if updated > 0:
                self.save()
                self._broadcast(
                    "mark_read",
                    {"id": notification_id, "app": app, "updated": updated, "summary": self.get_summary()},
                )
            return updated

    def get_summary(self) -> Dict[str, Any]:
        """Calculate counts for total, unread, critical, and per-app distribution."""
        with self._lock:
            app_counts: Dict[str, int] = {}
            unread_count = 0
            critical_count = 0
            for item in self._buffer:
                app = item.get("app_name") or "System"
                app_counts[app] = app_counts.get(app, 0) + 1
                if not item.get("read", False):
                    unread_count += 1
                if item.get("urgency") == "critical":
                    critical_count += 1

            return {
                "total": len(self._buffer),
                "unread": unread_count,
                "critical": critical_count,
                "app_counts": app_counts,
                "apps": sorted(list(app_counts.keys())),
            }

    def _broadcast(self, action: str, data: Dict[str, Any]) -> None:
        """Broadcast real-time push event to connected IPC socket clients."""
        if not self.ipc_server or not getattr(self.ipc_server, "is_running", False):
            return
        envelope = ShellEventEnvelope(
            domain="notifications",
            event="notifications.updated",
            data={"action": action, **data},
        )
        try:
            self.ipc_server.broadcast(envelope)
        except Exception as exc:
            logger.debug("Push broadcast notifications.updated failed: %s", exc)

    def register_ipc_handlers(self, ipc_server: Any) -> None:
        """Register Zero-Fork JSON-RPC endpoints on IPCServer."""
        self.ipc_server = ipc_server

        def _handle_list(p: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "notifications": self.get_history(
                    limit=p.get("limit"),
                    app=p.get("app"),
                    unread_only=bool(p.get("unread_only", False)),
                    query=p.get("query"),
                ),
                "summary": self.get_summary(),
            }

        def _handle_grouped(p: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "groups": self.get_grouped_by_app(limit_per_app=p.get("limit_per_app")),
                "summary": self.get_summary(),
            }

        def _handle_add(p: Dict[str, Any]) -> Dict[str, Any]:
            item = p.get("notification") if isinstance(p.get("notification"), dict) else p
            return {"success": True, "item": self.add(item)}

        def _handle_clear(p: Dict[str, Any]) -> Dict[str, Any]:
            return {"success": True, "cleared": self.clear(app=p.get("app"))}

        def _handle_dismiss(p: Dict[str, Any]) -> Dict[str, Any]:
            return {"success": self.dismiss(notification_id=p.get("id"))}

        def _handle_mark_read(p: Dict[str, Any]) -> Dict[str, Any]:
            return {"success": True, "count": self.mark_as_read(notification_id=p.get("id"), app=p.get("app"))}

        ipc_server.register_handler("notifications.list", _handle_list)
        ipc_server.register_handler("notifications.grouped", _handle_grouped)
        ipc_server.register_handler("notifications.add", _handle_add)
        ipc_server.register_handler("notifications.clear", _handle_clear)
        ipc_server.register_handler("notifications.dismiss", _handle_dismiss)
        ipc_server.register_handler("notifications.mark_read", _handle_mark_read)
        ipc_server.register_handler("notifications.summary", lambda _p: self.get_summary())


_notification_history_singleton: Optional[NotificationHistory] = None
_singleton_lock = threading.Lock()


def get_notification_history(
    storage_path: Optional[Union[str, Path]] = None,
    max_size: int = NotificationHistory.DEFAULT_MAX_SIZE,
    ipc_server: Optional[Any] = None,
) -> NotificationHistory:
    """Retrieve or initialize global NotificationHistory instance."""
    global _notification_history_singleton
    with _singleton_lock:
        if _notification_history_singleton is None:
            _notification_history_singleton = NotificationHistory(
                storage_path=storage_path,
                max_size=max_size,
                ipc_server=ipc_server,
            )
        elif ipc_server and not _notification_history_singleton.ipc_server:
            _notification_history_singleton.ipc_server = ipc_server
        return _notification_history_singleton
