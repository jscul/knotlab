"""amount.py: how much of a change arrives.  HOW-MUCH-ARRIVES-20261126-001 (a check by the thread, not registered);
README.md has the design and the expectations, written before the full run and revised once with the advisor.

A growth G and the same growth G' with one change are grown side by side.  Each birth is read three ways:
    name   how it was made: kind, parents' names, number among equal births of the round, from the start knots'
           names (the two-pattern bench's reading), with its fresh distinctions and places.  Hereditary: a birth
           whose parent was new is new.
    sig0   kind, number of parents, fresh distinctions, places: ancestry-free.
    sig1   sig0 and the sorted sig0 of its parents: ancestry-free, one parent step deep.
In each round t, for each reading, the DAMAGE is the number of births of G' with no match in G that round plus the
number of G with no match in G' (differences of multisets), against n + n', the births of both that round.  The
DESCENT is the births of G' with a changed knot among their ancestors.  For a change with a focus knot u, each birth
of round t is also placed by its distance from u in holder steps (knots sharing a distinction), in the structure as
it stands after round t, in G for G's births and in G' for G''s; the damage is then counted shell by shell.

Changes (setting A, the ordinary count):
    mark   one more loose distinction at start knot i
    move   one loose distinction taken from start knot i and given to start knot j
    made   one more loose distinction at a knot made in round s, each such knot in turn (at most MADE_CAP)
    pulse  as made, and after round s + 1 every knot made that round that holds the added distinction has its
           usable loose distinctions barred: the change is struck after one round
    pair   two made marks at once in round 2 (two-touching and chain3), against each alone

    amount.py list                 the jobs of setting A, one JSON per line
    amount.py one JOB_JSON         one job, one JSON line
"""
import sys, os, json, hashlib, collections, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
import eng

ROUNDS, BOUND = 16, 20000
READINGS = ('name', 'sig0', 'sig1')


def ring(n, loose):
    nxt, st = n, []
    for i in range(n):
        k = [(i - 1) % n, i]
        for _ in range(loose):
            k.append(nxt); nxt += 1
        st.append(k)
    return st


STARTS = {
    'ring5-bare': ring(5, 2),
    'ring7-bare': ring(7, 2),
    'two-touching': [[0, 1, 2], [0, 3, 4]],
    'chain3': [[0, 1, 2], [1, 3, 4], [3, 5, 6]],
    'ring5-eddy': ring(5, 3),
    'generator7': [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20],
                   [7, 8, 21, 22], [5, 8, 23, 24]],
}
MADE_ROUNDS = (2, 4)
MADE_CAP = 40
PAIR_STARTS = ('two-touching', 'chain3')


def loose_of(stars):
    cnt = collections.Counter(d for k in stars for d in k)
    return [[d for d in k if cnt[d] == 1] for k in stars]


