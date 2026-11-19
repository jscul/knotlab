"""Test how much contraction is needed and whether blue branches can share a pole."""

import json

import numpy as np

from weighted_core import INF
from weighted_shield import Deck, cut_names
from weighted_shield_grouped import coefficient_deck, comparisons, layout
from weighted_shield_literal import named_graft


def partial_red(counts,tests,hubs,costs):
    _, _, _, _, _, deck, _, before = named_graft(counts,tests,hubs,costs)
    indices = [deck.index[f'ou{i}'] for i in range(counts[0])]
    out = []
    for shrink in range(counts[0]+1):
        after = before.copy()
        after[indices[:shrink]] = 1
        cuts = after[None,:] @ deck.cut_matrix.T
        results = []
        for q,r in deck.targets():
            results.append({'marks':q,'image':r,'K':[int(deck.minimum(cuts,z)[0]) for z in (q,r)]})
        out.append({'red_shields_lowered':shrink,'readings':results})
    return out


def shared_layout(anchor):
    # Two named shields in each color suffice for a changed triple. Treat
    # the remaining four shields as two identical-neighbor representatives
    # of multiplicities one and three.
    base = layout((4,4), True, True)
    sites = base.sites[:-1] + (['blue'] if anchor == 'blue' else []) + ['o']
    edges = [(label, anchor if label.startswith('ow') else a, b) for label,a,b in base.edges]
    edges.append(('stem',anchor,'o'))
    support = cut_names(sites,edges)
    if support is None:
        return None
    deck = Deck(sites,edges,support)
    for i, (_,a,b) in enumerate(edges):
        if {a,b}.intersection({'u3','w3'}):
            deck.cut_matrix[:,i] *= 3
    return deck


def shared_blue(anchor, cap=48):
    deck = shared_layout(anchor)
    if deck is None:
        return {'anchor':anchor,'layout_passes_ordinary_gate':False}
    names, coefs = coefficient_deck(deck)
    stem = names.index('stem')
    initial = np.array([8 if name in ('hu','hw','ou','ow')
                        else 3 if name in ('ha','hb','hd','va','vb','vd') else 1
                        for name in names],dtype=np.int16)
    widths = np.repeat(initial[None,:],cap-1,axis=0)
    widths[:,stem] = list(range(2,cap+1))
    costs = widths @ coefs.T

    survivors = np.arange(len(widths))
    first_failures = []
    for order in (1,2,3):
        for q,r in comparisons(deck,order):
            if not len(survivors):
                break
            active = costs[survivors]
            first,second = deck.minimum(active,q),deck.minimum(active,r)
            for j in np.flatnonzero(first != second):
                first_failures.append({'stem':int(widths[survivors[j],stem]),'marks':q,'image':r,
                                       'K':[None if k == INF else int(k) for k in (first[j],second[j])]})
            survivors = survivors[first == second]
    breaks = []
    for index in survivors:
        after = widths[index].copy()
        after[names.index('ou')] = 1
        cuts = after[None,:] @ coefs.T
        for q,r in deck.targets():
            a,b = int(deck.minimum(cuts,q)[0]), int(deck.minimum(cuts,r)[0])
            if a < b:
                breaks.append({'stem':int(after[stem]),'marks':q,'image':r,'later_K':[a,b],
                               'current_junctions':123 + (anchor == 'blue') + int(after[stem])})
    return {'anchor':anchor, 'layout_passes_ordinary_gate': True, 'stem_range':[2,cap],
            'first_rejections': sorted(first_failures,key=lambda item:item['stem']),
            'old_reading_survivors':[int(widths[i,stem]) for i in survivors], 'pair_breaks':breaks}


def main():
    print(json.dumps({'partial_red':partial_red((6,6),(3,3),(8,8),(8,8)),
                      'partial_red_118_host':partial_red((5,5),(3,2),(8,8),(6,6)),
                      'shared_blue':[shared_blue(anchor) for anchor in ('blue','h1','v','r')]},indent=2))


if __name__ == '__main__':
    main()
