"""LEVEL-RETURN union certifier and unanchored bond certificates.

An anchor is used ONLY by the unchanged upstream union certifier. Bond
formulas contain original NAE clauses and the forbidden assignment's units.
"""
import hashlib
import os
import importlib.util
import json
from contextlib import contextmanager
import fcntl
from pathlib import Path
import subprocess
import time

import numpy as np

from pattern import HERE, ROOT, clauses

SOURCE = ROOT / 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels'
_spec = importlib.util.spec_from_file_location('level_reach_return_certifier', HERE / 'input_certify.py')
upstream = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upstream)
upstream.CHECKER = str(HERE / 'lrat_check')
CADICAL = upstream.CADICAL
CHECKER = upstream.CHECKER


@contextmanager
def external_slot(deadline):
    """At most one external certificate process across runner workers."""
    with (HERE / 'work' / 'certificate.lock').open('a') as lock:
        while True:
            seconds_left(deadline)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(min(0.02, seconds_left(deadline)))
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


class BudgetExpired(Exception):
    pass


def seconds_left(deadline):
    left = deadline - time.monotonic()
    if left <= 0:
        raise BudgetExpired('300-second search budget exhausted')
    return left


def model_from_literals(lits, nvars):
    value = [0] * nvars
    for lit in lits:
        if lit and abs(lit) <= nvars:
            value[abs(lit) - 1] = int(lit > 0)
    return value


def check_state(K, state, units=()):
    if any(state[abs(int(l)) - 1] != int(l > 0) for l in units):
        return False
    return all(not (state[int(a)] == state[int(b)] == state[int(c)]) for a, b, c in K)


