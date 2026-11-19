"""Replace parallel bundles by small exhausted simple parity parts."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import networkx as nx

from low_delayed import production_law, verifier


def simple_lift(histories, specified, literal_marks):
    check = verifier()
    least = check.Arrangement.parse(histories[0])
    exhausted = set(range(len(least.stars))) - least.live
    pairs = defaultdict(list)
    for x,owners in least.owners.items():
        if len(owners) == 2:
            pairs[tuple(owners)].append(x)
    expanded = [set(row) for row in histories[0]]
    interior = []
    bundles, eliminated = {},set()
    next_name = 1 + max(x for row in histories[-1] for x in row)

    def add(a,b):
        nonlocal next_name
        name = next_name
        next_name += 1
        for site in (a,b):
            if site < len(expanded):
                expanded[site].add(name)
            else:
                interior[site-len(expanded)].add(name)
        return name

    multiplicities = Counter()
    for owners,names in sorted(pairs.items()):
        labels = sorted(names)
        size = len(labels)-1
        if not size:
            continue
        assert size == 1 or exhausted.intersection(owners), "the graph substitution would create a live common witness"
        eliminated.update(labels[1:])
        for site in owners:
            expanded[site].difference_update(labels[1:])
        a,b = owners
        current_first = len(expanded)+len(interior)
        count = 3 if size == 1 else size
        holders = list(range(current_first,current_first+count))
        interior.extend(set() for _ in holders)
        module = nx.Graph()
        identities = []

        def wire(u,v):
            identities.append(add(u,v))
            module.add_edge(u,v,capacity=1)

        if size == 1:
            for i,u in enumerate(holders):
                wire(u,holders[(i+1)%3])
                wire(u,a if i<2 else b)
        else:
            for u in holders:
                wire(u,a)
                wire(u,b)
            left = count % 2
            if left:
                wire(holders[0],holders[1])
                wire(holders[1],holders[2])
                left = 3
            for i in range(left,count,2):
                wire(holders[i],holders[i+1])
        assert all(module.degree(u) >= 3 for u in holders)
        assert nx.minimum_cut_value(module,a,b) == size
        bundles[labels[0]] = identities
        multiplicities[size] += 1

    kept = sorted(set(least.labels)-eliminated)
    graft_bits = sorted(set().union(*interior)-set(kept))
    zero_age = kept + graft_bits
    fresh = range(len(least.labels), 1 + max(x for row in histories[-1] for x in row))
    rename = {x:i for i,x in enumerate([*zero_age,*fresh])}
    def transform(raw):
        return [sorted(rename[x] for x in row if x not in eliminated) for row in raw]

    forecast = []
    for raw in histories:
        older = transform(raw[:len(expanded)])
        forecast.append([*older,*transform(interior),*transform(raw[len(expanded):])])
    # The added module's links attach to old terminals as well as their new
    # internal holders. Keep those fixed old-terminal incidences at every age.
    for raw in forecast:
        for i in range(len(expanded)):
            raw[i].extend(rename[x] for x in expanded[i] if x in graft_bits)
            raw[i].sort()
    assert forecast[0][:len(expanded)] == transform(expanded)

    mapped = list(range(len(set().union(*map(set, forecast[1])))))
    for x in kept:
        mapped[rename[x]] = rename[specified[x]] if x < len(specified) else rename[x]
    for x,edge_names in bundles.items():
        target = specified[x] if x < len(specified) else x
        for a,b in zip(edge_names,bundles[target],strict=True):
            mapped[rename[a]] = rename[b]
    assert sorted(mapped) == list(range(len(mapped)))

    prepared = [check.Arrangement.parse(raw) for raw in forecast]
    audit = [check.start_audit(stage) for stage in prepared]
    assert all(item['census_open_legal'] and item['meets_once'] for item in audit)
    expected_hist = [check.round_replay(a,b) for a,b in zip(prepared,prepared[1:])]
    law = production_law()
    literal = law.from_junctions(forecast[0])
    for i, expected in enumerate(prepared[1:],start=1):
        assert literal.step(law.gf2(law.F.fewest),None)['new']
        assert literal.implied_mismatch == 0
        actual = check.Arrangement.parse([sorted(row) for row in literal.bits_of])
        assert sorted(map(tuple, map(sorted, expected.stars))) == sorted(map(tuple, map(sorted, actual.stars))), i
    assert all(mapped[x] == x for j in prepared[1].live for x in prepared[1].stars[j])
    for record in literal_marks.values():
        if 'marks_physical' in record:
            a,b = record['marks_physical'],record['image_physical']
            assert all(moved in rename for moved in (*a,*b))
            assert [mapped[rename[x]] for x in a] == [rename[x] for x in b]

    return {'sizes_by_age':[[len(stage.stars),len(stage.labels)] for stage in prepared],
            'bundle_modules_by_cost':dict(multiplicities),'added_internal_junctions':len(interior),
            'literal_rows':forecast,'literal_permutation':mapped,
            'counts_per_formation_round':[dict(Counter(str((len(r['taken']),len(r['fresh']))) for r in groups))
                                          for groups in expected_hist],
            'measured_old_names':{order:{key:[rename[x] for x in names] for key,names in record.items()
                                         if key in ('marks_physical','image_physical')}
                                  for order,record in literal_marks.items()}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('partial',type=Path)
    p.add_argument('all_order',type=Path)
    args = p.parse_args()
    partial = json.loads(args.partial.read_bytes())
    all_order = json.loads(args.all_order.read_bytes())
    witnesses = {}
    for case in partial['literal_witnesses']:
        name = str(case['shrinking_red']) + '_shrinking'
        witnesses[name] = simple_lift(case['rows'],case['core_permutation'],case['witnesses'])
    for host,case in all_order['through_three'].items():
        marks = {'4':{'marks_physical':case['quartet'],'image_physical':case['quartet_image']}}
        witnesses['all_order_' + host] = simple_lift(case['literal_rows'],case['core_permutation'],marks)
    print(json.dumps(witnesses,indent=2))


if __name__ == '__main__':
    main()
