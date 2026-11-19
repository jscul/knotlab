"""Amendment (logged in contract.json): rerun, with more memory per case, the cases of job.py that exceeded 2 GB.
Same cases, code and caps as job.py; `--param only=<id>,<id>,...` selects them."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402

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
