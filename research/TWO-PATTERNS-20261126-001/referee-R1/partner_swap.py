"""Swap the other start, holding fixed its site counts and the receiver's role.
Screen on recorded own-birth counts. Check complete birth records only on a
small specified set of candidates. This is a post hoc sensitivity check.
"""
from argparse import ArgumentParser
from collections import defaultdict, Counter
from itertools import combinations
import gzip
import json
from pathlib import Path
from time import monotonic
from random import Random
from mark_opportunities import part
from regrow_engine import Growth, joined

HERE=Path(__file__).resolve().parent

def candidates(limit):
    groups=defaultdict(list)
    with gzip.open(HERE.parent/'census/census_runs.jsonl.gz','rt') as f:
        for row in f:
            r=json.loads(row)
            if r.get('rounds',0)<7:
                continue
            for receiver,other in [('A','B'),('B','A')]:
                h,e,s=part(r[other])
                group=(r[receiver],receiver,r['join'],*r['law'],h[s],sum(s in p for p in e))
                groups[group].append((r[other],r['knots'],r['reads'][receiver]['own births']))
    counts=Counter(); frames=defaultdict(list)
    for group,growths in list(sorted(groups.items()))[:limit]:
        for (b,n,x),(c,m,y) in combinations(sorted(growths),2):
            first=next((i for i,(u,v) in enumerate(zip(x,y),1) if u!=v),0)
            counts[first or 'none']+=1
            if not first and max(n,m)<=250:
                frames[(group[2],group[3])].append((group,b,c,x[:len(y)],y[:len(x)]))
    return counts,frames

def verify(job):
    (a,tag,join,r,t,loose,shared),b,c,x,y=job
    names={}
    arms=[]
    for other in (b,c):
        ab=(a,other) if tag=='A' else (other,a)
        arms.append(Growth(*joined(*ab,1,join),r,t,name_table=names))
    by_round=[]
    for i in range(len(x)):
        both=[]
        for g in arms:
            row=g.step()
            both.append(sorted((g.tokens[u],row['fresh'][u],len(g.places[u]))
                               for u in row['births'] if g.ancestry[u]=={tag}))
        assert [len(z) for z in both]==[x[i],y[i]]
        by_round.append({'numbers':[len(both[0]),len(both[1])],'same complete records':both[0]==both[1]})
    return {'receiver':a,'role':tag,'partners':[b,c],'join':join,'law':[r,t],
            'partner site holdings':{'loose':loose,'shared':shared},
            'rounds':by_round,'first count difference':None,
            'first difference by making':next((i for i,x in enumerate(by_round,1) if not x['same complete records']),None)}

if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    start=monotonic()
    # One random equal-count swap per join and ration. The comparison costs
    # have an explicit size ceiling. The screen itself uses every saved case.
    counts,frames=candidates(None)
    rng=Random(261126)
    draws=[rng.choice(frame) for _,frame in sorted(frames.items())]
    chosen=[verify(job) for job in (draws[:1] if args.pilot else draws)]
    result={'seed':261126,'screen first count differences':counts,'screen comparisons':sum(counts.values()),
            'equal-count sample frames (at most 250 knots in either record)':{str(k):len(v) for k,v in frames.items()},
            'tested':chosen,'seconds':round(monotonic()-start,3)}
    if args.pilot:print('One sampled swap in',result['seconds'],'seconds, six estimated below two seconds.')
    else:(HERE/'partner_swap.json').write_text(json.dumps(result,indent=2)+'\n')
