import sys
from collections import Counter
from ring import ring
sys.path.append(str(__import__('pathlib').Path(__file__).resolve().parents[3] / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
import startlib as S
F=S.F
P=S.from_junctions(ring([4,4,4,4,5])); P.linalg=False
log=[]
def rule(P, info, rng):
    log.append((Counter((i['p'], i['d']) for i in info)))
    return F.fewest(P, info, rng)
for r in range(22):
    P.step(rule, None)
for t,c in enumerate(log, start=1): print(t, sum(c.values()), dict(sorted(c.items())))
