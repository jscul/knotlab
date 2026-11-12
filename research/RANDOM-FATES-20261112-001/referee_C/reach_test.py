import sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from reach import *
k = regen(0.0, 3); st = B.make_step(800, k)
import time; t0=time.time()
print(reach(800, st, 117), time.time()-t0)
km = mirror(800, k); stm = B.make_step(800, km)
print(799 - reach(800, stm, 799 - 128))
