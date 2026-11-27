"""Canonical whole-structure checks on the recorded transfer and fair-reveal examples."""
import argparse
from itertools import product
import json
import os
from pathlib import Path
import resource
import subprocess
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
CASES = [
    ('transfer', 'even', ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))),
    ('fair reveal', 'nae', ((0, 2, 3), (1, 2, 3))),
]


def check(law, scopes, names, row):
    clauses = []
    for scope in scopes:
        for bits in product((0, 1), repeat=len(scope)):
            allowed = sum(bits) % 2 == 0 if law == 'even' else len(set(bits)) == 2
            if not allowed:
                clauses.append(' '.join(('-' if b else '') + f'd{i}' for i, b in zip(scope, bits)))
    args = [str(ROOT/'.venv/bin/python'), '-B', '-m', 'knotlab', 'check', '--cnf', '; '.join(clauses),
            '--loops', *[f'd{i}' for i in row[:-1]], '--contact', f'd{row[-1]}', '--witnesses',
            *[f'd{i}' for i in names if i not in row], '--json']
    data = json.loads(subprocess.check_output(args, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT/'tools'))))
    assert data['is_knot']
    return dict(scope=row, allowed=data['allowed'], is_knot=data['is_knot'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--first-only', action='store_true')
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))
    t = perf_counter()
    result = {}
    for label, law, scopes in CASES:
        names = sorted(set.union(*map(set, scopes)))
        result[label] = [check(law, scopes, names, row) for row in (scopes[:1] if args.first_only else scopes)]
    result['seconds'] = round(perf_counter()-t, 4)
    print(json.dumps(result, indent=2))
