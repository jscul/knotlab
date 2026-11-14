"""Shared-runner shards for the inexpensive required finite controls."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # Sets single-thread numeric environment before further imports.
from gate_controls import g_brute, g_pattern
from gates import tree_gate
from search import SearchEngine


def cases():
    for name in ('brute', 'pattern', 'tree'):
        yield name, {}


def run(case_id, payload):
    if case_id == 'brute':
        result = g_brute(SearchEngine)

        def fallback(*args, **kwargs):
            kwargs['compiled_optimization'] = False
            return SearchEngine(*args, **kwargs)

        fallback_result = g_brute(fallback)
        job.atomic_json(HERE / 'g_brute_fallback.json', fallback_result)
        result['fallback_validation'] = {
            'passed': fallback_result['passed'], 'case_count': fallback_result['case_count'],
            'checks': fallback_result['checks'], 'evidence': 'g_brute_fallback.json'}
        result['passed'] = result['passed'] and fallback_result['passed']
    elif case_id == 'pattern':
        result = g_pattern()
    elif case_id == 'tree':
        result = tree_gate()
    else:
        raise ValueError(case_id)
    job.atomic_json(HERE / f'g_{case_id}.json', result)
    return {'gate': case_id, 'passed': result['passed'],
            'seconds': result.get('wall_seconds')}
