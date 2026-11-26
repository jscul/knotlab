"""Tally the committed class tables and rebuild a bounded not-all-equal sample."""

import argparse
import ast
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import resource
import sys
import time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CENSUS_SOURCE = STUDY.parent / 'FORBID-EDITS-20261126-001'
START = 'start'
GROWN = 'after one round'
STAGES = START, GROWN
PIN_MODES = 'loose free', 'loose pinned'
THROUGH = 'shortest through each distinction'
OVERALL = 'shortest overall'
KEPT = 'old classes kept by the grown moves'
SEED = 612026
STATE_CAP = 20_000


def json_lines(path):
    with gzip.open(path, 'rt', encoding='utf-8') as archive:
        rows = [json.loads(line) for line in archive]
    out = {row['structure']: row for row in rows}
    assert len(rows) == len(out), path
    return out


def status(stage):
    if isinstance(stage, str):
        assert stage.startswith('no round'), stage
        return 'no round'
    if stage.get('not run'):
        return 'not run'
    return 'read'


def class_maps(archive):
    out = {}
    for stage in STAGES:
        out[stage] = {}
        for pin in PIN_MODES:
            statuses, counts, skip_dims = Counter(), Counter(), Counter()
            for row in archive.values():
                result = row[stage]
                if isinstance(result, dict):
                    result = result[pin]
                outcome = status(result)
                statuses[outcome] += 1
                if outcome == 'read':
                    assert result['classes'] == 1 << (result['dim S'] - result['dim H'])
                    counts[result['classes']] += 1
                if outcome == 'not run':
                    skip_dims[result['dim S']] += 1
            out[stage][pin] = dict(statuses=statuses, class_counts=counts, skipped_dimensions=skip_dims)
    return out


def compare_engines(canonical, fold):
    assert canonical.keys() == fold.keys()
    assert all(canonical[name][START] == fold[name][START] for name in canonical)
    out = {}
    for pin in PIN_MODES:
        pairs, read_pairs = Counter(), Counter()
        fields, class_bearing_starts = Counter(), Counter()
        for name in canonical:
            a, b = [source[name][GROWN] for source in (canonical, fold)]
            a = a[pin] if isinstance(a, dict) else a
            b = b[pin] if isinstance(b, dict) else b
            a_status, b_status = status(a), status(b)
            pair = 'canonical ' + a_status + ' / fold ' + b_status
            pairs[pair] += 1
            if canonical[name][START][pin]['classes'] > 1:
                class_bearing_starts[pair] += 1
            if a_status == b_status == 'read':
                read_pairs[f"{a['classes']} / {b['classes']}"] += 1
                for field in a:
                    fields[field] += a[field] != b[field]
        out[pin] = dict(status_pairs=pairs, status_pairs_for_class_bearing_starts=class_bearing_starts,
                        class_pairs=read_pairs, differing_fields=fields)
    return out


def detailed_checks(archive):
    out = {}
    for stage in STAGES:
        out[stage] = {
            'statuses': Counter(status(row[stage]) for row in archive.values()),
        }
        for choice in (THROUGH, OVERALL):
            read = [row[stage][choice] for row in archive.values() if status(row[stage]) == 'read']
            class_counts, local, exchange, missing = Counter(), Counter(), Counter(), Counter()
            for entry in read:
                classes = entry['classes']
                assert classes == 1 << entry['dim S/H']
                class_counts[classes] += 1
                if entry['distinctions with no short change']:
                    missing[entry['distinctions with no short change']] += 1
                if classes > 1 and entry['dim (S0+H)/H'] == entry['dim S/H']:
                    exchange[classes] += 1
                if choice == THROUGH and entry['the class read inside one knot']:
                    assert classes > 1
                    local[classes] += 1
            out[stage][choice] = dict(
                class_counts=class_counts, some_nonconstant_local_label=local,
                all_classes_exchanged_avoiding_loose=exchange, missing_short_changes=missing,
            )
    kept = defaultdict(Counter)
    for row in archive.values():
        classes = row[START][THROUGH]['classes']
        if classes > 1:
            key = {True: 'kept', False: 'merged'}.get(row.get(KEPT), 'no round')
            kept[classes][key] += 1
    out['old class counts by outcome'] = kept
    return out


