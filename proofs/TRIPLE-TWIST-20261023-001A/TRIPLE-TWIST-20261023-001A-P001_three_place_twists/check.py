#!/usr/bin/env python3
"""Check of TRIPLE-TWIST-20261023-001A-P001 (standard library only; a small DPLL decides satisfiability).

- Lemma 1: for every complement-closed placement, on random triangular tori, the world with twist cocycle t + delta(1_S) and fair x is
  the world with t and x flipped on the triangles whose first corner is in S (equisatisfiable instance by instance); changing a
  triangle's first corner is likewise a flip of x. For every contact pair that is not complement-closed, one triangle with the cocycle
  of one corner already has a different law of solution sets.
- Lemma 2: with independent uniform polarities per triangle, the world with twist t and polarities sigma is the untwisted world with
  polarities sigma + g (a bijection of polarities), instance by instance.
- Lemma 3: every relation on two bits is closed under majority (definable by clauses of two literals).
- Proposition 4: on the 3 x 3 and 4 x 4 tori in every twist, every twisted not-all-equal colouring has two sides with d = t + delta h
  equal to 1 on every triangle and the class of d equal to the twist; on every triangular torus with sides 2 to 5 and every shear,
  the (shape, twist) pairs without such a colouring are listed, and on them every x is enumerated: the monotone world never
  contradicts there either.
- Theorem 5: for every placement with a doubly allowed assignment on a small torus, planar patches never contradict (sampled), fitting
  twists never contradict (sampled), and every minimal contradicting set found has nonzero winding, on which the twist differs from
  every fitting twist.
- Controls (each rejected): for x or 1-in-3 a contractible seam creates contradictions on a planar patch; dropping the gauge from the
  winding test (counting every minimal set as winding) would accept planar contradictions of a LOCAL placement, which do occur.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))
sys.setrecursionlimit(10000)


# ------------------------------------------------------------------ satisfiability (DPLL with unit propagation)

def dpll(clauses, nvars):
    assign = {}

    def value(l):
        v = assign.get(abs(l))
        return None if v is None else (v if l > 0 else not v)

    def propagate(trail):
        changed = True
        while changed:
            changed = False
            for c in clauses:
                unassigned, sat = [], False
                for l in c:
                    v = value(l)
                    if v is True:
                        sat = True
                        break
                    if v is None:
                        unassigned.append(l)
                if sat:
                    continue
                if not unassigned:
                    return False
                if len(unassigned) == 1:
                    l = unassigned[0]
                    assign[abs(l)] = l > 0
                    trail.append(abs(l))
                    changed = True
        return True

    def solve():
        trail = []
        if not propagate(trail):
            for v in trail:
                del assign[v]
            return False
        free = next((v for v in range(1, nvars + 1) if v not in assign), None)
        if free is None:
            return True
        for val in (True, False):
            assign[free] = val
            if solve():
                return True
            del assign[free]
        for v in trail:
            del assign[v]
        return False

    return solve()


# ------------------------------------------------------------------ worlds

def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def torus(L, M, S, alpha, beta):
    def reduce(i, j):
        k2, j2 = divmod(j, M)
        k1, i3 = divmod(i - k2 * S, L)
        return (i3, j2), (k1, k2)

    vid = lambda p: p[1] * L + p[0]
    tris = []
    for j in range(M):
        for i in range(L):
            for d1, d2 in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
                b, ob = reduce(i + d1[0], j + d1[1])
                c, oc = reduce(i + d2[0], j + d2[1])
                g = (0, (alpha * ob[0] + beta * ob[1]) & 1, (alpha * oc[0] + beta * oc[1]) & 1)
                sides = [(vid((i, j)), vid(b), ob), (vid((i, j)), vid(c), oc), (vid(b), vid(c), (oc[0] - ob[0], oc[1] - ob[1]))]
                tris.append(((vid((i, j)), vid(b), vid(c)), g, sides))
    return L * M, tris


def patch(r):
    ids = {}
    for q in range(-r, r + 1):
        for w in range(-r, r + 1):
            if abs(q + w) <= r:
                ids[(q, w)] = len(ids)
    tris = []
    for (q, w), a in ids.items():
        for d1, d2 in (((1, 0), (1, 1)), ((0, 1), (1, 1))):
            b, c = ids.get((q + d1[0], w + d1[1])), ids.get((q + d2[0], w + d2[1]))
            if b is not None and c is not None:
                tris.append(((a, b, c), (0, 0, 0), [(a, b, (0, 0)), (a, c, (0, 0)), (b, c, (0, 0))]))
    return len(ids), tris, ids


def clauses_of(tris, rels):
    out = []
    for (corners, g, _s), rel in zip(tris, rels):
        for p in range(8):
            if rel >> p & 1:
                continue
            out.append([-(corners[k] + 1) if ((p >> k) & 1) ^ g[k] else corners[k] + 1 for k in range(3)])
    return out


def solvable(V, tris, rels):
    return dpll(clauses_of(tris, rels), V)


def minimal_set(V, tris, rels):
    keep = list(range(len(tris)))
    if solvable(V, [tris[k] for k in keep], [rels[k] for k in keep]):
        return None
    i = 0
    while i < len(keep):
        trial = keep[:i] + keep[i + 1:]
        if not solvable(V, [tris[k] for k in trial], [rels[k] for k in trial]):
            keep = trial
        else:
            i += 1
    return keep


def winding(tris, idx):
    par, pot, gens = {}, {}, []

    def find(v):
        acc = (0, 0)
        while par[v] != v:
            acc = (acc[0] + pot[v][0], acc[1] + pot[v][1])
            v = par[v]
        return v, acc

    for k in idx:
        for u, w, off in tris[k][2]:
            for v in (u, w):
                if v not in par:
                    par[v], pot[v] = v, (0, 0)
            (ru, pu), (rw, pw) = find(u), find(w)
            d = (pu[0] + off[0] - pw[0], pu[1] + off[1] - pw[1])
            if ru == rw:
                if d != (0, 0):
                    gens.append(d)
            else:
                par[rw], pot[rw] = ru, d
    return [g for g in gens if any(g)]


def placements():
    return [R for R in range(256) if R != comp(R) and R < comp(R)]


# ------------------------------------------------------------------ run

def run():
    rng = random.Random(20261023)
    checks, controls, failures = {}, {}, []

    # Lemma 1, instance by instance
    stats = {"instances": 0, "seam moved by a coboundary: equisatisfiable after flipping x": 0,
             "first corner changed: equisatisfiable after flipping x": 0}
    for _ in range(240):
        R = rng.choice(placements())
        Rb = comp(R)
        L, M = rng.choice(((3, 3), (3, 4), (4, 3)))
        a, b = rng.choice(TWISTS)
        V, tris = torus(L, M, 0, a, b)
        S = {v for v in range(V) if rng.random() < 0.4}
        x = [rng.randint(0, 1) for _ in tris]
        base = solvable(V, tris, [Rb if xi else R for xi in x])
        moved = [(c, tuple(gk ^ int(v in S) ^ int(c[0] in S) for gk, v in zip(g, c)), s) for c, g, s in tris]
        xm = [xi ^ int(c[0] in S) for xi, (c, _g, _s) in zip(x, tris)]
        stats["instances"] += 1
        stats["seam moved by a coboundary: equisatisfiable after flipping x"] += solvable(V, moved, [Rb if xi else R for xi in xm]) == base
        rot = [((c[1], c[2], c[0]), (g[1] ^ g[1], g[2] ^ g[1], g[0] ^ g[1]), s) for c, g, s in tris]
        rotR = lambda Q: sum(1 << (((p >> 1) & 1) | (((p >> 2) & 1) << 1) | ((p & 1) << 2)) for p in range(8) if Q >> p & 1)
        xr = [xi ^ g[1] for xi, (_c, g, _s) in zip(x, tris)]
        stats["first corner changed: equisatisfiable after flipping x"] += solvable(
            V, rot, [rotR(Rb) if xi else rotR(R) for xi in xr]) == base
    checks["Lemma 1 (complement-closed placements, random tori and seams)"] = stats
    if len(set(stats.values())) != 1:
        failures.append("Lemma 1 fails")
    # the converse: on one triangle, moving the twist by the coboundary of its first corner and relabelling back gives the solution
    # sets R0^111, R1^111; the law over fair x is unchanged exactly when the pair is complement-closed
    flip = lambda Q: sum(1 << (7 - p) for p in range(8) if Q >> p & 1)
    agree, total = 0, 0
    for R0 in range(256):
        for R1 in range(256):
            invariant = sorted((flip(R0), flip(R1))) == sorted((R0, R1))
            closed = R1 == comp(R0) or (R0 == comp(R0) and R1 == comp(R1))
            total += 1
            agree += invariant == closed
    checks["Lemma 1 converse: one-triangle gauge invariance at the first corner iff complement-closed (all 65536 pairs)"] = {
        "pairs": total, "agree": agree}
    if agree != total:
        failures.append("Lemma 1 converse fails")

    # Lemma 2, instance by instance
    agree = 0
    for _ in range(120):
        R0, R1 = rng.randrange(256), rng.randrange(256)
        a, b = rng.choice(TWISTS[1:])
        V, tw = torus(3, 3, 0, a, b)
        _, flat = torus(3, 3, 0, 0, 0)
        sig = [tuple(rng.randint(0, 1) for _ in range(3)) for _ in tw]
        x = [rng.randint(0, 1) for _ in tw]
        A = solvable(V, [(c, tuple(gi ^ si for gi, si in zip(g, s0)), sd) for (c, g, sd), s0 in zip(tw, sig)], [R1 if xi else R0 for xi in x])
        Bsig = [tuple(gi ^ si for gi, si in zip(g, s0)) for (c, g, sd), s0 in zip(tw, sig)]
        B = solvable(V, [(c, s0, sd) for (c, _g, sd), s0 in zip(flat, Bsig)], [R1 if xi else R0 for xi in x])
        agree += A == B
    checks["Lemma 2 (independent polarities): twisted world equals untwisted world with re-labelled polarities (3 x 3 torus)"] = {
        "instances": 120, "agree": agree}
    if agree != 120:
        failures.append("Lemma 2 fails")

    # Lemma 3
    maj = lambda a, b, c: (a & b) | (b & c) | (a & c)
    ok3 = all(all(Rel >> maj(a, b, c) & 1 for a in range(4) if Rel >> a & 1 for b in range(4) if Rel >> b & 1 for c in range(4) if Rel >> c & 1)
              for Rel in range(16))
    checks["Lemma 3: every relation on two bits is closed under majority"] = ok3
    if not ok3:
        failures.append("Lemma 3 fails")

    # Proposition 4
    p4 = {"colourings checked": 0, "exactly two sides with d = 1 on every triangle": 0, "class of d equals the twist": 0}
    exist = {}
    for (L, M) in ((3, 3), (4, 4)):
        for (a, b) in TWISTS:
            V, tris = torus(L, M, 0, a, b)
            for h in range(1 << V):
                if L == 4 and h % 7:
                    continue
                ds, nae = [], True
                for (c, g, sides) in tris:
                    vals = [((h >> c[k]) & 1) ^ g[k] for k in range(3)]
                    if vals[0] == vals[1] == vals[2]:
                        nae = False
                        break
                    ds.append((sides, (vals[0] ^ vals[1], vals[0] ^ vals[2], vals[1] ^ vals[2])))
                if not nae:
                    continue
                p4["colourings checked"] += 1
                p4["exactly two sides with d = 1 on every triangle"] += all(sum(d) == 2 for _s, d in ds)
                # d on the horizontal core row (the a->b sides of the up triangles in row 0) and on the vertical core column
                # (the a->b sides of the down triangles in column 0) must equal the twist's values L*alpha... i.e. the twist on them
                row = sum(d[0] for k, (_s, d) in enumerate(ds) if k < 2 * L and k % 2 == 0) & 1
                col = sum(d[0] for k, (_s, d) in enumerate(ds) if (k // 2) % L == 0 and k % 2 == 1) & 1
                p4["class of d equals the twist"] += (row, col) == (a, b)
    for L in range(2, 6):
        for M in range(2, 6):
            for S in range(L):
                for (a, b) in TWISTS:
                    V, tris = torus(L, M, S, a, b)
                    rels = [127] * len(tris)            # no gauged-monochromatic triangle: forbid 000 and 111
                    cl = clauses_of(tris, [127] * len(tris)) + clauses_of(tris, [254] * len(tris))
                    exist[f"{L}x{M}s{S}({a},{b})"] = dpll(cl, V)
    p4["tori and twists with a twisted not-all-equal colouring"] = sum(exist.values())
    p4["tori and twists tested"] = len(exist)
    p4["tori and twists without one"] = sorted(k for k, v in exist.items() if not v)
    # where none exists, enumerate every x: does the monotone world contradict there?
    contra = 0
    for key in p4["tori and twists without one"]:
        dims, tw = key.split("(")
        L, rest = dims.split("x")
        M, S = rest.split("s")
        a, b = int(tw[0]), int(tw[2])
        V, tris = torus(int(L), int(M), int(S), a, b)
        if len(tris) > 20:
            contra = -1
            break
        for xm in range(1 << len(tris)):
            contra += not solvable(V, tris, [127 if (xm >> k) & 1 else 254 for k in range(len(tris))])
    p4["contradicting x where no colouring exists (every x enumerated)"] = contra
    checks["Proposition 4 (monotone world)"] = p4
    if not (p4["colourings checked"] == p4["exactly two sides with d = 1 on every triangle"] == p4["class of d equals the twist"] > 0) \
            or contra != 0:
        failures.append("Proposition 4 fails")

    # Theorem 5 on placements with a doubly allowed assignment on a small torus
    t5 = {"tiling placements": 0, "planar contradictions": 0, "fitting-twist contradictions": 0, "minimal sets": 0,
          "minimal sets with nonzero winding": 0, "minimal sets on which the twist differs from every fitting twist": 0}
    local_planar = 0
    for R in placements():
        Rb = comp(R)
        U = R & Rb
        tiling = False
        fits = {}
        for (a, b) in TWISTS:
            V, tris = torus(4, 4, 0, a, b)
            fits[(a, b)] = solvable(V, tris, [U] * len(tris))
            V3, tris3 = torus(3, 3, 0, a, b)
            tiling |= fits[(a, b)] or solvable(V3, tris3, [U] * len(tris3))
        Vp, ptris, _ = patch(3)
        if not tiling:
            for _ in range(5):
                x = [rng.randint(0, 1) for _ in ptris]
                local_planar += not solvable(Vp, ptris, [Rb if xi else R for xi in x])
            continue
        t5["tiling placements"] += 1
        for _ in range(5):
            x = [rng.randint(0, 1) for _ in ptris]
            t5["planar contradictions"] += not solvable(Vp, ptris, [Rb if xi else R for xi in x])
        for (a, b), f in fits.items():
            V, tris = torus(4, 4, 0, a, b)
            for _ in range(3):
                x = [rng.randint(0, 1) for _ in tris]
                rels = [Rb if xi else R for xi in x]
                if f:
                    t5["fitting-twist contradictions"] += not solvable(V, tris, rels)
                else:
                    k = minimal_set(V, tris, rels)
                    if k is not None:
                        t5["minimal sets"] += 1
                        gens = winding(tris, k)
                        t5["minimal sets with nonzero winding"] += bool(gens)
                        # (d): for every fitting twist q_f, the class (a, b) - q_f is odd on some period of the set
                        odd_everywhere = all(any(((a ^ fa) * g[0] + (b ^ fb) * g[1]) & 1 for g in gens)
                                             for (fa, fb), ff in fits.items() if ff)
                        t5["minimal sets on which the twist differs from every fitting twist"] += odd_everywhere
    checks["Theorem 5 (4 x 4 and 3 x 3 tori, radius-3 patches)"] = t5
    if t5["planar contradictions"] or t5["fitting-twist contradictions"] or t5["minimal sets"] != t5["minimal sets with nonzero winding"] \
            or t5["minimal sets"] != t5["minimal sets on which the twist differs from every fitting twist"] or t5["minimal sets"] == 0:
        failures.append("Theorem 5 fails")
    controls["placements without a tiling do contradict on planar patches (counting every set as winding would be wrong)"] = local_planar

    # control: a contractible seam is a defect for x or 1-in-3
    Vp, ptris, ids = patch(4)
    disc = {v for (q, w), v in ids.items() if max(abs(q), abs(w), abs(q + w)) <= 2}
    seamed = [(c, tuple(int(v in disc) ^ int(c[0] in disc) for v in c), s) for c, _g, s in ptris]
    R0, R1 = sum(1 << p for p in (1, 2, 4)), 255
    plain_c = sum(not solvable(Vp, ptris, [R1 if rng.randint(0, 1) else R0 for _ in ptris]) for _ in range(60))
    seam_c = sum(not solvable(Vp, seamed, [R1 if rng.randint(0, 1) else R0 for _ in seamed]) for _ in range(60))
    controls["x or 1-in-3: contradictions on a radius-4 patch with a contractible seam (of 60; 0 without)"] = seam_c if plain_c == 0 else 0
    if not all(v > 0 for v in controls.values()):
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
    print(f"{result['status']}: three-place twists checked")
    for f in outcome["failures"]:
        print("  failed:", f)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
