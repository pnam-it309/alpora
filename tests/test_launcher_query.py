"""Unit tests for LauncherQuery JavaScript logic (Omni-Search math and unit conversions)."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JS_FILE = ROOT / "shell/logic/LauncherQuery.js"


def _eval_js(fn_name: str, arg: str) -> str:
    runner = """
    const fs = require("fs");
    let code = fs.readFileSync(process.argv[1], "utf8");
    code = code.replace(/^\\s*\\.pragma\\s+library\\s*;?/m, "");
    const fnName = process.argv[2];
    const inputArg = process.argv[3];
    eval(code + "; globalThis.__fn = " + fnName + ";");
    const res = globalThis.__fn(inputArg);
    process.stdout.write(res !== undefined && res !== null ? String(res) : "");
    """
    proc = subprocess.run(
        ["node", "-e", runner, str(JS_FILE), fn_name, arg],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


class LauncherQueryTests(unittest.TestCase):
    def test_evaluate_math_basic_arithmetic(self):
        self.assertEqual(_eval_js("evaluateMath", "2 + 2"), "4")
        self.assertEqual(_eval_js("evaluateMath", "100 - 35"), "65")
        self.assertEqual(_eval_js("evaluateMath", "12 * 12"), "144")
        self.assertEqual(_eval_js("evaluateMath", "100 / 4"), "25")
        self.assertEqual(_eval_js("evaluateMath", "15 % 4"), "3")

    def test_evaluate_math_explicit_equals(self):
        self.assertEqual(_eval_js("evaluateMath", "= 42"), "42")
        self.assertEqual(_eval_js("evaluateMath", "= 5 * 10"), "50")
        self.assertEqual(_eval_js("evaluateMath", "= 100"), "100")

    def test_evaluate_math_functions_and_constants(self):
        self.assertEqual(_eval_js("evaluateMath", "sqrt(144)"), "12")
        self.assertEqual(_eval_js("evaluateMath", "= sqrt(16) + 4"), "8")
        self.assertEqual(_eval_js("evaluateMath", "2 ^ 8"), "256")
        self.assertEqual(_eval_js("evaluateMath", "abs(-50)"), "50")
        self.assertEqual(_eval_js("evaluateMath", "sin(0)"), "0")
        self.assertEqual(_eval_js("evaluateMath", "round(4.6)"), "5")
        self.assertEqual(_eval_js("evaluateMath", "floor(4.9)"), "4")
        self.assertEqual(_eval_js("evaluateMath", "ceil(4.1)"), "5")
        self.assertTrue(_eval_js("evaluateMath", "pi * 2").startswith("6.283"))

    def test_evaluate_math_rejections_and_security(self):
        self.assertEqual(_eval_js("evaluateMath", ""), "")
        self.assertEqual(_eval_js("evaluateMath", "firefox"), "")
        self.assertEqual(_eval_js("evaluateMath", "hello world"), "")
        self.assertEqual(_eval_js("evaluateMath", "2; process.exit()"), "")
        self.assertEqual(_eval_js("evaluateMath", "alert('xss')"), "")
        self.assertEqual(_eval_js("evaluateMath", "10 / 0"), "")
        self.assertEqual(_eval_js("evaluateMath", "++--"), "")

    def test_evaluate_conversion_currencies(self):
        res = _eval_js("evaluateConversion", "100 USD to VND")
        self.assertEqual(res, "2540000.00 VND")
        self.assertIn("USD", _eval_js("evaluateConversion", "10 EUR to USD"))

    def test_evaluate_conversion_length(self):
        self.assertEqual(_eval_js("evaluateConversion", "5 km in m"), "5000 m")
        self.assertEqual(_eval_js("evaluateConversion", "100 cm as m"), "1 m")

    def test_evaluate_conversion_mass(self):
        self.assertEqual(_eval_js("evaluateConversion", "2 kg to g"), "2000 g")
        self.assertEqual(_eval_js("evaluateConversion", "5000 g in kg"), "5 kg")

    def test_evaluate_conversion_temperature(self):
        self.assertEqual(_eval_js("evaluateConversion", "100 c to f"), "212 °F")
        self.assertEqual(_eval_js("evaluateConversion", "32 f to c"), "0 °C")

    def test_evaluate_conversion_invalid(self):
        self.assertEqual(_eval_js("evaluateConversion", ""), "")
        self.assertEqual(_eval_js("evaluateConversion", "not a conversion"), "")
        self.assertEqual(_eval_js("evaluateConversion", "100 bananas to apples"), "")


if __name__ == "__main__":
    unittest.main()
