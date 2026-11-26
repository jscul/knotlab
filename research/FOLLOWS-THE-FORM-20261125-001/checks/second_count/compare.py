"""The second count: the thread's own probe (ffp.py) against the registered study's outputs, study by study."""
import json, gzip, collections, itertools, sys
import os
A=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','artifacts','FOLLOWS-THE-FORM-20261125-001A','FOLLOWS-THE-FORM-20261125-001A-E001_place_fixed_form_changed')+'/'
mine=[json.loads(l) for l in gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ffp_held.jsonl.gz'),'rt')]
bad=[d for d in mine if 'error' in d]; mine=[d for d in mine if 'error' not in d]
print('my studies',len(mine),'failed or over time',len(bad),[(d['spec']['family'],d['spec']['first'],d['spec']['take'],d['spec']['ration'],d['spec']['treatment'],d['spec']['knot_law'],d['spec']['linked']) for d in bad][:6])
def load(R):
    out={}
    for l in gzip.open(A+'studies_%s.jsonl.gz'%R,'rt'):
        d=json.loads(l); k=d['key']; out[(k[3],k[4],k[5],k[6])]=d
    return out
theirs={('fresh',True,'nae'):load('R2'),('fresh',False,'nae'):load('R2u'),('fresh',True,'parity'):load('R4'),('chains',True,'nae'):load('R3')}
res=collections.defaultdict(collections.Counter)
depth=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for d in mine:
    sp=d['spec']; fam=(sp['family'],sp['linked'],sp['knot_law'])
    t=theirs[fam].get((sp['first'],'none' if sp['take'] is None else 'sole',sp['ration'],sp['treatment']))
    R=res[fam]; R['studies']+=1
    if t is None: R['missing in theirs']+=1; continue
    R['R* same']+= t['R*']==d['R*']
    R['classes among forms same']+= t['n_classes_forms']==d['classes among forms, own']
    R['classes by wider record same']+= t['n_classes_wider']==d['classes among forms, cone']
    # exact partition
    mineP=collections.defaultdict(set)
    for n,c in d['class of each form'].items(): mineP[c].add(n)
    theirP={frozenset(c) for c in t['classes'] if c!=['(none)'] and '(none)' not in c}
    theirP|={frozenset(x for x in c if x!='(none)') for c in t['classes'] if '(none)' in c and len(c)>1}
    R['partition same']+= {frozenset(v) for v in mineP.values()}==theirP
    a=t['after']; p=d['pairs']
    R['after-first-round count same']+= a['of those, the wider record of round 1 the same']==p.get('in round 2 or later, the round-1 record of every birth with a first-seed ancestor the same',0)
    R['round 2 or later count same']+= a['first told apart in round 2 or later']==p.get('in round 2 or later',0)
    pf=t['profile_function']
    R['profile flags same']+= (pf['the held knot'],pf["the second seed's births by round"],pf['both'])==(d['class is a function of the held knot'],d["class is a function of the second seed's births by round"],d['class is a function of both'])
    tf=collections.Counter(t['fates'].values()); mf=collections.Counter({k.replace('ends: no births in the cone','ends, no births').replace('ends: every birth is of both','ends, taken up'):v for k,v in d['fates'].items()})
    R['fates same']+= dict(tf)==dict(mf)
    if fam[1] is False: R['every form in the bare class (mine)']+= (d['classes among forms, own']==1 and not d['bare start alone'])
    if fam==('fresh',True,'nae'):
        kinds={('ends' if k.startswith('ends') else k) for k,v in d['fates'].items() if v>0} & {'ends','steady','grows'}
        R['PN5: two or more fates (mine)']+= len(kinds)>=2
        R['PN2: three or more classes (mine)']+= d['classes among forms, own']>=3
        R['PN7: not a function of the held knot (mine)']+= not d['class is a function of the held knot']; R['PN7: not a function of both (mine)']+= not d['class is a function of both']
    if fam[0]=='chains':
        ch={tuple(int(x) for x in f.split(':')[1].split(',')): c for f,c in d['class of each form'].items()}
        law='%s, %s, %s'%('none' if sp['take'] is None else 'sole',sp['ration'],sp['treatment'])
        for a_ in ch:
            for i in range(len(a_)):
                if a_[i]==2:
                    b=a_[:i]+(3,)+a_[i+1:]
                    if b in ch: c=depth[law]['depth %d'%i]; c[1]+=1; c[0]+=ch[a_]!=ch[b]
            for x in (2,3):
                b=a_+(x,)
                if b in ch: c=depth[law]['%d against %d knots'%(len(a_),len(a_)+1)]; c[1]+=1; c[0]+=ch[a_]!=ch[b]
for fam,R in res.items(): print(fam, dict(R))
t3=json.load(open(A+'tables_R3.json')); k=[x for x in t3 if x.startswith('depth')][0]
same=tot=0
for law,v in t3[k].items():
    for cell,val in v.items():
        tot+=1; same+= list(val)==depth[law][cell]
print('depth cells same',same,'of',tot)
