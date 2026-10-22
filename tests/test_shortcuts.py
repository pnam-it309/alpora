"""Shortcut conflicts, preservation, persistence and runtime rollback."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from poly_shell import shortcuts as s
from poly_shell.state import ConfigError, Paths, atomic_json

SOURCE = '''-- Existing personal configuration
local root = os.getenv("HOME") .. "/.config/hypr/"
local indicator = " && poly-shell osd "
run("SUPER + E", "nautilus --new-window")
run("SUPER + Return", 'kitty --config "' .. root .. 'kitty.conf"')
hl.bind("SUPER + R", hl.dsp.global("poly-shell:launcher"))
hl.bind("SUPER + C", hl.dsp.window.close())
run("XF86AudioMute", "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle" .. indicator .. "volume", { locked = true })
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
'''


class ShortcutTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        d = Path(temp.name)
        self.paths = Paths(d/'config/poly-shell',d/'state',d/'runtime')
        self.config = self.paths.config.parent/'hypr/hyprland.lua'
        self.config.parent.mkdir(parents=True)
        self.config.write_text(SOURCE)
        self.base = s.effective(self.paths)
        self.actual = [dict(modmask=s.signature(r['key'])[0],key=r['key'].split(' + ')[-1],keycode=0,description='',submap='') for r in self.base]
        self.reloads = 0
        self.fail = False
        self.missing = False
        self.errors = []
        mock = patch.object(s,'hypr',side_effect=self.hypr)
        mock.start();self.addCleanup(mock.stop)

    def hypr(self,*args):
        if args==('-j','binds'): return json.dumps(self.actual)
        if args==('-j','configerrors'): return json.dumps(self.errors)
        if args==('reload','config-only'):
            self.reloads += 1
            if self.fail and self.reloads==1:
                self.errors=['bad new configuration'];raise ConfigError('reload failed')
            self.errors=[]
            self.actual=[b for b in self.actual if not b.get('description','').startswith('Poly: ')]
            changes=s.stored(self.paths)
            for r in changes:
                if r['source']:self.actual=[b for b in self.actual if s.bind_signature(b)!=s.signature(r['source'])]
            for r in changes:
                if r['enabled'] and not self.missing:
                    mask,k=s.signature(r['key']);self.actual.append(dict(modmask=mask,key=k,keycode=0,description='Poly: '+r['title'],submap=''))
            return 'ok'
        raise AssertionError(args)

    def custom(self,key='SUPER + F8'):
        return dict(id='custom-test',source='',key=key,title='Тест',action='command',argument='foot',enabled=True,locked=False,repeat=False)

    def test_import_preserves_literal_commands_flags_and_leaves_mouse_external(self):
        self.assertEqual(len(self.base),5)
        terminal=next(r for r in self.base if r['key']=='SUPER + Return')
        self.assertEqual(terminal['argument'],'kitty --config "'+str(self.config.parent)+'/kitty.conf"')
        self.assertTrue(next(r for r in self.base if r['key']=='XF86AudioMute')['locked'])
        self.assertNotIn('mouse',json.dumps(self.base))

    def test_add_and_reopen_persists_only_changes_and_preserves_personal_config(self):
        values=self.base+[self.custom()]
        result=s.apply(self.paths,values,self.base)
        self.assertTrue(result['saved'])
        self.assertEqual(s.effective(self.paths),values)
        self.assertEqual(len(s.stored(self.paths)),1)
        self.assertTrue(self.config.read_text().startswith(SOURCE.rstrip()))
        self.assertEqual(self.config.read_text().count(s.HOOK),1)
        self.assertEqual((Path(result['backup'])/'hyprland.lua').read_text(),SOURCE)
        s.apply(self.paths,values,values)
        self.assertEqual(self.config.read_text().count(s.HOOK),1)

    def test_edit_disable_and_remove_custom_restore_on_reload(self):
        values=deepcopy(self.base);values[0]['key']='SUPER + F9';values[1]['enabled']=False
        s.apply(self.paths,values+[self.custom()],self.base)
        updated=s.effective(self.paths)
        s.apply(self.paths,values,updated)
        changes=s.stored(self.paths)
        self.assertEqual(len(changes),2)
        generated=self.config.with_name('poly-shell-shortcuts.lua').read_text()
        self.assertIn('hl.unbind("SUPER + E")',generated)
        self.assertNotIn('SUPER + F8',generated)
        self.assertFalse(s.effective(self.paths)[1]['enabled'])

    def test_duplicate_aliases_and_invalid_keys_rejected_before_writes(self):
        for shortcut in ('CTRL + SUPER + e','SUPER + SUPER + F1','SUPER + nonexistent-key','SUPER + NotAKeysym','SUPER + code:1','SUPER +', 'SUPER'):
            values=self.base+[self.custom(shortcut)]
            if shortcut=='CTRL + SUPER + e': values.append(dict(self.custom('SUPER + CTRL + E'),id='custom-other'))
            with self.subTest(shortcut=shortcut),self.assertRaises(ConfigError):s.apply(self.paths,values,self.base)
        self.assertEqual(self.reloads,0)
        self.assertEqual(self.config.read_text(),SOURCE)

    def test_external_and_submap_bindings_cannot_be_overwritten(self):
        for binding in [dict(modmask=64,key='F8',submap=''),dict(modmask=64,key='F8',submap='resize')]:
            self.actual.append(binding)
            with self.assertRaisesRegex(ConfigError,'Конфликт'):s.apply(self.paths,self.base+[self.custom()],self.base)
            self.actual.pop()
        self.assertEqual(self.reloads,0)

    def test_ambiguous_source_and_release_binding_cannot_be_disabled(self):
        duplicate=dict(self.actual[0],release=True);self.actual.append(duplicate)
        values=deepcopy(self.base);values[0]['enabled']=False
        with self.assertRaisesRegex(ConfigError,'Конфликт'):s.apply(self.paths,values,self.base)
        self.assertEqual(self.reloads,0)

    def test_stale_editor_rejected_without_overwriting_newer_state(self):
        s.apply(self.paths,self.base+[self.custom()],self.base)
        before=self.config.read_bytes()
        with self.assertRaisesRegex(ConfigError,'другом окне'):s.apply(self.paths,self.base,self.base)
        self.assertEqual(self.config.read_bytes(),before)

    def test_reload_failure_restores_all_files_and_reloads_previous_config(self):
        self.fail=True
        with self.assertRaisesRegex(ConfigError,'отменены'):s.apply(self.paths,self.base+[self.custom()],self.base)
        self.assertEqual(self.config.read_text(),SOURCE)
        self.assertFalse((self.paths.config/'shortcuts.json').exists())
        self.assertFalse(self.config.with_name('poly-shell-shortcuts.lua').exists())
        self.assertEqual(self.reloads,2)

    def test_missing_runtime_registration_also_rolls_back(self):
        self.missing=True
        with self.assertRaisesRegex(ConfigError,'не зарегистрировал'):s.apply(self.paths,self.base+[self.custom()],self.base)
        self.assertEqual(self.config.read_text(),SOURCE)
        self.assertEqual(self.reloads,2)

    def test_manual_generated_or_hook_changes_are_preserved(self):
        s.apply(self.paths,self.base+[self.custom()],self.base)
        generated=self.config.with_name('poly-shell-shortcuts.lua');generated.write_text('-- personal change\n')
        with self.assertRaisesRegex(ConfigError,'вручную'):s.apply(self.paths,s.effective(self.paths),s.effective(self.paths))
        self.assertEqual(generated.read_text(),'-- personal change\n')

    def test_command_and_title_cannot_escape_lua_string(self):
        item=self.custom();item['argument']='foot "); os.execute("bad") --'
        values=s.validate(self.base+[item],self.base)
        generated=s.generate([values[-1]])
        self.assertIn('foot \\"); os.execute(\\"bad\\") --',generated)
        item['argument']='foot\nother'
        with self.assertRaises(ConfigError):s.validate(self.base+[item],self.base)
        item['argument']='foot';item['title']='bad\nline'
        with self.assertRaises(ConfigError):s.validate(self.base+[item],self.base)

    def test_invalid_action_workspace_flags_source_and_payload_are_rejected(self):
        for changes in (dict(action='arbitrary-lua'),dict(action='workspace',argument='0'),dict(action='workspace',argument='1); bad'),
                        dict(action='global',argument='unknown'),dict(repeat=1),dict(source='SUPER + E')):
            with self.subTest(changes=changes),self.assertRaises(ConfigError):s.validate(self.base+[dict(self.custom(),**changes)],self.base)
        with self.assertRaises(ConfigError):s.validate(self.base[1:],self.base)

    def test_key_swap_unbinds_both_originals_before_registration(self):
        values=deepcopy(self.base);values[0]['key'],values[1]['key']=values[1]['key'],values[0]['key']
        result=s.apply(self.paths,values,self.base)
        self.assertTrue(result['saved'])
        lines=self.config.with_name('poly-shell-shortcuts.lua').read_text().splitlines()
        self.assertTrue(lines[1].startswith('hl.unbind'));self.assertTrue(lines[2].startswith('hl.unbind'))
        self.assertTrue(lines[3].startswith('hl.bind'))

    def test_corrupt_preferences_preserved_with_clear_error(self):
        for value in ({'version':1,'overrides':[{}]},{'version':1,'overrides':'bad'}):
            atomic_json(self.paths.config/'shortcuts.json',value)
            with self.assertRaises(ConfigError):s.effective(self.paths)
            self.assertTrue((self.paths.config/'shortcuts.json').exists())


if __name__=='__main__':unittest.main()
