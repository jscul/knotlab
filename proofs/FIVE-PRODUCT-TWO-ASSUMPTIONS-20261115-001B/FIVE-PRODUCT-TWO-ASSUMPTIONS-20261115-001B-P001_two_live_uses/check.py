#!/usr/bin/env python3
"""Replay the two paid declarations, their raw premises, live capacities and the fixed query census."""
import copy
from itertools import product
import json
from pathlib import Path

from programs import AXES, GROUP_MENU, INF, Search, TwoPremises, explicit, old, original, training
from replay import ProofError, expanded, inspect, raw, replay, require
from collections import Counter


HERE = Path(__file__).resolve().parent


def exact_counts(search, a):
    """Second recurrence counts actual uses instead of classifying their common ancestor."""
    g = old.guard_points(((4,a),(256,0)))
    l = old.equation_points(1,0)
    max_uses = 4 if a == 0 else 2
    rows = []
    for state in search.states:
        best = [state.cost]+[INF]*max_uses
        f = state.fixed
        if f & g & l and f & g & ~l:
            if not (state.raw & ~g):
                after = search.ids[state.raw & l]
                if search.states[after].fixed:
                    best[1] = 1+search.states[after].cost
            for _, child in state.checks:
                for n in range(1,max_uses+1):
                    best[n] = min(best[n], 1+rows[child][n])
            for _, left, right in state.branches:
                for i in range(max_uses+1):
                    for j in range(max(0,1-i),max_uses+1-i):
                        best[i+j] = min(best[i+j], 1+rows[left][i]+rows[right][j])
        rows.append(best)
    return [v+(5 if i else 0) for i,v in enumerate(rows[search.root])]


def construct():
    programs, scans = {}, {}
    for name, menu in [('coordinates',AXES), ('full_guard_triple',GROUP_MENU)]:
        search = Search(menu)
        scans[name] = {'masks':list(menu),'reachable_raw_guards':len(search.states), 'profiles':{}}
        for a in (0,1):
            priced = TwoPremises(search,a)
            costs = priced.prices()
            counts = exact_counts(search,a)
            require(priced.training_cost==5 and min(costs[2:])==min(counts[2:]), 'recurrences disagree')
            scans[name]['profiles'][str(a)] = {'no_single_neither_x2_v_both':costs, 'by_exact_use_count':counts}
            if name == 'full_guard_triple':
                for index, label in enumerate(('single','neither','only_x2','only_v','both'),1):
                    programs[f'a{a}_{label}'] = priced.proof(index)
                programs[f'a{a}_asked_separately'] = explicit(search,a,'two_asked')
                if a == 0:
                    programs['a0_three'] = explicit(search,a,'three')
                    programs['a0_four'] = explicit(search,a,'four')
    expected = [[23,24,32,32,38,31],[23,28,36,42,42,35]]
    actual = [scans['full_guard_triple']['profiles'][str(a)]['no_single_neither_x2_v_both'] for a in (0,1)]
    require(actual == expected, 'two-premise guard census changed')
    return programs, scans


def capacity_and_training(a):
    sides = original.sources(1)
    guard = raw([(4,a),(256,0)])
    sizes = [len(original.fixed(guard & original.equation(1, bit))) for bit in (0,1)]
    expected = 32 if a == 0 else 16
    require(sizes == [expected,expected], 'saturated positive or countercase changed')
    slices = []
    questions = (2,8) if a == 0 else (2,)
    for answers in product((0,1), repeat=len(questions)):
        cell = guard & raw(zip(questions, answers))
        pair = [original.fixed(cell & original.equation(1,e)) for e in (0,1)]
        require(all(len(core)==8 for core in pair), 'eight-state consumer core')
        for core in pair:
            require(all(len(core & side)==4 for side in sides.values()), 'complementary four-state evaluators')
        slices.append({'answers':list(answers), 'post_and_counter_core_sizes':[len(core) for core in pair]})
    # The same checked five-node ordinary refutation works when the v premise is removed entirely.
    two_premise = guard & original.equation(1,1)
    one_premise = original.equation(4,a) & original.equation(1,1)
    for allowed in (two_premise,one_premise):
        counts = Counter()
        replay(training(), allowed, sides, counts)
        require(original.weight(counts)==5 and all(allowed & side for side in sides.values()), 'nonvacuous training')
    # Embed one complete local good/bad triple using x1=x3=u=v=0 and x0=1.
    images=[]
    for y,w,p in product((0,1),repeat=3):
        point = 1 | (a<<2) | (y<<4) | (w<<5) | (p<<6)
        require(point in two_premise and (point in sides['R']) == (p==y*w) and (point in sides['P']) == (p!=y*w),
                'one-triple lower-bound embedding')
        images.append(point)
    return {'positive_and_countercase_sizes':sizes, 'maximal_live_uses':expected//8,
            'attaining_coordinate_questions':list(questions), 'slices':slices,
            'five_cost_embedding':images, 'training_rich_plain_rows':[len(two_premise & s) for s in sides.values()],
            'one_premise_training_rich_plain_rows':[len(one_premise & s) for s in sides.values()]}


