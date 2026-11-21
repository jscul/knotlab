"""Certify necessary loose-row tests and audit spent false candidates."""
from collections import Counter
from itertools import combinations
import gzip
import json

from target import OUTPUT, PRIOR_DATA


def screen(n,total,counts,rows):
    # Raw common denominator keeps every test exact even on very wide carriers.
    c=[[total if i==j else 0 for j in range(n)] for i in range(n)]
    for (i,j),value in zip(combinations(range(n),2),counts,strict=True):
        c[i][j]=c[j][i]=total-2*value
    own=[[] for _ in range(n)]
    for h,row in enumerate(rows):
        for i in row: own[i].append(h)
    truth={i for i in range(n) if len(own[i])==1}
    apparent=[]
    for i in range(n):
        value=min(c[i])
        others=[j for j in range(n) if j!=i and c[i][j]==value]
        if i in truth:
            assert {i,*others}==set(rows[own[i][0]])
        if len(others)<2 or value>=0:
            continue
        if len(others)==2:
            a,b=others
            feasible=(total+c[a][b]==-2*value)
        elif len(others)==3:
            a,b,d=others
            feasible=(total+c[a][b]+c[a][d]+c[b][d]==-4*value)
        else:
            feasible=all(total+c[a][b]+c[a][d]+c[b][d]>-4*value for a,b,d in combinations(others,3))
        if feasible: apparent.append(i)
    assert truth<=set(apparent)
    loose_sorted=sorted(truth)
    witnesses=0; exact=0
    # Test the difference identity as a necessary bound for each old input.
    for row in rows:
        loose=[u for u in row if u in truth]
        if not loose: continue
        f=loose[0]
        for x in set(row)-set(loose):
            values=[(c[x][j]-c[f][j],j) for j in range(n) if j not in (f,x)]
            low=min(a for a,_ in values)
            keys={j for a,j in values if a==low}
            K=next(set(rows[h]) for h in own[x] if set(rows[h])!=set(row))
            assert low<0 and K-{x}<=keys
            witnesses+=1; exact+=keys==K-{x}
    return dict(loose_names=len(truth),simple_minimum_screen=len(apparent),extra_spent_indices=sorted(set(apparent)-truth),
                old_inputs_tested=witnesses,former_holder_exact=exact)


def run():
    with gzip.open(PRIOR_DATA/'census_stages.json.gz','rt') as f: archive=json.load(f)['nae']
    with gzip.open(PRIOR_DATA/'census_rate_tables.json.gz','rt') as f: records=json.load(f)['nae']['records']
    result=[]
    for r in records:
        i,age=r['source_index'],r['age']
        rows=archive[i]['stages'][age-1]['rows']
        d=screen(r['width'],r['allowed_states'],r['disagreement_counts'],rows)
        if age>=2: assert d['old_inputs_tested']==d['former_holder_exact']
        result.append(dict(source_index=i,age=age,width=r['width'],**d))
    with (OUTPUT/'role_screen.json.gz').open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
        f.write(json.dumps(result,separators=(',',':')).encode())
    for age in (1,2):
        xs=[r for r in result if r['age']==age]
        print(age,len(xs),sum(not r['extra_spent_indices'] for r in xs),sum(r['old_inputs_tested'] for r in xs),sum(r['former_holder_exact'] for r in xs),
                sum(r['loose_names'] for r in xs),sum(len(r['extra_spent_indices']) for r in xs))

if __name__=='__main__':
    run()
