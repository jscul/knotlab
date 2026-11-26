"""weights.py: what growth does to the classes (README.md, part B). For every census start whose allowed states fall into
two or more classes under parity (classes.py, loose distinctions free), one round of growth under the ordinary count and
the two forbidding laws (A129, A130; canonical engine): the grown allowed space S' is linear, its projection P(S') onto
the start's distinctions is a subspace of S, and each class's weight under the equal weighting of grown states is
|ker P| times the size of its meet with P(S'), which is either 0 or one common value. So a class keeps the common
weight or is removed; read how many classes each law removes, and whether a removed class could be exchanged with a kept
one by a change that avoids the loose distinctions."""
import sys, json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import classes
forbid = classes.forbid
import numpy as np


def space(supports, names):
    idx = {d: i for i, d in enumerate(names)}; n = len(names)
    rows = [sum(1 << idx[d] for d in r) for r in supports]
    return classes.nullspace(rows, n)


def coset_key(v, Hbasis_piv):
    for p, h in Hbasis_piv:
        if (v >> p) & 1: v ^= h
    return v


def reduced(basis):
    piv = {}
    for v in basis:
        for p, h in list(piv.items()):
            if (v >> p) & 1: v ^= h
        if v:
            p = v.bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1: piv[q] ^= v
            piv[p] = v
    return sorted(piv.items(), reverse=True)


if __name__ == '__main__':
    S = forbid.census(); out = collections.Counter(); ex = []
    for i in range(len(S)):
        base = forbid.supports_of(S[i]); names = sorted({d for r in base for d in r})
        a = classes.analyse(base, False)
        if a.get('classes', 1) < 2: continue
        B = space(base, names)
        W = classes.span_words(B)[1:]; pc = classes.popcount(W); moves = set()
        for j in range(len(names)):
            m = (W >> np.uint64(j)) & np.uint64(1)
            if not m.any(): continue
            w = pc[m == 1].min()
            for v in W[(m == 1) & (pc == w)]: moves.add(int(v))
        Hp = reduced(list(moves))
        allS = [0] + [int(v) for v in W]
        cls = sorted({coset_key(v, Hp) for v in allS})
        for arm in forbid.ARMS:
            st, status, births = forbid.grown(base, 'parity', arm)
            if status != 'funded': out[(arm, 'no round')] += 1; continue
            gnames = sorted({d for r in st for d in r}); gidx = {d: k for k, d in enumerate(gnames)}
            Bg = space(st, gnames)
            # project each grown basis vector onto the start's distinctions (start names keep their numbers)
            proj = []
            for v in Bg:
                pv = 0
                for k, d in enumerate(names):
                    if (v >> gidx[d]) & 1: pv |= 1 << k
                proj.append(pv)
            img = classes.span_words([p for p in reduced(proj) and [h for _, h in reduced(proj)]])
            kept = sorted({coset_key(int(v), Hp) for v in img})
            out[(arm, 'classes', len(cls), 'kept', len(kept))] += 1
            if len(kept) < len(cls) and len(ex) < 4: ex.append((i, arm, len(cls), len(kept), a['a class change avoids the loose distinctions']))
            if len(kept) < len(cls): out[(arm, 'removes a class', 'class change avoids loose' if a['a class change avoids the loose distinctions'] else 'class fixed by loose')] += 1
    for k, v in sorted(out.items(), key=str): print(k, v)
    print('examples', ex)
