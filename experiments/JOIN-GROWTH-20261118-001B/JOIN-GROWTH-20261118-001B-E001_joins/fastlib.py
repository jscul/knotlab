"""The joining policy of freelib.Presentation.groups_among (FRESH-COUNT-20261118-001B, cap=None), computed faster with the same
output.

freelib's groups are the maximal valid sets (sets of at least three pairwise candidates with no neighbour common to all) and the
candidate pairs in none of them.  Having no common neighbour passes to supersets, so a valid set lies in a maximal clique of the
candidate graph that is itself valid; hence the maximal valid sets are exactly the maximal cliques of the candidate graph with at least
three members and no common neighbour.  They are listed here by Bron-Kerbosch with pivoting instead of enumerating every valid set."""
import itertools
from collections import defaultdict


def candidates(self, lv):
    cand = defaultdict(set)
    ws = set()
    for u in lv:
        ws |= self.nbr[u]
    for w in ws:
        ln = [u for u in self.nbr[w] if u in lv]
        for u, v in itertools.combinations(ln, 2):
            cand[u].add(v)
            cand[v].add(u)
    return cand


def maximal_cliques(cand, verts):
    out = []
    stack = [(set(), set(verts), set())]
    while stack:
        R, P, X = stack.pop()
        if not P and not X:
            out.append(R)
            continue
        if not P:
            continue
        u = max(P | X, key=lambda y: len(cand[y] & P))
        for v in list(P - cand[u]):
            stack.append((R | {v}, P & cand[v], X & cand[v]))
            P.discard(v)
            X.add(v)
    return out


def groups_among(self, live, cap=None):
    if cap is not None:
        return _orig(self, live, cap)
    lv = set(live)
    cand = candidates(self, lv)
    nbr = self.nbr
    big = []
    for C in maximal_cliques(cand, [u for u in lv if cand[u]]):
        if len(C) >= 3 and not set.intersection(*[nbr[x] for x in C]):
            big.append(frozenset(C))
    covered = set()
    for S in big:
        for p in itertools.combinations(sorted(S), 2):
            covered.add(p)
    pairs = [frozenset((u, v)) for u in sorted(lv) for v in sorted(cand[u]) if u < v and (u, v) not in covered]
    return sorted(big, key=sorted) + sorted(pairs, key=sorted)


_orig = None


def install(F):
    global _orig
    if _orig is None:
        _orig = F.Presentation.groups_among
    F.Presentation.groups_among = groups_among


def uninstall(F):
    if _orig is not None:
        F.Presentation.groups_among = _orig
