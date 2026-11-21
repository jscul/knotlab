"""New named source draws and physical ordinary cuts under both laws."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import factorial
from random import Random
import gzip
import json
from target import OUTPUT, PRIOR_DATA, advance, width
from census_stages import connected_archive, end_of, following

LEAF="STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B"


def sample():
    catalogue=connected_archive()
    with gzip.open(PRIOR_DATA/'census_stages.json.gz','rt') as f:
        prior=json.load(f)
    summaries={}
    for law,bywidth in catalogue.items():
        order={(tuple(tuple(h) for h in record['source_rows'])):i for i,record in enumerate(prior[law]) if record['source_components']==1}
        rng=Random(int.from_bytes(sha256((LEAF+'|'+law+'|small|fresh6438').encode()).digest(),'big'))
        draws=[]
        for k in range(64):
            n=rng.randrange(3,9)
            choices=bywidth[n]
            named=[factorial(n)//x.automorphisms for x in choices]
            wheel=rng.randrange(sum(named))
            for choice,weight in zip(choices,named,strict=True):
                if wheel<weight:
                    break
                wheel-=weight
            permutation=list(range(n))
            rng.shuffle(permutation)
            source=tuple(tuple(sorted(permutation[i] for i in row)) for row in choice.rows)
            idx=order[choice.rows]
            rows=source; stages=[]; statuses=[]
            for age in (1,2):
                status,after,created=advance(rows,law)
                statuses.append(status)
                if status!='births':
                    break
                physical,nextrows,made=advance(after,law)
                assert following(after)==(physical,len(made)) or (physical in ('stalled','stall') and following(after)[1]==0)
                archive=prior[law][idx]['stages'][age-1]
                assert (archive['width'],archive['next_birth_count'])==(width(after),len(made))
                end,loose=end_of(after)
                stages.append(dict(age=age,observed_width=width(after),physical_status=physical,
                    physical_rows=after,live_loose={h:v for h,v in sorted(loose.items())},next_parent_supports_fresh=[[sorted(after[h] for h in p),q] for p,q in made]))
                rows=after
            draws.append(dict(draw=k,source_width=n,source_index=idx,source=source,source_permutation=permutation,attempts=statuses,stages=stages))
        summaries[law]=draws
    dest=OUTPUT/'small_draws.json.gz'
    with dest.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as z:
        z.write(json.dumps(summaries,separators=(',',':')).encode())
    for law,draws in summaries.items():
        print(law,Counter(r['attempts'][0] for r in draws),Counter(len(r['stages']) for r in draws), len(set(r['source_index'] for r in draws)))

if __name__=='__main__':
    sample()
