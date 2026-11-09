#!/usr/bin/env python3
"""Stress test for GROWN-DISTANCE-20261109-001, one size past every computed claim:
- the square tori holding (2, 1) or a rotation of it (computed to index 100) at index 101 to 140, and their mirror images (late from 8);
- the triangular tori holding a vector of length sqrt 3 (computed to index 80) at index 81 to 110;
- the ladders (proved; checked to n = 200) at n = 201 to 230, both twists;
- the rectangular tori (proved; read to 10 x 40) for 2 <= n <= 14, n <= m <= 60.
Writes stress_test.json beside this file."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/GROWN-DISTANCE-20261109-001A/GROWN-DISTANCE-20261109-001A-P001_the_grown_torus_reads_distance_plainly_only_as_a_ladder"))
import grown_lib as GL  # noqa: E402

T0 = time.time()
R1 = {(2, 1), (-1, 2), (-2, -1), (1, -2)}
R2 = {(1, 2), (-2, 1), (-1, -2), (2, -1)}
out = {}


def family(kind, lo, hi, member):
    on = late = 0
    bad = []
    for B in GL.hermite_bases(hi, lo):
        n2, s = GL.shortest(kind, B)
        if not member(n2, s):
            continue
        T = GL.torus(kind, B)
        if T is None:
            continue
        ok, v = GL.on_time(*T, kind)
        on += ok
        late += not ok
        if not ok:
            bad.append(B)
    print(kind, lo, hi, on, late, round(time.time() - T0), "s", flush=True)
    return {"on time": on, "late": late, "late bases": bad[:20]}


out["square (2,1) tubes, index 101-140"] = family("square", 101, 140, lambda n2, s: n2 == 5 and s in R1)
out["square (1,2) tubes, index 101-140"] = family("square", 101, 140, lambda n2, s: n2 == 5 and s in R2)
out["triangular sqrt 3 tubes, index 81-110"] = family("triangular", 81, 110, lambda n2, s: n2 == 3)
lad = []
for a in range(201, 231):
    for t in (0, 1):
        ok, v = GL.on_time(*GL.torus("square", ((a, t), (0, 2))), "square")
        if not ok:
            lad.append((a, t))
out["ladders n = 201-230, both twists"] = {"late": lad}
print("ladders", lad, round(time.time() - T0), "s", flush=True)
rect = []
for n in range(2, 15):
    for m in range(n, 61):
        if GL.on_time(*GL.G.rect_torus(n, m), "square")[0]:
            rect.append((n, m))
out["rectangular n x m, 2 <= n <= 14, n <= m <= 60: on time"] = rect
print("rect", rect[-3:], round(time.time() - T0), "s", flush=True)
out["pass"] = (out["square (2,1) tubes, index 101-140"]["late"] == 0 and out["triangular sqrt 3 tubes, index 81-110"]["late"] == 0
               and out["square (1,2) tubes, index 101-140"]["on time"] == 0 and not lad
               and rect == [(2, m) for m in range(2, 61)] + [(3, 3)])
out["seconds"] = round(time.time() - T0)
(HERE / "stress_test.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
print("PASS" if out["pass"] else "FAIL")
