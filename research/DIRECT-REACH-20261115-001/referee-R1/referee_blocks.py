"""Referee R1, item (a), block side: my own orbit-type dynamic programming (written from the proof's statement of Theorem W,
not from window_tree.py).

Type of an orbit: its elements in a canonical order (breadth-first from a root element, maps in order) and, for each element and
each used word ("map"), the index of the image and the map's section there (a word of states). Children of an orbit: the 2m
addresses (i, b); map j sends (i, b) to (target_j(i), output of section_j(i) on b), with the section of section_j(i) at b. A child
orbit is the forward closure under the maps (maps are bijections of a finite level).

Exact per-depth computation (no periodicity assumed), for P_N:
  F[r][t]  assignments of a type-t orbit that extend to its r levels below (r = N - level);
  Up(O)    assignments of O allowed by everything outside O's subtree;
  J(Ou,Ov) joint of an orbit at level k and one at level k + s, by the tree path (O_v below O_u, or a split at a common
           ancestor orbit B at level b < k).
Every-depth computation: my own statement of the periodicity, used only as a prediction to compare with the exact per-depth DP
and with the study's stored sequences.
Assignments are ints, bit i = element i; for a block, x (orbit, m bits) and y (children, bit 2i + b = child (i, b)).
"""
import itertools
from collections import deque

import numpy as np

from referee_pattern import word_list


