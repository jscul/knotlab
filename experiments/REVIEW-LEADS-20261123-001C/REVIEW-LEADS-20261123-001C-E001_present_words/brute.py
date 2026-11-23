"""Brute-force enumeration of the words of the four finished structures of a pair of sides (used by gates_b.py and positive.py)."""
import itertools
import numpy as np
import common as c

def side_knots(struct, who):
    """struct: dict(internal, knots=[{members, law}]) with names x1.. s1.. h1..; rename for the side `who` in 'AB'."""
    ren = {'A': {}, 'B': {'x1': 'y1', 'x2': 'y2', 'x3': 'y3'}}[who]
    def r(nm):
        if nm.startswith('h'): return who + nm
        return ren.get(nm, nm)
    return [([r(m) for m in k['members']], k['law']) for k in struct['knots']]

def finished_knots(sA, sB, a, b, cut):
    """knots of the finished structure for settings (a,b): all old knots plus the two newborn not-all-equal knots."""
    ks = side_knots(sA, 'A') + side_knots(sB, 'B')
    ks.append((['x1', f'x{2 + a}', 'za'], 'nae'))
    ks.append((['y1', f'y{2 + b}', 'zb'], 'nae'))
    return ks

def all_words(knots, include_newborn=True):
    names = []
    for mem, law in knots:
        for m in mem:
            if m not in names: names.append(m)
    n = len(names)
    pos = {nm: i for i, nm in enumerate(names)}
    idx = np.arange(1 << n)
    bits = {nm: ((idx >> i) & 1) for nm, i in pos.items()}
    ok = np.ones(1 << n, dtype=bool)
    for mem, law in knots:
        s = sum(bits[m] for m in mem)
        if law == 'nae': ok &= (s != 0) & (s != len(mem))
        elif law == 'even': ok &= (s % 2 == 0)
        else: ok &= (s % 2 == 1)
    return names, bits, ok

def joint_record_counts(sA, sB, a, b, cut):
    """16x16 integer counts of finished words by (Alice record (x1,x2,x3,za), Bob record (y1,y2,y3,zb))."""
    ks = finished_knots(sA, sB, a, b, cut)
    names, bits, ok = all_words(ks)
    # distinctions that do not appear in any knot cannot occur (each distinction has a holder)
    key = lambda nm: bits[nm][ok]
    ra = ((key('x1') * 4 + key('x2') * 2 + key('x3')) * 2 + key('za'))
    rb = ((key('y1') * 4 + key('y2') * 2 + key('y3')) * 2 + key('zb'))
    J = np.zeros((16, 16), dtype=np.int64)
    np.add.at(J, (ra, rb), 1)
    return J, len(names)

def old_counts(sA, sB):
    ks = side_knots(sA, 'A') + side_knots(sB, 'B')
    names, bits, ok = all_words(ks)
    key = lambda nm: bits[nm][ok]
    xa = key('x1') * 4 + key('x2') * 2 + key('x3'); yb = key('y1') * 4 + key('y2') * 2 + key('y3')
    M = np.zeros((8, 8), dtype=np.int64)
    np.add.at(M, (xa, yb), 1)
    return M
