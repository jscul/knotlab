import sys, itertools, numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from scipy.stats import linregress, spearmanr
bases = load_bases()
rows = []
for rec in bases:
    k = regen(rec["q"], rec["base"]); ks = set(k)
    miss = {}
    for m in range(3, 800):
        miss[m] = sum(1 for t in itertools.combinations(range(m - 3, m + 1), 3) if t not in ks)
    for p in rec["pairs"]:
        if p["status"] != "ok" or p["g"] < 16: continue
        i, j = p["i"], p["j"]
        ms = [miss[m] for m in range(i + 3, j + 1)]
        openw = sum(1 for x in ms if x > 0)
        assert openw == p["open"]
        runs = sum(1 for a, b in zip([0] + ms, ms) if a == 0 and b > 0)
        # distinctions not inside any complete window
        cov = set()
        for m in range(i + 3, j + 1):
            if miss[m] == 0: cov.update(range(m - 3, m + 1))
        uncovered = sum(1 for v in range(i, j + 1) if v not in cov)
        # windows missing at least 2 / at least 3
        rows.append((rec["q"], p["L"], p["gap"], openw, sum(ms), runs, uncovered, sum(1 for x in ms if x >= 2), sum(1 for x in ms if x >= 3), p["d"]))
A = np.array(rows, float)
names = ["gap", "open", "missing_total", "open_runs", "uncovered", "miss>=2", "miss>=3", "d"]
for c, nm in enumerate(names, start=2):
    sl = []
    for q in (0.0, 0.1, 0.3, 0.5, 0.7, 0.9):
        s = A[A[:, 0] == q]; r = linregress(s[:, c], s[:, 1]); sl.append(round(r.slope, 3))
    r = linregress(A[:, c], A[:, 1])
    print(f"{nm:14s} per-q slope {sl}  pooled R2 {r.rvalue**2:.3f}")
