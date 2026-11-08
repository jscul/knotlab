"""INTERMITTENT-NET-20261108-001B-E001: are the composing lags native? (exploratory; see contract.json)

    .venv/bin/python3 -B run.py           the census; writes artifacts/INTERMITTENT-NET-20261108-001B/
                                          INTERMITTENT-NET-20261108-001B-E001_native_lags/run/rows.json and result.json
    .venv/bin/python3 -B run.py --sizes 5,7,5 5,8,5 --out stress   the same measures at other sizes (the stress test), written to
                                          research/INTERMITTENT-NET-20261108-001/stress_rows.json and stress_result.json"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/INTERMITTENT-NET-20261108-001A/INTERMITTENT-NET-20261108-001A-P001_when_intermittent_composition_is_a_law"))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import intermittent_lib as I  # noqa: E402
import time_knots_lib as K  # noqa: E402

C, S, P = I.C, I.S, I.P
OUT = ROOT / "artifacts" / "INTERMITTENT-NET-20261108-001B" / "INTERMITTENT-NET-20261108-001B-E001_native_lags" / "run"
SIZES = ((3, 4, 3), (4, 4, 4), (4, 5, 4), (4, 6, 4), (5, 6, 5))
COLUMNS = ["rule", "mA", "mB", "mC", "family", "law", "repeat from", "period", "composing cycle lags", "arrival cycle lags",
           "both-binding cycle lags", "composing lags equal arrival lags", "composing lags inside both-binding lags"]


def mask(cyc, f):
    return sum(1 << i for i, x in enumerate(cyc) if f(x))


def job(args):
    r, mA, mB, mC, family, law = args
    rows, T1, period = I.profile(r, mA, mB, mC, family, law)
    if T1 is None:
        return [r, mA, mB, mC, family, law, None, None, None, None, None, None, None]
    cyc = I.cycle(rows, T1, period)
    comp = mask(cyc, lambda x: x[0])
    arrive = mask(cyc, lambda x: x[1] and x[2])
    both = mask(cyc, lambda x: x[3] and x[4])
    return [r, mA, mB, mC, family, law, T1, period, bin(comp).count("1"), bin(arrive).count("1"), bin(both).count("1"),
            comp == arrive, (comp & ~both) == 0]


def main():
    t0 = time.time()
    sizes = SIZES
    out_dir, prefix = OUT, ""
    if "--sizes" in sys.argv:
        i = sys.argv.index("--sizes")
        sizes = tuple(tuple(int(v) for v in s.split(",")) for s in sys.argv[i + 1:] if "," in s)
        out_dir, prefix = ROOT / "research" / "INTERMITTENT-NET-20261108-001", "stress_"
    reps = K.classes()
    laws = [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", u) for u in S.NONCONSTANT_TWO]
    jobs = [(r, *size, fam, law) for size in sizes for r in reps for fam, law in laws]
    jobs.sort(key=lambda j: -(j[1] + j[2] + j[3]))
    out_dir.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=4)
    rec = [dict(zip(COLUMNS, row)) for row in rows]
    dec = [x for x in rec if x["repeat from"] is not None]
    comp = [x for x in dec if x["composing cycle lags"]]
    lin = set(P.LINEAR) | set(P.AFFINE)
    h1_fail = [x for x in comp if not x["composing lags equal arrival lags"]]
    h2_fail = [x for x in comp if not x["composing lags inside both-binding lags"]]
    native = [x for x in comp if x["composing lags equal arrival lags"] and x["composing lags inside both-binding lags"]]
    groups = defaultdict(set)
    for x in comp:
        groups[(x["rule"], x["family"], x["law"])].add((x["mA"], x["mB"], x["mC"]))
    decided_sizes = defaultdict(set)
    for x in dec:
        decided_sizes[(x["rule"], x["family"], x["law"])].add((x["mA"], x["mB"], x["mC"]))
    h3_fail = {g: sorted(s) for g, s in groups.items() if s != decided_sizes[g]}
    controls = {"linear and affine chains satisfy the arrival law (Theorem 2)": all(x["composing lags equal arrival lags"] for x in comp
                                                                                    if x["rule"] in lin and (x["family"] == "proposals" or x["law"] in S.AFFINE_TWO)),
                "every row is decided or reported undecided": len(rec) == len(jobs)}
    ex = lambda xs: [[x["rule"], f"{x['mA']}/{x['mB']}/{x['mC']}", x["family"], x["law"], x["period"], x["composing cycle lags"],
                      x["arrival cycle lags"], x["both-binding cycle lags"]] for x in xs[:20]]
    result = {
        "experiment": "INTERMITTENT-NET-20261108-001B-E001", "sizes": [list(s) for s in sizes], "chains": len(rec),
        "undecided": len(rec) - len(dec), "controls": controls, "controls_ok": all(controls.values()),
        "chains composing at recurring lags": len(comp),
        "by size": {"/".join(map(str, s)): sum(1 for x in comp if (x["mA"], x["mB"], x["mC"]) == s) for s in sizes},
        "H1 arrival (composing lags = arrival lags)": len(h1_fail) == 0, "H1 failures": len(h1_fail),
        "H1 failures (examples: rule, sizes, family, law, period, composing, arrival, both-binding)": ex(h1_fail),
        "H2 coexistence (composing lags inside both-binding lags)": len(h2_fail) == 0, "H2 failures": len(h2_fail),
        "H2 failures (examples)": ex(h2_fail),
        "chains whose composing lags are singled out (H1 and H2)": len(native),
        "rules among them": dict(Counter(x["rule"] for x in native).most_common(20)),
        "H3 transport (a rule and law composing at one size compose at every decided size)": len(h3_fail) == 0,
        "rule-law groups composing somewhere": len(groups), "H3 failures": len(h3_fail),
        "H3 failures (examples: group, sizes where it composes)": [[list(g), [list(s) for s in v]] for g, v in list(h3_fail.items())[:20]],
        "groups composing at every decided size": sorted([list(g) for g in groups if g not in h3_fail]),
        "seconds": round(time.time() - t0, 1)}
    (out_dir / f"{prefix}rows.json").write_text(json.dumps({"columns": COLUMNS, "rows": rows}) + "\n")
    (out_dir / f"{prefix}result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1)[:7000])


if __name__ == "__main__":
    main()
