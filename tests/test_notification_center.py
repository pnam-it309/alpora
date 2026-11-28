"""Unit tests for NotificationHistory ring buffer, persistence, and IPC event bus."""
import json
import os
from pathlib import Path
import socket
import tempfile
import time
import unittest

from poly_shell.core.notification_history import NotificationHistory, NotificationItem
from poly_shell.core.ipc_server import IPCServer


class TestNotificationHistoryBuffer(unittest.TestCase):
    """Test suite for NotificationHistory in-memory ring buffer, queries, and grouping."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_notifications.json"
        self.history = NotificationHistory(storage_path=self.storage_file, max_size=5)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_state(self):
        """Verify new history buffer starts empty and reports zero counts."""
        self.assertEqual(len(self.history.get_history()), 0)
        summary = self.history.get_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["unread"], 0)
        self.assertEqual(summary["critical"], 0)

    def test_add_and_ring_buffer_eviction(self):
        """Verify adding notifications beyond max_size evicts the oldest entries."""
        for i in range(8):
            self.history.add({
                "id": f"msg_{i}",
                "app_name": "Terminal" if i % 2 == 0 else "Browser",
                "summary": f"Notification {i}",
                "body": f"Details for message {i}",
                "urgency": "critical" if i == 7 else "normal",
            })

        items = self.history.get_history()
        self.assertEqual(len(items), 5)  # Constrained by max_size=5
        # Ordered newest first
        self.assertEqual(items[0]["id"], "msg_7")
        self.assertEqual(items[4]["id"], "msg_3")

        summary = self.history.get_summary()
        self.assertEqual(summary["total"], 5)
        self.assertEqual(summary["critical"], 1)

    def test_deduplication_by_id(self):
        """Verify re-adding an item with an existing ID updates it in place."""
        self.history.add({"id": "dup_1", "summary": "Original summary", "body": "Body 1"})
        self.history.add({"id": "dup_2", "summary": "Other item", "body": "Body 2"})
        self.history.add({"id": "dup_1", "summary": "Updated summary", "body": "Body 1 updated"})

        items = self.history.get_history()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], "dup_1")
        self.assertEqual(items[0]["summary"], "Updated summary")

    def test_query_and_filtering(self):
        """Verify filtering by application, unread state, query string, and limits."""
        self.history.add({"id": "1", "app_name": "Slack", "summary": "Meeting at 3pm", "read": False})
        self.history.add({"id": "2", "app_name": "Slack", "summary": "Lunch invitation", "read": True})
        self.history.add({"id": "3", "app_name": "Git", "summary": "Pipeline passed", "read": False})

        # Filter by app (case-insensitive)
        slack_items = self.history.get_history(app="slack")
        self.assertEqual(len(slack_items), 2)

        # Filter by unread
        unread = self.history.get_history(unread_only=True)
        self.assertEqual(len(unread), 2)

        # Filter by search query
        query_items = self.history.get_history(query="pipeline")
        self.assertEqual(len(query_items), 1)
        self.assertEqual(query_items[0]["id"], "3")

        # Limit
        limited = self.history.get_history(limit=1)
        self.assertEqual(len(limited), 1)

    def test_grouped_by_app(self):
        """Verify notifications group properly under their application names."""
        self.history.add({"id": "a1", "app_name": "Music", "summary": "Track 1"})
        self.history.add({"id": "b1", "app_name": "Chat", "summary": "Hello"})
        self.history.add({"id": "a2", "app_name": "Music", "summary": "Track 2"})

        groups = self.history.get_grouped_by_app()
        self.assertIn("Music", groups)
        self.assertIn("Chat", groups)
        self.assertEqual(len(groups["Music"]), 2)
        self.assertEqual(len(groups["Chat"]), 1)
        self.assertEqual(groups["Music"][0]["id"], "a2")  # Newest first

    def test_clear_all_and_per_app(self):
        """Verify clearing all notifications or clearing only a targeted app."""
        self.history.add({"id": "1", "app_name": "AppA", "summary": "A1"})
        self.history.add({"id": "2", "app_name": "AppB", "summary": "B1"})
        self.history.add({"id": "3", "app_name": "AppA", "summary": "A2"})

        # Clear only AppA
        cleared_appa = self.history.clear(app="AppA")
        self.assertEqual(cleared_appa, 2)
        remaining = self.history.get_history()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["app_name"], "AppB")

        # Clear remaining
        cleared_all = self.history.clear()
        self.assertEqual(cleared_all, 1)
        self.assertEqual(len(self.history.get_history()), 0)

    def test_dismiss_single_notification(self):
        """Verify dismissing individual notification item by ID."""
        self.history.add({"id": "d1", "summary": "Keep"})
        self.history.add({"id": "d2", "summary": "Remove me"})

        self.assertTrue(self.history.dismiss("d2"))
        self.assertFalse(self.history.dismiss("non_existent"))

        items = self.history.get_history()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "d1")

    def test_mark_as_read(self):
        """Verify marking single, per-app, and all notifications as read."""
        self.history.add({"id": "m1", "app_name": "Mail", "summary": "Mail 1", "read": False})
        self.history.add({"id": "m2", "app_name": "Mail", "summary": "Mail 2", "read": False})
        self.history.add({"id": "m3", "app_name": "Chat", "summary": "Chat 1", "read": False})

        # Mark single
        updated = self.history.mark_as_read(notification_id="m1")
        self.assertEqual(updated, 1)
        self.assertTrue(self.history.get_history(query="m1")[0]["read"])

        # Mark app
        updated_mail = self.history.mark_as_read(app="Mail")
        self.assertEqual(updated_mail, 1)

        # Mark all
        updated_all = self.history.mark_as_read()
        self.assertEqual(updated_all, 1)
        self.assertEqual(self.history.get_summary()["unread"], 0)


class TestNotificationHistoryPersistence(unittest.TestCase):
    """Test suite for atomic storage persistence and disaster recovery."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "subdir" / "notifications.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistence_across_instances(self):
        """Verify saved notifications and hidden IDs reload in new instance."""
        inst1 = NotificationHistory(storage_path=self.storage_file, max_size=10)
        inst1.add({"id": "p1", "app_name": "Editor", "summary": "File saved"})
        inst1.add({"id": "p2", "app_name": "Shell", "summary": "Build succeeded"})
        inst1.dismiss("p1")

        self.assertTrue(self.storage_file.exists())

        # Load second instance pointing to the same file
        inst2 = NotificationHistory(storage_path=self.storage_file, max_size=10)
        items = inst2.get_history()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "p2")
        self.assertIn("p1", inst2._hidden_ids)

    def test_recovery_from_corrupted_file(self):
        """Verify resilient fallback when notification storage file contains corrupt data."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.storage_file.write_text("{corrupt: json! invalid", encoding="utf-8")

        inst = NotificationHistory(storage_path=self.storage_file, max_size=10)
        self.assertEqual(len(inst.get_history()), 0)

        # Should recover and save cleanly
        inst.add({"id": "rec1", "summary": "Recovered"})
        self.assertTrue(inst.save())


class TestNotificationHistoryIpc(unittest.TestCase):
    """Test suite for IPC handlers, Zero-Fork RPC, and real-time push broadcasts."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.socket_path = Path(self.temp_dir.name) / "test_notif_ipc.sock"
        self.storage_file = Path(self.temp_dir.name) / "notif_storage.json"

        self.ipc_server = IPCServer(socket_path=self.socket_path)
        self.ipc_server.start()
        time.sleep(0.05)

        self.history = NotificationHistory(
            storage_path=self.storage_file,
            max_size=20,
            ipc_server=self.ipc_server,
        )
        self.history.register_ipc_handlers(self.ipc_server)

    def tearDown(self):
        self.ipc_server.stop()
        self.temp_dir.cleanup()

    def _create_client(self) -> socket.socket:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(self.socket_path))
        return sock

    def _send_request(self, client: socket.socket, action: str, params: dict, req_id: int = 1) -> dict:
        req = {"id": req_id, "action": action, "params": params}
        client.sendall((json.dumps(req) + "\n").encode("utf-8"))
        raw = client.recv(4096).decode("utf-8")
        lines = [line.strip() for line in raw.strip().split("\n") if line.strip()]
        for line in lines:
            data = json.loads(line)
            if data.get("id") == req_id:
                return data
        return {}

    def test_ipc_add_and_list_roundtrip(self):
        """Verify notifications.add and notifications.list over Unix socket."""
        client = self._create_client()
        try:
            # Add notification via IPC
            res_add = self._send_request(
                client,
                "notifications.add",
                {"id": "ipc_1", "app_name": "TestApp", "summary": "IPC Test", "body": "IPC Body"},
                req_id=10,
            )
            self.assertTrue(res_add.get("success"))
            self.assertEqual(res_add.get("data", {}).get("item", {}).get("id"), "ipc_1")

            # List notifications via IPC
            res_list = self._send_request(client, "notifications.list", {}, req_id=11)
            self.assertTrue(res_list.get("success"))
            notifs = res_list.get("data", {}).get("notifications", [])
            self.assertEqual(len(notifs), 1)
            self.assertEqual(notifs[0]["summary"], "IPC Test")

            # Summary via IPC
            res_summary = self._send_request(client, "notifications.summary", {}, req_id=12)
            self.assertTrue(res_summary.get("success"))
            self.assertEqual(res_summary.get("data", {}).get("total"), 1)
        finally:
            client.close()

    def test_ipc_grouped_and_clear(self):
        """Verify notifications.grouped and notifications.clear over IPC."""
        client = self._create_client()
        try:
            self._send_request(client, "notifications.add", {"id": "g1", "app_name": "Slack", "summary": "S1"}, 20)
            self._send_request(client, "notifications.add", {"id": "g2", "app_name": "Firefox", "summary": "F1"}, 21)

            # Grouped query
            res_grp = self._send_request(client, "notifications.grouped", {}, 22)
            groups = res_grp.get("data", {}).get("groups", {})
            self.assertIn("Slack", groups)
            self.assertIn("Firefox", groups)

            # Clear per app
            res_clr = self._send_request(client, "notifications.clear", {"app": "Slack"}, 23)
            self.assertTrue(res_clr.get("success"))
            self.assertEqual(res_clr.get("data", {}).get("cleared"), 1)

            # Dismiss item
            res_dism = self._send_request(client, "notifications.dismiss", {"id": "g2"}, 24)
            self.assertTrue(res_dism.get("success"))

            res_final = self._send_request(client, "notifications.list", {}, 25)
            self.assertEqual(len(res_final.get("data", {}).get("notifications", [])), 0)
        finally:
            client.close()

    def test_ipc_push_broadcasting(self):
        """Verify push broadcast notifications.updated is dispatched to connected clients."""
        client = self._create_client()
        try:
            # Trigger notification add on server
            self.history.add({"id": "push_1", "app_name": "Alert", "summary": "Realtime Push"})

            # Client should receive broadcast event envelope
            raw = client.recv(4096).decode("utf-8")
            event_line = raw.strip().split("\n")[0]
            event_obj = json.loads(event_line)

            self.assertEqual(event_obj.get("domain"), "notifications")
            self.assertEqual(event_obj.get("event"), "notifications.updated")
            self.assertEqual(event_obj.get("data", {}).get("action"), "add")
            self.assertEqual(event_obj.get("data", {}).get("item", {}).get("id"), "push_1")
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
