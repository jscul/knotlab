"""Referee R1 for BOND-NEXT-JOIN-20261117-001 (own code; the study's check_rearrangements.py and check_examples.py are not imported).

  ../../../.venv/bin/python -B referee_next.py <max junctions> > referee_next.json      (from this directory)

1. Every legal serial assembly of the pure parity rule (CUBIC-FROM-A-KNOT's move: one loose bit from each of one, two or three
   junctions, pairwise common neighbours, no neighbour common to all three; one parity junction on them and three fresh bits), up
   to isomorphism of the junction-bit incidence (loose bits included), to the given number of junctions (the study: 7; 8 is one
   past).  Count the distinct patterns per size.
2. For each pattern, the exact bond distance of every pair of bits, computed with no lemma: every nonzero sum of junction
   equations, the inclusion-minimal supports among them (the K1-K3 knots of a linear system), and the least such support through
   the pair.
3. The study's reader, written from the proof's section 3: thresholds 3..6 on distances at most 2..5, the two-star cross pairs
   removed, maximal cliques of size at least 3.  Does it return exactly the junctions' stars?  Do distinct patterns have distinct
   tables (up to renaming, distances above five pooled)?
4. The parallel round from the recovered stars (triples, pairs in no triple, singletons for the remaining loose bits, or blocked),
   against the same from the true stars; and the two worked examples (a chain of four; the seed with three children).
"""
import itertools
import json
import sys
from collections import Counter, defaultdict

import networkx as nx


def seed():
    return [frozenset({0, 1, 2})], 3


def owners(J):
    o = defaultdict(list)
    for i, s in enumerate(J):
        for b in s:
            o[b].append(i)
    return o


def neighbours(J):
    o = owners(J)
    nb = defaultdict(set)
    for b, js in o.items():
        if len(js) == 2:
            nb[js[0]].add(js[1])
            nb[js[1]].add(js[0])
    return nb


def loose(J):
    o = owners(J)
    return {i: sorted(b for b in s if len(o[b]) == 1) for i, s in enumerate(J)}


def legal_parent_sets(J):
    nb = neighbours(J)
    lo = loose(J)
    front = [i for i in range(len(J)) if lo[i]]
    out = [(i,) for i in front]
    for a, b in itertools.combinations(front, 2):
        if nb[a] & nb[b]:
            out.append((a, b))
    for a, b, c in itertools.combinations(front, 3):
        if nb[a] & nb[b] and nb[a] & nb[c] and nb[b] & nb[c] and not (nb[a] & nb[b] & nb[c]):
            out.append((a, b, c))
    return out


def add(J, nbits, parents):
    lo = loose(J)
    bits = {lo[p][0] for p in parents}
    new = frozenset(bits | {nbits, nbits + 1, nbits + 2})
    return J + [new], nbits + 3


def graph(J):
    G = nx.Graph()
    for i, s in enumerate(J):
        G.add_node(("j", i), t="j")
        for b in s:
            G.add_node(("b", b), t="b")
            G.add_edge(("j", i), ("b", b))
    return G


def enumerate_patterns(maxJ):
    levels = [[seed()]]
    for size in range(2, maxJ + 1):
        buckets = defaultdict(list)
        out = []
        for J, nb in levels[-1]:
            for ps in legal_parent_sets(J):
                J2, nb2 = add(J, nb, ps)
                G = graph(J2)
                h = nx.weisfeiler_lehman_graph_hash(G, node_attr="t", iterations=4)
                if any(nx.is_isomorphic(G, H, node_match=lambda a, b: a["t"] == b["t"]) for H in buckets[h]):
                    continue
                buckets[h].append(G)
                out.append((J2, nb2))
        levels.append(out)
        print("size", size, len(out), file=sys.stderr, flush=True)
    return levels


def bond_distances(J):
    """Exact: every nonzero sum of junction equations; its support; inclusion-minimal supports; least through each pair."""
    bits = sorted(set().union(*J))
    idx = {b: k for k, b in enumerate(bits)}
    rows = [sum(1 << idx[b] for b in s) for s in J]
    sups = set()
    for mask in range(1, 1 << len(J)):
        x = 0
        for i in range(len(J)):
            if (mask >> i) & 1:
                x ^= rows[i]
        if x:
            sups.add(x)
    sups = sorted(sups, key=lambda x: bin(x).count("1"))
    minimal = []
    for x in sups:
        if not any((m & x) == m for m in minimal):
            minimal.append(x)
    d = {}
    for m in minimal:
        sz = bin(m).count("1")
        mem = [bits[k] for k in range(len(bits)) if (m >> k) & 1]
        for a, b in itertools.combinations(mem, 2):
            key = (min(a, b), max(a, b))
            if key not in d or sz - 1 < d[key]:
                d[key] = sz - 1
    return bits, d


