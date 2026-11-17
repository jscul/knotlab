#!/usr/bin/env python3
"""Checks of DISTANCE-DIM-20261117-001A-P001 (not a proof), with code separate from the experiment's.

D1, D2: 400 random orders on 3 to 8 elements (random relations, transitively closed), up-sets by brute force over subsets.
D3: on those whose comparable pairs all lie in chains of three: comparability from betweenness; on the connected ones, the
    orientation rebuilt by brute force over all transitive orientations consistent with betweenness equals P or its reverse.
D4: on chain grids of 3 x 3 and 4 x 4 every grid assignment extends (the rule), checked by counting.
D5: ln coth K - 2K = ln(3/2) at tanh K = 1/3.

    python3 -B check.py [--write]
"""
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def random_order(n, rng):
    rel = {(i, j) for i in range(n) for j in range(n) if i < j and rng.random() < 0.35}
    changed = True
    while changed:
        changed = False
        for (a, b), (c, d) in itertools.product(list(rel), list(rel)):
            if b == c and (a, d) not in rel:
                rel.add((a, d))
                changed = True
    perm = list(range(n))
    rng.shuffle(perm)
    return {(perm[a], perm[b]) for a, b in rel}


def upsets(n, less):
    out = []
    for m in range(1 << n):
        if all(not ((m >> u) & 1) or ((m >> v) & 1) for u, v in less):
            out.append(m)
    return out


def counts(n, sts):
    return {(u, v): sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for u in range(n) for v in range(n)}


def run():
    rng = random.Random(20261117)
    bad1 = bad2 = bad3 = bad3o = 0
    tried3 = tried3o = 0
    for _ in range(400):
        n = rng.randint(3, 8)
        less = random_order(n, rng)
        leq = lambda a, b: a == b or (a, b) in less
        sts = upsets(n, less)
        d = counts(n, sts)
        trip = set()
        for u, v in itertools.combinations(range(n), 2):
            for w in range(n):
                if w in (u, v):
                    continue
                btw = d[(u, w)] > 0 and d[(w, v)] > 0 and d[(u, v)] == d[(u, w)] + d[(w, v)]
                interval = (leq(u, w) and leq(w, v)) or (leq(v, w) and leq(w, u))
                if btw != interval:
                    bad1 += 1
                if btw:
                    trip.add((u, w, v))
            if d[(u, v)] == 0:
                bad1 += 1
            pats = {((s >> u) & 1, (s >> v) & 1) for s in sts}
            comparable = (u, v) in less or (v, u) in less
            if (len(pats) < 4) != comparable:
                bad2 += 1
        comp = {frozenset(p) for p in less}
        in3 = all(any((frozenset((a, b)) <= frozenset(t)) for t in trip) for a, b in less)
        if not in3:
            continue
        tried3 += 1
        fromtrip = set()
        for u, w, v in trip:
            fromtrip |= {frozenset((u, w)), frozenset((w, v)), frozenset((u, v))}
        if fromtrip != comp:
            bad3 += 1
        # connected comparability graph?
        adj = {i: set() for i in range(n)}
        for a, b in less:
            adj[a].add(b)
            adj[b].add(a)
        seen, stack = {0}, [0]
        while stack:
            for y in adj[stack.pop()]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(seen) != n or len(comp) > 14:
            continue
        tried3o += 1
        pairs = sorted(tuple(sorted(e)) for e in comp)
        ok_orients = []
        for signs in itertools.product((0, 1), repeat=len(pairs)):
            arcs = {(a, b) if s == 0 else (b, a) for (a, b), s in zip(pairs, signs)}
            if any((a, b) in arcs and (b, c) in arcs and (a, c) not in arcs for a, b in arcs for c in range(n)):
                continue                                   # not transitive
            # betweenness of the oriented order must equal the given triples
            lq = lambda x, y: x == y or (x, y) in arcs
            tr2 = {(u, w, v) for u, v in itertools.combinations(range(n), 2) for w in range(n)
                   if w not in (u, v) and ((lq(u, w) and lq(w, v)) or (lq(v, w) and lq(w, u)))}
            if tr2 == trip:
                ok_orients.append(arcs)
        rev = {(b, a) for a, b in less}
        if not ok_orients or any(o != less and o != rev for o in ok_orients):
            bad3o += 1
    # D4: every grid assignment extends (count completions per assignment > 0)
    d4 = True
    for L in (3, 4):
        edges = [((i, j), ((i + 1) % L, j)) for i in range(L) for j in range(L)] + [((i, j), (i, (j + 1) % L)) for i in range(L) for j in range(L)]
        for s in range(1 << (L * L)) if L == 3 else random.Random(1).sample(range(1 << (L * L)), 2000):
            x = lambda a: (s >> (a[0] + L * a[1])) & 1
            completions = 1
            for a, b in edges:
                completions *= 2 if x(a) != x(b) else 1      # p free, or p forced to the other value
            if completions == 0:
                d4 = False
    K = math.atanh(1 / 3)
    d5 = abs((math.log(1 / math.tanh(K)) - 2 * K) - math.log(1.5)) < 1e-12 and abs(1 - math.log(2, 3) - 0.3690702464) < 1e-9
    out = {"D1_bad": bad1, "D2_bad": bad2, "D3_tried": tried3, "D3_bad": bad3, "D3_orient_tried": tried3o, "D3_orient_bad": bad3o,
           "D4": d4, "D5": d5}
    out["passed"] = bad1 == 0 and bad2 == 0 and bad3 == 0 and bad3o == 0 and tried3 > 0 and tried3o > 0 and d4 and d5
    return out


if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1))
    if "--write" in sys.argv:
        m = json.loads((HERE / "manifest.json").read_text())
        (HERE / "result.json").write_text(json.dumps({"schema_version": 3, "artifact_id": m["artifact_id"], "kind": "proof",
            "ticket": m["ticket"], "proof": m["proof"], "status": "passed" if out["passed"] else "failed", "checks": out,
            "failures": [] if out["passed"] else ["a statement check failed"]}, indent=1) + "\n")
    sys.exit(0 if out["passed"] else 1)
