"""Renamings of whole structures, used only to put places in one class (deviations.md, items 17 and 20).

Copied from PARENTS-FROM-HOLDERS-20261124-001A-E001 (commit 307b3bbe63) and extended for LEAST-RECORD-20261124-001A-E001:
whole graphs are coloured by stamps too, and every map is checked to keep every knot's stamp.

  whole_graph(T, root)          compressed form of a whole structure (optionally with a chosen place marked)
  record_generators(T, T0)      automorphisms of a reference structure built from the record: the start's
                                automorphisms and exchanges of siblings, each extended round by round, each checked
  structure_map(TA, TB, vmap)   a map of knots (vertex map of whole graphs) completed to distinctions and checked
  places_map(TA, TB, km, dm)    the induced map of chosen places

Every map returned here has been checked place by place on the whole structures; a candidate that fails the check is
counted and dropped.
"""
from __future__ import annotations

from collections import defaultdict

import pfh_iso as ISO
from pfh_iso import Graph


def whole_graph(T, variant='full', root=None):
    """Vertices = knots of T (local numbers); colour (is root, marks); edge label (number of shared distinctions, whether
    the chosen distinction is among them).  root = (x, a) or None."""
    n = T.n
    colour = [None] * n
    adj = [None] * n
    rx, ra = root if root is not None else (None, None)
    for y in range(n):
        U, B = T.nU[y], T.nB[y]
        if variant == 'full':
            c = (U, B, 0)
        elif variant == 'c1':
            c = (U + B, 0)
        else:
            c = (1 if U + B else 0, T.n_places(y))
        colour[y] = (1 if y == rx else 0,) + c + (T.stamp[y],)
        cnt = {}
        for e, z in T.sh[y]:
            k = cnt.get(z)
            if k is None:
                cnt[z] = [1, 1 if e == ra else 0]
            else:
                k[0] += 1
                if e == ra:
                    k[1] = 1
        adj[y] = sorted((z, (k[0], k[1])) for z, k in cnt.items())
    return Graph(n, colour, adj)


def structure_map(TA, TB, vmap):
    """Complete a knot map (TA -> TB) to distinctions and check it place by place.  Shared distinctions between the same
    two knots are matched in increasing order; loose distinctions of one knot in increasing order by mark.  Returns
    (km, dm) or None."""
    km = vmap
    dm = {}
    for y in range(TA.n):
        yb = km[y]
        if len(TA.Ul[y]) != len(TB.Ul[yb]) or len(TA.Bl[y]) != len(TB.Bl[yb]):
            return None
        for e, f in zip(TA.Ul[y], TB.Ul[yb]):
            dm[e] = f
        for e, f in zip(TA.Bl[y], TB.Bl[yb]):
            dm[e] = f
        ga = defaultdict(list)
        for e, z in TA.sh[y]:
            if y < z:
                ga[z].append(e)
        gb = defaultdict(list)
        for f, w in TB.sh[yb]:
            gb[w].append(f)
        for z, es in ga.items():
            fs = sorted(gb.get(km[z], []))
            es = sorted(es)
            if len(fs) != len(es):
                return None
            for e, f in zip(es, fs):
                dm[e] = f
    if not check_structure_map(TA, TB, km, dm):
        return None
    return km, dm


def check_structure_map(TA, TB, km, dm):
    if len(km) != TA.n or TA.n != TB.n or len(set(km)) != TA.n:
        return False
    if len(set(dm.values())) != len(dm):
        return False
    for y in range(TA.n):
        yb = km[y]
        if len(TA.places[y]) != len(TB.places[yb]):
            return False
        if TA.stamp[y] != TB.stamp[yb]:
            return False
        pb = set(TB.places[yb])
        for e in TA.places[y]:
            f = dm.get(e)
            if f is None or f not in pb:
                return False
            ha = TA.holders[e]
            hb = TB.holders[f]
            if len(ha) != len(hb):
                return False
            if len(ha) == 1:
                if bool(TA.barred[e]) != bool(TB.barred[f]):
                    return False
            elif sorted(km[h] for h in ha) != sorted(hb):
                return False
    return True


def places_map(TA, TB, km, dm):
    """Item index of TA -> item index of TB under a checked map."""
    out = {}
    for i, (x, e) in enumerate(TA.items):
        j = TB.item_index.get((km[x], dm[e]))
        if j is None:
            raise AssertionError('a checked map does not carry a chosen place to a chosen place')
        out[i] = j
    return out


# ============================================================================== generators from the record

