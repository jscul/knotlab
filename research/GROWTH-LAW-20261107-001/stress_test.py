#!/usr/bin/env python3
"""One size past for GROWTH-LAW-20261107-001A's computed claims (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B research/GROWTH-LAW-20261107-001/stress_test.py
Reuses the ticket's own library and writes stress_test.json beside this file."""
import collections
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"
sys.path.insert(0, str(A))
import growth_law_lib as G  # noqa: E402

T0 = time.time()
OUT = {}


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)


# 1 knots of 'time has no loop' are the cycles: one size past K4, prism, K3,3, cube (and the Petersen graph enumerated)
graphs = {
    "K5": (5, [(a, b) for a in range(5) for b in range(a + 1, 5)]),
    "Petersen": (10, [(i, (i + 1) % 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]),
    "Wagner": (8, [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]),
}
rows = []
ok = True
for name, (nv, E) in graphs.items():
    Arel = G.acyclic_orientations(nv, E)
    cyc = G.cycles_of(nv, E)
    ks = {frozenset(Arel.names_of(T)) for T in G.knots(Arel)}
    good = ks == {frozenset(Arel.names[e] for e in seq) for seq, _ in cyc}
    rows.append([name, len(E), len(Arel.rows), len(cyc), len(ks), good])
    ok &= good
# parallel seams are ties: a triangle with one doubled edge (multigraph)
E = [(0, 1), (0, 1), (1, 2), (0, 2)]
names = [f"e{i}" for i in range(len(E))]
rows_m = []
for r in range(1 << len(E)):
    out = collections.defaultdict(list)
    indeg = collections.Counter()
    for i, (a, b) in enumerate(E):
        x, y = (a, b) if r >> i & 1 else (b, a)
        out[x].append(y)
        indeg[y] += 1
    q = [v for v in range(3) if indeg[v] == 0]
    seen = 0
    while q:
        u = q.pop()
        seen += 1
        for w in out[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    if seen == 3:
        rows_m.append(r)
M = G.Rel(names, rows_m)
mc = sorted(sorted(M.names_of(T)) for T in G.minimal_constrained(M))
good_m = mc == [["e0", "e1"], ["e0", "e2", "e3"], ["e1", "e2", "e3"]]
rows.append(["triangle with a doubled seam (minimal constrained sets)", mc, good_m])
ok &= good_m
record("1 knots of acyclic orientations are exactly the cycles: K5, the Petersen graph (enumerated), the Wagner graph; a doubled "
       "seam is a tie", ok, rows)

# 2 pumping one size past k = 3: k = 4 labels at radius 1
rng = random.Random(20261108)
k = 4
N = G.pump_bound(1, k)
st = collections.Counter()
for _ in range(300):
    law = G.random_symmetric_law(k, rng, rng.uniform(0.25, 0.85))
    T = G.thread_lengths(law, k, N + 4)
    Rg = G.ring_lengths(law, k, N + 4)
    if T and not Rg:
        st["threads but no ring"] += 1
        st["longest such thread"] = max(st["longest such thread"], max(T))
    long_ = [n for n in T if n >= N]
    if long_:
        st["laws with a thread at the bound or longer"] += 1
        ring = G.pump(G.labelled_thread(law, k, max(long_)), 1)
        st["pumped ring valid"] += ring is not None and G.windows_ok(law, ring, ring=True) and len(ring) in Rg
record("2 Theorem 4 one size past: k = 4 labels at radius 1 (300 random laws, bound %d)" % N,
       st["pumped ring valid"] == st["laws with a thread at the bound or longer"] > 0 and st["longest such thread"] < N, dict(st))


# 3 Theorem 1(b)'s identity on larger worlds: the shadow on order and state variables is Full x (seed's law)
def existence_world(lo, hi, absent="free"):
    """sites lo..hi (lo <= 0 <= hi), seed 0; existence of every other site; pair bits for every left site against every right
    site (did the left one come first); states: an edge distinction between consecutive sites and outside the ends, and each
    site's own open end. Absent things are free (or, absent='zero', absent pair bits are 0)."""
    sites = list(range(lo, hi + 1))
    others = [s for s in sites if s != 0]
    ex = [f"e{s}" for s in others]
    pairs = [(a, b) for a in sites if a < 0 for b in sites if b > 0]
    od = [f"h{a}_{b}" for a, b in pairs]
    edges = [f"x{s}" for s in range(lo, hi + 2)]           # x{s} sits between site s-1 and site s
    ups = [f"u{s}" for s in sites]
    names = ex + od + edges + ups
    idx = {v: i for i, v in enumerate(names)}
    checks = {s: (1 << idx[f"x{s}"]) | (1 << idx[f"x{s + 1}"]) | (1 << idx[f"u{s}"]) for s in sites}
    states = edges + ups
    rows = []
    for L in range(0, -lo + 1):
        for R in range(0, hi + 1):
            present = set(range(-L, R + 1))
            emask = sum(1 << idx[f"e{s}"] for s in others if s in present)
            # orders: interleavings of the left chain -1, -2, ... and the right chain 1, 2, ...
            left = list(range(-1, -L - 1, -1))
            right = list(range(1, R + 1))
            orders = set()
            for pos in itertools.combinations(range(L + R), L):
                seq, li, ri = [], 0, 0
                for t in range(L + R):
                    if t in pos:
                        seq.append(left[li]); li += 1
                    else:
                        seq.append(right[ri]); ri += 1
                when = {s: t for t, s in enumerate(seq)}
                m = 0
                for (a, b) in pairs:
                    if a in present and b in present and when[a] < when[b]:
                        m |= 1 << idx[f"h{a}_{b}"]
                orders.add(m)
            free_pairs = [idx[f"h{a}_{b}"] for (a, b) in pairs if not (a in present and b in present)]
            if absent == "free":
                expanded = set()
                for m in orders:
                    for bits in itertools.product((0, 1), repeat=len(free_pairs)):
                        expanded.add(m | sum(b << i for b, i in zip(bits, free_pairs)))
                orders = expanded
            free_states = [idx[v] for v in states if (v.startswith("u") and int(v[1:]) not in present)
                           or (v.startswith("x") and int(v[1:]) - 1 not in present and int(v[1:]) not in present)]
            live = [idx[v] for v in states if idx[v] not in free_states]
            for bits in itertools.product((0, 1), repeat=len(live)):
                x = sum(b << i for b, i in zip(bits, live))
                if all(bin(x & checks[s]).count("1") % 2 == 0 for s in present):
                    for fb in itertools.product((0, 1), repeat=len(free_states)):
                        xs = x | sum(b << i for b, i in zip(fb, free_states))
                        for m in orders:
                            rows.append(emask | m | xs)
    return G.Rel(names, rows), set(od), states


rows = []
ok = True
for (lo, hi) in ((-2, 1), (-2, 2), (-3, 2)):
    for absent in ("free", "zero"):
        R, od, states = existence_world(lo, hi, absent)
        S = R.shadow(sorted(od) + states)
        seed_states = [r for r in R.rows if all((r >> R.index[v]) & 1 == 0 for v in R.names if v.startswith("e"))]
        seed_shadow = {sum(((r >> R.index[v]) & 1) << j for j, v in enumerate(states)) for r in seed_states}
        no = len(od)
        product_rows = {o | (x << no) for o in range(1 << no) for x in seed_shadow}
        is_product = set(S.rows) == product_rows
        rows.append([lo, hi, absent, R.n, len(R.rows), is_product])
        ok &= is_product == (absent == "free")
record("3 Theorem 1(b) on larger worlds (sites -2..2 and -3..2): with absent pair bits free, the shadow on the order and state "
       "variables is exactly Full x (the seed's law), so no knot meets the order without existence; set to 0, it is not", ok, rows)

# 4 random disc growth on K_m never sticks, one size past m <= 5
sys.path.insert(0, str(ROOT / "proofs/GROW-COIN-20261107-001A/GROW-COIN-20261107-001A-P001_refinement_shares_its_coin_accretion_must_carry_it"))
import growth_lib as GL  # noqa: E402
rows = []
ok = True
for m in (6, 7):
    order, _ = GL.ring_order(m)
    _, log = GL.greedy_grow(order)
    tris = [order[0]] + [t for *_, t in log]
    kinds, tot = G.chi_steps_2d(tris)
    stuck = sum(G.disc_growth(tris, rng)[1] > 0 for _ in range(30))
    rows.append([m, len(tris), dict(kinds), tot, stuck])
    ok &= tot == 2 and stuck == 0 and kinds["pinch"] == 0
record("4 K_m for m = 6, 7: one beginning and one end; random disc growth never sticks (30 runs each)", ok, rows)

# 5 rings one size past n <= 10
ok = True
rows = []
for n in (11, 12, 13, 14):
    E = G.ring_edges(n)
    loc = G.orientation_rel(n, E, lambda p: max(p) <= 1)
    beg = G.orientation_rel(n, E, lambda p: min(p) == 0)
    good = len(loc.rows) == 2 and beg.rows == G.nae(beg.names).rows and G.is_knot_set(beg, beg.names)
    rows.append([n, len(loc.rows), len(beg.rows), good])
    ok &= good
record("5 rings n = 11..14: local history two cyclic orientations; the beginning is NAE_n and a knot", ok, rows)

(HERE / "stress_test.json").write_text(json.dumps({"checks": OUT, "seconds": round(time.time() - T0, 1)}, indent=1, default=str) + "\n")
print("all passed" if all(v["pass"] for v in OUT.values()) else "SOME FAILED")
