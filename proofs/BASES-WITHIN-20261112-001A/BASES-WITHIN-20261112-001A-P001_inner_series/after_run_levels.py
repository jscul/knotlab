#!/usr/bin/env python3
"""After the run, descriptive (not frozen): E1 was dropped at its 1-hour cap (its level-3 enumerations, capped at 100,000 states on
up to 4,096 distinctions, did not finish). This reduced follow-up uses the frozen functions of nest_lib.py: level 2 of every
harmony, capped at 20,000 states, with its known states and the level-2 tie check of L7; and level 3 of 0011 alone (P1).

    .venv/bin/python3 -B after_run_levels.py --write"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def job(n):
    import nest_lib as N
    h = N.harmonies()[n]
    t = time.time()
    c = N.axial_count(h, 2, cap=20000)
    known = N.known_arrays(h, 2)
    line = N.harmony_line_ties(h)
    knots, idx = N.axial_knots(h, 2)
    tied = N.tie_class(knots, len(idx), idx[(0, 0)])
    inv = {v: co for co, v in idx.items()}
    row = {"n": n, "orbits": h["orbits"], "P": h["P"], "states": len(N.states(h)), "level 2": c, "known": known,
           "rigid (only linear states)": None if c is None else c == known["linear"],
           "not below the known states": c is None or c >= known["union"],
           "line ties of place 0": sorted(line), "level 2 ties = product of line ties": {inv[v] for v in tied} == {(i, j) for i in line for j in line},
           "seconds": round(time.time() - t, 1)}
    if h["orbits"] == ["0011"]:
        row["level 3"] = N.axial_count(h, 3, cap=20000)
    return row


if __name__ == "__main__":
    import nest_lib as N
    n = len(N.harmonies())
    with Pool(8) as pool:
        rows = pool.map(job, range(n), chunksize=1)
    out = {"status": "descriptive, after the run", "rows": rows}
    if "--write" in sys.argv:
        (HERE / "result_after_run_levels.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps([(r["orbits"], r["level 2"], r["rigid (only linear states)"]) for r in rows])[:3000])
