import json, sys, collections, time
sys.path.insert(0,'.')
from myscore import setting_test, setting_knots
from mykt import test_structure, allowed_states
S=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/structures.json'))
E=[(l,tuple(p)) for l,p in S['eleven (start)']]
par=[i for i,(l,p) in enumerate(E) if l in ('even','odd')]
assert len(par)==9
KA,KB=setting_knots()
out=[]
t0=time.time()
for idx in range(512):
    st=list(E)
    for bit,i in enumerate(par):
        st[i]=('odd' if (idx>>bit)&1 else 'even', E[i][1])
    order,states=allowed_states(st)
    pos={v:i for i,v in enumerate(order)}
    def tie(a,b):
        s={w[pos[a]]==w[pos[b]] for w in states}
        return 'eq' if s=={True} else ('neq' if s=={False} else 'none')
    f=setting_test([st],counting='finish'); s=setting_test([st],counting='start',s=0)
    fails=collections.Counter()
    for a in (0,1):
        for b in (0,1):
            T=test_structure(st+[KA[a],KB[b]])
            for x in T['rules']:
                if not x['whole']: fails[x['rule'].split('(')[1]]+=1
    T0=test_structure(st)
    f0=[x['rule'].split('(')[1] for x in T0['rules'] if not x['whole']]
    out.append({'idx':idx,'n_start':len(states),'finish':str(f[0]),'finish_change':str(f[1]),'start':str(s[0]),'start_change':str(s[1]),'tie_x':tie('x2','x3'),'tie_y':tie('y2','y3'),'fails_finished':dict(fails),'fails_start':f0})
json.dump(out,open('signs.json','w'))
print('done',round(time.time()-t0,1))
