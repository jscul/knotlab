"""Construct and replay a closed four-place parity example with disjoint readings."""

import argparse
import itertools as it
import json

from arity_parity import agrees, determined, image, knot_image, restrict_to


LOWER = [(0,1,2), (0,3,4), (1,5,6), (2,7,8)]
UPPER = [(3,5), (4,7), (6,8)]


def find(declared_sets):
    directions = [sum(1<<j for j, law in enumerate(LOWER) if i in law)
                  for i in range(9)]
    counts = {'label_sets':0,'completed_regular_assignments':0}
    # Translation lets the first label be zero. A distinction crossing the two
    # label classes for a bit occurs in that bit's sum of source parity laws.
    holder_count = 10
    for later in it.islice(it.combinations(range(1,16),holder_count-1), declared_sets):
        labels = (0,)+later
        counts['label_sets'] += 1
        options=[]
        for d in directions:
            meetings = [(a,b) for a,b in it.combinations(range(holder_count),2)
                        if labels[a]^labels[b]==d]
            options.append(list(it.combinations(meetings,2)))
        order = sorted(range(9),key=lambda k:len(options[k]))
        if not options[order[0]]:
            continue
        degree = [0]*holder_count
        selected = [None]*9
        def place(pos):
            if pos==len(order):
                if min(degree)<3: return
                counts['completed_regular_assignments'] += 1
                yield [link for two in selected for link in two]
                return
            var=order[pos]
            for pair in options[var]:
                ends = pair[0]+pair[1]
                if any(degree[i]==4 for i in ends): continue
                for i in ends: degree[i]+=1
                selected[var]=pair
                yield from place(pos+1)
                for i in ends: degree[i]-=1
        for pairs in place(0):
            cuts = [sum(1<<i for i,ends in enumerate(pairs) if v in ends) for v in range(holder_count)]
            if not adequate(cuts):
                continue
            return labels,pairs,counts
    return None,None,counts


def span(generators):
    values={0}
    for gen in generators:
        values |= {v^gen for v in values}
    return values


def adequate(cuts):
    d = span(cuts)
    if len(d)!=2**(len(cuts)-1): return False
    pair_masks = [3<<(2*i) for i in range(9)]
    if sum(v in d for v in span(pair_masks)) != 16: return False
    for c in cuts:
        positions = [1<<i for i in range(18) if c>>i&1]
        locally_available={x^y for x in d for y in span(positions)}
        if any(p in locally_available for p in pair_masks): return False
    return True


def replay(pairs, prefix):
    rows=[[i for i,p in enumerate(pairs) if v in p] for v in range(1+max(max(p) for p in pairs))]
    masks=[sum(1<<i for i in r) for r in rows]
    carriers=[(2*i,2*i+1) for i in range(9)]
    total=2**len(pairs)
    source=[s for s in range(min(prefix,total)) if all((m&s).bit_count()%2==0 for m in masks)]
    words={sum(agrees(s,c)<<i for i,c in enumerate(carriers)) for s in source}
    laws=[sum(1<<i for i in r) for r in LOWER]
    allowed=set()
    deletions=[set() for _ in LOWER]
    for w in range(512):
        bad=[i for i,m in enumerate(laws) if (m&w).bit_count()%2!=1]
        if not bad: allowed.add(w)
        elif len(bad)==1: deletions[bad[0]].add(w)
    if prefix < total:
        return {'assignments_checked':prefix,'allowed_source':len(source),'lower_words_seen':len(words)}
    assert words==allowed and len(words)==32
    assert all(len(r) in (3,4) for r in rows)
    assert all(not determined(source,c,row) for row in rows for c in carriers)
    # On the source, each member individually can affect the pair function
    # when the other is held fixed; parity need not allow a one-bit move.
    assert all(len({restrict_to(s,c) for s in source})==4 for c in carriers)
    lower_images=[image_on_indices(words,r) for r in LOWER]
    assert all(knot_image(ws,3) and len(ws)==4 for ws in lower_images)
    upper=image(words,UPPER)
    assert knot_image(upper,3)
    assert all(not determined(words,c,row) for row in LOWER for c in UPPER)
    assert all(image(extra,UPPER)-upper for extra in deletions)
    nae_words=set()
    for state in range(total):
        if all(0<(state&m)<m for m in masks):
            reduced=sum(agrees(state,c)<<i for i,c in enumerate(carriers))
            nae_words.add(reduced)
    return {
        'source_places':rows,'raw_distinctions':len(pairs),'allowed_source_states':len(source),
        'raw_pair_carriers':carriers,'lower_word_count':len(words),
        'exact_lower_presentation':[list(r) for r in LOWER],
        'lower_images':[sorted(ws) for ws in lower_images],
        'source_knot_readable_carriers':0,'raw_pairs_with_all_four_words':len(carriers),
        'upper_carriers':UPPER,'upper_words':sorted(upper),
        'single_lower_bond_readable_upper_carriers':0,
        'upper_words_restored_by_lower_bond_deletion':[sorted(image(x,UPPER)-upper) for x in deletions],
        'source_law_deletions_changing_the_relation':sum(
            any(all((m&s).bit_count()%2==0 for j,m in enumerate(masks) if j!=i)
                and (s&masks[i]).bit_count()%2 for s in range(total)) for i in range(len(masks))
        ),
        'same_supports_and_carriers_under_plain_not_all_equal':{
            'lower_word_count':len(nae_words),'lower_images':[sorted(image_on_indices(nae_words,r)) for r in LOWER],
            'upper_image':sorted(image(nae_words,UPPER))},
    }


def image_on_indices(states, row):
    return {tuple(s>>i&1 for i in row) for s in states}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--sets',type=int,default=None)
    p.add_argument('--prefix',type=int,default=2**18)
    args=p.parse_args()
    labels,pairs,counts=find(args.sets)
    result={'counts':counts,'labels':labels,'meetings':pairs}
    if pairs: result['replay']=replay(pairs,args.prefix)
    print(json.dumps(result,indent=2))
