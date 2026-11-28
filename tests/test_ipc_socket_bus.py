"""Unit tests for Unix Domain Socket IPC Server, Zero-Fork RPC, and Event Bus."""
import json
from pathlib import Path
import socket
import tempfile
import time
import unittest

from poly_shell.core.ipc_server import IPCServer
from poly_shell.core.daemon import PolyShellDaemon
from poly_shell.contracts.base import ShellEventEnvelope


class TestIpcSocketBus(unittest.TestCase):
    """Test suite verifying Unix Domain Socket IPC communication and push broadcasting."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.socket_path = Path(self.temp_dir.name) / "test_ipc.sock"
        self.server = IPCServer(socket_path=self.socket_path)
        self.server.start()
        time.sleep(0.05)  # Allow accept loop thread to spin up

    def tearDown(self):
        self.server.stop()
        self.temp_dir.cleanup()

    def _create_client(self) -> socket.socket:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(self.socket_path))
        return sock

    def test_ping_pong_roundtrip(self):
        """Verify standard JSON-RPC ping request returns matching ID and pong data in <10ms."""
        client = self._create_client()
        try:
            req = {"id": 101, "action": "ping", "params": {}}
            client.sendall((json.dumps(req) + "\n").encode("utf-8"))

            raw = client.recv(4096).decode("utf-8")
            self.assertTrue(raw.endswith("\n"))
            resp = json.loads(raw.strip())

            self.assertEqual(resp.get("id"), 101)
            self.assertTrue(resp.get("success"))
            self.assertTrue(resp.get("data", {}).get("pong"))
        finally:
            client.close()

    def test_custom_handler_registration(self):
        """Verify registering action handler executes and returns results."""
        self.server.register_handler("math.add", lambda p: {"result": p.get("a", 0) + p.get("b", 0)})

        client = self._create_client()
        try:
            req = {"id": 202, "action": "math.add", "params": {"a": 40, "b": 2}}
            client.sendall((json.dumps(req) + "\n").encode("utf-8"))

            raw = client.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())

            self.assertEqual(resp.get("id"), 202)
            self.assertTrue(resp.get("success"))
            self.assertEqual(resp.get("data", {}).get("result"), 42)
        finally:
            client.close()

    def test_unknown_action_error(self):
        """Verify querying an unregistered action returns structured error without crashing."""
        client = self._create_client()
        try:
            req = {"id": 303, "action": "nonexistent.action", "params": {}}
            client.sendall((json.dumps(req) + "\n").encode("utf-8"))

            raw = client.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())

            self.assertEqual(resp.get("id"), 303)
            self.assertFalse(resp.get("success"))
            self.assertIn("Unknown action", resp.get("error", ""))
        finally:
            client.close()

    def test_malformed_json_handling(self):
        """Verify sending bad JSON returns structured error response."""
        client = self._create_client()
        try:
            client.sendall(b"not a json object\n")
            raw = client.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())

            self.assertFalse(resp.get("success"))
            self.assertIn("error", resp)
        finally:
            client.close()

    def test_event_broadcasting_multiple_clients(self):
        """Verify broadcast pushes event envelopes to all connected clients."""
        client1 = self._create_client()
        client2 = self._create_client()
        time.sleep(0.05)

        try:
            self.assertEqual(self.server.client_count, 2)

            envelope = ShellEventEnvelope(
                domain="audio",
                event="volume.changed",
                data={"volume": 75, "muted": False},
            )
            sent = self.server.broadcast(envelope)
            self.assertEqual(sent, 2)

            for c in [client1, client2]:
                raw = c.recv(4096).decode("utf-8")
                msg = json.loads(raw.strip())
                self.assertEqual(msg.get("domain"), "audio")
                self.assertEqual(msg.get("event"), "volume.changed")
                self.assertEqual(msg.get("data", {}).get("volume"), 75)
        finally:
            client1.close()
            client2.close()

    def test_client_disconnect_cleanup(self):
        """Verify server cleans up closed client socket upon next broadcast or connection."""
        client = self._create_client()
        time.sleep(0.05)
        self.assertEqual(self.server.client_count, 1)

        client.close()
        time.sleep(0.05)

        envelope = ShellEventEnvelope(domain="test", event="ping", data={})
        self.server.broadcast(envelope)

        time.sleep(0.05)
        self.assertEqual(self.server.client_count, 0)


class TestDaemonSocketIntegration(unittest.TestCase):
    """Test suite verifying PolyShellDaemon registers and serves socket endpoints."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.socket_path = Path(self.temp_dir.name) / "daemon.sock"
        self.daemon = PolyShellDaemon(socket_path=self.socket_path)
        self.daemon.ipc_server.start()
        time.sleep(0.05)

    def tearDown(self):
        self.daemon.ipc_server.stop()
        self.temp_dir.cleanup()

    def test_daemon_status_and_system_health(self):
        """Verify daemon registers system.status and system.health RPC routes."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(self.socket_path))

        try:
            req = {"id": 1, "action": "system.status", "params": {}}
            sock.sendall((json.dumps(req) + "\n").encode("utf-8"))

            raw = sock.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())

            self.assertEqual(resp.get("id"), 1)
            self.assertTrue(resp.get("success"))
            self.assertIn("services", resp.get("data", {}))
        finally:
            sock.close()

    def test_daemon_desktop_control_and_status(self):
        """Verify daemon routes desktop.control and desktop.status zero-fork RPCs."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(self.socket_path))

        try:
            req = {"id": 10, "action": "desktop.status", "params": {}}
            sock.sendall((json.dumps(req) + "\n").encode("utf-8"))

            raw = sock.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())
            self.assertEqual(resp.get("id"), 10)
            self.assertTrue(resp.get("success"))
            self.assertIn("brightness", resp.get("data", {}))

            req2 = {"id": 11, "action": "desktop.control", "params": {"action": "status"}}
            sock.sendall((json.dumps(req2) + "\n").encode("utf-8"))
            raw2 = sock.recv(4096).decode("utf-8")
            resp2 = json.loads(raw2.strip())
            self.assertEqual(resp2.get("id"), 11)
            self.assertTrue(resp2.get("success"))
            self.assertIn("brightness", resp2.get("data", {}))
        finally:
            sock.close()

    def test_daemon_widgets_organizer_and_timeline(self):
        """Verify daemon routes widgets.weather, organizer.request, and timeline.get/set."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(str(self.socket_path))

        try:
            # organizer.request
            req = {"id": 20, "action": "organizer.request", "params": {"action": "get", "payload": {}}}
            sock.sendall((json.dumps(req) + "\n").encode("utf-8"))
            raw = sock.recv(4096).decode("utf-8")
            resp = json.loads(raw.strip())
            self.assertEqual(resp.get("id"), 20)
            self.assertTrue(resp.get("success"))
            self.assertIn("events", resp.get("data", {}))

            # timeline.get
            req2 = {"id": 21, "action": "timeline.get", "params": {}}
            sock.sendall((json.dumps(req2) + "\n").encode("utf-8"))
            raw2 = sock.recv(4096).decode("utf-8")
            resp2 = json.loads(raw2.strip())
            self.assertEqual(resp2.get("id"), 21)
            self.assertTrue(resp2.get("success"))

            # widgets.weather
            req3 = {"id": 22, "action": "widgets.weather", "params": {}}
            sock.sendall((json.dumps(req3) + "\n").encode("utf-8"))
            raw3 = sock.recv(4096).decode("utf-8")
            resp3 = json.loads(raw3.strip())
            self.assertEqual(resp3.get("id"), 22)
            self.assertTrue(resp3.get("success"))
        finally:
            sock.close()

    def test_daemon_mutation_broadcasts(self):
        """Verify mutating actions (timeline.set, organizer mutations) broadcast push events."""
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.settimeout(2.0)
        listener.connect(str(self.socket_path))
        listener_stream = listener.makefile("r", encoding="utf-8")
        time.sleep(0.05)

        caller = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        caller.settimeout(2.0)
        caller.connect(str(self.socket_path))
        caller_stream = caller.makefile("r", encoding="utf-8")

        try:
            # organizer.request note mutation
            req = {"id": 50, "action": "organizer.request", "params": {"action": "note", "payload": {"text": "Broadcast test"}}}
            caller.sendall((json.dumps(req) + "\n").encode("utf-8"))

            # caller receives response matching id: 50 (ignoring any broadcast lines)
            resp_caller = None
            while True:
                line = caller_stream.readline()
                self.assertTrue(line, "Stream ended unexpectedly before response")
                parsed = json.loads(line.strip())
                if parsed.get("id") == 50:
                    resp_caller = parsed
                    break

            self.assertIsNotNone(resp_caller)
            self.assertTrue(resp_caller.get("success"))

            # listener receives broadcast event
            raw_listener = listener_stream.readline()
            self.assertTrue(raw_listener, "Listener stream ended before broadcast")
            msg_listener = json.loads(raw_listener.strip())
            self.assertEqual(msg_listener.get("domain"), "organizer")
            self.assertEqual(msg_listener.get("event"), "organizer.updated")
            self.assertEqual(msg_listener.get("data", {}).get("note"), "Broadcast test")
        finally:
            listener.close()
            caller.close()

    def test_concurrent_heavy_traffic_integrity(self):
        """Verify concurrent requests and push broadcasts do not corrupt JSON packet streams."""
        import threading

        errors = []
        completed = []

        def worker(worker_id):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            try:
                sock.connect(str(self.socket_path))
                stream = sock.makefile("r", encoding="utf-8")
                for i in range(5):
                    req_id = worker_id * 100 + i
                    payload = {"id": req_id, "action": "ping", "params": {}}
                    sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                    # Broadcast concurrently from server
                    self.daemon.ipc_server.broadcast(ShellEventEnvelope(domain="test", event="load", data={"id": req_id}))
                    while True:
                        line = stream.readline()
                        if not line:
                            errors.append(f"Worker {worker_id}: EOF before response")
                            return
                        data = json.loads(line.strip())
                        if data.get("id") == req_id:
                            break
                completed.append(worker_id)
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
            finally:
                sock.close()

        threads = [threading.Thread(target=worker, args=(w,)) for w in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        self.assertEqual(errors, [])
        self.assertEqual(len(completed), 6)


if __name__ == "__main__":
    unittest.main()
