"""Independent one-use encoding check. An erasure symbol is computed without the sibling record."""
from collections import Counter
from fractions import Fraction
from itertools import combinations

import numpy as np

from independent_rates import exact, read_names, rows, source, witness
from erasure_access import fractional_mask


def records(law,c):
    words = source(law)
    unused, ports = read_names(words,8)
    cells = np.asarray(rows(ports,witness(c)),dtype=np.int64).reshape(16,512,2)
    return cells,32*int(words.sum())


def types(cells):
    # Compute exact integer pairs and multiplicity after grouping identical items.
    array, mult = np.unique(np.reshape(cells,(-1,2)),axis=0,return_counts=True)
    return {(int(w),int(s)): int(k) for (w,s),k in zip(array,mult)}


def whole_and_mixed(hist):
    # exact() also checks multiplicities and the integer budget when it is positive.
    return exact([key for key,k in hist.items() for _ in range(k)])


def scalar(hist, slope):
    u,v = slope.numerator,slope.denominator
    return Fraction(sum(k*max(0,w*v+s*u) for (w,s),k in hist.items()),v)


def full_multiplier(hist):
    candidates = {Fraction(0)} | {Fraction(w,-s) for w,s in hist if s<0}
    return min(candidates,key=lambda l:(scalar(hist,l),l))


def merged(cells,grouping):
    return np.array([cells[list(g)].sum(axis=0) for g in grouping])


def face(hist,slope):
    # All tied items are optional. Return both extreme slopes of the exposed set.
    num,den=slope.numerator,slope.denominator
    wgt=0
    low=0
    high=0
    for (w,s),k in hist.items():
        reduced=w*den+s*num
        if reduced>0:
            wgt+=k*reduced
            low+=k*s
            high+=k*s
        elif reduced==0:
            low+=k*min(s,0)
            high+=k*max(s,0)
    return Fraction(wgt,den),low,high


def lottery_price(hists):
    # A shared seed chooses an unconstrained encoder and decoder together.
    def collective(x):
        faces=[face(h,x) for h in hists]
        y=max(v[0] for v in faces)
        return y,min(lo for a,lo,hi in faces if a==y),max(hi for a,lo,hi in faces if a==y)
    left=Fraction(0)
    y,lo,hi=collective(left)
    if hi>=0:
        return y,left
    left_y,left_s=y,hi
    right=Fraction(1)
    while True:
        y,lo,hi=collective(right)
        if lo<=0<=hi:
            return y,right
        if lo>0:
            right_y,right_s=y,lo
            break
        left,left_y,left_s=right,y,hi
        right*=2
    while True:
        # Intersect the two active affine supports, then query the full envelope.
        x=(left_y-left*left_s-right_y+right*right_s)/(right_s-left_s)
        assert left<x<right
        y,lo,hi=collective(x)
        if lo<=0<=hi:
            return y,x
        if hi<0:
            left,left_y,left_s=x,y,hi
        else:
            right,right_y,right_s=x,y,lo


def pair_partitions():
    for i,j in combinations(range(16),2):
        yield (i,j),[(i,j)]+[(h,) for h in range(16) if h not in (i,j)]


def eraser_only_coin(cells, den):
    flat = [(int(w),int(s)) for w,s in cells.reshape(-1,2)]
    mask = fractional_mask(flat)
    boundary, = [i for i,p in mask.items() if 0 < p < 1]
    split_h, split_k = divmod(boundary,512)
    coin = mask[boundary]
    mass, surplus = 0,0
    # An extra erasure symbol records the coin, before the emitter knows k.
    for h in range(16):
        symbols = ((h,1-coin),(16,coin)) if h == split_h else ((h,1),)
        for symbol, chance in symbols:
            received_h = split_h if symbol == 16 else symbol
            for k in range(512):
                i = 512*received_h+k
                go = (symbol == 16) if i == boundary else mask.get(i,0) == 1
                if go:
                    mass += chance * flat[512*h+k][0]
                    surplus += chance * flat[512*h+k][1]
    assert surplus == 0 and mass == whole_and_mixed(types(cells))[1]
    assert mass.denominator != 1
    print("  eraser-only coin, 17 symbols",split_h,split_k,coin,"mass",mass,"rate",mass/den)


def all_pairs(cells,den):
    base = types(cells)
    full = whole_and_mixed(base)
    slope = full_multiplier(base)
    bound = scalar(base,slope)
    assert full[1] == bound
    hs = {}
    exacts = {}
    supports = {}
    for pair,grouping in pair_partitions():
        hist = types(merged(cells,grouping))
        hs[pair] = hist
        exacts[pair] = whole_and_mixed(hist)
        supports[pair] = scalar(hist,slope)
    highest = [max(q[i] for q in exacts.values()) for i in (0,1)]
    best_pairs = [[p for p,val in exacts.items() if val[i]==highest[i]] for i in (0,1)]
    print("  full",*(x/den for x in full),"lambda for integer surplus",slope)
    print("  highest fixed proper encoding",*(x/den for x in highest),"attainers",best_pairs)
    print("  full-rate preserving pairs",[[p for p,q in exacts.items() if q[i]==full[i]] for i in (0,1)])
    print("  highest common multiplier bound for even a shared lottery over proper maps",
          max(supports.values())/den,"lossless pairs",[p for p,s in supports.items() if s==bound])
    joint,multiplier=lottery_price(hs.values())
    assert highest[1]<=joint<=max(supports.values())
    print("  sharp shared lottery over all proper codes",joint/den,"at",multiplier)
    return full,slope,hs,exacts,supports


def main():
    for law in ("nae","parity"):
        for c in (0,1):
            cells,den = records(law,c)
            print(law,"orientation",c)
            if not cells[:,:,1].max() >= 0 or not any(w and s>=0 for (w,s) in types(cells)):
                assert whole_and_mixed(types(cells))==(0,0)
                print("  full upper bound zero; a one-symbol always-decline code attains it")
                continue
            all_pairs(cells,den)
            eraser_only_coin(cells,den)


if __name__ == "__main__":
    main()
