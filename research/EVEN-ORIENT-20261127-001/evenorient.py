"""evenorient.py: the smallest non-orientable even choices and the knots growth needs to make them
(EVEN-ORIENT-20261127-001; README.md, frozen predictions G, P1-P4).

A minimal strict choice is a set of failing pairs (x, y) of unheld values, each value in at most one pair, every pair of
knots a cross pair of an even number of them, and no proper sub-collection with that property. Its cycles a, c, b, d
(x held by a, b; y by c, d) are read as in the cross-pair study (A318). This script
  E  lists every labelled minimal choice covered twice on V knots (V <= 6, any size; V = 7, at most --e7 pairs);
  B  grows the built starts B1-B4 and the scaffold family of B1;
  X  grows the extension's starts (and a second sample) and lists every minimal strict birth choice at each closure;
  C  replays the census-start closures (birth and whole choices) against the cross-pair referee's counts.
    evenorient.py [--out DIR] [--second N] [--e7 7] [--probe]
"""
import argparse
import collections
import itertools
import json
import resource
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "CELL-SIGN-20261127-001"))
import cellsign as C  # noqa: E402  (cycles_of, commute_and_sign, orientable, separate, structure, steps)

forbid = C.forbid
ROUNDS, CAP = 10, 3000              # growth limits for built and extension starts
CENSUS_ROUNDS, CENSUS_CAP = 4, 40   # the cross-pair referee's limits for the census starts
SECOND_SEED = 20261200              # the second extension sample: seeds SECOND_SEED + n (the extension uses 20261126 + n)
WORD_CAP = 200_000                  # per closure; reaching it is reported as a cap


# ---------------------------------------------------------------- growth and eligibility

def history(start, rounds, cap, births=None):
    """grow to closure; births, when a list is given, receives (round, newborn, parents) for every recorded birth"""
    current = forbid.supports_of(start)
    stages = [current]
    while True:
        counts = collections.Counter(d for knot in current for d in knot)
        if all(c == 2 for c in counts.values()):
            return ("grown closed" if len(stages) > 1 else "initially closed"), stages
        new, status, made = forbid.grown(current, "parity", "ordinary")
        if status == "stalled":
            return "stalled", stages
        if len(stages) == rounds + 1:
            return "growing", stages
        if len(new) > cap:
            return "cut", stages
        if births is not None:
            births += [(len(stages), b["knot"], list(b["parents"])) for b in made]
        stages.append(new)
        current = new


def eligible(stages, whole):
    """holders of each distinction, and the failing-pair candidates: unheld pairs (four distinct holders); birth
    choices keep a pair only when one value had both holders by the round the other first appeared (A314)"""
    holders, first, second = collections.defaultdict(list), {}, {}
    old = 0
    for t, stage in enumerate(stages):
        for k in range(old, len(stage)):
            for d in stage[k]:
                holders[d].append(k)
                if d in first:
                    second[d] = t
                else:
                    first[d] = t
        old = len(stage)
    assert all(len(h) == 2 for h in holders.values())
    pairs = []
    for x, y in itertools.combinations(sorted(holders), 2):
        if len(set(holders[x]) | set(holders[y])) < 4:
            continue
        if not whole and min(second[x], second[y]) > max(first[x], first[y]):
            continue
        pairs.append((x, y))
    return {d: tuple(h) for d, h in holders.items()}, pairs


def doubled_between_start_knots(supports, start_size):
    """item 3: every pair of knots sharing two distinctions is a pair of start knots"""
    shared = collections.Counter()
    for d in {d for row in supports for d in row}:
        hs = tuple(sorted(i for i, row in enumerate(supports) if d in row))
        shared[hs] += 1
    return all(max(p) < start_size for p, k in shared.items() if k >= 2)


# ---------------------------------------------------------------- minimal strict words

