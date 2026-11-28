"""Unit tests for ArcadePhysics JavaScript logic (ALPORA Desktop Arcade Engine)."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JS_FILE = ROOT / "shell/logic/ArcadePhysics.js"


def _eval_js(expression: str) -> str:
    runner = """
    const fs = require("fs");
    let code = fs.readFileSync(process.argv[1], "utf8");
    code = code.replace(/^\\s*\\.pragma\\s+library\\s*;?/m, "");
    const expr = process.argv[2];
    eval(code + "; globalThis.__result = (" + expr + ");");
    const res = globalThis.__result;
    process.stdout.write(typeof res === "object" ? JSON.stringify(res) : String(res));
    """
    proc = subprocess.run(
        ["node", "-e", runner, str(JS_FILE), expression],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


class ArcadePhysicsTests(unittest.TestCase):
    def test_constants_defined(self):
        self.assertAlmostEqual(float(_eval_js("GRAVITY")), 0.44)
        self.assertAlmostEqual(float(_eval_js("FRICTION")), 0.995)
        self.assertAlmostEqual(float(_eval_js("RESTITUTION")), 0.78)
        self.assertAlmostEqual(float(_eval_js("MAX_VELOCITY")), 28.0)
        self.assertAlmostEqual(float(_eval_js("SLING_MULTIPLIER")), 0.18)

    def test_create_ball_state_default_and_custom(self):
        state_def = json.loads(_eval_js("createBallState()"))
        self.assertEqual(state_def["x"], 0)
        self.assertEqual(state_def["y"], 0)
        self.assertEqual(state_def["vx"], 4.5)
        self.assertEqual(state_def["vy"], -2.0)
        self.assertEqual(state_def["radius"], 18.0)

        state_custom = json.loads(_eval_js("createBallState(250, 480)"))
        self.assertEqual(state_custom["x"], 250)
        self.assertEqual(state_custom["y"], 480)
        self.assertEqual(state_custom["vx"], 4.5)
        self.assertEqual(state_custom["vy"], -2.0)

    def test_calculate_throw_velocity(self):
        vel_zero = json.loads(_eval_js("calculateThrowVelocity(0, 0)"))
        self.assertEqual(vel_zero["vx"], 0)
        self.assertEqual(vel_zero["vy"], 0)

        vel_normal = json.loads(_eval_js("calculateThrowVelocity(50, -50)"))
        self.assertAlmostEqual(vel_normal["vx"], 9.0)
        self.assertAlmostEqual(vel_normal["vy"], -9.0)

        # Clamping to MAX_VELOCITY (28.0)
        vel_clamped_high = json.loads(_eval_js("calculateThrowVelocity(300, 400)"))
        self.assertEqual(vel_clamped_high["vx"], 28.0)
        self.assertEqual(vel_clamped_high["vy"], 28.0)

        vel_clamped_low = json.loads(_eval_js("calculateThrowVelocity(-500, -600)"))
        self.assertEqual(vel_clamped_low["vx"], -28.0)
        self.assertEqual(vel_clamped_low["vy"], -28.0)

    def test_calculate_point_velocity(self):
        # Normal point velocity
        vel = json.loads(_eval_js("calculatePointVelocity(100, -100, 18)"))
        self.assertGreater(vel["vx"], 0)
        self.assertLessEqual(vel["vy"], -6.0)

        # Downward point must still retain minimum upward impulse (vy <= -6.0)
        vel_down = json.loads(_eval_js("calculatePointVelocity(0, 100, 18)"))
        self.assertLessEqual(vel_down["vy"], -6.0)

        # Zero delta handled safely without NaN or DivisionByZero
        vel_zero = json.loads(_eval_js("calculatePointVelocity(0, 0, 18)"))
        self.assertEqual(vel_zero["vx"], 0)
        self.assertLessEqual(vel_zero["vy"], -6.0)


if __name__ == "__main__":
    unittest.main()
