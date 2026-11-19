"""WALL-READ-20261119-001A-P001: the cheapest growth run on its live roster alone, and partnered sets of a stage.

**The roster engine.** By REDUCE-BLOCKS' Lemma R (refereed), from round 1 on the cheapest growth reads a connected start only through
its live knots, their open counts and the down-closure of the live-neighbour sets N(w) ∩ live (its maximal members are the
maximal blocks). So a state is (live points, open counts, maximal blocks), and one round is:
- candidates are two points that some block holds; a valid set is a set of three or more candidates pairwise that no block holds;
- the groups are the maximal cliques of the candidate graph that are valid, and the candidate pairs inside none of them;
- a point in more groups than its open count stalls the growth; otherwise each group is a junction whose parents are its members,
  and each point v also makes open(v) - use(v) offshoots (single-parent junctions);
- the new blocks are the sets {junctions with parent v}, reduced to the maximal ones (two junctions are candidates exactly when
  they share a parent);
- a new junction's open count is max(d, 3 - p, 1), d its number of next-round groups and p its parent count, or d when the round
  makes one junction holding every loose distinction (every live point in it, each with open count 1): then it closes.

The maximal cliques are listed by networkx's find_cliques, an enumeration separate from the program engine's (fastlib's
Bron-Kerbosch with its own pivot). Nothing here builds distinctions.

**Partnered sets.** A set W of 2k live points with a pairing is partnered when its candidate graph is every pair but the partner
pairs (the literature's cocktail-party graph O_k, an induced matching of the non-candidate graph). The search below is greedy and
deterministic for a given seed, so it gives lower bounds on the largest k, never the largest itself."""
import itertools
import random
from collections import Counter, defaultdict

import networkx as nx
import numpy as np


def roster_of(sizes, edges):
    """Live points 0..L-1, their open counts and the maximal blocks of a start (REDUCE-BLOCKS' live_and_blocks)."""
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    idx = {k: i for i, k in enumerate(live)}
    fam = [frozenset(idx[x] for x in nb[w] if x in idx) for w in range(n)]
    return [opn[k] for k in live], maximal_blocks(fam)


def maximal_blocks(fam):
    fam = {frozenset(B) for B in fam if len(B) >= 2}
    out = []
    for B in sorted(fam, key=len, reverse=True):
        if not any(B <= C for C in out):
            out.append(B)
    return out


def candidate_graph(points, blocks):
    G = nx.Graph()
    G.add_nodes_from(points)
    ps = set(points)
    for B in blocks:
        B = sorted(B & ps)
        G.add_edges_from(itertools.combinations(B, 2))
    return G


def groups_of(points, blocks):
    ps = set(points)
    of = defaultdict(set)
    for i, B in enumerate(blocks):
        for v in B & ps:
            of[v].add(i)
    G = candidate_graph(points, blocks)
    big = []
    for C in nx.find_cliques(G):
        if len(C) >= 3:
            common = set(of[C[0]])
            for x in C[1:]:
                common &= of[x]
                if not common:
                    break
            if not common:
                big.append(frozenset(C))
    covered = set()
    for S in big:
        covered.update(itertools.combinations(sorted(S), 2))
    pairs = [frozenset(e) for e in (tuple(sorted(x)) for x in G.edges()) if e not in covered]
    return big + pairs


def grow(opn, blocks, T, on_stage=None):
    """Yield one record per round: {'t', 'count', 'groups', 'offshoots', 'keys', 'largest'} or {'t', 'end': 'stall'|'closed'}.
    on_stage(t, points, blocks, par) is called on each built stage before its next round's groups are listed."""
    n = len(opn)
    f = {v: opn[v] for v in range(n)}
    live = [v for v in range(n) if f[v] >= 1]
    B = maximal_blocks(blocks)
    nid = n
    if on_stage is not None:
        on_stage(0, live, B, None)
    groups = groups_of(live, B)
    for t in range(1, T + 1):
        live = [v for v in live if f[v] >= 1]
        if not live:
            yield {'t': t, 'end': 'closed'}
            return
        use = Counter()
        for g in groups:
            for v in g:
                use[v] += 1
        if any(use[v] > f[v] for v in live):
            yield {'t': t, 'end': 'stall'}
            return
        par = {}
        for g in groups:
            par[nid] = g
            nid += 1
        off = 0
        for v in live:
            for _ in range(f[v] - use[v]):
                par[nid] = frozenset([v])
                nid += 1
                off += 1
        new = list(par)
        if not new:
            yield {'t': t, 'end': 'closed'}
            return
        implied = len(new) == 1 and set(par[new[0]]) == set(live) and all(f[v] == 1 for v in live)
        ch = defaultdict(set)
        for j in new:
            for v in par[j]:
                ch[v].add(j)
        Bn = maximal_blocks(ch.values())
        yield {'t': t, 'count': len(new), 'groups': len(groups), 'offshoots': off, 'blocks': len(Bn),
               'largest': max(len(par[j]) for j in new), 'largest_block': max((len(b) for b in Bn), default=0),
               'one_block': len(Bn) == 1 and len(Bn[0]) == len(new)}
        if on_stage is not None:
            on_stage(t, new, Bn, par)
        nxt = groups_of(new, Bn)
        d = Counter()
        for g in nxt:
            for j in g:
                d[j] += 1
        for j in new:
            p = len(par[j])
            f[j] = d[j] if implied else max(d[j], 3 - p, 1)
        yield {'t': t, 'keys': sorted(Counter((len(par[j]), f[j]) for j in new).items()),
               'open_sum': sum(f[j] for j in new), 'parent_sum': sum(len(par[j]) for j in new)}
        live, B, groups = new, Bn, nxt


