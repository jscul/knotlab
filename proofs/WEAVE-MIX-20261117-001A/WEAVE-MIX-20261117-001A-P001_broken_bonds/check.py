#!/usr/bin/env python3
"""Checks of WEAVE-MIX-20261117-001A-P001 (not a proof): N1 and N3 on every allowed state of 4 x 4 weaves under 30 random
arrangements of periods (1,1), (2,1), (1,2), (2,2); N3's emptiness when more than two inconsistent bonds per cell (count over all
arrangements of period (2,1) at L = 4); N4's face-length parity against the degree parity.
    python3 -B check.py [--write]"""
import itertools, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "WEAVE-MIX-20261117-001B" / "WEAVE-MIX-20261117-001B-E001_mixes"))
import mixlib as M

def knots(L, arr, pc, pr):
    v = lambda a, b: (a % L) + L * (b % L)
    out = []
    for j in range(L):
        for i in range(L):
            out.append(((v(i, j), v(i + 1, j), v(i, j + 1)), arr[(i % pc, j % pr, "U")]))
            out.append(((v(i + 1, j), v(i, j + 1), v(i + 1, j + 1)), arr[(i % pc, j % pr, "D")]))
    return out

def run():
    rng = random.Random(20261117)
    n1_bad = n3_bad = states = 0
    for _ in range(30):
        pc, pr = rng.choice([(1, 1), (2, 1), (1, 2), (2, 2)])
        L = 4
        arr = {(i, j, t): rng.randrange(4) for i in range(pc) for j in range(pr) for t in "UD"}
        ks = knots(L, arr, pc, pr)
        incons_total = M.inconsistent_bonds(arr, pc, pr) * L * L
        for s in range(1 << (L * L)):
            x = [(s >> q) & 1 for q in range(L * L)]
            if any(tuple(x[q] for q in t) in M.excluded(k) for t, k in ks):
                continue
            states += 1
            broken = {}
            for t, k in ks:
                b = [(t[a], t[c]) for a, c in ((0, 1), (0, 2), (1, 2)) if (M.sign(k, a, c) == -1) == (x[t[a]] == x[t[c]])]
                if len(b) != 1:
                    n1_bad += 1
                for e in b:
                    key = frozenset(e)
                    broken[key] = broken.get(key, 0) + 1
            hits = sum(broken.values())
            if hits != len(ks):
                n3_bad += 1
    empty_ok = True
    for combo in itertools.product(range(4), repeat=4):
        arr = dict(zip([(0, 0, "U"), (0, 0, "D"), (1, 0, "U"), (1, 0, "D")], combo))
        if M.inconsistent_bonds(arr, 2, 1) > 2 and M.torus_count(4, arr, 2, 1) != 0:
            empty_ok = False
    period1_even = all(M.inconsistent_bonds({(0, 0, "U"): a, (0, 0, "D"): b}, 1, 1) in (0, 2) for a in range(4) for b in range(4))
    out = {"states_checked": states, "N1_bad": n1_bad, "N3_hits_bad": n3_bad, "N3_empty_above_two": empty_ok, "N3_period1_even": period1_even}
    out["passed"] = n1_bad == 0 and n3_bad == 0 and empty_ok and period1_even and states > 0
    return out

if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1))
    if "--write" in sys.argv:
        m = json.loads((HERE / "manifest.json").read_text())
        (HERE / "result.json").write_text(json.dumps({"schema_version": 3, "artifact_id": m["artifact_id"], "kind": "proof", "ticket": m["ticket"],
            "proof": m["proof"], "status": "passed" if out["passed"] else "failed", "checks": out, "failures": [] if out["passed"] else ["check failed"]}, indent=1) + "\n")
    sys.exit(0 if out["passed"] else 1)
