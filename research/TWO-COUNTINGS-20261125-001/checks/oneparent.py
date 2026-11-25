import json, gzip, glob, sys, collections, time
sys.path.insert(0,'.')
from myscore import setting_test, setting_knots
from mykt import test_structure
OP='REPO_ROOT/artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/'
G=[]
for f in sorted(glob.glob(OP+'census_gains_c_*.jsonl.gz')):
    G+=[json.loads(l) for l in gzip.open(f,'rt')]
G1=[r for r in G if r['t']==1]
def parse(s):
    law,rest=s.split('('); return (law, tuple(rest.rstrip(')').split(',')))
KA,KB=setting_knots()
arm=sys.argv[1]
out=[]
t0=time.time()
for i,r in enumerate(G1):
    if r['arm']!=arm: continue
    ks=[parse(k) for k in r['knots']]
    nb=len(r['births'][0])
    pre=[ks[:len(ks)-nb], ks[len(ks)-nb:]]
    rec={'i':i,'tid':r['tid'],'kind':r['kind'],'laws':r.get('laws'),'choice':r.get('choice'),'recorded':r['eval'][3],'part':r['knots'][:len(ks)-nb],'births':r['knots'][len(ks)-nb:]}
    if arm=='uniform' or len(sys.argv)>2:
        f=setting_test(pre,counting='finish'); s=setting_test(pre,counting='start',s=0); s1=setting_test(pre,counting='start',s=1)
        rec.update(finish=str(f[0]), finish_change=str(f[1]), start=str(s[0]), start_change=str(s[1]), stage1=str(s1[0]), stage1_change=str(s1[1]), totals={str(k):v for k,v in f[2].items()})
    fails={}
    for a in (0,1):
        for b in (0,1):
            T=test_structure(ks+[KA[a],KB[b]])
            fails['%d%d'%(a,b)]=[x['rule']+':'+''.join(k for k in ('K1','K2','K3') if not x[k])+':'+','.join(x['induced']) for x in T['rules'] if not x['whole']]
    # knot test of the part and of the part + round too
    fails['part']=[x['rule'] for x in test_structure(pre[0])['rules'] if not x['whole']]
    fails['part+round']=[x['rule'] for x in test_structure(ks)['rules'] if not x['whole']]
    rec['fails']=fails
    out.append(rec)
json.dump(out,open('oneparent_%s%s.json'%(arm,'_scored' if len(sys.argv)>2 else ''),'w'),indent=1)
print(arm,len(out),round(time.time()-t0,1))
