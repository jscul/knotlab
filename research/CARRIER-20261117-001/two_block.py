"""Bonds inside an orbit and a block (CARRIER-20261117-001, the thread's own code, 2026-11-17): the least bond inside an orbit O_u at
level k and the block of an orbit O_v at level k + s (O_v with its child orbits at level k + s + 1) that holds a distinction of O_u
and one of O_v, at every depth N >= k + s and every s >= 1.

The threshold run found that bace53f8f952-147, which has no two-orbit bond from level 3 past s = 2, has a bond of 4 members at s = 5
and 6 at depth 11: one address at level 3, one at level 3 + s and two at level 4 + s. So the bond uses O_v's children. The windows form
a tree (window_tree.py), so the projection of the allowed states onto O_u, O_v and O_v's children is exact: it is the pair projection
J(O_u, O_v) before O_v's feasibility filter, joined with O_v's window W[t_v] whose child orbits are feasible at the remaining depth
below them. A bond in it is a bond of the pattern meeting levels k and k + s, so its least size bounds L_N(k, s) from above.

`every_depth_block` is `two_orbit.every_depth_cross` (KEEP-REACH-20261117-001, refereed) with that property in place of the two-orbit
one. The children read F[r - 1] where O_v reads F[r], so the depth tiers run to r0 + 1 (r0 + 1 standing for every r >= r0 + 1); at
r = 0, O_v is at the bottom level and has no children, and the property is the two-orbit one."""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree, level_states  # noqa: E402


def block_rows(tree, t1, t2, J, Fchild):
    """Rows over O_u (mu bits), O_v (mv bits) and O_v's children (2 mv bits, positions 2i + b as in W) of the exact projection.
    J: pairs (a, x) not yet filtered by O_v's feasibility. Fchild: feasible sets below the children (None: O_v is at the bottom)."""
    mu, mv = tree.m[t1], tree.m[t2]
    if Fchild is None:
        return frozenset(a | (x << mu) for a, x in J if x in tree.Wl[t2]), mu, mv, 0
    by_x = {}
    for x, y in tree.W[t2]:
        if all(tree.restrict(y, pos) in Fchild[c] for c, pos in tree.children[t2]):
            by_x.setdefault(x, []).append(y)
    rows = frozenset(a | (x << mu) | (y << (mu + mv)) for a, x in J for y in by_x.get(x, ()))
    return rows, mu, mv, 2 * mv


_cache = {}


def least_block_bond(rows, mu, mv, nc, cap=None):
    """Least size of a set holding a distinction of O_u (bits < mu) and one of O_v (bits mu..mu+mv-1), constrained in rows, every proper
    subset free; None if none of size at most cap (cap None: any size). Level by level: a set is a candidate when all its subsets one
    smaller are free (free sets are closed under subsets), and a candidate that is not free is a bond. Freeness of a batch of candidates
    is read by counting the distinct projections of the rows, vectorised."""
    n = mu + mv + nc
    top = n if cap is None else min(n, cap)
    key = (rows, mu, mv, nc)
    hit = _cache.get(key)
    if hit is not None and (hit[0] is not None or hit[1] >= top):
        return hit[0] if hit[0] is None or hit[0] <= top else None
    if not rows:
        _cache[key] = (None, n)
        return None
    R = np.array(sorted(rows), dtype=np.int64)
    bits = ((R[:, None] >> np.arange(n)) & 1).astype(np.int64)
    free_prev = {(i,) for i in range(n) if len(np.unique(bits[:, i])) == 2}
    out = None
    for size in range(2, top + 1):
        cands = [S for S in itertools.combinations(range(n), size)
                 if all(T in free_prev for T in itertools.combinations(S, size - 1))]
        if not cands:
            break
        free_now = set()
        weights = 1 << np.arange(size)
        full = 1 << size
        step = max(1, 4_000_000 // (len(R) * size))
        for i in range(0, len(cands), step):
            C = np.array(cands[i:i + step])
            codes = (bits[:, C] * weights).sum(axis=2) if len(R) >= full else None
            if codes is None:
                distinct = np.zeros(len(C), dtype=np.int64)
            else:
                codes.sort(axis=0)
                distinct = 1 + (np.diff(codes, axis=0) != 0).sum(axis=0)
            for S, d in zip(cands[i:i + step], distinct):
                if d == full:
                    free_now.add(S)
                elif S[0] < mu and any(mu <= j < mu + mv for j in S):
                    out = size
                    break
            if out is not None:
                break
        if out is not None:
            break
        free_prev = free_now
    _cache[key] = (out, top)
    return out


def best(values):
    vals = [v for v in values if v is not None]
    return min(vals) if vals else None


def best_capped(rel_args, cap=None):
    """min over relations of least_block_bond, searching each only below the best found so far."""
    cur = None
    for args in rel_args:
        lim = cap if cur is None else (cur - 1 if cap is None else min(cap, cur - 1))
        if lim is not None and lim < 2:
            break
        v = least_block_bond(*args, cap=lim)
        if v is not None and (cur is None or v < cur):
            cur = v
    return cur


def pair_states_raw(tree, N, k, s, F, states):
    """window_tree.pair_joints without its last filter on O_v (the filter on O_u in case (ii) is kept): (t_u, t_v, J)."""
    results = set()
    for t, up in states[k]:
        cur = {(t, frozenset((x, x) for x in up))}
        for lvl in range(k, k + s):
            Fr = F[N - lvl - 1]
            nxt = set()
            for t2, J in cur:
                for ci, (c, pos) in enumerate(tree.children[t2]):
                    nxt.add((c, tree.step(t2, Fr, ci, J)))
            cur = nxt
        for t2, J in cur:
            results.add((t, t2, J))
    for b in range(k):
        for t, up in states[b]:
            kids = tree.children[t]
            Fr = F[N - b - 1]
            for c1, c2 in itertools.permutations(range(len(kids)), 2):
                J = set()
                for x, y in tree.W[t]:
                    if x not in up:
                        continue
                    if all(tree.restrict(y, pos) in Fr[c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2)):
                        J.add((tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])))
                cur = {(kids[c1][0], kids[c2][0], frozenset(J))}
                for lvl in range(b + 1, k + s):
                    nxt = set()
                    for t1, t2, J in cur:
                        if lvl < k:
                            Fr1 = F[N - lvl - 1]
                            for ci, (c, pos) in enumerate(tree.children[t1]):
                                swapped = frozenset((z2, z1) for z1, z2 in J)
                                rel = tree.step(t1, Fr1, ci, swapped)
                                J1 = frozenset((z1, z2) for z2, z1 in rel)
                                for cj, (c2_, pos2) in enumerate(tree.children[t2]):
                                    nxt.add((c, c2_, tree.step(t2, Fr1, cj, J1)))
                        else:
                            Fr2 = F[N - lvl - 1]
                            for cj, (c2_, pos2) in enumerate(tree.children[t2]):
                                nxt.add((t1, c2_, tree.step(t2, Fr2, cj, J)))
                    cur = nxt
                Fu = F[N - k]
                for t1, t2, J in cur:
                    results.add((t1, t2, frozenset((a, z) for a, z in J if a in Fu[t1])))
    return results


