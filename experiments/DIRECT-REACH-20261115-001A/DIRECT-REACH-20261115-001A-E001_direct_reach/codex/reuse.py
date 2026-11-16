"""Read-only census imports; all writable execution state lives beside this file."""
import hashlib
import importlib.util
import os
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'
CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
os.environ['TMPDIR'] = str(HERE / 'tmp')
os.environ['REACH_KEEP_DIR'] = str(HERE / 'certificates')


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SOURCE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pattern = load('pattern', 'pattern.py')
certificates = load('certificates', 'certificates.py')
compiled_search = load('compiled_search', 'compiled_search.py')
search = load('search', 'search.py')


def provenance():
    names = ('pattern.py', 'input_addr.py', 'job.py', 'search.py', 'compiled_search.py',
             'certificates.py', 'input_certify.py', 'lrat_check')
    local_names = ('reuse.py', 'population.py', 'retention.py', 'ties.py', 'reach.py',
                   'homomorphisms.py', 'hom_gate.py', 'tie_gate.py', 'job.py',
                   'gate_job.py', 'smoke_job.py', 'gates.py')
    return {'implementation': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in local_names},
            'sources': {str(SOURCE / n): hashlib.sha256((SOURCE / n).read_bytes()).hexdigest()
                        for n in names},
            'census': {'path': str(CENSUS), 'sha256': hashlib.sha256(CENSUS.read_bytes()).hexdigest()}}


def freeze_provenance():
    raw = (json.dumps(provenance(), sort_keys=True, indent=2) + '\n').encode()
    digest = hashlib.sha256(raw).hexdigest()
    directory = HERE / 'source_manifests'
    directory.mkdir(exist_ok=True)
    path = directory / (digest + '.json')
    if path.exists():
        assert path.read_bytes() == raw
    else:
        path.write_bytes(raw)
    return {'sha256': digest, 'path': str(path.relative_to(HERE))}
