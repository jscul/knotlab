"""Score the predictions of research/MEET-DIST-20261118-001/preregistration.md.

  ../../../.venv/bin/python -B merge.py <runner output dir>
Prior: uniform over labelled presentations of one labelling of the line (a mirror pair counts twice, a self-mirror one once).
"""
import itertools
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results


def tv(a, b):
    return sum(abs(a.get(k, 0) - b.get(k, 0)) for k in set(a) | set(b)) / 2


def identification(rows, lev, key, law_name="table_law"):
    """Bayes chance of naming `key` (bare bracketing or presentation) from one grown sample's class, prior as above."""
    tot = sum(r["mirror_weight"] for r in rows)
    mass = defaultdict(lambda: defaultdict(Fraction))
    for r in rows:
        law = r["levels"][lev][law_name]
        for c, q in law.items():
            mass[c][key(r)] += Fraction(r["mirror_weight"]) * Fraction(q)
    return sum(max(v.values()) for v in mass.values()) / tot


def mutual_information_fraction(rows, lev, key, law_name="table_law"):
    """I(key; class) / H(key) under the prior, in bits (floats from exact masses)."""
    import math
    tot = sum(r["mirror_weight"] for r in rows)
    pk = defaultdict(Fraction)
    joint = defaultdict(Fraction)
    pc = defaultdict(Fraction)
    for r in rows:
        law = r["levels"][lev].get(law_name)
        if law is None:
            return None
        w = Fraction(r["mirror_weight"], tot)
        pk[key(r)] += w
        for c, q in law.items():
            joint[(key(r), c)] += w * Fraction(q)
            pc[c] += w * Fraction(q)
    H = -sum(float(p) * math.log2(float(p)) for p in pk.values() if p)
    I = sum(float(q) * math.log2(float(q) / (float(pk[k]) * float(pc[c]))) for (k, c), q in joint.items() if q)
    return I / H if H else None


def chance(rows, key):
    tot = sum(r["mirror_weight"] for r in rows)
    w = defaultdict(int)
    for r in rows:
        w[key(r)] += r["mirror_weight"]
    return Fraction(max(w.values()), tot)


def main(out_dir):
    recs = load_results(out_dir)
    bad = sorted(k for k, v in recs.items() if v["status"] != "ok")
    rows = [v["result"] for v in recs.values() if v["status"] == "ok"]
    for r in rows:
        for L in r["levels"]:
            L["lam_law"] = L["lam"]
    out = {"cases": len(recs), "not_ok": bad, "per_n0": {}}
    for n0 in sorted({r["n0"] for r in rows}):
        rs = sorted([r for r in rows if r["n0"] == n0], key=lambda r: r["ordered"])
        depth = rs[0]["depth"]
        per = []
        for lev in range(depth + 1):
            laws = [{k: Fraction(v) for k, v in r["levels"][lev]["table_law"].items()} for r in rs]
            diff_bare = [tv(laws[i], laws[j]) for i, j in itertools.combinations(range(len(rs)), 2) if rs[i]["bare"] != rs[j]["bare"]]
            same_bare = [tv(laws[i], laws[j]) for i, j in itertools.combinations(range(len(rs)), 2) if rs[i]["bare"] == rs[j]["bare"]]
            per.append({
                "n": n0 + lev,
                "min_tv_different_bare": float(min(diff_bare)) if diff_bare else None,
                "pairs_equal_different_bare": sum(1 for x in diff_bare if x == 0),
                "min_tv_same_bare": float(min(same_bare)) if same_bare else None,
                "pairs_equal_same_bare": sum(1 for x in same_bare if x == 0),
                "id_bare": str(identification(rs, lev, lambda r: r["bare"])),
                "id_bare_float": float(identification(rs, lev, lambda r: r["bare"])),
                "id_presentation_float": float(identification(rs, lev, lambda r: r["ordered"])),
                "id_bare_from_orders_float": float(identification(rs, lev, lambda r: r["bare"], "lam_law")),
                "id_bare_from_multiset_float": float(identification(rs, lev, lambda r: r["bare"], "multiset_law")),
                "id_bare_null_float": (float(identification(rs, lev, lambda r: r["bare"], "null_law"))
                                       if lev > 0 and rs[0]["levels"][lev].get("null_law") is not None else None),
                "mi_bare": mutual_information_fraction(rs, lev, lambda r: r["bare"]),
                "mi_bare_null": (mutual_information_fraction(rs, lev, lambda r: r["bare"], "null_law")
                                 if lev > 0 and rs[0]["levels"][lev].get("null_law") is not None else None),
                "mi_presentation": mutual_information_fraction(rs, lev, lambda r: r["ordered"]),
                "mi_bare_multiset": mutual_information_fraction(rs, lev, lambda r: r["bare"], "multiset_law"),
                "table_classes_total": len(set().union(*[set(x) for x in laws])),
            })
        out["per_n0"][n0] = {"presentations_up_to_mirror": len(rs), "bare_bracketings": len({r["bare"] for r in rs}),
                             "chance_bare": float(chance(rs, lambda r: r["bare"])), "levels": per}
    pv = out["per_n0"]
    d1 = all(L["pairs_equal_different_bare"] == 0 for v in pv.values() for L in v["levels"][1:])
    d2 = all(L["pairs_equal_different_bare"] == 0 and L["pairs_equal_same_bare"] == 0 for v in pv.values() for L in v["levels"][2:])
    d3 = True
    d4 = True
    d5 = True
    for v in pv.values():
        mis = [L["mi_bare"] for L in v["levels"]]
        best = max(range(len(mis)), key=lambda i: mis[i])
        d3 &= best in (1, 2) and mis[-1] < mis[best]
        for L in v["levels"][2:]:
            if L["mi_bare_null"] is not None:
                d4 &= L["mi_bare"] < L["mi_bare_null"]
        d5 &= all(L["mi_bare_multiset"] < L["mi_bare"] for L in v["levels"][2:])
    out["predictions"] = {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5}
    print(json.dumps(out["predictions"]))
    dest = ROOT / "artifacts/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print("not ok:", bad)
    for n0, v in out["per_n0"].items():
        print(n0, "bare", v["bare_bracketings"], "chance", round(v["chance_bare"], 4))
        for L in v["levels"]:
            print("   n", L["n"], "MI bare", L["mi_bare"] and round(L["mi_bare"], 4), "null", L["mi_bare_null"] and round(L["mi_bare_null"], 4),
                  "id bare", round(L["id_bare_float"], 4), "id pres", round(L["id_presentation_float"], 4),
                  "from orders", round(L["id_bare_from_orders_float"], 4), "equal pairs diff bare", L["pairs_equal_different_bare"],
                  "same bare", L["pairs_equal_same_bare"])


if __name__ == "__main__":
    main(sys.argv[1])
