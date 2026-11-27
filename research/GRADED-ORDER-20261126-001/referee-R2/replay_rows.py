"""Compare the finite-core reading with saved birth counts and first differences."""

import argparse
from collections import Counter
import json
from pathlib import Path
import resource
from time import perf_counter, process_time

from reading import predict


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SOURCES = (
    'fresh7_treeplus', 'fresh7_grow', 'held_treeplus', 'held_grow',
    'held8_treeplus', 'replays',
)
LAWS = ('nae', 'parity')
HORIZON = 24


def index(path, key):
    rows = {}
    with path.open() as stream:
        for line in stream:
            row = json.loads(line)
            ident = row[key]
            if ident in rows:
                raise ValueError(f'{path}: duplicate {key} {ident}')
            rows[ident] = row
    return rows


def birth_counts(row):
    sig0 = Counter({tuple(kind): n for kind, n in row['sig0']})
    sig1 = Counter({(tuple(kind), tuple(map(tuple, parents))): n
                    for (kind, parents), n in row['sig1']})
    if len(sig0) != len(row['sig0']) or len(sig1) != len(row['sig1']):
        raise ValueError('duplicate signature')
    if any(n <= 0 for counts in (sig0, sig1) for n in counts.values()):
        raise ValueError('nonpositive multiplicity')
    projected = Counter()
    for (kind, _), n in sig1.items():
        projected[kind] += n
    if sig0 != projected or sig0.total() != row['n']:
        raise ValueError('inconsistent saved birth counts')
    return sig0, sig1


def grade(ident, seed, grown, saved, law):
    if grown['stars'] != seed['stars'] or grown['knot law'] != law or saved['law'] != law:
        raise ValueError(f'row identity mismatch for {ident}')
    rows = grown['rows']
    if len(rows) > HORIZON:
        raise ValueError(f'too many saved growth rounds for {ident}')
    if 'error' in saved:
        if grown['end'] != 'guard':
            raise ValueError(f'unexpected saved predictor error for {ident}')
        return {'id': ident, 'end': grown['end'], 'grown_rounds': len(rows),
                'not_run': saved['error']}
    if saved['rounds read'] != len(rows):
        raise ValueError(f'number of stored rounds differs for {ident}')
    if grown['end'] == 'rounds' and len(rows) != HORIZON:
        raise ValueError(f'the recorded horizon is incomplete for {ident}')
    closing = grown['end'].startswith('closes at round ')
    if closing and int(grown['end'].split()[-1]) != len(rows) + 1:
        raise ValueError(f'wrong closing round for {ident}')
    depth = HORIZON if closing else len(rows)
    start = process_time()
    predicted = predict(seed['stars'], law, depth)
    cpu = process_time() - start
    if predicted is None or len(predicted) != depth:
        raise ValueError(f'no predictions through round {depth} for {ident}')
    observed = list(map(birth_counts, rows)) + [
        (Counter(), Counter()) for _ in range(depth - len(rows))
    ]
    differences = [[], []]
    first_details = [None, None]
    for t, (actual, forecast) in enumerate(zip(observed, predicted), start=1):
        for i, (actual_counts, forecast_counts) in enumerate(zip(actual, forecast)):
            if actual_counts == forecast_counts:
                continue
            if not differences[i]:
                first_details[i] = {
                    'grown_only': sorted((actual_counts - forecast_counts).items()),
                    'predicted_only': sorted((forecast_counts - actual_counts).items()),
                    'grown_n': actual_counts.total(),
                    'predicted_n': forecast_counts.total(),
                }
            differences[i].append(t)
    first = min((rounds[0] for rounds in differences if rounds), default=None)
    return {'id': ident, 'end': grown['end'], 'grown_rounds': len(rows),
            'graded_rounds': depth, 'empty_tail_rounds': depth - len(rows),
            'sig0_difference_rounds': differences[0],
            'sig1_difference_rounds': differences[1], 'first_difference': first,
            'saved_first_difference': saved['node reading'],
            'first_difference_details': first_details, 'predict_cpu_s': round(cpu, 6)}


def run_batch(source, law, pilot):
    start_wall, start_cpu = perf_counter(), process_time()
    key = 'name' if source == 'replays' else 'draw'
    suffix = f'{source}_{law}.jsonl'
    seeds = index(STUDY / f'{source}.jsonl', key)
    growths = index(STUDY / f'grown_{suffix}', key)
    scores = index(STUDY / f'nodesg_{suffix}', key)
    if seeds.keys() != growths.keys() or seeds.keys() != scores.keys():
        raise ValueError(f'start, growth, and score identifiers differ for {suffix}')
    identifiers = list(seeds)
    if pilot and source != 'replays':
        biggest = max(identifiers, key=lambda ident: growths[ident]['knots'])
        indices = {0, len(identifiers) - 1, identifiers.index(biggest)}
        identifiers = [identifiers[i] for i in sorted(indices)]
    cases = [grade(ident, seeds[ident], growths[ident], scores[ident], law)
             for ident in identifiers]
    tested = [case for case in cases if 'not_run' not in case]
    return {'source': source, 'law': law, 'available': len(seeds),
            'tested': len(tested), 'growth_rounds': sum(c['grown_rounds'] for c in tested),
            'graded_rounds': sum(c['graded_rounds'] for c in tested),
            'closed': sum(bool(c['empty_tail_rounds']) for c in tested),
            'empty_tail_rounds': sum(c['empty_tail_rounds'] for c in tested),
            'matches': sum(c['first_difference'] is None for c in tested),
            'sig0_matches': sum(not c['sig0_difference_rounds'] for c in tested),
            'sig1_matches': sum(not c['sig1_difference_rounds'] for c in tested),
            'saved_score_matches': sum(c['first_difference'] == c['saved_first_difference']
                                       for c in tested),
            'cpu_s': round(process_time() - start_cpu, 6),
            'wall_s': round(perf_counter() - start_wall, 6), 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--cpu-limit', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    memory = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (args.cpu_limit, args.cpu_limit))
    start_wall, start_cpu = perf_counter(), process_time()
    batches = [run_batch(source, law, args.pilot) for source in SOURCES for law in LAWS]
    result = {'horizon': HORIZON, 'memory_limit_bytes': memory,
              'cpu_limit_s': args.cpu_limit, 'peak_memory_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'selection': ('first, last, and largest grown knot count per sample and both ordinary replays'
                            if args.pilot else 'all saved scores without errors'),
              'cpu_s': round(process_time() - start_cpu, 6),
              'wall_s': round(perf_counter() - start_wall, 6), 'batches': batches}
    with args.output.open('w') as out:
        json.dump(result, out, separators=(',', ':'))
        out.write('\n')
    for batch in batches:
        counts = {k: v for k, v in batch.items() if k != 'cases'}
        print(json.dumps(counts))
    print(json.dumps({k: v for k, v in result.items() if k != 'batches'}))


if __name__ == '__main__':
    main()
