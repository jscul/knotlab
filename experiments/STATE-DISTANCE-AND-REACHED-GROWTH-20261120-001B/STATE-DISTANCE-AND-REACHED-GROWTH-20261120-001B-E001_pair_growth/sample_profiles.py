"""Exact named profile checks over the independently sampled source histories."""
from collections import defaultdict
from pathlib import Path
import gzip
import json
from target import OUTPUT, PRIOR_DATA, advance
from explosive_symmetry import table_moves, profile_move, inverse
from census_rate_tables import as_tuple

def load(path):
    with gzip.open(path,'rt') as f:return json.load(f)

def report():
    samples=load(OUTPUT/'small_draws.json.gz')
    rates=load(OUTPUT/'small_rates.json.gz')
    physical=load(PRIOR_DATA/'census_stages.json.gz')
    old_tables=load(PRIOR_DATA/'census_rate_tables.json.gz')
    result={}
    for law, draws in samples.items():
        reps={(r['source'],r['age']):r for r in rates[law]}
        old={(r['source_index'],r['age']):r for r in old_tables[law]['records']}
        outcomes={}
        for weight in ('uniform','inherited'):
            groups=defaultdict(list)
            for (i,age),r in reps.items():
                t=old[i,age] if weight=='uniform' else r
                key=as_tuple(t.get('key',t.get('table_key')))
                order=t.get('order',t.get('table_order'))
                aut=t.get('automorphisms',t.get('table_automorphisms'))
                stage=physical[law][i]['stages'][age-1]
                rows=tuple(map(tuple,stage['rows']))
                _,_,cut=advance(rows,law)
                profile=tuple((tuple(tuple(rows[h]) for h in sorted(s)),q) for s,q in cut)
                base=profile_move(profile,inverse(order))
                gens,size=table_moves(key)
                assert size==aut
                allfixed=all(profile_move(base,g)==base for g in gens)
                groups[key].append((base,allfixed,len(cut)))
            bykey={k:dict(count_unique=len({x[2] for x in v})==1,
                    profile_unique=all(x[1] for x in v) and len({x[0] for x in v})==1) for k,v in groups.items()}
            details={}
            for age in (1,2):
                statuses=[]
                for d in draws:
                    if len(d['stages'])<age:continue
                    r=(old if weight=='uniform' else reps)[d['source_index'],age]
                    k=as_tuple(r.get('key',r.get('table_key')))
                    statuses.append(bykey[k])
                details[str(age)]=dict(reached_draws=len(statuses),draws_with_unique_count=sum(x['count_unique'] for x in statuses),draws_with_unique_named_profile=sum(x['profile_unique'] for x in statuses))
            outcomes[weight]=dict(comparable_histories=len(reps),distinct_tables=len(groups),
                                counts_ambiguous=sum(not x['count_unique'] for x in bykey.values()),
                                named_profiles_ambiguous=sum(not x['profile_unique'] for x in bykey.values()),draws_by_age=details)
        result[law]=outcomes
    (OUTPUT/'small_profile_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':report()
