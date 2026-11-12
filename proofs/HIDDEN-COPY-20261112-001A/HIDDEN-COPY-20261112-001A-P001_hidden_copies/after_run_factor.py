#!/usr/bin/env python3
"""After the run (descriptive, with the advisor's second check; not frozen): which E-small (harmony, kind set) pairs admit gadget
relations that are factor-permutive, by the Galois correspondence, without searching for gadgets.

    .venv/bin/python3 -B after_run_factor.py [--write]
For each E-small pair of the endo part:
- essentially unary, certified without the binary search when Aut has at least two orbits, or |W| is not a prime power, or some
  automorphism is a single cycle through all of W with |W| not prime (the affine branch of Palfy's theorem needs |W| a prime power and
  Aut = {lambda x + c}, transitive, whose elements are never one |W|-cycle unless |W| is prime); otherwise the binary part's verdict;
- the Aut-invariant equivalences on W (closures of single pairs under the automorphisms, and joins of the coarse ones one level deep),
  and their class counts:
  3 classes give a ternary factor-permutive gadget relation ("all equal or all different" on the classes; Sym(3) keeps it); 2 or 4
  classes give a 4-member one (x + y + z + w = 0 over Z_2, or over Z_2^2)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def is_prime_power(n):
    for p in range(2, n + 1):
        if n % p == 0:
            while n % p == 0:
                n //= p
            return n == 1
    return False


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def single_cycle(perm):
    n = len(perm)
    x, k = perm[0], 1
    while x != 0:
        x = perm[x]
        k += 1
    return k == n


def closure(n, perms, pairs):
    """the least Aut-invariant equivalence containing the pairs: union-find, then close under the permutations"""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    todo = list(pairs)
    while todo:
        a, b = todo.pop()
        ra, rb = find(a), find(b)
        if ra == rb:
            continue
        parent[ra] = rb
        for g in perms:
            todo.append((g[a], g[b]))
    return tuple(find(x) for x in range(n))


def canon(labels):
    seen, out = {}, []
    for l in labels:
        seen.setdefault(l, len(seen))
        out.append(seen[l])
    return tuple(out)


def invariant_equivalences(n, perms):
    """the principal Aut-invariant equivalences (closures of single pairs), with the class counts of their pairwise joins among those of
    at most 4 classes' refinements skipped: principal ones suffice for transitive cyclic actions, joins are added one level deep"""
    principal = {canon(closure(n, perms, [(a, b)])) for a in range(n) for b in range(a + 1, n)}
    out = set(principal)
    coarse = [x for x in principal if len(set(x)) <= 8]
    for x in coarse:
        for y in coarse:
            if x < y:
                pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if x[i] == x[j] or y[i] == y[j]]
                out.add(canon(closure(n, perms, pairs)))
    return out


def main():
    import hidden_lib as L
    endo = json.loads((HERE / "result_endo.json").read_text())["checks"]["result"]["rows"]
    try:
        binary = {(r["i"], r["j"]): r for r in json.loads((HERE / "result_binary.json").read_text())["checks"]["result"]["rows"]}
    except FileNotFoundError:
        binary = {}
    hs = L.harmonies_with_kind_sets()
    rows = []
    for r in endo:
        if r["E"] != "small" or r["states"] < 3:
            continue
        h = hs[r["i"]]
        st = L.setup(h["orbits"], h["P"], h["kind sets"][r["j"]])
        if r["beyond shifts and flips"] > 0:
            auts, complete = L.automorphisms(st, cap=200)
        else:
            auts, complete = list(st["G"]), bool(r["automorphisms complete"])
        norb, _ = L.orbits(st["n"], auts)
        n = st["n"]
        if norb >= 2:
            unary = "certified (Aut not transitive)"
        elif not is_prime_power(n):
            unary = "certified (|W| not a prime power)"
        elif not is_prime(n) and any(single_cycle(g) for g in auts):
            unary = "certified (a |W|-cycle with |W| not prime)"
        else:
            b = binary.get((r["i"], r["j"]))
            unary = "binary search: " + ("unary" if b and b["essential binary"] is False else ("affine" if b and b["essential binary"] else "not settled"))
        eqs = invariant_equivalences(n, auts)
        counts = sorted({len(set(e)) for e in eqs})
        rows.append({"harmony": r["harmony"], "i": r["i"], "j": r["j"], "states": n, "automorphisms": len(auts), "complete": complete,
                     "Aut-orbits": norb, "essentially unary": unary, "invariant equivalence class counts": counts,
                     "ternary factor-permutive (3 classes)": 3 in counts, "4-member (2 or 4 classes)": (2 in counts) or (4 in counts)})
    certified = [x for x in rows if x["essentially unary"].startswith("certified") or x["essentially unary"].endswith("unary")]
    out = {"E-small pairs with at least 3 states": len(rows),
           "essentially unary, certified or searched": len(certified),
           "of them with a ternary factor-permutive gadget relation": sum(1 for x in certified if x["ternary factor-permutive (3 classes)"]),
           "of them with a 4-member one only": sum(1 for x in certified if x["4-member (2 or 4 classes)"] and not x["ternary factor-permutive (3 classes)"]),
           "harmonies with a ternary one under some kind set": sorted({x["harmony"] for x in certified if x["ternary factor-permutive (3 classes)"]}),
           "harmonies with a ternary one under every E-small kind set": sorted({x["harmony"] for x in certified} - {x["harmony"] for x in certified if not x["ternary factor-permutive (3 classes)"]}),
           "pairs not certified": [[x["harmony"], x["j"], x["essentially unary"]] for x in rows if x not in certified],
           "rows": rows}
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    if "--write" in sys.argv:
        (HERE / "result_after_run_factor.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
