"""Read-out for DISTANCE-ORDER-20261117-001B-E001 (frozen before running).

b1 the not-all-equal thread, n = 30; b2 a chain of 15 knots sharing one
distinction (n = 31); b3 the six-regular weave W(L), L = 6, 9 and 12, all
exact (frontier programme at 6, transfer matrices modulo five primes joined by
the Chinese remainder theorem at 9 and 12); b4 the threshold line, n = 10
(control); b5 every not-all-equal relation on n = 4, 5, 6 (exploratory).

For each base, for the disagreement count d: P1 (built from unit steps), the
strict betweenness triples among distinctions, the gap graph (is it a path, are
its gaps equal), the longest base-point chain (with o; with flips, with and
without the start's own flip); for steps apart: P1; for tau = -log_3 |1 - 2d/N|:
its largest difference from steps apart and whether it is additive along the
base.  Bond distance by brute force on b1 at n = 10 and b2 at four knots.
Writes artifacts/.../results.json.

    .venv/bin/python -B run.py
"""

import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import order as O  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "DISTANCE-ORDER-20261117-001B", "DISTANCE-ORDER-20261117-001B-E001_order")
DI = os.path.join(ROOT, "experiments", "DISTANCE-INFO-20261117-001A", "DISTANCE-INFO-20261117-001A-E001_tables")


def states(n, knots):
    return [s for s in range(1 << n) if all(tuple((s >> u) & 1 for u in t) not in ex for t, ex in knots)]


def bond_distance(n, sts, min_size=3):
    """Least bond size minus one for every pair (a bond: constrained, free after forgetting any one member)."""
    def proj(B):
        return {tuple((s >> i) & 1 for i in B) for s in sts}
    def is_bond(B):
        if len(proj(B)) == 1 << len(B):
            return False
        return all(len(proj(B[:i] + B[i + 1:])) == 1 << (len(B) - 1) for i in range(len(B)))
    bd = {}
    for u, v in itertools.combinations(range(n), 2):
        rest = [x for x in range(n) if x not in (u, v)]
        best = None
        for k in range(max(0, min_size - 2), n - 1):
            for extra in itertools.combinations(rest, k):
                if is_bond(tuple(sorted((u, v) + extra))):
                    best = k + 1
                    break
            if best is not None:
                break
        bd[(u, v)] = best if best is not None else math.inf
    return bd


def order_summary(D, nodes, flips=None):
    """flips: (n, E) with E the table on distinctions and flips (u + n the flip of u)."""
    nodes = list(nodes)
    gaps = O.gap_graph(D, nodes)
    gap_values = sorted({str(D[u][v]) for u, v in gaps})
    out = {"p1": O.p1(D, nodes), "between_triples": len(O.between_triples(D, nodes)),
           "gap_pairs": len(gaps), "all_pairs": len(nodes) * (len(nodes) - 1) // 2,
           "gap_graph_is_path": O.is_path(gaps, nodes), "distinct_gap_values": len(gap_values),
           "longest_chain": max(O.longest_chain(D, nodes, o) for o in nodes)}
    if flips is not None:
        n, E = flips
        allv = list(range(2 * n))
        out["with_flips_longest_chain"] = max(O.longest_chain(E, allv, o) for o in nodes)
        out["with_flips_longest_chain_without_own_flip"] = max(
            O.longest_chain(E, allv, o, exclude=(o + n,)) for o in nodes)
    return out


def tau_summary(N, d_of, steps, pairs):
    """tau against steps apart: largest |tau - steps|, and additivity tau(u,w) = tau(u,v) + tau(v,w)
    whenever v lies on a shortest route (steps(u,w) = steps(u,v) + steps(v,w))."""
    tau = {p: O.log_rate(N, d_of(*p)) for p in pairs}
    diffs = [abs(tau[p] - steps(*p)) for p in pairs if math.isfinite(tau[p])]
    by = {}
    for p in pairs:
        by.setdefault(steps(*p), []).append(tau[p])
    ks = sorted(by)
    mono = all(max(by[a]) < min(by[b]) for a, b in zip(ks, ks[1:]))
    return {"max_abs_tau_minus_steps": max(diffs) if diffs else None,
            "infinite_tau_pairs": sum(1 for p in pairs if not math.isfinite(tau[p])),
            "tau_equals_steps": bool(diffs) and max(diffs) < 1e-9 and all(math.isfinite(tau[p]) for p in pairs),
            "tau_increases_with_steps": mono,
            "tau_range_by_steps": {k: [min(by[k]), max(by[k])] for k in ks}}


