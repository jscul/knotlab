"""Referee R1 for NEVER-NEST-20261118-001 (own code; the study's nnlib.py, run.py and melib.py are not imported).

  ../../../.venv/bin/python -B referee_nest.py <rule> <n0> <bracketing index> <seed> <nmax>      one run -> stdout JSON

Rules, written from the note's words, on the referee's own KF3 move enumeration (`referee_meet.options`, knot-local, irredundant,
1..3 knots) and its own order count (`referee_cap.measure`: lambda by Eppstein's matching, k the crossing graph's colours):
  NN   the fills (options that add no state) after which the base has two orders (k = lambda = 2), uniform over knot sets; if
       none, a subdivision: one knot B(u, p, v) on a co-knotted pair differing in exactly two states, uniform over the pairs.
  NNF  the same with every old pair allowed (not only co-knotted ones), uniform over distinct extensions.
Per step: the number of orders, whether the base is a full grid (crossing graph complete bipartite on parts a, b with
n = (a + 1)(b + 1)), whether the step was a fill or a subdivision; at the end the fill fraction on steps 21..40 and whether every
subdivision after the first full grid came at a full grid.
"""
import itertools
import json
import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_cap as KC  # noqa: E402


def two_orders(S, n):
    m = KC.measure(S, n)
    return m["k"] == 2 and m["lam"] == 2


def full_grid(S, n):
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            G.add_edge(i, j)
    if not nx.is_connected(G) or not nx.is_bipartite(G):
        return False, None
    A, B = nx.bipartite.sets(G)
    complete = G.number_of_edges() == len(A) * len(B)
    return complete and n == (len(A) + 1) * (len(B) + 1), (len(A), len(B))


def free_pairs(n):
    return frozenset(itertools.combinations(range(n), 2))


def step(rule, S, n, G, rng):
    pairs = G if rule == "NN" else free_pairs(n)
    cost, top = RM.options(S, n, pairs)
    fills = []
    if cost == 0:
        for q0, q1, ks in top:
            S2 = RM.extend(S, n, q0, q1)
            fills.append((S2, ks))
    keep = {}
    good = []
    for S2, ks in fills:
        if S2 not in keep:
            keep[S2] = two_orders(S2, n + 1)
        if keep[S2]:
            good.append((S2, ks))
    if good:
        if rule == "NNF":                                    # uniform over distinct extensions
            exts = sorted({S2 for S2, _ in good})
            S2 = rng.choice(exts)
            ks = next(k for s, k in good if s == S2)
        else:                                                # uniform over knot sets
            S2, ks = rng.choice(good)
        return S2, G | RM.pairs_of(ks), "fill"
    subs = [(u, v) for u, v in sorted(pairs) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
    if not subs:
        return None
    u, v = rng.choice(subs)
    k = (u, n, v)
    S2 = RM.RC.base(n + 1, [k]) if False else tuple(sorted(x for s in S for x in (s, s | (1 << n))
                                                            if RM.RC.ok_btw(x, u, n, v)))
    return S2, G | RM.pairs_of([k]), "sub"


def run(rule, n0, j, seed, nmax):
    T = tuple(RM.bracketings(0, n0 - 1)[j])
    rng = random.Random(f"{rule}:{n0}:{j}:{seed}")
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    trace = []
    while n < nmax:
        r = step(rule, S, n, G, rng)
        if r is None:
            trace.append({"n": n + 1, "stalled": True})
            break
        S, G, kind = r
        n += 1
        fg, parts = full_grid(S, n)
        trace.append({"n": n, "kind": kind, "two_orders": two_orders(S, n), "full_grid": fg, "parts": parts, "states": len(S)})
        print(rule, n0, j, seed, json.dumps(trace[-1]), file=sys.stderr, flush=True)
    after = [t for t in trace if t["n"] >= n0 + 2]
    first_full = next((i for i, t in enumerate(trace) if t.get("full_grid")), None)
    subs_after = [i for i, t in enumerate(trace) if t.get("kind") == "sub" and first_full is not None and i > first_full]
    at_full = all(trace[i - 1].get("full_grid") for i in subs_after)
    late = [t for t in trace if 21 <= t["n"] - n0 + 0 and t["n"] <= 40] if False else [t for t in trace if 21 <= t["n"] <= 40]
    return {"rule": rule, "n0": n0, "bracketing": T, "seed": seed, "nmax": nmax,
            "two_orders_at_every_step_after_the_first": all(t.get("two_orders") for t in after),
            "stalled": any(t.get("stalled") for t in trace),
            "first_full_grid_n": trace[first_full]["n"] if first_full is not None else None,
            "full_grid_ns": [t["n"] for t in trace if t.get("full_grid")],
            "every_subdivision_after_the_first_full_grid_came_at_a_full_grid": at_full,
            "subdivisions_before_the_first_full_grid": sum(1 for i, t in enumerate(trace) if t.get("kind") == "sub" and
                                                          (first_full is None or i < first_full)),
            "fill_fraction_n21_40": round(sum(1 for t in late if t.get("kind") == "fill") / max(1, len(late)), 3),
            "final_parts": trace[-1].get("parts")}


if __name__ == "__main__":
    rule, n0, j, seed, nmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    print(json.dumps(run(rule, n0, j, seed, nmax)))
