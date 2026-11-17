"""Library for STATE-RULES-20261117-001B-E001: growth by uniform rules that read only the allowed states.

A base is a set of allowed states (bitmasks) over distinctions 0..n-1.  It is built from betweenness knots B(a, b, c), which
exclude 010 and 101 on (a, b, c), so it is complement-closed and holds both constant states.

A step adds distinction n with 1 to K knots, each a betweenness knot on a triple containing n, in one of three roles:
- B(u, n, v): n between u and v;
- B(u, v, n): v between u and n;
- B(v, u, n): u between v and n.

An extension is the state set the knots leave.  Two knot sets that leave the same states are the same extension.  Extensions are
admitted when:
- every old state still extends (the old base is the new one's restriction);
- the new distinction is constrained (N' < 2N);
- it is not tied to an old distinction (equal to it in every state).

The rule sees only the states, with the distinctions renamed at random before each read.  It weights the admitted extensions by
their state counts N' alone: fewest, uniform, or a softmax of the excess over the fewest.  It then picks one, ties uniformly.

The reading of a grown base is its split system, the non-constant states up to flipping:
- k: the chromatic number of the splits' crossing graph (the least number of trees);
- lam: the least number of chains of nested splits, that is the least number of lines whose product holds the distinctions with
  the disagreement count as twice the L1 distance (Eppstein's lattice dimension), computed as s - nu(semicube graph)."""
import collections
import itertools
import math
import random

import networkx as nx

BTW = ((0, 1, 0), (1, 0, 1))
pc = int.bit_count


# ---------- bases ----------

def base_from_knots(n, knots):
    return sorted(s for s in range(1 << n) if all(tuple((s >> x) & 1 for x in k) not in BTW for k in knots))


def extend_brute(states, n, knots):
    """Reference: states after adding distinction n with the given knots, by direct evaluation."""
    out = []
    for s in states:
        for b in (0, 1):
            t = s | (b << n)
            if all(tuple((t >> x) & 1 for x in k) not in BTW for k in knots):
                out.append(t)
    return sorted(out)


def relabel(states, n, perm):
    """perm[i] = new name of distinction i."""
    return sorted(sum(((s >> i) & 1) << perm[i] for i in range(n)) for s in states)


def columns(states, n):
    """Z[u], O[u]: bitmasks over state indices where distinction u is 0, 1."""
    Z, O = [0] * n, [0] * n
    for i, s in enumerate(states):
        for u in range(n):
            if (s >> u) & 1:
                O[u] |= 1 << i
            else:
                Z[u] |= 1 << i
    return Z, O


def knot_masks(states, n):
    """Each single knot containing n as (knot, A0, A1): bit i of A0 (A1) set when old state i allows n = 0 (1)."""
    full = (1 << len(states)) - 1
    Z, O = columns(states, n)
    out = []
    for u, v in itertools.combinations(range(n), 2):
        eq = (Z[u] & Z[v]) | (O[u] & O[v])
        ne = full ^ eq
        out.append(((u, n, v), ne | (Z[u] & Z[v]), ne | (O[u] & O[v])))   # forced to u's value where u = v
        out.append(((u, v, n), eq | (ne & Z[v]), eq | (ne & O[v])))        # forced to v's value where u != v
        out.append(((v, u, n), eq | (ne & Z[u]), eq | (ne & O[u])))        # forced to u's value where u != v
    return out, Z, O


def extensions(states, n, K):
    """Admitted extensions with up to K knots: {(A0, A1): fewest-knot set found first}."""
    masks, Z, O = knot_masks(states, n)
    N = len(states)
    full = (1 << N) - 1
    ties = {(Z[u], O[u]) for u in range(n)}
    found = {}

    def offer(A0, A1, ks):
        if (A0, A1) in found or (A0, A1) in ties or pc(A0) + pc(A1) >= 2 * N:
            return
        found[(A0, A1)] = ks

    m = len(masks)
    for i in range(m):
        ki, a0, a1 = masks[i]
        offer(a0, a1, (ki,))
    if K >= 2:
        for i in range(m):
            ki, a0, a1 = masks[i]
            for j in range(i + 1, m):
                kj, b0, b1 = masks[j]
                c0, c1 = a0 & b0, a1 & b1
                if (c0 | c1) != full:          # an old state dies; every superset kills it too
                    continue
                offer(c0, c1, (ki, kj))
                if K >= 3:
                    for l in range(j + 1, m):
                        kl, d0, d1 = masks[l]
                        e0, e1 = c0 & d0, c1 & d1
                        if (e0 | e1) == full:
                            offer(e0, e1, (ki, kj, kl))
    return found


