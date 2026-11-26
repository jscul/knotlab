"""Compare independent finite-map forecasts, the frozen archive and the saved births."""

import argparse
import gzip
import hashlib
import json
import resource
import time
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path

from map_predict import Start, contained, elements, evaluate, make_piece


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
FILES = [(sample, law, filename.format(law=law)) for sample, filename in [
    ('uniform', 'held_out_{law}.jsonl.gz'), ('stratified', 'grown_stratified_{law}.jsonl.gz'),
    ('handbuilt', 'grown_handbuilt_{law}.jsonl.gz'), ('grow7', 'grown_grow7_{law}.jsonl.gz'),
    ('horizon', 'grown_horizon_{law}.jsonl.gz'),
] for law in (('nae',) if sample == 'horizon' else ('nae', 'parity'))]
FIELDS = ('read', 'stratum', 'D', 'K0', 'K1', 'rows')


def first_difference(forecast, actual):
    for t, row in enumerate(actual['rows'], start=1):
        if forecast[t-1] != row:
            return t
    if actual['end'].startswith('stalls'):
        return len(actual['rows']) + 1
    if actual['end'].startswith('closes'):
        for t, row in enumerate(forecast[len(actual['rows']):], start=len(actual['rows'])+1):
            if row['n']:
                return t
    return None


def counter_entries(row, reading):
    return Counter({json.dumps(sig, separators=(',', ':')): n for sig, n in row[reading]})


def difference_example(first, forecast, actual):
    if first > len(actual['rows']):
        return {'round': first, 'end': actual['end']}
    raw = actual['rows'][first-1]
    pred = forecast[first-1]
    out = {'round': first, 'number predicted': pred['n'], 'number observed': raw['n']}
    for read in ('sig0', 'sig1'):
        left, right = counter_entries(pred, read), counter_entries(raw, read)
        out[read] = {'forecast excess': dict(left-right), 'observed excess': dict(right-left)}
    return out


def actual_cover_check(start):
    counts = Counter()
    examples = []
    for live_part in start.pieces:
        piece = make_piece(start, live_part, 'graded', None)
        masks = sorted(piece.rank, key=int.bit_count, reverse=True)
        counts['valid core sets'] += len(masks)
        for upper in masks:
            lowers = []
            for lower in masks:
                if upper == lower or not contained(lower, upper):
                    continue
                difference = piece.rank[upper] - piece.rank[lower]
                counts['proper inclusions'] += 1
                if difference <= 0:
                    counts['proper inclusions with no increase'] += 1
                # Retain maximal proper subsets: this computes actual covers
                # without counting any proposed rank-one pair as a given.
                if any(contained(lower, between) for between in lowers):
                    if difference == 1:
                        counts['rank-one inclusions with a set strictly between'] += 1
                    continue
                lowers.append(lower)
                counts['true covers'] += 1
                if difference != 1:
                    counts['true covers with rank difference other than one'] += 1
                    if len(examples) < 3:
                        examples.append({'lower mask': lower, 'upper mask': upper,
                                         'lower rank': piece.rank[lower]-1, 'upper rank': piece.rank[upper]-1})
    return {'counts': dict(counts), 'examples': examples}


def live_forms(start):
    bits = list(elements(start.live))
    labels = {}
    for bit in bits:
        chains = tuple(sorted(sum(root == p for root in start.rays.values()) for p in elements(start.pendants[bit])))
        labels[bit] = start.start_descriptions[bit][-1], chains
    bare, complete = None, None
    for order in permutations(bits):
        renaming = {bit: 1 << j for j, bit in enumerate(order)}
        tables = tuple(tuple(sorted(sum(renaming[v] for v in elements(h)) for h in hs))
                       for hs in (start.cells, start.blocks))
        colored = tables, tuple(labels[bit] for bit in order)
        if bare is None or tables < bare:
            bare = tables
        if complete is None or colored < complete:
            complete = colored
    return (len(bits), bare), (len(bits), complete)


def pilot_item(sample, pos, index, reason, tally):
    # Record the first eight in each roster, a large hand-built cell, the two
    # residual examples and up to two members of the stratum with shared cells.
    return (pos < 8 or (sample == 'grow7' and reason == 'predicted' and tally['predicted'] < 3) or
            (sample == 'handbuilt' and pos in (8, 14)) or
            (sample == 'uniform' and index == 6408) or (sample == 'stratified' and pos in (100, 101)))


