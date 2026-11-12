import json, statistics as st, numpy as np
from scipy.stats import spearmanr, linregress
P = "/home/jscul/p-vs-np-contact-first/artifacts/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count/bases.jsonl"
bases = [json.loads(l) for l in open(P)]
QS = (0.0, 0.1, 0.3, 0.5, 0.7, 0.9); GAPS = (4, 8, 16, 32, 64, 128, 256, 512)
print("q | g: defined share, median L, median open, median d, median L/open, rho(L,open) within g, rho(L,d) within g")
for q in QS:
    for g in GAPS:
        ps = [p for b in bases if b["q"] == q for p in b["pairs"] if p["g"] == g]
        dfn = [p for p in ps if p["status"] == "ok"]
        if len(dfn) < 5:
            print(q, g, round(len(dfn)/len(ps), 3), "few"); continue
        L = [p["L"] for p in dfn]; o = [p["open"] for p in dfn]; d = [p["d"] for p in dfn]
        print(q, g, round(len(dfn)/len(ps), 3), st.median(L), st.median(o), st.median(d), round(st.median([a/max(b,1) for a,b in zip(L,o)]), 3),
              round(spearmanr(L, o).statistic, 3) if len(set(o))>1 and len(set(L))>1 else None, round(spearmanr(L, d).statistic, 3) if len(set(d))>1 and len(set(L))>1 else None)
print()
print("per q: least-squares slope of L on gap, and of L on open, over defined pairs with g>=16; and L - (a*open+b) pooled")
allp = []
for q in QS:
    dfn = [p for b in bases if b["q"] == q for p in b["pairs"] if p["status"] == "ok" and p["g"] >= 16]
    L = np.array([p["L"] for p in dfn]); gap = np.array([p["gap"] for p in dfn]); o = np.array([p["open"] for p in dfn])
    r1 = linregress(gap, L); r2 = linregress(o, L)
    print(q, "n", len(dfn), "L~gap slope", round(r1.slope, 4), "int", round(r1.intercept, 2), "R2", round(r1.rvalue**2, 3), "| L~open slope", round(r2.slope, 4), "int", round(r2.intercept, 2), "R2", round(r2.rvalue**2, 3))
    allp += [(q, a, b, c) for a, b, c in zip(L, gap, o)]
A = np.array(allp)
r = linregress(A[:, 3], A[:, 1]); print("pooled over q: L~open slope", round(r.slope, 4), "int", round(r.intercept, 2), "R2", round(r.rvalue**2, 3))
r = linregress(A[:, 2], A[:, 1]); print("pooled over q: L~gap slope", round(r.slope, 4), "R2", round(r.rvalue**2, 3))
# multiple regression L ~ open + gap pooled
X = np.c_[A[:, 3], A[:, 2], np.ones(len(A))]; coef, res, *_ = np.linalg.lstsq(X, A[:, 1], rcond=None)
pred = X @ coef; print("pooled L ~ open + gap:", np.round(coef, 4), "R2", round(1 - ((A[:, 1]-pred)**2).sum()/((A[:, 1]-A[:, 1].mean())**2).sum(), 3))
