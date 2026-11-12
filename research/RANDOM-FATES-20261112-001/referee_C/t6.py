import sys, itertools
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from reach import *
k = regen(0.9, 6); st = B.make_step(800, k); km = mirror(800, k); stm = B.make_step(800, km)
r = reach(800, st, 140); print("r(140)", r)
rec = [x for x in load_bases() if x["q"] == 0.9 and x["base"] == 6][0]
print([(p["g"], p["i"], p["j"], p["L"]) for p in rec["pairs"] if p["i"] == 140])
ks = set(k)
for v in range(r - 6, r + 8):
    bm = reach(800, stm, 799 - v)
    print(v, "back-reach", None if bm is None else 799 - bm, "r", reach(800, st, v))
for m in range(r - 8, r + 10):
    win = list(itertools.combinations(range(m - 3, m + 1), 3))
    print(m, "window", m - 3, "..", m, "present", [t for t in win if t in ks], "missing", [t for t in win if t not in ks])