def apply(states, n, A0, A1):
    out = []
    for i, s in enumerate(states):
        if (A0 >> i) & 1:
            out.append(s)
        if (A1 >> i) & 1:
            out.append(s | (1 << n))
    return sorted(out)


SEEDS = {
    "line": (3, [(0, 1, 2)]),
    "2x2": (4, [(0, 1, 3), (0, 2, 3), (1, 0, 2), (1, 3, 2)]),     # cells 0=(0,0), 1=(1,0), 2=(0,1), 3=(1,1): box triples
    "star": (4, [(1, 0, 2), (1, 0, 3), (2, 0, 3)]),               # distinction 0 between every two leaves
    "fan6": (6, [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)]),   # a line of six; distinction 0 in all four knots
    "nonfan6": (6, [(1, 2, 3), (1, 3, 4), (4, 1, 0), (0, 4, 5)]),  # the same twelve states; no distinction in all four
}


def seed(name):
    n, knots = SEEDS[name]
    return n, base_from_knots(n, knots)


# ---------- weightings ----------

def weights(sizes, rule, beta=None):
    low, high = min(sizes), max(sizes)
    if rule == "fewest":
        return [1.0 if x == low else 0.0 for x in sizes]
    if rule == "uniform":
        return [1.0] * len(sizes)
    if rule == "softmax":
        return [math.exp(-beta * (x - low)) for x in sizes]
    raise ValueError(rule)


def options(states, n, rule, K, beta=None, count="extensions", canon=None):
    """[(weight, new states, knots)] over the admitted extensions, weights summing to 1.  With count="classes" each class of
    outcome (up to renaming) counts once: the rule's weight goes to classes, then uniformly to the extensions in each."""
    ext = extensions(states, n, K)
    items = list(ext.items())
    if not items:
        return []
    sizes = [pc(a0) + pc(a1) for (a0, a1), _ in items]
    built = [apply(states, n, a0, a1) for (a0, a1), _ in items]
    w = weights(sizes, rule, beta)
    if count == "classes":
        cls = [canon.cid(b, n + 1) for b in built]
        members = collections.Counter(c for c, wi in zip(cls, w) if wi > 0)
        first = {}
        for c, wi in zip(cls, w):
            if wi > 0:
                first.setdefault(c, wi)
        w = [first[c] / members[c] if wi > 0 else 0.0 for c, wi in zip(cls, w)]
    tot = sum(w)
    return [(wi / tot, b, ks) for wi, b, (_, ks) in zip(w, built, items) if wi > 0]


def step(states, n, rule, K, rng, beta=None, canon=None, count="extensions"):
    """One blind step.  Returns (new states, knots, record).  The record says how many inequivalent bases share the top weight."""
    perm = list(range(n))
    rng.shuffle(perm)
    blind = relabel(states, n, perm)                       # the rule's only input
    opts = options(blind, n, rule, K, beta, count, canon)
    if not opts:
        return None, None, {"options": 0}
    top = max(w for w, _, _ in opts)
    rec = {"options": len(opts), "N": len(blind)}
    if canon is not None:
        tops = [o for w, o, _ in opts if w >= top * (1 - 1e-12)]
        rec["top_options"] = len(tops)
        rec["top_classes"] = len({canon.cid(o, n + 1) for o in tops})
    r = rng.random()
    acc = 0.0
    for w, o, ks in opts:
        acc += w
        if r < acc:
            return o, ks, rec
    return opts[-1][1], opts[-1][2], rec


def grow(rule, K, start, nmax, seed_value, beta=None, canon=None, measure_every=True, count="extensions"):
    rng = random.Random(seed_value)
    n, states = seed(start)
    trace = [{"n": n, **measure(states, n)}]
    while n < nmax:
        new, ks, rec = step(states, n, rule, K, rng, beta, canon, count)
        if new is None:
            trace.append({"n": n + 1, "stopped": "no admitted extension"})
            break
        states, n = new, n + 1
        row = {"n": n, "knots": len(ks), **rec}
        if measure_every or n == nmax:
            row.update(measure(states, n))
        trace.append(row)
    return states, n, trace


