"""Maintainability guard: keep source files small enough to review."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 500
# Zero exceptions: every source file strictly under 500 lines.
ALLOWED = set()


class FileBudgetTests(unittest.TestCase):
    def test_no_source_file_exceeds_budget(self):
        offenders = []
        for base in ('poly_shell', 'shell'):
            for path in (ROOT / base).rglob('*'):
                if path.suffix not in ('.py', '.qml', '.js') or '__pycache__' in path.parts:
                    continue
                rel = path.relative_to(ROOT).as_posix()
                lines = len(path.read_text(encoding='utf-8', errors='replace').splitlines())
                if lines > LIMIT and rel not in ALLOWED:
                    offenders.append(f'{rel}: {lines} lines (limit {LIMIT})')
        self.assertFalse(offenders, 'Split these files:\n' + '\n'.join(offenders))


if __name__ == '__main__':
    unittest.main()