def pack_state(state):
    raw = bytearray((len(state) + 7) // 8)
    for v, b in enumerate(state):
        raw[v // 8] |= int(b) << (v % 8)
    return raw.hex()


def unpack_state(packed, nvars):
    raw = bytes.fromhex(packed)
    if len(raw) != (nvars + 7) // 8:
        raise ValueError('wrong packed-state length')
    return [(raw[v // 8] >> (v % 8)) & 1 for v in range(nvars)]


def union_fate(K, nvars, workdir, timeout=60):
    start = time.monotonic()
    deadline = start + timeout
    try:
        with external_slot(deadline):
            result = upstream.certify(np.asarray(K, dtype=np.int64).reshape((-1, 3)), nvars,
                                      str(workdir), seconds_left(deadline))
    except BudgetExpired:
        return {'verdict': 'undecided', 'certificate': 'union certification budget exhausted while acquiring external slot',
                'seconds': time.monotonic() - start}
    result['seconds_including_slot_wait'] = time.monotonic() - start
    if result['verdict'] not in ('alive', 'dead', 'undecided'):
        raise AssertionError(result)
    if not len(K):
        state = [0] * nvars
        assert check_state(K, state)
        result.update(certificate='all-zero state checked against every knot (empty union)',
                      model=pack_state(state))
    return result


def write_cnf(path, K, nvars, units):
    with path.open('w') as stream:
        stream.write(f'p cnf {nvars} {2 * len(K) + len(units)}\n')
        for row in clauses(K):
            stream.write(' '.join(map(str, row)) + ' 0\n')
        for lit in units:
            stream.write(f'{int(lit)} 0\n')


KEEP_DIR = Path(os.environ.get('REACH_KEEP_DIR', str(Path(__file__).resolve().parent / 'certificates')))


def keep_certificate(cnf, proof):
    """Thread's addition before the registered run (standing rule after LEVEL-RETURN-R1): keep the CNF and the LRAT proof,
    gzip-compressed, named by the CNF's SHA-256."""
    import gzip
    KEEP_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(Path(cnf).read_bytes()).hexdigest()
    for src, suffix in ((cnf, '.cnf.gz'), (proof, '.lrat.gz')):
        target = KEEP_DIR / (h + suffix)
        if not target.exists():
            with open(src, 'rb') as fi, gzip.open(target, 'wb') as fo:
                fo.write(fi.read())
    return h


def checked_refutation(K, nvars, units, workdir, deadline, corrupt_test=False):
    with external_slot(deadline):
        return _checked_refutation(K, nvars, units, workdir, deadline, corrupt_test)


def _checked_refutation(K, nvars, units, workdir, deadline, corrupt_test=False):
    """Two independent solves, an on-disk text LRAT, checker, then unlink.

    Hashes and the checker response survive scratch deletion. Optional gate
    corruption changes an actual used hint to a nonexistent clause id.
    """
    cnf = Path(workdir) / 'bond.cnf'
    proof = Path(workdir) / 'bond.lrat'
    bad = Path(workdir) / 'corrupt.lrat'
    write_cnf(cnf, K, nvars, units)
    t0 = time.monotonic()
    try:
        first = subprocess.run([CADICAL, '-q', str(cnf)], capture_output=True, text=True,
                               timeout=seconds_left(deadline))
        if first.returncode != 20:
            raise AssertionError(('forbidden assignment not refuted', first.returncode, first.stdout))
        second = subprocess.run([CADICAL, '--lrat=true', '--binary=false', '-q', str(cnf), str(proof)],
                                capture_output=True, text=True, timeout=seconds_left(deadline))
        if second.returncode != 20:
            raise AssertionError(('proof solve disagreed', second.returncode))
        checked = subprocess.run([CHECKER, str(cnf), str(proof)], capture_output=True, text=True,
                                 timeout=seconds_left(deadline))
        if checked.returncode or not checked.stdout.startswith('VERIFIED'):
            raise AssertionError(('LRAT rejected', checked.stdout, checked.stderr))
        raw = proof.read_bytes()
        answer = {'checked': True, 'checker': checked.stdout.strip(),
                  'proof_bytes': len(raw), 'proof_sha256': hashlib.sha256(raw).hexdigest(),
                  'cnf_sha256': hashlib.sha256(cnf.read_bytes()).hexdigest(),
                  'solver': 'CaDiCaL 2.1.2', 'unanchored': True,
                  'deleted_after_check': False, 'kept_as': keep_certificate(cnf, proof),
                  'seconds': time.monotonic() - t0}
        if corrupt_test:
            lines = raw.decode('ascii').splitlines()
            changed = False
            for i, line in enumerate(lines):
                tokens = line.split()
                if len(tokens) < 4 or tokens[1] == 'd':
                    continue
                end_clause = tokens.index('0', 1)
                if end_clause + 1 < len(tokens) and tokens[end_clause + 1] != '0':
                    tokens[end_clause + 1] = '999999999999'
                    lines[i] = ' '.join(tokens)
                    changed = True
                    break
            if not changed:
                raise AssertionError('no proof hint available to corrupt')
            bad.write_text('\n'.join(lines) + '\n')
            rejected = subprocess.run([CHECKER, str(cnf), str(bad)], capture_output=True, text=True,
                                      timeout=seconds_left(deadline))
            answer['corrupted_hint_rejected'] = rejected.returncode != 0 and rejected.stdout.startswith('FAILED')
            answer['corrupted_checker'] = rejected.stdout.strip()
            if not answer['corrupted_hint_rejected']:
                raise AssertionError('corrupted proof accepted')
        return answer
    except subprocess.TimeoutExpired as exc:
        raise BudgetExpired('external certificate deadline') from exc
    finally:
        for path in (cnf, proof, bad):
            path.unlink(missing_ok=True)


def verify_bond_certificate(K, nvars, result):
    """Independently recheck every retained proper-projection witness."""
    if not isinstance(result.get('L'), int):
        return {'bonds': 0, 'states': 0}
    bond = result['bond']
    cert = result['certificate']
    assert len(bond) == len(set(bond)) == result['L']
    assert cert['refutation']['checked'] and cert['refutation']['unanchored']
    assignment = result['forbidden_assignment']
    assert len(assignment) == len(bond) and all(v in (0, 1) for v in assignment)
    units = [v + 1 if b else -v - 1 for v, b in zip(bond, assignment)]
    # Bind the retained assignment to the exact CNF whose deleted proof
    # was checked; a mismatched support or value cannot reuse a summary.
    digest = hashlib.sha256()
    digest.update(f'p cnf {nvars} {2 * len(K) + len(units)}\n'.encode())
    for row in clauses(K):
        digest.update((' '.join(map(str, row)) + ' 0\n').encode())
    for lit in units:
        digest.update(f'{int(lit)} 0\n'.encode())
    assert digest.hexdigest() == cert['refutation']['cnf_sha256']
    pool = [unpack_state(s, nvars) for s in cert['state_pool']]
    assert all(check_state(K, state) for state in pool)
    count = 0
    assert len(cert['maximal_proper']) == len(bond)
    for missing, item in enumerate(cert['maximal_proper']):
        support = bond[:missing] + bond[missing + 1:]
        assert item['support'] == support
        assert len(item['state_indices']) == 1 << len(support)
        for assignment, index in enumerate(item['state_indices']):
            state = pool[index]
            assert all(state[v] == ((assignment >> j) & 1) for j, v in enumerate(support))
            count += 1
    assert count == cert['assignments_checked']
    return {'bonds': 1, 'states': count}
