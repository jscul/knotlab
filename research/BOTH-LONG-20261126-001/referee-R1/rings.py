"""With --pilot, measure five knots at the start and after one round."""
import argparse
import gzip
import json
from pathlib import Path
from time import perf_counter
from measure import measure
from starts import grow, ring

HERE = Path(__file__).resolve().parent


def compare(row, original):
    correspondence = {'read': 'd_read', 'change': 'd_change', 'allowed_rank': 'dim S',
                      'move_rank': 'dim H', 'classes': 'classes', 'knots': 'knots',
                      'distinctions': 'distinctions'}
    for new, old in correspondence.items():
        if isinstance(original.get(old), str):
            continue
        assert row[new] == original.get(old), (new, row, original)


def run(pilot):
    archive = {}
    with gzip.open(HERE.parent / 'rings_dist.jsonl.gz', 'rt') as stream:
        for line in stream:
            r = json.loads(line)
            archive[r['ring'], r['round']] = r
    results = []
    for n in ([5] if pilot else range(5, 10)):
        knots = ring(n)
        for r in range(2 if pilot else 5):
            if r:
                knots = grow(knots)
            for pinned in (False, True):
                begin = perf_counter()
                result = measure(knots, pinned, tuple(range(n)))
                compare(result, archive[n, r]['loose pinned' if pinned else 'loose free'])
                results.append(dict(ring=n, round=r, pinned=pinned, **result,
                                    seconds=round(perf_counter() - begin, 6)))
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    args = p.parse_args()
    print(json.dumps(run(args.pilot), indent=1))
