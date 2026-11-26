"""waiting_far.py OUT I0 I1: the far ends of recede.py that keep a member of their own that waits (made before the round
and still a member) at a distance that stops growing; for each, after round t0 = 3, 5, 8, one more loose distinction
(and, separately, one barred) at the nearest such waiting member; 24 rounds or 6,000 knots.  Read the first round
after t0 that the switch receiver's own births differ from the growth without the change."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import second
receivers, ring_line, again, jam, bench, eng = second.receivers, second.ring_line, second.again, second.jam, second.bench, second.eng
R = receivers.register()
A = 'tri:122@0'; bench.STARS[A], bench.SITE[A] = second.tri(1), 0
rows = [json.loads(l) for l in open(os.path.join(HERE, 'recede_runs.jsonl'))]
def steps(xs): return [xs[i + 1] - xs[i] for i in range(2, len(xs) - 1) if xs[i] is not None and xs[i + 1] is not None]
cands = [r['B'] for r in rows if any(s <= 0 for s in steps(r['nearest far member'])) and any(x is not None for x in r['nearest far member that waited'][2:])]
out = open(sys.argv[1], 'w')
for B in cands[int(sys.argv[2]):int(sys.argv[3])]:
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    W = ring_line.Growth(st, ro, jam.law_of('CAP-3', 'CANCEL-WAIT')); W.run(24, 6000)
    for t0 in (3, 5, 8):
        if t0 >= len(W.rows): continue
        dist = again.sharing_distance(W, t0); S = W.snaps[t0]
        old = sorted((dist[u], u) for u, h, k in eng.live_members(S) if ring_line.cls(W.anc[u]) == 'B' and S.made[u] < t0 and u in dist)
        if not old: continue
        du, u = old[0]
        for sign in ('add', 'bar'):
            H = second.changed_at(W, t0, u, sign)
            if H is None: continue
            r, n = ring_line.first_own_diff(W, H, t0)
            out.write(json.dumps({'B': B, 't0': t0, 'knot': u, 'made': S.made[u], 'sharings': du, 'sign': sign, 'heard': r, 'rounds': n,
                                  'own births': [x['own'][0] for x in W.rows], 'own births with': [x['own'][0] for x in H.rows]}) + '\n'); out.flush()
