#!/usr/bin/env python3
"""Check URQUHART-TSEITIN-20261020-001B-P001: hole-faithful refutations of Tseitin formulas, and the read-2 barrier.

For each declared graph G with charge odd at vertex 0, the check builds resolution refutations of T(G, c) in the clause
encoding and verifies them:
  * a carving refutation (parity clauses of the cuts of an optimal carving, combined by branching on shared edges) and
    Davis-Putnam refutations (variable elimination) for several random orders;
  * validity: every derived clause is the non-tautological resolvent of its two recorded premises, and the empty clause
    is derived;
  * hole-faithfulness: at every step from a consistent clause D to a consistent premise P on pivot x, no variable of D
    missing from P is an edge touching the region where the hole must lie after reading x.
It then walks every critical assignment (exactly one violated vertex, the hole) down each refutation and checks:
  * regions never grow along a walk;
  * given the walk so far (the exact path), the hole is uniform on the current clause's region, and so it is also
    uniform at every node after averaging over paths;
  * the fraction of walks passing a clause C is at most (|K_C|/n) * 2^-fd(vars C), where fd is the dimension of the
    cycle space projected onto the clause's variables.
Control: refutations whose second step forgets a variable at the hole's region (each needed clause derived by lifted
Davis-Putnam elimination) are not hole-faithful, and the hole's posterior becomes non-uniform.
Read-2 barrier: for each graph and an even charge, a branching program that checks the vertex constraints one after
another computes the satisfiable Tseitin formula, reads each variable at most twice on every path, and has size O(m).

The Graph class, carving() and grid() are copied from SOS-SIZE-20261020-001B-P001's check.py.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def popcount(x: int) -> int:
    return bin(x).count("1")


class Graph:
    def __init__(self, edges):
        self.edges = [tuple(e) for e in edges]
        self.n = 1 + max(max(e) for e in self.edges)
        self.m = len(self.edges)
        self.star = [0] * self.n
        self.nbr = [0] * self.n
        for i, (a, b) in enumerate(self.edges):
            self.star[a] |= 1 << i
            self.star[b] |= 1 << i
            self.nbr[a] |= 1 << b
            self.nbr[b] |= 1 << a
        self.deg = [popcount(s) for s in self.star]
        self.full = (1 << self.n) - 1

    def cut(self, U: int) -> int:
        return sum(1 << i for i, (a, b) in enumerate(self.edges) if (U >> a & 1) != (U >> b & 1))


def carving(g: Graph):
    cut = [0] * (1 << g.n)
    for S in range(1, 1 << g.n):
        v = (S & -S).bit_length() - 1
        R = S ^ (1 << v)
        cut[S] = cut[R] + g.deg[v] - 2 * popcount(g.nbr[v] & R)
    big = 10 ** 9
    best, split = [big] * (1 << g.n), [0] * (1 << g.n)
    for v in range(g.n):
        best[1 << v] = cut[1 << v]
    for S in sorted(range(1, g.full + 1), key=popcount):
        if popcount(S) < 2:
            continue
        low = S & -S
        b, arg = big, 0
        sub = (S - 1) & S
        while sub:
            if sub & low:
                val = max(best[sub], best[S ^ sub])
                if val < b:
                    b, arg = val, sub
            sub = (sub - 1) & S
        best[S], split[S] = max(cut[S], b), arg
    root = min((S for S in range(1, g.full) if S & 1), key=lambda S: max(best[S], best[g.full ^ S]))
    width = max(best[root], best[g.full ^ root])

    def tree(S):
        return S if popcount(S) == 1 else (S, tree(split[S]), tree(S ^ split[S]))

    return width, tree(root), tree(g.full ^ root)


def grid(a, b):
    E = []
    for r in range(a):
        for c in range(b):
            if c + 1 < b:
                E.append((r * b + c, r * b + c + 1))
            if r + 1 < a:
                E.append((r * b + c, (r + 1) * b + c))
    return E


GRAPHS = {
    "K4": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "prism": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5)],
    "K33": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)],
    "cube": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)],
    "wagner": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 7), (4, 7), (5, 6), (6, 7)],
    "grid3x3": grid(3, 3),
    "petersen": [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9),
                 (6, 9), (6, 8), (5, 8)],
}


# ---------------------------------------------------------------- clauses and refutations
# A clause is (pos, neg): edge bitmasks of its positive and negative literals. It is falsified exactly when every
# variable in pos is 0 and every variable in neg is 1.

def axioms(g: Graph, odd: int):
    out = []
    for v in range(g.n):
        bits = [i for i in range(g.m) if g.star[v] >> i & 1]
        for vals in product((0, 1), repeat=len(bits)):
            if sum(vals) % 2 != (odd >> v & 1):
                out.append((sum(1 << b for b, x in zip(bits, vals) if x == 0),
                            sum(1 << b for b, x in zip(bits, vals) if x == 1)))
    return out


class Proof:
    def __init__(self, g: Graph, odd: int):
        self.g, self.odd = g, odd
        self.axiom_set = set(axioms(g, odd))
        self.deriv = {c: None for c in self.axiom_set}

    def resolve(self, a, b, x):
        assert a[0] >> x & 1 and b[1] >> x & 1
        c = ((a[0] | b[0]) & ~(1 << x), (a[1] | b[1]) & ~(1 << x))
        assert c[0] & c[1] == 0, "tautological resolvent"
        self.deriv.setdefault(c, (x, a, b))
        return c

    def pick(self, c0, c1, x):
        """Derive a subclause of the resolvent of c0 (with x) and c1 (with not x), using subsumption."""
        if not c0[0] >> x & 1:
            return c0
        if not c1[1] >> x & 1:
            return c1
        return self.resolve(c0, c1, x)

    def reachable(self):
        seen, stack = set(), [(0, 0)]
        while stack:
            c = stack.pop()
            if c in seen:
                continue
            seen.add(c)
            d = self.deriv[c]
            if d:
                stack += [d[1], d[2]]
        return seen

    def valid(self):
        if (0, 0) not in self.deriv:
            return False
        for c in self.reachable():
            d = self.deriv[c]
            if d is None:
                if c not in self.axiom_set:
                    return False
                continue
            x, a, b = d
            if not (a[0] >> x & 1 and b[1] >> x & 1):
                return False
            if c != ((a[0] | b[0]) & ~(1 << x), (a[1] | b[1]) & ~(1 << x)) or c[0] & c[1]:
                return False
        return True


def carving_proof(g: Graph, odd: int):
    width, left, right = carving(g)
    P = Proof(g, odd)

    def vset(t):
        return t if isinstance(t, int) else t[0]

    def branch(target, F_bits, leaf):
        def rec(prefix):
            if len(prefix) == len(F_bits):
                gp = target[0] | sum(1 << x for x, y in zip(F_bits, prefix) if y == 0)
                gn = target[1] | sum(1 << x for x, y in zip(F_bits, prefix) if y == 1)
                return leaf(gp, gn)
            f = F_bits[len(prefix)]
            return P.pick(rec(prefix + (0,)), rec(prefix + (1,)), f)
        return rec(())

    def build(t):
        U = vset(t)
        if isinstance(t, int):
            return {c: c for c in P.axiom_set if (c[0] | c[1]) == g.star[U.bit_length() - 1]}
        _, a, b = t
        Ra, Rb = build(a), build(b)
        Ua, Ub = vset(a), vset(b)
        D = g.cut(U)
        bits = [i for i in range(g.m) if D >> i & 1]
        F_bits = [i for i in range(g.m) if (g.cut(Ua) & g.cut(Ub)) >> i & 1]
        cU = popcount(odd & U) % 2

        def leaf(gp, gn):
            for R, Uc in ((Ra, Ua), (Rb, Ub)):
                Dc = g.cut(Uc)
                if (gp & Dc, gn & Dc) in R:
                    return R[(gp & Dc, gn & Dc)]
            raise AssertionError("no child clause")

        res = {}
        for vals in product((0, 1), repeat=len(bits)):
            if sum(vals) % 2 != cU:
                target = (sum(1 << x for x, y in zip(bits, vals) if y == 0), sum(1 << x for x, y in zip(bits, vals) if y == 1))
                res[target] = branch(target, F_bits, leaf)
        return res

    RA, RB = build(left), build(right)
    A = vset(left)
    F_bits = [i for i in range(g.m) if g.cut(A) >> i & 1]

    def root_leaf(gp, gn):
        for R in (RA, RB):
            if (gp, gn) in R:
                return R[(gp, gn)]
        raise AssertionError("root")

    assert branch((0, 0), F_bits, root_leaf) == (0, 0)
    return P, width


def dp_proof(g: Graph, odd: int, order):
    P = Proof(g, odd)
    clauses = set(P.axiom_set)
    for x in order:
        pos = [c for c in clauses if c[0] >> x & 1]
        neg = [c for c in clauses if c[1] >> x & 1]
        rest = {c for c in clauses if not ((c[0] | c[1]) >> x & 1)}
        for a in pos:
            for b in neg:
                if ((a[0] | b[0]) & (a[1] | b[1])) & ~(1 << x):
                    continue
                rest.add(P.resolve(a, b, x))
        clauses = rest
        if (0, 0) in clauses:
            break
    return P


def derive_clause(P: Proof, target):
    """A derivation of a subclause of `target`: Davis-Putnam elimination of the variables outside it, with the
    target's literals passive (the lift of a refutation of the formula restricted by the target's falsifier)."""
    tvars = target[0] | target[1]
    clauses = {c for c in P.axiom_set if not ((c[0] & target[1]) or (c[1] & target[0]))}
    for c in clauses:
        if not (c[0] | c[1]) & ~tvars:
            return c
    for x in [i for i in range(P.g.m) if not tvars >> i & 1]:
        pos = [c for c in clauses if c[0] >> x & 1]
        neg = [c for c in clauses if c[1] >> x & 1]
        rest = {c for c in clauses if not ((c[0] | c[1]) >> x & 1)}
        for a in pos:
            for b in neg:
                if ((a[0] | b[0]) & (a[1] | b[1])) & ~(1 << x):
                    continue
                r = P.resolve(a, b, x)
                if not (r[0] | r[1]) & ~tvars:
                    return r
                rest.add(r)
        clauses = rest
    raise AssertionError("no derivation")


def forgetting_proof(g: Graph, odd: int, y: int, z: int):
    """bottom <= (x_y), (not x_y);  (x_y) <= (x_y or x_z), (not x_z): the step into (not x_z) forgets y."""
    P = Proof(g, odd)
    cy = P.pick(derive_clause(P, ((1 << y) | (1 << z), 0)), derive_clause(P, (0, 1 << z)), z)
    cny = derive_clause(P, (0, 1 << y))
    if cy == (0, 0) or cny == (0, 0):
        return None
    assert P.resolve(cy, cny, y) == (0, 0)
    return P


# ---------------------------------------------------------------- regions, faithfulness, walks

def components(g: Graph, removed: int):
    parent = list(range(g.n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, (a, b) in enumerate(g.edges):
        if not removed >> i & 1:
            parent[find(a)] = find(b)
    comps = {}
    for v in range(g.n):
        comps[find(v)] = comps.get(find(v), 0) | (1 << v)
    return list(comps.values())


def region_of(g: Graph, odd: int, Q: int, ones: int):
    """The unique odd component of G minus the edges Q under the assignment that is 1 on `ones` and 0 elsewhere on Q."""
    found = [K for K in components(g, Q) if (popcount(g.cut(K) & ones) + popcount(K & odd)) % 2]
    return found[0] if len(found) == 1 else None


def region(g, odd, c):
    return region_of(g, odd, c[0] | c[1], c[1])


def faithful(P: Proof):
    g, odd = P.g, P.odd
    bad, steps = 0, 0
    for c in P.reachable():
        d = P.deriv[c]
        if not d or region(g, odd, c) is None:
            continue
        x = d[0]
        for prem in (d[1], d[2]):
            if region(g, odd, prem) is None:
                continue
            Kx = region_of(g, odd, c[0] | c[1] | (1 << x), c[1] | (prem[1] & (1 << x)))
            forgotten = (c[0] | c[1]) & ~(prem[0] | prem[1])
            steps += 1
            if any(forgotten >> i & 1 and (Kx >> a & 1 or Kx >> b & 1) for i, (a, b) in enumerate(g.edges)):
                bad += 1
    return bad, steps


def critical(g: Graph, odd: int):
    out = []
    for alpha in range(1 << g.m):
        viol = [v for v in range(g.n) if (popcount(alpha & g.star[v]) + (odd >> v & 1)) % 2]
        if len(viol) == 1:
            out.append((alpha, viol[0]))
    return out


def free_dim(g: Graph, Q: int) -> int:
    return popcount(Q) - (len(components(g, Q)) - 1)


def walk_stats(P: Proof):
    g, odd = P.g, P.odd
    crit = critical(g, odd)
    by_prefix, by_node, monotone = {}, {}, True
    for alpha, h in crit:
        c, path = (0, 0), [(0, 0)]
        while P.deriv[c]:
            x, a, b = P.deriv[c]
            c = a if not alpha >> x & 1 else b
            path.append(c)
        sizes = [popcount(region(g, odd, q)) for q in path]
        monotone &= all(s >= t for s, t in zip(sizes, sizes[1:]))
        for i, q in enumerate(path):
            key = tuple(path[: i + 1])
            by_prefix.setdefault(key, {})
            by_prefix[key][h] = by_prefix[key].get(h, 0) + 1
            by_node.setdefault(q, {})
            by_node[q][h] = by_node[q].get(h, 0) + 1

    def uniform(c, hs):
        K = region(g, odd, c)
        counts = {hs.get(v, 0) for v in range(g.n) if K >> v & 1}
        return len(counts) == 1 and all(K >> v & 1 for v in hs)

    hist_bad = sum(1 for key, hs in by_prefix.items() if not uniform(key[-1], hs))
    node_bad = sum(1 for c, hs in by_node.items() if not uniform(c, hs))
    N = len(crit)
    passing_ok = all(sum(hs.values()) * g.n * (1 << free_dim(g, c[0] | c[1])) <= N * popcount(region(g, odd, c))
                     for c, hs in by_node.items())
    return {"critical_assignments": N, "walk_prefixes": len(by_prefix), "nodes_on_walks": len(by_node),
            "regions_never_grow": monotone, "history_nonuniform_prefixes": hist_bad, "nonuniform_nodes": node_bad,
            "passing_within_2^-fd": passing_ok}


# ---------------------------------------------------------------- the read-2 barrier

def read_two_program(g: Graph, odd_even: int):
    """A branching program checking vertex constraints one after another. Nodes are (vertex, position, parity) plus
    accept/reject sinks; returns (size, evaluator, max reads of a variable on a path)."""
    order = list(range(g.n))
    stars = [[i for i in range(g.m) if g.star[v] >> i & 1] for v in order]
    size = sum(2 * len(s) for s in stars) + 2

    def evaluate(alpha):
        reads = [0] * g.m
        for v, s in zip(order, stars):
            parity = 0
            for i in s:
                reads[i] += 1
                parity ^= alpha >> i & 1
            if parity != (odd_even >> v & 1):
                return False, max(reads)
        return True, max(reads)

    return size, evaluate


def read_two_check(g: Graph):
    even = 0b11                         # vertices 0 and 1 charged: even total, satisfiable
    size, evaluate = read_two_program(g, even)
    ok, worst = True, 0
    for alpha in range(1 << g.m):
        out, reads = evaluate(alpha)
        sat = all((popcount(alpha & g.star[v]) + (even >> v & 1)) % 2 == 0 for v in range(g.n))
        ok &= out == sat
        worst = max(worst, reads)
    return {"size": size, "correct_on_all_assignments": ok, "max_reads_per_variable": worst}


def run():
    rng = random.Random(20261020)
    checks, controls, failures = {}, {}, []
    for name, edges in GRAPHS.items():
        g = Graph(edges)
        odd = 1
        P, width = carving_proof(g, odd)
        fb, fs = faithful(P)
        row = {"n": g.n, "m": g.m, "cvw": width,
               "carving": {"size": len(P.reachable()), "valid": P.valid(), "faithful_violations": fb, "steps_checked": fs,
                           **walk_stats(P)}}
        dps = []
        for _ in range(3):
            order = list(range(g.m))
            rng.shuffle(order)
            D = dp_proof(g, odd, order)
            db, ds = faithful(D)
            dps.append({"size": len(D.reachable()), "valid": D.valid(), "faithful_violations": db, "steps_checked": ds,
                        **walk_stats(D)})
        row["davis_putnam"] = dps
        row["read_two_program"] = read_two_check(g)
        checks[name] = row
        for label, s in [("carving", row["carving"])] + [(f"davis_putnam[{i}]", d) for i, d in enumerate(dps)]:
            if not (s["valid"] and s["faithful_violations"] == 0 and s["regions_never_grow"]
                    and s["history_nonuniform_prefixes"] == 0 and s["nonuniform_nodes"] == 0 and s["passing_within_2^-fd"]):
                failures.append(f"{name} {label}: faithful refutation check failed")
        r2 = row["read_two_program"]
        if not (r2["correct_on_all_assignments"] and r2["max_reads_per_variable"] <= 2):
            failures.append(f"{name}: read-2 program check failed")
        if name in ("prism", "cube", "grid3x3", "petersen"):
            found = None
            for y in range(g.m):
                for z in range(g.m):
                    if y == z:
                        continue
                    F = forgetting_proof(g, odd, y, z)
                    if F is None or not F.valid():
                        continue
                    fb, _ = faithful(F)
                    st = walk_stats(F)
                    if fb and st["history_nonuniform_prefixes"]:
                        found = {"y": y, "z": z, "size": len(F.reachable()), "valid": True, "faithful_violations": fb,
                                 **st}
                        break
                if found:
                    break
            controls[name] = found
            if not found:
                failures.append(f"control {name}: no forgetting refutation with a non-uniform hole posterior")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
