"""Rebuild the registered physical controls and compare true-parent histories under both policies."""
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

import model
from model import HERE, ROOT

PREVIOUS = ROOT/'experiments/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A-E001_distance_delays'
sys.path.insert(0,str(PREVIOUS))
import built as baseline

LAWS = ('nae','parity')
RULES = ('ordinary','spent')


def add_terminals(stars, old_names, local_arity):
    """Attach one new terminal per formerly private name, preserving every old name."""
    result=list(stars)
    next_bit=max(max(row) for row in stars)+1
    for bit in old_names:
        own=tuple(range(next_bit,next_bit+local_arity-1))
        next_bit+=len(own)
        result.append((bit,*own))
    return tuple(result)


def expanded(length, shield=False):
    source=baseline.path([6]*(length+1))
    private=model.read(source).loose
    additions=[bit for v in range(1,length) for bit in private[v]]
    grown=add_terminals(source,additions,6)
    if shield:
        middle=length//2
        leaf_start=len(source)+4*(middle-1)
        marks=[bit for row in grown[leaf_start:leaf_start+4] for bit in row[1:]]
        grown=add_terminals(grown,marks,6)
    return grown


def additional_name(stars, a, b):
    rows=list(stars);n=max(max(row) for row in rows)+1
    rows[a]=(*rows[a],n);rows[b]=(*rows[b],n)
    return tuple(rows)


def pace_train(length):
    # Six vertices/section: outer live donors, consecutive spent pair, two live side donors.
    pairs=[];opens=[]
    for i in range(length):
        offset=6*i
        pairs.extend((offset+a,offset+b) for a,b in ((0,1),(1,2),(2,3),(1,4),(2,5)))
        if i:
            pairs.append((offset-3,offset))
        opens.extend((2,0,0,2,2,2))
    return baseline.fixtures.source_from(pairs,opens),0,6*(length-1)+3


def remote(length, changed):
    # Two spent knots w,z, their live a,b and two live chains, with one optional remote name.
    pairs=[(0,1),(0,2),(1,3)]
    n=4+2*length
    for side in (0,1):
        points=[side]+list(range(4+side*length,4+(side+1)*length))
        pairs.extend(zip(points,points[1:]))
    source=baseline.fixtures.source_from(pairs,[0,0]+[6]*(n-2))
    return additional_name(source,3+length,3+2*length) if changed else source


def frames():
    two=baseline.path([3,3]);three=add_terminals(two,[model.read(two).loose[1][-1]],3)
    four=baseline.path([3]*4)
    private=model.read(four).loose
    six=add_terminals(four,[*private[1],*private[2]],3)
    seven=baseline.fixtures.source_from([(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6),(0,1)],(3,0,3,3,3,2,2))
    names,src=baseline.periodic.frame('meeting');twentyone=tuple(src[i] for i in range(len(src)))
    result={
        'two':(two,0,1,4),'two_arity_four':(baseline.path([4,4]),0,1,3),'sole_parity':(baseline.tree([(0,1),(0,2),(0,3)],[3]*4),1,2,3),'three_adjacent':(three,0,1,4),
        'two_doubled':(additional_name(two,0,1),0,1,4),
        'four_ternary':(four,0,3,4),'six_ternary':(six,0,3,4),
        'five_all_live':(baseline.path([6]*5),0,4,3),
        'seventeen_three_spent':(expanded(4),0,4,3),
        'thirtyseven_shielded':(expanded(4,True),0,4,3),
        'seven_all_live':(baseline.path([6]*7),0,6,3),
        'twentyseven_five_spent':(expanded(6),0,6,4),
        'mixed_three':(baseline.path([3,7,3]),0,2,2),
        'mixed_five':(baseline.path([3,3,4,3,3]),0,4,2),
        'seven_source':(seven,0,2,4),'twentyone_source':(twentyone,names.index('s'),names.index('t'),4)}
    for length in range(1,5):
        result[f'pace_{length}']=(*pace_train(length),length)
    return result


def separation(pa, groups, receivers, senders):
    h=nx.Graph();h.add_nodes_from(pa.loose)
    h.add_edges_from(e for group in groups for e in combinations(group,2))
    if not receivers or not senders:
        return 'no_live_receiver_or_sender'
    parts=[dist for a in receivers for b,dist in nx.single_source_shortest_path_length(h,a).items() if b in senders]
    return min(parts) if parts else 'infinity'


def row(detail, phase):
    return dict(age=phase,status=detail.status,funded=detail.funded,groups=detail.groups,added=detail.added,
                bridges=detail.bridges,shortages=detail.shortages,parents=detail.parents,inputs=detail.inputs,
                fresh_counts=[len(bits) for bits in detail.fresh],demand=detail.demand,
                next_added=detail.next_added,planned_births_lower=detail.planned_births_lower)


