"""Shared helpers of the run scripts: output folder, JSON writing, resource readings."""
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'artifacts', 'RING-IN-BALANCE-20261123-001A',
                                    'RING-IN-BALANCE-20261123-001A-E001_ring'))
os.makedirs(OUT, exist_ok=True)

import engine as E  # noqa: E402

T0 = time.time()


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def resources():
    return {'seconds': round(time.time() - T0, 1), 'peak_rss_mb': peak_mb()}


def write(name, obj):
    path = os.path.join(OUT, name)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    print('wrote', path, resources(), flush=True)
    return path


def load(name):
    with open(os.path.join(OUT, name)) as f:
        return json.load(f)


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


START_BUILDERS = {'ring': E.ring, 'd2': E.d2, 'dw': E.dw}


def start_name(kind, n, a):
    return {'ring': 'Ring', 'd2': 'D2', 'dw': 'DW'}[kind] + '(%d, %d)' % (n, a)
