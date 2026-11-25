"""What is looked at within d holder steps of a knot x, with a place a chosen (pre-registration, "Definitions").

Copied from PARENTS-FROM-HOLDERS-20261124-001A-E001 (commit 307b3bbe63) and extended for LEAST-RECORD-20261124-001A-E001:
a look also shows the stamp of every knot it shows (and nothing of a knot farther than d); a renaming must keep stamps.

A look is extracted from a structure (pfh_struct.Struct) and from then on lives alone: every quantity used to tell two
looks apart is computed on the extracted look (deviations.md, items 10-15), never on the structure.

Kinds of look (deviations.md, items 10-12):
  'full'  every place of every knot within d, marked U (loose, usable), B (loose, barred) or S (shared); a shared
          distinction with both holders within d is one distinction; one whose other holder is farther is S only.
  'c1'    as 'full' with U and B merged into L.
  'c2'    each knot only as live or dead and its number of places; the shared distinctions with both holders within d.

Two forms of a look:
  FullLook     knots, distinctions with their holders in the look and their marks; x and a.  Used to check a renaming
               place by place and by the brute-force check (a).
  Compressed   (pfh_iso.Graph) one vertex per knot, coloured; one labelled edge per pair of knots that share
               distinctions in the look.  Used by the search.
"""
from __future__ import annotations

from collections import deque

from pfh_iso import Graph

VARIANTS = ('full', 'c1', 'c2')


class FullLook:
    """knots: list of structure knots (x first, then breadth-first); dist: knot -> distance; marks: distinction -> mark;
    holders: distinction -> tuple of knots of the look holding it (1 or 2); kplaces: knot -> list of its distinctions in
    the look; kattr: knot -> extra attribute (for 'c2': (live, number of places); else None)."""

    __slots__ = ('variant', 'd', 'x', 'a', 'knots', 'dist', 'marks', 'holders', 'kplaces', 'kattr', 'n_members',
                 'n_start', 'stamp')

    def n_knots(self):
        return len(self.knots)

    def n_distinctions(self):
        return len(self.marks)


def ball(S, x, d):
    """Knots within holder-step distance d of x, breadth-first (x first), with their distances."""
    dist = {x: 0}
    order = [x]
    q = deque([x])
    sh = S.sh
    while q:
        u = q.popleft()
        du = dist[u]
        if du >= d:
            continue
        for _, w in sh[u]:
            if w not in dist:
                dist[w] = du + 1
                order.append(w)
                q.append(w)
    return order, dist


def extract(S, x, a, d, variant='full'):
    """The look of (x, a) within d in structure S, as a FullLook."""
    if variant not in VARIANTS:
        raise ValueError(variant)
    hs = S.holders[a]
    if len(hs) != 2 or x not in hs:
        raise ValueError('the chosen place must be a shared place of x')
    order, dist = ball(S, x, d)
    L = FullLook()
    L.variant = variant
    L.d = d
    L.x = x
    L.a = a
    L.knots = order
    L.dist = dist
    marks = {}
    holders = {}
    kplaces = {}
    kattr = {}
    nmem = 0
    nst = 0
    for y in order:
        P = []
        if S.nU[y]:
            nmem += 1
        if S.is_start[y]:
            nst += 1
        for e, z in S.sh[y]:
            if z in dist:
                P.append(e)
                if e not in holders:
                    holders[e] = (y, z) if y < z else (z, y)
                    marks[e] = 'S'
            elif variant != 'c2':
                P.append(e)
                holders[e] = (y,)
                marks[e] = 'S'
        if variant != 'c2':
            lm_u = 'U' if variant == 'full' else 'L'
            lm_b = 'B' if variant == 'full' else 'L'
            for e in S.Ul[y]:
                P.append(e)
                holders[e] = (y,)
                marks[e] = lm_u
            for e in S.Bl[y]:
                P.append(e)
                holders[e] = (y,)
                marks[e] = lm_b
            kattr[y] = None
        else:
            kattr[y] = (S.nU[y] + S.nB[y] > 0, S.n_places(y))
        kplaces[y] = P
    L.marks = marks
    L.holders = holders
    L.kplaces = kplaces
    L.kattr = kattr
    L.n_members = nmem
    L.n_start = nst
    L.stamp = {y: S.stamp[y] for y in order}
    return L


