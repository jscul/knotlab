"""classes.py: the preserved two-class sign of READS-HOLDERS-SOURCES-20261120-001A (its motion study), mapped. Under
the parity knot law a structure's allowed assignments form a linear space S over two values; the moves are, for each
distinction, the shortest allowed changes that contain it (every tie kept); H is the space they generate; the classes are
the cosets of H in S (2^(dim S - dim H) of them), each move keeping its class. Read per structure, at the start and after
one round of ordinary growth, with loose distinctions free and pinned at zero:
    dim S, dim H, the number of classes, and whether some class-changing allowed change touches no loose distinction
    (then a renaming of values that keeps every loose value exchanges the classes, so anything growth does through loose
    distinctions treats them alike)
Structures: rings of n knots (n = 3..9, one or two loose distinctions a knot), every census start of three to five knots
(forbid.py), and the one-round growths of both; growth on the canonical engine of the 20 November studies (forbid.grown)
or, with --fold, the engine of the recent line.

    classes.py rings | census I0 I1 [--fold]"""
import sys, json, itertools
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import forbid
MAX_DIM = 22                        # S enumerated in full up to this dimension; larger is reported as not run


def nullspace(rows, n):
    """basis of {x in GF(2)^n : r.x = 0 for every row r} (rows and vectors as Python ints)"""
    piv = {}
    for r in rows:
        for p, v in piv.items():
            if (r >> p) & 1: r ^= v
        if r:
            p = r.bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1: piv[q] ^= r
            piv[p] = r
    free = [i for i in range(n) if i not in piv]
    basis = []
    for f in free:
        v = 1 << f
        for p, r in piv.items():
            if (r >> f) & 1: v |= 1 << p
        basis.append(v)
    return basis


def rank(vecs):
    piv = {}
    for v in vecs:
        while v:
            p = v.bit_length() - 1
            if p in piv: v ^= piv[p]
            else: piv[p] = v; break
    return len(piv)


def span_words(basis):
    words = np.zeros(1, dtype=np.uint64)
    for b in basis:
        words = np.concatenate([words, words ^ np.uint64(b)])
    return words


def popcount(a):
    a = a.copy(); c = np.zeros(a.shape, dtype=np.int64)
    while a.any():
        c += (a & np.uint64(1)).astype(np.int64); a >>= np.uint64(1)
    return c


def analyse(supports, pin_loose):
    names = sorted({d for r in supports for d in r}); idx = {d: i for i, d in enumerate(names)}; n = len(names)
    held = forbid.holders(supports)
    loose = [idx[d] for d in names if len(held[d]) == 1]
    rows = [sum(1 << idx[d] for d in r) for r in supports]
    if pin_loose: rows += [1 << i for i in loose]
    B = nullspace(rows, n)
    if len(B) > MAX_DIM: return {'dim S': len(B), 'not run': 'dimension above %d' % MAX_DIM}
    W = span_words(B)[1:]
    pc = popcount(W)
    moves = set()
    for i in range(n):
        m = (W >> np.uint64(i)) & np.uint64(1)
        if not m.any(): continue
        w = pc[m == 1].min()
        for v in W[(m == 1) & (pc == w)]: moves.add(int(v))
    dH = rank(list(moves))
    lmask = sum(1 << i for i in loose)
    # a class-changing change with no loose distinction: an element of S with zero loose part outside H
    S0 = [int(v) for v in W if not (int(v) & lmask)]
    outside = rank(list(moves) + S0) > dH
    return {'distinctions': n, 'dim S': len(B), 'dim H': dH, 'classes': 2 ** (len(B) - dH),
            'a class change avoids the loose distinctions': outside}


def ring(n, l):
    rows = []
    for i in range(n):
        rows.append(tuple([i, (i + 1) % n] + [n + l * i + j for j in range(l)]))
    return tuple(rows)


def grown(supports, fold):
    if not fold:
        stage, status, births = forbid.grown(supports, 'parity', 'ordinary')
        return stage if status == 'funded' else None
    sys.path.insert(0, str(HERE.parent / 'SHORT-AGAIN-20261126-001'))
    import ring_line
    eng = ring_line.eng
    S = eng.from_stars([list(r) for r in supports]); T = S.copy()
    try: rec = eng.play_round(T, eng.Law('ORD', 'CANCEL-WAIT', None, 'parity'), eng.Guard(4))
    except eng.GuardStop: return None
    if not rec['births']: return None
    return tuple(tuple(p) for p in T.places)


def read(name, supports, fold):
    out = {'structure': name, 'knots': len(supports)}
    for when, st in (('start', supports), ('after one round', grown(supports, fold))):
        if st is None: out[when] = 'no round (stall or close)'; continue
        out[when] = {pin: analyse(st, pin == 'loose pinned') for pin in ('loose free', 'loose pinned')}
    return out


if __name__ == '__main__':
    fold = '--fold' in sys.argv
    if sys.argv[1] == 'rings':
        for n in range(3, 10):
            for l in (1, 2):
                print(json.dumps(read('ring n=%d loose=%d' % (n, l), ring(n, l), fold)), flush=True)
    else:
        S = forbid.census()
        for i in range(int(sys.argv[2]), min(int(sys.argv[3]), len(S))):
            print(json.dumps(read('census %d' % i, forbid.supports_of(S[i]), fold)), flush=True)
