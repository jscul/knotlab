"""Amendment run (after the frozen run's census cases errored on starts with no live knot): job.py's census cases only, with
hublib's fix for an empty hub realization. Comparison logic unchanged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import job  # noqa: E402


def cases():
    for c, p in job.cases():
        if c.startswith('census'):
            yield c, p


def run(case_id, payload):
    return job.run(case_id, payload)
