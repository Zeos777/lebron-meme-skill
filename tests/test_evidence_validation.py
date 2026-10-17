"""Regression checks for versioned evidence selection; no model calls.

Fixtures are synthetic and stay in .tmp. They do not establish behavior quality.
"""
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import unittest

from validate import validate

ROOT = Path(__file__).resolve().parents[1]


class VersionedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='evidence-unit-', dir=ROOT / '.tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        assert self.root.resolve().is_relative_to((ROOT / '.tmp').resolve())
        shutil.copytree(ROOT / '.agents', self.root / '.agents')
        shutil.copytree(ROOT / 'tests', self.root / 'tests')
        for name in ('README.md', 'LICENSE', 'CONTRIBUTING.md', 'AGENTS.md'):
            shutil.copy2(ROOT / name, self.root / name)
        self.path = self.root / 'tests/chat-v0.2.1-evidence.json'
        self.legacy = self.root / 'tests/chat-evidence.json'
        self.old_bytes = self.legacy.read_bytes()
        self.evidence = json.loads(self.old_bytes)
        self.evidence.update(version='0.2.1', case_file='tests/chat-v0.2.1-cases.md',
                             synthetic_unit_test_fixture=True)
        self.evidence['published_output_file'] = 'tests/chat-v0.2.1-output.md'
        self.evidence['published_output_sha256'] = hashlib.sha256((self.root / self.evidence['published_output_file']).read_bytes()).hexdigest()
        self.evidence.pop('post_test_editorial_edits', None)
        self.evidence['case_file_sha256'] = hashlib.sha256((self.root / self.evidence['case_file']).read_bytes()).hexdigest()
        self.evidence['skill_hashes'] = {
            p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (self.root / '.agents/skills/lebron-meme').rglob('*') if p.is_file()
        }
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.evidence), encoding='utf-8')

    def test_current_version_selected_without_overwriting_legacy(self):
        errors, summary = validate(self.root, strict_evidence=True)
        self.assertEqual(errors, [])
        self.assertEqual(summary['chat_evidence_file'], 'tests/chat-v0.2.1-evidence.json')
        self.assertEqual(summary['chat_probes'], 11)
        self.assertEqual(self.legacy.read_bytes(), self.old_bytes)

    def test_changed_skill_fails_strict_check(self):
        path = self.root / '.agents/skills/lebron-meme/references/meme-catalog.md'
        path.write_bytes(path.read_bytes() + b'\n')
        errors, _ = validate(self.root, strict_evidence=True)
        self.assertTrue(any('Chat evidence is stale for:' in e for e in errors))

    def test_changed_scenario_fails_strict_check(self):
        path = self.root / self.evidence['case_file']
        path.write_bytes(path.read_bytes() + b'\n')
        errors, _ = validate(self.root, strict_evidence=True)
        self.assertTrue(any(self.evidence['case_file'] in e for e in errors))

    def test_omitted_skill_hash_is_stale(self):
        self.evidence['skill_hashes'].pop('.agents/skills/lebron-meme/SKILL.md')
        self.save()
        errors, _ = validate(self.root, strict_evidence=True)
        self.assertTrue(any('SKILL.md' in e for e in errors))

    def test_wrong_evidence_version_rejected(self):
        self.evidence['version'] = '0.2.0'
        self.save()
        errors, _ = validate(self.root)
        self.assertIn('Current chat evidence version differs from the Skill version', errors)

    def test_changed_published_output_rejected(self):
        path = self.root / self.evidence['published_output_file']
        path.write_bytes(path.read_bytes() + b'\n')
        errors, _ = validate(self.root, strict_evidence=True)
        self.assertIn('Published chat output hash differs from the recorded output', errors)

    def test_incomplete_model_run_rejected(self):
        self.evidence['runs'][0]['completed'] = False
        self.save()
        errors, _ = validate(self.root, strict_evidence=True)
        self.assertTrue(any('incomplete' in e for e in errors))

    def test_malformed_current_evidence_does_not_fall_back_to_legacy(self):
        self.path.write_text('[]', encoding='utf-8')
        errors, _ = validate(self.root)
        self.assertTrue(any('malformed' in e for e in errors))

    def test_scenario_outside_tests_rejected(self):
        self.evidence['case_file'] = 'README.md'
        self.save()
        errors, _ = validate(self.root)
        self.assertTrue(any('malformed' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
