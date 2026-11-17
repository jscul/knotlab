"""Controls for rules.py, run before the freeze: the mask form against direct evaluation, the lattice dimension against brute force,
known shapes, the zero-cost fill, and blindness of the scores."""
import itertools
import random
import sys

import rules as R

rng = random.Random("STATE-RULES checks")
fails = 0


def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    fails += not ok


# 1. mask extensions equal direct evaluation, on random bases from random knots
bad = 0
for trial in range(300):
    n = rng.randint(3, 7)
    knots = []
    for _ in range(rng.randint(1, 2 * n)):
        t = rng.sample(range(n), 3)
        knots.append(tuple(t))
    st = R.base_from_knots(n, knots)
    if len(st) < 2:
        continue
    masks, Z, O = R.knot_masks(st, n)
    for _ in range(5):
        pick = rng.sample(masks, rng.randint(1, 3))
        A0 = A1 = (1 << len(st)) - 1
        for _, a0, a1 in pick:
            A0 &= a0
            A1 &= a1
        if R.apply(st, n, A0, A1) != R.extend_brute(st, n, [k for k, _, _ in pick]):
            bad += 1
check("mask form = direct evaluation (1,500 random knot sets)", bad == 0, f"{bad} mismatches")

# 2. extensions() admits exactly the conservative, constrained, untied extensions (brute force over knot sets, small n)
bad = 0
for trial in range(40):
    n = rng.randint(3, 5)
    st = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, n))])
    if len(st) < 2:
        continue
    ext = R.extensions(st, n, 3)
    got = {tuple(R.apply(st, n, a0, a1)) for a0, a1 in ext}
    cands = [(u, n, v) for u, v in itertools.combinations(range(n), 2)] + \
            [(u, v, n) for u, v in itertools.permutations(range(n), 2)]
    want = set()
    for r in (1, 2, 3):
        for ks in itertools.combinations(cands, r):
            new = R.extend_brute(st, n, list(ks))
            if {x & ((1 << n) - 1) for x in new} != set(st) or len(new) >= 2 * len(st):
                continue
            if any(all(((x >> u) & 1) == ((x >> n) & 1) for x in new) for u in range(n)):
                continue
            want.add(tuple(new))
    if got != want:
        bad += 1
check("extensions() = brute force over all knot sets of size <= 3 (40 bases)", bad == 0, f"{bad} mismatches")

# 3. lattice dimension by matching = brute force over orientations and chain partitions
bad = 0
tested = 0
for trial in range(400):
    n = rng.randint(3, 7)
    st = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, 2 * n))])
    sp = R.splits(st, n)
    if not 1 <= len(sp) <= 9:
        continue
    tested += 1
    full = (1 << n) - 1
    if R.lattice_dimension(sp, full) != R.lattice_dimension_brute(sp, full):
        bad += 1
check(f"lattice dimension: matching = brute force ({tested} split systems)", bad == 0, f"{bad} mismatches")

# 4. known shapes
def grid(r, c):
    cells = [(x, y) for y in range(c) for x in range(r)]
    idx = {p: i for i, p in enumerate(cells)}
    knots = [(idx[a], idx[b], idx[d]) for a, b, d in itertools.permutations(cells, 3)
             if min(a[0], d[0]) <= b[0] <= max(a[0], d[0]) and min(a[1], d[1]) <= b[1] <= max(a[1], d[1])]
    return len(cells), R.base_from_knots(len(cells), knots)

def cube(dim):
    pts = list(range(1 << dim))
    knots = [(a, b, d) for a, b, d in itertools.permutations(pts, 3) if all(
        min((a >> i) & 1, (d >> i) & 1) <= (b >> i) & 1 <= max((a >> i) & 1, (d >> i) & 1) for i in range(dim))]
    return len(pts), R.base_from_knots(len(pts), knots)

