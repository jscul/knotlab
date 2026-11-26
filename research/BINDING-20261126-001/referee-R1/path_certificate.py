"""Verify the ten-knot sample's path parities from its support lists and joint states."""
import argparse
from collections import Counter, defaultdict, deque
from itertools import combinations, product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from replay_growth import grow

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIMIT = 2 * 1024 ** 3
resource.setrlimit(resource.RLIMIT_AS, (LIMIT, LIMIT))
PATHS = ((12, 24, 27, 32, 39, 46), (1, 18, 21, 29), (22, 33, 37))


def mask(names):
    return sum(1 << i for i in names)


def solve(equations):
    """One assignment for equations (support, value), with free distinctions zero."""
    pivots = {}
    for lhs, rhs in equations:
        while lhs:
            i = lhs.bit_length() - 1
            if i not in pivots:
                pivots[i] = (lhs, rhs)
                break
            other, value = pivots[i]
            lhs ^= other
            rhs ^= value
        else:
            if rhs:
                return None
    state = 0
    for i, (lhs, rhs) in sorted(pivots.items()):
        if (lhs & state).bit_count() % 2 != rhs:
            state |= 1 << i
    return state


def joint(rows, paths, fixed=()):
    equations = [(r, 0) for r in rows] + [(1 << i, 0) for i in fixed]
    out = {}
    for values in product(range(2), repeat=len(paths)):
        state = solve(equations + list(zip(paths, values)))
        if state is not None:
            assert all((state & r).bit_count()%2 == b for r,b in equations + list(zip(paths,values)))
            out[''.join(map(str, values))] = list(i for i in range(state.bit_length()) if state >> i & 1)
    return out


def shortest_literal(stage):
    names = sorted(set().union(*stage))
    synd = {i:mask(k for k,s in enumerate(stage) if i in s) for i in names}
    mins = {}
    shortest = set()
    counts = {}
    for weight in range(1, len(names)+1):
        accepted = 0
        for chosen in combinations(names, weight):
            s = 0
            for d in chosen:
                s ^= synd[d]
            if s:
                continue
            accepted += 1
            for d in chosen:
                mins.setdefault(d, weight)
            if any(mins[d] == weight for d in chosen):
                shortest.add(mask(chosen))
        counts[weight] = accepted
        if len(mins) == len(names):
            break
    return shortest, counts, Counter(mins.values())


