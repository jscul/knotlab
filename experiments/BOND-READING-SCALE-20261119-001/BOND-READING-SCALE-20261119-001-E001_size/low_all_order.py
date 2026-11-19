"""Literal low-order-invariant growth with an already hidden higher-order reading."""

from collections import Counter
from itertools import combinations
import json
import sys

import networkx as nx

from low_delayed import production_law, verifier
from low_partial import HOSTS, named_graft, reader, rescore, total_shared_copies


def study(host):
    _,_,_,_,_,deck,_,weights = named_graft(*HOSTS[host])
    check = verifier()
    rule = production_law()
    rows = [[] for _ in deck.sites]
    mapping = {site:j for j,site in enumerate(deck.sites)}
    classes = {}
    width = 0
    for (name,u,v),count in zip(deck.edges,weights,strict=True):
        stored = list(range(width,width+int(count)))
        rows[mapping[u]].extend(stored)
        rows[mapping[v]].extend(stored)
        width += int(count)
        classes[name] = stored
    compact = check.Arrangement.parse(rows)
    full = rescore(deck,weights)
    assert all(not item['differences'] for item in full.values())
    phi = list(range(width))
    for name, image in deck.swapped.items():
        for a,b in zip(classes[name],classes[image],strict=True):
            phi[a] = b
    quartet = ('ha','va','hb','rb')
    image_quartet = tuple(deck.swapped.get(x,x) for x in quartet)
    read = reader(deck,weights)
    values = [read(q) for q in (quartet,image_quartet)]
    assert values[0] is None and values[1] is not None

    # Use a fixed original distinction at the fourth test junction. Retain
    # its old name as the loose distinction at one of its two holders.
    replaced = classes['hd'][0]
    assert phi[replaced] == replaced
    s,t = compact.owners[replaced]
    assert not set(compact.neighbors[s]) & set(compact.neighbors[t])
    rows[t] = sorted([x for x in rows[t] if x != replaced] + [width])
    growth = rule.from_junctions(rows)
    literal = [rows]
    for _ in range(3):
        assert growth.step(rule.gf2(rule.F.fewest),None)['new']
        assert growth.implied_mismatch == 0
        literal.append([sorted(row) for row in growth.bits_of])
    stages = [check.Arrangement.parse(raw) for raw in literal]

    rank_cycle = {classes[key][0] for key in ('ha','va','vb','hb')}
    hub = stages[1].stars[mapping['h0']]
    hub_image = {phi[x] for x in hub}
    assert len(hub & rank_cycle) == 2 and len(hub_image & rank_cycle) == 1
    assert set(compact.labels) - {replaced} >= hub | hub_image

    audit = []
    for index,stage in enumerate(stages):
        assert check.start_audit(stage)['census_open_legal']
        assert all(len(rank_cycle & support)%2 == 0 for support in stage.stars)
        assert hub <= stage.stars[mapping['h0']]
        ends,_,outside = stage.holder_graph()
        exterior = nx.Graph()
        for name,(a,b) in ends.items():
            if name < width and name != replaced:
                continue
            if not exterior.has_edge(a,b):
                exterior.add_edge(a,b,capacity=0)
            exterior[a][b]['capacity'] += 1
        assert nx.is_connected(exterior)
        assert nx.minimum_cut_value(exterior,s,t) == 1
        if index:
            independent = check.round_replay(stages[index-1],stage)
            group_shapes = sorted(Counter((len(r['taken']),len(r['fresh'])) for r in independent).items())
            assert all(phi[x] == x for j in stage.live for x in stage.stars[j] if x < width)
        else:
            group_shapes = []
        audit.append({'age':index,'junctions':len(stage.stars),'width':len(stage.labels),
                      'exterior_unit_cost':True,'independent_parent_counts':group_shapes})
    assert all(classes[name][0] != replaced for name in (*quartet,*image_quartet))
    projection = total_shared_copies(rows)
    projection['current_junctions'] = audit[1]['junctions'] + projection['meet_once_lift_extra_junctions']
    projection['current_distinctions'] = audit[1]['width'] + projection['meet_once_lift_extra_distinctions']
    return {'source_model':host,'literal_rows':literal,'core_full_through_three':full,
            'removed_fixed_distinction':replaced,'terminal_holders':[s,t],
            'core_permutation':phi,'audit':audit,'late_quartet_K':values,
            'quartet':[classes[name][0] for name in quartet],
            'quartet_image':[classes[name][0] for name in image_quartet],
            'red_cycle_allowed_state_change':sorted(rank_cycle),
            'old_bond':sorted(hub),'old_bond_image_outside_span':sorted(hub_image),
            'meet_once_lift':projection}


def small_pair_only(meet_once):
    # The complete graph on four ordinary holders supplies the first six
    # names. Replace the fixed distinction 0 by the growing exterior.
    reference = verifier()
    law = production_law()
    core = [[0,1,2],[0,3,4],[1,3,5],[2,4,5]]
    old = reference.Arrangement.parse(core)
    image = {x:{1:4,4:1}.get(x,x) for x in old.labels}
    least,_,_ = reference.exact_table(old, 32)
    assert all(x == least[tuple(sorted(image[i] for i in q))] for q,x in least.items())
    initial = [[0,1,2] if meet_once else [0,1,2,7], [3,4,6], [1,3,5], [2,4,5], [0,7,8]]
    executor = law.from_junctions(initial)
    rows = [initial]
    for _ in range(3):
        assert executor.step(law.gf2(law.F.fewest),None)['new']
        rows.append([sorted(row) for row in executor.bits_of])
    stages = [reference.Arrangement.parse(raw) for raw in rows]
    counters = []
    for age,stage in enumerate(stages):
        assert reference.start_audit(stage)['census_open_legal']
        assert reference.start_audit(stage)['meets_once'] == meet_once
        measured = None
        if age:
            reference.round_replay(stages[age-1],stage)
            assert all(x not in (1,4) for j in stage.live for x in stage.stars[j])
            if age <= 2:
                pairs,_,_ = reference.exact_table(stage, 1 << 19)
                assert all(value == pairs[tuple(sorted(image.get(x,x) for x in mark))] for mark,value in pairs.items())
                measured = len(pairs)
        ends,_,out = stage.holder_graph()
        branch = nx.Graph()
        for x,(a,b) in ends.items():
            if 1 <= x <= 5:
                continue
            if not branch.has_edge(a,b):
                branch.add_edge(a,b,capacity=0)
            branch[a][b]['capacity'] += 1
        assert nx.minimum_cut_value(branch,0,1) == 1
        assert (stages[1].stars[2] == stage.stars[2] == frozenset((1,3,5)))
        assert all(len({3,4,5} & support)%2 == 0 for support in stage.stars)
        counters.append({'age':age,'junctions':len(stage.stars),'width':len(stage.labels),
                         'branches_have_unit_cut':True,'pairs_checked':measured})
    return {'meeting_convention':'meet_once' if meet_once else 'parallel_allowed',
            'literal_rows':rows,'positive_stages':counters,'old_permutation':image,
            'old_star':[1,3,5],'old_star_image':[3,4,5],'future_K':[3,None]}


def main():
    print(json.dumps({'through_two':[small_pair_only(once) for once in (False,True)],
                      'through_three':{host:study(host) for host in HOSTS}},indent=2))


if __name__ == '__main__':
    main()
