"""Verify frozen physical controls using unrestricted named erasure and actual consumed names."""
from collections import Counter
from itertools import chain
import json

import networkx as nx

from paid_controls import LAWS, OUT, RULES, cases, central, detour, jsonbytes, model, source_from


def independent_permissions(physical):
    """Remove a name, preserving all other names, and measure the residual global distance."""
    live = physical.loose.keys()
    graph = nx.MultiGraph()
    graph.add_nodes_from(physical.graph)
    for (a, b), names in physical.shared.items():
        for bit in names:
            graph.add_edge(a, b, key=bit)
    found = []
    for (w, z), names in physical.shared.items():
        if w in live or z in live:
            continue
        left = tuple(sorted(set(graph[w]) & live))
        right = tuple(sorted(set(graph[z]) & live))
        if not left or not right:
            continue
        for bit in names:
            graph.remove_edge(w, z, key=bit)
            paths = nx.single_source_shortest_path_length(graph,w,cutoff=5)
            graph.add_edge(w, z, key=bit)
            if z not in paths:
                assert set(left).isdisjoint(right)
                found.append((bit,w,z,left,right))
    return sorted(found)


def check(stars, law, rule, row):
    old = model.read(stars)
    observed = sorted(model.local_witnesses(old))
    assert independent_permissions(old)==observed
    if rule == 'local':
        assert observed==sorted((b,w,z,tuple(left),tuple(right)) for b,w,z,left,right in row['bridges'])
    if row['status'] != 'extend':
        return None
    parents = [tuple(p) for p in row['parents']]
    uses = [tuple(p) for p in row['inputs']]
    assert sum(map(len,uses))==len(set(chain.from_iterable(uses)))
    assert set(chain.from_iterable(uses))==set(chain.from_iterable(old.loose.values()))
    for family,bits in zip(parents,uses,strict=True):
        assert len(set(family))==len(family)
        assert all(b in old.loose[k] for k,b in zip(family,bits,strict=True))
    names=[tuple(range(start,start+n)) if n else () for start,n in zip(row['fresh_first'],row['fresh_counts'],strict=True)]
    after=stars+tuple(bs+fs for bs,fs in zip(uses,names,strict=True))
    new=model.read(after)
    inferred=independent_permissions(new)
    assert sorted(model.local_witnesses(new))==inferred
    if rule=='ordinary':
        extras=[]
    elif rule=='spent':
        extras=[(l,r) for _,_,_,l,r in model.separating_witnesses(new)]
    else:
        extras=[(l,r) for _,_,_,l,r in inferred]
    additions=[tuple(sorted(l+r)) for l,r in extras]
    witnesses, end = cases.baseline.fixtures.witnessed_end(new.graph,new.loose)
    ordinary=cases.baseline.fixtures.multi_groups(witnesses,end)
    assert len(additions)==len(set(additions)) and not set(additions).intersection(ordinary)
    assert sorted(additions)==sorted(map(tuple,row['next_added']))
    counts=Counter(p for group in list(ordinary)+additions for p in group)
    assert row['demand']==[counts[len(stars)+j] for j in range(len(parents))]
    floors=[max(1,3-len(ps),counts[len(stars)+j]) for j,ps in enumerate(parents)]
    assert row['fresh_counts']==([0] if law=='parity' and len(parents)==1 else floors)
    return after


def mechanics():
    # Sharing with both sides, and multiple names on the same donor incidence.
    common=source_from([(0,1),(0,2),(1,3),(0,4),(1,4)],[0,0,6,6,6])
    base=detour((3,3),False)
    same_side=cases.additional_name(base,0,2)
    result={}
    for label,stars in [('one_donor_on_both_sides',common),('two_names_for_one_side_donor',same_side)]:
        src=model.read(stars)
        bit=src.shared[0,1][0]
        donors=tuple(sorted((set(src.graph[0])|set(src.graph[1]))&src.loose.keys()))
        result[label]={'holdings':stars,'full_record':model.rooted_record(src,bit),'laws':{}}
        for law in LAWS:
            cases.baseline.law_record(stars,law)
            detail=model.step(stars,law,'local')
            assert detail.status=='extend'
            assert (donors in detail.added)==(label=='two_names_for_one_side_donor')
            assert independent_permissions(src)==sorted(detail.bridges)
            result[label]['laws'][law]=central(detail,src,bit,donors)
    return result


def main():
    cases_data=json.loads((OUT/'old_controls.json').read_text())
    visits=Counter()
    for label,case in cases_data.items():
        for law in LAWS:
            histories=case['laws'][law]
            assert histories['local']==histories['spent']
            if label in ('seven_source','twentyone_source'):
                assert histories['local']==histories['ordinary']
            for rule in RULES:
                stars=tuple(map(tuple,case['holdings']))
                for row in histories[rule]['actions']:
                    visits[(law,rule,row['status'])]+=1
                    stars=check(stars,law,rule,row)
    for arm in json.loads((OUT/'detours.json').read_text()).values():
        assert arm['detour_meetings'][0] is None
        assert arm['radius_two_no_detour'][1]==(arm['detour_meetings'][1]>5)
        assert arm['isomorphic_under_renaming']==arm['same_addressed_record']
        for law in LAWS:
            for stars,policies in zip(arm['holdings'],arm['laws'][law],strict=True):
                for rule,item in policies.items():
                    assert item['funded'] is True
                    check(tuple(map(tuple,stars)),law,rule,item['first_cut'])
                    visits[law,rule,'paid_detour']+=1
    price=json.loads((OUT/'private_edits.json').read_text())
    for h, arm in price.items():
        h=int(h)
        assert arm['rooted_records_equal']
        for law in LAWS:
            for policy in ('local','spent'):
                assert all(p[policy]['focal_grant']==3 for p in arm['laws'][law]['first'])
            rows=arm['laws'][law]['physical_match']
            for i,source in enumerate(arm['holdings']):
                stars=tuple(map(tuple,source))
                for row in rows:
                    stars=check(stars,law,'local',row['arms'][i])
            for key,q in [('A',h),('G',h+1)]:
                changed=[r['age'] for r in rows if r['ancestry'][key]['changed_grants']]
                unmatched=[r['age'] for r in rows if any(r['ancestry'][key]['unmatched'])]
                assert min(changed)==q
                assert (min(unmatched) if unmatched else None)==(q+1 if q+1<=4 else None)
    short=json.loads((OUT/'remote_shortage.json').read_text())
    assert short['records_equal']
    for law in LAWS:
        ok,fail=short['laws'][law]
        assert ok['local']['actual'] and fail['local']['proposed'] and not fail['local']['actual']
        assert fail['local']['shortages']==[[15,1]]
    result={'checks':{'prefix_rosters_and_ancestry':len(cases_data),
                      'distinct_physical_detour_preparations':12,'private_pairs':3,'shortage_pairs':1,
                      'visits':{'/'.join(k):v for k,v in sorted(visits.items())}},
            'local_overlap_multiplicity':mechanics()}
    (OUT/'physical_audit.json').write_bytes(jsonbytes(result)+b'\n')
    print('all funded physical histories, bounded vs independent erasure, actual forecasts, local controls passed')


if __name__=='__main__':
    main()
