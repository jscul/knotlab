"""Fixed stratified referee samples and resumable exact recomputation."""
from __future__ import annotations
import argparse
import collections
import gzip
import hashlib
import json
import random
import time
from pathlib import Path
from fresh_pattern import build, direct_build
from fresh_search import compile_existence, elimination_order, levels, search, Limit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT/'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


def forest(knots, nv):
    parent = list(range(nv+len(knots)))
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for i,row in enumerate(knots):
        f = nv+i
        for v in row:
            a,b = find(f),find(v)
            if a == b:
                return False
            parent[a] = b
    return True


def select():
    records = [json.loads(l) for l in gzip.open(DATA,'rt')]
    rng = random.Random(20261114917)
    by_profile = collections.defaultdict(list)
    for r in records:
        by_profile[tuple(z['L_N'] for z in r['levels'])].append(r)
    sample = []
    groups = [('chained',(3,4,5,6),12),('direct3',(3,3,3,3),4),
              ('direct2',(2,2,2,2),4),('slow',(3,3,4,4),3)]
    for label,profile,num in groups:
        pool = sorted(by_profile[profile],key=lambda r:r['case'])
        rng.shuffle(pool)
        chosen = []
        if label == 'chained':
            strata = collections.defaultdict(list)
            for r in pool:
                knots = build(r['key'],9)
                try:
                    _,width = elimination_order(knots,1023,8)
                except Limit:
                    continue
                strata[forest(knots,1023)].append((r,width))
            # Six cyclic and six incidence-forest descriptions, no ruler shortcut.
            for acyclic in (False,True):
                for r,width in strata[acyclic][:6]:
                    chosen.append(r)
                    r['_forest'] = acyclic
                    r['_width'] = width
        else:
            chosen = pool[:num]
        for r in chosen:
            sample.append({'stratum':label,'case':r['case'],'key':r['key'],
                           'study':[z['L_N'] for z in r['levels']],
                           'incidence_forest':r.get('_forest'),'N9_width':r.get('_width')})
    others = [r for profile,pool in by_profile.items() if '> 10' in profile for r in pool]
    rng.shuffle(others)
    for r in others[:3]:
        sample.append({'stratum':'over10','case':r['case'],'key':r['key'],
                       'study':[z['L_N'] for z in r['levels']]})
    unsure = [r for profile,pool in by_profile.items() if 'undecided' in profile for r in pool]
    rng.shuffle(unsure)
    # Diverse decided-prefix profiles; a width failure remains explicitly undecided.
    used_profiles = set()
    for r in unsure:
        profile = tuple(z['L_N'] for z in r['levels'])
        if profile in used_profiles:
            continue
        used_profiles.add(profile)
        sample.append({'stratum':'undecided','case':r['case'],'key':r['key'],'study':list(profile)})
        if len(used_profiles) == 4:
            break
    for prefix in ['58480a08','e1fc9d92']:
        r = next(r for r in records if r['case'].startswith(prefix))
        sample.append({'stratum':'Q3_targeted','case':r['case'],'key':r['key'],
                       'study':[z['L_N'] for z in r['levels']]})
    plan = {'selection_seed':20261114917,'selection_rule':'6 cyclic +6 forest chained with independent min-degree elimination width<=8; other strata shuffled by key with fixed RNG; four different undecided prefixes; two Q3 failures',
            'sample':sample,'limits':{'processes':1,'memory_GiB':3,'cap':10,'query_seconds_default':60},
            'method':'fresh exact bucket-elimination circuit; no assumed ruler formula or forest shortcut',
            'input_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest()}
    (HERE/'sample_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    return plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select',action='store_true')
    parser.add_argument('--depth',action='store_true')
    parser.add_argument('--seconds',type=float,default=60)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--stratum')
    args = parser.parse_args()
    if args.select:
        plan = select()
        print(json.dumps(collections.Counter(x['stratum'] for x in plan['sample'])))
        return
    plan = json.loads((HERE/'sample_plan.json').read_text())
    sample = plan['sample']
    if args.stratum:
        sample = [x for x in sample if x['stratum']==args.stratum]
    if args.depth:
        sample = ([x for x in sample if x['stratum']=='chained'][:10]
                  + [x for x in sample if x['stratum']=='direct3'][:2]
                  + [x for x in sample if x['stratum']=='slow'][:2])
    if args.limit:
        sample = sample[:args.limit]
    output = HERE/('depth_results.jsonl' if args.depth else 'optimality_results.jsonl')
    done = set()
    if output.exists():
        done = {(r['case'],r['N'],r['s']) for r in map(json.loads,output.read_text().splitlines())}
    for entry in sample:
        for N in ([10,11] if args.depth else [9]):
            wanted = [s for s in ([3,4] if args.depth else [1,2,3,4]) if (entry['case'],N,s) not in done]
            if not wanted:
                continue
            knots = build(entry['key'],N)
            if N==9:
                assert knots == direct_build(entry['key'],N), 'builder control mismatch'
            nv = (1<<(N+1))-1
            start = time.monotonic()
            try:
                compilation = compile_existence(knots,nv,start+min(120,args.seconds),8)
                failure = None
            except Limit as e:
                compilation = None
                failure = str(e)
            for s in wanted:
                if failure:
                    result = {'L':'undecided','exact':False,'reason':failure,'stats':{}}
                else:
                    A,B = levels(3,s)
                    result = search(knots,nv,A,B,cap=10,seconds=args.seconds,precompiled=compilation)
                row = {'case':entry['case'],'stratum':entry['stratum'],'key':entry['key'],'N':N,'s':s,
                       'study_N9':entry['study'][s-1],'knots':len(knots),'result':result}
                with output.open('a') as h:
                    h.write(json.dumps(row,separators=(',',':'))+'\n')
                print(json.dumps({'case':entry['case'][:16],'stratum':entry['stratum'],'N':N,'s':s,
                                  'study':entry['study'][s-1],'fresh':result['L'],'exact':result['exact'],
                                  'seconds':result['stats'].get('seconds'),'reason':result.get('reason')}),flush=True)


if __name__=='__main__':
    main()
