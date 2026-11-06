#!/usr/bin/env python3
"""Check the directed-cone theorem on small tori. Standard library only.

A torus is Z^2 modulo the periods w1 = (Lh, 0) and w2 = (s, Lv); classes are written in period coefficients (a, b).
For sampled orientations (uniform, and twisted by p on the double cover) the check computes, independently:
- (i) whether some primal directed closed walk W has det([W], d) < 0, by Bellman-Ford negative-cycle detection with
  arc weights det(arc vector, d);
- (ii) whether some dual directed closed walk has class exactly d, by breadth-first search over (dual vertex, period
  offset) states inside a box of the universal cover;
for every primitive d of the relevant lattice with |d| <= 2, and asserts that exactly one holds (Theorem 1). It then
asserts that the primal classes found are the primitive periods of a convex cone and the dual classes those of its
polar (Theorem 2), that twisted class sets are symmetric under negation (Theorem 3), and two law-level identities on
square tori by sampling (Theorem 4). Controls must be rejected.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOX = 4


class Torus:
    def __init__(self, Lh, Lv, s, p=(0, 0)):
        self.Lh, self.Lv, self.s, self.V = Lh, Lv, s, Lh * Lv
        self.p = p
        self.area = Lh * Lv
        self.edges = []   # (u, w, step, offset, other face, offset of other face's corner)
        for u in range(self.V):
            x, y = u % Lh, u // Lh
            for step in ((1, 0), (0, 1)):
                w, off = self.reduce(x + step[0], y + step[1])
                fo, offo = self.reduce(x, y - 1) if step == (1, 0) else self.reduce(x - 1, y)
                self.edges.append((u, w, step, off, fo, offo))

    def reduce(self, X, Y):
        q = Y // self.Lv
        X1, Y1 = X - q * self.s, Y - q * self.Lv
        r = X1 // self.Lh
        return Y1 * self.Lh + (X1 - r * self.Lh), (r, q)

    def geom(self, k):
        return (k[0] * self.Lh + k[1] * self.s, k[1] * self.Lv)

    def par(self, k):
        return (k[0] * self.p[0] + k[1] * self.p[1]) % 2


def neg(k):
    return (-k[0], -k[1])


def det(u, v):
    return u[0] * v[1] - u[1] * v[0]


def arcs_untwisted(T, bits):
    """Primal and dual arcs as (source, target, period offset, unit vector)."""
    prim, dual = [], []
    for e, (u, w, step, off, fo, offo) in enumerate(T.edges):
        fwd = bits[e]
        if fwd:
            prim.append((u, w, off, step))
        else:
            prim.append((w, u, neg(off), neg(step)))
        if step == (1, 0):
            dual.append((fo, u, neg(offo), (0, 1)) if fwd else (u, fo, offo, (0, -1)))
        else:
            dual.append((u, fo, offo, (-1, 0)) if fwd else (fo, u, neg(offo), (1, 0)))
    return T.V, prim, dual


def arcs_twisted(T, bits):
    """Double cover for the twist p: node 2v + sheet; the lift from (u, s) goes to (w, s ^ p(off)) and points along +step
    exactly when bit ^ s = 1; dual arcs are the rotations, between lifted faces 2f + sheet."""
    prim, dual = [], []
    for e, (u, w, step, off, fo, offo) in enumerate(T.edges):
        t, to = T.par(off), T.par(offo)
        for s in (0, 1):
            fwd = (bits[e] ^ s) == 1
            a, b = 2 * u + s, 2 * w + (s ^ t)
            prim.append((a, b, off, step) if fwd else (b, a, neg(off), neg(step)))
            own, other = 2 * u + s, 2 * fo + (s ^ to)
            if step == (1, 0):
                dual.append((other, own, neg(offo), (0, 1)) if fwd else (own, other, offo, (0, -1)))
            else:
                dual.append((own, other, offo, (-1, 0)) if fwd else (other, own, neg(offo), (1, 0)))
    return 2 * T.V, prim, dual


def realized(n, arcs, box=BOX):
    """Classes k (period coefficients, |k| <= box) of directed closed walks whose lift stays inside the box."""
    out = [[] for _ in range(n)]
    for (a, b, off, _v) in arcs:
        out[a].append((b, off))
    found = set()
    for start in range(n):
        seen = {(start, 0, 0)}
        stack = [(start, 0, 0)]
        while stack:
            v, ka, kb = stack.pop()
            for (w, off) in out[v]:
                na, nb = ka + off[0], kb + off[1]
                if abs(na) > box or abs(nb) > box:
                    continue
                st = (w, na, nb)
                if st not in seen:
                    seen.add(st)
                    stack.append(st)
                    if w == start and (na, nb) != (0, 0):
                        found.add((na, nb))
    return found


def negative_walk(T, n, arcs, d):
    """Bellman-Ford: is there a directed closed walk W with det([W], d) < 0?"""
    dg = T.geom(d)
    wts = [(a, b, det(vec, dg)) for (a, b, _off, vec) in arcs]
    dist = [0] * n
    for _ in range(n):
        changed = False
        for a, b, w in wts:
            if dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                changed = True
        if not changed:
            return False
    return any(dist[a] + w < dist[b] for a, b, w in wts)


def primitive_set(lattice_ok, bound=2):
    pts = [(a, b) for a in range(-bound, bound + 1) for b in range(-bound, bound + 1) if (a, b) != (0, 0) and lattice_ok((a, b))]
    def prim(k):
        g = math.gcd(abs(k[0]), abs(k[1]))
        for m in range(2, g + 1):
            if g % m == 0 and lattice_ok((k[0] // m, k[1] // m)):
                return False
        return True
    return [k for k in pts if prim(k)]


def in_cone(k, gens):
    """Is k a nonnegative combination of the generators (2D, at most two generators)?"""
    if not gens:
        return False
    for g in gens:
        if det(g, k) == 0 and g[0] * k[0] + g[1] * k[1] > 0:
            return True
    for g in gens:
        for h in gens:
            D = det(g, h)
            if D == 0:
                continue
            al, be = det(k, h) / D, det(g, k) / D
            if al >= -1e-12 and be >= -1e-12:
                return True
    return False


def check_family(T, twisted, n_samples, seed, bound=2):
    rng = random.Random(seed)
    lattice_ok = (lambda k: T.par(k) == 0) if twisted else (lambda k: True)
    dirs = primitive_set(lattice_ok, bound)
    stats = {"samples": n_samples, "directions": len(dirs), "lemma_violations": 0, "cone_violations": 0,
             "polar_violations": 0, "symmetry_violations": 0, "cone_types": {}}
    for _ in range(n_samples):
        bits = [rng.getrandbits(1) for _ in T.edges]
        n, prim, dual = (arcs_twisted if twisted else arcs_untwisted)(T, bits)
        S = realized(n, prim)
        Sd = realized(n, dual)
        Sp = {k for k in S if k in dirs}
        Sdp = {k for k in Sd if k in dirs}
        for d in dirs:
            if negative_walk(T, n, prim, d) == (d in Sd):
                stats["lemma_violations"] += 1
        gens = sorted(S)
        for d in dirs:
            if (d in Sp) != in_cone(d, gens):
                stats["cone_violations"] += 1
            if (d in Sdp) != all(det(c, d) >= 0 for c in gens):
                stats["polar_violations"] += 1
        if twisted:
            # a walk of class k with partial offsets inside the box reverses (after the swap) into a walk of class -k whose
            # partial offsets lie within box + |k|; so test |k| <= 2 found in box 4 against box 6
            S6 = realized(n, prim, box=BOX + 2)
            if any(neg(k) not in S6 for k in S if max(abs(k[0]), abs(k[1])) <= 2):
                stats["symmetry_violations"] += 1
        kind = cone_kind(Sp)
        stats["cone_types"][kind] = stats["cone_types"].get(kind, 0) + 1
    return stats


def cone_kind(P):
    if not P:
        return "zero"
    vs = list(P)
    if all(det(vs[0], v) == 0 for v in vs):
        same = all(vs[0][0] * v[0] + vs[0][1] * v[1] > 0 for v in vs)
        return "ray" if same else "line"
    if all(neg(v) in P for v in vs):
        return "plane"
    if any(neg(v) in P for v in vs):
        return "half-plane"
    return "sector"


def law_identities(L, n, seed):
    """On the L x L torus: P(no horizontal winding) = P(pure vertical cycles both ways) and
    P(positive horizontal winding) + P(pure (1,0) cycle) = 1, by sampling both sides on independent orientations."""
    T = Torus(L, L, 0)
    rng = random.Random(seed)
    noH = bothV = posH = pure10 = 0
    for _ in range(n):
        nn, prim, _d = arcs_untwisted(T, [rng.getrandbits(1) for _ in T.edges])
        S = realized(nn, prim)
        noH += not any(k[0] != 0 for k in S)
        posH += any(k[0] > 0 for k in S)
        nn, prim, _d = arcs_untwisted(T, [rng.getrandbits(1) for _ in T.edges])
        S = realized(nn, prim)
        bothV += (0, 1) in S and (0, -1) in S
        pure10 += (1, 0) in S
    return {"samples": n, "P_no_horizontal": noH / n, "P_pure_vertical_both": bothV / n,
            "P_positive_horizontal": posH / n, "P_pure_10": pure10 / n}


def run() -> dict:
    checks, controls, failures = {}, {}, []
    fams = [((3, 3, 0), (0, 0), 3000), ((3, 4, 0), (0, 0), 800), ((4, 4, 0), (0, 0), 800), ((3, 3, 1), (0, 0), 800),
            ((3, 3, 0), (1, 0), 600), ((3, 3, 0), (1, 1), 600), ((4, 3, 0), (1, 0), 400), ((3, 3, 1), (1, 1), 400)]
    for (Lh, Lv, s), p, n in fams:
        T = Torus(Lh, Lv, s, p)
        st = check_family(T, p != (0, 0), n, Lh * 1000 + Lv * 100 + s * 10 + 2 * p[0] + p[1])
        key = f"{Lh}x{Lv} s={s} twist={p}"
        checks[key] = st
        for name in ("lemma_violations", "cone_violations", "polar_violations", "symmetry_violations"):
            if st[name]:
                failures.append(f"{key}: {name} {st[name]}")
        if p != (0, 0) and any(k in st["cone_types"] for k in ("ray", "half-plane", "sector")):
            failures.append(f"{key}: twisted cone of a forbidden type")
        ct = st["cone_types"]
        for a, b in (("zero", "plane"), ("ray", "half-plane")):
            x, y = ct.get(a, 0), ct.get(b, 0)
            if abs(x - y) > 4 * math.sqrt(max(x + y, 1)):
                failures.append(f"{key}: polar invariance {a} {x} vs {b} {y}")
    law = law_identities(5, 3000, 5)
    checks["law_identities_5x5"] = {k: round(v, 4) if isinstance(v, float) else v for k, v in law.items()}
    se = math.sqrt(0.25 / law["samples"])
    if abs(law["P_no_horizontal"] - law["P_pure_vertical_both"]) > 5 * math.sqrt(2) * se:
        failures.append("law identity 1 fails")
    if abs(law["P_positive_horizontal"] + law["P_pure_10"] - 1) > 5 * math.sqrt(2) * se:
        failures.append("law identity 2 fails")
    # controls
    T = Torus(3, 3, 0)
    rng = random.Random(3)
    wrong = 0
    for _ in range(300):
        n, prim, dual = arcs_untwisted(T, [rng.getrandbits(1) for _ in T.edges])
        Sd = realized(n, dual)
        for d in primitive_set(lambda k: True):
            # control: the opposite sign convention (det(d, [W]) < 0) must break the lemma somewhere
            dg = T.geom(d)
            flipped = negative_walk(T, n, [(a, b, off, (-v[0], -v[1])) for (a, b, off, v) in prim], d)
            wrong += flipped == (d in Sd)
    controls["opposite_sign_rejected"] = wrong > 0
    rng = random.Random(4)
    asym = 0
    for _ in range(200):
        n, prim, _dual = arcs_untwisted(T, [rng.getrandbits(1) for _ in T.edges])
        S = realized(n, prim)
        asym += any(neg(k) not in S for k in S)
    controls["untwisted_symmetry_rejected"] = asym > 0
    failures += [f"control {k}" for k, ok in controls.items() if not ok]
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"], "controls": outcome["controls"], "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: directed-cone theorem checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
