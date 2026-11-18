"""NEVER-NEST-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read; it computes the
pre-registered derived readings, the decision rule and predictions P1-P8 from results.json, and writes readout.json."""
import gzip
import json
import os
import statistics
import sys
from collections import Counter, defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "NEVER-NEST-20261118-001B", "NEVER-NEST-20261118-001B-E001_nest")


def at(tr, n):
    for r in tr:
        if r.get("n") == n and "stopped" not in r:
            return r
    return None


def run_summary(tr):
    rows = [r for r in tr[1:] if "stopped" not in r]
    last = rows[-1] if rows else tr[0]
    s = {"reached": last["n"], "stalled": any("stopped" in r for r in tr)}
    late = [r for r in rows if 21 <= r["n"] <= 40]
    s["fill_frac_21_40"] = sum(r["kind"] == "fill" for r in late) / 20 if len(late) == 20 else None
    early = [r for r in rows if r["n"] <= 20]
    s["fill_frac_early"] = sum(r["kind"] == "fill" for r in early) / len(early) if early else None
    s["full_any"] = any(r["full_grid"] for r in rows)
    s["full_30_40"] = any(r["full_grid"] for r in rows if 30 <= r["n"] <= 40)
    s["first_full"] = next((r["n"] for r in rows if r["full_grid"]), None)
    s["no_fill_31_40"] = not any(r["kind"] == "fill" for r in rows if 31 <= r["n"] <= 40)
    r20, r40 = at(tr, 20), at(tr, 40)
    s["both_grow"] = bool(r20 and r40 and r20["chains"] and r40["chains"]
                          and r40["chains"][0] > r20["chains"][0] and r40["chains"][1] > r20["chains"][1])
    big = small = 0
    for a, b in zip(rows, rows[1:]):
        if b["kind"] == "sub" and b["n"] > 20 and a["chains"] and b["chains"] and a["chains"][0] != a["chains"][1]:
            if b["chains"][0] > a["chains"][0]:
                big += 1
            elif b["chains"][1] > a["chains"][1]:
                small += 1
    s["strip"] = big / (big + small) if big + small else None
    s["two_40"] = bool(r40 and r40["two"])
    s["two_every"] = all(r["two"] for r in rows)
    s["lam_40"] = r40["lam"] if r40 else None
    s["empty_40"] = r40["empty"] if r40 else None
    s["isolated_40"] = r40["isolated"] if r40 else None
    s["chains_40"] = r40["chains"] if r40 else None
    s["N_40"] = r40["N"] if r40 else None
    s["kinds"] = dict(Counter(r["kind"] for r in rows))
    # the advisor's diagnostic: fills that keep two orders available right after a subdivision
    s["after_sub"] = [b.get("zero_two") for a, b in zip(rows, rows[1:]) if a["kind"] == "sub" and "zero_two" in b]
    s["tracked_40"] = bool(r40 and "lemma_c" in r40)
    s["max_middles"] = max((len(r["middles"]) for r in rows if "middles" in r), default=None)
    s["odd_sizes"] = dict(Counter(len(r["odd"]) for r in rows if "odd" in r))
    s["lemma_c_disagree"] = sum(1 for r in rows if r.get("lemma_c") is not None and (r["lemma_c"] == 2) != r["two"])
    return s


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def share(xs):
    xs = list(xs)
    return sum(1 for x in xs if x) / len(xs) if xs else None


def verdict(group):
    med = median(g["fill_frac_21_40"] for g in group)
    full = share(g["full_30_40"] for g in group)
    grow = share(g["both_grow"] for g in group)
    nofill = share(g["no_fill_31_40"] for g in group)
    if med is not None and med >= 0.7 and full >= 0.8 and grow >= 0.8:
        v = "grows"
    elif (med is not None and med <= 0.15) or nofill >= 0.5:
        v = "starved"
    else:
        v = "intermediate"
    return v, {"median_fill_21_40": med, "full_30_40": full, "both_grow": grow, "no_fill_31_40": nofill}


