#!/usr/bin/env python3
"""Checks for PLANAR-COMPOSE-20261102-001A: the hub reaches the ports on a plane side.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About ten minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402

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
NONPLANAR = [("Fano plane", ) + SP[21], ("census 58",) + SP[58]]


def solutions(H, s, n, M):
    keep = [k for k in range(len(H)) if k != M]
    return G.states(n)[G.sat_matrix([H[k] for k in keep], [s[k] for k in keep], n).all(axis=1)]


def tied_to(A, h, n):
    return {p for p in range(n) if len({(int(r[h]), int(r[p])) for r in A}) == 2}


def odd_index(t, sigma):
    d = [i for i in range(3) if t[i] != sigma[i]]
    if len(d) == 1:
        return d[0]
    return next(i for i in range(3) if t[i] == sigma[i])


def classify_pinnings(H, s, n):
    """every pinning of the closing line's pattern by the hub and one near point, over all (closing line, removed line) pairs with six
    patterns: (i) hub tied to a non-odd port, (i') to the odd port, (ii) hub, non-odd ports form a knot excluding a pattern one step
    from the pinned one, (ii') two steps, (iv) neither"""
    out = collections.Counter()
    for mi, M in enumerate(H):
        A = solutions(H, s, n, mi)
        h = M[0]
        hub = tied_to(A, h, n)
        for li, L1 in enumerate(H):
            if li == mi:
                continue
            X = list(L1)
            I = {tuple(int(b) for b in r) for r in A[:, X]}
            if len(I) != 6:
                continue
            sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
            tied = [i for i, y in enumerate(X) if y in hub]
            for a in sorted(set(range(n)) - set(L1) - hub):
                for hv, av in itertools.product((0, 1), repeat=2):
                    rows = A[(A[:, h] == hv) & (A[:, a] == av)]
                    pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                    if len(pats) != 1:
                        continue
                    tau = next(iter(pats))
                    oi = odd_index(tau, sigma)
                    if tied:
                        out["(i) hub tied to a non-odd port" if tied[0] != oi else "(i') hub tied to the odd port"] += 1
                        continue
                    j, k = [i for i in range(3) if i != oi]
                    allowed = {(int(r[X[j]]), int(r[X[k]])) for r in A if int(r[h]) == hv}
                    excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                    if not excl:
                        out["(iv) hub free of the two non-odd ports"] += 1
                    elif any((e[0] != tau[j]) + (e[1] != tau[k]) == 1 for e in excl):
                        out["(ii) two-port knot, excluded pattern one step from the pinned one"] += 1
                    else:
                        out["(ii') two-port knot, excluded pattern two steps from the pinned one"] += 1
    return out


# ------------------------------------------------------------------------------------------------ 1. the hub's tie class
info1 = collections.Counter()
ok1 = True
for name, H, s, n in PLANE:
    g = nx.Graph()
    g.add_edges_from((("p", p), ("l", k)) for k, L in enumerate(H) for p in L)
    fcs = PL.faces(nx.check_planarity(g)[1])
    for mi, M in enumerate(H):
        A = solutions(H, s, n, mi)
        hub = tied_to(A, M[0], n)
        on_faces = {v[1] for f in fcs if ("l", mi) in f for v in f if v[0] == "p"}
        ok1 &= on_faces <= hub
        info1["removals"] += 1
        info1["hub tie class contains every point on the removed line's faces"] += on_faces <= hub
        info1["and equals that set"] += on_faces == hub
check("1 on 30 plane knot spaces (the six planar census spaces and ticket A's 24 of HANDLE-EMERGENCE), at every removal, the hub's tie "
      "class contains every point on the removed line's three faces", ok1 and info1["removals"] > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. the access lemma
info2, plane2, non2 = {}, collections.Counter(), collections.Counter()
for name, H, s, n in PLANE:
    c = classify_pinnings(H, s, n)
    plane2.update(c)
for name, H, s, n in NONPLANAR:
    c = classify_pinnings(H, s, n)
    info2[name] = dict(c)
    non2.update(c)
good_plane = {"(i) hub tied to a non-odd port", "(ii) two-port knot, excluded pattern one step from the pinned one"}
check("2 the access lemma splits plane from non-planar: on the 30 plane spaces every pinning of the closing line's pattern by the hub and "
      "a near point has the hub tied to a non-odd port (i) or forming a near knot with the two non-odd ports whose excluded pattern is one "
      "step from the pinned one (ii); on the Fano plane and census 58 every pinning fails both",
      set(plane2) <= good_plane and sum(plane2.values()) > 0 and not (set(non2) & good_plane) and sum(non2.values()) > 0,
      {"plane spaces": dict(plane2), "non-planar": info2})


# ------------------------------------------------------------------------------------------------ 3. the routes, knot by knot
def splice_analysis(H1, s1, n1, li, H2, s2, n2):
    ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, 0)
    X = sorted(ports)
    P = {v for v in range(n) if side[v] == 0}
    inner = sum(1 << v for v in P - ports)
    outer = sum(1 << v for v in range(n) if v not in P)
    for M, line in enumerate(ls):
        if not set(line) <= P:
            continue
        S = G.removal(ls, ss, n, M)
        A = np.array(S, dtype=np.int8)
        cs = E.circuits(S, n)
        rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
        knots = [m for m in cs if bin(m).count("1") >= 3]
        can = {m: E.canon(m, rep) for m in knots}
        allk = set(can.values())
        cross = {m: bool(m & inner and m & outer) for m in knots}
        gen = E.closure(allk, {can[m] for m in knots if not cross[m]}, n)
        I = {tuple(int(b) for b in row) for row in A[:, X]}
        yield dict(S=S, A=A, X=X, P=P, ports=ports, n=n, M=line, rep=rep, knots=knots, can=can, allk=allk, cross=cross, gen=gen,
                   patterns=len(I))


def pin_separate(r, m):
    """for a crossing knot {h, a, c} through the hub: the pinning (hv, av, tau) and a separating value of c, or None"""
    A, X = r["A"], r["X"]
    hubrep = r["rep"][r["M"][0]]
    pts = E.bits(m)
    hs = [v for v in pts if r["rep"][v] == hubrep]
    near = [v for v in pts if v in r["P"] and v not in r["ports"] and r["rep"][v] != hubrep]
    far = [v for v in pts if v not in r["P"]]
    if len(pts) != 3 or len(hs) != 1 or len(near) != 1 or len(far) != 1:
        return None
    h, a, c = hs[0], near[0], far[0]
    for hv, av in itertools.product((0, 1), repeat=2):
        T = {tuple(int(b) for b in row) for row in A[(A[:, h] == hv) & (A[:, a] == av)][:, X]}
        if len(T) != 1:
            continue
        tau = next(iter(T))
        for cv in (0, 1):
            if tau not in {tuple(int(b) for b in row) for row in A[A[:, c] == cv][:, X]}:
                return h, a, c, hv, tau
    return None


def bit(v):
    return 1 << v


def verify_route(r, m, h, a, c, hv, tau):
    """build the route of the lemma and check every step; returns a label"""
    A, X, rep, allk = r["A"], r["X"], r["rep"], r["allk"]
    I = {tuple(int(b) for b in row) for row in A[:, X]}
    sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
    oi = odd_index(tau, sigma)
    j, k = [i for i in range(3) if i != oi]
    can = lambda s: E.canon(s, rep)
    K = can(m)
    tied = [i for i in range(3) if rep[X[i]] == rep[h]]
    if tied:
        if tied[0] == oi:
            return "pinning of type (i'): no route claimed"
        y0, y1 = X[tied[0]], X[k if tied[0] == j else j]
        K1, K2 = can(bit(h) | bit(a) | bit(y1)), can(bit(y0) | bit(y1) | bit(c))
        ok = K1 in allk and K2 in allk and can((K1 | K2) & ~bit(rep[y1])) == K
        return "(i) route verified" if ok else "(i) route FAILED"
    y2, y3 = X[j], X[k]
    allowed = {(int(row[y2]), int(row[y3])) for row in A if int(row[h]) == hv}
    excl = [e for e in [(b1, b2) for b1 in (0, 1) for b2 in (0, 1)] if e not in allowed]
    step = [e for e in excl if (e[0] != tau[j]) + (e[1] != tau[k]) == 1]
    if not step:
        return "no route claimed"
    e = step[0]
    keep, drop = (y2, y3) if e[0] == tau[j] else (y3, y2)
    K0 = can(bit(h) | bit(y2) | bit(y3))
    K2 = can(bit(y2) | bit(y3) | bit(c))
    K3 = can(bit(h) | bit(keep) | bit(c))
    K1 = can(bit(h) | bit(a) | bit(keep))
    ok = all(x in allk for x in (K0, K2, K3, K1)) and can((K0 | K2) & ~bit(rep[drop])) == K3 and \
        can((K1 | K3) & ~bit(rep[keep])) == K
    return "(ii) route verified" if ok else "(ii) route FAILED"


info3 = collections.Counter()
FAR = {"K4^(3)": SP[1], "census 6": SP[6], "Fano": SP[21], "census 58": SP[58]}
near3 = [x for x in PLANE if x[0].startswith("census") or x[0].startswith("grown 10")]
for name, H1, s1, n1 in near3:
    for fname, (H2, s2, n2) in FAR.items():
        for li in (0, 1):
            for r in splice_analysis(H1, s1, n1, li, H2, s2, n2):
                for m in r["knots"]:
                    if not r["cross"][m] or bin(m).count("1") != 3:
                        continue
                    ps = pin_separate(r, m)
                    if ps is None:
                        continue
                    if r["patterns"] != 6:
                        info3["at %d-pattern removals (outside the lemma): generated" % r["patterns"]] += r["can"][m] in r["gen"]
                        info3["at %d-pattern removals (outside the lemma)" % r["patterns"]] += 1
                        continue
                    info3["pinned-and-separated three-point crossing knots at six-pattern removals"] += 1
                    info3[verify_route(r, m, *ps)] += 1
                    info3["of which generated"] += r["can"][m] in r["gen"]
check("3 the routes, knot by knot, at six-pattern removals: on the six planar census spaces and the six 10-point grown spaces, spliced (lines 0 and 1) into K4^(3), "
      "census 6, the Fano plane and census 58, every pinned-and-separated three-point crossing knot through the hub is produced by the "
      "route of the lemma: in case (i) the near knot {h, a, y'} and the far knot {y0, y', c} eliminate to it; in case (ii) the near knot "
      "{h, y, y'} and the far knot {y, y', c} give the crossing knot {h, y, c}, which eliminates against the near knot {h, a, y} to it",
      info3["pinned-and-separated three-point crossing knots at six-pattern removals"] > 0 and
      info3["(i) route verified"] + info3["(ii) route verified"] ==
      info3["pinned-and-separated three-point crossing knots at six-pattern removals"] == info3["of which generated"] and
      all(info3["at %d-pattern removals (outside the lemma): generated" % q] == info3["at %d-pattern removals (outside the lemma)" % q]
          for q in (2, 4)), dict(info3))

# ------------------------------------------------------------------------------------------------ 4. the premise, on larger far sides
info4 = collections.Counter()
ok4 = True
far4 = [x for x in PLANE if "10 points" in x[0] or "10-cycle" in x[0]] + [("census %d" % i,) + SP[i] for i in sorted(SP)]
for name, H1, s1, n1 in NONPLANAR:
    for fname, H2, s2, n2 in far4:
        for li in (0, 1):
            for r in splice_analysis(H1, s1, n1, li, H2, s2, n2):
                for m in r["knots"]:
                    if r["cross"][m] and r["can"][m] not in r["gen"]:
                        ps = pin_separate(r, m)
                        info4["new knots"] += 1
                        info4["pinned-and-separated three-point knots through the hub"] += ps is not None
                        ok4 &= ps is not None
check("4 the premise holds further: on the Fano plane and census 58 spliced (lines 0 and 1) into every census space and into the eight "
      "10-point plane spaces, every new knot is a pinned-and-separated three-point knot through the hub",
      ok4 and info4["new knots"] > 0, dict(info4))

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
