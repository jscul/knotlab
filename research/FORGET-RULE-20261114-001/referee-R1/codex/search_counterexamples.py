"""Bounded deterministic searches outside the census; literal and repaired A."""
from __future__ import annotations
import argparse, collections, gzip, hashlib, itertools, json, random, time
from pathlib import Path
import independent_rules as R
HERE=R.HERE; ROOT=R.ROOT
CENSUS=ROOT/'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'


def exhaustive_one():
    # All unordered NAE-block subsets of at most three triples, and every
    # ordered distinct continuation triple. Local caps 0..2 are fully covered.
    for local in range(3):
        triples=list(itertools.combinations(range(3+local),3))
        for arguments in itertools.permutations(range(3+local),3):
            for number in range(4):
                for block in itertools.combinations(triples,number):
                    yield 'exhaustive_1def_l0to2_K0to3',[[3,local,[['K',list(t)] for t in block]+[['SELF',list(arguments)]]]]


def exhaustive_two():
    # Every nonrecursive zero-local ternary NAE helper (one triple),
    # all its placements and all continuation placements in local caps 0..2,
    # with an optional NAE triple. This exhausts that explicitly narrow grid.
    for local in range(3):
        n=3+local; triples=list(itertools.combinations(range(n),3))
        for helper_args in triples:
            for continuation in itertools.permutations(range(n),3):
                for knot in [None]+triples:
                    body=[[0,list(helper_args)],['SELF',list(continuation)]]
                    if knot is not None: body.append(['K',list(knot)])
                    yield 'exhaustive_2def_helperK_l0to2_K0to1',[[3,0,[['K',[0,1,2]]]],[3,local,body]]


def random_families(seed,count):
    rng=random.Random(seed)
    for j in range(count):
        number=1 if j%3==0 else 2; defs=[]
        for i in range(number):
            local=rng.randrange(7); size=3+local
            calls=[]
            for _ in range(rng.randint(0,10)):
                options=['K','K','K']+([0,0] if i else [])+(['SELF'] if i==number-1 or j%4==0 else [])
                callee=rng.choice(options); args=rng.sample(range(size),3)
                calls.append([callee,args])
            if i==number-1 or j%4==0:
                if not any(c=='SELF' for c,_ in calls): calls.append(['SELF',rng.sample(range(size),3)])
            if not calls: calls=[['K',rng.sample(range(size),3)]]
            defs.append([3,local,calls])
        yield 'random_A79_seed'+str(seed),defs


def f_targeted(seed,count):
    rng=random.Random(seed)
    for j in range(count):
        local=rng.randint(1,6); n=3+local
        # Passing untouched ports later is essential to the suspected F issue.
        self_args=rng.sample(range(n),3)
        triples=list(itertools.combinations(range(n),3))
        knots=rng.sample(triples,min(len(triples),rng.randint(1,8)))
        body=[['K',list(t)] for t in knots]+[['SELF',self_args]]
        if j%3==0: body.append(['SELF',rng.sample(range(n),3)])
        yield 'F_output_targeted_seed'+str(seed),[[3,local,body]]


