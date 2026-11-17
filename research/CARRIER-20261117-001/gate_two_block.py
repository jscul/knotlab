"""Gates for two_block.py (CARRIER-20261117-001, the thread's own code, 2026-11-17).
(a) least_block_bond against an independent brute force (every subset holding a distinction of each orbit; bond = constrained with every
    proper subset free, checked over all proper subsets) on 2,000 random relations with orbit sizes 1, 2, 4 and up to 4 child bits.
(b) The exact orbit-and-block projection against SAT: on 40 small-orbit patterns of KEEP-REACH's sample and mutations, at depth 7, three
    random pairs (O_u at level 1..3, O_v at a level above the bottom), the tree's rows against the projection of all states of the
    address-level pattern onto O_u, O_v and O_v's children, enumerated by Cadical with blocking clauses.
(c) every_depth_block's tiers against direct_block at each depth: 40 patterns, s = 1..6, remaining depth r = 0..4.
(d) No orbit-and-block bound below a decided census value at depth 9 (top level 3, s = 1..4, r = 9 - 3 - s) on every small-orbit census
    description, and none below a certified reading of the threshold run or of KEEP-REACH's exact readings."""
import gzip
import itertools
import json
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from two_block import WindowTree, block_rows, least_block_bond, every_depth_block, direct_block  # noqa: E402
from gate_window_tree import aid, orbits_by_level, joint_exact  # noqa: E402
from pattern import pattern, clauses  # noqa: E402


def brute(rows, mu, mv, nc):
    if not rows:
        return None
    n = mu + mv + nc
    R = {tuple((r >> i) & 1 for i in range(n)) for r in rows}

    def free(S):
        return len({tuple(r[i] for i in S) for r in R}) == 2 ** len(S)
    out = None
    for mask in range(1, 1 << n):
        S = [i for i in range(n) if mask >> i & 1]
        if not (any(i < mu for i in S) and any(mu <= i < mu + mv for i in S)) or free(S):
            continue
        if all(free([S[i] for i in range(len(S)) if sub >> i & 1]) for sub in range((1 << len(S)) - 1)):
            out = len(S) if out is None else min(out, len(S))
    return out


def sat_rows(K, addrs):
    vs = [aid(a) + 1 for a in addrs]
    if len(set(vs)) < len(vs):
        raise AssertionError('addresses overlap')
    out = set()
    with Cadical195(bootstrap_with=clauses(K)) as s:
        while s.solve():
            m = s.get_model()
            bits = [1 if v - 1 < len(m) and m[v - 1] > 0 else 0 for v in vs]  # a variable in no clause yet is free; 0 is allowed
            out.add(sum(b << i for i, b in enumerate(bits)))
            s.add_clause([-v if b else v for v, b in zip(vs, bits)])
    return frozenset(out)


def at(e, r, s):
    r0, period = e['r0'], e['period']
    P = e['sequences']['r=%d' % r if r <= r0 else 'r>=%d' % (r0 + 1)]
    while s > len(P):
        s -= period
    return P[s - 1]


def population():
    rows = []
    for name in ('sample_keep.jsonl', 'mutants_keep.jsonl'):
        for line in open(ROOT / 'research/KEEP-REACH-20261117-001' / name):
            r = json.loads(line)
            if r.get('small_orbits') and r.get('alive_every_depth'):
                rows.append(r)
    return rows


