"""Library for EXACT-TOWERS-20261029-001B-P001: the three minimal exact gadgets (parity triangle, twisted not-all-equal punctured
tetrahedron, not-all-equal punctured Fano plane), the towers they generate by substitution with private hidden variables, exact
counting by variable elimination, tree decompositions, softened weight polynomials, and controls."""
import itertools, math
from collections import Counter, defaultdict
cube = list(itertools.product((0, 1), repeat=3))
PAR = frozenset(s for s in cube if sum(s) % 2 == 0)
NAE = frozenset(cube) - {(0, 0, 0), (1, 1, 1)}
TW1 = frozenset(cube) - {(0, 1, 1), (1, 0, 0)}   # twisted NAE, first coordinate the odd one
TW2 = frozenset(cube) - {(0, 1, 0), (1, 0, 1)}   # twisted NAE, second coordinate the odd one
FANO_LINES = [(0, 1, 3), (0, 4, 5), (0, 2, 6), (1, 2, 4), (2, 3, 5), (3, 4, 6), (1, 5, 6)]
# a gadget: (name, hidden names, copies as (ordered triple of names, allowed set)); legs are "a", "b", "c"
TRIANGLE = ("parity triangle", ["d", "e", "f"], [(("a", "d", "e"), PAR), (("b", "d", "f"), PAR), (("c", "e", "f"), PAR)])
TETRA = ("twisted not-all-equal tetrahedron", ["d", "e", "f"],
         [(("a", "d", "e"), TW1), (("b", "d", "f"), TW1), (("c", "e", "f"), TW2), (("d", "e", "f"), TW1)])
FANO = ("not-all-equal Fano plane", ["p1", "p2", "p3", "p4", "p5", "p6"],
        [(("a", "p1", "p3"), NAE), (("b", "p4", "p5"), NAE), (("c", "p2", "p6"), NAE)]
        + [(tuple("p%d" % i for i in ln), NAE) for ln in FANO_LINES[3:]])
def relation_counts(g):
    name, hid, cops = g
    cnt = Counter()
    for t in cube:
        for h in itertools.product((0, 1), repeat=len(hid)):
            val = dict(zip("abc", t)); val.update(zip(hid, h))
            if all(tuple(val[v] for v in vs) in Q for vs, Q in cops): cnt[t] += 1
    return cnt
def transported(R, sigma):
    """the relation on (u,v,w) imposed by legs a, b, c placed at positions sigma[0], sigma[1], sigma[2]"""
    return frozenset(x for x in cube if (x[sigma[0]], x[sigma[1]], x[sigma[2]]) in R)
class Tower:
    """level-k network: copies (variable ids, allowed set), hierarchy nodes with bags"""
    def __init__(self, g, R0):
        self.g = g
        name, hid, cops = g
        cnt = relation_counts(g)
        self.R = frozenset(t for t in cube if cnt[t])
        self.c = {cnt[t] for t in self.R}
        self.copies = [((0, 1, 2), R0)]
        self.nvars = 3
        self.node_of_copy = [None]       # hierarchy node that created each current copy (None for the root copy)
        self.nodes = []                  # (parent node, bag)
        self.level = 0
    def substitute(self):
        name, hid, cops = self.g
        new, new_node = [], []
        for (vs, Q), parent in zip(self.copies, self.node_of_copy):
            sigma = next(s for s in itertools.permutations(range(3)) if transported(self.R, s) == Q)
            ids = {"a": vs[sigma[0]], "b": vs[sigma[1]], "c": vs[sigma[2]]}
            for h in hid:
                ids[h] = self.nvars; self.nvars += 1
            node = len(self.nodes)
            self.nodes.append((parent, frozenset(ids.values())))
            for cvs, P in cops:
                new.append((tuple(ids[x] for x in cvs), P)); new_node.append(node)
        self.copies, self.node_of_copy = new, new_node
        self.level += 1
    def adjacency(self):
        adj = [set() for _ in range(self.nvars)]
        for vs, Q in self.copies:
            for u in vs:
                for v in vs:
                    if u != v: adj[u].add(v)
        return adj
def bfs(adj, src, banned=frozenset()):
    d = {src: 0}; q = [src]
    for u in q:
        for w in adj[u]:
            if w not in d and w not in banned: d[w] = d[u] + 1; q.append(w)
    return d
