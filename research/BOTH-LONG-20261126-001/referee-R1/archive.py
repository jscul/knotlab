"""Count starts and growth stages in the three closed distance archives."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
SETTINGS = ('loose free', 'loose pinned')


def records(kind):
    with gzip.open(HERE.parent / f'{kind}_dist.jsonl.gz', 'rt') as source:
        return [json.loads(line) for line in source]


def tally(kind, limit=None):
    rows = records(kind)
    if limit:
        rows = rows[:limit]
    by_start = defaultdict(list)
    for r in rows:
        label = int(r['structure'].split()[-1])
        by_start[label].append(r)
    n_population, n_selected = (7075, 200) if kind == 'census' else (3000, 150)
    expected = set(Random(20261127).sample(range(n_population), n_selected))
    if not limit:
        assert set(by_start) == expected
    depths = Counter()
    sizes = Counter()
    peaks = defaultdict(list)
    multiclass = []
    maxima = []
    missing = []
    cap_fields = 0
    cases = Counter()
    for label, stages in by_start.items():
        rounds = [s['round'] for s in stages]
        assert rounds == list(range(len(stages)))
        depths[rounds[-1]] += 1
        sizes[stages[0][SETTINGS[0]]["knots"]] += 1
        max_value = None
        for stage in stages:
            for k in SETTINGS:
                a = stage[k]
                cases[a['classes']] += 1
                cap_fields += 'tie cap reached' in a
                if a['classes'] > 1:
                    read, change = a.get('d_read'), a.get('d_change')
                    if not isinstance(read, int) or not isinstance(change, int):
                        missing.append([label, stage['round'], k, read, change])
                        continue
                    if a['classes'] > 2:
                        multiclass.append([label, stage['round'], k, read, change])
                    value = min(read, change)
                    if value >= 4:
                        maxima.append([label, stage['round'], k, read, change])
                    max_value = value if max_value is None else max(max_value, value)
        peaks["no measured class distance" if max_value is None else max_value].append(label)
    return dict(starts=len(by_start), stages=len(rows), preparations=cases, last_round=depths, starting_knots=sizes,
                best_by_start={k:len(v) for k,v in peaks.items()}, reached_four=maxima,
                multiple_class_bits=multiclass, missing=missing, cap_fields=cap_fields)


def ring_archive():
    rows = records('rings')
    missing = [[r['ring'], r['round'], k] for r in rows for k in SETTINGS
               if isinstance(r[k].get('d_read'), str)]
    above = [[r['ring'], r['round'], k, r[k].get('d_read'), r[k].get('d_change')]
             for r in rows for k in SETTINGS if any(isinstance(d, int) and d > r['ring']
             for d in [r[k].get('d_read'), r[k].get('d_change')])]
    return dict(stages=len(rows), settings=2*len(rows), missing_read=missing, above_size=above,
                cap_hits=sum(r[k]['tie cap reached'] for r in rows for k in SETTINGS))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    args = p.parse_args()
    data = {k:tally(k, 1 if args.pilot else None) for k in ('census', 'extension')}
    if not args.pilot:
        data['rings'] = ring_archive()
    print(json.dumps(data, indent=1))
