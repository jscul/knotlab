"""Offline independent TIE-CYCLE referee: fresh ties and idempotent labels.

Only permitted earlier referee engines supply block semantics, SAT projection,
and exact nonrectangular-product decisions. This file supplies the new tie,
closure, core, label, parity, split and chain computations from the prose.
No current study Python is read/imported. Outputs are confined beside this file.
"""
from __future__ import annotations
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse, collections, gzip, hashlib, importlib.util, itertools, json, resource, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FORBIDDEN = ROOT/'experiments/TIE-CYCLE-20261114-001A'
OPENED = set()
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str,bytes)):
        p = Path(os.fsdecode(args[0])).absolute()
        if p.is_relative_to(FORBIDDEN) and p.suffix != '.json':
            raise RuntimeError('Forbidden study implementation read: '+str(p))
        if p.is_relative_to(ROOT): OPENED.add(str(p.relative_to(ROOT)))
sys.addaudithook(audit)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
R=module('permitted_rules',ROOT/'research/FORGET-RULE-20261114-001/referee-R1/codex/independent_rules.py')
E=R.E
SOURCE=E.RESULTS
CENSUS=E.CENSUS
PRIOR=ROOT/'research/FORGET-RULE-20261114-001/referee-R1/codex/heldout_fresh.jsonl'
STUDY=FORBIDDEN/'TIE-CYCLE-20261114-001A-E001_ties/heldout.json'
ALL=(1<<64)-1

def bitpar(x,mask): return (x&mask).bit_count()&1
EQ={(a,b):sum(1<<(8*x+y) for x in range(8) for y in range(8) if bitpar(x,a)==bitpar(y,b))
    for a in range(1,8) for b in range(1,8)}

def parity_ties(rel, pairs):
    if not rel: return []
    out=[]
    dom=[x for x in range(8) if (rel>>(8*x))&255]
    for a,b in pairs:
        # A constant at an endpoint is not a transported open label.
        if len({bitpar(x,a) for x in dom})!=2: continue
        equal=EQ[a,b]
        if rel&~equal==0: out.append([a,b,0])
        elif rel&equal==0: out.append([a,b,1])
    return out
COORD=[(1<<a,1<<b) for a in range(3) for b in range(3)]
SELFCOORD=[(1<<a,1<<a) for a in range(3)]
SELF_PARITY=[(a,a) for a in range(1,8) if a.bit_count()>1]
ALL_PARITY=[(a,b) for a in range(1,8) for b in range(1,8)]

def selftie(rel):
    # Complement closure makes the openness check automatic on these inputs.
    if not rel: return None
    for a,b in SELFCOORD:
        equal=EQ[a,b]
        if rel&~equal==0: return [a,b,0]
        if rel&equal==0: return [a,b,1]
    return None

def compose(a,b):
    rows=[(b>>(8*y))&255 for y in range(8)]
    out=0
    for x in range(8):
        row=(a>>(8*x))&255; image=0
        while row:
            low=row&-row; image|=rows[low.bit_length()-1]; row^=low
        out|=image<<(8*x)
    return out

def word_value(gens,word):
    value=E.identity(8)
    for i in word: value=compose(value,gens[i])
    return value

def idempotent_power(rel):
    value=rel; exponent=1; seen=set()
    while True:
        if compose(value,value)==value: return value,exponent
        assert value not in seen, 'finite cyclic semigroup should contain an idempotent'
        seen.add(value); value=compose(value,rel); exponent+=1

def occurrence_counts(raw):
    result=[]
    for i,(_,_,calls) in enumerate(raw):
        c=collections.Counter()
        for callee,_ in calls:
            if callee=='SELF': c[i]+=1
            elif isinstance(callee,int):
                assert 0<=callee<i; c.update(result[callee])
            else: assert callee=='K'
        result.append(c)
    return result

