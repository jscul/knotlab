"""Brute-force count of homomorphisms pi1(S^3_p(K)) -> G for a closed braid K.

All meridians of a knot are conjugate, so a homomorphism is fixed by the image
g of top arc 0 and images of the other top arcs inside the class of g.  The
search assigns the top arcs position by position (depth-first), pushes the
crossings through as soon as both of their input arcs are known, rejects as
soon as a position's bottom arc is final and differs from its top arc
(closure), and at the leaves checks the surgery relator x_0^p * lambda.

`literal=True` enumerates every g in G; otherwise one representative per
conjugacy class is used and weighted by the class size (the number of
homomorphisms with x_0 = g only depends on the class of g).

Independent replay code: written from scratch, standard library only.
"""
from group import MULT, INV, IDENTITY, ORDER, conjugacy_classes, decode

CLASSES = conjugacy_classes()
CLASS_OF = {g: cls for cls in CLASSES for g in cls}


def _search(knot, x0, leaf):
    n, L = knot.n, len(knot.crossings)
    crossings, max_pos = knot.crossings, knot.max_pos
    last, bottom = knot.last_touch, knot.bottom
    cls = CLASS_OF[x0]
    img = [IDENTITY] * knot.n_arcs

    def rec(j, c):
        count = 0
        for g in ((x0,) if j == 0 else cls):
            img[j] = g
            c2 = c
            while c2 < L and max_pos[c2] <= j:
                over, inn, out, sign = crossings[c2]
                o = img[over]
                if sign > 0:
                    img[out] = MULT[MULT[INV[o]][img[inn]]][o]
                else:
                    img[out] = MULT[MULT[o][img[inn]]][INV[o]]
                c2 += 1
            ok = True
            for q in range(j + 1):                 # positions that just became final
                if last[q] < c2 and not (q < j and last[q] < c):
                    if img[bottom[q]] != img[q]:
                        ok = False
                        break
            if not ok:
                continue
            if j == n - 1:
                count += leaf(img)
            else:
                count += rec(j + 1, c2)
        return count

    return rec(0, 0)


def count_homs(knot, p, literal=False):
    """|Hom(pi1(S^3_p(K)), G)|, and the split by the meridian's coset N h^k."""
    def leaf(img):
        return 1 if knot.surgery_value(img, p) == IDENTITY else 0

    starts = ([(g, 1) for g in range(ORDER)] if literal
              else [(cls[0], len(cls)) for cls in CLASSES])
    total, by_coset = 0, [0, 0, 0]
    for x0, weight in starts:
        c = weight * _search(knot, x0, leaf)
        total += c
        by_coset[decode(x0)[3]] += c
    return total, by_coset


def check_longitude(knot):
    """For every homomorphism of the knot group (closure relations only) to G,
    check that lambda maps into G'' = Z(N) = {(0,0,z,0)} and commutes with the
    meridian x_0.  Returns the number of knot-group homomorphisms."""
    bad = []

    def leaf(img):
        lam = knot.longitude_value(img)
        x, y, z, k = decode(lam)
        if (x, y, k) != (0, 0, 0) or MULT[lam][img[0]] != MULT[img[0]][lam]:
            bad.append(tuple(img[:knot.n]))
        return 1

    total = sum(len(cls) * _search(knot, cls[0], leaf) for cls in CLASSES)
    if bad:
        raise AssertionError("longitude check failed for %d homs" % len(bad))
    return total
