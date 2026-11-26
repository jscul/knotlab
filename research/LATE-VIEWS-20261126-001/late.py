"""late.py: a start's view, round by round, from its map of joins alone.  LATE-VIEWS-20261126-001 (a check by the
thread, not registered); README.md.

By the proved identification (RING-IDENT, CHAIN-IDENT, RELAY-IDENT, DOUBLE-IDENT), in the class of DOUBLE-IDENT a birth of
round t is a connected set of t + 1 points of the extended map X+ (live knots, s = open - d pendant points per live knot,
R(open) endless chains on each pendant point; a block N(w) & live for every knot w), its parents are the points whose removal
leaves it connected and holding a live knot, and its fresh distinctions are its outside neighbours.  Nothing is grown here.

The finite part of each piece (its CORE: live knots and pendant points) is listed once.  A connected set of the extended map
is a connected set C of the core holding a live knot, a set E of the endless chains that leave from points of C, and a
length a_e >= 1 along each chain in E.  Its kind depends only on (C, E), so the number of round-t births of that kind is a
sum of binomial coefficients in t: the late view is a finite sum over the core, read off without growing.

A finite piece (a tree with no chains) relays under not-all-equal (NAE-GROWTH-20261118-001): the set of all its points
takes one fresh distinction, and a relay point with two chains hangs from it; under parity it relays only when the start
has two or more pieces, and closes otherwise.  Pieces with a cycle are outside this predictor (reported, not predicted).

    late.py check GROWN.jsonl[.gz] OUT.json [KNOT_LAW [ABLATE]]   predicted against grown views, round by round, both
                                                    readings; and the static settling bound.  ABLATE (negative
                                                    controls): relay, cells, or relay,cells
"""
import sys, os, json, gzip, itertools, collections, importlib.util
from math import comb, factorial
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
_s = importlib.util.spec_from_file_location(
    'di_check', ROOT + '/proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/machine_check.py')
DI = importlib.util.module_from_spec(_s); _s.loader.exec_module(DI)
sys.path.insert(0, os.path.join(HERE, '..', 'LOOK-ALIKE-20261126-001'))
import phase2                                    # the look-alike study's views and settling, unchanged


def sizes_edges(stars):
    owner = collections.defaultdict(list)
    for i, k in enumerate(stars):
        for d in k: owner[d].append(i)
    return [len(k) for k in stars], sorted(tuple(o) for o in owner.values() if len(o) == 2)


def round1(sizes, edges):
    """the start's live knots, open counts, live-neighbour sets and round-1 groups, read off the start alone: two live
    knots are candidates when some knot is a neighbour of both; the groups are the maximal cliques of the candidate graph
    of three or more knots that no block (a set N(w) & live) holds, and the candidate pairs inside none of them
    (WALL-READ-20261119-001A's roster rule; computed here without the engine)"""
    n = len(sizes); nb = collections.defaultdict(set); sh = collections.Counter()
    for a, b in edges: sh[a] += 1; sh[b] += 1; nb[a].add(b); nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]; L = set(live)
    blocks = [nb[w] & L for w in range(n)]
    cand = {frozenset(p) for B in blocks for p in itertools.combinations(sorted(B), 2)}
    cl = [frozenset(S) for r in range(3, len(live) + 1) for S in itertools.combinations(live, r)
          if all(frozenset(p) in cand for p in itertools.combinations(S, 2))]
    big = [S for S in cl if not any(S < T for T in cl) and not any(S <= B for B in blocks)]
    pairs = [p for p in cand if not any(p <= S for S in big)]
    groups = [sorted(S) for S in big] + [sorted(p) for p in pairs]
    d = collections.Counter(k for g in groups for k in g)
    return n, nb, opn, live, groups, d


def R_of(opn):
    return 0 if opn >= 3 else (1 if opn == 2 else 2)


