#!/usr/bin/env python3
"""After the run (descriptive; not frozen): the tiling reading of 0011 + 01, and the lock rule of 0011, against the lock shapes of
after_run_wedge.py (n, m = 2..16).

    .venv/bin/python3 -B after_run_tiling.py [--write]
- 0011 + 01: on the orbit of 0011 the increments are {(0,0), (1,2), (1,3), (2,3)} mod 4; a state with no constant cell lifts to a
  height function with cells (1, -2), (1, -1), (2, -1). Counting cells of each type, windings S_c, S_r (multiples of 4) must satisfy
  S_c / m >= 1, S_r / n >= 1, S_c / m + S_r / n <= 3 (the slope polygon). Predicted: the repeat locks iff no such pair exists.
- The found states with no short step for 0011 + 01: which orbit they use and which cell types.
- 0011: locks iff 4 does not divide m and gcd(n, m) <= 3."""
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def polygon_point(n, m):
    return any(F(Sc, m) + F(Sr, n) <= 3 for Sc in range(m, 2 * m + 1) if Sc % 4 == 0 for Sr in range(n, 2 * n + 1) if Sr % 4 == 0)


def main():
    import shift_lib as L
    wedge = {r["harmony"]: r for r in json.loads((HERE / "result_after_run_wedge.json").read_text())["rows"]}
    NS = range(2, 17)
    out = {}
    r = wedge["0011 + 01"]
    out["0011 + 01: locked exactly when the slope polygon has no point (n, m = 2..16)"] = [
        sum((m in r["locked"][str(n)]) == (not polygon_point(n, m)) for n in NS for m in NS), len(NS) ** 2]
    r = wedge["0011"]
    out["0011: locked exactly when 4 does not divide m and gcd(n, m) <= 3 (n, m = 2..16)"] = [
        sum((m in r["locked"][str(n)]) == (m % 4 != 0 and math.gcd(n, m) <= 3) for n in NS for m in NS), len(NS) ** 2]
    h = [x for x in L.harmonies() if L.name(x) == "0011 + 01"][0]
    S = L.setup(h)
    phase, y = {}, 0b1100
    for k in range(4):
        phase[S["W"].index(y)] = k
        y = L.L.rot(y, 1, S["P"])
    two = json.loads((HERE / "result_two.json").read_text())["checks"]["result"]["rows"]
    rows = []
    for x in [rr for rr in two if rr["harmony"] == "0011 + 01"][0]["rows"]:
        if x["unlocks"] and x["short"] is False:
            X, n, m = x["broad state"], x["n"], x["m"]
            v = L.cell(n, m)
            only = all(s in phase for s in X)
            types = sorted({((phase[X[v(a, b + 1)]] - phase[X[v(a, b)]]) % 4, (phase[X[v(a + 1, b)]] - phase[X[v(a, b)]]) % 4)
                            for a in range(n) for b in range(m)}) if only else None
            rows.append({"n": n, "m": m, "uses only the orbit of 0011": only, "cell types": types})
    out["0011 + 01: the found states with no short step"] = rows
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list) or len(v) == 2}, indent=1))
    print(sum(1 for r in rows if r["uses only the orbit of 0011"] and r["cell types"] == [[1, 2], [1, 3], [2, 3]]
              or r["cell types"] == [(1, 2), (1, 3), (2, 3)]), "of", len(rows), "states: the orbit of 0011, all three cell types")
    if "--write" in sys.argv:
        (HERE / "result_after_run_tiling.json").write_text(json.dumps(out, indent=1, default=list) + "\n")


if __name__ == "__main__":
    main()
