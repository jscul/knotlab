"""Serial growth pilot: one join at a time, chosen at random among the moves the current presentation allows."""
import sys, random
from collections import defaultdict, Counter
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins')
import joinlib as J
S, F = J.S, J.F

def new_junction(P, bits):
    jid = len(P.bits_of)
    P.bits_of.append(list(bits)); P.nbr.append(set())
    for b in bits:
        for o in P.owner[b]:
            P.nbr[o].add(jid); P.nbr[jid].add(o)
        P.owner[b].append(jid)
    P.parents.append(len(bits)); P.fresh.append(0); P.round_of.append(0); P.demand_at_birth.append(None)
    return jid

def moves(P, children_of):
    live = [j for j in range(len(P.bits_of)) if P.loose(j)]
    gs = P.groups_among(live)
    ok = []
    for g in gs:
        g = tuple(sorted(g))
        # not already joined: no junction has all of g among its parents
        common = set.intersection(*[children_of[j] for j in g]) if g else set()
        if not common:
            ok.append(g)
    use = Counter(j for g in ok for j in g)
    off = [(j,) for j in live if len(P.loose(j)) > use[j]]
    return ok, off, live

def grow_serial(sizes, edges, steps, seed, policy='uniform', maxj=4000):
    rng = random.Random(seed)
    P = S.from_junctions(J.stars_from(sizes, edges)); P.linalg = False
    rank = [0] * len(P.bits_of)
    children_of = defaultdict(set)
    for _ in range(steps):
        ok, off, live = moves(P, children_of)
        if policy == 'joins-first' and ok:
            pool = [('j', g) for g in ok]
        else:
            pool = [('j', g) for g in ok] + [('o', o) for o in off]
        if not pool: return P, rank, 'closed'
        kind, g = rng.choice(pool)
        all_loose = sorted(b for j in live for b in P.loose(j))
        bits = [P.loose(j)[0] for j in g]
        jid = new_junction(P, bits)
        rank.append(1 + max(rank[j] for j in g))
        for j in g: children_of[j].add(jid)
        # fresh bits: the fewest rule with demand read from the current state
        implied = sorted(bits) == all_loose
        live2 = [j for j in range(len(P.bits_of)) if P.loose(j) or j == jid]
        d = sum(1 for h in P.groups_among(live2) if jid in h)
        p = len(bits)
        k = 0 if (implied and d == 0) else max(d, 3 - p, 1)
        for _ in range(k):
            b = P.nbits; P.nbits += 1; P.bits_of[jid].append(b); P.owner[b] = [jid]
        P.fresh[jid] = k
        if len(P.bits_of) > maxj: return P, rank, 'cap'
    return P, rank, 'steps'

def by_rank(rank):
    c = Counter(rank)
    return [c[r] for r in range(max(rank) + 1)]
