"""named.py: the named cases of SIDE-SIGN-20261126-001 (README.md, 'Population').

    named.py rings          N1, N2: bare rings of 5, 4 and 6 knots with two loose distinctions each, rounds 0 and 1, with the
                            preserved class sign W5 (the parity of the old shared distinctions) beside the swap's weightings
    named.py lone           N3: the lone four-place knot grown to its end (16 knots)
    named.py partnered [R]  N4: the partnered start of order three (a blow-up), rounds 0..R under parity by exact sums
    named.py classes I0 I1  P9: each swap's action on the other thread's classes, census stages of rounds 0 and 1
"""
import sys, json, itertools
import numpy as np
from pathlib import Path
import sides as S

ROOT = Path(__file__).resolve().parents[2]


def ring(n, loose=2):
    """knot i shares one distinction with knot i + 1 (mod n) and holds `loose` loose distinctions"""
    sup = [[] for _ in range(n)]
    for i in range(n):
        sup[i].append(i); sup[(i + 1) % n].append(i)
    nxt = n
    for i in range(n):
        for _ in range(loose): sup[i].append(nxt); nxt += 1
    return sup


def class_sign(P, old):
    """W5: (-1)^(sum of the old shared distinctions), the preserved two-class sign of READS-HOLDERS-SOURCES-20261120-001"""
    m = np.uint64(sum(1 << P.index[d] for d in old))
    return lambda x: (1 - 2 * (np.bitwise_count(x & m).astype(np.int64) & 1)).astype(np.int8)


def compare_w5(P, law, old):
    """is W5 unchanged by every swap; and on the states a swap keeps or flips, does W3 equal W5"""
    x = S.states(P, law)
    if x is None: return 'not run: too many states'
    w5 = class_sign(P, old)(x)
    auts, _ = P.automorphisms(); out = []
    for p in S.involution_classes(auts, S.involutions(auts)):
        for maximal in (False, True):
            sig = P.lift(p, maximal)
            sx = S.apply_sig(x, P, sig)
            pos = {v: i for i, v in enumerate(x.tolist())}
            w5s = w5[[pos[v] for v in sx.tolist()]]
            full = np.uint64((1 << P.D) - 1)
            keep = sx == x; flip = sx == (x ^ full)
            out.append({'perm': p, 'lift': 'max' if maximal else 'min', 'kind': P.sides(p, sig)[0],
                        'W5 unchanged by the swap': bool((w5s == w5).all()), 'kept': int(keep.sum()), 'flipped': int(flip.sum()),
                        'W5 on kept': sorted(set(w5[keep].tolist())), 'W5 on flipped': sorted(set(w5[flip].tolist()))})
    return out


def rings():
    for n in (5, 4, 6):
        base = ring(n)
        for law in ('parity', 'nae'):
            stages, status = S.grow_rounds(base, law, 1)
            for r, st in enumerate(stages):
                P = S.Pattern(st)
                old = [d for d in range(n)]              # the ring's own shared distinctions
                res = S.analyse(P, law, extra={'W5': class_sign(P, old)})
                print(json.dumps({'case': f'ring-{n}', 'law': law, 'round': r, 'K': P.K, 'D': P.D,
                                  'W5 against the swaps': compare_w5(P, law, old), **res}, default=str), flush=True)


def lone():
    for law in ('parity', 'nae'):
        stages, status = S.grow_rounds([[0, 1, 2, 3]], law, 6)
        P = S.Pattern(stages[-1])
        res = S.analyse(P, law)
        print(json.dumps({'case': 'lone four-place knot, end', 'law': law, 'round': len(stages) - 1, 'status': status,
                          'K': P.K, 'D': P.D, **res}, default=str), flush=True)


