"""Exploratory: search, by SAT, for a state that is a function of a feature automaton's final state (the final states of the
automaton's runs from each start, the first letter, the last letter, the parity), at the alive levels read (to 11); then hand any
table found to the all-level prover."""
import json, gzip, sys, itertools
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
sys.path.insert(0, 'proofs/LEVEL-RETURN-20261113-001B/LEVEL-RETURN-20261113-001B-P001_alternation')
from certify import pattern
from prover import check, words_of
A = 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz'
recs = [json.loads(l) for l in gzip.open(A, 'rt')]
prof = lambda r: ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])
alt = [r for r in recs if r['return'] and prof(r)[4:] in ('10101010', '01010101')]
def feature_dfa(aut, s):
    sw, d0, d1 = aut
    start = ('S',)
    states = {start: 0}; delta = []; order = [start]; i = 0
    def nxt(st, b):
        inv = lambda q, c: (d0 if (c ^ sw[q]) == 0 else d1)[q]
        if st == ('S',):
            return (tuple((d0 if b == 0 else d1)[q] for q in range(s)), tuple(inv(q, b) for q in range(s)), (b,), (b,), b)
        runs, iruns, first, last, par = st
        return (tuple((d0 if b == 0 else d1)[q] for q in runs), tuple(inv(q, b) for q in iruns), first if len(first) == 2 else first + (b,), (last + (b,))[-2:], par ^ b)
    while i < len(order):
        st = order[i]; row = []
        for b in (0, 1):
            t = nxt(st, b)
            if t not in states: states[t] = len(order); order.append(t)
            row.append(states[t])
        delta.append(row); i += 1
    return delta, len(order)
def final(delta, n):
    X = np.arange(1 << n); m = np.zeros(1 << n, dtype=np.int64)
    for i in range(n - 1, -1, -1): m = np.array(delta)[m, (X >> i) & 1]
    return m
for idx, r in enumerate(alt):
    s, sw, d0, d1, pls = r['key']; p = prof(r)
    par = 0 if p[9] == '1' else 1  # alive parity from level 10
    delta, k = feature_dfa((sw, d0, d1), s)
    S = Cadical195()
    for n in range(5, 12):
        if p[n - 1] != '1' or n % 2 != par: continue
        f = final(delta, n); K = np.unique(np.sort(f[pattern(r['key'], n)], 1), axis=0)
        for a, b, c in K.tolist():
            if a == b == c: S.add_clause([1, -1]); S.add_clause([1]); S.add_clause([-1]); break
            S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    ok = S.solve()
    msg = 'none'
    if ok:
        mdl = S.get_model(); out = [1 if mdl[j] > 0 else 0 for j in range(k)] if len(mdl) >= k else None
        res = check((sw, d0, d1), words_of(s), pls, (delta, out, 0), par, 4)
        msg = f'table found on {k} feature states; all-level check: {res if not res[0] else (True, res[1])}'
    print(idx + 1, p, 'alive parity', par, 'feature states', k, msg, flush=True)
