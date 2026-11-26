"""rule.py OUT: the rule read from the first pass (read as receivers.py reads a receiver: the first round its own births
differ between two of the five senders, and the classes of senders) (README.md, "A rule read from the first pass"), tested under caps of
six and seven on starts outside the census (a knot holding four or five loose distinctions), with the caps one
smaller and one larger as controls, and the far site changed in the middle of the run."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import receivers
jam, switch, bench, eng = receivers.jam, receivers.switch, receivers.bench, receivers.eng
for k in (6, 7, 8):
    bench.LAWS['CAP-%d' % k] = (lambda k: (lambda treatment, take: receivers.CapK(k, treatment, take)))(k)

def tri(a):
    """three mutually sharing knots holding a, 2 and 2 loose distinctions; the first is the site"""
    n = 3
    return [[0, 1] + list(range(n, n + a)), [0, 2] + list(range(n + a, n + a + 2)), [1, 2] + list(range(n + a + 2, n + a + 4))]

def grow(A, B, d, ration, t0=None):
    st, ro, _ = jam.changed(A, B, d, None, 'meeting')
    g = jam.Growth(st, ro, jam.law_of(ration, 'CANCEL-WAIT'))
    if t0 is not None:
        g.run(t0, 3000)
        kk = ro.index('B') + (0 if B == 'stub' else bench.SITE[B]); S = g.S; x = len(S.holders)
        S.places[kk].append(x); S.holders.append([kk]); S.barred.append(False); S.maker.append(kk)
    g.run(16, 3000); return g

if __name__ == '__main__':
    receivers.register()
    with open(sys.argv[1], 'w') as f:
        for a in (1, 2, 3, 4, 5):
            name = 'tri:%d22@0' % a; bench.STARS[name], bench.SITE[name] = tri(a), 0
            for k in sorted({a + 1, a + 2, a + 3} & {3, 4, 5, 6, 7, 8}):
                for d in (2, 3):
                    r = receivers.one(name, d, 'CAP-%d' % k); r['reading'] = 'classes'; r['cap'] = k
                    f.write(json.dumps(r) + '\n')
                if k == a + 2:
                    W = grow(name, 'g3:22@0', 3, 'CAP-%d' % k)
                    for t0 in range(0, 6):
                        G = grow(name, 'g3:22@0', 3, 'CAP-%d' % k, t0); n = min(len(W.rows), len(G.rows))
                        r = next((W.rows[i]['round'] for i in range(n) if W.rows[i]['own'] != G.rows[i]['own']), None)
                        f.write(json.dumps({'reading': 'swap', 'A': name, 'cap': k, 't0': t0, 'heard': r, 'rounds': n}) + '\n')
            f.flush()