def run(args):
    start=time.monotonic(); deadline=start+args.seconds
    census_keys=set()
    with gzip.open(CENSUS,'rt') as f:
        for line in f: census_keys.add(json.loads(line)['key'])
    seen=set(); counts=collections.Counter(); buckets=collections.defaultdict(collections.Counter)
    counterexamples=[]; bounds=[]; nfail=[]; records=0; exact_counts=collections.Counter(); skipped=collections.Counter()
    streams=[]
    if args.mode in ('exhaustive','all'): streams.extend([exhaustive_one(),exhaustive_two()])
    if args.mode in ('random','all'): streams.extend([f_targeted(args.seed,args.count),random_families(args.seed+1,args.count)])
    log=(HERE/(args.name+'.jsonl')).open('w')
    try:
        for kind,raw in itertools.chain.from_iterable(streams):
            if time.monotonic()>deadline: counts['time_gate_reached']+=1; break
            key=R.canonical(raw)
            if key in seen: skipped['duplicate_description']+=1; continue
            seen.add(key); counts['generated_unique']+=1
            if key in census_keys: skipped['in_census_exact_key']+=1; continue
            counts['outside_census']+=1; buckets[kind]['outside_census']+=1
            defs,allG,G,size,calls,hist=R.prepare(raw)
            if not allG[-1]: counts['dead_limit']+=1; buckets[kind]['dead_limit']+=1; continue
            counts['alive']+=1; buckets[kind]['alive']+=1
            S=len(defs)-1
            a=R.rule_A(size,calls,G,S); n=R.rule_N(calls,S)
            fixed=R.rule_A(size,calls,G,S,protect_F_outputs=True)
            counts['A_certified']+=a['certified']; counts['N_cyclic']+=n['cyclic']; counts['F_peeling_used']+=bool(a.get('F_peelings',0))
            counts['repaired_A_certified']+=fixed['certified']
            buckets[kind]['A_certified']+=a['certified']; buckets[kind]['N_cyclic']+=n['cyclic']
            # Exact check every alive family, with caps only recording unknown.
            matrices,decision=R.exact(size,calls,G,S,max_states=args.states)
            counts['exact_tested']+=1; exact_counts[decision['verdict']]+=1; buckets[kind]['exact_'+decision['verdict']]+=1
            counts['R_i']+=len(matrices)
            bad=a['certified'] and decision['verdict']=='non-forgetting'
            badfixed=fixed['certified'] and decision['verdict']=='non-forgetting'
            badbound=a['certified'] and decision['r'] is not None and decision['r']>a['bound']
            badfixedbound=fixed['certified'] and decision['r'] is not None and decision['r']>fixed['bound']
            counts['repaired_A_bound_failures']+=badfixedbound
            counts['repaired_A_false_certificates']+=badfixed
            counts['A_certified_exact_'+decision['verdict']]+=a['certified']
            counts['repaired_A_certified_exact_'+decision['verdict']]+=fixed['certified']
            counts['N_cyclic_exact_'+decision['verdict']]+=n['cyclic']
            badN=n['cyclic'] and decision['verdict']=='certified'
            if bad or badbound or badN or badfixed or badfixedbound:
                row={'kind':kind,'description_sha256':hashlib.sha256(key.encode()).hexdigest(),'defs':raw,'S':S,
                     'G':{str(i):hex(R.E.mask(v)) for i,v in G.items()},'size':size,'calls':calls,'A':a,'repaired_A':fixed,
                     'N':n,'R_i':list(map(hex,matrices)),'exact':decision,'A_false_certificate':bad,'repaired_A_false_certificate':badfixed,
                     'A_bound_failure':badbound,'repaired_A_bound_failure':badfixedbound,'N_violation':badN}
                log.write(json.dumps(row)+'\n'); log.flush(); records+=1
                if bad:
                    counterexamples.append(row)
                    if len(counterexamples)<=3: print(json.dumps({'event':'COUNTEREXAMPLE','index':counts['outside_census'],'defs':raw,'A':a,'exact':decision}),flush=True)
                if badbound: bounds.append(row)
                if badN: nfail.append(row)
                if args.stop_first and bad: break
            if counts['outside_census']%10000==0:
                print(json.dumps({'event':'progress','seconds':round(time.monotonic()-start,2),'counts':dict(counts),'exact':dict(exact_counts)}),flush=True)
    finally:
        log.close()
        summary={'mode':args.mode,'seed':args.seed,'seconds':round(time.monotonic()-start,4),'counts':dict(counts),'by_generator':{k:dict(v) for k,v in buckets.items()},
                 'exact_verdicts':dict(exact_counts),'skipped':dict(skipped),'counterexamples':counterexamples[:20],
                 'counterexample_count':len(counterexamples),'bound_failure_count':len(bounds),'N_violation_count':len(nfail),
                 'repaired_A_counterexample_count':counts['repaired_A_false_certificates'],
                 'repaired_A_bound_failure_count':counts['repaired_A_bound_failures'],
                 'evidence_jsonl':args.name+'.jsonl','max_rss_kib':R.resource.getrusage(R.resource.RUSAGE_SELF).ru_maxrss,
                 'caveat':'Exact graph resource caps are unknown; dead-limit families excluded from Rule N theorem domain.'}
        (HERE/(args.name+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({'event':'done',**{k:v for k,v in summary.items() if k not in ('counterexamples','by_generator')}}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['exhaustive','random','all'],default='all');p.add_argument('--seed',type=int,default=20261114)
    p.add_argument('--count',type=int,default=100000);p.add_argument('--seconds',type=int,default=600);p.add_argument('--states',type=int,default=10000)
    p.add_argument('--name',default='search');p.add_argument('--stop-first',action='store_true'); run(p.parse_args())