def count_by_elimination(nvars, copies, corners=(0, 1, 2)):
    """exact counts of solutions per corner tuple by variable elimination, Python integers; variables are eliminated newest first
    (the finest sub-gadgets first), which keeps every intermediate factor on at most h + 2 variables"""
    factors = [(tuple(vs), {s: 1 for s in Q}) for vs, Q in copies]
    holders = defaultdict(set)
    for i, (vs, tab) in enumerate(factors):
        for v in vs: holders[v].add(i)
    live = set(range(len(factors)))
    for v in sorted((x for x in range(nvars) if x not in corners), reverse=True):
        inv = [factors[i] for i in holders[v] if i in live]
        for i in holders[v]: live.discard(i)
        scope = sorted(set().union(*[set(f[0]) for f in inv]) - {v})
        tab = {}
        for x in itertools.product((0, 1), repeat=len(scope)):
            asg = dict(zip(scope, x)); tot = 0
            for b in (0, 1):
                asg[v] = b; prod = 1
                for fvs, ftab in inv:
                    prod *= ftab.get(tuple(asg[u] for u in fvs), 0)
                    if not prod: break
                tot += prod
            if tot: tab[x] = tot
        factors.append((tuple(scope), tab))
        j = len(factors) - 1
        live.add(j)
        for u in scope: holders[u].add(j)
    out = Counter()
    for t in cube:
        asg = dict(zip(corners, t)); prod = 1
        for i in live:
            fvs, ftab = factors[i]
            prod *= ftab.get(tuple(asg[u] for u in fvs), 0)
        out[t] = prod
    return out
def check_tree_decomposition(tw):
    """bags of the hierarchy nodes; every copy inside the bag of the node that created it; each variable's nodes form a subtree"""
    nodes = tw.nodes
    cover = all(set(vs) <= nodes[nd][1] for (vs, Q), nd in zip(tw.copies, tw.node_of_copy))
    children = defaultdict(list)
    for i, (par, bag) in enumerate(nodes):
        if par is not None: children[par].append(i)
    holders = defaultdict(list)
    for i, (par, bag) in enumerate(nodes):
        for v in bag: holders[v].append(i)
    connected = True
    for v, hs in holders.items():
        hs = set(hs)
        # a set of tree nodes is connected iff exactly one of them has its parent outside the set
        tops = [i for i in hs if nodes[i][0] is None or nodes[i][0] not in hs]
        connected &= len(tops) == 1
    width = max(len(bag) for par, bag in nodes) - 1
    return cover, connected, width
def check_separators(tw, sample=None):
    """for every hierarchy node: deleting its three corners separates the variables it introduced (and below) from the rest"""
    nodes = tw.nodes
    adj = tw.adjacency()
    children = defaultdict(list)
    for i, (par, bag) in enumerate(nodes):
        if par is not None: children[par].append(i)
    # corners of a node = the variables of the copy it replaced = bag minus the hidden it introduced; recover by levels
    introduced = {}
    seen = set(range(3))
    order = list(range(len(nodes)))
    for i in order:
        par, bag = nodes[i]
        introduced[i] = set(bag) - seen if False else None
    # simpler: interior(i) = union of bags of the subtree minus corners(i); corners(i) = bag(i) ∩ bag(parent) for non-root
    def subtree(i):
        st, out = [i], []
        while st:
            u = st.pop(); out.append(u); st.extend(children[u])
        return out
    ok = True; tested = 0
    idx = range(len(nodes)) if sample is None else sample
    for i in idx:
        par, bag = nodes[i]
        corners = set(bag) & set(nodes[par][1]) if par is not None else set(range(3))
        if len(corners) != 3: ok = False; continue
        inner = set().union(*[set(nodes[u][1]) for u in subtree(i)]) - corners
        if not inner: continue
        start = next(iter(inner))
        reach = bfs(adj, start, banned=frozenset(corners))
        ok &= set(reach) == inner or (par is None and set(reach) <= inner | set())
        tested += 1
    return ok, tested
# --- integer polynomials (coefficient lists, lowest degree first) ---
def _trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0: p.pop()
    return p
def _padd(p, q):
    n = max(len(p), len(q)); return _trim([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])
def _pneg(p): return [-x for x in p]
def _pmul(p, q):
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q): out[i + j] += a * b
    return _trim(out)
def _pprod(*ps):
    out = [1]
    for p in ps: out = _pmul(out, p)
    return out
def _peval(p, x): return sum(c * x ** i for i, c in enumerate(p))
import types as _types
P = _types.SimpleNamespace(padd=_padd, pneg=_pneg, pmul=_pmul, pprod=_pprod, peval=_peval, R=[0, 1], lin=lambda a, b: [b, a])
def soft_polys(g):
    """for each leg tuple, the polynomial sum over hidden assignments of r^(number of violated copies)"""
    name, hid, cops = g
    W = {}
    for t in cube:
        coef = [0] * (len(cops) + 1)
        for h in itertools.product((0, 1), repeat=len(hid)):
            val = dict(zip("abc", t)); val.update(zip(hid, h))
            coef[sum(1 for vs, Q in cops if tuple(val[v] for v in vs) not in Q)] += 1
        W[t] = _trim(coef)
    return W
