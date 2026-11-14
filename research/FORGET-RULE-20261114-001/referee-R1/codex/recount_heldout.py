"""Fresh rules and exact decisions on all 12,772 eligible census families."""
import collections,gzip,hashlib,json,time
import independent_rules as R
HERE=R.HERE; ROOT=R.ROOT
SOURCE=ROOT/'experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl'
CENSUS=ROOT/'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
REPORT=ROOT/'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/heldout.json'


def run():
    start=time.monotonic(); source={}
    with SOURCE.open() as f:
        for line in f:
            row=json.loads(line); source[row['case']]=row['result']
    census={}
    with gzip.open(CENSUS,'rt') as f:
        for line in f:
            row=json.loads(line)
            if row['key'] in source: census[row['key']]=row
    assert len(source)==len(census)==12772
    aggregate={name:{'families':0,'H1_violations':0,'H2_violations':0,'H2_bound_violations':0,'r_within_bound':0,
                     'coverage':collections.defaultdict(collections.Counter),'table':collections.Counter(),
                     'N_acyclic_forgetting':collections.defaultdict(collections.Counter),'repaired_A':0,'literal_vs_repaired_disagreements':0,
                     'fresh_exact_verdicts':collections.Counter(),'recorded_verdicts':collections.Counter()}
               for name in ('train','heldout')}
    mismatches=[]; special=[]; rows=0; fullR=0; output=HERE/'heldout_fresh.jsonl'; capped=[]
    with output.open('w') as f:
        for key,recorded in source.items():
            raw=json.loads(key); S=census[key]['S']; defs,allG,G,size,calls,_=R.prepare(raw,S)
            msize,mcalls=R.E.flatten(defs,len(defs)-1)
            chain=collections.Counter(c for c,_ in calls if c!='K')=={S:1} and collections.Counter(c for c,_ in mcalls if c!='K')=={S:1}
            stratum=('chain' if chain else 'nonchain')+('/1def' if len(defs)==1 else '/multi')
            half='train' if int(hashlib.sha256(key.encode()).hexdigest()[:8],16)%2==0 else 'heldout'
            a=R.rule_A(size,calls,G,S); fixed=R.rule_A(size,calls,G,S,protect_F_outputs=True); n=R.rule_N(calls,S)
            matrices,decision=R.exact(size,calls,G,S,max_states=250000); fullR+=len(matrices)
            errors=[]
            if list(map(hex,matrices))!=[hex(int(v,16)) for v in recorded['R_i']]: errors.append('R_i')
            if chain!=recorded['chain']: errors.append('chain')
            if recorded['verdict']!='capped' and (decision['verdict']!=recorded['verdict'] or decision['r']!=recorded['r']): errors.append('exact')
            if not allG[-1]: errors.append('unexpected dead limit')
            if errors: mismatches.append({'key':key,'errors':errors,'fresh':decision,'recorded':recorded})
            d=aggregate[half]; d['families']+=1; d['fresh_exact_verdicts'][decision['verdict']]+=1; d['recorded_verdicts'][recorded['verdict']]+=1
            forget=decision['verdict']=='certified'; known=decision['verdict']!='capped'
            d['H1_violations']+=n['cyclic'] and forget; d['H2_violations']+=a['certified'] and known and not forget
            d['H2_bound_violations']+=a['certified'] and forget and decision['r']>a['bound']
            d['r_within_bound']+=a['certified'] and forget and decision['r']<=a['bound']
            d['coverage'][stratum]['certified']+=forget; d['coverage'][stratum]['by_A']+=a['certified']
            d['repaired_A']+=fixed['certified']; d['literal_vs_repaired_disagreements']+=a['certified']!=fixed['certified'] or a['bound']!=fixed['bound']
            if not n['cyclic']:
                group='chain' if chain else 'nonchain'; d['N_acyclic_forgetting'][group]['n']+=1;d['N_acyclic_forgetting'][group]['forget']+=forget
            d['table']['|'.join((stratum,'N-cyclic' if n['cyclic'] else 'N-acyclic','A' if a['certified'] else 'notA',recorded['verdict']))]+=1
            row={'key':key,'half':half,'S':S,'stratum':stratum,'A':a,'repaired_A':fixed,'N':n,'R_i':list(map(hex,matrices)),
                 'exact':decision,'recorded_verdict':recorded['verdict'],'mismatches':errors}
            f.write(json.dumps(row)+'\n'); rows+=1
            if recorded['verdict']=='capped': capped.append({'key':key,'fresh':decision})
            if a['certified'] and (not forget or decision['r']>a['bound']): special.append(row)
            if rows%500==0:
                f.flush(); print(json.dumps({'completed':rows,'R_i':fullR,'seconds':round(time.monotonic()-start,2),'mismatches':len(mismatches)}),flush=True)
            if time.monotonic()-start>820:
                print('explicit 820-second command gate reached',flush=True); break
    for half,d in aggregate.items():
        for bucket in d['coverage'].values(): bucket['share']=round(bucket['by_A']/bucket['certified'],4) if bucket['certified'] else None
        d['coverage_total']=round(sum(b['by_A'] for b in d['coverage'].values())/sum(b['certified'] for b in d['coverage'].values()),4)
        for group in d['N_acyclic_forgetting'].values(): group['share']=round(group['forget']/group['n'],4)
    recorded_report=json.loads(REPORT.read_text()); comparisons=[]
    for half in ('train','heldout'):
        for field in ('families','H1_violations','H2_violations','coverage','coverage_total','N_acyclic_forgetting','table'):
            if aggregate[half][field]!=recorded_report[half][field]: comparisons.append({'half':half,'field':field,'fresh':aggregate[half][field],'recorded':recorded_report[half][field]})
    result={'complete':rows==12772,'families':rows,'R_i_fresh':fullR,'seconds':round(time.monotonic()-start,4),'aggregate':aggregate,'mismatches_vs_census_results':mismatches,
            'mismatches_vs_heldout_report':comparisons,'A_failures':special,'previously_capped':capped,
            'max_rss_kib':R.resource.getrusage(R.resource.RUSAGE_SELF).ru_maxrss}
    (HERE/'heldout_recount.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'complete':result['complete'],'families':rows,'seconds':result['seconds'],'mismatches':len(mismatches),'report_mismatches':len(comparisons),'aggregate':aggregate}),flush=True)

if __name__=='__main__': run()