def xor_zero(solver, lits, nxt):
    """lits sum to zero mod 2 (a chain of auxiliary sums)"""
    if len(lits) == 1:
        solver.add_clause([-lits[0]])
        return nxt
    acc = lits[0]
    for lit in lits[1:]:
        z = nxt
        nxt += 1
        solver.add_clause([-z, acc, lit])
        solver.add_clause([-z, -acc, -lit])
        solver.add_clause([z, -acc, lit])
        solver.add_clause([z, acc, -lit])
        acc = z
    solver.add_clause([-acc])
    return nxt


def circuit(chosen, cols):
    """the unique dependency among independent pivots and the first column they span: a circuit inside chosen"""
    piv = {}
    for i in chosen:
        v, used = cols[i], 1 << i
        while v:
            h = v.bit_length() - 1
            if h not in piv:
                piv[h] = (v, used)
                break
            v ^= piv[h][0]
            used ^= piv[h][1]
        else:
            return [j for j in range(len(cols)) if used >> j & 1]
    raise AssertionError("a commuting choice without a dependency")


def minimal_words(holders, pairs, cap=WORD_CAP):
    """every minimal strict commuting choice among the candidate pairs; returns (words, capped)"""
    index, cols = {}, []
    at_val = collections.defaultdict(list)
    for i, (x, y) in enumerate(pairs):
        c = 0
        for u in holders[x]:
            for v in holders[y]:
                c ^= 1 << index.setdefault(frozenset((u, v)), len(index))
        cols.append(c)
        at_val[x].append(i + 1)
        at_val[y].append(i + 1)
    if not pairs:
        return [], False
    at_pair = collections.defaultdict(list)
    for i, c in enumerate(cols):
        for b in range(c.bit_length()):
            if c >> b & 1:
                at_pair[b].append(i + 1)
    words = []
    with Solver(name="minicard") as s:
        nxt = len(pairs) + 1
        for lits in at_pair.values():
            nxt = xor_zero(s, lits, nxt)
        for lits in at_val.values():
            if len(lits) > 1:
                s.add_atmost(lits, 1)
        s.add_clause(list(range(1, len(pairs) + 1)))
        while s.solve():
            chosen = [v - 1 for v in s.get_model() if 0 < v <= len(pairs)]
            circ = circuit(chosen, cols)
            words.append([pairs[i] for i in circ])
            if len(words) >= cap:
                return words, True
            s.add_clause([-(i + 1) for i in circ])
    return words, False


# ---------------------------------------------------------------- what a choice is

def describe(holders, F, start_size=None):
    ok, sign = C.commute_and_sign(holders, F)
    assert ok
    cycles = C.cycles_of(holders, F)
    m, euler, one, bip = C.structure(cycles)
    two = all(k == 2 for k in m.values())
    try:
        orient = C.orientable(cycles, m)
    except C.Unsettled:
        orient = None                       # an undecided search; gate (iv) fails on any
    sep = C.separate(cycles) if two else None
    sep_euler = C.structure(sep)[1] if two else None
    diag = collections.Counter(frozenset(holders[v]) for p in F for v in p)
    doubled = [tuple(sorted(p)) for p, k in diag.items() if k >= 2]
    knots = sorted({u for c in cycles for u in c})
    on_doubled = {u for p in doubled for u in p}
    out = {"pairs": len(F), "sign": sign, "orientable": orient, "covered twice": two, "coverage": max(m.values()),
           "knots": len(knots), "Euler count": euler, "separated Euler count": sep_euler, "one cycle at every knot": one,
           "two-colourable": bip, "doubled pairs": len(doubled), "knots on a doubled pair": len(on_doubled),
           "every knot on a doubled pair": set(knots) <= on_doubled}
    if two:
        out["same-order parity"] = same_order_parity(cycles)
    if start_size is not None:
        out["start knots"] = sum(1 for u in knots if u < start_size)
        out["newborns"] = sum(1 for u in knots if u >= start_size)
    return out, cycles


