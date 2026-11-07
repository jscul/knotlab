#!/usr/bin/env python3
"""Finite checks for LOGIC-AXIS-20261107-001B-P001 (the frozen axis).

The uniform arguments are in proof.md. Each check states its range and has a control that must be
rejected. The lower bound (conjecture) is checked only inside the stated windows.

    python3 -B check.py          verify against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from ledrappier_lib import (d_norm_table, hop_knot, is_frobenius_triangle, is_knot, naf_weight,  # noqa: E402
                            rank, rotate, smallest_vanishing_through, swap, vanishes, vec)

RNG = random.Random(20261107)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_dependencies() -> dict:
    manifest = json.loads((HERE / "manifest.json").read_text())
    mismatched, statuses = {}, {}
    for path, digest in manifest["parent_bindings"].items():
        if sha256(ROOT / path) != digest:
            mismatched[path] = "digest"
        statuses[path] = json.loads((ROOT / path).read_text()).get("status")
    ok = not mismatched and all(s in ("Proved", "passed") for s in statuses.values())
    return {"pass": ok, "info": {"mismatched": mismatched, "statuses": statuses}}


# --- 1. the polynomial model agrees with the law on a patch -------------------------------------------
def patch_columns(n: int, law: str = "ledrappier") -> dict:
    """Columns of the allowed states of the law on the patch i,j>=0, i+j<=n, by Gaussian elimination on
    its parity checks (independent of the polynomial model)."""
    pts = [(i, j) for i in range(n + 1) for j in range(n + 1 - i)]
    index = {p: k for k, p in enumerate(pts)}
    rows = []
    for (i, j) in pts:
        if law == "ledrappier":
            tri = [(i, j), (i + 1, j), (i, j + 1)]
        else:  # control: a different three-point law
            tri = [(i, j), (i + 1, j), (i + 1, j + 1)]
        if all(t in index for t in tri):
            m = 0
            for t in tri:
                m ^= 1 << index[t]
            rows.append(m)
    basis = []
    for r in rows:
        for p, b in basis:
            if r >> p & 1:
                r ^= b
        if r:
            p = r.bit_length() - 1
            basis = [(q, b ^ r if b >> p & 1 else b) for q, b in basis]
            basis.append((p, r))
    pivots = {p for p, _ in basis}
    sols = []
    for free in range(len(pts)):
        if free in pivots:
            continue
        s = 1 << free
        for p, b in basis:
            if b >> free & 1:
                s |= 1 << p
        sols.append(s)
    cols = {}
    for p, k in index.items():
        c = 0
        for j, s in enumerate(sols):
            if s >> k & 1:
                c |= 1 << j
        cols[p] = c
    return cols


def implied_by_patch(cols, s) -> bool:
    total = 0
    for p in s:
        total ^= cols[p]
    return total == 0


def check_model() -> dict:
    n = 24
    cols = patch_columns(n)
    pts = list(cols)
    agree = disagree = 0
    hits = 0
    for _ in range(3000):
        k = RNG.randint(3, 5)
        s = RNG.sample(pts, k)
        if RNG.random() < 0.3:  # also test Frobenius triangles and hop knots placed inside the patch
            e = RNG.randint(0, 3)
            c = (RNG.randint(0, n - 2 ** e - 1), 0)
            s = [c, (c[0] + 2 ** e, 0), (c[0], 2 ** e)]
        model = vanishes(s)
        patch = implied_by_patch(cols, s)
        hits += model
        if model == patch:
            agree += 1
        else:
            disagree += 1
    control_cols = patch_columns(n, law="other")
    frob = [(0, 0), (4, 0), (0, 4)]
    control = vanishes(frob) and not implied_by_patch(control_cols, frob)
    return {"pass": disagree == 0 and hits > 100 and control,
            "info": {"random sets (and placed triangles) tested on the side-24 patch": agree + disagree,
                     "implied checks among them": hits, "disagreements with X^a(1+X)^b": disagree,
                     "control: another three-point law does not imply the Frobenius triangle": control}}


# --- 2. three-point knots are Frobenius triangles -------------------------------------------------------
def check_three_point_knots() -> dict:
    r = 32
    window = [(a, b) for a in range(-r, r + 1) for b in range(-r, r + 1)]
    v = {w: vec(w[0] + r, w[1] + r) for w in window}
    lookup = {v[w]: w for w in window}
    origin = v[(0, 0)]
    triangles = set()
    for s in window:
        if s == (0, 0):
            continue
        t = lookup.get(origin ^ v[s])
        if t is not None and t not in ((0, 0), s):
            triangles.add(frozenset([(0, 0), s, t]))
    all_frob = all(is_frobenius_triangle(t) for t in triangles)
    expected = set()
    for e in range(0, 6):
        h = 2 ** e
        for c in [(0, 0), (-h, 0), (0, -h)]:
            tri = frozenset([c, (c[0] + h, c[1]), (c[0], c[1] + h)])
            if all(max(abs(x), abs(y)) <= r for x, y in tri):
                expected.add(tri)
    neighbours = sorted({p for t in triangles for p in t if p != (0, 0)})
    control = not vanishes([(0, 0), (1, 0), (0, 2)])
    return {"pass": all_frob and triangles == expected and control,
            "info": {"three-point knots through the origin in [-32,32]^2": len(triangles),
                     "all are Frobenius triangles": all_frob, "equal to the expected list": triangles == expected,
                     "bond-2 neighbours of the origin in the window": len(neighbours),
                     "control: {(0,0),(1,0),(0,2)} is not a check": control}}


# --- 3. the signed-binary hop knots --------------------------------------------------------------------
def check_hop_knots() -> dict:
    bad = [n for n in range(1, 2049) if not (is_knot(hop_knot(n)) and len(hop_knot(n)) == 2 + naf_weight(n))]
    lines_bad = []
    for n in range(1, 257):
        k = hop_knot(n)
        for image in ([swap(p) for p in k], [rotate(p) for p in k]):
            if not is_knot(image):
                lines_bad.append(n)
    frob_bad = [k for k in range(0, 21) if not is_knot([(0, 0), (2 ** k, 0), (0, 2 ** k)])]
    k = hop_knot(43)
    control = not vanishes(k[:-1])
    return {"pass": not bad and not lines_bad and not frob_bad and control,
            "info": {"n = 1..2048: hop knot is a knot of size 2 + w(n)": not bad,
                     "n = 1..256: its images on the other two lattice lines are knots": not lines_bad,
                     "k = 0..20: {(0,0),(2^k,0),(0,2^k)} is a knot": not frob_bad,
                     "control: the hop set for 43 without its last apex does not vanish": control}}


# --- 4. the conjecture, inside windows ------------------------------------------------------------------
def check_lower_bound_windows() -> dict:
    found = []
    for n in range(1, 129):
        w = naf_weight(n)
        if w < 2:
            continue
        window = [(a, b) for a in range(-8, n + 9) for b in range(-(n + 8), 2 * n + 9)]
        s = smallest_vanishing_through((0, 0), (n, 0), window, min(4, 1 + w))
        if s is not None:
            found.append((n, s))
    five = {}
    for n in (43, 45, 51, 53):
        window = [(a, b) for a in range(-8, n + 9) for b in range(-(n + 8), 2 * n + 9)]
        five[n] = smallest_vanishing_through((0, 0), (n, 0), window, 5)
    # controls: the same searches find the hop knots when allowed their size (4 points for 3, 5 for 11)
    w3 = [(a, b) for a in range(-8, 3 + 9) for b in range(-(3 + 8), 2 * 3 + 9)]
    w11 = [(a, b) for a in range(-8, 11 + 9) for b in range(-(11 + 8), 2 * 11 + 9)]
    s3 = smallest_vanishing_through((0, 0), (3, 0), w3, 4)
    s11 = smallest_vanishing_through((0, 0), (11, 0), w11, 5)
    control = s3 is not None and len(s3) == 4 and s11 is not None and len(s11) == 5
    ok = not found and all(v is None for v in five.values()) and control
    return {"pass": ok,
            "info": {"n = 1..128, window [-8,n+8]x[-(n+8),2n+8]: knots smaller than 2+w(n) (sizes <= 4)": found,
                     "n = 43, 45, 51, 53 (w = 4), window [-8,n+8]x[-(n+8),2n+8]: knots of size 5": {k: v for k, v in five.items()},
                     "control: the searches find the 4-point knot for n=3 and a 5-point knot for n=11": control}}


def check_plane_windows() -> dict:
    r, margin = 6, 8
    table = d_norm_table(r, 6)
    window = [(a, b) for a in range(-r - margin, r + margin + 1) for b in range(-r - margin, r + margin + 1)]
    agree, disagree, bad = 0, 0, []
    for v, dn in sorted(table.items()):
        if v == (0, 0):
            continue
        if dn <= 3:
            s = smallest_vanishing_through((0, 0), v, window, 5)
            ok = s is not None and len(s) == 2 + dn
        else:
            ok = smallest_vanishing_through((0, 0), v, window, 4) is None
        agree += ok
        if not ok:
            disagree += 1
            bad.append((v, dn))
    wrong = {v: dn + 1 for v, dn in table.items() if v != (0, 0)}
    s = smallest_vanishing_through((0, 0), (3, 0), window, 5)
    control = s is not None and len(s) != 2 + wrong[(3, 0)]
    return {"pass": disagree == 0 and control,
            "info": {"vectors in [-6,6]^2": agree + disagree,
                     "smallest knot size = 2 + |v|_D (|v|_D <= 3), or none below 5 points (|v|_D = 4)": agree,
                     "disagreements": bad,
                     "control: the shifted norm |v|_D + 1 is rejected at (3,0)": control}}


def run() -> dict:
    checks = {
        "0 dependency artifacts bound by hash; upstream proofs Proved": check_dependencies(),
        "1 model: on a side-24 patch, X^a(1+X)^b vanishing = implied check of the patch law (control: another law)": check_model(),
        "2 three-point knots through the origin in [-32,32]^2 are exactly the Frobenius triangles (control)": check_three_point_knots(),
        "3 hop knots: size 2+w(n), n <= 2048, all three lattice lines (control: drop an apex)": check_hop_knots(),
        "4 lower bound inside windows: none smaller than 2+w(n) for n <= 128 (sizes <= 4) and n = 43, 45, 51, 53 (size 5)": check_lower_bound_windows(),
        "5 plane: smallest knot through 0 and v is 2+|v|_D in [-6,6]^2 (|v|_D <= 3; > 4 points at 4) (control: shifted norm)": check_plane_windows(),
    }
    failures = [name for name, value in checks.items() if not value["pass"]]
    return {"checks": checks, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
              "claim": manifest["claim"], **outcome}
    print(json.dumps(outcome, indent=1, default=str)[:5000])
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not outcome["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
