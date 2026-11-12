import sys, itertools
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from reach import *
k = regen(0.9, 6); st = B.make_step(800, k); km = mirror(800, k); stm = B.make_step(800, km)
ks = set(k)
print("r(205)", reach(800, st, 205), "back(205)", 799 - reach(800, stm, 799 - 205))
print([(v, B.least_bond(800, k, 140, v, margin=800, step=st)[0]) for v in range(196, 216)])
print([(u, B.least_bond(800, k, u, 205, margin=800, step=st)[0]) for u in range(170, 205)])
for m in range(199, 212):
    win = list(itertools.combinations(range(m - 3, m + 1), 3))
    print(m, "missing", [t for t in win if t not in ks])