def same_order_parity(cycles):
    """item 2(b) of the cross-pair study: with every cross pair in two cycles, the number listed the same way, mod 2"""
    seen = {}
    total = 0
    for c in cycles:
        for u, v in C.steps(c):
            e = frozenset((u, v))
            if e in seen:
                total += seen[e] == (u, v)
            else:
                seen[e] = (u, v)
    return total % 2


# ---------------------------------------------------------------- E: abstract choices covered twice

def all_cycles(V):
    out = []
    for p0, p1, p2, p3 in itertools.combinations(range(V), 4):
        for (a, b), (c, d) in (((p0, p1), (p2, p3)), ((p0, p2), (p1, p3)), ((p0, p3), (p1, p2))):
            out.append((a, c, b, d))
    return out


def abstract(V, fmax):
    """every labelled connected set of at least three distinct cycles on exactly V knots, each pair of knots in zero or
    two of them, with at most fmax cycles; grown from its least cycle through its least open cross pair"""
    cyc = all_cycles(V)
    edges = [[frozenset(e) for e in C.steps(c)] for c in cyc]
    containing = collections.defaultdict(list)
    for i, es in enumerate(edges):
        for e in es:
            containing[e].append(i)
    order = {e: k for k, e in enumerate(sorted(containing, key=lambda e: tuple(sorted(e))))}
    cover = collections.Counter()
    open_edges = set()
    chosen = []
    found = []

    def add(j, sgn):
        for e in edges[j]:
            cover[e] += sgn
            if cover[e] == 1:
                open_edges.add(e)
            else:
                open_edges.discard(e)

    def grow(c0):
        if not open_edges:
            if len(chosen) >= 3 and len({u for j in chosen for u in cyc[j]}) == V:
                found.append([cyc[j] for j in chosen])
            return
        if len(chosen) >= fmax:
            return
        e = min(open_edges, key=order.__getitem__)
        for j in containing[e]:
            if j <= c0 or j in chosen or any(cover[f] >= 2 for f in edges[j]):
                continue
            chosen.append(j)
            add(j, 1)
            grow(c0)
            add(j, -1)
            chosen.pop()

    for c0 in range(len(cyc)):
        chosen.append(c0)
        add(c0, 1)
        grow(c0)
        add(c0, -1)
        chosen.pop()
    return found


def from_cells(cells):
    """the pattern of a set of cycles: each cycle's two values new distinctions held by its opposite knots"""
    holders, F = {}, []
    for a, c, b, d in cells:
        x, y = len(holders), len(holders) + 1
        holders[x], holders[y] = (a, b), (c, d)
        F.append((x, y))
    return holders, F


def canonical(cells):
    """a relabelling-invariant key: a hash of the knot, cross-pair and cycle incidence graph, refined below"""
    G = nx.Graph()
    for i, c in enumerate(cells):
        G.add_node(("c", i), t="c")
        for u, v in C.steps(c):
            e = ("e",) + tuple(sorted((u, v)))
            G.add_node(e, t="e")
            G.add_edge(("c", i), e)
            for w in (u, v):
                G.add_node(("k", w), t="k")
                G.add_edge(e, ("k", w))
    return G, nx.weisfeiler_lehman_graph_hash(G, node_attr="t", iterations=4)


def classes(structs):
    """group labelled structures up to relabelling (hash buckets, then exact isomorphism)"""
    buckets = collections.defaultdict(list)
    for cells in structs:
        G, h = canonical(cells)
        for rep in buckets[h]:
            if nx.is_isomorphic(rep[0], G, node_match=lambda a, b: a["t"] == b["t"]):
                rep[2] += 1
                break
        else:
            buckets[h].append([G, cells, 1])
    return [(cells, n) for reps in buckets.values() for _, cells, n in reps]


