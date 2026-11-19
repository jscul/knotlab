"""Post hoc readout (logged in contract.json): the two starts over the frozen run's 3.5 GB cap (G-000, the theta, and G-009),
grown by job.py's child with 10 GB and 3,000 s, recording groups.  The theta was already regrown so in pilot/theta_groups.py
(18 rounds); this run covers G-009 under the shared runner."""
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
    pop = json.loads((HERE / 'population.json').read_text())
    yield 'G-009', {'start': pop[9]}


def run(case_id, payload):
    return job.run(case_id, payload)
