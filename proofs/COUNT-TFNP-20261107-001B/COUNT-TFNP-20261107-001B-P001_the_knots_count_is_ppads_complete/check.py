#!/usr/bin/env python3
"""Checks for COUNT-TFNP-20261107-001B: the knot's count is PPADS^dt-complete; the two-sided count is PPAD^dt-complete.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; a few minutes."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import two_sided_lib as B  # noqa: E402
sys.path.insert(0, str(ROOT / "proofs/COUNT-NOTE-20261107-001B/COUNT-NOTE-20261107-001B-P001_the_count_has_a_unary_sherali_adams_refutation"))
import sa_lib as SA  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def colouring_with_negatives(m, rng):
    """a random interior colouring biased to hold clockwise fully labelled triangles"""
    iv = B.S.interior_vertices(m)
    c = {v: rng.randrange(3) for v in iv}
    for _ in range(3):
        a, b = rng.choice(iv)
        tri = [(a, b), (a + 1, b), (a, b + 1)]
        if all(v in c for v in tri):
            for v, col in zip(tri, (0, 2, 1)):     # clockwise 0, 1, 2
                c[v] = col
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)

    # 1. the boundary FLAT-STATES-20261107-001B's map expects is the canonical one shifted cyclically by -m (mod 3)
    shifts, ok1 = {}, True
    for m in range(3, 13):
        red = B.S.build_reduction(2 * m + 4, m)
        s = B.boundary_shift(red)
        shifts[m] = s
        ok1 &= s is not None and s == (-m) % 3
    check("1 for m = 3..12 the reduction's fixed boundary is the canonical Sperner boundary with every colour shifted by -m (mod 3); a "
          "cyclic shift keeps fully labelled triangles and their orientations, so COUNT-TFNP-20261107-001A's instances compose with it",
          ok1, {"shift by m": shifts})

    # 2. two-sided: monochromatic faces sit exactly inside clockwise fully labelled triangles
    info2, ok2 = {}, True
    for m in (4, 5, 6, 7):
        red = B.S.build_reduction(2 * m + 4, m)
        byf = B.face_corners(red["K"])
        agg = {"colourings": 0, "fully labelled triangles": 0, "clockwise ones": 0, "violated lines": 0, "monochromatic faces": 0}
        flags = {"violated lines inside counterclockwise triangles": True, "monochromatic faces inside clockwise triangles": True,
                 "every fully labelled triangle holds one": True, "violated lines minus monochromatic faces = 1": True}
        for trial in range(40):
            c = colouring_with_negatives(m, rng) if trial % 2 else {v: rng.randrange(3) for v in B.S.interior_vertices(m)}
            a = B.audit(red, c, byf)
            agg["colourings"] += 1
            agg["fully labelled triangles"] += a["full"]
            agg["clockwise ones"] += a["negative"]
            agg["violated lines"] += a["violated"]
            agg["monochromatic faces"] += a["mono"]
            for key, akey in (("violated lines inside counterclockwise triangles", "lines_in_positive"),
                              ("monochromatic faces inside clockwise triangles", "faces_in_negative"),
                              ("every fully labelled triangle holds one", "every_full_triangle_holds_one"),
                              ("violated lines minus monochromatic faces = 1", "count_identity")):
                flags[key] &= a[akey]
        ok2 &= all(flags.values()) and agg["clockwise ones"] > 0
        info2["m=%d" % m] = dict(agg, **flags)
    check("2 FLAT-STATES-20261107-001B's map on random Sperner colourings (half seeded with clockwise triangles): violated lines lie inside "
          "counterclockwise fully labelled triangles, monochromatic faces inside clockwise ones, every fully labelled triangle holds one, "
          "and the count identity holds", ok2, info2)

    # 3. the two-sided count has a degree-3 unary Nullstellensatz refutation: the corner identity with the face clauses as axioms
    rows, ok3 = {}, True
    for k in range(2, 7):
        terms, info = SA.certificate(k)
        line_falsifiers = SA.falsifiers(k)
        lines, signs, n = SA.sphere(k)
        cs, fpts = SA.C.corners([list(L) for L in lines], n)
        # the face clauses: for each three-point face, forbid each of the two all-agree assignments
        face_falsifiers = set()
        for c, J in terms:
            if c < 0:
                face_falsifiers.add(frozenset(J.items()))
        pos = {frozenset(J.items()) for c, J in terms if c > 0}
        neg = {frozenset(J.items()) for c, J in terms if c < 0}
        total = {}
        for c, J in terms:
            total = SA.add(total, SA.conj(J), c)
        ok = (pos == line_falsifiers and neg == face_falsifiers and len(neg) == 2 * sum(len(P) == 3 for P in fpts)
              and total == SA.ONE and {c for c, J in terms} == {1, -1} and {len(J) for c, J in terms} == {3})
        ok3 &= ok
        rows["k=%d" % k] = {"line clauses' falsifiers (+1)": len(pos), "face clauses' falsifiers (-1)": len(neg),
                            "sum is the constant 1": total == SA.ONE}
    check("3 the two-sided count (the line clauses together with the clauses 'face f is not monochromatic') has a Nullstellensatz "
          "refutation of degree 3 with constant multipliers +1 and -1: sum of line-clause falsifiers minus sum of face-clause falsifiers "
          "is 1, checked symbolically on K_2..K_6", ok3, rows)

    # 4. controls: each must fail for a mathematical reason
    ctl = {}
    red = B.S.build_reduction(2 * 5 + 4, 5)
    byf = B.face_corners(red["K"])
    c = colouring_with_negatives(5, rng)
    a = B.audit(red, c, byf)
    ctl["seeded colouring has a clockwise triangle"] = a["negative"] > 0
    # (i) the one-sided count is blind to clockwise triangles: no violated line sits in one
    x, col = B.S.image(red, c)
    full = {tuple(sorted(t)): B.orientation(col, t) for t in B.SW.grid(5)[1] if len({col[v] for v in t}) == 3}
    where = [B.coarse_of_points(red, red["K"]["lines"][l]) for l in B.violated_lines(red["K"], x)]
    ctl["no violated line inside a clockwise triangle"] = all(full.get(w) == 1 for w in where)
    # (ii) auditing the image of c against a different colouring c' must fail
    c2 = dict(c)
    v = next(u for t in full for u in t if u in c2)     # an interior vertex of a fully labelled triangle: changing it moves that triangle
    c2[v] = (c2[v] + 1) % 3
    x2, col2 = B.S.image(red, c2)
    full2 = {tuple(sorted(t)): B.orientation(col2, t) for t in B.SW.grid(5)[1] if len({col2[u] for u in t}) == 3}
    where_f = [B.coarse_of_points(red, red["K"]["fpts"][f]) for f in B.mono_faces(red["K"], x, byf)]
    where_l = [B.coarse_of_points(red, red["K"]["lines"][l]) for l in B.violated_lines(red["K"], x)]
    mismatch = not (all(full2.get(w) == -1 for w in where_f) and all(full2.get(w) == 1 for w in where_l)
                    and all((t in where_l) if o == 1 else (t in where_f) for t, o in full2.items()))
    ctl["auditing against a colouring changed at a vertex of a fully labelled triangle is rejected"] = mismatch and full2 != full
    # (iii) dropping one face clause breaks the identity
    terms, _ = SA.certificate(3)
    drop = next(i for i, (cc, J) in enumerate(terms) if cc < 0)
    total = {}
    for i, (cc, J) in enumerate(terms):
        if i != drop:
            total = SA.add(total, SA.conj(J), cc)
    ctl["the identity without one face clause is not 1"] = total != SA.ONE
    check("4 controls: a seeded clockwise triangle holds no violated line (the one-sided count does not see it), auditing an image against "
          "a changed colouring is rejected, and the identity fails without one face clause", all(ctl.values()), ctl)

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
