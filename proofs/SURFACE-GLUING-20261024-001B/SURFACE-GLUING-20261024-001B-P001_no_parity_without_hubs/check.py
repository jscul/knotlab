#!/usr/bin/env python3
"""Check of SURFACE-GLUING-20261024-001B-P001 (standard library only, seed 20261024).

Relations are sets of 0/1 tuples. A relation is co-independent when no two excluded tuples differ in exactly one place. Hub-free
operations: glue two relations along one variable each and forget it; glue two variables of one relation and forget them; pin a
variable to 0 or 1.
- Lemmas 2 and 3 on random co-independent relations: the operations keep co-independence, and the glued excluded count is
  |Z_M^0| |Z_N^1| + |Z_M^1| |Z_N^0| exactly.
- Lemma 4: on up to four variables, the co-independent relations excluding half of all tuples are exactly the two parity relations.
- Theorem 5 on random co-independent relations without a parity face of dimension three or more: no result of an operation has one.
- Corollary 6: the hub-free closure, with intermediate relations of at most five variables, of every knot, and of all 32 non-parity
  knots together, contains no relation with a parity face of dimension three or more; the parity knots reach parity on 3, 4, 5.
Controls: a four-variable co-independent relation with a parity face but not itself parity reaches parity by one pin; with hubs, the
not-all-equal relation and pins define three-variable parity; a mutated gluing that drops the co-independence step miscounts.

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
AMAX = 5


# ------------------------------------------------------------------ operations

def excluded(n, S):
    return {t for t in itertools.product((0, 1), repeat=n) if t not in S}


def co_independent(n, S):
    Z = excluded(n, S)
    return all(tuple(t[k] ^ (k == i) for k in range(n)) not in Z for t in Z for i in range(n))


def glue2(a, b, i, j):
    (na, A), (nb, B) = a, b
    out = set()
    for s in A:
        for t in B:
            if s[i] == t[j]:
                out.add(tuple(s[k] for k in range(na) if k != i) + tuple(t[k] for k in range(nb) if k != j))
    return (na + nb - 2, frozenset(out))


def self_glue(a, i, j):
    na, A = a
    return (na - 2, frozenset(tuple(s[k] for k in range(na) if k not in (i, j)) for s in A if s[i] == s[j]))


def pin(a, i, v):
    na, A = a
    return (na - 1, frozenset(tuple(s[k] for k in range(na) if k != i) for s in A if s[i] == v))


def is_parity(n, S):
    return n >= 1 and len(S) == 2 ** (n - 1) and len({sum(t) % 2 for t in S}) == 1


def parity_faces(n, S, dmin=3):
    """dimensions >= dmin of faces (pinning some variables) on which S is a parity relation"""
    found = set()
    for k in range(0, n - dmin + 1):
        for fixed in itertools.combinations(range(n), k):
            for vals in itertools.product((0, 1), repeat=k):
                free = [i for i in range(n) if i not in fixed]
                F = {tuple(t[i] for i in free) for t in S if all(t[f] == v for f, v in zip(fixed, vals))}
                if is_parity(len(free), F):
                    found.add(len(free))
    return found


def canon(n, S):
    best = None
    for perm in itertools.permutations(range(n)):
        key = tuple(sorted(tuple(t[p] for p in perm) for t in S))
        if best is None or key < best:
            best = key
    return (n, best)


def closure(starts, amax):
    seen = {canon(n, S) for n, S in starts}
    frontier = list(seen)
    while frontier:
        new = []
        items = list(seen)
        for n, S in frontier:
            x = (n, frozenset(S))
            cand = [pin(x, i, v) for i in range(n) for v in (0, 1)]
            cand += [self_glue(x, i, j) for i in range(n) for j in range(i + 1, n)]
            for m, T in items:
                if n + m - 2 <= amax:
                    y = (m, frozenset(T))
                    cand += [glue2(x, y, i, j) for i in range(n) for j in range(m)]
            for c in cand:
                if c[0] >= 1 and c[1]:
                    k = canon(*c)
                    if k not in seen:
                        seen.add(k)
                        new.append(k)
        frontier = new
    return seen


# ------------------------------------------------------------------ random co-independent relations

def random_coind(rng, n, p):
    Z = set()
    order = list(itertools.product((0, 1), repeat=n))
    rng.shuffle(order)
    for t in order:
        if rng.random() < p and all(tuple(t[k] ^ (k == i) for k in range(n)) not in Z for i in range(n)):
            Z.add(t)
    return (n, frozenset(t for t in itertools.product((0, 1), repeat=n) if t not in Z))


def lemma_checks(rng):
    closed = formula = 0
    for _ in range(400):
        n, m = rng.randint(1, 4), rng.randint(1, 4)
        M, N = random_coind(rng, n, 0.6), random_coind(rng, m, 0.6)
        i, j = rng.randrange(n), rng.randrange(m)
        C = glue2(M, N, i, j)
        ZM, ZN = excluded(*M), excluded(*N)
        zm = [sum(1 for t in ZM if t[i] == v) for v in (0, 1)]
        zn = [sum(1 for t in ZN if t[j] == v) for v in (0, 1)]
        if C[0] >= 1:
            formula += len(excluded(*C)) == zm[0] * zn[1] + zm[1] * zn[0]
            closed += co_independent(*C)
        else:
            formula += 1
            closed += 1
    selfp = all(co_independent(*self_glue(M, 0, 1)) and co_independent(*pin(M, 0, 1))
                for M in (random_coind(rng, 4, 0.6) for _ in range(200)))
    return {"glued counts match the formula": formula == 400, "glued relations co-independent": closed == 400,
            "self-glued and pinned relations co-independent": selfp}


def lemma4():
    ok = True
    for n in range(1, 5):
        cube = list(itertools.product((0, 1), repeat=n))
        for Zbits in range(1 << len(cube)):
            Z = {cube[k] for k in range(len(cube)) if Zbits >> k & 1}
            if len(Z) != 2 ** (n - 1):
                continue
            S = frozenset(t for t in cube if t not in Z)
            if co_independent(n, S):
                ok &= is_parity(n, S)
    return ok


def theorem5_random(rng):
    tried = violations = 0
    while tried < 300:
        n, m = rng.randint(2, 4), rng.randint(2, 4)
        M, N = random_coind(rng, n, 0.5), random_coind(rng, m, 0.5)
        if parity_faces(*M) or parity_faces(*N):
            continue
        tried += 1
        outs = [glue2(M, N, rng.randrange(n), rng.randrange(m))]
        if n >= 2:
            outs.append(self_glue(M, 0, 1))
        outs.append(pin(M, 0, 0))
        violations += sum(1 for c in outs if c[0] >= 3 and parity_faces(*c))
    return {"pairs tried": tried, "results with a parity face of dimension >= 3": violations}


def knots():
    cube = list(itertools.product((0, 1), repeat=3))
    out = []
    for m in range(256):
        R = frozenset(cube[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append((3, R))
    return out


def corollary6():
    rows = []
    nonparity = []
    for idx, K in enumerate(knots()):
        cl = closure([K], AMAX)
        faces = set()
        for n, S in cl:
            faces |= parity_faces(n, frozenset(S))
        par = is_parity(*K)
        rows.append({"knot": sorted(''.join(map(str, t)) for t in K[1]), "parity knot": par, "closure size": len(cl),
                     "parity faces of dimension >= 3": sorted(faces)})
        if not par:
            nonparity.append(K)
    union = closure(nonparity, AMAX)
    union_faces = set()
    for n, S in union:
        union_faces |= parity_faces(n, frozenset(S))
    return rows, {"closure size": len(union), "parity faces of dimension >= 3": sorted(union_faces)}


def control_face():
    """M on 4 variables: excluded {(x, 0): x odd}. Co-independent, not parity, with a parity face; one pin gives parity."""
    cube = list(itertools.product((0, 1), repeat=4))
    M = (4, frozenset(t for t in cube if not (t[3] == 0 and sum(t[:3]) % 2 == 1)))
    return co_independent(*M) and not is_parity(*M) and is_parity(*pin(M, 3, 0))


def control_hub():
    """With hubs: inequality u != v as NAE(u, v, 0) and NAE(u, v, 1); OR(a, b, c) as NAE(a, b, w) and NAE(w, not-c, 1); the
    four clauses excluding the odd tuples give even parity on x, y, z. Some variables lie in three or more constraints."""
    NAE = {t for t in itertools.product((0, 1), repeat=3) if 0 < sum(t) < 3}
    x, y, z, nx, ny, nz, w1, w2, w3, w4, ZERO, ONE = range(12)
    cons = []
    for u, nu in ((x, nx), (y, ny), (z, nz)):
        cons += [(u, nu, ZERO), (u, nu, ONE)]
    comp = {x: nx, y: ny, z: nz, nx: x, ny: y, nz: z}
    for (a, b, c), w in (((nx, y, z), w1), ((x, ny, z), w2), ((x, y, nz), w3), ((nx, ny, nz), w4)):
        cons += [(a, b, w), (w, comp[c], ONE)]
    occ = [sum(c.count(v) for c in cons) for v in range(12)]
    rel = set()
    for a in itertools.product((0, 1), repeat=10):
        val = list(a) + [0, 1]
        if all(tuple(val[v] for v in c) in NAE for c in cons):
            rel.add((val[x], val[y], val[z]))
    return {"glued relation is even parity": rel == {t for t in itertools.product((0, 1), repeat=3) if sum(t) % 2 == 0},
            "uses a hub": max(occ[:10]) >= 3}


def control_mutation(rng):
    """Counting excluded glued tuples as |Z_M^0||Z_N^0| + |Z_M^1||Z_N^1| (same-side pairs) disagrees with the truth."""
    bad = 0
    for _ in range(200):
        M, N = random_coind(rng, 3, 0.6), random_coind(rng, 3, 0.6)
        C = glue2(M, N, 0, 0)
        ZM, ZN = excluded(*M), excluded(*N)
        zm = [sum(1 for t in ZM if t[0] == v) for v in (0, 1)]
        zn = [sum(1 for t in ZN if t[0] == v) for v in (0, 1)]
        bad += len(excluded(*C)) != zm[0] * zn[0] + zm[1] * zn[1]
    return bad > 0


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    lem = lemma_checks(rng)
    l4 = lemma4()
    t5 = theorem5_random(rng)
    rows, union = corollary6()
    hub = control_hub()
    controls = {
        "a co-independent relation with a parity face reaches parity by one pin": control_face(),
        "with hubs, not-all-equal and pins define three-variable parity": hub["glued relation is even parity"] and hub["uses a hub"],
        "a same-side count mutation disagrees with the glued excluded count": control_mutation(rng),
    }
    nonpar_ok = all(not r["parity faces of dimension >= 3"] for r in rows if not r["parity knot"])
    par_ok = all(r["parity faces of dimension >= 3"] == [3, 4, 5] for r in rows if r["parity knot"])
    ok = (all(lem.values()) and l4 and t5["results with a parity face of dimension >= 3"] == 0 and nonpar_ok and par_ok
          and not union["parity faces of dimension >= 3"] and all(controls.values()))
    result["checks"] = {"Lemmas 2 and 3": lem, "Lemma 4 (up to four variables)": l4, "Theorem 5 (random)": t5,
                        "Corollary 6 (closures, at most five variables)": rows, "all 32 non-parity knots together": union}
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
    print(json.dumps({"status": result["status"], "Lemmas": lem, "Lemma 4": l4, "Theorem 5": t5, "union": union,
                      "closure sizes": sorted({r["closure size"] for r in rows}), "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
