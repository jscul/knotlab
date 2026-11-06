#!/usr/bin/env python3
"""Checks for PLANAR-THEOREM-20261102-001C: every pinning on a plane side has access; what the premise still needs.

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

src = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
exec(src[src.index("def solutions("):src.index("def classify_pinnings(")])

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
NONPLANAR = [("census %d" % idx, H, s, n) for idx, (H, s, n) in SP.items() if not PL.incidence_planar(H)]


# ------------------------------------------------------------------------------------------------ 1. every pinning pair has access
def classify_pairs(H, s, n):
    """every ordered pair (p, a) of untied points (ports allowed) whose values leave one pattern on a gluing line with six patterns,
    classified relative to p: (i) p is, or is tied to, a non-odd port; (i') to the odd port; (ii) p tied to no port and {p, y, y'}
    (the non-odd ports) excludes, at p's pinning value, a pattern one step from the pinned one; (ii') two steps; (iv) no exclusion"""
    out = collections.Counter()
    for mi, M in enumerate(H):
        A = solutions(H, s, n, mi)  # noqa: F821
        hub = tied_to(A, M[0], n)  # noqa: F821
        tie = {p: tied_to(A, p, n) for p in range(n)}  # noqa: F821
        for li, L1 in enumerate(H):
            if li == mi:
                continue
            X = list(L1)
            I = {tuple(int(b) for b in r) for r in A[:, X]}
            if len(I) != 6:
                continue
            sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in I)
            for p in range(n):
                tied = [i for i, y in enumerate(X) if y in tie[p]]
                for a in range(n):
                    if a == p or a in tie[p]:
                        continue
                    for pv, av in itertools.product((0, 1), repeat=2):
                        rows = A[(A[:, p] == pv) & (A[:, a] == av)]
                        pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                        if len(pats) != 1:
                            continue
                        tau = next(iter(pats))
                        oi = odd_index(tau, sigma)  # noqa: F821
                        role = ("port" if p in X else ("hub" if p in hub else "other point")) + " as p, " + \
                               ("port" if a in X else ("hub" if a in hub else "other point")) + " as a"
                        if tied:
                            kind = "(i)" if tied[0] != oi else "(i')"
                        else:
                            j, k = [i for i in range(3) if i != oi]
                            allowed = {(int(r[X[j]]), int(r[X[k]])) for r in A if int(r[p]) == pv}
                            excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                            if not excl:
                                kind = "(iv)"
                            elif any((e[0] != tau[j]) + (e[1] != tau[k]) == 1 for e in excl):
                                kind = "(ii)"
                            else:
                                kind = "(ii')"
                        out[(role, kind)] += 1
    return out


info1 = collections.Counter()
plane_kinds, nonplane_kinds = collections.Counter(), collections.Counter()
for name, H, s, n in PLANE:
    for (role, kind), v in classify_pairs(H, s, n).items():
        plane_kinds[kind] += v
        info1["plane: %s, type %s" % (role, kind)] += v
for name, H, s, n in NONPLANAR:
    for (role, kind), v in classify_pairs(H, s, n).items():
        if "port" not in role:
            nonplane_kinds[kind] += v
        info1["%s: %s, type %s" % (name, role, kind)] += v
check("1 every pinning has access on a plane side: on 30 plane knot spaces, every ordered pair (p, a) of untied points (ports and the hub "
      "included) whose values leave one pattern of a six-pattern gluing line is of type (i) or (ii) relative to p; on the two non-planar "
      "census spaces (the Fano plane and census 58), no pinning by two non-port points is of type (i) or (ii) relative to either point",
      set(plane_kinds) <= {"(i)", "(ii)"} and sum(plane_kinds.values()) > 0 and not (set(nonplane_kinds) & {"(i)", "(ii)"})
      and sum(nonplane_kinds.values()) > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2-3. splices
NEAR = [("census %d" % i,) + SP[i] for i in (6, 14, 38, 45, 21, 58)]
for seed in (0, 1):
    NEAR.append(("grown 10 points, seed %d" % seed,) + PL.to_space(PL.grow(10, seed)))
FAR = [SP[i] for i in (1, 6, 21, 58)]


def bit(v):
    return 1 << v


info2, info3, info4 = collections.Counter(), collections.Counter(), collections.Counter()
ok2 = ok3 = True
for name, H1, s1, n1 in NEAR:
    kind = "plane" if PL.incidence_planar(H1) else "non-planar"
    for H2, s2, n2 in FAR:
        for li in (0, 1):
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
                I = {tuple(int(b) for b in r) for r in A[:, X]}
                six = len(I) == 6
                sigma = next((t for t in itertools.product((0, 1), repeat=3) if t not in I), None) if six else None
                cs = E.circuits(S, n)
                rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
                knots = [m for m in cs if bin(m).count("1") >= 3]
                can = {m: E.canon(m, rep) for m in knots}
                allk = set(can.values())
                cross = {m: bool(m & inner and m & outer) for m in knots}
                base = {can[m] for m in knots if not cross[m]}
                gen = E.closure(allk, base, n)
                hubrep = rep[line[0]]

                def T(Y, y):
                    msk = np.all(A[:, Y] == y, axis=1)
                    return frozenset(tuple(int(b) for b in r) for r in A[msk][:, X])

                def knot(mask):
                    return E.canon(mask, rep) in allk
                pinned3 = set()
                record = []
                for m in knots:
                    if not cross[m]:
                        continue
                    pts = E.bits(m)
                    U = [v for v in pts if v in P]
                    V = [v for v in pts if v not in P]
                    seps, pins, farpins = False, [], False
                    for u in itertools.product((0, 1), repeat=len(U)):
                        Tu = T(U, u)
                        for v in itertools.product((0, 1), repeat=len(V)):
                            Tv = T(V, v)
                            if Tu & Tv:
                                continue
                            for j in range(3):
                                a_, b_ = {t[j] for t in Tu}, {t[j] for t in Tv}
                                if len(a_) == 1 and len(b_) == 1 and a_ != b_:
                                    seps = True
                            if len(Tu) == 1:
                                pins.append((u, next(iter(Tu))))
                            ys = [U.index(y) for y in U if y in ports]
                            if len({t for t in Tv if all(t[X.index(U[i])] == u[i] for i in ys)}) == 1:
                                farpins = True
                    through = any(rep[v] == hubrep for v in pts)
                    if seps:
                        cls = "separated by one port (ticket B)"
                    elif pins and len(U) == 2 and len(V) == 1:
                        cls = "near-pinned three-point"
                        pinned3.add(can[m])
                    elif pins:
                        cls = "residual: near side pins, %d near + %d far points" % (len(U), len(V))
                    elif farpins:
                        cls = "residual: far side pins, %d near + %d far points" % (len(U), len(V))
                    else:
                        cls = "residual: neither side pins, %d near + %d far points" % (len(U), len(V))
                    record.append((m, cls, through, U, V, pins))
                gen2 = E.closure(allk, base | pinned3, n)
                for m, cls, through, U, V, pins in record:
                    status_ = "generated" if can[m] in gen else "new"
                    info3["%s near sides, %d-pattern removals: %s, %s" % (kind, len(I), cls, status_)] += 1
                    if status_ == "new":
                        ok3 &= cls == "near-pinned three-point" and through and six and kind == "non-planar"
                    ok3 &= can[m] in gen2
                    info3["crossing knots generated by one-sided knots and near-pinned three-point knots"] += can[m] in gen2
                    info3["crossing knots"] += 1
                    if cls != "near-pinned three-point" or not six:
                        continue
                    # 2. the route given by access, relative to either pinning point
                    c = V[0]
                    routes = set()
                    for (u, tau) in pins:
                        oi = odd_index(tau, sigma)  # noqa: F821
                        o = X[oi]
                        n1_, n2_ = [X[i] for i in range(3) if i != oi]
                        for r, other in ((U[0], U[1]), (U[1], U[0])):
                            rv = u[U.index(r)]
                            tiedport = next((y for y in X if rep[y] == rep[r]), None)
                            if tiedport is not None:
                                if tiedport == o:
                                    continue
                                y, yp = tiedport, (n2_ if tiedport == n1_ else n1_)
                                K1, K2 = bit(r) | bit(other) | bit(yp), bit(y) | bit(yp) | bit(c)
                                if knot(K1) and knot(K2) and rep[yp] not in {rep[q] for q in E.bits(m)} and \
                                        E.canon(K1, rep) | E.canon(K2, rep) == E.canon(m, rep) | bit(rep[yp]):
                                    routes.add("(i) %s tied to a non-odd port" % ("hub" if rep[r] == hubrep else "point"))
                                continue
                            for y, yp in ((n1_, n2_), (n2_, n1_)):
                                ty, typ = tau[X.index(y)], tau[X.index(yp)]
                                if np.any((A[:, r] == rv) & (A[:, y] == ty) & (A[:, yp] == 1 - typ)):
                                    continue        # {r, y, y'} does not exclude the pattern one step from tau at y'
                                K0, K2 = bit(r) | bit(y) | bit(yp), bit(y) | bit(yp) | bit(c)
                                K3, K1 = bit(r) | bit(y) | bit(c), bit(r) | bit(other) | bit(y)
                                if all(knot(k) for k in (K0, K2, K3, K1)) and \
                                        E.canon(K0, rep) | E.canon(K2, rep) == E.canon(K3, rep) | bit(rep[yp]) and \
                                        E.canon(K1, rep) | E.canon(K3, rep) == E.canon(m, rep) | bit(rep[y]):
                                    routes.add("(ii) %s and the non-odd ports form a knot one step from the pinned pattern" %
                                               ("hub" if rep[r] == hubrep else "point"))
                    if kind == "plane":
                        ok2 &= bool(routes) or can[m] in base
                    label = "route verified" if routes else ("tie-equivalent to a one-sided knot" if can[m] in base else "no route from access")
                    info2["%s near sides: near-pinned three-point knots, %s, %s" % (kind, label, "generated" if can[m] in gen else "new")] += 1
                    for r_ in routes:
                        info2["%s near sides: route %s" % (kind, r_)] += 1
check("2 the routes, knot by knot: on splices of six census near sides (four plane, two non-planar) and two 10-point plane near sides into "
      "K4^(3), census 6, the Fano plane and census 58 (lines 0 and 1, every near removal with six port patterns), every crossing knot on a "
      "plane near side that a near pair pins and a far point separates, and that no single port separates, is produced by the route its "
      "pinning pair's access gives (relative to either pinning point)", ok2 and info2, dict(info2))
check("3 the census and the reduction: on the same splices at every near removal, every crossing knot is generated by one-sided knots "
      "together with the near-pinned three-point crossing knots, and every new knot is a near-pinned three-point knot through the hub, at "
      "a six-pattern removal on a non-planar near side", ok3 and info3["crossing knots"] > 0, dict(info3))



# ------------------------------------------------------------------------------------------------ 4. pinning on a point-split side
def split_point(H, s, n, z):
    """the knot space with point z split into three ports, one on each line through z"""
    lines, ports, k = [], [], n
    for L in H:
        if z in L:
            L = tuple(k if q == z else q for q in L)
            ports.append(k)
            k += 1
        lines.append(L)
    A = G.states(k)[G.sat_matrix(lines, list(s), k).all(axis=1)]
    return A, ports, k, [q for q in range(k) if q != z]


def classify_far(H, s, n):
    out = collections.Counter()
    for z in range(n):
        A, X, k, keep = split_point(H, s, n, z)
        J = {tuple(int(b) for b in r) for r in A[:, X]}
        if len(J) != 6:
            continue
        sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in J)
        tie = {p: tied_to(A, p, k) for p in keep}  # noqa: F821
        for p in keep:
            if p in X:
                continue
            tied = [i for i, y in enumerate(X) if y in tie[p]]
            for a in keep:
                if a == p or a in X or a in tie[p]:
                    continue
                for pv, av in itertools.product((0, 1), repeat=2):
                    rows = A[(A[:, p] == pv) & (A[:, a] == av)]
                    pats = {tuple(int(b) for b in r) for r in rows[:, X]}
                    if len(pats) != 1:
                        continue
                    tau = next(iter(pats))
                    oi = odd_index(tau, sigma)  # noqa: F821
                    if tied:
                        out["(i)" if tied[0] != oi else "(i')"] += 1
                        continue
                    j, kk = [i for i in range(3) if i != oi]
                    allowed = {(int(r[X[j]]), int(r[X[kk]])) for r in A if int(r[p]) == pv}
                    excl = {(b1, b2) for b1 in (0, 1) for b2 in (0, 1)} - allowed
                    out["(iv)" if not excl else ("(ii)" if any((e[0] != tau[j]) + (e[1] != tau[kk]) == 1 for e in excl) else "(ii')")] += 1
    return out


info4 = collections.Counter()
ok4 = True
for idx in sorted(SP):
    H, s, n = SP[idx]
    c = classify_far(H, s, n)
    planar = PL.incidence_planar(H)
    ok4 &= set(c) <= {"(i)", "(ii)"} if planar else not c
    info4["census %d (%s): pinnings by two non-port points" % (idx, "plane" if planar else "non-planar")] += sum(c.values())
    for kk, v in c.items():
        info4["plane, type " + kk] += v
for size, seed in ((10, 0), (10, 1), (12, 0)):
    H, s, n = PL.to_space(PL.grow(size, seed))
    c = classify_far(H, s, n)
    ok4 &= set(c) <= {"(i)", "(ii)"} and sum(c.values()) > 0
    info4["grown %d points, seed %d: pinnings by two non-port points" % (size, seed)] += sum(c.values())
    for kk, v in c.items():
        info4["plane, type " + kk] += v
check("4 the point-split side (computation): splitting a point of a knot space into three ports, one on each line through it, every pinning "
      "of the port pattern by two non-port points is of type (i) or (ii) on the plane census spaces and three grown plane spaces, while on "
      "the Fano plane and census 58 no two non-port points pin the pattern at all", ok4, dict(info4))

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
