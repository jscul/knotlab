"""Post hoc readout: the theta (and G-009) grown with job.py's child at 10 GB, recording groups (after the frozen run, whose
runner cap of 3.5 GB stopped both)."""
import importlib.util, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bej', HERE.parent / 'job.py'); job = importlib.util.module_from_spec(spec); spec.loader.exec_module(job)
job.CHILD_AS = 10 * 2 ** 30
pop = json.loads((HERE.parent / 'population.json').read_text())
out = {}
for i in (0, 9):
    out[i] = job.grow(pop[i])
    print(i, pop[i]['sizes'], out[i]['stop'], out[i]['counts'][-6:], out[i]['group'][-6:], flush=True)
(HERE / 'theta_groups.json').write_text(json.dumps(out))
