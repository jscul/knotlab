"""Shared-runner job: one finite addressed-pattern description per case."""
import collections
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time

# Also apply before NumPy is imported by the dynamically loaded job module.
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from certificates import union_fate, verify_bond_certificate
from pattern import pattern, level_ids, level, flags, classes
from population import build_population
from search import SearchEngine

POPULATION = None


BUDGET = float(os.environ.get('REACH_BUDGET', '300'))  # thread's addition: the registered run sets 150


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def setup(params):
    global POPULATION, BUDGET
    BUDGET = float(params.get('budget', BUDGET))  # thread's addition
    global W_LIMIT, E_CLASSES
    W_LIMIT = int(params['w_limit']) if 'w_limit' in params else None
    E_CLASSES = set(params['e_classes'].split(',')) if 'e_classes' in params else None
    pop = params.get('pop', 'P')
    if pop not in ('P', 'R'):
        raise ValueError('pop must be P or R')
    POPULATION = build_population(pop)
    prepared = HERE / 'prepared'
    prepared.mkdir(exist_ok=True)
    atomic_json(prepared / f'population_{pop}.json', POPULATION)


W_LIMIT = None      # thread's additions before the registered run (frozen in the pre-registration):
E_CLASSES = None    # keep W_R draws with index < W_LIMIT, and E_R lists whose relative class is in E_CLASSES


def keep_case(payload):
    if W_LIMIT is None and E_CLASSES is None:
        return True
    for m in payload['memberships']:
        if m['family'] == 'W_R' and (W_LIMIT is None or m['index'] < W_LIMIT):
            return True
        if m['family'] == 'E_R' and (E_CLASSES is None or classes(payload['key'])['relative']['class'] in E_CLASSES):
            return True
    return False


def cases():
    if POPULATION is None:
        raise RuntimeError('setup(params) must precede cases()')
    for payload in POPULATION['keys']:
        if keep_case(payload):
            yield payload['id'], payload


def _uncomputed(reason):
    return {'L': 'undecided', 'optimality_proved': False, 'reason': reason}


def compute(key, workdir, N=9, k0=3, S=4, histograms=True):
    """All budgets for the two searches/histogram at one s share 300s."""
    started = time.monotonic()
    K = pattern(key, N)
    nvars = (1 << (N + 1)) - 1
    out = {'N': N, 'k0': k0, 'S': S, 'k_max': 10, 'nvars': nvars,
           'knot_count': len(K), 'flags': flags(key), 'classes': classes(key),
           'budget_seconds_per_key_s': BUDGET,
           'budget_scope': 'L_N, L_target and all per-target searches share one deadline at each s'}
    out['union'] = union_fate(K, nvars, workdir)
    engine = SearchEngine(K, nvars, workdir)
    assert engine.alive == (out['union']['verdict'] == 'alive') or out['union']['verdict'] == 'undecided'
    try:
        rows = []
        A = level_ids(k0)
        checked_bonds = checked_states = 0
        for s in range(1, S + 1):
            row_start = time.monotonic()
            deadline = row_start + BUDGET
            B = level_ids(k0 + s)
            connected = bool({engine.labels[a] for a in A} & {engine.labels[b] for b in B})
            row = {'s': s, 'components': connected}
            if out['union']['verdict'] != 'alive':
                row.update(L_N=None, L_target=None, reason='L defined only for an alive union')
                if histograms and s <= 2:
                    row['histogram'] = None
                rows.append(row)
                continue
            any_result = engine.search(A, B, deadline=deadline)
            target_result = engine.search(A, B, allowed=range((1 << (k0 + s + 1)) - 1), deadline=deadline)
            row.update(L_N=any_result['L'], L_target=target_result['L'],
                       anywhere=any_result, target_restricted=target_result)
            if isinstance(row['L_N'], int) and isinstance(row['L_target'], int):
                assert row['L_target'] >= row['L_N']
            if isinstance(any_result['L'], int):
                row['overshoot'] = max(level(v) for v in any_result['bond']) - (k0 + s)
            if histograms and s <= 2:
                targets, histogram = [], collections.Counter()
                for b in B:
                    # An attained global minimum is also optimal for each
                    # target b it contains; reuse its complete certificate.
                    if isinstance(any_result['L'], int) and b in any_result['bond']:
                        result = dict(any_result)
                        result['reused_global_minimum'] = True
                    else:
                        result = engine.search(A, [b], deadline=deadline)
                    targets.append({'b': b, **result})
                    histogram[str(result['L'])] += 1
                row['per_target'] = targets
                row['histogram'] = dict(sorted(histogram.items()))
                numbers = [t['L'] for t in targets if isinstance(t['L'], int)]
                row['maximum_target_least_bond'] = max(numbers) if len(numbers) == len(B) else None
                row['target_count'] = len(B)
            # Retained witnesses are independently replayable after work removal.
            for result in [any_result, target_result] + row.get('per_target', []):
                summary = verify_bond_certificate(K, nvars, result)
                checked_bonds += summary['bonds']
                checked_states += summary['states']
            row['seconds'] = time.monotonic() - row_start
            rows.append(row)
        out['levels'] = rows
        out['checked_certificate_totals'] = {'bonds': checked_bonds, 'proper_projection_states': checked_states}
        out['seconds'] = time.monotonic() - started
        return out
    finally:
        engine.close()


def run(case_id, payload):
    if not case_id or any(ch not in '0123456789abcdef' for ch in case_id):
        raise ValueError('case id must be a lowercase hexadecimal key hash')
    work = HERE / 'work' / case_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    try:
        result = compute(payload['key'], work)
        result.update(case=case_id, key=payload['key'], memberships=payload['memberships'])
        return result
    finally:
        shutil.rmtree(work)
