"""parity2.py: parity.py again with the mark that renews the parity equations (the referee's second Block, R2): after one
more loose distinction is given to a knot by hand, the structure's parity equations are rebuilt from every knot's
places, so the next round's implied test reads the changed knot's new equation.  Everything else as parity.py.

    parity2.py run I0 I1"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parity
shortage = parity.shortage; ring_line, eng = shortage.ring_line, shortage.eng
_mark = ring_line.mark

def mark_renewed(h, u):
    _mark(h, u)
    S = h.S; S.basis = {}
    for v in range(S.n_knots):
        eng.basis_insert(S.basis, eng.row_of(S.places[v]))

ring_line.mark = mark_renewed

if __name__ == '__main__':
    R = shortage.receivers.register()
    sample = sorted(random.Random(shortage.SEED).sample(range(646), 100))
    for i in sample[int(sys.argv[2]):int(sys.argv[3])]:
        for B in shortage.receivers.SENDERS:
            for lw in shortage.LAWS:
                r = shortage.pair(R[i][0], B, lw); r['knot law'] = 'parity'; r['mark'] = 'equations renewed'
                print(json.dumps(r), flush=True)
