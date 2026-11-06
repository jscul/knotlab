"""Native genus, for NATIVE-GENUS-20261104-001.

A design is a base space (plane glue, or any knot space) with atoms attached at 3-edge cuts. An atom is a census knot space with one
element removed: at a base point it loses a line and emits; at a base line it loses a point and receives. Points and lines keep keys
across builds, so the space with any subset of the atoms can be compared with the full one entry by entry. Each splice puts the port in
the place of the removed vertex, with the twist under which an intact atom acts as that vertex (interface lemma, HANDLE-LOCALITY A).

The creation map: for a removal M and a gluing line L that shows six patterns in the solutions of the space minus M, whether splicing L
into one of the four census far sides creates a new crossing knot of up to three points (join method, exact). Lines showing fewer
patterns count as non-creating.
"""
import collections
import itertools
import sys
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RELAY-NET-20261104-001A/RELAY-NET-20261104-001A-P001_arc_signals_and_repeaters"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"))
import relay_lib as RL  # noqa: E402
import surface_lib as SU  # noqa: E402

G, J, E, CL, PL, FL = RL.G, RL.J, RL.E, RL.CL, RL.PL, RL.FL
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FANO, C58 = SP[21], SP[58]
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
ATOMS = {"F": FANO, "c58": C58}


class Space:
    """lines H with signs s on n points; lkey/pkey: stable keys; owner[k]: the atom holding line k (atom side of its cut), else None"""

    def __init__(self, H, s, n, lkey, pkey, owner):
        self.H, self.s, self.n = [tuple(L) for L in H], [list(x) for x in s], n
        self.lkey, self.pkey, self.owner = list(lkey), list(pkey), list(owner)
        assert len(self.H) == len(self.s) == len(self.lkey) == len(self.owner) and len(self.pkey) == n

    def line(self, key):
        return self.lkey.index(key)

    def point(self, key):
        return self.pkey.index(key)


def base(H, s, n):
    return Space(H, s, n, [("g", k) for k in range(len(H))], [("g", p) for p in range(n)], [None] * len(H))


def plane(g):
    return base(*PL.to_space(g))


def attach_point(S, pkey, atom, li, name, perm=(0, 1, 2)):
    """splice the atom minus its line li into the point pkey of S: the line's perm[i]-th point replaces the point on the i-th line
    through it, with sign s_line(p) + s_li(point), so an intact atom acts as the point"""
    p = S.point(pkey)
    HA, sA, nA = atom
    Lp, sl = HA[li], sA[li]
    relabel = {q: (nA + k) for k, q in enumerate(q for q in range(S.n) if q != p)}
    through = [k for k, l in enumerate(S.H) if p in l]
    assert len(through) == 3
    lines, signs, lkey, owner = [], [], [], []
    for k, (l, sg) in enumerate(zip(S.H, S.s)):
        if p in l:
            i = perm[through.index(k)]
            j = l.index(p)
            lines.append(tuple(Lp[i] if q == p else relabel[q] for q in l))
            ns = list(sg)
            ns[j] = sg[j] ^ sl[i]
            signs.append(ns)
        else:
            lines.append(tuple(relabel[q] for q in l))
            signs.append(list(sg))
        lkey.append(S.lkey[k])
        owner.append(S.owner[k])
    for i, (l, sg) in enumerate(zip(HA, sA)):
        if i != li:
            lines.append(tuple(l))
            signs.append(list(sg))
            lkey.append((name, i))
            owner.append(name)
    pkey = [(name, q) for q in range(nA)] + [S.pkey[q] for q in range(S.n) if q != p]
    return Space(lines, signs, S.n + nA - 1, lkey, pkey, owner)


def attach_line(S, lkey_, atom, pt, name, perm=(0, 1, 2)):
    """splice the line lkey_ of S into the atom's point pt: the line's perm[i]-th point replaces pt on the i-th atom line through it,
    with sign s_l(point) + s_m(pt), so an intact atom acts as the line"""
    l = S.line(lkey_)
    Ll, sl = S.H[l], S.s[l]
    HA, sA, nA = atom
    relabel = {q: (S.n + k) for k, q in enumerate(q for q in range(nA) if q != pt)}
    through = [i for i, m in enumerate(HA) if pt in m]
    assert len(through) == 3
    lines, signs, lkey, owner = [], [], [], []
    for k, (L, sg) in enumerate(zip(S.H, S.s)):
        if k != l:
            lines.append(L)
            signs.append(list(sg))
            lkey.append(S.lkey[k])
            owner.append(S.owner[k])
    for i, (m, sg) in enumerate(zip(HA, sA)):
        if pt in m:
            t = perm[through.index(i)]
            j = m.index(pt)
            lines.append(tuple(Ll[t] if q == pt else relabel[q] for q in m))
            ns = list(sg)
            ns[j] = sl[t] ^ sg[j]
            signs.append(ns)
        else:
            lines.append(tuple(relabel[q] for q in m))
            signs.append(list(sg))
        lkey.append((name, i))
        owner.append(name)
    pkey = list(S.pkey) + [(name, q) for q in range(nA) if q != pt]
    return Space(lines, signs, S.n + nA - 1, lkey, pkey, owner)


