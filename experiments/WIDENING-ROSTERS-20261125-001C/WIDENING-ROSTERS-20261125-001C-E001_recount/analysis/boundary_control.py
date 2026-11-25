"""Check the two-knot/round-one exception using two growth engines and exact states."""

from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(next((ROOT / 'experiments/KNOTS-WITHIN-REACH-20261125-001A').glob('*-E001*'))))
import kwr
sys.path.insert(0, str(next((ROOT / 'experiments/LOCAL-ROUND-20261123-001A').glob('*-E001*'))))
import lr_core

START = [[0, 1, 2], [0, 3, 4]]


def projection_masks(knots, law):
    allowed = [set() for _ in knots]
    for bits in product(range(2), repeat=1 + max(max(k) for k in knots)):
        rows = [tuple(bits[i] for i in knot) for knot in knots]
        if law == 'parity':
            accepts = all(sum(row) % 2 == 0 for row in rows)
        else:
            accepts = all(0 < sum(row) < len(row) for row in rows)
        if accepts:
            for projection, row in zip(allowed, rows):
                projection.add(row)
    return allowed


def read(law):
    g = kwr.Grown('two', kwr.make_law('L0', law), 1, S=kwr.pm.from_stars(START), parts_every_round=False)
    second = lr_core.Str([k[:] for k in START])
    # No closing group exists in this control. NAE and parity then use the same count.
    lr_core.own_round(second, 'ORD', 'STALL')
    first_supports = g.S.places
    second_supports = second.places
    first = len(g.members[1])
    other = sum(bool(second.usable(i)) for i in range(len(second_supports)))
    assert first == other == 4
    arity = 3
    target = set(product(range(2), repeat=arity))
    target = {x for x in target if (sum(x) % 2 == 0 if law == 'parity' else 0 < sum(x) < arity)}
    checks = []
    for supports in [first_supports, second_supports]:
        verdict = [x == target for x in projection_masks(supports, law)]
        assert all(verdict)
        checks.append(len(verdict))
    names = ['a', 'b', 'c']
    excluded = set(product(range(2), repeat=arity)) - target
    cnf = ';'.join(' '.join('~' + v if b else v for v, b in zip(names, x)) for x in sorted(excluded))
    cmd = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--loops', 'a', 'b', '--contact', 'c', '--json']
    report = json.loads(subprocess.check_output(cmd, cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')}))
    return dict(law=law, members=[first,other], proposed=3, full_stage_checked=checks, canonical_report=report)


if __name__ == '__main__':
    start = monotonic()
    for law in ['nae','parity']:
        read(law)
    rehearsal = monotonic() - start
    print(json.dumps(dict(rehearsal_seconds=rehearsal, evidence=[read(law) for law in ['nae','parity']]),indent=2))
