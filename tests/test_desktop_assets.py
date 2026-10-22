"""Desktop assets must preserve user themes, INI values and recovery state."""
import io
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from poly_shell import desktop_assets as assets
from poly_shell.state import ConfigError, Paths


class DesktopAssetsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.paths=Paths(self.root/'config/poly-shell',self.root/'state',self.root/'runtime')
        self.env=patch.dict(os.environ,{'XDG_DATA_HOME':str(self.root/'data'),'XDG_CACHE_HOME':str(self.root/'cache')})
        self.env.start();self.addCleanup(self.env.stop)
        self.hypr=self.root/'config/hypr/hyprland.lua';self.hypr.parent.mkdir(parents=True)
        self.hypr.write_text('-- personal config\nhl.monitor({output="",mode="preferred"})\n')

    def test_existing_user_theme_prevents_all_installation(self):
        existing=self.root/'data/icons/Bibata-Modern-Ice';existing.mkdir(parents=True)
        (existing/'personal').write_text('keep')
        with patch.object(assets,'download') as download, self.assertRaises(ConfigError):assets.install(self.paths)
        download.assert_not_called();self.assertEqual((existing/'personal').read_text(),'keep')
        self.assertFalse((self.root/'data/icons/Poly-Alpine').exists())

    def test_archive_cannot_escape_through_paths_or_symlinks(self):
        for name,link in (('../escape',''),('link','../../outside')):
            archive=self.root/'bad.tar'
            with tarfile.open(archive,'w') as t:
                info=tarfile.TarInfo(name)
                if link:info.type=tarfile.SYMTYPE;info.linkname=link;t.addfile(info)
                else:info.size=4;t.addfile(info,io.BytesIO(b'oops'))
            destination=self.root/'stage';destination.mkdir(exist_ok=True)
            with self.assertRaises(tarfile.FilterError):assets.unpack(archive,destination)
            self.assertFalse((self.root/'escape').exists())

    def test_cursor_settings_preserve_sections_and_managed_block_is_idempotent(self):
        gtk=self.root/'config/gtk-3.0/settings.ini';gtk.parent.mkdir()
        gtk.write_text('[Settings]\ngtk-icon-theme-name=Custom\ngtk-cursor-theme-name=Old\n[Other]\nkeep=yes\n')
        files=assets.settings_files(self.paths)
        self.assertIn('gtk-icon-theme-name=Custom',files[gtk]);self.assertIn('[Other]\nkeep=yes',files[gtk])
        self.assertEqual(files[gtk].count('gtk-cursor-theme-name='),1)
        self.assertTrue(files[self.hypr].startswith('-- personal config'))
        self.hypr.write_text(files[self.hypr]);self.assertNotIn(self.hypr,assets.settings_files(self.paths))
        self.hypr.write_text(self.hypr.read_text().replace('"24"','"32"'))
        with self.assertRaises(ConfigError):assets.settings_files(self.paths)

    def test_failed_runtime_apply_restores_files_and_records_backup(self):
        cursor=self.root/'data/icons/Bibata-Modern-Ice/cursors/left_ptr';cursor.parent.mkdir(parents=True);cursor.write_bytes(b'cursor')
        original=self.hypr.read_bytes();calls=[]
        def run(command,**kwargs):
            calls.append(command)
            if command[:2]==['gsettings','get']:
                return subprocess.CompletedProcess(command,0,stdout="'Old'\n" if command[-1]=='cursor-theme' else '32\n',stderr='')
            if command[:2]==['hyprctl','eval']:
                return subprocess.CompletedProcess(command,0,stdout='error',stderr='')
            return subprocess.CompletedProcess(command,0,stdout='',stderr='')
        with patch.dict(os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(assets.subprocess,'run',side_effect=run):
            with self.assertRaises(ConfigError):assets.apply(self.paths)
        self.assertEqual(self.hypr.read_bytes(),original)
        self.assertFalse((self.root/'config/gtk-3.0/settings.ini').exists())
        self.assertIn(['gsettings','set','org.gnome.desktop.interface','cursor-theme',"'Old'"],calls)
        self.assertEqual(len(list((self.paths.state/'backups').glob('*/manifest.json'))),1)

    def test_corrupt_download_is_rejected_before_install(self):
        spec={'sha256':'0'*64,'url':'https://example.test/asset'}
        with patch.object(assets.urllib.request,'urlopen',return_value=io.BytesIO(b'not a release')):
            with self.assertRaises(ConfigError):assets.download(spec,self.root/'cache')
        self.assertFalse((self.root/'cache'/spec['sha256']).exists())
        self.assertFalse(list((self.root/'cache').glob('*.part')))
