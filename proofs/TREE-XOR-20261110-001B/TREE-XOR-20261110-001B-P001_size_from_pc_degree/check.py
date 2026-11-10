"""Checks for TREE-XOR-20261110-001B. The theorem is proved by hand; check 1 confirms its combination step on small formulas: for random
unsatisfiable 3-CNFs on 8 variables, every complete parity decision tree's size s and the formula's F2 polynomial-calculus degree D
satisfy D <= log2 s + 3, where D is computed exactly by degree-bounded linear algebra (the space of polynomials of degree <= D derivable
by PC's rules contains 1).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = {}
T0 = time.time()
NV = 8


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# multilinear polynomials over F2 as frozensets of monomials (monomial = bitmask of variables)
def mul_mono(p, m):
    return frozenset_xor(q | m for q in p)


def frozenset_xor(items):
    s = set()
    for x in items:
        s ^= {x}
    return frozenset(s)


def falsifier(clause):
    """the conjunction falsifying a clause [(var, sign)] (sign 1: positive literal), as a multilinear polynomial"""
    p = frozenset([0])
    for v, sgn in clause:
        lit = frozenset([1 << v]) if sgn == 0 else frozenset([0, 1 << v])     # x_v (negative literal false iff x = 1) or 1 + x_v
        p = frozenset_xor(a | b for a in p for b in lit)
    return p


def pc_degree(axioms, maxdeg):
    """least D such that 1 lies in the degree-D PC closure over F2 (multilinear, so x^2 = x is built in): the span of m * a for axioms a
    and monomials m with deg(m * a) <= D, closed under multiplication by variables while the degree stays <= D"""
    for D in range(1, maxdeg + 1):
        basis = {}

        def reduce(p):
            p = set(p)
            while p:
                lead = max(p, key=lambda m: (bin(m).count("1"), m))
                if lead not in basis:
                    return frozenset(p), lead
                p ^= basis[lead]
            return frozenset(), None

        def insert(p):
            r, lead = reduce(p)
            if lead is None:
                return False
            basis[lead] = set(r)
            return True
        queue = [a for a in axioms if max(bin(m).count("1") for m in a) <= D]
        for a in queue:
            insert(a)
        changed = True
        while changed:
            changed = False
            for lead, p in list(basis.items()):
                for v in range(NV):
                    q = mul_mono(frozenset(p), 1 << v)
                    if q and max(bin(m).count("1") for m in q) <= D and insert(q):
                        changed = True
            r, lead = reduce(frozenset([0]))
            if lead is None:
                return D
        r, lead = reduce(frozenset([0]))
        if lead is None:
            return D
    return None


def satisfiable(cls):
    for x in range(1 << NV):
        if all(any(((x >> v) & 1) == s for v, s in c) for c in cls):
            return True
    return False


def tree_size(cls, rng, strategy):
    """leaves of a complete parity decision tree for the false-clause search, built by a simple strategy"""
    def forced(sub):
        for c in cls:
            if all(all(((x >> v) & 1) != s for v, s in c) for x in sub):
                return True
        return False

    def build(sub):
        if forced(sub):
            return 1
        while True:
            if strategy == "variables":
                free = [v for v in range(NV) if len({(x >> v) & 1 for x in sub}) == 2]
                mask = 1 << rng.choice(free)
            else:
                mask = rng.randrange(1, 1 << NV)
            parts = [[x for x in sub if bin(x & mask).count("1") % 2 == b] for b in (0, 1)]
            if all(parts):
                break
        return sum(build(p) for p in parts)
    return build(list(range(1 << NV)))


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    rng = random.Random(20261110)
    rows, ok = [], True
    while len(rows) < 12:
        cls = [tuple((v, rng.randrange(2)) for v in rng.sample(range(NV), 3)) for _ in range(rng.randint(40, 70))]
        if satisfiable(cls):
            continue
        D = pc_degree([falsifier(c) for c in cls], 8)
        for strat in ("variables", "parities"):
            s = tree_size(cls, rng, strat)
            ok &= D is not None and D <= math.log2(s) + 3
            rows.append({"clauses": len(cls), "PC degree": D, "strategy": strat, "tree size": s, "log2 s + 3": round(math.log2(s) + 3, 2)})
    check("1_pc_degree_at_most_log_size_plus_width", ok, {"formulas and trees": rows})
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "TREE-XOR-20261110-001B", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
