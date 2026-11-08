#!/usr/bin/env python3
"""SWITCH-READ-M1's maps: the exact native creation map of one placement (seed, hash seed), computed row by row with TRISUM-READ C's
fixed-order enumerator on the space HANDLE-COUNT A's generator gives under that hash seed (ticket A's sw_lib.generate). This is how the
nine maps in stress_test_m1_maps.json.gz were made (run `sw-maps1`, docs/LONG_RUNNING.md; 4 to 20 minutes each with 20 processes).

    python3 -B research/SWITCH-READ-20261108-001/stress_test_m1_map.py SEED HASHSEED OUT.json.gz [processes]
Run from the repository root with its .venv."""
import gzip
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "proofs/SWITCH-READ-20261108-001A/SWITCH-READ-20261108-001A-P001_placements_in_one_switching_class"))
sys.path.insert(0, str(ROOT / "proofs/TRISUM-READ-20261107-001C/TRISUM-READ-20261107-001C-P001_one_size_past_four_junctions"))
import sw_lib as SW  # noqa: E402
import order_lib as OL  # noqa: E402

OL.TR.engine()
SEED, HS = int(sys.argv[1]), int(sys.argv[2])
PLACE = json.loads((Path(SW.__file__).parent / "placements.json").read_text())
H = [tuple(l) for l in SW.generate(sorted(int(s) for s in PLACE), HS)[SEED]["lines"]]
N = 1 + max(max(l) for l in H)
W, S0, ORDER = OL.fixed_order(H, N)


def row(M):
    out, ns = OL.exact_row(H, N, M, ORDER)
    return M, {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()}, ns


if __name__ == "__main__":
    t0 = time.time()
    rows = {}
    with Pool(int(sys.argv[4]) if len(sys.argv) > 4 else 20) as pool:
        for M, out, ns in pool.imap_unordered(row, range(len(H)), chunksize=1):
            rows[str(M)] = {"row": out, "solutions": ns}
    path = sys.argv[3]
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump({"seed": SEED, "hash seed": HS, "lines": [list(l) for l in H], "points": N, "rows": rows}, f, sort_keys=True)
    os.replace(path + ".tmp", path)
    print("seed", SEED, "hash seed", HS, "lines", len(H), "order width", W, "done", round(time.time() - t0, 1), "s", flush=True)
