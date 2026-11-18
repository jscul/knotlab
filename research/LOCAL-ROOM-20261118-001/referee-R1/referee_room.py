"""Referee R1 for LOCAL-ROOM-20261118-001 (own code; the study's locallib.py and STATE-RULES' rules.py are not imported).

  ../../../.venv/bin/python -B referee_room.py <part> > referee_room_<part>.json      (from this directory)

Semantics (the referee's CUBE-DOUBLING-R1 code): states as ints over n bits, B(x, y, z) forbids x = z != y, a step adds p = n with
one to three knots on p and two old distinctions, A99 (every old state extends, p constrained, not a copy).  The reach limit r: a
knot's old pair may differ on at most r splits (disagreement count at most 2r).  LF3(r) takes the fewest states, uniform over the
distinct extensions (the study's weighting).  The number of orders is the referee's KNOT-CAP-R1 `measure` (lambda by Eppstein's
matching, k the crossing graph's colour count).

Parts:
  r23     R2 under every tie rule: every class reachable by LF3(2) and LF3(3) from one knot and from the 2 x 2 pattern, to n = 33
          (classes as orientation sets up to the cube's symmetries); is Q_d the only class at 4, 8, 16, 32?  And R2's proof step
          "for s >= 3 only subdivisions are allowed": the cheapest extensions of Q_3 and Q_4 under r = 2, sorted into subdivisions
          and pendants.
  r1      LF3(1) exactly (labelled bases merged by isomorphism of their state sets) to n = 11 from one knot and to n = 10 from the
          2 x 2 pattern: the distribution of kinds and of lambda, against the study's; no step free (R1).
  runs1   300 seeded LF3(1) runs from each start to n = 20: does any run change kind after n = 5; in the two-order runs, the two
          chains' lengths from the crossing graph's two colours and from a maximum matching, and the crossings.
  class   the class law, written from the note's words: 200 seeded runs from the 2 x 2 pattern to n = 30; two orders at every step,
          stalls, a full grid (a + 1)(b + 1) = n at some n > 9 in every run, and whether a new split is ever added before the grid
          is full.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CUBE-DOUBLING-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
import referee_cube as RC  # noqa: E402  (the referee's CUBE-DOUBLING-R1 semantics: allowed, extend, cols, admitted, canon)
import referee_cap as KC  # noqa: E402  (the referee's KNOT-CAP-R1 measure)

pc = RC.pc


def disagree(st, u, v):
    return sum(((s >> u) ^ (s >> v)) & 1 for s in st)


def knot_values(st, n, r):
    O, Z, full = RC.cols(st, n)
    p = n
    out = []
    for u, v in itertools.combinations(range(n), 2):
        if r is not None and disagree(st, u, v) > 2 * r:
            continue
        out.append(((u, p, v), full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])))
        out.append(((u, v, p), full ^ (Z[u] & O[v]), full ^ (O[u] & Z[v])))
        out.append(((v, u, p), full ^ (Z[v] & O[u]), full ^ (O[v] & Z[u])))
    return out, O, Z, full


def extensions(st, n, r):
    """Every admitted extension with 1..3 knots within reach r, as packed (a0, a1), and the least cost."""
    N = len(st)
    kv, O, Z, full = knot_values(st, n, r)
    if not kv:
        return None, []
    if 2 * N <= 62:
        vals = np.unique(np.array([a0 | (a1 << N) for _, a0, a1 in kv], dtype=np.uint64))
        reach = set(int(x) for x in vals)
        frontier = vals
        for _ in range(2):
            new = set()
            step = max(1, 4_000_000 // len(vals))
            for i in range(0, len(frontier), step):
                new.update(int(x) for x in np.unique((frontier[i:i + step, None] & vals[None, :]).ravel()))
            frontier = np.array(sorted(new - reach), dtype=np.uint64)
            reach |= new
    else:                                                # wide masks (more than 31 states): plain Python integers
        vals = sorted({a0 | (a1 << N) for _, a0, a1 in kv})
        reach = set(vals)
        frontier = list(vals)
        for _ in range(2):
            new = {x & y for x in frontier for y in vals}
            frontier = list(new - reach)
            reach |= new
    mask = (1 << N) - 1
    adm = [(x & mask, x >> N) for x in reach if RC.admitted(x & mask, x >> N, O, Z, full, N)]
    if not adm:
        return None, []
    low = min(pc(a0) + pc(a1) for a0, a1 in adm)
    return low - N, [(a0, a1) for a0, a1 in adm if pc(a0) + pc(a1) == low]


def apply(st, n, a0, a1):
    return tuple(RC.apply(st, n, a0, a1))


def kind(st, n):
    m = KC.measure(st, n)
    if m["lam"] == 1:
        return "a line"
    if m["crossings"] == 0:
        return "a branching tree"
    if m["k"] == 2 and m["lam"] == 2:
        return "two orders"
    return f"{m['lam']} orders"


SEEDS = {"one knot": (3, tuple(sorted(s for s in range(8) if RC.allowed(s, 3, [(0, 1, 2)])))),
         "2x2": (4, tuple(sorted(RC.cube(2)[0])))}


def part_r23():
    out = {}
    for r in (2, 3):
        for start, (n, st) in SEEDS.items():
            dist = {RC.canon(list(st), n): [st, Fraction(1)]}
            rows = []
            while True:
                lam = Counter()
                cube = 0
                for key, (S, p) in dist.items():
                    lam[KC.measure(S, n)["lam"]] += p
                d = n.bit_length() - 1
                only_cube = (n == 1 << d) and all(key[0] == d for key in dist)
                rows.append({"n": n, "classes": len(dist), "lambda": {str(k): str(v) for k, v in sorted(lam.items())},
                             "Q_d_only_class": only_cube if n == 1 << d else None})
                if n >= 33:
                    break
                new = {}
                for key, (S, p) in dist.items():
                    cost, top = extensions(list(S), n, r)
                    exts = sorted(set(apply(S, n, a0, a1) for a0, a1 in top))
                    for e in exts:
                        k2 = RC.canon(list(e), n + 1)
                        if k2 not in new:
                            new[k2] = [e, Fraction(0)]
                        new[k2][1] += p / len(exts)
                dist = new
                n += 1
            out[f"r={r}, {start}"] = rows
            print("r23", r, start, json.dumps([(x["n"], x["classes"], x["Q_d_only_class"]) for x in rows if x["Q_d_only_class"] is not None]),
                  file=sys.stderr, flush=True)
    # R2's proof step: under r = 2, are pendants among the cheapest extensions of Q_3 and Q_4?
    pend = {}
    for s in (3, 4):
        st, n = RC.cube(s)
        cost, top = extensions(st, n, 2)
        kinds = Counter("pendant (the constants double)" if (a0 & a1) & 1 else "subdivision" for a0, a1 in top)
        pend[s] = {"least_cost": cost, "extensions": len(top), "kinds": dict(kinds)}
        print("r23 pendants", s, json.dumps(pend[s]), file=sys.stderr, flush=True)
    out["cheapest_extensions_of_Q_s_under_r=2"] = pend
    return out


def incidence_graph(st, n):
    G = nx.Graph()
    for u in range(n):
        G.add_node(("d", u), t="d")
    for s in st:
        G.add_node(("s", s), t="s")
        for u in range(n):
            if (s >> u) & 1:
                G.add_edge(("s", s), ("d", u))
    return G


class Classes:
    """Bases merged up to renaming of distinctions, by WL hash and then VF2 on the distinction-state incidence."""

    def __init__(self):
        self.buckets = defaultdict(list)

    def key(self, st, n):
        G = incidence_graph(st, n)
        h = nx.weisfeiler_lehman_graph_hash(G, node_attr="t", iterations=4)
        for i, (G2, rep) in enumerate(self.buckets[h]):
            if nx.is_isomorphic(G, G2, node_match=lambda a, b: a["t"] == b["t"]):
                return (h, i), rep
        self.buckets[h].append((G, st))
        return (h, len(self.buckets[h]) - 1), st


def part_r1():
    out = {}
    for start, nmax in (("one knot", 11), ("2x2", 10)):
        n, st = SEEDS[start]
        C = Classes()
        k, rep = C.key(st, n)
        dist = {k: [rep, Fraction(1)]}
        rows = []
        free_steps = 0
        while True:
            kinds = Counter()
            lam = Counter()
            Ns = set()
            for key, (S, p) in dist.items():
                kinds[kind(S, n)] += p
                lam[KC.measure(S, n)["lam"]] += p
                Ns.add(len(S))
            rows.append({"n": n, "classes": len(dist), "states": sorted(Ns), "kinds": {a: str(b) for a, b in sorted(kinds.items())},
                         "kinds_float": {a: round(float(b), 6) for a, b in sorted(kinds.items())}})
            print("r1", start, json.dumps({x: rows[-1][x] for x in ("n", "classes", "states", "kinds_float")}), file=sys.stderr, flush=True)
            if n >= nmax:
                break
            C = Classes()
            new = {}
            for key, (S, p) in dist.items():
                cost, top = extensions(list(S), n, 1)
                free_steps += cost == 0
                exts = sorted(set(apply(S, n, a0, a1) for a0, a1 in top))
                for e in exts:
                    k2, rep = C.key(e, n + 1)
                    if k2 not in new:
                        new[k2] = [rep, Fraction(0)]
                    new[k2][1] += p / len(exts)
            dist = new
            n += 1
        out[start] = {"levels": rows, "classes_with_a_free_step": free_steps}
    return out


def chains_by_colour(st, n):
    """The two chains as the crossing graph's colour classes, when it is connected; else None."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in st if s not in (0, full)})
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b))):
            G.add_edge(i, j)
    iso = [v for v in G if G.degree(v) == 0]
    H = G.subgraph([v for v in G if G.degree(v) > 0])
    if H.number_of_nodes() == 0 or not nx.is_connected(H) or not nx.is_bipartite(H):
        return None, len(iso)
    A, B = nx.bipartite.sets(H)
    return sorted([len(A), len(B)]), len(iso)


