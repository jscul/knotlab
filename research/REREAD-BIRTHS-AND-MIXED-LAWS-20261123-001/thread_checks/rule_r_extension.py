# Thread's separate check of study A's test (a): every old word extends at every round under rule R.
# Own enumeration; reads only the stored small histories (knot lists per stage) of the study.
import gzip, json, glob, numpy as np, collections, sys
A='artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/'
def allowed(stars, law, names):
    idx={d:i for i,d in enumerate(names)}; n=len(names)
    W=np.arange(1<<n,dtype=np.int64); ok=np.ones(1<<n,dtype=bool)
    for s in stars:
        t=np.zeros(1<<n,dtype=np.int64)
        for d in s: t+=(W>>idx[d])&1
        ok&= ((t>0)&(t<len(s))) if law=='nae' else ((t&1)==0)
    return W[ok]
rows=[json.loads(l) for f in sorted(glob.glob(A+'prefixes/c_*.jsonl.gz')) for l in gzip.open(f,'rt')]
c=collections.Counter()
for r in rows:
    stars=[tuple(s) for s in r['stars']]; n_at=r['n_at']
    for t in range(len(n_at)-1):
        old=stars[:n_at[t]]; new=stars[:n_at[t+1]]
        on=sorted({d for s in old for d in s}); nn=on+sorted({d for s in new for d in s}-set(on))
        if len(nn)>20: c['rounds skipped (over 20 distinctions)']+=1; continue
        a0=allowed(old,r['law'],on); a1=allowed(new,r['law'],nn)
        proj=np.unique(a1 & ((1<<len(on))-1))
        c['rounds']+=1; c['old words']+=len(a0); c['paying rounds']+= r['paid_births'][t]>0
        holders=collections.Counter(d for s in new for d in s)
        c['rounds whose new stage has a distinction held three or more times']+= max(holders.values())>=3
        if len(proj)!=len(a0) or not np.array_equal(proj,a0): c['ROUNDS WHERE AN OLD WORD FAILS']+=1
        births=new[n_at[t]:]
        c['births with no fresh distinction']+=sum(1 for b in births if all(d in on for d in b))
print(len(rows),'stored histories'); [print(' ',k,v) for k,v in sorted(c.items())]