def trace(stars,law,rule,receiver,sender,depth):
    seen=[];R={receiver};S={sender};first=None;prediction=None
    for age in range(depth):
        detail=model.step(stars,law,rule)
        rec=row(detail,age)
        if rule=='ordinary' and detail.status=='extend':
            ref=baseline.ordinary.step(baseline.ordinary.from_stars(stars),law,max_births=256)
            assert ref.parents==detail.parents and ref.fresh==tuple(len(group) for group in detail.fresh)
        if detail.status!='extend':
            seen.append(rec)
            if detail.status in ('stall','closed') and first is None:
                prediction='infinity_ended'
            break
        # Past the second cut, all subsequent steps use ordinary overlaps. Hence the
        # completed one-step descendants and exact next co-input distance suffice.
        if age==1 and first is None:
            d=separation(model.read(stars),detail.groups,R,S)
            prediction=d+1 if isinstance(d,int) else d
        if age>=2:
            assert not detail.added and not detail.next_added
        firstid=len(stars)
        R={firstid+j for j,p in enumerate(detail.parents) if R.intersection(p)}
        S={firstid+j for j,p in enumerate(detail.parents) if S.intersection(p)}
        common=sorted(R&S)
        rec['receiver_descendants']=sorted(R);rec['sender_descendants']=sorted(S);rec['common']=common
        if common and first is None:
            first=age+1
        rec['state_extension']=baseline.state_extension(stars,detail.stars,law) if age==0 else 'proved'
        seen.append(rec)
        stars=detail.stars
    if first is not None and prediction is not None:
        assert first==prediction,(first,prediction)
    return {'trace':seen, 'first_observed':first, 'first_certified':first if first is not None else prediction}


def matched(case,law):
    stars,r,s,depth=case
    physical=model.read(stars)
    evidence={'lawfulness':baseline.law_record(stars,law),'marks':[physical.loose[r][0],physical.loose[s][0]],
              'physical_distance':nx.shortest_path_length(physical.graph,r,s), 'rule':{}}
    for rule in RULES:
        evidence['rule'][rule]=trace(stars,law,rule,r,s,depth)
    if nx.is_tree(physical.graph) and all(len(bits)==1 for bits in physical.shared.values()):
        evidence['tree_rulers']=baseline.tree_read(stars,r,s)
    return evidence


def distant_controls():
    output={}
    for length in (3,5,8):
        arms=[remote(length,mode) for mode in (False,True)]
        assert len(arms[0])==len(arms[1]) and sum(map(len,arms[1]))==sum(map(len,arms[0]))+2
        assert all(set(old)<=set(new) for old,new in zip(*arms,strict=True))
        pair={}
        for law in LAWS:
            records=[]
            for src in arms:
                baseline.law_record(src,law)
                old=model.read(src)
                rec=model.step(src,law,'spent');assert rec.status=='extend'
                donors={2,3};target=[ps for ps in rec.parents if 2 in ps or 3 in ps]
                records.append({'plan':row(rec,0),'local_births':target,'holder_distance':min(nx.shortest_path_length(old.graph,2,k) for k in (3+length,3+2*length))})
            assert bool(records[0]['plan']['added']) and not records[1]['plan']['added']
            assert records[0]['local_births']!=records[1]['local_births']
            pair[law]=records
        output[length]={'holdings':arms,'laws':pair}
    return output


def run():
    source=frames();results={}
    for name,case in source.items():
        stars,r,s,depth=case
        results[name]={'holdings':stars,'endpoints':[r,s],'law':{law:matched(case,law) for law in LAWS}}
    for law in LAWS:
        rival=lambda name:results[name]['law'][law]['rule']['spent']
        ordinary=lambda name:results[name]['law'][law]['rule']['ordinary']
        for tag in ('seven_source','twentyone_source'):
            assert rival(tag)==ordinary(tag)
        for name in ('two','three_adjacent','two_doubled','four_ternary','six_ternary','five_all_live','seventeen_three_spent','thirtyseven_shielded','seven_all_live','twentyseven_five_spent','mixed_three','mixed_five'):
            assert rival(name)['trace'][0]['funded']
        outcomes={'two':2,'two_arity_four':2,'two_doubled':'infinity','three_adjacent':'infinity',
                  'five_all_live':2,'seventeen_three_spent':2,'thirtyseven_shielded':'infinity',
                  'seven_all_live':3,'twentyseven_five_spent':4,'four_ternary':'infinity','six_ternary':1,
                  'mixed_three':1,'mixed_five':2}
        for tag,expected in outcomes.items():
            assert rival(tag)['first_certified']==expected,(law,tag,rival(tag)['first_certified'],expected)
        for tags in [('two','three_adjacent'),('four_ternary','six_ternary'),
                     ('five_all_live','seventeen_three_spent','thirtyseven_shielded'),
                     ('seven_all_live','twentyseven_five_spent')]:
            values={(results[tag]['law'][law]['tree_rulers']['r'],results[tag]['law'][law]['tree_rulers']['bond_distance']) for tag in tags}
            assert len(values)==1
            assert len({tuple(results[tag]['law'][law]['marks']) for tag in tags})==1
        for n in range(1,5):
            label=f'pace_{n}';assert results[label]['law'][law]['physical_distance']==4*n-1
            assert rival(label)['first_certified']==n
    return {'cases':results,'distant_controls':distant_controls()}


if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'artifacts'/HERE.parent.name/HERE.name/'cases.json');args=parser.parse_args()
    result=run();args.out.write_text(json.dumps(result,separators=(',',':'),sort_keys=True)+'\n');print(len(result['cases']),'physical cases; two laws and policies; three distant edits; receipt',args.out)
