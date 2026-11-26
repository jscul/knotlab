"""receivers.py: which receivers switch their way of growing on what is at the far end of a line, under a cap.  First
study of SWITCH-RECEIVERS-20261126-001 (a check by the thread, not registered); README.md has the design and the
expectations, written before the full run.

Receivers: every sited start of one to four knots of the census of parts that copy themselves (cpcensus.py: a connected
graph on the knots, one shared distinction for each pair it joins, zero to three loose distinctions on each knot, at
least three places on every knot; each start once up to its symmetries, sited once for each class of knots under the
symmetries that keep the loose counts): 1 + 4 + 39 + 599 = 643, and the bench's ring, two-knot part and source.
Senders, one for each kind of far end the switch study told apart: a one-knot start (its site holds three loose
distinctions), a two-knot start sited at a knot holding two, a path of three knots sited at its middle knot holding
one, the switch receiver itself (three mutually sharing knots, sited at its knot holding one), and a stub.
Each receiver is joined to each sender by a meeting through d - 1 link knots and grown under a law, 16 rounds or 3,000
knots.  Read, for each receiver: its own births in each round with each sender (as jam.py reads them), and from these
the first round in which they differ between two senders, the senders that agree through the last round read, and
whether any own knot of the receiver was short before that round.

    receivers.py list                  the receivers
    receivers.py one I D RATION        receiver I with every sender at distance D, one JSON line
    receivers.py all I                 receiver I at d = 2 to 5 under each law of LAWS, a line each"""
import sys, os, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.join(HERE, '..', 'SHORT-AGAIN-20261126-001')
sys.path.insert(0, SA)
import jam, switch
bench, eng = jam.bench, jam.eng
sys.path.insert(0, bench.ROOT + '/experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies')
import cpcensus

ROUNDS, BOUND = 16, 3000


class CapK(eng.Law):
    """a cap of k on the ordinary count (switch.py has k = 4)"""
    def __init__(self, k, treatment, take=None):
        eng.Law.__init__(self, 'ORD', treatment, take, 'nae'); self.k = k
    def fresh(self, kind, p, D, o):
        return min(max(D, 3 - p, 1), self.k)
    def name(self):
        return 'CAP-%d/%s/RELEASE/no-take/nae' % (self.k, self.treatment)

bench.LAWS['CAP-5'] = lambda treatment, take: CapK(5, treatment, take)
SENDERS = ['g1:3@0', 'g3:22@0', 'g6:122@0', 'g7:122@0', 'stub']
LAWS = ['CAP-3', 'CAP-4', 'CAP-5', 'REC-ONE-FEWER', 'ORD']


def receivers():
    """[(name, stars, site)]: the census's sited starts of one to four knots, then the bench's three patterns"""
    out = []
    for n in (1, 2, 3, 4):
        for gi, loose in cpcensus.starts(n):
            keep = [a for a in cpcensus.autos(gi) if all(loose[a[v]] == loose[v] for v in range(n))]
            seen = set()
            for v in range(n):
                orbit = min(a[v] for a in keep)
                if orbit in seen: continue
                seen.add(orbit)
                out.append(('n%d:g%d:%s@%d' % (n, gi, ''.join(map(str, loose)), v), cpcensus.stars(gi, loose), v))
    for P in ('ring', 'copier', 'source'): out.append((P, bench.STARS[P], bench.SITE[P]))
    return out


def register():
    jam.starts()                                   # the jam study's 47, which hold every sender but the stub
    R = receivers()
    for name, stars, site in R: bench.STARS[name], bench.SITE[name] = stars, site
    return R


def grow(A, B, d, ration):
    st, ro, _ = jam.changed(A, B, d, None, 'meeting')
    g = jam.Growth(st, ro, jam.law_of(ration, 'CANCEL-WAIT')); g.run(ROUNDS, BOUND); return g


def one(A, d, ration):
    t0 = time.time(); rows = {}
    for B in SENDERS:
        g = grow(A, B, d, ration)
        rows[B] = {'rounds': len(g.rows), 'knots': g.rows[-1]['knots'], 'own births': [r['own'][0] for r in g.rows],
                   'own': [r['own'][1] for r in g.rows], 'A short': [r['A short'] for r in g.rows]}
    n = min(r['rounds'] for r in rows.values())
    first = next((i + 1 for i in range(n) if len({rows[B]['own'][i] for B in SENDERS}) > 1), None)
    # senders that agree through the n rounds read: classes
    cls = {}
    for B in SENDERS: cls.setdefault(tuple(rows[B]['own'][:n]), []).append(B)
    short_before = None if first is None else any(any(rows[B]['A short'][:first - 1]) for B in SENDERS)
    # each sender against the stub (the advisor's common baseline), up to the last round both were read
    for B in SENDERS:
        m = min(rows[B]['rounds'], rows['stub']['rounds'])
        rows[B]['differs from the stub'] = next((i + 1 for i in range(m) if rows[B]['own'][i] != rows['stub']['own'][i]), None)
        rows[B]['rounds with the stub'] = m
    for B in SENDERS: del rows[B]['own']
    return {'A': A, 'd': d, 'law': ration, 'rounds compared': n, 'first differs': first, 'classes': sorted(cls.values()),
            'own short before': short_before, 'by sender': rows, 'seconds': round(time.time() - t0, 2)}


if __name__ == '__main__':
    R = register()
    if sys.argv[1] == 'list':
        for k, (name, stars, site) in enumerate(R): print(k, name, stars, 'site', site)
    elif sys.argv[1] == 'one':
        i, d, ration = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        print(json.dumps(one(R[i][0], d, ration)))
    elif sys.argv[1] == 'all':
        i = int(sys.argv[2])
        for ration in LAWS:
            for d in (2, 3, 4, 5):
                print(json.dumps(one(R[i][0], d, ration)), flush=True)
