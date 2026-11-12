import sys
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
k = regen(0.0, 3)
print([t for t in k if 176 <= max(t) <= 194])
