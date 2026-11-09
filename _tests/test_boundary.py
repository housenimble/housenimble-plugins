"""Prevent accidental inclusion of native core source/builds/history in this proposal."""
from pathlib import Path
import json
import os
import unittest
import importlib.util
import tempfile

ROOT=Path(__file__).resolve().parents[1]

class PublicBoundary(unittest.TestCase):
    def test_no_core_or_private_build_files(self):
        forbidden={'.c','.cc','.cpp','.h','.hpp','.o','.a','.bin','.elf','.map','.pem','.key'}
        for directory, folders, files in os.walk(ROOT, followlinks=False):
            # This checkout owns its root Git database; copied/nested history is forbidden.
            if Path(directory) == ROOT:
                if '.git' in folders:folders.remove('.git')
                if '.git' in files:files.remove('.git')
            for name in folders + files:
                p = Path(directory) / name
                with self.subTest(path=str(p.relative_to(ROOT))):
                    self.assertNotIn(p.name,{'.git','.pio','.env','credentials.json'})
                    self.assertFalse(p.is_symlink())
                    self.assertNotIn(p.suffix.lower(),forbidden)

    def test_only_verified_plugins_are_installable(self):
        catalog=json.loads((ROOT/'catalog.json').read_text())
        self.assertEqual(catalog['installable'],['flight','consumption'])
        for name in catalog['installable']:
            self.assertTrue((ROOT/name/'main.lua').is_file())
            self.assertTrue((ROOT/name/'plugin.json').is_file())
            self.assertNotIn(name,catalog['plannedPlugins'])
        # Release metadata must still identify the exact physically attested
        # public package. This checks integrity, not the truth of human evidence.
        result=json.loads((ROOT/'consumption/tests/device-result.json').read_text())
        self.assertEqual(result['result'],'passed-scoped-physical-smoke')
        self.assertTrue(all(result['ownerConfirmed'].values()))
        self.assertEqual(result['usb']['uploads'],2)
        self.assertEqual(result['usb']['stops'],2)
        for field in ['luaBytesAfterEachStop','mediaBytesAfterEachStop','widgetsAfterEachStop']:
            self.assertEqual(result['usb'][field],0)
        self.assertEqual(result['hostCapabilities'],dict(consumptionData=1,pieChart=1,settingsSchema=1))
        spec=importlib.util.spec_from_file_location('release_package_validator',ROOT/'_tools/validate_plugin.py')
        validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as folder:
            digest=validator.package(ROOT/'consumption',Path(folder)/'consumption.hnplugin')
        self.assertEqual(digest,result['packageSha256'])
        self.assertEqual(catalog['status'],'released')
        for name in catalog['plannedPlugins']:
            folder=ROOT/name
            self.assertTrue((folder/'README.md').is_file())
            self.assertTrue((folder/'DEVICE-TEST.md').is_file())
            schema=json.loads((folder/'config.schema.json').read_text())
            self.assertIn('country',schema['properties'])
            self.assertFalse((folder/'main.lua').exists())

if __name__=='__main__':unittest.main()