for name, (n, st), want in [
        ("line of 3", R.seed("line"), ("a line", 1, "1")),
        ("2 x 2", R.seed("2x2"), ("two orders", 2, "2")),
        ("3-leaf star", R.seed("star"), ("a branching tree", 2, "1")),
        ("line of 6", (6, R.base_from_knots(6, [(i, j, l) for i, j, l in itertools.combinations(range(6), 3)])), ("a line", 1, "1")),
        ("3 x 3 grid", grid(3, 3), ("two orders", 2, "2")),
        ("2 x 4 grid", grid(2, 4), ("two orders", 2, "2")),
        ("cube Q3", cube(3), ("a cube of 3 orders", 3, "3"))]:
    m = R.measure(st, n)
    check(f"shape {name}", (m["kind"], m["lam"], m["k"]) == want, f"{m['kind']}, lam {m['lam']}, k {m['k']}, N {m['N']}")

# 5. the zero-cost fill from the line of three: N' = N, unique, and it is the square
n, st = R.seed("line")
ext = R.extensions(st, n, 3)
zero = [(a0, a1) for a0, a1 in ext if R.pc(a0) + R.pc(a1) == len(st)]
canon = R.Canon()
sq = canon.cid(R.seed("2x2")[1], 4)
check("line of 3: exactly one zero-cost extension with <= 3 knots, and it is the square",
      len(zero) == 1 and canon.cid(R.apply(st, n, *zero[0]), 4) == sq, f"{len(zero)} zero-cost")
ext1 = R.extensions(st, n, 1)
check("line of 3: no zero-cost extension with one knot", all(R.pc(a) + R.pc(b) > len(st) for a, b in ext1))

# 6. blindness: the multiset of option sizes and the classes of the options do not depend on the names
bad = 0
for start in ("line", "2x2", "star"):
    n, st = R.seed(start)
    base_sizes = sorted(len(o) for _, o, _ in R.options(st, n, "uniform", 3))
    base_classes = sorted(canon.cid(o, n + 1) for _, o, _ in R.options(st, n, "uniform", 3))
    for _ in range(5):
        perm = list(range(n)); rng.shuffle(perm)
        b = R.relabel(st, n, perm)
        if sorted(len(o) for _, o, _ in R.options(b, n, "uniform", 3)) != base_sizes:
            bad += 1
        if sorted(canon.cid(o, n + 1) for _, o, _ in R.options(b, n, "uniform", 3)) != base_classes:
            bad += 1
check("blind: option sizes and classes invariant under renaming (3 starts x 5 renamings)", bad == 0, f"{bad} differences")

# 7. Canon: a renamed base is the same class; the line of four and the star of four are different classes
n, st = R.seed("line")
check("Canon: renamed line of 3 is the same class", canon.cid(R.relabel(st, 3, [2, 0, 1]), 3) == canon.cid(st, 3))
l4 = R.base_from_knots(4, [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
check("Canon: line of 4 and star of 4 differ", canon.cid(l4, 4) != canon.cid(R.seed("star")[1], 4))

# 8. the matched six-starts: the same twelve states (a line of six); one distinction in all four knots, or none
f, nf = R.SEEDS["fan6"][1], R.SEEDS["nonfan6"][1]
line6 = R.base_from_knots(6, [(i, j, l) for i, j, l in itertools.combinations(range(6), 3)])
deg = lambda ks: max(sum(x in k for k in ks) for x in range(6))
check("fan6 and nonfan6: both exactly the line of six's 12 states",
      R.base_from_knots(6, f) == line6 == R.base_from_knots(6, nf) and len(line6) == 12)
check("fan6 has a distinction in all four knots, nonfan6 none", deg(f) == 4 and deg(nf) < 4, f"{deg(f)}, {deg(nf)}")
c2 = R.Canon()
check("Canon: states alone merge fan6 and nonfan6; with knots they differ",
      c2.cid(line6, 6) == c2.cid(line6, 6) and c2.cid(line6, 6, list(f)) != c2.cid(line6, 6, list(nf)))

# 9. knot moves: without locality they reach exactly the admitted extensions; with it, every knot is local
bad = 0
for trial in range(60):
    n = rng.randint(3, 6)
    ks = [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, n))]
    st = R.base_from_knots(n, ks)
    if len(st) < 2:
        continue
    free = {(a0, a1) for a0, a1, _ in R.knot_moves(st, n, ks, 3, local=None)}
    if free != set(R.extensions(st, n, 3)):
        bad += 1
    lp = R.local_pairs(ks)
    for a0, a1, kk in R.knot_moves(st, n, ks, 3, local="knot"):
        if any(tuple(sorted(x for x in k if x != n)) not in lp for k in kk):
            bad += 1
        if R.apply(st, n, a0, a1) != R.extend_brute(st, n, list(kk)):
            bad += 1
    for a0, a1, kk in R.knot_moves(st, n, ks, 3, local="strict"):
        if not any(all(set(x for x in k if x != n) <= set(h) for k in kk) for h in ks):
            bad += 1
    vp = R.valid_pairs(st, n)
    for a0, a1, kk in R.knot_moves(st, n, ks, 3, local="closure"):
        if any(tuple(sorted(x for x in k if x != n)) not in vp for k in kk):
            bad += 1
