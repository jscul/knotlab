"""Recount the knot-test records and replay the comparison sample selection."""

import gzip
import json
import random
from collections import Counter
from itertools import islice
from pathlib import Path
from sys import argv


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / 'artifacts/TIME-AS-FOLD-20261125-001A/TIME-AS-FOLD-20261125-001A-E001_count_of_returns'
GROWTH_FILES = [f'run1_part{i}' for i in range(1, 9)] + ['run2', 'run3']
KEY = ('group', 'start', 'base', 'rule', 'choice', 'knot_law')


def rows(name):
    with gzip.open(SOURCE / (name + '.jsonl.gz'), 'rt') as source:
        for line in source:
            yield json.loads(line)


def key(row):
    return tuple(row[item] for item in KEY)


def predicted_case(item):
    return item == ('main', 'two-knot', 'RING-LAW', 'MET', 'NEWEST', 'parity')


def start_widths():
    data = json.loads((REPO / 'research/TIME-AS-FOLD-20261125-001A/starts.json').read_text())
    widths = {name: [len(part) for part in start] for name, start in data['named'].items()}
    for start in data['ring_study_returning_starts']:
        index = start['atlas_index']
        loose = start['loose']
        name = f'atlas {index} loose ' + ','.join(str(h) for h in loose)
        widths[name] = [len(part) for part in start['stars']]
    return widths


def comparison_counts(group):
    counts = Counter()
    for row in group:
        counts['sources'] += 1
        if 'unfinished' in row:
            counts['unfinished_sources'] += 1
        checked = row.get('kt_comparisons', {})
        counts['sources_with_comparison'] += checked.get('runs', 0) > 0
        for field in ('runs', 'verdicts', 'fails', 'disagree', 'untested'):
            counts[field] += checked.get(field, 0)
    return dict(counts)


def main(limit):
    run_a = {key(row): row for row in islice(rows('run7_runA'), limit)}
    widths = start_widths()
    clock_pool = []
    totals = {law: Counter() for law in ('nae', 'parity')}
    listing = []
    source_keys = set()
    stop_counts = Counter()
    for name in GROWTH_FILES:
        for row in islice(rows(name), limit):
            item = key(row)
            if row.get('unfinished'):
                continue
            assert item not in source_keys
            source_keys.add(item)
            if row['nopast']['n_clocks']:
                clock_pool.append(item)
            checked = run_a.get(item)
            if checked is None:
                continue
            assert checked['knots'] == row['knots'] and checked['rounds'] == row['rounds']
            stop_counts[row['stop'] or 'round bound'] += 1
            count = totals[item[-1]]
            count['runs'] += 1
            sizes = widths[checked['start']]
            assert len(sizes) == row['per_round'][0][-1]
            count['start_knots'] += len(sizes)
            count['max_start_width'] = max(count['max_start_width'], *sizes)
            count['start_knots_above_12_places'] += sum(size > 12 for size in sizes)
            if item[-1] == 'nae':
                count['same_method_rechecks'] += sum(size <= 12 for size in sizes)
            count['unfinished_runs'] += bool(checked.get('unfinished'))
            count['runs_with_failure'] += bool(checked['kt']['fails'])
            count['knot_rounds_by_extension'] += sum(r[-1] for r in row['per_round'])
            for field in ('verdicts', 'fails', 'disagree', 'untested', 'compared'):
                count[field] += checked['kt'][field]
            for field in ('extension_bad', 'cuts'):
                count[field] += len(checked['kt'][field])
            count['only_one_method'] += checked['kt']['verdicts'] - checked['kt']['compared']
            count['two_distinct_methods'] = count['compared'] - count['same_method_rechecks']
            if literal := checked.get('literal'):
                count['literal_runs'] += 1
                count['literal_knot_rounds'] += literal['verdicts']
                count['literal_failed_knot_rounds'] += literal['fails']
                count['literal_method_disagreements'] += literal['disagree_methods']
                count['literal_runs_with_different_failing_knots'] += not literal['same_failing_knots']
            assert checked['kt']['fails'] == len(checked['kt']['fail_rows'])
            for failure in checked['kt']['fail_rows']:
                listing.append({
                    'configuration': item,
                    **failure,
                    'met_newest_predicted': predicted_case(item) and failure['parents'] == 12,
                    'has_clock': bool(row['nopast']['n_clocks']),
                })
    failed_keys = {tuple(f['configuration']) for f in listing}
    positive = Counter(key(row) for row in islice(rows('run4'), limit) if row.get('verdict_C_iii') == 'holds')
    sample = list(rows('run7_comparisons'))
    timing = list(rows('run7_comparisons_timing'))
    sample_keys = {key(row) for row in sample}
    timing_keys = {key(row) for row in timing}
    pool = clock_pool[:5000]
    seed = 2026112508
    seeds_replayed = False
    if limit is None:
        assert run_a.keys() == source_keys
        assert len(sample_keys) == len(sample) and len(timing_keys) == len(timing)
        assert sample_keys == set(random.Random(seed).sample(pool, len(sample)))
        run1_pool = [item for item in clock_pool if item[0] in ('main', 'fbp', 'dbt')]
        assert timing_keys == set(random.Random(seed).sample(run1_pool, len(timing)))
        seeds_replayed = True
    return {
        'run_a': {
            'totals': totals,
            'source_keys_without_knot_test': len(source_keys - run_a.keys()),
            'knot_tests_without_source_key': len(run_a.keys() - source_keys),
            'stops': stop_counts,
            'failure_rows': sorted(listing, key=lambda f: (str(f['configuration']), f['knot'])),
            'failure_runs_with_clock': sum(any(f['configuration'] == item and f['has_clock'] for f in listing)
                                           for item in failed_keys),
            'failure_runs_that_reach_comparison_pool': len(failed_keys.intersection(pool)),
            'failure_runs_that_reach_seeded_sample': len(failed_keys & sample_keys),
            'positive_c_iii_tests': sum(positive.values()),
            'positive_c_iii_runs': len(positive),
            'positive_c_iii_runs_by_law': Counter(item[-1] for item in positive),
            'positive_c_iii_runs_without_run_a_knot_test': len(positive.keys() - run_a.keys()),
            'positive_c_iii_runs_with_run_a_failure': len(positive.keys() & failed_keys),
            'positive_c_iii_sources_in_seeded_sample': len(positive.keys() & sample_keys),
            'positive_c_iii_sources_in_timing_sample': len(positive.keys() & timing_keys),
        },
        'comparisons': {
            'seed': seed,
            'seed_replay_matches_source_keys': seeds_replayed,
            'selection_order': 'completion order saved in raw growth files',
            'pool_size_before_prefix': len(clock_pool),
            'prefix_size': len(pool),
            'sample_timing_overlap': len(sample_keys & timing_keys),
            'timing_sources_in_prefix': len(timing_keys.intersection(pool)),
            'timing_sources_in_each_group': Counter(row['group'] for row in timing),
            'registered_sample': {law: comparison_counts(row for row in sample if row['knot_law'] == law)
                                  for law in ('nae', 'parity')},
            'timing_sample': {law: comparison_counts(row for row in timing if row['knot_law'] == law)
                              for law in ('nae', 'parity')},
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(int(argv[1]) if len(argv) > 1 else None), indent=2))
