"""Offline structural and comparator smoke tests for the two packaged skills."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPARE = ROOT / 'spring-to-go' / 'scripts' / 'compare_snapshots.py'


def load_py(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillMetadataTests(unittest.TestCase):
    def test_frontmatter_and_relative_links(self):
        for folder in ('go-backend', 'spring-to-go'):
            path = ROOT / folder / 'SKILL.md'
            self.assertTrue(path.is_file())
            body = path.read_text(encoding='utf-8')
            self.assertTrue(body.startswith('---\n'))
            match = re.match(r'^---\n(.*?)\n---\n', body, re.S)
            self.assertIsNotNone(match)
            attrs = dict(re.findall(r'^(name|description):\s*(.*)$', match.group(1), re.M))
            self.assertEqual(attrs.get('name'), folder)
            self.assertTrue(10 < len(attrs.get('description', '')) <= 1024)
            self.assertNotIn('--', attrs['description'])
            self.assertLessEqual(len(body.splitlines()), 500)
            for relative in re.findall(r'\]\((references/[^)]+)\)', body):
                self.assertTrue((ROOT / folder / relative).exists(), relative)

    def test_required_dependency_and_four_phases(self):
        main = (ROOT / 'spring-to-go' / 'SKILL.md').read_text(encoding='utf-8')
        self.assertEqual(len(re.findall(r'^### PHASE [1-4] —', main, re.M)), 4)
        self.assertIn('../go-backend/SKILL.md', main)
        self.assertIn('schema', main)
        self.assertIn('Rollback', (ROOT / 'spring-to-go' / 'references' / 'cutover.md').read_text(encoding='utf-8').title())


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.spring = Path(self.tmp.name) / 'spring.json'
        self.go = Path(self.tmp.name) / 'go.json'
        self.sample = {'cases': [{'id': 'p:ok', 'request': {'method': 'GET', 'path': '/products/1'},
                                   'response': {'status': 200, 'headers': {'Content-Type': 'application/json'},
                                                'body': {'id': 1, 'stock': 0, 'tags': [], 'nickname': None}},
                                   'database': {'products': [{'id': 1, 'stock': 0}]}, 'side_effects': []}]}

    def check(self, source, target):
        self.spring.write_text(json.dumps(source), encoding='utf-8')
        self.go.write_text(json.dumps(target), encoding='utf-8')
        return subprocess.run([sys.executable, str(COMPARE), str(self.spring), str(self.go)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def test_same_payload_and_case_insensitive_header_name_pass(self):
        target = json.loads(json.dumps(self.sample))
        target['cases'][0]['response']['headers'] = {'content-type': 'application/json'}
        result = self.check(self.sample, target)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('PASS: 1 case(s)', result.stdout)

    def test_null_vs_missing_fails(self):
        target = json.loads(json.dumps(self.sample))
        del target['cases'][0]['response']['body']['nickname']
        result = self.check(self.sample, target)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('nickname', result.stdout)

    def test_boolean_vs_number_fails(self):
        target = json.loads(json.dumps(self.sample))
        target['cases'][0]['response']['body']['stock'] = False
        result = self.check(self.sample, target)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('differing types', result.stdout)

    def test_added_case_fails(self):
        target = json.loads(json.dumps(self.sample))
        target['cases'].append(dict(target['cases'][0], id='p:extra'))
        result = self.check(self.sample, target)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('only in Go', result.stdout)

    def test_duplicate_case_fails(self):
        target = json.loads(json.dumps(self.sample))
        target['cases'].append(target['cases'][0])
        result = self.check(self.sample, target)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('duplicate case', result.stdout)

    def test_numeric_representation_difference(self):
        self.spring.write_text('{"cases":[{"id":"n","request":{},"response":{},"database":{"amount":1},"side_effects":[]}]}', encoding='utf-8')
        self.go.write_text('{"cases":[{"id":"n","request":{},"response":{},"database":{"amount":1.0},"side_effects":[]}]}', encoding='utf-8')
        result = subprocess.run([sys.executable, str(COMPARE), str(self.spring), str(self.go)],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(result.returncode, 1, result.stdout)


class GoScriptTests(unittest.TestCase):
    def test_walk_skips_vendor_and_testdata(self):
        module = load_py(ROOT / 'go-backend' / 'scripts' / 'check_go.py', 'go_checker')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for sub in ('pkg', 'vendor', 'testdata', '.git'):
                (root / sub).mkdir()
                (root / sub / 'sample.go').write_text('package p\n', encoding='utf-8')
            self.assertEqual(len(module.go_files(root)), 1)


class SchemaComparisonTests(unittest.TestCase):
    def test_same_and_changed_schema(self):
        tool = ROOT / 'spring-to-go' / 'scripts' / 'compare_schema.py'
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / 'old.sql', Path(td) / 'new.sql'
            a.write_text('CREATE TABLE products (id bigint);\n', encoding='utf-8')
            b.write_text('CREATE TABLE products (id bigint);\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(tool), str(a), str(b)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            b.write_text('CREATE TABLE products (id integer);\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(tool), str(a), str(b)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main(verbosity=2)
