"""PICK-TWO-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read; it computes the
pre-registered readings, tiers and predictions P1-P9 from results.json (or results.json.gz) and writes readout.json."""
import gzip
import json
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "PICK-TWO-20261118-001B", "PICK-TWO-20261118-001B-E001_pick")


def load():
    f = os.path.join(OUT, "results.json")
    return json.load(open(f)) if os.path.exists(f) else json.load(gzip.open(f + ".gz", "rt"))


def summary(tr):
    rows = [r for r in tr if "stopped" not in r]
    stop = next((r["stopped"] for r in tr if "stopped" in r), None)
    first_fill = next((i for i, r in enumerate(rows) if r.get("kind") == "fill"), None)
    after = rows[first_fill:] if first_fill is not None else []
    two = lambda r: r["k"] == 2 and r["lam"] == 2
    full2 = [r for r in rows if r["full_grid"] and r["grid"] and len(r["grid"]) == 2]
    ff2 = next((i for i, r in enumerate(rows) if r["full_grid"] and r["grid"] and len(r["grid"]) == 2), None)
    subs_after_full = [(a, b) for a, b in zip(rows[ff2:], rows[ff2 + 1:]) if b.get("kind") == "sub"] if ff2 is not None else []
    fulls = [r for r in rows if r["full_grid"]]
    first_full = next((i for i, r in enumerate(rows) if r["full_grid"] and i > 0), None)
    return {
        "n_end": rows[-1]["n"], "stopped": stop, "lam_start": rows[0]["lam"], "lam_end": rows[-1]["lam"],
        "lam_max": max(r["lam"] for r in rows), "k_end": rows[-1]["k"],
        "filled": first_fill is not None,
        "weak": first_fill is not None and all(two(r) for r in after),
        "full2_count": len(full2),
        "subs_after_full2_at_full2": all(a["full_grid"] for a, b in subs_after_full) if ff2 is not None else None,
        "strong": len(full2) >= 3 and ff2 is not None and all(a["full_grid"] for a, b in subs_after_full),
        "full_count": len(fulls), "full_dims": dict(Counter(len(r["grid"]) for r in fulls)),
        "first_full_n": rows[first_full]["n"] if first_full is not None else None,
        "subs_before_first_full": sum(1 for r in rows[1:first_full + 1] if r.get("kind") == "sub") if first_full is not None else None,
        "omega_eq_lam": all(r["omega"] == r["lam"] for r in rows),
        "lam_at": {str(n): next((r["lam"] for r in rows if r["n"] == n), None) for n in (10, 20, 30, 40, 50, 60)},
        "isolated_end": rows[-1]["isolated"], "components_end": rows[-1]["components"],
        "kinds": dict(Counter(r.get("kind") for r in rows[1:])),
    }


def share(xs):
    xs = list(xs)
    return sum(1 for x in xs if x) / len(xs) if xs else None


