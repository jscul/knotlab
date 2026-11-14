"""Second-method exact validation and evidence summary; no producer imports.

Finite relations here are Python sets of ordered pairs. Every residual closure
is independently regenerated. All binary endpoint functions are enumerated to
validate whether *any* nonconstant quantity can be conserved. The source study
report is read as JSON only, after independent outputs have been produced.
"""
from __future__ import annotations
import collections, hashlib, itertools, json, resource, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STUDY=ROOT/'experiments/TIE-CYCLE-20261114-001A/TIE-CYCLE-20261114-001A-E001_ties/heldout.json'

def pairs(h):
    n=int(h,16) if isinstance(h,str) else h
    return frozenset((a,b) for a in range(8) for b in range(8) if (n>>(8*a+b))&1)

def multiply(A,B):
    return frozenset((a,c) for a,b in A for bb,c in B if b==bb)

def rect(A):
    return A==frozenset(itertools.product({a for a,b in A},{b for a,b in A}))

def value(gens,word):
    out=frozenset((x,x) for x in range(8))
    for k in word: out=multiply(out,gens[k])
    return out

def endpoint_labels(A):
    """Enumerate every Boolean f on the start states; derive g if possible.

    Any nonconstant label with any finite codomain yields a nonconstant binary
    coarsening. Thus absence here excludes all nonconstant carried quantities
    f(start)=g(end), rather than just ties and linear parities.
    """
    active={a for a,b in A}; answers=[]
    for f in range(256):
        if len({(f>>a)&1 for a in active})!=2: continue
        g={}; good=True
        for a,b in A:
            bit=(f>>a)&1
            if b in g and g[b]!=bit: good=False; break
            g[b]=bit
        if good: answers.append({'start_truth_table':f,'end_values':g})
    return answers

def bit_labels(A,self_only=False,parity=False):
    masks=range(1,8) if parity else (1,2,4)
    out=[]
    for p in masks:
        for q in masks:
            if self_only and p!=q: continue
            vals={(a&p).bit_count()%2 ^ (b&q).bit_count()%2 for a,b in A}
            if len(vals)==1 and len({(a&p).bit_count()%2 for a,b in A})==2:
                out.append([p,q,next(iter(vals))])
    return out

def core_info(A):
    core={a for a,b in A if a==b}; unseen=set(core); classes=[]
    while unseen:
        a=min(unseen)
        cl={b for b in core if (a,b) in A and (b,a) in A}
        classes.append(sorted(cl)); unseen-=cl
    comp=[[i,j] for i,X in enumerate(classes) for j,Y in enumerate(classes) if i!=j and (X[0],Y[0]) in A]
    return sorted(core),classes,comp

def controls():
    # A wrong alleged self-tie is rejected; a wrong idempotent is rejected.
    full=frozenset(itertools.product(range(8),repeat=2))
    assert not bit_labels(full,True)
    step=frozenset({(0,1),(7,6)})
    assert bit_labels(step,True) and not multiply(step,step) and multiply(step,step)!=step
    # The literal core-label inference fails even with a living support.
    bridge=frozenset({(0,0),(7,7),(0,1),(0,6),(7,1),(7,6)})
    assert multiply(bridge,bridge)==bridge
    assert len(core_info(bridge)[1])==2 and not endpoint_labels(bridge)
    return {'passed':True,'wrong_self_tie_rejected':True,'wrong_idempotent_rejected':True,
            'empty_power_exposes_missing_living_hypothesis':True,'antichain_core_does_not_guarantee_global_label':True}

