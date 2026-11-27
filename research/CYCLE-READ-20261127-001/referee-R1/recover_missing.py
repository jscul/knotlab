"""Replay the unscored Part 2 starts through their first chained-twin birth round.

Run from this directory with the repository interpreter and -B. The pilot
and remaining cases use the same limits. Only the two local readers and the
ordinary growth supply predictions and observations. Saved scores select
the cases; saved growth rows, where available, check the replay.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import gzip
import hashlib
import json
from math import comb
from pathlib import Path
import resource
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY.parent / 'LOOK-ALIKE-20261126-001'))
from alike import grow
from core import build_core
from reader import predict_core

LAWS = ('nae', 'parity')
OUTPUT = HERE / 'recover_missing.json'
BIRTH_LIMIT = 5_000
MAX_SIZE = 26  # Start size 1; the study's rank 25 is ordinary birth round 25.
WORK_LIMIT = 2_000_000
CASE_CPU = 10


class CaseLimit(Exception):
    pass


def expire(*_):
    raise CaseLimit('case CPU limit')


def rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as src:
        return list(map(json.loads, src))


def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def selected_cases():
    cases = []
    scores = rows(STUDY / 'scores2.jsonl')
    for prefix, weighting in [('twin9', 'W1 tree+ nine knots'), ('twin8', 'W2 tree+s50 eight knots')]:
        selected = defaultdict(dict)
        for row in scores:
            if (row['weighting'] == weighting and row['bucket'] == 'twins, chained'
                    and row['verdict'] not in ('agrees', 'differs')):
                selected[row['draw']][row['law']] = row
        observations = {}
        for law in LAWS:
            observations[law] = {row['draw']: row for row in rows(STUDY / f'grown_{prefix}_{law}.jsonl.gz')
                                 if row['draw'] in selected}
        for line, row in enumerate(rows(STUDY / f'{prefix}_draw.jsonl'), 1):
            draw = row['draw']
            if draw in selected:
                if set(selected[draw]) != set(LAWS):
                    raise ValueError('an unscored start has a different law denominator')
                archived = {law: observations[law][draw] for law in LAWS}
                assert all(a['stars'] == row['stars'] for a in archived.values())
                cases.append((prefix, row, line, selected[draw], archived))
    if len(cases) != 13:
        raise ValueError('the saved scores no longer identify thirteen starts')
    return cases


def piece_details(piece):
    counts = [len(layer) for layer in piece.ranks.values()]
    # For each ordinary birth round, sum the pairs of its births sharing
    # each parent. A pair sharing two parents is counted at both parents.
    pairs = [sum(comb(len(piece.nodes[p].children), 2) for p in layer)
             for layer in piece.ranks.values()]
    distinct = []
    for size, layer in list(piece.ranks.items())[1:]:
        position = {child: i for i, child in enumerate(layer)}
        siblings = [0] * len(layer)
        for p in piece.ranks[size - 1]:
            family = [position[child] for child in piece.nodes[p].children]
            mask = sum(1 << i for i in family)
            for i in family:
                siblings[i] |= mask & ~(1 << i)
        distinct.append(sum(mask.bit_count() for mask in siblings) // 2)
    return dict(stop=piece.stop, starts=counts[0], non_start_births=piece.birth_count,
                total_nodes=len(piece.nodes), knots_by_round_from_zero=counts,
                parent_pair_incidence_by_round_from_one=pairs[:-1],
                distinct_pairs_sharing_parents_by_round_from_one=distinct,
                chain_counts=sorted(piece.chains.values()),
                twin_birth_round=piece.twin_rank - 1 if piece.twin else None,
                twin_witness_start_size_one=asdict(piece.twin) if piece.twin else None)


def run_law(stars, law, saved):
    read = build_core(stars, law, max_births=BIRTH_LIMIT, max_rank=MAX_SIZE, group_work=WORK_LIMIT)
    pieces = [piece_details(piece) for piece in read.pieces]
    first_twin = min((p['twin_birth_round'] for p in pieces if p['twin_birth_round'] is not None), default=None)
    out = dict(pieces=pieces, twin_birth_round=first_twin, saved_growth_end=saved['end'],
               saved_growth_rounds=len(saved['rows']))
    if first_twin is None:
        out['censor'] = f'no chained twins through complete ranks: {read.status}'
        return out
    predicted, status = predict_core(read, first_twin, law)
    out['prediction_status'] = status
    if predicted is None:
        return out
    observed = grow(stars, rounds=first_twin, bound=30_000, knot_law=law)
    actual = observed['rows']
    out['observed_end'] = observed['end']
    out['observed_rounds'] = len(actual)
    out['grown_births'] = [a['n'] for a in actual]
    out['predicted_births'] = [p['n'] for p in predicted]
    out['grown_prefix_sha256'] = fingerprint(actual)
    out['predicted_prefix_sha256'] = fingerprint(predicted)
    out['first_difference'] = {key: next((r for r, (a, p) in enumerate(zip(actual, predicted), 1)
                                          if a[key] != p[key]), None) for key in ('n', 'sig0', 'sig1')}
    if len(actual) == first_twin:
        def sig0(row):
            return Counter({tuple(key): n for key, n in row['sig0']})
        c0, p0 = sig0(actual[-1]), sig0(predicted[-1])
        out['extra_grown_sig0_at_twin'] = sorted((list(key), n) for key, n in (c0 - p0).items())
        out['extra_predicted_sig0_at_twin'] = sorted((list(key), n) for key, n in (p0 - c0).items())
    if saved['rows']:
        n = min(len(saved['rows']), len(actual))
        out['saved_prefix_rounds_compared'] = n
        out['agrees_with_saved_growth'] = saved['rows'][:n] == actual[:n]
    return out


def replay(case):
    prefix, start, line, scores, archived = case
    out = dict(source=f'{prefix}_draw.jsonl', line=line, draw=start['draw'], weighting=start['weighting'],
               n_knots=len(start['stars']), stars_sha256=fingerprint(start['stars']), laws={})
    for law in LAWS:
        before = time.process_time()
        signal.setitimer(signal.ITIMER_PROF, CASE_CPU)
        try:
            result = run_law(start['stars'], law, archived[law])
        except (CaseLimit, MemoryError, RecursionError) as exc:
            result = dict(censor=type(exc).__name__)
        finally:
            signal.setitimer(signal.ITIMER_PROF, 0)
        result['saved_verdict'] = scores[law]['verdict']
        result['saved_least_rank'] = scores[law]['least rank of chained twins']
        result['cpu_seconds'] = round(time.process_time() - before, 5)
        out['laws'][law] = result
    return out


def save(result):
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='run just the first nine-knot start and the pair-cap case')
    parser.add_argument('--remaining', action='store_true', help='continue after the saved pilot')
    args = parser.parse_args()
    signal.signal(signal.SIGPROF, expire)
    resource.setrlimit(resource.RLIMIT_AS, (1700 << 20, 1700 << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (280, 290))
    cases = selected_cases()
    pilot = [cases[0], next(c for c in cases if c[3]['nae']['verdict'].startswith('not predicted'))]
    result = json.loads(OUTPUT.read_text()) if args.remaining else dict(
        question='First difference through the ordinary birth round of the least chained twins',
        limits=dict(non_start_births_per_piece=BIRTH_LIMIT, last_ordinary_core_round=MAX_SIZE-1,
                    group_work=WORK_LIMIT, CPU_seconds_per_start_and_law=CASE_CPU,
                    memory_MiB=1700, ordinary_growth_knot_bound=30_000), starts=[])
    if not args.remaining:
        for case in pilot:
            result['starts'].append(replay(case))
        pilot_cpu = sum(law['cpu_seconds'] for start in result['starts'] for law in start['laws'].values())
        result['pilot_start_draws'] = [case[1]['draw'] for case in pilot]
        result['pilot_cpu_seconds'] = round(pilot_cpu, 5)
        result['full_estimate_from_pilot_cpu_seconds'] = round(pilot_cpu * len(cases) / len(pilot), 3)
        save(result)
        print('pilot estimate', result['full_estimate_from_pilot_cpu_seconds'], flush=True)
    if args.pilot:
        return
    done = {(start['source'], start['draw']) for start in result['starts']}
    for case in cases:
        if (case[0] + '_draw.jsonl', case[1]['draw']) not in done:
            result['starts'].append(replay(case))
            save(result)
    print('completed starts', len(result['starts']), flush=True)


if __name__ == '__main__':
    main()
