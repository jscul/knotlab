"""Count distinct law-records across overlapping direct replays."""
import argparse
from collections import defaultdict
import gzip
from itertools import islice
import json
from pathlib import Path
from random import Random
from time import perf_counter

OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((OUT / (name + '.json')).read_text())


def main(pilot):
    started = perf_counter()
    capped = read('regrowth')
    given = read('regrowth_pilot')['records checked']
    initial = {(r['index'], r['knot law']) for r in given}
    extended = read('regrowth_extension')['records checked']
    direct_extensions = {(r['index'], r['knot law']) for r in extended
                         if tuple(r.get('same first plan and laws agree through replay') or (r['index'], r['knot law']))
                         == (r['index'], r['knot law'])}
    strata = defaultdict(list)
    all_runs = {}
    late = {r['index'] for r in capped['records checked'] if r['late by at least one archived reading']}
    for law in ('nae', 'parity'):
        with gzip.open(OUT.parent / f'grown_fresh_{law}.jsonl.gz', 'rt') as stream:
            for x in map(json.loads, islice(stream, 100 if pilot else None)):
                r = x['rows']
                strata[law, x['kind'], x['end'], len(r)].append(x['index'])
                all_runs[x['index'], law] = (len(r), sum(z['n'] for z in r))
    selected = set(late)
    rng = Random(capped['seed for sampling and pilots'])
    for group in strata.values():
        selected.update(rng.sample(group, min(3, len(group))))
    primary = {key for key, (n, _) in all_runs.items() if n == 0 or key[0] in selected}
    direct = (primary | initial | direct_extensions) & all_runs.keys()
    if not pilot:
        assert len(primary) == sum(r.get('complete replays', 0) for r in capped['by law, kind, ending, saved rounds'])
        assert len(direct_extensions) == 12
    counts = {'records read': len(all_runs), 'primary complete capped records': len(primary),
              'direct through saved end across both capped selections and extension': len(direct),
              'of those with positive saved rounds': sum(all_runs[k][0] > 0 for k in direct),
              'sum of saved rounds for directly completed records': sum(all_runs[k][0] for k in direct),
              'sum of births for directly completed records': sum(all_runs[k][1] for k in direct),
              'without direct replay through saved end': len(all_runs)-len(direct),
              'seconds': round(perf_counter()-started, 3)}
    target = OUT / ('coverage_pilot.json' if pilot else 'coverage.json')
    target.write_text(json.dumps(counts, indent=2) + '\n')
    print(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    main(parser.parse_args().pilot)