def path_base(name, n, knots, bond_small):
    t = time.time()
    N, d = O.disagreement_table(n, knots)
    D = O.as_matrix(n, d)
    st = O.path_steps(n, knots)
    E = O.with_flips(n, N, D)
    pairs = list(itertools.combinations(range(n), 2))
    res = {"name": name, "n": n, "knots": len(knots), "N": str(N),
           "disagreement": order_summary(D, range(n), (n, E)),
           "steps": {"p1": O.p1(st, range(n))},
           "tau": tau_summary(N, lambda u, v: D[u][v], lambda u, v: st[u][v], pairs),
           "rate_from_0_by_steps": [[st[0][v], str(Fraction(D[0][v], N))] for v in range(1, n)],
           "rate_middle_by_steps": [[st[n // 2][v], str(Fraction(D[n // 2][v], N))] for v in range(n) if v != n // 2]}
    if bond_small is not None:
        m, kk = bond_small
        bd = bond_distance(m, states(m, kk))
        B = O.as_matrix(m, bd)
        stm = O.path_steps(m, kk)
        res["bond_small"] = {"n": m, "p1": O.p1(B, range(m)),
                             "equals_steps_plus_one": all(B[u][v] == stm[u][v] + 1 for u, v in itertools.combinations(range(m), 2)),
                             "between_triples": len(O.between_triples(B, range(m)))}
    res["seconds"] = round(time.time() - t, 1)
    return res


def weave_base(L):
    t = time.time()
    n = L * L
    if L <= 6:
        _, knots = O.weave_knots(L)
        N, d0 = O.disagreement_table(n, knots, [(0, v) for v in range(1, n)])
        d0 = {v: d0[(0, v)] for v in range(1, n)}
        method = "frontier programme"
    else:
        N, d0 = O.weave_transfer_crt(L)
        method = "transfer matrices modulo five primes, Chinese remainder"
    d0[0] = 0
    def tr(u, v):
        return ((v % L) - (u % L)) % L + L * (((v // L) - (u // L)) % L)
    D = [[d0[tr(u, v)] for v in range(n)] for u in range(n)]
    E = [[0] * (2 * n) for _ in range(2 * n)]
    for u in range(n):
        for v in range(n):
            E[u][v] = E[u + n][v + n] = D[u][v]
            E[u][v + n] = E[u + n][v] = N - D[u][v]
    allv = list(range(2 * n))
    gaps = O.gap_graph(D, range(n))
    res = {"name": f"weave L={L}", "n": n, "method": method, "N": str(N),
           "disagreement": {"p1": O.p1(D, range(n)), "between_triples": len(O.between_triples(D, range(n))),
                            "gap_pairs": len(gaps), "all_pairs": n * (n - 1) // 2,
                            "gap_graph_is_path": O.is_path(gaps, range(n)),
                            "longest_chain": O.longest_chain(D, range(n), 0),
                            "with_flips_longest_chain": O.longest_chain(E, allv, 0),
                            "with_flips_longest_chain_without_own_flip": O.longest_chain(E, allv, 0, exclude=(n,))}}
    steps = lambda u, v: O.weave_steps(L, u, v)
    res["steps"] = {"p1": O.p1([[steps(u, v) for v in range(n)] for u in range(n)], range(n))}
    res["tau"] = tau_summary(N, lambda u, v: D[u][v], steps, [(0, v) for v in range(1, n)])
    prof = {}
    for v in range(1, n):
        prof.setdefault(steps(0, v), set()).add(str(Fraction(d0[v], N)))
    res["rate_by_steps"] = {k: sorted(vs, key=lambda x: Fraction(x)) for k, vs in sorted(prof.items())}
    res["rate_along_line"] = [[i, str(Fraction(d0[i % L], N)), float(Fraction(d0[i % L], N))] for i in range(1, L)]
    res["seconds"] = round(time.time() - t, 1)
    return res


def census(n):
    sys.path.insert(0, DI)
    import tables as T
    rels = sorted(T.distinct_relations(n))
    tally = {"relations": len(rels), "p1": 0, "p1_nonconstant": 0, "with_between": 0, "gap_path": 0,
             "chain_state_bound_holds": True, "examples_between": [], "distinct_tau_tables_with_N": 0}
    seen_tau = set()
    for r in rels:
        sts = T.states_of(n, r)
        N = len(sts)
        D = [[sum(((s >> u) ^ (s >> v)) & 1 for s in sts) for v in range(n)] for u in range(n)]
        nodes = list(range(n))
        vals = {D[u][v] for u in nodes for v in nodes if u != v}
        if O.p1(D, nodes)[0]:
            tally["p1"] += 1
            if len(vals) > 1:
                tally["p1_nonconstant"] += 1
        bt = O.between_triples(D, nodes)
        if bt:
            tally["with_between"] += 1
            if len(tally["examples_between"]) < 5:
                tally["examples_between"].append({"N": N, "states": sts, "triples": bt[:3]})
        if O.is_path(O.gap_graph(D, nodes), nodes):
            tally["gap_path"] += 1
        # chains cost states: a chain of m distinctions allows at most 2m patterns on them
        for o in nodes:
            for chain in chains_from(D, nodes, o):
                pats = {tuple((s >> x) & 1 for x in chain) for s in sts}
                if len(pats) > 2 * len(chain):
                    tally["chain_state_bound_holds"] = False
        seen_tau.add((N, tuple(abs(N - 2 * D[u][v]) for u, v in itertools.combinations(nodes, 2))))
    tally["distinct_tau_tables_with_N"] = len(seen_tau)
    return tally


def chains_from(D, nodes, o):
    """Every maximal chain o, v1, ..., vk of the base-point order from o (small n only)."""
    others = [x for x in nodes if x != o and D[o][x] > 0]
    below = {w: [v for v in others if v != w and D[o][v] < D[o][w] and D[v][w] > 0 and D[o][w] == D[o][v] + D[v][w]]
             for w in others}
    out = []
    def grow(seq):
        top = seq[-1]
        ups = [w for w in others if top in below[w] or (top == o and w not in seq)]
        ups = [w for w in ups if all(x == o or x in below[w] for x in seq)]
        if not ups:
            out.append(seq)
            return
        for w in ups:
            grow(seq + [w])
    if others:
        grow([o])
    return [c for c in out if len(c) >= 3]


def main():
    os.makedirs(OUT, exist_ok=True)
    results = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    results["b4_threshold_line"] = path_base("threshold line", *O.threshold_line(10), None)
    results["b1_thread"] = path_base("thread", *O.thread(30), O.thread(10))
    results["b2_chain"] = path_base("chain", *O.chain(15), O.chain(4))
    results["b3_weave"] = [weave_base(L) for L in (6, 9, 12)]
    results["b5_census"] = {n: census(n) for n in (4, 5, 6)}
    results["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), results["started"], results["finished"])


if __name__ == "__main__":
    main()
