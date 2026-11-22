"""Independent four-name check of the source support and the meter obstructions.

Run with ordinary Python. No investigator code or stored source arrays are used.
Names in the printed four-place words are ordered a,c,b,d.
"""

from collections import Counter
from fractions import Fraction
from itertools import product


BITS = (0, 1)
ROWS = tuple(product(BITS, repeat=2))


def allows(law, triple):
    if law == "parity":
        return sum(triple) % 2 == 0
    return min(triple) != max(triple)


def source(first, companion, together):
    return {
        (a, c, b, d)
        for a, c, b, d in product(BITS, repeat=4)
        if allows(first, (a, c, b))
        and allows(companion, (a, c if together else b, d))
    }


def column(words, d, b):
    return tuple(int((a, c, b, d) in words) for a, c in ROWS)


def count_case(first, companion, together):
    words = source(first, companion, together)
    primary = {(a, c, b) for a, c, b, d in words}
    other = {(a, c if together else b, d) for a, c, b, d in words}
    for law, projection in ((first, primary), (companion, other)):
        assert projection == {t for t in product(BITS, repeat=3) if allows(law, t)}
        assert 0 < len(projection) < 8
        for discard in range(3):
            assert {t[:discard] + t[discard+1:] for t in projection} == set(ROWS)

    numbers = Counter((a, c, b) for a, c, b, d in words)
    expected = {("parity", "parity"):4, ("parity","nae"):6,
                ("nae","parity"):6, ("nae","nae"):10}
    assert len(words) == expected[first, companion]
    if first == "parity":
        # With the physical first-reader pair fixed, even parity fixes b.
        assert all((a,c,1-b,d) not in words for a,c,b,d in words)
    if companion == "parity" and not together:
        # The unread d separates the two parities of a,b. Neither reader
        # can individually change its member while the other stays put.
        assert all((a,c,1-b,d) not in words for a,c,b,d in words)
        assert all((1-a,c2,b,d) not in words for a,c,b,d in words for c2 in BITS)
    if first == "nae" and companion == "parity" and together:
        choices = {d:{(a,c,b) for a,c,b,e in words if d==e} for d in BITS}
        assert choices[0] == {(0,0,1),(1,1,0)}
        assert choices[1] == {(0,1,0),(0,1,1),(1,0,0),(1,0,1)}
    print(first, companion, "together" if together else "split", len(words), "/16",
          "primary completion multiplicities", dict(sorted(Counter(numbers.values()).items())))


def check_two_nae():
    together = source("nae","nae",True)
    shared_column = column(together,0,1)
    assert shared_column == column(together,1,0) == (0,1,1,0)
    # After resolving local residual work, a successful exact map on 00
    # would require the two slice matrices to be multiples of a common
    # invertible matrix, which has independent columns.

    split = source("nae","nae",False)
    for a,c in ROWS:
        b = 1-a
        assert all((a,c,b,d) in split for d in BITS)
        # Isolating any such basis input leaves the unread bit unrestricted.
        # No local sequence can be the first to change a or b on that input.
        for new_a in BITS:
            if new_a != a:
                assert all(any((new_a,c2,b,d) not in split for d in BITS) for c2 in BITS)
        assert any((a,c,1-b,d) not in split for d in BITS)
    # At fixed original a, one slice has a single possible b, and that
    # exact column is repeated in the other slice.
    for a in BITS:
        at = {w for w in split if w[0]==a}
        forced = {b for x,c,b,d in at if d==a}
        assert forced == {1-a}
        assert column(at,a,1-a) == column(at,1-a,1-a)

    # Relaxed comparison. Select a=c without reading their common value,
    # then allow unrestricted local transfers to private work.
    success = {(a,c,b,d) for a,c,b,d in split if a==c}
    assert success == {(a,a,1-a,d) for a,d in product(BITS,repeat=2)}
    print("Split NAE, unrestricted transfer control:", Fraction(len(success),len(split)))
    # Wordwise lawfulness blocks transfer while keeping both knots lawful.
    assert (0,0,0,1) not in split


def check_prepared_state_control():
    # The three intermediate work indices remember the two old a sectors.
    # At a=0 the first success combines c=0 and c=1 with opposite signs.
    first = ((Fraction(1,2), Fraction(-1,2),0,0),(0,0,1,0),(0,0,0,1))
    last = ((Fraction(2,3),0,Fraction(1,3)),(0,Fraction(1,3),Fraction(-1,3)))
    split = source("nae","nae",False)

    def apply(matrix, v):
        return tuple(sum(x*y for x,y in zip(row,v)) for row in matrix)

    pass_mass = 0
    forbidden_individual = []
    for a,c,b,d in sorted(split):
        if (a,1-a,0,d) not in split:
            forbidden_individual.append((a,c,b,d))
    assert forbidden_individual == [(0,0,1,0),(0,1,1,0)]
    for d,b in product(BITS,repeat=2):
        intermediate = apply(first,column(split,d,b))
        pass_mass += sum(t*t for t in intermediate)
        for work,amplitude in enumerate(intermediate):
            a = int(work != 0)
            if amplitude:
                assert (a,1-a,0,d) in split and (1,0,0,d) in split
        out = apply(last,intermediate)
        want = tuple(Fraction(int(i==b and d==0),3) for i in BITS)
        assert out == want
    assert pass_mass/len(split)==Fraction(21,40)
    # Norm of the two nonzero outputs (1/3 each), divided by ten input words.
    probability = Fraction(2,9*len(split))
    print("Split NAE with coherent-state lawfulness:", probability,
          "succeeds and", 1-probability, "is refused by the first calibration.")
    # The two eigenvalues of 9 K K^T solve x^2 - 7x + 9 = 0.
    g00 = sum(v*v for v in last[0])
    g01 = sum(v*z for v,z in zip(last[0],last[1]))
    g11 = sum(v*v for v in last[1])
    assert (9*g00,9*g01,9*g11)==(5,-1,2)
    assert 81*(g00*g11-g01*g01)==9
    # Maximal rescaling of this same success map multiplies its probability
    # by 18/(7+sqrt(13)). Both singular values then remain at most one.
    assert 7**2-4*9==13
    print("Rescaled success probability: (7-sqrt(13))/90")


if __name__ == "__main__":
    for first, companion, together in product(("parity","nae"),("parity","nae"),(True,False)):
        count_case(first,companion,together)
    check_two_nae()
    check_prepared_state_control()
