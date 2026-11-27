"""chains.py: chains of three-place knots in a stage.  CHAIN-STEP-20261127-001; README.md.

A chain of length L is a sequence of L distinct knots of three places each, in which each knot shares exactly one
distinction with the next and no two non-consecutive knots of the sequence share any distinction (the referee's
definition in FOUR-CLAUSE-20261127-001, report R1).  has_chain answers whether a stage holds one, by depth-first search;
count_chains counts them up to reversal, with a cap."""
import collections


def _meets(sup):
    h = collections.defaultdict(list)
    for k, r in enumerate(sup):
        for x in r: h[x].append(k)
    share = collections.defaultdict(lambda: collections.defaultdict(int))
    for x, ks in h.items():
        for a in ks:
            for b in ks:
                if a != b: share[a][b] += 1
    three = [k for k, r in enumerate(sup) if len(r) == 3]
    return share, set(three)


def chains(sup, L, cap=None):
    """yield chains (tuples of knot indices), each once up to reversal"""
    share, three = _meets(sup)
    found = 0
    def grow(path, used_nb):
        nonlocal found
        if len(path) == L:
            if path[0] < path[-1]:
                found += 1; yield tuple(path)
            return
        last = path[-1]
        for nxt in share[last]:
            if nxt not in three or nxt in path or share[last][nxt] != 1: continue
            if any(nxt in share[p] for p in path[:-1]): continue      # no sharing with non-consecutive knots
            path.append(nxt)
            yield from grow(path, used_nb)
            path.pop()
            if cap and found >= cap: return
    for s in sorted(three):
        yield from grow([s], None)
        if cap and found >= cap: return


def has_chain(sup, L=8):
    return next(chains(sup, L), None) is not None


def count_chains(sup, L=8, cap=10000):
    return sum(1 for _ in chains(sup, L, cap))
