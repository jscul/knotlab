"""KNOT-SWITCH-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read; it computes W3 at
every step, predictions Q1-Q4, SEEDK's tiers and descriptive readings of the knot complex, and writes readout.json."""
import gzip
import json
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "KNOT-SWITCH-20261118-001B", "KNOT-SWITCH-20261118-001B-E001_switch")


def load():
    f = os.path.join(OUT, "results.json")
    return json.load(open(f)) if os.path.exists(f) else json.load(gzip.open(f + ".gz", "rt"))


def main():
    res = load()["S1"]["results"]
    W3 = Counter()
    Q2 = Counter()
    by = defaultdict(list)
    for r in res:
        rows = [x for x in r["trace"] if "stopped" not in x]
        fills = 0
        for x in rows:
            if x.get("kind") == "fill":
                fills += 1
            readings = (x["nothing_crosses"], x["filled_knots"] == 0, x["b2"] == 0, fills == 0)
            W3[len(set(readings)) == 1] += 1
            Q2[x["full_four"] == (not x["nothing_crosses"])] += 1
        first_fill = next((i for i, x in enumerate(rows) if x.get("kind") == "fill"), None)
        after = rows[first_fill:] if first_fill is not None else []
        f2 = [i for i, x in enumerate(rows) if x["full_grid"] and x["k"] == 2 and x["lam"] == 2]
        subs = [(a, b) for a, b in zip(rows[f2[0]:], rows[f2[0] + 1:]) if b.get("kind") == "sub"] if f2 else []
        last = rows[-1]
        by[(r["rule"], r["n0"])].append({
            "weak": first_fill is not None and all(x["k"] == 2 and x["lam"] == 2 for x in after),
            "strong": len(f2) >= 3 and all(a["full_grid"] for a, b in subs),
            "full2": len(f2), "n_end": last["n"], "stopped": next((x["stopped"] for x in r["trace"] if "stopped" in x), None),
            "lam_end": last["lam"], "b1_end": last["b1"], "b2_end": last["b2"], "filled_end": last["filled_knots"],
            "fills": fills, "max_per_pair": last["max_knots_per_pair"],
            "b1_positive_ever": any(x["b1"] > 0 for x in rows),
            "disconnected_moves": sum(1 for x in rows if x.get("pair_components", 1) > 1),
            "b2_eq_fills": last["b2"] == fills,
        })
    G = {}
    for (rule, n0), g in sorted(by.items()):
        G[f"{rule}/{n0}"] = {
            "runs": len(g), "weak": sum(x["weak"] for x in g) / len(g), "strong": sum(x["strong"] for x in g) / len(g),
            "lam_end": dict(Counter(x["lam_end"] for x in g)), "n_end": dict(Counter(x["n_end"] for x in g)),
            "stopped": dict(Counter(x["stopped"] for x in g)),
            "b1_end_median": statistics.median(x["b1_end"] for x in g), "b1_positive_end": sum(x["b1_end"] > 0 for x in g) / len(g),
            "b2_end_median": statistics.median(x["b2_end"] for x in g), "fills_median": statistics.median(x["fills"] for x in g),
            "b2_eq_fills": sum(x["b2_eq_fills"] for x in g) / len(g),
            "filled_end_median": statistics.median(x["filled_end"] for x in g),
            "disconnected_moves_median": statistics.median(x["disconnected_moves"] for x in g),
            "max_per_pair": dict(Counter(x["max_per_pair"] for x in g)),
        }
    P = {
        "Q1": W3[False] == 0,
        "Q2": Q2[False] == 0,
        "Q3": all(G[f"SEEDK/{n0}"]["weak"] == 1 and G[f"SEEDK/{n0}"]["strong"] >= 0.9 for n0 in (5, 6, 7, 8)),
        "Q4": sum(x["b1_end"] > 0 for n0 in (5, 6, 7, 8) for x in by[("KF3", n0)]) >= 0.5 * sum(len(by[("KF3", n0)]) for n0 in (5, 6, 7, 8)),
    }
    out = {"W3_steps": dict(W3), "Q2_steps": dict(Q2), "groups": G, "predictions": P}
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(P), json.dumps({str(k): v for k, v in W3.items()}), json.dumps({str(k): v for k, v in Q2.items()}))


if __name__ == "__main__":
    main()