def partnered_start(n=3):
    from importlib.util import spec_from_file_location, module_from_spec
    path = ROOT / 'proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/hublib.py'
    spec = spec_from_file_location('hublib_for_sides', path); HB = module_from_spec(spec); sys.modules['hublib_for_sides'] = HB
    spec.loader.exec_module(HB)
    pts = list(range(2 * n))
    blocks = [frozenset((u, v)) for u, v in itertools.combinations(pts, 2) if u // 2 != v // 2]
    opn = [2 ** (n - 1)] * (2 * n)
    L = len(opn); e = []
    for h, B in enumerate(blocks):
        for k in sorted(B): e.append((k, L + h))
    from collections import Counter
    sh = Counter()
    for a, b in e: sh[a] += 1; sh[b] += 1
    sizes = [sh[k] + opn[k] for k in range(L)] + [sh[L + h] for h in range(len(blocks))]
    sizes, edges = HB.hub_realization(sizes, e)
    return [sorted(s) for s in S.forbid().ENGINE.J.stars_from(sizes, edges)]


def partnered_symmetric(n=3):
    """the partnered start with every renaming of its points kept: live knots 0..2n-1 with 2^(n-1) loose distinctions each,
    one dead knot per block {u, v} (u, v not partners) sharing a distinction with u and with v, and each dead knot sharing
    its third distinction with the dead knot of the partner block {u', v'} (u' the partner of u).  Its blocks N(w) ∩ live
    are those of WALL-READ's start, so by Lemma R its rounds from 1 on are the same; the hub realization's connector chain,
    which has no symmetry, is left out."""
    pts = list(range(2 * n)); partner = lambda u: u ^ 1
    blocks = [(u, v) for u, v in itertools.combinations(pts, 2) if u // 2 != v // 2]
    sup = [[] for _ in pts] + [[] for _ in blocks]; nxt = 0
    for h, (u, v) in enumerate(blocks):
        for k in (u, v): sup[k].append(nxt); sup[2 * n + h].append(nxt); nxt += 1
    index = {b: h for h, b in enumerate(blocks)}
    for h, (u, v) in enumerate(blocks):
        g = index[tuple(sorted((partner(u), partner(v))))]
        if h < g: sup[2 * n + h].append(nxt); sup[2 * n + g].append(nxt); nxt += 1
    for k in pts:
        for _ in range(2 ** (n - 1)): sup[k].append(nxt); nxt += 1
    return sup


def partnered(R):
    base = partnered_symmetric()
    stages, status = S.grow_rounds(base, 'parity', R)
    for r, st in enumerate(stages):
        P = S.Pattern(st)
        small = S.states(P, 'parity') is not None
        res = S.analyse(P, 'parity', gauss_path=not small)
        print(json.dumps({'case': 'partnered start of order 3, every renaming kept', 'law': 'parity', 'round': r, 'K': P.K, 'D': P.D,
                          'parity_dim': P.parity_dim(), 'path': 'enumeration' if small else 'exact sums', **res}, default=str),
              flush=True)


def classes_action(i0, i1):
    """P9: on census stages (rounds 0 and 1, parity) with a swap, the other thread's classes (shortest changes through each
    distinction, TWO-CLASS-SIGN-20261126-001's classes2.analyse, read as code) and each swap's action on them"""
    sys.path.insert(0, str(ROOT / 'research' / 'TWO-CLASS-SIGN-20261126-001'))
    import classes2
    F = S.forbid(); starts = S.census_starts()
    for i in range(i0, min(i1, len(starts))):
        stages, status = S.grow_rounds(F.supports_of(starts[i]), 'parity', 1)
        for r, st in enumerate(stages):
            P = S.Pattern(st)
            auts, _ = P.automorphisms(); invs = S.involutions(auts)
            if not invs: continue
            try:
                res, names = classes2.analyse([list(s) for s in st])
            except Exception as e:
                print(json.dumps({'start': i, 'round': r, 'error': repr(e)})); continue
            rec = res['shortest through each distinction']; ncls = rec['classes']
            if ncls < 2: continue
            assert names == P.dist
            H = echelon(list(rec['_moves'])); B = S.parity_basis(P)
            acts = []
            for p in S.involution_classes(auts, invs):
                for maximal in (False, True):
                    sig = P.lift(p, maximal)
                    perm = {P.index[d]: P.index[sig[d]] for d in P.dist}
                    move = lambda v: sum(1 << perm[k] for k in range(P.D) if v >> k & 1)
                    identity = all(reduce(H, b ^ move(b)) == 0 for b in B)
                    acts.append({'perm': p, 'lift': 'max' if maximal else 'min', 'identity on the classes': identity})
            print(json.dumps({'start': i, 'round': r, 'classes': ncls, 'swaps': acts}, default=str), flush=True)


def echelon(vecs):
    piv = {}
    for v in vecs:
        for b in sorted(piv, reverse=True):
            if v >> b & 1: v ^= piv[b]
        if v: piv[v.bit_length() - 1] = v
    return piv


def reduce(piv, v):
    for b in sorted(piv, reverse=True):
        if v >> b & 1: v ^= piv[b]
    return v


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'rings': rings()
    elif cmd == 'lone': lone()
    elif cmd == 'partnered': partnered(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif cmd == 'classes': classes_action(int(sys.argv[2]), int(sys.argv[3]))
