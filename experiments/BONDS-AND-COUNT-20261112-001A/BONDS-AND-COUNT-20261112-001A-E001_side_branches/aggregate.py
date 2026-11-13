"""Bounded aggregate search; see AGGREGATE_PLAN.md, written before this run.

Previous witnesses and receipt are read-only. Outputs use aggregate_* names.
"""
from __future__ import annotations

import hashlib
import itertools as it
import json
from pathlib import Path
import resource
import time

import compare as C

OUT=C.OUT


def table(states,support,cache):
    key=tuple(sorted(support))
    if key not in cache:
        cache[key]=C.projection(states,key)
    return cache[key]


def verdict(states,support,cache):
    support=tuple(sorted(support))
    allowed=table(states,support,cache)
    if not allowed or len(allowed)==1 << len(support):
        return False
    return all(len(table(states,support[:j]+support[j+1:],cache))==1 << (len(support)-1)
               for j in range(len(support)))


def supports(pool,pairs,maximum=3):
    seen=set()
    for size in range(2,maximum+1):
        for pair in pairs:
            for extra in it.combinations([x for x in pool if x not in pair],size-2):
                support=tuple(sorted((*pair,*extra)))
                if support not in seen:
                    seen.add(support)
                    yield support


def ray_scan(cut):
    pairs=list(it.product(range(3),cut['target']))
    cache={}
    counts={2:0,3:0}
    for support in supports(cut['ray'],pairs):
        counts[len(support)]+=1
        if verdict(cut['states'],support,cache):
            direct=any(set(v)==set(support) and relation==126 for v,relation in cut['factors'])
            return support,cache,counts,direct
    return None,cache,counts,False


def freeze_cut(cut):
    return {k:v for k,v in cut.items() if k!='states'}


def run():
    started=time.monotonic()
    old_receipt=OUT/'receipt.json'
    receipt_hash=hashlib.sha256(old_receipt.read_bytes()).hexdigest()
    rows=C.corpus()
    cases=[]
    counters=dict(eligible_families=len(rows),family_limit=64,ray_cases=0,ray_cap_omissions=0,
                  cheap_ray_bonds=0,no_small_ray_bond=0,side_cuts=0,side_cap_omissions=0)
    result=None
    for rank,row in enumerate(rows[:64],1):
        definition=row['definition'];local_count=definition[1]
        selfs=sum(cl=='SELF' for cl,_ in definition[2])
        for depth in (1,2,3,4):
            case=dict(rank=rank,file=row['file'],line=row['line'],depth=depth)
            if 3+(depth+1)*local_count>18:
                counters['ray_cap_omissions']+=1
                case['status']='ray-variable cap';cases.append(case);continue
            ray=C.cut(definition,depth)
            counters['ray_cases']+=1
            small,cache,counts,direct=ray_scan(ray)
            case.update(ray_variables=len(ray['ray']),ray_models=len(ray['states']),
                        gfp=ray['gfp'],incidence=('no cycle' if C.incidence_forest(ray) else
                                               ('has cycle' if ray['gfp']==255 else 'non-TOP summary')),
                        support_checks=counts)
            if small is not None:
                counters['cheap_ray_bonds']+=1
                case.update(status='ray aggregate at most three',ray_bond=[ray['names'][x] for x in small],
                            direct_factor=direct)
                cases.append(case)
                print(json.dumps(case),flush=True)
                continue
            counters['no_small_ray_bond']+=1
            case['status']='all eligible ray supports of size <=3 excluded'
            cases.append(case)
            for level,side in it.product(range(depth+1),range(1,selfs)):
                if 3+(depth+2)*local_count>21:
                    counters['side_cap_omissions']+=1
                    continue
                branch=C.cut(definition,depth,(level,side))
                counters['side_cuts']+=1
                ids={name:j for j,name in enumerate(branch['names'])}
                pairs=[(u,ids[ray['names'][v]]) for u,v in it.product(range(3),ray['target'])]
                branch_cache={}
                direct_candidates=[]
                pair_sets=[set(pair) for pair in pairs]
                for variables,relation in branch['factors']:
                    if relation==126 and any(pair<=set(variables) for pair in pair_sets):
                        direct_candidates.append(tuple(sorted(variables)))
                seen=set()
                found=None
                for support in it.chain(direct_candidates,supports(range(len(branch['names'])),pairs)):
                    support=tuple(sorted(support))
                    if support in seen:
                        continue
                    seen.add(support)
                    if verdict(branch['states'],support,branch_cache):
                        found=support;break
                if found is None:
                    continue
                assert len(found)==3  # all eligible pair tables unchanged
                ray_names=[ids[name] for name in ray['names']]
                ray_table=C.projection(ray['states'],list(range(len(ray['names']))))
                branch_to_ray=C.projection(branch['states'],ray_names)
                assert ray_table==branch_to_ray
                ray_four=None
                for support in supports(ray['ray'],list(it.product(range(3),ray['target'])),4):
                    if len(support)==4 and verdict(ray['states'],support,cache):
                        ray_four=support;break
                result=dict(source=row,rank=rank,depth=depth,side=[level,side],
                            unrestricted_support=[branch['names'][x] for x in found],
                            unrestricted_minimum=3,ray_minimum=4 if ray_four else None,
                            ray_lower_bound=4,ray_minimum_witness=None if ray_four is None else [ray['names'][x] for x in ray_four],
                            ray_cut=freeze_cut(ray),branch_cut=freeze_cut(branch),
                            ray_allowed_assignments=list(map(int,ray['states'])),
                            branch_allowed_assignments=list(map(int,branch['states'])),
                            ray_small_supports=[dict(support=list(s),allowed=table(ray['states'],s,cache))
                                                for s in supports(ray['ray'],list(it.product(range(3),ray['target'])))],
                            side_support_table=table(branch['states'],found,branch_cache),
                            ray_projection_unchanged=True,elapsed_seconds=time.monotonic()-started,
                            ray_incidence_forest=C.incidence_forest(ray))
                case['status']='strict aggregate shortcut found'
                break
            print(json.dumps(case),flush=True)
            if result is not None:break
        if result is not None:break
    counters.update(families_reached=rank,elapsed_seconds=time.monotonic()-started,
                    peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    old_receipt_sha256=receipt_hash,
                    stop='first strict aggregate shortcut' if result is not None else 'coverage complete')
    assert hashlib.sha256(old_receipt.read_bytes()).hexdigest()==receipt_hash
    (OUT/'aggregate_coverage.json').write_text(json.dumps(dict(summary=counters,cases=cases),indent=2)+'\n')
    if result is not None:
        (OUT/'aggregate_witness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(counters,indent=2))
    if result is not None:
        print(json.dumps({k:result[k] for k in ('source','rank','depth','side','unrestricted_support','ray_minimum','ray_incidence_forest')},indent=2))


if __name__=='__main__':run()
