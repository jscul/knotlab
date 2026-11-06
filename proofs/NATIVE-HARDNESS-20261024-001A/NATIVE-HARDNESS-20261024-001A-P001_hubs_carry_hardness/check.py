#!/usr/bin/env python3
"""Check of NATIVE-HARDNESS-20261024-001A-P001 (standard library only, seed 20261024).

Census of the 34 three-place knots (relations on three bits with every pair of places unconstrained, not the full cube):
- delta-matroid (symmetric exchange: for feasible A, B and x in A xor B there is y in A xor B with A xor {x, y} feasible);
- even (all tuples of one parity);
- coverable in the sense of Kazda, Kolmogorov and Rolinek (Definitions 9 and 10 of arXiv:1602.03124): for every alpha there is an
  even delta-matroid M_alpha containing every tuple reachable from alpha by even-neighbour steps, such that whenever gamma is
  reachable and gamma + u + v lies in M_alpha but not in M, both gamma + u and gamma + v lie in M;
- Schaefer classes with constants (affine, Horn, dual-Horn, bijunctive), which decide NP-hardness of the unrestricted problem;
- for the seven symmetric knots, the allowed numbers of ones and their largest gap (general factor problem).
Context: all 155 nonempty three-place delta-matroids and the unary relations are coverable; the hub relation (all-equal on three
places) is not a delta-matroid. Reductions are checked on random networks: hub-free networks are edge problems (every variable in
exactly two constraints after giving each open distinction a unary 'free' constraint), and a variable in three copies is equivalent to
three copies joined by the all-equal relation.
Controls: a four-place delta-matroid that is not coverable is rejected; the hub relation fails the exchange axiom; dropping the
third coverability condition would accept the non-coverable example.

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
NONCOVERABLE_4 = ["0000", "0001", "0010", "0110", "0111", "1010", "1011", "1100", "1101"]   # located by the producer's scan


def flip(t, *idx):
    t = list(t)
    for i in idx:
        t[i] ^= 1
    return tuple(t)


def is_delta_matroid(S):
    n = len(next(iter(S)))
    for a in S:
        for b in S:
            diff = [i for i in range(n) if a[i] != b[i]]
            for x in diff:
                if not any((flip(a, x) if y == x else flip(a, x, y)) in S for y in diff):
                    return False
    return True


def is_even(S):
    return len({sum(t) % 2 for t in S}) == 1


def even_delta_matroids(n):
    cube = list(itertools.product((0, 1), repeat=n))
    out = []
    for par in (0, 1):
        cls = [t for t in cube if sum(t) % 2 == par]
        for m in range(1, 1 << len(cls)):
            S = frozenset(cls[i] for i in range(len(cls)) if m >> i & 1)
            if is_delta_matroid(S):
                out.append(S)
    return out


def reachable(M, a, n):
    seen, stack = {a}, [a]
    while stack:
        x = stack.pop()
        for u in range(n):
            if flip(x, u) in M:
                continue
            for v in range(n):
                if v != u:
                    y = flip(x, u, v)
                    if y in M and y not in seen:
                        seen.add(y)
                        stack.append(y)
    return seen


def coverable(M, evens, use_condition_3=True):
    n = len(next(iter(M)))
    for a in M:
        R = reachable(M, a, n)
        ok = False
        for Ma in evens:
            if not R <= Ma:
                continue
            if not use_condition_3 or all(not (flip(g, u, v) in Ma and flip(g, u, v) not in M)
                                          or (flip(g, u) in M and flip(g, v) in M)
                                          for g in R for u in range(n) for v in range(n) if u != v):
                ok = True
                break
        if not ok:
            return False
    return True


def closed_under(S, op):
    return all(op(*ts) in S for ts in itertools.product(S, repeat=3 if op.__code__.co_argcount == 3 else 2))


def schaefer(S):
    AND = lambda a, b: tuple(x & y for x, y in zip(a, b))
    OR = lambda a, b: tuple(x | y for x, y in zip(a, b))
    MAJ = lambda a, b, c: tuple((x & y) | (y & z) | (x & z) for x, y, z in zip(a, b, c))
    AFF = lambda a, b, c: tuple(x ^ y ^ z for x, y, z in zip(a, b, c))
    classes = {"affine": closed_under(S, AFF), "Horn": closed_under(S, AND), "dual-Horn": closed_under(S, OR),
               "bijunctive": closed_under(S, MAJ)}
    classes["NP-hard with constants"] = not any(classes.values())
    return classes


def knots():
    cube = list(itertools.product((0, 1), repeat=3))
    out = []
    for m in range(256):
        R = frozenset(cube[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def max_gap(W):
    W = sorted(W)
    return max([b - a - 1 for a, b in zip(W, W[1:])] or [0])


def solve(nv, cons):
    """brute force: cons = list of (scope, relation set)"""
    return any(all(tuple(a[v] for v in sc) in R for sc, R in cons) for a in itertools.product((0, 1), repeat=nv))


def reduction_checks(rng, K3):
    """(i) hub-free networks are edge problems: each variable in exactly two constraints once open variables get the unary free
    constraint; (ii) a variable in three copies is equisatisfiable with three copies joined by all-equal."""
    EQ3 = {(0, 0, 0), (1, 1, 1)}
    FREE = {(0,), (1,)}
    ok_edge = ok_hub = True
    agree = 0
    for _ in range(300):
        nvar = rng.randint(4, 8)
        ncopies = rng.randint(2, 4)
        cons, occ = [], [0] * nvar
        for _ in range(ncopies):
            sc = tuple(rng.randrange(nvar) for _ in range(3))
            cons.append((sc, rng.choice(K3)))
            for v in sc:
                occ[v] += 1
        pins = [(v, rng.randint(0, 1)) for v in range(nvar) if occ[v] and rng.random() < 0.2]
        full = cons + [((v,), {(b,)}) for v, b in pins]
        truth = solve(nvar, full)
        # split every occurrence into its own copy variable; join copies of a variable by all-equal (or equality chains)
        newcons, nv, copies = [], 0, {}
        for sc, R in full:
            sc2 = []
            for v in sc:
                copies.setdefault(v, []).append(nv)
                sc2.append(nv)
                nv += 1
            newcons.append((tuple(sc2), R))
        for v, cs in copies.items():
            if len(cs) == 1:
                newcons.append(((cs[0],), FREE))
            elif len(cs) == 2:
                newcons.append(((cs[0], cs[1]), {(0, 0), (1, 1)}))
            else:
                prev = cs[0]
                for c in cs[1:-1]:
                    extra = nv
                    nv += 1
                    newcons.append(((prev, c, extra), EQ3))
                    prev = extra
                newcons.append(((prev, cs[-1]), {(0, 0), (1, 1)}))
        occ2 = [0] * nv
        for sc, _ in newcons:
            for v in sc:
                occ2[v] += 1
        ok_edge &= all(o == 2 for o in occ2)
        agree += solve(nv, newcons) == truth
    ok_hub = agree == 300
    return {"every variable in exactly two constraints after splitting": ok_edge,
            "split instances equisatisfiable (300 random networks)": ok_hub}


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    E3, E1, E4 = even_delta_matroids(3), even_delta_matroids(1), even_delta_matroids(4)
    K = knots()
    rows = []
    for R in K:
        sym = all(tuple(t[i] for i in p) in R for t in R for p in itertools.permutations(range(3)))
        row = {"knot": sorted(''.join(map(str, t)) for t in R), "delta-matroid": is_delta_matroid(R), "even": is_even(R),
               "coverable": coverable(R, E3), **schaefer(R)}
        if sym:
            W = sorted({sum(t) for t in R})
            row["symmetric: allowed numbers of ones"] = W
            row["largest gap"] = max_gap(W)
        rows.append(row)
    cube3 = list(itertools.product((0, 1), repeat=3))
    all_dm = [frozenset(cube3[i] for i in range(8) if m >> i & 1) for m in range(1, 256)]
    all_dm = [S for S in all_dm if is_delta_matroid(S)]
    unary = [frozenset({(0,)}), frozenset({(1,)}), frozenset({(0,), (1,)})]
    EQ3 = frozenset({(0, 0, 0), (1, 1, 1)})
    nc4 = frozenset(tuple(int(c) for c in s) for s in NONCOVERABLE_4)
    summary = {
        "knots": len(K),
        "delta-matroids": sum(r["delta-matroid"] for r in rows), "even": sum(r["even"] for r in rows),
        "coverable": sum(r["coverable"] for r in rows),
        "affine": sum(r["affine"] for r in rows), "Horn": sum(r["Horn"] for r in rows),
        "dual-Horn": sum(r["dual-Horn"] for r in rows), "bijunctive": sum(r["bijunctive"] for r in rows),
        "NP-hard with constants": sum(r["NP-hard with constants"] for r in rows),
        "symmetric knots (allowed ones, largest gap)": [(r["symmetric: allowed numbers of ones"], r["largest gap"])
                                                        for r in rows if "largest gap" in r],
        "nonempty three-place delta-matroids": len(all_dm),
        "of which coverable": sum(coverable(S, E3) for S in all_dm),
        "unary relations coverable": all(coverable(S, E1) for S in unary),
        "hub relation is a delta-matroid": is_delta_matroid(EQ3),
        "hub relation's largest gap": max_gap([0, 3]),
    }
    red = reduction_checks(rng, K)
    controls = {
        "a four-place delta-matroid that is not coverable is rejected": is_delta_matroid(nc4) and not coverable(nc4, E4),
        "the hub relation fails the exchange axiom": not is_delta_matroid(EQ3),
        "without the third condition the non-coverable example would pass": coverable(nc4, E4, use_condition_3=False),
    }
    ok = (summary["delta-matroids"] == 34 and summary["even"] == 2 and summary["coverable"] == 34
          and summary["of which coverable"] == summary["nonempty three-place delta-matroids"] == 155
          and summary["unary relations coverable"] and not summary["hub relation is a delta-matroid"]
          and summary["hub relation's largest gap"] == 2
          and all(g <= 1 for _, g in summary["symmetric knots (allowed ones, largest gap)"])
          and all(red.values()) and all(controls.values()))
    result["checks"] = {"summary": summary, "knots": rows, "reductions": red}
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
    print(json.dumps({"status": result["status"], "summary": summary, "reductions": red, "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
