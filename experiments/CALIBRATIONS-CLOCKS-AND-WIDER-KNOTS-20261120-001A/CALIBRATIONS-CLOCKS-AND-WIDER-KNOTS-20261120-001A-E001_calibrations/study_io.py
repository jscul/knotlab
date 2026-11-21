"""Paths and reproducible serialization for exact calibration comparisons."""
import gzip
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
RESEARCH = ROOT / 'research' / HERE.parent.name
VERIFY_ONLY = False

def family(ticket, kind='experiments'):
    return next((ROOT / kind / ticket).glob('*-E001_*'))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def write(name, record):
    raw = (json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode()
    if name.endswith('.gz'):
        raw = gzip.compress(raw, mtime=0)
    target = OUT / name
    if VERIFY_ONLY:
        if target.read_bytes() != raw:
            raise ValueError(f'Replay differs from {target}')
    else:
        target.write_bytes(raw)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def failed(word, supports, law):
    values = [(word & sum(1 << bit for bit in row)).bit_count() for row in supports]
    return [j for j, (k, row) in enumerate(zip(values, supports)) if (k % 2 if law == 'parity' else k in (0,len(row)))]

def allowed(supports, law):
    return {x for x in range(1 << (1 + max(map(max,supports)))) if not failed(x,supports,law)}

def plus(n, m):
    return str(Fraction(n + m, 2 * n))
