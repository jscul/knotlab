"""Recount guarded Rule A, and independently test a main-relative start."""
import collections,gzip,json,time
import independent_rules as R
HERE=R.HERE;ROOT=R.ROOT


def entry_state(size,k,calls,G,chosen):
    args=calls[chosen][1];protected=set(args);remaining=R.constraint_data(calls,G,chosen)
    while True:
        degree=collections.Counter(v for vs,_ in remaining for v in vs)
        removable=next((j for j,(vs,full) in enumerate(remaining) if full and any(v>=k and v not in protected and degree[v]==1 for v in vs)),None)
        if removable is None:break
        remaining.pop(removable)
    uf=R.Union(size)
    for vs,_ in remaining:
        for v in vs[1:]:uf.join(vs[0],v)
    roots=[uf.root(v) for v in args]; names={};sigma=tuple(names.setdefault(v,len(names)) for v in roots)
    markedroots={uf.root(v) for v in range(k)};marked=sum((v in markedroots)<<j for j,v in enumerate(roots))
    touched={v for vs,_ in remaining for v in vs};F=sum((v>=k and v not in touched)<<j for j,v in enumerate(args))
    return sigma,marked,F


def run():
    started=time.monotonic();agg={h:{'families':0,'H1_violations':0,'H2_violations':0,'r_within_bound':collections.Counter(),
        'coverage':collections.defaultdict(collections.Counter),'N_acyclic_forgetting':collections.defaultdict(collections.Counter),'table':collections.Counter()}
        for h in ('train','heldout')}
    mains=[];false=[];n=0
    with (HERE/'heldout_fresh.jsonl').open() as f:
        for line in f:
            row=json.loads(line);h=row['half'];d=agg[h];a=row['repaired_A'];dec=row['exact'];forget=dec['verdict']=='certified';cyclic=row['N']['cyclic']
            stratum=row['stratum'];d['families']+=1;d['H1_violations']+=cyclic and forget;d['H2_violations']+=a['certified'] and dec['verdict']=='non-forgetting'
            if a['certified']: d['r_within_bound'][str(forget and dec['r']<=a['bound']).lower()]+=1
            d['coverage'][stratum]['certified']+=forget;d['coverage'][stratum]['by_A']+=a['certified']
            if not cyclic:
                group=stratum.split('/')[0].replace('nonchain','nonchain');d['N_acyclic_forgetting'][group]['n']+=1;d['N_acyclic_forgetting'][group]['forget']+=forget
            d['table']['|'.join((stratum,'N-cyclic' if cyclic else 'N-acyclic','A' if a['certified'] else 'notA',row['recorded_verdict']))]+=1
            raw=json.loads(row['key']);S=row['S'];main=len(raw)-1
            if main==S:continue
            defs,allG,G,size,calls,_=R.prepare(raw,S);msize,mcalls=R.E.flatten(defs,main);entries=[j for j,(c,_) in enumerate(mcalls) if c==S]
            if not entries:continue
            starts=[entry_state(msize,defs[main][0],mcalls,G,j) for j in entries]
            entryA=[]
            for state in starts:
                if not state[1]:entryA.append({'certified':True,'bound':0,'live_states':0})
                else:entryA.append(R.rule_A(size,calls,G,S,protect_F_outputs=True,start=state))
            relative=all(x['certified'] for x in entryA)
            result={'key':row['key'],'half':h,'S':S,'main':main,'entry_starts':starts,'main_relative_A':relative,'generic_A':a['certified'],'exact':dec}
            if relative and not a['certified']:mains.append(result)
            if relative and dec['verdict']=='non-forgetting':false.append(result)
            n+=1
    report=json.loads((ROOT/'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/heldout.json').read_text());mismatches=[]
    for h,d in agg.items():
        for b in d['coverage'].values():b['share']=round(b['by_A']/b['certified'],4)
        d['coverage_total']=round(sum(b['by_A'] for b in d['coverage'].values())/sum(b['certified'] for b in d['coverage'].values()),4)
        for b in d['N_acyclic_forgetting'].values():b['share']=round(b['forget']/b['n'],4)
        for field,value in d.items():
            if value!=report[h][field]:mismatches.append({'half':h,'field':field,'fresh':value,'recorded':report[h][field]})
    result={'guarded_rule_A_aggregate':agg,'mismatches_vs_heldout_json':mismatches,'wrapper_families':n,'main_relative_extra_certificates':len(mains),
            'main_relative_nonforgetting_false_certificates':len(false),'main_relative_nonforgetting_by_half':dict(collections.Counter(x['half'] for x in false)),
            'main_relative_false_examples':false,'all_main_relative_extra_certificates':mains,'seconds':time.monotonic()-started,
            'historical_qualification':'Main-relative initialization is independently reconstructed. No first-version code or list of its eight examples was supplied/read.'}
    (HERE/'guarded_recount_and_starts.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('main_relative_false_examples','all_main_relative_extra_certificates')}))

if __name__=='__main__':run()
