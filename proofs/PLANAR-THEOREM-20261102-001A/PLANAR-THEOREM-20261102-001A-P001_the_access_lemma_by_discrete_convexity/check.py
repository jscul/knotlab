#!/usr/bin/env python3
"""Checks for PLANAR-THEOREM-20261102-001A: the access lemma, by discrete convexity.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About five minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
import numpy as np  # noqa: E402,F401
import planar_lib as PL  # noqa: E402
import potential_lib as POT  # noqa: E402

G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
PLANE = [("census %d" % idx, H, s, n) for idx, (H, s, n) in SP.items() if PL.incidence_planar(H)]
for size, seeds in ((10, range(3)), (12, range(3)), (14, range(2))):
    for seed in seeds:
        g = PL.grow(size, seed)
        for swap in (False, True):
            PLANE.append(("grown %d points, seed %d%s" % (size, seed, ", dual reading" if swap else ""),) + PL.to_space(g, swap))
for k in (5, 6, 7):
    for swap in (False, True):
        PLANE.append(("prism over a %d-cycle%s" % (2 * k, ", dual reading" if swap else ""),) + PL.to_space(PL.prism(k), swap))
for swap in (False, True):
    PLANE.append(("truncated octahedron%s" % (", dual reading" if swap else ""),) + PL.to_space(PL.permutohedron(), swap))
LARGE = []
for size, seeds in ((16, range(3)), (18, range(2)), (20, range(1))):
    for seed in seeds:
        g = PL.grow(size, 100 + seed)
        for swap in (False, True):
            LARGE.append(("grown %d points, seed %d%s" % (size, 100 + seed, ", dual reading" if swap else ""),) + PL.to_space(g, swap))


def up(a, b):
    return tuple(-((-(x + y)) // 2) for x, y in zip(a, b))


def down(a, b):
    return tuple((x + y) // 2 for x, y in zip(a, b))


# ------------------------------------------------------------------------------------------------ 1. potentials
info1 = collections.Counter()
ok1 = True
DATA = []
for name, H, s, n in PLANE:
    for M in range(len(H)):
        pl = POT.Plane(H, s, n, M)
        sols = G.removal(H, s, n, M)
        mus = [pl.matching(x) for x in sols]
        x0, mu0, hub = sols[0], mus[0], H[M][0]
        pots, cons, par = [], True, True
        for x, mu in zip(sols, mus):
            c, ok = pl.heights(mu, mu0)
            cons &= ok
            par &= all((x[p] ^ x0[p] ^ x[hub] ^ x0[hub]) == c[p] % 2 for p in range(n))
            pots.append(tuple(c))
        V = set(pots)
        lnat = all(up(a, b) in V and down(a, b) in V for a, b in itertools.combinations(V, 2))
        one = len(V) == len(sols) // 2 and len({tuple(sorted(mu.items())) for mu in mus}) == len(V)
        ok1 &= cons and par and lnat and one
        info1["removals"] += 1
        info1["heights well defined"] += cons
        info1["parity of the potential = value relative to the hub"] += par
        info1["one potential per matching (solutions / 2)"] += one
        info1["potentials closed under rounded midpoints (L-natural convex)"] += lnat
        DATA.append((name, H, s, n, M, pl, sols, mus, pots))
check("1 potentials: on 30 plane knot spaces at every removal, integrating the matching against a reference from the hole gives well "
      "defined integer potentials, one per matching; a point's value relative to the hub is the parity of its potential; and the set of "
      "potentials is closed under rounded midpoints", ok1 and info1["removals"] > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. the staircase at the gluing line
info2 = collections.Counter()
ok2 = True
for name, H, s, n, M, pl, sols, mus, pots in DATA:
    for li, L1 in enumerate(H):
        if li == M or any(f in pl.mfaces for (L, f, p, q) in pl.edges if L == li) or \
                len([1 for (L, f, p, q) in pl.edges if L == li]) != 3:
            continue
        X = list(L1)
        edge_of = {f: (p, q) for (L, f, p, q) in pl.edges if L == li}
        states = []
        for mu in mus:
            p, q = edge_of[mu[li]]
            states.append(next(y for y in X if y not in (p, q)))
        if len(set(states)) != 3:
            continue
        cp = [{y: c[y] for y in X} for c in pots]
        # (b) the two non-odd ports of each state: their difference takes one value on the state and one off it
        for st in X:
            y, yp = [z for z in X if z != st]
            on = {v[y] - v[yp] for t, v in zip(states, cp) if t == st}
            off = {v[y] - v[yp] for t, v in zip(states, cp) if t != st}
            good = len(on) == 1 and len(off) == 1 and abs(next(iter(on)) - next(iter(off))) == 1
            ok2 &= good
            info2["(state, gluing line, removal) triples"] += 1
            info2["non-odd difference: one value on the state, the neighbouring value off it"] += good
        # (a) a port of constant potential: the other two ports trace a chain with that port's state in the middle
        tied = [y for y in X if len({v[y] for v in cp}) == 1]
        if tied:
            y0 = tied[0]
            y, yp = [z for z in X if z != y0]
            pts = collections.defaultdict(set)
            for t, v in zip(states, cp):
                pts[t].add((v[y], v[yp]))
            single = all(len(w) == 1 for w in pts.values())
            p1 = {t: next(iter(w)) for t, w in pts.items()}
            order = sorted(p1, key=lambda t: p1[t])
            chain = all(p1[order[i]][0] <= p1[order[i + 1]][0] and p1[order[i]][1] <= p1[order[i + 1]][1] for i in range(2))
            good = single and chain and order[1] == y0
            ok2 &= good
            info2["gluing lines with a port tied to the hub"] += 1
            info2["the other two ports: one point per state, a chain, the tied port's state in the middle"] += good
check("2 the staircase: for every gluing line sharing no face with the removed line and showing all three states, the two non-odd ports of "
      "each state differ by one potential value on that state and by the neighbouring value off it; and when a port's potential is "
      "constant (the port tied to the hub), the other two ports take one point per state, forming a chain with that port's state in the "
      "middle", ok2 and info2["gluing lines with a port tied to the hub"] > 0, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. the theorem
src = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
exec(src[src.index("def solutions("):src.index("# ------------------------------------------------------------------------------------------------ 1. the hub's tie class")])
info3 = collections.Counter()
for name, H, s, n in PLANE + LARGE:
    info3.update(classify_pinnings(H, s, n))  # noqa: F821
good_kinds = {"(i) hub tied to a non-odd port", "(ii) two-port knot, excluded pattern one step from the pinned one"}
check("3 the theorem's conclusion, on 42 plane knot spaces (the 30 above and 12 grown spaces of 16, 18 and 20 points): every pinning of "
      "the gluing pattern by the hub and a near point is of type (i) or (ii)",
      set(info3) <= good_kinds and sum(info3.values()) > 0, dict(info3))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
