"""Four fault controls for retention.py; run only after the gate runner stops.

Every proof is emitted by the real CaDiCaL and checked by the real checker.
Faults affect only the expected failure being exercised. Calls are sequential;
there is at most one external child. Fixtures stay beneath this CODEX directory
and are explicitly marked as failed-certification fixtures, never evidence.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import retention
from reuse import HERE


FORMULA = [[1, 2], [1, -2], [-1, 2], [-1, -2]]
NVARS = 2
RAW_CNF = b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
CNF_HASH = hashlib.sha256(RAW_CNF).hexdigest()


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _hash_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _read_gzip(path):
    with gzip.open(path, 'rb') as stream:
        return stream.read()


def _write_fault_gzip(path, raw):
    """Deliberately alter this control's own fixture, retaining the original."""
    with Path(path).open('wb') as stream:
        with gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0) as compressed:
            compressed.write(raw)


@contextmanager
def _sandbox(root):
    work = root / 'work'
    if work.exists():
        shutil.rmtree(work)
    with patch.object(retention, 'HERE', root), patch.object(retention, 'PROOF_DIR', root / 'certificates'):
        store = retention.ProofStore(work / 'case', NVARS)
        try:
            yield store
        finally:
            if work.exists():
                shutil.rmtree(work)


@contextmanager
def _real_processes(observed, reject_checker=False):
    """Use real processes, optionally replace an accepted checker response."""
    real_run = subprocess.run
    active = 0

    def run(args, *positional, **kwargs):
        nonlocal active
        command = list(args)
        _require(command[0] in (retention.cert.CADICAL, retention.cert.CHECKER),
                 'control attempted an unexpected external command')
        active += 1
        observed['peak_external_children'] = max(observed.get('peak_external_children', 0), active)
        _require(active == 1, 'external calls overlapped')
        try:
            result = real_run(args, *positional, **kwargs)
        finally:
            active -= 1
        entry = {'program': command[0], 'returncode': result.returncode}
        observed.setdefault('processes', []).append(entry)
        if command[0] == retention.cert.CADICAL:
            _require('--lrat=true' in command and result.returncode == 20,
                     'real CaDiCaL did not emit the expected refutation')
            observed['emitted_cnf'] = Path(command[-2]).read_bytes()
            observed['emitted_proof'] = Path(command[-1]).read_bytes()
            _require(observed['emitted_cnf'] == RAW_CNF, 'fixture CNF changed')
            _require(observed['emitted_proof'], 'real proof file is empty')
        else:
            _require(result.returncode == 0 and result.stdout.startswith('VERIFIED'),
                     'real checker rejected the original emitted proof')
            observed['real_checker_verified'] = True
            if reject_checker:
                entry['injected_returncode'] = 1
                return subprocess.CompletedProcess(command, 1,
                                                   'FAILED injected checker rejection\n',
                                                   'retention control fault')
        return result

    with patch.object(retention.subprocess, 'run', run):
        yield


def _negative_answer(store):
    with retention.context(store, time.monotonic() + 60), retention.RetainingMinisat(bootstrap_with=FORMULA) as solver:
        return solver.solve()


def _expect_error(function, kind, text):
    try:
        value = function()
    except kind as exc:
        _require(text in str(exc), f'unexpected failure: {exc}')
        return f'{type(exc).__name__}: {exc}'
    raise AssertionError(f'negative answer escaped the injected failure: {value!r}')


def _failed_artifacts(root, store, observed):
    _require(len(store.incomplete) == 1, 'failed certification was not recorded once')
    item = store.incomplete[0]
    _require(item['checked'] is False, 'failed certification was labeled checked')
    _require(_read_gzip(root / item['cnf_path']) == observed['emitted_cnf'],
             'failed certification did not retain its actual CNF')
    _require(_read_gzip(root / item['partial_proof_path']) == observed['emitted_proof'],
             'failed certification did not retain its actual emitted LRAT')
    _require(item['partial_proof_sha256'] == hashlib.sha256(observed['emitted_proof']).hexdigest(),
             'retained failed-proof digest is incorrect')
    return item


def _process_report(observed):
    _require(observed.get('peak_external_children') == 1, 'no real external execution was checked')
    return {key: value for key, value in observed.items() if key not in ('emitted_cnf', 'emitted_proof')}


def _checker_rejection(root):
    observed = {}
    with _sandbox(root) as store, _real_processes(observed, reject_checker=True):
        error = _expect_error(lambda: _negative_answer(store), AssertionError, 'LRAT check failed')
        fixture = _failed_artifacts(root, store, observed)
        _require(not store.records, 'rejected checker response became a consumed refutation')
    return {'passed': True, 'fault': 'replace verified real checker response with rejection',
            'consumed_refutation': False, 'observed_error': error,
            'failed_fixture': fixture, **_process_report(observed)}


