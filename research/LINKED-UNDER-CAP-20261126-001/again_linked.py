"""again_linked.py IN OUT: in the pairs of the census that stay linked through round 16, a change made by the far
pattern after both exist, then another, then another, each in the growth with the ones before: after rounds 3, 7, 11
and 15, one more loose distinction at the member of the far end's own knots, in a part linked to the receiver's,
nearest the receiver in sharings; 32 rounds or 10,000 knots.  Read the first round each change is heard by the
receiver's own knots (its own births differ from the growth with the changes before it only), and, round by round,
whether the two are still linked in the growth with the change.  Second pass of
LINKED-UNDER-CAP-20261126-001; README.md, "Sent again", has the expectations, written before it was run."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import linked
second, receivers, ring_line, jam, bench = linked.second, linked.receivers, linked.ring_line, linked.jam, linked.bench
ROUNDS, BOUND, T0 = 32, 10000, (3, 7, 11, 15)
second.ROUNDS, second.BOUND = ROUNDS, BOUND          # changed_at grows each changed run this far

if __name__ == '__main__':
    receivers.register()
    pairs = []
    for l in open(sys.argv[1]):
        r = json.loads(l)
        if 'law' in r and len(r['linked']) >= 16 and r['linked'][15]: pairs.append((r['A'], r['B'], r['law']))
    with open(sys.argv[2], 'w') as f:
        for A, B, law in pairs:
            if A.startswith('tri:'):
                a = int(A.split(':')[1][0]); bench.STARS[A], bench.SITE[A] = second.tri(a), 0
            st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
            G = ring_line.Growth(st, ro, jam.law_of(law, 'CANCEL-WAIT')); G.run(ROUNDS, BOUND)
            out = {'A': A, 'B': B, 'law': law, 'rounds': len(G.rows), 'knots': G.rows[-1]['knots'], 'changes': []}
            for t0 in T0:
                if t0 >= len(G.rows): break
                ms, dist = linked.far_members(G, t0, True)
                if not ms: out['changes'].append({'t0': t0, 'none linked': True}); break
                H = second.changed_at(G, t0, ms[0], 'add'); h, n = ring_line.first_own_diff(G, H, t0)
                out['changes'].append({'t0': t0, 'knot': ms[0], 'sharings': dist.get(ms[0]), 'heard': h, 'rounds': n,
                                       'linked after it': linked.linked_rounds(H)})
                G = H                                   # the next change is made in the growth with this one
            f.write(json.dumps(out) + '\n'); f.flush()
