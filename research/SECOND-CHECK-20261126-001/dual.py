"""dual.py: is the second kind of check already in the structure? (README.md). Under parity, a structure's knots are its
first checks (each knot: its places sum to zero). Read each move (a shortest allowed change through a distinction, the
motion study's rule; classes2.py) as a knot holding the distinctions it changes: the exchanged pattern. Read per
structure: whether the exchanged pattern is lawful (every one of its knots with three or more places, every distinction
held by at most two of them); its allowed space (the class labels and the knots' own place sets); whether the class
labels and the long change (an allowed change outside the moves' span) are allowed in it; the fewest distinctions a
reader must hold to tell the classes apart (d_read: the least class label) and to change one class into another (d_change:
the least class-changing allowed change); and, on rings, whether growing the exchanged pattern gives the exchanged
pattern of the grown structure.

    dual.py rings | census FILE"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'TWO-CLASS-SIGN-20261126-001'))
import classes, classes2
forbid = classes.forbid
np = classes.np


def words(basis):
    return [int(v) for v in classes.span_words(basis)]


def least_outside(space_basis, sub_basis, n):
    """least weight of an element of span(space_basis) not in span(sub_basis), by enumeration"""
    rs = classes.rank(sub_basis); best = None
    for v in words(space_basis)[1:]:
        if classes.rank(sub_basis + [v]) > rs:
            w = bin(v).count('1')
            if best is None or w < best: best = w
    return best


def analyse(supports, pin_loose):
    names, idx, n, held, loose, rows = classes2.setup(supports, pin_loose)
    B = classes.nullspace(rows, n)
    if len(B) > classes.MAX_DIM: return {'not run': 'dimension %d' % len(B)}
    M, missing = classes2.short_moves(n, rows, True)
    M = sorted(M); Hb = [h for _, h in sorted(classes2.reduced(M) if hasattr(classes2, 'reduced') else [])] if False else None
    dH = classes.rank(M); dS = len(B)
    out = {'dim S': dS, 'dim H': dH, 'classes': 2 ** (dS - dH)}
    if dS == dH: return out
    # the exchanged pattern: one knot per move, holding the distinctions it changes
    holders = [0] * n
    for t in M:
        for i in range(n):
            if (t >> i) & 1: holders[i] += 1
    sizes = [bin(t).count('1') for t in M]
    out['exchanged knots'] = len(M)
    out['exchanged lawful'] = min(sizes) >= 3 and max(holders) <= 2
    out['places of exchanged knots'] = sorted(set(sizes))
    out['most holders of a distinction in the exchanged pattern'] = max(holders)
    # its allowed space: vectors with even overlap with every move = H-perp; the class labels are H-perp outside S-perp
    Hperp = classes.nullspace(M, n)
    rowsp = rows[:len(supports)] + ([1 << i for i in loose] if pin_loose else [])
    out['dim of the exchanged allowed space'] = len(Hperp)
    out['d_read (least class label)'] = least_outside(Hperp, [r for r in rowsp], n) if len(Hperp) <= classes.MAX_DIM else 'not run'
    out['d_change (least class-changing change)'] = least_outside(B, M, n)
    # is a least class-changing change allowed in the exchanged pattern (even overlap with every move)?
    longs = [v for v in words(B)[1:] if classes.rank(M + [v]) > dH and bin(v).count('1') == out['d_change (least class-changing change)']]
    out['a least class change is allowed in the exchanged pattern'] = any(all(bin(v & t).count('1') % 2 == 0 for t in M) for v in longs)
    out['_exchanged'] = [tuple(names[i] for i in range(n) if (t >> i) & 1) for t in M]
    return out


def read(name, supports):
    out = {'structure': name}
    st, status, births = forbid.grown(supports, 'parity', 'ordinary')
    for when, s in (('start', supports), ('after one round', st if status == 'funded' else None)):
        if s is None: out[when] = 'no round'; continue
        out[when] = {pin: analyse(s, pin == 'loose pinned') for pin in ('loose free', 'loose pinned')}
    # commuting check on rings: exchanged pattern of the grown structure, against growth of the exchanged start pattern
    try:
        ex0 = out['start']['loose pinned'].get('_exchanged')
        exg = out['after one round']['loose pinned'].get('_exchanged') if isinstance(out['after one round'], dict) else None
        if ex0 and exg:
            g2, s2, b2 = forbid.grown(tuple(ex0), 'parity', 'ordinary')
            out['growth commutes with the exchange'] = (s2 == 'funded' and sorted(map(len, g2)) == sorted(map(len, exg)) and len(g2) == len(exg))
    except Exception as e:
        out['growth commutes with the exchange'] = 'not run: %s' % type(e).__name__
    for when in ('start', 'after one round'):
        if isinstance(out[when], dict):
            for v in out[when].values(): v.pop('_exchanged', None)
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'rings':
        for n in range(3, 11):
            print(json.dumps(read('ring n=%d loose=2' % n, classes.ring(n, 2))), flush=True)
    else:
        S = forbid.census()
        for i in json.load(open(sys.argv[2])):
            print(json.dumps(read('census %d' % i, forbid.supports_of(S[i]))), flush=True)
