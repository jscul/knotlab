"""Retry named remaining G-mono memory failures with unchanged case code."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mono_job

RETRY_IDS = set()


def setup(params):
    global RETRY_IDS
    assert json.loads((HERE / 'mono_gate' / 'state.json').read_text())['final']
    RETRY_IDS = set(params['ids'].split(','))
    failures = {r['case'] for r in map(json.loads, (HERE / 'mono_gate' / 'results.jsonl').read_text().splitlines())
                if r['status'] == 'memory'}
    assert RETRY_IDS and RETRY_IDS <= failures
    assert 'b7af5bcb77f74404b9e42ebf5b166c8a405073106163c3a2e171a0e416846dd4' not in RETRY_IDS
    mono_job.setup(params)
    assert RETRY_IDS <= {case_id for case_id, _ in mono_job.cases()}


def cases():
    for case_id, payload in mono_job.cases():
        if case_id in RETRY_IDS:
            yield case_id, payload


def run(case_id, payload):
    assert case_id in RETRY_IDS
    return mono_job.run(case_id, payload)