def fast(cells):
    """sign (interleaving in index order), same-order parity, orientability, separated Euler count, two-colourable
    cross pairs and doubled diagonals of a structure covered twice, without the general machinery"""
    sign = 0
    for a, c, b, d in cells:
        x1, x2 = sorted((a, b))
        y1, y2 = sorted((c, d))
        sign ^= int(x1 < y1 < x2 < y2 or y1 < x1 < y2 < x2)
    m = collections.Counter(frozenset(e) for c in cells for e in C.steps(c))
    assert all(k == 2 for k in m.values())
    orient = C.orientable(cells, m)
    parent = {}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    pieces = 0
    knots = {u for c in cells for u in c}
    for v in knots:
        parent.clear()
        for c in cells:
            if v in c:
                j = c.index(v)
                p, q = (v, c[(j - 1) % 4]), (v, c[(j + 1) % 4])
                for r in (p, q):
                    parent.setdefault(r, r)
                parent[find(p)] = find(q)
        pieces += len({find(r) for r in parent})
    adj = collections.defaultdict(set)
    for e in m:
        u, v = tuple(e)
        adj[u].add(v)
        adj[v].add(u)
    colour, bip = {}, True
    for s0 in knots:
        if s0 in colour:
            continue
        colour[s0] = 0
        stack = [s0]
        while stack and bip:
            u = stack.pop()
            for w in adj[u]:
                if w not in colour:
                    colour[w] = colour[u] ^ 1
                    stack.append(w)
                elif colour[w] == colour[u]:
                    bip = False
    diag = collections.Counter(frozenset(p) for a, c, b, d in cells for p in ((a, b), (c, d)))
    on = {u for p, k in diag.items() if k >= 2 for u in p}
    return {"pairs": len(cells), "knots": len(knots), "sign": sign, "same-order parity": same_order_parity(cells),
            "orientable": orient, "separated Euler count": pieces - len(m) + len(cells), "two-colourable": bip,
            "doubled pairs": sum(1 for k in diag.values() if k >= 2), "every knot on a doubled pair": knots <= on}


SEVEN_CONTROL = [(0, 3, 1, 4), (0, 5, 1, 6), (0, 3, 2, 5), (0, 4, 2, 6), (1, 3, 2, 6), (1, 4, 2, 5)]   # kind (a)
# kind (c), the reviewer's six-knot Klein bottle with one doubled pair ({1, 4}), labelled so that knot 5 is the one a
# built start leaves out: its partners 0, 1 and 3 all meet knot 4
KLEIN_C = [(5, 3, 1, 4), (5, 4, 3, 1), (5, 1, 0, 3), (2, 0, 3, 4), (2, 4, 0, 1), (2, 1, 4, 0)]


def same_structure(a, b):
    Ga, ha = canonical(a)
    Gb, hb = canonical(b)
    return ha == hb and nx.is_isomorphic(Ga, Gb, node_match=lambda p, q: p["t"] == q["t"])


def kind(cells):
    """which six-pair kind a set of cycles is: 'a', 'b', 'c' or None"""
    if len(cells) != 6:
        return None
    for name, ref in (("a", SEVEN_CONTROL), ("b", KLEIN_SIX), ("c", KLEIN_C)):
        if same_structure(cells, ref):
            return name
    return None


def orient_brute(cells):
    """an independent orientability test: some reversal of the cycles lists every cross pair equally often each way"""
    m = collections.Counter(frozenset(e) for c in cells for e in C.steps(c))
    for mask in range(1 << (len(cells) - 1)):
        fwd = collections.Counter()
        for i, c in enumerate(cells):
            for u, v in C.steps(C.reverse(c) if mask >> i & 1 else c):
                fwd[frozenset((u, v))] += u < v
        if all(2 * fwd[e] == k for e, k in m.items()):
            return True
    return False


