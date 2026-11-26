"""census.py: the bench's readings on every pair of small starts.  Third direction of TWO-PATTERNS-20261126-001 (a
check by the thread, not registered).  See README.md; its expectations were written before the first full run.

The small starts are the census starts of one to three knots of the study of parts that copy themselves
(experiments/COPYING-PARTS-20261123-001A/.../cpcensus.py): a connected graph on the knots, one shared distinction
for each pair of knots it joins, and zero to three loose distinctions on each knot, with at least three places on
every knot and at least one loose distinction somewhere; each start once up to the graph's symmetries.  There are
1, 3 and 19 of them.  A SITED start is a start with one of its knots named as its site, once for each class of
knots under the symmetries that keep the loose counts.

Two sited starts are joined at one step, by a meeting or by a shared distinction, and grown under nine laws (the
ordinary count, a cap of three, just enough for three places; a short knot waits, retires, or makes offshoots),
with nothing taken.  A joined start has two to six knots besides the spent knot of a meeting.  Read, for each of
the two: the last round with a kept join between its own knots and any other; the first round its own births differ
from with a stub in the other's place; and, for a mark at each start knot of the other, the first round its own
knots hear it and the first round the joint descent does.  The programs are the bench's (../bench/bench.py).

    census.py list                  the sited starts
    census.py pair I J              the 18 cases of sited starts I and J, a line a case"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'bench'))
import bench
sys.path.insert(0, bench.ROOT + '/experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies')
import cpcensus

ROUNDS, BOUND = 10, 1500
LAWS = [(r, t) for r in ('ORD', 'CAP-3', 'FLOOR1') for t in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')]

def sited():
    """[(name, stars, site)] in the census's order"""
    out = []
    for n in (1, 2, 3):
        for gi, loose in cpcensus.starts(n):
            keep = [a for a in cpcensus.autos(gi) if all(loose[a[v]] == loose[v] for v in range(n))]
            seen = set()
            for v in range(n):
                orbit = min(a[v] for a in keep)
                if orbit in seen: continue
                seen.add(orbit)
                out.append(('g%d:%s@%d' % (gi, ''.join(map(str, loose)), v), cpcensus.stars(gi, loose), v))
    return out

def pair(i, j):
    S = sited()
    for k in (i, j):
        name, stars, site = S[k]
        bench.STARS[name] = stars; bench.SITE[name] = site
    A, B = S[i][0], S[j][0]
    # the ordinary count with a shared distinction and waiting comes last: waiting members can pile up there until one
    # round's roster takes minutes, and a pair stopped by the clock then loses that case only
    order = [(jn, r, t) for jn in ('meeting', 'share') for r, t in LAWS]
    order.sort(key=lambda x: x == ('share', 'ORD', 'CANCEL-WAIT'))
    for join, ration, treatment in order:
        if True:
            t0 = time.time()
            r = bench.case(A, B, 1, ration, treatment, None, rounds=ROUNDS, bound=BOUND, checkpoints=(), marks=True, join=join)
            last = lambda xs: max((n + 1 for n, x in enumerate(xs) if x), default=0)
            line = {'i': i, 'j': j, 'A': A, 'B': B, 'join': join, 'law': [ration, treatment], 'rounds': r['rounds read'], 'ended': r['ended by'],
                    'knots': r['knots'], 'short': r['short members by round'], 'joint': r['joint descent, births by round'], 'reads': {}}
            for X in 'AB':
                a = r['reads'][X]
                line['reads'][X] = {'last kept': last(a['kept by round']), 'last joined': last(a['joined by round']),
                                    'stub': a['own making differs from with a stub, first round'],
                                    'own births': a['own births by round'],
                                    'marks': [[m['own making first differs'], m['joint descent first differs']]
                                              for _, m in sorted(a['mark at a start knot of the other'].items(), key=lambda kv: int(kv[0]))]}
            line['seconds'] = round(time.time() - t0, 2)
            print(json.dumps(line), flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'list':
        for k, (name, stars, site) in enumerate(sited()): print(k, name, stars, 'site', site)
    else:
        pair(int(sys.argv[2]), int(sys.argv[3]))
