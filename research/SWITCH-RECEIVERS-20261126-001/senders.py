"""senders.py OUT: the switch receiver (three mutually sharing knots, sited at its knot holding one loose distinction)
against every sender of the jam study (47 starts and a stub) under caps of four and five, d = 2 and 3, by a meeting,
waiting, 16 rounds or 3,000 knots (the advisor's test of the reading of passes and turns)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import receivers
jam, switch = receivers.jam, receivers.switch
S = jam.starts() + [('stub', None, None)]
receivers.register()
with open(sys.argv[1], 'w') as f:
    for ration in ('CAP-4', 'CAP-5'):
        for d in (2, 3):
            for name, stars, site in S:
                g = receivers.grow('g7:122@0', name, d, ration)
                own = [r['own'][0] for r in g.rows]
                f.write(json.dumps({'law': ration, 'd': d, 'B': name, 'rounds': len(g.rows), 'own births': own,
                                    'leaves first way': switch.leaves_first_way(own), 'A short': [r['A short'] for r in g.rows]}) + '\n'); f.flush()