def identity_word(calls,S):
    arcs=collections.defaultdict(list)
    chosen=[args for callee,args in calls if callee==S]
    for label,args in enumerate(chosen):
        for end,start in enumerate(args):
            if start<3: arcs[start].append((end,label))
    for start in range(3):
        queue=collections.deque([(start,[])])
        seen={start}
        while queue:
            v,word=queue.popleft()
            for end,label in arcs[v]:
                if end==start: return word+[label]
                if end not in seen: seen.add(end); queue.append((end,word+[label]))
    return None

def closure_without_selfties(gens,cap=250000):
    """All nonrectangular products, or a positive self-tie witness.

    Rectangles may be discarded: the ideal property ensures no extension can
    become nonrectangular or acquire a nonconstant tie or parity.
    """
    apply=E.composition_machine(gens)
    words={}; queue=collections.deque()
    for i,g in enumerate(gens):
        if E.rectangular(g): continue
        if g not in words: words[g]=[i]; queue.append(g)
    parity=[]
    while queue:
        rel=queue.popleft()
        tie=selftie(rel)
        if tie: return {'tie':True,'word':words[rel],'tie_label':tie,'product':hex(rel),'complete':False,'seen':len(words)},None
        if not parity:
            labels=parity_ties(rel,SELF_PARITY)
            if labels: parity=[{'word':words[rel],'product':hex(rel),'labels':labels}]
        for i in range(len(gens)):
            p=apply(rel,i)
            if E.rectangular(p) or p in words: continue
            if len(words)>=cap:
                return {'tie':None,'complete':False,'seen':len(words),'reason':'referee nonrectangular closure cap','parity_witnesses':parity},None
            words[p]=words[rel]+[i]; queue.append(p)
    return {'tie':False,'complete':True,'seen':len(words),'parity_witnesses':parity},words

def classify_idempotent(rel):
    assert rel and compose(rel,rel)==rel and not E.rectangular(rel)
    core=[x for x in range(8) if (rel>>(8*x+x))&1]
    classes=[]; assigned=set()
    for x in core:
        if x in assigned: continue
        cl=[y for y in core if ((rel>>(8*x+y))&1) and ((rel>>(8*y+x))&1)]
        assigned.update(cl); classes.append(cl)
    one_way=[]
    for i,A in enumerate(classes):
        for j,B in enumerate(classes):
            if i!=j and (rel>>(8*A[0]+B[0]))&1:
                assert not (rel>>(8*B[0]+A[0]))&1
                one_way.append([i,j])
    # Exact conserved labels f(start)=g(end) are the components of the
    # bipartite incidence relation, with start/end treated as separate roles.
    uf=R.Union(16); dom=[]; ran=set()
    for x in range(8):
        row=(rel>>(8*x))&255
        if row: dom.append(x)
        for y in range(8):
            if (row>>y)&1: uf.join(x,8+y); ran.add(y)
    groups=collections.defaultdict(lambda:{'start':[],'end':[]})
    for x in dom: groups[uf.root(x)]['start'].append(x)
    for y in sorted(ran): groups[uf.root(8+y)]['end'].append(y)
    label_classes=list(groups.values())
    ties=parity_ties(rel,COORD)
    parities=parity_ties(rel,ALL_PARITY)
    label_type='tie' if ties else 'parity' if parities else 'nonlinear label' if len(label_classes)>1 else None
    # This recreates the written any-comparable-core-classes rule, while the
    # independent strict type additionally checks "no quantity is conserved".
    core_rel=sum(1<<(8*x+y) for x in core for y in core if (rel>>(8*x+y))&1)
    core_ties=parity_ties(core_rel,COORD)
    core_parities=parity_ties(core_rel,ALL_PARITY)
    core_label_type='tie' if len(classes)==2 and core_ties else 'parity' if len(classes)==2 and core_parities else 'nonlinear label'
    study_type='order' if one_way else core_label_type
    strict_type=(('mixed label/order' if len(label_classes)>1 else 'order') if one_way else label_type) or 'no conserved label and no core order'
    assert len(classes)>=2
    # For the prose 'top class <= deep class', test unique endpoint maps to
    # the core quotient. A start must have a principal upward class set, and
    # an end a principal downward class set. Some transient endpoints fail.
    at={x:i for i,cl in enumerate(classes) for x in cl}
    up=[{at[y] for y in core if (rel>>(8*cl[0]+y))&1} for cl in classes]
    down=[{at[x] for x in core if (rel>>(8*x+cl[0]))&1} for cl in classes]
    start_map={}; end_map={}
    for x in dom:
        reach={at[y] for y in core if (rel>>(8*x+y))&1}
        hits=[j for j,U in enumerate(up) if U==reach]
        if len(hits)==1: start_map[x]=hits[0]
    for y in ran:
        reach={at[x] for x in core if (rel>>(8*x+y))&1}
        hits=[j for j,D in enumerate(down) if D==reach]
        if len(hits)==1: end_map[y]=hits[0]
    endpoint_order_exact=len(start_map)==len(dom) and len(end_map)==len(ran)
    if endpoint_order_exact:
        assert all(bool((rel>>(8*x+y))&1)==((classes[start_map[x]][0],classes[end_map[y]][0]) in E.pairs(rel,8))
                   for x in dom for y in ran)
    return {'product':hex(rel),'core':core,'core_classes':classes,'one_way_class_pairs':one_way,
            'unique_core_endpoint_maps':endpoint_order_exact,'start_class_map':start_map,'end_class_map':end_map,
            'conserved_label_classes':label_classes,'nonconstant_label':len(label_classes)>1,
            'coordinate_ties':ties,'linear_labels':parities,'core_coordinate_ties':core_ties,'core_linear_labels':core_parities,
            'study_type':study_type,'strict_type':strict_type}

