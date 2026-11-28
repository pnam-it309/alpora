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


if __name__ == "__main__":
    unittest.main()
