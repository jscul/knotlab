#!/usr/bin/env python3
"""Checks for HANDLE-EMERGENCE-20261102-001C: the odd-point and skip models, planar interfaces, and the slack a handle leaves.

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
import planar_lib as PL  # noqa: E402

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


def solutions(H, s, n, M):
    keep = [k for k in range(len(H)) if k != M]
    return G.states(n)[G.sat_matrix([H[k] for k in keep], [s[k] for k in keep], n).all(axis=1)]


def odd_point(row, L, sg):
    v = [int(row[p]) ^ sg[j] for j, p in enumerate(L)]
    return next(L[j] for j in range(3) if v[j] != v[(j + 1) % 3] and v[j] != v[(j + 2) % 3])


def incidence_graph(H, skip=None):
    g = nx.Graph()
    g.add_edges_from((("p", p), ("l", k)) for k, L in enumerate(H) for p in L if k != skip)
    return g


SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}

# ------------------------------------------------------------------------------------------------ 1. the odd-point model
info1 = collections.Counter()
ok1 = True
for idx, (H, s, n) in SP.items():
    sign = {(k, p): s[k][j] for k, L in enumerate(H) for j, p in enumerate(L)}
    for M in range(len(H)):
        A = solutions(H, s, n, M)
        chosen = {tuple(odd_point(row, H[k], s[k]) for k in range(len(H)) if k != M) for row in A}
        basis = nx.cycle_basis(incidence_graph(H, skip=M))
        lines = [k for k in range(len(H)) if k != M]
        allowed = set()
        for pick in itertools.product(*[H[k] for k in lines]):
            F = {("l", k): p for k, p in zip(lines, pick)}
            good = True
            for cyc in basis:
                par = 0
                for a, b in zip(cyc, cyc[1:] + cyc[:1]):
                    L, p = (a, b) if a[0] == "l" else (b, a)
                    par ^= sign[(L[1], p[1])] ^ (F[L] == p[1])
                if par:
                    good = False
                    break
            if good:
                allowed.add(pick)
        same = allowed == chosen and len(A) == 2 * len(chosen)
        ok1 &= same
        info1["removals"] += 1
        info1["removals where solutions up to complement = incidence choices with the cycle parities"] += same
check("1 the odd-point model: on every census knot space (planar or not) and every removal, choosing each line's odd point is a bijection "
      "between the solutions up to complement and the choices of one incidence per line whose number on each cycle of the incidence graph "
      "(without the removed line) has the parity of the cycle's signs", ok1 and info1["removals"] > 0, dict(info1))


# ------------------------------------------------------------------------------------------------ 2-3. the skip model and interfaces on plane spaces
def plane_faces(H):
    ok, emb = nx.check_planarity(incidence_graph(H))
    assert ok
    return PL.faces(emb)


def face_condition(fcs, sign):
    return all(sum(sign[(v[1], w[1])] if v[0] == "l" else sign[(w[1], v[1])] for v, w in zip(f, f[1:] + f[:1])) % 2 == (len(f) // 2 + 1) % 2
               for f in fcs)


def line_faces(fcs):
    """for each line: list of (face index, the two incidences of the line on that face)"""
    out = collections.defaultdict(list)
    for fi, f in enumerate(fcs):
        for i, v in enumerate(f):
            if v[0] == "l":
                out[v[1]].append((fi, {f[i - 1][1], f[(i + 1) % len(f)][1]}))
    return out


def matchings(lf, lines, targets):
    """the perfect matchings of lines to target faces (each line to one of its own faces), as dicts"""
    out = []

    def rec(i, used, cur):
        if i == len(lines):
            out.append(dict(cur))
            return
        for fi, _ in lf[lines[i]]:
            if fi in targets and fi not in used:
                cur[lines[i]] = fi
                rec(i + 1, used | {fi}, cur)
                del cur[lines[i]]
    rec(0, frozenset(), {})
    return out


PLANE = [("census %d" % idx, H, s, n) for idx, (H, s, n) in SP.items() if PL.incidence_planar(H)]
for size, seed in ((10, 0), (10, 1), (12, 0), (12, 2)):
    for swap in (False, True):
        PLANE.append(("grown %d points, seed %d%s" % (size, seed, ", dual reading" if swap else ""),) + PL.to_space(PL.grow(size, seed), swap))
for k in (5, 6):
    PLANE.append(("prism over a %d-cycle" % (2 * k),) + PL.to_space(PL.prism(k)))
PLANE.append(("truncated octahedron",) + PL.to_space(PL.permutohedron()))
info2, info3 = {}, collections.Counter()
ok2 = ok3 = True
for name, H, s, n in PLANE:
    fcs = plane_faces(H)
    sign = {(k, p): s[k][j] for k, L in enumerate(H) for j, p in enumerate(L)}
    lf = line_faces(fcs)
    t = collections.Counter()
    t["faces"] = len(fcs)
    t["faces = lines + 2"] = len(fcs) == len(H) + 2
    t["face condition"] = face_condition(fcs, sign)
    for M in range(len(H)):
        A = solutions(H, s, n, M)
        mfaces = {fi for fi, _ in lf[M]}
        lines = [k for k in range(len(H)) if k != M]
        pms = matchings(lf, lines, set(range(len(fcs))) - mfaces)
        skips = set()
        for row in A:
            mu = []
            for k in lines:
                o = odd_point(row, H[k], s[k])
                mu.append(next(fi for fi, inc in lf[k] if o not in inc))
            skips.add(tuple(mu))
        pmset = {tuple(pm[k] for k in lines) for pm in pms}
        good = skips == pmset and len(A) == 2 * len(pms)
        t["removals"] += 1
        t["solutions up to complement = perfect matchings of the other lines to the faces off the removed line"] += good
        # interfaces: the odd points of each other line L
        for L in lines:
            actual = {odd_point(row, H[L], s[L]) for row in A}
            matched = {pm[L] for pm in pms}
            predicted = {next(p for p in H[L] if p not in inc) for fi, inc in lf[L] if fi in matched}
            shared = sum(1 for fi, _ in lf[L] if fi in mfaces)
            info3["(line, removed line) pairs"] += 1
            info3["odd points = incidences opposite the line's faces matched to it in some perfect matching"] += actual == predicted
            ok3 &= actual == predicted
            ok3 &= len(actual) <= 3 - shared
            if set(H[L]) & set(H[M]):
                info3["pairs meeting in a point"] += 1
                info3["pairs meeting in a point that share a face"] += shared > 0
                info3["pairs meeting in a point with at most four port patterns"] += len(actual) <= 2
                ok3 &= shared > 0 and len(actual) <= 2
            info3["interfaces of %d patterns (%d faces shared with the removed line)" % (2 * len(actual), shared)] += 1
    ok2 &= t["faces = lines + 2"] and t["face condition"] and \
        t["solutions up to complement = perfect matchings of the other lines to the faces off the removed line"] == t["removals"]
    info2[name] = dict(t)
census_signings = collections.Counter()
for idx, (H, s, n) in SP.items():
    if not PL.incidence_planar(H):
        continue
    fcs = plane_faces(H)
    for sg in G.failing_signings(H, n):
        census_signings["failing signings of planar census spaces"] += 1
        census_signings["satisfying the face condition"] += face_condition(fcs, {(k, p): sg[k][j] for k, L in enumerate(H) for j, p in enumerate(L)})
ok2 &= census_signings["failing signings of planar census spaces"] == census_signings["satisfying the face condition"] > 0
check("2 the skip model on 17 plane knot spaces (the planar census spaces, grown spaces of 10 and 12 points, prisms, the truncated "
      "octahedron): faces = lines + 2, the signs satisfy the face condition, and at every removal the solutions up to complement are exactly "
      "the perfect matchings of the other lines to the faces not touching the removed line (each line to one of its own faces, the face it "
      "skips); every failing signing of the planar census spaces satisfies the face condition",
      ok2, {"spaces": info2, "census signings": dict(census_signings)})
check("3 interfaces on the same spaces: after a removal, a line's possible odd points are exactly the incidences opposite its faces matched "
      "to it in some perfect matching; a line sharing faces with the removed line loses those faces, and every line meeting the removed "
      "line in a point shares a face with it and has at most four port patterns", ok3, dict(info3))

# ------------------------------------------------------------------------------------------------ 4. a handle leaves slack
H, s, n = SP[21]
verts = [("p", p) for p in range(n)] + [("l", k) for k in range(len(H))]
nbr = {v: [] for v in verts}
for k, L in enumerate(H):
    for p in L:
        nbr[("l", k)].append(("p", p))
        nbr[("p", p)].append(("l", k))


def faces_of(rot):
    seen, out = set(), []
    for u in verts:
        for v in nbr[u]:
            if (u, v) in seen:
                continue
            f, a, b = [], u, v
            while (a, b) not in seen:
                seen.add((a, b))
                f.append(a)
                r = rot[b]
                a, b = b, r[(r.index(a) + 1) % 3]
            out.append(f)
    return out


sign = {(k, p): s[k][j] for k, L in enumerate(H) for j, p in enumerate(L)}
tori, first = collections.Counter(), None
for bits in itertools.product((0, 1), repeat=len(verts)):
    rot = {v: (list(nbr[v]) if b == 0 else [nbr[v][0], nbr[v][2], nbr[v][1]]) for v, b in zip(verts, bits)}
    fcs = faces_of(rot)
    if (2 - len(verts) + 3 * n - len(fcs)) // 2 != 1:
        continue
    tori["torus embeddings"] += 1
    tori["with 7 hexagonal faces"] += sorted(len(f) for f in fcs) == [6] * 7
    tori["on which the knot's signs satisfy the face condition"] += face_condition(fcs, sign)
    if first is None:
        first = fcs
lf = line_faces(first)
slack = collections.Counter()
for M in range(len(H)):
    A = solutions(H, s, n, M)
    lines = [k for k in range(len(H)) if k != M]
    sols = set()
    for row in A:
        sols.add(tuple(next(fi for fi, inc in lf[k] if odd_point(row, H[k], s[k]) not in inc) for k in lines))
    mf = [fi for fi, _ in lf[M]]
    faceodd = set()
    for mu in itertools.product(*[[fi for fi, _ in lf[k]] for k in lines]):
        c = collections.Counter(list(mu) + mf)
        if all(c[f] % 2 for f in range(len(first))):
            faceodd.add(mu)
    slack["removals"] += 1
    slack["skip assignments with every face skipped an odd number of times"] += len(faceodd)
    slack["of which solutions"] += len(sols & faceodd)
    slack["solutions"] += len(A)
    slack["every solution among them"] += sols <= faceodd
    slack["each with one face skipped three times"] += all(max(collections.Counter(list(mu) + mf).values()) == 3 for mu in faceodd)
check("4 a handle leaves slack: the Fano plane has 16 torus embeddings (rotation systems with 7 faces), all with 7 hexagons, and on each "
      "the knot's signs satisfy the face condition; 7 lines meet 7 faces, so counting no longer forces failure; after each removal the 9 "
      "skips cover the 7 faces oddly only with one face skipped three times, and of the 14 such assignments just 5 are solutions (twice, "
      "for the complement): the two homology parities, absent on a plane space, decide",
      tori["torus embeddings"] == tori["with 7 hexagonal faces"] == tori["on which the knot's signs satisfy the face condition"] == 16 and
      slack["every solution among them"] == slack["each with one face skipped three times"] == slack["removals"] == 7 and
      slack["skip assignments with every face skipped an odd number of times"] == 14 * 7 and slack["of which solutions"] == 5 * 7 and
      slack["solutions"] == 10 * 7, {"tori": dict(tori), "slack": dict(slack)})

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