def compare_census_checks(canonical, checks, checked_names):
    class_bearing = {name for name, row in canonical.items() if row[START]['loose free']['classes'] > 1}
    assert checks.keys() == set(checked_names)
    assert class_bearing <= checks.keys()
    class_crosscheck = Counter()
    for name, row in checks.items():
        for stage in STAGES:
            detail, census = row[stage], canonical[name][stage]
            if status(detail) == 'no round':
                assert status(census) == 'no round'
            else:
                census = census['loose free']
                if status(census) == 'read':
                    assert detail[THROUGH]['classes'] == census['classes'], (name, stage)
                    class_crosscheck[stage + ' agrees'] += 1
                else:
                    assert detail['dim S'] == census['dim S']
                    class_crosscheck[stage + ' bounded search beyond full enumeration'] += 1
    return dict(class_bearing_starts=len(class_bearing), singleton_controls=len(checks) - len(class_bearing),
                comparisons=class_crosscheck)


def weight_log(path):
    results = defaultdict(Counter)
    for line in path.read_text().splitlines():
        key, count = line.rsplit(' ', 1)
        if key == 'examples':
            assert ast.literal_eval(count) == []
            continue
        arm, *observation = ast.literal_eval(key)
        if tuple(observation) == ('no round',):
            results[arm]['no round'] = int(count)
        else:
            metric, old, action, kept = observation
            assert (metric, action) == ('classes', 'kept')
            results[arm][f'{old} old classes / {kept} kept'] = int(count)
    return dict(
        counts=results, engine='canonical',
        measured='Number of old classes intersecting the projection of grown allowed states',
        absent_from_log=['start identities for each arm', 'numerical completion counts per class', 'fold engine'],
    )


def nae_archive(archive):
    out = {}
    for stage in STAGES:
        statuses, classes, sizes = Counter(), Counter(), []
        for row in archive.values():
            result = row[stage]
            outcome = status(result)
            statuses[outcome] += 1
            if outcome == 'read':
                assert len(result['sizes']) == result['classes']
                assert sum(result['sizes']) == result['states']
                assert result['states'] <= STATE_CAP
                classes[result['classes']] += 1
                sizes.append(result['states'])
        out[stage] = dict(statuses=statuses, class_counts=classes, allowed_state_range=[min(sizes), max(sizes)])
    return out


def read_archives():
    names = (
        'census_canonical', 'census_fold', 'census_checks', 'rings_canonical',
        'rings_fold', 'rings2', 'nae_sample', 'nae_rings',
    )
    files = {name: STUDY / (name + '.jsonl.gz') for name in names}
    archives = {name: json_lines(path) for name, path in files.items()}
    canonical = archives['census_canonical']
    assert set(canonical) == {f'census {i}' for i in range(7075)}
    assert set(archives['nae_sample']) == {f'census {i}' for i in random.Random(20261126).sample(range(7075), 200)}
    out = dict(
        zip_sha256={path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files.values()},
        census_knots=Counter(row['knots'] for row in canonical.values()),
        parity_maps={name: class_maps(archives[name]) for name in ('census_canonical', 'census_fold', 'rings_canonical', 'rings_fold')},
        census_engine_comparison=compare_engines(canonical, archives['census_fold']),
        ring_engine_comparison=compare_engines(archives['rings_canonical'], archives['rings_fold']),
        census_detailed_checks=detailed_checks(archives['census_checks']),
        ring_detailed_checks=detailed_checks(archives['rings2']),
        archive_consistency=compare_census_checks(
            canonical, archives['census_checks'],
            [f'census {i}' for i in json.loads((STUDY / 'checks_starts.json').read_text())],
        ),
        weights=weight_log(STUDY / 'weights_out.txt'),
        nae_sample=nae_archive(archives['nae_sample']),
        nae_rings=nae_archive(archives['nae_rings']),
        nae_ring_rows=list(archives['nae_rings'].values()),
    )
    return out, archives


def census_supports(record):
    knots, shared, loose = record
    supports = [[] for _ in range(knots)]
    distinction = 0
    for first, second, multiplicity in shared:
        for _ in range(multiplicity):
            supports[first].append(distinction)
            supports[second].append(distinction)
            distinction += 1
    for knot, count in enumerate(loose):
        supports[knot].extend(range(distinction, distinction + count))
        distinction += count
    return tuple(tuple(row) for row in supports)


def ring_supports(name):
    knots, loose = [int(part.split('=')[1]) for part in name.split()[1:]]
    return tuple(
        (knot, (knot + 1) % knots, *range(knots + loose * knot, knots + loose * (knot + 1)))
        for knot in range(knots)
    )


