"""Recount the first checkpoint from its archived tables of individual cases."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
from statistics import median, median_high


RECORD = Path(__file__).resolve().parents[1]
PRIOR_CENSUS = RECORD.parent / 'TWO-PATTERNS-20261126-001' / 'census' / 'census_runs.jsonl.gz'
RATIONS = ('ORD', 'ODD-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'THIRD-FEWER')
WAIT, RETIRE, OFFSHOOT = ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')
TREATMENTS = (WAIT, RETIRE, OFFSHOOT)
SMALL = ('g7:112@0', 'g6:133@0', 'g6:123@0', 'g6:122@0')
BENCH = ('ring', 'copier', 'source')


def rows(stem, limit=None):
    if stem == 'receivers':
        return json.loads((RECORD / 'receivers.json').read_text())[:limit]
    path = PRIOR_CENSUS if stem == 'prior_census' else RECORD / f'{stem}.jsonl.gz'
    result = []
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            result.append(json.loads(line))
            if len(result) == limit:
                break
    return result


def last_round(series):
    return max((i for i, value in enumerate(series, 1) if value), default=0)


def fresh(ration, places_given, demand):
    floor = max(3 - places_given, 1)
    reduction = {
        'ORD': False,
        'ODD-FEWER': demand % 2 == 1,
        'BUSY-FEWER': places_given > 1 and demand > places_given,
        'ONE-FEWER': True,
        'JOIN-FEWER': places_given > 1,
        'THIRD-FEWER': demand % 3 == 2,
    }[ration]
    return max(floor, demand - reduction)


def law_bins(cases, key):
    result = defaultdict(list)
    for row in cases:
        result[key(row)].append(row)
    return result


def check_factor_cells(cases, expected, key):
    recorded = Counter(key(row) for row in cases)
    return {
        'missing': sorted(set(expected) - recorded.keys()),
        'unexpected': sorted(recorded.keys() - set(expected)),
        'duplicates': sorted(k for k, v in recorded.items() if v > 1),
    }


def reach(rows_in, complete):
    cases = [row for row in rows_in if 'changes' in row]
    result = {'cases_read': len(cases), 'baseline_rounds': Counter(r['rounds'] for r in cases)}
    if complete:
        result['coverage'] = check_factor_cells(
            cases, list(product(SMALL, SMALL, range(1, 9), RATIONS, TREATMENTS)),
            lambda r: (r['A'], r['B'], r['d'], *r['law']))
    by_law = law_bins(cases, lambda r: ' / '.join(r['law']))
    result['by_law'] = {}
    result['late_cancelled_groups'] = []
    result['two_or_more'] = []
    demand = Counter()
    for law, members in by_law.items():
        short_rounds = [sum(bool(x) for x in r['short']) for r in members]
        bins = defaultdict(Counter)
        comparisons = Counter()
        joint = Counter()
        for row in members:
            assert len(row['kept']) == len(row['short']) == len(row['own births']) == len(row['joint births']) == row['rounds']
            if complete:
                # The meeting supplies one usable loose distinction at each end.
                expected_changes = {'B0', 'B1', 'B2', 'two', 'less', *(f'L{x}' for x in range(1, row['d']))}
                assert set(row['changes']) == expected_changes
            for k, v in row.get('demand', []):
                demand[tuple(k)] += v
            for label, read in row['changes'].items():
                # All three knots are pairwise joined or the marked site is the middle knot.
                if label.startswith('L'):
                    steps = int(label[1:])
                else:
                    steps = row['d'] + (label in ('B1', 'B2'))
                assert 0 < read['rounds'] <= row['rounds']
                assert all(0 < x <= read['rounds'] for k, x in read.items() if k != 'rounds' and x is not None)
                tally = bins[min(steps, 4)]
                tally['tried'] += 1
                tally['read_through_7'] += read['rounds'] >= 7
                tally['read_through_16'] += read['rounds'] == 16
                tally['heard'] += read['own'] is not None
                comparisons[read['rounds']] += 1
                joint[read['joint'] or 0] += 1
                detail = [row['A'], row['B'], row['d'], *row['law'], label, steps, read['own'], read['groups']]
                if read['own'] and steps >= 2:
                    result['two_or_more'].append(detail)
                if read['own'] and (read['groups'] is None or read['groups'] > read['own']):
                    result['late_cancelled_groups'].append(detail)
        result['by_law'][law] = {
            'cases': len(members),
            'kept_in_last_round': sum(bool(r['kept'][-1]) for r in members),
            'latest_kept': Counter(last_round(r['kept']) for r in members),
            'last_round_of_shortness': Counter(last_round(r['short']) for r in members),
            'median_short_rounds': median(short_rounds),
            'upper_median_short_rounds': median_high(short_rounds),
            'receiver_alone_births_last_round': sum(r['alone']['own births, last round'] > 0 for r in members),
            'by_steps_4_is_4_or_more': dict(bins),
            'comparison_rounds': comparisons,
            'joint_hearings_by_round_0_unheard': joint,
        }
    result['ordinary_birth_demand'] = [(*k, v) for k, v in sorted(demand.items())]
    result['ordinary_births_short_under_ration'] = {}
    for ration in RATIONS:
        counts = Counter()
        for (owner, _, p, d), count in demand.items():
            counts[owner] += count if d > fresh(ration, p, d) else 0
        result['ordinary_births_short_under_ration'][ration] = counts
    return result


def made(rows_in, bench, complete):
    cases = [r for r in rows_in if 'reads' in r]
    lost = [r for r in rows_in if 'not run' in r]
    rounds_key = 'rounds read' if bench else 'rounds'
    short_key = 'short members by round' if bench else 'short'
    result = {
        'cases_read': len(cases),
        'missing_cases': lost,
        'baseline_rounds': Counter(r[rounds_key] for r in cases),
        'late_hearings': [],
        'by_law': {},
    }
    if complete and bench:
        expected = [(*pair, d, join, ration, treatment) for pair, d, join, ration, treatment in product(
            combinations_with_replacement(BENCH, 2), range(1, 4), ('meeting', 'share'), RATIONS[1:], TREATMENTS)]
        result['coverage'] = check_factor_cells(cases, expected,
                                               lambda r: (r['A'], r['B'], r['steps'], r['join'], *r['law'][:2]))
    elif complete:
        expected = [(*pair, join, ration, treatment) for pair, join, ration, treatment in product(
            combinations_with_replacement(range(44), 2), ('meeting', 'share'), RATIONS[1:3], TREATMENTS)]
        result['coverage'] = check_factor_cells(cases, expected, lambda r: (r['i'], r['j'], r['join'], *r['law']))
        roster_index = {r[k]: r[p] for r in cases for k, p in (('i', 'A'), ('j', 'B'))}
        result['sited_starts_in_record_order'] = [roster_index[i] for i in range(44)]
    for key, members in law_bins(cases, lambda r: ' / '.join((r['join'], *r['law'][:2]))).items():
        tally = Counter(cases=len(members), two_readings_per_case=2 * len(members))
        first = Counter()
        comparison_rounds = Counter()
        upper_bound_rounds = Counter()
        marks_per_marked_pattern_size = defaultdict(Counter)
        for row in members:
            n = row[rounds_key]
            assert len(row[short_key]) == n
            tally['short_in_half_the_rounds_or_more'] += 2 * sum(bool(x) for x in row[short_key]) >= n
            tally['baseline_read_through_7'] += n >= 7
            for orientation in 'AB':
                read = row['reads'][orientation]
                if bench:
                    marks = [(int(i), a['own making first differs'], a['joint descent first differs'], a['rounds compared'])
                             for i, a in read['mark at a start knot of the other'].items()]
                    kept = last_round(read['kept by round'])
                else:
                    marks = [(i, own, joint, None) for i, (own, joint) in enumerate(read['marks'])]
                    kept = read['last kept']
                tally['directed_readings_with_hearing'] += any(own is not None for _, own, _, _ in marks)
                tally['kept_in_last_round'] += kept == n
                for i, own, joint, compared in marks:
                    bound = n if compared is None else compared
                    assert bound <= n
                    assert all(0 < x <= bound for x in (own, joint) if x is not None)
                    tally['marks'] += 1
                    tally['heard_by_joint'] += joint is not None
                    tally['heard_by_own'] += own is not None
                    first[own or 0] += 1
                    upper_bound_rounds[n] += 1
                    if compared is not None:
                        comparison_rounds[compared] += 1
                    marks_per_marked_pattern_size[len(marks)]['marks'] += 1
                    marks_per_marked_pattern_size[len(marks)]['heard'] += own is not None
                    if (own or 0) > 6:
                        result['late_hearings'].append({
                            'A': row['A'], 'B': row['B'], 'receiver_role': orientation,
                            'law': row['law'][:2], 'join': row['join'], 'd': row.get('steps', 1),
                            'marked_knot': i, 'heard_round': own, 'compared_rounds': compared,
                            'baseline_rounds': n,
                        })
        result['by_law'][key] = {
            **tally,
            'first_heard_by_round_0_unheard': first,
            'comparison_rounds': dict(comparison_rounds),
            'comparison_rounds_upper_bounds': upper_bound_rounds,
            'marks_per_marked_pattern_size': dict(marks_per_marked_pattern_size),
        }
    return result


def made_mark(rows_in, complete):
    result = {'studies': len(rows_in), 'baseline_rounds': Counter(r['rounds'] for r in rows_in), 'by_law': {}}
    if complete:
        result['coverage'] = check_factor_cells(rows_in, list(product(SMALL, SMALL, (2, 4), RATIONS[:3], TREATMENTS)),
                                               lambda r: (r['A'], r['B'], r['d'], *r['law']))
    for key, members in law_bins(rows_in, lambda r: ' / '.join(r['law'])).items():
        per_steps = defaultdict(Counter)
        compared_rounds = Counter()
        own_rounds = Counter()
        for row in members:
            for owner, steps, own, n, short_only_in_marked in row['marks']:
                assert own is None or 6 < own <= n
                assert 6 <= n <= row['rounds']
                tally = per_steps[str(min(steps, 4)) if steps is not None else 'disconnected']
                tally['marks'] += 1
                tally['heard'] += own is not None
                tally['through_round_8'] += n >= 8
                tally['marked_only_short_round_present'] += short_only_in_marked > 0
                own_rounds[own or 0] += 1
                compared_rounds[n] += 1
        result['by_law'][key] = {
            'studies': len(members),
            'marks': sum(v['marks'] for v in per_steps.values()),
            'by_holder_steps_4_is_4_or_more': dict(per_steps),
            'first_heard_by_round_0_unheard': own_rounds,
            'comparison_rounds': compared_rounds,
        }
    return result


def far(rows_in, complete):
    result = {'cases': len(rows_in), 'baseline_rounds': Counter(r['rounds'] for r in rows_in), 'by_law': {}}
    if complete:
        result['coverage'] = check_factor_cells(rows_in, list(product(range(1, 9), RATIONS, (WAIT, RETIRE))),
                                               lambda r: (r['d'], *r['law']))
    for key, members in law_bins(rows_in, lambda r: ' / '.join(r['law'])).items():
        result['by_law'][key] = {}
        for row in members:
            d = row['d']
            if complete:
                assert set(row['changes']) == {'two', 'less', *(f'B{i}' for i in range(7)), *(f'L{i}' for i in range(1, d))}
            changed = row['changes']
            first = {k: v['own'] for k, v in changed.items() if v['own'] is not None}
            result['by_law'][key][d] = {
                'baseline_rounds': row['rounds'], 'baseline_stop': row['ended'],
                'changes': len(changed), 'comparison_rounds': Counter(v['rounds'] for v in changed.values()),
                'first_heard': first,
                'cancelled_group_read_late': [k for k, v in changed.items()
                                              if v['own'] is not None and (v['groups'] is None or v['groups'] > v['own'])],
            }
    return result


def receiver_controls(rows_in):
    return [r for r in rows_in if any(r['B marks heard']) or any(r['link marks']) or r['two'] or r['less']]


def earlier_census(rows_in):
    by_law = defaultdict(Counter)
    selected = defaultdict(dict)
    for row in rows_in:
        if 'reads' not in row:
            continue
        key = ' / '.join((row['join'], *row['law']))
        by_law[key]['cases'] += 1
        for side, other in ('AB', 'BA'):
            read = row['reads'][side]
            by_law[key]['marks'] += len(read['marks'])
            by_law[key]['heard'] += sum(own is not None for own, _ in read['marks'])
            if row[side] in SMALL and row['join'] == 'meeting' and row['law'] == ['ORD', WAIT]:
                kept_in_last = read['last kept'] == row['rounds']
                selected[row[side]][row[other]] = kept_in_last and read['own births'][-1] > 0
    return {'comparison_cells': dict(by_law),
            'selected_receivers_in_ordinary_meetings': {r: {
                'partners': len(by_partner), 'kept_join_and_own_birth_in_last_round': sum(by_partner.values()),
            } for r, by_partner in selected.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='Read a small prefix of each record.')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    limit = 3 if args.pilot else None
    result = {
        'reach': reach(rows('reach_runs', limit), not args.pilot),
        'bench': made(rows('made_bench', limit), bench=True, complete=not args.pilot),
        'census': made(rows('made_census', limit), bench=False, complete=not args.pilot),
        'marks_at_new_knots': made_mark(rows('made_mark', limit), not args.pilot),
        'two_seven_knot_generators': far(rows('far', limit), not args.pilot),
        'three_meeting_step_controls_with_any_hearing': receiver_controls(rows('receivers', limit)),
        'earlier_census_comparisons': earlier_census(rows('prior_census', limit)),
    }
    if args.pilot:
        print('Read and tallied 3 rows from each record.')
        return
    result['input_sha256'] = {
        stem: hashlib.sha256((RECORD / f'{stem}.jsonl.gz').read_bytes()).hexdigest()
        for stem in ('reach_runs', 'made_bench', 'made_census', 'made_mark', 'far')
    }
    result['input_sha256']['receivers'] = hashlib.sha256((RECORD / 'receivers.json').read_bytes()).hexdigest()
    result['input_sha256']['prior_census'] = hashlib.sha256(PRIOR_CENSUS.read_bytes()).hexdigest()
    out = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.out:
        args.out.write_text(out)
    else:
        print(out, end='')


if __name__ == '__main__':
    main()
