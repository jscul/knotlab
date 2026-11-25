import json, sys
sys.path.insert(0,'.')
from fractions import Fraction as Fr
from myscore import weights, joint, score, change
from mykt import allowed_states
I=json.load(open('items_structs.json'))
def P(rules, counting):
    rules=[(l,tuple(p)) for l,p in rules]
    if counting=='finish':
        o,st=allowed_states(rules); return o,st,[Fr(1,len(st))]*len(st)
    o,st,W,tot=weights([rules[:10],rules[10:]],0); return o,st,W
for name in ['ten A x2-x3/y3-t','ten B x2-x3/y2-t','ten A x2-c/y3-t','ten B x3-c/y2-t']:
    hist=sorted({k.split(' | ')[1] for k in I if k.startswith(name+' |')})
    res={}
    pooled={'finish':{}, 'finish_nu':{}, 'start':{}}
    for h in hist:
        for c in ('finish','start'):
            Ps={}
            for a in (0,1):
                for b in (0,1):
                    o,st,W=P(I['%s | %s | (%d, %d)'%(name,h,a,b)],c)
                    Ps[(a,b)]=joint(o,st,W)
                    if c=='finish':
                        # TD 3.5 pooled: each (history, state) once -> counts
                        J=joint(o,st,[Fr(1)]*len(st))
                        for k,v in J.items(): pooled['finish'].setdefault((a,b),{}); pooled['finish'][(a,b)][k]=pooled['finish'][(a,b)].get(k,0)+v
                        for k,v in Ps[(a,b)].items(): pooled['finish_nu'].setdefault((a,b),{}); pooled['finish_nu'][(a,b)][k]=pooled['finish_nu'][(a,b)].get(k,0)+v/len(hist)
                    else:
                        for k,v in Ps[(a,b)].items(): pooled['start'].setdefault((a,b),{}); pooled['start'][(a,b)][k]=pooled['start'][(a,b)].get(k,0)+v/len(hist)
            res[(h,c)]=(str(score(Ps)),str(change(Ps)))
    for ab,J in pooled['finish'].items():
        t=sum(J.values()); pooled['finish'][ab]={k:v/t for k,v in J.items()}
    print(name, res, 'pooled finish TD3.5', str(score(pooled['finish'])), str(change(pooled['finish'])), 'pooled finish nu', str(score(pooled['finish_nu'])), str(change(pooled['finish_nu'])),'pooled start', str(score(pooled['start'])), str(change(pooled['start'])))
