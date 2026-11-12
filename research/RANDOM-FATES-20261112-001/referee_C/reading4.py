import sys, itertools, numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from scipy.stats import spearmanr, linregress
bases = load_bases()
cells = {}
for rec in bases:
    if rec["q"] < 0.5: continue
    k = regen(rec["q"], rec["base"]); ks = set(k)
    miss = {m: sum(1 for t in itertools.combinations(range(m - 3, m + 1), 3) if t not in ks) for m in range(3, 800)}
    for p in rec["pairs"]:
        if p["status"] != "ok" or p["g"] < 128: continue
        ms = [miss[m] for m in range(p["i"] + 3, p["j"] + 1)]
        cells.setdefault((rec["q"], p["g"]), []).append((p["L"], p["open"], sum(ms), sum(1 for x in ms if x >= 2)))
for key in sorted(cells):
    A = np.array(cells[key])
    if len(A) < 20: continue
    print(key, len(A), "rho(L,open)", round(spearmanr(A[:, 0], A[:, 1]).statistic, 3), "rho(L,missing)", round(spearmanr(A[:, 0], A[:, 2]).statistic, 3), "rho(L,miss>=2)", round(spearmanr(A[:, 0], A[:, 3]).statistic, 3))
