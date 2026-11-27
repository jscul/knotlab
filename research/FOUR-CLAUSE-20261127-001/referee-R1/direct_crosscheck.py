"""Directly enumerate the omitted stages with surviving four-clause choices."""
import argparse
import json
from pathlib import Path
from time import perf_counter

from read_recount import calculate, stage_source

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]


def canonical(pairs, clauses, chosen):
    return (tuple(sorted(tuple(sorted(p)) for p in pairs)),
            tuple(sorted(tuple(sorted(c)) for c in clauses)),
            tuple(sorted(pairs[chosen])))


def from_search(pattern):
    positions=((0,2,4),(0,3,5),(1,2,5),(1,3,4))
    pairs=[[2*sum(1<<d for d in c)+s for c,s in p] for p in pattern['signed_pairs']]
    six=pairs[0]+pairs[1]+pairs[2]
    clauses=[[six[i] for i in t] for t in positions]
    return {canonical(pairs,clauses,r['both_pair']):sorted(r['initial_law_deletions']+r['birth_law_deletions'])
            for r in pattern['qualifying_roles']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    start=perf_counter()
    census=json.loads((RESEARCH/'FORBID-EDITS-20261126-001/starts.json').read_text())
    screened=[json.loads(line) for line in (HERE/'omitted_screen.jsonl').read_text().splitlines()]
    selected=sorted((r['start'],r['round']) for r in screened if r['structural_patterns_tested'])
    exact={}
    if args.pilot:
        selected=[(5260,2), min((r['start'],r['round']) for r in screened if r['distinctions']==20)]
    else:
        for line in (HERE/'omitted_stages.jsonl').read_text().splitlines():
            r=json.loads(line)
            exact[r['start'],r['round']]=r
    results=[]
    for idx,t in selected:
        tic=perf_counter()
        stages=dict(stage_source(census,idx))
        source=stages[t]
        outcome=calculate(source,len(stages[0]),0)
        positives={canonical(r['pairs'],r['clauses'],r['both']):r['laws_needed']
                   for r in outcome.get('relations',[]) if r['pairs_free'] and not r['upper_reading_determined_by_selected_lower_bond'] and len(r['words'])<8}
        if not args.pilot:
            independent={}
            for p in exact[idx,t]['patterns']:
                independent.update(from_search(p))
            assert positives==independent
        results.append({'census_entry':idx,'round':t,'distinctions':1+max(max(k) for k in source),
                        'raw_state_count':1<<(1+max(max(k) for k in source)), 'source_knots':source,
                        'elapsed_seconds':round(perf_counter()-tic,3),
                        'matched_roles_and_all_individual_deletions':None if args.pilot else len(positives),
                        **outcome})
    filename='direct_crosscheck_pilot.json' if args.pilot else 'direct_crosscheck.json'
    (HERE/filename).write_text(json.dumps(results,indent=2)+'\n')
    print([(r['census_entry'],r['bonds'],r['patterns'],r['elapsed_seconds']) for r in results],
          'total seconds',round(perf_counter()-start,2))

if __name__=='__main__':
    main()
