"""Stress test for HONEY-REACH-20261109-001, one size past the checks of HONEY-REACH-20261109-001A: the mirror lines, the turn-fixed
ring, full reach when 3 | n and the count formula on sides 201 to 300 (checked to 200); the contact level on sides 17 to 20 (checked to
16); the cell level on sides 8 and 9 (checked to 7). Output: stress_test.json beside this script."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/HONEY-REACH-20261109-001A/HONEY-REACH-20261109-001A-P001_three_divides_the_side"))
import check as C  # noqa: E402

H = C.H


def main():
    t0 = time.time()
    out = {}
    with Pool(12) as pool:
        mir = pool.map(C.task_mirrors, range(201, 301))
        cen = pool.map(C.task_census, range(201, 301))
        con = pool.map(C.task_contact_level, range(17, 21))
        cel = pool.map(C.task_cells, [(8, 2), (9, 2)])
    out["mirror lines, sides 201 to 300"] = all(ok for n, ok, d in mir)
    out["turn-fixed ring never needs A(0), 3 not dividing n"] = all(c["hexagram on mirrors"] and c["B(t,t) never needs A(0)"]
                                                                   for c in cen if c["n"] % 3)
    out["full reach exactly when 3 | n"] = all((c["A"] + c["B"] == 0) == (c["n"] % 3 == 0) for c in cen)
    out["count formula"] = all(c["A"] + c["B"] == H.predicted_misses(c["n"]) for c in cen)
    out["counts not 1"] = {str(c["n"]): c["A"] + c["B"] for c in cen if c["A"] + c["B"] > 1}
    out["odd sides with zeros off the mirror lines"] = [c["n"] for c in cen if c["n"] % 2 and c["extra zeros"]]
    out["contact level, sides 17 to 20"] = {str(n): ok for n, ok, p in con}
    out["cell level, sides 8 and 9"] = {"%d/g=%d" % (n, g): ok for n, g, ok, p in cel}
    out["elapsed_seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
