"""ondemand.py: a local reader's view grown on demand.  ON-DEMAND-20261126-001 (a check by the thread, not registered);
README.md.

The growth is run on its live roster alone (REDUCE-BLOCKS' Lemma R, proved: from round 1 on it reads only the live knots,
their open counts and the down-closure of the sets N(w) & live), one round at a time, as WALL-READ-20261119-001A's roster
engine runs it, with each birth's ancestry carried: the start knots it descends from.  A READER is one live start knot k;
its VIEW at round t is the multiset of round-t births descending from k, read by (parents, fresh distinctions) (sig0) and
with its parents' readings (sig1).  ON DEMAND, the growth is run only on a REGION of the start: a set of its live knots,
with each block cut to the region; the open counts are not changed.

    ondemand.py verify N OUT.json       the roster engine's whole views against the look-alike study's growth, every
                                        census start of N knots, both knot laws, every round to 24
"""
import sys, os, json, itertools, collections
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'LATE-VIEWS-20261126-001'))
import late                                       # sizes_edges and round1 (the start read without the engine)


def maximal(fam):
    fam = {frozenset(B) for B in fam if len(B) >= 2}
    out = []
    for B in sorted(fam, key=len, reverse=True):
        if not any(B <= C for C in out): out.append(B)
    return out


def groups_of(points, blocks):
    """WALL-READ's roster rule: maximal cliques of three or more of the candidate graph that no block holds, and the
    candidate pairs inside none of them"""
    ps = set(points); cand = defaultdict(set)
    for B in blocks:
        for a, b in itertools.combinations(sorted(B & ps), 2): cand[a].add(b); cand[b].add(a)
    cliques = []
    def bk(R, P, X):                              # Bron-Kerbosch with a pivot
        if not P and not X: cliques.append(frozenset(R)); return
        u = max(P | X, key=lambda v: len(cand[v] & P))
        for v in list(P - cand[u]):
            bk(R | {v}, P & cand[v], X & cand[v]); P = P - {v}; X = X | {v}
    bk(set(), set(v for v in ps if cand[v]), set())
    big = [C for C in cliques if len(C) >= 3 and not any(C <= B for B in blocks)]
    covered = {frozenset(p) for C in big for p in itertools.combinations(sorted(C), 2)}
    pairs = {frozenset((a, b)) for a in cand for b in cand[a] if a < b} - covered
    return big + sorted(pairs, key=sorted)


def roster(stars):
    """live start knots, their open counts and places, and the maximal blocks"""
    sizes, edges = late.sizes_edges(stars)
    n = len(sizes); nb = defaultdict(set); sh = Counter()
    for a, b in edges: sh[a] += 1; sh[b] += 1; nb[a].add(b); nb[b].add(a)
    live = [k for k in range(n) if sizes[k] - sh[k] >= 1]; L = set(live)
    return {k: sizes[k] - sh[k] for k in live}, {k: sizes[k] for k in live}, maximal(nb[w] & L for w in range(n))


def dist_from(k, points, blocks):
    adj = defaultdict(set)
    for B in blocks:
        for a in B: adj[a] |= B - {a}
    D = {k: 0}; Q = [k]
    for a in Q:
        for b in adj[a]:
            if b in points and b not in D: D[b] = D[a] + 1; Q.append(b)
    return D


