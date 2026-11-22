"""Independently reconstruct the three-reader inequality from the full ordinary truth table."""
import argparse
from collections import Counter
from fractions import Fraction
from functools import reduce
from math import gcd

import numpy as np


def signed_sum(bits):
    return (-1) ** bits.bit_count()


def source(law):
    """Array indexed by paid word, sibling word, then focal triple; each entry is zero or one."""
    paid, siblings, focal = np.ogrid[:16, :512, :8]
    legal = np.array([word.bit_count() % 2 == 0 if law == "parity" else 0 < word < 15
                      for word in range(16)])
    valid = legal[paid] & legal[((paid & 1) << 3) | focal]
    for i in range(3):
        sibling_knot = (((paid >> (i + 1)) & 1) << 3) | ((siblings >> (3*i)) & 7)
        valid = valid & legal[sibling_knot]
    return valid.astype(np.int64)


def witness(orientation):
    """Eight times the witness, built from signed or ordinary local outcome projectors."""
    matrix = np.zeros((8, 8), dtype=np.int64)
    target = 7 * orientation
    for setting in range(8):
        z = 7 ^ setting
        for answer in range(8):
            if setting == 7:
                coefficient = int(answer.bit_count() >= 2)
            elif setting == 0:
                coefficient = -int(answer == target)
            elif setting.bit_count() == 1:
                coefficient = -int(bool(setting & answer) and bool(z & (answer ^ target)))
            else:
                coefficient = 0
            vector = np.array([signed_sum(x & answer & setting) if not (x ^ answer) & z else 0
                               for x in range(8)])
            matrix += coefficient * (8 >> setting.bit_count()) * np.outer(vector, vector)
    return matrix


def read_names(words, bit):
    ordinary = [r for r in range(512) if not r & (1 << bit)]
    first = words[:, ordinary, :]
    second = words[:, [r | 1 << bit for r in ordinary], :]
    read = np.stack((first + second, first - second), axis=2).reshape(16, 512, 8)
    # Suppressing the paid outcome trace leaves a sum of outer products.
    retained = np.einsum("sri,srj->rij", read, read)
    characters = np.array([[signed_sum(s & h) for s in range(16)] for h in range(16)])
    amplitude = np.einsum("hs,sri->hri", characters, read)
    recorded = np.einsum("hri,hrj->hrij", amplitude, amplitude)
    assert np.array_equal(recorded.sum(axis=0), 16 * retained)
    return retained, recorded


def rows(grams, score):
    masses = np.trace(grams, axis1=-2, axis2=-1).ravel()
    eight_score = np.einsum("...ij,ij->...", grams, score).ravel()
    # The constraint on a pooled flag is sum(a * (7 * eight_score - 2 * mass)) >= 0.
    return [(int(w), int(7*y - 2*w)) for w,y in zip(masses, eight_score)]


def exact(rows):
    """An exact bounded integer budget and the exact fractional relaxation on identical items."""
    positive = [(w,s) for w,s in rows if s >= 0 and w]
    base = sum(w for w,s in positive)
    budget = sum(s for w,s in positive)
    losses = Counter((w,-s) for w,s in rows if s < 0 and w)
    if not losses or not budget:
        return Fraction(base), Fraction(base)
    available = sorted(losses, key=lambda k: Fraction(k[0],k[1]), reverse=True)
    balance = Fraction(budget)
    mixed = Fraction(base)
    for w,cost in available:
        count = min(Fraction(losses[w,cost]), balance/cost)
        mixed += w * count
        balance -= cost * count
        if not balance:
            break
    affordable = [(w,cost) for w,cost in available if cost <= budget]
    if not affordable:
        return Fraction(base), mixed
    unit = reduce(gcd, (cost for w,cost in affordable))
    limit = budget // unit
    best = np.zeros(limit + 1, dtype=np.int64)
    for w,cost in affordable:
        cost_units = cost // unit
        count = min(losses[w,cost],limit // cost_units)
        chunk = 1
        while count:
            take = min(chunk, count)
            need = take * cost_units
            # Copy from the previous array before updating this multiplicity chunk.
            best[need:] = np.maximum(best[need:], best[:-need] + w*take)
            count -= take
            chunk *= 2
    return Fraction(base + int(best[-1])), mixed


def proportions(rowlist, denominator):
    return tuple(p / denominator for p in exact(rowlist))


def price_mask(cells, mask, denominator):
    mass = sum(prob * cells[index][0] for index, prob in mask.items())
    surplus = sum(prob * cells[index][1] for index, prob in mask.items())
    if not mass:
        return Fraction(0), None
    return Fraction(mass, denominator), Fraction(surplus + 2*mass, 56*mass)


def checks_on_recorded_masks(retained, recorded, count):
    # The two ordinary siblings of the changed name are the high two retained
    # label bits in this independent ordering. Record index = 2*label + sign.
    det_ret = {385: Fraction(1)}
    det_clean = {0: Fraction(1), 385: Fraction(1)}
    random_ret = det_ret | {0: Fraction(1, 4)}
    random_clean = det_clean | {387: Fraction(13, 31)}
    focal_score = witness(0)
    old = rows(retained, focal_score)
    clean = rows(recorded[0], focal_score)
    for mode, branch, dest, den in (("retained", old, (det_ret, random_ret), 2*count),
                                    ("clean", clean, (det_clean, random_clean), 32*count)):
        optimum = proportions(branch, den)
        for mask, best in zip(dest, optimum):
            observed = price_mask(branch, mask, den)
            assert observed[0] == best and observed[1] >= Fraction(1,28)
            # An old Z-value tag on the changed sibling makes its two signs equally weighted.
            averaged = [[Fraction(x+y,2) for x,y in zip(row,branch[i^1])]
                        for i,row in enumerate(branch)]
            print(mode, "attaining mask", mask, "rate and excess", observed,
                  "sibling tag", price_mask(averaged, mask, den))
            if mode == "clean":
                print("paid-past tag still present at selected port",
                      price_mask(old, mask, den))
    diagnostics = [price_mask(rows(g, focal_score), det_clean, 32*count) for g in recorded]
    qualifying = [(h,p,v) for h,(p,v) in enumerate(diagnostics)
                  if p and v >= Fraction(1,28)]
    assert len(qualifying) == 8 and sum(p for h,p,v in qualifying) == Fraction(11,19208)
    print("Same deterministic mask applied at each erasure port:", diagnostics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, nargs="+", default=[8])
    args = parser.parse_args()
    for law in ("nae","parity"):
        words = source(law)
        count = int(words.sum())
        for bit in args.bits:
            retained, recorded = read_names(words,bit)
            assert np.trace(retained,axis1=-2,axis2=-1).sum() == 2*count
            for c in (0,1):
                obs = witness(c)
                for name, gram, denominator in (("retained",retained,2*count),
                                                ("clean",recorded[0],32*count)):
                    cells = rows(gram,obs)
                    best = proportions(cells,denominator)
                    print(law, "j", bit, "orientation",c,name,"total",count,
                          "deterministic",best[0],"randomized",best[1],
                          "eligible",sum(w>0 and s>=0 for w,s in cells))
            if law == "nae" and bit == 8:
                checks_on_recorded_masks(retained, recorded, count)

if __name__ == "__main__":
    main()