def part_runs1(runs=300, nmax=20):
    out = {}
    for start in SEEDS:
        changed = 0
        final = Counter()
        rows = defaultdict(list)
        for i in range(runs):
            rng = random.Random(f"R1:{start}:{i}")
            n, st = SEEDS[start]
            st = tuple(st)
            kinds = []
            trace = {}
            while n < nmax:
                cost, top = extensions(list(st), n, 1)
                exts = sorted(set(apply(st, n, a0, a1) for a0, a1 in top))
                st = rng.choice(exts)
                n += 1
                kinds.append(kind(st, n))
                if n in (6, 10, 14, 20):
                    trace[n] = st
            final[kinds[-1]] += 1
            changed += any(k != kinds[-1] for k, nn in zip(kinds, range(SEEDS[start][0] + 1, nmax + 1)) if nn >= 5)
            if kinds[-1] == "two orders":
                for nn, S in trace.items():
                    m = KC.measure(S, nn)
                    col, isolated = chains_by_colour(S, nn)
                    rows[nn].append({"crossings": m["crossings"], "splits": m["splits"], "colour_chains": col,
                                     "splits_crossing_nothing": isolated})
        summ = {}
        for nn, v in sorted(rows.items()):
            cols = [x["colour_chains"] for x in v if x["colour_chains"]]
            summ[nn] = {"runs": len(v), "splits": sorted({x["splits"] for x in v}),
                        "crossings_median": sorted(x["crossings"] for x in v)[len(v) // 2],
                        "crossings_range": [min(x["crossings"] for x in v), max(x["crossings"] for x in v)],
                        "connected_crossing_graph": len(cols),
                        "shorter_colour_class_mean": round(float(np.mean([c[0] for c in cols])), 3) if cols else None,
                        "shorter_colour_class_counts": dict(sorted(Counter(c[0] for c in cols).items())),
                        "crossings_at_most_3": sum(1 for x in v if x["crossings"] <= 3),
                        "splits_crossing_nothing_mean": round(float(np.mean([x["splits_crossing_nothing"] for x in v])), 3)}
        out[start] = {"runs": runs, "final_kinds": dict(final), "runs_changing_kind_after_n5": changed, "two_order_runs": summ}
        print("runs1", start, json.dumps(out[start]), file=sys.stderr, flush=True)
    return out


def splits_of(st, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in st if s not in (0, full)})


