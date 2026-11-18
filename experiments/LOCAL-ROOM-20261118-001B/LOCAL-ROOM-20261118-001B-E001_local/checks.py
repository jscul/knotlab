"""Controls for locallib.py, run before the freeze."""
import random
import sys

import locallib as L

R = L.R
rng = random.Random("LOCAL-ROOM checks")
fails = 0


def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    fails += not ok


bad = tested = 0
for trial in range(80):
    n = rng.randint(3, 6)
    st = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, n))])
    if len(st) < 2:
        continue
    tested += 1
    if set(L.local_extensions(st, n, 3, 64)) != set(R.extensions(st, n, 3)):
        bad += 1
check(f"no reach limit (r = 64) gives exactly rules.extensions ({tested} bases)", bad == 0, f"{bad}")

bad = 0
for trial in range(80):
    n = rng.randint(3, 6)
    st = R.base_from_knots(n, [tuple(rng.sample(range(n), 3)) for _ in range(rng.randint(1, n))])
    if len(st) < 2:
        continue
    for (a0, a1), ks in L.local_extensions(st, n, 3, 1).items():
        Z, O = R.columns(st, n)
        for u, v in [tuple(x for x in k if x != n) for k in ks]:
            if R.pc(Z[u] & O[v]) + R.pc(O[u] & Z[v]) > 2:
                bad += 1
check("r = 1: every knot's old pair is adjacent (80 bases)", bad == 0, f"{bad}")

_, n, tr = L.grow("star", 10, "smoke", 3, 2)
check("growth runs (star start, r = 2, to 10)", n == 10 or any("stopped" in t for t in tr))
print("FAILURES:", fails)
sys.exit(1 if fails else 0)