def grow(opn, places, blocks, T, law='nae', region=None, reader=None, cap=None):
    """rounds 1..T on the roster (cut to region if given); per round the births' (id, parents, fresh) and, for each
    birth, its start ancestors; ends 'stall' or 'closed' or 'rounds'.  The fresh count is max(d, 3 - p, 1), d its
    number of next-round groups; under parity a round that makes one birth holding every live knot, each with one
    loose distinction, closes (the implied birth: it takes every loose distinction).  cap: stop ('cap') before a round
    of more births."""
    pts = set(opn) if region is None else set(region) & set(opn)
    f = {v: opn[v] for v in pts}
    B = maximal(b & pts for b in blocks)
    anc = {v: frozenset([v]) for v in pts}
    sig = {v: ('start', 0, 0, places[v]) for v in pts}
    live = [v for v in sorted(pts) if f[v] >= 1]
    groups = groups_of(live, B)
    nid = max(opn) + 1; rounds = []; end = 'rounds'; allpar = {}
    for t in range(1, T + 1):
        live = [v for v in live if f[v] >= 1]
        if not live: end = 'closed'; break
        use = Counter(v for g in groups for v in g)
        if any(use[v] > f[v] for v in live): end = 'stall'; break
        par = {}
        for g in groups: par[nid] = frozenset(g); nid += 1
        for v in live:
            for _ in range(f[v] - use[v]): par[nid] = frozenset([v]); nid += 1
        new = list(par)
        if not new: end = 'closed'; break
        if cap is not None and len(new) > cap: end = 'cap'; break
        implied = law == 'parity' and len(new) == 1 and set(par[new[0]]) == set(live) and all(f[v] == 1 for v in live)
        ch = defaultdict(set)
        for j in new:
            for v in par[j]: ch[v].add(j)
        Bn = maximal(ch.values())
        nxt = groups_of(new, Bn)
        d = Counter(j for g in nxt for j in g)
        row = []
        for j in new:
            p = len(par[j]); f[j] = d[j] if implied else max(d[j], 3 - p, 1)
            anc[j] = frozenset().union(*(anc[v] for v in par[j]))
            sig[j] = ('offshoot' if p == 1 else 'join', p, f[j], p + f[j])
            row.append(j)
        rounds.append(row); allpar.update(par)
        live, B, groups = new, Bn, nxt
        if implied and f[new[0]] == 0: end = 'closed'; break
    return {'rounds': rounds, 'par': allpar, 'anc': anc, 'sig': sig, 'end': end}


def view(g, reader=None):
    """per round, the reader's view: (sig0 counter, sig1 counter) of the births descending from reader"""
    out = []
    for row in g['rounds']:
        c0, c1 = Counter(), Counter()
        for j in row:
            if reader is not None and reader not in g['anc'][j]: continue
            s0 = g['sig'][j]; c0[s0] += 1
            c1[s0 + (tuple(sorted(g['sig'][p] for p in g['par'][j])),)] += 1
        out.append((c0, c1))
    return out


def verify(N, out, law_list=('nae', 'parity')):
    """the roster engine's whole views (no reader) against the look-alike study's growth (alike.grow), both laws; one
    line per start and law, written as it goes; the engine stops before a round of more than 30,000 births and is then
    compared through the rounds it made"""
    sys.path.insert(0, os.path.join(HERE, '..', 'LOOK-ALIKE-20261126-001'))
    import alike
    with open(out, 'w') as f:
        for law in law_list:
            for i, gi, loose, stars in alike.census(N):
                a = alike.grow(stars, rounds=24, knot_law=law)
                opn, places, B = roster(stars)
                g = grow(opn, places, B, len(a['rows']) + 1, law, cap=30000)
                V = view(g); m = min(len(V), len(a['rows'])) if g['end'] == 'cap' else len(a['rows'])
                same = len(V) >= m and all(
                    late.cnt(a['rows'][t], 'sig0') == Counter({json.dumps(list(k)): v for k, v in V[t][0].items()}) and
                    late.cnt(a['rows'][t], 'sig1') == Counter({json.dumps([list(k[:4]), [list(x) for x in k[4]]]): v
                                                               for k, v in V[t][1].items()})
                    for t in range(m))
                f.write(json.dumps({'law': law, 'index': i, 'agree': same, 'rounds compared': m, 'growth end': a['end'],
                                    'engine end': g['end']}) + '\n'); f.flush()


if __name__ == '__main__':
    if sys.argv[1] == 'verify': verify(int(sys.argv[2]), sys.argv[3], tuple(sys.argv[4].split(',')) if len(sys.argv) > 4 else ('nae', 'parity'))
