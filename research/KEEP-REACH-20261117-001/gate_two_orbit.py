"""Gates for two_orbit.py (KEEP-REACH-20261117-001, the thread's own code, 2026-11-17).
(a) least_cross_bond against an independent brute force (every subset meeting both orbits; bond = constrained with every proper subset
    free, checked over all proper subsets) on 3,000 random relations with orbit sizes 1, 2 and 4.
(b) Agreement with Theorem W's verdicts (DIRECT-REACH's window_tree_census.json) on the 85 small-orbit population-D descriptions:
    tie at every s gives 2 at every s; a two-orbit three-member bond and no tie gives 3; at every depth tier.
(c) No two-orbit bound below a decided census value at depth 9 (top level 3, s = 1..4, tier r = 9 - 3 - s), on every small-orbit
    census description."""
import gzip
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from two_orbit import least_cross_bond, every_depth_cross  # noqa: E402
from window_tree import WindowTree  # noqa: E402


def brute(J, mu, mv):
    if not J:
        return None
    n = mu + mv
    rows = {tuple(((a >> i) & 1) for i in range(mu)) + tuple(((z >> j) & 1) for j in range(mv)) for a, z in J}

    def free(S):
        return len({tuple(r[i] for i in S) for r in rows}) == 2 ** len(S)
    best = None
    for mask in range(1, 1 << n):
        S = [i for i in range(n) if mask >> i & 1]
        if not (any(i < mu for i in S) and any(i >= mu for i in S)):
            continue
        if free(S):
            continue
        if all(free([S[i] for i in range(len(S)) if sub >> i & 1]) for sub in range((1 << len(S)) - 1)):
            best = len(S) if best is None else min(best, len(S))
    return best


def at(seq, r0, r, s, period):
    P = seq['r=%d' % r if r < r0 else 'r>=%d' % r0]
    while s > len(P):
        s -= period
    return P[s - 1]


if __name__ == '__main__':
    rng = random.Random(1117)
    bad_a = 0
    for _ in range(3000):
        mu, mv = rng.choice([1, 2, 4]), rng.choice([1, 2, 4])
        J = frozenset((a, z) for a in range(1 << mu) for z in range(1 << mv) if rng.random() < rng.choice([0.3, 0.6, 0.9]))
        if least_cross_bond(J, mu, mv) != brute(J, mu, mv):
            bad_a += 1
    wt = json.load(open(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory/window_tree_census.json'))['cases']
    keys = {}
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        r = json.loads(line)
        if r.get('union') == 'alive' and 'key' in r:
            keys[r['case']] = r
    bad_b, checked_b = [], 0
    for cid, row in wt.items():
        if 'k3' not in row:
            continue
        e = every_depth_cross(WindowTree(keys[cid]['key']), 3)
        v = row['k3']['verdict']
        for name, seq in e['sequences'].items():
            for x in seq:
                checked_b += 1
                if (v == 'tie at every s' and x != 2) or (v.startswith('no tie; two-orbit 3-bond at every') and x != 3):
                    bad_b.append((cid[:12], name, x))
    bad_c, checked_c = [], 0
    for cid, rec in keys.items():
        try:
            tree = WindowTree(rec['key'])
        except ValueError:
            continue
        e = every_depth_cross(tree, 3)
        for lv in rec['levels']:
            if isinstance(lv['L_N'], int):
                checked_c += 1
                x = at(e['sequences'], e['r0'], 9 - 3 - lv['s'], lv['s'], e['period'])
                if x is not None and x < lv['L_N']:
                    bad_c.append((cid[:12], lv['s'], x, lv['L_N']))
    res = dict(a_relations=3000, a_mismatches=bad_a, b_values=checked_b, b_mismatches=bad_b[:10], c_cells=checked_c,
               c_below_census=bad_c[:10], passed=bad_a == 0 and not bad_b and not bad_c)
    json.dump(res, open(HERE / 'gate_two_orbit.json', 'w'), indent=1)
    print(res)
