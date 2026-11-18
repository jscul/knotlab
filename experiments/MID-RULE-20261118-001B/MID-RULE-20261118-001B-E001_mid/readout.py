"""MID-RULE-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read: the invariant, tiers,
starvation, the stratified free-line verdicts and predictions Q1-Q5.  Writes readout.json."""
import gzip
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "MID-RULE-20261118-001B", "MID-RULE-20261118-001B-E001_mid")


def load():
    """results.json (both parts), or, while part F is pending, part_K.json(.gz) alone."""
    f = os.path.join(OUT, "results.json")
    if os.path.exists(f):
        return json.load(open(f))
    if os.path.exists(f + ".gz"):
        return json.load(gzip.open(f + ".gz", "rt"))
    k = os.path.join(OUT, "part_K.json")
    return {"K": json.load(open(k)) if os.path.exists(k) else json.load(gzip.open(k + ".gz", "rt"))}


def summary(tr):
    rows = [r for r in tr if "stopped" not in r]
    ff = next((i for i, r in enumerate(rows) if r.get("kind") == "fill"), None)
    after = rows[ff:] if ff is not None else []
    invariant = all((a["k"], a["lam"]) == (b["k"], b["lam"]) for a, b in zip(after, after[1:]))
    full2 = [i for i, r in enumerate(rows) if r["full_grid"]]
    subs = [(a, b) for a, b in zip(rows[full2[0]:], rows[full2[0] + 1:]) if b.get("kind") == "sub"] if full2 else []
    late = [r for r in rows if 31 <= r["n"] <= 60]
    first = rows[ff] if ff is not None else None
    return {
        "invariant": invariant, "two_after_first": ff is not None and all(r["k"] == 2 and r["lam"] == 2 for r in after),
        "strong": len(full2) >= 3 and all(a["full_grid"] for a, b in subs) and ff is not None
                  and all(r["k"] == 2 and r["lam"] == 2 for r in after),
        "full_any": bool(full2), "full_count": len(full2),
        "lam_max": max(r["lam"] for r in rows), "n_end": rows[-1]["n"],
        "stopped": next((r["stopped"] for r in tr if "stopped" in r), None),
        "fill_frac_31_60": sum(r.get("kind") == "fill" for r in late) / len(late) if late else None,
        "fills": sum(r.get("kind") == "fill" for r in rows),
        "spanning_first": first is not None and first["isolated_after_first"] == 0 if first and "isolated_after_first" in first else None,
    }


def main():
    res = load()
    G = defaultdict(list)
    spans = {}
    for part in res.values():
        for r in part["results"]:
            s = summary(r["trace"])
            if r["part"] == "F" and r["rule"] in ("MID2", "ONE") and r["start"].startswith("line"):
                # the first fill spans the line iff, right after it, every split crosses something (E5); read from the trace
                rows = [x for x in r["trace"] if "stopped" not in x]
                ff = next((i for i, x in enumerate(rows) if x.get("kind") == "fill"), None)
                s["spanning_first"] = None
                spans[(r["rule"], r["start"], r["index"])] = s
            G[(r["part"], r["rule"], r["start"])].append(s)
    out = {"groups": {}}
    for (part, rule, start), g in sorted(G.items()):
        fr = [x["fill_frac_31_60"] for x in g if x["fill_frac_31_60"] is not None]
        out["groups"][f"{part}/{rule}/{start}"] = {
            "runs": len(g), "invariant": all(x["invariant"] for x in g), "two_after_first": sum(x["two_after_first"] for x in g) / len(g),
            "strong": sum(x["strong"] for x in g) / len(g), "full_any": sum(x["full_any"] for x in g) / len(g),
            "lam_max": dict(Counter(x["lam_max"] for x in g)), "n_end": dict(Counter(x["n_end"] for x in g)),
            "stopped": dict(Counter(x["stopped"] for x in g)),
            "fill_frac_31_60_mean": sum(fr) / len(fr) if fr else None, "fill_frac_31_60_max": max(fr) if fr else None,
            "fills_median": sorted(x["fills"] for x in g)[len(g) // 2],
            "strong_iff_full_any": all(x["strong"] == x["full_any"] for x in g),
        }
    O = out["groups"]
    K = {k: v for k, v in O.items() if k.startswith("K/")}
    F = {k: v for k, v in O.items() if k.startswith("F/")}
    P = {
        "Q1": all(v["invariant"] for k, v in O.items() if "/ANY/" not in k),
        "Q2": all(O[f"F/{r}/2x2"]["strong"] == 1 for r in ("MID2", "ONE")),
        "Q3": all(O[f"F/{r}/{s}"]["strong_iff_full_any"] for r in ("MID2", "ONE") for s in ("line5", "line8", "line12")),
        "Q4": all((v["fill_frac_31_60_max"] or 0) <= 0.15 and set(v["lam_max"]) <= {2} for v in K.values()),
        "Q5": all(set(map(int, O[f"F/ANY/{s}"]["lam_max"])) and min(map(int, O[f"F/ANY/{s}"]["lam_max"])) > 2 for s in ("line5", "line8")),
    }
    out["predictions"] = P
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(P))
    for k, v in O.items():
        print(k, v)


if __name__ == "__main__":
    main()