def run_abstract(e7):
    rows, special = [], []
    seen_control = seen_klein = seen_c = False
    for V, fmax in [(4, 99), (5, 99), (6, 99), (7, e7)]:
        t = time.time()
        structs = abstract(V, fmax)
        tally = collections.Counter()
        odd_noneven, mismatch = [], 0
        for cells in structs:
            f = fast(cells)
            mismatch += f["sign"] != f["same-order parity"]
            key = (V, f["pairs"], f["separated Euler count"], f["orientable"], f["sign"], f["doubled pairs"] > 0,
                   f["every knot on a doubled pair"], f["two-colourable"])
            tally[key] += 1
            if not f["orientable"] and not f["sign"]:
                odd_noneven.append(cells)
        cls = classes(odd_noneven)
        for cells, n in cls:
            f = fast(cells)
            h, F = from_cells(cells)
            g, _ = describe(h, F)          # the general machinery agrees with the fast one
            agree = all(g[k] == f[k] for k in ("sign", "orientable", "separated Euler count", "two-colourable"))
            agree = agree and orient_brute(cells) == f["orientable"]
            special.append({"knots": V, "labelled copies": n, "cycles": cells, "general agrees": agree,
                            "kind": kind(cells), **f})
            seen_control |= V == 7 and same_structure(cells, SEVEN_CONTROL)
            seen_klein |= V == 6 and same_structure(cells, KLEIN_SIX)
            seen_c |= V == 6 and same_structure(cells, KLEIN_C)
        rows.append({"knots": V, "max pairs": fmax if fmax < 99 else None, "labelled structures": len(structs),
                     "seconds": round(time.time() - t, 1), "sign differs from same-order parity": mismatch,
                     "tally": [list(k) + [v] for k, v in sorted(tally.items(), key=str)],
                     "non-orientable even classes": len(cls)})
        print(f"E V={V}: {len(structs)} structures, {time.time() - t:.1f}s", flush=True)
    return rows, special, {"kind (a), the seven-knot control, found": seen_control,
                           "kind (b) found": seen_klein, "kind (c) found": seen_c}


# ---------------------------------------------------------------- B, X, C: grown closures

KLEIN_SIX = [(0, 1, 2, 5), (0, 1, 4, 3), (0, 3, 2, 4), (0, 4, 3, 5), (1, 2, 3, 5), (1, 4, 2, 5)]


def b1_holding():
    """two rings of three knots (0, 1, 2 and 3, 4, 5), knot i sharing two distinctions with knot i + 3"""
    return [(0, 1, 1), (0, 2, 1), (1, 2, 1), (3, 4, 1), (3, 5, 1), (4, 5, 1), (0, 3, 2), (1, 4, 2), (2, 5, 2)]


def b1(loose):
    return (6, tuple(sorted(b1_holding())), tuple(loose))


def b2():
    """knots 0, 1, 2 sharing two distinctions pairwise; a ring 3, 4, 5 each with one loose distinction; 0 meets 3"""
    mult = [(0, 1, 2), (0, 2, 2), (1, 2, 2), (3, 4, 1), (3, 5, 1), (4, 5, 1), (0, 3, 1)]
    return (6, tuple(sorted(mult)), (0, 0, 0, 1, 1, 1))


C_LESS_FIVE = [(0, 1, 1), (0, 2, 1), (0, 4, 1), (1, 3, 1), (1, 4, 2), (2, 3, 1), (2, 4, 1), (3, 4, 1)]


def b3():
    """kind (c) without knot 5: its three distinctions left loose at knots 0, 1 and 3, all of which meet knot 4
    (twelve distinctions on five knots, the census's bounds)"""
    return (5, tuple(sorted(C_LESS_FIVE)), (1, 1, 0, 1, 0))


def b4():
    """B3 with one more loose distinction, at knot 4 (thirteen distinctions)"""
    return (5, tuple(sorted(C_LESS_FIVE)), (1, 1, 0, 1, 1))


