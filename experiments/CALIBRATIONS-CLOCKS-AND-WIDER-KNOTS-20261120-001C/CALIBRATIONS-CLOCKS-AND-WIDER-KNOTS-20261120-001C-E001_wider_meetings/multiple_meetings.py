"""Read a tree of larger repeated meetings and verify its secondary scope."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random

import networkx as nx

from local_parts import (HERE, OUT, count_pairs, decode, frozen, legal_part, load_catalogue,
                         member, nae_separator, physical_parts, width)
from census_rates import twin_classes
from controls import interval
from disconnected import advance, naelib, rows_of
from membership import sources
from sample_pair_births import load_large, sample


@cache
def multiple_tree(rows):
    if len(rows)<3:
        return False
    owners=defaultdict(list)
    for i,r in enumerate(rows):
        for x in r:
            owners[x].append(i)
    private=Counter(h[0] for h in owners.values() if len(h)==1)
    if any(private[i]<2 for i in range(len(rows))):
        return False
    joins=Counter(tuple(h) for h in owners.values() if len(h)==2)
    g=nx.Graph()
    g.add_nodes_from(range(len(rows)))
    g.add_edges_from(joins)
    return nx.is_tree(g) and min(joins.values(),default=0)>=2


def read_groups(names,signed,total):
    n=len(names)
    matrix=[[None if i==j else Fraction(signed[i][j],total) for j in names] for i in names]
    groups=twin_classes(matrix)
    assert min(map(len,groups))>=2
    p=[]
    for group in groups:
        c=matrix[group[0]][group[1]]
        k=len(group)
        p.append(c+(1-c)/2**(k-1))
    result=nx.Graph()
    result.add_nodes_from(range(len(groups)))
    def corr(i,j):
        return matrix[groups[i][0]][groups[j][0]]
    for a,b in combinations(range(len(groups)),2):
        if all(abs(corr(a,b))*p[k] > abs(corr(a,k)*corr(k,b)) for k in range(len(groups)) if k not in (a,b)):
            result.add_edge(a,b)
    return tuple(sorted(tuple(sorted(names[i] for g in h for i in groups[g])) for h in nx.find_cliques(result)))


def test_parts():
    out=[]
    for joins,priv in [([(0,1,2),(1,2,2)],[2,2,2]),
                       ([(0,1,3),(1,2,2),(2,3,2)],[3,2,4,2]),
                       ([(0,1,2),(0,2,3),(0,3,2)],[2,3,2,2]),
                       ([(0,1,3),(0,2,2),(1,3,3),(1,4,2)],[3,2,2,3,2])]:
        rows=[[] for _ in priv]
        i=0
        for a,b,k in joins:
            for _ in range(k):
                rows[a].append(i);rows[b].append(i);i+=1
        for j,k in enumerate(priv):
            rows[j].extend(range(i,i+k));i+=k
        core=tuple(map(tuple,rows))
        assert multiple_tree(core)
        for attached in (False,True):
            system=core+((rows[0][-1],i,i+1),) if attached else core
            total,counts=count_pairs(system,'nae')
            inferred=decode(width(system),total,counts,{},read_groups)
            assert set(map(frozenset,system))==set(map(frozenset,inferred))
            assert not nae_separator(system,inferred) and not nae_separator(inferred,system)
            out.append({'critical_joins':joins,'private_per_holder':priv,'single_name_attachment':attached,
                        'stage_width':width(system),'words':total,'all_named_rules_read':True})
        # Changing one supply or one meeting moves the presentation outside
        # the secondary hypothesis, irrespective of what its rates happen to do.
        a,b,_=joins[0]
        one_name=rows[a][0]
        short=[tuple(i for i in h if i!=one_name) for h in core]
        if joins[0][2]==2:
            assert not multiple_tree(tuple(short))
        j=next((j for j,k in enumerate(priv) if k==2),None)
        if j is not None:
            private_less=list(core);private_less[j]=private_less[j][:-1]
            assert not multiple_tree(tuple(private_less))
    return out


def classify_stage(rows,library,law):
    flags=member(rows,library,law=='parity')
    if any(len(r)<3 for r in rows):
        return flags|{'extended_analytic':False,'extended_library':False,'contains_secondary':False}
    parts=physical_parts(rows)
    outside=[local for _,local in parts if not multiple_tree(local)]
    hit=len(outside)<len(parts)
    if not hit:
        return flags|{'extended_analytic':flags['analytic'],'extended_library':flags['library'],'contains_secondary':False}
    other=[member(local,library,law=='parity') for local in outside]
    return flags|{'extended_analytic':all(f['analytic'] for f in other),
                  'extended_library':all(f['library'] for f in other),'contains_secondary':True}


def saved_and_fresh(fresh):
    library=load_catalogue()
    small=sources()
    large={k:{'id':k,'source_rows':v,'source_width':width(v)} for k,v in load_large().items()}
    @cache
    def classify(law,rows):
        stage=naelib.S.from_junctions(rows)
        cuts=[]
        for age in (1,2):
            status,births=advance(stage,law)
            item={'age':age,'status':status,'births':len(births)}
            if status=='births':
                item['membership']=classify_stage(rows_of(stage),library,law)
            cuts.append(item)
            if status!='births':break
        return cuts
    primary=None
    if not fresh:
        with gzip.open(OUT/'membership.json.gz','rt') as f:primary=json.load(f)['samples']
    panels={}
    all_flags=('old','analytic','library','extended_analytic','extended_library','contains_secondary')
    for law in ('nae','parity'):
        panels[law]={}
        for panel in ('tree','extra','explosive'):
            population=large if panel=='explosive' else small[law]
            draws=[]
            if fresh:
                seed=sha256(f'{HERE.parent.name}|multiple-meetings-confirmation|{law}|{panel}|202611209037'.encode()).digest()
                rng=Random(int.from_bytes(seed,'big'))
            for i in range(128):
                if fresh:
                    source=sample(rng,population,panel)
                    perm=list(range(source['source_width']));rng.shuffle(perm)
                else:
                    old=primary[law][panel]['draws'][i]
                    source=population[old['source_id']];perm=old['source_permutation']
                cuts=classify(law,source['source_rows'])
                if not fresh:
                    assert all(c['status']==o['status'] for c,o in zip(cuts,old['cuts'],strict=True))
                    for c,o in zip(cuts,old['cuts'],strict=True):
                        if c['status']=='births':
                            assert all(c['membership'][k]==o['membership'][k] for k in ('old','analytic','library'))
                draws.append({'index':i+1,'id':source['id'],'permutation':perm,'cuts':cuts})
            by_age={}
            for age in (1,2):
                reached=[d['cuts'][age-1]['membership'] for d in draws if len(d['cuts'])>=age and d['cuts'][age-1]['status']=='births']
                counts={k:sum(s[k] for s in reached) for k in all_flags}
                by_age[age]={'initial':128,'reached':len(reached),'missing':128-len(reached),'inside':counts,
                             'interval_extended_library':interval(counts['extended_library'],len(reached)),
                             'joint_flag_classes':dict(Counter(''.join(str(int(s[k])) for k in all_flags) for s in reached))}
            panels[law][panel]={'age_summary':by_age,'draws':draws}
            print('fresh' if fresh else 'original',law,panel,[(k,d['reached'],d['inside']['extended_library'],d['inside']['contains_secondary']) for k,d in by_age.items()],flush=True)
    return {'flag_order':all_flags,'panels':panels}


def main(fresh):
    data=saved_and_fresh(fresh)
    if not fresh:
        data['constructed_verification']=test_parts()
        library=load_catalogue()
        with gzip.open(OUT/'census_stages.json.gz','rt') as f:cases=json.load(f)
        census={}
        for law,roster in cases.items():
            scope=defaultdict(Counter)
            for source in roster:
                for stage in source['stages']:
                    key=f"{stage['age']}:{'up_to_eight' if source['source_width']<=8 else source['source_width']}"
                    flags=classify_stage(frozen(stage['rows']),library,law)
                    scope[key]['total']+=1
                    for flag in ('old','analytic','library','extended_analytic','extended_library','contains_secondary'):
                        scope[key][flag]+=flags[flag]
            census[law]=scope
        data['census']=census
    name='multiple_meetings_confirmation.json.gz' if fresh else 'multiple_meetings.json.gz'
    (OUT/name).write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument('--fresh-confirmation',action='store_true')
    main(a.parse_args().fresh_confirmation)
