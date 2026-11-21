"""Test named co-holding and transposition witnesses on every NAE state representative."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
OLD='READS-HOLDERS-SOURCES-20261120-001B'
OLDER=ROOT/'artifacts'/OLD/(OLD+'-E001_irredundant')


def read_cases():
    with gzip.open(OLDER/'census_cases.json.gz','rt') as f:
        sizes={int(n):laws['nae'] for n,laws in json.load(f).items()}
    with gzip.open(OUT/'census_cases.json.gz','rt') as f:
        sizes[10]=json.load(f)['nae']
    return sizes


def main():
    out={}
    for n,cases in read_cases().items():
        stats=Counter()
        examples={}
        masks={i:sum(1<<w for w in range(1<<n) if not w>>i&1) for i in range(n)}
        for case in cases:
            s=int(case['state_words_hex'],16)
            for pres in case['presentations']:
                rows=[set(r) for r in pres['supports']]
                inc=[{i for i,row in enumerate(rows) if v in row} for v in range(n)]
                simple=all(len(a&b)<=1 for a,b in combinations(rows,2))
                stats['presentations']+=1
                stats['simple' if simple else 'repeated_meetings']+=1
                overlaps=set()
                missing=set()
                for i,j in combinations(range(n),2):
                    di,dj=1<<i,1<<j
                    q00=masks[i]&masks[j]
                    positive=bool(q00&~s&(s>>di)&(s>>dj)&(s>>(di+dj)))
                    common=inc[i]&inc[j]
                    if positive:
                        assert common
                    elif common:
                        missing.add((i,j))
                        var='loose' if len(inc[i])==1 or len(inc[j])==1 else 'shared'
                        label='missing_'+var
                        stats[label]+=1
                        examples.setdefault(label,{'rows':pres['supports'],'pair':[i,j],'owners':[sorted(inc[i]),sorted(inc[j])]})
                        if any(len(rows[k]&rows[l])>=2 for k in common for l in (inc[i]|inc[j])-common):
                            stats['incomplete_at_repeated_neighbour']+=1
                        assert not simple
                    if common:
                        overlaps.add((i,j))
                    if q00 & ((s>>di)^(s>>dj)) == 0:
                        stats['symmetric_pairs']+=1
                        if inc[i]==inc[j]:
                            stats['symmetric_pairs_with_identical_holders']+=1
                        else:
                            p=lambda h: sorted(sorted((j if x==i else i if x==j else x) for x in row) for row in h)
                            rewrites=p(rows)==sorted(sorted(row) for row in rows)
                            key='transposition_moves_holders' if not rewrites else 'transposition_permutes_holders'
                            stats[key]+=1
                            examples.setdefault(key,{'rows':pres['supports'],'pair':[i,j],'simple':simple, 'closed':all(len(h)==2 for h in inc)})
                if not missing:
                    stats['all_physical_pairs_read']+=1
                else:
                    stats['incomplete_presentations']+=1
                    if not pres['has_loose_distinction']:stats['incomplete_and_closed']+=1
        out[str(n)]={'counts':stats,'examples':examples}
    (OUT/'pair_repairs.json').write_text(json.dumps(out,indent=2)+'\n')
    for n,row in out.items():
        print(n,dict(row['counts']))


if __name__=='__main__':
    main()
