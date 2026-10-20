"""Dependency provenance must cover the libraries that affect cached outputs."""
import importlib.metadata
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from packaging.requirements import Requirement
from pisa.environment import DISTRIBUTIONS,package_versions
from pisa.pipeline import fingerprint


def canonical(name):
    return re.sub(r'[-_.]+','-',name).lower()


class DependencyProvenance(unittest.TestCase):
    def test_pins_cover_observed_active_dependency_closure(self):
        root=Path(__file__).resolve().parents[1]
        lines=(root/'requirements.txt').read_text().splitlines()
        declared=[Requirement(line) for line in lines if line.strip() and not line.startswith('#')]
        expected={canonical(name) for name in DISTRIBUTIONS}
        self.assertEqual({canonical(req.name) for req in declared},expected)
        self.assertEqual(len(declared),len(expected))
        self.assertTrue(all(str(req.specifier).startswith('==') for req in declared))
        # Distribution metadata is inspected; no numerical package is imported.
        for name in DISTRIBUTIONS:
            for value in importlib.metadata.requires(name) or []:
                req=Requirement(value)
                if req.marker is None or req.marker.evaluate({'extra':''}):
                    self.assertIn(canonical(req.name),expected,(name,value))

    def test_transitive_version_change_invalidates_cache_fingerprint(self):
        original=importlib.metadata.version
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'data/manifests').mkdir(parents=True)
            (root/'data/manifests/inputs.json').write_text('[]')
            config=root/'config.yaml';config.write_text('seed: 1')
            before=fingerprint(root,config)
            def changed(name):
                return 'different-fonttools-version' if name=='fonttools' else original(name)
            with patch('pisa.environment.importlib.metadata.version',side_effect=changed):
                self.assertNotEqual(before,fingerprint(root,config))

    def test_missing_distribution_is_explicit(self):
        original=importlib.metadata.version
        def missing(name):
            if name=='pillow':raise importlib.metadata.PackageNotFoundError(name)
            return original(name)
        with patch('pisa.environment.importlib.metadata.version',side_effect=missing):
            versions=package_versions()
        self.assertIn('pillow',versions)
        self.assertIsNone(versions['pillow'])
