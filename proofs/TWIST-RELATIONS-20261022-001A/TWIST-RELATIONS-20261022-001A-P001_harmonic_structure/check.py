#!/usr/bin/env python3
"""Check of TWIST-RELATIONS-20261022-001A-P001: the harmonic structure of the twist sectors.

Standard library only. Square-lattice tori have periods w1 = (Lh, 0) and w2 = (s, Lv); a twist (a, b) takes the values a on w1
and b on w2, and the twisted model is the swap-reversed orientation of the double cover. For each sector the check records the
kind (contractible, cross, winding), the winding class and whether a cluster is odd under the twist.
- Basis covariance, pathwise on sampled orientations: the torus with shear s + Lh is the same torus, and its sector (a, b) is the
  sector (a, a + b) of shear s, with classes mapped by (x, y) -> (x + y, y); the mirror x -> -x maps shear s to -s, reverses the
  horizontal arrows, keeps every sector and maps classes by (x, y) -> (-x, y).
- The half-shear identity, pathwise: when 2s = Lh, mirroring exchanges the sectors (1, 0) and (1, 1).
- Exhaustive 3 x 3 counts at shears 0 and 1: contractible and cross counts agree and consistency = 1 - contractible - odd winding
  in every twisted sector, exactly; hence the consistency relation is equivalent to D = odd10 + odd01 - odd11. The large-size
  relations (D = 0, a shear-independent E, O(1) = O(0) cos(pi/3), the consistency relation) all fail at this size.
- Controls: shearing without relabeling and mirroring without reversing horizontal arrows must give mismatches.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTORS = ((0, 0), (1, 0), (0, 1), (1, 1))


class Torus:
    """Edges (u, w, (a, b)): stepping from a lift of u along the edge reaches the lift of w shifted by a w1 + b w2."""

    def __init__(self, Lh, Lv, s):
        self.Lh, self.Lv, self.s, self.V = Lh, Lv, s, Lh * Lv
        self.edges = []
        for u in range(self.V):
            x, y = u % Lh, u // Lh
            self.edges.append((u, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
            if y + 1 < Lv:
                self.edges.append((u, u + Lh, (0, 0)))
            else:
                X = x - s
                a = X // Lh
                self.edges.append((u, X - a * Lh, (a, 1)))


def normalize(c):
    a, b = c
    return (a, b) if a > 0 or (a == 0 and b > 0) else (-a, -b)


def classify(T, o, p):
    """(kind, class, odd): kind 0 contractible, 1 cross, 2 winding; odd when some cluster has a cycle odd under p."""
    pa, pb = p
    tw = bool(pa or pb)
    n = 2 * T.V if tw else T.V
    adj = [0] * n
    par = []
    for (u, w, (a, b)), bit in zip(T.edges, o):
        t = (a * pa + b * pb) & 1
        par.append(t)
        if not tw:
            if bit:
                adj[u] |= 1 << w
            else:
                adj[w] |= 1 << u
        elif bit:
            adj[2 * u] |= 1 << (2 * w + t)
            adj[2 * w + (1 ^ t)] |= 1 << (2 * u + 1)
        else:
            adj[2 * w + t] |= 1 << (2 * u)
            adj[2 * u + 1] |= 1 << (2 * w + (1 ^ t))
    reach = [adj[i] | (1 << i) for i in range(n)]
    for k in range(n):
        bk, rk = 1 << k, reach[k]
        for i in range(n):
            if reach[i] & bk:
                reach[i] |= rk
    parent, pot, gens = list(range(T.V)), [(0, 0)] * T.V, [[] for _ in range(T.V)]

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        acc = (0, 0)
        for node in reversed(path):
            q = pot[node]
            acc = (acc[0] + q[0], acc[1] + q[1])
            pot[node], parent[node] = acc, x
        return x

    for (u, w, off), t in zip(T.edges, par):
        i, j = (2 * u, 2 * w + t) if tw else (u, w)
        if not ((reach[i] >> j) & 1 and (reach[j] >> i) & 1):
            continue
        ru, rw = find(u), find(w)
        pu, pw = (pot[u] if u != ru else (0, 0)), (pot[w] if w != rw else (0, 0))
        d = (pu[0] + off[0] - pw[0], pu[1] + off[1] - pw[1])
        if ru == rw:
            if d != (0, 0):
                gens[ru].append(d)
        else:
            parent[rw], pot[rw] = ru, d
            gens[ru] += gens[rw]
    kind, cls, odd = 0, None, False
    for r in range(T.V):
        g = gens[r]
        if parent[r] != r or not g:
            continue
        odd |= any((x * pa + y * pb) & 1 for x, y in g)
        if any(g[0][0] * y - g[0][1] * x for x, y in g[1:]) or any(g[i][0] * g[j][1] - g[i][1] * g[j][0]
                                                                   for i in range(len(g)) for j in range(i + 1, len(g))):
            kind = 1
        elif kind != 1:
            x, y = g[0]
            m = gcd(abs(x), abs(y))
            c = normalize((x // m, y // m))
            assert cls in (None, c), "parallel winding clusters must share their class"
            kind, cls = 2, c
    return kind, (cls if kind == 2 else None), odd


def mirror_image(T, o, p, reverse=True):
    """The mirror x -> -x maps the torus of shear s onto the torus of shear -s, vertex (x, y) to (-x, y). It swaps the ends of
    every horizontal edge. In the double cover a lift's sheet is read at its lattice tail, so a horizontal arrow keeps its bit when
    the edge crosses the seam (twist parity 1) and reverses otherwise; vertical arrows keep their bits. Returns the image bits on
    the mirrored torus and the image edges' twist parities (the seam is moved later by gauge)."""
    Lh, bits, t_img = T.Lh, [0] * len(o), [0] * len(o)
    pa, pb = p
    for v in range(T.V):
        x, y = v % Lh, v // Lh
        for d, img in ((0, 2 * (y * Lh + (-x - 1) % Lh)), (1, 2 * (y * Lh + (-x) % Lh) + 1)):
            e = 2 * v + d
            a, b = T.edges[e][2]
            t = (a * pa + b * pb) & 1
            flip = (d == 0 and t == 0) if reverse else False
            bits[img], t_img[img] = o[e] ^ flip, t
    return bits, t_img


