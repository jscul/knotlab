"""Bonds between a top chain and a lower orbit (CARRIER-20261117-001, the thread's own code, 2026-11-17).

8db5da810c00-73 reads 6 at s = 5 and 6 (depth 11 and 13), with no two-orbit bond and no orbit-and-block bond there. Its certified bonds
lie on one chain of orbits: two addresses of the top orbit A_0 (level 3), one of A_1 (level 4) and two of A_2 (level 5), where
A_0, A_1, A_2 are the ancestors of O_v, and one address of O_v at level 3 + s. So the head of the bond is the chain of O_v's ancestors
just below the top.

For an orbit O_u at level k and an orbit O_v at level k + s, the head of depth d is O_u with O_v's ancestor orbits at levels
k + 1 .. k + d (when O_v descends from O_u these are the chain from O_u to O_v). The projection of the allowed states onto the head
and O_v (and optionally O_v's children) is exact by the same message passing as the pair projection (window_tree.py): the descent from
level k to O_v records each ancestor's assignment for the first d steps. A bond in it holding a distinction of O_u and one of O_v is a
bond of the pattern meeting levels k and k + s, so its least size bounds L_N(k, s) from above (Theorem K's argument). With d = 0 and
children this is two_block.py's orbit-and-block bond, which is checked."""
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree, level_states  # noqa: E402

_cache = {}
DP_BITS = 18  # largest number of bits read by the top-down free flags (memory about 3^n / n booleans per level)


def free_flags(rows, n):
    """free[S] for every set S of the n bits (as a bitmask): the projection of rows onto S is all of {0,1}^S. Top down: the projection
    onto S is the projection onto S with its lowest missing bit added, with that bit's axis reduced by any (3^n steps in all)."""
    ind = np.zeros((2,) * n, dtype=bool)
    R = np.array(sorted(rows), dtype=np.int64)
    ind[tuple(((R >> j) & 1) for j in range(n))] = True
    full = (1 << n) - 1
    free = np.zeros(1 << n, dtype=bool)
    free[full] = ind.all()
    level = {full: ind}
    for m in range(n - 1, -1, -1):
        nxt = {}
        for T, arr in level.items():
            # S = T minus bit i has parent T exactly when every bit below i lies in T; that bit is then axis i of T's array
            i = 0
            while i < n and (T >> i) & 1:
                proj = arr.any(axis=i)
                S = T & ~(1 << i)
                nxt[S] = proj
                free[S] = proj.all()
                i += 1
        level = nxt
    return free


def least_bond_dp(rows, mu, nh, mv, nc, cap=None):
    n = nh + mv + nc
    free = free_flags(rows, n)
    top = n if cap is None else min(n, cap)
    vmask = ((1 << mv) - 1) << nh
    umask = (1 << mu) - 1
    for size in range(2, top + 1):
        for S in itertools.combinations(range(n), size):
            M = sum(1 << i for i in S)
            if not (M & umask) or not (M & vmask) or free[M]:
                continue
            if all(free[M & ~(1 << i)] for i in S):
                return size
    return None


def least_bond(rows, mu, nh, mv, nc, cap=None):
    """Least size of a set holding a distinction of O_u (bits < mu) and one of O_v (bits nh..nh+mv-1; bits mu..nh-1 are the rest of the
    head, bits after O_v its children), constrained in rows with every proper subset free; None if none of size at most cap. Up to 18
    bits by the top-down free flags; above, level by level over sets whose subsets one smaller are all free, with freeness read by
    counting distinct projections (vectorised)."""
    n = nh + mv + nc
    top = n if cap is None else min(n, cap)
    key = (rows, mu, nh, mv, nc)
    hit = _cache.get(key)
    if hit is not None and (hit[0] is not None or hit[1] >= top):
        return hit[0] if hit[0] is None or hit[0] <= top else None
    if not rows:
        _cache[key] = (None, n)
        return None
    if n <= DP_BITS:
        out = least_bond_dp(rows, mu, nh, mv, nc, cap)
        _cache[key] = (out, top)
        return out
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
            if len(R) >= full:
                codes = (bits[:, C] * weights).sum(axis=2)
                codes.sort(axis=0)
                distinct = 1 + (np.diff(codes, axis=0) != 0).sum(axis=0)
            else:
                distinct = np.zeros(len(C), dtype=np.int64)
            for S, dd in zip(cands[i:i + step], distinct):
                if dd == full:
                    free_now.add(S)
                elif S[0] < mu and any(nh <= j < nh + mv for j in S):
                    out = size
                    break
            if out is not None:
                break
        if out is not None:
            break
        free_prev = free_now
    _cache[key] = (out, top)
    return out


def rows_of(tree, state, Fv, Fchild, children):
    """state = (mu, nh, t2, J), J of (head code, x on O_v) not yet filtered by O_v's feasibility. Fv: O_v's feasible sets at its remaining
    depth; Fchild: those below the children (None at the bottom)."""
    mu, nh, t2, J = state
    mv = tree.m[t2]
    if not children or Fchild is None:
        return frozenset(h | (x << nh) for h, x in J if x in Fv[t2]), mu, nh, mv, 0
    by_x = {}
    for x, y in tree.W[t2]:
        if all(tree.restrict(y, pos) in Fchild[c] for c, pos in tree.children[t2]):
            by_x.setdefault(x, []).append(y)
    return frozenset(h | (x << nh) | (y << (nh + mv)) for h, x in J for y in by_x.get(x, ())), mu, nh, mv, 2 * mv


