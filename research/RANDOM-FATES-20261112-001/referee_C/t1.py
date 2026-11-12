import sys, time
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
import exhpy
bases = load_bases()
rec = [r for r in bases if r["q"] == 0.0][0]
knots = regen(rec["q"], rec["base"])
print("knots", len(knots), rec["knots"], "N", max(max(t) for t in knots) + 1)
pp = regen_pairs(rec["q"], rec["base"])
print(all((p["i"], p["j"]) == (a[2], a[3]) for p, a in zip(rec["pairs"], pp)))
qs = []; ps = []
for p in rec["pairs"]:
    if p["g"] <= 16:
        lo, hi = max(0, p["i"] - 8), min(799, p["j"] + 8)
        K = p["L"] if p["L"] else 12
        qs.append((lo, hi, p["i"], p["j"], K, 2 * 10**8)); ps.append(p)
t0 = time.time()
res = exhpy.run(800, knots, qs)
for p, r in zip(ps, res): print(p["g"], p["i"], p["j"], p["L"], r[0], r[1], r[2], p["members"], r[3])
print(time.time() - t0)
