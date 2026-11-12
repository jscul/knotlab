#!/usr/bin/env python3
"""Referee LINE-LOCK-R1, every presentation: the stitch R depends on the kind set that presents a harmony, not on its states alone
(two kind sets of the period-112 harmony 00000001111111 + 0001100011100111 + 01 give stitch pairs of sizes 24 and 9 in the census and
19 and 12 here). The census holds one kind set per harmony. This runs the same analysis on every kind set of 1 to 3 kinds of span 2 to
8 that is a harmony (the census's family), with the referee's code.

    python3 -B ref_line_presentations.py      (writes result_presentations.json)"""
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as RL  # noqa: E402
import ref_line as L  # noqa: E402
import ref_line_checks as C  # noqa: E402


def main():
    t0 = time.time()
    per = {}
    rows = []
    for span in range(2, 9):
        for S in RL.kind_sets(span):
            cyc = RL.window_cycles(S)
            if cyc is None:
                continue
            key = tuple(sorted(set(RL.canon(c) for c in cyc)))
            P = 1
            for w in key:
                P = P * len(w) // math.gcd(P, len(w))
            h = {"orbits": ["".join(map(str, w)) for w in key], "P": P}
            W = sorted(sum(b << i for i, b in enumerate(w)) for w in RL.states(h))
            hh = {"name": " + ".join(h["orbits"]), "P": P, "kinds": [tuple(k) for k in S], "W": W}
            an = [L.analyse_orbit(hh, u, o) for u, o in L.orbits(hh)]
            bl = C.blocks(hh)
            row = {"harmony": hh["name"], "P": P, "kinds": [list(k) for k in S], "free site": L.free_site(hh),
                   "|A| per orbit": [o["|A|"] for o in an],
                   "cyclic subgroups inside": sum(o["cyclic subgroups inside"] for o in an),
                   "cosets inside": sum(o["cosets inside"] for o in an),
                   "genuine subgroups": sum(len(o["genuine subgroups"]) for o in an),
                   "genuine cosets": sum(len(o["genuine cosets"]) for o in an),
                   "genuine cosets a lag can give": sum(1 for o in an for d, g, c in o["genuine cosets"] if d[0][1] == 0 and d[1][1] == 0),
                   **bl}
            rows.append(row)
            per.setdefault(hh["name"], []).append(row)
        print("span", span, "presentations so far", len(rows), "harmonies", len(per), round(time.time() - t0), "s", flush=True)
    keys = ["genuine subgroups", "genuine cosets", "genuine cosets a lag can give", "Z2xZ2 blocks", "Z2xZ2 block cosets", "free pairs",
            "free pair cosets"]
    summ = {"presentations": len(rows), "harmonies": len(per), "free sites": sum(1 for r in rows if r["free site"]),
            **{k: sum(r[k] for r in rows) for k in keys},
            "cyclic subgroups inside (all presentations)": sum(r["cyclic subgroups inside"] for r in rows),
            "cosets inside (all presentations)": sum(r["cosets inside"] for r in rows),
            "harmonies whose stitch differs between presentations": sum(1 for v in per.values() if len({json.dumps(r["|A| per orbit"]) for r in v}) > 1),
            "presentations per harmony (max)": max(len(v) for v in per.values())}
    (HERE / "result_presentations.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
