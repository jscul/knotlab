#!/usr/bin/env python3
"""Checks for PHASE-HALO-20261103-001B: the ladder and grid laws.

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

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001C/HALO-FORCING-20261103-001C-P001_the_reach_on_ladders_and_grids"))
sys.path.insert(0, str(ROOT / "proofs/PHASE-HALO-20261103-001A/PHASE-HALO-20261103-001A-P001_opposite_faces_carry_the_halo"))
import planar_lib as PL  # noqa: E402
import halo_pipeline as HP  # noqa: E402
import families_lib as FL  # noqa: E402

TL = HP.TL
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
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
HF, sF, nF = SP[21]


# ------------------------------------------------------------------------------------------------ 1. the grid law: independence
def cross_range(Q, L):
    """the smallest range of height differences between a port's region and a region of L, over L's corners (D(a, b) + D(b, a): it does
    not depend on the reference matching)"""
    X = [q for q in Q.lines[L] if q not in Q.ports]
    best = None
    for phi in [i for i, e in enumerate(Q.edges) if e[0] == L]:
        D = TL.shortest(Q.graph({L: phi}), list(Q.ports) + X)
        if D is None:
            continue
        r = min(D[a][b] + D[b][a] for a in Q.ports for b in X)
        best = r if best is None else min(best, r)
    return best


info1 = collections.Counter()
ok1 = True
ranges = collections.defaultdict(list)
for level, zs in ((2, (0, 5, 17, 40)), (3, (0,))):
    H2, s2, n2 = PL.to_space(FL.octahedral(level))
    for z in zs:
        Q = TL.Split(H2, [list(x) for x in s2], n2, z)
        g = nx.Graph()
        g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(Q.lines) for q in L)
        dist = nx.multi_source_dijkstra_path_length(g, [("p", y) for y in Q.ports])
        for L in range(len(Q.lines)):
            if any(y in Q.lines[L] for y in Q.ports):
                continue
            d = dist[("l", L)]
            independent = len(Q.transfer(L)) == 36
            if d >= 9 or (d >= 7 and (level == 3 or z in (0, 40))):
                ok1 &= independent
            info1["grid of %d points, attached at %d: lines at distance %s %s" % (n2, z, d if d < 9 else ">= 9",
                                                                              "independent of the split point" if independent else
                                                                              "coupled to the split point")] += 1
            if z == 0:
                ranges[("grid of %d points" % n2, d)].append(cross_range(Q, L))
for k in (10, 20):
    H2, s2, n2 = PL.to_space(PL.prism(k))
    Q = TL.Split(H2, [list(x) for x in s2], n2, 0)
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(Q.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(g, [("p", y) for y in Q.ports])
    for L in range(len(Q.lines)):
        if any(y in Q.lines[L] for y in Q.ports):
            continue
        ranges[("ladder of %d points" % n2, dist[("l", L)])].append(cross_range(Q, L))
for (name, d), v in sorted(ranges.items()):
    info1["%s: smallest cross height range at distance %d (min, max over lines)" % (name, d)] = "%d..%d" % (min(v), max(v))
ladder_frozen = all(max(v) == 0 for (name, d), v in ranges.items() if name.startswith("ladder"))
grid_growth = True
for name in ("grid of 64 points", "grid of 256 points"):
    mins = [min(v) for (nm, d), v in sorted(ranges.items()) if nm == name]
    ds = [d for (nm, d), v in sorted(ranges.items()) if nm == name]
    grid_growth &= all(a <= b for a, b in zip(mins, mins[1:])) and all(m >= 1 for d, m in zip(ds, mins) if d >= 5)
ok1 &= ladder_frozen and grid_growth
check("1 the grid law: on the 64-point grid (four attachment points) every gluing line at distance 9 or more, and from two of the points and "
      "on the 256-point grid every line at distance 7 or more, is independent of the split point (its exact transfer is all 36 pairs), so no "
      "knot through handle points reaches it. The reason is the smallest range of height differences between a port's region and the "
      "line's: 0 at every distance along ladders of 20 and 40 points (frozen), non-decreasing with distance on the grids and positive from "
      "distance 5 (liquid)", ok1, dict(info1))


# ------------------------------------------------------------------------------------------------ 2. the ladder law
def chain(k):
    """the prism over a 2k-cycle as the cyclic chain of consecutive triples, with the canonical signs: (0, 0, 1) on every line except
    lines 0 and 1, which carry (0, 0, 0) and (0, 1, 0)"""
    n = 2 * k
    H = [((j - 1) % n, j, (j + 1) % n) for j in range(n)]
    s = [[0, 0, 1] for _ in range(n)]
    s[0], s[1] = [0, 0, 0], [0, 1, 0]
    return H, s, n


def nae(vals, sg):
    v = [a ^ b for a, b in zip(vals, sg)]
    return not (v[0] == v[1] == v[2])


STATES = list(itertools.product((0, 1), repeat=2))
T = {(a, b): {(b, c) for c in (0, 1) if nae((a, b, c), (0, 0, 1))} for (a, b) in STATES}


def tpow(m):
    out = {s: {s} for s in STATES}
    for _ in range(m):
        out = {s: set().union(*[T[t] for t in out[s]]) if out[s] else set() for s in STATES}
    return out


def transfer_by_matrices(k, j):
    """R(line j) of the chain split at point 0, assembled from powers of T (ports ordered as the split's: lines 0, 1, n-1)"""
    H, s, n = chain(k)
    A, B = tpow(j - 2), tpow(n - 2 - j)
    out = set()
    for x1, x2, xa, xb, ya, yb, yc in itertools.product((0, 1), repeat=7):
        # x1, x2 = points 1, 2; xa, xb = points n-2, n-1; the ports of lines n-1, 0, 1 are ya, yb, yc
        if not (nae((xb, yb, x1), s[0]) and nae((yc, x1, x2), s[1]) and nae((xa, xb, ya), s[n - 1])):
            continue
        for s1 in A[(x1, x2)]:
            for s2 in T[s1]:
                if (xa, xb) in B[s2]:
                    out.add(((yb, yc, ya), (s1[0], s1[1], s2[1])))
    return out


info2 = collections.Counter()
ok2 = True
for k in range(4, 41):
    H, s, n = chain(k)
    # the explicit isomorphism with the prism: top vertex j and bottom vertex j of PL.prism(k) go to chain element j (points: top even,
    # bottom odd; lines: top odd, bottom even)
    gp = PL.prism(k)
    m = 2 * k
    img = {}
    for j in range(m):
        img[j] = ("p", j) if j % 2 == 0 else ("l", j)                # top vertex j
        img[m + j] = ("l", j) if j % 2 == 0 else ("p", j)            # bottom vertex j
    gc = nx.Graph()
    gc.add_edges_from((("p", p), ("l", j)) for j, L in enumerate(H) for p in L)
    iso = all(gc.has_edge(img[a], img[b]) for a, b in gp.edges()) and gp.number_of_edges() == gc.number_of_edges()
    faces, corners = TL.faces_with_corners(H)
    sg = {(kk, p): s[kk][i] for kk, L in enumerate(H) for i, p in enumerate(L)}
    par = collections.Counter()
    for (kk, fi, p, q) in corners:
        par[fi] += 1 + (sg[(kk, p)] ^ sg[(kk, q)])
    kast = len(faces) == n + 2 and all(par[fi] % 2 == 1 for fi in range(len(faces)))
    ok2 &= iso and kast
    info2["prisms whose chain labelling is an isomorphism and whose canonical signs are Kasteleyn (all faces odd)"] += iso and kast
P2, P4 = tpow(2), tpow(4)
ok2 &= P2 == P4 and tpow(3) == tpow(5)
info2["the transfer matrix's powers repeat with period 2 from the second power (T^2 = T^4, T^3 = T^5)"] = int(P2 == P4 and tpow(3) == tpow(5))
classes = collections.defaultdict(set)
for k in range(4, 26):
    H, s, n = chain(k)
    Q = TL.Split(H, s, n, 0)
    for j in range(2, n - 1):
        Rm = transfer_by_matrices(k, j)
        Rh = Q.transfer(j)
        ok2 &= Rm == Rh
        info2["(prism, line) pairs whose transfer from the matrices equals the heights computation"] += Rm == Rh
        if j - 2 >= 2 and n - 2 - j >= 2:
            classes[j % 2].add(frozenset(Rm))
ok2 &= all(len(v) == 1 for v in classes.values())
info2["far lines (both arcs of length 2 or more): distinct transfers by parity of position"] = {("even (bottom face)" if p == 0 else
                                                                                               "odd (top face)"): len(v) for p, v in classes.items()}
check("2 the ladder law, transfer matrices: the prism over a 2k-cycle is the cyclic chain of consecutive triples (explicit isomorphism, k = 4 "
      "to 40) with Kasteleyn signs constant except at two lines beside the split point; its 4-state transfer matrix has powers of period 2 "
      "from the second; the transfer assembled from these powers equals the heights computation on every line (k = 4 to 25); so every far "
      "line's transfer depends only on its parity, the same on every prism", ok2, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. the ladder halo on every prism
info3 = collections.Counter()
ok3 = True
for k in range(5, 41):
    H, s, n = chain(k)
    hs = HP.HaloSpace(HF, sF, 0, H, s, n, 0, G)
    pos = {}
    for L in range(hs.nh, len(hs.lines)):
        j = hs.qline[L]
        pos[L] = j
    R = {L: hs.transfer(L) for L in pos}
    halo = set()
    for M in range(hs.nh):
        Hand = hs.handle(M)
        for L in R:
            for fname, F in FARS:
                if L not in halo and HP.creates(hs, M, L, F, Hand, R[L]):
                    halo.add(L)
    far = [L for L in pos if pos[L] - 2 >= 2 and n - 2 - pos[L] >= 2]
    even_in = all(L in halo for L in far if pos[L] % 2 == 0)
    odd_out = all(L not in halo for L in far if pos[L] % 2 == 1)
    ok3 &= even_in and odd_out
    info3["prisms whose far bottom-face lines all create and far top-face lines none"] += even_in and odd_out
check("3 the ladder halo: with the Fano plane attached at point 0 of the chain (k = 5 to 40) and removals inside it, every far line on the "
      "face opposite the attachment point creates and no far line on the attachment point's own face does; by check 2 the same holds on "
      "every prism, since creation is decided from the transfer", ok3, dict(info3))

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