class Growth:
    """one start grown round by round under one law, keeping each round's births in the three readings, their ids,
    and which have a watched knot among their ancestors"""

    def __init__(self, stars, law):
        self.law, self.G, self.S = law, eng.Guard(100), eng.from_stars(stars)
        n = len(stars)
        self.name = {i: 'S%d' % i for i in range(n)}
        self.sig0 = {i: ('start', 0, 0, len(stars[i])) for i in range(n)}
        self.rows, self.stop, self.anc, self.struck = [], None, {}, None

    def fork(self):
        g = Growth.__new__(Growth)
        g.law, g.G, g.S = self.law, eng.Guard(100), self.S.copy()
        g.name, g.sig0, g.rows, g.stop = dict(self.name), dict(self.sig0), list(self.rows), self.stop
        g.anc, g.struck = dict(self.anc), self.struck
        return g

    def watch_knots(self, us):
        for u in us: self.anc[u] = True

    def mark(self, u):
        """one more loose distinction at knot u; returns the distinction"""
        S = self.S
        d = len(S.holders)
        S.holders.append([u]); S.barred.append(False); S.maker.append(u); S.places[u].append(d)
        S.basis = {}
        for k in range(S.n_knots):
            eng.basis_insert(S.basis, eng.row_of(S.places[k]))
        self.sig0[u] = self.sig0[u][:3] + (len(S.places[u]),)
        self.watch_knots([u])
        return d

    def strike(self, d):
        """bar every usable loose distinction of every knot made in the last round that holds distinction d"""
        S = self.S; n = 0
        for x in S.holders[d]:
            if S.made[x] == S.round:
                for e in S.usable(x):
                    S.barred[e] = True; n += 1
        return n

    def step(self):
        T = self.S.copy()
        try:
            rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T
        seen, out = collections.Counter(), []
        for b in rec['births']:
            ps = tuple(sorted(self.name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            nm = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]
            u = b['id']; self.name[u] = nm
            s0 = (b['kind'], len(b['parents']), b['f'], len(S.places[u])); self.sig0[u] = s0
            s1 = s0 + (tuple(sorted(self.sig0[p] for p in b['parents'])),)
            a = any(self.anc.get(p, False) for p in b['parents']); self.anc[u] = a
            out.append({'id': u, 'name': (nm, b['f'], len(S.places[u])), 'sig0': s0, 'sig1': s1, 'desc': a})
        self.rows.append({'births': out, 'short': len(rec['short']), 'knots': S.n_knots})
        return True

    def run(self, rounds=ROUNDS, bound=BOUND):
        while self.stop is None and self.S.round < rounds:
            if not self.step(): break
            if not self.rows[-1]['births']:
                self.stop = 'closed'; break
            if self.S.n_knots > bound: self.stop = 'knots'
        return self

    def distances(self, u, t):
        """holder-step distance from knot u of every knot made by round t, in the structure after round t"""
        S = self.S
        made = S.made
        dist = {u: 0}; frontier = [u]
        while frontier:
            nxt = []
            for x in frontier:
                for d in S.places[x]:
                    for y in S.holders[d]:
                        if y not in dist and made[y] <= t:
                            dist[y] = dist[x] + 1; nxt.append(y)
            frontier = nxt
        return dist


def diff(a, b):
    A, B = collections.Counter(a), collections.Counter(b)
    return sum((B - A).values()), sum((A - B).values())


def compare(g, h, after=0, focus=None):
    """per round after `after`: n, n', and for each reading [c, c-] (G' unmatched, G unmatched); desc; and, with a
    focus knot, the sig1 damage by holder-step shell: {shell: [births of G, of G', damage]}"""
    out = []
    for i in range(after, min(len(g.rows), len(h.rows))):
        bg, bh = g.rows[i]['births'], h.rows[i]['births']
        row = {'round': i + 1, 'n': len(bg), "n'": len(bh), 'desc': sum(1 for x in bh if x['desc'])}
        for R in READINGS:
            row[R] = list(diff([x[R] for x in bg], [x[R] for x in bh]))
        if focus is not None:
            dg, dh = g.distances(focus, i + 1), h.distances(focus, i + 1)
            shells = collections.defaultdict(lambda: [[], []])
            for x in bg: shells[dg.get(x['id'], -1)][0].append(x['sig1'])
            for x in bh: shells[dh.get(x['id'], -1)][1].append(x['sig1'])
            row['shells'] = {str(r): [len(a), len(b), sum(diff(a, b))] for r, (a, b) in sorted(shells.items())}
        out.append(row)
    return out


def verdict(rows, R):
    """the README's verdicts on the damage both ways in reading R, over the rounds read (at least eight)"""
    if len(rows) < 8: return 'too few rounds'
    c = [sum(r[R]) for r in rows]; n = [r['n'] + r["n'"] for r in rows]
    half = len(rows) // 2
    if all(x == 0 for x in c[half:]): return 'dies out'
    if all(x >= 0.95 * m and m > 0 for x, m in zip(c[-4:], n[-4:])): return 'takes over'
    if n[-1] <= n[half]:
        return 'bounded' if c[-1] <= c[half] else 'grows'
    if c[-1] <= c[half] and n[-1] >= 1.5 * n[half]: return 'weakens'
    return 'holds'


def summary(rows):
    return {R: verdict(rows, R) for R in READINGS}


def law_ord(knot_law='nae'):
    return eng.Law('ORD', 'CANCEL-WAIT', None, knot_law)


def jobs():
    J = []
    for name, st in STARTS.items():
        L = loose_of(st)
        for i in range(len(st)):
            J.append({'start': name, 'change': 'mark', 'at': i})
        for i in range(len(st)):
            if not L[i]: continue
            for j in range(len(st)):
                if j != i: J.append({'start': name, 'change': 'move', 'at': [i, j]})
        for s in MADE_ROUNDS:
            J.append({'start': name, 'change': 'made', 'round': s})
            J.append({'start': name, 'change': 'pulse', 'round': s})
    for name in PAIR_STARTS:
        J.append({'start': name, 'change': 'pair', 'round': 2})
    return J


def made_in(g, s, n_start):
    return [u for u in range(len(g.S.places)) if u >= n_start and g.S.made[u] == s]


def run_job(job, knot_law='nae'):
    t0 = time.time()
    st = [list(k) for k in STARTS[job['start']]]
    law = law_ord(knot_law)
    base = Growth(st, law)
    res = dict(job)
    if job['change'] in ('mark', 'move'):
        base.run()
        ch = [list(k) for k in st]
        if job['change'] == 'mark':
            i = job['at']; ch[i].append(1 + max(d for k in st for d in k)); focus, watched = i, [i]
        else:
            i, j = job['at']; d = loose_of(st)[i][-1]; ch[i].remove(d); ch[j].append(d); focus, watched = None, [i, j]
        g = Growth(ch, law); g.watch_knots(watched); g.run()
        rows = compare(base, g, focus=focus)
        res.update(rows=rows, verdicts=summary(rows), base_stop=base.stop, stop=g.stop)
    else:
        s = job['round']
        while base.S.round < s and base.stop is None:
            base.step()
        made = made_in(base, s, len(st))
        snap = base.fork()
        base.run()
        if job['change'] in ('made', 'pulse'):
            marks = []
            for u in made[:MADE_CAP]:
                g = snap.fork(); d = g.mark(u)
                if job['change'] == 'pulse':
                    if g.step(): g.struck = g.strike(d)
                g.run()
                rows = compare(base, g, after=s, focus=u)
                marks.append({'knot': u, 'struck': g.struck, 'rows': rows, 'verdicts': summary(rows), 'stop': g.stop})
            res.update(made=len(made), marked=len(marks), marks=marks)
        else:                                                    # pair: every pair of knots made in round s
            alone = {}
            for u in made:
                g = snap.fork(); g.mark(u); g.run(); alone[u] = g
            pairs = []
            for u, v in itertools.combinations(made, 2):
                g = snap.fork(); g.mark(u); g.mark(v); g.run()
                last = min(len(base.rows), len(g.rows), len(alone[u].rows), len(alone[v].rows)) - 1
                dam = {}
                for R in READINGS:
                    dam[R] = [sum(diff([x[R] for x in base.rows[last]['births']], [x[R] for x in h.rows[last]['births']]))
                              for h in (alone[u], alone[v], g)]
                pairs.append({'knots': [u, v], 'round': last + 1, 'damage u, v, both': dam})
            res.update(made=len(made), pairs=pairs)
        res['base_stop'] = base.stop
    res['base counts'] = [len(r['births']) for r in base.rows]
    res['knot law'] = knot_law
    res['seconds'] = round(time.time() - t0, 1)
    return res


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        for j in jobs(): print(json.dumps(j))
    elif sys.argv[1] == 'one':
        job = json.loads(sys.argv[2])
        print(json.dumps(run_job(job, job.get('knot law', 'nae'))))