def given_graded_tally():
    expected = defaultdict(Counter)
    archive = json.loads((STUDY / 'posthoc.json').read_text())
    for key, count in archive['tally'].items():
        split = key.split(' / ')
        if split[0].startswith('fitting'):
            continue
        expected[' / '.join(split[:2])][' / '.join(split[2:])] = count
    return expected


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--pilot', action='store_true')
    args.add_argument('--output', required=True, type=Path)
    options = args.parse_args()
    cap = 5 * 1024**3 // 2
    current, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (min(cap, current) if current > 0 else cap, hard))
    elapsed = time.monotonic()
    totals = defaultdict(Counter)
    measured = defaultdict(Counter)
    failures = []
    archived_differences = []
    examples = []
    fixed_bare, fixed_complete, fixed_readings = Counter(), Counter(), Counter()
    digest = hashlib.sha256()
    time_by_set = {}
    frozen_name = STUDY / 'predictions.jsonl.gz'
    with gzip.open(frozen_name, 'rb') as frozen:
        for sample, law, filename in FILES:
            begin = time.monotonic()
            roster = sample + ' / ' + law
            tally = totals[roster]
            graded_tally = measured[roster]
            rounds = 40 if sample == 'horizon' else 24
            with gzip.open(STUDY / filename, 'rb') as actual_file:
                for pos, line in enumerate(actual_file):
                    raw = json.loads(line)
                    frozen_line = next(frozen)
                    digest.update(frozen_line)
                    archived = json.loads(frozen_line)
                    if (archived['set'], archived['knot law'], archived['index']) != (sample, law, raw['index']):
                        raise ValueError(('roster/order', sample, law, raw['index']))
                    if options.pilot and not pilot_item(sample, pos, raw['index'], archived['read'], tally):
                        continue
                    tally['starts read'] += 1
                    pred = evaluate(raw['stars'], rounds, law, 'frozen')
                    mismatched = [f for f in FIELDS if pred[f] != archived[f]]
                    if mismatched:
                        archived_differences.append([sample, law, raw['index'], mismatched])
                    else:
                        tally['independent frozen matches all archived fields'] += 1
                    if pred['read'] != 'predicted':
                        tally[pred['read']] += 1
                        graded_tally['not predicted: ' + pred['read']] += 1
                        continue
                    tally['predicted'] += 1
                    tally['frozen forecast rounds checked against archive'] += rounds
                    tally['rounds of positive-length or saved birth data read'] += len(raw['rows'])
                    tally['accepted, end ' + raw['end'].split()[0]] += 1
                    prior = first_difference(pred['rows'], raw)
                    graded = evaluate(raw['stars'], rounds, law, 'graded')
                    new = first_difference(graded['rows'], raw)
                    verdict = 'agree' if new is None else 'differ'
                    graded_tally[graded['stratum'] + ' / ' + verdict] += 1
                    if prior is None and new is None:
                        tally['old hit preserved'] += 1
                    elif prior is not None and new is None:
                        tally['old miss fixed'] += 1
                    elif prior is not None and new is not None:
                        tally['old miss persists'] += 1
                    else:
                        tally['old hit lost'] += 1
                    if pred['rows'] != graded['rows']:
                        tally['revised rows differ from frozen through forecast horizon'] += 1
                    if any(a != b for a, b in zip(pred['rows'], graded['rows'][:len(raw['rows'])])):
                        tally['revised rows differ within the saved birth rounds'] += 1
                    if pred['D'] != graded['D'] or pred['K0'] != graded['K0'] or pred['K1'] != graded['K1']:
                        tally['revised D or cuts differ from frozen'] += 1
                    if prior is not None or new is not None:
                        start = Start(raw['stars'], law)
                        overlap_sizes = sorted((b & c).bit_count() for b in start.blocks for c in start.cells if (b & c).bit_count() >= 2)
                        details = {'set': sample, 'law': law, 'index': raw['index'], 'end': raw['end'],
                                   'saved birth rounds': len(raw['rows']), 'first frozen difference': prior,
                                   'first graded difference': new, 'stratum': pred['stratum'],
                                   'drawn for': raw.get('drawn for'),
                                   'cell sizes': sorted(c.bit_count() for c in start.cells),
                                   'cell pair intersection sizes': sorted((a & b).bit_count() for a, b in combinations(start.cells, 2)),
                                   'block intersections of at least two knots with cells': overlap_sizes}
                        if law == 'nae':
                            details['inclusion covers tested against assigned ranks'] = actual_cover_check(start)
                            if new is None:
                                bare, complete = live_forms(start)
                                fixed_bare[bare] += 1
                                fixed_complete[complete] += 1
                                fingerprint = hashlib.sha256(json.dumps(graded['rows']).encode()).hexdigest()
                                fixed_readings[fingerprint] += 1
                        failures.append(details)
                        if new is not None:
                            examples.append(dict(details, first_round_detail=difference_example(new, graded['rows'], raw)))
            time_by_set[roster] = round(time.monotonic() - begin, 3)
        if frozen.readline():
            raise ValueError('extra archived predictions')
    trusted = given_graded_tally()
    result = {
        'pilot': options.pilot, 'uncompressed frozen archive sha256': digest.hexdigest(),
        'fields compared against frozen file': list(FIELDS),
        'by set and law': totals, 'graded counts by archived stratum': measured,
        'independent frozen discrepancies': archived_differences,
        'first differences observed': failures, 'remaining graded discrepancies': examples,
        'corrected distinct starts, grouped up to renaming': {
            'bare live knots, cells and maximal blocks, multiplicities': sorted(fixed_bare.values(), reverse=True),
            'also attaching pendants, chains and original knot sizes, multiplicities': sorted(fixed_complete.values(), reverse=True),
            'identical revised two-reading forecasts through 24 under not-all-equal, multiplicities': sorted(fixed_readings.values(), reverse=True),
        },
        'graded counts match the source post hoc counts on every held-out stratum': None if options.pilot else trusted == measured,
        'time in seconds by set and law including archive parsing': time_by_set,
        'total elapsed seconds': round(time.monotonic()-elapsed, 3), 'peak KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    options.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k in (
        'pilot', 'total elapsed seconds', 'peak KiB', 'graded counts match the source post hoc counts on every held-out stratum')}, indent=2))
    print('frozen discrepancies:', len(archived_differences), 'remaining graded discrepancies:', len(examples))


if __name__ == '__main__':
    main()
