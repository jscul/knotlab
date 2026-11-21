"""Exact marked-pair counts and an independent inversion of the 29-name reached observation."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path

ORIGINAL = ((0,6,7), (1,2,3,4,5,8), (6,7,8))
NEW = (((0,1), (9,10,11,12)), ((2,), (13,14,15,16)), ((3,), (17,18,19,20)),
       ((4,), (21,22,23,24)), ((5,), (25,26,27,28)))
N = 29
PAIR = tuple(combinations(range(N),2))


def observed():
    """Sum current uniform words and equal divisions over literal original words."""
    laws = ('uniform','inherited')
    totals = dict.fromkeys(laws,0)
    signs = {law:Counter() for law in laws}
    # Every private mark has conditional denominator either 1 or 15.
    scale = 15*15
    extent = Counter()
    for word in product((1,-1), repeat=9):
        if any(len({word[x] for x in row}) == 1 for row in ORIGINAL):
            continue
        single = [15*w for w in word]+[0]*20
        together = {}
        extension_count = 1
        for inputs, fresh in NEW:
            held = {word[x] for x in inputs}
            mixed = len(held)>1
            extension_count *= 16 if mixed else 15
            for f in fresh:
                single[f] = 0 if mixed else -word[inputs[0]]
            for ij in combinations(fresh,2):
                together[ij] = 0 if mixed else -15
        extent[extension_count]+=1
        for ij in PAIR:
            i,j = ij
            value = together.get(ij, single[i]*single[j])
            signs['uniform'][ij]+=value*extension_count
            signs['inherited'][ij]+=value
        totals['uniform']+=extension_count
        totals['inherited']+=1
    matrices={}
    for law in laws:
        matrices[law]=[[Fraction(signs[law][tuple(sorted((i,j)))],scale*totals[law])
                        if i!=j else Fraction(1) for j in range(N)] for i in range(N)]
    return matrices,totals,dict(extent)


def min_support(c,u):
    row = {v: c[u][v] for v in range(N) if v!=u}
    low=min(row.values())
    return frozenset(v for v,z in row.items() if z==low),low


def triple_probability(c,marks):
    if len(marks)==2:
        i,j=marks
        return (1+c[i][j])/2
    i,j,k=marks
    return (1+c[i][j]+c[i][k]+c[j][k])/4


def candidates(c):
    result=set()
    for u in range(N):
        other,m = min_support(c,u)
        if m>=0 or len(other)<2:
            continue
        if len(other)<=3:
            if triple_probability(c,tuple(other))!=-m:
                continue
        elif any(triple_probability(c,t)<=-m for t in combinations(other,3)):
            continue
        H=other|{u}
        F={v for v in H if all(c[u][z]==c[v][z] for z in range(N) if z not in (u,v))}
        I=H-F
        if not I or len(F)<max(1,3-len(I)):
            continue
        result.add((tuple(sorted(I)),tuple(sorted(F))))
    return tuple(sorted(result))


def antichain_limit(count):
    """Directly verify the four small bounds used in the price argument."""
    points = range(count)
    subsets = [frozenset(v) for size in range(1,count+1) for v in combinations(points,size)]
    largest = 0
    for mask in range(1 << len(subsets)):
        family = [v for i,v in enumerate(subsets) if mask & (1 << i)]
        if all(not (a <= b or b <= a) for a,b in combinations(family,2)):
            largest = max(largest,len(family))
    return largest


def filter_options(c, law):
    initial = candidates(c)
    options = []
    excluded = []
    for inputs, fresh in initial:
        f = fresh[0]
        p = len(inputs)
        # With at most two inputs the unanimous sign, zero on a mixed pair,
        # equals their mean. This determines the complete conditional row.
        mismatch = next((z for z in range(N) if z not in fresh and
                         p * (2**len(fresh)-1) * c[f][z] != -sum(c[x][z] for x in inputs)), None)
        if p <= 2 and mismatch is not None:
            excluded.append(dict(candidate_fresh=fresh,reason="unary/binary conditional sign",witness=mismatch))
        else:
            options.append((inputs,fresh))
    guaranteed_old = set(range(N)).difference(v for _,fs in options for v in fs)
    survivors = []
    for inputs, fresh in options:
        possible_companions = {}
        holding = set(inputs) | set(fresh)
        f = fresh[0]
        for x in inputs:
            if law=='uniform':
                delta = {z:c[x][z]-c[f][z] for z in range(N) if z not in (x,f)}
                bound = min(delta.values())
                witnesses = {z for z,v in delta.items() if z not in holding and v==bound}
            else:
                # The true earlier row contains all these indices. Its minimum
                # can only be lower if other, unmarked, old indices also remain.
                certain = (guaranteed_old | set(inputs)) - {x}
                bound = min(c[x][z] for z in certain)
                witnesses = {z for z in range(N) if z not in holding and c[x][z]<=bound}
            possible_companions[x] = witnesses
        short = min(len(v) for v in possible_companions.values()) < 2
        # Each of the distinct older parents needs at least two places beyond its
        # input. Each possible companion can occupy at most two holders globally.
        cap = 2 * len(set.union(*possible_companions.values()))
        if short or cap < 2*len(inputs):
            excluded.append(dict(candidate_fresh=fresh,reason="insufficient exterior places for distinct preceding holders",
                                 possible_exterior={x:sorted(v) for x,v in possible_companions.items()},
                                 required_occurrences=2*len(inputs),maximum_occurrences=cap))
        else:
            survivors.append((inputs,fresh))
    return survivors,excluded


def decode(c,law):
    survivors,excluded = filter_options(c,law)
    # Every remaining candidate actually included would have price four,
    # strictly exceeding its ordinary lower floor, so its demand is four.
    assert len(survivors)==5
    assert all(len(fs)==4 and len(fs)>max(1,3-len(xs)) for xs,fs in survivors)
    supports = sorted(tuple(sorted((*xs,*fs))) for xs,fs in survivors)
    assert sum(len(s) for s in supports)==len(set().union(*supports))
    assert [antichain_limit(i) for i in range(4)]==[0,1,2,3]
    # Degree at most three is impossible. A nonempty five-holder observation
    # must therefore contain every candidate with all five mutually witnessed.
    # A jointly unheld group of all five would cost only one per holder, so
    # a common witness is necessary and all ten unordered pairs must be born.
    roster=[(x,y,len(supports)-2) for x,y in combinations(supports,2)]
    all_loose=sorted(v for _,fs in survivors for v in fs)
    old=set(range(N))-set(all_loose)
    bounds={}
    for xs,fs in survivors:
        for x in xs:
            if law=='uniform':
                row={z:c[x][z]-c[fs[0]][z] for z in range(N) if z not in (x,fs[0])}
            else:
                row={z:c[x][z] for z in old-{x}}
            low=min(row.values())
            bounds[x]=sorted(z for z,v in row.items() if v==low and z in old and z not in xs)
    return dict(initial_options=len(candidates(c)),excluded=excluded,loose=all_loose,
                current_parent_supports=supports,next_birth_roster=roster,
                previous_holder_other_places=bounds)


def run():
    matrices,totals,ext=observed()
    base=Path(__file__).resolve().parent
    ticket=base.name+'A'
    source=base.parents[1]/'artifacts'/ticket/(ticket+'-E001_loose_roles')
    outputs={}
    for weight,c in matrices.items():
        archived=json.loads((source/(weight+'_rates.json')).read_bytes())
        rates=[(1-c[i][j])/2 for i,j in PAIR]
        assert rates==list(map(Fraction,archived))
        outputs[weight]=decode(c,weight)
    assert outputs['uniform']['next_birth_roster']==outputs['inherited']['next_birth_roster']
    reference=json.loads((source/'selection.json').read_bytes())
    assert reference['uniform_word_count']==totals['uniform']
    actual=[(tuple(parents[0]),tuple(parents[1]),q) for parents,q in reference['reference_named_roster']]
    assert outputs['uniform']['next_birth_roster']==actual
    return dict(original_words=totals['inherited'],uniform_current_words=totals['uniform'],extensions=ext,
                pairs_per_weight=len(PAIR),changed_pairs=sum(matrices['uniform'][i][j]!=matrices['inherited'][i][j]
                    for i,j in PAIR),antichain_maximum_at_zero_through_three_neighbors=[antichain_limit(i) for i in range(4)],
                by_weight=outputs)


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
