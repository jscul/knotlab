#!/usr/bin/env python3
"""Checks for BEYOND-TWO-20261101-001A: the known cycle-composing laws count easily.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


# ------------------------------------------------------------------------------------------------ the groups and the field
def cyclic(n):
    return list(range(n)), (lambda a, b: (a + b) % n), (lambda a: (-a) % n)


def klein():
    return [0, 1, 2, 3], (lambda a, b: a ^ b), (lambda a: a)


def s3():
    els = list(itertools.permutations(range(3)))
    comp = {(a, b): tuple(a[b[i]] for i in range(3)) for a in els for b in els}
    inv = {a: tuple(sorted(range(3), key=lambda i: a[i])) for a in els}
    idx = {a: i for i, a in enumerate(els)}
    return list(range(6)), (lambda x, y: idx[comp[(els[x], els[y])]]), (lambda x: idx[inv[els[x]]])


GF4_MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]       # 0, 1, w, w^2 = w + 1, addition is xor


def algebra(name):
    """(domain, operations as dicts on tuples): the Mal'tsev operation x y^-1 z, plus w x + w^2 y for GF(4)"""
    if name == "GF(4)":
        D = [0, 1, 2, 3]
        ops = [{t: t[0] ^ t[1] ^ t[2] for t in itertools.product(D, repeat=3)},
               {t: GF4_MUL[2][t[0]] ^ GF4_MUL[3][t[1]] for t in itertools.product(D, repeat=2)}]
        return D, ops
    D, mul, inv = {"Z3": cyclic(3), "Z4": cyclic(4), "Z2 x Z2": klein(), "S3": s3()}[name]
    return D, [{(x, y, z): mul(mul(x, inv(y)), z) for x in D for y in D for z in D}]


def closed(S, ops):
    return all(op[t] in S for op in ops for t in itertools.product(sorted(S), repeat=len(next(iter(op)))))


def partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


def congruences(S, ops):
    out = []
    for p in partitions(sorted(S)):
        cls = {v: i for i, block in enumerate(p) for v in block}
        good = True
        for op in ops:
            ar = len(next(iter(op)))
            for pos in range(ar):
                for block in p:
                    for a, b in itertools.combinations(block, 2):
                        for others in itertools.product(sorted(S), repeat=ar - 1):
                            t1 = others[:pos] + (a,) + others[pos:]
                            t2 = others[:pos] + (b,) + others[pos:]
                            if cls[op[t1]] != cls[op[t2]]:
                                good = False
                                break
                        if not good:
                            break
                    if not good:
                        break
                if not good:
                    break
            if not good:
                break
        if good:
            out.append(frozenset(frozenset(b) for b in p))
    return out


def maximal_proper(congs, S):
    full = frozenset([frozenset(S)])
    proper = [c for c in congs if c != full]

    def finer(c, d):  # c finer than or equal to d
        return all(any(b <= e for e in d) for b in c)
    return [c for c in proper if not any(c != d and finer(c, d) for d in proper)]


# ------------------------------------------------------------------------------------------------ 1. Theorem 1's criterion
expect = {"Z3": True, "Z4": True, "GF(4)": True, "S3": True, "Z2 x Z2": False}
info1, ok1 = {}, True
for name in expect:
    D, ops = algebra(name)
    subs = [frozenset(S) for r in range(2, len(D) + 1) for S in itertools.combinations(D, r) if closed(frozenset(S), [
        {t: v for t, v in op.items() if all(x in S for x in t)} for op in ops])]
    unique = {}
    for S in subs:
        rops = [{t: v for t, v in op.items() if all(x in S for x in t)} for op in ops]
        unique[len(S)] = unique.get(len(S), []) + [len(maximal_proper(congruences(S, rops), S))]
    clc = all(n == 1 for v in unique.values() for n in v)
    ok1 &= clc == expect[name]
    info1[name] = {"subalgebras by size: number of maximal congruences": unique, "composes like cycles (Theorem 1)": clc}
