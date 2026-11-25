import json, time, sys
sys.path.insert(0,'.')
from myscore import setting_test
S=json.load(open('REPO_ROOT/research/TWO-COUNTINGS-20261125-001A/structures.json'))
S={k:[(l,tuple(p)) for l,p in v] for k,v in S.items()}
def run(name, pre, **kw):
    t=time.time()
    f=setting_test(pre, counting='finish', **kw)
    st=setting_test(pre, counting='start', s=0, **kw)
    out=[name,'finish',str(f[0]),'change',str(f[1]),'start',str(st[0]),'change',str(st[1]), 'kept', {k:str(v) for k,v in st[2].items()}]
    if len(pre)>1:
        s1=setting_test(pre, counting='start', s=1, **kw); out+=['stage1',str(s1[0]),str(s1[1])]
    print(out, round(time.time()-t,1), flush=True)
for oa in [('x2','x3'),('x2','c'),('x3','c')]:
    for ob in [('y2','y3'),('y2','t'),('y3','t')]:
        run('eleven %s/%s'%(oa,ob), [S['eleven (start)']], optA=oa, optB=ob)
part=S['smallest gain: part']; rnd=S['smallest gain: part + rule-Q round 1']
run('smallest gain', [part, [k for k in rnd if k not in part]])
for k in ['seven (start)','eight (start)','nine, the pencil (start)']:
    run(k,[S[k]])
