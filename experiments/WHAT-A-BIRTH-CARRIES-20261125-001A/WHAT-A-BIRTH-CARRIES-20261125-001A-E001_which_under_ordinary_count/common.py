"""Paths, memory cap, output and the class lists of WHAT-A-BIRTH-CARRIES-20261125-001A-E001."""
import sys

sys.dont_write_bytecode = True

import gzip
import hashlib
import json
import os
import resource
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/home/jscul/p-vs-np-contact-first'
OUT = os.path.join(ROOT, 'artifacts', 'WHAT-A-BIRTH-CARRIES-20261125-001A',
                   'WHAT-A-BIRTH-CARRIES-20261125-001A-E001_which_under_ordinary_count')
TICKET = os.path.join(ROOT, 'research', 'WHAT-A-BIRTH-CARRIES-20261125-001A')
if HERE not in sys.path:
    sys.path.insert(0, HERE)

T0 = time.time()

FROZEN = {
    'research/WHAT-A-BIRTH-CARRIES-20261125-001A/preregistration.md':
        '730716a606fc0b933793b62f422941654bc5719237128723916b38e0a5eb3497',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions.md':
        '3b5378ec013938ae7ac8399dbe91187d36abf510a10e2a512a0d3853fd3f4160',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/claim.md':
        '99bf7df4a80c98d607ac7f4286be8a142f89dd7d7f28ceb93d84fe6a617bc811',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001A/numberings.json':
        '8bc25791071d88321c62802b3377644d79f5a4c198213133cd5e03d9af4a03e7',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001A/gate_listing.txt':
        'ca1354e85f45b20ec9f88fc6133970543bf3b5325493916029c6ad799ddd2dea',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001A/attribution_records.json':
        'e0909c44e77a8027c5040640815b19ce1c500da25c6fcafe08babcfec9200f57',
}


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_frozen():
    for rel, h in FROZEN.items():
        assert sha256(os.path.join(ROOT, rel)) == h, 'frozen file changed: ' + rel


def cap_memory(gb=6):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def log(*a):
    print('[%8.1fs]' % (time.time() - T0), *a, flush=True)


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def write_json(name, obj):
    p = out_path(name)
    op = gzip.open if name.endswith('.gz') else open
    with op(p, 'wt') as f:
        json.dump(obj, f, sort_keys=True, default=_default, indent=None if name.endswith('.gz') else 1)
    log('wrote', p, os.path.getsize(p), 'bytes')
    return p


class JsonLines:
    def __init__(self, name):
        self.path = out_path(name)
        self.f = (gzip.open if name.endswith('.gz') else open)(self.path, 'wt')

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, default=_default) + '\n')

    def close(self):
        self.f.close()
        log('wrote', self.path, os.path.getsize(self.path), 'bytes')


def read_jsonl(name):
    p = out_path(name)
    with (gzip.open if name.endswith('.gz') else open)(p, 'rt') as f:
        for line in f:
            yield json.loads(line)


def numberings():
    with open(os.path.join(TICKET, 'numberings.json')) as f:
        return json.load(f)


def class_by_nu(h):
    """{underlying numbering (stars, as a tuple): [(a, usable names)]} over a = 0..h, in list order."""
    N = numberings()
    out = defaultdict(list)
    order = []
    for a in range(h + 1):
        for e in N['class_h_by_a']['made-%d|a=%d' % (h, a)]:
            key = json.dumps(e['stars'])
            if key not in out:
                order.append(key)
            out[key].append((a, sorted(e['usable'])))
    made = [json.dumps(s) for s in N['made_class']['made-%d' % h]]
    assert sorted(order) == sorted(made) and len(order) == len(made), 'class entries do not cover made_class'
    for k in order:
        assert len(out[k]) == 2 ** h, (k, len(out[k]))
    return [(made.index(k), json.loads(k), out[k]) for k in made]
