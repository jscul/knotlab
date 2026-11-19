"""Readout of the referee's joint check (runs/referee-states, from job_states.py), against the studies' records read as data
(runs/states-growth, runs/many-valued, runs/dropped-junction).

  ../../../.venv/bin/python -B states_readout.py > referee_states.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/NAE-GROWTH-20261119-001/referee-R1"))


def lines(run):
    return [json.loads(x) for x in open(ROOT / "runs" / run / "results.jsonl")]


def main():
    import referee_nae as RN
    st = RN.load_stages()
    R = {r["case"]: r for r in lines("referee-states")}
    bad = sorted(c for c, r in R.items() if r["status"] != "ok")
    X = {c: r["result"] for c, r in R.items() if r["status"] == "ok"}
    # part B
    mine = {}
    for c in X:
        if c.startswith("B-"):
            for s in X[c]["stages"]:
                mine.setdefault((json.dumps(st[s["i"]]["key"]), st[s["i"]]["round"]), []).append(s)
    theirs = {}
    for r in lines("states-growth"):
        if r["case"].startswith("B-"):
            for s in r["result"]["stages"]:
                theirs.setdefault((json.dumps(s["key"]), s["round"]), []).append(s)
    agree = sum(sorted((x["verdict at the cut"], x["redundant"]) for x in mine[k]) ==
                sorted((x["verdict"], int(x["redundant"])) for x in theirs[k]) for k in theirs)
    allm = [x for v in mine.values() for x in v]
    irr = [x for x in allm if not x["redundant"]]
    B = {"stages": len(allm), "the study's verdict and redundancy reproduced at its cut": agree,
         "stages with a minimal constraint above the cut": sum(x["constraints above the cut"] > 0 for x in allm),
         "verdicts at the cut": dict(Counter(f"{x['verdict at the cut']} / {'redundant' if x['redundant'] else 'irredundant'}" for x in allm)),
         "verdicts, every minimal constraint": dict(Counter(f"{x['verdict']} / {'redundant' if x['redundant'] else 'irredundant'}" for x in allm)),
         "saturated share of irredundant stages: at the cut, every constraint": [
             round(sum(x["verdict at the cut"] == "saturated" for x in irr) / len(irr), 4),
             round(sum(x["verdict"] == "saturated" for x in irr) / len(irr), 4)],
         "saturated at the cut but not with every constraint": sum(x["verdict at the cut"] == "saturated" and x["verdict"] != "saturated" for x in allm)}
    # part T
    T = [t for c in sorted(X) if c.startswith("T-") for t in X[c]["trajectories"]]
    nored = [t for t in T if not t["redundant"]]
    fail = [t for t in nored if not (all(t["agree"]) and not any(":" in v and not v.endswith("unique") for v in t["verdicts"]))]
    Tsum = {"trajectories": len(T), "without a redundant knot": len(nored),
            "... refined rule (every constraint) defined and equal to the cheapest growth at every round": len(nored) - len(fail),
            "... not": [{"key": t["key"], "verdicts": t["verdicts"], "agree": t["agree"], "presentations": t["presentations"]} for t in fail],
            "first verdicts": dict(Counter(t["verdicts"][0] if t["verdicts"] else "-" for t in T)),
            "points not saturated (every constraint), with their presentation counts (presentations, classes)":
                dict(Counter(f"{p[4]}: {p[1]} / {p[2]}{' capped' if p[3] else ''}" for t in T for p in t["presentations"])),
            "trajectories meeting an unsaturated stage": sum(bool(t["presentations"]) for t in T)}
    # part D
    D = X.get("D", {})
    P = [p for p in D.get("pairs", []) if p["same states"]]
    both = [p for p in P if all(p["three-connected"])]
    Dsum = {"distinct presentations": D.get("distinct presentations"), "table collisions": D.get("table collisions"),
            "same-state pairs": len(P), "both completed systems three-connected (referee's test)": len(both),
            "... nx test agrees": sum(p["three-connected"] == p["nx three-connected"] for p in P),
            "... isomorphism inducing the renaming (Whitney)": sum(p["isomorphism inducing the renaming"] for p in both),
            "plain isomorphism, all same-state pairs": sum(p["plain isomorphism"] for p in P),
            "isomorphism inducing the renaming, all same-state pairs": sum(p["isomorphism inducing the renaming"] for p in P)}
    # part P
    S = [s for c in sorted(X) if c.startswith("P-") for s in X[c]["starts"]]
    ch = [(s["name"], c) for s in S for c in s["choices"]]
    Psum = {"starts": len(S), "eddies": sum(not s["name"].startswith("S-") for s in S), "choices": len(ch),
            "same parity states as the original": sum(c["same states"] for _, c in ch),
            "first 20 counts equal to the study's": sum(c.get("counts equal (first 20)", False) for _, c in ch),
            "choices with a junction of fewer than three places": sum(c.get("smallest junction", 3) < 3 for _, c in ch),
            "eddies: exponential choices other than the original (study's class)": sum(
                1 for n, c in ch if not n.startswith("S-") and c["drop"] != "out" and c.get("class (study)") == "exponential"),
            "eddies: original exponential (study's class)": sum(1 for n, c in ch if not n.startswith("S-") and c["drop"] == "out"
                                                                and c.get("class (study)") == "exponential"),
            "mismatched counts": [(n, c["drop"], c.get("counts")) for n, c in ch if not c.get("counts equal (first 20)", False)][:10]}
    print(json.dumps({"cases not ok": bad, "B": B, "T": Tsum, "D": Dsum, "X": X.get("X"), "P": Psum, "P detail": S}, indent=1, default=str))


if __name__ == "__main__":
    main()
