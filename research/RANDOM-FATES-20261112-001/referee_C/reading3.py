import sys, itertools, numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from scipy.stats import linregress, spearmanr
bases = load_bases()
rows = []
for rec in bases:
    k = regen(rec["q"], rec["base"]); ks = set(k)
    for p in rec["pairs"]:
        if p["status"] != "ok" or p["g"] < 16: continue
        i, j = p["i"], p["j"]
        band = [t for a in range(i, j - 1) for t in itertools.combinations(range(a, min(a + 4, j + 1)), 3) if t[0] == a]
        absent = sum(1 for t in band if t not in ks)
        present = sum(1 for t in k if i <= t[0] and t[2] <= j)
        span = j - i + 1
        possible = len(band)
        rows.append((rec["q"], p["g"], p["L"], p["open"], absent, present, possible, span))
A = np.array(rows, float)
for c, nm in ((3, "open"), (4, "absent knots"), (5, "present knots")):
    out = []
    for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9):
        s = A[A[:, 0] == q]; r = linregress(s[:, c], s[:, 2]); out.append((round(r.slope, 3), round(r.intercept, 2)))
    r = linregress(A[:, c], A[:, 2]); res = A[:, 2] - (r.slope * A[:, c] + r.intercept)
    print(f"{nm:14s} per-q (slope, intercept) {out}\n   pooled slope {r.slope:.4f} int {r.intercept:.2f} R2 {r.rvalue**2:.4f} resid sd {res.std():.2f}")
    print("   per-q mean residual of pooled fit", [round(res[A[:, 0] == q].mean(), 2) for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)])
print("within-cell Spearman of L with open / absent knots:")
for q in (0.3, 0.5, 0.7, 0.9):
    for g in (64, 128, 256, 512):
        s = A[(A[:, 0] == q) & (A[:, 1] == g)]
        if len(s) >= 20:
            print(q, g, len(s), round(spearmanr(s[:, 2], s[:, 3]).statistic, 3), round(spearmanr(s[:, 2], s[:, 4]).statistic, 3))
