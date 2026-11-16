"""Retain checked LRAT for every negative SAT answer consumed by this job.

This includes the census engine's internal original and auxiliary CNFs, not
only its reported bonds. A negative answer is never returned before checking
and retaining its proof. Deadlines turn incomplete certification into undecided.
"""
from contextlib import contextmanager
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

import numpy as np
from pysat.solvers import Minisat22 as NativeMinisat22
from reuse import HERE, certificates as cert, search

ACTIVE = None
DEADLINE = None
PROOF_DIR = HERE / 'certificates'


def _remaining(deadline):
    return 86400.0 if deadline is None else cert.seconds_left(deadline)


def _gzip_bytes(path, raw):
    if path.exists():
        with gzip.open(path, 'rb') as stream:
            existing_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
        if existing_hash != hashlib.sha256(raw).hexdigest():
            raise RuntimeError(f'existing retained bytes disagree: {path.name}')
        return
    temp = path.with_name(path.name + f'.{uuid.uuid4().hex}.tmp')
    with temp.open('wb') as stream:
        with gzip.GzipFile(filename='', fileobj=stream, mode='wb', compresslevel=1, mtime=0) as compressed:
            compressed.write(raw)
    temp.replace(path)


@contextmanager
def external_slot(deadline=None):
    # A supervisor + two workers + one external solver/checker is four processes.
    (HERE / 'locks').mkdir(exist_ok=True)
    with (HERE / 'locks' / 'certificate.lock').open('a') as lock:
        while True:
            _remaining(deadline)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(min(0.01, _remaining(deadline)))
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


class ProofStore:
    def __init__(self, workdir, nvars=0):
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        PROOF_DIR.mkdir(exist_ok=True)
        self.nvars = nvars
        self.records = {}
        self.incomplete = []
        self.external_seconds = 0.0
        self.reused_external_seconds = 0.0

    def refute(self, formula, nvars, units=(), deadline=None, purpose='SAT refutation'):
        path = self.workdir / 'retained.cnf'
        with path.open('w') as stream:
            stream.write(f'p cnf {nvars} {len(formula) + len(units)}\n')
            for clause in formula:
                stream.write(' '.join(map(str, clause)) + ' 0\n')
            for lit in units:
                stream.write(f'{int(lit)} 0\n')
        try:
            return self.refute_file(path, deadline, purpose)
        finally:
            path.unlink(missing_ok=True)

    def refute_file(self, cnf, deadline=None, purpose='SAT refutation'):
        raw_cnf = Path(cnf).read_bytes()
        digest = hashlib.sha256(raw_cnf).hexdigest()
        if digest in self.records:
            _remaining(deadline)
            return self.records[digest]
        meta_path = PROOF_DIR / (digest + '.json')
        with external_slot(deadline):
            if meta_path.exists():
                result = json.loads(meta_path.read_text())
                assert result['cnf_sha256'] == digest and result['checked']
                for suffix, expected in (('.cnf.gz', digest), ('.lrat.gz', result['proof_sha256'])):
                    with gzip.open(PROOF_DIR / (digest + suffix), 'rb') as stream:
                        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
                    assert actual == expected, 'retained certificate digest mismatch'
                self.records[digest] = result
                self.reused_external_seconds += result['seconds']
                _remaining(deadline)
                return result
            proof = self.workdir / 'retained.lrat'
            start = time.monotonic()
            try:
                assert hashlib.sha256(Path(cnf).read_bytes()).hexdigest() == digest, 'CNF changed before proof solve'
                solved = subprocess.run([cert.CADICAL, '--lrat=true', '--binary=false', '-q',
                                         str(cnf), str(proof)], capture_output=True, text=True,
                                        timeout=None if deadline is None else _remaining(deadline))
                if solved.returncode != 20:
                    raise AssertionError(('negative SAT answer disagrees with CaDiCaL', solved.returncode,
                                          solved.stdout[-1000:], solved.stderr[-1000:]))
                checked = subprocess.run([cert.CHECKER, str(cnf), str(proof)], capture_output=True,
                                         text=True, timeout=None if deadline is None else _remaining(deadline))
                if checked.returncode or not checked.stdout.startswith('VERIFIED'):
                    raise AssertionError(('LRAT check failed', checked.stdout, checked.stderr))
                assert hashlib.sha256(Path(cnf).read_bytes()).hexdigest() == digest, 'CNF changed during proof certification'
                raw_proof = proof.read_bytes()
                _gzip_bytes(PROOF_DIR / (digest + '.cnf.gz'), raw_cnf)
                _gzip_bytes(PROOF_DIR / (digest + '.lrat.gz'), raw_proof)
                result = {'checked': True, 'checker': checked.stdout.strip(), 'cnf_sha256': digest,
                          'proof_sha256': hashlib.sha256(raw_proof).hexdigest(),
                          'proof_bytes': len(raw_proof), 'cnf_bytes': len(raw_cnf),
                          'kept_as': digest, 'deleted_after_check': False,
                          'cnf_path': str((PROOF_DIR / (digest + '.cnf.gz')).relative_to(HERE)),
                          'proof_path': str((PROOF_DIR / (digest + '.lrat.gz')).relative_to(HERE)),
                          'solver': 'CaDiCaL 2.1.2', 'purpose': purpose,
                          'seconds': time.monotonic() - start}
                temp = meta_path.with_name(meta_path.name + f'.{uuid.uuid4().hex}.tmp')
                temp.write_text(json.dumps(result, sort_keys=True) + '\n')
                temp.replace(meta_path)
                self.records[digest] = result
                _remaining(deadline)
                return result
            except BaseException as exc:
                # Preserve even checker rejection, disagreement, interruption,
                # and storage failure; cleanup must never erase emitted evidence.
                attempts = HERE / 'incomplete_certifications'
                attempts.mkdir(exist_ok=True)
                _gzip_bytes(attempts / (digest + '.cnf.gz'), raw_cnf)
                item = {'cnf_sha256': digest, 'purpose': purpose, 'checked': False,
                        'reason': f'{type(exc).__name__}: {exc}',
                        'cnf_path': str((attempts / (digest + '.cnf.gz')).relative_to(HERE))}
                if proof.exists():
                    partial = proof.read_bytes()
                    partial_hash = hashlib.sha256(partial).hexdigest()
                    name = digest + '.' + partial_hash + '.partial.lrat.gz'
                    _gzip_bytes(attempts / name, partial)
                    item.update(partial_proof_sha256=partial_hash, partial_proof_path=str((attempts / name).relative_to(HERE)))
                self.incomplete.append(item)
                (attempts / (digest + f'.{uuid.uuid4().hex}.json')).write_text(json.dumps(item, sort_keys=True) + '\n')
                if isinstance(exc, (subprocess.TimeoutExpired, cert.BudgetExpired)):
                    raise cert.BudgetExpired('LRAT certification deadline; negative answer not consumed') from exc
                raise
            finally:
                self.external_seconds += time.monotonic() - start
                proof.unlink(missing_ok=True)


