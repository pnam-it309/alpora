from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from poly_shell.organizer import organizer
from poly_shell.state import ConfigError, Paths


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.paths = Paths(root / "config", root / "state", root / "runtime")

    def test_concurrent_adds_and_day_boundaries_survive_reload(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda index: organizer(self.paths, "task-add", {"date": "2026-10-19", "title": f"Task {index}"}), range(12)))
        state = organizer(self.paths)
        self.assertEqual(len(state["tasks"]), 12)
        self.assertEqual(len({item["id"] for item in state["tasks"]}), 12)
        identifier = state["tasks"][0]["id"]
        organizer(self.paths, "task-toggle", {"id": identifier})
        self.assertTrue(organizer(self.paths)["tasks"][0]["done"])
        organizer(self.paths, "item-remove", {"id": identifier})
        self.assertEqual(len(organizer(self.paths)["tasks"]), 11)

    def test_invalid_date_time_and_payload_preserve_saved_data(self):
        organizer(self.paths)
        target = self.paths.state / "organizer.json"
        before = target.read_bytes()
        for payload in ({"date": "2026-02-30", "title": "Test", "time": "12:00"},
                        {"date": "2026-10-19", "title": "Test", "time": "25:61"},
                        {"date": "2026-10-19", "title": " ", "time": "12:00"}):
            with self.assertRaises(ConfigError): organizer(self.paths, "event-add", payload)
            self.assertEqual(target.read_bytes(), before)

    def test_timer_is_idempotent_and_tracks_wall_clock_after_restart(self):
        organizer(self.paths, "timer-start", now=100)
        self.assertEqual(organizer(self.paths, "timer-start", now=200)["timer"]["endsAt"], 1600)
        self.assertEqual(organizer(self.paths, "timer-pause", now=700)["timer"]["remaining"], 900)
        self.assertEqual(organizer(self.paths, "timer-start", now=1000)["timer"]["endsAt"], 1900)
        self.assertEqual(organizer(self.paths, now=2000)["timer"], {"duration": 1500, "remaining": 0, "endsAt": 0})
        self.assertEqual(organizer(self.paths, "timer-reset", now=2000)["timer"]["remaining"], 1500)

    def test_failed_write_and_corrupt_file_are_preserved(self):
        organizer(self.paths)
        target = self.paths.state / "organizer.json"
        before = target.read_bytes()
        with patch("poly_shell.state.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError): organizer(self.paths, "note", {"text": "important"})
        self.assertEqual(target.read_bytes(), before)
        target.write_text("corrupt")
        with self.assertRaises(ConfigError): organizer(self.paths)
        self.assertEqual(target.read_text(), "corrupt")

    def test_notes_and_events_keep_literal_text(self):
        note = "Заметка\n`$(not a command)`\n<script>literal text</script>"
        organizer(self.paths, "note", {"text": note})
        organizer(self.paths, "event-add", {"date": "2026-10-20", "time": "09:05", "title": "Созвон"})
        saved = organizer(self.paths)
        self.assertEqual(saved["note"], note)
        self.assertEqual(saved["events"][0]["date"], "2026-10-20")


if __name__ == "__main__": unittest.main()
