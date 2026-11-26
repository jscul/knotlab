"""jam.py: is hearing from afar the end of a jam?  Second study after the first checkpoint of SHORT-AGAIN-20261126-001
(directions 2 and 3 of report_1.md).  JAM.md has the design, the rule under test and the expectations, written
before the full run.

The far table's two sources, joined through a line under JOIN-FEWER or ONE-FEWER with waiting, make nothing after
round 1: every member is short and waits, through round 16.  A change at the other end lets one knot act, and the
receiver's own knots then hear it.  The rule under test: under waiting, a change two or more steps away is heard by
a pattern's own knots only in a round in which those knots are JAMMED (the pattern still has members, and every one
of them is short and waits: the record's "jammed", said of a pattern's own knots) in the growth with the change or in
the one without.

Receivers and senders: the census's 44 sited starts of one to three knots and the bench's three patterns (ring,
copier, source), every ordered pair, joined by a meeting through D - 1 link knots.  Laws: JOIN-FEWER, ONE-FEWER
(rations.py), the record's one fewer and a cap of three (ring_line.py), "just enough for three places" (FLOOR1)
and the ordinary count, a short knot waiting; and JOIN-FEWER with a short knot retiring, as the control (no knot
can stay jammed).  Changes, as reach.py: one more loose distinction at each start knot of B and at each link knot; and, the change of
the other sign (the advisor's), one of its usable loose distinctions barred there.  A stub as sender as well.
Read, for the growth without a change and each change: A's own members and A's own short members in each round,
A's own births; for each change, the first round A's own births differ.

    jam.py list
    jam.py pair I J D [JOIN]    every law for receiver I and sender J (indices of `list`; 47 is a stub), a line a law"""
import sys, os, json, collections, time, hashlib, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ring_line, reach
bench, eng = ring_line.bench, ring_line.eng
sys.path.insert(0, os.path.join(HERE, '..', 'TWO-PATTERNS-20261126-001', 'census'))
import census

ROUNDS, BOUND = 12, 1500
LAWS = [('JOIN-FEWER', 'CANCEL-WAIT'), ('ONE-FEWER', 'CANCEL-WAIT'), ('REC-ONE-FEWER', 'CANCEL-WAIT'), ('CAP-3', 'CANCEL-WAIT'),
        ('FLOOR1', 'CANCEL-WAIT'), ('ORD', 'CANCEL-WAIT'), ('JOIN-FEWER', 'CANCEL-RETIRE')]


def starts():
    """[(name, stars, site)]: the census's sited starts, then the bench's three patterns"""
    out = list(census.sited())
    for P in ('ring', 'copier', 'source'): out.append((P, bench.STARS[P], bench.SITE[P]))
    for name, stars, site in out: bench.STARS[name], bench.SITE[name] = stars, site
    return out


def depth(P):
    """sharings from P's site to each of its start knots"""
    st = bench.STARS[P]; s = bench.SITE[P]; dist = {s: 0}; fr = [s]
    while fr:
        nx_ = []
        for u in fr:
            for v in range(len(st)):
                if v not in dist and set(st[u]) & set(st[v]): dist[v] = dist[u] + 1; nx_.append(v)
        fr = nx_
    return [dist.get(v) for v in range(len(st))]


class Growth(bench.Growth):
    """bench.Growth reading, each round, A's own members and short members, A's own births (as reach.py) and all births"""
    def step(self):
        T = self.S.copy()
        try: rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T; anc, name = self.anc, self.name
        A = frozenset(['A']); short = set(rec['short'])
        memA = [u for u in rec['members'] if anc[u] == A]
        own = []; seen = collections.Counter()
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            name[b['id']] = n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]
            if a == A: own.append((n, b['f'], len(S.places[b['id']])))
        own.sort()
        owe, h = rec['owe'], rec['h']
        gapA = collections.Counter(str(owe[u] - h[u]) for u in memA if u in short)
        gap = collections.Counter(str(owe[u] - h[u]) for u in short)
        self.rows.append({'round': S.round, 'knots': S.n_knots, 'births': len(rec['births']), 'A members': len(memA),
                          'A short': sum(1 for u in memA if u in short), 'own': [len(own), hashlib.sha1(repr(own).encode()).hexdigest()[:12]],
                          'A shortfall': dict(gapA), 'shortfall': dict(gap)})
        return True


