"""Count connected starts on which a single starting knot already reads a family fact."""
from collections import Counter
from itertools import islice
import argparse
import json
from pathlib import Path
import resource
from time import perf_counter

from growth import load_starts, families, SETS
from grouping import as_mask, pivots_for, reduced


def check(one_set, pilot):
    tally = Counter()
    sizes = Counter()
    first = None
    it = load_starts(one_set)
    for name, start in (islice(it, 2) if pilot else it):
        _, loose = families(start)
        m = len(loose)
        if m < 3:
            continue
        tally['three or more families'] += 1
        base = list(pivots_for(as_mask(row) for row in start).values())
        facts = [as_mask(group) for group in loose]
        read = set()
        for knot in start:
            visible = pivots_for(base + [1 << d for d in knot])
            read.update(i for i, f in enumerate(facts) if not reduced(f, visible))
        sizes[len(read)] += 1
        tally['facts examined'] += m
        tally['facts with a single-knot reader'] += len(read)
        tally['starts with at least one single-knot reader'] += bool(read)
        tally['starts with a single-knot reader for every fact'] += len(read) == m
        if first is None and len(read) == m:
            first = {'source key': name, 'starting knots': start, 'family supports': loose}
    return {'counts': dict(tally), 'readable fact counts by start': dict(sorted(sizes.items())),
            'first fully readable family tuple': first}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (1536 << 20, 1536 << 20))
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    began = perf_counter()
    results = {k: check(k, args.pilot) for k in SETS}
    total = sum((Counter(v['counts']) for v in results.values()), Counter())
    if not args.pilot:
        out = {'totals': dict(total), 'by roster': results}
        Path(__file__).with_name('reader_counts.json').write_text(json.dumps(out, indent=2) + '\n')
    print(dict(total), 'elapsed seconds', round(perf_counter()-began, 3))


if __name__ == '__main__':
    main()
