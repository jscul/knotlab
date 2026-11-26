"""controls.py OUT: the advisor's controls on the receivers that switch under the cap of three (README.md, "Taken from
the advisor's review"), at d = 3 by a meeting, waiting.

    swap     the far end's site given one more loose distinction after round t0 (t0 = 0 to 8), for the one-knot sender
             (three loose, so four after), the two-knot sender (two, so three after) and a stub: the first round the
             receiver's own births differ from the growth without the change
    long     22 rounds or 6,000 knots with each of the five senders: does the receiver stay in the way it switched to
    both     the switch receiver as sender: the first round the sender's own knots leave the first way, beside the
             receiver's"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import receivers
jam, switch, bench, eng = receivers.jam, receivers.switch, receivers.bench, receivers.eng
SWITCHERS = ['n3:g7:122@0', 'n4:g17:1122@0', 'n4:g17:1122@1', 'n4:g17:1212@0', 'n4:g17:2121@1', 'n4:g18:1122@0']
D, LAW = 3, 'CAP-3'


def grow(A, B, rounds, bound, t0=None):
    st, ro, _ = jam.changed(A, B, D, None, 'meeting')
    g = jam.Growth(st, ro, jam.law_of(LAW, 'CANCEL-WAIT'))
    if t0 is not None:
        g.run(t0, bound)
        k = ro.index('B') + (0 if B == 'stub' else bench.SITE[B]); S = g.S; x = len(S.holders)
        S.places[k].append(x); S.holders.append([k]); S.barred.append(False); S.maker.append(k)
    g.run(rounds, bound); return g


def both(A, rounds=16, bound=3000):
    st, ro, _ = jam.changed(A, A, D, None, 'meeting')
    g = bench.Growth(st, ro, jam.law_of(LAW, 'CANCEL-WAIT')); g.run(rounds, bound)
    return [r['A']['births'] for r in g.rows], [r['B']['births'] for r in g.rows]


if __name__ == '__main__':
    receivers.register()
    with open(sys.argv[1], 'w') as f:
        for A in SWITCHERS:
            for B in ('g1:3@0', 'g3:22@0', 'stub'):
                W = grow(A, B, 16, 3000)
                for t0 in range(0, 9):
                    G = grow(A, B, 16, 3000, t0)
                    n = min(len(W.rows), len(G.rows))
                    r = next((W.rows[i]['round'] for i in range(n) if W.rows[i]['own'] != G.rows[i]['own']), None)
                    f.write(json.dumps({'reading': 'swap', 'A': A, 'B': B, 't0': t0, 'heard': r, 'rounds': n}) + '\n')
            for B in receivers.SENDERS:
                g = grow(A, B, 22, 6000)
                f.write(json.dumps({'reading': 'long', 'A': A, 'B': B, 'rounds': len(g.rows), 'knots': g.rows[-1]['knots'],
                                    'own births': [r['own'][0] for r in g.rows], 'A short': [r['A short'] for r in g.rows]}) + '\n')
            a, b = both(A)
            f.write(json.dumps({'reading': 'both', 'A': A, 'own births A': a, 'own births B': b,
                                'A leaves first way': switch.leaves_first_way(a), 'B leaves first way': switch.leaves_first_way(b)}) + '\n')
            f.flush()