check("knot moves: unrestricted = admitted extensions; knot, strict and closure moves obey their rule (60 bases)", bad == 0, f"{bad} problems")

# 10. irredundancy: no move's knot set has a knot whose removal leaves the same states
bad = 0
n, st = 6, line6
for a0, a1, kk in R.knot_moves(st, n, list(f), 3):
    for drop in range(len(kk)):
        rest = [k for i, k in enumerate(kk) if i != drop]
        if rest and R.extend_brute(st, n, rest) == R.apply(st, n, a0, a1):
            bad += 1
check("knot moves are irredundant (fan6)", bad == 0, f"{bad} redundant")

# 11. symmetric continuations: plumbing on the 3-leaf star (not a frozen read-out)
n, st = R.seed("star")
inv = R.invariant_continuations(st, n)
check("symmetric continuations: the free and fixed continuations are always found", {"free", "fixed"} <= {k for _, k in inv})

# 12. closure locality is a function of the states: the same moves (as state sets) from fan6 and nonfan6
mf = sorted((a0, a1) for a0, a1, _ in R.knot_moves(line6, 6, list(f), 3, local="closure"))
mn = sorted((a0, a1) for a0, a1, _ in R.knot_moves(line6, 6, list(nf), 3, local="closure"))
check("closure-local moves identical from fan6 and nonfan6", mf == mn)

# 13. amendment 2: the disagreement-weighted class graph gives the same classes as the frozen incidence graph (small bases)
import networkx as nx


def old_graph(states, n):
    full = (1 << n) - 1
    G = nx.Graph()
    for x in range(n):
        G.add_node(("p", x), kind="p")
    for i, a in enumerate(R.splits(states, n)):
        for side, m in ((0, a), (1, full ^ a)):
            G.add_node(("s", i, side), kind="s")
            for x in range(n):
                if (m >> x) & 1:
                    G.add_edge(("p", x), ("s", i, side))
        G.add_edge(("s", i, 0), ("s", i, 1), role="pair")
    return G


nm = lambda a, b: a["kind"] == b["kind"]
em = lambda a, b: a.get("role") == b.get("role")
bad = tested = 0
for trial in range(300):
    n = rng.randint(4, 7)
    a = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, 2 * n))])
    if rng.random() < 0.5:
        perm = list(range(n)); rng.shuffle(perm)
        b = R.relabel(a, n, perm)
    else:
        b = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, 2 * n))])
    if len(a) != len(b) or len(a) < 2:
        continue
    tested += 1
    old = nx.is_isomorphic(old_graph(a, n), old_graph(b, n), node_match=nm, edge_match=em)
    new = nx.is_isomorphic(R.Canon.graph(a, n), R.Canon.graph(b, n), node_match=nm, edge_match=em)
    bad += old != new
check(f"amendment 2: new class graph = frozen class graph on {tested} pairs of bases", bad == 0, f"{bad} disagreements")

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
