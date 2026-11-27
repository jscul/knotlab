"""Join fixed and arbitrary carrier tests to the eight-law and reading checks."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
NAMES = ('A0', 'A1', 'B0', 'B1', 'C0', 'C1')


def rows(name):
    with gzip.open(HERE / f'{name}.jsonl.gz', 'rt') as database:
        for line in database:
            yield json.loads(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pilot', action='store_true')
    args = ap.parse_args()
    before = perf_counter()
    pilot = {(2030, 3), (1278, 6), (90, 3), (0, 6)}
    def included(r):
        return not args.pilot or (r['start'], r['round']) in pilot
    scopes = {'all': Counter(), **{str(t): Counter() for t in range(7)}}
    stage_sets = {t: defaultdict(set) for t in range(7)}
    fixed = {}
    for stage in rows('other_bonds_paired_all'):
        if not included(stage):
            continue
        for query in stage['fixed_pairs']:
            groups = tuple(sorted(map(tuple, query['pair'])))
            for i, a in query['chain_and_pair_slots']:
                key = stage['start'], stage['round'], i + 1, a
                assert key not in fixed
                fixed[key] = groups, {tuple(b['third']) for b in query['bonds']}
    by_func = {}
    suffix = 'pilot' if args.pilot else 'counts'
    for r in rows('other_bonds_determination_' + suffix):
        if not included(r):
            continue
        key = r['start'], r['round'], r['chain_index_zero_based'] + 1, r['pair_index_zero_based']
        expected_pair, thirds = fixed[key]
        assert expected_pair == tuple(sorted(map(tuple, r['pair'])))
        assert set(r['mandatory']) == set().union(*map(set, r['pair']))
        assert not r['two_touching_groups_left_to_examine']
        assert [tuple(sorted(map(tuple, double))) for double in r['two_touching_groups']] == [expected_pair]
        determined = {tuple(sorted((*expected_pair, z))) for z in thirds}
        determined.update(tuple(sorted(map(tuple, b['groups']))) for b in r['determining_three_touching_bonds'])
        by_func[key + (r['mode'],)] = determined
    cross = Counter()
    locations = set()
    raw_starts = set()
    for r in rows('stage_readings'):
        if not included(r):
            continue
        start, t, chain = r['start'], r['round'], r['chain_number']
        key = start, t, chain
        raw_starts.add(start)
        frozen = r['frozen_fields']['a step']
        strict = r['strict_step_on_defining_bonds']
        all_named = {name: tuple(sorted(g)) for name, g in zip(NAMES, r['carriers'])}
        bonds_on_six = set()
        for b in r['other_bonds_on_the_six_named_readings']:
            bond = tuple(sorted(all_named[j] for j in b['readings']))
            for pos, (both_fixes, either_fixes) in enumerate(b['mixed_fixes_by_upper_pair_and_function']):
                for mode, mixed in [('both', both_fixes), ('either', either_fixes)]:
                    if not mixed:
                        assert bond in by_func[key + (pos, mode)]
                        bonds_on_six.add((pos, bond))
        lost = []
        pair_witnesses = set()
        for pos in range(3):
            a = by_func[key + (pos, 'both')]
            b = by_func[key + (pos, 'either')]
            if a or b:
                lost.append(pos)
                pair_witnesses.update((pos, q) for q in a | b)
        assert bonds_on_six == {(pos, q) for pos, q in pair_witnesses if all(g in all_named.values() for g in q)}
        independent_roles = [
            all(not by_func[key + (pos, 'both' if pos == role else 'either')] for pos in range(3))
            for role in range(3)
        ]
        assert all(independent_roles) == (not lost)
        if lost:
            locations.add((start, t))
        final = strict and not lost
        cross[f'frozen={int(frozen)},all_eight={int(strict)},all_stage_bonds_pass={int(not lost)}'] += 1
        for counter in (scopes['all'], scopes[str(t)]):
            counter['checked_chains'] += 1
            counter['frozen_step'] += int(frozen)
            counter['frozen_plus_eight_deletions_and_defining_bond_test'] += int(strict)
            counter['one_or_more_determining_bonds'] += int(bool(lost))
            counter['affected_upper_pairs_across_chains'] += len(lost)
            counter['determining_bonds_by_chain_and_upper_pair'] += len(pair_witnesses)
            counter['determining_bonds_using_only_the_six_named_carriers_by_chain_and_pair'] += len(bonds_on_six)
            counter['failed_arbitrary_bond_test_but_passed_same_six_test'] += int(bool(lost) and not bonds_on_six)
            counter['all_stage_bonds_pass'] += int(not lost)
            counter['frozen_and_all_stage_bonds_pass'] += int(frozen and not lost)
            counter['all_checks_pass'] += int(final)
            counter['complete_roles'] += sum(
                independent_roles[role] and frozen and all(x[role] for x in r['by_single_chain_law_deletion_upper_111_restored'])
                for role in range(3)
            )
        for label, flag in [('chain', True), ('frozen', frozen), ('all_checks', final)]:
            if flag:
                stage_sets[t][label].add(start)
    first = Counter()
    seen = set()
    lost_earlier = {}
    for t in range(7):
        strong = stage_sets[t]['all_checks']
        first[t] = len(strong - seen)
        lost_earlier[t] = sorted(seen - strong)
        seen |= strong
        for label in ('chain', 'frozen', 'all_checks'):
            scopes[str(t)][f'starts_holding_{label}_on_checked_chains'] = len(stage_sets[t][label])
        scopes[str(t)]['starts_with_a_checked_step_on_an_earlier_or_current_stage'] = len(seen)
    assert 2 * len(fixed) == len(by_func) == 6 * scopes['all']['checked_chains']
    result = {'scope': 'Up to three checked chains per stage. Each upper reading is compared with every eligible stage bond.',
              'pilot': args.pilot, 'counts': scopes, 'cross_counts': cross,
              'stages_with_determining_bonds': len(locations), 'starts_with_determining_bonds': len({i for i, t in locations}),
              'starts_with_any_checked_chain': len(raw_starts), 'starts_with_any_complete_checked_step': len(seen),
              'first_round_with_a_complete_checked_step': first,
              'previously_positive_starts_without_a_complete_checked_step_in_this_round': lost_earlier,
              'seconds': round(perf_counter() - before, 3)}
    tag = '_pilot' if args.pilot else ''
    (HERE / f'other_bonds_summary{tag}.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'checked': scopes['all'], 'first': first, 'seconds': result['seconds']}, separators=(',', ':')))


if __name__ == '__main__':
    main()
