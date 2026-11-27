"""bonds.py: bonds among agreement readings on a stage.  RING-BOND-20261127-001; README.md.

A reading is an agreement [the distinctions of its carrier C all take one value], for a carrier of two or three
distinctions (unchanged when every value is flipped, using every place).  A bond is three readings on pairwise disjoint
carriers whose joint values over the allowed states (under the stage's law) miss at least one of the eight triples while
every pair of them takes all four, such that removing any one knot's law lets all eight occur (every law essential),
and no reading is a function of one knot's values (none read at a single knot).  Everything is exact, by enumerating
all assignments of the stage's distinctions."""
import itertools, collections


def assignments(sup, law):
    names = sorted({x for r in sup for x in r}); idx = {x: i for i, x in enumerate(names)}; n = len(names)
    masks = [sum(1 << idx[x] for x in r) for r in sup]
    N = 1 << n
    viol = [0] * N                                      # bitmask over knots of the laws each assignment breaks
    for s in range(N):
        v = 0
        for k, m in enumerate(masks):
            c = bin(s & m).count('1')
            bad = (c % 2 == 1) if law == 'parity' else (c == 0 or c == bin(m).count('1'))
            if bad: v |= 1 << k
        viol[s] = v
    allowed = sum(1 << s for s in range(N) if viol[s] == 0)
    without = [sum(1 << s for s in range(N) if viol[s] in (0, 1 << k)) for k in range(len(sup))]
    return names, idx, n, allowed, without


def reading_bits(C, idx, n):
    """bitset over all assignments of [the carrier's distinctions are all equal]"""
    bits = [idx[x] for x in C]; out = 0
    for s in range(1 << n):
        vals = {(s >> b) & 1 for b in bits}
        if len(vals) == 1: out |= 1 << s
    return out


def bonds(sup, law, sizes=(2, 3)):
    names, idx, n, allowed, without = assignments(sup, law)
    FULL = (1 << (1 << n)) - 1
    carriers = [C for k in sizes for C in itertools.combinations(names, k)]
    R = {C: reading_bits(C, idx, n) for C in carriers}
    # nonconstant on the allowed states
    carriers = [C for C in carriers if R[C] & allowed and (~R[C] & FULL) & allowed]
    # read at a single knot: constant on every class of allowed states agreeing on that knot's distinctions
    def read_by_knot(C):
        for r in sup:
            ks = [idx[x] for x in r]; seen = {}
            ok = True; a = allowed; s = 0
            while a:
                low = a & -a; s = low.bit_length() - 1; a ^= low
                key = tuple((s >> b) & 1 for b in ks); val = (R[C] >> s) & 1
                if seen.setdefault(key, val) != val: ok = False; break
            if ok: return True
        return False
    unread = {C: not read_by_knot(C) for C in carriers}
    def words(Cs, mask):
        out = set()
        for vals in itertools.product((0, 1), repeat=len(Cs)):
            m = mask
            for C, v in zip(Cs, vals):
                m &= R[C] if v else (~R[C] & FULL)
                if not m: break
            if m: out.add(vals)
        return out
    found = []
    pair_free = {}
    def free(a, b):
        key = (a, b)
        if key not in pair_free: pair_free[key] = len(words((a, b), allowed)) == 4
        return pair_free[key]
    cs = [C for C in carriers if unread[C]]
    for a, b, c in itertools.combinations(cs, 3):
        if set(a) & set(b) or set(a) & set(c) or set(b) & set(c): continue
        if not (free(a, b) and free(a, c) and free(b, c)): continue
        w = words((a, b, c), allowed)
        if len(w) == 8: continue
        if all(len(words((a, b, c), without[k])) == 8 for k in range(len(sup))):
            found.append({'carriers': [list(a), list(b), list(c)], 'words': len(w),
                          'missing': [''.join(map(str, v)) for v in itertools.product((0, 1), repeat=3) if v not in w]})
    return {'distinctions': n, 'allowed': bin(allowed).count('1'), 'readings': len(carriers), 'unread readings': len(cs), 'bonds': found}


def shared_readings(found):
    cnt = collections.Counter(tuple(C) for b in found for C in map(tuple, b['carriers']))
    return {'readings in bonds': len(cnt), 'readings in two or more bonds': sum(1 for v in cnt.values() if v >= 2)}