def load():
    source={r['case']:r['result'] for r in map(json.loads,SOURCE.open())}
    census={}
    with gzip.open(CENSUS,'rt') as f:
        for line in f:
            r=json.loads(line)
            if r['class']=='grows' and r['ray']=='first': census[r['key']]=r
    prior={r['key']:r for r in map(json.loads,PRIOR.open())}
    assert set(source)==set(census)==set(prior) and len(source)==12772
    return source,census,prior

def controls():
    inherited=E.controls()
    checked=0
    for a in range(256):
        for b in (0,1,3,7,19,126,255):
            # Embed all 2x2 relations independently for cross-checking compose.
            p=sum(1<<(8*x+y) for x,y in E.pairs(a&15,2))
            q=sum(1<<(8*x+y) for x,y in E.pairs(b&15,2))
            want=sum(1<<(8*x+y) for x,y in E.pairs(E.compose_sets(a&15,b&15,2),2))
            assert compose(p,q)==want; checked+=1
    identity=E.identity(8); full=ALL
    opposite=sum(1<<(8*x+(x^7)) for x in range(8))
    assert len(parity_ties(identity,SELFCOORD))==3
    assert len(parity_ties(opposite,SELFCOORD))==3
    assert not parity_ties(full,ALL_PARITY) and not parity_ties(0,ALL_PARITY)
    # A two-bit self-parity preserves a nonconstant parity but no coordinate.
    parity=EQ[3,3]
    assert not selftie(parity) and parity_ties(parity,SELF_PARITY)
    z=classify_idempotent(parity); assert z['strict_type']=='parity'
    # Total two-class order: at most the starting class may be followed.
    order=sum(1<<(8*x+y) for x in range(8) for y in range(8) if (x&1)<=(y&1))
    z=classify_idempotent(order); assert z['strict_type']=='order' and not z['nonconstant_label']
    # Comparable classes plus an independent conserved bit: not a pure order.
    mixed=sum(1<<(8*x+y) for x in range(8) for y in range(8) if (x&1)==(y&1) and ((x>>1)&1)<=((y>>1)&1))
    z=classify_idempotent(mixed); assert z['study_type']=='order' and z['strict_type']=='mixed label/order'
    ds=[[3,0,[['SELF',[0,1,2]]]],[3,0,[[0,[0,1,2]],[0,[0,1,2]]]]]
    assert occurrence_counts(ds)[-1]=={0:2}
    return {'passed':True,'inherited':inherited,'fresh_embedded_compositions':checked,
            'positive_negative_controls':['identity','opposite','full','empty','tie-free parity','pure order','order plus conserved label','duplicate calls counted twice']}