def keys_by_round(opn, blocks, T):
    """Per-round sorted (parents, open) multisets, then 'stall' or 'closed' if the growth ends, as hublib.grow_keys reports."""
    out = []
    for r in grow(opn, blocks, T):
        if 'end' in r:
            out.append(r['end'])
            return out
        if 'keys' in r:
            out.append([tuple(x) for x in r['keys']])
    return out


# -- partnered sets -----------------------------------------------------------------------------------------------------------

class Bits:
    """The candidate graph of a stage as numpy bit rows (bit j of row i: points i and j are candidates; no self bits)."""

    def __init__(self, points, blocks):
        self.points = list(points)
        self.N = len(self.points)
        ix = {v: i for i, v in enumerate(self.points)}
        self.W = (self.N + 63) // 64
        self.rows = np.zeros((self.N, self.W), dtype=np.uint64)
        for B in blocks:
            m = np.zeros(self.W, dtype=np.uint64)
            mem = [ix[v] for v in B if v in ix]
            for i in mem:
                m[i >> 6] |= np.uint64(1) << np.uint64(i & 63)
            if mem:
                self.rows[mem] |= m
        for i in range(self.N):
            self.rows[i, i >> 6] &= ~(np.uint64(1) << np.uint64(i & 63))
        self.full = np.zeros(self.W, dtype=np.uint64)
        for i in range(self.N):
            self.full[i >> 6] |= np.uint64(1) << np.uint64(i & 63)

    def bit(self, i):
        m = np.zeros(self.W, dtype=np.uint64)
        m[i >> 6] = np.uint64(1) << np.uint64(i & 63)
        return m

    def members(self, m):
        out = []
        for w in np.nonzero(m)[0]:
            x = int(m[w])
            while x:
                b = x & -x
                out.append(int(w) * 64 + b.bit_length() - 1)
                x ^= b
        return out

    def adjacent(self, i, j):
        return bool((int(self.rows[i, j >> 6]) >> (j & 63)) & 1)


def partnered_set(bits, mode, seed=0, pool=1):
    """Greedy partnered set. R is the set of points still candidates of every chosen point; each step takes a non-candidate pair
    (u, v) inside R and keeps R & cand(u) & cand(v).
    mode 'large': u has the fewest non-candidates in R, v the fewest among u's non-candidates in R (aims at a large k).
    mode 'cover': (u, v) removes the most points of R (aims at emptying R: no outside common candidate).
    With pool > 1 the choice is uniform among the pool best (seeded). Returns (pairs, R left)."""
    rng = random.Random(seed)
    R = bits.full.copy()
    pairs = []
    while True:
        idx = bits.members(R)
        if len(idx) < 2:
            break
        sub = bits.rows[idx] & R
        cdeg = np.bitwise_count(sub).sum(axis=1).astype(np.int64)
        non = [int(x) for x in len(idx) - 1 - cdeg]    # non-candidates of each point inside R
        have = [k for k in range(len(idx)) if non[k] >= 1]
        if not have:
            break
        if mode == 'large':
            have.sort(key=lambda k: (non[k], idx[k]))
            u = idx[rng.choice(have[:pool])]
            nonu = [x for x in bits.members(R & ~bits.rows[u]) if x != u]
            pos = {x: k for k, x in enumerate(idx)}
            nonu.sort(key=lambda x: (non[pos[x]], x))
            v = rng.choice(nonu[:pool])
        else:
            have.sort(key=lambda k: (-non[k], idx[k]))
            best = []
            for k in have[:max(8, pool)]:
                u0 = idx[k]
                for v0 in [x for x in bits.members(R & ~bits.rows[u0]) if x != u0][:64]:
                    keep = int(np.bitwise_count(R & bits.rows[u0] & bits.rows[v0]).sum())
                    best.append((keep, u0, v0))
            best.sort()
            _, u, v = rng.choice(best[:pool])
        pairs.append((bits.points[u], bits.points[v]))
        R = R & bits.rows[u] & bits.rows[v]
    return pairs, [bits.points[i] for i in bits.members(R)]


def check_partnered(bits, pairs):
    """True when the pairs are partnered in the candidate graph (partners non-candidates, every other pair candidates)."""
    ix = {v: i for i, v in enumerate(bits.points)}
    flat = [ix[x] for p in pairs for x in p]
    if len(set(flat)) != len(flat):
        return False
    for a in range(len(flat)):
        for b in range(a + 1, len(flat)):
            partners = (a // 2 == b // 2)
            if bits.adjacent(flat[a], flat[b]) == partners:
                return False
    return True


def best_sets(bits, restarts=8):
    """The largest partnered set found, and the largest with no outside common candidate, over both modes and seeded restarts."""
    found = []
    for mode in ('large', 'cover'):
        for s in range(restarts):
            pairs, left = partnered_set(bits, mode, seed=s, pool=1 if s == 0 else 3)
            assert check_partnered(bits, pairs)
            found.append((len(pairs), not left, mode, s, pairs))
    k_any = max(found, key=lambda x: x[0])
    iso = [x for x in found if x[1]]
    k_iso = max(iso, key=lambda x: x[0]) if iso else None
    return k_any, k_iso
