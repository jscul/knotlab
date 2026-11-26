"""switch.py: the one receiver that hears from afar under the cap of three, read under swaps of each scaffold.  Added
after the jam study's full pass (JAM.md, "What was found"), which found under the cap of three with waiting 77
changes heard from three or four steps, all by one receiver, the three-knot start g7:122 sited at its knot with one
loose distinction, first heard in round 7 or 9, with no own knot of it waiting.

That receiver grows in one of two ways: its own knots make 3, 4, 5, ... knots in rounds 1, 2, 3, ... and none is
ever short; or, from round 7 or 9, many more, with own knots short every other round.  Which way, and from which
round, depends on what is at the other end of the line.  Read here, for the receiver under each swap: for every
sender, the round its own births leave the first way (3, 4, 5, ...: two more than the round), or never; and for every
change as in jam.py, the first round its own births differ.

Swaps: the distance (2 to 6), the join (a meeting, a shared distinction), the cap (three, four), what a short knot
does (waits, retires, makes offshoots), the receiver's site (each of its three knots, two classes), 16 rounds.

    switch.py one D JOIN LAW TREATMENT SITE      every sender for one swap, a JSON line a sender"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jam
bench, eng = jam.bench, jam.eng


class Cap4(eng.Law):
    def __init__(self, treatment, take=None):
        eng.Law.__init__(self, 'ORD', treatment, take, 'nae')
    def fresh(self, kind, p, D, o):
        return min(max(D, 3 - p, 1), 4)
    def name(self):
        return 'CAP-4/%s/RELEASE/no-take/nae' % self.treatment

bench.LAWS['CAP-4'] = lambda treatment, take: Cap4(treatment, take)
jam.ROUNDS, jam.BOUND = 16, 3000


def leaves_first_way(own):
    return next((i + 1 for i, x in enumerate(own) if x != i + 3), None)


if __name__ == '__main__':
    S = jam.starts() + [('stub', None, None)]
    d, join, ration, treatment, site = int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6])
    name = 'g7:122@%d' % site
    if name not in bench.STARS:
        base = dict((n, (st, s)) for n, st, s in S if n and n.startswith('g7:122@'))
        bench.STARS[name], bench.SITE[name] = next(iter(base.values()))[0], site
    for j in range(len(S)):
        t0 = time.time(); r = jam.case(name, S[j][0], d, ration, treatment, join)
        out = {'A': name, 'B': S[j][0], 'd': d, 'join': join, 'law': [ration, treatment], 'rounds': r['rounds'], 'knots': r['knots'],
               'own births': r['own births'], 'A short': r['A short'], 'leaves first way': leaves_first_way(r['own births']),
               'changes': [{k: c.get(k) for k in ('at', 'distance', 'heard', 'waiting own without', 'waiting own with')} for c in r['changes']],
               'seconds': round(time.time() - t0, 2)}
        print(json.dumps(out), flush=True)
