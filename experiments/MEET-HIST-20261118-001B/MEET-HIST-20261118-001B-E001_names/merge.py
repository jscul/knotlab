"""Score H1-H4 (ties count as failures) of research/MEET-HIST-20261118-001/preregistration.md.

  ../../../.venv/bin/python -B merge.py <runner output dir>
Prior: uniform over labelled presentations (every bracketing of one labelling of the line, weight 1).
"""
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results


def share(rows, lev, r):
    """I(bare bracketing; reading r) / H(bare bracketing)."""
    w = Fraction(1, len(rows))
    pk, pc, j = defaultdict(Fraction), defaultdict(Fraction), defaultdict(Fraction)
    for x in rows:
        pk[x["bare"]] += w
        for c, q in x["levels"][lev]["laws"][r].items():
            j[(x["bare"], c)] += w * Fraction(q)
            pc[c] += w * Fraction(q)
    H = -sum(float(p) * math.log2(float(p)) for p in pk.values() if p)
    I = sum(float(q) * math.log2(float(q) / (float(pk[k]) * float(pc[c]))) for (k, c), q in j.items() if q)
    return I / H if H else 0.0


def cond_entropy(rows, lev, joint, given):
    """H(X | U) in bits, from the pooled joint law of (U, X) keys 'u:x'."""
    w = Fraction(1, len(rows))
    pj, pu = defaultdict(Fraction), defaultdict(Fraction)
    for x in rows:
        for c, q in x["levels"][lev]["laws"][joint].items():
            pj[c] += w * Fraction(q)
            pu[c.split(":")[0]] += w * Fraction(q)
    return -sum(float(q) * math.log2(float(q) / float(pu[c.split(":")[0]])) for c, q in pj.items() if q)


def entropy(rows, lev, r):
    w = Fraction(1, len(rows))
    p = defaultdict(Fraction)
    for x in rows:
        for c, q in x["levels"][lev]["laws"][r].items():
            p[c] += w * Fraction(q)
    return -sum(float(q) * math.log2(float(q)) for q in p.values() if q)


recs = load_results(sys.argv[1])
bad = sorted(k for k, v in recs.items() if v["status"] != "ok")
rows = [v["result"] for v in recs.values() if v["status"] == "ok"]
out = {"cases": len(recs), "not_ok": bad, "per_n0": {}}
h1 = h2 = h3 = h4 = sanity = True
for n0 in sorted({r["n0"] for r in rows}):
    rs = [r for r in rows if r["n0"] == n0]
    levs = []
    for lev in range(rs[0]["depth"] + 1):
        L = {"n": n0 + lev}
        for r in ("U", "NL", "NO", "N"):
            L[r] = share(rs, lev, r)
        L["H_order_given_U"] = cond_entropy(rs, lev, "U|NO", "U")
        L["H_line_given_U"] = cond_entropy(rs, lev, "U|NL", "U")
        L["H_order"] = entropy(rs, lev, "NO")
        L["H_order_given_NL"] = cond_entropy(rs, lev, "NL|N", "NL")
        levs.append(L)
        if lev >= 2:
            h1 &= L["H_order_given_NL"] > 1e-9
            h2 &= L["N"] > L["NL"] + 1e-9
            h3 &= L["NL"] > L["U"] + 1e-9
            h4 &= (L["N"] - L["NL"]) > (L["NL"] - L["U"]) + 1e-9
        if lev >= 1:
            sanity &= abs(L["NO"] - L["N"]) < 1e-9
    out["per_n0"][n0] = levs
out["predictions"] = {"H1": h1, "H2": h2, "H3": h3, "H4": h4, "sanity NO = N": sanity}
dest = ROOT / "artifacts/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names"
dest.mkdir(parents=True, exist_ok=True)
(dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(out["predictions"]), "not ok:", bad)
for n0, levs in out["per_n0"].items():
    for L in levs:
        print(n0, L["n"], {k: round(v, 4) for k, v in L.items() if k != "n"})