def reject(operation, text):
    try:
        operation()
    except (ProofError, ValueError) as error:
        require(text in str(error), 'unexpected negative control: '+str(error))
        return str(error)
    raise ProofError('invalid proof accepted')


def controls(a, programs):
    proof = programs[f'a{a}_asked_separately']
    bad = copy.deepcopy(proof)
    x_branch = 2+a
    bad['root'][x_branch] = bad['root'][x_branch][2]
    missing_v = reject(lambda:inspect(bad), '256=0 unestablished')
    bad = dict(proof,root=proof['root'][x_branch])
    missing_x = reject(lambda:inspect(bad), f'4={a} unestablished')
    sides = original.sources(1)
    witnesses = {}
    for label, held, absent in [('v', (4,a), (256,0)), ('x2', (256,0), (4,a))]:
        cell = raw([held,(2,0)])  # The first consumer chooses x1=0 after the route with one premise omitted.
        violators = cell - original.equation(*absent)
        require(original.fixed(cell) and all(cell & rows for rows in sides.values()), 'negative used a closed branch')
        witnesses[label] = {name:min(violators & rows) if violators & rows else None for name,rows in sides.items()}
        require(witnesses[label]['P'] is not None, 'missing raw plain witness')
    without_x2 = raw([(1,1),(256,0),(16,0)])
    surviving_plain = original.span(without_x2 & sides['R']) & sides['P']
    require(surviving_plain, 'old five-node training accidentally works without x2')
    named_wrong_training = reject(lambda:replay(training(), raw([(1,1),(256,0)]), sides, Counter()), 'surviving rows')
    matched = reject(lambda:inspect(proof,charge=0), 'surviving rows')
    require(len(original.sources(0)['R'] & original.sources(0)['P'])==64, 'matching-charge control')
    return {'missing_v':missing_v, 'missing_x2':missing_x, 'missing_raw_premise_witnesses':witnesses,
            'drop_x2_from_training':named_wrong_training,'surviving_plain_training_row':min(surviving_plain),
            'matching_charge_rejected':matched}


def main():
    proofs, scans = construct()
    require(proofs == json.loads((HERE/'certificates.json').read_text()), 'saved program changed')
    results = {}
    for name, proof in proofs.items():
        report = inspect(proof)
        one_premise = dict(proof,premise=proof['premise'][0])
        one_premise_info = original.inspect(one_premise)
        require(one_premise_info['cost']==report['total'] and len(one_premise_info['uses'])==len(report['uses']), 'one-premise rule replay')
        report['ordinary_expansion_cost'] = expanded(proof)
        results[name] = report
    for a in (0,1):
        for index,label in enumerate(('single','neither','only_x2','only_v','both'),1):
            require(results[f'a{a}_{label}']['total'] == scans['full_guard_triple']['profiles'][str(a)]['no_single_neither_x2_v_both'][index], 'individual certificate price')
    for n,name in ((3,'a0_three'),(4,'a0_four')):
        require(len(results[name]['uses']) == n and results[name]['total'] == scans['full_guard_triple']['profiles']['0']['by_exact_use_count'][n],
                'three/four-use construction misses the counted minimum')
    out = {'status':'passed','menu_census':scans,'programs':results,
           'capacity_and_five_cost':{str(a):capacity_and_training(a) for a in (0,1)},
           'negative_controls':{str(a):controls(a,proofs) for a in (0,1)}}
    saved = HERE/'checks.json'
    if saved.exists():
        require(json.loads(saved.read_text())==out, 'saved numeric evidence changed')
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