def run(limit=None):
    start=time.monotonic(); source,census,prior=load(); control=controls()
    stats=collections.defaultdict(collections.Counter); errors=[]; residual=[]; positive=[]; capped=[]
    output=HERE/('smoke_families.jsonl' if limit else 'families_fresh.jsonl')
    count=0; relations=0
    with output.open('w') as f:
        for key,recorded in source.items():
            if limit and count>=limit: break
            raw=json.loads(key); S=census[key]['S']; defs,allG,G,size,calls,_=R.prepare(raw,S)
            occ=occurrence_counts(raw); chain=occ[S]=={S:1} and occ[-1]=={S:1}
            _,main_calls=E.flatten(defs,len(defs)-1)
            chain2=collections.Counter(c for c,_ in calls if c!='K')=={S:1} and collections.Counter(c for c,_ in main_calls if c!='K')=={S:1}
            assert chain==chain2==recorded['chain']
            half='train' if int(hashlib.sha256(('TIE:'+key).encode()).hexdigest()[:8],16)%2==0 else 'heldout'
            oldhalf='train' if int(hashlib.sha256(key.encode()).hexdigest()[:8],16)%2==0 else 'heldout'
            selected=[j for j,(c,_) in enumerate(calls) if c==S]
            gens=[E.derive_R(size,calls,G,j)[0] for j in selected]; relations+=len(gens)
            assert all(g and all(bool((g>>(8*x+y))&1)==bool((g>>(8*(x^7)+(y^7)))&1) for x in range(8) for y in range(8)) for g in gens)
            assert G[S] and all(any((g>>(8*x+y))&1 for y in G[S]) for g in gens for x in G[S]), 'living support must realize every word/power'
            if list(map(hex,gens))!=[hex(int(p,16)) for p in recorded['R_i']]: errors.append({'key':key,'kind':'R_i'})
            if list(map(hex,gens))!=prior[key]['R_i']: errors.append({'key':key,'kind':'previous R_i'})
            exact=E.graph_decision(gens)
            assert exact['verdict']!='capped'
            if exact['verdict']!=prior[key]['exact']['verdict'] or exact['r']!=prior[key]['exact']['r']: errors.append({'key':key,'kind':'prior exact'})
            if recorded['verdict']!='capped' and (exact['verdict']!=recorded['verdict'] or exact['r']!=recorded['r']): errors.append({'key':key,'kind':'census exact'})
            iw=identity_word(calls,S)
            if iw is not None:
                p=word_value(gens,iw); tie=selftie(p); assert tie
                tie_info={'tie':True,'word':iw,'tie_label':tie,'product':hex(p),'method':'raw identity cycle'}; closure=None
            else:
                tie_info,closure=closure_without_selfties(gens)
                assert tie_info['tie'] is not None
            forget=exact['verdict']=='certified'
            idem_witness=None
            if not forget:
                cw=exact['lasso']['cycle']; cp=word_value(gens,cw); ep,exponent=idempotent_power(cp)
                assert not E.rectangular(ep)
                idem_witness={'cycle_word':cw,'exponent':exponent,'product':hex(ep)}
            if tie_info['tie']:
                w=tie_info['word']; p=word_value(gens,w); assert selftie(p)
                power,exponent=idempotent_power(p); assert selftie(power) and not E.rectangular(power)
                assert not forget
                if iw is None: positive.append({'key':key,'half':half,'S':S,'calls':calls,'R_i':list(map(hex,gens)),'tie':tie_info})
            idem_rows=[]
            if not tie_info['tie'] and not forget:
                assert closure is not None
                for p,word in closure.items():
                    if compose(p,p)==p:
                        row=classify_idempotent(p); row['word']=word; idem_rows.append(row)
                assert idem_rows
                row={'key':key,'half':half,'S':S,'chain':chain,'closure_nonrectangular_products':len(closure),'idempotents':idem_rows,
                     'study_types':sorted({z['study_type'] for z in idem_rows}),'strict_types':sorted({z['strict_type'] for z in idem_rows}),
                     'parity_cycle':bool(tie_info.get('parity_witnesses')),'parity_witnesses':tie_info.get('parity_witnesses',[])}
                residual.append(row)
            d=stats[half]; d['families']+=1; d['chain' if chain else 'nonchain']+=1
            d['1def' if len(raw)==1 else 'multi']+=1
            d['forgetting' if forget else 'nonforgetting']+=1
            d['identity_cycle']+=iw is not None
            d['tie_cycle']+=bool(tie_info['tie']); d['tie_beyond_identity']+=bool(tie_info['tie']) and iw is None
            if tie_info['tie']: d['tie_and_forget']+=forget
            else:
                group='chain' if chain else 'nonchain'; d['no_tie_'+group]+=1; d['no_tie_'+group+'_forget']+=forget
            if chain:
                d['chain_'+('1def' if len(raw)==1 else 'multi')]+=1
                d['chain_wrapper']+=S!=len(raw)-1
            if recorded['verdict']=='capped':
                d['census_capped']+=1; d['census_capped_tie']+=bool(tie_info['tie'])
                capped.append({'key':key,'half':half,'tie':tie_info['tie'],'exact':exact,'idempotent':idem_witness})
            if chain and oldhalf=='heldout' and iw is None: stats['old_split']['N_acyclic_chains_heldout']+=1; stats['old_split']['forget']+=forget
            if chain: stats['split_overlap'][oldhalf+'|'+half]+=1
            record={'key':key,'key_sha256':hashlib.sha256(key.encode()).hexdigest(),'S':S,'half':half,'old_half':oldhalf,
                    'chain':chain,'n_defs':len(raw),'wrapper':S!=len(raw)-1,'G_S':hex(E.mask(G[S])),'R_i':list(map(hex,gens)),
                    'identity_cycle':iw is not None,'tie':tie_info,'exact':exact,'nonrectangular_idempotent':idem_witness,
                    'census_verdict':recorded['verdict']}
            f.write(json.dumps(record,separators=(',',':'))+'\n'); count+=1
            if count%1000==0: f.flush(); print(json.dumps({'families':count,'relations':relations,'seconds':round(time.monotonic()-start,2),'residual':len(residual)}),flush=True)
    summary={'complete':count==12772,'families':count,'relations_fresh':relations,'seconds':round(time.monotonic()-start,3),
             'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'stats':dict(stats),'errors':errors,'controls':control,
             'residual_families':len(residual),'every_nonforgetting_has_verified_nonrectangular_idempotent':True,
             'opened_repository_files':sorted(OPENED),'forbidden_study_python_opened':False}
    stem='smoke_' if limit else ''
    (HERE/(stem+'residual_idempotents.json')).write_text(json.dumps(residual,indent=2)+'\n')
    (HERE/(stem+'ties_beyond_identity.json')).write_text(json.dumps(positive,indent=2)+'\n')
    (HERE/(stem+'capped_decisions.json')).write_text(json.dumps(capped,indent=2)+'\n')
    (HERE/(stem+'recomputation.json')).write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('controls','opened_repository_files')}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--limit',type=int); args=parser.parse_args(); run(args.limit)
