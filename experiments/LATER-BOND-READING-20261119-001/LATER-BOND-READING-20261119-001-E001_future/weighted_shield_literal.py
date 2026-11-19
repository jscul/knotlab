"""Replay named asymmetric shield candidates with lawful growing branches."""

from argparse import ArgumentParser
from collections import Counter
import json
from pathlib import Path
import sys
from unittest.mock import patch

import networkx as nx
import numpy as np

from weighted_core import INF, ROOT
from weighted_shield_grouped import layout
from weighted_shield_optimize import current_sites


def named_graft(counts, first_widths, fixed_widths, costs, compact_blue_eight=False):
    deck = layout(counts, True, True)
    sites = {name:j for j,name in enumerate(deck.sites[:-1])}
    rows = [[] for name in sites]
    width_by_bit = []
    bundle_labels = {}
    lineage = {}

    def site(pole):
        j = len(rows)
        rows.append([])
        lineage[j] = pole
        return j

    def attach(first, second, width=1):
        labels = []
        for _ in range(width):
            x = len(width_by_bit)
            rows[first].append(x)
            if second is not None:
                rows[second].append(x)
            width_by_bit.append(x)
            labels.append(x)
        return labels

    widths = []
    for label, left, right in deck.edges:
        if label.startswith('o'):
            widths.append(costs[0 if right.startswith('u') else 1])
            continue
        w = 1
        if label[0] in 'hv' and right in 'abcd':
            w = first_widths[0 if label[0] == 'h' else 1]
        if label.startswith(('hu','hw')):
            w = fixed_widths[0 if label[1] == 'u' else 1]
        widths.append(w)
        bundle_labels[label] = attach(sites[left],sites[right],w)
    old_core_size = len(width_by_bit)
    pi = list(range(old_core_size))
    for a,b in deck.swapped.items():
        for x,y in zip(bundle_labels[a],bundle_labels[b],strict=True):
            pi[x] = y

    for name,pole in sites.items():
        if name.startswith('w'):
            c = costs[1]
            if compact_blue_eight:
                assert c == 8
                for size in (3,3,2):
                    j = site(pole)
                    attach(pole,j,size)
                    attach(j,None,size)
            else:
                j = site(pole)
                attach(pole,j,c)
                attach(j,None,c)
        if name.startswith('u'):
            c = costs[0]
            if c == 2:
                a,b,z = (site(pole) for _ in range(3))
                for x,y,n in ((pole,a,1),(pole,b,1),(a,b,1),(b,z,2),(a,None,2),(b,None,1),(z,None,1)):
                    attach(x,y,n)
            elif c == 3:
                for _ in range(3):
                    q = site(pole)
                    attach(pole,q)
                    attach(q,None,2)
            else:
                live = [site(pole) for _ in range(c)]
                z = site(pole)
                u,v = live[1:3]
                for q in live:
                    attach(pole,q)
                for i,q in enumerate(live[1:]):
                    if q not in (u,v):
                        attach(q,u if i % 2 == 0 else v)
                    attach(q,None,2)
                for x,y in ((u,z),(v,z),(u,v),(z,None)):
                    attach(x,y)
                attach(live[0],None,c-1)
    virtual = np.array(widths,dtype=np.int16)
    return rows, lineage, old_core_size, pi, sites, deck, bundle_labels, virtual


def phase_controls(start, lineage, old_core_size, sites, costs):
    sys.path.insert(0, str(ROOT / 'research/LATER-BOND-READING-20261119-001'))
    from boundary_linear import extend, fastlib, verify

    subset = [frozenset(s) for s in start]
    with patch.object(extend.C.F.Presentation, 'groups_among', fastlib.groups_among):
        here = extend.grow1(subset)
        after = extend.grow1(here)
    stages = [verify.Arrangement.parse([sorted(row) for row in phase]) for phase in (subset,here,after)]
    data = []
    for age, phase in enumerate(stages):
        checks = verify.start_audit(phase)
        assert checks['census_open_legal']
        if age:
            previous = stages[age-1]
            verified = verify.round_replay(previous,phase)
            groups = Counter((len(j['taken']),len(j['fresh'])) for j in verified)
            for j,row in enumerate(phase.stars[len(previous.stars):], start=len(previous.stars)):
                linked = {lineage[previous.loose[x]] for x in row if x in previous.owners}
                assert len(linked) == 1
                lineage[j] = linked.pop()
        else:
            groups = Counter()
        ends, _, out = phase.holder_graph()
        networks = {j:nx.Graph() for name,j in sites.items() if name.startswith(('u','w'))}
        for name,(a,b) in sorted(ends.items()):
            if name < old_core_size:
                continue
            g = networks[lineage[a] if a in lineage else lineage[b]]
            if not g.has_edge(a,b):
                g.add_edge(a,b,capacity=0,names=[])
            g[a][b]['capacity'] += 1
            g[a][b]['names'].append(name)
        capacities = {}
        marked_cut = {}
        for name,pole in sites.items():
            if pole not in networks:
                continue
            g = networks[pole]
            minimum,(left,right) = nx.minimum_cut(g,pole,out)
            expected = (costs[0] if age < 2 else 1) if name.startswith('u') else costs[1]
            assert minimum == expected
            assert nx.is_connected(g.subgraph(left)) and nx.is_connected(g.subgraph(right))
            capacities[name] = int(minimum)
            marked_cut[name] = sorted(x for a,b,d in g.edges(data=True) if (a in left) != (b in left)
                                      for x in d['names'])
        data.append({'junctions':len(phase.stars),'width':len(phase.labels),'minimum_by_branch':capacities,
                     'literal_minimizing_boundary':marked_cut,
                     'new_junctions_by_inputs_and_outputs':[(p,f,n) for (p,f),n in sorted(groups.items())]})
    return stages,data


