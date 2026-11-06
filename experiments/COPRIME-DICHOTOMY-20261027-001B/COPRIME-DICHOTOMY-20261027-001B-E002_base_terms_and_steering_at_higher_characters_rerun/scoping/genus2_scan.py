import sys, itertools
from fractions import Fraction
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cdA")
from presmodel import PresModel, two_bridge
from twobridge_scan import fourway
from cd_lib import root_of_unity

def cf(a):
    x = Fraction(a[-1])
    for v in reversed(a[:-1]): x = v + 1 / x
    return x.numerator, x.denominator

rng = np.random.default_rng(int(sys.argv[1]))
p, d, e = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
zeta = root_of_unity(p, d); t0 = pow(zeta, e, p)
A = fourway(p, d, zeta, e)
tested = van = 0
seen = set()
R = int(sys.argv[5])
for a in itertools.product([v for v in range(-R, R + 1) if v], repeat=4):
    al, be = cf([2 * v for v in a])
    if al % 2 == 0 or abs(al) > 400: continue
    key = (abs(al), be % abs(al))
    if key in seen: continue
    seen.add(key)
    n, rels = two_bridge(al, be)
    Mo = PresModel(n, rels, A)
    if len(Mo.cocycles[e % d]) != 2 or len(Mo.cocycles[(-e) % d]) != 2: continue
    ix, iy, iw = (A.idx[s] for s in "xyw")
    bs = 20
    def rc(c): return (rng.integers(0, p, (bs, 2)) @ Mo.cocycles[c]) % p
    ok, _ = Mo.solve({ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)})
    tested += 1
    if ok.all():
        van += 1
        amph = (be * be + 1) % abs(al) == 0
        print(f"vanishing: [2a] = {[2 * v for v in a]} b({abs(al)}, {be % abs(al)}) amphichiral={amph}", flush=True)
print(f"p={p} d={d} t0={t0} square={pow(t0, (p - 1) // 2, p) == 1}: tested {tested}, vanishing {van}")
