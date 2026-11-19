"""Amendment (logged in contract.json, added after the freeze): the referee's three shapes from LOOP-CATALOGUE-20261119-001's R1,
which no list grew (population_ref.json): two triangles of knots joined by one shared distinction, two triangles joined by two,
and the three-regular six-knot graph, with spares.  Grown and read as job.py's cases, with a 10 GB child and 3,000 s."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('break_eddies_job', HERE / 'job.py')
job = importlib.util.module_from_spec(_spec)
sys.modules['break_eddies_job'] = job
_spec.loader.exec_module(job)
job.CHILD_AS = 10 * 2 ** 30


def cases():
    for i, st in enumerate(json.loads((HERE / 'population_ref.json').read_text())):
        yield f'F-{i:02d}', {'start': st}


def run(case_id, payload):
    return job.run(case_id, payload)