def build(design, subset=None):
    """design = (base Space, [(name, kind 'point'|'line', key, atom (H, s, n), element, perm)]); keep the atoms named in subset"""
    S, atts = design
    for name, kind, key, atom, el, perm in atts:
        if subset is not None and name not in subset:
            continue
        S = (attach_point if kind == "point" else attach_line)(S, key, atom, el, name, perm)
    return S


def interface(atom, kind, el):
    """the patterns an intact atom offers its three ports: for an atom minus a line, the line's literals (value + sign), so it acts as
    the point iff they are the two constant patterns; for an atom split at a point, the values of the three copies, so it acts as the
    line iff they are the six non-constant patterns"""
    HA, sA, nA = atom
    if kind == "point":
        AN = CL.solutions(HA, sA, nA, skip=el)
        return {tuple(int(r[q]) ^ sA[el][i] for i, q in enumerate(HA[el])) for r in AN}
    through = [i for i, m in enumerate(HA) if el in m]
    lines = [tuple((nA + through.index(i)) if q == el else q for q in m) for i, m in enumerate(HA)]
    AN = CL.solutions(lines, sA, nA + 3)
    return {tuple(int(r[nA + t]) for t in range(3)) for r in AN}


def six(AN, L):
    return len({tuple(int(b) for b in r) for r in AN[:, list(L)]}) == 6


def row_task(args):
    """creation by removal M at every other line: a tuple over the four far sides, or None where L shows fewer than six patterns"""
    S, M = args
    AN = CL.solutions(S.H, S.s, S.n, skip=M)
    out = {}
    for L in range(len(S.H)):
        if L == M:
            continue
        if not six(AN, S.H[L]):
            out[L] = None
            continue
        out[L] = tuple(bool(J.new_knots(E, G, AN, S.H, S.s, S.n, L, F, 3)[0]) for fname, F in FARS)
    return M, out


def matrix(S, procs=22, pool=None):
    tasks = [(S, M) for M in range(len(S.H))]
    if pool is not None:
        return dict(pool.map(row_task, tasks))
    with Pool(max(1, min(procs, len(S.H)))) as p:
        return dict(p.map(row_task, tasks))


def creates(res, M, L):
    v = res[M].get(L)
    return bool(v) and any(v)


def by_key(S, res):
    """the creation map keyed by line keys: {(key M, key L): None | bool}"""
    return {(S.lkey[M], S.lkey[L]): (None if v is None else any(v)) for M, row in res.items() for L, v in row.items()}


def creation_graph(S, res):
    g = nx.Graph()
    g.add_nodes_from(range(len(S.H)))
    g.add_edges_from((M, L) for M in res for L in res[M] if creates(res, M, L))
    return g


def quiet_parts(S, res, limit=500):
    """every maximum set of lines with no creation between any two (both directions): maximum independent sets of the creation graph"""
    comp = nx.complement(creation_graph(S, res))
    best, out = 0, []
    for c in nx.find_cliques(comp):
        if len(c) > best:
            best, out = len(c), [frozenset(c)]
        elif len(c) == best:
            out.append(frozenset(c))
        if len(out) > limit:
            break
    return best, out


def pieces(S, V):
    """the creative part's pieces: (lines joined through shared points, interior points joined along creative lines), where a point is
    interior when all its lines are creative"""
    V = set(V)
    gp = nx.Graph()
    gp.add_nodes_from(V)
    gp.add_edges_from((a, b) for a, b in itertools.combinations(sorted(V), 2) if set(S.H[a]) & set(S.H[b]))
    on = collections.defaultdict(list)
    for k, L in enumerate(S.H):
        for q in L:
            on[q].append(k)
    interior = [q for q in range(S.n) if on[q] and all(k in V for k in on[q])]
    gi = nx.Graph()
    gi.add_nodes_from(interior)
    gi.add_edges_from((p, q) for p, q in itertools.combinations(interior, 2) if any(p in S.H[k] and q in S.H[k] for k in V))
    return [sorted(c) for c in nx.connected_components(gp)], [sorted(c) for c in nx.connected_components(gi)]


def native(S, res):
    """the native counts over every quiet part: {'quiet size', 'quiet parts', 'counts' (set of (by points, by interior points)),
    'V' (the creative part of the first quiet part), 'line pieces', 'interior pieces'}"""
    best, Ps = quiet_parts(S, res)
    counts, first = set(), None
    for P in Ps:
        V = [k for k in range(len(S.H)) if k not in P]
        lp, ip = pieces(S, V)
        counts.add((len(lp), len(ip)))
        if first is None:
            first = (V, lp, ip)
    return {"quiet size": best, "quiet parts": len(Ps), "counts": sorted(counts), "V": first[0], "line pieces": first[1],
            "interior pieces": first[2]}


def sat_genus(S, lo=0):
    edges = [(("p", q), ("l", k)) for k, L in enumerate(S.H) for q in L]
    return SU.genus(edges, lo=lo)
