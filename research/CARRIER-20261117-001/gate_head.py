"""Gates for head_bond.py's stem bonds (CARRIER-20261117-001, the thread's own code, 2026-11-17). The stem of depth d is the top orbit
O_u with O_v's ancestor orbits at levels k + 1 .. k + d.
(a) least_bond (top-down free flags) against an independent brute force on 1,500 random relations with a stem part (run before, see
    the decision note) is repeated here on 1,000 relations.
(b) The exact projection onto the stem of depth 2 and O_v against SAT: 40 small-orbit patterns of KEEP-REACH's sample and mutations,
    depth 8, three random pairs each (O_u at level 1..3, O_v at least three levels below), the tree's rows (by the address-level path,
    as gate_window_tree.joint_exact) against the projection of all states of the address-level pattern, enumerated by Cadical.
(c) every_depth_head's tiers against direct_head at each depth: 30 patterns, d = 2, s = 3..8, remaining depth r = 0..3.
(d) No stem bound below a certified reading (the threshold run's cells, KEEP-REACH's exact readings at depth 11 and 13)."""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
import head_bond as hb  # noqa: E402
from head_bond import WindowTree, least_bond, every_depth_head, direct_head  # noqa: E402
from gate_window_tree import orbits_by_level  # noqa: E402
from gate_two_block import sat_rows, population  # noqa: E402
from pattern import pattern  # noqa: E402


def brute(rows, mu, nh, mv, nc):
    n = nh + mv + nc
    R = {tuple((r >> i) & 1 for i in range(n)) for r in rows}

    def free(S):
        return len({tuple(r[i] for i in S) for r in R}) == 2 ** len(S)
    out = None
    for mask in range(1, 1 << n):
        S = [i for i in range(n) if mask >> i & 1]
        if not (any(i < mu for i in S) and any(nh <= i < nh + mv for i in S)) or free(S):
            continue
        if all(free([S[i] for i in range(len(S)) if sub >> i & 1]) for sub in range((1 << len(S)) - 1)):
            out = len(S) if out is None else min(out, len(S))
    return out


def stem_exact(tree, N, F, lv, iu, k, iv, ks, d):
    """Rows over O_u, O_v's ancestors at levels k+1..k+d, and O_v, for one address-level pair, by the path (gate_window_tree style)."""
    parent = {}
    for n in range(ks):
        idx = 0
        for pi, (t, up, addrs) in enumerate(lv[n]):
            for ci in range(len(tree.children[t])):
                parent[(n + 1, idx)] = (n, pi, ci)
                idx += 1

    def chain(n, i):
        out = [(n, i)]
        while n > 0:
            n, i, _ = parent[(n, i)]
            out.append((n, i))
        return out[::-1]
    cu, cv = chain(k, iu), chain(ks, iv)
    b = max(j for j in range(len(cu)) if j < len(cv) and cu[j] == cv[j])
    Bn, Bi = cu[b]
    tB, upB, _ = lv[Bn][Bi]
    mu = tree.m[lv[k][iu][0]]
    if (Bn, Bi) == (k, iu):
        J = frozenset((x, x) for x in upB if x in F[N - k][tB])
        cur = tB
        rest = cv[b + 1:]
    else:
        kids = tree.children[tB]
        c1, c2 = parent[cu[b + 1]][2], parent[cv[b + 1]][2]
        J = set()
        for x, y in tree.W[tB]:
            if x in upB and all(tree.restrict(y, pos) in F[N - Bn - 1][c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2)):
                J.add((tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])))
        J = frozenset(J)
        t1, cur = kids[c1][0], kids[c2][0]
        for (n, i) in cu[b + 2:]:
            rel = tree.step(t1, F[N - n], parent[(n, i)][2], frozenset((z2, z1) for z1, z2 in J))
            J = frozenset((z1, z2) for z2, z1 in rel)
            t1 = lv[n][i][0]
        J = frozenset((a, z) for a, z in J if a in F[N - k][t1])
        rest = cv[b + 2:]
        # the descent of O_v's line from level b + 1 to level k carries no recorded bits
        pre = [x for x in rest if x[0] <= k]
        for (n, i) in pre:
            J = tree.step(cur, F[N - n], parent[(n, i)][2], J)
            cur = lv[n][i][0]
        rest = [x for x in rest if x[0] > k]
    nh = mu
    addrs = list(lv[k][iu][2])
    for (n, i) in rest:
        rel = tree.step(cur, F[N - n], parent[(n, i)][2], J)
        cur = lv[n][i][0]
        if n <= k + d:
            J = frozenset((h | (z << nh), z) for h, z in rel)
            nh += tree.m[cur]
            addrs += list(lv[n][i][2])
        else:
            J = rel
    addrs += list(lv[ks][iv][2])
    rows = frozenset(h | (x << nh) for h, x in J if x in F[N - ks][cur])
    return rows, addrs


