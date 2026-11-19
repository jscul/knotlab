"""Exact asymmetric multi-shield search at exterior costs two and three."""

import argparse
from collections import Counter
from itertools import combinations, product
import json

import numpy as np

from weighted_core import INF
from weighted_shield import Deck, cut_names


def layout(counts, has_d, relay):
    tests = 'abcd' if has_d else 'abc'
    shields = [(color, f'{color}{i}') for color, size in zip('uw', counts) for i in range(size)]
    middles = [*tests, *(name for _, name in shields)]
    sites = ['h0','h1','v', *middles] + (['r'] if relay else []) + ['o']
    edges = [(prefix+arm, origin, arm) for arm in tests
             for prefix, origin in [('h', 'h0' if arm in 'ab' else 'h1'), ('v','v')]]
    for color, arm in shields:
        edges.extend([('h'+arm, 'h0' if color == 'u' else 'h1', arm), ('v'+arm, 'v',arm), ('o'+arm,'o',arm)])
    if relay:
        edges.extend(('r'+arm,'r',arm) for arm in middles)
    supports = cut_names(sites, edges)
    return None if supports is None else Deck(sites, edges, supports)


def coefficient_deck(deck):
    # All shields of one color have the same weighted incidence. Repeated
    # groups of distinctions remain separate marks in the query support.
    names = [name[0] + 'a' if name.endswith('c') else name for name in deck.names]
    names = [name[:-1] if name[-1].isdecimal() else name for name in names]
    order = tuple(dict.fromkeys(names))
    positions = [order.index(name) for name in names]
    weights = np.zeros((len(deck.supports),len(order)), dtype=np.int16)
    for i, pos in enumerate(positions):
        weights[:, pos] += deck.cut_matrix[:, i]
    return order,weights


def comparisons(deck, arity):
    # Any changed query names a moved test distinction. Thus it names at
    # most arity-1 distinct shields. Each pair or triple of actual names
    # reduces to up to three parallel classes and one orbit of shield labels.
    seen = set()
    for query in combinations(deck.names, arity):
        moved = tuple(deck.swapped.get(x,x) for x in query)
        if query == moved or set(query) == set(moved):
            continue
        marks = tuple(x for x in query if not x[-1].isdecimal())
        slots = sorted({x[1:] for x in query if x[-1].isdecimal()})
        allowed = set()
        for c in 'uw':
            ns = [x for x in slots if x[0] == c]
            allowed.update(f'{c}{i}' for i in range(len(ns)))
        if allowed != set(slots):
            continue
        canonical = tuple(sorted(query))
        other = tuple(sorted(moved))
        key = min(canonical,other), max(canonical,other)
        if key in seen:
            continue
        seen.add(key)
        assert marks
        yield key


def rows_for_weights(names, has_d, relay, maximum_hub, maximum_test):
    tested = 'abd' if has_d else 'ab'
    arms = [p for p in product(range(1, maximum_test+1), repeat=2) if sum(p) + relay >= 3]
    values = []
    for test_weights in product(arms, repeat=len(tested)):
        initial = {prefix+arm: value for arm,pair in zip(tested,test_weights) for prefix,value in zip('hv',pair)}
        for hu,hw,ou,ow in product(range(1, maximum_hub+1), range(1, maximum_hub+1), (2,3), (2,3)):
            trial = {**initial, 'hu':hu,'hw':hw,'ou':ou,'ow':ow}
            values.append([trial.get(x,1) for x in names])
    return np.asarray(values, dtype=np.int16)


def search(maximum_count, maximum_hub, maximum_test):
    result, hits = Counter(), []
    for sizes in product(range(1, maximum_count+1), repeat=2):
        if sizes == (1,1):
            continue
        for has_d, relay in product((False,True), repeat=2):
            result['layouts'] += 1
            deck = layout(sizes, has_d, relay)
            if deck is None:
                result['unrooted_layouts'] += 1
                continue
            names, coeff = coefficient_deck(deck)
            # Retain only distinct linear costs for a query. Equal costs
            # arise from exchanging unmarked shields or same-side holders.
            memo = {}

            def terms(mark):
                mark = tuple(sorted(mark))
                if mark not in memo:
                    memo[mark] = np.unique(coeff[deck.marks(mark)],axis=0)
                return memo[mark]

            comparisons_by_order = {order: list(comparisons(deck,order)) for order in (1,2,3)}
            if any(bool(len(deck.marks(x))) != bool(len(deck.marks(y)))
                   for pairs in comparisons_by_order.values() for x,y in pairs):
                result['existence_rejections'] += 1
                continue
            weights = rows_for_weights(names,has_d,relay,maximum_hub,maximum_test)
            if has_d and sizes[0] == sizes[1]:
                # The peer's uniform cells have all equal test pairs and both
                # shield classes proportional to the same exterior cost.
                indices = [names.index(k) for k in ('ha','va','hb','vb','hd','vd','hu','hw','ou','ow')]
                ha,va,hb,vb,hd,vd,hu,hw,ou,ow = weights[:,indices].T
                weights = weights[~((ha==hb)&(ha==hd)&(va==vb)&(va==vd)&(hu==hw)&(hu==ou)&(ou==ow))]
            result['weighted_decks'] += len(weights)

            def value(indices, query, array=weights):
                return (array[indices] @ terms(query).T).min(axis=1,initial=INF)

            viable = np.arange(len(weights))
            for order in (1,2):
                items = sorted(comparisons_by_order[order], key=lambda pair: sum(len(deck.marks(q)) for q in pair))
                for x,y in items:
                    viable = viable[value(viable,x) == value(viable,y)]
                    if not len(viable):
                        break
                if not len(viable):
                    break
            result['pair_and_lower_survivors'] += len(viable)
            if not len(viable):
                continue
            triple_candidates = viable
            for x,y in comparisons_by_order[3]:
                triple_candidates = triple_candidates[value(triple_candidates,x) == value(triple_candidates,y)]
                if not len(triple_candidates):
                    break
            result['full_current_survivors'] += len(triple_candidates)
            if not len(triple_candidates):
                continue
            for shrink in (('ou',),('ow',),('ou','ow')):
                future = weights[triple_candidates].copy()
                for name in shrink:
                    future[:,names.index(name)] = 1
                indices = np.arange(len(future))
                for left,right in deck.targets():
                    first,second = value(indices,left,future),value(indices,right,future)
                    for index in np.flatnonzero(first < second):
                        result['breaking_cases'] += 1
                        if len(hits) < 20:
                            old = weights[triple_candidates[index]]
                            hits.append({'shield_counts':sizes,'has_d':has_d,'relay':relay,
                                         'order':names,'weights':old.tolist(),
                                         'costs_leveled':shrink,'target':[left,right],
                                         'successor_K':[int(first[index]),int(second[index])]})
    return {'parameters': {'maximum_count':maximum_count,'maximum_hub':maximum_hub,'maximum_test':maximum_test},
            'counts':dict(result),'first_twenty_breaking_examples':hits}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--count',type=int,default=3)
    p.add_argument('--hub',type=int,default=6)
    p.add_argument('--test',type=int,default=2)
    args = p.parse_args()
    print(json.dumps(search(args.count,args.hub,args.test),indent=2))


if __name__ == '__main__':
    main()
