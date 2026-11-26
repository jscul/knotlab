"""bench.py: two lasting patterns joined in one start, and what each one's own knots make with the other there.
First direction of TWO-PATTERNS-20261126-001 (a check by the thread, not registered).  See README.md for the
readings and for the expectations, which were written there before the first full run.

A pattern is a start of the record with one of its knots named as its site:
    ring     the ring of five knots, each sharing one distinction with each neighbour and holding three loose
             (the fold study's Ring(5,3); it returns under a cap of three with waiting)
    copier   two knots sharing one distinction, each holding two loose (the two-knot start; it copies itself under
             "just enough for three places")
    source   the generator study's seven knots (it keeps releasing families under the ordinary count)
Two patterns A and B are joined at n steps, in one of two ways (see `build`): at one step their sites meet (through
a spent knot, each site supplied for it; or by sharing one new distinction, nothing supplied); at two steps one
link knot sits between them, at three steps two.  A STUB in place of a pattern is the least knot that can hold the
other end.  A MARK at a knot is one more loose distinction there.

A knot's descent is read from its start ancestors: `own A` when every one is a knot of A, `of B` when any is a
knot of B (or of the stub standing for B), and likewise with A and B exchanged.  A knot is named by how it was made
(kind, parents' names, number among equal births of the round), from the names of its own pattern's start knots,
so an own knot of A has the same name whatever A is joined to.  The JOINT DESCENT is every knot with a start knot
of A and one of B among its ancestors."""
import sys, os, json, hashlib, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('PROBE_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
import eng

STARS = {
    'ring': [[4, 0, 5, 6, 7], [0, 1, 8, 9, 10], [1, 2, 11, 12, 13], [2, 3, 14, 15, 16], [3, 4, 17, 18, 19]],
    'copier': [[0, 1, 2], [0, 3, 4]],
    'source': [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20],
               [7, 8, 21, 22], [5, 8, 23, 24]],
}
SITE = {'ring': 0, 'copier': 0, 'source': 0}
MULT = 100
# rations added by a later study: name -> a function (treatment, take) giving a law of the engine's kind.  Empty here.
LAWS = {}

def build(A, B, steps, mark=None, join='meeting', site_a=None, site_b=None):
    """stars and each start knot's role.  A: a pattern's name or 'stub'.  B: a pattern's name, 'stub', or None (nothing
    joined: the bare pattern).  mark: ('A' or 'B', index of a start knot of that pattern), one more loose distinction there.

    join='meeting' (the generator study's way, and the third step's of FAMILIES-THAT-MEET): two knots x, y meet
    through one spent knot of three places, holding one distinction with x and two with y, and each of x and y
    receives one more loose distinction, so that each can afford the one join the meeting asks of it.  A link knot
    is a new knot made only of its two meetings (three shared distinctions and two loose); a stub is a new knot
    made of its one meeting, with loose distinctions up to three places (two shared and one loose where the
    pattern stood second, one shared and two loose where it stood first).  Roles: the spent knots are 'spent'.
    join='share' (the form study's way): the two knots share one new distinction and nothing else is added; a link
    knot holds one distinction toward each side and one loose; a stub holds the link and two loose."""
    stars, role, nxt = [], [], 0
    def put(P, tag):
        nonlocal nxt
        first = len(stars); base = nxt
        stars.extend([base + d for d in k] for k in STARS[P]); role.extend([tag] * len(STARS[P]))
        nxt = base + 1 + max(d for k in STARS[P] for d in k)
        return first
    def new_knot(tag):
        stars.append([]); role.append(tag); return len(stars) - 1
    def meet(x, y):
        nonlocal nxt
        if join == 'share':
            stars[x].append(nxt); stars[y].append(nxt); nxt += 1
        else:
            w = new_knot('spent'); d = nxt; nxt += 5
            stars[w].extend([d, d + 1, d + 2]); stars[x].extend([d, d + 3]); stars[y].extend([d + 1, d + 2, d + 4])
    def pad(k, places):                                           # loose distinctions up to three places
        nonlocal nxt
        while len(stars[k]) < places:
            stars[k].append(nxt); nxt += 1
    # the two ends of the chain: a pattern's site, or a stub standing where the pattern stood (it keeps that role,
    # so that the pattern at the other end has the same names for its knots as when both patterns are there)
    stub_a = (A == 'stub'); stub_b = (B == 'stub')
    a0 = None if stub_a else put(A, 'A')
    b0 = None if (B is None or stub_b) else put(B, 'B')
    if B is not None:
        end = new_knot('A') if stub_a else a0 + (SITE[A] if site_a is None else site_a)
        left = end; links = []
        for _ in range(steps - 1):
            q = new_knot('link'); meet(end, q); links.append(q); end = q
        right = new_knot('B') if stub_b else b0 + (SITE[B] if site_b is None else site_b)
        meet(end, right)
        if join == 'share':
            for q in links: pad(q, 3)
        if stub_a: pad(left, 3)                                 # a stub is a knot of three places: what the join gave it,
        if stub_b: pad(right, 3)                                # and loose distinctions for the rest
    if mark is not None:
        tag, i = mark
        stars[role.index(tag) + i].append(nxt); nxt += 1
    return stars, role