class Map:
    """the extended map's finite part: points 0..n-1 are knots (live ones used), n.. pendant points.  Blocks are the
    distinct maximal sets N(w) & live (Lemma R: the growth reads only their down-closure); each round-1 group of three
    or more live knots is a GROUP CELL, and blocks inside a group cell are dropped"""
    def __init__(self, stars, knot_law='nae'):
        sizes, edges = sizes_edges(stars)
        self.stars, self.sizes = stars, sizes
        n, nb, opn, live, groups, d = round1(sizes, edges)
        self.n, self.live = n, set(live)
        loose = sum(opn[k] for k in live)
        if any(d[k] > opn[k] for k in live): self.cls = 'stall'
        elif loose == 0: self.cls = 'none'
        elif loose == 1 and knot_law != 'nae': self.cls = 'one loose'
        else: self.cls = 'in'
        raw = {frozenset(nb[w] & self.live) for w in range(n) if len(nb[w] & self.live) >= 2}
        self.cells = [frozenset(g) for g in groups if len(g) >= 3]
        blocks = [B for B in raw if not any(B < B2 for B2 in raw) and not any(B <= G for G in self.cells)]
        self.overlap = (any(len(set(B) & G) >= 2 for B in blocks for G in self.cells),     # reported, not excluded
                        any(len(G & G2) >= 2 for G, G2 in itertools.combinations(self.cells, 2)))
        dc = DI.classify(sizes, edges)              # the stratum: which of the predictor's readings a start needs
        if dc == 'in': self.stratum = 'proved class'
        elif dc == 'one loose': self.stratum = 'one loose distinction'
        elif not self.cells: self.stratum = 'repeated blocks only'
        elif self.overlap[1]: self.stratum = 'group cells sharing two knots'
        elif self.overlap[0]: self.stratum = 'a block meeting a group cell in two knots'
        elif any(G & G2 for G, G2 in itertools.combinations(self.cells, 2)): self.stratum = 'group cells sharing a knot'
        else: self.stratum = 'group cells'
        self.adj = collections.defaultdict(set); self.chains = {}
        blocks = [tuple(sorted(B)) for B in blocks]
        hyper = blocks + [tuple(sorted(G)) for G in self.cells]
        nv = n
        for k in sorted(self.live):
            for _ in range(opn[k] - d[k]):
                hyper.append((k, nv)); self.chains[nv] = R_of(opn[k]); nv += 1
        for H in hyper:
            for a, b in itertools.combinations(H, 2): self.adj[a].add(b); self.adj[b].add(a)
        self.points = sorted(self.live) + list(range(n, nv))
        self.pieces = []                          # (points, is_tree, chains)
        seen = set()
        for p in self.points:
            if p in seen: continue
            comp, st = {p}, [p]
            while st:
                a = st.pop()
                for b in self.adj[a]:
                    if b not in comp: comp.add(b); st.append(b)
            seen |= comp
            hs = [H for H in hyper if H[0] in comp]
            rank = sum(len(H) for H in hs) - len(comp) - len(hs) + 1    # cycles of the incidence graph
            filled = sum(len(set(B) & G) - 1 for B in blocks for G in self.cells if len(set(B) & G) >= 2 and B[0] in comp)
            tree = rank == filled                 # a tree once a block meeting a group in m knots is read as m - 1 cycles
            self.pieces.append((sorted(comp), tree, sum(self.chains.get(q, 0) for q in comp)))


def connected_sets(points, adj):
    """every connected subset of points (adjacency adj restricted to points), each once"""
    P = set(points); order = {p: i for i, p in enumerate(sorted(points, key=str))}
    for r in sorted(points, key=str):
        def rec(S, ext, banned):
            yield S
            ext = list(ext)
            for i, w in enumerate(ext):
                S2 = S | {w}; b2 = banned | set(ext[:i + 1])
                new = [u for u in adj[w] if u in P and order[u] > order[r] and u not in S2 and u not in b2
                       and u not in ext]
                yield from rec(S2, ext[i + 1:] + new, b2)
        yield from rec(frozenset([r]), [u for u in adj[r] if u in P and order[u] > order[r]], frozenset([r]))


