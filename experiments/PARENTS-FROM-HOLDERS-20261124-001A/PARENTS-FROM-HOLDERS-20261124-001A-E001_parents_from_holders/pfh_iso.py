"""Exact tests of being alike for compressed looks (deviations.md, items 14-16).

A Graph has vertices 0..n-1, a colour per vertex (an orderable tuple) and labelled undirected edges (adj[v] = sorted
list of (w, label)).  Vertex 0 is x; x is told by its colour; the chosen place a is told by its edge label.

  cr_invariant(G, intern)  canonical colour refinement of one graph: (rounds to stability, multiset of final colours),
                           colours named by interned signatures.  An invariant of G: equal for alike graphs.
  find_renaming(GA, GB)    exhaustive individualization-refinement on the disjoint union.  Returns a vertex map
                           A -> B that is checked edge by edge, or None when there is none (every branch failed).
  all_automorphisms(G)     every automorphism of a small graph (the starts), by the same search, not pruned.
"""
from __future__ import annotations

import sys
from collections import Counter, deque

sys.setrecursionlimit(100000)


class Graph:
    __slots__ = ('n', 'colour', 'adj')

    def __init__(self, n, colour, adj):
        self.n = n
        self.colour = colour
        self.adj = adj


STATS = Counter()


# ============================================================================== colour refinement of one graph

def cr_invariant(G, intern):
    """Rounds of refinement until the partition stops changing, and the sorted multiset of the final colours.  Colours
    are named by interning (old colour, sorted (label, neighbour colour) list), so the value is a function of the graph
    up to renaming.  intern is a dict shared by every graph compared."""
    n = G.n
    col = [intern.setdefault(('c', G.colour[v]), len(intern)) for v in range(n)]
    ncells = len(set(col))
    rounds = 0
    adj = G.adj
    while True:
        new = [0] * n
        for v in range(n):
            sig = (col[v], tuple(sorted((lab, col[w]) for w, lab in adj[v])))
            c = intern.get(sig)
            if c is None:
                c = len(intern)
                intern[sig] = c
            new[v] = c
        rounds += 1
        nc = len(set(new))
        col = new
        if nc == ncells:
            break
        ncells = nc
    return (rounds, tuple(sorted(Counter(col).items()))), col


# ============================================================================== refinement on a disjoint union

class _Union:
    """The disjoint union of A (vertices 0..nA-1) and B (nA..n-1) with integer edge weights encoding labels."""

    __slots__ = ('n', 'nA', 'adj')

    def __init__(self, GA, GB):
        labels = sorted({lab for G in (GA, GB) for v in range(G.n) for _, lab in G.adj[v]})
        if len(labels) > 7:
            raise ValueError('too many edge labels for the weight encoding')
        wt = {lab: 1 << (8 * i) for i, lab in enumerate(labels)}
        nA = GA.n
        self.nA = nA
        self.n = nA + GB.n
        adj = [None] * self.n
        for v in range(nA):
            adj[v] = [(w, wt[lab]) for w, lab in GA.adj[v]]
        for v in range(GB.n):
            adj[nA + v] = [(nA + w, wt[lab]) for w, lab in GB.adj[v]]
        self.adj = adj


def _initial(U, GA, GB):
    """Initial ordered partition by colour; None when some colour class is unbalanced."""
    nA = U.nA
    n = U.n
    keyed = sorted(range(n), key=lambda v: (GA.colour[v] if v < nA else GB.colour[v - nA]))
    lab = keyed
    pos = [0] * n
    for i, v in enumerate(lab):
        pos[v] = i
    cs = [0] * n
    ce = [0] * n
    starts = []
    i = 0
    while i < n:
        v = lab[i]
        c = GA.colour[v] if v < nA else GB.colour[v - nA]
        j = i + 1
        while j < n:
            w = lab[j]
            cw = GA.colour[w] if w < nA else GB.colour[w - nA]
            if cw != c:
                break
            j += 1
        na = 0
        for k in range(i, j):
            cs[lab[k]] = i
            if lab[k] < nA:
                na += 1
        if 2 * na != j - i:
            return None, None
        ce[i] = j
        starts.append(i)
        i = j
    return [lab, pos, cs, ce], starts


def _refine(st, U, queue_starts):
    """Refine to the coarsest equitable partition (splitter queue, all fragments but the largest re-queued).  Returns
    False as soon as some fragment holds unequal numbers of vertices of A and B."""
    lab, pos, cs, ce = st
    adj = U.adj
    nA = U.nA
    q = deque(queue_starts)
    inq = set(queue_starts)
    while q:
        s = q.popleft()
        inq.discard(s)
        e = ce[s]
        cnt = {}
        for i in range(s, e):
            for v, wt in adj[lab[i]]:
                cnt[v] = cnt.get(v, 0) + wt
        if not cnt:
            continue
        byc = {}
        for v in cnt:
            t = cs[v]
            L = byc.get(t)
            if L is None:
                byc[t] = [v]
            else:
                L.append(v)
        for t in sorted(byc):
            tv = byc[t]
            te = ce[t]
            size = te - t
            if size == 1:
                continue
            if len(tv) == size:
                k0 = cnt[tv[0]]
                same = True
                for v in tv:
                    if cnt[v] != k0:
                        same = False
                        break
                if same:
                    continue
            # move the touched vertices to the tail of the cell
            tail = te
            for v in tv:
                tail -= 1
                pv = pos[v]
                u = lab[tail]
                lab[pv] = u
                pos[u] = pv
                lab[tail] = v
                pos[v] = tail
            seg = sorted(lab[tail:te], key=cnt.__getitem__)
            lab[tail:te] = seg
            for i in range(tail, te):
                pos[lab[i]] = i
            frags = []
            if tail > t:
                frags.append((t, tail))
            i = tail
            while i < te:
                k = cnt[lab[i]]
                j = i + 1
                while j < te and cnt[lab[j]] == k:
                    j += 1
                frags.append((i, j))
                i = j
            if len(frags) == 1:
                continue
            for (a, b) in frags:
                ce[a] = b
                na = 0
                for i in range(a, b):
                    v = lab[i]
                    cs[v] = a
                    if v < nA:
                        na += 1
                if 2 * na != b - a:
                    return False
            if t in inq:
                for (a, b) in frags[1:]:
                    q.append(a)
                    inq.add(a)
            else:
                big = 0
                bsz = frags[0][1] - frags[0][0]
                for k in range(1, len(frags)):
                    sz = frags[k][1] - frags[k][0]
                    if sz > bsz:
                        big, bsz = k, sz
                for k, (a, b) in enumerate(frags):
                    if k != big:
                        q.append(a)
                        inq.add(a)
    return True


