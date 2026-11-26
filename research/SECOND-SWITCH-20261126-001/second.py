"""second.py: after both exist, can the far pattern change the switch receiver's course?  First study of
SECOND-SWITCH-20261126-001 (a check by the thread, not registered); README.md has the design and the expectations,
written before the full run.

Receivers: the switch kind under each cap k = 3 to 7 (three mutually sharing knots, the site holding k - 2 loose
distinctions so that it has k places, the other two holding two), joined by a meeting through two link knots (d = 3)
to a far end: the two-knot start sited at a knot holding two loose distinctions (it switches the receiver at round
7), the one-knot start (three loose) or a stub (neither does).  After round t0 = 3 to 10, one more loose distinction
(and, separately, one barred) at each of the five members of the far end's own knots nearest the receiver's own
knots in sharings; grown to round 24 or 6,000 knots.  Read: the first round after t0 the receiver's own births differ
from the growth without the change; the change's sharing distance at t0; the receiver's own births with the change,
without it and with a stub at the far end (its slow way).

    second.py one A_LOOSE SENDER RATION     a JSON line per change"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.join(HERE, '..', 'SHORT-AGAIN-20261126-001')
SW = os.path.join(HERE, '..', 'SWITCH-RECEIVERS-20261126-001')
sys.path.insert(0, SA); sys.path.insert(0, SW)
import receivers, ring_line, again
jam, bench, eng = receivers.jam, receivers.bench, receivers.eng
for k in (6, 7):
    bench.LAWS['CAP-%d' % k] = (lambda k: (lambda treatment, take: receivers.CapK(k, treatment, take)))(k)
bench.LAWS['CAP-4'] = lambda treatment, take: receivers.CapK(4, treatment, take)
ROUNDS, BOUND, D = 24, 6000, 3


def tri(a):
    return [[0, 1] + list(range(3, 3 + a)), [0, 2] + list(range(3 + a, 5 + a)), [1, 2] + list(range(5 + a, 7 + a))]


def grow(A, B, ration):
    st, ro, _ = jam.changed(A, B, D, None, 'meeting')
    g = ring_line.Growth(st, ro, jam.law_of(ration, 'CANCEL-WAIT')); g.run(ROUNDS, BOUND); return g


def changed_at(g, t0, u, sign):
    h = ring_line.fork_at(g, t0)
    if sign == 'add': ring_line.mark(h, u)
    else:
        us = h.S.usable(u)
        if not us: return None
        h.S.barred[us[-1]] = True
    h.run(ROUNDS, BOUND); return h


if __name__ == '__main__':
    receivers.register()
    a, B, ration = int(sys.argv[2]), sys.argv[3], sys.argv[4]
    A = 'tri:%d22@0' % a; bench.STARS[A], bench.SITE[A] = tri(a), 0
    W = grow(A, B, ration); stub = grow(A, 'stub', ration)
    own = lambda g: [r['own'][0] for r in g.rows]
    print(json.dumps({'reading': 'base', 'A': A, 'B': B, 'law': ration, 'rounds': len(W.rows), 'knots': W.rows[-1]['knots'],
                      'own births': own(W), 'own births with a stub': own(stub)}), flush=True)
    # how far the far end's own knots are from the receiver's, round by round (the advisor: does the way lengthen
    # faster than a change travels?)
    far = []
    for c in range(1, len(W.rows) + 1):
        dist = again.sharing_distance(W, c); S = W.snaps[c]
        bs = [dist.get(u) for u, h, k in eng.live_members(S) if ring_line.cls(W.anc[u]) == 'B' and dist.get(u) is not None]
        far.append(min(bs) if bs else None)
    print(json.dumps({'reading': 'far end distance', 'A': A, 'B': B, 'law': ration, 'by round': far}), flush=True)
    # the horizon: a change after round t0 at knots that are not the receiver's own, s sharings from its own knots
    for t0 in (3, 6):
        if t0 >= len(W.rows): break
        dist = again.sharing_distance(W, t0); S = W.snaps[t0]
        mem = [u for u, h, k in eng.live_members(S) if ring_line.cls(W.anc[u]) != 'A' and dist.get(u) is not None]
        for s_ in range(1, 9):
            for u in sorted(v for v in mem if dist[v] == s_)[:3]:
                H = changed_at(W, t0, u, 'add'); r, n = ring_line.first_own_diff(W, H, t0)
                print(json.dumps({'reading': 'horizon', 'A': A, 'B': B, 'law': ration, 't0': t0, 'knot': u, 'class': ring_line.cls(W.anc[u]),
                                  'sharings': s_, 'heard': r, 'rounds': n}), flush=True)
    for t0 in range(3, 11):
        if t0 >= len(W.rows): break
        for u, du in again.nearest_B(W, t0):
            for sign in ('add', 'bar'):
                H = changed_at(W, t0, u, sign)
                if H is None: continue
                r, n = ring_line.first_own_diff(W, H, t0)
                print(json.dumps({'reading': 'change', 'A': A, 'B': B, 'law': ration, 't0': t0, 'knot': u, 'sharings': du, 'sign': sign,
                                  'heard': r, 'rounds': n, 'own births with': own(H)}), flush=True)
