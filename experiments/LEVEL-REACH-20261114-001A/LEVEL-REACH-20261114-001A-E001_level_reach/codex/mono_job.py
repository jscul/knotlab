"""Shared-runner G-mono only: first 50 pilot keys alive at N=10."""
from pathlib import Path
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job
from pattern import pattern
from search import SearchEngine

SELECTED = []


def setup(params):
    global SELECTED
    job.setup({'pop': 'P'})
    SELECTED = []
    probe = HERE / 'work' / 'mono_selection'
    probe.mkdir(exist_ok=True)
    try:
        for payload in job.POPULATION['keys']:
            K = pattern(payload['key'], 10)
            engine = SearchEngine(K, 2047, probe, certify=False)
            alive = engine.alive
            engine.close()
            if alive:
                SELECTED.append(payload)
            if len(SELECTED) == 50:
                break
        assert len(SELECTED) == 50
        job.atomic_json(HERE / 'mono_selection.json', [p['id'] for p in SELECTED])
    finally:
        shutil.rmtree(probe)


def cases():
    for payload in SELECTED:
        yield payload['id'], payload


def run(case_id, payload):
    work = HERE / 'work' / ('mono_' + case_id)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    start = time.monotonic()
    try:
        nine = job.compute(payload['key'], work, N=9)
        ten = job.compute(payload['key'], work, N=10)
        assert ten['union']['verdict'] == 'alive'
        assert nine['union']['verdict'] == 'alive'
        comparisons = []
        for a, b in zip(nine['levels'], ten['levels']):
            x, y = a['L_N'], b['L_N']
            numeric = isinstance(x, int) and isinstance(y, int)
            comparisons.append({'s': a['s'], 'L_9': x, 'L_10': y,
                                'numeric': numeric, 'passed': y <= x if numeric else None})
        return {'case': case_id, 'key': payload['key'], 'N9': nine, 'N10': ten,
                'comparisons': comparisons,
                'passed': all(c['passed'] is not False for c in comparisons),
                'seconds': time.monotonic() - start}
    finally:
        shutil.rmtree(work)
