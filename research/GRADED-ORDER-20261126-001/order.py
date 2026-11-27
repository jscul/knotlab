"""order.py: the order lemma, checked without growing, and a reading for starts with a split pair.
GRADED-ORDER-20261126-001 (README.md, "The order lemma").

Lemma R (REDUCE-BLOCKS-20261119-001A, proved, item 3): from round 1 on, the live knots are the last round's births; two
are candidates exactly when they share a parent, and a set has a common neighbour exactly when its members share one
parent. So a round's births are, among the last round's births, the maximal sets of three or more that pairwise share a
parent and do not all share one, and the candidate pairs no such set contains. Call this the ROUND RULE.

    order.py check FILE.jsonl [LAW]     on each start's core, are rank 1's valid sets the round-1 groups and offshoots, does
                                        the round rule applied to the valid sets of each rank return the parent sets of the
                                        valid sets of the next rank, and nothing after the top rank (the order lemma)?
    order.py core FILE.jsonl GROWN.jsonl LAW [--groups]   the reading for starts with a split pair: the core's births
                                        built by the round rule from the round-1 valid sets (each birth a node, not a set),
                                        then the chains and the relay as late.py reads them, the relay taken by the one last
                                        core birth holding the whole piece; --groups: rank 1 from the round-1 groups
                                        themselves instead of the valid sets; compared with the growth
"""
import sys, os, json, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graded
late, score = graded.late, graded.score


def round_rule(nodes, par):
    """the next round's parent sets from this round's nodes (par: node -> frozenset of its parents)"""
    nodes = list(nodes)
    adj = {a: set() for a in nodes}
    for a, b in itertools.combinations(nodes, 2):
        if par[a] & par[b]: adj[a].add(b); adj[b].add(a)
    out = []
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(nodes)
    for a in nodes:
        for b in adj[a]: G.add_edge(a, b)
    groups = []
    for Q in nx.find_cliques(G):                   # maximal cliques; a maximal valid set is one (any larger clique
        if len(Q) >= 3 and not frozenset.intersection(*[par[q] for q in Q]):   # would share no parent either)
            groups.append(frozenset(Q))
    covered = {frozenset(p) for S in groups for p in itertools.combinations(S, 2)}
    pairs = [frozenset((a, b)) for a in nodes for b in adj[a] if str(a) < str(b) and frozenset((a, b)) not in covered]
    return collections.Counter(groups + pairs)


def check_start(stars, law):
    M = late.Map(stars, law)
    if M.cls != 'in' or not all(t for _, t, _ in M.pieces): return None
    res = []
    groups = late.round1(*late.sizes_edges(stars))[4]
    for pts, tree, nch in M.pieces:
        P = late.GeneralPiece(pts, M.adj, M.chains, lambda v: v < M.n, None, lambda v: 1, M.cells)
        by = collections.defaultdict(list)
        for C, z in P.sizes_of.items(): by[z - 1].append(C)
        top = max(by) if by else 0
        # both ends (referee R2, fix 4): rank 1 must be the round-1 groups and offshoots, and the top rank must have
        # no births after it
        ones = [frozenset(g) for g in groups if set(g) <= set(pts)]
        ones += [frozenset([k, q]) for q in pts if not P.is_knot(q) for k in P.adj[q] if P.is_knot(k)]
        res.append((0, collections.Counter(frozenset(C) for C in by[1]) == collections.Counter(ones)))
        for t in range(1, top + 1):
            par = {A: frozenset(P.core_parents[A]) for A in by[t]}
            want = round_rule(by[t], par)
            have = collections.Counter(frozenset(P.core_parents[C]) for C in by[t + 1])
            res.append((t, want == have))
    return res


def check(path, law='nae'):
    tally = collections.Counter()
    for l in late.opener(path):
        x = json.loads(l)
        if 'stars' not in x: continue
        r = check_start(x['stars'], law)
        if r is None: tally['not in the class'] += 1; continue
        ok = all(v for _, v in r)
        flag = 'split pair' if graded.split_pair(x['stars'], law) else ('cells share two' if graded.cells_share_two(late.Map(x['stars'], law)) else 'neither')
        first = min((t for t, v in r if not v), default=None)
        tally[(flag, 'lemma holds at every rank' if ok else 'fails first at rank %d' % first)] += 1
    for k, v in sorted(tally.items(), key=str): print(v, k)


