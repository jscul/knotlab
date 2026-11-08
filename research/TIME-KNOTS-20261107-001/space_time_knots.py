#!/usr/bin/env python3
"""The correction of 2026-11-08 to TIME-KNOTS-20261107-001 (docs/CORRECTIONS.md): the census's knot-free rules, read on their whole
space-time law instead of their two-time law.

    .venv/bin/python3 -B research/TIME-KNOTS-20261107-001/space_time_knots.py   writes space_time_knots.json
The law is cut to the cone of a first-row window of w cells: row t keeps the cells t..w-1-t, each a function of the window. That is
a projection of the whole law, so every knot found in it is a knot of the whole law (a set's verdict depends only on the projection
on it); a window without a knot shows nothing beyond itself. Reuses GROWTH-LAW-20261107-001A's generic K1-K3 enumerator, a few
seconds in all."""
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import growth_law_lib as G  # noqa: E402

T0 = time.time()
CENSUS = ROOT / "artifacts/TIME-KNOTS-20261107-001B/TIME-KNOTS-20261107-001B-E001_elementary_census/run/result.json"


def cone(rule, w, T):
    cells = [(t, i) for t in range(T + 1) for i in range(t, w - t)]
    idx = {c: k for k, c in enumerate(cells)}
    rows = set()
    for u in range(1 << w):
        v = {(0, i): (u >> i) & 1 for i in range(w)}
        for t in range(1, T + 1):
            for i in range(t, w - t):
                v[(t, i)] = (rule >> (4 * v[(t - 1, i - 1)] + 2 * v[(t - 1, i)] + v[(t - 1, i + 1)])) & 1
        rows.add(sum(v[c] << idx[c] for c in cells))
    return cells, G.Rel([f"x({t},{i})" for t, i in cells], sorted(rows))


def survey(rule, w, T, max_size=None):
    cells, R = cone(rule, w, T)
    kn = G.minimal_constrained(R, max_size)
    kn = [S for S in kn if bin(S).count("1") >= 3]
    met = Counter()
    first = None
    for S in sorted(kn, key=lambda S: (bin(S).count("1"), S)):
        times = {cells[j][0] for j in range(len(cells)) if S >> j & 1}
        met[len(times)] += 1
        if len(times) >= 2 and first is None:
            first = [list(cells[j]) for j in range(len(cells)) if S >> j & 1]
    return {"window": w, "T": T, "variables": len(cells), "knots up to": max_size or "all", "knots": len(kn),
            "by number of times met": {str(k): v for k, v in sorted(met.items())}, "first knot meeting two times": first}


def main():
    free = json.loads(CENSUS.read_text())["classes of behaviour"]["knot-free at every lag"]
    out = {"two-time knot-free rules (ticket B)": free, "rules": {}}
    for r in free:
        rows = [survey(r, 7, 3)]
        if rows[0]["knots"]:
            rows.append(survey(r, 9, 2))
        else:
            rows += [survey(r, 9, 3, max_size=5), survey(r, 11, 2, max_size=5)]
        out["rules"][str(r)] = rows
        print(r, [(x["window"], x["T"], x["knots"], x["by number of times met"]) for x in rows], round(time.time() - T0, 1), "s",
              flush=True)
    # the example of the correction, checked directly: x(1,1) and x(2,4) on force x(1,2) on under rule 128 (all of x(0,0..6) on)
    cells, R = cone(128, 7, 2)
    out["rule 128: {x(1,1), x(1,2), x(2,4)} is a knot"] = G.is_knot_set(R, ["x(1,1)", "x(1,2)", "x(2,4)"])
    out["rule 128: {x(1,1), x(1,2), x(1,3)} is a knot (its image never shows 1 0 1)"] = G.is_knot_set(R, ["x(1,1)", "x(1,2)", "x(1,3)"])
    with_knots = sorted(int(r) for r, rows in out["rules"].items() if any(x["knots"] for x in rows))
    across = sorted(int(r) for r, rows in out["rules"].items() if any(x["first knot meeting two times"] for x in rows))
    out["rules with a knot of the whole law in some window"] = with_knots
    out["rules with a knot meeting two times in some window"] = across
    out["rules with no knot in any window (all knots at w = 7, T = 3; up to 5 places at w = 9, T = 3 and w = 11, T = 2)"] = sorted(
        int(r) for r in out["rules"] if int(r) not in with_knots)
    out["seconds"] = round(time.time() - T0, 1)
    (HERE / "space_time_knots.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rules"}, indent=1))


if __name__ == "__main__":
    main()
