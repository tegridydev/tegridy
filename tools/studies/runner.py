"""Isolated, content-addressed CPU studies. This command never starts services."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import statistics
import shutil
import tempfile
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS = HERE.parent / '_runs'
SEEDS = [17, 29, 43, 59, 71]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def registry():
    entries = json.loads((HERE / 'register.json').read_text())['entries']
    ids = [entry['id'] for entry in entries]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate study identity')
    for entry in entries:
        folder = (ROOT / entry['directory']).resolve()
        if not folder.is_relative_to(ROOT) or folder.is_symlink():
            raise ValueError('study outside the source tree')
        entry['runnable'] = (folder / 'study.py').is_file()
    return entries


def identity(entry, seed, profile):
    files = {}
    # Conservative fingerprint includes cross-article helpers and execution infrastructure.
    for base in [ROOT / 'blog', ROOT / 'research', HERE]:
        for folder, directories, names in os.walk(base):
            directories[:] = sorted(d for d in directories if not d.startswith('.') and d != '__pycache__')
            for name in sorted(names):
                path = Path(folder) / name
                if path.is_file() and path.name not in {'register.json', 'comparison-results.json'} and path.suffix in {'.py', '.toml', '.lock', '.json', '.txt', '.npy', '.npz'}:
                    files[str(path.relative_to(ROOT))] = digest(path)
    packages = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
    config = dict(study=entry['id'], directory=entry['directory'], seed=seed, data_seed=1729, profile=profile,
                  source=files, packages=packages, python=platform.python_version(),
                  protocol=entry['protocol'], platform=platform.platform(), threads=2, artifact_storage='temporary filesystem: '+tempfile.gettempdir())
    key = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:24]
    return key, config


def verify_run(directory):
    record = json.loads((directory / 'record.json').read_text())
    if record['status'] != 'completed':
        raise ValueError('run did not complete')
    for name, checksum in record['artifacts'].items():
        path = directory / name
        if not path.resolve().is_relative_to(directory.resolve()) or path.is_symlink() or digest(path) != checksum:
            raise ValueError('artifact integrity failure: ' + name)
    result = json.loads((directory / 'result.json').read_text())
    if not isinstance(result.get('metrics'), dict) or not result.get('scope'):
        raise ValueError('result requires metrics and explicit scope')
    for name, value in result['metrics'].items():
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('invalid metric: ' + name)
    return record, result


def worker(entry, seed, profile, directory):
    import resource
    sys.path.insert(0, str(ROOT / 'research'))
    sys.path.insert(0, str(ROOT / entry['directory']))
    spec = importlib.util.spec_from_file_location('study_module', ROOT / entry['directory'] / 'study.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    start = time.perf_counter()
    spec.loader.exec_module(module)
    result = module.run(seed=seed, data_seed=1729, profile=profile, output=directory)
    result['execution'] = dict(elapsed_seconds=time.perf_counter() - start,
                               peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               memory_scope='whole isolated process; Linux ru_maxrss')
    atomic_json(directory / 'result.json', result)


def execute(entry, seed, profile, resume, timeout):
    key, config = identity(entry, seed, profile)
    parent = RUNS / entry['id'] / key
    parent.mkdir(parents=True, exist_ok=True)
    if resume:
        for previous in sorted(parent.glob('*/record.json')):
            try:
                verify_run(previous.parent)
                print('RESUME', entry['id'], seed, flush=True)
                return True
            except (ValueError, KeyError, OSError):
                continue
    directory = parent / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
    directory.mkdir()
    scratch = Path(tempfile.mkdtemp(prefix='tegridy-study-'))
    started = datetime.now(timezone.utc).isoformat()
    record = dict(schema=1, identity=key, config=config, started=started, status='running', artifacts={}, working_directory=str(scratch))
    atomic_json(directory / 'record.json', record)
    environment = dict(os.environ, OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2',
                       PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '_worker', '--study', entry['id'],
               '--seed', str(seed), '--profile', profile, '--output', str(scratch)]
    print('RUN', entry['id'], seed, profile, flush=True)
    started_clock = time.monotonic()
    process = None
    try:
        with (scratch / 'execution.log').open('w') as log:
            process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            returncode = process.wait(timeout=timeout)
        if returncode:
            raise RuntimeError('worker exited ' + str(returncode))
        result = json.loads((scratch / 'result.json').read_text())
        if not result.get('scope') or not isinstance(result.get('metrics'), dict):
            raise ValueError('invalid study result')
        record['status'] = 'completed'
    except (Exception, KeyboardInterrupt) as error:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        record.update(status='interrupted' if isinstance(error, KeyboardInterrupt) else 'failed', error=str(error))
        if isinstance(error, KeyboardInterrupt):
            raise
    finally:
        record['elapsed_seconds'] = time.monotonic() - started_clock
        record['finished'] = datetime.now(timezone.utc).isoformat()
        copied = False
        try:
            for source in sorted(scratch.rglob('*')):
                if source.is_symlink():
                    raise ValueError('study output contains a symlink')
                if source.is_file():
                    target = directory / source.relative_to(scratch)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
            record['artifacts'] = {str(p.relative_to(directory)): digest(p) for p in sorted(directory.rglob('*'))
                                   if p.is_file() and p.name != 'record.json'}
            copied = True
        except Exception as error:
            record.update(status='failed', error='Artifact copy failed; working_directory retained: '+str(error))
        atomic_json(directory / 'record.json', record)
        if copied:
            shutil.rmtree(scratch)

    if record['status'] == 'completed':
        try:
            verify_run(directory)
        except (ValueError, KeyError, OSError) as error:
            record.update(status='failed', error=str(error))
            atomic_json(directory / 'record.json', record)
    print(record['status'].upper(), entry['id'], seed, '→', directory.relative_to(ROOT), flush=True)
    return record['status'] == 'completed'


def report():
    groups, failures = {}, []
    for path in sorted(RUNS.glob('*/*/*/record.json')):
        try:
            record, result = verify_run(path.parent)
        except (ValueError, OSError, KeyError) as error:
            failures.append(dict(run=str(path.parent.relative_to(ROOT)), error=str(error)))
            continue
        config = dict(record['config'])
        seed = config.pop('seed')
        group = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        item = groups.setdefault(group, dict(config=config, seeds={}, scope=result['scope']))
        # Repeated executions of one seed are not independent observations.
        item['seeds'][seed] = dict(metrics=result['metrics'], run=str(path.parent.relative_to(ROOT)))
    summaries = []
    for group in groups.values():
        seeds = group.pop('seeds')
        names = set.intersection(*(set(v['metrics']) for v in seeds.values()))
        summary = {}
        for name in sorted(names):
            values = [row['metrics'][name] for row in seeds.values()]
            summary[name] = dict(mean=statistics.mean(values), standard_deviation=statistics.stdev(values) if len(values)>1 else None,
                                 minimum=min(values), maximum=max(values), independent_seeds=len(values))
        summaries.append(dict(**group, runs=seeds, metrics=summary))
    data = dict(schema=1, entries=registry(), comparisons=summaries, unsuccessful_or_invalid_runs=failures,
                interpretation='Completion describes execution, not scientific validation. No significance claim follows from seed averages.')
    atomic_json(RUNS / 'summary.json', data)
    print(json.dumps(dict(registered=len(data['entries']), runnable=sum(e['runnable'] for e in data['entries']),
                         comparison_groups=len(summaries), unsuccessful_or_invalid_runs=len(failures),
                         summary=str(RUNS / 'summary.json')), indent=2))


def check():
    commands = [[sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tools/tests', '-v'],
                [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tools/studies/tests', '-v'],
                [sys.executable, '-B', 'tools/test_modules.py'],
                ['bun', 'test', 'tools/site.test.mjs'],
                ['bun', 'blog/model-interpretability/what-a-model-map-can-show/test_viewer.cjs']]
    failures = []
    for command in commands:
        if command[:2] == ['bun', 'test'] and not (ROOT / command[-1]).exists():
            print('Local website script checks are not part of this public source export.')
            continue
        if subprocess.run(command, cwd=ROOT).returncode:
            failures.append(command)
    print(json.dumps(dict(failed=failures), indent=2))
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'report', 'check', '_worker'])
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--study')
    selection.add_argument('--all', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--profile', choices=['cpu', 'smoke'], default='cpu')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error('timeout must be positive')
    if args.command == 'check':
        return check()
    if args.command == 'report':
        report()
        return 0
    entries = registry()
    if args.list:
        for e in entries:
            print(e['id'], 'READY' if e['runnable'] else 'PENDING', e['verification'], sep='\t')
        return 0
    if not args.all and not args.study:
        parser.error('choose --study, --all or --list')
    selected = entries if args.all else [e for e in entries if e['id'] == args.study]
    if not selected:
        parser.error('unknown study')
    if args.command == '_worker':
        if args.output is None or args.seed is None or len(selected) != 1:
            parser.error('worker requires one study, seed and output')
        worker(selected[0], args.seed, args.profile, args.output)
        return 0
    RUNS.mkdir(exist_ok=True)
    # Atomic directory lock prevents two invocations consuming the same CPU budget.
    lock = RUNS / '.runner-lock'
    try:
        lock.mkdir()
    except FileExistsError:
        parser.error('another runner owns _runs/.runner-lock; after a crash confirm no process remains before removing it')
    atomic_json(lock / 'owner.json', dict(pid=os.getpid(), started=datetime.now(timezone.utc).isoformat()))
    okay = True
    try:
        for entry in selected:
            if not entry['runnable']:
                print('PENDING', entry['id'], entry['remaining'])
                okay = False
                continue
            for seed in [args.seed] if args.seed is not None else entry['protocol'].get('seeds', SEEDS):
                okay = execute(entry, seed, args.profile, args.resume, args.timeout) and okay
        report()
    finally:
        (lock / 'owner.json').unlink()
        lock.rmdir()
    return 0 if okay else 1


if __name__ == '__main__':
    sys.exit(main())
