#!/usr/bin/env python3
"""Referee HIDDEN-COPY-R1 (lean): are the after-run's three-class invariant partitions complete? For every E-small pair of
result_after_run_factor.json, the automorphisms as the census computes them (hidden_lib, the only import of the census's code: the
group, not the partitions) and the referee's own lattice of Aut-invariant equivalences: every principal closure, then joins of any two
lattice elements until nothing new appears (the full lattice, not one level). Counts the pairs with an invariant three-class partition
against the census's 102, and lists the pairs whose automorphism list was capped (incomplete), where invariance under a part of Aut can
over-count.

    python3 -B ref_partitions.py      (writes result_partitions.json)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE.parents[2] / "proofs" / "HIDDEN-COPY-20261112-001A" / "HIDDEN-COPY-20261112-001A-P001_hidden_copies"
sys.path.insert(0, str(D))


def classes_of(labels):
    m = {}
    return tuple(m.setdefault(l, len(m)) for l in labels)


def join(n, x, y, perms):
    parent = list(range(n))

    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for lab in (x, y):
        first = {}
        for i, l in enumerate(lab):
            if l in first:
                ra, rb = f(i), f(first[l])
                if ra != rb:
                    parent[ra] = rb
            else:
                first[l] = i
    return classes_of([f(i) for i in range(n)])


def principal(n, perms, a, b):
    parent = list(range(n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    todo = [(a, b)]
    while todo:
        u, v = todo.pop()
        ru, rv = f(u), f(v)
        if ru == rv:
            continue
        parent[ru] = rv
        for g in perms:
            todo.append((g[u], g[v]))
    return classes_of([f(i) for i in range(n)])


def lattice(n, perms, limit=20000):
    L = {principal(n, perms, a, b) for a in range(n) for b in range(a + 1, n)}
    frontier = set(L)
    while frontier:
        new = set()
        for x in frontier:
            for y in L:
                z = join(n, x, y, perms)
                if z not in L and z not in new:
                    new.add(z)
        L |= new
        frontier = new
        if len(L) > limit:
            return L, False
    return L, True


def main():
    import hidden_lib as H
    fac = json.loads((D / "result_after_run_factor.json").read_text())
    endo = {(r["i"], r["j"]): r for r in json.loads((D / "result_endo.json").read_text())["checks"]["result"]["rows"]}
    hs = H.harmonies_with_kind_sets()
    out = {"pairs": 0, "census ternary": 0, "referee ternary": 0, "disagree": [], "automorphism lists capped": [], "lattice capped": 0}
    for row in fac["rows"]:
        h = hs[row["i"]]
        st = H.setup(h["orbits"], h["P"], h["kind sets"][row["j"]])
        e = endo[(row["i"], row["j"])]
        if e["beyond shifts and flips"] > 0:
            auts, complete = H.automorphisms(st, cap=200)
        else:
            auts, complete = list(st["G"]), bool(e["automorphisms complete"])
        n = st["n"]
        Lt, done = lattice(n, auts)
        out["lattice capped"] += not done
        three = any(len(set(x)) == 3 for x in Lt)
        out["pairs"] += 1
        out["census ternary"] += row["ternary factor-permutive (3 classes)"]
        out["referee ternary"] += three
        if three != row["ternary factor-permutive (3 classes)"]:
            out["disagree"].append([row["harmony"], row["j"], n, row["ternary factor-permutive (3 classes)"], three])
        if not complete:
            out["automorphism lists capped"].append([row["harmony"], row["j"], n, len(auts), three])
    (HERE / "result_partitions.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in out.items()}, indent=1))
    print(out["disagree"][:10], out["automorphism lists capped"][:10])


if __name__ == "__main__":
    main()