def closure_rows(start, rounds, cap, whole_too=False, births=None):
    outcome, stages = history(start, rounds, cap, births)
    row = {"outcome": outcome, "rounds": len(stages) - 1, "start knots": start[0]}
    if outcome != "grown closed":
        return row, []
    sup = stages[-1]
    row["knots"] = len(sup)
    row["distinctions"] = len({d for r in sup for d in r})
    row["doubled only between start knots"] = doubled_between_start_knots(sup, start[0])
    found = []
    for whole in ((False, True) if whole_too else (False,)):
        holders, pairs = eligible(stages, whole)
        words, capped = minimal_words(holders, pairs)
        tally = collections.Counter()
        for F in words:
            f, cyc = describe(holders, F, start[0])
            tally[(f["pairs"], "odd" if f["sign"] else "even", f["orientable"])] += 1
            if not f["sign"] and not f["orientable"]:
                uses_birth = any(max(holders[v]) >= start[0] for p in F for v in p)
                found.append({"whole": whole, "failing pairs": F, "cycles": cyc, "birth value": uses_birth,
                              "kind": kind(cyc), **f})
        name = "whole" if whole else "birth"
        row[name] = {"candidates": len(pairs), "words": len(words), "capped": capped,
                     "tally": [list(k) + [v] for k, v in sorted(tally.items(), key=str)]}
    return row, found


def run_grown(population, starts, rounds, cap, whole_too, probe):
    rows, found = [], []
    t = time.time()
    for i, s in enumerate(starts):
        row, fnd = closure_rows(s, rounds, cap, whole_too)
        row["index"] = i
        rows.append(row)
        for f in fnd:
            f["index"] = i
        found += fnd
        if probe and i >= 300:
            break
    print(f"{population}: {len(rows)} starts, {sum(r['outcome'] == 'grown closed' for r in rows)} closures, "
          f"{time.time() - t:.1f}s", flush=True)
    return rows, found


def word_totals(rows, which="birth"):
    t = collections.Counter()
    for r in rows:
        for pairs, sign, orient, n in r.get(which, {}).get("tally", []):
            t[(sign, orient)] += n
    return t


def by_size(found, which_whole=False):
    t = collections.Counter()
    for f in found:
        if f["whole"] == which_whole:
            t[f["pairs"]] += 1
    return dict(sorted(t.items()))