def path_geometry(stage, support, moves=None):
    holders = defaultdict(list)
    for k, row in enumerate(stage):
        for d in row:
            holders[d].append(k)
    links, local = defaultdict(list), defaultdict(list)
    for d, who in holders.items():
        a, b = who if len(who)==2 else [who[0], f'loose {d}']
        links[a].append((b,d))
        links[b].append((a,d))
        if d in support:
            local[a].append(b)
            local[b].append(a)
    u, v = [a for a, adj in local.items() if len(adj) == 1]
    dist, paths = {u:0}, {u:1}
    queue = deque([u])
    while queue:
        a = queue.popleft()
        for b,_ in links[a]:
            if b not in dist:
                dist[b] = dist[a]+1
                paths[b] = paths[a]
                queue.append(b)
            elif dist[b] == dist[a]+1:
                paths[b] += paths[a]
    assert dist[v] == len(support)
    out = {'endpoints':[u,v], 'shortest_length':dist[v], 'shortest_supports_between_endpoints':paths[v]}
    if moves is not None:
        # Compare all tied shortest paths for the fixed endpoint pair. Acyclic
        # backtracking by decreasing distance visits each support once.
        laws = list(map(mask,stage))
        stack = [(v,0)]
        kinds = Counter()
        while stack:
            at, path = stack.pop()
            if at != u:
                stack.extend((other,path | (1 << d)) for other,d in links[at] if dist[other] == dist[at]-1)
                continue
            if any((m&path).bit_count()%2 for m in moves):
                kinds['changes on a shortest move'] += 1
            elif len(joint(laws,[path])) == 1:
                kinds['constant on allowed states'] += 1
            elif any(len(joint(laws,[path],fixed=row)) == 1 for row in stage):
                kinds['read by a single knot'] += 1
            elif len(joint(laws,[path ^ mask(support)])) == 1:
                kinds['unread and gives the selected parity'] += 1
            else:
                kinds['unread and gives another parity'] += 1
        assert sum(kinds.values()) == paths[v]
        out['all_tied_path_parities'] = dict(kinds)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    previous_referee = HERE.parents[1]/'LAYERS-20261126-001'/'referee-R1'
    raw = json.loads((previous_referee/'extended_witness.json').read_text())[0]
    stages = [raw['start supports']]
    for t in range(3):
        nxt,status = grow(stages[-1])
        assert status == 'funded'
        stages.append(nxt)
    dest = stages[-1]
    carriers = list(map(mask, PATHS))
    rows = list(map(mask,dest))
    assert all(a&b==0 for a,b in combinations(carriers,2))
    out = dict(source=raw['sample index'], path_supports=PATHS, grown_knots=dest,
               geometry=[path_geometry(dest,p) for p in PATHS])
    moves, counts, mins = shortest_literal(stages[0] if args.pilot else dest)
    out.update(allowed_changes_by_size=counts, distinctions_by_minimum=mins, shortest_changes=len(moves))
    if not args.pilot:
        out['grown_support_joint_images'] = [sorted(joint(rows, [1 << i for i in support])) for support in dest]
        assert all(len(image) == 1 << (len(support)-1) for support, image in zip(dest,out['grown_support_joint_images']))
        out['geometry'] = [path_geometry(dest,p,moves) for p in PATHS]
        out['moves_changing_each_fact'] = [sum((m&p).bit_count()%2 for m in moves) for p in carriers]
        out['joint_states'] = joint(rows, carriers)
        out['values_with_each_knot_fixed_to_zero'] = [sorted(joint(rows,carriers,s)) for s in dest]
        out['omitting_one_law'] = {k:sorted(joint(rows[:k]+rows[k+1:],carriers)) for k in range(len(rows))}
        out['rounds'] = []
        for t, stage in enumerate(stages):
            available = set().union(*stage)
            small, _, _ = shortest_literal(stage)
            out['rounds'].append({'round':t,'knots':len(stage),'distinctions':len(available),
                    'exact_supports_exist':[set(p)<=available for p in PATHS],
                    'moves_changing_existing_fact':[sum((p&m).bit_count()%2 for m in small) if set(names)<=available else None
                                                     for p,names in zip(carriers,PATHS)],
                    'joint_states_leaving_absent_distinctions_free':sorted(joint(list(map(mask,stage)),carriers)),
                    'joint_values_of_existing_facts_with_each_knot_fixed':[
                        sorted(joint(list(map(mask,stage)),[p for p,ns in zip(carriers,PATHS) if set(ns)<=available],s))
                        for s in stage]})
        columns = [mask(k for k,row in enumerate(rows) if row >> d & 1) for d in range(max(set().union(*dest))+1)]
        total = carriers[0]^carriers[1]^carriers[2]
        coeff = solve([(column,(total>>d)&1) for d,column in enumerate(columns)])
        assert coeff is not None
        used = [k for k in range(len(rows)) if coeff >> k & 1]
        check = 0
        for k in used:
            check ^= rows[k]
        assert check == total
        out['laws_giving_the_relation'] = used
        later, status = grow(dest)
        assert status == 'funded'
        later_moves, _, _ = shortest_literal(later)
        out['fourth_round_on_the_same_supports'] = {
            'geometry':[path_geometry(later,p) for p in PATHS],
            'every_distinction_on_the_three_carriers_has_two_holders':all(sum(d in row for row in later)==2 for p in PATHS for d in p),
            'shortest_changes':len(later_moves), 'moves_changing_each_fact':[sum((p&m).bit_count()%2 for m in later_moves) for p in carriers],
            'joint_values_per_knot_fixed_to_zero':[sorted(joint(list(map(mask,later)),carriers,s)) for s in later]}
        # An arbitrary bijection transports the actual supports. It does not choose them anew.
        renamed = {i:(17*i+11)%len(set().union(*dest)) for i in set().union(*dest)}
        assert len(set(renamed.values())) == len(renamed)
        other = [tuple(renamed[i] for i in row) for row in reversed(dest)]
        other_paths = [tuple(renamed[i] for i in row) for row in PATHS]
        other_moves, _, _ = shortest_literal(other)
        out['renaming_check'] = {'joint_values':sorted(joint(list(map(mask,other)),list(map(mask,other_paths)))),
               'moves_changing_each_fact':[sum((m&mask(p)).bit_count()%2 for m in other_moves) for p in other_paths],
               'all_knots_keep_all_four_values':all(len(joint(list(map(mask,other)),list(map(mask,other_paths)),s))==4 for s in other)}
        # Derive a clause for each value triple actually missing from the image.
        clauses = []
        for values in product(range(2), repeat=3):
            if ''.join(map(str, values)) not in out['joint_states']:
                clauses.append(' '.join(('~' if v else '')+x for x,v in zip('abc',values)))
        proc = subprocess.run([sys.executable,'-B','-m','knotlab','check','--cnf','; '.join(clauses),
                               '--loops','a','b','--contact','c','--json'], cwd=ROOT,
                              env={**os.environ,'PYTHONPATH':str(ROOT/'tools')},check=True,capture_output=True,text=True)
        out['knot_test_of_measured_image'] = json.loads(proc.stdout)
        assert len(out['joint_states'])==4 and out['moves_changing_each_fact']==[0,0,0]
    out['seconds'] = round(time.monotonic()-start,3)
    (HERE/('path_certificate_pilot.json' if args.pilot else 'path_certificate.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(out['geometry'], out.get('laws_giving_the_relation'),out['seconds'])


if __name__=='__main__':
    main()