@contextmanager
def context(store, deadline=None):
    global ACTIVE, DEADLINE
    old = ACTIVE, DEADLINE
    ACTIVE, DEADLINE = store, deadline
    try:
        yield
    finally:
        ACTIVE, DEADLINE = old


class RetainingMinisat:
    """Census SAT API with a proof obligation on every UNSAT return."""
    def __init__(self, bootstrap_with=None, **kwargs):
        self.formula = [list(map(int, c)) for c in (bootstrap_with or [])]
        self.native = NativeMinisat22(bootstrap_with=self.formula, **kwargs)

    def __getattr__(self, name):
        return getattr(self.native, name)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.delete()

    def add_clause(self, clause, **kwargs):
        row = list(map(int, clause))
        self.formula.append(row)
        return self.native.add_clause(row, **kwargs)

    def _solve(self, limited, assumptions=None, **kwargs):
        assumptions = list(assumptions or [])
        method = self.native.solve_limited if limited else self.native.solve
        result = method(assumptions=assumptions, **kwargs)
        if result is False:
            if ACTIVE is None:
                raise RuntimeError('refutation outside retention context')
            nvars = max(self.native.nof_vars(), ACTIVE.nvars)
            ACTIVE.refute(self.formula, nvars, assumptions, DEADLINE, 'census internal SAT query/exhaustion')
        return result

    def solve(self, assumptions=None, **kwargs):
        return self._solve(False, assumptions, **kwargs)

    def solve_limited(self, assumptions=None, **kwargs):
        return self._solve(True, assumptions, **kwargs)

    def delete(self):
        self.native.delete()


def checked_refutation(K, nvars, units, workdir, deadline, corrupt_test=False):
    if corrupt_test:
        raise ValueError('the requested gates do not use proof corruption')
    if ACTIVE is None:
        raise RuntimeError('bond proof outside retention context')
    result = dict(ACTIVE.refute(cert.clauses(K), nvars, units, deadline, 'reported bond or tie'))
    result['unanchored'] = True
    return result


def union_fate(K, nvars, workdir, timeout=60):
    if ACTIVE is None:
        raise RuntimeError('union fate outside retention context')
    start = time.monotonic()
    deadline = start + timeout
    cnf = Path(workdir) / 'union.cnf'
    cert.write_cnf(cnf, K, nvars, ())
    try:
        with external_slot(deadline):
            solved = subprocess.run([cert.CADICAL, '-q', str(cnf)], capture_output=True,
                                    text=True, timeout=_remaining(deadline))
        if solved.returncode == 10:
            literals = [int(x) for line in solved.stdout.splitlines() if line.startswith('v')
                        for x in line[1:].split() if x != '0']
            state = cert.model_from_literals(literals, nvars)
            assert cert.check_state(K, state)
            result = {'verdict': 'alive', 'certificate': 'total model checked against every knot',
                      'model': cert.pack_state(state)}
        elif solved.returncode == 20:
            proof = ACTIVE.refute_file(cnf, deadline, 'union fate')
            result = {'verdict': 'dead', 'certificate': proof}
        else:
            result = {'verdict': 'undecided', 'reason': f'CaDiCaL exit {solved.returncode}'}
    except (cert.BudgetExpired, subprocess.TimeoutExpired):
        result = {'verdict': 'undecided', 'reason': 'union fate/certification deadline'}
    finally:
        cnf.unlink(missing_ok=True)
    result['seconds'] = time.monotonic() - start
    return result


cert.KEEP_DIR = PROOF_DIR
cert.external_slot = external_slot
cert.checked_refutation = checked_refutation
cert.union_fate = union_fate
search.Minisat22 = RetainingMinisat
search.checked_refutation = checked_refutation
