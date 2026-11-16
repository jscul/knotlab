#!/usr/bin/env python3
"""Reconstruct and price the saved proofs, the coordinate census and wider lower bounds."""
from collections import Counter
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import cap_obstructions
import focused_cases
import guard_prefix
import one_premise_audit
import rich_covers
import sector_audit
import solver
import verifier


HOME = Path(__file__).resolve().parent


def census(search):
    compiler = shutil.which('c++')
    verifier.ensure(compiler, 'a C++17 compiler is required for the full coordinate census')
    with tempfile.TemporaryDirectory(prefix='five-product-coordinate-') as tmp:
        program = str(Path(tmp) / 'census')
        subprocess.run([compiler, '-std=c++17', '-O2', str(HOME / 'census.cpp'), '-o', program], check=True)
        result = subprocess.run([program], input=search.census_input(), text=True, capture_output=True, check=True)
    rows = {}
    for line in result.stdout.splitlines():
        guard, conclusion, *costs = map(int, line.split())
        verifier.ensure(len(costs) == 4 and (guard, conclusion) not in rows, 'invalid census row')
        rows[guard, conclusion] = costs
    labels = {(g, l) for g in range(18) for l in range(18) if g//2 != l//2}
    verifier.ensure(set(rows) == labels and len(rows) == 288, 'incomplete signed coordinate list')
    histograms = [Counter(row[k] for row in rows.values()) for k in range(4)]
    verifier.ensure([(min(hist), hist[min(hist)]) for hist in histograms] == [(23,288),(23,72),(30,86),(30,62)],
                    'coordinate census extrema changed')
    verifier.ensure(rows[16,0] == [23,26,32,33], 'named literal sector')
    hist = [{('unreachable' if k == solver.INF else str(k)): v for k, v in sorted(h.items())} for h in histograms]
    return {'candidate_count': len(rows), 'reachable_affine_states': len(search.states),
            'literal_v0_implies_x0_zero': rows[16,0],
            'histograms_in_order_ordinary_single_common_outside': hist}


def reject(call, expected):
    try:
        call()
    except ValueError as error:
        verifier.ensure(expected in str(error), f'wrong rejection: {error}')
        return str(error)
    raise ValueError('invalid proof was accepted')


def negative_controls(proofs):
    errors = {}
    p = copy.deepcopy(proofs['old_crossing'])
    left = p['root'][2]
    verifier.ensure(left[0] == 'R' and left[1][0] == 'L', 'expected a paid guard-establishing check')
    p['root'][2] = left[1]
    errors['omit_a_paid_guard_check'] = reject(lambda: verifier.inspect(p), 'do not establish')
    witness = 320
    verifier.ensure(witness in verifier.sources(1)['P'] and witness in verifier.equation(4,0)
                    and witness not in verifier.equation(256,0), 'lost explicit wrong-guard witness')
    p = copy.deepcopy(proofs['old_single'])
    p['body'] = ['P']
    errors['unproved_discharge'] = reject(lambda: verifier.inspect(p), 'accepted a state')
    p['body'] = ['L', ['P']]
    errors['circular_citation'] = reject(lambda: verifier.inspect(p), 'circular')
    p = dict(proofs['old_single'], root=proofs['ordinary']['root'])
    errors['unused_declaration'] = reject(lambda: verifier.inspect(p), 'unreachable')
    p = copy.deepcopy(proofs['ordinary'])
    p['root'][1] = 512
    errors['hidden_product_question'] = reject(lambda: verifier.inspect(p), 'displayed')
    errors['wrong_common_guard'] = reject(lambda: verifier.hoist(proofs['old_crossing']), 'does not establish')
    errors['matched_totals'] = reject(lambda: verifier.inspect(proofs['ordinary'], charge=0), 'accepted a state')
    matched = len(verifier.sources(0)['R'] & verifier.sources(0)['P'])
    verifier.ensure(matched == 64, 'matched input count')
    return {'rejected': errors, 'plain_wrong_guard_witness': witness, 'matched_solutions': matched}


def checked_programs(search):
    programs = solver.chosen_proofs(search)
    saved = json.loads((HOME / 'certificates.json').read_text())
    verifier.ensure(programs == saved, 'saved certificates differ from their constructors')
    summary = {}
    for name, proof in programs.items():
        info = verifier.inspect(proof)
        actual = verifier.inspect(verifier.expand(proof))
        verifier.ensure(actual['cost'] <= info['textual_expansion_cost'], 'specialization increased the budget')
        info['specialized_ordinary_expansion_cost'] = actual['cost']
        if info['common_ancestor'] and not info['common_ancestor']['raw_outside_premise']:
            common = verifier.inspect(verifier.hoist(proof))
            verifier.ensure(common['cost'] <= info['cost'] - len(info['uses']) + 1, 'ancestor normalization failed')
            info['ordinary_after_common_ancestor_rewrite'] = common['cost']
        summary[name] = info
    costs = {name: data['cost'] for name, data in summary.items()}
    verifier.ensure(costs == {'ordinary':23, 'old_single':26, 'old_repeated':32, 'old_crossing':33,
                              'single_at_tree_optimum':23, 'best_repeated':30, 'best_crossing':30,
                              'old_delay_x2':32, 'old_hoisted':27, 'old_split_once':27, 'crossed_reordered':23},
                    'unexpected exact certificate charges')
    return summary, negative_controls(programs)


def ordinary_lower():
    good = frozenset(a | (b << 1) | (a*b << 2) for a in range(2) for b in range(2))
    bad = frozenset(range(8)) - good
    for local in (good, bad):
        verifier.ensure(len(verifier.span(local)) == 8, 'local source lost full affine span')
        for question in range(1, 8):
            answers = {(point & question).bit_count() % 2 for point in local}
            verifier.ensure(answers == {0, 1}, 'a base answer has only one source type')
    bounds = [5]
    for _ in range(2):
        bounds.append(1 + 2*bounds[-1])
    return {'local_good': sorted(good), 'local_bad': sorted(bad), 'local_questions': 7,
            'weighted_lower_by_number_of_triples': bounds}


def earlier_terminal_guards():
    shared = solver.old.verify(solver.old.six_terminal_certificate())
    uses = len(shared['rich_routes'])
    queries = shared['rules']['split']
    calls = shared['sequential_calls_then_support_visits']['right'][0] + uses
    scores = []
    sides = solver.old.evaluator_sets((1,6), 1)
    for node in solver.old.six_terminal_certificate(route=False)['nodes']:
        if node['rule'] == 'terminal':
            space = solver.old.guard_points(node['guard'])
            scores.append(min(solver.old.sequential(space, sides, first)[1] for first in ('left','right')))
    verifier.ensure((queries,calls,uses,sum(scores)) == (7,20,8,22), 'predecessor guard repricing')
    return {'queries':queries, 'evaluator_checks_including_guard_entailment':calls, 'terminal_citations':uses,
            'shared_work':queries+calls+uses, 'direct_same_questions_work':queries+sum(scores)}


def conclusions(result):
    orbit = result['one_affine_premise_full_census']
    direct = result['proofs']['ordinary']['cost']
    one_lower = min(map(int, orbit['lower_bound_by_representative_orientation']))
    covers = result['affine_covers']
    verifier.ensure(not covers['one_lagrangian_plus_five_caps_covers'] and not covers['two_cap_five_lagrangian_partition'],
                    'a low-cost source cover survived')
    forest_lower = min(2*6+9, 2*7+7, 2*8+5)
    verifier.ensure(one_lower == direct, 'single-implication proof gap')
    return {'ordinary_optimum': direct, 'optional_one_equation_implies_one_equation_optimum': one_lower,
            'old_named_training_and_main_interval': [orbit['named_v_zero_implies_x0_zero']['total_lower_bound'],
                                                     result['proofs']['old_single']['cost']],
            'optional_many_guarded_scalar_facts_interval': [forest_lower, direct]}


def main():
    search = solver.Search()
    summary, negatives = checked_programs(search)
    coordinates = census(search)
    del search
    # A larger menu contains the genuinely mixed questions of the predecessor guarded proofs.
    mixed = solver.Search(solver.AXES + (192,10,138,72,96))
    mixed_scores, mixed_programs = mixed.single((256,0), (1,0))
    verifier.ensure(mixed_scores == [23,26,32,33], 'old literal under mixed questions')
    verifier.ensure(all(verifier.inspect(p)['cost'] == mixed_scores[k] for k, p in mixed_programs.items()),
                    'mixed-menu certificates')
    mixed_report = {'query_masks': list(mixed.menu), 'states': len(mixed.states), 'scores': mixed_scores}
    del mixed
    raw_rich = io.StringIO()
    with redirect_stdout(raw_rich):
        rich_covers.main()
    result = {'status':'passed', 'proofs':summary, 'ordinary_embedding':ordinary_lower(), 'coordinate_census':coordinates,
              'earlier_terminal_guards':earlier_terminal_guards(),
              'mixed_menu_control':mixed_report, 'two_cheap_sectors':focused_cases.audit(),
              'live_guard_prefixes':guard_prefix.audit(), 'affine_covers':cap_obstructions.verify(),
              'one_affine_premise_full_census':one_premise_audit.audit(),
              'sector_bound':sector_audit.audit(), 'source_cover':json.loads(raw_rich.getvalue()),
              'negative_controls':negatives}
    result['work_bounds'] = conclusions(result)
    saved = HOME / 'checks.json'
    if saved.exists():
        verifier.ensure(json.loads(saved.read_text()) == json.loads(json.dumps(result)),
                        'saved numerical check record differs')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
