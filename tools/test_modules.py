#!/usr/bin/env python3
"""Run each article's offline pytest/reference tests in its own process.

Use a Python environment with the article requirements installed. The website's
small .venv intentionally does not install model/research dependencies.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def suites():
    groups = {}
    for section in ('blog', 'research'):
        for path in sorted((ROOT / section).rglob('*.py')):
            if any(part.startswith('.') or part == '__pycache__' for part in path.relative_to(ROOT).parts):
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'))
            reference = any(isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Attribute) and base.attr == 'TestCase' for base in node.bases
            ) for node in tree.body)
            if path.name.startswith('test_') or reference:
                groups.setdefault(path.parent, []).append(path.name)
    return groups


def main():
    failed = []
    environment = dict(os.environ, OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2',
                       HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    for directory, files in suites().items():
        label = str(directory.relative_to(ROOT))
        print(f'\n{label}', flush=True)
        result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *files],
                                cwd=directory, env=environment)
        if result.returncode:
            failed.append(label)
    if failed:
        print('\nFailed suites:\n' + '\n'.join(failed))
    else:
        print('\nAll article test suites passed.')
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())