class Piece:
    """the configurations (C, E) of one piece and their kinds.  A set is VALID when it is connected, holds a knot, and
    holds one knot or none of each group cell, or all of it; its SIZE is its number of points less g - 2 for each
    whole cell of g knots it holds (a group is born in round 1).  Its parents are its valid subsets of size one less
    that leave every extended chain attached: one point removed, or a whole cell cut to one of its knots; its fresh
    distinctions are its ways to grow by one: an outside point, the rest of a cell it meets once, or one step along a
    chain.  A relay piece is a piece of its own (see predict)."""
    def __init__(self, pts, adj, chains, is_knot, single_type, weight, cells=()):
        self.pts, self.adj, self.chains, self.is_knot = pts, adj, chains, is_knot
        self.single_type, self.weight = single_type, weight
        self.cells = [G for G in cells if G <= set(pts)]
        self.memo = {}

    def connected(self, S):
        st = [next(iter(S))]; seen = {st[0]}
        while st:
            a = st.pop()
            for b in self.adj[a] & S:
                if b not in seen: seen.add(b); st.append(b)
        return len(seen) == len(S)

    def valid(self, S):
        return (bool(S) and any(self.is_knot(x) for x in S) and all(len(S & G) <= 1 or G <= S for G in self.cells)
                and self.connected(S))

    def size(self, S):
        return sum(self.weight(v) for v in S) - sum(len(G) - 2 for G in self.cells if G <= S)

    def parent_sets(self, C, E):
        bases = {e[0] for e in E}; z = self.size(C) - 1; out = set()
        for v in C:
            T = C - {v}
            if v not in bases and self.valid(T) and self.size(T) == z: out.add(T)
        for G in self.cells:
            if G <= C:
                for u in G:
                    T = C - (G - {u})
                    if bases <= T and self.valid(T) and self.size(T) == z: out.add(T)
        return out

    def kind(self, C, E):
        """(parents, fresh) of the set C with one point along each chain in E (E: tuples (pendant, index))"""
        key = (C, E)
        if key in self.memo: return self.memo[key]
        par = len(E) + len(self.parent_sets(C, E))
        bd, covered = 0, set()
        for G in self.cells:
            if len(C & G) == 1:
                covered |= G
                if self.valid(C | G): bd += 1
        for v in set().union(*(self.adj[v] for v in C)) - C:
            if v not in covered and self.valid(C | {v}): bd += 1
        bd += sum(self.chains.get(v, 0) for v in C)    # each chain at C: its first point, or the point past its tip
        self.memo[key] = (par, bd)
        return par, bd

    def sig0(self, C, E):
        if not E and len(C) == 1: return self.single_type(next(iter(C)))
        p, f = self.kind(C, E)
        return ('offshoot' if p == 1 else 'join', p, f, p + f)

    def parent_sigs(self, C, E, J):
        """sorted sig0 of the parents of (C, E) with the chains in J at length exactly 1"""
        out = [self.sig0(C, E - {e}) if e in J else self.sig0(C, E) for e in E]
        out += [self.sig0(T, E) for T in self.parent_sets(C, E)]
        return tuple(sorted(out))

    def configs(self):
        """(C, E, size of C) for every valid C and every set E of chains leaving C"""
        for C in connected_sets(self.pts, self.adj):
            if not self.valid(C): continue
            ch = [(v, i) for v in sorted(C, key=str) for i in range(self.chains.get(v, 0))]
            w = self.size(C)
            for r in range(len(ch) + 1):
                for E in itertools.combinations(ch, r):
                    yield frozenset(C), frozenset(E), w