class Blocks:
    def __init__(self, key, max_orbit=4, max_types=5000):
        s, sw, d0, d1, placements = key
        self.sw, self.d = list(sw), [list(d0), list(d1)]
        W = word_list(s)
        self.placements = sorted({tuple(sorted(int(t) for t in p)) for p in placements})
        self.used = sorted({t // 3 for p in self.placements for t in p})
        self.maps = [W[i] for i in self.used]
        self.mapidx = {wi: j for j, wi in enumerate(self.used)}
        self.K = len(self.maps)
        self.types, self.tid = [], {}
        self.kids = []           # per type: list of (child type, [block child-bit position for each child element])
        root = self._canon([[(0, tuple(w)) for w in self.maps]])
        self._intern(root)
        q = deque([root])
        while q:
            T = q.popleft()
            if len(T) > max_orbit:
                raise ValueError('orbit larger than %d' % max_orbit)
            kl = []
            for C, pos in self._children(T):
                if C not in self.tid:
                    if len(self.types) >= max_types:
                        raise ValueError('too many types')
                    self._intern(C)
                    q.append(C)
                kl.append((self.tid[C], pos))
            self.kids.append(kl)
        self._blocks()

    # -- sections ------------------------------------------------------------------------------------------------------
    def read(self, word, b):
        """The word reads letter b: the rightmost state first. Returns (output letter, section word)."""
        c, new = b, list(word)
        for i in range(len(word) - 1, -1, -1):
            q = word[i]
            new[i] = self.d[c][q]
            c ^= self.sw[q]
        return c, tuple(new)

    # -- types ---------------------------------------------------------------------------------------------------------
    def _intern(self, T):
        self.tid[T] = len(self.types)
        self.types.append(T)

    @staticmethod
    def _canon(rows, root=0):
        """rows[i][j] = (target, section). Relabel breadth-first from root, maps in order."""
        order, idx = [root], {root: 0}
        h = 0
        while h < len(order):
            i = order[h]
            h += 1
            for tgt, _ in rows[i]:
                if tgt not in idx:
                    idx[tgt] = len(order)
                    order.append(tgt)
        assert len(order) == len(rows)
        return tuple(tuple((idx[t], sec) for t, sec in rows[i]) for i in order)

    def _children(self, T):
        """Child orbits of a type-T orbit, each as (canonical type, block child positions in canonical element order)."""
        m = len(T)
        node_rows = {}
        for i in range(m):
            for b in (0, 1):
                row = []
                for j in range(self.K):
                    tgt, sec = T[i][j]
                    out, nsec = self.read(sec, b)
                    row.append(((tgt, out), nsec))
                node_rows[(i, b)] = row
        done, out = set(), []
        for start in sorted(node_rows):
            if start in done:
                continue
            comp, q = [start], deque([start])
            seen = {start}
            while q:
                u = q.popleft()
                for v, _ in node_rows[u]:
                    if v not in seen:
                        seen.add(v)
                        comp.append(v)
                        q.append(v)
            done |= seen
            loc = {u: n for n, u in enumerate(comp)}
            rows = [[(loc[v], sec) for v, sec in node_rows[u]] for u in comp]
            # canonical order from comp[0]
            order, idx, h = [0], {0: 0}, 0
            while h < len(order):
                i = order[h]
                h += 1
                for tgt, _ in rows[i]:
                    if tgt not in idx:
                        idx[tgt] = len(order)
                        order.append(tgt)
            C = tuple(tuple((idx[t], sec) for t, sec in rows[i]) for i in order)
            pos = [2 * comp[i][0] + comp[i][1] for i in order]
            out.append((C, pos))
        return out

    def block_knots(self, T):
        """Knots of a type-T orbit's block on variables 0..m-1 (orbit) and m + 2i + b (child (i, b)); members distinct."""
        m = len(T)
        ks = set()
        for i in range(m):
            for p in self.placements:
                mem = []
                for t in p:
                    wi, e = divmod(t, 3)
                    tgt = T[i][self.mapidx[wi]][0]
                    mem.append(tgt if e == 0 else m + 2 * tgt + e - 1)
                if len(set(mem)) == 3:
                    ks.add(tuple(sorted(mem)))
        return sorted(ks)

    def _blocks(self):
        self.m = [len(T) for T in self.types]
        self.sols, self.F0 = [], []
        for t, T in enumerate(self.types):
            m = self.m[t]
            ks = self.block_knots(T)
            nv = 3 * m
            A = (np.arange(1 << nv)[:, None] >> np.arange(nv)) & 1
            ok = np.ones(1 << nv, dtype=bool)
            ok0 = np.ones(1 << nv, dtype=bool)
            for a, b, c in ks:
                ssum = A[:, a] + A[:, b] + A[:, c]
                good = (ssum > 0) & (ssum < 3)
                ok &= good
                if c < m:
                    ok0 &= good
            sols = [(int(z) & ((1 << m) - 1), int(z) >> m) for z in np.nonzero(ok)[0]]
            self.sols.append(sols)
            self.F0.append(frozenset(int(z) for z in np.nonzero(ok0)[0] if int(z) < (1 << m)))

    @staticmethod
    def proj(y, pos):
        z = 0
        for i, p in enumerate(pos):
            z |= ((y >> p) & 1) << i
        return z

    # -- feasibility -----------------------------------------------------------------------------------------------------
    def feas(self, R):
        F = [list(self.F0)]
        for _ in range(R):
            prev = F[-1]
            cur = []
            for t in range(len(self.types)):
                good = set()
                for x, y in self.sols[t]:
                    if x not in good and all(self.proj(y, pos) in prev[c] for c, pos in self.kids[t]):
                        good.add(x)
                cur.append(frozenset(good))
            F.append(cur)
        return F

    def r0(self, Rmax=60):
        F = self.feas(Rmax)
        for r in range(Rmax):
            if F[r] == F[r + 1]:
                return r, F
        return None, F

    # -- messages --------------------------------------------------------------------------------------------------------
    def down(self, t, ci, Fside, rel):
        """rel: set of (a, x), x on a type-t orbit. Returns {(a, z)}: z on child ci, the block of t and every other child
        subtree (feasible in Fside) satisfied."""
        kl = self.kids[t]
        table = {}
        for x, y in self.sols[t]:
            ok = True
            for cj, (c, pos) in enumerate(kl):
                if cj != ci and self.proj(y, pos) not in Fside[c]:
                    ok = False
                    break
            if ok:
                table.setdefault(x, set()).add(self.proj(y, kl[ci][1]))
        out = set()
        for a, x in rel:
            for z in table.get(x, ()):
                out.add((a, z))
        return frozenset(out)

    def split(self, t, c1, c2, Fside, up):
        """Joint of two distinct child orbits c1, c2 of a type-t orbit whose assignments are restricted to up."""
        kl = self.kids[t]
        out = set()
        for x, y in self.sols[t]:
            if x not in up:
                continue
            if all(self.proj(y, pos) in Fside[c] for cj, (c, pos) in enumerate(kl) if cj not in (c1, c2)):
                out.add((self.proj(y, kl[c1][1]), self.proj(y, kl[c2][1])))
        return frozenset(out)

    def ups(self, N, F, upto):
        """Level n -> set of (type, Up) for n = 0..upto, in P_N."""
        L = {0: {(0, frozenset(range(1 << self.m[0])))}}
        for n in range(upto):
            nxt = set()
            for t, up in L[n]:
                for ci, (c, _) in enumerate(self.kids[t]):
                    rel = self.down(t, ci, F[N - n - 1], frozenset((0, x) for x in up))
                    nxt.add((c, frozenset(z for _, z in rel)))
            L[n + 1] = nxt
        return L

    def level_k_pairs(self, N, F, k, U):
        """The set of (tu, tv, J) for an orbit at level k (first) and an orbit at level k (second): the diagonal (same orbit)
        and the pairs split at a common ancestor; the first coordinate filtered by F[N - k]. U = ups(N, F, k)."""
        out = set()
        for t, up in U[k]:
            out.add((t, t, frozenset((x, x) for x in up if x in F[N - k][t])))
        for b in range(k):
            for t, up in U[b]:
                kl = self.kids[t]
                for c1, c2 in itertools.permutations(range(len(kl)), 2):
                    cur = {(kl[c1][0], kl[c2][0], self.split(t, c1, c2, F[N - b - 1], up))}
                    for lvl in range(b + 1, k):
                        Fs = F[N - lvl - 1]
                        nxt = set()
                        for t1, t2, J in cur:
                            for i1 in range(len(self.kids[t1])):
                                sw = frozenset((z2, z1) for z1, z2 in J)
                                J1 = frozenset((z1, z2) for z2, z1 in self.down(t1, i1, Fs, sw))
                                for i2 in range(len(self.kids[t2])):
                                    nxt.add((self.kids[t1][i1][0], self.kids[t2][i2][0], self.down(t2, i2, Fs, J1)))
                        cur = nxt
                    for t1, t2, J in cur:
                        out.add((t1, t2, frozenset((a, z) for a, z in J if a in F[N - k][t1])))
        return frozenset(out)

    def advance(self, S, Fs):
        """Move the second orbit one level down (every child)."""
        nxt = set()
        for t1, t2, J in S:
            for i2 in range(len(self.kids[t2])):
                nxt.add((t1, self.kids[t2][i2][0], self.down(t2, i2, Fs, J)))
        return frozenset(nxt)

    # -- properties of a joint -------------------------------------------------------------------------------------------
    def flags(self, S, Fv):
        """(tie, b3) over the joints in S, the second coordinate filtered by Fv."""
        tie = b3 = False
        for t1, t2, J in S:
            Jf = [(a, z) for a, z in J if z in Fv[t2]]
            assert Jf, 'empty joint'
            mu, mv = self.m[t1], self.m[t2]
            bits = np.array([[(a >> i) & 1 for i in range(mu)] + [(z >> j) & 1 for j in range(mv)] for a, z in Jf], dtype=np.int8)
            nb = mu + mv
            tiedp = set()
            for p, q in itertools.combinations(range(nb), 2):
                x = bits[:, p] ^ bits[:, q]
                if x.min() == x.max():
                    tiedp.add((p, q))
                    if p < mu <= q:
                        tie = True
            if not b3:
                for tri in itertools.combinations(range(nb), 3):
                    if not (tri[0] < mu <= tri[2]):
                        continue
                    if any(pq in tiedp for pq in itertools.combinations(tri, 2)):
                        continue
                    pats = {tuple(r) for r in bits[:, list(tri)].tolist()}
                    if len(pats) < 8:
                        b3 = True
                        break
            if tie and b3:
                break
        return int(tie), int(b3)

    # -- exact per depth -------------------------------------------------------------------------------------------------
    def exact_cells(self, N, k, F=None):
        """(tie, b3) for s = 1..N-k at depth N, exactly (F recomputed to depth N; no periodicity)."""
        if F is None:
            F = self.feas(N)
        U = self.ups(N, F, k)
        S = self.level_k_pairs(N, F, k, U)
        out = {}
        for s in range(1, N - k + 1):
            S = self.advance(S, F[N - (k + s - 1) - 1])
            out[s] = self.flags(S, F[N - k - s])
        return out

    # -- every depth (my own periodicity statement) ----------------------------------------------------------------------
    def every_depth(self, k, smax):
        """Predict (tie, b3) for every s <= smax and every remaining depth r = N - k - s, as {r: [flags for s = 1..smax]} for
        r = 0..r0 (r0 standing for every r >= r0), plus the period of the stable sequence."""
        r0, F = self.r0()
        Fc = F[r0]
        Nbig = k + r0 + 2                        # any depth with N - k >= r0 + 1 gives the stable level-k states
        Fstab = [F[min(i, r0)] for i in range(Nbig + 1)]
        U = self.ups(Nbig, Fstab, k)
        S0 = self.level_k_pairs(Nbig, Fstab, k, U)
        seq, seen = [S0], {S0: 0}
        while True:
            nxt = self.advance(seq[-1], Fc)
            if nxt in seen:
                start, period = seen[nxt], len(seq) - seen[nxt]
                break
            seen[nxt] = len(seq)
            seq.append(nxt)

        def Sig(s):
            return seq[s] if s < len(seq) else seq[start + (s - start) % period]
        pred = {}
        for r in range(r0 + 1):
            P = []
            for s in range(1, smax + 1):
                if r >= r0:
                    P.append(self.flags(Sig(s), Fc))
                    continue
                back = r0 - r                   # steps whose remaining depth is below r0
                if s < back:                    # N - k = s + r < r0: compute directly
                    P.append(self.exact_cells(k + s + r, k)[s])
                    continue
                S = Sig(s - back)
                for lvl_from_bottom in range(back, 0, -1):
                    S = self.advance(S, F[r + lvl_from_bottom - 1])
                P.append(self.flags(S, F[r]))
            pred[r] = P
        alive = all(len(F[n][0]) > 0 for n in range(r0 + 1))
        return dict(r0=r0, start=start, period=period, alive_every_depth=alive, pred=pred)
