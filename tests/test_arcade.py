import json
from pathlib import Path
import tempfile
import unittest

from poly_shell.core.state import Paths
from poly_shell.services.arcade_service import (
    get_arcade_data,
    record_score,
    reset_scores,
    save_arcade_data,
)


class ArcadeServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        self.paths = Paths(root / "config", root / "state", root / "runtime")

    def test_default_arcade_data(self):
        data = get_arcade_data(self.paths)
        self.assertEqual(data["version"], 1)
        self.assertIn("catch", data["high_scores"])
        self.assertEqual(data["high_scores"]["catch"], 0)
        self.assertTrue(data["sound_fx"])

    def test_record_new_high_score(self):
        is_new, high = record_score(self.paths, "catch", 350)
        self.assertTrue(is_new)
        self.assertEqual(high, 350)

        # Lower score should not overwrite
        is_new_lower, high_lower = record_score(self.paths, "catch", 120)
        self.assertFalse(is_new_lower)
        self.assertEqual(high_lower, 350)

        # Higher score should update
        is_new_higher, high_higher = record_score(self.paths, "catch", 500)
        self.assertTrue(is_new_higher)
        self.assertEqual(high_higher, 500)

        data = get_arcade_data(self.paths)
        self.assertEqual(data["high_scores"]["catch"], 500)

    def test_reset_scores(self):
        record_score(self.paths, "catch", 400)
        record_score(self.paths, "retro", 250)
        reset_scores(self.paths)
        data = get_arcade_data(self.paths)
        self.assertEqual(data["high_scores"]["catch"], 0)
        self.assertEqual(data["high_scores"]["retro"], 0)

    def test_corrupt_file_recovery(self):
        arcade_file = self.paths.config / "arcade.json"
        arcade_file.parent.mkdir(parents=True, exist_ok=True)
        arcade_file.write_text("{ corrupt json ...", encoding="utf-8")
        data = get_arcade_data(self.paths)
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["high_scores"]["catch"], 0)


if __name__ == "__main__":
    unittest.main()