def best_capped(args_iter, cap=None):
    cur = None
    for args in args_iter:
        lim = cap if cur is None else (cur - 1 if cap is None else min(cap, cur - 1))
        if lim is not None and lim < 2:
            break
        v = least_bond(*args, cap=lim)
        if v is not None and (cur is None or v < cur):
            cur = v
    return cur


def level_k_states(tree, k, Fat, Fu, st):
    """States (mu, nh, t_B, J) at level k: O_u and B, the ancestor at level k of the deeper orbit (B = O_u when it descends from O_u),
    J of (a on O_u, x on B). Fat(lvl): feasible sets for sibling subtrees whose orbits sit at level lvl + 1. Fu: O_u's own subtree
    feasibility (applied to a)."""
    out = set()
    for t, up in st[k]:
        out.add((tree.m[t], tree.m[t], t, frozenset((x, x) for x in up if x in Fu[t])))
    for b in range(k):
        for t, up in st[b]:
            kids = tree.children[t]
            Fr = Fat(b)
            for c1, c2 in itertools.permutations(range(len(kids)), 2):
                J = set()
                for x, y in tree.W[t]:
                    if x in up and all(tree.restrict(y, pos) in Fr[c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2)):
                        J.add((tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])))
                cur = {(kids[c1][0], kids[c2][0], frozenset(J))}
                for lvl in range(b + 1, k):
                    Fr1 = Fat(lvl)
                    nxt = set()
                    for t1, t2, J in cur:
                        for ci in range(len(tree.children[t1])):
                            rel = tree.step(t1, Fr1, ci, frozenset((z2, z1) for z1, z2 in J))
                            J1 = frozenset((z1, z2) for z2, z1 in rel)
                            for cj in range(len(tree.children[t2])):
                                nxt.add((tree.children[t1][ci][0], tree.children[t2][cj][0], tree.step(t2, Fr1, cj, J1)))
                    cur = nxt
                for t1, t2, J in cur:
                    out.add((tree.m[t1], tree.m[t1], t2, frozenset((a, z) for a, z in J if a in Fu[t1])))
    return out


def advance(tree, S, Fr, record):
    """One step of the deeper orbit to each child; with record, the child's assignment joins the head."""
    nxt = set()
    for mu, nh, t2, J in S:
        for cj, (c, pos) in enumerate(tree.children[t2]):
            rel = tree.step(t2, Fr, cj, J)
            if record:
                nxt.add((mu, nh + tree.m[c], c, frozenset((h | (z << nh), z) for h, z in rel)))
            else:
                nxt.add((mu, nh, c, rel))
    return frozenset(nxt)


def direct_head(tree, N, k, s, d, children=False, cap=None):
    """Least head-and-orbit bond at depth N (s > d), from the depth-N feasible sets."""
    assert s > d
    F = tree.feasible(N)
    st = level_states(tree, N, F)
    S = frozenset(level_k_states(tree, k, lambda lvl: F[N - lvl - 1], F[N - k], st))
    for lvl in range(k, k + s):
        S = advance(tree, S, F[N - lvl - 1], record=lvl < k + d)
    r = N - k - s
    Fchild = F[r - 1] if r >= 1 else None
    return best_capped((rows_of(tree, x, F[r], Fchild, children) for x in S), cap=cap)


def every_depth_head(tree, k, d, children=False, Rmax=12, smax=400, cap=None):
    """For every s > d and every depth N >= k + s: tiers r = 0..R-1 and r >= R (R = r0, or r0 + 1 with children), each a sequence over
    s = d + 1, d + 2, ... (eventually periodic); small cases that the periodic states do not cover are computed at their depth."""
    F = tree.feasible(Rmax)
    r0 = next((r for r in range(Rmax) if F[r] == F[r + 1]), None)
    if r0 is None:
        return None
    Fc = F[r0]
    st = level_states(tree, k, [Fc] * (k + 2))
    S = frozenset(level_k_states(tree, k, lambda lvl: Fc, Fc, st))
    for _ in range(d):
        S = advance(tree, S, Fc, record=True)
    seen, seq = {}, []
    for j in range(smax + 1):
        if S in seen:
            start = seen[S]
            break
        seen[S] = j
        seq.append(S)
        S = advance(tree, S, Fc, record=False)
    else:
        raise RuntimeError('no repeat')
    period = len(seq) - start

    def S_at(j):
        return seq[j] if j < len(seq) else seq[start + (j - start) % period]

    R = r0 + 1 if children else r0
    out = {}
    horizon = start + period + R + 1
    for r in range(R + 1):
        Fv = F[min(r, r0)]
        Fchild = None if r == 0 else F[min(r - 1, r0)]
        P = []
        for s in range(d + 1, d + horizon + period + 1):
            j = s - d
            back = max(0, r0 - r)
            if j - back < 0 or (back and s + r - d < r0):
                P.append(direct_head(tree, k + s + r, k, s, d, children, cap))
                continue
            S = S_at(j - back)
            for i in range(back, 0, -1):
                S = advance(tree, S, F[r + i - 1], record=False)
            P.append(best_capped((rows_of(tree, x, Fv, Fchild, children) for x in S), cap=cap))
        out['r=%d' % r if r < R else 'r>=%d' % R] = P
    return dict(r0=r0, start=start, period=period, horizon=horizon, d=d, children=children, first_s=d + 1, sequences=out)


if __name__ == '__main__':
    import json
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    index, d = sys.argv[1], int(sys.argv[2])
    tree = WindowTree(third[index]['key'])
    for s in map(int, sys.argv[3:]):
        print(index, 'd', d, 's', s, 'N=11', direct_head(tree, 11, 3, s, d, cap=8), flush=True)
