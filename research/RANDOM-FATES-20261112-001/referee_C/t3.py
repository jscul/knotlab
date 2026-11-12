import sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
bases = load_bases()
rec = [r for r in bases if r["q"] == 0.0][0]
knots = regen(rec["q"], rec["base"])
print([t for t in knots if 105 <= max(t) <= 140])
step = B.make_step(800, knots)
row = []
for j in range(118, 160):
    L = B.least_bond(800, knots, 117, j, margin=800, step=step)[0]
    row.append((j, L))
print(row)
row = []
for i in range(100, 128):
    L = B.least_bond(800, knots, i, 128, margin=800, step=step)[0]
    row.append((i, L))
print(row)
