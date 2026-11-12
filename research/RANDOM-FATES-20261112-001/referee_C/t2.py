import sys, time
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
bases = load_bases()
rec = [r for r in bases if r["q"] == 0.0][0]
knots = regen(rec["q"], rec["base"])
step = B.make_step(800, knots)
for mg in (8, 16, 32, 64, 128, 800):
    t0 = time.time()
    print(mg, B.least_bond(800, knots, 117, 128, margin=mg, step=step, max_states=10**6), round(time.time() - t0, 1), flush=True)
