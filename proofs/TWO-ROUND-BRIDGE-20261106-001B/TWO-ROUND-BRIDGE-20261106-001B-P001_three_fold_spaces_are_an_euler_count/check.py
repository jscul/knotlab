#!/usr/bin/env python3
"""Checks for TWO-ROUND-BRIDGE-20261106-001B: three-fold spaces are an Euler count.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, scipy, networkx, python-sat). Single process; the solver runs take a few minutes."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import count_lib as C  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

GR, PL = C.GR, C.PL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def port_patterns(lines, n, ports):
    sols = []
    for x in itertools.product((0, 1), repeat=n):
        if all(len({x[p] for p in L}) == 2 for L in lines):
            sols.append(tuple(x[p] for p in ports))
    return set(sols)


def solve(cls, budget=None):
    with Solver(name="cadical153", bootstrap_with=cls) as S:
        if budget:
            S.conf_budget(budget)
            r = S.solve_limited()
        else:
            r = S.solve()
        return r, S.accum_stats().get("conflicts")


def families():
    out = []
    for k in range(2, 11):
        out.append(("octahedron k=%d" % k, C.octa_dual(k)))
    for m in range(2, 8):
        out.append(("prism over the %d-cycle" % (2 * m), PL.prism(m)))
    out.append(("truncated octahedron", PL.permutohedron()))
    for npts in (10, 14, 20, 30, 40):
        for seed in range(3):
            out.append(("ladder growth to %d points, seed %d" % (npts, seed), PL.grow(npts, seed)))
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. the Fano pieces and what they pass through their ports
    FANO, T14 = GR.FANO, GR.T14
    pieces = {}
    # block: the Fano plane minus a line; ports = that line's points
    L0 = FANO[0]
    pieces["Fano block (minus a line)"] = ([l for l in FANO if l != L0], 7, list(L0), {(0, 0, 0), (1, 1, 1)})
    # dual block: the Fano plane split at a point into three ports, one on each line through it
    p0 = 0
    lines_d, nxt, ports = [], 7, []
    for l in FANO:
        if p0 in l:
            lines_d.append(tuple(nxt if q == p0 else q for q in l))
            ports.append(nxt)
            nxt += 1
        else:
            lines_d.append(l)
    pieces["dual block (split at a point)"] = (lines_d, 10, ports, {v for v in itertools.product((0, 1), repeat=3) if len(set(v)) == 2})
    # T14 minus its root line, twisted at (root line, port 0): its ports satisfy not x0 = x1 = x2
    pieces["T14 minus its root line"] = ([l for l in T14[1:]], 14, list(T14[0]), {(0, 1, 1), (1, 0, 0)})
    info1, ok1 = {}, True
    for name, (lines, n, prts, expect) in pieces.items():
        pats = port_patterns(lines, n, prts)
        cls = C.nae_clauses(lines)
        hidden = [q + 1 for q in range(n) if q not in prts]
        S, produced, wmax = C.dp_eliminate(cls, hidden)
        # what Davis-Putnam leaves on the ports is exactly the port relation
        left = {v for v in itertools.product((0, 1), repeat=3)
                if all(any((l > 0) == bool(v[prts.index(abs(l) - 1)]) for l in cl) for cl in S)}
        info1[name] = {"points": n, "port patterns": sorted(pats), "as expected": pats == expect,
                       "Davis-Putnam over the hidden points: clauses produced": produced, "largest width": wmax,
                       "clauses left on the ports define the port relation": left == pats}
        ok1 &= pats == expect and left == pats
    check("1 the Fano pieces: a block ties its ports, a dual block passes exactly a line's six patterns, T14 minus its root line passes "
          "not x0 = x1 = x2; each port relation is derived by resolution of small width (the constant cost of contracting a piece)",
          ok1, info1)

    # 2. the Euler count on plane families, with a control
    fam = families()
    info2, ok2 = {}, True
    for name, g in fam:
        sp = C.signed_space(g)
        if sp is None:
            continue
        lines, signs, n = sp
        c = C.certificate(lines, signs, n)
        good = (c["faces minus lines"] == 2 and c["faces with an agreeing corner under every assignment"] == c["faces"]
                and c["corners partition by lines and faces"] and c["a line has one agreeing corner if satisfied, three if not"])
        ok2 &= good
        info2[name] = {k: c[k] for k in ("points", "faces minus lines", "most points on a face")} | {"certificate": good}
    # control: one sign flipped breaks the face condition on the two faces through that incidence
    g = C.octa_dual(3)
    lines, signs, n = C.signed_space(g)
    signs2 = [list(s) for s in signs]
    signs2[0][0] ^= 1
    c2 = C.certificate(lines, signs2, n)
    info2["control: octahedron k=3 with one sign flipped"] = {"faces failing": c2["faces"] - c2["faces with an agreeing corner under every assignment"]}
    ok2 &= c2["faces"] - c2["faces with an agreeing corner under every assignment"] == 2
    check("2 the Euler count: on every plane family member with Kasteleyn signs, every face carries an agreeing corner under every "
          "assignment, a line has one agreeing corner if satisfied and three if not, corners partition by lines and by faces, and faces "
          "exceed lines by two; flipping one sign breaks exactly the two faces through it (the check can fail)", ok2, info2)

    # 3. assignments modulo complement are the odd-degree corner sets
    info3, ok3 = {}, True
    for name, g in fam:
        sp = C.signed_space(g)
        lines, signs, n = sp
        b = C.tseitin_bijection(lines, signs, n)
        good = b["connected"] and b["dimension of odd-degree corner sets"] == b["dimension of assignments modulo complement"]
        if "exhaustive: distinct images" in b:
            good &= b["exhaustive: every image has odd degree everywhere"] and \
                b["exhaustive: distinct images"] == b["exhaustive: odd-degree corner sets"]
        ok3 &= good
        if n <= 20 or name.startswith("octahedron k=10"):
            info3[name] = b
    check("3 the corner map: assignments modulo complement correspond one to one to the corner sets of odd degree at every line and "
          "every face (the solutions of a parity system on the line-face graph); dimensions agree on every member, exhaustively on "
          "those with at most 20 points", ok3, info3)

    # 4. Sherali-Adams of level 3 sees the count; without the faces it does not
    info4, ok4 = {}, True
    for name, g in fam:
        lines, signs, n = C.signed_space(g)
        if n > 40:
            continue
        mf = C.certificate(lines, signs, n)["most points on a face"]
        if mf > 3:
            continue
        s_faces = C.sa_restricted(lines, signs, n, use_faces=True)
        s_lines = C.sa_restricted(lines, signs, n, use_faces=False)
        cs, fpts = C.corners(lines, n)
        faces_add = any(not any(set(U) <= set(L) for L in lines) for U in fpts)
        info4[name] = {"with faces": "infeasible" if s_faces == 2 else s_faces,
                       "lines only": "feasible" if s_lines == 0 else ("infeasible" if s_lines == 2 else s_lines),
                       "some face's points lie in no line": faces_add}
        ok4 &= s_faces == 2 and (s_lines == 0 or not faces_add)
        controls4 = info4.setdefault("_controls where faces add point sets", 0)
        info4["_controls where faces add point sets"] = controls4 + (faces_add and s_lines == 0)
    check("4 Sherali-Adams: the level-3 relaxation restricted to local distributions on the lines and on the faces' point sets "
          "(consistent pair marginals) is infeasible on every family member whose faces carry at most three points and at most 40 "
          "points; restricted to the lines alone it is feasible on every member where some face's points lie in no line, so there the "
          "faces are what refutes (the check can fail); on the cube, K4^(3), every face lies in a line and the lines already refute",
          ok4 and info4["_controls where faces add point sets"] >= 4, info4)

    # 5. decorations are three-fold spaces
    info5, ok5 = {}, True
    for name, g in fam:
        if not (name.startswith("octahedron") and int(name.split("=")[1]) <= 6):
            continue
        H3, nneg = C.three_fold_space(g)
        n3 = 1 + max(max(l) for l in H3)
        deg = {}
        for l in H3:
            for p in l:
                deg[p] = deg.get(p, 0) + 1
        cubic = len(H3) == n3 and all(deg[p] == 3 for p in range(n3)) and all(len(set(l)) == 3 for l in H3)
        r, conf = solve(C.nae_clauses(H3))
        sep = C.separating_triangles(int(name.split("=")[1]))
        info5[name] = {"three-fold points": n3, "negated incidences decorated": nneg, "cubic": cubic, "2-colourable": r,
                       "solver conflicts (CaDiCaL 1.5.3)": conf, "separating triangles of the glue's dual (0 = the glue is a brace)": sep}
        ok5 &= cubic and r is False and sep == 0
    sepk = {k: C.separating_triangles(k) for k in range(1, 9)}
    info5["separating triangles of the k-frequency octahedron, k = 1..8"] = sepk
    ok5 &= not any(sepk.values())
    check("5 decorating the octahedral family (T14 pieces at negated incidences) gives cubic triple systems that are not 2-colourable: "
          "unsigned three-fold spaces whose plane core is the octahedral glue, a single brace (its dual triangulation has no separating "
          "triangle), so their handle tree is a star of T14 pieces around one brace", ok5, info5)

    # 6. resolution: widths, the treewidth bound, solver cost
    info6 = {}
    dp = {}
    for k in range(2, 5):
        lines, signs, n = C.signed_space(C.octa_dual(k))
        cls = C.nae_clauses(lines, signs)
        order = C.min_degree_order(cls, list(range(1, n + 1)))
        S, produced, wmax = C.dp_eliminate(cls, order)
        dp["k=%d (%d points)" % (k, n)] = {"refuted": frozenset() in S, "clauses produced": produced, "largest width": wmax}
    info6["Davis-Putnam refutations along a minimum-degree order (regular resolution; size and width are upper bounds)"] = dp
    tw = {}
    for k in range(2, 11):
        lines, signs, n = C.signed_space(C.octa_dual(k))
        tw["k=%d (%d points)" % (k, n)] = C.primal_width_bound(lines, n)
    info6["treewidth upper bound of the primal graph (min-fill)"] = tw
    cd = {}
    for k in range(2, 7):
        lines, signs, n = C.signed_space(C.octa_dual(k))
        r, conf = solve(C.nae_clauses(lines, signs))
        cd["k=%d (%d points)" % (k, n)] = conf
        assert r is False
    info6["solver conflicts on the signed octahedral family (CaDiCaL 1.5.3)"] = cd
    vals = list(cd.values())
    ratios = [round(vals[i + 1] / vals[i], 1) for i in range(len(vals) - 1)]
    info6["ratios of successive conflict counts"] = ratios
    check("6 resolution measurements (evidence, not proof): Davis-Putnam refutations of the signed octahedral spaces (upper bounds on "
          "size and width), the primal treewidth bound of the octahedral family (linear in k, so treewidth dynamic programming gives "
          "size 2^O(k) = 2^O(sqrt n)), and solver conflicts growing by a factor of at least five per step in k",
          all(r >= 5 for r in ratios) and all(v["refuted"] for v in dp.values()), info6)

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