def allowed_nae(supports):
    names = sorted({distinction for knot in supports for distinction in knot})
    membership = Counter(distinction for knot in supports for distinction in knot)
    ordered = sorted(names, key=lambda distinction: (-membership[distinction], distinction))
    indices = {name: i for i, name in enumerate(ordered)}
    n = len(names)
    tests_at_bit = [[] for _ in range(n)]
    for support in supports:
        bits = [indices[name] for name in support]
        tests_at_bit[max(bits)].append(sum(1 << bit for bit in bits))

    allowed = set()

    def enumerate_state(bit, state):
        if len(allowed) > STATE_CAP:
            return
        if bit == n:
            allowed.add(state)
            return
        for extension in (state, state | (1 << bit)):
            if all((extension & mask) not in (0, mask) for mask in tests_at_bit[bit]):
                enumerate_state(bit + 1, extension)

    enumerate_state(0, 0)
    return n, allowed


def single_flip_components(states, width):
    pending = states.copy()
    flips = tuple(1 << bit for bit in range(width))
    sizes = []
    while pending:
        to_visit = [pending.pop()]
        size = 0
        while to_visit:
            state = to_visit.pop()
            size += 1
            for flip in flips:
                neighbor = state ^ flip
                if neighbor in pending:
                    pending.remove(neighbor)
                    to_visit.append(neighbor)
        sizes.append(size)
    return sorted(sizes)


def rebuild_nae(archives, pilot):
    sys.path.insert(0, str(CENSUS_SOURCE))
    from forbid import grown

    census = json.loads((CENSUS_SOURCE / 'starts.json').read_text())
    sample = archives['nae_sample']
    rng = random.Random(SEED)
    grown_read = sorted(name for name, row in sample.items() if status(row[GROWN]) == 'read')
    no_round = sorted(name for name, row in sample.items() if status(row[GROWN]) == 'no round')
    over_cap = sorted(name for name, row in sample.items() if status(row[GROWN]) == 'not run')
    chosen = rng.sample(grown_read, 8) + rng.sample(no_round, 4) + rng.sample(over_cap, 2)
    cases = [(name, sample[name]) for name in chosen] + list(archives['nae_rings'].items())
    if pilot:
        largest = max(chosen[:8], key=lambda name: sample[name][GROWN]['states'])
        selected = {largest, chosen[-1], 'ring n=5 loose=2'}
        cases = [(name, row) for name, row in cases if name in selected]
    results = []
    for name, archive in cases:
        started = time.monotonic()
        if name in sample:
            supports = census_supports(census[int(name.split()[1])])
        else:
            supports = ring_supports(name)
        next_supports, outcome, _ = grown(supports, 'nae', 'ordinary')
        result = dict(structure=name)
        for stage, current in [(START, supports), (GROWN, next_supports if outcome == 'funded' else None)]:
            expected = archive[stage]
            if current is None:
                assert status(expected) == 'no round', (name, stage)
                result[stage] = dict(status='no round', funding=outcome)
                continue
            width, allowed = allowed_nae(current)
            if len(allowed) > STATE_CAP:
                assert status(expected) == 'not run', (name, stage)
                result[stage] = dict(status='not run', states=f'>{STATE_CAP}', distinctions=width)
                continue
            assert status(expected) == 'read' and len(allowed) == expected['states'], (name, stage)
            sizes = single_flip_components(allowed, width)
            # An allowed single flip is a true shortest change through its distinction.
            shortest_sizes = sizes if len(sizes) == 1 else None
            result[stage] = dict(
                states=len(allowed), distinctions=width, single_flip_component_sizes=sizes,
                shortest_change_component_sizes=shortest_sizes,
                matches_archive=None if shortest_sizes is None else shortest_sizes == expected['sizes'],
            )
        result['seconds'] = round(time.monotonic() - started, 4)
        results.append(result)
    return dict(
        seed=SEED,
        case_selection='Eight read grown census rows, four with no round and two over the grown cap, sampled within the archived sample. All ten archived ring profiles.',
        growth='Existing canonical construction with the ordinary law',
        check='Enumerate allowed states independently and find the components under allowed single flips',
        results=results,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    began = time.monotonic()
    archived, archives = read_archives()
    after_archives = time.monotonic()
    rebuilt = rebuild_nae(archives, args.pilot)
    result = dict(
        archived=archived, rebuilt_nae=rebuilt, pilot=args.pilot,
        timing=dict(archive_seconds=round(after_archives - began, 4),
                    nae_seconds=round(time.monotonic() - after_archives, 4),
                    peak_resident_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    )
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    else:
        print(json.dumps(result['timing']))
        print(json.dumps(result['rebuilt_nae']))


if __name__ == '__main__':
    main()