def compress(L, extra=None):
    """The compressed form of a FullLook (deviations.md, item 14), with the data needed to rebuild a full renaming.
    extra: optional dict knot -> value appended to the knot's colour (a value computed on the look, pfh_views.in_look).

    Returns (graph, info): graph vertices are the look's knots in L.knots order (x is vertex 0); info holds, for each
    vertex, its loose and one-holder distinctions by mark, and for each edge its shared distinctions."""
    idx = {y: i for i, y in enumerate(L.knots)}
    n = len(L.knots)
    colour = [None] * n
    adjm = [dict() for _ in range(n)]
    per_mark = [dict() for _ in range(n)]       # vertex -> mark -> sorted list of one-holder distinctions
    edge_d = {}                                  # (i, j) i<j -> sorted list of shared distinctions
    for y in L.knots:
        i = idx[y]
        pm = per_mark[i]
        for e in L.kplaces[y]:
            hs = L.holders[e]
            if len(hs) == 2:
                z = hs[0] if hs[1] == y else hs[1]
                j = idx[z]
                key = (i, j) if i < j else (j, i)
                if i < j:
                    edge_d.setdefault(key, []).append(e)
            else:
                pm.setdefault(L.marks[e], []).append(e)
        for m in pm:
            pm[m].sort()
    for key in edge_d:
        edge_d[key].sort()
    for (i, j), es in edge_d.items():
        lab = (len(es), 1 if L.a in es else 0)
        adjm[i][j] = lab
        adjm[j][i] = lab
    for y in L.knots:
        i = idx[y]
        isx = 1 if y == L.x else 0
        pm = per_mark[i]
        if L.variant == 'full':
            colour[i] = (isx, len(pm.get('U', ())), len(pm.get('B', ())), len(pm.get('S', ())))
        elif L.variant == 'c1':
            colour[i] = (isx, len(pm.get('L', ())), len(pm.get('S', ())))
        else:
            live, npl = L.kattr[y]
            colour[i] = (isx, 1 if live else 0, npl)
        colour[i] = colour[i] + (L.stamp[y],)
        if extra is not None:
            colour[i] = colour[i] + (L.dist[y], extra[y])
    adj = [sorted(adjm[i].items()) for i in range(n)]
    G = Graph(n, colour, adj)
    info = {'idx': idx, 'per_mark': per_mark, 'edge_d': edge_d}
    return G, info


def full_renaming(LA, infoA, LB, infoB, vmap):
    """Extend a renaming of compressed forms (vmap: vertex of A -> vertex of B) to a renaming of looks: a map of knots
    and a map of distinctions (deviations.md, item 14)."""
    kmap = {}
    for i, y in enumerate(LA.knots):
        kmap[y] = LB.knots[vmap[i]]
    dmap = {}
    for i in range(len(LA.knots)):
        j = vmap[i]
        pa = infoA['per_mark'][i]
        pb = infoB['per_mark'][j]
        for m, es in pa.items():
            fs = pb.get(m, [])
            if len(fs) != len(es):
                return None, None
            for e, f in zip(es, fs):
                dmap[e] = f
    for (i, j), es in infoA['edge_d'].items():
        bi, bj = vmap[i], vmap[j]
        key = (bi, bj) if bi < bj else (bj, bi)
        fs = infoB['edge_d'].get(key)
        if fs is None or len(fs) != len(es):
            return None, None
        es2 = list(es)
        fs2 = list(fs)
        if LA.a in es2:
            if LB.a not in fs2:
                return None, None
            es2.remove(LA.a)
            fs2.remove(LB.a)
            dmap[LA.a] = LB.a
        for e, f in zip(es2, fs2):
            dmap[e] = f
    return kmap, dmap


def check_renaming(LA, LB, kmap, dmap):
    """Place by place: x to x, a to a, knots one to one, distinctions one to one, every place of every knot carried to a
    place of its image with the same mark, every distinction's holders carried to the image's holders, and (for 'c2')
    every knot's live bit and number of places kept.  Returns (ok, reason)."""
    if LA.variant != LB.variant:
        return False, 'different kinds of look'
    if kmap is None or dmap is None:
        return False, 'no renaming'
    if kmap.get(LA.x) != LB.x:
        return False, 'x not carried to x'
    if dmap.get(LA.a) != LB.a:
        return False, 'a not carried to a'
    if set(kmap) != set(LA.knots) or sorted(kmap.values()) != sorted(LB.knots):
        return False, 'knot map not one to one onto'
    if set(dmap) != set(LA.marks) or len(set(dmap.values())) != len(dmap) or set(dmap.values()) != set(LB.marks):
        return False, 'distinction map not one to one onto'
    for y in LA.knots:
        yb = kmap[y]
        if LA.kattr[y] != LB.kattr[yb]:
            return False, 'knot attribute of %r' % (y,)
        if LA.stamp[y] != LB.stamp[yb]:
            return False, 'stamp of %r' % (y,)
        pa = LA.kplaces[y]
        pb = LB.kplaces[yb]
        if len(pa) != len(pb):
            return False, 'number of places of %r' % (y,)
        sb = set(pb)
        for e in pa:
            f = dmap[e]
            if f not in sb:
                return False, 'place %r of %r not carried to a place of %r' % (e, y, yb)
            if LA.marks[e] != LB.marks[f]:
                return False, 'mark of %r' % (e,)
            ha = LA.holders[e]
            hb = LB.holders[f]
            if sorted(kmap[h] for h in ha) != sorted(hb):
                return False, 'holders of %r' % (e,)
    for y in LA.knots:
        if LA.dist[y] != LB.dist[kmap[y]]:
            return False, 'distance of %r (cannot happen for a renaming)' % (y,)
    return True, 'ok'


def look_summary(L):
    return {'variant': L.variant, 'd': L.d, 'knots': len(L.knots), 'distinctions': len(L.marks),
            'members': L.n_members, 'start_knots': L.n_start}


def renaming_record(LA, LB, kmap, dmap):
    """A renaming written out for an output file."""
    return {'knots': [[y, kmap[y]] for y in LA.knots], 'stamps': [[LA.stamp[y], LB.stamp[kmap[y]]] for y in LA.knots],
            'distinctions': [[e, dmap[e]] for e in sorted(dmap, key=repr)],
            'x': [LA.x, LB.x], 'a': [LA.a, LB.a]}