def jammed(row):
    return row['A members'] > 0 and row['A short'] == row['A members']


def law_of(ration, treatment):
    return bench.LAWS[ration](treatment, None) if ration in bench.LAWS else eng.Law(ration, treatment, None, 'nae')


def changed(A, B, d, change, join):
    """stars, roles and the knot at which one loose distinction is to be barred (or None).  A change is (kind, i):
    'B' one more loose distinction at start knot i of B, 'L' at the i-th link knot; 'bB' and 'bL' one barred there."""
    stars, role = bench.build(A, B, d, None, join)
    if change is None: return stars, role, None
    nxt = 1 + max(x for k in stars for x in k); kind, i = change
    k = role.index('B') + i if kind[-1] == 'B' else [q for q, r in enumerate(role) if r == 'link'][i - 1]
    if kind[0] == 'b': return stars, role, k
    stars[k].append(nxt); return stars, role, None


def case(A, B, d, ration, treatment, join='meeting'):
    law = law_of(ration, treatment)
    def grown(change):
        st, ro, bar = changed(A, B, d, change, join); g = Growth(st, ro, law)
        if bar is not None:
            us = g.S.usable(bar)
            if not us: return None
            g.S.barred[us[-1]] = True
        g.run(ROUNDS, BOUND); return g
    whole = grown(None); dep = [0] if B == 'stub' else depth(B)
    nB = 1 if B == 'stub' else len(bench.STARS[B])
    out = {'A': A, 'B': B, 'd': d, 'join': join, 'law': [ration, treatment], 'rounds': len(whole.rows), 'ended': whole.stop or 'rounds',
           'knots': whole.rows[-1]['knots'], 'births': [r['births'] for r in whole.rows],
           'A members': [r['A members'] for r in whole.rows], 'A short': [r['A short'] for r in whole.rows],
           'own births': [r['own'][0] for r in whole.rows], 'A shortfall': [r['A shortfall'] for r in whole.rows],
           'shortfall': [r['shortfall'] for r in whole.rows], 'changes': []}
    chs = [(kind, j, d + dep[j]) for kind in ('B', 'bB') for j in range(nB)] + [(kind, k, k) for kind in ('L', 'bL') for k in range(1, d)]
    for kind, i, dist in chs:
        g = grown((kind, i))
        if g is None: continue
        n = min(len(whole.rows), len(g.rows))
        r = next((i2 for i2 in range(n) if whole.rows[i2]['own'] != g.rows[i2]['own']), None)
        c = {'at': '%s%d' % (kind, i), 'distance': dist, 'heard': None if r is None else whole.rows[r]['round'], 'rounds': n}
        if r is not None:
            w, x = whole.rows[r], g.rows[r]
            c.update({'jammed without': jammed(w), 'jammed with': jammed(x), 'waiting own without': w['A short'] > 0, 'waiting own with': x['A short'] > 0,
                      'jammed without, round before': None if r == 0 else jammed(whole.rows[r - 1]),
                      'A short with': [y['A short'] for y in g.rows], 'own births with': [y['own'][0] for y in g.rows]})
        out['changes'].append(c)
    return out


SEED = 20261126
def sample(n=400):
    """a sample of ordered pairs (receiver 0..46, sender 0..47), seed SEED"""
    pairs = [(i, j) for i in range(47) for j in range(48)]
    return sorted(random.Random(SEED).sample(pairs, n))


if __name__ == '__main__':
    S = starts() + [('stub', None, None)]
    if sys.argv[1] == 'list':
        for k, (name, stars, site) in enumerate(S): print(k, name, stars, 'site', site, 'depth', depth(name) if stars else [0])
    elif sys.argv[1] == 'pair':
        i, j, d = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); join = sys.argv[5] if len(sys.argv) > 5 else 'meeting'
        for ration, treatment in LAWS:
            t0 = time.time(); r = case(S[i][0], S[j][0], d, ration, treatment, join); r['seconds'] = round(time.time() - t0, 2)
            print(json.dumps(r), flush=True)
