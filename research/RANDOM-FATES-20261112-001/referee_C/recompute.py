import json, statistics as st, math
from scipy.stats import spearmanr
P = "/home/jscul/p-vs-np-contact-first/artifacts/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count/bases.jsonl"
bases = [json.loads(l) for l in open(P)]
QS = (0.0, 0.1, 0.3, 0.5, 0.7, 0.9); GAPS = (4, 8, 16, 32, 64, 128, 256, 512)
def ok(p): return p["status"] == "ok"
def bmed(b, g):
    v = [p["L"] for p in b["pairs"] if p["g"] == g and ok(p)]
    return st.median(v) if v else None
def ndef(b, g): return sum(ok(p) for p in b["pairs"] if p["g"] == g)
print("statuses", {s: sum(p["status"] == s for b in bases for p in b["pairs"]) for s in ("ok", "none", "blowup")})
# Q1
def ghalf(b):
    for g in GAPS:
        if ndef(b, g) < 4: return g
    return math.inf
for q in QS:
    gh = sorted(ghalf(b) for b in bases if b["q"] == q)
    print("Q1 q", q, "g_half per base", gh, "median", st.median(gh))
# Q2
r = []
for b in bases:
    if b["q"] != 0.5: continue
    el = all(ndef(b, g) >= 6 for g in (32, 64, 128))
    m = [bmed(b, g) for g in (32, 64, 128)]
    print("Q2 base", b["base"], "defined", [ndef(b, g) for g in (32, 64, 128)], "meds", m, "eligible", el,
          "ratio", (m[2] - m[1]) / (m[1] - m[0]) if None not in m and m[1] != m[0] else None)
    if el: r.append((m[2] - m[1]) / (m[1] - m[0]))
print("Q2 ratios", r, "in range", sum(1.5 <= x <= 2.7 for x in r), "eligible", len(r))
# Q3
for q in (0.3, 0.5, 0.7, 0.9):
    v = [bmed(b, 64) for b in bases if b["q"] == q and ndef(b, 64) >= 4]
    print("Q3 q", q, "eligible", len(v), "median of base medians", st.median(v), sorted(v))
# Q4a
for q in (0.7, 0.9):
    ps = [p for b in bases if b["q"] == q for p in b["pairs"] if p["g"] == 256 and ok(p)]
    rho = spearmanr([p["L"] for p in ps], [p["open"] for p in ps])
    rho_gap = spearmanr([p["L"] for p in ps], [p["gap"] for p in ps])
    rho_d = spearmanr([p["L"] for p in ps], [p["d"] for p in ps])
    print("Q4a q", q, "n", len(ps), "rho(L,open)", round(rho.statistic, 4), "rho(L,gap)", round(rho_gap.statistic, 4), "rho(L,d)", round(rho_d.statistic, 4))
# Q4b
v = []
for b in bases:
    if b["q"] == 0.9:
        a, c = bmed(b, 128), bmed(b, 512)
        v.append(None if a is None or c is None else c - a)
print("Q4b", v, sum(1 for x in v if x is not None and x >= 3))
# Q5
for q in QS:
    print("Q5 q", q, sum(1 for b in bases if b["q"] == q for p in b["pairs"] if p["g"] >= 32 and ok(p) and p["L"] == 2))
