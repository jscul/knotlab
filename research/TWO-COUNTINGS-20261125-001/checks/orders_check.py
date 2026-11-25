import json, sys, collections, time
sys.path.insert(0,'.')
from fractions import Fraction as Fr
from myscore import weights, joint, score, change, setting_knots
S=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/structures.json'))
O=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/construction_orders.json'))
KA,KB=setting_knots()
E=[(l,tuple(p)) for l,p in S['eleven (start)']]
part=[(l,tuple(p)) for l,p in S['smallest gain: part']]
rnd=[(l,tuple(p)) for l,p in S['smallest gain: part + rule-Q round 1']]
G=part+[k for k in rnd if k not in part]
lst=sys.argv[1]
base=E if lst.startswith('eleven') else G
ia=len(base); ib=len(base)+1
def knot(i,a,b):
    if i==ia: return KA[a]
    if i==ib: return KB[b]
    return base[i]
def in_class(o):
    ok=True
    for idx,places in ((ia,{'x1','x2','x3'}),(ib,{'y1','y2','y3'})):
        p=o.index(idx); held=set()
        for j in o[:p]:
            if j==ia: held|={'x1','za'}
            elif j==ib: held|={'y1','zb'}
            else: held|=set(base[j][1])
        ok = ok and places<=held
    return ok
out=[]
t0=time.time()
orders=O[lst]['orders']
rng=range(len(orders)) if len(sys.argv)<3 else [int(x) for x in sys.argv[2].split(',')]
for n in rng:
    o=orders[n]
    Ps={}; kept={}
    for a in (0,1):
        for b in (0,1):
            stages=[[]]+[[knot(i,a,b)] for i in o]
            od,st,W,tot=weights(stages,0)
            Ps[(a,b)]=joint(od,st,W); kept['%d%d'%(a,b)]=str(tot)
    sc=score(Ps); ch=change(Ps)
    out.append({'n':n,'class':in_class(o),'score':str(sc),'change':str(ch),'kept':kept})
json.dump(out,open('orders_%s.json'%lst,'w'))
c=collections.Counter()
for r in out:
    s=Fr(r['score']); h=Fr(r['change'])==0
    c[(r['class'], 'at 2' if s==2 else ('above 2' if s>2 else 'below 2'), 'hidden' if h else 'not hidden')]+=1
print(lst, dict(c), round(time.time()-t0,1))
hid=[ (Fr(r['score']),r['n']) for r in out if not r['class'] and Fr(r['change'])==0]
if hid:
    m=max(hid)[0]; print('largest hidden outside', m, [n for s,n in hid if s==m])
