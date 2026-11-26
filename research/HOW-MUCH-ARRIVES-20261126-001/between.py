"""between.py: setting B of HOW-MUCH-ARRIVES-20261126-001, the supplied settings in which the record hears a change
between two patterns.  Starts, joins and laws are the earlier studies' own, imported unchanged:
    B1  two seven-knot generators ('source') joined by a meeting through d - 1 link knots, d = 1 .. 8, under the
        record's "one fewer than asked" (REC-ONE-FEWER, ring_line.py of SHORT-AGAIN-20261126-001) with waiting;
        changes: a mark (one more loose distinction) at each start knot of the far generator.
    B2  the switch receiver g7:122@0 of SWITCH-RECEIVERS-20261126-001 joined by a meeting through d - 1 link knots,
        d = 2 .. 5, under the cap of three with waiting, to the far sites g3:22@0 (its site holds two loose) and
        g1:3@0 (three) and a stub.
    B0  both under the ordinary count.
Read in the near pattern's own births (every start ancestor in A), round by round, in the three readings of
amount.py: the damage both ways against the births of both, the first round of any difference, and the share then.

    between.py b1 D LAW        one line: B1 at distance D under LAW (REC-ONE-FEWER or ORD)
    between.py b2 D LAW        one line: B2 at distance D under LAW (CAP-3 or ORD)
"""
import sys, os, json, hashlib, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.join(HERE, '..', 'SHORT-AGAIN-20261126-001')
sys.path.insert(0, SA)
import jam                      # registers the census starts and the bench's patterns, and the rations
bench, eng = jam.bench, jam.eng
import amount

ROUNDS, BOUND = 16, 3000


class Own(bench.Growth):
    """bench.Growth keeping, each round, the near pattern's own births in the three readings of amount.py"""
    def __init__(self, stars, role, law):
        bench.Growth.__init__(self, stars, role, law)
        self.sig0 = {i: ('start', 0, 0, len(stars[i])) for i in range(len(stars))}

    def step(self):
        T = self.S.copy()
        try: rec = eng.play_round(T, self.law, self.G)
        except eng.GuardStop:
            self.stop = 'guard'; return False
        self.S = S = T; anc, name = self.anc, self.name
        A = frozenset(['A']); own = []; seen = collections.Counter()
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            nm = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]; name[b['id']] = nm
            s0 = (b['kind'], len(b['parents']), b['f'], len(S.places[b['id']])); self.sig0[b['id']] = s0
            if a == A:
                own.append({'name': (nm, b['f'], len(S.places[b['id']])), 'sig0': s0,
                            'sig1': s0 + (tuple(sorted(self.sig0[p] for p in b['parents'])),)})
        self.rows.append({'own': own, 'knots': S.n_knots, 'short': len(rec['short'])})
        return True


def grown(A, B, d, law, mark=None):
    stars, role = bench.build(A, B, d, None, 'meeting')
    if mark is not None:
        nxt = 1 + max(x for k in stars for x in k)
        stars[role.index('B') + mark].append(nxt)
    g = Own(stars, role, jam.law_of(law, 'CANCEL-WAIT')); g.run(ROUNDS, BOUND); return g


def against(g, h):
    """per round: own births of each, and [c, c-] in each reading"""
    out = []
    for i in range(min(len(g.rows), len(h.rows))):
        a, b = g.rows[i]['own'], h.rows[i]['own']
        row = {'round': i + 1, 'n': len(a), "n'": len(b)}
        for R in amount.READINGS: row[R] = list(amount.diff([x[R] for x in a], [x[R] for x in b]))
        out.append(row)
    first = next((r['round'] for r in out if sum(r['name']) > 0), None)
    return {'rows': out, 'first': first, 'rounds': len(out), 'stops': [g.stop, h.stop]}


def b1(d, law):
    t0 = time.time(); base = grown('source', 'source', d, law)
    marks = {str(j): against(base, grown('source', 'source', d, law, mark=j)) for j in range(len(bench.STARS['source']))}
    return {'setting': 'B1', 'd': d, 'law': law, 'base knots': [r['knots'] for r in base.rows], 'marks': marks,
            'seconds': round(time.time() - t0, 1)}


def b2(d, law):
    t0 = time.time(); A = 'g7:122@0'
    g = {B: grown(A, B, d, law) for B in ('g3:22@0', 'g1:3@0', 'stub')}
    pairs = {'two against three': against(g['g1:3@0'], g['g3:22@0']), 'two against the stub': against(g['stub'], g['g3:22@0']),
             'three against the stub': against(g['stub'], g['g1:3@0'])}
    return {'setting': 'B2', 'd': d, 'law': law, 'pairs': pairs, 'seconds': round(time.time() - t0, 1)}


if __name__ == '__main__':
    jam.starts()
    kind, d, law = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    print(json.dumps(b1(d, law) if kind == 'b1' else b2(d, law)))