def gauge(T, bits, t_have, p):
    """Move the seam of an image configuration onto T's own seam for the twist p. Flipping the sheets of a vertex set R is an
    isomorphism of the swap-reversed double cover; it flips the twist parity of the edges leaving R and reverses the edges whose
    lattice tail lies in R. R is found by solving r(u) + r(w) = t_have + t_want on every edge."""
    pa, pb = p
    t_want = [(a * pa + b * pb) & 1 for _u, _w, (a, b) in T.edges]
    nbr = [[] for _ in range(T.V)]
    for (u, w, _o), th, tw in zip(T.edges, t_have, t_want):
        nbr[u].append((w, th ^ tw))
        nbr[w].append((u, th ^ tw))
    r, stack = [None] * T.V, [0]
    r[0] = 0
    while stack:
        u = stack.pop()
        for w, d in nbr[u]:
            if r[w] is None:
                r[w] = r[u] ^ d
                stack.append(w)
            assert r[w] == r[u] ^ d, "the two seams are not in the same class"
    return [b ^ r[u] for b, (u, _w, _o) in zip(bits, T.edges)]


def covariance(Lh, Lv, s, samples, rng):
    A, B, C = Torus(Lh, Lv, s), Torus(Lh, Lv, s + Lh), Torus(Lh, Lv, -s)
    assert [(u, w) for u, w, _ in A.edges] == [(u, w) for u, w, _ in B.edges]
    bad = {"relabel": 0, "mirror": 0, "half_shear": 0}
    control = {"unrelabeled": 0, "unreversed_mirror": 0}
    for _ in range(samples):
        o = [rng.getrandbits(1) for _ in A.edges]
        ra = {p: classify(A, o, p) for p in SECTORS}
        for (a, b) in SECTORS:
            kb, cb, ob = classify(B, o, (a, b))
            ka, ca, oa = ra[(a, (a + b) & 1)]
            mapped = normalize((cb[0] + cb[1], cb[1])) if cb else None
            bad["relabel"] += (ka, ca, oa) != (kb, mapped, ob)
            control["unrelabeled"] += (kb, ob) != (ra[(a, b)][0], ra[(a, b)][2])
            img, t_img = mirror_image(A, o, (a, b))
            kc, cc, occ = classify(C, gauge(C, img, t_img, (a, b)), (a, b))
            ka, ca, oa = ra[(a, b)]
            mapped = normalize((-ca[0], ca[1])) if ca else None
            bad["mirror"] += (ka, mapped, oa) != (kc, cc, occ)
            img_u, _t = mirror_image(A, o, (a, b), reverse=False)
            control["unreversed_mirror"] += classify(C, gauge(C, img_u, t_img, (a, b)), (a, b))[0] != ka
        if 2 * s == Lh:
            img, t_img = mirror_image(A, o, (1, 0))
            bad["half_shear"] += ra[(1, 0)][0] != classify(A, gauge(C, img, t_img, (1, 0)), (1, 1))[0]
    return bad, control


def exhaustive(Lh, Lv, s):
    T = Torus(Lh, Lv, s)
    m = len(T.edges)
    cnt = {p: {"contr": 0, "cross": 0, "odd_winding": 0, "cons": 0, "lines": {}} for p in SECTORS}
    for mask in range(1 << m):
        o = [(mask >> e) & 1 for e in range(m)]
        for p in SECTORS:
            k, _c, odd = classify(T, o, p)
            c = cnt[p]
            c["contr"] += k == 0
            c["cross"] += k == 1
            c["odd_winding"] += k == 2 and odd
            if k == 2 and odd:
                c["lines"][_c] = c["lines"].get(_c, 0) + 1
            c["cons"] += not odd
    return cnt, 1 << m


