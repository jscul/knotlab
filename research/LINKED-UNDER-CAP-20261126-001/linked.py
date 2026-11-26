"""linked.py: do two patterns joined under a cap stay linked, and where they do, can the far one change the receiver's
course after both exist?  First study of LINKED-UNDER-CAP-20261126-001 (a check by the thread, not registered);
README.md has the design and the expectations, written before the full run.

A PART is a class of the roster's joinable relation; two parts are LINKED when a member of each holds one distinction
(the fold study's classes, FD 1.6).  For a pair (receiver A, far end B), joined by a meeting through two link knots
under a cap, waiting, read per round whether some member of B's own knots is in a part linked to a part holding a
member of A's own (parts.py of SECOND-SWITCH-20261126-001).  Where the two are linked after round t0 (t0 = 3, 5, 8),
one more loose distinction at each of the (up to five) members of B's own knots in a linked part, nearest A in
sharings; 24 rounds or 6,000 knots; the first round after t0 A's own births differ.  And, as the control the
advisor's wording asks, the same change where the two are not linked.

    linked.py census KIND_A I0 I1     the switch kind under its cap against census far ends I0..I1-1
    linked.py receivers I0 I1         census receivers I0..I1-1 against the five senders, under the cap of three"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
SS = os.path.join(HERE, '..', 'SECOND-SWITCH-20261126-001')
sys.path.insert(0, SS)
import second
receivers, ring_line, again, jam, bench, eng = second.receivers, second.ring_line, second.again, second.jam, second.bench, second.eng


def linked_rounds(g):
    """per round: is some member of B's own in a part linked to a part holding a member of A's own (None: either has none)"""
    out = []
    for c in range(1, len(g.rows) + 1):
        S = g.snaps[c]; R = eng.build_roster(S, eng.live_members(S), 'parts', eng.Guard(1000), parts=True)
        cl = eng.classes_of_parts(S, R.parts)
        pa = {cl[R.part_of[u]] for u in R.members if ring_line.cls(g.anc[u]) == 'A'}
        pb = {cl[R.part_of[u]] for u in R.members if ring_line.cls(g.anc[u]) == 'B'}
        out.append(None if not pa or not pb else bool(pa & pb))
    return out


def far_members(g, c, linked):
    """members of B's own after round c, in a part linked to A's (linked=True) or not (False), nearest A first"""
    S = g.snaps[c]; R = eng.build_roster(S, eng.live_members(S), 'parts', eng.Guard(1000), parts=True)
    cl = eng.classes_of_parts(S, R.parts)
    pa = {cl[R.part_of[u]] for u in R.members if ring_line.cls(g.anc[u]) == 'A'}
    dist = again.sharing_distance(g, c)
    ms = [u for u in R.members if ring_line.cls(g.anc[u]) == 'B' and (cl[R.part_of[u]] in pa) == linked]
    return sorted(ms, key=lambda u: (dist.get(u, 10 ** 6), u))[:5], dist


def pair(A, B, ration, rounds=24, bound=6000):
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    W = ring_line.Growth(st, ro, jam.law_of(ration, 'CANCEL-WAIT')); W.run(rounds, bound)
    lk = linked_rounds(W)
    out = {'A': A, 'B': B, 'law': ration, 'rounds': len(W.rows), 'knots': W.rows[-1]['knots'], 'linked': lk, 'changes': []}
    for t0 in (3, 5, 8):
        if t0 >= len(W.rows) or lk[t0 - 1] is None: continue
        for want in (True, False):
            ms, dist = far_members(W, t0, want)
            for u in ms:
                H = second.changed_at(W, t0, u, 'add'); r, n = ring_line.first_own_diff(W, H, t0)
                out['changes'].append({'t0': t0, 'linked': want, 'knot': u, 'sharings': dist.get(u), 'heard': r, 'rounds': n})
    return out


if __name__ == '__main__':
    R = receivers.register()
    if sys.argv[1] == 'list':
        for k, (name, stars, site) in enumerate(R): print(k, name)
    elif sys.argv[1] == 'census':
        a = int(sys.argv[2]); A = 'tri:%d22@0' % a; bench.STARS[A], bench.SITE[A] = second.tri(a), 0
        for name, stars, site in R[int(sys.argv[3]):int(sys.argv[4])]:
            r = pair(A, name, 'CAP-%d' % (a + 2)); r.pop('knots', None)
            print(json.dumps(r), flush=True)
    elif sys.argv[1] == 'receivers':
        for name, stars, site in R[int(sys.argv[2]):int(sys.argv[3])]:
            for B in receivers.SENDERS:
                print(json.dumps(pair(name, B, 'CAP-3', rounds=16, bound=3000)), flush=True)
