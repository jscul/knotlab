"""Paths, output, memory cap and logging shared by the run scripts of PARTS-MEET-AGAIN-20261124-001A-E001."""
import gzip
import importlib.util
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'artifacts', 'PARTS-MEET-AGAIN-20261124-001A', 'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
sys.path.insert(0, HERE)

RING_ENGINE = os.path.join(ROOT, 'experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py')
RLAW_DIR = os.path.join(ROOT, 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/'
                              'REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law')
QLAW_DIR = os.path.join(ROOT, 'experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread')
SHA = {'ring_engine': '2c6eac5645658a2992d54c63205156f22c45489ef0bd5eea0c8b5fcee2917671',
       'rlaw': '29aa3d9112d4a12b2d7970756c455e11dd3ed7abaef99b85daa64f4c4222d8f8',
       'qlaw': '457abaa5a05e05785282b31dcd5f58a5eb6181f0a1a7adf7df81d4867c747942'}

T0 = time.time()


def cap_memory(gb=8):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def log(*a):
    print('[%8.1fs %6.0fMB]' % (time.time() - T0, peak_mb()), *a, flush=True)


def sha256(path):
    import hashlib
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def ring_engine():
    assert sha256(RING_ENGINE) == SHA['ring_engine'], 'the ring engine differs from the one named'
    return load_module('ring_engine', RING_ENGINE)


def rq_engines():
    """rlaw and qlaw, unchanged.  rlaw.USE_C = False so that nothing is ever built in that ticket's folder."""
    assert sha256(os.path.join(RLAW_DIR, 'rlaw.py')) == SHA['rlaw']
    assert sha256(os.path.join(QLAW_DIR, 'qlaw.py')) == SHA['qlaw']
    sys.path.insert(0, RLAW_DIR)
    import rlaw
    rlaw.USE_C = False
    sys.path.insert(0, QLAW_DIR)
    import qlaw
    rlaw.USE_C = False
    return rlaw, qlaw


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def write_json(name, obj):
    p = out_path(name)
    op = gzip.open if name.endswith('.gz') else open
    with op(p, 'wt') as f:
        json.dump(obj, f, sort_keys=True, default=_default)
    log('wrote', p, os.path.getsize(p), 'bytes')
    return p


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


class JsonLines:
    def __init__(self, name):
        p = out_path(name)
        self.path = p
        self.f = (gzip.open if name.endswith('.gz') else open)(p, 'wt')

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, default=_default) + '\n')
        self.f.flush()

    def close(self):
        self.f.close()
        log('wrote', self.path, os.path.getsize(self.path), 'bytes')