class Growth:
    """One start grown round by round, reading what the own knots of A and of B make and the groups that join an own
    knot of one to a knot of the other's descent."""
    def __init__(self, stars, role, law):
        self.law = law; self.G = eng.Guard(MULT); self.S = eng.from_stars(stars)
        self.anc = {i: frozenset([r]) for i, r in enumerate(role)}
        self.name = {}
        cnt = collections.Counter()
        for i, r in enumerate(role):
            self.name[i] = '%s%d' % (r, cnt[r]); cnt[r] += 1
        self.rows = []; self.stop = None

    def fork(self):
        g = Growth.__new__(Growth); g.law = self.law; g.G = eng.Guard(MULT); g.S = self.S.copy()
        g.anc = dict(self.anc); g.name = dict(self.name); g.rows = list(self.rows); g.stop = self.stop
        return g

    def retire(self, tag):
        """bar every loose distinction of every member that has a start knot of `tag` among its ancestors"""
        n = 0
        for u, h, k in eng.live_members(self.S):
            if tag in self.anc[u]:
                n += 1
                for d in self.S.usable(u): self.S.barred[d] = True
        return n

    def step(self):
        T = self.S.copy()
        try: rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T; anc, name = self.anc, self.name
        short = set(rec['short'])
        own = lambda u, t: anc[u] == frozenset([t])
        # groups with an own knot of X and (first pair) a knot that is not X's own, (second pair) a knot of the
        # other's descent; each as [groups, kept groups].  Beyond one step the second is always nothing: an own knot's
        # group partners are children of an own parent, and only at one step can such a child have the other pattern
        # among its ancestors.
        join = {'A': [0, 0, 0, 0], 'B': [0, 0, 0, 0]}
        for g in rec['groups']:
            kept = not any(u in short for u in g)
            for X, Y in (('A', 'B'), ('B', 'A')):
                if any(own(u, X) for u in g):
                    if any(not own(u, X) for u in g): join[X][0] += 1; join[X][1] += kept
                    if any(Y in anc[u] for u in g): join[X][2] += 1; join[X][3] += kept
        mem = collections.Counter(next(iter(anc[u])) for u in rec['members'] if len(anc[u]) == 1)
        births = {'A': [], 'B': [], 'both': []}; seen = collections.Counter(); takes = 0
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            takes += bool(b['takes'])
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]; name[b['id']] = n
            t = next(iter(a)) if len(a) == 1 else ('both' if ('A' in a and 'B' in a) else None)
            if t in births: births[t].append((n, b['f'], len(S.places[b['id']])))
        row = {'round': S.round, 'knots': S.n_knots, 'short': len(short), 'takes': takes}
        for X in ('A', 'B'):
            births[X].sort()
            row[X] = {'members': mem[X], 'births': len(births[X]), 'digest': hashlib.sha1(repr(births[X]).encode()).hexdigest()[:12],
                      'joined': join[X][0], 'kept': join[X][1], 'joined to the other': join[X][2], 'kept with the other': join[X][3]}
        births['both'].sort()                              # the joint descent: births with a start knot of each among their ancestors
        row['both'] = {'births': len(births['both']), 'digest': hashlib.sha1(repr(births['both']).encode()).hexdigest()[:12]}
        self.rows.append(row)
        return True

    def run(self, rounds, bound, checkpoints=()):
        """grow to `rounds`, stopping after the first round that leaves more than `bound` knots; returns forks taken
        after each checkpoint round"""
        forks = {}
        while self.stop is None and self.S.round < rounds:
            if not self.step(): break
            if self.S.round in checkpoints: forks[self.S.round] = self.fork()
            if self.S.n_knots > bound: self.stop = 'knots'
        return forks

