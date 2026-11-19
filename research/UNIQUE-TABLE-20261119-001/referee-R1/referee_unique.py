"""Referee R1 for UNIQUE-TABLE-20261119-001 (own code; the eleven truth/rival pairs read from verify_rivals.json as data; no study
code imported or run).

  ../../../.venv/bin/python -B referee_unique.py <part> > referee_unique_<part>.json      (from this directory)

Parts:
  pairs   each of the eleven different-equation rivals against its truth: static legality (every distinction in one or two
          junctions, every junction of three or more, no two sharing two, every junction's star a bond: no cut vertex but the
          outside), both exact tables by two methods of the referee's (brute force over the allowed states' minimal non-free sets,
          and its closed-aware shore enumeration), equal entry by entry; the equation spaces; isomorphism as arrangements; whether
          every symmetry of the truth's table keeps the truth's junctions; the least bond holding each triple (how many triples
          differ); and the next round of the cheapest counts from each, with the round-1 junctions live.
  reach   whether each truth and each rival can be reached: (a) by the cheapest growth in complete rounds from any start, where a
          start is any subset of its junctions (a stage's start knots are among its junctions, with their full supports), grown
          by the referee's engine for at least one round until it passes the size; (b) under Codex's serial mixed law (one to three parents, two or three
          fresh), by isomorphism with the referee's 001F census of every reachable presentation at the same width.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/NAE-GROWTH-20261119-001/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1",
          "research/VARIABLE-OUTPUT-READER-20261118-001L/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
import referee_f as F  # noqa: E402
import referee_first as RFK  # noqa: E402
import referee_nae as RN  # noqa: E402
import referee_census as RC  # noqa: E402

VR = ROOT / "artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique/verify_rivals.json"


def legal_static(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    if any(len(v) > 2 for v in own.values()) or any(len(s) < 3 for s in stars):
        return False, "multiplicity or size"
    share = Counter(tuple(sorted(v)) for v in own.values() if len(v) == 2)
    if share and max(share.values()) >= 2:
        return False, "two junctions share two"
    n = len(stars)
    G = nx.MultiGraph()
    G.add_nodes_from(range(n + 1))
    for b, v in own.items():
        G.add_edge(v[0], v[1] if len(v) == 2 else n)
    if not any(len(v) == 1 for v in own.values()):
        G.remove_node(n)
    for j in range(n):
        H = G.copy()
        H.remove_node(j)
        if H.number_of_nodes() and not nx.is_connected(H):
            return False, f"junction {j} is a cut vertex"
    return True, "legal"


def span(stars):
    basis = {}
    for S in stars:
        r = sum(1 << x for x in S)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    for p in sorted(basis):
        for q in basis:
            if q != p and basis[q] >> p & 1:
                basis[q] ^= basis[p]
    return frozenset(basis.values())


def inc(stars):
    G = nx.Graph()
    for j, s in enumerate(stars):
        G.add_node(("j", j), k="j")
        for b in s:
            G.add_node(("b", b), k="b")
            G.add_edge(("j", j), ("b", b))
    return G


NM = nx.algorithms.isomorphism.categorical_node_match("k", None)


def least_bond_containing(stars, nbits, triple):
    """Least bond (cut with both sides connected; closed-aware) containing the three distinctions."""
    n = len(stars)
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    star = [sum(1 << x for x in s) for s in stars]
    adj = [0] * n
    haslo = 0
    for x, ks in own.items():
        if len(ks) == 2:
            adj[ks[0]] |= 1 << ks[1]
            adj[ks[1]] |= 1 << ks[0]
        else:
            haslo |= 1 << ks[0]
    full = (1 << n) - 1

    def grow(seed, U):
        comp = seed
        while True:
            new = comp
            m = comp
            while m:
                low = m & -m
                new |= adj[low.bit_length() - 1] & U
                m ^= low
            if new == comp:
                return comp
            comp = new
    need = sum(1 << x for x in triple)
    best = None
    word = [0] * (1 << n)
    for U in range(1, 1 << n):
        low = U & -U
        word[U] = word[U ^ low] ^ star[low.bit_length() - 1]
        w = word[U]
        if w & need != need or grow(low, U) != U:
            continue
        O = full & ~U
        if haslo:
            if grow(O & haslo, O) != O:
                continue
        elif not O or grow(O & -O, O) != O:
            continue
        s = bin(w).count("1")
        best = s if best is None else min(best, s)
    return best


def next_round(stars, round1):
    G = RFK.Start(stars)
    G.round = [1 if j in round1 else 0 for j in range(len(stars))]
    G.rounds = 1
    G.live = sorted(round1)
    r = G.step(RFK.fewest, None, None)
    return r, len(G.bits) - len(stars)


def part_pairs():
    rows = json.load(open(VR))
    out = []
    for r in rows:
        T, Rv = [sorted(s) for s in r["truth"]], [sorted(s) for s in r["rival"]]
        nb = 1 + max(max(s) for s in T)
        Kt_b, _ = RN.nae_table(nb, RN.parity_states(nb, T)), None
        Kr_b = RN.nae_table(nb, RN.parity_states(nb, Rv))
        Kt_s, _ = RC.shore_table(T)
        Kr_s, _ = RC.shore_table(Rv)
        start = RC.stars_of(tuple(map(tuple, r["key"])))
        r1 = {j for j, s in enumerate(T) if sorted(s) not in [sorted(x) for x in start]}
        gens = F.generators(Kt_b)[0]
        triples = list(itertools.combinations(range(nb), 3))
        diff3 = sum(least_bond_containing(T, nb, t) != least_bond_containing(Rv, nb, t) for t in triples)
        nt, nr = next_round(T, r1), next_round(Rv, r1)
        out.append({"case": r["case"], "distinctions": nb, "junctions": len(T),
                    "truth legal (static)": legal_static(T), "rival legal (static)": legal_static(Rv),
                    "tables equal entry by entry (brute force)": bool((Kt_b == Kr_b).all()),
                    "brute force = shore enumeration (truth, rival)": [bool((Kt_b == Kt_s).all()), bool((Kr_b == Kr_s).all())],
                    "equation spaces equal": span(T) == span(Rv),
                    "isomorphic as arrangements": nx.is_isomorphic(inc(T), inc(Rv), node_match=NM),
                    "every symmetry of the truth's table keeps its junctions": F.keeps(gens, {frozenset(s) for s in T}),
                    "triples whose least containing bond differs": [diff3, len(triples)],
                    "junctions that differ (truth, rival)": [sorted(sorted(s) for s in T if sorted(s) not in Rv),
                                                             sorted(sorted(s) for s in Rv if sorted(s) not in T)],
                    "next round, round-1 junctions live (truth, rival): outcome, new junctions": [list(nt), list(nr)]})
    return out


def reach_rounds(target):
    """Is the target a stage of the cheapest growth from a start made of some of its junctions?"""
    n = len(target)
    Gt = inc(target)
    hits = []
    for k in range(1, n):
        for S in itertools.combinations(range(n), k):
            sub = [target[j] for j in S]
            # the start must be connected through shared distinctions
            own = defaultdict(list)
            for j, s in enumerate(sub):
                for b in s:
                    own[b].append(j)
            Gs = nx.Graph()
            Gs.add_nodes_from(range(k))
            Gs.add_edges_from(tuple(v) for v in own.values() if len(v) == 2)
            if not nx.is_connected(Gs):
                continue
            G = RFK.Start(sub)
            for rnd in range(n - k + 1):
                if rnd >= 1 and len(G.bits) == n and nx.is_isomorphic(inc(G.bits), Gt, node_match=NM):   # a grown stage, not the start
                    hits.append({"start": [sorted(s) for s in sub], "round": rnd})
                    break
                if len(G.bits) >= n:
                    break
                if G.step(RFK.fewest, None, None) != "ok":
                    break
            if hits:
                return hits
    return hits


def part_reach():
    rows = json.load(open(VR))
    targets = {}
    for r in rows:
        targets[r["case"] + " truth"] = [sorted(s) for s in r["truth"]]
        targets[r["case"] + " rival " + str(sum(1 for k in targets if k.startswith(r["case"] + " rival")))] = [sorted(s) for s in r["rival"]]
    widths = {k: 1 + max(max(s) for s in v) for k, v in targets.items()}
    levels = F.census(max(widths.values()), workers=10)
    out = {}
    for k, stars in targets.items():
        T = F.from_supports(stars)
        G = F.graph(T)
        serial = any(nx.is_isomorphic(G, F.graph(C), node_match=F.nm) for C in levels.get(widths[k], []) if C[0] == T[0])
        hits = reach_rounds(stars)
        out[k] = {"distinctions": widths[k], "three-place junctions": sum(len(s) == 3 for s in stars),
                  "reachable by the cheapest growth in complete rounds": bool(hits), "a start and round": hits[:1],
                  "reachable under the serial mixed law (001F census)": serial}
    return out


if __name__ == "__main__":
    print(json.dumps({"pairs": part_pairs, "reach": part_reach}[sys.argv[1]](), indent=1, default=str))