# ---------- reading the grown base ----------

def splits(states, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in states if s not in (0, full)})


def crosses(a, b, full):
    return bool(a & b) and bool(a & (full ^ b)) and bool((full ^ a) & b) and bool((full ^ a) & (full ^ b))


def colourable(nv, adj, k):
    order = sorted(range(nv), key=lambda v: -len(adj[v]))
    col = {}

    def bt(i):
        if i == nv:
            return True
        v = order[i]
        used = {col[w] for w in adj[v] if w in col}
        for c in range(k):
            if c not in used:
                col[v] = c
                if bt(i + 1):
                    return True
                del col[v]
        return False
    return bt(0)


def lattice_dimension(sp, full):
    """Least number of chains of nested oriented splits covering sp: s - nu(semicube graph)."""
    G = nx.Graph()
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    G.add_nodes_from(range(len(sides)))
    for p, q in itertools.combinations(range(len(sides)), 2):
        (i, x), (j, y) = sides[p], sides[q]
        if i != j and (x | y) == full:
            G.add_edge(p, q)
    return len(sp) - len(nx.max_weight_matching(G, maxcardinality=True))


def lattice_dimension_brute(sp, full):
    """Reference: try every orientation and every chain partition (small s only)."""
    s = len(sp)
    if s == 0:
        return 0
    best = s
    for orient in range(1 << s):
        sides = [sp[i] if not (orient >> i) & 1 else full ^ sp[i] for i in range(s)]
        # with fixed orientations, chains are chains of the inclusion order: Dilworth by matching
        G = nx.DiGraph()
        B = nx.Graph()
        B.add_nodes_from([("a", i) for i in range(s)] + [("b", i) for i in range(s)])
        for i in range(s):
            for j in range(s):
                if i != j and (sides[i] & sides[j]) == sides[i] and sides[i] != sides[j]:
                    B.add_edge(("a", i), ("b", j))
        mt = nx.bipartite.maximum_matching(B, top_nodes=[("a", i) for i in range(s)])
        best = min(best, s - len(mt) // 2)
    return best


def measure(states, n, k_limit=4):
    sp = splits(states, n)
    full = (1 << n) - 1
    s = len(sp)
    adj = [set() for _ in range(s)]
    crossings = 0
    for i, j in itertools.combinations(range(s), 2):
        if crosses(sp[i], sp[j], full):
            adj[i].add(j)
            adj[j].add(i)
            crossings += 1
    if crossings == 0:
        k = 1
    elif nx.is_bipartite(nx.Graph([(i, j) for i in range(s) for j in adj[i]])):
        k = 2
    elif s <= 24:
        k = next((kk for kk in range(3, k_limit + 1) if colourable(s, adj, kk)), None)
    else:
        k = None
    k_text = str(k) if k is not None else (f">{k_limit}" if s <= 24 else ">=3")
    lam = lattice_dimension(sp, full)
    cube = s > 0 and n == 2 ** s
    return {"N": len(states), "splits": s, "crossings": crossings, "k": k_text, "lam": lam, "points_per_split": n / s if s else None,
            "line": lam == 1 and len(states) == 2 * n, "tree": k == 1, "two_way": k == 2 and lam == 2,
            "cube": cube, "kind": kind(k, lam, len(states), n, cube)}


def kind(k, lam, N, n, cube):
    if lam == 1:
        return "a line"
    if k == 1:
        return "a branching tree"
    if k == 2 and lam == 2:
        return "two orders"
    if cube:
        return f"a cube of {lam} orders"
    return f"{lam} orders"


# ---------- isomorphism classes ----------

class Canon:
    """Classes of bases up to renaming, by isomorphism of the incidence graph of distinctions and split sides.  A cheap invariant
    (the sorted rows of disagreement counts and the split sizes) buckets them first; graphs are built only within a bucket."""

    def __init__(self):
        self.buckets = {}
        self.reps = []

    @staticmethod
    def invariant(states, n, knots=None):
        Z, O = columns(states, n)
        rows = tuple(sorted(tuple(sorted(pc(Z[u] & O[v]) + pc(O[u] & Z[v]) for v in range(n))) for u in range(n)))
        sizes = tuple(sorted(min(pc(a), n - pc(a)) for a in splits(states, n)))
        kd = None
        if knots is not None:
            kd = tuple(sorted((sum(x in k for k in knots), sum(k[1] == x for k in knots)) for x in range(n)))
        return (n, len(states), rows, sizes, kd)

    @staticmethod
    def graph(states, n, knots=None):
        """The complete graph on the distinctions weighted by the disagreement count, plus a node per knot joined to its three
        distinctions by its roles.  For n >= 4 the counts and N determine a base of betweenness knots
        (DISTANCE-ORDER-20261117-001A, statement 3(a)), and N is in the bucket key, so isomorphism of these graphs is
        isomorphism of the bases.  (Amendment 2: this replaces the incidence graph of distinctions and split sides, on which the
        isomorphism search blew up exponentially; the classes are the same.)"""
        Z, O = columns(states, n)
        G = nx.Graph()
        for x in range(n):
            G.add_node(("p", x), kind="p")
        for u, v in itertools.combinations(range(n), 2):
            G.add_edge(("p", u), ("p", v), role=pc(Z[u] & O[v]) + pc(O[u] & Z[v]))
        for j, k in enumerate(sorted(set(knots or []))):
            G.add_node(("k", j), kind="k")
            for pos, x in enumerate(k):
                G.add_edge(("k", j), ("p", x), role="middle" if pos == 1 else "outer")
        return G

    def cid(self, states, n, knots=None):
        h = self.invariant(states, n, knots)
        bucket = self.buckets.setdefault(h, [])
        if bucket:
            G = self.graph(states, n, knots)
            nm = lambda a, b: a["kind"] == b["kind"]
            em = lambda a, b: a.get("role") == b.get("role")
            for entry in bucket:
                if entry[2] is None:
                    entry[2] = self.graph(*self.reps[entry[0]])
                if nx.is_isomorphic(G, entry[2], node_match=nm, edge_match=em):
                    return entry[0]
        c = len(self.reps)
        self.reps.append((tuple(states), n, tuple(sorted(knots)) if knots is not None else None))
        bucket.append([c, None, None])
        return c


def exact(rule, K, start, nmax, beta=None, canon=None, count="extensions"):
    """Exact distribution over classes at each n, from a start, ties and weights as in options()."""
    canon = canon or Canon()
    n, states = seed(start)
    dist = {canon.cid(states, n): 1.0}
    levels = []
    while True:
        rows = []
        for c, p in sorted(dist.items()):
            st, nn, _ = canon.reps[c]
            rows.append((c, p, measure(list(st), nn)))
        levels.append({"n": n, "classes": len(dist), "dist": rows})
        if n >= nmax:
            break
        new = {}
        determined = 0.0
        for c, p in dist.items():
            st, nn, _ = canon.reps[c]
            opts = options(list(st), nn, rule, K, beta, count, canon)
            top = max(w for w, _, _ in opts)
            tops = set()
            for w, o, _ in opts:
                d = canon.cid(o, nn + 1)
                new[d] = new.get(d, 0.0) + p * w
                if w >= top * (1 - 1e-12):
                    tops.add(d)
            if len(tops) == 1:
                determined += p
        levels[-1]["determined_next"] = determined
        dist = new
        n += 1
    return levels, canon


# ---------- the knot arm: bases that keep their knots ----------

def local_pairs(knots):
    return {(min(a, b), max(a, b)) for k in knots for a, b in itertools.combinations(k, 2)}


def valid_pairs(states, n):
    """Pairs lying together in some betweenness triple that every state satisfies (a function of the states alone)."""
    S = set(states)
    out = set()
    for x, y, z in itertools.permutations(range(n), 3):
        if all(not (((s >> x) & 1) == ((s >> z) & 1) != ((s >> y) & 1)) for s in S):
            out |= {(min(x, y), max(x, y)), (min(x, z), max(x, z)), (min(y, z), max(y, z))}
    return out


def knot_moves(states, n, knots, K, local="knot"):
    """Irredundant sets of 1..K knots containing n, admitted as in extensions().  Distinct knot sets are distinct moves.
    local: "knot" (each knot's two old distinctions lie together in one existing knot), "strict" (all the move's old
    distinctions lie in one existing knot), "closure" (each knot's old pair lies in a betweenness triple every state satisfies:
    a function of the states, the control), or None.  Returns [(A0, A1, knots)]."""
    masks, Z, O = knot_masks(states, n)
    old_pair = lambda m: tuple(sorted(x for x in m[0] if x != n))
    if local == "knot":
        lp = local_pairs(knots)
        masks = [m for m in masks if old_pair(m) in lp]
    elif local == "closure":
        lp = valid_pairs(states, n)
        masks = [m for m in masks if old_pair(m) in lp]
    elif local == "strict":
        lp = local_pairs(knots)
        masks = [m for m in masks if old_pair(m) in lp]
        homes = [set(k) for k in knots]
        inside = lambda ks: any(all(set(x for x in k if x != n) <= h for k in ks) for h in homes)
    N = len(states)
    full = (1 << N) - 1
    ties = {(Z[u], O[u]) for u in range(n)}
    ok = lambda a0, a1: (a0, a1) not in ties and pc(a0) + pc(a1) < 2 * N
    if local != "strict":
        inside = lambda ks: True
    out = []
    m = len(masks)
    for i in range(m):
        ki, a0, a1 = masks[i]
        if ok(a0, a1) and inside((ki,)):
            out.append((a0, a1, (ki,)))
        if K < 2:
            continue
        for j in range(i + 1, m):
            kj, b0, b1 = masks[j]
            c0, c1 = a0 & b0, a1 & b1
            if (c0 | c1) != full:
                continue
            if (c0, c1) not in ((a0, a1), (b0, b1)) and ok(c0, c1) and inside((ki, kj)):
                out.append((c0, c1, (ki, kj)))
            if K < 3:
                continue
            for l in range(j + 1, m):
                kl, d0, d1 = masks[l]
                e0, e1 = c0 & d0, c1 & d1
                if (e0 | e1) != full or not ok(e0, e1):
                    continue
                if (e0, e1) in ((c0, c1), (a0 & d0, a1 & d1), (b0 & d0, b1 & d1)) or not inside((ki, kj, kl)):
                    continue
                out.append((e0, e1, (ki, kj, kl)))
    return out


def relabel_knots(knots, perm):
    return sorted(tuple(perm[x] for x in k) for k in knots)


def knot_step(states, n, knots, rule, K, rng, canon=None, local="knot"):
    """One blind step of the knot arm: the rule reads the states and the knots, renamed at random."""
    perm = list(range(n))
    rng.shuffle(perm)
    blind, bknots = relabel(states, n, perm), relabel_knots(knots, perm)
    moves = knot_moves(blind, n, bknots, K, local)
    if not moves:
        return None, None, None, {"options": 0}
    sizes = [pc(a0) + pc(a1) for a0, a1, _ in moves]
    w = weights(sizes, rule)
    tot = sum(w)
    rec = {"options": len(moves), "N": len(blind)}
    if canon is not None:
        top = max(w)
        tops = [mv for mv, wi in zip(moves, w) if wi >= top * (1 - 1e-12)]
        rec["top_options"] = len(tops)
        rec["top_classes"] = len({canon.cid(apply(blind, n, a0, a1), n + 1, bknots + list(ks)) for a0, a1, ks in tops})
    r = rng.random() * tot
    acc = 0.0
    for (a0, a1, ks), wi in zip(moves, w):
        acc += wi
        if r < acc:
            break
    return apply(blind, n, a0, a1), bknots + list(ks), ks, rec


def knot_grow(rule, K, start, nmax, seed_value, canon=None, local="knot"):
    rng = random.Random(seed_value)
    n, knots = SEEDS[start][0], list(SEEDS[start][1])
    states = base_from_knots(n, knots)
    trace = [{"n": n, **measure(states, n)}]
    while n < nmax:
        new, nk, ks, rec = knot_step(states, n, knots, rule, K, rng, canon, local)
        if new is None:
            trace.append({"n": n + 1, "stopped": "no admitted move"})
            break
        states, knots, n = new, nk, n + 1
        trace.append({"n": n, "knots": len(ks), "most_knots_on_one": max(collections.Counter(x for k in knots for x in k).values()),
                      **rec, **measure(states, n)})
    return states, knots, n, trace


# ---------- a single continuation that respects every symmetry ----------

def signed_symmetries(states, n):
    S = set(states)
    out = []
    for perm in itertools.permutations(range(n)):
        for flip in range(1 << n):
            img = {sum(((((s >> i) & 1) ^ ((flip >> i) & 1)) << perm[i]) for i in range(n)) for s in states}
            if img == S:
                out.append((perm, flip))
    return out


def invariant_continuations(states, n, group="signed"):
    """Every continuation (each old state allows new = 0, 1 or both) invariant under every signed symmetry of the base, the new bit
    allowed to flip.  Returns [(choice tuple, kind)], kind: fixed (new constant), free, tie (a copy of an old distinction or its
    flip), or open (otherwise)."""
    syms = signed_symmetries(states, n)
    if group == "complement":
        syms = [(p, f) for p, f in syms if f in (0, (1 << n) - 1)]
    out = []
    for choice in itertools.product((0, 1, 2), repeat=len(states)):
        cont = {(s, b) for s, c in zip(states, choice) for b in ((0, 1) if c == 2 else (c,))}
        good = True
        for perm, flip in syms:
            img = {(sum(((((s >> i) & 1) ^ ((flip >> i) & 1)) << perm[i]) for i in range(n)), b) for s, b in cont}
            if img != cont and {(t, 1 - b) for t, b in img} != cont:
                good = False
                break
        if not good:
            continue
        vals = {b for _, b in cont}
        if len(vals) == 1:
            kind = "fixed"
        elif all(c == 2 for c in choice):
            kind = "free"
        elif all(c != 2 for c in choice) and any(all(((s >> u) & 1) == b for s, b in cont) or
                                                 all(((s >> u) & 1) != b for s, b in cont) for u in range(n)):
            kind = "tie"
        else:
            kind = "open"
        out.append((choice, kind))
    return out


def knot_exact(rule, K, start, nmax, local="knot", canon=None):
    """Exact distribution over classes of (states, knots) at each n."""
    canon = canon or Canon()
    n, knots = SEEDS[start][0], list(SEEDS[start][1])
    states = base_from_knots(n, knots)
    dist = {canon.cid(states, n, knots): 1.0}
    levels = []
    while True:
        rows = []
        for c, p in sorted(dist.items()):
            st, nn, kk = canon.reps[c]
            rows.append((c, p, measure(list(st), nn)))
        levels.append({"n": n, "classes": len(dist), "dist": rows})
        if n >= nmax:
            break
        new, determined = {}, 0.0
        for c, p in dist.items():
            st, nn, kk = canon.reps[c]
            moves = knot_moves(list(st), nn, list(kk), K, local)
            w = weights([pc(a0) + pc(a1) for a0, a1, _ in moves], rule)
            tot, top = sum(w), max(w)
            tops = set()
            for (a0, a1, ks), wi in zip(moves, w):
                if wi == 0:
                    continue
                d = canon.cid(apply(list(st), nn, a0, a1), nn + 1, list(kk) + list(ks))
                new[d] = new.get(d, 0.0) + p * wi / tot
                if wi >= top * (1 - 1e-12):
                    tops.add(d)
            if len(tops) == 1:
                determined += p
        levels[-1]["determined_next"] = determined
        dist = new
        n += 1
    return levels, canon


def invariant_knot_extensions(states, n, K, group="signed"):
    """Admitted betweenness-knot extensions (up to K knots) invariant under the base's symmetries, the new bit allowed to flip.
    group: "signed" (permutations with any flips) or "complement" (permutations with no flip or the global flip)."""
    syms = signed_symmetries(states, n)
    full = (1 << n) - 1
    if group == "complement":
        syms = [(p, f) for p, f in syms if f in (0, full)]
    out = []
    for a0, a1 in extensions(states, n, K):
        cont = {(s, 0) for i, s in enumerate(states) if (a0 >> i) & 1} | {(s, 1) for i, s in enumerate(states) if (a1 >> i) & 1}
        good = True
        for perm, flip in syms:
            img = {(sum(((((s >> i) & 1) ^ ((flip >> i) & 1)) << perm[i]) for i in range(n)), b) for s, b in cont}
            if img != cont and {(t, 1 - b) for t, b in img} != cont:
                good = False
                break
        if good:
            out.append(len(cont))
    return out
