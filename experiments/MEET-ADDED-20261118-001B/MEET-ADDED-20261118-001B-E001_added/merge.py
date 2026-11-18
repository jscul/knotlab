"""Score Q1, Q2, Q4 and Q5 (Q3 merged into Q2 on the advisor's advice) of research/MEET-ADDED-20261118-001/preregistration.md (equalities to 1e-9; strict inequalities by more than 1e-9).

  ../../../.venv/bin/python -B merge.py <runner output dir>
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


def cond_entropy(rows, lev, joint):
    w = Fraction(1, len(rows))
    pj, pa = defaultdict(Fraction), defaultdict(Fraction)
    for x in rows:
        for c, q in x["levels"][lev]["laws"][joint].items():
            pj[c] += w * Fraction(q)
            pa[c.split(":")[0]] += w * Fraction(q)
    return -sum(float(q) * math.log2(float(q) / float(pa[c.split(":")[0]])) for c, q in pj.items() if q)


recs = load_results(sys.argv[1])
bad = sorted(k for k, v in recs.items() if v["status"] != "ok")
rows = [v["result"] for v in recs.values() if v["status"] == "ok"]
out = {"cases": len(recs), "not_ok": bad, "per_n0": {}}
q1 = q2 = q3 = q4 = q5 = True
eps = 1e-9
for n0 in sorted({r["n0"] for r in rows}):
    rs = [r for r in rows if r["n0"] == n0]
    levs = []
    any_gap = False
    for lev in range(rs[0]["depth"] + 1):
        L = {"n": n0 + lev}
        for r in ("P0", "U", "P1", "T1", "K1", "SG", "N"):
            L[r] = share(rs, lev, r)
        for a in ("U", "P1", "T1", "K1"):
            L["H_N_given_" + a] = cond_entropy(rs, lev, a + "|N")
        levs.append(L)
        if lev >= 1:
            q1 &= L["P0"] < 0.25 * L["U"]
        q2 &= abs(L["T1"] - L["N"]) < 1e-6 and abs(L["K1"] - L["N"]) < 1e-6
        if lev >= 2:
            q5 &= L["P1"] > L["U"] + eps
        if lev >= 3 and L["P1"] < L["T1"] - eps:
            any_gap = True
    q4 &= any_gap
    out["per_n0"][n0] = levs
out["predictions"] = {"Q1": q1, "Q2": q2, "Q4": q4, "Q5": q5}
dest = ROOT / "artifacts/MEET-ADDED-20261118-001B/MEET-ADDED-20261118-001B-E001_added"
dest.mkdir(parents=True, exist_ok=True)
(dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(out["predictions"]), "not ok:", bad)
for n0, levs in out["per_n0"].items():
    for L in levs:
        print(n0, L["n"], {k: round(v, 4) for k, v in L.items() if k != "n"})