def reader(bits, d):
    """The proof's section 3."""
    dist = lambda a, b: d.get((min(a, b), max(a, b)), 99)
    stars = []
    for k in range(3, 7):
        G = nx.Graph()
        G.add_nodes_from(bits)
        for a, b in itertools.combinations(bits, 2):
            if dist(a, b) <= k - 1:
                G.add_edge(a, b)
        for S, T in itertools.combinations(stars, 2):
            if S & T and len(S) + len(T) - 2 <= k:
                for a in S - T:
                    for b in T - S:
                        if G.has_edge(a, b):
                            G.remove_edge(a, b)
        stars = [frozenset(c) for c in nx.find_cliques(G) if len(c) >= 3]
    return stars


def table_key(bits, d):
    G = nx.Graph()
    G.add_nodes_from(bits)
    for a, b in itertools.combinations(bits, 2):
        v = d.get((min(a, b), max(a, b)), 99)
        G.add_edge(a, b, d=str(min(v, 6)))
    return G


def parallel_round(J):
    """Triples, pairs in no triple, singletons for the remaining loose bits; or 'blocked'."""
    nb = neighbours(J)
    lo = loose(J)
    front = [i for i in range(len(J)) if lo[i]]
    cand = {frozenset(p) for p in itertools.combinations(front, 2) if nb[p[0]] & nb[p[1]]}
    triples = [t for t in itertools.combinations(front, 3)
               if all(frozenset(p) in cand for p in itertools.combinations(t, 2)) and not (nb[t[0]] & nb[t[1]] & nb[t[2]])]
    in_t = {frozenset(p) for t in triples for p in itertools.combinations(t, 2)}
    pairs = [p for p in cand if p not in in_t]
    use = Counter()
    for t in triples:
        use.update(t)
    for p in pairs:
        use.update(p)
    if any(use[i] > len(lo[i]) for i in front):
        return "blocked"
    singles = sum(len(lo[i]) - use[i] for i in front)
    return {"single": singles, "two": len(pairs), "three": len(triples)}


def main(maxJ):
    levels = enumerate_patterns(maxJ)
    out = {"patterns_by_size": [len(L) for L in levels], "per_size": []}
    for size, L in enumerate(levels, start=1):
        ok = 0
        same_round = 0
        blocked = 0
        tables = defaultdict(list)
        for J, nb in L:
            bits, d = bond_distances(J)
            rec = reader(bits, d)
            ok += set(rec) == set(J)
            pr_true = parallel_round(J)
            pr_read = parallel_round(sorted(rec, key=lambda s: min(s))) if set(rec) == set(J) else None
            same_round += pr_true == pr_read or (set(rec) == set(J))
            blocked += pr_true == "blocked"
            G = table_key(bits, d)
            h = nx.weisfeiler_lehman_graph_hash(G, edge_attr="d", iterations=3)
            if not any(nx.is_isomorphic(G, H, edge_match=lambda a, b: a["d"] == b["d"]) for H in tables[h]):
                tables[h].append(G)
        row = {"junctions": size, "patterns": len(L), "reader_recovers_every_star": ok,
               "distinct_tables_distances_above_5_pooled": sum(len(v) for v in tables.values()),
               "patterns_whose_parallel_round_is_blocked": blocked}
        out["per_size"].append(row)
        print("check", json.dumps(row), file=sys.stderr, flush=True)
    # the worked examples
    chain = [frozenset({0, 1, 2}), frozenset({0, 3, 4, 5}), frozenset({3, 6, 7, 8}), frozenset({6, 9, 10, 11})]
    star = [frozenset({0, 1, 2}), frozenset({0, 3, 4, 5}), frozenset({1, 6, 7, 8}), frozenset({2, 9, 10, 11})]
    ex = {}
    for name, J in (("chain of four", chain), ("seed with three children", star)):
        bits, d = bond_distances(J)
        rec = reader(bits, d)
        ex[name] = {"bits": len(bits), "log2_states": len(bits) - len(J), "reader_exact": set(rec) == set(J),
                    "next_round_from_read_stars": parallel_round(sorted(rec, key=lambda s: min(s)))}
    out["worked_examples"] = ex
    return out


if __name__ == "__main__":
    print(json.dumps(main(int(sys.argv[1])), indent=1))
