"""Reconstruct the census from unordered pairs of knots and loose counts."""
import argparse
from collections import Counter, defaultdict
import gzip
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent


def connected(knots, pairs):
    reached = {0}
    for _ in range(knots - 1):
        for first, second in pairs:
            if first in reached or second in reached:
                reached.update((first, second))
    return len(reached) == knots


def audit(knots, mask_limit=None):
    pairs = list(itertools.combinations(range(knots), 2))
    permutations = list(itertools.permutations(range(knots)))
    bits = {pair: 1 << index for index, pair in enumerate(pairs)}
    transforms = [[bits[tuple(sorted((perm[first], perm[second])))]
                   for first, second in pairs] for perm in permutations]
    masks = {}
    expected = set()
    all_loose_zero = []
    labelled_connected = 0
    mask_count = 1 << len(pairs)
    selected = range(min(mask_count, mask_limit or mask_count))
    for mask in selected:
        indices = [i for i in range(len(pairs)) if mask & (1 << i)]
        included = [pairs[i] for i in indices]
        if not connected(knots, included):
            continue
        labelled_connected += 1
        renamed = [sum(table[i] for i in indices) for table in transforms]
        least = min(renamed)
        # perm maps an archive knot to its canonical position. Its inverse
        # reorders loose counts into that canonical numbering.
        orderings = [tuple(sorted(range(knots), key=permutations[j].__getitem__))
                     for j, value in enumerate(renamed) if value == least]
        masks[mask] = (least, orderings)
        if least != mask:
            continue
        degrees = Counter(i for pair in included for i in pair)
        domains = [range(max(0, 3 - degrees[v]), 4) for v in range(knots)]
        for counts in itertools.product(*domains):
            if any(counts):
                canonical = min(tuple(counts[i] for i in order) for order in orderings)
                expected.add((mask, canonical))
            else:
                all_loose_zero.append(included)

    archive = set()
    repeats = []
    inconsistent = []
    seen_indices = []
    phase = 1 if knots < 5 else 2
    with gzip.open(HERE.parent / f'phase{phase}_grown.jsonl.gz', 'rt') as data:
        for line in data:
            # Stars precede the birth rows in neither archive. Read each complete record.
            record = json.loads(line)
            if record['n knots'] != knots:
                continue
            holders = defaultdict(list)
            for v, distinctions in enumerate(record['stars']):
                for distinction in distinctions:
                    holders[distinction].append(v)
            shared = [tuple(sorted(group)) for group in holders.values() if len(group) > 1]
            counts = Counter(group[0] for group in holders.values() if len(group) == 1)
            loose = tuple(counts[i] for i in range(knots))
            if (len(record['stars']) != knots or len(set(shared)) != len(shared)
                    or any(pair not in bits for pair in shared)
                    or list(loose) != record['loose']):
                inconsistent.append(record['index'])
                continue
            mask = sum(bits[pair] for pair in shared)
            if mask not in masks:
                if mask in selected:
                    inconsistent.append(record['index'])
                continue
            least, orderings = masks[mask]
            item = least, min(tuple(loose[v] for v in order) for order in orderings)
            if item in archive:
                repeats.append(record['index'])
            archive.add(item)
            seen_indices.append(record['index'])
    return {'labelled_connected_patterns': labelled_connected,
            'meeting_patterns': len({val[0] for val in masks.values()}),
            'predicted_with_loose': len(expected), 'observed_with_loose': len(archive),
            'missing': sorted(expected - archive), 'extra': sorted(archive - expected),
            'repeated_starts': repeats, 'inconsistent_records': inconsistent,
            'indices_contiguous': sorted(seen_indices) == list(range(len(seen_indices))),
            'excluded_no_loose_patterns_as_pairs_of_knots': all_loose_zero}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    options = parser.parse_args()
    start = time.monotonic()
    result = ({5: audit(5, 256)} if options.pilot else
              {knots: audit(knots) for knots in range(1, 6)})
    output = dict(sizes=result, seconds=round(time.monotonic() - start, 3))
    if options.pilot:
        output = {"five_knot_numbered_patterns_tried": 256, "scope": "timing only",
                  "seconds": output["seconds"]}
    path = HERE / ('census_pilot.json' if options.pilot else 'census.json')
    path.write_text(json.dumps(output, indent=2) + '\n')
    print(path.name, output['seconds'])
