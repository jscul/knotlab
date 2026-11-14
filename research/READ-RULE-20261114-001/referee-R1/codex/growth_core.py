"""READ referee helper: permitted older unfolded-CNF search, fresh witness audit.

No Python below the READ producer experiment or proof checker is read/imported.
The older grow_core intentionally extracts DirectSearch from FREE-TARGET;
that transitive source was expressly confirmed permitted by the lead.
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from pysat.solvers import Solver

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex'
OLDER = ROOT / 'research/CARRY-BOUND-20261114-001/referee-R1/codex/grow_core.py'
spec = importlib.util.spec_from_file_location('permitted_older_grow_core', OLDER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

READS = {str(OLDER.relative_to(ROOT)): hashlib.sha256(OLDER.read_bytes()).hexdigest()}
READS.update(old.READS)

def read(path):
    path = Path(path)
    relative = str(path.relative_to(ROOT))
    assert not (path.suffix == '.py' and relative.startswith((
        'experiments/READ-RULE-20261114-001B/',
        'proofs/READ-RULE-20261114-001Z/')))
    data = path.read_bytes()
    READS[relative] = hashlib.sha256(data).hexdigest()
    return data

def projection(clauses, support):
    """Independently enumerate the complete projection using MiniSat22."""
    allowed = []
    with Solver(name='minisat22', bootstrap_with=clauses) as sat:
        living = sat.solve()
        for state in range(1 << len(support)):
            assumptions = [v + 1 if state >> j & 1 else -(v + 1)
                           for j, v in enumerate(support)]
            if sat.solve(assumptions=assumptions):
                allowed.append(state)
    return living, allowed

def verify(clauses, support, roots=None, targets=None, require=True):
    support = list(support)
    living, allowed = projection(clauses, support)
    deletions = []
    for drop in range(len(support)):
        keep = [j for j in range(len(support)) if j != drop]
        got = sorted({sum(((state >> j) & 1) << p for p, j in enumerate(keep))
                      for state in allowed})
        deletions.append({'dropped': support[drop], 'allowed': got,
                          'full': len(got) == 1 << len(keep)})
    non_shattered = 0 < len(allowed) < 1 << len(support)
    endpoints = ((roots is None or bool(set(support) & set(roots))) and
                 (targets is None or bool(set(support) & set(targets))))
    is_bond = (living and len(set(support)) == len(support) and endpoints and
               non_shattered and all(d['full'] for d in deletions))
    record = {'support': support, 'living': living, 'allowed': allowed,
              'non_shattered': non_shattered, 'deletions': deletions,
              'every_single_deletion_full': all(d['full'] for d in deletions),
              'endpoints_valid': endpoints, 'is_bond': is_bond,
              'backend': 'minisat22; search uses cadical195/glucose42'}
    if require and not is_bond:
        raise ValueError(record)
    return record

def controls():
    result = old.controls()
    clauses = [[1, 2, 3], [-1, -2, -3]]
    negative = {}
    for name, support, roots, targets in (
        ('shattered_pair', [0, 2], {0}, {2}),
        ('nonminimal_superset', [0, 1, 2, 3], {0}, {3}),
        ('wrong_target', [0, 1, 2], {0}, {3}),
    ):
        try:
            verify(clauses, support, roots, targets)
        except ValueError:
            negative[name] = True
        else:
            raise AssertionError('invalid witness accepted: ' + name)
    verify(clauses, [0, 1, 2], {0}, {2})
    result['fresh_witness_checker_invalid_controls_rejected'] = negative
    return result

def sources():
    return {**READS, **old.READS,
            str(Path(__file__).relative_to(ROOT)):
                hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
