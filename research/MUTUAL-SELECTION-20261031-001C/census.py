"""Lane C (MUTUAL-SELECTION-20261031-001C): census of the signed Fibonacci (no-lone) law on small cubic systems.

Every connected cubic bipartite graph on 2n vertices (n = 3..8; the counts 1, 1, 2, 5, 13, 38 of OEIS A006823 are reached by sampling
with isomorphism rejection) is read as a cubic system (one side lines, the other points). For every signing modulo point switching
(fix the sign of each point's first incidence) we decide, with bitset arithmetic over all 2^n colourings, whether the signed law has a
solution. Laws: no-lone {0,2,3} (Fibonacci), its complement {0,1,3}, and not-all-equal {1,2} for comparison.

Run: .venv/bin/python -B census.py [--write]"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
T0 = time.time()
A006823 = {3: 1, 4: 1, 5: 2, 6: 5, 7: 13, 8: 38}
rng = random.Random(20261031)


def sample(n):
    while True:
        slots = [p for p in range(n) for _ in range(3)]
        rng.shuffle(slots)
        lines = [tuple(slots[3 * i:3 * i + 3]) for i in range(n)]
        if all(len(set(l)) == 3 for l in lines):
            g = nx.Graph([(('l', i), ('p', p)) for i, l in enumerate(lines) for p in l])
            if g.number_of_edges() == 3 * n and nx.is_connected(g):
                return lines, g


def all_graphs(n):
    reps = []
    tries = 0
    while len(reps) < A006823[n]:
        lines, g = sample(n)
        tries += 1
        if any(nx.is_isomorphic(g, h) for h, _ in reps):
            continue
        reps.append((g, lines))
    return reps, tries


def unsat_signings(lines, n, W):
    """the signings (mod point switching) with no solution, as tuples of sign bits over the free incidences"""
    N = 1 << n
    col = [[(c >> p) & 1 for p in range(n)] for c in range(N)]
    masks = {}
    for i, l in enumerate(lines):
        for sg in itertools.product((0, 1), repeat=3):
            m = 0
            for c in range(N):
                if sum(col[c][p] ^ sg[k] for k, p in enumerate(l)) in W:
                    m |= 1 << c
            masks[(i, sg)] = m
    first = {}
    for i, l in enumerate(lines):
        for k, p in enumerate(l):
            first.setdefault(p, (i, k))
    fixed = set(first.values())
    free = [(i, k) for i in range(n) for k in range(3) if (i, k) not in fixed]
    out = []
    full = (1 << N) - 1
    for bits in itertools.product((0, 1), repeat=len(free)):
        sg = dict(zip(free, bits))
        m = full
        for i in range(n):
            m &= masks[(i, tuple(sg.get((i, k), 0) for k in range(3)))]
            if not m:
                break
        if not m:
            out.append(bits)
    return out, len(free)


OUT = {}
for n in range(3, 9):
    reps, tries = all_graphs(n)
    rows = []
    for g, lines in reps:
        fib, nf = unsat_signings(lines, n, {0, 2, 3})
        nae, _ = unsat_signings(lines, n, {1, 2})
        fib2, _ = unsat_signings(lines, n, {0, 1, 3})
        rows.append({"girth": nx.girth(g), "repeated lines": len({tuple(sorted(l)) for l in lines}) < n,
                     "no-lone unsat signings": len(fib), "complement law {0,1,3} unsat": len(fib2),
                     "not-all-equal unsat signings (Pfaffian iff > 0)": len(nae), "signings": 2 ** nf,
                     "lines": [list(l) for l in lines]})
        print(f"n={n} girth {nx.girth(g)}: no-lone {len(fib)}, {{0,1,3}} {len(fib2)}, NAE {len(nae)} of {2 ** nf}", round(time.time() - T0, 1),
              "s", flush=True)
    OUT[n] = {"graphs": len(reps), "sampling tries": tries, "rows": rows,
              "graphs with no-lone failures": sum(1 for r in rows if r["no-lone unsat signings"]),
              "graphs with not-all-equal failures": sum(1 for r in rows if r["not-all-equal unsat signings (Pfaffian iff > 0)"]),
              "graphs with both": sum(1 for r in rows if r["no-lone unsat signings"] and r["not-all-equal unsat signings (Pfaffian iff > 0)"])}
    print("SUMMARY n =", n, {k: v for k, v in OUT[n].items() if k != "rows"}, flush=True)
if "--write" in sys.argv:
    (HERE / "census.json").write_text(json.dumps(OUT, indent=1) + "\n")
print("seconds", round(time.time() - T0, 1))
