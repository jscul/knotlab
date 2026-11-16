"""Recompute total discovery, search and verification cost for every prefix and depth."""
from collections import Counter
import gzip
import hashlib
from itertools import accumulate
import json
from pathlib import Path
from statistics import median
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T=HERE.name
DEFAULT=ROOT/'artifacts'/T/(T+'-E001_learned_library')
ARMS=('primitive','learned','flat','given')


def read(path):
    return json.loads(path.read_bytes())


def records(path):
    with gzip.open(path,'rt') as source:
        return [json.loads(line) for line in source]


def metrics(row, truth):
    item=row['result']
    w=item['work']; t=item.get('timing',{})
    return {'exact':int(item['status']=='exact' and item['truth']==truth and item['circuit'] is not None),
            'tests':w['binary_placement_trials']+w['ternary_placement_tests'],
            'failed_trials':w['binary_placement_failures']+w['ternary_placement_failures'],
            'cofactor_bit_reads':w['factor_truth_bit_reads'], 'template_uses':item.get('template_uses',0),
            'physical_nands':item.get('expanded_NANDs') or 0, 'verified_rows':w['verification_rows'],
            'search_cpu_ns':t.get('search_cpu_ns',0),'search_wall_ns':round(t.get('search_seconds',0)*1e9),
            'build_ns':round(t.get('build_seconds',0)*1e9),'verify_ns':round(t.get('verification_seconds',0)*1e9),
            'wall_ns':row.get('wall_ns',row.get('elapsed_ns',0))}


def total(items):
    out=Counter()
    for item in items:
        out.update(item)
    return dict(out)


def med(items):
    return {k:median(v[k] for v in items) for k in items[0]}


def crossing(a,b):
    delta=[x-y for x,y in zip(a,b,strict=True)]
    earliest=next((k for k in range(1,len(delta)) if delta[k]<=0),None)
    best=min(range(1,len(delta)),key=delta.__getitem__)
    return {'first_break_even':earliest,'end_gap_ns':delta[-1],'minimum_gap_ns':delta[best],'closest_prefix':best,
            'reversals':[k for k in range(2,len(delta)) if delta[k-1]<=0<delta[k]]}


def summarize(out):
    acquisition=read(out/'gate-freeze.json')
    held=read(out/'held.json')
    grade=read(out/'grading.json')
    train={r['id']:r['truth'] for r in read(out/'train.json')}
    log=records(out/'training.jsonl.gz')
    training_counts=total(metrics(r,train[r['id']]) for r in log)
    curves={};observations={}; raw={}; startups={}
    errors=0
    for line in (out/'results.jsonl').read_text().splitlines():
        rec=json.loads(line)
        if rec['status']!='ok':
            raise ValueError(f"unresolved runner failure in {rec['case']}: {rec['status']}")
        case=rec['result']; a=case['arm']; c=case['cache']; repeat=case['repeat']
        path=out/case['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=case['sha256']:
            raise ValueError('receipt hash disagrees')
        rows=records(path)
        if [r['id'] for r in rows]!=[r['id'] for r in held]:
            raise ValueError('the held order changed')
        values=[metrics(row,t['truth']) for row,t in zip(rows,held,strict=True)]
        errors+=sum(1-x['exact'] for x in values)
        upfront=acquisition['wall_ns'] if a in ('learned','flat') else 0
        curves[c,a,repeat]=list(accumulate((x['wall_ns'] for x in values),initial=upfront+case['startup_ns']))
        startups[c,a,repeat]=case['startup_ns']
        observations[c,a,repeat]=values
        raw[c,a,repeat]=rows
    if len(curves)!=40:
        raise ValueError('incomplete transfer runs')
    totals={};groups={}
    for c in ('warm','cold'):
        totals[c]={};groups[c]={}
        base=[median(x) for x in zip(*(curves[c,'primitive',r] for r in range(5)))]
        for a in ARMS:
            by_prefix=[median(x) for x in zip(*(curves[c,a,r] for r in range(5)))]
            repeated=[observations[c,a,r] for r in range(5)]
            for r in range(1,5):
                for x,y in zip(raw[c,a,0],raw[c,a,r],strict=True):
                    for k in ('status','truth','circuit','expr','work'):
                        if x['result'].get(k)!=y['result'].get(k):
                            raise ValueError(f'paid repeat changed behavior for {a} {x["id"]}')
            summary=med([total(v) for v in repeated])
            upstream=acquisition['wall_ns'] if a in ('learned','flat') else 0
            summary.update(acquisition_ns=upstream,total_paid_ns=by_prefix[-1],
                           downstream_ns=by_prefix[-1]-upstream,
                           run_paid_ns=[curves[c,a,r][-1] for r in range(5)],
                           startup_ns=median(startups[c,a,r] for r in range(5)),
                           vs_primitive=crossing(by_prefix,base))
            summary['paired_repeat_crossings']=[crossing(curves[c,a,r],curves[c,'primitive',r]) for r in range(5)]
            totals[c][a]=summary
            for depth in (2,3,4):
                for kind in ('positive','negative'):
                    ids=[i for i,t in enumerate(held) if grade[t['id']]['depth']==depth and grade[t['id']]['kind']==kind]
                    cell=groups[c].setdefault(f'{depth}-{kind}',{'tasks':len(ids)})
                    cell[a]=med([total(observations[c,a,r][i] for i in ids) for r in range(5)])
        for r in range(5):
            for x,y in zip(raw[c,'learned',r],raw[c,'flat',r],strict=True):
                for k in ('binary_placement_trials','ternary_placement_tests','peel_pair_probes','factor_truth_bit_reads'):
                    if x['result']['work'][k]!=y['result']['work'][k]:
                        raise ValueError('inlining changed the placement search')
    return {'entry':read(out/'entry.json'),'selected_proposal':read(out/'candidates.json')['selected'],
            'acquisition':acquisition,'training_counts':training_counts,
            'training_tasks':len(train),'held_tasks':len(held),'failed_held_runs':errors,
            'held_runs':len(curves)*len(held),'held_rule_input_pairs_per_run':sum(1<<x['n'] for x in held),
            'totals':totals,'depths':groups}


if __name__=='__main__':
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DEFAULT
    result=summarize(out)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'training':result['acquisition']['wall_ns'],'selected':result['entry'],
                      'endpoints':{a:result['totals']['warm'][a]['total_paid_ns'] for a in ARMS},
                      'gap':result['totals']['warm']['learned']['vs_primitive'],'failed':result['failed_held_runs']},indent=2))