def grid_course(tr):
    """For NNF, CC and the class law: two orders at every step after the first; every subdivision taken at a full grid and every
    full grid followed by a subdivision (a full grid after every completed row or column)."""
    rows = [r for r in tr if "stopped" not in r]
    two = lambda r: r["two"] if "two" in r else (str(r["k"]) == "2" and r["lam"] == 2)  # the class law's trace: k (as text), lam
    ok_two = all(two(r) for r in rows[1:])
    full = lambda r: r["full_grid"] if "full_grid" in r else r["n"] == 4      # the class law's start row: the 2 x 2 pattern
    subs_at_full = all(full(a) for a, b in zip(rows, rows[1:]) if b.get("kind") == "sub" or b.get("excess", 0) > 0)
    return ok_two, subs_at_full


def main():
    res = json.load(gzip.open(os.path.join(OUT, "results.json.gz"), "rt"))   # run.py --merge's results.json, compressed
    out = {}
    # ---------------- R1
    by = defaultdict(list)
    for r in res["R1"]["results"]:
        by[(r["rule"], r["n0"])].append(run_summary(r["trace"]))
    r1 = {}
    for (rule, n0), group in sorted(by.items()):
        v, nums = verdict(group)
        after = Counter()
        for g in group:
            for x in g["after_sub"]:
                after[min(x, 2)] += 1
        r1[f"{rule}/{n0}"] = {
            "runs": len(group), "verdict": v, **nums,
            "full_any": share(g["full_any"] for g in group),
            "first_full_median": median(g["first_full"] for g in group),
            "median_fill_early": median(g["fill_frac_early"] for g in group),
            "fill_21_40_quartiles": statistics.quantiles([g["fill_frac_21_40"] for g in group if g["fill_frac_21_40"] is not None], n=4)
            if len(group) > 3 else None,
            "two_40": share(g["two_40"] for g in group), "two_every": share(g["two_every"] for g in group),
            "lam_40": dict(Counter(g["lam_40"] for g in group)),
            "strip_median": median(g["strip"] for g in group),
            "empty_40_median": median(g["empty_40"] for g in group),
            "isolated_40_median": median(g["isolated_40"] for g in group),
            "N_40_median": median(g["N_40"] for g in group),
            "stalled": share(g["stalled"] for g in group),
            "kinds": dict(sum((Counter(g["kinds"]) for g in group), Counter())),
            "after_sub_0_1_2plus": dict(after),
            "tracked_40": share(g["tracked_40"] for g in group),
            "max_middles": dict(Counter(g["max_middles"] for g in group)),
            "odd_sizes": dict(sum((Counter(g["odd_sizes"]) for g in group), Counter())),
            "lemma_c_disagree": sum(g["lemma_c_disagree"] for g in group),
        }
    out["R1"] = r1
    # ---------------- R2
    by2 = defaultdict(list)
    for r in res["R2"]["results"]:
        by2[(r["rule"], r["start"])].append(r["trace"])
    r2 = {}
    for (rule, start), trs in sorted(by2.items()):
        rows40 = [at(tr, 40) for tr in trs]
        course = [grid_course(tr) for tr in trs]
        shapes = Counter(tuple(r["chains"]) if r and r.get("chains") else None for r in rows40) if rule != "class" else \
            Counter(tuple(sorted(r["class_splits"], reverse=True)) if r else None for r in rows40)
        firsts = Counter(next((r["n"] for r in tr[1:] if r.get("full_grid")), None) for tr in trs)
        fills = [sum(1 for r in tr[1:] if r.get("kind") == "fill" or r.get("excess") == 0) for tr in trs]
        r2[f"{rule}/{start}"] = {
            "runs": len(trs),
            "two_every_after_first": share(c[0] for c in course),
            "subs_only_at_full_grids": share(c[1] for c in course),
            "full_any": share(any(r.get("full_grid") for r in tr[1:]) for tr in trs),
            "full_at_12": share(bool(at(tr, 12) and at(tr, 12).get("full_grid")) for tr in trs),
            "full_at_30": share(bool(at(tr, 30) and at(tr, 30).get("full_grid")) for tr in trs),
            "full_30_40": share(any(r.get("full_grid") for r in tr if 30 <= r.get("n", 0) <= 40) for tr in trs),
            "first_full": {str(k): v for k, v in sorted(firsts.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))},
            "shapes_40": {str(k): v for k, v in shapes.most_common()},
            "fills_median": median(fills),
            "reached_40": share(bool(at(tr, 40)) for tr in trs),
        }
    out["R2"] = r2
    # ---------------- E1, E2
    for part in ("E1", "E2"):
        if part not in res:
            continue
        agg = defaultdict(list)
        for r in res[part]["results"]:
            L = r["levels"]
            last = L[-1]
            n0 = r["n0"]
            # expected fills at the last level: every non-fill step of NN costs exactly two states
            EN = sum(Fraction(v) * int(k) for k, v in last["N"].items())
            steps = last["n"] - n0
            fills = Fraction(steps) - (EN - 2 * n0) / 2
            agg[n0].append({"two_last": Fraction(last["two"]), "full_last": Fraction(last["full_grid"]),
                            "full_any_level": max(Fraction(l["full_grid"]) for l in L[1:]),
                            "stalled": Fraction(last["stalled"]), "classes": last["classes"],
                            "two_all": all(Fraction(l["two"]) == 1 for l in L[1:]),
                            "exp_fill_frac": fills / steps if part == "E1" else None, "seconds": r["seconds"],
                            "n_last": last["n"]})
        out[part] = {str(n0): {
            "starts": len(g), "n_last": g[0]["n_last"],
            "two_orders_with_prob_1_every_level": all(x["two_all"] for x in g),
            "two_last_min": float(min(x["two_last"] for x in g)),
            "full_grid_last_mean": float(sum(x["full_last"] for x in g) / len(g)),
            "full_grid_last_range": [float(min(x["full_last"] for x in g)), float(max(x["full_last"] for x in g))],
            "exp_fill_frac_mean": float(sum(x["exp_fill_frac"] for x in g) / len(g)) if part == "E1" else None,
            "exp_fill_frac_range": [float(min(x["exp_fill_frac"] for x in g)), float(max(x["exp_fill_frac"] for x in g))]
            if part == "E1" else None,
            "stalled_max": float(max(x["stalled"] for x in g)),
            "classes_max": max(x["classes"] for x in g)} for n0, g in sorted(agg.items())}
    # ---------------- predictions
    P = {}
    nn = {n0: r1[f"NN/{n0}"] for n0 in (5, 6, 7, 8)}
    nn2 = {n0: r1[f"NN2/{n0}"] for n0 in (5, 6, 7, 8)}
    kf = {n0: r1[f"KF3/{n0}"] for n0 in (5, 6, 7, 8)}
    P["P1"] = all(nn[n]["verdict"] == "intermediate" for n in nn)
    P["P2"] = all(nn[n]["full_any"] >= 0.5 for n in nn) and nn[8]["full_any"] < nn[5]["full_any"]
    P["P3"] = all(0.25 <= nn[n]["median_fill_21_40"] <= 0.65 for n in nn)
    P["P4"] = all(nn[n]["no_fill_31_40"] <= 0.15 for n in nn)
    P["P5"] = all(nn2[n]["median_fill_21_40"] < nn[n]["median_fill_21_40"] for n in nn)
    P["P6"] = all(kf[n]["two_40"] <= 0.1 for n in kf)
    P["P7"] = all(r2[k]["two_every_after_first"] == 1 and r2[k]["subs_only_at_full_grids"] == 1
                  for k in r2 if k.startswith("NNF/") or k == "CC/2x2")
    P["P8"] = all(r2[f"CC/fill{n0}"]["full_any"] < 0.5 for n0 in (5, 6, 7, 8))
    out["predictions"] = P
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(P))


if __name__ == "__main__":
    main()
