"""Test the scope of the separation claim at the study's first intervention round."""
import argparse
from collections import Counter
import json
import random
from time import perf_counter

from growth import start
from structure import A, HERE, records

SEED = 26112645


def three(b, join='meeting', treatment='wait'):
    state = start(A,b,'CAP-3',join=join,treatment=treatment)
    for _ in range(3):
        state.step()
    return state


def compare(state,u,sign):
    changed = state.copy()
    base = state.copy()
    changed.mark(u,sign)
    first = None
    count_first = None
    while base.r < 24 and max(len(base.h),len(changed.h)) <= 6000:
        changed.step()
        base.step()
        if first is None and base.own != changed.own:
            first = base.r
        if count_first is None and len(base.own) != len(changed.own):
            count_first = base.r
    return {'knot':u,'sign':sign,'heard':first,'count_first':count_first,'end':base.r}


def run(pilot):
    names = [r['B'] for r in records('recede_runs.jsonl.gz')]
    picked = []
    original = sorted(set(r['B'] for r in records('waiting_far_runs.jsonl.gz')) | {'g3:22@0','g1:3@0'})
    by_join = Counter()
    retired = Counter()
    for b in original[:2] if pilot else original:
        probe = three(b, treatment='retire')
        retired[str(probe.links()['class'])] += 1
        for join in ('meeting','share'):
            for inclusive in (False,True):
                state = three(b, join)
                result = state.links(inclusive=inclusive)
                by_join[str((join,inclusive,result['class']))] += 1
    for b in names:
        state = three(b)
        if state.links()['class']:
            picked.append(b)
    # A scope check, weighted equally per census entry still linked at round 3.
    chosen = random.Random(SEED).sample(picked,8)
    strict = {}
    for b in chosen[:1] if pilot else chosen:
        state = three(b)
        parts,_,classes = state.partition()
        allowed = {classes[u] for u in parts if state.role[u] == 1}
        dist = state.distances()
        sites = sorted((dist[u],u) for u in parts if state.role[u]==2)[:5]
        strict[b] = [dict(compare(state,u,sign),sharing=d, in_receiver_class=classes[u] in allowed)
                     for d,u in sites for sign in ('add','bar')]
    mixed = {}
    # Count only strict receiver births and allow the far site to descend from
    # the far end and a link knot, while excluding all receiver descendants.
    for k in (3,) if pilot else range(3,8):
        for b in ('g3:22@0','g1:3@0'):
            st = start(f'tri:{k-2}22@0',b,f'CAP-{k}')
            for _ in range(3):
                st.step()
            parts,_,classes = st.partition()
            ac = {classes[u] for u in parts if st.role[u]==1}
            dist = st.distances()
            sites = sorted((dist[u],u) for u in parts if st.role[u]==6 and classes[u] in ac)
            mixed[str((k,b))] = [dict(compare(st,u,sign),sharing=d) for d,u in sites for sign in ('add','bar')]
    retired_case = three('n4:g16:1112@1',treatment='retire')
    dist = retired_case.distances()
    sites = sorted((dist[u],u) for u,h in enumerate(retired_case.h) if h and retired_case.role[u]==2)[:5]
    retired_marks = [dict(compare(retired_case,u,sign),sharing=d) for d,u in sites for sign in ('add','bar')]
    return {'retire_instead_of_wait_at_round_3':retired,
            'four_knot_far_end_with_retiring':{'linked':retired_case.links(),'marks':retired_marks},'seed':SEED,'eligible_at_round_3':len(picked),'selected':chosen,'scope_check':strict,
            'both_ownership_and_join_at_round_3':by_join,'far_and_link_ancestry_only':mixed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    flags=parser.parse_args()
    before=perf_counter()
    result=run(flags.pilot)
    if not flags.pilot:
        (HERE/'swaps.json').write_text(json.dumps(result,indent=1)+'\n')
    print('seconds',round(perf_counter()-before,2), 'eligible',result['eligible_at_round_3'])
    for k in ('scope_check','far_and_link_ancestry_only'):
        cases=[r for rows in result[k].values() for r in rows]
        print(k,len(cases),sum(r['heard'] is not None for r in cases))