def _expiration_during_retention(root):
    observed, expired = {}, [False]
    real_gzip, real_remaining = retention._gzip_bytes, retention._remaining

    def gzip_then_expire(path, raw):
        real_gzip(path, raw)
        if Path(path) == root / 'certificates' / (CNF_HASH + '.lrat.gz'):
            expired[0] = True

    def remaining(deadline):
        if expired[0]:
            raise retention.cert.BudgetExpired('injected expiration after proof retention')
        return real_remaining(deadline)

    with _sandbox(root) as store, _real_processes(observed):
        with patch.object(retention, '_gzip_bytes', gzip_then_expire), patch.object(retention, '_remaining', remaining):
            error = _expect_error(lambda: _negative_answer(store), retention.cert.BudgetExpired,
                                  'negative answer not consumed')
        _require(expired[0], 'expiration fault was never reached')
        fixture = _failed_artifacts(root, store, observed)
        _require(_read_gzip(root / 'certificates' / (CNF_HASH + '.lrat.gz')) == observed['emitted_proof'],
                 'verified proof was not retained before reporting the expired query')
    return {'passed': True, 'fault': 'expire immediately after retaining real LRAT',
            'consumed_refutation': False, 'observed_error': error,
            'failed_fixture': fixture, **_process_report(observed)}


def _orphan_disagreement(root):
    observed = {}
    orphan = root / 'certificates' / (CNF_HASH + '.lrat.gz')
    with _sandbox(root) as store, _real_processes(observed):
        _write_fault_gzip(orphan, b'FAILED FIXTURE: orphan bytes are not an LRAT proof.\n')
        before = _hash_file(orphan)
        error = _expect_error(lambda: _negative_answer(store), RuntimeError,
                              'existing retained bytes disagree')
        _require(_hash_file(orphan) == before, 'mismatching orphan was overwritten')
        _require(not store.records and not orphan.with_name(CNF_HASH + '.json').exists(),
                 'mismatching orphan received successful metadata')
        fixture = _failed_artifacts(root, store, observed)
    return {'passed': True, 'fault': 'preexisting orphan proof gzip contains different raw bytes',
            'consumed_refutation': False, 'observed_error': error,
            'orphan_path': str(orphan.relative_to(HERE)), 'orphan_gzip_sha256': before,
            'failed_fixture': fixture, **_process_report(observed)}


def _cache_hash_mismatch(root):
    observed = {}
    with _sandbox(root) as store, _real_processes(observed):
        _require(_negative_answer(store) is False, 'real baseline refutation did not succeed')
        proof = root / 'certificates' / (CNF_HASH + '.lrat.gz')
        original = root / 'original_before_fault.lrat.gz'
        shutil.copyfile(proof, original)
        original_hash = hashlib.sha256(_read_gzip(original)).hexdigest()
        _require(original_hash == store.records[CNF_HASH]['proof_sha256'], 'baseline proof hash differs')
        _write_fault_gzip(proof, b'FAILED FIXTURE: cache proof bytes disagree with metadata.\n')
        fault_hash = _hash_file(proof)
        process_count = len(observed['processes'])
        # A new consumer must verify persistent cache bytes before returning UNSAT.
        consumer = retention.ProofStore(root / 'work' / 'cache_consumer', NVARS)
        error = _expect_error(lambda: _negative_answer(consumer), AssertionError,
                              'retained certificate digest mismatch')
        _require(not consumer.records, 'invalid persistent cache was accepted')
        _require(len(observed['processes']) == process_count, 'corrupt cache unexpectedly started a child')
        _require(_hash_file(proof) == fault_hash, 'corrupt-cache fixture was overwritten')
    return {'passed': True, 'fault': 'alter persistent proof gzip after valid metadata is saved',
            'consumed_refutation': False, 'observed_error': error,
            'original_proof_path': str(original.relative_to(HERE)),
            'original_proof_sha256': original_hash,
            'corrupt_cache_path': str(proof.relative_to(HERE)),
            'corrupt_cache_gzip_sha256': fault_hash, **_process_report(observed)}


def run_controls():
    """Return JSON-compatible results; retain only explicitly labeled fixtures."""
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + f'-{os.getpid()}'
    fixtures = HERE / 'retention_control_fixtures' / stamp
    fixtures.mkdir(parents=True)
    hashes = {name: _hash_file(HERE / name) for name in ('retention.py', 'retention_controls.py', 'reuse.py')}
    binaries = {name: {'path': path, 'sha256': _hash_file(path)}
                for name, path in (('cadical', retention.cert.CADICAL), ('checker', retention.cert.CHECKER))}
    results = {}
    for name, function in (('checker_rejection', _checker_rejection),
                           ('expiration_during_retention', _expiration_during_retention),
                           ('orphan_disagreement', _orphan_disagreement),
                           ('persistent_cache_hash_mismatch', _cache_hash_mismatch)):
        root = fixtures / name
        root.mkdir()
        start = time.monotonic()
        try:
            value = function(root)
        except Exception as exc:
            value = {'passed': False, 'error': f'{type(exc).__name__}: {exc}',
                     'traceback': traceback.format_exc()}
        value.update(fixture_kind='explicit failed-certification test fixture; not research evidence',
                     fixture_root=str(root.relative_to(HERE)), seconds=time.monotonic() - start)
        (root / 'fixture.json').write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
        results[name] = value
    return {'passed': all(value['passed'] for value in results.values()),
            'controls': results, 'implementation_sha256': hashes, 'binaries': binaries,
            'fixture_root': str(fixtures.relative_to(HERE)),
            'execution': 'sequential real CaDiCaL/LRAT checker; controlled faults only; at most one child',
            'nonclaims': ['contract failure controls only', 'no additional scientific gate or population run']}


if __name__ == '__main__':
    result = run_controls()
    target = HERE / 'retention_controls.json'
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    temporary.replace(target)
    print(json.dumps({'passed': result['passed'],
                      'controls': {name: value['passed'] for name, value in result['controls'].items()}}, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
