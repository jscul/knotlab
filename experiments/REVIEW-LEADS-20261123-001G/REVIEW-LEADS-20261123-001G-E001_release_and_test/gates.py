"""Gate G, first clause: ticket A's code reproduces its recorded first failing steps for the seven-knot and nine-knot sources.

Recorded (ticket A, artifacts/REVIEW-LEADS-20261123-001A/.../p2_seven_knot.jsonl and p2_nine_knot_drawn.jsonl, both laws):
first failing step 1 at 15 knots (seven-knot source) and 1 at 24 knots (nine-knot drawn source).  Both laws are grown
separately here (no sharing).  Also checked (not gate clauses): the recorded stage counts agree on the common steps; the
unedited Q1 source of the reads-holders-sources study (edits.json `original_supports`, another labelling of the same source)
gives the same history and first failing step; Q2 draw 60 with two extra meetings is ticket A's nine-knot source; the routine
without the Euler shortcut gives the same verdicts at the first failing stage and the stage before it.
The second clause (recorded verdict counts) is in populations.py / gate_populations.json.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import read_test as R  # noqa: E402

A = C.A


def recorded(name, law):
    for line in (C.A_OUT / f"p2_{name}.jsonl").open():
        r = json.loads(line)
        if r["kind"] == "history" and r["law"] == law:
            return r
    raise KeyError(name)


def main():
    t0 = time.time()
    pops = C.load_populations()
    cases = {"seven_knot": (A.seven_knot_source(), 1, 15), "nine_knot_drawn": (A.nine_knot_source(), 1, 24),
             "q1_unedited_labelling": (tuple(map(tuple, pops["Q1"]["original_supports"])), 1, 15)}
    rows, ok = [], True
    for name, (stars, want_step, want_knots) in cases.items():
        for law in C.LAWS:
            h = R.grow(stars, law)
            ff = A.first_failing_stage(h["stars"], h["n_at"])
            ref = recorded("seven_knot" if name == "q1_unedited_labelling" else name, law)
            common = min(len(ref["n_at"]), len(h["n_at"]))
            no_shortcut = ([A.passes(A.incidence_graph(h["stars"], h["n_at"][t]), shortcut=False) for t in (ff - 1, ff)]
                           if ff else None)
            r = {"source": name, "law": law, "first_failing_step": ff, "knots": h["n_at"][ff] if ff is not None else None,
                 "recorded_first_failing_step": ref["first_failing_step"], "want": [want_step, want_knots],
                 "n_at": h["n_at"], "outcome": h["outcome"], "steps": h["steps"],
                 "n_at_agree_on_common_steps": h["n_at"][:common] == ref["n_at"][:common],
                 "routine_without_shortcut_pass_fail": no_shortcut}
            r["gate"] = (ff == want_step == ref["first_failing_step"] and h["n_at"][ff] == want_knots
                         and r["n_at_agree_on_common_steps"] and no_shortcut == [True, False])
            ok &= r["gate"]
            rows.append(r)
    q2 = {s["id"]: s for s in pops["Q2"]["starts"]}
    nine_is_draw60 = [list(x) for x in A.nine_knot_source()] == q2["Q2-x2-60"]["stars"]
    gp = json.loads((C.OUT / "gate_populations.json").read_text())
    out = {"sources": rows, "nine_knot_source_is_Q2_x2_60": nine_is_draw60,
           "verdict_counts_recovered": {"Q1_16_33_4": gp["Q1"]["gate_counts_16_33_4"], "Q2_5_of_192": gp["Q2"]["gate_5_of_192"]},
           "seconds": round(time.time() - t0, 1)}
    out["gate_G"] = bool(ok and nine_is_draw60 and all(out["verdict_counts_recovered"].values()))
    (C.OUT / "gates.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "sources"}, sort_keys=True))
    for r in rows:
        print(json.dumps({k: r[k] for k in ("source", "law", "first_failing_step", "knots", "outcome", "n_at", "gate")}))
    if not out["gate_G"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
