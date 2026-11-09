"""Stress test for LATTICE-REACH-20261109-001, one size past check 3 of LATTICE-REACH-20261109-001A: every lattice of odd index 83 to
151 (checked to 81) of the three lattices, against the rule (composition reaches everywhere unless a digon face or the honeycomb
n x n with 3 not dividing n). Output: stress_test.json beside this script."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/LATTICE-REACH-20261109-001A/LATTICE-REACH-20261109-001A-P001_odd_index_reaches_everywhere"))
import check as K  # noqa: E402


def main():
    t0 = time.time()
    out = {}
    with Pool(20) as pool:
        for kind in ("square", "triangular", "honeycomb"):
            jobs = [(kind, B) for N in range(83, 152, 2) for B in K.hnf_lattices(N)]
            res = pool.map(K.reach_task, jobs, chunksize=2)
            exc, n, full = [], 0, 0
            for k, B, r in res:
                if not r:
                    continue
                n += 1
                full += r["contact miss"] == 0
                digon = any(K.contains(B, v) for v in K.DIGON[kind])
                pinned = kind == "honeycomb" and B[0][1] == 0 and B[1] == (0, B[0][0]) and B[0][0] % 3 != 0
                if (r["contact miss"] == 0) != (not digon and not pinned):
                    exc.append([list(map(list, B)), r])
            out[kind] = {"tori": n, "composing everywhere": full, "exceptions": exc}
    out["pass"] = all(not v["exceptions"] for v in out.values())
    out["elapsed_seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1)[:2000])


if __name__ == "__main__":
    main()