def main():
    start=time.monotonic(); controls_result=controls()
    rows=[json.loads(l) for l in (HERE/'families_fresh.jsonl').open()]
    bykey={r['key']:r for r in rows}
    residual=json.loads((HERE/'residual_idempotents.json').read_text())
    study=json.loads(STUDY.read_text())
    checks=collections.Counter(); differences=[]; cases=[]
    aggregates={}
    for r in rows:
        gs=[pairs(h) for h in r['R_i']]
        live={x for x in range(8) if (int(r['G_S'],16)>>x)&1}
        assert live and all(all(any((x,y) in g for y in live) for x in live) for g in gs)
        assert all(all(((x^7,y^7) in g) for x,y in g) for g in gs)
        checks['families_with_verified_common_serial_living_support']+=1
        if r['nonrectangular_idempotent']:
            w=r['nonrectangular_idempotent']; cp=value(gs,w['cycle_word']); p=frozenset((x,x) for x in range(8))
            for _ in range(w['exponent']): p=multiply(p,cp)
            assert p==pairs(w['product']) and multiply(p,p)==p and not rect(p)
            checks['all_nonforgetting_idempotent_witnesses']+=1
        if r['tie']['tie']:
            p=value(gs,r['tie']['word'])
            assert p==pairs(r['tie']['product']) and bit_labels(p,True)
            checks['all_positive_tie_witnesses']+=1
    for r in residual:
        gs=[pairs(h) for h in bykey[r['key']]['R_i']]
        seen=set(g for g in gs if not rect(g)); todo=list(seen)
        while todo:
            p=todo.pop()
            assert not bit_labels(p,True)
            for g in gs:
                q=multiply(p,g)
                if not rect(q) and q not in seen: seen.add(q); todo.append(q)
        assert len(seen)==r['closure_nonrectangular_products']
        expected={p for p in seen if multiply(p,p)==p}
        assert expected=={pairs(i['product']) for i in r['idempotents']}
        checks['independently_regenerated_residual_closures']+=1
        checks['nonrectangular_products_in_residual_closures']+=len(seen)
        allpar=any(any(p==q and p.bit_count()>1 for p,q,s in bit_labels(A,True,True)) for A in seen)
        assert allpar==r['parity_cycle']
        for i in r['idempotents']:
            A=pairs(i['product']); assert value(gs,i['word'])==A
            core,classes,comp=core_info(A)
            assert (core,classes,comp)==(i['core'],i['core_classes'],i['one_way_class_pairs'])
            if i['unique_core_endpoint_maps']:
                sm={int(k):v for k,v in i['start_class_map'].items()}
                em={int(k):v for k,v in i['end_class_map'].items()}
                assert set(sm)=={a for a,b in A} and set(em)=={b for a,b in A}
                assert all(((a,b) in A)==((classes[sm[a]][0],classes[em[b]][0]) in A) for a in sm for b in em)
            checks['idempotents_with_unique_endpoint_core_classes']+=i['unique_core_endpoint_maps']
            labels=endpoint_labels(A)
            assert bool(labels)==i['nonconstant_label']
            assert sorted(bit_labels(A))==sorted(i['coordinate_ties'])
            assert sorted(bit_labels(A,False,True))==sorted(i['linear_labels'])
            checks['every_residual_idempotent_and_all_Boolean_endpoint_labels']+=1
            if i['strict_type']!='order':
                cases.append({'key':r['key'],'key_sha256':hashlib.sha256(r['key'].encode()).hexdigest(),
                              'half':r['half'],'product':i['product'],'word':i['word'],'study_type':i['study_type'],
                              'strict_type':i['strict_type'],'coordinate_ties':i['coordinate_ties'],
                              'linear_labels':i['linear_labels'],'nonconstant_boolean_labels':labels,
                              'core':core,'core_classes':classes,'one_way_class_pairs':comp})
    for half in ('train','heldout'):
        group=[r for r in rows if r['half']==half]; res=[r for r in residual if r['half']==half]
        d={'families':len(group),'decided_independently':len(group),
           'no_tie':{s:{'n':sum(not r['tie']['tie'] and r['chain']==(s=='chain') for r in group),
                         'forget':sum(not r['tie']['tie'] and r['chain']==(s=='chain') and r['exact']['verdict']=='certified' for r in group)}
                     for s in ('chain','nonchain')},
           'tie_families':sum(r['tie']['tie'] for r in group),
           'identity_cycle_families':sum(r['identity_cycle'] for r in group),
           'ties_beyond_identity':sum(r['tie']['tie'] and not r['identity_cycle'] for r in group),
           'residual':len(res),'residual_order_only_core_proxy':sum(r['study_types']==['order'] for r in res),
           'residual_order_only_no_conserved_value':sum(r['strict_types']==['order'] for r in res),
           'residual_order_only_unique_core_endpoint_classes':sum(r['strict_types']==['order'] and all(i['unique_core_endpoint_maps'] for i in r['idempotents']) for r in res),
           'residual_core_proxy_types':dict(collections.Counter('|'.join(r['study_types']) for r in res)),
           'residual_endpoint_types':dict(collections.Counter('|'.join(r['strict_types']) for r in res)),
           'parity_without_coordinate_self_tie':sum(r['parity_cycle'] for r in res),
           'census_capped_tied':sum(r['census_verdict']=='capped' and r['tie']['tie'] for r in group),
           'census_capped_identity_cycle':sum(r['census_verdict']=='capped' and r['identity_cycle'] for r in group),
           'chains':sum(r['chain'] for r in group),
           'chain_single_definition':sum(r['chain'] and r['n_defs']==1 for r in group),
           'chain_multiple_definitions':sum(r['chain'] and r['n_defs']>1 for r in group),
           'chain_wrappers':sum(r['chain'] and r['wrapper'] for r in group)}
        aggregates[half]=d
        for name,fresh,recorded in [
            ('families',d['families'],study[half]['families']),
            ('chain_no_tie_n',d['no_tie']['chain']['n'],study[half]['no_tie']['chain']['n']),
            ('chain_no_tie_forget',d['no_tie']['chain']['forget'],study[half]['no_tie']['chain']['forget']),
            ('nonchain_no_tie_n',d['no_tie']['nonchain']['n'],study[half]['no_tie']['nonchain']['n']),
            ('nonchain_no_tie_forget',d['no_tie']['nonchain']['forget'],study[half]['no_tie']['nonchain']['forget']),
            ('residual',d['residual'],study[half]['residual']),
            ('core_proxy_order_only',d['residual_order_only_core_proxy'],study[half]['residual_order_only']),
            ('core_proxy_types',d['residual_core_proxy_types'],study[half]['residual_types']),
            ('parity_without_tie',d['parity_without_coordinate_self_tie'],study[half]['parity_without_tie']),
            ('all_capped_tied',d['census_capped_tied'],study[half]['capped_settled_by_tie']),
            ('strict_order_only',d['residual_order_only_no_conserved_value'],study[half]['residual_order_only'])]:
            if fresh!=recorded: differences.append({'half':half,'field':name,'independent':fresh,'study':recorded})
    out={'complete':len(rows)==12772,'checks':dict(checks),'controls':controls_result,
         'aggregates':aggregates,'differences_from_study':differences,
         'definitions':{'core_proxy':'Every nonrectangular idempotent has some comparable distinct core classes.',
                        'no_conserved_value':'Core proxy plus no nonconstant f(start)=g(end) on the full active endpoint supports.',
                        'unique_core_endpoint_classes':'Additionally every active endpoint has a unique principal class in the core quotient, separately for the start and end roles; this is a stronger literal reading, not the published core-only definition.'},
         'seconds':round(time.monotonic()-start,3),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE/'classification_counterexamples.json').write_text(json.dumps(cases,indent=2)+'\n')
    (HERE/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)

if __name__=='__main__': main()
