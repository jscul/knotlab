#!/usr/bin/env python3
"""Cross-check of the stress test against the crystals (CRYSTAL-UP-20261108-001).

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CRYSTAL-UP-20261108-001/stress_crosscheck.py
Every labelled parent collar of a crystal occurs in a plane obeying the law one level up, so it must survive exhaustive extension at
every distance. This reads the 26 crystals of CRYSTAL-UP-20261108-001A-E002 and the survivors of the stress test at tile distance 3
(stress_distance4.json), and counts the crystals' labelled parent collars that are neither in L(s) nor among the survivors (expect 0).
Writes stress_crosscheck.json beside this file."""
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E001_crystals_from_survivors"))
import torus_lib as T  # noqa: E402

F, D = T.F, T.D
T.light_setup()
surv = json.loads((ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone/survivors.json").read_text())
L, inL, ko, nk = T.survivor_law(surv)
st = json.loads((HERE / "stress_distance4.json").read_text())
d3 = {(yi, tuple(p)) for yi, p in st["survivors after distance 3"]["non-keys"] + st["survivors after distance 3"]["keys outside L(s)"]}
alive3 = set(inL) | d3
rows = [json.loads(x) for x in (ROOT / "artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E002_compatible_periods/run/rows.jsonl")
        .read_text().splitlines()]
tot = bad = 0
kinds = set()
for r in rows:
    for t in r["tori"]:
        cell = [tuple((Fr(x), Fr(y)) for x, y in tile) for tile, _ in t["cell"]]
        labs = [lab for _, lab in t["cell"]]
        lat = tuple(tuple(Fr(x) for x in v) for v in t["lattice"])
        plane = D.Plane(F.G["sk"], cell, lat, radius=6)
        for s, (n, coll) in enumerate(plane.root):
            yi = F.G["sets"].index(F.G["sk"].types[n][1])
            p = tuple(labs[s2] for s2, _, _ in coll)
            tot += 1
            kinds.add((yi, p))
            bad += (yi, p) not in alive3
out = {"labelled parent collars in the 26 crystals": tot, "distinct": len(kinds),
       "distinct off-law": len([k for k in kinds if k not in set(inL)]),
       "not in L(s) and not among the distance-3 survivors": bad}
(HERE / "stress_crosscheck.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