class GeneralPiece(Piece):
    """the revised reading found after the frozen test failed (post hoc, not tested on held-out starts): a valid set's
    parents are all its valid subsets of size one less (cutting two cells that share a knot at once included), and its
    fresh distinctions are its valid supersets of size one more within the core, plus one per chain at it"""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.sizes_of = {}
        for C in connected_sets(self.pts, self.adj):
            if self.valid(C): self.sizes_of[frozenset(C)] = self.size(C)
        self.core_parents = {}; self.children = collections.Counter()
        for C, z in self.sizes_of.items():
            ex = sum(len(G) - 2 for G in self.cells if G <= C); out = set()
            for r in range(1, min(len(C) - 1, 1 + ex) + 1):
                for X in itertools.combinations(sorted(C, key=str), r):
                    T = C - frozenset(X)
                    if self.sizes_of.get(T) == z - 1: out.add(T)
            self.core_parents[C] = out
            for T in out: self.children[T] += 1

    def parent_sets(self, C, E):
        bases = {e[0] for e in E}
        return {T for T in self.core_parents[C] if bases <= T}

    def kind(self, C, E):
        key = (C, E)
        if key not in self.memo:
            self.memo[key] = (len(E) + len(self.parent_sets(C, E)),
                              self.children[C] + sum(self.chains.get(v, 0) for v in C))
        return self.memo[key]


def gbinom(m, r):
    """the binomial coefficient as a polynomial in m (any integer m, r >= 0)"""
    out = 1
    for i in range(r): out = out * (m - i)
    return out // factorial(r)


def term_at(t, w, k, j):
    """(count, polynomial part) at round t of the sets of size w with k chains, j of them at length exactly 1 (j = k:
    every chain at length 1; k = 0: the set itself, born in round w - 1)"""
    if k == 0: return (1 if t + 1 == w else 0), 0
    q = k - j
    if q == 0: return (1 if t + 1 - w == k else 0), 0
    m = t - w - k
    return (comb(m, q - 1) if m >= q - 1 else 0), gbinom(m, q - 1)


def predict(stars, rounds, knot_law='nae', ablate=(), static=None, general=False):
    """the predicted rows (round 1..rounds) in the readings sig0 and sig1, or a reason it is not predicted.
    ablate (negative controls only): 'relay' closes every finite piece, 'cells' reads no group cells.  static, a dict,
    receives the stratum, the predicted dimension D and, in each reading, the predicted settling round K: the least
    K >= max(D, 3) with every count, from round K - D + 1 on, equal to its polynomial part (each kind's count is a sum
    of binomial coefficients in the round; its polynomial part continues them below the sizes they start at)"""
    M = Map(stars, knot_law)
    if static is not None: static['stratum'] = M.stratum
    if 'cells' in ablate: M.cells = []
    if M.cls != 'in': return None, M.cls
    if not all(tree for _, tree, _ in M.pieces): return None, 'a piece with a cycle'
    start = lambda v: ('start', 0, 0, M.sizes[v])
    many = len(M.pieces) >= 2
    terms = []                                   # (sig0, sig1, size w, chains k, chains at length 1 j)

    def add(P, C, E, w, bump=False):
        for J in (frozenset(x) for r in range(len(E) + 1) for x in itertools.combinations(sorted(E, key=str), r)):
            s0 = P.sig0(C, E)
            if bump: s0 = (s0[0], s0[1], s0[2] + 1, s0[3] + 1)
            terms.append((s0, s0 + (P.parent_sigs(C, E, J),), w, len(E), len(J)))
            if not E: break

    for pts, tree, nch in M.pieces:
        P = (GeneralPiece if general else Piece)(pts, M.adj, M.chains, lambda v: v < M.n, start, lambda v: 1, M.cells)
        relay = nch == 0 and (knot_law == 'nae' or many) and 'relay' not in ablate
        whole = frozenset(pts)
        for C, E, w in P.configs():
            add(P, C, E, w, bump=relay and C == whole and not E)
        if relay:                                # the relay: a point with two chains hanging from the whole piece
            Wsig = P.sig0(whole, frozenset()); Wsig = (Wsig[0], Wsig[1], Wsig[2] + 1, Wsig[3] + 1)
            radj = collections.defaultdict(set); radj['W'].add('q'); radj['q'].add('W')
            R = Piece(['W', 'q'], radj, {'q': 2}, lambda v: v == 'W', lambda v: Wsig,
                      lambda v: P.size(whole) if v == 'W' else 1)
            for C, E, w in R.configs():
                if C == frozenset(['W']) and not E: continue
                add(R, C, E, w)
    D = max((k for _, _, _, k, _ in terms), default=0)
    H = max(rounds, max((w + k for _, _, w, k, _ in terms), default=0) + 1)
    rows = [collections.Counter() for _ in range(H + 1)], [collections.Counter() for _ in range(H + 1)]
    poly = [collections.Counter() for _ in range(H + 1)], [collections.Counter() for _ in range(H + 1)]
    for s0, s1, w, k, j in terms:
        for t in range(1, H + 1):
            c, p = term_at(t, w, k, j)
            for R, key in ((0, s0), (1, s1)):
                if c: rows[R][t][key] += c
                if p: poly[R][t][key] += p
    if static is not None:
        static['D'] = D
        for R in (0, 1):
            off = [t for t in range(1, H + 1) if +rows[R][t] != +poly[R][t] or any(v < 0 for v in poly[R][t].values())]
            e = max(off) + 1 if off else 1
            static['K%d' % R] = max(e + D - 1, D, 3)
    out = []
    for t in range(1, rounds + 1):
        out.append({'n': sum(rows[0][t].values()),
                    'sig0': sorted([list(k), v] for k, v in rows[0][t].items() if v),
                    'sig1': sorted([[list(k[:4]), [list(x) for x in k[4]]], v] for k, v in rows[1][t].items() if v)})
    return out, 'predicted'


