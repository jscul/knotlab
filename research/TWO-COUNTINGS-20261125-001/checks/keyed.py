import json, sys, itertools
sys.path.insert(0,'.')
from fractions import Fraction as Fr
from myscore import setting_knots, tv, setting_test
from mykt import allowed_states
S=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/structures.json'))
KA,KB=setting_knots()
for name in ['eleven (start)','eighteen (start)']:
    st=[(l,tuple(p)) for l,p in S[name]]
    o0,A0=allowed_states(st); p0={v:i for i,v in enumerate(o0)}
    pats=sorted({tuple(w[p0[v]] for v in ('x1','x2','x3')) for w in A0})
    allpats=list(itertools.product((0,1),repeat=3))
    # for each setting pair, finished states grouped by old state
    fin={}
    for a in (0,1):
        for b in (0,1):
            o,A=allowed_states(st+[KA[a],KB[b]]); p={v:i for i,v in enumerate(o)}
            grp={}
            for w in A:
                old=tuple(w[p[v]] for v in o0)
                rb=tuple(w[p[v]] for v in ('y1','y2','y3','zb'))
                grp.setdefault(old,[]).append(rb)
            fin[(a,b)]=grp
    dom = pats if name.startswith('eleven') else allpats
    res={}
    for b in (0,1):
        dS=[];dF=[]
        for g in itertools.product((0,1),repeat=len(dom)):
            gm=dict(zip(dom,g))
            PS={};PF={};tot=0
            for old in A0:
                a=gm[tuple(old[p0[v]] for v in ('x1','x2','x3'))]
                comps=fin[(a,b)].get(old,[])
                for rb in comps:
                    PS[rb]=PS.get(rb,0)+Fr(1,len(A0))/len(comps)
                    PF[rb]=PF.get(rb,0)+1
                tot+=len(comps)
            PF={k:Fr(v,tot) for k,v in PF.items()}
            dS.append(PS);dF.append(PF)
        mS=max(tv(x,y) for x in dS for y in dS); mF=max(tv(x,y) for x in dF for y in dF)
        res[b]=(str(mS),str(mF))
    f=setting_test([st],counting='finish'); s=setting_test([st],counting='start',s=0)
    print(name,'patterns',len(pats),'g',2**len(dom),'keyed (start, finish pooled) per b',res,'| finish',str(f[0]),str(f[1]),'start',str(s[0]),str(s[1]), 'finished states', f[2])
