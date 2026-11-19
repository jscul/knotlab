"""Amendment (logged in contract.json): rerun, with more memory per case, the cases of job.py that exceeded 4 GB.
Same cases, code and caps as job.py; `--param only=<id>,<id>,...` selects them."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location('ring_pair_job', HERE / 'job.py')
job = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(job)
ONLY = None


def setup(params):
    global ONLY
    ONLY = set(params.get('only', '').split(','))


def cases():
    for cid, pay in job.cases():
        if ONLY is None or cid in ONLY:
            yield cid, pay


def run(case_id, payload):
    return job.run(case_id, payload)
