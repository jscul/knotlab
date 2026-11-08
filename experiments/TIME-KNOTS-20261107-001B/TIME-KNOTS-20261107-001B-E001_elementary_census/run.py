"""TIME-KNOTS-20261107-001B-E001: which elementary automata bind their past in knots (exploratory; see contract.json).

    .venv/bin/python3 -B run.py
Writes artifacts/TIME-KNOTS-20261107-001B/TIME-KNOTS-20261107-001B-E001_elementary_census/run/rows.json and result.json."""
from __future__ import annotations

import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import time_knots_lib as K  # noqa: E402

OUT = ROOT / "artifacts" / "TIME-KNOTS-20261107-001B" / "TIME-KNOTS-20261107-001B-E001_elementary_census" / "run"
LAGS = range(1, 7)


def term_or_clause(F, n):
    dep = K.depends(F, n)
    vs = [j for j in range(n) if dep >> j & 1]
    u = np.arange(1 << n)
    for signs in itertools.product((0, 1), repeat=len(vs)):
        lits = [((u >> j) & 1) == s for j, s in zip(vs, signs)]
        if (np.logical_and.reduce(lits).astype(np.uint8) == F).all() or (np.logical_or.reduce(lits).astype(np.uint8) == F).all():
            return True
    return False


def measure(rule, T):
    n = 2 * T + 1
    F = K.t_step_map(rule, T)
    kn, ties, const = K.knots_across_time(F, n)
    sizes = sorted(bin(S).count("1") + 1 for S in kn)
    centre = [bin(S).count("1") + 1 for S in kn if S >> T & 1]
    return {"T": T, "constant": const, "knots": len(kn), "ties": len(ties),
            "knot sizes": dict(sorted(Counter(sizes).items())), "least knot": sizes[0] if sizes else None,
            "centre in a knot": bool(centre), "least knot through the centre": min(centre) if centre else None,
            "depends on": bin(K.depends(F, n)).count("1"),
            "term or clause": (not const) and (not kn) and term_or_clause(F, n)}


def behaviour(ms):
    counts = [m["knots"] for m in ms]
    if all(c == 0 for c in counts):
        return "knot-free at every lag"
    if all(c == 1 for c in counts):
        return "one knot at every lag"
    if all(c > 0 for c in counts) and all(b > a for a, b in zip(counts, counts[1:])):
        return "knots at every lag, growing"
    return "other"


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = {}
    for r in K.classes():
        rows[r] = [measure(r, T) for T in LAGS]
    controls = {
        "linear rules one knot of Theorem 3's size": all(
            [m["knots"] for m in rows[r]] == [1] * len(LAGS)
            and [m["least knot"] for m in rows[r]] == [len(K.poly_power_support(p, T)) + 1 for T in LAGS]
            for r, p in ((60, {-1, 0}), (90, {-1, 1}), (150, {-1, 0, 1}))),
        "AND (rule 128, whose class holds OR, rule 254) knot-free with 2T + 1 ties": 128 in rows and K.complement(254) == 128
            and all(m["knots"] == 0 and m["ties"] == 2 * m["T"] + 1 for m in rows[128]),
        "every knot-free map is constant or a term or clause": all(
            m["constant"] or m["knots"] > 0 or m["term or clause"] for ms in rows.values() for m in ms),
    }
    classes = {}
    for r, ms in rows.items():
        classes.setdefault(behaviour(ms), []).append(r)
    first_knot = {r: next((m["T"] for m in ms if m["knots"]), None) for r, ms in rows.items()}
    late = {r: t for r, t in first_knot.items() if t and t > 1}
    growing = classes.get("knots at every lag, growing", [])
    pattern = {r: [m["least knot through the centre"] for m in rows[r]] for r in growing}
    t_plus_2 = [r for r, seq in pattern.items() if seq == [T + 2 for T in LAGS]]
    result = {
        "experiment": "TIME-KNOTS-20261107-001B-E001", "rules": len(rows), "lags": list(LAGS), "controls": controls,
        "controls_ok": all(controls.values()),
        "classes of behaviour": {k: sorted(v) for k, v in sorted(classes.items())},
        "class sizes": {k: len(v) for k, v in sorted(classes.items())},
        "rules whose first knot comes after lag 1": late,
        "growing rules whose least knot through the centre is T + 2 at every lag": sorted(t_plus_2),
        "growing rules with another least-knot sequence": {r: seq for r, seq in pattern.items() if r not in t_plus_2},
        "seconds": round(time.time() - t0, 1),
    }
    (OUT / "rows.json").write_text(json.dumps({str(r): ms for r, ms in rows.items()}, indent=1) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
