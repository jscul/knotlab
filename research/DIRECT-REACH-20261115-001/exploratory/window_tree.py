"""The pattern of a description with bounded orbits is a tree of windows; exact relations at every depth by message passing.

DIRECT-REACH-20261115-001, exploratory, the thread's own code (check before relying on it).

Orbits of the placement's words partition each level, and the orbit of wa lies in O(w)·{0,1}; the child orbits of an orbit O
partition O·{0,1}. Every knot placed at an address of O lies in O's window (O with its children), and two windows share addresses
only when one orbit is a child orbit of the other's. So the windows form a tree (bags O ∪ O·{0,1}) and the depth-N pattern is a
tree-structured constraint system over it: the projection of its states onto any orbit, or any two orbits, is computed exactly by
passing feasible sets along the tree. With finitely many orbit types the computation is finite at every depth.

Exact objects, for depth N:
- F[r][t]: the assignments of an orbit of type t that extend to its subtree of r further levels (r = N - level).
- Up(O): the assignments of O allowed by everything outside O's subtree.
- J(O_u, O_v): the projection of the states onto two orbits, at levels k and k + s.
From J: the ties between the two orbits, and the bonds of size 3 inside O_u ∪ O_v.
"""
import itertools
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from window_types import Description, step_word  # noqa: E402


def canon_with_order(elems, root):
    order, seen = [root], {root: 0}
    for i in order:
        for tgt, _ in elems[i]:
            if tgt not in seen:
                seen[tgt] = len(order)
                order.append(tgt)
    return tuple(tuple((seen[t], sec) for t, sec in elems[i]) for i in order), order


class WindowTree:
    def __init__(self, key, max_types=2000, max_orbit=4):
        self.D = D = Description(key)
        root, _ = canon_with_order([[(0, m) for m in D.maps]], 0)
        self.types, self.index = [], {}
        self.children = []         # per type: list of (child type, positions 2j+b in the child's canonical order)
        dq = deque([root])
        self._add(root)
        while dq:
            T = dq.popleft()
            m = len(T)
            if m > max_orbit:
                raise ValueError('orbit larger than %d' % max_orbit)
            assigned, kids = {}, []
            for j in range(m):
                for b in (0, 1):
                    if (j, b) in assigned:
                        continue
                    idx, elems, q = {(j, b): 0}, [], deque([(j, b)])
                    while q:
                        i, bb = q.popleft()
                        row = []
                        for k in range(len(D.maps)):
                            tgt, sec = T[i][k]
                            out, nsec = step_word(D.aut, sec, bb)
                            node = (tgt, out)
                            if node not in idx:
                                idx[node] = len(idx)
                                q.append(node)
                            row.append((idx[node], nsec))
                        elems.append(row)
                    nodes = list(idx)
                    C, order = canon_with_order(elems, 0)
                    pos = [2 * nodes[o][0] + nodes[o][1] for o in order]
                    for o in order:
                        assigned[nodes[o]] = True
                    if C not in self.index:
                        if len(self.types) >= max_types:
                            raise ValueError('too many types')
                        self._add(C)
                        dq.append(C)
                    kids.append((self.index[C], pos))
            self.children.append(kids)
        self._windows()

    def _add(self, T):
        self.index[T] = len(self.types)
        self.types.append(T)

    def _windows(self):
        self.W, self.Wl, self.m = [], [], []
        for T in self.types:
            m = len(T)
            nv, knots = self.D.window(T)
            X = ((np.arange(1 << nv, dtype=np.int64)[:, None] >> np.arange(nv)) & 1).astype(np.int8)
            ok = np.ones(len(X), dtype=bool)
            okl = np.ones(1 << m, dtype=bool)
            Xl = X[: 1 << m, :m]
            for a, b, c in knots:
                s = X[:, a] + X[:, b] + X[:, c]
                ok &= (s != 0) & (s != 3)
                if c < m:
                    sl = Xl[:, a] + Xl[:, b] + Xl[:, c]
                    okl &= (sl != 0) & (sl != 3)
            rows = np.nonzero(ok)[0]
            self.W.append([(int(r) & ((1 << m) - 1), int(r) >> m) for r in rows])
            self.Wl.append(frozenset(int(x) for x in np.nonzero(okl)[0]))
            self.m.append(m)

    @staticmethod
    def restrict(y, pos):
        z = 0
        for i, p in enumerate(pos):
            z |= ((y >> p) & 1) << i
        return z

    def feasible(self, R):
        """F[r][t] for r = 0..R."""
        F = [list(self.Wl)]
        for r in range(R):
            prev = F[-1]
            cur = []
            for t in range(len(self.types)):
                xs = set()
                for x, y in self.W[t]:
                    if x in xs:
                        continue
                    if all(self.restrict(y, pos) in prev[c] for c, pos in self.children[t]):
                        xs.add(x)
                cur.append(frozenset(xs))
            F.append(cur)
        return F

    def step(self, t, Fr, ci, xs_rel):
        """xs_rel: set of (a, x) with x an assignment of an orbit of type t; returns {(a, z)}: z on child orbit ci, with every other
        child orbit's subtree feasible at remaining depth Fr (a list over types) and the window satisfied."""
        out = set()
        kids = self.children[t]
        by_x = {}
        for x, y in self.W[t]:
            if all(self.restrict(y, pos) in Fr[c] for k, (c, pos) in enumerate(kids) if k != ci):
                by_x.setdefault(x, set()).add(self.restrict(y, kids[ci][1]))
        for a, x in xs_rel:
            for z in by_x.get(x, ()):
                out.add((a, z))
        return frozenset(out)


