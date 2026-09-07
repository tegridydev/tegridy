import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('study_runner',Path(__file__).resolve().parents[1]/'runner.py')
runner=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_all_articles_have_unique_register_entries(self):
        entries=runner.registry()
        articles=[p for section in ['blog','research'] for p in (runner.ROOT/section).glob('*/*/*.md') if p.read_text().startswith('+++\n')]
        self.assertEqual({e['article'] for e in entries},{str(p.relative_to(runner.ROOT)) for p in articles})

    def test_artifact_corruption_and_nonfinite_metrics_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            runner.atomic_json(folder/'result.json',dict(scope='fixture',metrics={'accuracy':.5}))
            record=dict(status='completed',artifacts={'result.json':runner.digest(folder/'result.json')})
            runner.atomic_json(folder/'record.json',record)
            runner.verify_run(folder)
            (folder/'result.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'integrity'):runner.verify_run(folder)
            with self.assertRaises(ValueError):runner.atomic_json(folder/'bad.json',{'metric':float('nan')})
            self.assertFalse((folder/'bad.json').exists())
            self.assertFalse(list(folder.glob('*.tmp')))

    def test_resume_identity_changes_with_seed_and_protocol(self):
        entry=runner.registry()[0]
        key,_=runner.identity(entry,17,'cpu')
        self.assertNotEqual(key,runner.identity(entry,29,'cpu')[0])
        self.assertNotEqual(key,runner.identity(entry,17,'smoke')[0])
        changed=dict(entry,protocol=dict(entry['protocol'],version=99))
        self.assertNotEqual(key,runner.identity(changed,17,'cpu')[0])
