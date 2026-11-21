"""Apply the certified integer contraction to the separately seeded small sources."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
import gzip
import json
from explosive_rates import nae_rates, parity_rates, canonical_weighted, component_plan, compact
from target import OUTPUT, PRIOR_DATA

def read(path):
    with gzip.open(path,'rt') as f: return json.load(f)

def save(path,obj):
    with path.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
        f.write(json.dumps(obj,separators=(',',':')).encode())

def run():
    roster=read(OUTPUT/'small_draws.json.gz')
    catalogue=read(PRIOR_DATA/'census_stages.json.gz')
    previous=read(PRIOR_DATA/'census_rate_tables.json.gz')
    archive={law:{(v['source_index'],v['age']):v for v in sheet['records']} for law,sheet in previous.items()}
    result={}
    for law,draws in roster.items():
        keys={(r['source_index'],stage['age']) for r in draws for stage in r['stages']}
        records=[]
        for i,age in sorted(keys):
            old=catalogue[law][i]
            stage=old['stages'][age-1].copy()
            stage['limits']=[len(old['source_rows'])]
            if age==2: stage['limits'].append(len(old['stages'][0]['rows']))
            d=archive[law][i,age]
            if law=='nae':
                try:
                    denominator,counts=nae_rates(stage,'inherited')
                except ValueError as failure:
                    records.append(dict(source=i,age=age,undecided=True,detail=str(failure)))
                    continue
                key=canonical_weighted(stage['width'],denominator,counts)
                assert list(counts.keys())==list(combinations(range(stage['width']),2))
                differ=sum(Fraction(r,denominator)!=Fraction(u,d['allowed_states']) for r,u in zip(counts.values(),d['disagreement_counts'],strict=True))
            else:
                key,_,denominator,counts=parity_rates(stage)
                differ=0
            records.append(dict(source=i,age=age,width=stage['width'],total=denominator,counts=list(counts.values()),key=key.key,order=key.order,automorphisms=key.automorphisms,
                differing_pair_entries=differ,next_count=stage['next_birth_count']))
        result[law]=records
        covered={(r['source'],r['age']):r for r in records}
        for age in (1,2):
            xs=[covered[r['source_index'],age] for r in draws if len(r['stages'])>=age]
            print(law,age,len(xs),sum(x.get('undecided',False) for x in xs),sum((x.get('differing_pair_entries') or 0)>0 for x in xs))
    save(OUTPUT/'small_rates.json.gz',result)

if __name__=='__main__': run()
