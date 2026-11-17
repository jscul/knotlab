#!/usr/bin/env python3
"""Checks of KNOT-ORDER-20261117-001A-P001 (not a proof).
K1: for n = 5, 6, every (p, q) state and 300 random constraints (2 to 4 places, excluded patterns chosen so every threshold stays
    allowed): any constraint excluding the (p, q) state has a place in each block.
K2: windows of three consecutive places allow the (1, 3) state at n = 4 (0110) and n = 5.
K4: inserting with B(k, new, k + 1) into lines of m = 3..7 gives the line on the new order (2(m + 1) states).
    python3 -B check.py [--write]"""
import itertools, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent

def thresholds(order, n):
    out = set()
    for k in range(n + 1):
        a = sum(1 << order[i] for i in range(k, n))
        out |= {a, ((1 << n) - 1) ^ a}
    return out

def state_pq(n, p, q):
    return sum(1 << i for i in range(p, q))      # positions 0-based: ones on [p, q-1], i.e. changes after p and q (1-based)

def run():
    rng = random.Random(3)
    k1_bad = 0
    for n in (5, 6):
        th = thresholds(list(range(n)), n)
        for _ in range(300):
            k = rng.randint(2, 4)
            pl = sorted(rng.sample(range(n), k))
            seen = {tuple((s >> x) & 1 for x in pl) for s in th}
            free = [t for t in itertools.product((0, 1), repeat=k) if t not in seen]
            if not free:
                continue
            ex = set(rng.sample(free, rng.randint(1, len(free))))
            for p in range(1, n - 1):
                for q in range(p + 1, n):
                    s = state_pq(n, p, q)
                    if tuple((s >> x) & 1 for x in pl) in ex:
                        blocks = (range(0, p), range(p, q), range(q, n))
                        if not all(any(x in b for x in pl) for b in blocks):
                            k1_bad += 1
    BTW = {(0, 1, 0), (1, 0, 1)}
    def allowed(n, knots):
        return {s for s in range(1 << n) if all(tuple((s >> x) & 1 for x in t) not in BTW for t in knots)}
    k2 = all(state_pq(n, 1, 3) in allowed(n, [(i, i + 1, i + 2) for i in range(n - 2)]) for n in (4, 5))
    k4 = True
    for m in range(3, 8):
        base = [(i, j, l) for i, j, l in itertools.combinations(range(m), 3)]
        for kk in range(m - 1):
            sts = allowed(m + 1, base + [(kk, m, kk + 1)])
            order = list(range(kk + 1)) + [m] + list(range(kk + 1, m))
            k4 &= sts == thresholds(order, m + 1) and len(sts) == 2 * (m + 1)
    out = {"K1_bad": k1_bad, "K2": k2, "K4": k4}
    out["passed"] = k1_bad == 0 and k2 and k4
    return out

if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1))
    if "--write" in sys.argv:
        m = json.loads((HERE / "manifest.json").read_text())
        (HERE / "result.json").write_text(json.dumps({"schema_version": 3, "artifact_id": m["artifact_id"], "kind": "proof", "ticket": m["ticket"],
            "proof": m["proof"], "status": "passed" if out["passed"] else "failed", "checks": out, "failures": [] if out["passed"] else ["check failed"]}, indent=1) + "\n")
    sys.exit(0 if out["passed"] else 1)
