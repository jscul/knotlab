"""Theorem K's computation (KEEP-REACH-20261117-001, the thread's own code, 2026-11-17): the least bond of ANY size inside two orbits,
one at level k and one at level k + s, that meets both, at every depth N >= k + s and every s >= 1.

`every_depth_cross` is `window_tree.every_depth_pairs` (DIRECT-REACH-20261115-001, checked against SAT and refereed) with one change:
the property read from each pair state is the least size of a subset of the two orbits that meets both and is a bond in their exact
joint (constrained, every proper subset free), instead of the two flags (tie, three-member bond). The joint of two orbits is the exact
projection of the whole pattern onto them (Theorem W), so a bond in the joint is a bond of the pattern, and its value bounds L_N(k, s)
from above. The sequences over s are eventually periodic, as in every_depth_pairs; every remaining depth r < r0 is read separately."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import level_states, pair_joints  # noqa: E402


def least_cross_bond(J, mu, mv):
    """Least size of a subset of O_u ∪ O_v meeting both orbits that is constrained in J with every proper subset free; None if none."""
    if not J:
        return None
    n = mu + mv
    rows = [tuple(((a >> i) & 1) for i in range(mu)) + tuple(((z >> j) & 1) for j in range(mv)) for a, z in J]
    cache = {}

    def free(S):
        if S not in cache:
            cache[S] = len({tuple(r[i] for i in S) for r in rows}) == 1 << len(S)
        return cache[S]
    for size in range(2, n + 1):
        for S in itertools.combinations(range(n), size):
            if min(S) < mu <= max(S) and not free(S) and all(free(T) for T in itertools.combinations(S, size - 1)):
                return size
    return None


def best(values):
    vals = [v for v in values if v is not None]
    return min(vals) if vals else None


def every_depth_cross(tree, k, Rmax=12, smax=400):
    """Every depth N >= k + s and every s >= 1. The feasible sets F[r] become constant from some r0 (checked); for remaining depth
    at least r0 nothing depends on N, and the pair states after s further steps of the deeper path form a sequence S_s on a finite
    set, eventually periodic. For N = k + s + r with r < r0 the last r0 - r steps use the early F[r] and are applied to S_{s-r0+r}.
    Returns for each r in 0..r0 (r0 standing for every r >= r0) the sequence over s >= 1 (prefix and cycle) of the least bond inside
    two orbits meeting both (None where there is none)."""
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

    def props(S, Ff):
        return best(least_cross_bond(frozenset((a, z) for a, z in J if z in Ff[t2]), tree.m[t1], tree.m[t2]) for t1, t2, J in S)

    out = {}
    horizon = start + period + r0 + 1
    for r in range(r0 + 1):
        P = []
        for s in range(1, horizon + period + 1):
            if r == r0:
                P.append(props(S_at(s), Fc))
                continue
            back = r0 - r
            if s - back < 1:
                N = k + s + r
                Fn = tree.feasible(N)
                stn = level_states(tree, N, Fn)
                Js = pair_joints(tree, N, k, s, Fn, stn)
                P.append(best(least_cross_bond(J, tree.m[a], tree.m[b]) for a, b, J in Js))
                continue
            S = S_at(s - back)
            for j in range(back, 0, -1):
                S = advance(S, F[r + j - 1])
            P.append(props(S, F[r]))
        out['r=%d' % r if r < r0 else 'r>=%d' % r0] = P
    return dict(r0=r0, start=start, period=period, horizon=horizon, alive_every_depth=all(bool(F[n][0]) for n in range(r0 + 1)),
                sequences=out)
