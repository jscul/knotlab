"""Shared-runner job for UNIQUE-TABLE-20261119-001A-E001, Amendment 1: the main run's cases that timed out (600 seconds, three
attempts), rerun with a longer limit, and the 5 + 59 stages of population_unknown.json.  --param timedout=pop-0237,... names them."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job as J  # noqa: E402

_T = []
_U = None


def setup(params):
    global _T, _U
    J.setup(params)
    _T = [x for x in params.get('timedout', '').split(',') if x]
    _U = json.loads((HERE / 'population_unknown.json').read_text())


def cases():
    main = dict(J.cases())
    for c in _T:
        yield c, main[c]
    for i, row in enumerate(_U['population']):
        yield f'popu-{i:04d}', {'part': 'population', **row}
    for i, row in enumerate(_U['controls']):
        yield f'ctrlu-{i:04d}', {'part': 'control', **row}


def run(case_id, p):
    return J.run(case_id, p)