check("1 Theorem 1's criterion, computed: every subalgebra of the Mal'tsev algebra of Z3, Z4, GF(4) and S3 has exactly one maximal "
      "congruence (they compose like cycles), while Z2 x Z2 has three (it does not), as KNOT-CIRCUITS found", ok1, info1)


# ------------------------------------------------------------------------------------------------ 2. uniform fibres
def subgroup_closure(gens, mul, k):
    """subgroup of G^k generated by tuples (coordinatewise multiplication)"""
    ident = tuple([0] * k)
    H = {ident}
    frontier = [ident]
    gens = list(gens)
    while frontier:
        new = []
        for h in frontier:
            for g in gens:
                p = tuple(mul(a, b) for a, b in zip(h, g))
                if p not in H:
                    H.add(p)
                    new.append(p)
        frontier = new
    return H


def random_coset_relation(name, D, rng):
    """a random coset of a subgroup of G^k (k = 2 or 3); for GF(4) a random affine subspace (solutions of a GF(4)-linear equation)"""
    k = rng.choice([2, 3])
    if name == "GF(4)":
        coef = [rng.choice([1, 2, 3]) for _ in range(k)]
        c = rng.choice(D)
        rel = set()
        for t in itertools.product(D, repeat=k):
            s = 0
            for a, x in zip(coef, t):
                s ^= GF4_MUL[a][x]
            if s == c:
                rel.add(t)
        return k, rel
    _, mul, inv = {"Z3": cyclic(3), "Z4": cyclic(4), "Z2 x Z2": klein(), "S3": s3()}[name]
    gens = [tuple(rng.choice(D) for _ in range(k)) for _ in range(rng.choice([1, 2]))]
    H = subgroup_closure(gens, mul, k)
    a = tuple(rng.choice(D) for _ in range(k))
    return k, {tuple(mul(x, y) for x, y in zip(a, h)) for h in H}


info2, ok2 = {}, True
rng = random.Random(20261101)
for name in ("Z3", "Z4", "GF(4)", "S3"):
    D, _ = algebra(name)
    n = 4
    tally = collections.Counter()
    for trial in range(40):
        constraints = []
        for _ in range(rng.choice([2, 3, 4])):
            k, rel = random_coset_relation(name, D, rng)
            constraints.append((rng.sample(range(n), k), rel))
        sols = [t for t in itertools.product(D, repeat=n) if all(tuple(t[v] for v in vs) in rel for vs, rel in constraints)]
        if not sols:
            tally["empty systems"] += 1
            continue
        for r in range(1, n):
            for Y in itertools.combinations(range(n), r):
                fib = collections.Counter(tuple(t[v] for v in Y) for t in sols)
                uniform = len(set(fib.values())) == 1
                ok2 &= uniform
                tally["uniform projections" if uniform else "non-uniform projections"] += 1
    info2[name] = dict(tally)
check("2 uniform fibres: on 40 random systems of coset constraints over each of Z3, Z4, GF(4) and S3 (4 variables), every projection of "
      "the solution set has fibres of one size, so every count matrix is constant on the blocks of its support (strongly balanced)",
      ok2, info2)

# ------------------------------------------------------------------------------------------------ 3. control
D3 = [0, 1, 2]
blur = {(x, y, z) for x in D3 for y in D3 for z in D3 if ((x == 2) + (y == 2) + (z == 2)) % 2 == 0}
fib = collections.Counter((x, y) for x, y, z in blur)
ctrl = {"the preimage of even parity under 0,1 -> 0 and 2 -> 1 has fibre sizes": sorted(set(fib.values())),
        "so it is not a coset relation": len(set(fib.values())) > 1}
check("3 control: a blurred relation (ticket B) has fibres of two sizes, so the uniform-fibre test separates it from the coset laws",
      ctrl["so it is not a coset relation"], ctrl)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