def _individualize(st, v, w):
    """Split v (of A) and w (of B) off their common cell into a cell of their own; return the splitter."""
    lab, pos, cs, ce = st
    s = cs[v]
    e = ce[s]
    for target, u in ((s, v), (s + 1, w)):
        pu = pos[u]
        z = lab[target]
        lab[pu] = z
        pos[z] = pu
        lab[target] = u
        pos[u] = target
    ce[s] = s + 2
    if s + 2 < e:
        ce[s + 2] = e
        for i in range(s + 2, e):
            cs[lab[i]] = s + 2
    cs[v] = s
    cs[w] = s
    return [s]


def _copy(st):
    return [st[0][:], st[1][:], st[2][:], st[3][:]]


def _check_map(GA, GB, m):
    if len(m) != GA.n or sorted(m) != list(range(GB.n)):
        return False
    for v in range(GA.n):
        if GA.colour[v] != GB.colour[m[v]]:
            return False
        ea = sorted((m[w], lab) for w, lab in GA.adj[v])
        eb = sorted(GB.adj[m[v]])
        if ea != eb:
            return False
    return True


def find_renaming(GA, GB, collect_all=False, max_count=None):
    """Exhaustive individualization-refinement search for a renaming A -> B (colours and labelled edges kept).

    Returns a list m with m[v] = image of v, checked edge by edge, or None when no renaming exists.  With collect_all,
    returns the list of every renaming (used only for the small starts)."""
    STATS['searches'] += 1
    if GA.n != GB.n:
        STATS['different_sizes'] += 1
        return [] if collect_all else None
    if sorted(GA.colour) != sorted(GB.colour):
        STATS['different_colours'] += 1
        return [] if collect_all else None
    U = _Union(GA, GB)
    st, starts = _initial(U, GA, GB)
    if st is None:
        STATS['different_colours'] += 1
        return [] if collect_all else None
    if not _refine(st, U, starts):
        STATS['root_unbalanced'] += 1
        return [] if collect_all else None
    nA = U.nA
    n = U.n
    found = []

    # iterative depth-first search
    stack = [(st, None, None, 0)]
    # each frame: (state, cell vertices of B to try, v, next index)
    def leaf_or_target(stt):
        lab, pos, cs, ce = stt
        i = 0
        while i < n:
            e = ce[i]
            if e - i > 2:
                return i, e
            i = e
        return None

    root = leaf_or_target(st)
    if root is None:
        m = _leaf_map(st, nA, n)
        if _check_map(GA, GB, m):
            STATS['found'] += 1
            return [m] if collect_all else m
        raise AssertionError('balanced discrete partition is not a renaming')
    frames = []

    def push(stt, cell):
        lab = stt[0]
        s, e = cell
        vs = [lab[j] for j in range(s, e)]
        v = min(u for u in vs if u < nA)
        ws = [u for u in vs if u >= nA]
        frames.append((stt, v, ws, [0]))

    push(st, root)
    nodes = 0
    while frames:
        stt, v, ws, ptr = frames[-1]
        if ptr[0] >= len(ws):
            frames.pop()
            continue
        w = ws[ptr[0]]
        ptr[0] += 1
        nodes += 1
        st2 = _copy(stt)
        spl = _individualize(st2, v, w)
        if not _refine(st2, U, spl):
            continue
        tgt = leaf_or_target(st2)
        if tgt is None:
            m = _leaf_map(st2, nA, n)
            if _check_map(GA, GB, m):
                if not collect_all:
                    STATS['found'] += 1
                    STATS['nodes'] += nodes
                    return m
                found.append(m)
                if max_count is not None and len(found) >= max_count:
                    return found
            continue
        push(st2, tgt)
    STATS['nodes'] += nodes
    if collect_all:
        return found
    STATS['exhausted'] += 1
    return None


def _leaf_map(st, nA, n):
    lab, pos, cs, ce = st
    m = [None] * nA
    i = 0
    while i < n:
        e = ce[i]
        a, b = lab[i], lab[i + 1]
        if a >= nA:
            a, b = b, a
        m[a] = b - nA
        i = e
    return m


def all_automorphisms(G, max_count=100000):
    """Every automorphism of G (each checked edge by edge).  Only for small graphs (the starts)."""
    return find_renaming(G, G, collect_all=True, max_count=max_count)
