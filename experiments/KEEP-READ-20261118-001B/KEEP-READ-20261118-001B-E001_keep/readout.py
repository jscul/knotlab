"""KEEP-READ-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read: clean-witness fractions
per tier (all classes, and classes met more than once), the in-run verified collisions, coverage, the 2 x 2 table, the candidate
rules against SEED, and predictions P1-P5.  Writes readout.json."""
import gzip
import json
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "KEEP-READ-20261118-001B", "KEEP-READ-20261118-001B-E001_keep")
TIERS = ("0", "1", "2", "c")


def load():
    f = os.path.join(OUT, "results.json")
    return json.load(open(f)) if os.path.exists(f) else json.load(gzip.open(f + ".gz", "rt"))


def main():
    res = load()["results"]
    E = [dict(e, run=i) for i, r in enumerate(res) for e in r["extensions"]]
    table = Counter((e["keep"], e["accepted"]) for e in E)
    out = {"extensions": len(E), "runs": len(res), "keep_vs_accepted": {f"keep={k} accepted={a}": v for (k, a), v in table.items()}}
    tiers = {}
    for t in TIERS:
        dirty = {"keep": set(), "accepted": set()}
        seen = Counter()
        for e in E:
            for h in e["h"][t]:
                seen[h] += 1
                if not e["keep"]:
                    dirty["keep"].add(h)
                if not e["accepted"]:
                    dirty["accepted"].add(h)
        row = {}
        for label in ("keep", "accepted"):
            pos = [e for e in E if e[label]]
            clean = [e for e in pos if any(h not in dirty[label] for h in e["h"][t])]
            rep = [e for e in pos if any(seen[h] >= 2 for h in e["h"][t])]
            clean_rep = [e for e in rep if any(h not in dirty[label] and seen[h] >= 2 for h in e["h"][t])]
            row[label] = {"positives": len(pos), "clean_witness": len(clean) / len(pos) if pos else None,
                          "repeated_positives": len(rep), "clean_witness_repeated": len(clean_rep) / len(rep) if rep else None}
        row["classes"] = len(seen)
        row["classes_repeated"] = sum(1 for v in seen.values() if v >= 2)
        row["verified_mixed_in_run"] = sum(r["verified"][t]["isomorphic"] for r in res) if t in res[0]["verified"] else None
        row["hash_mixed_in_run"] = sum(r["verified"][t]["mixed"] for r in res) if t in res[0]["verified"] else None
        tiers[t] = row
    out["tiers"] = tiers
    out["coverage"] = {"radius1_mean": statistics.mean(e["cov1"] for e in E), "radius2_mean": statistics.mean(e["cov2"] for e in E)}
    rules = {}
    for k in E[0]["rules"]:
        tp = sum(1 for e in E if e["rules"][k] and e["accepted"])
        fp = sum(1 for e in E if e["rules"][k] and not e["accepted"])
        fn = sum(1 for e in E if not e["rules"][k] and e["accepted"])
        fp_raise = sum(1 for e in E if e["rules"][k] and not e["keep"])
        rules[k] = {"true_accepts": tp, "false_accepts": fp, "missed": fn, "accepts_raising": fp_raise,
                    "recall": tp / (tp + fn) if tp + fn else None, "matches_SEED": fp == 0 and fn == 0}
    out["rules"] = rules
    T = tiers
    P = {
        "P1": T["0"]["keep"]["clean_witness"] < 1,
        "P2": T["1"]["keep"]["clean_witness"] < 1 and 0.3 <= (T["1"]["keep"]["clean_witness_repeated"] or 0) <= 0.6,
        "P3": T["2"]["keep"]["clean_witness"] < 1 or out["coverage"]["radius2_mean"] >= 0.75,
        "P4": T["c"]["keep"]["clean_witness"] >= 0.8 and T["c"]["keep"]["clean_witness"] < 1,
        "P5": (not any(v["matches_SEED"] for v in rules.values())) and rules["two_middles"]["accepts_raising"] == 0
              and 0.05 <= (rules["two_middles"]["recall"] or 0) <= 0.15,
    }
    out["predictions"] = P
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(P))
    print(json.dumps(out["tiers"], indent=1))
    print(json.dumps(out["coverage"]), json.dumps(out["keep_vs_accepted"]))
    print(json.dumps(rules, indent=1))


if __name__ == "__main__":
    main()
