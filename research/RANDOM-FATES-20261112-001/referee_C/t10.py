import sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
k = regen(0.9, 6); st = B.make_step(800, k)
print([(v, B.least_bond(800, k, 140, v, margin=800, step=st)[0]) for v in (185, 189, 193, 197, 201, 205, 209, 301, 401, 501)])
