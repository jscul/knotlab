"""Shared-runner gate cases; no production population is launched."""
from pathlib import Path
import shutil
import sys
import re
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reuse import HERE, pattern, freeze_provenance
from retention import ProofStore, context
from population import populations
from ties import compute_ties
from reach import query
from tie_gate import run_one
from hom_gate import run_gate

ROWS = []
SOURCE_MANIFEST = None
WORK_ROOT = None


def setup(params):
    global ROWS, SOURCE_MANIFEST, WORK_ROOT
    tag = params.get('run_tag', 'gates')
    if re.fullmatch(r'[A-Za-z0-9_-]{1,64}', tag) is None:
        raise ValueError('invalid gate run tag')
    WORK_ROOT = HERE / 'gate_work' / tag
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    (HERE / 'tmp').mkdir(exist_ok=True)
    ROWS = populations()['D']
    SOURCE_MANIFEST = freeze_provenance()


def cases():
    yield 'hom', {'gate': 'G-hom'}
    for index in range(50):
        yield f'tie-{index:02d}', {'gate': 'G-tie', 'index': index}
    for row in ROWS:
        yield 'reach-' + row['id'], {'gate': 'G-reach', 'description': row}


def run(case_id, payload):
    started = time.monotonic()
    print(f'GATE START {case_id}', flush=True)
    work = WORK_ROOT / case_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    store = ProofStore(work, 31 if payload['gate'] == 'G-tie' else 1023)
    try:
        if payload['gate'] == 'G-hom':
            value = run_gate()
            print(f'GATE DONE {case_id} passed={value.get("passed")} seconds={time.monotonic()-started:.1f}', flush=True)
            return {'gate': 'G-hom', 'source_manifest': SOURCE_MANIFEST, **value}
        if payload['gate'] == 'G-tie':
            with context(store):
                value = run_one(payload['index'], work, store)
        else:
            row = payload['description']
            ties = compute_ties(pattern.pattern(row['key'], 9), 1023, work, row['id'], store=store)
            reach = query(row['key'], work, store, 3, [1, 2, 3, 4], k_max=3, budget=300)
            checked = []
            for census, result in zip(row['census']['levels'], reach['levels']):
                s = census['s']
                assert s == result['s']
                spanning = next(r['spanning'] for r in ties['summaries'] if r['k0'] == 3 and r['s'] == s)
                threshold = result['thresholds']['3']
                complete = threshold != 'undecided'
                okay = (spanning == (census['L_N'] == 2)
                        and complete and (threshold == 'yes') == (census['L_N'] <= 3))
                checked.append({'s': s, 'census_L_N': census['L_N'], 'spanning_class': spanning,
                                'threshold': threshold, 'passed': okay})
            value = {'gate': 'G-reach', 'description': row['id'],
                     'passed': all(r['passed'] for r in checked), 'comparisons': checked,
                     'ties': ties, 'threshold_reach': reach}
        value.update(refutations=store.records, incomplete_certifications=store.incomplete,
                     external_certificate_seconds=store.external_seconds,
                     source_manifest=SOURCE_MANIFEST)
        print(f'GATE DONE {case_id} passed={value["passed"]} seconds={time.monotonic()-started:.1f}', flush=True)
        return value
    finally:
        if work.exists():
            shutil.rmtree(work)
