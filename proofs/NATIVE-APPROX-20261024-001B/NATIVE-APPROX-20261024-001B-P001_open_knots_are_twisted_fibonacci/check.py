#!/usr/bin/env python3
"""Check of NATIVE-APPROX-20261024-001B-P001 (standard library only, seed 20261024).

The Fibonacci knot Fib allows 0, 2 or 3 ones; S excludes 000, 011 and 101 (one of the six open knots).
Checks:
- the six non-symmetric knots excluding three tuples form one orbit under place permutations and global complement; each equals Fib
  with one or two places negated (and no other knot does, apart from Fib, its full complement and the twisted ones);
- S(x, y, z) = Fib(x, y, not z);
- on random native networks of S with pinned and unpinned legs (random place assignment), the count equals the count of the twisted
  Fibonacci network: every knot becomes Fib, an edge with exactly one end at a negated place carries a disequality, an edge with both
  ends at negated places is plain, and pins at negated places are complemented;
- in the Fibonacci eigenbasis (v_j = (S_0j, S_1j), lambda_j = 1/S_0j), the disequality X becomes C = [[2 phi, phi], [phi, -2 phi]]/D^2,
  a symmetric orthogonal reflection with one negative entry; the signed two-spin sum (vertex weights lambda, plain edges delta,
  twisted edges C, legs v_s(pin) or v_s(0) + v_s(1)) equals the count on every network.
Controls: not-all-equal is not Fib with any negations; treating twisted edges as plain changes the count on some network; replacing C by
its entrywise absolute value changes the signed sum on some network.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))
FIB = frozenset(t for t in CUBE if sum(t) in (0, 2, 3))
S_KNOT = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)})


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def negate(R, neg):
    return frozenset(tuple(b ^ n for b, n in zip(t, neg)) for t in R)


def orbit_checks():
    K = knots()
    open_six = [R for R in K if len(R) == 5 and not all(tuple(t[p] for p in perm) in R for t in R
                                                        for perm in itertools.permutations(range(3)))]
    orbit = set()
    for perm in itertools.permutations(range(3)):
        for comp in (0, 1):
            orbit.add(frozenset(tuple(t[p] ^ comp for p in perm) for t in S_KNOT))
    twisted = {}
    for neg in CUBE:
        twisted.setdefault(negate(FIB, neg), []).append(sum(neg))
    return {"open knots": len(open_six), "they form one orbit": set(open_six) == orbit,
            "each is Fib with one or two negated places": all(R in twisted and set(twisted[R]) <= {1, 2} for R in open_six),
            "Fib with 0 or 3 negations gives the two no-lone-value knots": {negate(FIB, (0, 0, 0)), negate(FIB, (1, 1, 1))} ==
            {R for R in K if len(R) == 5 and R not in open_six},
            "S(x, y, z) = Fib(x, y, not z)": S_KNOT == negate(FIB, (0, 0, 1))}


def random_network(rng, n, L, free_prob):
    while True:
        slots = [(v, p) for v in range(n) for p in range(3)]
        rng.shuffle(slots)
        legs, rest = slots[:L], slots[L:]
        pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in pairs:
            parent[find(a[0])] = find(b[0])
        if len({find(v) for v in range(n)}) != 1:
            continue
        legvals = [None if rng.random() < free_prob else rng.randint(0, 1) for _ in legs]
        return pairs, list(zip(legs, legvals))


def count_S(n, pairs, legs):
    """direct count of the S network: knot v uses S on (slot 0, slot 1, slot 2)"""
    var = {}
    for k, (a, b) in enumerate(pairs):
        var[a] = var[b] = ("e", k)
    free = [i for i, (_, val) in enumerate(legs) if val is None]
    total = 0
    for fb in itertools.product((0, 1), repeat=len(free)):
        lv = {s: val for s, val in legs}
        for i, b in zip(free, fb):
            lv[legs[i][0]] = b
        for bits in range(1 << len(pairs)):
            ok = True
            for v in range(n):
                t = tuple((bits >> var[(v, p)][1] & 1) if (v, p) in var else lv[(v, p)] for p in range(3))
                if t not in S_KNOT:
                    ok = False
                    break
            total += ok
    return total


def twisted_description(n, pairs, legs):
    """Fib network: place 2 of each S knot is negated; edges with exactly one negated end are twisted; pins at place 2 complemented"""
    edges = []
    for (a, b) in pairs:
        twist = (a[1] == 2) != (b[1] == 2)
        edges.append((a, b, twist))
    pins = [(s, (None if val is None else (1 - val if s[1] == 2 else val))) for s, val in legs]
    return edges, pins


def count_twisted(n, edges, pins, plain_instead=False):
    free = [i for i, (_, val) in enumerate(pins) if val is None]
    total = 0
    for fb in itertools.product((0, 1), repeat=len(free)):
        pv = {s: val for s, val in pins}
        for i, b in zip(free, fb):
            pv[pins[i][0]] = b
        for bits in range(1 << len(edges)):
            seen = {}
            for k, (a, b, twist) in enumerate(edges):
                x = bits >> k & 1
                seen[a] = x
                seen[b] = (1 - x) if (twist and not plain_instead) else x
            seen.update(pv)
            if all(tuple(seen[(v, p)] for p in range(3)) in FIB for v in range(n)):
                total += 1
    return total


PHI = (1 + 5 ** 0.5) / 2
D2 = 2 + PHI
D = math.sqrt(D2)
V = [(1 / D, PHI / D), (PHI / D, -1 / D)]          # v_j = (S_0j, S_1j)
LAM = [D, D / PHI]                                   # lambda_j = 1 / S_0j


def c_matrix(absolute=False):
    C = [[V[j][0] * V[k][1] + V[j][1] * V[k][0] for k in range(2)] for j in range(2)]
    return [[abs(x) for x in row] for row in C] if absolute else C


def signed_sum(n, edges, pins, absolute=False):
    C = c_matrix(absolute)
    tot = 0.0
    for s in itertools.product((0, 1), repeat=n):
        w = 1.0
        for v in range(n):
            w *= LAM[s[v]]
        for a, b, twist in edges:
            if twist:
                w *= C[s[a[0]]][s[b[0]]]
            elif s[a[0]] != s[b[0]]:
                w = 0.0
                break
        if w == 0.0:
            continue
        for (v, p), val in pins:
            w *= (V[s[v]][0] + V[s[v]][1]) if val is None else V[s[v]][val]
        tot += w
    return tot


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    orb = orbit_checks()
    C = c_matrix()
    expected = [[2 * PHI / D2, PHI / D2], [PHI / D2, -2 * PHI / D2]]
    cinfo = {"C matches [[2 phi, phi], [phi, -2 phi]]/D^2": all(abs(C[i][j] - expected[i][j]) < 1e-12 for i in range(2) for j in range(2)),
             "C is symmetric and orthogonal (C C = I)": all(abs(sum(C[i][k] * C[k][j] for k in range(2)) - (i == j)) < 1e-12
                                                         for i in range(2) for j in range(2)),
             "negative entries of C": sum(x < 0 for row in C for x in row),
             "Fib = sum lambda_j v_j^3": all(abs(sum(LAM[j] * V[j][x[0]] * V[j][x[1]] * V[j][x[2]] for j in range(2)) - (x in FIB)) < 1e-12
                                            for x in CUBE)}
    nets = {"networks": 0, "S count = twisted Fibonacci count": 0, "signed two-spin sum = count": 0,
            "twisted edges present": 0}
    plain_differs = abs_differs = False
    for _ in range(1000):
        n = rng.randint(1, 7)
        L = 3 if n == 1 else rng.randint(0, n + 2)
        if (3 * n - L) % 2:
            L += 1
        if L > 3 * n or L > n + 2 + (n == 1) * 2:
            continue
        pairs, legs = random_network(rng, n, L, free_prob=rng.choice([0.0, 0.3]))
        if len(pairs) > 11:
            continue
        cs = count_S(n, pairs, legs)
        edges, pins = twisted_description(n, pairs, legs)
        ct = count_twisted(n, edges, pins)
        sg = signed_sum(n, edges, pins)
        nets["networks"] += 1
        nets["twisted edges present"] += any(t for _, _, t in edges)
        nets["S count = twisted Fibonacci count"] += cs == ct
        nets["signed two-spin sum = count"] += abs(sg - cs) < 1e-6 * max(1, cs)
        plain_differs |= count_twisted(n, edges, pins, plain_instead=True) != cs
        abs_differs |= abs(signed_sum(n, edges, pins, absolute=True) - cs) > 1e-6 * max(1, cs)
    nae = frozenset(t for t in CUBE if 0 < sum(t) < 3)
    controls = {"not-all-equal is not Fib with negations": all(negate(FIB, neg) != frozenset(tuple(t[p] for p in perm) for t in nae)
                                                                for neg in CUBE for perm in itertools.permutations(range(3))),
                "treating twisted edges as plain changes some count": plain_differs,
                "the absolute value of C changes the signed sum on some network": abs_differs}
    ok = (all(v is True for k, v in orb.items() if isinstance(v, bool)) and orb["open knots"] == 6
          and cinfo["C matches [[2 phi, phi], [phi, -2 phi]]/D^2"] and cinfo["C is symmetric and orthogonal (C C = I)"]
          and cinfo["negative entries of C"] == 1 and cinfo["Fib = sum lambda_j v_j^3"]
          and nets["S count = twisted Fibonacci count"] == nets["signed two-spin sum = count"] == nets["networks"] > 0
          and nets["twisted edges present"] > 0 and all(controls.values()))
    result["checks"] = {"orbit and twists": orb, "the twist in the Fibonacci basis": cinfo, "random networks": nets}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
