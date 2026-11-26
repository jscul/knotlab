"""recede.py OUT I0 I1: every receiver of the switch census (receivers.py) as the FAR END, against the switch receiver of
the cap of three (three mutually sharing knots holding one, two and two loose distinctions, sited at the one), d = 3 by
a meeting, waiting, 16 rounds or 3,000 knots: the sharings from the receiver's own knots to the nearest member of the
far end's own knots, round by round, and how many of those members are short.  Does any far end keep a member that
does not recede?"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import second
receivers, ring_line, again, jam, bench, eng = second.receivers, second.ring_line, second.again, second.jam, second.bench, second.eng
R = receivers.register()
A = 'tri:122@0'; bench.STARS[A], bench.SITE[A] = second.tri(1), 0
out = open(sys.argv[1], 'w')
for name, stars, site in R[int(sys.argv[2]):int(sys.argv[3])]:
    st, ro, _ = jam.changed(A, name, 3, None, 'meeting')
    g = ring_line.Growth(st, ro, jam.law_of('CAP-3', 'CANCEL-WAIT')); g.run(16, 3000)
    far, waiting = [], []
    for c in range(1, len(g.rows) + 1):
        dist = again.sharing_distance(g, c); S = g.snaps[c]
        bs = [(dist.get(u), u) for u, h, k in eng.live_members(S) if ring_line.cls(g.anc[u]) == 'B' and dist.get(u) is not None]
        far.append(min(bs)[0] if bs else None)
        old = [u for d_, u in bs if S.made[u] < c]                  # far members made before this round: they waited
        waiting.append(min((dist[u] for u in old), default=None))
    out.write(json.dumps({'B': name, 'rounds': len(g.rows), 'nearest far member': far, 'nearest far member that waited': waiting,
                          'own births': [r['own'][0] for r in g.rows]}) + '\n'); out.flush()
