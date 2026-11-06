#!/usr/bin/env python3
"""Check of SOFT-HUB-20261024-001A-P001 (standard library only, seed 20261024).

A native gadget is a connected native network of one knot with pins, free legs (summed) and three terminals; F(x) counts its
consistent assignments with terminal values x. For an axis u (an antipodal pair u, u-bar), the split products are
s_u = sum_i F(u + e_i) F(u-bar + e_i), and the hub ratio is min(F(u), F(u-bar)) / max over the other six F(x).
Checks, on random gadgets of all 34 knots enumerated exhaustively:
- Theorem 1: every support is co-independent and excludes at most four tuples, so none is the equality on three legs; no
  co-independent relation on three bits excludes more than four tuples;
- Lemma 2: for every axis, the pairs (sigma with terminals u, tau with terminals u-bar) whose difference graph does not link all three
  terminals are mapped, by exchanging the component of terminal 1, to valid pairs on split terminal patterns, injectively; so
  F(u) F(u-bar) = separated + linked with separated <= s_u;
- Lemma 3: every linked pair has a knot where the difference branches, with antipodal local tuples; parity knots allow no antipodal
  pair, so their gadgets have no linked pairs;
- Theorem 4 (given McQuillan, consistency only): gadgets of windable knots satisfy F(u) F(u-bar) <= s_u on every axis;
- Theorem 5: parity gadgets are constant on their support and have hub ratio at most 1; gadgets of the no-lone-1 knot satisfy
  f2 = f0 + f1 and f3 = f1 + f2 (by terminal weight), those of the no-lone-0 knot the mirror recurrence, and both have hub ratio at
  most 1 on every axis;
- Proposition 6: the eight knots excluding three tuples are exactly the closed neighbourhoods plus antipodes N[c] + {c-bar}; their
  only allowed antipodal pair is {c, c-bar}, where every one-slot exchange fails; in the six open knots every allowed pair at distance
  two has an excluded intermediate.
Controls: three equality wires sharing one variable (a hub, not native) give the equality on three legs, and the co-independence
test rejects its support; exchanging only terminal 1's own edge instead of its whole component gives an invalid configuration on
some pair; the open knot excluding 000, 011 and 101 violates the split inequality on the axis 110.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))
AXES = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def excluded(R):
    return [t for t in CUBE if t not in R]


def comp(x):
    return tuple(1 - b for b in x)


def xor(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def unit(i):
    return tuple(int(j == i) for j in range(3))


def adjacent(s, t):
    return sum(a != b for a, b in zip(s, t)) == 1


def split_sum(F, u):
    return sum(F[xor(u, unit(i))] * F[xor(comp(u), unit(i))] for i in range(3))


def hub_ratio(F, u):
    off = max(F[x] for x in CUBE if x not in (u, comp(u)))
    m = min(F[u], F[comp(u)])
    if m == 0:
        return 0.0
    return m / off if off > 0 else float("inf")


def windable(R):
    F = {x: int(x in R) for x in CUBE}
    return all(F[x] * F[comp(x)] <= split_sum(F, x) for x in CUBE)


def connected(n, a):
    parent = list(range(n))

    def find(z):
        while parent[z] != z:
            parent[z] = parent[parent[z]]
            z = parent[z]
        return z
    ends = {}
    for (v, p), k in a.items():
        if k[0] == "E":
            ends.setdefault(k[1], []).append(v)
    for vs in ends.values():
        parent[find(vs[0])] = find(vs[1])
    return len({find(v) for v in range(n)}) == 1


def random_gadget(rng, n):
    slots = [(v, p) for v in range(n) for p in range(3)]
    for _ in range(2000):
        rng.shuffle(slots)
        a = {slots[k]: ("T", k) for k in range(3)}
        rest = slots[3:]
        m = len(rest)
        npf = rng.randint(0, max(0, m - 2 * (n - 1)))
        if (m - npf) % 2:
            npf += 1
        if npf > m:
            continue
        for s in rest[:npf]:
            a[s] = ("P", rng.randint(0, 1)) if rng.random() < 0.7 else ("F",)
        pr = rest[npf:]
        for i in range(0, len(pr), 2):
            a[pr[i]] = a[pr[i + 1]] = ("E", i // 2)
        if connected(n, a):
            return a
    return None


def item(a, s):
    k = a[s]
    return ("E", k[1]) if k[0] == "E" else ("T", k[1]) if k[0] == "T" else ("F", s) if k[0] == "F" else None


def local(a, conf, v):
    return tuple(conf[item(a, (v, p))] if a[(v, p)][0] != "P" else a[(v, p)][1] for p in range(3))


def configurations(R, n, a):
    items = sorted({item(a, s) for s in a if a[s][0] != "P"})
    by = {x: [] for x in CUBE}
    for vals in itertools.product((0, 1), repeat=len(items)):
        conf = dict(zip(items, vals))
        if all(local(a, conf, v) in R for v in range(n)):
            by[tuple(conf[("T", k)] for k in range(3))].append(conf)
    return by


def components(n, a, diff):
    parent = {z: z for z in diff}

    def find(z):
        while parent[z] != z:
            parent[z] = parent[parent[z]]
            z = parent[z]
        return z
    for v in range(n):
        its = [item(a, (v, p)) for p in range(3) if a[(v, p)][0] != "P" and item(a, (v, p)) in diff]
        for z in its[1:]:
            parent[find(its[0])] = find(z)
    out = {}
    for z in diff:
        out.setdefault(find(z), set()).add(z)
    return list(out.values())


def exchange_pairs(R, n, a, by, u):
    """returns (separated, linked, ok) for the axis u"""
    sep = linked = 0
    images = set()
    ok = True
    for s in by[u]:
        for t in by[comp(u)]:
            diff = {z for z in s if s[z] != t[z]}
            comps = components(n, a, diff)
            c1 = next(c for c in comps if ("T", 0) in c)
            terms = {z[1] for z in c1 if z[0] == "T"}
            if terms == {0, 1, 2}:
                linked += 1
                branching = [v for v in range(n)
                             if sum(1 for p in range(3) if a[(v, p)][0] != "P" and item(a, (v, p)) in c1) == 3]
                ok &= any(local(a, s, v) == comp(local(a, t, v)) for v in branching)
                continue
            sep += 1
            s2 = {z: (t[z] if z in c1 else s[z]) for z in s}
            t2 = {z: (s[z] if z in c1 else t[z]) for z in t}
            ok &= all(local(a, s2, v) in R and local(a, t2, v) in R for v in range(n))
            X = tuple(int(k in terms) for k in range(3))
            ok &= X in ((1, 0, 0), (1, 1, 0), (1, 0, 1))
            ok &= tuple(s2[("T", k)] for k in range(3)) == xor(u, X)
            key = (tuple(sorted(s2.items())), tuple(sorted(t2.items())))
            ok &= key not in images
            images.add(key)
    return sep, linked, ok


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    K = knots()
    parity = [R for R in K if len(R) == 4]
    nolone1 = frozenset(t for t in CUBE if sum(t) != 1)
    nolone0 = frozenset(t for t in CUBE if sum(t) != 2)

    # census of co-independent relations
    coind_max = max(8 - bin(m).count("1") for m in range(256)
                    if all(not adjacent(s, t) for s in CUBE for t in CUBE
                           if not (m >> CUBE.index(s) & 1) and not (m >> CUBE.index(t) & 1)))
    t1 = {"largest excluded set of a co-independent relation on three bits": coind_max,
          "gadgets": 0, "supports co-independent": 0, "supports excluding at most four": 0, "equality supports": 0}
    lem = {"gadget-axis cases": 0, "pairs": 0, "linked pairs": 0, "exchange valid and injective, terminals on split patterns": True,
           "F(u)F(u-bar) = separated + linked": True, "separated <= split products": True,
           "every linked pair branches at antipodal local tuples": True, "parity gadgets with linked pairs": 0}
    t4 = {"windable gadget-axis cases": 0, "F(u)F(u-bar) <= s_u": 0}
    t5 = {"parity gadgets": 0, "constant on support, hub ratio <= 1 on every axis": 0, "no-lone gadgets": 0,
          "recurrence holds": 0, "hub ratio <= 1 on every axis": 0}
    partial_fails = False
    for R in K:
        for g in range(14):
            n = rng.randint(1, 6)
            a = random_gadget(rng, n)
            if a is None:
                continue
            nvars = len({item(a, s) for s in a if a[s][0] != "P"})
            if nvars > 15:
                continue
            by = configurations(R, n, a)
            F = {x: len(by[x]) for x in CUBE}
            t1["gadgets"] += 1
            Z = [x for x in CUBE if F[x] == 0]
            co = all(not adjacent(s, t) for s in Z for t in Z)
            t1["supports co-independent"] += co
            t1["supports excluding at most four"] += len(Z) <= 4
            t1["equality supports"] += F[(0, 0, 0)] > 0 and F[(1, 1, 1)] > 0 and len(Z) == 6
            for u in AXES:
                if F[u] * F[comp(u)] > 6000:
                    continue
                sep, linked, ok = exchange_pairs(R, n, a, by, u)
                lem["gadget-axis cases"] += 1
                lem["pairs"] += sep + linked
                lem["linked pairs"] += linked
                lem["exchange valid and injective, terminals on split patterns"] &= ok
                lem["F(u)F(u-bar) = separated + linked"] &= sep + linked == F[u] * F[comp(u)]
                lem["separated <= split products"] &= sep <= split_sum(F, u)
                if R in parity:
                    lem["parity gadgets with linked pairs"] += linked > 0
                if windable(R):
                    t4["windable gadget-axis cases"] += 1
                    t4["F(u)F(u-bar) <= s_u"] += F[u] * F[comp(u)] <= split_sum(F, u)
                # control (ii): exchanging only terminal 1's own edge
                if not partial_fails and R == frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)}):
                    for s in by[u]:
                        for t in by[comp(u)]:
                            if s[("T", 0)] != t[("T", 0)]:
                                s2 = dict(s)
                                s2[("T", 0)] = t[("T", 0)]
                                if not all(local(a, s2, v) in R for v in range(n)):
                                    partial_fails = True
                                    break
                        if partial_fails:
                            break
            if R in parity:
                t5["parity gadgets"] += 1
                pos = {F[x] for x in CUBE if F[x] > 0}
                t5["constant on support, hub ratio <= 1 on every axis"] += len(pos) <= 1 and all(hub_ratio(F, u) <= 1 for u in AXES)
            if R in (nolone1, nolone0):
                t5["no-lone gadgets"] += 1
                f = {}
                sym = True
                for x in CUBE:
                    w = sum(x)
                    sym &= f.setdefault(w, F[x]) == F[x]
                rec = (f[2] == f[0] + f[1] and f[3] == f[1] + f[2]) if R == nolone1 else (f[1] == f[2] + f[3] and f[0] == f[1] + f[2])
                t5["recurrence holds"] += sym and rec
                t5["hub ratio <= 1 on every axis"] += all(hub_ratio(F, u) <= 1 for u in AXES)

    # Proposition 6
    nonwind = [R for R in K if len(excluded(R)) == 3]
    def closed_nbhd_plus_antipode(c):
        return frozenset([c, comp(c)] + [xor(c, unit(i)) for i in range(3)])
    centers = {R: [c for c in CUBE if closed_nbhd_plus_antipode(c) == R] for R in nonwind}
    six = [R for R in nonwind if R not in (nolone1, nolone0)]
    p6 = {"non-windable knots": len(nonwind),
          "each is N[c] + {c-bar} for exactly one c": all(len(cs) == 1 for cs in centers.values()),
          "the six open knots have non-constant c, the no-lone knots constant c":
              all(centers[R][0] not in ((0, 0, 0), (1, 1, 1)) for R in six) and
              {centers[nolone1][0], centers[nolone0][0]} == {(1, 1, 1), (0, 0, 0)},
          "only allowed antipodal pair is {c, c-bar}": all({frozenset((x, comp(x))) for x in R if comp(x) in R} ==
                                                         {frozenset((centers[R][0], comp(centers[R][0])))} for R in nonwind),
          "every one-slot exchange at {c, c-bar} fails": all(not (xor(centers[R][0], unit(i)) in R and xor(comp(centers[R][0]), unit(i)) in R)
                                                            for R in nonwind for i in range(3)),
          "in the six, every allowed pair at distance two has an excluded intermediate":
              all(any(xor(s, unit(i)) not in R for i in range(3) if s[i] != t[i])
                  for R in six for s in R for t in R if sum(p != q for p, q in zip(s, t)) == 2),
          "knots allowing an antipodal pair": sum(any(comp(x) in R for x in R) for R in K)}

    # controls
    eq_wire = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)})   # the open knot; slot z pinned to 1 gives equality
    hubF = {x: sum(all((x[k], h, 1) in eq_wire for k in range(3)) for h in (0, 1)) for x in CUBE}
    Zh = [x for x in CUBE if hubF[x] == 0]
    S = eq_wire
    controls = {"a hub (one variable in three knots) gives the equality on three legs, and its support is rejected":
                    sorted(x for x in CUBE if hubF[x] > 0) == [(0, 0, 0), (1, 1, 1)] and not all(not adjacent(s, t) for s in Zh for t in Zh),
                "exchanging only terminal 1's own edge gives an invalid configuration on some pair": partial_fails,
                "the open knot violates the split inequality on the axis 110":
                    int((1, 1, 0) in S) * int((0, 0, 1) in S) > split_sum({x: int(x in S) for x in CUBE}, (1, 1, 0))}

    ok = (t1["largest excluded set of a co-independent relation on three bits"] == 4 and t1["gadgets"] > 0
          and t1["supports co-independent"] == t1["supports excluding at most four"] == t1["gadgets"] and t1["equality supports"] == 0
          and lem["exchange valid and injective, terminals on split patterns"] and lem["F(u)F(u-bar) = separated + linked"]
          and lem["separated <= split products"] and lem["every linked pair branches at antipodal local tuples"]
          and lem["linked pairs"] > 0 and lem["parity gadgets with linked pairs"] == 0
          and t4["F(u)F(u-bar) <= s_u"] == t4["windable gadget-axis cases"] > 0
          and t5["constant on support, hub ratio <= 1 on every axis"] == t5["parity gadgets"] > 0
          and t5["recurrence holds"] == t5["hub ratio <= 1 on every axis"] == t5["no-lone gadgets"] > 0
          and p6["non-windable knots"] == 8 and all(v is True for k, v in p6.items() if isinstance(v, bool))
          and p6["knots allowing an antipodal pair"] == 32 and all(controls.values()))
    result["checks"] = {"Theorem 1": t1, "Lemmas 2 and 3": lem, "Theorem 4 (consistency)": t4, "Theorem 5": t5, "Proposition 6": p6}
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
