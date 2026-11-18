"""PLUS-ONE-20261118-001B: the linked-class rule for the cheapest growth's dimension.

A birth is an offshoot of demand 1 whose parent is not itself an offshoot of demand 1; its partner is its unique candidate. Births of
one round with one partner form a class (sibling births are one class of two). Two classes of one round are linked when their
partners share a neighbour (or are neighbours). Rule: the dimension is the largest, over rounds and linked components, of the sum of
the class sizes in a component; 0 if there is no birth."""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib as A  # noqa: E402

F = A.F


def grow_births(stars, rounds=30, maxj=6000, deadline=None):
    import time
    births = []

    def rule(P, info, rng):
        ks = F.fewest(P, info, rng)
        byid = {i['j']: i for i in info}
        rows = []
        for i in info:
            if i['p'] != 1 or i['d'] != 1:
                continue
            j = i['j']
            parent = [x for x in P.owner[P.bits_of[j][0]] if x != j][0]
            if P.parents[parent] == 1 and P.demand_at_birth[parent] == 1:
                continue
            sib = [x for bb in P.bits_of[parent] for x in P.owner[bb] if x not in (parent, j) and x in byid]
            rows.append((j, sib[0] if sib else None))
        births.append(rows)
        return ks

    P = A.S.from_junctions(stars)
    out = 'alive'
    for _ in range(rounds):
        r = P.step(A.S.gf2(rule), None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if len(P.bits_of) > maxj:
            out = 'big'
            break
        if deadline is not None and time.time() > deadline:
            out = 'timed'
            break
    return P, out, births


def linked_rule(P, births):
    """(largest class, largest linked-component sum, the shapes of components of two or more classes) over all rounds.
    A shape lists the component's class sizes and whether its links form a clique."""
    big_class, big_sum = 0, 0
    shapes = []
    for rows in births:
        if not rows:
            continue
        ids = {j for j, _ in rows}
        cls = {}
        for j, partner in rows:
            key = frozenset((j, partner)) if partner in ids else partner
            cls.setdefault(key, set()).add(j)
        keys = list(cls)
        partners = {k: ([x for x in k] if isinstance(k, frozenset) else [k]) for k in keys}

        def linked(k1, k2):
            return any(x is not None and y is not None and (P.nbr[x] & P.nbr[y] or x in P.nbr[y])
                       for x in partners[k1] for y in partners[k2])

        root = {k: k for k in keys}

        def find(k):
            while root[k] != k:
                k = root[k]
            return k

        for a in range(len(keys)):
            for b in range(a + 1, len(keys)):
                if linked(keys[a], keys[b]):
                    root[find(keys[a])] = find(keys[b])
        sums = defaultdict(int)
        members = defaultdict(list)
        for k in keys:
            sums[find(k)] += len(cls[k])
            members[find(k)].append(k)
        for ks in members.values():
            if len(ks) >= 2:
                clique = all(linked(x, y) for i, x in enumerate(ks) for y in ks[i + 1:])
                shapes.append([sorted(len(cls[k]) for k in ks), clique])
        big_class = max(big_class, max(len(v) for v in cls.values()))
        big_sum = max(big_sum, max(sums.values()))
    return big_class, big_sum, shapes
