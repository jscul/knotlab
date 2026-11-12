#!/usr/bin/env python3
"""After the run (stress test one size past; labelled, not frozen): the same census on the harmonies of span exactly 9 that the
frozen census (span <= 8) did not hold.

    .venv/bin/python3 -B stress_one_size_past.py [--write]"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()


def main():
    import line_lib as L
    import nest_lib as N
    old = {h["name"] for h in L.census_harmonies()}
    rows = []
    for h in N.harmonies(max_span=9, max_period=10 ** 9):
        name = " + ".join(h["orbits"])
        if name in old:
            continue
        W = sorted({sum(b << i for i, b in enumerate(w)) for w in N.states(h)})
        hh = {"name": name, "P": h["P"], "kinds": [tuple(k) for k in h["kinds"]], "states": W, "source": "span 9"}
        orbs = L.summarise(hh)
        rows.append({"harmony": name, "P": h["P"], "states": len(W), "free site": L.free_site(hh),
                     "genuine subgroups": sum(len(o["genuine subgroups"]) for o in orbs), "F4 blocks": sum(len(o["F4 blocks"]) for o in orbs),
                     "free pairs": sum(len(o["free pairs"]) for o in orbs), "genuine cosets": sum(len(o["genuine cosets"]) for o in orbs),
                     "genuine cosets a lag can give": sum(len(o["genuine cosets a lag can give"]) for o in orbs), "orbits": len(orbs)})
    out = {"new harmonies": len(rows), "periods": sorted({r["P"] for r in rows}),
           "free sites": sum(1 for r in rows if r["free site"]),
           "genuine subgroups, F4 blocks, free pairs": sum(r["genuine subgroups"] + r["F4 blocks"] + r["free pairs"] for r in rows),
           "genuine cosets": sum(r["genuine cosets"] for r in rows), "genuine cosets a lag can give": sum(r["genuine cosets a lag can give"] for r in rows),
           "rows": rows, "seconds": round(time.time() - T0, 1)}
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
    if "--write" in sys.argv:
        (HERE / "result_stress.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
