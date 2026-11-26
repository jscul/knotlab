"""ring_line.py: direction 1 of the report at the first checkpoint of SHORT-AGAIN-20261126-001 (report_1.md): the ring
of five that returns, at one end of a line of waiting knots, the seven-knot source at the other.  Does a change pass
each time the ring comes round?  RING_LINE.md has the design and the expectations, written before the full run.

A start is the source (A) and the ring (B) joined by a meeting through d - 1 link knots (bench.py, `build`), or the
source with a stub in place of the ring.  Laws, short knots waiting in each:
    CAP-3          the ring's law (the two added rules of RING-IN-BALANCE: a cap of three, waiting with release)
    REC-ONE-FEWER  the record's "one fewer than asked" (RING-IN-BALANCE definitions, step 7: none at least where three
                   places are given), under which the ring also returns
    ONE-FEWER      the far table's (rations.py: one at least)
    JOIN-FEWER     the far table's other carrier (rations.py)
    ORD            the ordinary count, the baseline
Read each round: knots; short members and births by whose knot it is (A's own, B's own, link side, joint); A's own
births (name, fresh, places) as reach.py reads them; and the parts of the roster, for the ring's returns (a part Y of
B's own knots after round s returns at t > s when the members after round t that descend from Y include a part the
same as Y, up to renaming, with each member's usable and barred counts: RING-IN-BALANCE definitions).

    ring_line.py look D LAW          one start, printed round by round
    ring_line.py run D LAW           the whole reading for one start and law, as one JSON line"""
import sys, os, json, collections, hashlib, time
import networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rations, reach
bench, eng = rations.bench, rations.eng

ROUNDS, BOUND = 16, 3000


class RecOneFewer(eng.Law):
    """the record's ONE-FEWER (RING-IN-BALANCE definitions, step 7): f = min(q, max(3 - p, 0, q - 1)), q = max(D, 3 - p, 1)"""
    def __init__(self, treatment, take=None):
        eng.Law.__init__(self, 'ORD', treatment, take, 'nae')
    def fresh(self, kind, p, D, o):
        q = max(D, 3 - p, 1)
        return min(q, max(3 - p, 0, q - 1))
    def name(self):
        return 'REC-ONE-FEWER/%s/RELEASE/no-take/nae' % self.treatment

bench.LAWS['REC-ONE-FEWER'] = lambda treatment, take: RecOneFewer(treatment, take)
LAWS = ['CAP-3', 'REC-ONE-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'ORD']


def law_of(ration, treatment='CANCEL-WAIT'):
    return bench.LAWS[ration](treatment, None) if ration in bench.LAWS else eng.Law(ration, treatment, None, 'nae')


def cls(a):
    return 'A' if a == frozenset(['A']) else 'B' if a == frozenset(['B']) else 'joint' if ('A' in a and 'B' in a) else 'link'


class Growth(bench.Growth):
    """bench.Growth, keeping each round's structure (the starts here stay under a few thousand knots) and reading what
    the returns and the marks need"""
    def __init__(self, stars, role, law):
        bench.Growth.__init__(self, stars, role, law)
        self.snaps = [self.S.copy()]

    def step(self):
        T = self.S.copy()
        try: rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T; anc, name = self.anc, self.name
        short = set(rec['short'])
        sh = collections.Counter(cls(anc[u]) for u in short)
        bc = collections.Counter(); own = []; seen = collections.Counter()
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            name[b['id']] = n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]
            c = cls(a); bc[c] += 1
            if c == 'A': own.append((n, b['f'], len(S.places[b['id']])))
        own.sort()
        self.rows.append({'round': S.round, 'knots': S.n_knots, 'short': len(short), 'short by': dict(sh), 'births by': dict(bc),
                          'own': [len(own), hashlib.sha1(repr(own).encode()).hexdigest()[:12]]})
        self.snaps.append(S.copy())
        return True


def roster_of(S):
    G = eng.Guard(1000)
    return eng.build_roster(S, eng.live_members(S), 'look', G, parts=True)


def part_graph(R, P):
    """members coloured (h, k), one vertex per inclusion-maximal met set within the part (as RING-IN-BALANCE)"""
    ms = set(P); G = nx.Graph()
    for u in P: G.add_node(('m', u), c='m%d,%d' % (R.h[u], R.k[u]))
    for i, M in enumerate(R.maxsets):
        if next(iter(M)) in ms:
            G.add_node(('s', i), c='s')
            for u in M: G.add_edge(('s', i), ('m', u))
    return G


def same(R1, P1, R2, P2):
    if len(P1) != len(P2) or sorted((R1.h[u], R1.k[u]) for u in P1) != sorted((R2.h[u], R2.k[u]) for u in P2): return False
    return nx.is_isomorphic(part_graph(R1, P1), part_graph(R2, P2), node_match=lambda a, b: a['c'] == b['c'])


def returns(g, least=5, who='B'):
    """the returns of parts of B's own knots with at least `least` members, least s first, then least t: [(s, t, part at
    s, part at t)].  Descent: a new knot descends from what its parents descend from; a member that waits, from itself;
    the part at t must descend from Y alone (the advisor's point: in a growth that multiplies, a part the same as Y can
    turn up elsewhere).
    A part made of the very knots of Y (every one waited) is not counted as a return: a held part is the same after
    every round."""
    snaps = g.snaps; R = [roster_of(S) for S in snaps]; out = []
    for s in range(1, len(snaps) - 1):
        cand = [P for P in R[s].parts if len(P) >= least and all(cls(g.anc[u]) == who for u in P)]
        for Y in cand:
            # what each knot descends from among the members after round s: Y, others, or both
            lab = {u: ('Y' if u in Y else 'o') for u in R[s].members}
            for t in range(s + 1, len(snaps)):
                S = snaps[t]
                for x in range(snaps[t - 1].n_knots, S.n_knots):
                    ls = {lab.get(p, 'o') for p in S.parents[x]}; lab[x] = 'Y' if ls == {'Y'} else 'o'
                hit = next((P for P in R[t].parts if set(P) != set(Y) and all(lab.get(u) == 'Y' for u in P) and same(R[s], Y, R[t], P)), None)
                if hit is not None:
                    out.append((s, t, list(Y), list(hit))); break
    return out


