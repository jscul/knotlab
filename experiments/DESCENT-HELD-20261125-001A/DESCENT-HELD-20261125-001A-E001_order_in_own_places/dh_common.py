"""Shared helpers of DESCENT-HELD-20261125-001A-E001: paths, the imported modules (unchanged), data files, JSON output.

Imported without change (pre-registration, first paragraph):
  lr_core.py   of experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/
  cpcensus.py  of experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies/  (deviations 15)
  knots.py     of experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'artifacts', 'DESCENT-HELD-20261125-001A', 'DESCENT-HELD-20261125-001A-E001_order_in_own_places')
RESEARCH = os.path.join(ROOT, 'research', 'DESCENT-HELD-20261125-001A')

LR_DIR = os.path.join(ROOT, 'experiments', 'LOCAL-ROUND-20261123-001A', 'LOCAL-ROUND-20261123-001A-E001_local_round')
CP_DIR = os.path.join(ROOT, 'experiments', 'COPYING-PARTS-20261123-001A', 'COPYING-PARTS-20261123-001A-E001_copies')
KN_DIR = os.path.join(ROOT, 'experiments', 'PARTS-MEET-AGAIN-20261124-001A', 'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')

if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.dont_write_bytecode = True


def _import_from(dirname, modname):
    """Import one module from another study's folder, read-only, without putting the folder ahead of ours."""
    import importlib.util
    path = os.path.join(dirname, modname + '.py')
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


lr_core = _import_from(LR_DIR, 'lr_core')
_stub = types.ModuleType('cpcommon')        # deviations 15: cpcensus uses only cpcommon.ROOT
_stub.ROOT = ROOT
sys.modules['cpcommon'] = _stub
cpcensus = _import_from(CP_DIR, 'cpcensus')
knots = _import_from(KN_DIR, 'knots')

compute_groups = lr_core.compute_groups


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


IMPORTED_SHA = {name: sha256(os.path.join(d, name + '.py'))
                for name, d in (('lr_core', LR_DIR), ('cpcensus', CP_DIR), ('knots', KN_DIR))}


def load_json(name):
    with open(os.path.join(RESEARCH, name)) as f:
        return json.load(f)


LAWS_JSON = load_json('laws.json')
STARTS_JSON = load_json('starts.json')
HAND = load_json('hand_cases.json')

T0 = time.time()


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def write(name, obj):
    os.makedirs(OUT, exist_ok=True)
    obj = dict(obj)
    obj['_imported_sha256'] = IMPORTED_SHA
    obj['_written_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    tmp = os.path.join(OUT, name + '.tmp')
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=False, default=_default)
    os.replace(tmp, os.path.join(OUT, name))


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def read_out(name):
    p = os.path.join(OUT, name)
    if not os.path.exists(p) and os.path.exists(p + '.gz'):   # part8.json is stored gzipped (deviations 37)
        import gzip
        with gzip.open(p + '.gz', 'rt') as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)


def log(*a):
    print('[%7.1fs %6.0fMB]' % (time.time() - T0, peak_mb()), *a, flush=True)


def load_avg():
    return os.getloadavg()[0]


def n_procs():
    """At most 6 processes, 4 while the load is above 18 (the brief)."""
    return 4 if load_avg() > 18 else 6
