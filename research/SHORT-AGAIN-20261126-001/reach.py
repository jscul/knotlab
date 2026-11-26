"""reach.py: does a pattern's own knots hear a mark from afar under a ration made so that knots are short now and
then?  First study of SHORT-AGAIN-20261126-001 (a check by the thread, not registered).  README.md has the design,
the advisor's review of it and the expectations, written before the candidates were run.

A receiver A and a sender B are small starts of the census of TWO-PATTERNS-20261126-001 (census.py, `sited`),
joined by a meeting through a chain of d - 1 link knots (bench.py, `build`).  A CHANGE is made on the sender's side:
    B<j>     one more loose distinction at start knot j of B (the bench's mark)
    L<k>     one more loose distinction at the k-th link knot, counted from A (k = 1 .. d - 1)
    two      two more loose distinctions at B's site
    less     one loose distinction fewer at B's site (only where it keeps three places and one loose)
Each changed start is grown beside the unchanged one under the same law, and read each round:
    own      the births of A's own knots (name, fresh, places): the first round they differ is when A HEARS it
    joint    the births of the joint descent (knots with a start knot of A and one of B among their ancestors)
    groups   the cancelled groups that hold one of A's own knots, by their members' names: the only way a change
             can reach an own knot, so its first difference should come no later than `own`
Also read on the unchanged start: A's own kept joins with knots not its own, by round; the short knots by round;
and, under the ordinary count, how many joins every new knot is owed (its demand), by whose knot it is and by
whether it is a join or an offshoot, from which each ration's short knots can be counted before it is run.

    reach.py list
    reach.py run A B D            every ration and treatment for receiver A, sender B (indices) at distance D"""
import sys, os, json, hashlib, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
import rations
bench, eng = rations.bench, rations.eng
sys.path.insert(0, os.path.join(HERE, '..', 'TWO-PATTERNS-20261126-001', 'census'))
import census

ROUNDS, BOUND = 16, 3000
PATTERNS = ['g7:112@0', 'g6:133@0', 'g6:123@0', 'g6:122@0']
RATIONS = ['ORD', 'ODD-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'THIRD-FEWER']
TREATMENTS = ['CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT']

def register():
    S = {name: (stars, site) for name, stars, site in census.sited()}
    for name in PATTERNS:
        bench.STARS[name], bench.SITE[name] = S[name]

class Growth(bench.Growth):
    """the bench's growth, with the cancelled groups of A's own knots and the demand of every birth read as well"""
    def step(self):
        T = self.S.copy()
        try: rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T; anc, name = self.anc, self.name
        short = set(rec['short']); ownA = lambda u: anc[u] == frozenset(['A'])
        kept = 0; cancelled = []
        for g in rec['groups']:
            if any(ownA(u) for u in g):
                if any(u in short for u in g): cancelled.append(tuple(sorted(name[u] for u in g)))
                elif any(not ownA(u) for u in g): kept += 1
        own, joint = [], []; seen = collections.Counter(); demand = collections.Counter()
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            name[b['id']] = n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]
            cls = 'own A' if a == frozenset(['A']) else 'own B' if a == frozenset(['B']) else 'joint' if ('A' in a and 'B' in a) else 'link side'
            demand[(cls, b['kind'], len(b['parents']), b['D'])] += 1
            if cls == 'own A': own.append((n, b['f'], len(S.places[b['id']])))
            elif cls == 'joint': joint.append((n, b['f'], len(S.places[b['id']])))
        dig = lambda x: hashlib.sha1(repr(sorted(x)).encode()).hexdigest()[:12]
        self.rows.append({'round': S.round, 'knots': S.n_knots, 'short': len(short), 'kept': kept, 'own': [len(own), dig(own)],
                          'joint': [len(joint), dig(joint)], 'groups': dig(cancelled), 'demand': demand})
        return True

def changed(A, B, d, change):
    stars, role = bench.build(A, B, d, None, 'meeting')
    nxt = 1 + max(x for k in stars for x in k)
    if change is None: return stars, role
    kind, i = change
    if kind == 'B': stars[role.index('B') + i].append(nxt)
    elif kind == 'L': stars[[k for k, r in enumerate(role) if r == 'link'][i - 1]].append(nxt)
    elif kind == 'two': stars[role.index('B') + bench.SITE[B]] += [nxt, nxt + 1]
    elif kind == 'less':
        k = role.index('B') + bench.SITE[B]
        loose = [x for x in stars[k] if sum(x in s for s in stars) == 1]
        if len(stars[k]) < 4 or len(loose) < 2: return None
        stars[k].remove(loose[-1])
    return stars, role

def case(A, B, d, ration, treatment):
    law = bench.LAWS[ration](treatment, None) if ration in bench.LAWS else eng.Law(ration, treatment, None, 'nae')
    def grown(change):
        sr = changed(A, B, d, change)
        if sr is None: return None
        g = Growth(sr[0], sr[1], law); g.run(ROUNDS, BOUND); return g
    whole = grown(None)
    out = {'A': A, 'B': B, 'd': d, 'law': [ration, treatment], 'rounds': len(whole.rows), 'ended': whole.stop or 'rounds',
           'knots': whole.rows[-1]['knots'], 'short': [r['short'] for r in whole.rows], 'kept': [r['kept'] for r in whole.rows],
           'own births': [r['own'][0] for r in whole.rows], 'joint births': [r['joint'][0] for r in whole.rows], 'changes': {}}
    if ration == 'ORD' and treatment == 'CANCEL-WAIT':
        dem = collections.Counter()
        for r in whole.rows: dem.update(r['demand'])
        out['demand'] = [[list(k), v] for k, v in sorted(dem.items())]
    nB = len(bench.STARS[B])
    changes = [('B', j) for j in range(nB)] + [('L', k) for k in range(1, d)] + [('two', 0), ('less', 0)]
    for ch in changes:
        g = grown(ch)
        if g is None: continue
        n = min(len(whole.rows), len(g.rows))
        first = lambda f: next((whole.rows[i]['round'] for i in range(n) if f(whole.rows[i]) != f(g.rows[i])), None)
        out['changes']['%s%d' % ch if ch[0] in 'BL' else ch[0]] = {'own': first(lambda r: r['own']), 'joint': first(lambda r: r['joint']),
                                                               'groups': first(lambda r: r['groups']), 'rounds': n}
    # the receiver alone under this law: does its own making go on?
    st, ro = bench.build(A, None, 1); alone = Growth(st, ro, law); alone.run(ROUNDS, BOUND)
    out['alone'] = {'rounds': len(alone.rows), 'own births, last round': alone.rows[-1]['own'][0], 'knots': alone.rows[-1]['knots']}
    return out

if __name__ == '__main__':
    register()
    if sys.argv[1] == 'list':
        for i, n in enumerate(PATTERNS): print(i, n, bench.STARS[n], 'site', bench.SITE[n])
    else:
        A, B, d = PATTERNS[int(sys.argv[2])], PATTERNS[int(sys.argv[3])], int(sys.argv[4])
        for ration in RATIONS:
            for treatment in TREATMENTS:
                t0 = time.time(); r = case(A, B, d, ration, treatment); r['seconds'] = round(time.time() - t0, 2)
                print(json.dumps(r), flush=True)
