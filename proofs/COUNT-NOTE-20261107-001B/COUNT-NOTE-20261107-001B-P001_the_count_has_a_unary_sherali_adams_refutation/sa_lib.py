"""The sphere's count as a unary Sherali-Adams refutation, for COUNT-NOTE-20261107-001B.

Polynomials are multilinear, stored as {frozenset(points): integer coefficient}. A conjunction is a dict {point: value}; its
polynomial is the product of x_p (value 1) and 1 - x_p (value 0). A Sherali-Adams refutation of a clause set is an identity
sum_i c_i J_i = 1 between multilinear polynomials in which every J_i with c_i > 0 is the falsifying conjunction of a clause and
every J_i with c_i < 0 is a conjunction. On an assignment that satisfies every clause the left side is at most 0, so no such
assignment exists. The refutation is unary when the c_i are integers of polynomial size; here every c_i is +1 or -1 and every J_i
has exactly three literals."""
import itertools
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/TWO-ROUND-BRIDGE-20261106-001B/TWO-ROUND-BRIDGE-20261106-001B-P001_three_fold_spaces_are_an_euler_count"))
import count_lib as C  # noqa: E402

ONE = {frozenset(): 1}


def add(P, Q, c=1):
    R = defaultdict(int, P)
    for m, v in Q.items():
        R[m] += c * v
    return {m: v for m, v in R.items() if v}


def mul(P, Q):
    R = defaultdict(int)
    for m1, v1 in P.items():
        for m2, v2 in Q.items():
            R[m1 | m2] += v1 * v2
    return {m: v for m, v in R.items() if v}


def literal(p, sign):
    """x_p xor sign"""
    return {frozenset([p]): 1} if not sign else {frozenset(): 1, frozenset([p]): -1}


def conj(assign):
    P = ONE
    for p, v in assign.items():
        P = mul(P, literal(p, 1 - v))
    return P


def agreement(ya, yb):
    """1 when the two literals are equal, 0 otherwise: 1 - ya - yb + 2 ya yb"""
    return add(add(add(ONE, ya, -1), yb, -1), mul(ya, yb), 2)


def evaluate(P, x):
    return sum(v for m, v in P.items() if all(x[q] for q in m))


def sphere(k):
    lines, signs, n = C.signed_space(C.octa_dual(k))
    return [tuple(L) for L in lines], [tuple(int(s) for s in S) for S in signs], n


def certificate(k):
    """The refutation's terms [(coefficient, conjunction)] for K_k, with the local identities it rests on.

    Lines: the sum of a line's three corner agreements is 1 + 2 N_l, where N_l is the sum of its two clauses' falsifying conjunctions.
    Faces: the sum of a face's corner agreements is 1 on a two-point (corner) face and 1 + 2 M_f on a three-point face, where M_f is
    the sum of two complementary conjunctions on the face's points. Every corner lies on one line and one face, and there are two
    more faces than lines, so sum_l N_l - sum_f M_f = 1."""
    lines, signs, n = sphere(k)
    sg = {(i, p): s for i, (L, S) in enumerate(zip(lines, signs)) for p, s in zip(L, S)}
    terms, info = [], {"line identities hold": True, "corner faces sum to 1": True, "three-point faces give two complementary conjunctions": True}
    for i, L in enumerate(lines):
        low = {p: sg[(i, p)] for p in L}            # every literal 0: falsifies (y_a or y_b or y_c)
        high = {p: 1 - sg[(i, p)] for p in L}       # every literal 1: falsifies (not y_a or not y_b or not y_c)
        terms += [(1, low), (1, high)]
        S = {}
        for a, b in itertools.combinations(L, 2):
            S = add(S, agreement(literal(a, sg[(i, a)]), literal(b, sg[(i, b)])))
        info["line identities hold"] &= add(add(S, ONE, -1), add(conj(low), conj(high)), -2) == {}
    cs, fpts = C.corners([list(L) for L in lines], n)
    byf = defaultdict(list)
    for l, a, b, f in cs:
        byf[f].append((l, a, b))
    sizes = defaultdict(int)
    for f, crn in byf.items():
        S = {}
        for l, a, b in crn:
            S = add(S, agreement(literal(a, sg[(l, a)]), literal(b, sg[(l, b)])))
        R = add(S, ONE, -1)
        P = fpts[f]
        sizes[len(P)] += 1
        if len(P) == 2:
            info["corner faces sum to 1"] &= R == {}
            continue
        if any(v % 2 for v in R.values()):
            info["three-point faces give two complementary conjunctions"] = False
            continue
        M = {m: v // 2 for m, v in R.items()}
        ones = [u for u in itertools.product((0, 1), repeat=len(P)) if evaluate(M, dict(zip(P, u))) == 1]
        ok = len(ones) == 2 and tuple(1 - b for b in ones[0]) == ones[1]
        ok = ok and M == add(conj(dict(zip(P, ones[0]))), conj(dict(zip(P, ones[1]))))
        info["three-point faces give two complementary conjunctions"] &= ok
        terms += [(-1, dict(zip(P, ones[0]))), (-1, dict(zip(P, ones[1])))]
    total = {}
    for c, J in terms:
        total = add(total, conj(J), c)
    info.update({"points": n, "lines": len(lines), "faces by number of points": dict(sorted(sizes.items())),
                 "faces minus lines": len(fpts) - len(lines), "sum of the terms is the constant 1": total == ONE})
    return terms, info


def falsifiers(k):
    """the falsifying conjunctions of the formula's own clauses (count_lib.nae_clauses)"""
    lines, signs, n = sphere(k)
    out = set()
    for cl in C.nae_clauses([list(L) for L in lines], [list(S) for S in signs]):
        out.add(frozenset((abs(x) - 1, 0 if x > 0 else 1) for x in cl))
    return out