def grow(d, ration, B='ring', rounds=ROUNDS, bound=BOUND, stars=None):
    if stars is None: stars, role = bench.build('source', B, d, None, 'meeting')
    else: stars, role = stars
    g = Growth(stars, role, law_of(ration)); g.run(rounds, bound); return g


def fork_at(g, c):
    """the growth g as it stood after round c, ready to be marked and grown on"""
    h = Growth.__new__(Growth); h.law = g.law; h.G = eng.Guard(bench.MULT); h.S = g.snaps[c].copy()
    h.anc = {u: a for u, a in g.anc.items() if u < h.S.n_knots}; h.name = {u: n for u, n in g.name.items() if u < h.S.n_knots}
    h.rows = list(g.rows[:c]); h.snaps = list(g.snaps[:c + 1]); h.stop = None
    return h


def mark(h, u):
    """one more loose distinction at knot u"""
    S = h.S; x = len(S.holders)
    S.places[u].append(x); S.holders.append([u]); S.barred.append(False); S.maker.append(u)


def first_own_diff(g1, g2, after):
    n = min(len(g1.rows), len(g2.rows))
    return next((g1.rows[i]['round'] for i in range(after, n) if g1.rows[i]['own'] != g2.rows[i]['own']), None), n


def nearest(g, c, who='B', n=5):
    """the n members of `who`'s own knots after round c nearest, in sharings, to a knot that is not theirs"""
    S = g.snaps[c]; adj = collections.defaultdict(set)
    for hs in S.holders:
        for u in hs:
            adj[u].update(v for v in hs if v != u)
    dist = {u: 0 for u in range(S.n_knots) if cls(g.anc[u]) != who}; fr = list(dist)
    while fr:
        nx_ = []
        for u in fr:
            for v in adj[u]:
                if v not in dist: dist[v] = dist[u] + 1; nx_.append(v)
        fr = nx_
    mem = [u for u, h, k in eng.live_members(S) if cls(g.anc[u]) == who]
    return sorted(mem, key=lambda u: (dist.get(u, 10 ** 6), u))[:n]


def marked(g, c, u):
    h = fork_at(g, c); mark(h, u); h.run(ROUNDS, BOUND); return h


def series(g):
    return {'knots': [r['knots'] for r in g.rows], 'short by': [r['short by'] for r in g.rows],
            'births by': [r['births by'] for r in g.rows], 'own births': [r['own'][0] for r in g.rows]}


def run(d, ration, join):
    t0 = time.time()
    whole = grow(d, ration, stars=bench.build('source', 'ring', d, None, join))
    stub = grow(d, ration, stars=bench.build('source', 'stub', d, None, join))
    n = min(len(whole.rows), len(stub.rows))
    out = {'d': d, 'law': ration, 'join': join, 'rounds': len(whole.rows), 'ended': whole.stop or 'rounds',
           'whole': series(whole), 'stub': series(stub),
           'own births differ from with a stub, rounds': [whole.rows[i]['round'] for i in range(n) if whole.rows[i]['own'] != stub.rows[i]['own']]}
    rets = returns(whole)
    out['ring returns'] = [[s, t, len(Y)] for s, t, Y, P in rets]
    # the changes: at each round the ring has come back (the members of the part that returned), or, where it never
    # does, after rounds 2, 4, ..., 12 at the five members of the ring's own knots nearest the line
    at = {}
    for s, t, Y, P in rets:
        if t not in at and t < len(whole.rows): at[t] = P
    if not at:
        at = {c: nearest(whole, c) for c in range(2, 13, 2) if c < len(whole.rows)}
    out['changes from'] = 'returns' if rets else 'rounds'
    out['marks'] = []
    heard_first = None
    for c in sorted(at)[:6]:
        for u in at[c]:
            h = marked(whole, c, u); r, m = first_own_diff(whole, h, c)
            out['marks'].append([c, u, r, m])
            if r is not None and heard_first is None: heard_first = (c, u, r, h)
    # sent again: in the growth marked first, a second change at the five members of the ring's own knots nearest the
    # line, the round after the first was heard; then a third the round after the second
    out['again'] = []
    if heard_first is not None:
        c, u, r, h = heard_first
        for _ in range(2):
            c2 = r + 1
            if c2 >= len(h.rows): break
            got = None
            for v in nearest(h, c2):
                h2 = marked(h, c2, v); r2, m2 = first_own_diff(h, h2, c2)
                out['again'].append([c2, v, r2, m2])
                if r2 is not None and got is None: got = (r2, h2)
            if got is None: break
            r, h = got
    out['seconds'] = round(time.time() - t0, 1)
    return out


def look(d, ration, join='meeting'):
    g = grow(d, ration, stars=bench.build('source', 'ring', d, None, join))
    for r in g.rows: print(r['round'], r['knots'], 'short', r['short by'], 'births', r['births by'])
    for s, t, Y, P in returns(g): print('return', s, t, len(Y))


if __name__ == '__main__':
    if sys.argv[1] == 'look': look(int(sys.argv[2]), sys.argv[3], *(sys.argv[4:5]))
    elif sys.argv[1] == 'run': print(json.dumps(run(int(sys.argv[2]), sys.argv[3], sys.argv[4])))
