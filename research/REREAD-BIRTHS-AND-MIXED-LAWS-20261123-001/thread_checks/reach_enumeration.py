# Thread's separate check of study B (reachability). Own enumeration of words; only evaluate(M) is shared (the recorded scorer).
import gzip, json, glob, re, collections, itertools, sys, random
import numpy as np
from fractions import Fraction
src=open('docs/prompts/missed_leads_checks/finished_weighting_chsh.py').read().split('# ---- 1.')[0]; ns={}; exec(src,ns)
evaluate=ns['evaluate']
A='artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/'
def parse(k):
    if isinstance(k,str):
        m=re.match(r'(nae|even|odd)\((.*)\)',k); return (m.group(1),tuple(m.group(2).split(',')))
    return (k[0],tuple(k[1]))
def table(knots, obs=('x1','x2','x3','y1','y2','y3')):
    knots=[parse(k) for k in knots]
    names=sorted({m for _,mem in knots for m in mem}|set(obs)); n=len(names); idx={v:i for i,v in enumerate(names)}
    W=np.arange(1<<n,dtype=np.int64); bit=lambda nm:(W>>idx[nm])&1
    ok=np.ones(1<<n,dtype=bool)
    for law,mem in knots:
        s=sum(bit(m) for m in mem)
        ok&= ((s>0)&(s<len(mem))) if law=='nae' else ((s&1)==(0 if law=='even' else 1))
    xa=bit(obs[0])*4+bit(obs[1])*2+bit(obs[2]); xb=bit(obs[3])*4+bit(obs[4])*2+bit(obs[5])
    M=np.zeros((8,8),dtype=np.int64); np.add.at(M,(xa[ok],xb[ok]),1)
    return M
def score(knots, obs=('x1','x2','x3','y1','y2','y3')):
    M=table(knots,obs); s,hid,ch,_=evaluate(M); return Fraction(s).limit_denominator(100000), bool(hid), int((M>0).sum()), M
targets=json.load(open(A+'targets.json'))
starts=[json.loads(l) for l in gzip.open(A+'starts.jsonl.gz','rt')]
if __name__=='__main__':
    # (a) the seven-knot structure: every connected proper subset holding all six observer distinctions
    seven=[parse(k) for k in targets[0]['knots']]
    full=score(seven); print('seven-knot structure whole:',full[:3])
    def connected(ks):
        if not ks: return False
        comp={0}; grew=True
        while grew:
            grew=False
            for i in range(len(ks)):
                if i not in comp and any(set(ks[i][1])&set(ks[j][1]) for j in comp): comp.add(i); grew=True
        return len(comp)==len(ks)
    sup=collections.Counter(); nst=0
    for mask in range(1,(1<<7)-1):
        ks=[seven[i] for i in range(7) if mask>>i&1]
        held={m for _,mem in ks for m in mem}
        if not {'x1','x2','x3','y1','y2','y3'}<=held or not connected(ks): continue
        nst+=1; sup[score(ks)[2]]+=1
    print('founder starts of the seven-knot structure:',nst,'observer words allowed:',dict(sup),'(whole structure:',full[2],')')
    # (c) new-excess histories: brute-force the start and each written stage-1 table of a sample (all with at most 22 distinctions)
    hits=[json.loads(l) for f in sorted(glob.glob(A+'t1_hits_c2_*.jsonl.gz')) for l in gzip.open(f,'rt')]
    new=[h for h in hits if h['t']>=1 and not h['stage0_excess'] and h['eval'][0] and Fraction(h['eval'][3])>2]
    by=collections.defaultdict(list)
    for h in new: by[(h['tid'],h['mask'],h['si'])].append(h)
    done=agree=0; start_ok=0; nstart=0
    for (tid,mask,si),hs in sorted(by.items()):
        tk=[parse(k) for k in targets[tid]['knots']]
        fk=[tk[i] for i in range(len(tk)) if mask>>i&1]
        if len({m for _,mem in fk for m in mem})<=22:
            s0=score(fk); nstart+=1; start_ok+= (s0[0]<=2 or not s0[1])
        for h in hs:
            ks=[parse(k) for k in h['knots']]
            if len({m for _,mem in ks for m in mem})>22: continue
            s=score(ks); done+=1
            agree+= (s[1] and s[0]==Fraction(h['eval'][3]) and s[0]>2 and (s[3].reshape(-1).tolist()==list(h['table'])))
    print('new-excess tables re-enumerated (stages of at most 22 distinctions):',done,'hidden with the recorded exact score above 2 and the recorded table:',agree)
    print('their starts re-enumerated:',nstart,'with no hidden excess:',start_ok)
