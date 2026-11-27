"""ext.py: the extended nodes of a start, and the order lemma for them, checked without growing.
CHAIN-COUNT-20261127-001 (README.md).

An EXTENDED NODE is x = (C, a): a core node C (GRADED-ORDER-20261126-001's node reading: births built by Lemma R's round
rule from the round-1 groups and offshoots) and a length a_e >= 1 for each chain e in a set E of chains based at points of
C. Its round is rank(C) + sum(a). Its parents P(x) are x shortened along one chain (dropping the chain at length 1), and
(T, a) for each core parent T of C whose points hold every base of E. The node reading says ordinary growth's births are
the extended nodes with these parents. This checks, without growing, whether Lemma R's round rule applied to the extended
nodes of each round returns exactly the parent sets P(y) of the next round's extended nodes with two parents or more
(the ORDER LEMMA FOR EXTENDED NODES), and the condition

  (*) any two core parents T, T' of one core node that both hold a set B of chain bases share a core parent holding B.

    ext.py check FILE.jsonl[.gz] ... [--rounds R]   per start: the first round where the lemma fails, and (*)'s failures
"""
import sys, os, json, gzip, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'GRADED-ORDER-20261126-001'))
import order, twins
late = order.late


def extended(P, chains, R):
    """the extended nodes of piece P (a NodePiece) of rounds 1..R, each with its parent set"""
    rank = {n: z - 1 for n, z in P.sizes_of.items()}
    by_round = collections.defaultdict(list); par = {}
    for C, r in rank.items():
        if r < 1 or r > R: continue
        ch = [(q, i) for q in sorted(P.points_of[C], key=str) for i in range(chains.get(q, 0))]
        budget = R - r
        for k in range(0, min(len(ch), budget) + 1):
            for E in itertools.combinations(ch, k):
                for a in itertools.product(range(1, budget - k + 2), repeat=k):
                    if sum(a) > budget: continue
                    x = (C, tuple(zip(E, a)))
                    by_round[r + sum(a)].append(x)
    def parents(x):
        C, ea = x; out = set()
        for i, (e, ae) in enumerate(ea):
            out.add((C, ea[:i] + ((e, ae - 1),) + ea[i + 1:]) if ae > 1 else (C, ea[:i] + ea[i + 1:]))
        bases = {e[0] for e, _ in ea}
        for T in P.core_parents[C]:
            if rank[T] >= 1 and bases <= P.points_of[T]: out.add((T, ea))
            elif rank[T] == 0 and not ea: out.add((T, ea))
        return frozenset(out)
    for t in by_round:
        for x in by_round[t]: par[x] = parents(x)
    return by_round, par


def star_fails(P, chains):
    """(*): pairs of core parents of one node, both holding a set of chain bases, with no common core parent holding it"""
    out = []
    based = {q for q in chains if chains[q]}
    for C, ps in P.core_parents.items():
        for T, U in itertools.combinations(sorted(ps, key=str), 2):
            B = P.points_of[T] & P.points_of[U] & based
            if not B or P.sizes_of[T] < 2: continue
            common = P.core_parents[T] & P.core_parents[U]
            for k in range(1, len(B) + 1):
                for S in itertools.combinations(sorted(B, key=str), k):
                    if not any(set(S) <= P.points_of[W] and P.sizes_of[W] >= 2 for W in common):
                        out.append({'rank': P.sizes_of[C] - 1, 'bases': len(S)}); break
                else: continue
                break
    return out


def n3_fails(P, chains):
    """(N3): every maximal family of three or more core nodes of one rank that hold a set B of chain bases and pairwise
    share a core parent holding B has a common core parent holding B, or a common core child"""
    import networkx as nx
    based = sorted({q for q in chains if chains[q]}, key=str); out = []
    by_rank = collections.defaultdict(list)
    for n, z in P.sizes_of.items():
        if z >= 2: by_rank[z - 1].append(n)
    kids = collections.defaultdict(set)
    for n, ps in P.core_parents.items():
        for T in ps: kids[T].add(n)
    for k in range(1, len(based) + 1):
        for B in itertools.combinations(based, k):
            B = set(B)
            for r, ns in by_rank.items():
                H = [n for n in ns if B <= P.points_of[n]]
                if len(H) < 3: continue
                G = nx.Graph(); G.add_nodes_from(H)
                for X, Y in itertools.combinations(H, 2):
                    if any(B <= P.points_of[W] for W in P.core_parents[X] & P.core_parents[Y]): G.add_edge(X, Y)
                for Q in nx.find_cliques(G):
                    if len(Q) < 3: continue
                    cp = set.intersection(*[set(P.core_parents[X]) for X in Q])
                    if any(B <= P.points_of[W] for W in cp): continue
                    if set.intersection(*[kids[X] for X in Q]): continue
                    out.append({'rank': r, 'bases': k, 'family': len(Q)})
    return out


def check_start(stars, R):
    M = late.Map(stars, 'nae'); res = {'first failing round': None, 'star fails': 0, 'n3 fails': 0}
    if M.cls != 'in': return None
    order.NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4]
    order.NodePiece.max_rank = 25                     # pieces late.py counts as a cycle: read when the core finishes
    try:
        for pts, tree, nch in M.pieces:
            P = order.NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
            if not P.finished: return None
            res['star fails'] += len(star_fails(P, M.chains))
            res['n3 fails'] = res.get('n3 fails', 0) + len(n3_fails(P, M.chains))
            by_round, par = extended(P, M.chains, R)
            for t in range(1, R):
                want = order.round_rule(by_round[t], par)
                have = collections.Counter(par[y] for y in by_round[t + 1] if len(par[y]) >= 2)
                if want != have:
                    f = res['first failing round']
                    res['first failing round'] = t + 1 if f is None else min(f, t + 1)
                    extra = [sorted(map(str, S)) for S in (want - have)][:1]
                    res.setdefault('example', {'round': t + 1, 'round rule only': len(want - have),
                                               'extended nodes only': len(have - want)})
                    break
    finally:
        order.NodePiece.round1_groups = None; order.NodePiece.max_rank = None
    return res


if __name__ == '__main__':
    R = int(sys.argv[sys.argv.index('--rounds') + 1]) if '--rounds' in sys.argv else 8
    files = [a for a in sys.argv[2:] if a.endswith(('.jsonl', '.gz'))]
    tally = collections.Counter()
    for fn in files:
        op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
        for l in op:
            x = json.loads(l)
            try:
                r = check_start(x['stars'], R)
                T = twins.twins(x['stars'], cycles=True)
            except RuntimeError: tally[(fn, 'core over the cap')] += 1; continue
            if r is None: continue
            tw = 'chained twins' if T else 'no chained twins'
            key = (os.path.basename(fn), tw, 'lemma holds' if r['first failing round'] is None else 'fails', '(*) fails' if r['star fails'] else '(*) holds', '(N3) fails' if r['n3 fails'] else '(N3) holds')
            tally[key] += 1
            if r['first failing round'] is not None or r['star fails'] or r['n3 fails']:
                print(json.dumps({'file': fn, 'draw': x.get('draw', x.get('index')), 'twins': tw, **r}), flush=True)
    for k, v in sorted(tally.items()): print(v, k)