# --- controls ---
def drift_control():
    """x or (y != z): the four-copy rebuilding gadget (legs a, b with hub d; two parallel copies on (d, e, f); leg c with e, f) has
    non-uniform counts, and its tower's corner law changes from level 1 to level 2"""
    K = frozenset(cube) - {(0, 0, 0), (0, 1, 1)}
    PL = sorted({frozenset(tuple(s[p[i]] for i in range(3)) for s in K) for p in itertools.permutations(range(3))}, key=sorted)
    slots = [("a", "b", "d"), ("c", "e", "f"), ("d", "e", "f"), ("d", "e", "f")]
    for choice in itertools.product(range(3), repeat=4):
        g = ("x or (y != z) four copies", ["d", "e", "f"], [(slots[i], PL[choice[i]]) for i in range(4)])
        cnt = relation_counts(g)
        R = frozenset(t for t in cube if cnt[t])
        if R in set(PL) and len({cnt[t] for t in R}) > 1:
            excl = sorted(set(cube) - R)
            far = [t for t in sorted(R) if all(sum(x != y for x, y in zip(t, e)) >= 2 for e in excl)]
            tw = Tower(g, R)
            laws, shares = [], []
            for k in (1, 2, 3):
                tw.substitute()
                cc = count_by_elimination(tw.nvars, tw.copies)
                tot = sum(cc.values())
                laws.append({str(t): str(Fraction(cc[t], tot)) for t in sorted(R)})
                shares.append(Fraction(sum(cc[t] for t in far), tot))
            return {"placements": [sorted(set(cube) - PL[q]) for q in choice], "level-1 counts": {str(t): cnt[t] for t in sorted(R)},
                    "corner law level 1": laws[0], "corner law level 2": laws[1], "changes": laws[0] != laws[1],
                    "tuples far from both excluded tuples": far, "their share at levels 1, 2, 3": [round(float(x), 6) for x in shares],
                    "share increases": shares[0] < shares[1] < shares[2]}
    return {"changes": False}
from fractions import Fraction
def shared_midpoint_control(side=4):
    """the triangular grid of the given side (midpoints shared between neighbouring triangles): deleting the three corners of the
    corner sub-triangle of half the side does not cut off its other vertices"""
    V = [(i, j) for i in range(side + 1) for j in range(side + 1 - i)]
    idx = {v: n for n, v in enumerate(V)}
    tris = []
    for i in range(side):
        for j in range(side - i):
            tris.append(((i, j), (i + 1, j), (i, j + 1)))
            if i + j + 2 <= side: tris.append(((i + 1, j), (i, j + 1), (i + 1, j + 1)))
    adj = [set() for _ in V]
    for t in tris:
        for u in t:
            for w in t:
                if u != w: adj[idx[u]].add(idx[w])
    half = side // 2
    corners = {idx[(0, 0)], idx[(half, 0)], idx[(0, half)]}
    inside = {idx[(i, j)] for i in range(half + 1) for j in range(half + 1 - i)} - corners
    start = next(iter(inside))
    reach = set(bfs(adj, start, banned=frozenset(corners)))
    return {"side": side, "triangles": len(tris), "sub-triangle vertices besides corners": len(inside),
            "reached outside after deleting corners": len(reach - inside), "not cut off": bool(reach - inside)}
def mutated_fano_control():
    """replace the line (p1, p5, p6) of the punctured Fano gadget by (p1, p4, p6): the relation or the counts change"""
    name, hid, cops = FANO
    mcops = [c for c in cops if c[0] != ("p1", "p5", "p6")] + [(("p1", "p4", "p6"), NAE)]
    cnt = relation_counts((name, hid, mcops))
    R = frozenset(t for t in cube if cnt[t])
    exact = R == NAE and len({cnt[t] for t in R}) == 1
    return {"relation excluded": sorted(set(cube) - R), "counts": sorted({cnt[t] for t in R}), "not exact": not exact}
def leg_conditions(g, s):
    """every variable within s of each leg; every copy holds a variable within s - 1 of each leg"""
    name, hid, cops = g
    names = ["a", "b", "c"] + list(hid)
    adj = {x: set() for x in names}
    for vs, Q in cops:
        for u in vs:
            for v in vs:
                if u != v: adj[u].add(v)
    def dist(src):
        d = {src: 0}; q = [src]
        for u in q:
            for w in adj[u]:
                if w not in d: d[w] = d[u] + 1; q.append(w)
        return d
    ds = {l: dist(l) for l in "abc"}
    within = all(max(ds[l].values()) <= s and len(ds[l]) == len(names) for l in "abc")
    copies_ok = all(min(ds[l][x] for x in vs) <= s - 1 for l in "abc" for vs, Q in cops)
    return within, copies_ok