def direct_block(tree, N, k, s, cap=None):
    """The least orbit-and-block bond at one depth N, from the depth-N feasible sets (no periodicity used)."""
    F = tree.feasible(N)
    st = level_states(tree, N, F)
    Fchild = F[N - k - s - 1] if N > k + s else None
    return best_capped((block_rows(tree, t1, t2, J, Fchild) for t1, t2, J in pair_states_raw(tree, N, k, s, F, st)), cap=cap)


def every_depth_block(tree, k, Rmax=12, smax=400, cap=None):
    """As two_orbit.every_depth_cross, with the orbit-and-block property; tiers r = 0..r0 and r >= r0 + 1."""
    F = tree.feasible(Rmax)
    r0 = next((r for r in range(Rmax) if F[r] == F[r + 1]), None)
    if r0 is None:
        return None
    Fc = F[r0]
    st = level_states(tree, k, [Fc] * (k + 2))
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

    def advance(S, Fr):
        nxt = set()
        for t1, t2, J in S:
            for cj in range(len(tree.children[t2])):
                nxt.add((t1, tree.children[t2][cj][0], tree.step(t2, Fr, cj, J)))
        return frozenset(nxt)

    seen, seq = {}, []
    S = frozenset(S0)
    for s in range(smax + 1):
        if S in seen:
            start = seen[S]
            break
        seen[S] = s
        seq.append(S)
        S = advance(S, Fc)
    else:
        raise RuntimeError('no repeat')
    period = len(seq) - start

    def S_at(s):
        return seq[s] if s < len(seq) else seq[start + (s - start) % period]

    def props(S, Fchild):
        return best_capped((block_rows(tree, t1, t2, J, Fchild) for t1, t2, J in S), cap=cap)

    out = {}
    horizon = start + period + r0 + 2
    for r in range(r0 + 2):
        Fchild = None if r == 0 else F[r - 1]
        P = []
        for s in range(1, horizon + period + 1):
            if r >= r0:
                P.append(props(S_at(s), Fchild))
                continue
            back = r0 - r
            if s - back < 1:
                P.append(direct_block(tree, k + s + r, k, s, cap=cap))
                continue
            S = S_at(s - back)
            for j in range(back, 0, -1):
                S = advance(S, F[r + j - 1])
            P.append(props(S, Fchild))
        out['r=%d' % r if r <= r0 else 'r>=%d' % r] = P
    return dict(r0=r0, start=start, period=period, horizon=horizon, alive_every_depth=all(bool(F[n][0]) for n in range(r0 + 1)),
                sequences=out)


if __name__ == '__main__':
    import json
    rows = {str(json.loads(l)['index']): json.loads(l) for l in open(ROOT / 'research/KEEP-REACH-20261117-001/mutants_keep.jsonl')}
    index = sys.argv[1]
    tree = WindowTree(rows[index]['key'])
    for s in map(int, sys.argv[2:]):
        print(index, 's', s, 'N=11', direct_block(tree, 11, 3, s, cap=8))
