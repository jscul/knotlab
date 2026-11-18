"""PICK-TWO-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import hashlib
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import picklib as P  # noqa: E402

L, M = P.L, P.M
ROOT = P.ROOT
PIN = {
    "experiments/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest/nnlib.py": None,
    "experiments/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/melib.py":
        "9d1b32f3c600a8e489862bc14bff8a78eb0b7c925eb73adcff1635205d1788a4",
}
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


def relations(S, n):
    """For each pair of splits (as masks over the first n distinctions' extension classes), crossing or which quadrant is empty."""
    sp, full = P.splits(S, n)
    out = {}
    for a, b in itertools.combinations(sp, 2):
        q = (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))
        out[(a, b)] = tuple(bool(x) for x in q)
    return out


def restrict(S, n, m):
    """The states restricted to the first m distinctions."""
    mask = (1 << m) - 1
    return tuple(sorted({s & mask for s in S}))


# 1. pins (nnlib's digest is recorded in the contract; melib's is NEVER-NEST's)
h = hashlib.sha256(open(os.path.join(ROOT, list(PIN)[1]), "rb").read()).hexdigest()
check("pin melib.py", h == PIN[list(PIN)[1]])

# 2. full grids recognised: Q2, Q3, Q4, a 2 x 3 and 3 x 3 grid grown by NNF; lines and a line with one fill are not
ok = P.grid(*P.cube(2)) == (2, [1, 1]) and P.grid(*P.cube(3)) == (3, [1, 1, 1]) and P.grid(*P.cube(4)) == (4, [1, 1, 1, 1])
for n0 in (4, 5, 6):
    ok &= P.grid(*P.start(f"line{n0}")) is None
S, n = L.square_states(), 4
rng = random.Random(2)
seen = 0
while n < 16:
    ops, _ = L.free_options(S, n)
    (a0, a1), _ = rng.choice(ops)
    S, n = M.apply(S, n, a0, a1), n + 1
    g = P.grid(S, n)
    ok &= (g is not None) == L.reading(S, n)["full_grid"]
    seen += g is not None
check("full grids recognised (cubes, NNF's 2-grids, not lines)", ok and seen >= 3, f"{seen} full 2-grids")

# 3. P1: CAP(3) from Q3 keeps lambda = 3; at a full 3-grid it only subdivides, and right after a subdivision the fills offered are
#    exactly the empty cells of the new grid (prod(s_i + 1) - n)
def part_sizes(S, n):
    sp, full = P.splits(S, n)
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    G.add_edges_from((i, j) for i, j in itertools.combinations(range(len(sp)), 2) if P.cross(sp[i], sp[j], full))
    parts = [len(c) for c in nx.connected_components(nx.complement(G))]
    return parts


ok = True
cnt = 0
for seed in range(4):
    S, n = P.cube(3)
    rng = random.Random(30 + seed)
    last_sub = False
    while n < 24:
        r = P.reading(S, n)
        ok &= r["lam"] == 3
        ops, kind = P.options(S, n, "CAP", 3)
        if r["full_grid"]:
            ok &= kind == "sub"
        if last_sub:
            prod = 1
            for x in part_sizes(S, n):
                prod *= x + 1
            ok &= kind == "fill" and len(ops) == prod - n
            cnt += 1
        a0, a1 = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        last_sub = len(S2) > len(S)
        S, n = S2, n + 1
    ok &= P.reading(S, n)["lam"] == 3
check("P1: CAP(3) from Q3 keeps three orders; after a subdivision it offers exactly the empty cells", ok, f"{cnt} subdivisions")