def first_diff(g1, g2, X, after=0):
    """the first round after `after` in which the births of X (A's own, B's own, or 'both', the joint descent) differ"""
    n = min(len(g1.rows), len(g2.rows))
    return next((g1.rows[i]['round'] for i in range(n) if g1.rows[i]['round'] > after and g1.rows[i][X]['digest'] != g2.rows[i][X]['digest']), None), n

def case(A, B, steps, ration, treatment, take, rounds=12, bound=3000, checkpoints=(2, 4, 6, 8), marks=True, join='meeting'):
    law = LAWS[ration](treatment, take) if ration in LAWS else eng.Law(ration, treatment, take, 'nae')
    t0 = time.time()
    def grown(a, b, mark=None, cp=()):
        stars, role = build(a, b, steps, mark, join)
        g = Growth(stars, role, law); f = g.run(rounds, bound, cp); return g, f
    whole, forks = grown(A, B, cp=checkpoints)
    out = {'A': A, 'B': B, 'steps': steps, 'join': join, 'law': [ration, treatment, take], 'rounds read': len(whole.rows), 'ended by': whole.stop or 'rounds',
           'knots': whole.rows[-1]['knots'] if whole.rows else 0, 'births that took': sum(r['takes'] for r in whole.rows), 'reads': {}}
    out['joint descent, births by round'] = [x['both']['births'] for x in whole.rows]
    out['short members by round'] = [x['short'] for x in whole.rows]
    for X, Y in (('A', 'B'), ('B', 'A')):
        P = A if X == 'A' else B
        r = {'pattern': P}
        rows = whole.rows
        r['own members by round'] = [x[X]['members'] for x in rows]; r['own births by round'] = [x[X]['births'] for x in rows]
        r['joined by round'] = [x[X]['joined'] for x in rows]; r['kept by round'] = [x[X]['kept'] for x in rows]
        r['joined to the other by round'] = [x[X]['joined to the other'] for x in rows]
        # the bare pattern (built as A; only its counts are read), and the pattern with a stub where the other was
        bare, _ = grown(P, None); stub, _ = grown(A, 'stub') if X == 'A' else grown('stub', B)
        n = min(len(bare.rows), len(rows))
        r["own series is the bare pattern's through"] = next((i for i in range(n) if (bare.rows[i]['A']['members'], bare.rows[i]['A']['births']) != (rows[i][X]['members'], rows[i][X]['births'])), n)
        d, m = first_diff(whole, stub, X)
        r['own making differs from with a stub, first round'] = d; r['rounds compared with the stub'] = m
        # the other's descent retired by hand after round c: does the own making differ later?
        r['other retired after round'] = {}
        for c, f in forks.items():
            g = f.fork(); k = g.retire(Y); g.run(rounds, bound)
            dd, mm = first_diff(whole, g, X, after=c)
            r['other retired after round'][str(c)] = {'members retired': k, 'own making first differs': dd, 'rounds compared': mm}
        # a mark at each start knot of the other: one more loose distinction there
        if marks:
            r['mark at a start knot of the other'] = {}
            other = B if X == 'A' else A
            for i in range(len(STARS[other])):
                g, _ = grown(A, B, mark=(Y, i))
                dd, mm = first_diff(whole, g, X); jj, _ = first_diff(whole, g, 'both')
                r['mark at a start knot of the other'][str(i)] = {'own making first differs': dd, 'joint descent first differs': jj, 'rounds compared': mm}
        out['reads'][X] = r
    out['seconds'] = round(time.time() - t0, 1)
    return out

if __name__ == '__main__':
    spec = json.loads(sys.argv[1])
    print(json.dumps(case(spec['A'], spec['B'], spec['steps'], spec['ration'], spec['treatment'], spec.get('take'),
                          spec.get('rounds', 12), spec.get('bound', 3000), marks=spec.get('marks', True),
                          join=spec.get('join', 'meeting'))))
