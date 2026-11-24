"""Structures of PARENTS-FROM-HOLDERS-20261124-001A-E001, in one form for the reference rounds and the serial states.

A structure here is read-only: knots 0..n-1 (local numbers), each with its places (distinction numbers), the holders of
every distinction (one or two knots), the barred bit of every loose distinction, and the record of parents.  The record is
used only to give each chosen place its kind (deviations.md, item 9) and for reports; nothing in pfh_look.py reads it.

Two constructors:
  Struct.from_engine(S)         a structure of the reference engine (RING-IN-BALANCE-20261123-001A), knots kept
  Struct.induced(ref, I, Bar)   the serial state (I, Bar) of the one-birth-at-a-time study (deviations.md, item 4)
"""
from __future__ import annotations

from collections import deque


def bits(m):
    out = []
    while m:
        low = m & -m
        out.append(low.bit_length() - 1)
        m ^= low
    return out


class Struct:
    __slots__ = ('n', 'places', 'holders', 'barred', 'parents', 'is_start', 'made', 'ref_id', 'label',
                 'sh', 'nU', 'nB', 'Ul', 'Bl', 'items', 'item_index', 'kinds', '_dist_start', '_dist_member',
                 'strict')

    def __init__(self, places, holders, barred, parents, is_start, made=None, ref_id=None, label=None, strict=True):
        self.n = len(places)
        self.places = places          # knot -> list of distinction ids
        self.holders = holders        # dict or list: distinction -> list of 1 or 2 knots (local)
        self.barred = barred          # dict or list: distinction -> bool (meaningful when loose)
        self.parents = parents        # knot -> tuple of parent knots (local)
        self.is_start = is_start      # knot -> bool
        self.made = made              # knot -> round of birth (reference rounds), or None
        self.ref_id = ref_id          # knot -> reference knot number (serial states), or None
        self.label = label
        self.strict = strict      # False only for the hand-made structures of check (a): a place may then have no kind
        self._prepare()

    # ------------------------------------------------------------------ constructors
    @classmethod
    def from_engine(cls, S, label=None):
        n = S.n_knots
        places = [list(P) for P in S.places]
        holders = [list(h) for h in S.holders]
        barred = list(S.barred)
        parents = [tuple(p) for p in S.parents]
        is_start = [len(parents[x]) == 0 for x in range(n)]
        made = list(S.made)
        return cls(places, holders, barred, parents, is_start, made=made, label=label)

    @classmethod
    def induced(cls, refS, I, Bar, n_start, extra=None, label=None):
        """The sub-structure of the reference structure refS on the knots of the bit set I, with the knots of Bar
        barred.  extra = (parent reference knots, fresh count): one more knot, made as deviations.md item 5 says."""
        ids = bits(I)
        loc = {r: i for i, r in enumerate(ids)}
        places = []
        holders = {}
        barred = {}
        for r in ids:
            P = []
            for e in refS.places[r]:
                hs = [loc[h] for h in refS.holders[e] if h in loc]
                P.append(e)
                if e not in holders:
                    holders[e] = hs
            places.append(P)
        for e, hs in holders.items():
            if len(hs) == 1:
                barred[e] = bool((Bar >> ids[hs[0]]) & 1)
            else:
                barred[e] = False
        parents = [tuple(loc[p] for p in refS.parents[r]) for r in ids]
        is_start = [r < n_start for r in ids]
        made = [refS.made[r] for r in ids]
        ref_id = list(ids)
        if extra is not None:
            B, f = extra
            x = len(places)
            P = []
            nxt = max(len(refS.holders), 1 + max(holders)) if holders else len(refS.holders)
            for b in B:
                lb = loc[b]
                cand = sorted(e for e in places[lb] if len(holders[e]) == 1 and not barred[e])
                if not cand:
                    raise AssertionError('extra knot: parent %d has no usable loose distinction' % b)
                e = cand[0]
                holders[e] = holders[e] + [x]
                P.append(e)
            for _ in range(f):
                e = nxt
                nxt += 1
                holders[e] = [x]
                barred[e] = False
                P.append(e)
            places.append(P)
            parents.append(tuple(loc[b] for b in B))
            is_start.append(False)
            made.append(None)
            ref_id.append(None)
        return cls(places, holders, barred, parents, is_start, made=made, ref_id=ref_id, label=label)

    # ------------------------------------------------------------------ derived tables
    def _prepare(self):
        n = self.n
        H = self.holders
        Bd = self.barred
        sh = [None] * n
        nU = [0] * n
        nB = [0] * n
        Ul = [None] * n
        Bl = [None] * n
        items = []
        kinds = []
        for x in range(n):
            L = []
            u = []
            b = []
            for e in self.places[x]:
                hs = H[e]
                if len(hs) == 2:
                    y = hs[0] if hs[1] == x else hs[1]
                    if y == x:
                        raise AssertionError('a distinction held twice by one knot')
                    L.append((e, y))
                elif len(hs) == 1:
                    if Bd[e]:
                        b.append(e)
                    else:
                        u.append(e)
                else:
                    raise AssertionError('distinction %r has %d holders' % (e, len(hs)))
            L.sort()
            u.sort()
            b.sort()
            sh[x] = L
            nU[x] = len(u)
            nB[x] = len(b)
            Ul[x] = u
            Bl[x] = b
        par = [set(p) for p in self.parents]
        for x in range(n):
            for e, y in sh[x]:
                if y in par[x]:
                    k = 'P'
                elif x in par[y]:
                    k = 'C'
                elif self.is_start[x] and self.is_start[y]:
                    k = 'S'
                elif not self.strict:
                    k = 'X'
                else:
                    raise AssertionError('shared place (%d, %r) of no kind' % (x, e))
                items.append((x, e))
                kinds.append(k)
        self.sh = sh
        self.nU = nU
        self.nB = nB
        self.Ul = Ul
        self.Bl = Bl
        self.items = items
        self.item_index = {it: i for i, it in enumerate(items)}
        self.kinds = kinds
        self._dist_start = None
        self._dist_member = None

    def other(self, x, e):
        hs = self.holders[e]
        return hs[0] if hs[1] == x else hs[1]

    def n_places(self, x):
        return len(self.places[x])

    def members(self):
        return [x for x in range(self.n) if self.nU[x] > 0]

    def multi_bfs(self, sources):
        dist = [-1] * self.n
        q = deque()
        for s in sources:
            if dist[s] < 0:
                dist[s] = 0
                q.append(s)
        sh = self.sh
        while q:
            u = q.popleft()
            du = dist[u] + 1
            for _, w in sh[u]:
                if dist[w] < 0:
                    dist[w] = du
                    q.append(w)
        return dist

    def dist_start(self):
        if self._dist_start is None:
            self._dist_start = self.multi_bfs([x for x in range(self.n) if self.is_start[x]])
        return self._dist_start

    def dist_member(self):
        if self._dist_member is None:
            self._dist_member = self.multi_bfs(self.members())
        return self._dist_member

    def dist_from(self, x, dmax=None):
        dist = {x: 0}
        q = deque([x])
        sh = self.sh
        while q:
            u = q.popleft()
            du = dist[u]
            if dmax is not None and du >= dmax:
                continue
            for _, w in sh[u]:
                if w not in dist:
                    dist[w] = du + 1
                    q.append(w)
        return dist

    def knot_signature(self, x):
        """What changes when a knot's places change: its places with their marks."""
        out = []
        for e in self.places[x]:
            hs = self.holders[e]
            if len(hs) == 2:
                out.append((e, 'S', hs[0] if hs[1] == x else hs[1]))
            else:
                out.append((e, 'B' if self.barred[e] else 'U'))
        return tuple(sorted(out, key=repr))


def changed_between(A, B, a_to_b):
    """Knots of B that are new or whose places changed, with a_to_b mapping A's knots to B's knots (same reference
    knots).  Used for identity certificates (deviations.md, item 18)."""
    inA = set(a_to_b.values())
    ch = set(y for y in range(B.n) if y not in inA)
    for xa, xb in a_to_b.items():
        if _sig_ref(A, xa, a_to_b) != _sig_ref_b(B, xb):
            ch.add(xb)
    return ch


def _sig_ref(A, x, a_to_b):
    out = []
    for e in A.places[x]:
        hs = A.holders[e]
        if len(hs) == 2:
            y = hs[0] if hs[1] == x else hs[1]
            out.append((e, 'S', a_to_b[y]))
        else:
            out.append((e, 'B' if A.barred[e] else 'U'))
    return tuple(sorted(out, key=repr))


def _sig_ref_b(B, x):
    out = []
    for e in B.places[x]:
        hs = B.holders[e]
        if len(hs) == 2:
            y = hs[0] if hs[1] == x else hs[1]
            out.append((e, 'S', y))
        else:
            out.append((e, 'B' if B.barred[e] else 'U'))
    return tuple(sorted(out, key=repr))
