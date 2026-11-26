"""alike.py: which starts look alike to a local reader.  LOOK-ALIKE-20261126-001 (a check by the thread, not
registered); README.md has the design and the expectations, written before the runs they speak of.

Ordinary growth only: the cheapest growth (the ordinary count), not-all-equal, nothing taken; a round in which some
knot would have to give more loose distinctions than it holds is a STALL, and the growth stops there (lesson 8.1).
The shared engine is used with its waiting treatment only to detect the shortage: a round with any short knot is
recorded as a stall and nothing of it is kept.

Each birth is read without names (HOW-MUCH-ARRIVES-20261126-001's readings):
    sig0   kind, number of parents, fresh distinctions, places
    sig1   sig0 and the sorted sig0 of its parents
For each start: the births of each round in both readings, and its KIND from the counts per round:
    stalls, closes, dim D (the count per round eventually a polynomial of degree D - 1 in the round), rate x
    (the count multiplied by about x each round), or unread.
For a pair of starts of one kind, in a reading: the first round r0 from which, in every round read by both, the
births of one are contained in the births of the other (they AGREE UP TO THE COUNT), and the first from which they
are equal (AGREE EXACTLY); None when they never do in the rounds read.

    alike.py grow N [FIRST LAST]       grow the census starts of N knots (or those with index FIRST..LAST), JSON lines
    alike.py one N I                   grow census start I of N knots, one JSON line
"""
import sys, os, json, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, ROOT + '/experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
sys.path.insert(0, ROOT + '/experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies')
import eng
import cpcensus

ROUNDS, BOUND = int(os.environ.get("ALIKE_ROUNDS", 20)), 30000


def census(n):
    return [(i, gi, list(loose), cpcensus.stars(gi, loose)) for i, (gi, loose) in enumerate(cpcensus.starts(n))]


def grow(stars, rounds=ROUNDS, bound=BOUND, knot_law='nae'):
    """per round: the count and the sig0 and sig1 multisets (as sorted [item, count] lists); and how it ended"""
    law = eng.Law('ORD', 'CANCEL-WAIT', None, knot_law)
    S = eng.from_stars([list(k) for k in stars]); G = eng.Guard(100)
    sig0 = {i: ('start', 0, 0, len(stars[i])) for i in range(len(stars))}
    rows, end = [], 'rounds'
    while S.round < rounds:
        T = S.copy()
        try:
            rec = eng.play_round(T, law, G)
        except eng.GuardStop:
            end = 'guard'; break
        if rec['short']:
            end = 'stalls at round %d' % (S.round + 1); break
        S = T
        c0, c1 = collections.Counter(), collections.Counter()
        for b in rec['births']:
            s0 = (b['kind'], len(b['parents']), b['f'], len(S.places[b['id']])); sig0[b['id']] = s0
            c0[s0] += 1
            c1[s0 + (tuple(sorted(sig0[p] for p in b['parents'])),)] += 1
        if not rec['births']:
            end = 'closes at round %d' % S.round; break
        rows.append({'n': sum(c0.values()), 'sig0': sorted([list(k), v] for k, v in c0.items()),
                     'sig1': sorted([[list(k[:4]), [list(x) for x in k[4]]], v] for k, v in c1.items())})
        if S.n_knots > bound:
            end = 'bound'; break
    return {'rows': rows, 'end': end, 'knots': S.n_knots}


def kind(counts, end):
    """the kind of growth from the counts per round"""
    if end.startswith('stalls'): return 'stalls'
    if end.startswith('closes'): return 'closes'
    if len(counts) < 10: return 'unread'
    tail = counts[-8:]
    for D in (1, 2, 3, 4):                      # dimension D: the (D - 1)-th differences of the count are constant
        d = list(tail)
        for _ in range(D - 1): d = [b - a for a, b in zip(d, d[1:])]
        if len(set(d)) == 1 and d[0] > 0: return 'dim %d' % D
    r = [b / a for a, b in zip(counts[-5:], counts[-4:]) if a]
    if len(r) == 4 and min(r) > 1.05 and max(r) - min(r) < 0.01: return 'rate %.2f' % r[-1]
    return 'unread'


def agreement(a, b, R):
    """the first round from which a's and b's births in reading R are nested (contained one in the other), and from
    which they are equal, through the rounds read by both; None when never"""
    n = min(len(a), len(b))
    def cnt(row): return collections.Counter({json.dumps(k): v for k, v in row[R]})
    nested, equal = [], []
    for i in range(n):
        A, B = cnt(a[i]), cnt(b[i])
        nested.append(not (A - B) or not (B - A)); equal.append(A == B)
    def first(flags):
        k = n
        while k > 0 and flags[k - 1]: k -= 1
        return k + 1 if k < n else None
    return first(nested), first(equal), n


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'grow':
        N = int(sys.argv[2]); C = census(N)
        lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(C) - 1)
        for i, gi, loose, stars in C[lo:hi + 1]:
            t0 = time.time(); g = grow(stars)
            g.update({'n knots': N, 'index': i, 'graph': gi, 'loose': loose, 'stars': stars,
                      'kind': kind([r['n'] for r in g['rows']], g['end']), 'seconds': round(time.time() - t0, 2)})
            print(json.dumps(g), flush=True)
    elif cmd == 'one':
        N, I = int(sys.argv[2]), int(sys.argv[3]); i, gi, loose, stars = census(N)[I]
        g = grow(stars); g.update({'index': I, 'graph': gi, 'loose': loose, 'kind': kind([r['n'] for r in g['rows']], g['end'])})
        print(json.dumps(g))
