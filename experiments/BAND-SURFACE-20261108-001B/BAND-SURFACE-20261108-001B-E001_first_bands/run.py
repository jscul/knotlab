"""BAND-SURFACE-20261108-001B-E001: a census of first bands (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/BAND-SURFACE-20261108-001B/BAND-SURFACE-20261108-001B-E001_first_bands/run/result.json
    .venv/bin/python3 -B run.py --pilot   times n = 3 single rungs and prints no verdicts
Every rotation system of a loop of n rings plus one band of n rings (BAND-SURFACE-20261108-001A's band_lib), single rungs for n = 3 to 8
and double rungs for n = 3 and 4; for each balanced one (exact, GROW-NET-20261108-001A's grow_lib), its genus, face sizes, and whether a
flip fixes every contact (loopnet_lib.flip)."""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BAND-SURFACE-20261108-001A/BAND-SURFACE-20261108-001A-P001_one_band_makes_the_torus"))
import band_lib as B  # noqa: E402

G, LN = B.G, B.LN
OUT = ROOT / "artifacts" / "BAND-SURFACE-20261108-001B" / "BAND-SURFACE-20261108-001B-E001_first_bands" / "run"


def job(item):
    n, double = item
    inc, edges = B.loop_and_band(n, double)
    tot, kinds = 0, Counter()
    for rot in B.rotations(inc):
        tot += 1
        if G.balanced(rot, len(edges)):
            g, faces = B.genus_and_faces(rot, edges)
            flips = all(LN.flip(rot, edges, e) is not None for e in range(len(edges)))
            kinds[(g, flips, tuple(sorted(Counter(faces).items())))] += 1
    return n, double, tot, kinds


def main():
    t0 = time.time()
    items = [(n, False) for n in range(3, 9)] + [(3, True), (4, True)]
    if "--pilot" in sys.argv:
        job((3, False))
        print("pilot in", round(time.time() - t0, 1), "s")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(8) as pool:
        res = pool.map(job, sorted(items, key=lambda x: -(x[0] + 10 * x[1])), chunksize=1)
    by = {}
    for n, double, tot, kinds in sorted(res, key=lambda r: (r[1], r[0])):
        by["%d rings, %s rungs" % (n, "double" if double else "single")] = {
            "rotation systems": tot, "balanced": sum(kinds.values()),
            "balanced by kind": [{"genus": k[0], "a flip at every contact": k[1], "faces (size: count)": dict(k[2]), "count": v} for k, v in sorted(kinds.items())]}
    sphere = {k: sum(x["count"] for x in v["balanced by kind"] if x["genus"] == 0) for k, v in by.items()}
    torus2 = {k: sum(x["count"] for x in v["balanced by kind"] if x["genus"] == 1) for k, v in by.items() if "double" in k}
    result = {"experiment": "BAND-SURFACE-20261108-001B-E001", "by loop size": by,
              "H1 (balanced first bands on the sphere occur only for single rungs at n = 4, the cube)": all(
                  (v > 0) == (k == "4 rings, single rungs") for k, v in sphere.items()),
              "H2 (with double rungs some balanced first band has genus 1, the n x 2 torus)": all(v > 0 for v in torus2.values()),
              "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "by loop size"}, indent=1))
    for k, v in by.items():
        print(k, v["rotation systems"], v["balanced"], [(x["genus"], x["a flip at every contact"], x["count"]) for x in v["balanced by kind"]])


if __name__ == "__main__":
    main()
