import sys, itertools
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from verify_bonds import *
k = regen(0.9, 6); N = 800
MS, FS = tables(N, k)
def ext(assign):
    R = 255
    for m in range(N):
        R = MS[m][assign[m]][R] if m in assign else FS[m][R]
        if R == 0: return False
    return True
V = [140, 202, 203, 204, 205]
pats = [p for p in itertools.product((0, 1), repeat=5) if ext(dict(zip(V, p)))]
print("allowed patterns on", V, len(pats)); print(pats)
# where does the complete region start? list missing triples before 199
ks = set(k)
last_open = max(m for m in range(3, 200) if any(t not in ks for t in itertools.combinations(range(m - 3, m + 1), 3)))
print("last open window before 199 ends at", last_open)
print("knots 136..146:", [t for t in k if 136 <= max(t) <= 146])
for m in range(136, 150):
    win = list(itertools.combinations(range(m - 3, m + 1), 3)); print(m, "missing", [t for t in win if t not in ks])
