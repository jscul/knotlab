"""Compare unequal hub costs, shield counts, and one-sided contraction exactly."""

import argparse
from collections import Counter
from itertools import product
import json

import numpy as np

from weighted_core import INF
from weighted_shield_grouped import coefficient_deck, comparisons, layout


def model(counts, explicit):
    reduced = tuple(min(n, explicit+2) for n in counts)
    deck = layout(reduced, True, True)
    assert deck is not None
    scales = {f'{color}{count-1}': max(1, total-count+1)
              for color,total,count in zip('uw',counts,reduced,strict=True)}
    for i, (_, u, v) in enumerate(deck.edges):
        deck.cut_matrix[:,i] *= scales.get(u, scales.get(v, 1))
    names, coefficients = coefficient_deck(deck)
    return deck, names, coefficients


def capture(deck, names, coefficients):
    cached = {}
    source = {'ha':0,'hb':0,'hd':0,'va':1,'vb':1,'vd':1,'hu':2,'hw':3,'ou':4,'ow':5}
    coalesced = np.zeros((len(coefficients),7),dtype=np.int16)
    for index,name in enumerate(names):
        coalesced[:,source.get(name,6)] += coefficients[:,index]

    def terms(query):
        q = tuple(sorted(query))
        if q not in cached:
            choices = np.unique(coalesced[deck.marks(q)],axis=0)
            # Every coefficient is multiplied by a positive width, so a
            # componentwise dominated cut can never improve the minimum.
            keep = []
            for row in choices[np.argsort(choices.sum(axis=1),kind='stable')]:
                if not keep or not np.any(np.all(np.array(keep) <= row,axis=1)):
                    keep.append(row)
            cached[q] = np.array(keep,dtype=np.int16).reshape((-1,7))
        return cached[q]

    def value(rows, query):
        return (rows @ terms(query).T).min(axis=1,initial=INF)

    def as_arrays(matrix):
        return np.column_stack((matrix,np.ones(len(matrix),dtype=np.int16)))

    return value,as_arrays,terms


def current_sites(counts, costs):
    def shrinking(price):
        return {2:5,3:6}.get(price, 2 * price + 1)

    a,b = costs
    x,y = counts
    return 8+x+y+x*shrinking(a)+y*(b+1)


def four(counts, parameters):
    deck,names,coefficients = model(counts,3)
    value,as_arrays,_ = capture(deck,names,coefficients)
    rows = as_arrays(np.array([parameters]))
    for q,r in comparisons(deck,4):
        a,b = int(value(rows,q)[0]),int(value(rows,r)[0])
        if a != b:
            return {'query': q, 'image': r, 'K': [None if x == INF else x for x in (a,b)]}
    return None


def search(counts, test_max, fixed_max, price_max, cap):
    deck,names,coefficients = model(counts,2)
    value,as_arrays,terms = capture(deck,names,coefficients)
    current = np.array([
        (s,i,h,g,u,w) for (s,i,h,g,u,w) in product(range(1,test_max+1), range(1,test_max+1),
                                                   range(1,fixed_max+1), range(1,fixed_max+1),
                                                   range(2,price_max+1), range(2,price_max+1))
        if current_sites(counts,(u,w)) <= cap
    ], dtype=np.int16).reshape((-1,6))
    summary = Counter({'assigned_parameters':len(current)})
    ordered = [(('ha','hb'), ('hc','hb')), (('va','vb'),('vc','vb'))]
    future = current.copy()
    future[:,4] = 1
    forward = as_arrays(future)
    target_hit = np.zeros(len(current),dtype=bool)
    for q,r in ordered:
        target_hit |= value(forward,q) < value(forward,r)
    current = current[target_hit]
    summary['successor_pair_breaks'] = len(current)
    typed = as_arrays(current)

    def filter_query(q,r):
        nonlocal current,typed
        if np.array_equal(terms(q),terms(r)):
            return
        keep = value(typed,q) == value(typed,r)
        current = current[keep]
        typed = typed[keep]

    preferred = [('ha','hb'),('ha','hu0'),('ha','hb','hu0'),('ha','hu0','hu1')]
    for q in preferred:
        moved = tuple(deck.swapped.get(x,x) for x in q)
        filter_query(q,moved)
    summary['after_four_necessary_comparisons'] = len(current)
    for order in (1,2,3):
        for q,r in comparisons(deck,order):
            if not len(current):
                break
            filter_query(q,r)
        summary[f'after_order_{order}'] = len(current)
    if not len(current):
        return {'shields': counts, 'counts':dict(summary), 'best':None}

    best = min(current.tolist(), key=lambda x: (current_sites(counts,x[4:]),sum(x),x))
    price = best[:4] + [1,best[-1]]
    old, future = as_arrays(np.array([best,price]))
    for q,r in ordered:
        before, after = value(future[None,:],q)[0],value(future[None,:],r)[0]
        if before < after:
            hit = {'shields':counts,'test_to_hub_and_v':best[:2],'permanent_shield_to_hub':best[2:4],
                   'current_exterior_costs':best[4:],'later_exterior_costs':price[4:],
                   'current_junctions_for_small_graft':current_sites(counts,best[4:]),
                   'old_K':int(value(old[None,:],q)[0]),'successor_K':[int(before),int(after)],
                   'mark':q,'image':r,'first_four_difference':four(counts,best)}
            return {'shields':counts,'counts':dict(summary),'best':hit}
    raise AssertionError('the saved candidate did not split')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shields', nargs=2, type=int, required=True)
    p.add_argument('--test',type=int,default=4)
    p.add_argument('--fixed',type=int,default=16)
    p.add_argument('--prices',type=int,default=14)
    p.add_argument('--cap',type=int,default=240)
    a = p.parse_args()
    if not all(2 <= n <= 6 for n in a.shields):
        p.error('use two through six shields of each color')
    print(json.dumps(search(a.shields,a.test,a.fixed,a.prices,a.cap),indent=2))


if __name__ == '__main__':
    main()
