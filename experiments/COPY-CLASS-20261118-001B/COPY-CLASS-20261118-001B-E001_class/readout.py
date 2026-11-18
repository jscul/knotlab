"""COPY-CLASS-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read: agreement of CR and
CRANY with SEED, the refusal breakdown, the absorbing fills' model sizes, the copy class, and predictions P1-P5.  Writes
readout.json."""
import gzip
import json
import os
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "COPY-CLASS-20261118-001B", "COPY-CLASS-20261118-001B-E001_class")


def load():
    f = os.path.join(OUT, "results.json")
    return json.load(open(f)) if os.path.exists(f) else json.load(gzip.open(f + ".gz", "rt"))


def main():
    res = load()["results"]
    T = Counter()
    for r in res:
        T.update(r["tally"])
    agree = Counter()
    cls = Counter()
    for k, v in T.items():
        if k.startswith("seed="):
            parts = dict(x.split("=") for x in k.split())
            agree[("seed", parts["seed"], "cr", parts["cr"])] += v
            agree[("seed", parts["seed"], "crany", parts["crany"])] += v
            if parts["seed"] == "1":
                cls[parts["class"]] += v
    absorbing = [a for r in res for a in r["absorbing"]]
    dis = [d for r in res for d in r["disagreements"]]
    out = {
        "extensions": sum(r["extensions"] for r in res), "knot_sets": sum(r["knot_sets"] for r in res),
        "absorbing": len(absorbing),
        "cr_vs_seed": {f"seed={a[1]} cr={a[3]}": v for a, v in agree.items() if a[2] == "cr"},
        "crany_vs_seed": {f"seed={a[1]} crany={a[3]}": v for a, v in agree.items() if a[2] == "crany"},
        "refusals": {k[len("refusal: "):]: v for k, v in T.items() if k.startswith("refusal: ")},
        "local_not_all": T.get("local_not_all", 0),
        "absorbing_in_copy_class": dict(cls),
        "model_crossers": dict(Counter(a["model_crossers"] for a in absorbing)),
        "model_crossers_ge2": sum(1 for a in absorbing if a["model_crossers"] >= 2),
        "absorb_n_median": statistics.median(a["n"] for a in absorbing) if absorbing else None,
        "disagreements": dis[:50], "disagreement_count": len(dis),
        "by_start": {str(n0): sum(len(r["absorbing"]) for r in res if r["n0"] == n0) for n0 in (5, 6, 7, 8, 12)},
    }
    cr = out["cr_vs_seed"]
    P = {
        "P1": cr.get("seed=1 cr=0", 0) == 0 and cr.get("seed=0 cr=1", 0) == 0,
        "P2": out["crany_vs_seed"].get("seed=1 crany=0", 0) == 0 and out["crany_vs_seed"].get("seed=0 crany=1", 0) == 0
              and out["local_not_all"] == 0,
        "P3": (out["refusals"].get("(a) crossed splits come to cross", 0) > sum(v for k, v in out["refusals"].items() if k != "(a) crossed splits come to cross"))
              and out["refusals"].get("(b) a strict subset of a model's crossers", 0) > out["refusals"].get("(b) a strict superset", 0),
        "P4": out["model_crossers_ge2"] > 0,
        "P5": cls.get("0", 0) == 0,
    }
    out["predictions"] = P
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1)
    print(json.dumps(P))
    print(json.dumps({k: v for k, v in out.items() if k not in ("disagreements", "predictions")}, indent=1))
    for d in dis[:5]:
        print(d)


if __name__ == "__main__":
    main()