# 4. P2: a CC fill r never lands in an empty quadrant of two old splits (so every crossing and every nesting is kept), from 2 x 2,
#    Q3 and a line with one fill; k and lambda unchanged over the run
ok = True
cnt = 0
for st in ("2x2", "Q3", "fill"):
    for seed in range(3):
        if st == "fill":
            S, n = P.start("line6")
            z = P.fills(S, n)
            S, n = M.apply(S, n, *random.Random(seed).choice(z)), n + 1
        else:
            S, n = P.start(st)
        k0 = P.kl(S, n)
        rng = random.Random(40 + seed)
        for _ in range(14):
            ops, kind = P.options(S, n, "CC")
            a0, a1 = rng.choice(ops)
            if kind == "fill":
                idx = {x: i for i, x in enumerate(S)}
                full = (1 << n) - 1
                val = lambda X: (a1 >> idx[X]) & 1
                sp, _ = P.splits(S, n)
                for a, b in itertools.combinations(sp, 2):
                    for X in (a, full ^ a):
                        for Y in (b, full ^ b):
                            if X & Y == 0:
                                ok &= not (val(X) and val(Y))
                                cnt += 1
            S, n = M.apply(S, n, a0, a1), n + 1
        ok &= P.kl(S, n) == k0
check("P2: CC fills never fill an empty quadrant; k and lambda kept", ok, f"{cnt} empty quadrants")


# 5. P3: at full 2- and 3-grids with a chain of two or more splits, the twisted corner on three cells along it is a fill that
#    raises lambda
ok = True
cnt = 0
for seed in range(3):
    S, n = L.square_states(), 4
    rng = random.Random(50 + seed)
    while n < 14:
        ops, _ = L.free_options(S, n)
        (a0, a1), _ = rng.choice(ops)
        S, n = M.apply(S, n, a0, a1), n + 1
        g = P.grid(S, n)
        if g and max(g[1]) >= 2:
            l0 = P.kl(S, n)[1]
            raising = [f for f in P.fills(S, n) if P.kl(M.apply(S, n, *f), n + 1)[1] > l0]
            ok &= len(raising) > 0
            cnt += 1
check("P3: a raising fill exists at every full grid with a chain of two splits", ok, f"{cnt} grids")

# 6. P5: KEEP keeps lambda (from 2 x 2 and Q3) and never fills a line
ok = True
for st in ("2x2", "Q3", "line5"):
    S, n = P.start(st)
    tr = P.grow(S, n, n + 10, "KEEP", 60)
    ok &= len({r["lam"] for r in tr if "lam" in r}) == 1
    if st == "line5":
        ok &= all(r["kind"] in ("start", "sub") for r in tr)
check("P5: KEEP keeps the start's lambda; a line stays a line", ok)

# 7. P4: PRICE(lin, w) from a line: w = 3 never fills; w = 1 raises lambda above 2 by n = 20
ok = True
S, n = P.start("line5")
tr = P.grow(S, n, 16, "PRICE", 70, ("lin", 3.0))
ok &= all(r["lam"] == 1 for r in tr)
tr = P.grow(S, n, 20, "PRICE", 71, ("lin", 1.0))
ok &= max(r["lam"] for r in tr) >= 3
check("P4: linear price: w = 3 keeps the line, w = 1 passes two orders", ok)

# 8. the fast fill enumeration = NEVER-NEST's full one (every candidate function), on random bases from lines, 2 x 2 and Q3
ok = True
cnt = 0
rng = random.Random(80)
for trial in range(120):
    S, n = P.start(rng.choice(["line5", "line6", "line7", "line8", "2x2", "Q3"]))
    for _ in range(rng.randrange(0, 9)):
        ops = list(L.free_zero(S, n)) + list(L.free_subs(S, n))
        if not ops:
            break
        a0, a1 = rng.choice(ops)
        S, n = M.apply(S, n, a0, a1), n + 1
        if len(S) > 30:
            break
    ok &= set(P.fills(S, n)) == set(L.free_zero(S, n))
    cnt += 1
check("fills() = free_zero (all candidate functions)", ok, f"{cnt} bases")

# 9. the 3 x 3 x 3 grid is a full 3-grid; every rule's options on it are found; KEEP and CC keep lambda = 3 there
import run as RUN  # noqa: E402
S, n = RUN.grid333()
ok = P.grid(S, n) == (3, [2, 2, 2]) and P.kl(S, n)[1] == 3
for rule in ("KEEP", "CC"):
    tr = P.grow(S, n, n + 6, rule, 90)
    ok &= all(r["lam"] == 3 for r in tr)
check("3 x 3 x 3 grid recognised; KEEP and CC keep three orders on it", ok)

print(sum(results), "of", len(results), "checks pass")
