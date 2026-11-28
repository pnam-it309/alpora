"""Unit tests for runtime watchdog, telemetry, and crash logging in poly_shell.watchdog."""
import json
import tempfile
import unittest
from pathlib import Path

from poly_shell.commands.parser import build_parser
from poly_shell.commands.watchdog_cmd import handle_watchdog, _ping_ipc_socket
from poly_shell.core.ipc_server import IPCServer
from poly_shell.state import Paths
from poly_shell.watchdog import CrashReporter, HeartbeatWatchdog, ProcessMonitor


class TestWatchdog(unittest.TestCase):
    def test_process_monitor_metrics(self):
        # Current python process metrics should resolve without error
        telemetry = ProcessMonitor.get_process_metrics()
        if telemetry is not None:
            self.assertGreater(telemetry.pid, 0)
            self.assertIsInstance(telemetry.rss_mb, float)
            self.assertGreaterEqual(telemetry.threads_count, 1)

    def test_heartbeat_watchdog_detects_stall(self):
        watchdog = HeartbeatWatchdog(heartbeat_timeout=0.05)
        self.assertFalse(watchdog.is_stalled())
        watchdog.beat()
        self.assertFalse(watchdog.is_stalled())

        import time
        time.sleep(0.12)
        self.assertTrue(watchdog.is_stalled())

    def test_crash_reporter_dump(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_paths = Paths(
                config=temp_path / "config",
                state=temp_path / "state",
                runtime=temp_path / "runtime",
            )
            fake_paths.state.mkdir(parents=True, exist_ok=True)

            CrashReporter.install(fake_paths)
            try:
                raise RuntimeError("Simulated test panic")
            except RuntimeError as exc:
                dump_file = CrashReporter._create_crash_dump(type(exc), exc, exc.__traceback__)

            self.assertTrue(dump_file.exists())
            data = json.loads(dump_file.read_text(encoding="utf-8"))
            self.assertEqual(data["exception"]["type"], "RuntimeError")
            self.assertIn("Simulated test panic", data["exception"]["message"])
            self.assertTrue(len(data["exception"]["traceback"]) > 0)

    def test_watchdog_parser(self):
        parser = build_parser("1.0.0")
        args = parser.parse_args(["watchdog"])
        self.assertEqual(args.command, "watchdog")
        self.assertEqual(args.action, "run")
        self.assertEqual(args.interval, 5.0)

        args = parser.parse_args(["watchdog", "status"])
        self.assertEqual(args.action, "status")

        args = parser.parse_args(["watchdog", "metrics"])
        self.assertEqual(args.action, "metrics")

        args = parser.parse_args(["watchdog", "run", "--interval", "2.0", "--timeout", "10.0", "--once"])
        self.assertEqual(args.action, "run")
        self.assertEqual(args.interval, 2.0)
        self.assertEqual(args.timeout, 10.0)
        self.assertTrue(args.once)

    def test_watchdog_cmd_metrics_and_status(self):
        import argparse
        import io
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_paths = Paths(
                config=temp_path / "config",
                state=temp_path / "state",
                runtime=temp_path / "runtime",
            )
            fake_paths.runtime.mkdir(parents=True, exist_ok=True)

            # Test metrics action
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                args = argparse.Namespace(action="metrics")
                code = handle_watchdog(fake_paths, args)
                self.assertEqual(code, 0)
                data = json.loads(fake_out.getvalue())
                self.assertIn("rss_mb", data)

            # Test status action when socket is inactive
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                args = argparse.Namespace(action="status")
                code = handle_watchdog(fake_paths, args)
                self.assertEqual(code, 1)
                data = json.loads(fake_out.getvalue())
                self.assertEqual(data["status"], "degraded")
                self.assertFalse(data["ipc_socket"]["responsive"])

            # Test status action when socket is active
            sock_path = fake_paths.runtime / "ipc.sock"
            server = IPCServer(socket_path=sock_path)
            server.start()
            try:
                import time
                time.sleep(0.05)
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    args = argparse.Namespace(action="status")
                    code = handle_watchdog(fake_paths, args)
                    self.assertEqual(code, 0)
                    data = json.loads(fake_out.getvalue())
                    self.assertEqual(data["status"], "healthy")
                    self.assertTrue(data["ipc_socket"]["responsive"])

                # Test run once
                args = argparse.Namespace(action="run", interval=0.1, timeout=0.5, once=True)
                code = handle_watchdog(fake_paths, args)
                self.assertEqual(code, 0)
            finally:
                server.stop()


if __name__ == "__main__":
    unittest.main()
