"""Exact later pair and triple tests with only some old exterior branches shortened."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = ROOT / 'experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future'
sys.path.insert(0, str(PREVIOUS))
from weighted_shield_literal import named_graft, phase_controls  # noqa: E402

HOSTS = {
    '104': ((6,6), (2,3), (6,6), (4,4)),
    '118': ((5,5), (3,2), (8,8), (6,6)),
}


def reader(deck, weights):
    scalar = weights @ deck.cut_matrix.T
    order = np.argsort(scalar, kind='stable')
    minima, supports = scalar[order], deck.supports[order]
    occurs = {
        name: int.from_bytes(np.packbits((supports >> i) & 1, bitorder='little').tobytes(),'little')
        for i,name in enumerate(deck.names)
    }

    def query(names):
        common = occurs[names[0]]
        for name in names[1:]:
            common &= occurs[name]
        if not common:
            return None
        first = (common & -common).bit_length()-1
        return int(minima[first])

    return query


def rescore(deck, weights):
    read = reader(deck, weights)
    grades = {}
    for order in (1,2,3):
        grades[order] = {'comparisons':0,'differences':0,'pure_core_differences':0,
                         'first_difference':None,'first_pure_core_difference':None}
        grade = grades[order]
        for marks, image in deck.comparisons(order):
            grade['comparisons'] += 1
            a,b = read(marks),read(image)
            if a == b:
                continue
            grade['differences'] += 1
            certificate = {'marks':marks,'image':image,'K':[a,b]}
            if grade['first_difference'] is None:
                grade['first_difference'] = certificate
            if all(not mark.startswith('o') for mark in marks):
                grade['pure_core_differences'] += 1
                if grade['first_pure_core_difference'] is None:
                    grade['first_pure_core_difference'] = certificate
    return grades


def remove_and_replace(rows, lineage, sites, old_core_size, stable_red, price):
    stable_poles = {sites[name] for name in stable_red}
    retained = [i for i in range(len(rows)) if lineage.get(i) not in stable_poles]
    assignment = {i:j for j,i in enumerate(retained)}
    uses = Counter(x for row in rows for x in row)
    still_used = Counter(x for i in retained for x in rows[i])
    bits = [x for x in sorted(still_used) if uses[x] == still_used[x]]
    images = {x:i for i,x in enumerate(bits)}
    assert bits[:old_core_size] == list(range(old_core_size))
    result = [[images[x] for x in rows[i] if x in images] for i in retained]
    owners = {assignment[i]:lineage[i] for i in retained if i in lineage}
    label = len(bits)
    for pole in sorted(stable_poles):
        assert assignment[pole] == pole
        owners[len(result)] = pole
        result[pole].extend(range(label,label+price))
        result.append(list(range(label,label+2*price)))
        label += 2*price
    aliases = {('w' + name if i in stable_poles else name):i for name,i in sites.items()}
    return result,owners,aliases


def total_shared_copies(rows):
    owners = {}
    for j,row in enumerate(rows):
        for x in row:
            owners.setdefault(x, []).append(j)
    pairs = Counter(tuple(indices) for indices in owners.values() if len(indices) == 2)
    extra = sum(count-1 for count in pairs.values())
    return {'beginning_parallel_copies_beyond_one':extra,
            'meet_once_lift_extra_junctions':4*extra,'meet_once_lift_extra_distinctions':6*extra}


def physical_anchor_cap(stage, pole, family, mark, nominal):
    """Exact cut cost through the old anchor wire selected as a virtual proxy."""
    ends, _, exterior = stage.holder_graph()
    vertices = [pole,*sorted(family),exterior]
    indices = {site:i for i,site in enumerate(vertices)}
    edges = [(x,1 << indices[a],1 << indices[b]) for x,(a,b) in ends.items()
             if a in indices and b in indices and {a,b}.intersection(family)]
    assert any(x == mark and a == 1 for x,a,_ in edges)
    pole_wires = [x for x,a,b in edges if (a | b) & 1]
    if len({a | b for _,a,b in edges if (a | b) & 1}) == 1:
        assert len(pole_wires) == nominal
        return nominal,pole_wires

    # A shrinking branch in these hosts has at most 14 internal holders.
    assert len(vertices) <= 16
    adjacent = [0] * len(vertices)
    for _,a,b in edges:
        adjacent[a.bit_length()-1] |= b
        adjacent[b.bit_length()-1] |= a
    from weighted_shield import connected

    all_sites = (1 << len(vertices))-1
    required = next((a,b) for x,a,b in edges if x == mark)
    best = None
    for side in range(1,1 << (len(vertices)-1),2):
        if bool(side & required[0]) == bool(side & required[1]):
            continue
        if not connected(adjacent,side) or not connected(adjacent,all_sites ^ side):
            continue
        cut = [x for x,a,b in edges if bool(side & a) != bool(side & b)]
        if best is None or len(cut)<len(best):
            best = cut
    assert best and len(best) >= nominal
    return len(best),best


def lift_examples(data, host, shrink, comparisons):
    rows,lineage,core,permutation,sites,deck,classes,virtual = data
    counts,_,_,costs = HOSTS[host]
    assert costs[0] == costs[1], 'the inherited literal check uses one common stable price'
    stable = {f'u{i}' for i in range(shrink,counts[0])}
    start, owners, aliases = remove_and_replace(rows,lineage,sites,core,stable,costs[0])
    stages, phases = phase_controls(start,owners,core,aliases,costs)
    here = stages[1]
    assert all(min(here.stars[j]) >= core for j in here.live)
    members = {pole:{j for j,u in owners.items() if u == pole} for name,pole in sites.items()
               if name.startswith(('u','w'))}

    before = reader(deck,virtual)
    lowered = virtual.copy()
    for i in range(shrink):
        lowered[deck.index[f'ou{i}']] = 1
    costs_by_age = [widths @ deck.cut_matrix.T for widths in (virtual,lowered)]

    def lift_minimum(query, phase, marked):
        requested = sum(1 << deck.index[name] for name in query)
        options = np.flatnonzero(deck.supports & requested == requested)
        if not options.size:
            return None
        readings = costs_by_age[phase-1]
        support = int(deck.supports[options[np.argmin(readings[options])]])
        physical = set()
        for j,name in enumerate(deck.names):
            if not support & (1 << j):
                continue
            if name in classes:
                physical.update(classes[name])
            elif name in marked:
                physical.update(marked[name]['witnesses'][phase-1])
            else:
                pole = name[1:]
                alias = 'w'+pole if pole in stable else pole
                physical.update(phases[phase]['literal_minimizing_boundary'][alias])
        ends,_,outside = stages[phase].holder_graph()
        residual = nx.Graph()
        residual.add_nodes_from(range(len(stages[phase].stars)+1))
        assert outside == len(stages[phase].stars)
        residual.add_edges_from(e for x,e in ends.items() if x not in physical)
        pieces = list(nx.connected_components(residual))
        assert len(pieces)==2
        assert physical=={x for x,(a,b) in ends.items() if (a in pieces[0]) != (b in pieces[0])}
        return sorted(physical)

    records = {}
    for order in (2,3):
        group = comparisons[order]
        example = group['first_pure_core_difference'] or group['first_difference']
        if not example:
            continue
        marks, image = example['marks'],example['image']
        physical = {}
        before_adjustment, after_adjustment = 0,0
        local = {}
        for name in (*marks,*image):
            if name in physical:
                continue
            if name in classes:
                physical[name] = min(classes[name]); continue
            pole = sites[name[1:]]
            z = min(x for x in start[pole] if x >= core)
            assert z < len(here.labels)
            physical[name] = z
            after_price = 1 if name.startswith('ou') and name[1:] not in stable else costs[1]
            stages_of_branch = [s for s in stages[1:]]
            previous_cost, previous_bond = physical_anchor_cap(stages_of_branch[0], pole,
                                                                {j for j in members[pole] if j < len(here.stars)}, z, costs[0])
            next_cost, next_bond = physical_anchor_cap(stages_of_branch[1], pole,members[pole],z,after_price)
            before_adjustment += previous_cost-costs[0]
            after_adjustment += next_cost-after_price
            local[name] = {'old_anchor_name':z,'marked_costs':[previous_cost,next_cost],
                           'witnesses':[previous_bond,next_bond]}
        p,q = [physical[name] for name in marks],[physical[name] for name in image]
        assert q == [permutation[x] if x < core else x for x in p]
        old = [before(marks),before(image)]
        word = {'marks_physical':p,'image_physical':q,'virtual':example,'marked_branch_cuts':local,
                'current_K':[None if x is None else x+before_adjustment for x in old],
                'next_K':[None if x is None else x+after_adjustment for x in example['K']]}
        for phase,key in ((1,'current'),(2,'next')):
            bonds = [lift_minimum(args, phase,local) for args in (marks,image)]
            assert [None if bond is None else len(bond) for bond in bonds] == word[key + '_K']
            assert all(bond is None or set(query) <= set(bond) for bond,query in zip(bonds,(p,q),strict=True))
            word[key + '_physical_minimizers'] = bonds
        records[order] = word
    counts_meet_once = total_shared_copies(start)
    counts_meet_once['current_junctions'] = phases[1]['junctions'] + counts_meet_once['meet_once_lift_extra_junctions']
    counts_meet_once['current_distinctions'] = phases[1]['width'] + counts_meet_once['meet_once_lift_extra_distinctions']
    return {'shrinking_red':shrink,'phases':phases,'witnesses':records,'meet_once_lift':counts_meet_once,
            'rows':[[sorted(row) for row in stage.stars] for stage in stages], 'core_permutation':permutation}


def study(host):
    parameters = HOSTS[host]
    counts,_,_,costs = parameters
    data = named_graft(*parameters)
    _,_,_,_,_,deck,_,virtual = data
    source = rescore(deck,virtual)
    assert all(not grade['differences'] for grade in source.values())
    around = []
    best = {}
    # Red branches have one type and their shield permutations commute with
    # the mark. Thus one chosen subset covers every subset of that size.
    for k in range(counts[0]+1):
        weights = virtual.copy()
        for i in range(k):
            weights[deck.index[f'ou{i}']] = 1
        grades = rescore(deck,weights)
        around.append({'shrinking_red':k,'later':grades})
        for order in (2,3):
            if grades[order]['differences'] and order not in best:
                best[order] = k
    literal = [lift_examples(data,host,k,around[k]['later']) for k in sorted(set(best.values()))]
    return {'parent_host':host,'parameters':parameters,'current':source,'later_tests':around,
            'first_break_by_order':best,'literal_witnesses':literal}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=HOSTS, required=True)
    args = parser.parse_args()
    print(json.dumps(study(args.host), indent=2))


if __name__ == '__main__':
    main()