def part_class(runs=200, nmax=30):
    """The class law: each split carries a class (0 or 1); a knot's old pair may be separated only by splits of pairwise different
    classes; no step may make a split that is constant on the old distinctions (no pendant); a new split inherits the class of its
    restriction to the old distinctions.  From the 2 x 2 pattern, its two splits in the two classes."""
    res = Counter()
    full_after9 = 0
    early_new_split = 0
    full_by_n = Counter()
    balance = Counter()
    for i in range(runs):
        rng = random.Random(f"CLASS:{i}")
        n, st = SEEDS["2x2"]
        st = tuple(st)
        sp = splits_of(st, n)
        cls = {sp[0]: 0, sp[1]: 1}
        ok_two = True
        stalled = False
        saw_full_after9 = False
        for _ in range(nmax - n):
            full_old = (1 << n) - 1
            O, Z, full = RC.cols(st, n)

            def sep_ok(u, v):
                c = [cls[s] for s in splits_of(st, n) if ((s >> u) & 1) != ((s >> v) & 1)]
                return len(c) == len(set(c))
            N = len(st)
            kv = []
            for u, v in itertools.combinations(range(n), 2):
                if not sep_ok(u, v):
                    continue
                kv.append((full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])))
                kv.append((full ^ (Z[u] & O[v]), full ^ (O[u] & Z[v])))
                kv.append((full ^ (Z[v] & O[u]), full ^ (O[v] & Z[u])))
            vals = {a0 | (a1 << N) for a0, a1 in kv}
            allv = set(vals)
            for x, y in itertools.combinations_with_replacement(sorted(vals), 2):
                allv.add(x & y)
            two = set(allv)
            for x in two:
                for y in vals:
                    allv.add(x & y)
            cand = []
            for x in allv:
                a0, a1 = x & ((1 << N) - 1), x >> N
                if not RC.admitted(a0, a1, O, Z, full, N):
                    continue
                new = apply(st, n, a0, a1)
                if any(s not in (0, (1 << (n + 1)) - 1) and (s & full_old) in (0, full_old) for s in new):
                    continue                                 # a pendant
                cand.append((pc(a0) + pc(a1), new))
            if not cand:
                stalled = True
                break
            low = min(c for c, _ in cand)
            choices = sorted({e for c, e in cand if c == low})
            was_full = (Counter(cls.values())[0] + 1) * (Counter(cls.values())[1] + 1) == n
            st2 = rng.choice(choices)
            if low > N and not was_full:
                early_new_split += 1                          # a new split while the grid was not full
            newcls = {}
            for s in splits_of(st2, n + 1):
                newcls[s] = cls[min(s & full_old, full_old ^ (s & full_old))]
            st, n, cls = st2, n + 1, newcls
            m = KC.measure(st, n)
            ok_two &= m["k"] == 2 and m["lam"] == 2
            cnt = Counter(cls.values())
            if (cnt[0] + 1) * (cnt[1] + 1) == n:
                full_by_n[n] += 1
                if n > 9:
                    saw_full_after9 = True
        res["two orders at every step" if ok_two and not stalled else "not"] += 1
        res["stalled"] += stalled
        full_after9 += saw_full_after9
        cnt = Counter(cls.values())
        balance[str(tuple(sorted((cnt[0], cnt[1]))))] += 1
        if i % 20 == 0:
            print("class", i, dict(res), full_after9, early_new_split, file=sys.stderr, flush=True)
    return {"runs": runs, "tally": dict(res), "runs_with_a_full_grid_after_n9": full_after9,
            "new_splits_added_before_the_grid_was_full": early_new_split,
            "full_grids_by_n": {str(k): v for k, v in sorted(full_by_n.items())},
            "class_sizes_at_30_unordered": dict(balance)}


if __name__ == "__main__":
    part = sys.argv[1]
    res = {"r23": part_r23, "r1": part_r1, "runs1": part_runs1, "class": part_class}[part]()
    print(json.dumps(res, indent=1, default=str))