# ---------------------------------------------------------------- the reading for starts with a split pair

class NodePiece(late.GeneralPiece):
    round1_groups = None                                 # set by predict_nodes(..., groups=True)
    max_rank = None                                      # pieces with a cycle: stop building the core at this rank
    cap = int(os.environ.get('CORE_CAP', '200000'))       # core births at most, else the core is called unending
    """as GeneralPiece, but the core's births are built by the round rule from the round-1 valid sets, each birth a node
    (its points the union of its parents' points), so that two births with one union are two births"""
    def __init__(self, *a, **k):
        late.Piece.__init__(self, *a, **k)
        G = late.GeneralPiece(*a, **k) if NodePiece.round1_groups is None else None   # the valid sets only when needed
        self.points_of, self.sizes_of, self.core_parents = {}, {}, {}
        nid = 0
        def node(C, z, parents):
            nonlocal nid
            n = ('n', nid); nid += 1
            self.points_of[n] = frozenset(C); self.sizes_of[n] = z; self.core_parents[n] = set(parents); return n
        base = {}
        if NodePiece.round1_groups is None:              # rank 1 from the valid sets of the graded order
            for C, z in G.sizes_of.items():
                if z <= 2: base[C] = node(C, z, [])
            for C, n in base.items():
                if G.sizes_of[C] == 2: self.core_parents[n] = {base[T] for T in G.core_parents[C] if T in base}
        else:                                            # rank 1 from the round-1 groups themselves (Lemma R, item 1)
            pts = set(self.pts)
            for v in pts:
                if self.is_knot(v): base[frozenset([v])] = node([v], 1, [])
            ones = [frozenset(g) for g in NodePiece.round1_groups if set(g) <= pts]
            ones += [frozenset([k, q]) for q in pts if not self.is_knot(q) for k in self.adj[q] if self.is_knot(k)]
            for C in ones:
                base[C] = node(C, 2, [base[frozenset([v])] for v in C if frozenset([v]) in base])
        layer = [n for n in self.points_of if self.sizes_of[n] == 2]
        z = 2
        while layer and (NodePiece.max_rank is None or z <= NodePiece.max_rank):
            par = {a: frozenset(self.core_parents[a]) for a in layer}
            nxt = []
            for S in round_rule(layer, par):
                C = frozenset().union(*(self.points_of[a] for a in S))
                nxt.append(node(C, z + 1, S))
            layer, z = nxt, z + 1
            if nid > NodePiece.cap: raise RuntimeError('too many core births')
        self.children = collections.Counter()
        for n, ps in self.core_parents.items():
            for T in ps: self.children[T] += 1

    def valid(self, S):
        return S in self.points_of if not isinstance(S, frozenset) else True

    def configs(self):
        for n, w in self.sizes_of.items():
            C = self.points_of[n]
            if not any(self.is_knot(x) for x in C): continue
            ch = [(v, i) for v in sorted(C, key=str) for i in range(self.chains.get(v, 0))]
            for r in range(len(ch) + 1):
                for E in itertools.combinations(ch, r):
                    yield n, frozenset(E), w

    def parent_sets(self, C, E):
        bases = {e[0] for e in E}
        return {T for T in self.core_parents[C] if bases <= self.points_of[T]}

    def kind(self, C, E):
        key = (C, E)
        if key not in self.memo:
            self.memo[key] = (len(E) + len(self.parent_sets(C, E)),
                              self.children[C] + sum(self.chains.get(v, 0) for v in self.points_of[C]))
        return self.memo[key]

    def sig0(self, C, E):
        if not E and self.sizes_of[C] == 1: return self.single_type(next(iter(self.points_of[C])))
        p, f = self.kind(C, E)
        return ('offshoot' if p == 1 else 'join', p, f, p + f)


