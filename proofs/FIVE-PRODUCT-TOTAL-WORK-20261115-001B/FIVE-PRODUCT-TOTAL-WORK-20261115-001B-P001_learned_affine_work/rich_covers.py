"""Single-error plain rows removed by one rich local affine check, codimensions one and two."""
from itertools import product
from functools import cache
import json


def selected(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def packed(x, errors=0):
    raw = x
    for i in range(3):
        raw |= ((((x >> (2*i)) & (x >> (2*i+1)) & 1) ^ (errors >> i & 1)) << (6+i))
    return raw


def par(x):
    return x.bit_count() % 2


def main():
    rich = tuple(packed(x) for x in range(64))
    single = tuple(packed(x,1<<i) for i in range(3) for x in range(64))
    lr = (1<<len(rich))-1
    sr = (1<<len(single))-1
    r_masks = [sum(par(q & x)<<i for i,x in enumerate(rich)) for q in range(512)]
    s_masks = [sum(par(q & x)<<i for i,x in enumerate(single)) for q in range(512)]
    rich_row_single = {v:1<<i for i,v in enumerate(single)}

    @cache
    def span_single(subs):
        if not subs:
            return 0
        inp = [rich[t] for t in selected(subs)]
        x = inp[0]
        basis = [0]*9
        for a in inp[1:]:
            d = a ^ x
            while d:
                k=d.bit_length()-1
                if not basis[k]:
                    basis[k]=d
                    break
                d ^= basis[k]
        points = [x]
        for b in basis:
            if b: points.extend([p^b for p in points])
        return sum(rich_row_single.get(pt,0) for pt in points)

    maxn=0
    maxsets=set()
    high_by_size={}
    examined=0
    def observe(r,s):
        nonlocal maxn,maxsets,examined
        examined += 1
        if s.bit_count() < 48:
            return
        removed=s&~span_single(r)
        n=removed.bit_count()
        if n < 48:
            return
        high_by_size[n]=high_by_size.get(n,0)+1
        if n>maxn:
            maxn,maxsets=n,set()
        if n==maxn:maxsets.add(removed)

    for a in range(1,512):
        cr,cs = r_masks[a],s_masks[a]
        observe(cr,cs);observe(lr^cr,sr^cs)
        for b in range(a+1,512):
            if a^b<=b:continue
            dr,ds=r_masks[b],s_masks[b]
            observe(cr&dr,cs&ds);observe(cr&~dr,cs&~ds)
            observe(dr&~cr,ds&~cs);observe(lr&~(cr|dr),sr&~(cs|ds))
    shapes = sorted({tuple((m >> (64*i) & lr).bit_count() for i in range(3)) for m in maxsets})
    assert examined == 174762 and maxn == 48 and len(maxsets)==372
    assert set(shapes) == {(0,0,48),(0,24,24),(0,48,0),(24,0,24),(24,24,0),(48,0,0)}
    block_totals = {tuple(map(sum,zip(*four))) for four in product(shapes,repeat=4)}
    assert (64,64,64) not in block_totals and (96,48,48) in block_totals
    # A singleton-error block gives a concrete sharp cut: t0=1 on the rich
    # side forces both inputs to its first product to be one.
    one = r_masks[64]; wrong = s_masks[64] & ~span_single(one)
    assert wrong.bit_count()==48 and (wrong & lr)==wrong
    # At total cost 17 the other two checks would cover the very same input
    # values at each error position. Test every disjoint triple of maximizers.
    maximum_sets = sorted(maxsets)
    disjoint_triples = same_residual = 0
    for i, a in enumerate(maximum_sets):
        for j, b in enumerate(maximum_sets[i+1:], i+1):
            if a & b:
                continue
            union = a | b
            for c in maximum_sets[j+1:]:
                if union & c:
                    continue
                disjoint_triples += 1
                residual = sr ^ (union | c)
                columns = tuple((residual >> (64*k)) & lr for k in range(3))
                same_residual += len(set(columns)) == 1
    assert disjoint_triples == 2944 and same_residual == 0
    # Check the quadratic densities used for source projections of codimension-three guards.
    tot = sum(par((x & (x >> 1)) & 21) << x for x in range(64))
    affine = r_masks[:64] + [lr ^ row for row in r_masks[:64]]
    slices = {4:set(),5:set(),6:{lr}}
    for a,first in enumerate(r_masks[1:64],1):
        slices[5].update((first,lr^first))
        for b in range(a+1,64):
            if a^b<=b: continue
            second=r_masks[b]
            slices[4].update((first&second,first&~second,second&~first,lr&~(first|second)))
    maxima = {dim:max(((tot^linear)&dom).bit_count() for linear in affine for dom in domains)
              for dim,domains in slices.items()}
    assert maxima == {4:12,5:20,6:36}
    # k=4: each four-row fibre has only three positions with exactly one error.
    # k=5,6: the maximum fibre has two or one points, respectively.
    codim_three = max(32,3*maxima[4],2*maxima[5],maxima[6])
    assert codim_three==40
    print(json.dumps({'examined_affine_guards':examined,'max':maxn,'number_of_max_sets':len(maxsets),
                      'max_group_shapes':shapes, 'four_can_cover_three_64_blocks':(64,64,64) in block_totals,
                      'codimension_three_maximum_upper_bound':codim_three,
                      'density_maxima':maxima,'counts_at_least48':sorted(high_by_size.items()),
                      'disjoint_maximizer_triples':disjoint_triples,
                      'triples_leaving_identical_input_residues':same_residual},sort_keys=True))
if __name__=='__main__':
    main()