def level_states(tree, N, F):
    """Single orbits by level: dict level -> set of (type, Up) with Up a frozenset of assignments."""
    states = {0: {(0, frozenset(range(1 << tree.m[0])))}}
    for n in range(N):
        nxt = set()
        Fr = F[N - n - 1]
        for t, up in states[n]:
            for ci, (c, pos) in enumerate(tree.children[t]):
                rel = tree.step(t, Fr, ci, frozenset((0, x) for x in up))
                nxt.add((c, frozenset(z for _, z in rel)))
        states[n + 1] = nxt
    return states


def pair_joints(tree, N, k, s, F, states):
    """All distinct exact joints J (frozenset of (x_u, x_v)) of an orbit at level k and one at level k + s, with their types."""
    results = set()
    # case (i): O_v in the subtree of O_u
    for t, up in states[k]:
        cur = {(t, frozenset((x, x) for x in up))}
        for lvl in range(k, k + s):
            Fr = F[N - lvl - 1]
            nxt = set()
            for t2, J in cur:
                for ci, (c, pos) in enumerate(tree.children[t2]):
                    nxt.add((c, tree.step(t2, Fr, ci, J)))
            cur = nxt
        Fv = F[N - k - s]
        for t2, J in cur:
            results.add((t, t2, frozenset((a, z) for a, z in J if z in Fv[t2])))
    # case (ii): the paths split below an orbit B at level b < k
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
                # descend path 1 to level k (first coordinate), path 2 to level k + s (second coordinate)
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
                Fu, Fv = F[N - k], F[N - k - s]
                for t1, t2, J in cur:
                    results.add((t1, t2, frozenset((a, z) for a, z in J if a in Fu[t1] and z in Fv[t2])))
    return results


def ties_between(J, mu, mv):
    out = []
    if not J:
        return None
    for i in range(mu):
        for j in range(mv):
            vals = {((a >> i) ^ (z >> j)) & 1 for a, z in J}
            if len(vals) == 1:
                out.append((i, j, vals.pop()))
    return out


def three_bonds(J, mu, mv):
    """Triples inside O_u ∪ O_v holding one address of each orbit: non-shattered with every pair shattered."""
    if not J:
        return None
    nb = mu + mv
    rows = [[(a >> i) & 1 for i in range(mu)] + [(z >> j) & 1 for j in range(mv)] for a, z in J]
    A = np.array(rows, dtype=np.int8)
    tied = set()
    for p, q in itertools.combinations(range(nb), 2):
        if len(set(A[:, p] ^ A[:, q])) == 1:
            tied.add((p, q))
    out = []
    for tri in itertools.combinations(range(nb), 3):
        if not (min(tri) < mu <= max(tri)):
            continue
        if any(pq in tied for pq in itertools.combinations(tri, 2)):
            continue
        pats = {tuple(r) for r in A[:, list(tri)]}
        if len(pats) < 8:
            out.append(tri)
    return out


def every_depth_pairs(tree, k, Rmax=12, smax=400):
    """Every depth N >= k + s and every s >= 1. The feasible sets F[r] become constant from some r0 (checked); for remaining depth
    at least r0 nothing depends on N, and the pair states after s further steps of the deeper path form a sequence S_s on a finite
    set, eventually periodic. For N = k + s + r with r < r0 the last r0 - r steps use the early F[r] and are applied to S_{s-r0+r}.
    Returns for each r in 0..r0 (r0 standing for every r >= r0) the property sequence (tie, three-member bond inside the two orbits)
    over s >= 1 as prefix and cycle."""
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
        tie = b3 = False
        for t1, t2, J in S:
            Jf = frozenset((a, z) for a, z in J if z in Ff[t2])
            if ties_between(Jf, tree.m[t1], tree.m[t2]):
                tie = True
            if three_bonds(Jf, tree.m[t1], tree.m[t2]):
                b3 = True
        return int(tie), int(b3)

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
                P.append((int(any(ties_between(J, tree.m[a], tree.m[b]) for a, b, J in Js)),
                          int(any(three_bonds(J, tree.m[a], tree.m[b]) for a, b, J in Js))))
                continue
            S = S_at(s - back)
            for j in range(back, 0, -1):
                S = advance(S, F[r + j - 1])
            P.append(props(S, F[r]))
        out['r=%d' % r if r < r0 else 'r>=%d' % r0] = P
    return dict(r0=r0, start=start, period=period, horizon=horizon, alive_every_depth=all(bool(F[n][0]) for n in range(r0 + 1)),
                sequences=out)
