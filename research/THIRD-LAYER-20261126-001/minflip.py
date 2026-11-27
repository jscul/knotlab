"""minflip.py: the least size of an allowed change that flips a parity (the least flipping change), by a solver.
THIRD-LAYER-20261126-001.  An allowed change is a set z of distinctions meeting every knot evenly; it flips a parity f
when it meets f's support oddly.  least(st, f, kmax) is the least |z|; None for a fixed parity (a sum of laws), and the string 'more than kmax' for a least above kmax."""
import itertools
from pysat.solvers import Minisat22
from pysat.card import CardEnc, EncType


def least(st, support, kmax=30):
    names = sorted({x for r in st for x in r}); idx = {x: i + 1 for i, x in enumerate(names)}
    top = [len(names)]
    def new(): top[0] += 1; return top[0]
    base = []
    def xor(vs, val):
        acc = vs[0]
        for y in vs[1:]:
            z = new(); base.extend([[-z, acc, y], [-z, -acc, -y], [z, -acc, y], [z, acc, -y]]); acc = z
        base.append([acc] if val else [-acc])
    for r in st: xor([idx[x] for x in r], 0)
    xor([idx[x] for x in support], 1)
    lits = [idx[x] for x in names]
    s = Minisat22(bootstrap_with=base)
    if not s.solve(): s.delete(); return None          # f is a sum of laws: no change flips it
    s.delete()
    def sat(k):
        card = CardEnc.atmost(lits=lits, bound=k, top_id=top[0], encoding=EncType.seqcounter)
        s2 = Minisat22(bootstrap_with=base + card.clauses); ok = s2.solve()
        w = sum(1 for l in lits if s2.get_model()[l - 1] > 0) if ok else None
        s2.delete(); return w
    w = sat(kmax)
    if w is None: return 'more than %d' % kmax
    lo, hi = 0, w                                      # least is in (lo, hi]
    while hi - lo > 1:
        mid = (lo + hi) // 2; w2 = sat(mid)
        if w2 is None: lo = mid
        else: hi = w2
    return hi
