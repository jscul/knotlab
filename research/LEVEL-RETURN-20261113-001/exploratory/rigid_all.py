"""Exploratory (levels <= 12): how many states (one value fixed; counted up to 5) do the seven alternating patterns have at their
living levels?"""
import json, gzip, sys
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
A = 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz'
recs = [json.loads(l) for l in gzip.open(A, 'rt')]
prof = lambda r: ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])
alt = [r for r in recs if r['return'] and prof(r)[4:] in ('10101010', '01010101')]
for idx, r in enumerate(alt):
    p = prof(r); row = []
    for n in range(4, 13):
        if p[n - 1] != '1': continue
        K = pattern(r['key'], n); used = sorted(set(K.ravel().tolist()))
        S = Cadical195()
        for a, b, c in K.tolist(): S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
        S.add_clause([used[0] + 1]); us = set(used); cnt = 0
        while cnt < 5 and S.solve():
            cnt += 1; S.add_clause([-l for l in S.get_model() if abs(l) - 1 in us])
        row.append((n, len(used), 1 << n, cnt))
    print(idx + 1, p, row, flush=True)