def opener(path):
    return gzip.open(path, 'rt') if path.endswith('.gz') else open(path)


def cnt(row, R):
    return collections.Counter({json.dumps(k): v for k, v in row[R]})


def check(path, out, knot_law='nae', ablate=()):
    res = collections.Counter(); misses = []; bound = collections.Counter(); slack = collections.Counter()
    strata = collections.Counter()
    for l in opener(path):
        x = json.loads(l)
        g = x['rows']; kind = x['kind'].split()[0] if not x['kind'].startswith('dim') else x['kind']
        st = {}
        P, why = predict(x['stars'], len(g), knot_law, ablate, st)
        if P is None:
            res[(kind, 'not predicted: ' + why)] += 1; continue
        if kind.startswith('dim'):              # the predicted settling round, each reading
            D = int(kind.split()[1]); V = phase2.views(x)
            bound[('predicted D', 'equals the observed' if st['D'] == D else 'differs')] += 1
            for R, Kp in (('sig0', st['K0']), ('sig1', st['K1'])):
                K = phase2.settles(V[R], D)
                if Kp > len(g) - 2: bound[(R, 'predicted K past the rounds read')] += 1; continue
                bound[(R, 'K as predicted' if K == Kp else 'K differs')] += 1; slack[(R, (K or 0) - Kp)] += 1
        first = {}
        for R in ('sig0', 'sig1'):
            bad = [t + 1 for t in range(len(g)) if cnt(g[t], R) != cnt(P[t], R)]
            first[R] = bad[0] if bad else None
        ok = first['sig0'] is None and first['sig1'] is None
        res[(kind, 'agree every round' if ok else 'differ')] += 1
        strata[(st['stratum'], 'agree every round' if ok else 'differ')] += 1
        if not ok and len(misses) < 60:
            t = (first['sig0'] or first['sig1']) - 1
            misses.append({'index': x['index'], 'kind': x['kind'], 'stars': x['stars'], 'first differing round': first,
                           'grown': g[t]['sig0'], 'predicted': P[t]['sig0']})
    r = {'tally': {' / '.join(k): v for k, v in sorted(res.items())},
         'by stratum': {' / '.join(k): v for k, v in sorted(strata.items())},
         'settling round': {' / '.join(k): v for k, v in sorted(bound.items())},
         'observed K minus predicted': {'%s / %d' % k: v for k, v in sorted(slack.items())}, 'misses (first 60)': misses}
    json.dump(r, open(out, 'w'), indent=1)
    print(json.dumps({k: r[k] for k in ('tally', 'by stratum', 'settling round', 'observed K minus predicted')}, indent=1))
    print('misses listed:', len(misses))


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        check(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'nae',
              tuple(sys.argv[5].split(',')) if len(sys.argv) > 5 else ())