def main():
    res = load()
    groups = defaultdict(list)
    for part in res.values():
        for r in part["results"]:
            groups[(r["rule"], json.dumps(r["param"]), r["start"])].append(summary(r["trace"]))
    G = {}
    for (rule, param, start), g in sorted(groups.items()):
        G[f"{rule}|{param}|{start}"] = {
            "runs": len(g), "weak": share(x["weak"] for x in g), "strong": share(x["strong"] for x in g),
            "lam_end": dict(Counter(x["lam_end"] for x in g)), "lam_max": dict(Counter(x["lam_max"] for x in g)),
            "lam_start": dict(Counter(x["lam_start"] for x in g)),
            "filled": share(x["filled"] for x in g), "full_any": share(x["full_count"] > 0 for x in g),
            "full2_ge3": share(x["full2_count"] >= 3 for x in g),
            "full_dims": dict(sum((Counter(x["full_dims"]) for x in g), Counter())),
            "first_full_n": dict(Counter(x["first_full_n"] for x in g)),
            "subs_before_first_full": dict(Counter(x["subs_before_first_full"] for x in g)),
            "omega_eq_lam": share(x["omega_eq_lam"] for x in g),
            "stopped": dict(Counter(x["stopped"] for x in g)), "n_end": dict(Counter(x["n_end"] for x in g)),
            "lam_at_median": {n: statistics.median([x["lam_at"][n] for x in g if x["lam_at"][n] is not None])
                              if any(x["lam_at"][n] is not None for x in g) else None for n in ("10", "20", "30", "40", "50", "60")},
            "isolated_end_median": statistics.median([x["isolated_end"] for x in g]),
            "components_end": dict(Counter(x["components_end"] for x in g)),
        }
    out = {"groups": G}
    g = lambda rule, param, start: G[f"{rule}|{json.dumps(param)}|{start}"]
    lines = ("line5", "line6", "line7", "line8", "line10", "line12")
    P = {}
    runs = defaultdict(list)                       # per-run rows by group, for the predictions that need them
    for part in res.values():
        for r in part["results"]:
            runs[(r["rule"], json.dumps(r["param"]), r["start"])].append([x for x in r["trace"] if "stopped" not in x])

    def full_d(rows, d):
        return [i for i, x in enumerate(rows) if x["full_grid"] and len(x["grid"]) == d]
    p1 = {}
    for st in ("line5", "line6", "line7", "line8"):
        rs = runs[("CAP", "3", st)]
        firsts = [full_d(rows, 3) for rows in rs]
        p1[st] = {
            "lam_reaches_3_never_more": all(max(x["lam"] for x in rows) == 3 for rows in rs),
            "full3_before_first_sub": all(f and not any(x.get("kind") == "sub" for x in rows[1:f[0] + 1])
                                          for rows, f in zip(rs, firsts)),
            "full3_ge2": share(len(f) >= 2 for f in firsts),
            "first_full3_n": dict(Counter(rows[f[0]]["n"] if f else None for rows, f in zip(rs, firsts))),
        }
    out["cap3"] = p1
    P["P1"] = (all(v["lam_reaches_3_never_more"] and v["full3_before_first_sub"] for v in p1.values())
               and all(p1[st]["full3_ge2"] >= 0.9 for st in ("line5", "line6")))
    P["P2"] = all(all(max(x["lam"] for x in rows) == 4 for rows in runs[("CAP", "4", st)]) for st in ("line5", "Q4"))
    lin = lambda w, st: runs[("PRICE", json.dumps(["lin", w]), st)]
    P["P3"] = (all(all(max(x["lam"] for x in rows) == 1 for rows in lin(w, st)) for w in (2.1, 3.0) for st in ("line5", "line8"))
               and all(all(rows[-1]["n"] == 40 and rows[-1]["lam"] >= 4 for rows in lin(w, "line5")) for w in (1.0, 1.9))
               and share(rows[-1]["lam"] > 2 for st in ("line5", "line8") for rows in lin(2.0, st)) > 0.5)
    want = {0.25: 4, 0.35: 3, 0.5: 2, 1.0: 1}
    P["P4"] = all(set(g("PRICE", ["quad", w], s)["lam_max"]) == {want[w]} for w in want for s in ("line5", "line8"))
    P["P5"] = all(g("ODD", None, s)["weak"] == 1 and g("ODD", None, s)["full_any"] == 1 for s in lines)
    P["P6"] = all(g("FRESH", None, s)["weak"] == 1 for s in lines) and all(g("FRESH", None, s)["strong"] < 0.9 for s in lines)
    ne = g("NEWCROSS", None, "line8")
    P["P7"] = ne["lam_end"].get(2, 0) < ne["runs"] / 2
    P["P8"] = (all(g("SEED", None, s)["weak"] == 1 and g("SEED", None, s)["strong"] >= 0.9 for s in lines)
               and all(g("SEED", None, s)["lam_max"] == {3: 10} for s in ("Q3", "G333")))
    P["P9"] = (all(g(r, None, s)["lam_max"] == {1: 20} for r in ("KEEP", "CC") for s in lines)
               and all(g(r, None, s)["lam_max"] == {3: 10} for r in ("KEEP", "CC") for s in ("Q3", "G333")))
    out["predictions"] = P
    tiers = {}
    for rule in ("KEEP", "CC", "ODD", "FRESH", "NEWCROSS", "SEED"):
        weak = all(g(rule, None, s)["weak"] == 1 for s in lines)
        strong = weak and all(g(rule, None, s)["strong"] >= 0.9 for s in lines)
        conserves = all(set(g(rule, None, s)["lam_max"]) == {3} for s in ("Q3", "G333"))
        tiers[rule] = {"weak": weak, "strong": strong, "conserves_three": conserves,
                       "weak_by_line": {s: g(rule, None, s)["weak"] for s in lines},
                       "strong_by_line": {s: g(rule, None, s)["strong"] for s in lines}}
    out["tiers"] = tiers
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(P))
    print(json.dumps({k: (v["weak"], v["strong"], v["conserves_three"]) for k, v in tiers.items()}))


if __name__ == "__main__":
    main()