if __name__ == '__main__':
    rng = random.Random(20261117)
    bad_a = 0
    for _ in range(2000):
        mu, mv, nc = rng.choice([1, 2, 4]), rng.choice([1, 2, 4]), rng.choice([0, 2, 4])
        n = mu + mv + nc
        if n > 10:
            nc = 0
            n = mu + mv
        p = rng.choice([0.3, 0.6, 0.9])
        rows = frozenset(r for r in range(1 << n) if rng.random() < p)
        if least_block_bond(rows, mu, mv, nc) != brute(rows, mu, mv, nc):
            bad_a += 1
    print('a', bad_a, flush=True)

    pop = population()
    picks = rng.sample(pop, 40)
    bad_b, checked_b = [], 0
    N = 7
    for r in picks:
        tree = WindowTree(r['key'])
        F = tree.feasible(N + 2)
        if not F[N][0]:
            continue
        lv = orbits_by_level(tree, N, F)
        K = pattern(r['key'], N)
        for _ in range(3):
            k = rng.randint(1, 3)
            ks = rng.randint(k + 1, N - 1)
            iu, iv = rng.randrange(len(lv[k])), rng.randrange(len(lv[ks]))
            t1, t2 = lv[k][iu][0], lv[ks][iv][0]
            J = joint_exact(tree, N, F, lv, iu, k, iv, ks)
            mine = block_rows(tree, t1, t2, J, F[N - ks - 1])[0]
            av = lv[ks][iv][2]
            kids = [av[p // 2] + (p % 2,) for p in range(2 * len(av))]
            theirs = sat_rows(K, list(lv[k][iu][2]) + list(av) + kids)
            checked_b += 1
            if mine != theirs:
                bad_b.append((r['index'], k, ks, iu, iv, len(mine), len(theirs)))
    print('b', checked_b, bad_b, flush=True)

    bad_c, checked_c = [], 0
    for r in rng.sample(pop, 40):
        tree = WindowTree(r['key'])
        e = every_depth_block(tree, 3, cap=8)
        for s in range(1, 7):
            for rr in range(5):
                checked_c += 1
                x, y = at(e, rr, s), direct_block(tree, 3 + s + rr, 3, s, cap=8)
                if x != y:
                    bad_c.append((r['index'], s, rr, x, y))
    print('c', checked_c, bad_c[:10], flush=True)

    bad_d, checked_d = [], 0
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        rec = json.loads(line)
        if rec.get('union') != 'alive' or 'key' not in rec:
            continue
        try:
            tree = WindowTree(rec['key'])
        except ValueError:
            continue
        e = every_depth_block(tree, 3, cap=8)
        for cell in rec['levels']:
            if isinstance(cell['L_N'], int):
                checked_d += 1
                x = at(e, 9 - 3 - cell['s'], cell['s'])
                if x is not None and x < cell['L_N']:
                    bad_d.append((rec['case'][:12], cell['s'], x, cell['L_N']))
    readings = []
    for f in sorted(HERE.glob('threshold_*.json')):
        d = json.load(open(f))
        for cell in d['cells']:
            readings.append((d['index'], d['key'], 11, cell['s'], cell['L_N'], d['bound']))
    for f in sorted((ROOT / 'research/KEEP-REACH-20261117-001').glob('exact_third_*_N1[13].json')):
        d = json.load(open(f))
        for cell in d.get('cells', d.get('levels', [])):
            readings.append((d.get('index', f.stem), d['key'], d.get('N', 11), cell['s'], cell['L_N'], None))
    for idx, key, Nr, s, L, c in readings:
        if not (isinstance(L, int) or (isinstance(L, str) and L.startswith('> '))):
            continue
        checked_d += 1
        x = direct_block(WindowTree(key), Nr, 3, s, cap=8)
        low = L if isinstance(L, int) else int(L[2:]) + 1
        if x is not None and x < low:
            bad_d.append((idx, Nr, s, x, L))
    print('d', checked_d, bad_d[:10], flush=True)
    res = dict(a_relations=2000, a_mismatches=bad_a, b_projections=checked_b, b_mismatches=bad_b, c_values=checked_c,
               c_mismatches=bad_c[:10], d_cells=checked_d, d_below=bad_d[:10],
               passed=bad_a == 0 and not bad_b and not bad_c and not bad_d)
    json.dump(res, open(HERE / 'gate_two_block.json', 'w'), indent=1)
    print(res)
