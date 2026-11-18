"""RING-READ-20261118-001B: scores the frozen predictions Q0-Q4 (research/RING-READ-20261118-001/preregistration.md, amendment).

  .venv/bin/python -B check.py gate          -> gate.json
  .venv/bin/python -B check.py T [T ...]      -> round_<T>.json
  .venv/bin/python -B check.py merge          -> results.json
in artifacts/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental/.
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reader3 as R3  # noqa: E402
R = R3.R

OUT = HERE.parents[2] / 'artifacts/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental'
ROUNDS = [10, 12, 14, 15, 16, 18, 20]
M = 6


def table_at(T):
    P = R.grow(T)
    st = R.stars_of(P)
    K = max(map(len, st))
    tab, _ = R.bond_table(st, M, K)
    return P, st, K, tab


def gate():
    out = {}
    for T in range(3, 10):
        _, st, K, tab = table_at(T)
        out[f'r3_exact_round_{T}'] = R3.r3(tab, K) == set(st)
    _, st, K, tab = table_at(10)
    big = next(s for s in st if len(s) == K)
    pair = tuple(sorted(sorted(big)[:2]))
    mut = dict(tab)
    mut[pair] = K + 1
    surv, rep = R3.repair(R3.r3(mut, K), mut, M, K)
    out['mutant_report'] = rep
    out['mutant_returns_true_junctions'] = any(s == frozenset(st) for s in surv)
    out['gate_passes'] = all(v for k, v in out.items() if k.startswith('r3_exact')) and not out['mutant_returns_true_junctions']
    return out


def one_round(T):
    t0 = time.time()
    P, st, K, tab = table_at(T)
    truth = frozenset(st)
    res = {'T': T, 'junctions': len(st), 'largest_junction': K}
    got = R3.r3(tab, K)
    res['Q1_r3'] = {'exact': got == set(truth), 'missed': len(truth - got), 'spurious': len(got - truth),
                    'missed_sizes': dict(Counter(map(len, truth - got))), 'spurious_sizes': dict(Counter(map(len, got - truth)))}
    surv, rep = R3.repair(got, tab, M, K)
    res['Q2_report'] = rep
    res['Q2_survivors'] = len(surv)
    res['Q2_works'] = len(surv) == 1 and surv[0] == truth
    nxt = R.true_next_round(T)
    res['Q3_regrown_round_equals_true'] = bool(res['Q2_works']) and R.next_round(surv[0]) == nxt
    works = {}
    for H in range(K - 1, 2, -1):
        pt = R.pooled(tab, H)
        s2, _ = R3.repair(R3.r3(pt, H + 1), pt, M, H)
        works[H] = len(s2) == 1 and s2[0] == truth
        if not works[H]:
            break
    res['Q4_works_by_horizon'] = works
    good = [H for H, w in works.items() if w]
    res['Q4_least_working_horizon'] = min(good) if good else None
    res['Q4_predicted'] = K - 1
    res['seconds'] = round(time.time() - t0, 1)
    return res


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == 'gate':
        g = gate()
        (OUT / 'gate.json').write_text(json.dumps(g, indent=1))
        print(json.dumps(g, indent=1))
    elif sys.argv[1] == 'merge':
        merged = {'gate': json.loads((OUT / 'gate.json').read_text()),
                  'rounds': [json.loads((OUT / f'round_{T}.json').read_text()) for T in ROUNDS]}
        (OUT / 'results.json').write_text(json.dumps(merged, indent=1))
        print('merged', len(merged['rounds']), 'rounds')
    else:
        for T in map(int, sys.argv[1:]):
            r = one_round(T)
            (OUT / f'round_{T}.json').write_text(json.dumps(r, indent=1))
            print(json.dumps(r), flush=True)
