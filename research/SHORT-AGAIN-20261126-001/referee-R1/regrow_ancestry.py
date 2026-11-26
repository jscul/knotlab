"""Swap strict own descent for the receiver reading with any receiving ancestor."""

import argparse
import gzip
import json
import random
import resource
import time
from collections import defaultdict
from pathlib import Path

from growth import build, changes, first_difference, grow
from regrow import HOME, SEED, leaves_first_way, record_growth, signature


ONE_FEWER = ('JOIN-FEWER', 'ONE-FEWER', 'REC-ONE-FEWER')


def inclusive(g):
    return [tuple(sorted((g.names[b.id], b.fresh, b.places) for b in r.birth_records if 'A' in g.roles[b.id]))
            for r in g.rows]


def first_changed(a, b):
    return next((n for n, (x, y) in enumerate(zip(a, b), 1) if x != y), None)


def comparisons(a, b):
    inc_a, inc_b = inclusive(a), inclusive(b)
    return {
        'rounds compared': min(len(inc_a), len(inc_b)),
        'own first birth signature difference': first_difference(a, b),
        'own first birth count difference': first_changed(signature(a.rows, 'own_births'), signature(b.rows, 'own_births')),
        'inclusive first birth signature difference': first_changed(inc_a, inc_b),
        'inclusive first birth count difference': first_changed(list(map(len, inc_a)), list(map(len, inc_b))),
    }


def switch(pilot):
    cases = [(d, sender) for d in (2, 3, 4, 5, 6) for sender in ('g3:22@0', 'g7:113@0', 'g1:3@0')]
    if pilot:
        cases = cases[:1]
    results = []
    for d, sender in cases:
        stub = grow(build('g7:122@0', 'stub', d), 'CAP-3', trace=True)
        other = grow(build('g7:122@0', sender, d), 'CAP-3', trace=True)
        results.append({'d': d, 'sender': sender, 'leaves first way': leaves_first_way(other), **comparisons(stub, other)})
    return results


def sample_hearings(seed, pilot):
    rng = random.Random(seed)
    for file in ('jam_d3_meeting.jsonl.gz', 'jam_d3_share_sample.jsonl.gz'):
        strata = defaultdict(list)
        with gzip.open(HOME.parent / file, 'rt') as f:
            for line, record in enumerate(map(json.loads, f), 1):
                if 'law' not in record or record['law'][0] not in ONE_FEWER or record['law'][1] != 'CANCEL-WAIT':
                    continue
                far = [c for c in record['changes'] if c['heard'] and c['distance'] >= 3]
                if far:
                    strata[record['law'][0]].append((line, record, far))
        for law in ONE_FEWER:
            for line, record, far in rng.sample(strata[law], 1 if pilot else 2):
                yield file, line, record, rng.choice(far)


def jam(seed, pilot):
    results = []
    for file, line, record, trial in sample_hearings(seed, pilot):
        edit = next(edit for label, _, edit in changes(record['B'], record['d']) if label == trial['at'])
        whole, marked = (record_growth(record, 12, 1500, change, trace=True) for change in (None, edit))
        differences = comparisons(whole, marked)
        own_round = differences['own first birth signature difference']
        inclusive_round = differences['inclusive first birth signature difference']
        assert own_round == trial['heard'] and inclusive_round is not None
        results.append({
            'file': file, 'line': line, 'A': record['A'], 'B': record['B'], 'law': record['law'], 'join': record['join'],
            'change': trial['at'], 'steps': trial['distance'], **differences,
            'own waiting at own hearing': [g.rows[own_round - 1].a_short for g in (whole, marked)],
            'inclusive waiting at inclusive hearing': [sum('A' in g.roles[u] for u in g.rows[inclusive_round - 1].short)
                                                       for g in (whole, marked)],
        })
    return results


def restart(counts):
    return next((r for r, n in enumerate(counts, 1) if r > 1 and n), None)


def ring(pilot):
    cases = [(d, ration) for d in (2, 3, 6) for ration in ONE_FEWER]
    if pilot:
        cases = cases[:1]
    results = []
    for d, ration in cases:
        ring_end, stub_end = [grow(build('source', b, d), ration, trace=True) for b in ('ring', 'stub')]
        result = {'d': d, 'ration': ration, **comparisons(ring_end, stub_end)}
        for name, counter in (('own', lambda g: signature(g.rows, 'own_births')), ('inclusive', lambda g: list(map(len, inclusive(g))))):
            left, right = counter(ring_end), counter(stub_end)
            left_start, right_start = restart(left), restart(right)
            result[name + ' restart'] = [left_start, right_start]
            result[name + ' same numbers after restart'] = all(a == b for a, b in zip(left[left_start - 1:], right[right_start - 1:]))
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    began = time.monotonic()
    result = {'seed': SEED, 'pilot': args.pilot, 'switch': switch(args.pilot), 'jam': jam(SEED, args.pilot), 'ring': ring(args.pilot)}
    result['seconds'] = round(time.monotonic() - began, 3)
    result['peak KiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
