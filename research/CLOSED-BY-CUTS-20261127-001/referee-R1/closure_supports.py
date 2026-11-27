"""Count closed systems up to renaming and test the projected law at each displayed knot."""
import argparse
from collections import Counter, defaultdict
import contextlib
import io
import json
from time import perf_counter

import networkx as nx
from verify_readings import HERE, column, knot_check, letter, read, tuples_in, words


def check_projection(width, missing):
    names = [f'X{k}' for k in range(width)]
    clauses = '; '.join(' '.join(letter(x,v) for x,v in zip(names,w)) for w in missing)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status=knot_check(['check','--cnf',clauses,'--loops',*names[:-1],'--contact',names[-1],'--json'])
    assert status == 0
    result = json.loads(output.getvalue())
    return {k: result[k] for k in ('binding','loss_on_erasure','coexistence','is_knot')}


def record(row, canonical):
    knots = row['supports']
    held = defaultdict(list)
    for i,k in enumerate(knots):
        for x in k:
            held[x].append(i)
    assert all(len(v)==2 for v in held.values())
    shared = Counter(map(tuple,held.values()))
    system = nx.Graph()
    system.add_nodes_from(range(len(knots)))
    system.add_weighted_edges_from((i,j,c) for (i,j),c in shared.items())
    signature = (len(knots),tuple(sorted(map(len,knots))),tuple(sorted(shared.values())))

    n=len(held)
    raw = {x:column(i,n) for i,x in enumerate(sorted(held))}
    allowed = (1 << (1<<n)) - 1
    for k in knots:
        ones = zeros = allowed
        for x in k:
            ones &= raw[x]
            zeros &= ~raw[x]
        allowed ^= ones | zeros
    assert allowed
    extra, lost, failures = [], [], []
    for i,k in enumerate(knots):
        cells = tuples_in(allowed,[raw[x] for x in k])
        missing=tuple(w for w in words(len(k)) if w not in cells)
        if len(missing)>2:
            extra.append(i)
        key = (len(k),missing)
        if key not in canonical:
            canonical[key] = check_projection(*key)
        verdict=canonical[key]
        assert verdict['binding'] and verdict['coexistence']
        if not verdict['is_knot']:
            lost.append(i)
            for j,x in enumerate(k):
                projected = {w[:j]+w[j+1:] for w in cells}
                absent = sorted(set(words(len(k)-1)) - projected)
                if absent:
                    failures.append(dict(support=i, distinctions=k, forget=x,
                                         still_excluded=[''.join(map(str,w)) for w in absent]))
                    break
    return system,signature,dict(id=row['census_id'],round=row['round'],displayed=len(knots),
                                 permitted_states=allowed.bit_count(),additional_missing_words_at=extra,
                                 failed_projection_at=lost, erasure_examples=failures,
                                 knots_passing=len(knots)-len(lost))


def main(pilot):
    rows = [r for r in read(HERE/'growth_stages.json') if r['law']=='arity_floor']
    if pilot:
        rows=rows[:10]
    canonical={}
    representatives=defaultdict(list)
    simple=Counter()
    results=[]
    for row in rows:
        system,sig,rec = record(row,canonical)
        assert nx.is_connected(system)
        for representative,members in representatives[sig]:
            if nx.is_isomorphic(system,representative,edge_match=nx.algorithms.isomorphism.numerical_edge_match('weight',1)):
                members.append(rec['id'])
                break
        else:
            representatives[sig].append((system,[rec['id']]))
        if set(sig[1])=={3}:
            simple['three_place']+=1
            simple['three_place_each_pair_meets_at_most_once']+=max(sig[2])==1
        results.append(rec)
    sizes=Counter((len(rep),len(members)) for group in representatives.values() for rep,members in group)
    return dict(starts=len(rows),unmarked_classes=sum(sizes.values()),
                classes=[dict(knots=k,starts_per_class=m,classes=count) for (k,m),count in sorted(sizes.items())],
                all_three_place=dict(simple),number_displayed=sum(r['displayed'] for r in results),
                displayed_which_fail_projection=sum(len(r['failed_projection_at']) for r in results),
                stages_with_a_failed_projection=sum(bool(r['failed_projection_at']) for r in results),
                stages_with_extra_local_exclusions=sum(bool(r['additional_missing_words_at']) for r in results),
                families_of_distinct_projected_tables=len(canonical),
                passing_support_count_histogram=Counter(r['knots_passing'] for r in results),
                projections_with_failures=[r for r in results if r['failed_projection_at']])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    result=main(args.pilot)
    if not args.pilot:
        (HERE/'closure_supports.json').write_text(json.dumps(result,indent=2)+'\n')
    print({k:v for k,v in result.items() if k not in ('projections_with_failures','classes')},round(perf_counter()-t,4))