class RecordGenerators:
    """For a reference structure T (pfh_struct.Struct.from_engine; knots numbered in order of birth), candidate
    automorphisms: every automorphism of the start (compressed form, found by exhaustive search), and every exchange of
    two knots born in the same round with the same parents and the same numbers of places and barred places; each is
    extended round by round (a knot with parents Q goes to an unused knot of its round with parents sigma(Q) and the same
    numbers, itself when possible) and checked place by place."""

    def __init__(self, T, n_start):
        self.T = T
        self.n_start = n_start
        n = T.n
        self.nfresh = [len(T.places[c]) - len(T.parents[c]) for c in range(n)]
        self.nbar = [T.nB[c] for c in range(n)]
        self.own = [None] * n
        self.by_key = defaultdict(list)
        for c in range(n_start, n):
            k = (T.made[c], tuple(sorted(T.parents[c])), self.nfresh[c], self.nbar[c])
            self.own[c] = k
            self.by_key[k].append(c)
        self.checked = 0
        self.failed = 0

    def start_maps(self):
        """Automorphisms of the start's compressed form, as knot maps on the start knots, with their place maps checked
        on the start (shared and loose places of the start, not the later children)."""
        T = self.T
        ns = self.n_start
        colour = []
        adj = []
        for y in range(ns):
            # in the reference, a start knot's places: shared with start knots, or taken by children / loose; at the
            # start they were loose. The start's own compressed form: loose count = places not shared with a start knot
            cnt = {}
            loose = 0
            for e in T.places[y]:
                hs = T.holders[e]
                z = None
                if len(hs) == 2:
                    z = hs[0] if hs[1] == y else hs[1]
                if z is not None and z < ns:
                    cnt[z] = cnt.get(z, 0) + 1
                else:
                    loose += 1
            colour.append((loose,))
            adj.append(sorted((z, (k, 0)) for z, k in cnt.items()))
        G = Graph(ns, colour, adj)
        return ISO.all_automorphisms(G)

    def extend(self, sigma0, first):
        """sigma0: dict on knots < first (and possibly some knots >= first); returns the knot map or None."""
        T = self.T
        n = T.n
        sigma = list(range(n))
        used = [False] * n
        fixed = [False] * n
        for c, v in sigma0.items():
            sigma[c] = v
            used[v] = True
            fixed[c] = True
        for c in range(n):
            if c < first and not fixed[c]:
                # identity on the prefix not given
                sigma[c] = c
                used[c] = True
                fixed[c] = True
        ptr = defaultdict(int)
        for c in range(first, n):
            if fixed[c]:
                continue
            k = self.own[c]
            if k is None:
                return None
            P = tuple(sorted(sigma[p] for p in T.parents[c]))
            key = (k[0], P, k[2], k[3])
            if key == k and not used[c]:
                sigma[c] = c
                used[c] = True
                continue
            cands = self.by_key.get(key)
            if not cands:
                return None
            chosen = None
            for v in cands:
                if not used[v]:
                    chosen = v
                    break
            if chosen is None:
                return None
            sigma[c] = chosen
            used[chosen] = True
        return sigma

    def complete(self, sigma):
        """Distinction map for a knot map of the whole reference structure, and the check."""
        T = self.T
        dm = {}
        for y in range(T.n):
            yb = sigma[y]
            if len(T.Ul[y]) != len(T.Ul[yb]) or len(T.Bl[y]) != len(T.Bl[yb]):
                return None
            for e, f in zip(T.Ul[y], T.Ul[yb]):
                if e != f:
                    dm[e] = f
            for e, f in zip(T.Bl[y], T.Bl[yb]):
                if e != f:
                    dm[e] = f
        # shared distinctions: group by pair of holders
        for y in range(T.n):
            yb = sigma[y]
            ga = defaultdict(list)
            for e, z in T.sh[y]:
                if y < z:
                    ga[z].append(e)
            if not ga:
                continue
            gb = defaultdict(list)
            for f, w in T.sh[yb]:
                gb[w].append(f)
            for z, es in ga.items():
                fs = gb.get(sigma[z], [])
                if len(fs) != len(es):
                    return None
                for e, f in zip(sorted(es), sorted(fs)):
                    if e != f:
                        dm[e] = f
        self.checked += 1
        ok = check_structure_map(T, T, sigma, _Full(dm))
        if not ok:
            self.failed += 1
            return None
        return dm

    def generators(self, max_gens=None):
        """Yield (sigma, dm) for every candidate that passes the check."""
        T = self.T
        ns = self.n_start
        for a in self.start_maps():
            if a == list(range(ns)):
                continue
            s0 = {c: a[c] for c in range(ns)}
            sig = self.extend(s0, ns)
            if sig is None:
                self.failed += 1
                continue
            dm = self.complete(sig)
            if dm is not None:
                yield sig, dm
        groups = defaultdict(list)
        for c in range(ns, T.n):
            groups[self.own[c]].append(c)
        for k, cs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            if len(cs) < 2:
                continue
            for c1, c2 in zip(cs, cs[1:]):
                s0 = {c1: c2, c2: c1}
                sig = self.extend(s0, c1)
                if sig is None:
                    self.failed += 1
                    continue
                dm = self.complete(sig)
                if dm is not None:
                    yield sig, dm


class _Full(dict):
    """A distinction map stored sparsely: identity where no entry."""

    def get(self, k, default=None):
        return dict.get(self, k, k)

    def values(self):
        return dict.values(self)


def orbit_links(T, gens):
    """Item pairs (i, j) linked by the generators (each (sigma, dm) with dm sparse)."""
    links = []
    for sig, dm in gens:
        moved = {y for y in range(T.n) if sig[y] != y}
        touched = set(moved)
        for e, f in dm.items():
            for h in T.holders[e]:
                touched.add(h)
        for y in touched:
            for e, z in T.sh[y]:
                i = T.item_index[(y, e)]
                j = T.item_index.get((sig[y], dm.get(e, e)))
                if j is None:
                    raise AssertionError('generator does not carry a place to a place')
                if i != j:
                    links.append((i, j))
    return links
