"""The depth-d unfolding of every chosen place of a structure at once (deviations.md, item 21).

Copied from PARENTS-FROM-HOLDERS-20261124-001A-E001 (commit 307b3bbe63) and extended for LEAST-RECORD-20261124-001A-E001:
the marks of a knot include its stamp, which the look shows for every knot it shows.

unfold(S, variant, dmax, intern) returns, for d = 1..dmax, a list over S.items (the chosen places, in order) of the
interned identifier of the unfolding of depth d.  Identifiers are interned tuples, shared by every structure that uses
the same intern dict, so equal identifiers mean equal unfoldings.

Why this is a function of the look of (x, a) within d (and so may tell looks apart): a non-backtracking walk of at most d
holder steps from x visits only knots within d; a knot reached after t < d steps is within d - 1 of x, so every shared
place of it leads to a knot of the look and is seen there as one distinction; a knot reached after d steps contributes
only its marks, which the look shows for every knot it holds.
"""
from __future__ import annotations


def marks_of(S, variant):
    out = []
    for y in range(S.n):
        U = S.nU[y]
        B = S.nB[y]
        Sh = len(S.sh[y])
        st = S.stamp[y]
        if variant == 'full':
            out.append((U, B, Sh, st))
        elif variant == 'c1':
            out.append((U + B, Sh, st))
        elif variant == 'c2':
            out.append((1 if U + B > 0 else 0, U + B + Sh, st))
        else:
            raise ValueError(variant)
    return out


def unfold(S, variant, dmax, intern, stable=False):
    """With stable=True, continue past dmax until the partition of places stops refining (used on whole structures,
    deviations.md item 27); returns (dict d -> list, depth reached)."""
    n = S.n
    sh = S.sh
    mk = marks_of(S, variant)
    get = intern.get
    # directed edges: for knot u, index i -> (u entered through sh[u][i].e)
    prev = []
    for u in range(n):
        c = get(('m', mk[u]))
        if c is None:
            c = len(intern)
            intern[('m', mk[u])] = c
        prev.append([c] * len(sh[u]))
    # position of each directed edge from the other side: for u, i (e, w): the index j of e in sh[w]
    back = []
    for u in range(n):
        L = []
        for e, w in sh[u]:
            j = None
            for k, (e2, w2) in enumerate(sh[w]):
                if e2 == e:
                    j = k
                    break
            L.append(j)
        back.append(L)
    out = {}
    d = 0
    last_classes = None
    while True:
        d += 1
        # the view of w entered through e (from u) is prev[w][back[u][i]]
        root = []
        for u in range(n):
            L = sh[u]
            if not L:
                continue
            ch = [prev[w][back[u][i]] for i, (e, w) in enumerate(L)]
            for i in range(len(L)):
                rest = tuple(sorted(ch[:i] + ch[i + 1:]))
                key = ('r', mk[u], ch[i], rest)
                c = get(key)
                if c is None:
                    c = len(intern)
                    intern[key] = c
                root.append(c)
        if d <= dmax or not stable:
            out[d] = root
        nxt = []
        for u in range(n):
            L = sh[u]
            ch = [prev[w][back[u][i]] for i, (e, w) in enumerate(L)]
            row = []
            for i in range(len(L)):
                key = ('v', mk[u], tuple(sorted(ch[:i] + ch[i + 1:])))
                c = get(key)
                if c is None:
                    c = len(intern)
                    intern[key] = c
                row.append(c)
            nxt.append(row)
        if not stable:
            prev = nxt
            if d >= dmax:
                return out
        else:
            # the partition of directed steps determines every later depth: once it stops refining, it never changes,
            # and the partition of places at every later depth equals the one at this depth
            flat_prev = [c for row in prev for c in row]
            flat_nxt = [c for row in nxt for c in row]
            prev = nxt
            if d >= dmax and _same_partition(flat_prev, flat_nxt):
                out['stable'] = root
                return out, d


def _same_partition(a, b):
    m = {}
    for x, y in zip(a, b):
        if m.setdefault(x, y) != y:
            return False
    m2 = {}
    for x, y in zip(a, b):
        if m2.setdefault(y, x) != x:
            return False
    return True


def in_look(L, intern):
    """The unfoldings of item 21 computed on an extracted look (pfh_look.FullLook) alone: the root unfolding of (x, a)
    at depth L.d, and for every knot y of the look its unfolding of depth L.d - dist(y) entered from no side.  Uses the
    same interning as the structure-wide computation, so equal values have equal identifiers; for every compared place
    the root value is checked against the structure-wide one (deviations.md, item 32)."""
    d = L.d
    variant = L.variant
    vis = {}
    mk = {}
    for y in L.knots:
        V = []
        nS = 0
        nU = nB = nL = 0
        for e in L.kplaces[y]:
            hs = L.holders[e]
            m = L.marks[e]
            if m == 'S':
                nS += 1
                if len(hs) == 2:
                    V.append((e, hs[0] if hs[1] == y else hs[1]))
            elif m == 'U':
                nU += 1
            elif m == 'B':
                nB += 1
            else:
                nL += 1
        V.sort()
        vis[y] = V
        st = L.stamp[y]
        if variant == 'full':
            mk[y] = (nU, nB, nS, st)
        elif variant == 'c1':
            mk[y] = (nL, nS, st)
        else:
            live, npl = L.kattr[y]
            mk[y] = (1 if live else 0, npl, st)
    get = intern.get

    def iid(key):
        c = get(key)
        if c is None:
            c = len(intern)
            intern[key] = c
        return c
    memo = {}

    def val(z, e, k):
        key = (z, e, k)
        r = memo.get(key)
        if r is not None:
            return r
        if k == 0:
            r = iid(('m', mk[z]))
        else:
            if L.dist[z] > d - k:
                raise AssertionError('an unfolding would leave the look')
            if variant != 'c2' and len(vis[z]) != sum(1 for f in L.kplaces[z] if L.marks[f] == 'S'):
                raise AssertionError('a knot inside the rim with a shared place leading outside')
            r = iid(('v', mk[z], tuple(sorted(val(w, f, k - 1) for f, w in vis[z] if f != e))))
        memo[key] = r
        return r
    x = L.x
    a = L.a
    ch = []
    ca = None
    for f, w in vis[x]:
        c = val(w, f, d - 1)
        if f == a:
            ca = c
        else:
            ch.append(c)
    root = iid(('r', mk[x], ca, tuple(sorted(ch))))
    unr = {}
    for y in L.knots:
        k = d - L.dist[y]
        if k == 0:
            unr[y] = iid(('u0', mk[y]))
        else:
            unr[y] = iid(('u', mk[y], tuple(sorted(val(w, f, k - 1) for f, w in vis[y]))))
    return root, unr
