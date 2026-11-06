import sys, sympy as sp
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
from presmodel import two_bridge
t = sp.symbols("t")
def fox(rel, gen):
    out, pref = 0, 0
    for g in rel:
        if abs(g) == gen:
            out += t ** pref if g > 0 else -t ** (pref - 1)
        pref += 1 if g > 0 else -1
    return sp.expand(out)
for (al, be) in [(3, 1), (5, 2), (5, 3), (7, 2), (7, 3), (9, 2), (13, 5), (17, 4)]:
    n, rels = two_bridge(al, be)
    r = rels[0]
    da = fox(r, 1)
    print(al, be, sp.factor(da), "| abelian exponent sums:", sum(1 for g in r if g == 1) - sum(1 for g in r if g == -1), sum(1 for g in r if g == 2) - sum(1 for g in r if g == -2))