if __name__ == '__main__':
    rng = random.Random(201711172)
    bad_a = 0
    for _ in range(1000):
        mu, h, mv, nc = rng.choice([1, 2, 4]), rng.choice([0, 1, 2, 4]), rng.choice([1, 2, 4]), rng.choice([0, 2])
        if mu + h + mv + nc > 11:
            nc = 0
        if mu + h + mv + nc > 11:
            h = 0
        n = mu + h + mv + nc
        p = rng.choice([0.3, 0.6, 0.9, 0.97])
        rows = frozenset(r for r in range(1 << n) if rng.random() < p)
        if not rows:
            continue
        hb._cache.clear()
        if least_bond(rows, mu, mu + h, mv, nc) != brute(rows, mu, mu + h, mv, nc):
            bad_a += 1
    print('a', bad_a, flush=True)

    pop = population()
    bad_b, checked_b = [], 0
    N, d = 8, 2
    for r in rng.sample(pop, 40):
        tree = WindowTree(r['key'])
        F = tree.feasible(N + 2)
        if not F[N][0]:
            continue
        lv = orbits_by_level(tree, N, F)
        K = pattern(r['key'], N)
        for _ in range(3):
            k = rng.randint(1, 3)
            ks = rng.randint(k + d + 1, N)
            iu, iv = rng.randrange(len(lv[k])), rng.randrange(len(lv[ks]))
            mine, addrs = stem_exact(tree, N, F, lv, iu, k, iv, ks, d)
            if len(addrs) > 20:
                continue
            theirs = sat_rows(K, addrs)
            checked_b += 1
            if mine != theirs:
                bad_b.append((r['index'], k, ks, iu, iv, len(mine), len(theirs)))
    print('b', checked_b, bad_b[:10], flush=True)

    bad_c, checked_c = [], 0
    for r in rng.sample(pop, 30):
        tree = WindowTree(r['key'])
        e = every_depth_head(tree, 3, 2, cap=8)
        R = e['r0']
        for s in range(3, 9):
            for rr in range(4):
                P = e['sequences']['r=%d' % rr if rr < R else 'r>=%d' % R]
                j = s - 3
                while j >= len(P):
                    j -= e['period']
                checked_c += 1
                x, y = P[j], direct_head(tree, 3 + s + rr, 3, s, 2, cap=8)
                if x != y:
                    bad_c.append((r['index'], s, rr, x, y))
    print('c', checked_c, bad_c[:10], flush=True)

    readings = []
    for f in sorted(HERE.glob('threshold_*.json')):
        dd = json.load(open(f))
        for cell in dd['cells']:
            readings.append((dd['index'], dd['key'], 11, cell['s'], cell['L_N']))
    for f in sorted((ROOT / 'research/KEEP-REACH-20261117-001').glob('exact_third_*_N1[13].json')):
        dd = json.load(open(f))
        for cell in dd['levels']:
            readings.append((dd['index'], dd['key'], dd['N'], cell['s'], cell['L_N']))
    bad_d, checked_d = [], 0
    for idx, key, Nr, s, L in readings:
        if s < 3 or not (isinstance(L, int) or (isinstance(L, str) and L.startswith('> '))):
            continue
        checked_d += 1
        x = direct_head(WindowTree(key), Nr, 3, s, 2, cap=8)
        low = L if isinstance(L, int) else int(L[2:]) + 1
        if x is not None and x < low:
            bad_d.append((idx, Nr, s, x, L))
    print('d', checked_d, bad_d[:10], flush=True)
    res = dict(a_relations=1000, a_mismatches=bad_a, b_projections=checked_b, b_mismatches=bad_b[:10], c_values=checked_c,
               c_mismatches=bad_c[:10], d_cells=checked_d, d_below=bad_d[:10],
               passed=bad_a == 0 and not bad_b and not bad_c and not bad_d)
    json.dump(res, open(HERE / 'gate_head.json', 'w'), indent=1)
    print(res)
