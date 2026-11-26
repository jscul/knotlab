"""Check recorded growth, returns and selected comparisons from frozen inputs."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import resource
from time import perf_counter, process_time

from growth_comparisons import examine, own_and_joint, sum_after
from growth_model import Growth, Law, Returns, Shape, Span, mask_of, maximal_sets, member_parts


ROOT = Path(__file__).resolve().parents[3]
TICKET = 'TIME-AS-FOLD-20261125-001A'
ARTIFACTS = ROOT / 'artifacts' / TICKET / f'{TICKET}-E001_count_of_returns'
INPUT = ROOT / 'research' / TICKET
KEYS = ('group', 'start', 'base', 'rule', 'choice', 'knot_law')
MISSING = ('fbp', 'DW(5,3)', 'COPY-LAW(WAIT)', 'STEPS-3:join', 'BY-COUNT', 'parity')
FAILED_KNOTS = ('main', 'two-knot', 'RING-LAW', 'MET', 'NEWEST', 'parity')
NAMED = (
    ('main', 'Ring(5,3)', 'RING-LAW', None, 'OLDEST', 'nae'),
    ('main', 'two-knot', 'COPY-LAW(OFFSHOOT)', 'STEPS-1', 'OLDEST', 'nae'),
    ('main', 'two-knot', 'COPY-LAW(WAIT)', 'STEPS-2:join', 'OLDEST', 'parity'),
    FAILED_KNOTS,
    ('main', 'Ring(9,3)', 'RING-LAW', 'MET', 'IN-TURN', 'parity'),
    ('main', 'D2(4,3)', 'CAP-3(RETIRE)', 'MET', 'NEWEST', 'nae'),
    ('main', 'D2(5,3)', 'CAP-3(OFFSHOOT)', 'MET:offshoot', 'BY-COUNT', 'nae'),
    ('main', 'D2(6,3)', 'COPY-LAW(RETIRE)', 'UP-TO-2', 'IN-TURN', 'parity'),
    ('main', 'DW(5,3)', 'RING-LAW', 'MET:join', 'BY-COUNT', 'nae'),
    ('main', 'Ring(5,4)', 'COPY-LAW(OFFSHOOT)', 'STEPS-2', 'BY-COUNT', 'parity'),
    ('main', 'Ring(7,3)', 'RING-LAW+FILLERS', 'STEPS-1:join', 'NEWEST', 'nae'),
    ('main', 'three-knot', 'RING-LAW+FILLERS', 'Q', 'OLDEST', 'nae'),
    ('fbp', 'three-knot-larger', 'COPY-LAW(WAIT)', 'STEPS-2:offshoot', 'NEWEST', 'parity'),
    ('dbt', 'generator7', 'CAP-3(RETIRE)', 'MET', 'NEWEST', 'nae'),
    MISSING,
)
LADDER = (
    ('ladder', 'Ring(5,3)', 'RING-LAW', 'STEPS-1', 'IN-TURN', 'nae'),
    ('ladder', 'Ring(9,3)', 'RING-LAW', 'STEPS-8', 'OLDEST', 'parity'),
    ('ladder', 'Ring(7,3)', 'RING-LAW', 'STEPS-4', 'BY-COUNT', 'nae'),
    ('ladder', 'D2(5,3)', 'RING-LAW', 'STEPS-2', 'NEWEST', 'parity'),
)
BAR_CASES = (
    ('main', 'two-knot', 'COPY-LAW(OFFSHOOT)', 'STEPS-1', 'OLDEST', 'nae'),
    ('main', 'Ring(5,3)', 'COPY-LAW(OFFSHOOT)', 'STEPS-2', 'BY-COUNT', 'nae'),
    ('main', 'two-knot', 'COPY-LAW(WAIT)', 'STEPS-2:join', 'OLDEST', 'parity'),
    ('main', 'Ring(5,3)', 'RING-LAW', None, 'OLDEST', 'nae'),
)


def read_rows(file):
    with gzip.open(ARTIFACTS / file, 'rt') as f:
        yield from map(json.loads, f)


def key(row):
    return tuple(row[k] for k in KEYS)


def get_starts():
    source = json.loads((INPUT / 'starts.json').read_text())
    census = {
        f"atlas {row['atlas_index']} loose {','.join(map(str, row['loose']))}": row['stars']
        for row in source['ring_study_returning_starts']
    }
    return source['named'] | census, list(census)


def replay(starts, item, rounds=18, bound=4000):
    return Growth(starts[item['start']], Law.from_record(item)).grow(rounds, bound)


def coarse_replay(growth, expected):
    checked = {}
    checks = {
        'rounds': growth.round_count(),
        'knots': len(growth.knots),
        'births': sum(k.born != 0 for k in growth.knots),
        'stop': growth.stop,
        'stopped': not growth.rosters[-1].members,
        'jammed': bool(growth.rosters[-1].members and growth.records and not growth.records[-1][-1]),
        'per_round': growth.summary_rounds(),
        'first_take_round': next((k.born for k in growth.knots if k.take), None),
        'first_offshoot_take_round': next((k.born for k in growth.knots if k.take and len(k.parents) == 1), None),
    }
    if 'start_roster_returns' in expected:
        checks['start_roster_returns'] = growth.start_returns()
        start = growth.rosters[0]
        ring_members = set(start.members)
        for t in checks['start_roster_returns']:
            roster = growth.rosters[t]
            # The previously specified ring identification uses the same full roster.
            whole = Shape(start.members, start.h, start.k, maximal_sets(start.met_sets))
            for part, shape in roster.shapes.items():
                if whole.same(shape):
                    ring_members.update(part)
        checks['ring_member_offshoot_first_take'] = next((
            k.born for k in growth.knots if k.take and len(k.parents) == 1 and k.parents[0] in ring_members
        ), None)
    if expected['guard'] is not None:
        guard = expected['guard']
        expected_guard = ('demand ' if guard['where'].startswith('demand') else '') + {
            'pairs': 'joinable pairs',
            'incidence': 'holder incidences',
            'incidences': 'holder incidences',
            'cliques': 'maximal cliques',
            'births': 'births',
            'groups': 'groups',
            'distinctions': 'distinctions',
            'vars': 'distinctions',
        }.get(guard['what'], guard['what'])
        if growth.guard != expected_guard:
            checked['guard'] = {'recorded': guard, 'replayed': growth.guard}

    for label, actual in checks.items():
        if label in expected and actual != expected[label]:
            checked[label] = {'recorded': expected[label], 'replayed': actual}
    return checked


def return_checks(growth, expected, detailed=False, through_roster=True):
    differing = {}
    counts = {}
    prefix_names = ('past', 'nopast') if detailed else ('past', 'nopast', 'past_greatest', 'nopast_greatest')
    for name in prefix_names:
        if not through_roster and name.startswith('no'):
            continue
        field = f'series_{name}' if detailed else f'{name}_series'
        if field not in expected:
            continue
        greatest = name.endswith('greatest')
        returns = Returns(growth, not name.startswith('no'), greatest, through_roster)
        full_series = returns.records(include_single=not greatest)
        multi = [row for row in full_series if row['size'] > 1]
        if detailed:
            series = [row for row in full_series if row['ticks_off'] >= 2]
            exposed = series
        else:
            # These two limits are properties of the archive exports. All
            # aggregate readings below use the complete independently grown run.
            series = [row for row in full_series if row['size'] > 1 or row['ticks_off']]
            exposed = series[:200]
        counts[name] = {
            'eligible_series_before_export_cap': len(series),
            'one_member_series_before_export_cap': sum(row['size'] == 1 for row in series),
            'recorded_series_checked': len(expected[field]),
            'recorded_ticks_checked': sum(len(s['ticks']) for s in expected[field]),
        }
        order = lambda s: (s['t0'], s['P0'])
        row_diffs = {}
        if sorted(exposed, key=order) != sorted(expected[field], key=order):
            difference = set(json.dumps(r, sort_keys=True) for r in exposed) ^ set(
                json.dumps(r, sort_keys=True) for r in expected[field]
            )
            row_diffs['listed_series'] = {
                'differing_rows': len(difference),
                'first_three': [json.loads(s) for s in sorted(difference)[:3]],
                'recorded_count': len(expected[field]), 'replayed_count': len(exposed),
            }
        if detailed:
            if row_diffs:
                differing[name] = row_diffs
            continue
        endless = returns.endless()
        single_field = f'{name}_endless'
        if single_field in expected:
            if sorted(endless[:50]) != sorted(expected[single_field]):
                row_diffs['endless'] = {'recorded_count': len(expected[single_field]), 'replayed_count': len(endless[:50])}
            counts[name]['recorded_endless_series_checked'] = len(expected[single_field])
            counts[name]['endless_series_before_export_cap'] = len(endless)
        for field, observed in returns.metrics(multi, endless).items():
            if field in expected[name] and expected[name][field] != observed:
                row_diffs[field] = {'recorded': expected[name][field], 'replayed': observed}
        if row_diffs:
            differing[name] = row_diffs
    return counts, differing


def listing_checks(growth, expected):
    rows = growth.listing()
    differed_rounds = []
    for actual, recorded in zip(rows, expected):
        mismatches = [field for field in actual if actual[field] != recorded[field]]
        if not mismatches:
            continue
        mismatch_row = {'round': actual['round'], 'fields': mismatches}
        if 'births' in mismatches:
            left, right = actual['births'], recorded['births']
            mismatch_row['births'] = {
                'replayed_count': len(left), 'recorded_count': len(right),
                'mismatch_fields': dict(Counter(
                    k for a, b in zip(left, right) for k in a if a[k] != b[k]
                )),
                'first_mismatch': next((
                    {'replayed': a, 'recorded': b} for a, b in zip(left, right) if a != b
                ), None),
            }
        differed_rounds.append(mismatch_row)
    return {
        'replayed_rounds': len(rows),
        'recorded_rounds': len(expected),
        'replayed_births': sum(len(row['births']) for row in rows),
        'recorded_births': sum(len(row['births']) for row in expected),
        'differing_round_count': len(differed_rounds) + abs(len(rows) - len(expected)),
        'first_differing_rounds': differed_rounds[:3],
    }


def parity_checks(growth, expected):
    final_ranks = []
    count = literal_failures = 0
    for t in range(growth.round_count() + 1):
        knots = [k for k in growth.knots if k.born <= t]
        rows = [mask_of(k.places) for k in knots]
        span = Span()
        for row in rows:
            span.add(row)
        ranks = []
        for s in rows:
            outside = Span()
            for row in rows:
                outside.add(row & ~s)
            ranks.append(len(span.pivots) - len(outside.pivots))
        count += len(ranks)
        literal_failures += sum(r != 1 for r in ranks)
        final_ranks = ranks
    failing = [
        {'knot': i, 'made': k.born, 'places': len(k.places), 'parents': len(k.parents),
         'kind': 'join' if len(k.parents) > 1 else 'offshoot', 'how': 'parity'}
        for i, (k, rank) in enumerate(zip(growth.knots, final_ranks)) if rank != 1
    ]
    return {
        'fail_rows': failing,
        'same_fail_rows': failing == expected['kt']['fail_rows'],
        'literal_verdicts': count,
        'literal_fails': literal_failures,
        'same_literal_counts': (count, literal_failures) == (
            expected['literal']['verdicts'], expected['literal']['fails']
        ),
    }


def no_comparison_diff(actual, expected):
    # Compare quantities available in both records and keep every difference.
    differences = {}
    for field in ('tick_rounds', 'P_j', 'own_A_per_period', 'joint_A_per_period', 'clause1', 'verdict_C', 'verdict_C_iii'):
        if actual[field] != expected[field]:
            differences[field] = [expected[field], actual[field]]
    for section in ('X_barred', 'run_A'):
        for field, value in actual[section].items():
            if value != expected[section][field]:
                differences[f'{section}.{field}'] = [expected[section][field], value]
    for i, (bar, ref) in enumerate(zip(actual['bars'], expected['bars']), 1):
        if 'course_differs' not in bar and 'course_differs' in ref:
            differences[f'bar_{i}.examined'] = [True, False]
        for field, value in bar.items():
            if field not in ref:
                continue
            if isinstance(value, dict) and isinstance(ref[field], dict):
                for k, v in value.items():
                    if k in ref[field] and ref[field][k] != v:
                        differences[f'bar_{i}.{field}.{k}'] = [ref[field][k], v]
            elif field in ('B', 'M', 'B\'', 'Ball', 'r', 't_bar', 'X_desc_in_barred_part',
                           'course_differs', 'demand_differs', 'grown_2_periods', 'grown_4_periods',
                           'own_A_after_bar_by_round', 'own_B_after_bar_by_round', 'joint_B_after_bar',
                           'own_after_lag_rounds', 'e', 'M_equals_B_2', 'M_equals_B_4',
                           'M_differs_from_B_at', 'c_iii') and value != ref[field]:
                differences[f'bar_{i}.{field}'] = [ref[field], value]
    return differences


def group_bars(growth, choose_every_clock=False, whole_period_tuple=False):
    returns = Returns(growth)
    all_clocks = [record for record in returns.records() if record['clock']]
    representatives = {}
    for clock in all_clocks:
        periods = tuple(clock['periods'])
        if not whole_period_tuple:
            periods = tuple(sorted(set(periods)))
        form = clock['size'], periods, clock['t0'] % 2
        if form not in representatives or clock['P0'][0] < representatives[form]['P0'][0]:
            representatives[form] = clock
    selected_clocks = all_clocks if choose_every_clock else representatives.values()
    pairs = []
    eligible_choices = 0
    for clock in selected_clocks:
        members = [tuple(clock['P0'])] + [tuple(tick[1]) for tick in clock['ticks']]
        rounds = [clock['t0']] + [tick[0] for tick in clock['ticks']]
        periods = clock['periods']
        for j in (0, 1):
            if len(periods[j:j + 4]) != 4 or len(set(periods[j:j + 4])) != 1:
                continue
            eligible_choices += 1
            selected = rounds[j]
            y = members[j]
            roster = growth.rosters[selected]
            links = {u: roster.adjacency[u] | roster.direct[u] for u in roster.members}
            y_class = next(frozenset(p) for p in member_parts(links) if y[0] in p)
            eligible = [
                part for part in roster.parts
                if not y_class.intersection(part) and any(growth.knots[u].born > 0 for u in part)
            ]
            for x in eligible[:8]:
                own, joint = own_and_joint(growth, x, y, selected)
                counts = [sum_after(own, rounds[i], rounds[i + 1]) for i in range(j, j + 4)]
                pairs.append({
                    't0': clock['t0'], 'P0': clock['P0'], 'j': j, 't_j': selected, 'Y': list(y), 'X': list(x),
                    'period': periods[j], 'own': counts,
                    'joint': [sum_after(joint, rounds[i], rounds[i + 1]) for i in range(j, j + 4)],
                    'clause1': len(set(counts)) == 1 and counts[0] > 0,
                })
    return {
        'all_clocks': len(all_clocks),
        'forms': len(representatives),
        'eligible_clock_and_j_choices': eligible_choices,
        'pairs_tested_for_clause1': len(pairs),
        'passes_clause1': sum(p['clause1'] for p in pairs),
        'pairs': pairs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('listed', 'summary', 'bars', 'omitted'))
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ceiling = 3 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    start_wall = perf_counter()
    start_cpu = process_time()
    starts, census = get_starts()
    rows = []

    if args.phase == 'listed':
        chosen = {2, 12, 44} if args.pilot else set(range(52))
        for i, row in enumerate(read_rows('replay_census_listings.jsonl.gz')):
            if i not in chosen:
                continue
            mark = perf_counter()
            case = row['item']
            growth = replay(starts, case)
            result = listing_checks(growth, row['rounds'])
            counts, differences = return_checks(growth, row, detailed=True)
            _, part_local_diffs = return_checks(growth, row, detailed=True, through_roster=False)
            rows.append({'row': i + 1, 'item': case, 'listing': result, 'series_counts': counts,
                         'series_differences': differences, 'within_part_filter_differences': part_local_diffs,
                         'stop': growth.stop, 'wall_s': perf_counter() - mark})

    if args.phase == 'summary':
        sample = tuple(
            ('ring227', name, 'RING-LAW', rule, choice, logic)
            for name in (census[0], census[len(census) // 2], census[-1])
            for rule, choice, logic in ((None, 'OLDEST', 'nae'), ('MET', 'BY-COUNT', 'parity'))
        )
        want = set(NAMED + LADDER + sample)
        if args.pilot:
            want = {NAMED[0], NAMED[3], LADDER[1], sample[-1]}
        files = [f'run1_part{i}.jsonl.gz' for i in range(1, 9)] + ['run2.jsonl.gz', 'run3.jsonl.gz']
        found = {}
        for file in files:
            for row in read_rows(file):
                case = key(row)
                if case in want:
                    if case in found:
                        raise ValueError(f'duplicate source row: {case}')
                    found[case] = (file, row)
        if set(found) != want:
            raise ValueError(f'missing rows: {sorted(want - set(found), key=str)}')
        for case in sorted(want, key=str):
            mark = perf_counter()
            file, expected = found[case]
            ladder = expected['group'] == 'ladder'
            rounds = 2 * expected['k'] + 4 if ladder else 18
            growth = replay(starts, expected, rounds, 6000 if ladder else 4000)
            counts, differences = return_checks(growth, expected)
            _, part_local_diffs = return_checks(growth, expected, through_roster=False)
            row = {'item': dict(zip(KEYS, case)), 'source': file, 'rounds': growth.round_count(),
                   'knots': len(growth.knots), 'stop': growth.stop, 'round_differences': coarse_replay(growth, expected),
                   'series_counts': counts, 'series_differences': differences,
                   'within_part_filter_differences': part_local_diffs, 'wall_s': perf_counter() - mark}
            if case == FAILED_KNOTS:
                target = next(o for o in read_rows('run7_runA.jsonl.gz') if key(o) == case)
                row['parity'] = parity_checks(growth, target)
            rows.append(row)

    if args.phase == 'bars':
        want = {BAR_CASES[2]} if args.pilot else set(BAR_CASES)
        seen = set()
        for row in read_rows('run4.jsonl.gz'):
            case = key(row)
            wanted_verdict = 'fails' if row['rule'] is None else 'holds'
            if case not in want or case in seen or row['verdict_C_iii'] != wanted_verdict:
                continue
            mark = perf_counter()
            growth = replay(starts, row)
            selection = group_bars(growth)
            pair = next((
                candidate for candidate in selection['pairs']
                if all(candidate[field] == row[field] for field in ('t0', 'P0', 'j', 'X'))
            ), None)
            observed = examine(growth, row)
            differences = no_comparison_diff(observed, row)
            if pair is None:
                differences['registered_pair_is_selected'] = [True, False]
            rows.append({'item': dict(zip(KEYS, case)), 't0': row['t0'], 'P0': row['P0'],
                         'j': row['j'], 'X': row['X'], 'wall_s': perf_counter() - mark,
                         'registered_pair_is_selected': pair is not None,
                         'eligible_pairs_in_source': selection['pairs_tested_for_clause1'],
                         'differences': differences, 'replay': observed})
            seen.add(case)
        if seen != want:
            raise ValueError(f'missing cases: {want - seen}')

    if args.phase == 'omitted':
        case = dict(zip(KEYS, MISSING))
        growth = replay(starts, case)
        variants = [('recorded_run_4_grouping', False, False)]
        if not args.pilot:
            variants += [('whole_period_tuple_grouping', False, True), ('every_clock', True, False)]
        for label, every, whole in variants:
            observed = group_bars(growth, every, whole)
            rows.append({'item': case, 'variant': label, 'rounds': growth.round_count(),
                         'knots': len(growth.knots), 'stop': growth.stop, 'replay': observed})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump({
            'phase': args.phase,
            'pilot': args.pilot,
            'wall_s': perf_counter() - start_wall,
            'process_s': process_time() - start_cpu,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'address_space_limit_bytes': ceiling,
            'rows': rows,
        }, f, indent=2)
        f.write('\n')
    print(f'{args.phase}: {len(rows)} recorded comparisons, {perf_counter() - start_wall:.2f} s')


if __name__ == '__main__':
    main()
