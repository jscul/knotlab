"""C0, the gate. Usage: python -B run_c0.py trace | gate

trace: c0_trace.json, the part-round law under ALL-IN-TURN on Ring(5,3), D2(4,3) and D2(5,3)
       under the two and the three added rules, sweeps 1 to 8 (for gate G(a), compared by the
       coordinator with ticket A's complete rounds). Each sweep is also checked against this
       ticket's own complete-round function (trace numbers equal, structures the same).
gate:  c0_results.json with G(b) (the ordinary present-state law of ROUND-FREE) and G(c) (the
       sameness test).
"""

import json
import os
import sys
import time

import growth as g
import iso
import part_round as pr
from selfcheck import ART, check_sameness

STARTS = ["Ring(5,3)", "D2(4,3)", "D2(5,3)"]
KEYS = ["members", "parts", "h_sorted", "maximal_met_set_sizes_sorted", "births", "fresh_total",
        "births_sorted"]


def trace():
    out = {"description": "Part-round law under ALL-IN-TURN; one sweep moves every part once (parts made "
                          "during the sweep wait for the next). After each sweep: members, parts, sorted h "
                          "over members, sorted sizes of the inclusion-maximal met sets of the whole roster; "
                          "for the sweep: births, total fresh distinctions f (usable and barred), sorted list "
                          "of births as [number of parents, f]. 'fresh_usable_total' and 'moves' are extra.",
           "laws": {"two": "CAP-3, CANCEL-WAIT with RELEASE", "three": "CAP-3, CANCEL-WAIT with RELEASE, FILLERS"},
           "runs": {}}
    checks = []
    for start in STARTS:
        out["runs"][start] = {}
        for law in (g.TWO, g.THREE):
            run = pr.PartRoundRun(start, law, "ALL-IN-TURN")
            tr = run.run_sweeps(8)
            S, hist = g.complete_rounds(start, law, 8)
            same_trace = len(tr) == len(hist) and all(all(a[k] == b[k] for k in KEYS) for a, b in zip(tr, hist))
            # structures after each round: rebuild complete rounds round by round
            same_struct = []
            for R in range(1, 9):
                kn1 = [k for k in range(run.S.nknots()) if run.S.born[k] <= R]
                kn2 = [k for k in range(S.nknots()) if S.born[k] <= R]
                g1 = g.structure_graph(run.S, kn1, lambda k: run.S.born[k])
                g2 = g.structure_graph(S, kn2, lambda k: S.born[k])
                same_struct.append(iso.isomorphism(g1, g2) is not None)
            out["runs"][start][law.name] = tr
            checks.append({"start": start, "law": law.name, "trace_equals_own_complete_rounds": same_trace,
                           "structure_same_as_own_complete_rounds_after_each_round": same_struct})
    out["own_complete_round_check"] = checks
    path = os.path.join(ART, "c0_trace.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("written", path)
    for c in checks:
        print(c)


def gate_b():
    import birth_by_birth as bb
    res = {}
    for start in ["TWO-THREE", "LONE-FOUR"]:
        runs = []
        for seed in range(40):
            r = bb.BBB(start, rule="ANY", ration="PRESENT-ORD", shortness="FIRST-COME", order="UNIFORM",
                       seed=seed, run_id="C0-Gb", check_start_copy=False)
            r.run(max_moves=300, max_knots=10**9)
            runs.append({"seed": seed, "end": r.end, "moves": r.moves_made, "knots": r.S.nknots()})
        res[start] = {
            "runs": runs,
            "stopped": sum(1 for x in runs if x["end"] == "stopped"),
            "reached_300": sum(1 for x in runs if x["moves"] >= 300),
            "other": sum(1 for x in runs if x["end"] not in ("stopped",) and x["moves"] < 300),
        }
    two, lone = res["TWO-THREE"], res["LONE-FOUR"]
    verdict = two["stopped"] > 0 and two["reached_300"] > 0 and lone["reached_300"] >= 30
    return {"results": res, "pass": verdict,
            "rule": "TWO-THREE stops in some seeds and reaches 300 moves in others; LONE-FOUR reaches 300 in >= 30 of 40"}


def gate():
    t0 = time.time()
    out = {"G(b)": gate_b(), "G(c)": check_sameness(seed=11), "iso_stats": dict(iso.STATS),
           "time_s": round(time.time() - t0, 2)}
    path = os.path.join(ART, "c0_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("written", path)
    print("G(b)", out["G(b)"]["pass"], {k: {kk: v for kk, v in d.items() if kk != "runs"} for k, d in out["G(b)"]["results"].items()})
    print("G(c)", out["G(c)"]["pass"])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "trace"
    os.makedirs(ART, exist_ok=True)
    {"trace": trace, "gate": gate}[what]()
