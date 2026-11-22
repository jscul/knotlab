"""Independently price the fixed orientation inequality from complete sixteen-bit holdings."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import product


def allowed(value, width, law):
    return value.bit_count() % 2 == 0 if law == "parity" else value not in (0, (1 << width) - 1)


def families(law):
    # Each of the four original bits pays one child. Each child has three fresh bits.
    original = [s for s in range(16) if allowed(s, 4, law)]
    for r in range(512):
        out = Counter()
        for s in original:
            if all(allowed(((s >> (j + 1) & 1) << 3) | (r >> (3*j) & 7), 4, law) for j in range(3)):
                out[s & 1] += 1
        yield (out[0], out[1])


@cache
def focal(law, clean, a, b):
    vectors = [[int(allowed((d << 3) | x, 4, law)) for x in range(8)] for d in range(2)]
    u, v = vectors
    amp = [a*i + b*j for i,j in zip(u,v)]
    gram = [[amp[x]*amp[y] if clean else a*u[x]*u[y] + b*v[x]*v[y] for y in range(8)] for x in range(8)]
    w = sum(gram[i][i] for i in range(8))
    def event(setting, predicate):
        total = 0
        for outcome in range(8):
            if not predicate(outcome):
                continue
            matching = [i for i in range(8) if (i ^ outcome) & (7 ^ setting) == 0]
            for i,j in product(matching, repeat=2):
                sign = (-1) ** ((i ^ j) & outcome & setting).bit_count()
                total += sign*gram[i][j]
        return Fraction(total, 2 ** setting.bit_count())
    excess = event(7, lambda y:y.bit_count() >= 2) - gram[0][0]
    for name in (1,2,4):
        excess -= event(name, lambda y:(y & name) and (y & (7 ^ name)))
    if law == "nae":
        # Independent evaluation using the two template vectors missing 000 and 111.
        assert 2*excess == (a*a + a*b - 4*b*b if clean else a - 4*b)
        assert w == (7*a*a + 12*a*b + 7*b*b if clean else 7*(a+b))
    return w, excess


def optimize(items, target, fraction_step=None):
    # Keep all strictly profitable records and all exactly balanced ones.
    credit = Fraction(0)
    mass = Fraction(0)
    remaining = []
    for w, score in items:
        surplus = score - target*w
        if not w:
            continue
        if surplus >= 0:
            credit += surplus
            mass += w
        else:
            remaining.append((-surplus, w))
    if mass == 0:
        return mass
    if remaining and fraction_step is not None:
        # A direct exact obstruction for the integer and fair-bit cases in this study.
        assert min(d for d,w in remaining)*fraction_step > credit
        return mass
    # Exchange: one unit of surplus spent on the highest mass per cost maximizes mass.
    remaining.sort(key=lambda pair:Fraction(pair[1],pair[0]),reverse=True)
    for deficit,w in remaining:
        q = min(Fraction(1), credit/deficit)
        mass += w*q
        credit -= deficit*q
        if not credit:
            break
    return mass


def main():
    assignments = list(product(range(8), repeat=2))
    assert max(int(x.bit_count() >= 2) - int(z == 0)
               - sum(bool(x & k) and bool(z & (7 ^ k)) for k in (1,2,4))
               for z,x in assignments) == 0
    for law in ("nae","parity"):
        coeff = list(families(law))
        n = sum(focal(law,False,*c)[0] for c in coeff)
        for clean in (False, True):
            items = [focal(law,clean,*c) for c in coeff]
            den = n*(16 if clean else 1)
            clean_rate = Fraction(sum(w for w,s in items), den)
            target = Fraction(1,28)
            strict = optimize(items,target,1)/den
            fair = optimize(items,target,Fraction(1,2))/den
            random = optimize(items,target)/den
            assert strict == fair
            coarse = [tuple(x+y for x,y in zip(items[r],items[r+256])) for r in range(256)]
            coarse_rate = optimize(coarse,target)/den
            full_excess = optimize(items,2*target)/den
            if law == "nae":
                assert strict == Fraction(1, 76832 if clean else 4802)
                assert random == (Fraction(630,31*den) if clean else Fraction(10,den))
                assert full_excess == strict and coarse_rate == 0
            else:
                assert strict == random == coarse_rate == full_excess == 0
            print(law,"clean" if clean else "retained","port",clean_rate,"deterministic",strict,
                  "randomized",random,"eight bits",coarse_rate,"threshold 1/14",full_excess)

    # Fix eight other sibling bits at zero and ask the supplied change question on the ninth.
    # Its two outcomes have opposite interference terms but identical diagonals on these words.
    marginal = list(families("nae"))
    u, v = marginal[0], marginal[1]
    rows = []
    for sign in (1,-1):
        a,b = (i+sign*j for i,j in zip(u,v))
        w,j = focal("nae",True,a,b)
        rows.append((Fraction(w,2),j/2))
    (wp,jp),(wm,jm)=rows
    wd,jd=(Fraction(sum(values),2) for values in zip(focal("nae",True,*u),focal("nae",True,*v)))
    assert wp+wm==2*wd and jp+jm==2*jd
    assert (wp,jp/wp,wm,jm/wm,Fraction(wd),jd/wd)==(53,Fraction(2,53),13,Fraction(-1,26),33,Fraction(1,44))
    print("Fixed sibling change read: plus mass 53/537824 and excess 2/53.",
          "A fair bit on the same ordinary words gives only 1/44 excess.")


if __name__ == "__main__":
    main()
