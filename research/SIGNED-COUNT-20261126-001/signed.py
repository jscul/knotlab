"""signed.py: a reader's statistics under the count weighting, written through the signed form (README.md).
Not-all-equal on three places is (3 - s1 s2 - s1 s3 - s2 s3) / 4 with s = (-1)^x, so the number of allowed states of a
structure, and the count behind any reading, expand into a sum over choices of one term per knot (its constant or one of
its three pair products), each term signed by (-1) to the number of pair products chosen and nonzero only where every
distinction is used an even number of times (the literature's loop expansion). Parity's indicator is (1 + s1 s2 s3)/2 on
three places, so its expansion has no negative coefficient, and a character sum over its allowed space is 0 or the size.
On two starts with a loop (the advisor's ring of four and ring of three), with and without a far edit: the signed parts
of the expansion behind a near reader's statistic, the statistic itself, and the identity that the edited count is the
unedited count plus the count with the far knot deleted."""
import sys, json, itertools
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import forbid


def nae_terms(row):
    """the signed expansion of a not-all-equal knot on its places, constants merged (the advisor's fix): NAE = 1 - [all
    equal] and [all equal] = 2^(1-k) * sum over even subsets of the product, so the constant is 1 - 2^(1-k) and each
    nonempty even subset has -2^(1-k)"""
    k = len(row); out = [(1 - Fraction(1, 2 ** (k - 1)), frozenset())]
    for r in range(2, k + 1, 2):
        for sub in itertools.combinations(row, r):
            out.append((-Fraction(1, 2 ** (k - 1)), frozenset(sub)))
    return out


def expand(supports, extra):
    """sum over x of prod_knots NAE * prod over the reading's extra spins: positive and negative parts of the expansion"""
    names = sorted({d for r in supports for d in r}); n = len(names)
    pos = neg = Fraction(0)
    choices = [nae_terms(r) for r in supports]
    for pick in itertools.product(*choices):
        coef = Fraction(1); used = {}
        for c, sub in pick:
            coef *= c
            for d in sub: used[d] = used.get(d, 0) ^ 1
        for d in extra: used[d] = used.get(d, 0) ^ 1
        if any(used.values()): continue                       # an odd use of a distinction sums to zero over x
        term = coef * 2 ** n
        if term > 0: pos += term
        else: neg += term
    return pos, neg


def direct(supports, extra):
    names = sorted({d for r in supports for d in r}); idx = {d: i for i, d in enumerate(names)}; tot = 0
    for bits in itertools.product((0, 1), repeat=len(names)):
        if all(0 < sum(bits[idx[d]] for d in r) < len(r) for r in supports):
            s = 1
            for d in extra: s *= (-1) ** bits[idx[d]]
            tot += s
    return tot


def mean(supports, extra):
    return Fraction(direct(supports, extra), direct(supports, ()))


if __name__ == '__main__':
    # the advisor's examples, starts with a loop: a ring of four three-place knots (A and B share no distinction) and a
    # ring of three; Alice reads the product of the two distinctions her knot shares; Bob's edit adds one loose
    # distinction to his knot. Read: the count and Alice's statistic with and without Bob's edit, their signed parts,
    # and whether the edited count is the unedited count plus the count with Bob's knot deleted (a nonnegative mixture).
    cases = {'ring of four': (((0, 1, 10), (0, 2, 11), (1, 3, 12), (2, 3, 13)), 3, (0, 1)),       # 10-13 loose
             'ring of three': (((0, 1, 10), (0, 2, 11), (1, 2, 13)), 2, (0, 1))}
    for name, (base, bob, read) in cases.items():
        edited = tuple(r + (20,) if i == bob else r for i, r in enumerate(base))
        without = tuple(r for i, r in enumerate(base) if i != bob)
        free = 2 ** len(set(base[bob]) - {d for i, r in enumerate(base) if i != bob for d in r})   # the far knot's own distinctions, kept unconstrained
        row = {'case': name}
        for label, sup in (('no edit', base), ("Bob's edit", edited)):
            p, q = expand(sup, read); pc, qc = expand(sup, ())
            row[label] = {'count': direct(sup, ()), 'count, signed parts': [str(pc), str(qc)],
                          "Alice's statistic": str(mean(sup, read)), 'its sum, signed parts': [str(p), str(q)]}
        row['edited = unedited + with the far knot deleted'] = {
            'count': direct(edited, ()) == direct(base, ()) + free * direct(without, ()),
            "Alice's sum": direct(edited, read) == direct(base, read) + free * direct(without, read)}
        print(json.dumps(row))