def summarise(res, special, found_fixtures, b_rows, family, x_found, x2_found, c_found, a):
    g = {}
    # (i) the abstract choices
    small = [s for s in special if s["pairs"] <= 5]
    k5 = [k for r in res["E"] if r["knots"] == 5 for k in r["tally"] if k[2] == 0]
    g["E: no non-orientable even choice with at most five pairs"] = not small
    g["E: kinds (a), (b) and (c) found"] = all(found_fixtures.values())
    g["E: Euler count 0 on five knots occurs and is always orientable"] = bool(k5) and all(k[3] for k in k5)
    g["E: sign equals the same-order parity on every structure"] = all(
        r["sign differs from same-order parity"] == 0 for r in res["E"])
    g["E: the general machinery agrees on every class"] = all(s["general agrees"] for s in special)
    # (ii) item 3 at every closure
    closures = [r for r in res["X"] + res["X2"] + res["C"] if r["outcome"] == "grown closed"]
    closures += [r for r in list(b_rows.values()) + family if r.get("outcome") == "grown closed"]
    g["item 3: doubled meetings only between start knots"] = all(r["doubled only between start knots"]
                                                                  for r in closures)
    # (iii) the census-start closures against the referee's replay
    ct = word_totals(res["C"])
    g["C: 6,534 minimal strict even birth choices, all orientable"] = (ct[("even", True)], ct[("even", False)]) == (
        6534, 0)
    g["C: 4,803 minimal strict odd birth choices, none orientable"] = (ct[("odd", False)], ct[("odd", True)]) == (
        4803, 0)
    g["C: 1,819 closures"] = sum(r["outcome"] == "grown closed" for r in res["C"]) == 1819
    # (iv) every listing finished
    g["every listing finished below the cap"] = not any(
        r.get(w, {}).get("capped") for r in closures for w in ("birth", "whole"))
    g["every orientation decided"] = not any(
        k[2] is None for r in closures for w in ("birth", "whole") for k in r.get(w, {}).get("tally", []))
    g["all gates"] = all(g.values())
    # predictions
    p1_scope = [s for s in special if s["knots"] <= 6 or s["pairs"] <= 6]
    p1 = all(s["doubled pairs"] > 0 for s in p1_scope)
    B1, B2, B3, B4 = (b_rows[k] for k in ("B1", "B2", "B3", "B4"))
    p2_b1 = B1["outcome"] == "grown closed" and any(f["kind"] == "b" for f in B1["non-orientable even"])
    p2_b2 = B2["outcome"] == "grown closed" and any(
        f["kind"] == "a" and f["birth value"] for f in B2["non-orientable even"])
    p2_b3 = not any(sorted(par) == [0, 1, 3] for _, _, par in B3["births"])
    x_birth = [f for f in x_found if not f["whole"]]
    summary = {
        "P1": {"holds": p1, "classes in scope": len(p1_scope),
               "classes": [{k: s[k] for k in ("knots", "pairs", "labelled copies", "kind", "separated Euler count",
                                              "two-colourable", "doubled pairs", "every knot on a doubled pair")}
                           for s in special]},
        "P2": {"holds": p2_b1 and p2_b2 and p2_b3, "B1": p2_b1, "B2": p2_b2, "B3": p2_b3,
               "outcomes": {k: [b_rows[k]["outcome"], b_rows[k]["rounds"]] for k in b_rows},
               "census start of B3": B3["census start"],
               "births (round, newborn, parents)": {k: b_rows[k]["births"] for k in b_rows},
               "B4, measured: closes and holds kind (c) with a newborn's value": B4["outcome"] == "grown closed" and any(
                   f["kind"] == "c" and f["birth value"] for f in B4["non-orientable even"])},
        "P3": {"holds": bool(x_birth), "closures with one": len({f["index"] for f in x_birth}),
               "choices": len(x_birth)},
        "P4": {},
        "seconds": res["seconds"], "peak MiB": res["peak MiB"], "second sample draws per size": a.second,
        "seven-knot listing bound": a.e7,
    }
    for name, rows, fnd in [("extension", res["X"], x_found), ("second sample", res["X2"], x2_found),
                            ("census starts", res["C"], c_found)]:
        cl = [r for r in rows if r["outcome"] == "grown closed"]
        entry = {"draws or starts": len(rows), "outcomes": dict(collections.Counter(r["outcome"] for r in rows)),
                 "closures by knots": dict(sorted(collections.Counter(r["knots"] for r in cl).items())),
                 "birth words (sign, orientable)": {f"{s} {o}": n for (s, o), n in sorted(word_totals(rows).items())},
                 "non-orientable even birth choices by pairs": by_size(fnd),
                 "closures with a non-orientable even birth choice": len({f["index"] for f in fnd if not f["whole"]})}
        if any("whole" in r for r in cl):
            entry["whole words (sign, orientable)"] = {f"{s} {o}": n for (s, o), n in
                                                       sorted(word_totals(rows, "whole").items())}
            entry["non-orientable even whole choices by pairs"] = by_size(fnd, True)
        nb = [f for f in fnd if not f["whole"]]
        entry["their start knots, newborns, doubled pairs, every knot on one, separated Euler count"] = dict(
            collections.Counter(str((f["start knots"], f["newborns"], f["doubled pairs"],
                                     f["every knot on a doubled pair"], f["separated Euler count"]))
                                for f in nb))
        entry["those using a newborn's value"] = sum(1 for f in nb if f["birth value"])
        summary["P4"][name] = entry
    summary["P4"]["B1 family"] = {
        "starts": len(family), "outcomes": dict(collections.Counter(f["outcome"] for f in family)),
        "closures holding kind (b)": sum(f["kind (b)"] for f in family),
        "closures": sum(f["outcome"] == "grown closed" for f in family)}
    summary["P4"]["kinds of the six-pair choices at grown closures"] = {
        name: dict(collections.Counter(str(f["kind"]) for f in fnd if not f["whole"] and f["pairs"] == 6))
        for name, fnd in (("extension", x_found), ("second sample", x2_found), ("census starts", c_found))}
    return g, summary


