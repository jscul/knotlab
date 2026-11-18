"""COPY-CLASS-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import classlib as C  # noqa: E402

M = C.M
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


# 1. C1: on short runs, the new crossings found between the two end pairs' splits are all the new crossings; and CRANY (SEED's own
#    clause (b) with clause (a) read locally) equals SEED's verdict on every crossing-making knot set (a check of the engine)
ok1 = ok2 = True
cnt = 0
for n0, i in ((6, 3), (7, 10), (8, 5)):
    rows = C.run(M.bracketings(0, n0 - 1)[i], n0, 18, 500 + i)
    for r in rows:
        if r["local_equals_all"] is not None:
            ok1 &= r["local_equals_all"]
        cnt += 1
    ext = {}
    for r in rows:
        k = (r["n"], tuple(r["ext"]))
        e = ext.setdefault(k, [r["seed"], False])
        e[1] |= r["crany"]
    ok2 &= all(a == b for a, b in ext.values())
check("C1: local new crossings = all new crossings", ok1, f"{cnt} knot sets")
check("CRANY = SEED on every extension", ok2)
print(sum(results), "of", len(results), "checks pass")
