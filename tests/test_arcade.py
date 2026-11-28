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
        self.assertIn("fishing", data["high_scores"])
        self.assertEqual(data["high_scores"]["fishing"], 0)
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

    def test_record_fishing_score(self):
        is_new, high = record_score(self.paths, "fishing", 1450)
        self.assertTrue(is_new)
        self.assertEqual(high, 1450)

        data = get_arcade_data(self.paths)
        self.assertEqual(data["high_scores"]["fishing"], 1450)
        self.assertEqual(data["last_game"], "fishing")

    def test_reset_scores(self):
        record_score(self.paths, "catch", 400)
        record_score(self.paths, "fishing", 650)
        record_score(self.paths, "retro", 250)
        reset_scores(self.paths)
        data = get_arcade_data(self.paths)
        self.assertEqual(data["high_scores"]["catch"], 0)
        self.assertEqual(data["high_scores"]["fishing"], 0)
        self.assertEqual(data["high_scores"]["retro"], 0)

    def test_corrupt_file_recovery(self):
        arcade_file = self.paths.config / "arcade.json"
        arcade_file.parent.mkdir(parents=True, exist_ok=True)
        arcade_file.write_text("{ corrupt json ...", encoding="utf-8")
        data = get_arcade_data(self.paths)
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["high_scores"]["catch"], 0)
        self.assertEqual(data["high_scores"]["fishing"], 0)

    def test_cli_handle_arcade_play_and_record(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from poly_shell.commands.arcade_cmd import handle_arcade

        # CLI play fishing
        with patch("poly_shell.commands.arcade_cmd.call_shell_ipc", return_value=True) as mock_ipc:
            args = SimpleNamespace(action="play", game="fishing", score=0)
            ret = handle_arcade(self.paths, args)
            self.assertEqual(ret, 0)
            mock_ipc.assert_called_once_with("openArcade", "fishing")

        # CLI record fishing score
        args_record = SimpleNamespace(action="record", game="fishing", score=850)
        ret_record = handle_arcade(self.paths, args_record)
        self.assertEqual(ret_record, 0)
        data = get_arcade_data(self.paths)
        self.assertEqual(data["high_scores"]["fishing"], 850)

    def test_blitz_mode_persistence(self):
        data = get_arcade_data(self.paths)
        self.assertFalse(data.get("blitz_mode", False))
        data["blitz_mode"] = True
        save_arcade_data(self.paths, data)
        reloaded = get_arcade_data(self.paths)
        self.assertTrue(reloaded["blitz_mode"])

    def test_cli_scores_and_status(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import io
        from poly_shell.commands.arcade_cmd import handle_arcade

        record_score(self.paths, "fishing", 1200)
        record_score(self.paths, "catch", 800)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            args = SimpleNamespace(action="scores")
            ret = handle_arcade(self.paths, args)
            self.assertEqual(ret, 0)
            out = mock_out.getvalue()
            self.assertIn("Fishing: 1200 pts", out)
            self.assertIn("Catch: 800 pts", out)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            args = SimpleNamespace(action="status")
            ret = handle_arcade(self.paths, args)
            self.assertEqual(ret, 0)
            out_json = json.loads(mock_out.getvalue())
            self.assertEqual(out_json["high_scores"]["fishing"], 1200)

    def test_required_i18n_fishing_keys(self):
        locales_dir = Path(__file__).resolve().parents[1] / "assets" / "locales"
        required_keys = [
            "arcade.game_catch",
            "arcade.game_fishing",
            "arcade.blitz_mode",
            "arcade.blitz_time",
            "arcade.blitz_over",
            "arcade.fishing_cast_hint",
            "arcade.fishing_wait_hint",
            "arcade.fishing_bite_hint",
            "arcade.fishing_reel_hint",
            "arcade.fishing_caught",
            "arcade.fishing_escaped",
            "arcade.fish_ro",
            "arcade.fish_chep",
            "arcade.fish_hoi",
            "arcade.fish_than_thoai",
            "arcade.fish_specs",
            "arcade.fish_again",
            "arcade.play_again",
        ]
        for lang in ("en", "vi", "es", "ru"):
            file_path = locales_dir / f"{lang}.json"
            self.assertTrue(file_path.exists(), f"Missing locale file {lang}.json")
            data = json.loads(file_path.read_text(encoding="utf-8"))
            for k in required_keys:
                self.assertIn(k, data, f"Missing key '{k}' in {lang}.json")
                self.assertTrue(len(data[k].strip()) > 0, f"Empty translation for '{k}' in {lang}.json")


if __name__ == "__main__":
    unittest.main()
