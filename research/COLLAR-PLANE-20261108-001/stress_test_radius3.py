#!/usr/bin/env python3
"""One size past for COLLAR-PLANE-20261108-001A (research-next-steps, "Stress-Test Published Claims").

    python3 -B research/COLLAR-PLANE-20261108-001/stress_test_radius3.py [workers]

Ticket A checked the twice-cut rhombus lattice R_2 against the pinwheel's radius-2 dart atlas. One size past: the radius-3 atlas.
- The radius-3 atlas is computed as PINWHEEL-ATLAS-20261107-001A computed the radius-2 one (its Theorem 4): the radius-3 rooted codes
  of the darts whose tail is a corner of a descendant of a complete collar's central tile, in the j-fold cut of the collar, with j
  raised until no such dart is within distance 4 of the cut collar's edge. By Theorem 3 of ticket A these are pinwheel codes.
- Then R_2, R_3 and R_4 are tested: every interior dart's radius-3 code in that atlas? Ticket A's Theorem 3 predicts a pass from
  some number of cuts on (its bound, for tile radius 5, is 5 cuts); R_2 is the published size.
Writes stress_test_radius3.json beside this file."""
import json
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADIR = ROOT / "proofs/COLLAR-PLANE-20261108-001A/COLLAR-PLANE-20261108-001A-P001_a_periodic_plane_obeys_every_radius"
sys.path.insert(0, str(ADIR))
import check as CA  # noqa: E402

A = CA.A
R = 3


def key_codes(args):
    key, j = args
    got, short = A.collar_codes(key, j, R)
    return {c: sorted(map(str, labs)) for c, labs in got.items()}, short


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    t0 = time.time()
    keys, complete = CA.law()
    out = {"radius": R, "atlas": {}, "planes": {}}
    with mp.Pool(workers) as pool:
        for j in (4, 5):
            res = pool.map(key_codes, [(k, j) for k in complete])
            short = sum(s for _, s in res)
            out["atlas"][f"j={j}"] = {"darts near the edge": short}
            print("j", j, "short", short, round(time.time() - t0, 1), flush=True)
            if short == 0:
                break
    codes = defaultdict(set)
    for got, _ in res:
        for c, labs in got.items():
            codes[c] |= set(labs)
    out["atlas"]["codes"] = len(codes)
    out["atlas"]["codes with two labels"] = sum(1 for v in codes.values() if len(v) > 1)
    out["atlas"]["complete (no dart near the edge)"] = short == 0
    print("radius-3 atlas", len(codes), round(time.time() - t0, 1), flush=True)
    cset = set(codes)
    for k, rad in ((2, 3), (3, 2), (4, 1)):
        tiles = CA.cut_k(CA.lattice_plane(CA.RHOMBUS, CA.LATTICE_R, rad), k)
        tested, bad = CA.dart_test(tiles, cset, R)
        out["planes"][f"R_{k}"] = {"interior darts": tested, "outside the radius-3 atlas": bad, "passes": tested > 0 and bad == 0}
        print(f"R_{k}", tested, bad, round(time.time() - t0, 1), flush=True)
    # control: the rectangle lattice cut three times must fail
    tiles = CA.cut_k(CA.lattice_plane(CA.RECTANGLE, CA.LATTICE_Q, 2), 3)
    tested, bad = CA.dart_test(tiles, cset, R)
    out["control: rectangle lattice cut 3 times fails"] = {"interior darts": tested, "outside": bad, "fails": bad > 0}
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test_radius3.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
