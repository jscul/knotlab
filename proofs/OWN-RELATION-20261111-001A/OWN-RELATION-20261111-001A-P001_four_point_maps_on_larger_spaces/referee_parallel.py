#!/usr/bin/env python3
"""After the freeze: runs own_referee.py's frozen functions (r1, count_space) unchanged, over the exported spaces in parallel, and
writes referee.json exactly as own_referee.main() would. Added because the serial referee would take about two hours."""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import own_referee as R  # noqa: E402

OUT1, CLS_OF = R.r1()


def one(sp):
    return sp["label"], R.count_space(sp, CLS_OF)


def main():
    spaces = json.loads((HERE / "spaces.json").read_text())["spaces"]
    census = {r["label"]: r for r in json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]}
    order = sorted(spaces, key=lambda s: -(s["n"] * len(s["classes"])))
    with Pool(20) as pool:
        mine = dict(pool.map(one, order, chunksize=1))
    rows = []
    for sp in spaces:
        theirs = {k: census[sp["label"]]["tally"].get(k, 0) for k in "ABCD"}
        rows.append({"label": sp["label"], "referee": mine[sp["label"]], "census": theirs, "agree": mine[sp["label"]] == theirs})
    res = {"R1 classes": OUT1, "R2 spaces": rows,
           "passed": OUT1["orbits using all four inputs"] == 4 and OUT1["orbits that can give a mod-3 bit"] == ["C", "D"]
           and all(r["agree"] for r in rows)}
    (HERE / "referee.json").write_text(json.dumps(res, indent=1) + "\n")
    print("referee passed" if res["passed"] else "referee FAILED")
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
