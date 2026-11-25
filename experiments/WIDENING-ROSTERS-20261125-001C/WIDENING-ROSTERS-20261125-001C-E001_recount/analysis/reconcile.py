"""Reconcile the two independent growth records and the separately defined finite model."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from finite_model import describe

HERE = Path(__file__).resolve().parent
CASEFILE = HERE.parent / 'cases.json'
CONTRACT = HERE.parent / 'contract.json'
FIELDS = ('knots', 'members', 'pairs', 'part_sizes', 'degree_histogram', 'greatest_counts', 'reach_sha256')


def records(path):
    latest = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        latest[row['case']] = row
    failures = {key: row['status'] for key, row in latest.items() if row['status'] != 'ok'}
    return [row['result'] for row in latest.values() if row['status'] == 'ok'], failures


def extract(results, first):
    stages, terminal = {}, {}
    for record in results:
        for run in (record['laws'] if first else [record]):
            last = {'case': record['case'], 'kl':run['kl'],'round':run['rounds_done'],'knots':run['knots']} if first else run['terminal']
            key = (last['case'], last['kl'])
            terminal[key] = last
            for row in run['stages']:
                index = (*key,row['round'])
                if index in stages:
                    raise ValueError(f'Duplicate stage {index}')
                stages[index] = row
    return stages, terminal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('producer',type=Path)
    parser.add_argument('referee',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    sources = {}
    for path in (args.producer, args.referee, CASEFILE, CONTRACT):
        sources[str(path)] = sha256(path.read_bytes()).hexdigest()
    cases = {x['id']:x for x in json.loads(CASEFILE.read_text())}
    groups = json.loads(CONTRACT.read_text())['groups']
    category = {f'census:{idx}':g for g,ids in enumerate(groups) for idx in ids}
    a,af = records(args.producer)
    a,at = extract(a,True)
    if args.referee.name == 'stages.jsonl':
        row_key = lambda row: (row['case'], row['kl'], row['round'])
        rows = [json.loads(line) for line in args.referee.read_text().splitlines()]
        b = {row_key(row):row for row in rows}
        assert len(b)==len(rows), 'duplicate referee stages'
        terminal_path = args.referee.with_name('terminal.jsonl')
        sources[str(terminal_path)] = sha256(terminal_path.read_bytes()).hexdigest()
        end = [json.loads(line) for line in terminal_path.read_text().splitlines()]
        bt = {(r['case'],r['kl']):r for r in end}
        assert len(bt)==len(end), 'duplicate terminal records'
        bf = {}
    else:
        b,bf = records(args.referee)
        b,bt = extract(b,False)
    missing = []; disagreements=[]; terminal_mismatch=[]; model_fail=[]; hypotheses=[]; kstats=Counter()
    best=[]; heldout=[]; checked=0; agree_n=0; cutoff_tests=Counter(); cap_cases=Counter()
    for id,case in cases.items():
        start, law = case['start'], case['law']
        g=category.get(start)
        m = int(start.split(':')[1]) if start.startswith('touching:') else 4 if g==1 else 3
        k = 2 if g==2 else 4 if g==3 else 0
        modeled = start.startswith('touching:') or g==0 or (g==1 and law in ('L0','L9','L11')) or (g in (2,3) and law in ('L0','L9'))
        for kl in ['nae','parity']:
            key=(id,kl)
            aa,bb=at.get(key,{}),bt.get(key,{})
            if aa.get('round')!=bb.get('round') or aa.get('knots')!=bb.get('knots'):
                terminal_mismatch.append([*key, aa.get('round'),bb.get('round'),aa.get('knots'),bb.get('knots')])
            for t in case['rounds']:
                index=(*key,t)
                if index not in a or index not in b:
                    missing.append([*index,index in a,index in b]);continue
                x,y=a[index],b[index]
                bad=[f for f in FIELDS if x[f]!=y[f]]
                if bad:
                    disagreements.append([*index,bad]);continue
                agree_n+=1
                kstats[kl]+=x['knots']
                if modeled and t>=(3 if k else 1):
                    expected=describe(m,k,t,case['r_max'])
                    bad=[f for f,v in expected.items() if x[f]!=v]
                    if bad: model_fail.append([*index,bad])
                    checked+=1
                if g in (2,3) and law in ('L0','L9') and t>=20:
                    cutoff=(t-1-k//2)//3
                    lower= 2 if k==4 else 1
                    actual=x['greatest_counts']
                    def poly(r):
                        return (12*r*r+2) if k==2 else (48*r*r-48*r+24)
                    for r in range(lower,min(cutoff+1,len(actual))):
                        if actual[r]!=poly(r):hypotheses.append([*index,r,'at or below predicted cutoff',actual[r],poly(r)])
                    if lower<=cutoff+1<len(actual):
                        cutoff_tests[g]+=1
                        if actual[cutoff+1]>=poly(cutoff+1):hypotheses.append([*index,cutoff+1,'above predicted cutoff',actual[cutoff+1],poly(cutoff+1)])
                if g==1 and law in ('L1','L6','L7') and t>=2:
                    cap_cases[law]+=1
                    if len(x['part_sizes']) not in (4,5) or x['greatest_counts'] != [min(2*r+1,x['part_sizes'][0]) for r in range(case['r_max']+1)]:
                        hypotheses.append([*index,'cap-three parts or reach',x['part_sizes'],x['greatest_counts']])
                if t==case['rounds'][-1] and kl=='nae':
                    datum=[id,t,x['members'],x['pairs'],x['part_sizes'],x['greatest_counts']]
                    if g is None and start.startswith('census:'):heldout.append(datum)
                    else:best.append(datum)
    aggregate=dict(inputs=sources,registered_cases=len(cases),registered_stage_laws=sum(2*len(c['rounds']) for c in cases.values()),producer_runs=len(at),referee_runs=len(bt),producer_failures=af,referee_failures=bf,agreed_stages=agree_n,agreed_knot_stage_occurrences=dict(kstats),omitted=missing,terminal_mismatches=terminal_mismatch,disagreements=disagreements,model_spectra_compared=checked,model_failures=model_fail,sharp_cutoff_tests=dict(cutoff_tests),cap_three_tests=dict(cap_cases),prediction_exceptions=hypotheses,last_rosters=best,heldout_last_rosters=heldout)
    args.output.write_text(json.dumps(aggregate,indent=1)+'\n')


if __name__=='__main__':
    main()