def predict_nodes(stars, rounds, law, groups=False, cycles=False):
    """late.predict with NodePiece in place of GeneralPiece: the same terms, chains and relay, except that the relay's
    whole-piece birth is the node whose points are the whole piece (not predicted if there are several)"""
    M = late.Map(stars, law)
    if M.cls != 'in': return None, M.cls
    if not all(tree for _, tree, _ in M.pieces) and not cycles: return None, 'a piece with a cycle'
    NodePiece.max_rank = rounds + 1 if cycles else None  # a birth of rank r is born in round r, so rank rounds suffices
    NodePiece.round1_groups = late.round1(*late.sizes_edges(stars))[4] if groups else None
    start = lambda v: ('start', 0, 0, M.sizes[v])
    many = len(M.pieces) >= 2
    terms = []
    def add(P, C, E, w, bump=False):
        for J in (frozenset(x) for r in range(len(E) + 1) for x in itertools.combinations(sorted(E, key=str), r)):
            s0 = P.sig0(C, E)
            if bump: s0 = (s0[0], s0[1], s0[2] + 1, s0[3] + 1)
            terms.append((s0, s0 + (P.parent_sigs(C, E, J),), w, len(E), len(J)))
            if not E: break
    for pts, tree, nch in M.pieces:
        P = NodePiece(pts, M.adj, M.chains, lambda v: v < M.n, start, lambda v: 1, M.cells)
        relay = tree and nch == 0 and (law == 'nae' or many)   # a piece with a cycle never finishes
        whole = frozenset(pts)
        tops = [n for n in P.points_of if P.points_of[n] == whole and not P.children[n]]   # the last core births
        if relay and len(tops) != 1: return None, 'not one last birth holding the whole piece'
        for C, E, w in P.configs():
            add(P, C, E, w, bump=relay and C in tops and not E)
        for top in (tops if relay else []):
            Wsig = P.sig0(top, frozenset()); Wsig = (Wsig[0], Wsig[1], Wsig[2] + 1, Wsig[3] + 1)
            radj = collections.defaultdict(set); radj['W'].add('q'); radj['q'].add('W')
            R = late.Piece(['W', 'q'], radj, {'q': 2}, lambda v: v == 'W', (lambda s: (lambda v: s))(Wsig),
                           (lambda z: (lambda v: z if v == 'W' else 1))(P.sizes_of[top]))
            for C, E, w in R.configs():
                if C == frozenset(['W']) and not E: continue
                add(R, C, E, w)
    H = max(rounds, max((w + k for _, _, w, k, _ in terms), default=0) + 1)
    rows = [collections.Counter() for _ in range(H + 1)], [collections.Counter() for _ in range(H + 1)]
    for s0, s1, w, k, j in terms:
        for t in range(1, H + 1):
            c, p = late.term_at(t, w, k, j)
            for Rr, key in ((0, s0), (1, s1)):
                if c: rows[Rr][t][key] += c
    out = []
    for t in range(1, rounds + 1):
        out.append({'n': sum(rows[0][t].values()),
                    'sig0': sorted([list(k), v] for k, v in rows[0][t].items() if v),
                    'sig1': sorted([[list(k[:4]), [list(x) for x in k[4]]], v] for k, v in rows[1][t].items() if v)})
    return out, 'predicted'


def core(path, grown, law, groups=False):
    stars_by = {}
    for l in late.opener(grown):
        x = json.loads(l)
        try:
            P, why = predict_nodes(x['stars'], graded.ROUNDS, law, groups)
        except Exception as e:
            print(json.dumps({'draw': x.get('draw'), 'name': x.get('name'), 'law': law, 'error': repr(e)})); continue
        first = score.compare(P, x) if P is not None else 'not predicted: ' + why
        G, _ = late.predict(x['stars'], graded.ROUNDS, law, general=True)
        print(json.dumps({'draw': x.get('draw'), 'name': x.get('name'), 'law': law,
                          'split pair': graded.split_pair(x['stars'], law),
                          'cells share two': graded.cells_share_two(late.Map(x['stars'], law)),
                          'graded order': score.compare(G, x) if G is not None else 'not predicted',
                          'node reading': first, 'rounds read': len(x['rows'])}), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'check': check(sys.argv[2], *(sys.argv[3:4] or ['nae']))
    elif sys.argv[1] == 'core': core(sys.argv[2], sys.argv[3], sys.argv[4], '--groups' in sys.argv)
