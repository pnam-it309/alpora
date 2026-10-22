"""Missing optional applications must not look like a failed core installation."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from poly_shell import cli
from poly_shell.state import Paths


class ProgramDiagnosticsTests(unittest.TestCase):
    def diagnose(self,items):
        output=io.StringIO()
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            with patch.object(cli,'inventory',return_value=items),patch.object(cli,'runtime_check',return_value='test runtime'),redirect_stdout(output):
                code=cli.doctor(Paths(root/'config',root/'state',root/'runtime'))
        return code,output.getvalue()

    def test_missing_required_tool_fails_diagnostics(self):
        code,text=self.diagnose([dict(name='Core',package='core',purpose='Runtime',tools={'core':None},available=False,required=True)])
        self.assertEqual(code,1);self.assertIn('MISSING Core',text)

    def test_missing_optional_tool_names_affected_function_without_failing_core(self):
        code,text=self.diagnose([dict(name='Editor',package='editor',purpose='Network shortcut',tools={'editor':None},available=False,required=False)])
        self.assertEqual(code,0);self.assertIn('OPTIONAL MISSING Editor',text);self.assertIn('Network shortcut',text)

    def test_available_capability_is_reported(self):
        code,text=self.diagnose([dict(name='Core',package='core',purpose='Runtime',tools={'core':'/usr/bin/core'},available=True,required=True)])
        self.assertEqual(code,0);self.assertIn('OK Core',text)
