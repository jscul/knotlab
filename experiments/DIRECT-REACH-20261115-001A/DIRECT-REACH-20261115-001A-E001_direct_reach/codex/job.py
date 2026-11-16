"""Shared-runner production interface for DIRECT-REACH D and U."""
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reuse import HERE, pattern, provenance, freeze_provenance
from population import populations
from retention import ProofStore, context, union_fate
from ties import compute_ties
from reach import query
from homomorphisms import evaluate

POPULATION = None
SOURCE_MANIFEST = None


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    temp.replace(path)


def setup(params):
    global POPULATION, SOURCE_MANIFEST
    pop = params.get('pop', 'D')
    if pop not in ('D', 'U'):
        raise ValueError('pop must be D or U')
    POPULATION = populations()[pop]
    SOURCE_MANIFEST = freeze_provenance()
    (HERE / 'tmp').mkdir(exist_ok=True)
    (HERE / 'case_work').mkdir(exist_ok=True)
    atomic_json(HERE / 'prepared' / f'population_{pop}.json', POPULATION)
    atomic_json(HERE / 'source_hashes.json', provenance())


def cases():
    if POPULATION is None:
        raise RuntimeError('setup(params) must precede cases()')
    for row in POPULATION:
        yield row['id'], row


def run(case_id, payload):
    if (len(case_id) != 64 or any(c not in '0123456789abcdef' for c in case_id)
            or case_id != payload['id']):
        raise ValueError('case id must be the census hexadecimal SHA-256')
    work = HERE / 'case_work' / case_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    started = time.monotonic()
    print(f'CASE START {payload["pop"]} {case_id}', flush=True)
    key = payload['key']
    store = ProofStore(work, 1023)
    timings = {}
    try:
        result = {'case': case_id, 'key': key, 'pop': payload['pop'],
                  'source_manifest': SOURCE_MANIFEST,
                  'memberships': payload['memberships'], 'census': payload['census'],
                  'N': 9, 'nvars': 1023}
        t = time.monotonic()
        K = pattern.pattern(key, 9)
        with context(store):
            base_union = union_fate(K, 1023, work, 600)
        result['union_N9'] = base_union
        if base_union['verdict'] == 'alive':
            result['ties'] = compute_ties(K, 1023, work, case_id, store=store)
        else:
            result['ties'] = {'verdict': 'not_computed', 'reason': 'N9 union is not certified alive'}
        timings['ties_and_N9_union'] = time.monotonic() - t
        print(f'CASE PHASE {case_id[:12]} ties seconds={timings["ties_and_N9_union"]:.1f}', flush=True)
        t = time.monotonic()
        thresholds = []
        for k0 in (2, 3):
            thresholds.append(query(key, work, store, k0, list(range(1, 9-k0)),
                                    k_max=4 if payload['half_rate'] else 3, budget=300))
        result['threshold_reach'] = thresholds
        timings['threshold_reach'] = time.monotonic() - t
        print(f'CASE PHASE {case_id[:12]} threshold_reach seconds={timings["threshold_reach"]:.1f}', flush=True)
        t = time.monotonic()
        result['homomorphisms'] = evaluate(key, 8, 9)
        timings['homomorphisms'] = time.monotonic() - t
        t = time.monotonic()
        life = []
        for N in (10, 11, 12):
            next_K = pattern.pattern(key, N)
            with context(store):
                fate = union_fate(next_K, (1 << (N + 1))-1, work, 600)
            life.append({'N': N, 'knot_count': len(next_K), **fate})
        result['life'] = life
        timings['life'] = time.monotonic() - t
        print(f'CASE PHASE {case_id[:12]} life seconds={timings["life"]:.1f}', flush=True)
        t = time.monotonic()
        followups = []
        if payload['pop'] == 'U':
            resolved = {r['s']: r for out in thresholds if out['k0'] == 3 for r in out['levels']}
            for row in payload['census']['levels']:
                if row['L_N'] != 'undecided':
                    continue
                s = row['s']
                existing = resolved[s]
                spanning = next((r for r in result['ties'].get('summaries', [])
                                 if r['k0'] == 3 and r['s'] == s and r['spanning']), None)
                if spanning is not None:
                    followups.append({'s': s, 'reused_step_1': True, 'L_N': 2,
                                      'source': {'k0': 3, 's': s,
                                                 'tie_class_indices': spanning['class_indices']}})
                elif isinstance(existing['L_N'], int):
                    followups.append({'s': s, 'reused_step_2': True,
                                      'L_N': existing['L_N'], 'source': {'k0': 3, 's': s}})
                else:
                    print(f'CASE QUERY {case_id[:12]} U-followup s={s} budget=900', flush=True)
                    followups.append(query(key, work, store, 3, [s], k_max=10, budget=900))
        result['U_followups'] = followups
        timings['U_followups'] = time.monotonic() - t
        result.update(timings=timings, seconds=time.monotonic()-started,
                      external_certificate_seconds=store.external_seconds,
                      reused_external_certificate_seconds=store.reused_external_seconds,
                      refutations=store.records, incomplete_certifications=store.incomplete)
        atomic_json(HERE / 'case_results' / payload['pop'] / (case_id + '.json'), result)
        print(f'CASE DONE {payload["pop"]} {case_id} seconds={result["seconds"]:.1f}', flush=True)
        return result
    finally:
        if work.exists():
            shutil.rmtree(work)