def run() -> dict[str, object]:
    rng = random.Random("twist-relations-A")
    checks, controls, failures = {}, {}, []
    cov = {}
    for (Lh, Lv, s, k) in ((4, 3, 1, 300), (4, 4, 2, 300), (5, 4, 2, 200), (6, 4, 3, 150), (6, 5, 1, 100), (5, 5, -2, 100)):
        bad, ctl = covariance(Lh, Lv, s, k, rng)
        cov[f"{Lh}x{Lv} s={s}"] = {"samples": k, "mismatches": bad, "control_mismatches": ctl}
        if any(bad.values()):
            failures.append(f"covariance {Lh}x{Lv} s={s}: {bad}")
        controls[f"{Lh}x{Lv} s={s}"] = ctl
    checks["covariance"] = cov
    ex = {}
    for s in (0, 1):
        cnt, N = exhaustive(3, 3, s)
        P = {p: Fraction(cnt[p]["contr"], N) for p in SECTORS}
        odd = {p: Fraction(cnt[p]["odd_winding"], N) for p in SECTORS}
        cons = {p: Fraction(cnt[p]["cons"], N) for p in SECTORS}
        dual_ok = all(cnt[p]["contr"] == cnt[p]["cross"] for p in SECTORS[1:])
        cons_ok = all(cons[p] == 1 - P[p] - odd[p] for p in SECTORS[1:]) and cons[(0, 0)] == 1
        D = P[(0, 0)] - P[(1, 0)] - P[(0, 1)] + P[(1, 1)]
        R3 = 1 - cons[(1, 0)] - cons[(0, 1)] + cons[(1, 1)]
        equiv_ok = R3 - P[(0, 0)] == -D + odd[(1, 0)] + odd[(0, 1)] - odd[(1, 1)]
        ex[f"3x3 s={s}"] = {"orientations": N, "P_contractible": {f"{a}{b}": str(P[(a, b)]) for a, b in SECTORS},
                            "P_odd_winding": {f"{a}{b}": str(odd[(a, b)]) for a, b in SECTORS}, "D": str(D),
                            "E": str(P[(0, 0)] - P[(0, 1)]), "O": str(P[(1, 0)] - P[(1, 1)]),
                            "consistency_relation_lhs": str(R3), "duality_exact": dual_ok, "consistency_identity_exact": cons_ok,
                            "equivalence_exact": equiv_ok,
                            "odd_lines": {f"{a}{b}": {f"{x},{y}": v for (x, y), v in sorted(cnt[(a, b)]["lines"].items())} for a, b in SECTORS}}
        lines = {p: cnt[p]["lines"] for p in SECTORS}
        same = all(lines[p].get(cl, 0) == lines[q].get(cl, 0)
                   for cl in set().union(*lines.values())
                   for p in SECTORS[1:] for q in SECTORS[1:] if p < q and (cl[0] * p[0] + cl[1] * p[1]) & 1 and (cl[0] * q[0] + cl[1] * q[1]) & 1)
        ex[f"3x3 s={s}"]["odd_line_identity_exact"] = same
        if not same:
            failures.append(f"odd-line identity fails on 3x3 s={s}")
        if not (dual_ok and cons_ok and equiv_ok):
            failures.append(f"exact identities fail on 3x3 s={s}")
    e0, e1 = Fraction(ex["3x3 s=0"]["E"]), Fraction(ex["3x3 s=1"]["E"])
    o0, o1 = Fraction(ex["3x3 s=0"]["O"]), Fraction(ex["3x3 s=1"]["O"])
    finite = {"additivity_fails": Fraction(ex["3x3 s=0"]["D"]) != 0, "E_depends_on_shear": e0 != e1,
              "O_not_first_harmonic": o1 != o0 / 2,
              "consistency_relation_fails": Fraction(ex["3x3 s=0"]["consistency_relation_lhs"]) != Fraction(ex["3x3 s=0"]["P_contractible"]["00"])}
    ex["finite_size"] = finite
    l0, l1 = ex["3x3 s=0"]["odd_lines"]["10"].get("1,0"), ex["3x3 s=1"]["odd_lines"]["10"].get("1,0")
    ex["odd_line_shear_independent_3x3"] = l0 == l1
    if l0 != l1:
        failures.append("the odd horizontal line of the twist (1, 0) depends on the shear on 3x3")
    if not all(finite.values()):
        failures.append(f"a large-size relation holds exactly on 3x3: {finite}")
    checks["exhaustive"] = ex
    if not all(c["unrelabeled"] > 0 and c["unreversed_mirror"] > 0 for c in controls.values()):
        failures.append("a control was not rejected")
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
    print(f"{result['status']}: harmonic structure of the twist sectors checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
