"""COPY-READ-20261118-001B-E001: gate checks, run before the freeze.  Each prints PASS or FAIL."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import copylib as C  # noqa: E402

M = C.M
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS" if ok else "FAIL"), name, detail, flush=True)


# 1. on short runs: every recorded absorbing move has two or more end knots (MID-RULE-20261118-001A, E1), and the in-run look-alike
#    pairs are confirmed by exact isomorphism
ok = True
cnt = iso = 0
for n0, i in ((6, 3), (7, 10), (7, 30), (8, 5)):
    rows, refused, n_ref, ver = C.run(M.bracketings(0, n0 - 1)[i], n0, 18, 1000 + i)
    ok &= all(r["ends"] >= 2 for r in rows)
    cnt += len(rows)
    for t, v in ver.items():
        ok &= v["isomorphic"] <= v["mixed"]
        iso += v["isomorphic"]
check("absorbing moves have two or more end knots; look-alikes confirmed", ok, f"{cnt} absorbing moves, {iso} confirmed look-alikes")
print(sum(results), "of", len(results), "checks pass")