def census_starts():
    return [(n, tuple(tuple(e) for e in m), tuple(l))
            for n, m, l in json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--second", type=int, default=10000, help="draws per size in the second extension sample")
    ap.add_argument("--e7", type=int, default=7, help="most pairs listed on seven knots")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = {}
    res["E"], special, found_fixtures = run_abstract(5 if a.probe else a.e7)
    # B: built starts and the scaffold family
    b_rows = {}
    canon = {(n, m, loose): i for i, (n, m, loose) in enumerate(census_starts())}   # stored in canonical form
    for name, s in [("B1", b1((1, 1, 1, 0, 0, 0))), ("B2", b2()), ("B3", b3()), ("B4", b4())]:
        births = []
        row, fnd = closure_rows(s, ROUNDS, CAP, births=births)
        key = (s[0],) + forbid.canonical(s[0], {(x, y): k for x, y, k in s[1]}, s[2]) if s[0] <= 5 else None
        b_rows[name] = {"start": s, **row, "births": births, "census start": canon.get(key),
                        "non-orientable even": fnd}
    family = []
    for loose in itertools.product((0, 1, 2), repeat=6):
        if not any(loose):
            continue
        row, fnd = closure_rows(b1(loose), ROUNDS, CAP)
        klein = any(f["kind"] == "b" for f in fnd)
        family.append({"loose": loose, **row, "non-orientable even": len(fnd), "kind (b)": klein})
        if a.probe and len(family) >= 20:
            break
    res["B"] = b_rows
    res["B1 family"] = family
    # X: the extension and the second sample
    ext = forbid.extension()
    second = [s for n in forbid.SAMPLE_SIZES for s in forbid.sampled(n, a.second, SECOND_SEED + n)]
    res["X"], x_found = run_grown("extension", ext, ROUNDS, CAP, True, a.probe)
    res["X2"], x2_found = run_grown("second sample", second, ROUNDS, CAP, False, a.probe)
    # C: the census-start closures (the referee's limits), birth and whole choices
    res["C"], c_found = run_grown("census starts", census_starts(), CENSUS_ROUNDS, CENSUS_CAP, True, a.probe)
    res["seconds"] = round(time.time() - t0, 1)
    res["peak MiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    if a.probe:
        print(f"probe done in {res['seconds']}s, peak {res['peak MiB']} MiB; nothing written", flush=True)
        return
    gates, summary = summarise(res, special, found_fixtures, b_rows, family, x_found, x2_found, c_found, a)
    (out / "gates.json").write_text(json.dumps(gates, indent=1) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=list) + "\n")
    (out / "abstract.json").write_text(json.dumps({"rows": res["E"], "non-orientable even classes": special},
                                                  indent=1) + "\n")
    (out / "built.json").write_text(json.dumps({"B": res["B"], "B1 family": family}, indent=1, default=list) + "\n")
    for name, rows, fnd in [("extension", res["X"], x_found), ("second_sample", res["X2"], x2_found),
                            ("census_starts", res["C"], c_found)]:
        with open(out / f"{name}.jsonl", "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        (out / f"{name}_nonorientable_even.json").write_text(json.dumps(fnd, indent=1) + "\n")
    print(f"done in {res['seconds']}s, peak {res['peak MiB']} MiB", flush=True)


if __name__ == "__main__":
    main()
