"""Exploratory (KEEP-REACH-20261117-001, the thread's own, 2026-11-17, before any design is frozen): the four small-orbit descriptions
that never forget and are not direct, with two direct ones as controls. From the exact two-orbit joints at every depth
(window_tree.every_depth_pairs' pair states, stable tier r >= r0): for each s, whether some pair of orbits (level 3, level 3 + s) has a
non-product joint, and the least bond of any size inside the two orbits that meets both (minimal constrained set in the joint)."""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
import window_tree as W  # noqa: E402


def least_cross_bond(J, mu, mv):
    """Least size of a subset of the two orbits, meeting both, that is constrained in J with every proper subset free."""
    if not J:
        return None
    n = mu + mv
    rows = [tuple(((a >> i) & 1) for i in range(mu)) + tuple(((z >> j) & 1) for j in range(mv)) for a, z in J]
    free_cache = {}

    def free(S):
        if S not in free_cache:
            free_cache[S] = len({tuple(r[i] for i in S) for r in rows}) == 1 << len(S)
        return free_cache[S]
    best = None
    for size in range(2, n + 1):
        for S in itertools.combinations(range(n), size):
            if not (min(S) < mu <= max(S)):
                continue
            if free(S):
                continue
            if all(free(T) for T in itertools.combinations(S, size - 1)):
                return size
    return best


def rectangular(J):
    A = {a for a, _ in J}
    B = {z for _, z in J}
    return len(J) == len(A) * len(B)


def profile(key, k=3, smax=24):
    tree = W.WindowTree(key)
    F = tree.feasible(12)
    r0 = next(r for r in range(12) if F[r] == F[r + 1])
    Fc = F[r0]
    # reuse every_depth_pairs' construction of the pair-state sequence at stable depth
    st = W.level_states(tree, k, [Fc] * (k + 2))
    out = []
    import types
    res = W.every_depth_pairs(tree, k)
    # recompute the stable pair states explicitly (as every_depth_pairs does) to read the joints
    S0 = set()
    for t, up in st[k]:
        S0.add((t, t, frozenset((x, x) for x in up)))
    for b in range(k):
        for t, up in st[b]:
            kids = tree.children[t]
            for c1, c2 in itertools.permutations(range(len(kids)), 2):
                J = set()
                for x, y in tree.W[t]:
                    if x in up and all(tree.restrict(y, pos) in Fc[c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2)):
                        J.add((tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])))
                cur = {(kids[c1][0], kids[c2][0], frozenset(J))}
                for lvl in range(b + 1, k):
                    nxt = set()
                    for t1, t2, J in cur:
                        for ci in range(len(tree.children[t1])):
                            rel = tree.step(t1, Fc, ci, frozenset((z2, z1) for z1, z2 in J))
                            J1 = frozenset((z1, z2) for z2, z1 in rel)
                            for cj in range(len(tree.children[t2])):
                                nxt.add((tree.children[t1][ci][0], tree.children[t2][cj][0], tree.step(t2, Fc, cj, J1)))
                    cur = nxt
                for t1, t2, J in cur:
                    S0.add((t1, t2, frozenset((a, z) for a, z in J if a in Fc[t1])))
    S = frozenset(S0)
    for s in range(1, smax + 1):
        nxt = set()
        for t1, t2, J in S:
            for cj in range(len(tree.children[t2])):
                nxt.add((t1, tree.children[t2][cj][0], tree.step(t2, Fc, cj, J)))
        S = frozenset(nxt)
        joints = [(t1, t2, frozenset((a, z) for a, z in J if z in Fc[t2])) for t1, t2, J in S]
        nonprod = any(J and not rectangular(J) for _, _, J in joints)
        bonds = [least_cross_bond(J, tree.m[t1], tree.m[t2]) for t1, t2, J in joints]
        bonds = [b for b in bonds if b]
        out.append((s, nonprod, min(bonds) if bonds else None))
    return r0, out


if __name__ == '__main__':
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    import gzip
    keys = {}
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        r = json.loads(line)
        if r['case'] in rows:
            keys[r['case']] = r['key']
    four = sorted(c for c, r in rows.items() if r['r'] is None and r['name'] != 'direct')
    direct = sorted(c for c, r in rows.items() if r['name'] == 'direct')[:2]
    res = {}
    for c in four + direct:
        r0, out = profile(keys[c])
        res[c] = dict(profile=rows[c]['profile'], name=rows[c]['name'], r0=r0, by_s=out)
        print(c[:12], rows[c]['name'], rows[c]['profile'], 'r0', r0, [(s, int(n), b) for s, n, b in out[:12]], flush=True)
    json.dump(res, open(HERE / 'look_four.json', 'w'), indent=1)
