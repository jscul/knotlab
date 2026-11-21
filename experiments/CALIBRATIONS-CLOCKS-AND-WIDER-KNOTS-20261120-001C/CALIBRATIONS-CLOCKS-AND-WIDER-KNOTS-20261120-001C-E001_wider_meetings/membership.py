"""Structural membership of actual first and second cuts, with fresh named draws."""
from collections import Counter, defaultdict
from functools import cache
import gzip
from hashlib import sha256
import json
from math import factorial
from random import Random

from local_parts import HERE, OUT, archive, frozen, load_catalogue, member
from controls import interval
from disconnected import advance, naelib, rows_of
from sample_pair_births import load_large, sample


def sources():
    old=archive()
    result={}
    for law in ('nae','parity'):
        rows={}
        for n in range(3,9):
            for state in old[str(n)][law]:
                for p in state['presentations']:
                    r=frozen(p['supports'])
                    rows[len(rows)]={'id':len(rows),'source_rows':r,'source_width':n,
                                     'meeting_count':sum(map(len,r))-n,'holder_count':len(r),
                                     'labelled_source_multiplicity':factorial(n)//p['presentation_automorphisms']}
        result[law]=rows
    return result


def run():
    library=load_catalogue()
    small=sources()
    raw_large=load_large()
    large={k:{'id':k,'source_rows':v,'source_width':1+max(max(r) for r in v)} for k,v in raw_large.items()}
    @cache
    def observe(law,initial):
        stage=naelib.S.from_junctions(initial)
        cuts=[]
        for age in (1,2):
            status,births=advance(stage,law)
            item={'age':age,'status':status,'births':len(births)}
            if status=='births':
                rows=rows_of(stage)
                item.update(names=stage.nbits,holders=len(rows),membership=member(rows,library,law=='parity'))
            cuts.append(item)
            if status!='births':
                break
        return cuts
    samples={}
    for law in ('nae','parity'):
        samples[law]={}
        for panel in ('tree','extra','explosive'):
            seed=sha256(f'{HERE.parent.name}|{law}|{panel}|202611204126'.encode()).digest()
            rng=Random(int.from_bytes(seed,'big'))
            draws=[]
            for i in range(128):
                source=sample(rng,large if panel=='explosive' else small[law],panel)
                permutation=list(range(source['source_width']))
                rng.shuffle(permutation)
                if i==0:
                    renamed=tuple(tuple(permutation[j] for j in r) for r in source['source_rows'])
                    assert observe(law,renamed)==observe(law,source['source_rows'])
                draws.append({'index':i+1,'source_id':source['id'],'source_width':source['source_width'],
                              'source_permutation':permutation,'cuts':observe(law,source['source_rows'])})
            by_age={}
            for age in (1,2):
                reached=[x['cuts'][age-1] for x in draws if len(x['cuts'])>=age and x['cuts'][age-1]['status']=='births']
                summary={'initial':len(draws),'reached':len(reached),'missing':len(draws)-len(reached),
                         'nonreached_at_attempt':dict(Counter(x['cuts'][age-1]['status'] for x in draws
                             if len(x['cuts'])>=age and x['cuts'][age-1]['status']!='births'))}
                for criterion in ('old','analytic','library'):
                    k=sum(s['membership'][criterion] for s in reached)
                    summary[criterion]={'inside':k,'outside':len(reached)-k,'95pct':interval(k,len(reached))}
                by_age[age]=summary
            samples[law][panel]={'summary':by_age,'draws':draws}
            print(law,panel,[(k,s['reached'],s['old']['inside'],s['analytic']['inside'],s['library']['inside'])
                             for k,s in by_age.items()],flush=True)
    output={'samples':samples}
    # These physical stages are the independently enumerated census. Their
    # class tests do not use a numerical estimate of their full pair table.
    with gzip.open(OUT/'census_stages.json.gz','rt') as f: roster=json.load(f)
    census={}
    for law,cases in roster.items():
        stats=defaultdict(Counter)
        smallest=None
        for case in cases:
            for stage in case['stages']:
                scope=f"{stage['age']}:{'up_to_eight' if case['source_width']<=8 else case['source_width']}"
                flag=member(frozen(stage['rows']),library,law=='parity')
                stats[scope]['total']+=1
                for criterion in ('old','analytic','library'): stats[scope][criterion]+=flag[criterion]
                if not flag['library']:
                    rank=(case['source_width'],stage['age'],stage['width'],len(case['source_rows']))
                    if smallest is None or rank<smallest[0]:
                        smallest=(rank,{'source_rows':case['source_rows'],'reached_rows':stage['rows'],
                                        'next_count':stage['next_birth_count']})
        census[law]={'membership':stats,'first_outside':smallest}
    output['complete_stage_roster']=census
    (OUT/'membership.json.gz').write_bytes(gzip.compress(json.dumps(output,separators=(',',':')).encode(),mtime=0))
    print('Complete membership:',{k:v['membership'] for k,v in census.items()},flush=True)


if __name__=='__main__':
    run()
