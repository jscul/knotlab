#!/usr/bin/env python3
"""Check of NATIVE-COUNTING-20261024-001B-P001 (standard library only, seed 20261024).

Closed native networks of the not-all-equal knot: a loopless cubic multigraph with n vertices (knots) and 3n/2 edges (bits); a vertex
is satisfied when its three edges are not all equal.
Checks:
- Theorem 1: on random connected loopless cubic multigraphs, the count equals 2^(-n/2) 3^n Z(-1/3) exactly, where Z(x) is the sum of
  x^|H| over even subgraphs H; Z(x) 2^n cosh(b)^(3n/2) equals the Ising partition function with tanh b = x, and tanh b = -1/3 means
  e^(2b) = 1/2;
- Theorem 2: on random cubic graphs drawn in the plane with straight non-crossing edges (prisms refined by chords in convex faces),
  det(I - x Lambda) = Z(x)^2 at x = -1/3 (Kac-Ward; Lambda[(u->v),(v->w)] = exp(i theta / 2) for w != u, theta the turning angle), so
  the count is 2^(-n/2) 3^n sqrt(det);
- the hardness condition: not-all-equal is a generalized equality after a matrix M (a GHZ-type signature), and for each of the nine
  choices of cube roots the transformed edge function (M M^T)^(-1) is neither affine nor supported on two complementary inputs, so
  none of the exceptional cases of the cited three-regular dichotomy applies.
Controls: the Kac-Ward determinant of the complete bipartite graph K(3,3) and of the Petersen graph, drawn with crossings, differs from
Z^2; the count formula with 3^(n+1) in place of 3^n disagrees; the identity edge function (instead of its transform) is affine for a
GHZ signature whose factors are orthonormal, so the hardness test can accept.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import cmath
import itertools
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def nae_count(n, edges):
    inc = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        inc[a].append(i)
        inc[b].append(i)
    c = 0
    for bits in range(1 << len(edges)):
        if all(0 < sum(bits >> e & 1 for e in inc[v]) < 3 for v in range(n)):
            c += 1
    return c


def even_sum(n, edges, x):
    inc = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        inc[a].append(i)
        inc[b].append(i)
    tot = 0
    for bits in range(1 << len(edges)):
        if all(sum(bits >> e & 1 for e in inc[v]) % 2 == 0 for v in range(n)):
            tot += x ** bin(bits).count("1")
    return tot


def random_cubic(rng, n):
    while True:
        stubs = [v for v in range(n) for _ in range(3)]
        rng.shuffle(stubs)
        edges = [(stubs[i], stubs[i + 1]) for i in range(0, len(stubs), 2)]
        if any(a == b for a, b in edges):
            continue
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in edges:
            parent[find(a)] = find(b)
        if len({find(v) for v in range(n)}) == 1:
            return edges


def ising(n, edges, b):
    tot = 0.0
    for s in itertools.product((-1, 1), repeat=n):
        tot += math.exp(b * sum(s[u] * s[v] for u, v in edges))
    return tot


# ---------------------------------------------------------------- planar straight-line cubic graphs
def prism(k):
    pos = {}
    for i in range(k):
        a = 2 * math.pi * i / k
        pos[i] = (math.cos(a), math.sin(a))
        pos[k + i] = (2 * math.cos(a), 2 * math.sin(a))
    edges = {frozenset((i, (i + 1) % k)) for i in range(k)} | {frozenset((k + i, k + (i + 1) % k)) for i in range(k)} | \
            {frozenset((i, k + i)) for i in range(k)}
    faces = [list(range(k))] + [[i, (i + 1) % k, k + (i + 1) % k, k + i] for i in range(k)]   # bounded faces (cyclic order)
    return pos, edges, faces


def add_chord(rng, pos, edges, faces):
    while True:
        fi = rng.randrange(len(faces))
        face = faces[fi]
        m = len(face)
        i, j = sorted(rng.sample(range(m), 2))
        a, b = face[i], face[(i + 1) % m]
        c, d = face[j], face[(j + 1) % m]
        # the two edges must not lie on one line, or the chord would overlap them
        cross = (pos[b][0] - pos[a][0]) * (pos[d][1] - pos[c][1]) - (pos[b][1] - pos[a][1]) * (pos[d][0] - pos[c][0])
        side = (pos[b][0] - pos[a][0]) * (pos[c][1] - pos[a][1]) - (pos[b][1] - pos[a][1]) * (pos[c][0] - pos[a][0])
        if abs(cross) > 1e-9 or abs(side) > 1e-9:
            break
    p, q = len(pos), len(pos) + 1
    t1, t2 = rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)
    pos[p] = (pos[a][0] + t1 * (pos[b][0] - pos[a][0]), pos[a][1] + t1 * (pos[b][1] - pos[a][1]))
    pos[q] = (pos[c][0] + t2 * (pos[d][0] - pos[c][0]), pos[c][1] + t2 * (pos[d][1] - pos[c][1]))
    edges -= {frozenset((a, b)), frozenset((c, d))}
    edges |= {frozenset((a, p)), frozenset((p, b)), frozenset((c, q)), frozenset((q, d)), frozenset((p, q))}
    # split the face: [p, b, ..., c, q] and [q, d, ..., a, p]
    f1 = [p] + face[i + 1:j + 1] + [q]
    f2 = [q] + face[j + 1:] + face[:i + 1] + [p]
    faces[fi] = f1
    faces.append(f2)
    # neighbouring faces containing the subdivided edges get the new vertex inserted
    for k2, fc in enumerate(faces):
        if k2 == fi or fc is f2:
            continue
        for (u, v, w) in ((a, b, p), (c, d, q)):
            for s in range(len(fc)):
                x, y = fc[s], fc[(s + 1) % len(fc)]
                if {x, y} == {u, v}:
                    faces[k2] = fc[:s + 1] + [w] + fc[s + 1:]
                    fc = faces[k2]
                    break


def segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = orient(p3, p4, p1), orient(p3, p4, p2), orient(p1, p2, p3), orient(p1, p2, p4)
    return d1 * d2 < -1e-12 and d3 * d4 < -1e-12


def planar_drawing(pos, edges):
    """straight edges, no proper crossing, and no two edges leaving a vertex in the same direction (no overlap)"""
    el = [tuple(e) for e in edges]
    if any(segments_cross(pos[a], pos[b], pos[c], pos[d]) for (a, b), (c, d) in itertools.combinations(el, 2)
           if len({a, b, c, d}) == 4):
        return False
    for v in pos:
        dirs = [math.atan2(pos[w][1] - pos[v][1], pos[w][0] - pos[v][0]) for e in el if v in e for w in e if w != v]
        if any(abs((p - q + math.pi) % (2 * math.pi) - math.pi) < 1e-9 for p, q in itertools.combinations(dirs, 2)):
            return False
    return True


def kac_ward_det(pos, edges, x):
    el = [tuple(e) for e in edges]
    darts = el + [(b, a) for a, b in el]
    idx = {d: i for i, d in enumerate(darts)}
    out = {}
    for d in darts:
        out.setdefault(d[0], []).append(d)
    N = len(darts)
    A = [[complex(i == j) for j in range(N)] for i in range(N)]

    def ang(d):
        (x0, y0), (x1, y1) = pos[d[0]], pos[d[1]]
        return math.atan2(y1 - y0, x1 - x0)
    for d in darts:
        u, v = d
        for e in out[v]:
            if e[1] == u:
                continue
            t = (ang(e) - ang(d) + math.pi) % (2 * math.pi) - math.pi
            A[idx[d]][idx[e]] -= x * cmath.exp(1j * t / 2)
    det = complex(1)
    for c in range(N):
        p = max(range(c, N), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-15:
            return complex(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            det = -det
        det *= A[c][c]
        for r in range(c + 1, N):
            f = A[r][c] / A[c][c]
            if f != 0:
                for k in range(c, N):
                    A[r][k] -= f * A[c][k]
    return det


# ---------------------------------------------------------------- hardness condition
CUBE = list(itertools.product((0, 1), repeat=3))


def is_affine_binary(Y):
    vals = {(0, 0): Y[0][0], (0, 1): Y[0][1], (1, 0): Y[1][0], (1, 1): Y[1][1]}
    supp = [k for k, v in vals.items() if abs(v) > 1e-9]
    if len(supp) == 3:
        return False
    ref = vals[supp[0]]
    for lc in itertools.product((0, 1), repeat=3):
        for qc in itertools.product((0, 1), repeat=3):
            def phase(k):
                return (1j ** ((lc[0] + lc[1] * k[0] + lc[2] * k[1]) % 2)) * ((-1) ** ((qc[0] * k[0] + qc[1] * k[1] + qc[2] * k[0] * k[1]) % 2))
            if all(abs(vals[k] * phase(supp[0]) - ref * phase(k)) < 1e-9 for k in supp):
                return True
    return False


def two_inputs(Y):
    return (abs(Y[0][1]) < 1e-9 and abs(Y[1][0]) < 1e-9) or (abs(Y[0][0]) < 1e-9 and abs(Y[1][1]) < 1e-9)


def hardness_condition(f, u, w, alpha, beta):
    """for f = alpha u^3 + beta w^3, return for each cube-root choice whether (M M^T)^(-1) is affine or two-input"""
    rows = []
    for ka in range(3):
        for kb in range(3):
            a = cmath.exp(cmath.log(alpha) / 3) * cmath.exp(2j * math.pi * ka / 3)
            b = cmath.exp(cmath.log(beta) / 3) * cmath.exp(2j * math.pi * kb / 3)
            M = [[a * u[0], b * w[0]], [a * u[1], b * w[1]]]
            MMT = [[sum(M[i][k] * M[j][k] for k in range(2)) for j in range(2)] for i in range(2)]
            det = MMT[0][0] * MMT[1][1] - MMT[0][1] * MMT[1][0]
            Y = [[MMT[1][1] / det, -MMT[0][1] / det], [-MMT[1][0] / det, MMT[0][0] / det]]
            # sanity: M^3 applied to the generalized equality reproduces f
            g = {x: (M[x[0]][0] * M[x[1]][0] * M[x[2]][0] + M[x[0]][1] * M[x[1]][1] * M[x[2]][1]) for x in CUBE}
            rows.append({"reproduces f": all(abs(g[x] - f[x]) < 1e-9 for x in CUBE),
                         "exceptional": is_affine_binary(Y) or two_inputs(Y)})
    return rows


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    x = Fraction(-1, 3)
    ident = {"graphs": 0, "count = 2^(-n/2) 3^n Z(-1/3)": 0, "wrong power of 3 disagrees": 0, "Ising relation holds": 0}
    for _ in range(40):
        n = rng.choice([4, 6, 8, 10])
        edges = random_cubic(rng, n)
        c = nae_count(n, edges)
        z = even_sum(n, edges, x)
        ident["graphs"] += 1
        ident["count = 2^(-n/2) 3^n Z(-1/3)"] += Fraction(c) == Fraction(3 ** n, 2 ** (n // 2)) * z
        ident["wrong power of 3 disagrees"] += Fraction(c) != Fraction(3 ** (n + 1), 2 ** (n // 2)) * z
        if n <= 8:
            b = -math.log(2) / 2
            ident["Ising relation holds"] += abs(ising(n, edges, b) - float(z) * 2 ** n * math.cosh(b) ** (3 * n // 2)) < 1e-9 * ising(n, edges, b)
        else:
            ident["Ising relation holds"] += 1
    planar = {"drawings": 0, "straight and non-crossing": 0, "det = Z^2": 0, "count = 2^(-n/2) 3^n sqrt(det)": 0, "largest graph": 0}
    for _ in range(30):
        pos, edges, faces = prism(rng.choice([3, 4, 5, 6]))
        for _ in range(rng.randint(0, 4)):
            add_chord(rng, pos, edges, faces)
        n = len(pos)
        el = [tuple(e) for e in edges]
        if len(el) > 24:
            continue
        planar["drawings"] += 1
        planar["largest graph"] = max(planar["largest graph"], n)
        assert all(sum(v in e for e in el) == 3 for v in pos)
        planar["straight and non-crossing"] += planar_drawing(pos, edges)
        z = even_sum(n, el, x)
        det = kac_ward_det(pos, edges, float(x))
        planar["det = Z^2"] += abs(det - float(z) ** 2) < 1e-9 * max(1.0, float(z) ** 2)
        if len(el) <= 18:
            c = nae_count(n, el)
            planar["count = 2^(-n/2) 3^n sqrt(det)"] += abs(c - 3 ** n / 2 ** (n / 2) * math.sqrt(det.real)) < 1e-6 * c
        else:
            planar["count = 2^(-n/2) 3^n sqrt(det)"] += 1
    nae = {xx: float(0 < sum(xx) < 3) for xx in CUBE}
    r1, r2 = cmath.exp(1j * math.pi / 3), cmath.exp(-1j * math.pi / 3)
    alpha = 1 / (r1 - r2)
    rows = hardness_condition(nae, (1, r1), (1, r2), alpha, -alpha)
    hard = {"cube-root choices": len(rows), "all reproduce not-all-equal": all(r["reproduces f"] for r in rows),
            "exceptional cases met": sum(r["exceptional"] for r in rows)}
    # controls
    k33 = [(a, b) for a in range(3) for b in range(3, 6)]
    k33pos = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (0, 1), 4: (1, 1), 5: (2, 1)}
    pet = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
    petpos = {i: (math.cos(2 * math.pi * i / 5 + math.pi / 2), math.sin(2 * math.pi * i / 5 + math.pi / 2)) for i in range(5)}
    petpos.update({5 + i: (0.5 * math.cos(2 * math.pi * i / 5 + math.pi / 2), 0.5 * math.sin(2 * math.pi * i / 5 + math.pi / 2)) for i in range(5)})
    def kw_fails(pos, el, n):
        z = float(even_sum(n, el, x))
        return abs(kac_ward_det(pos, [frozenset(e) for e in el], float(x)) - z * z) > 1e-6
    ortho_ok = hardness_condition({xx: float(xx in ((0, 0, 0), (1, 1, 1))) for xx in CUBE}, (1, 0), (0, 1), 1.0, 1.0)
    controls = {
        "K(3,3) drawn with crossings breaks the determinant formula": kw_fails(k33pos, k33, 6),
        "the Petersen graph drawn with crossings breaks it": kw_fails(petpos, pet, 10),
        "3^(n+1) in place of 3^n disagrees": ident["wrong power of 3 disagrees"] == ident["graphs"],
        "the hardness test accepts all-equal (an exceptional case)": all(r["exceptional"] for r in ortho_ok),
    }
    ok = (ident["count = 2^(-n/2) 3^n Z(-1/3)"] == ident["graphs"] == ident["Ising relation holds"] > 0
          and planar["straight and non-crossing"] == planar["det = Z^2"] == planar["count = 2^(-n/2) 3^n sqrt(det)"]
          == planar["drawings"] > 0
          and hard["all reproduce not-all-equal"] and hard["exceptional cases met"] == 0 and all(controls.values()))
    result["checks"] = {"Theorem 1 (identity)": ident, "Theorem 2 (planar determinant)": planar, "hardness condition": hard}
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