def virtual_checks(deck, virtual):
    old = virtual @ deck.cut_matrix.T
    future = virtual.copy()
    for name,i in deck.index.items():
        if name.startswith('ou'):
            future[i] = 1
    after = future @ deck.cut_matrix.T

    def minimum_reader(costs):
        order = np.argsort(costs, kind='stable')
        supports = deck.supports[order]
        values = costs[order]
        occurs = {name: int.from_bytes(np.packbits((supports >> i) & 1, bitorder='little').tobytes(), 'little')
                  for i,name in enumerate(deck.names)}

        def read(query):
            possible = occurs[query[0]]
            for name in query[1:]:
                possible &= occurs[name]
            if not possible:
                return INF,None
            index = (possible & -possible).bit_length() - 1
            return int(values[index]),int(supports[index])

        return read

    before_read, after_read = minimum_reader(old), minimum_reader(after)

    def named_support(mask):
        return None if mask is None else [name for i,name in enumerate(deck.names) if mask & (1 << i)]

    histories, four = {}, None
    for order in (1,2,3,4):
        histories[order] = 0
        for p,q in deck.comparisons(order):
            a,b = before_read(p)[0],before_read(q)[0]
            histories[order] += 1
            if order < 4:
                assert a == b, (p,q,a,b)
            elif a != b:
                four={'marks':p,'image':q,'K':[a,b],
                      'virtual_bonds':[named_support(before_read(z)[1]) for z in (p,q)]}
                break
    targets = []
    for p,q in deck.targets():
        targets.append({'marks':p,'image':q,'old_K':[before_read(z)[0] for z in (p,q)],
                        'later_K':[after_read(z)[0] for z in (p,q)],
                        'virtual_later_bonds':[named_support(after_read(z)[1]) for z in (p,q)]})
    assert any(rec['later_K'][0] < rec['later_K'][1] for rec in targets)
    return histories,four,targets


def replay(counts, tests, widths, costs, compact_blue_eight=False):
    start, lineage, core_width, pi, sites, deck, bundle_labels, virtual = named_graft(counts,tests,widths,costs,compact_blue_eight)
    comparisons, four, targets = virtual_checks(deck,virtual)
    stages, phases = phase_controls(start,lineage,core_width,sites,costs)
    assert phases[1]['junctions'] == current_sites(counts,costs) - (counts[1] if compact_blue_eight else 0)
    assert all(min(stages[1].stars[j]) >= core_width for j in stages[1].live)
    def representative(name):
        if name in bundle_labels:
            return min(bundle_labels[name])
        return phases[1]['literal_minimizing_boundary'][name[1:]][0]

    def lift_bond(bundles, phase_index):
        if bundles is None:
            return None
        names = sorted(x for name in bundles for x in (
            bundle_labels[name] if name in bundle_labels
            else phases[phase_index]['literal_minimizing_boundary'][name[1:]]
        ))
        stage = stages[phase_index]
        ends, _, exterior = stage.holder_graph()
        complement = nx.Graph()
        complement.add_nodes_from(range(len(stage.stars)+1))
        assert exterior == len(stage.stars)
        omitted = set(names)
        complement.add_edges_from(e for x,e in ends.items() if x not in omitted)
        components = list(nx.connected_components(complement))
        assert len(components) == 2
        first = components[0]
        assert omitted == {x for x,(a,b) in ends.items() if (a in first) != (b in first)}
        return names
    for entry in [four, *targets]:
        if entry is not None:
            entry.update({key + '_physical':[representative(name) for name in entry[key]] for key in ('marks','image')})
    if four:
        four['literal_bonds'] = [lift_bond(which,1) for which in four['virtual_bonds']]
        assert [len(bond) if bond is not None else INF for bond in four['literal_bonds']] == four['K']
    for target in targets:
        target['literal_later_bonds'] = [lift_bond(which,2) for which in target['virtual_later_bonds']]
        assert [len(bond) if bond is not None else INF for bond in target['literal_later_bonds']] == target['later_K']
        assert set(target['marks_physical']) <= set(target['literal_later_bonds'][0] or ())
        assert set(target['image_physical']) <= set(target['literal_later_bonds'][1] or ())
    return {'shield_counts':counts,'test_arm_widths':tests,'permanent_to_hubs':widths,'costs':costs,
            'compact_blue_eight':compact_blue_eight,
            'comparisons_on_uncompressed_virtual_model':comparisons,'pair_breaks':targets,'first_four':four,
            'phases':phases,'fixed_core_width':core_width,'core_permutation':pi,
            'rows':[[sorted(row) for row in stage.stars] for stage in stages]}


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--counts',type=int,nargs=2,default=[5,5])
    p.add_argument('--test',type=int,nargs=2,default=[3,3])
    p.add_argument('--hubs',type=int,nargs=2,default=[14,14])
    p.add_argument('--costs',type=int,nargs=2,default=[14,14])
    p.add_argument('--compact-blue-eight',action='store_true')
    a=p.parse_args()
    print(json.dumps(replay(a.counts,a.test,a.hubs,a.costs,a.compact_blue_eight),indent=2))


if __name__ == '__main__':
    main()
