"""Paths, frozen hashes, memory cap and output of WHAT-A-BIRTH-CARRIES-20261125-001B-E001."""
import sys

sys.dont_write_bytecode = True

import gzip
import hashlib
import json
import os
import resource
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/home/jscul/p-vs-np-contact-first'
OUT = os.path.join(ROOT, 'artifacts', 'WHAT-A-BIRTH-CARRIES-20261125-001B',
                   'WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
TICKET = os.path.join(ROOT, 'research', 'WHAT-A-BIRTH-CARRIES-20261125-001B')
TICKET_A = os.path.join(ROOT, 'research', 'WHAT-A-BIRTH-CARRIES-20261125-001A')
if HERE not in sys.path:
    sys.path.insert(0, HERE)

T0 = time.time()

FROZEN = {
    'research/WHAT-A-BIRTH-CARRIES-20261125-001B/preregistration.md':
        'b446100194b6616ee12dac039175b44bc1156274a9494ad7cd95f244043cf4aa',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md':
        'd1af2cf45f6f3d1a4594d98e4762be5d9b4543e8b727c18c28ff0c7369ccae78',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/claim_b.md':
        '0d640468dfcf11aa643beb662d7d6b0b163dd170fe7493e992141a06d4653c70',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001B/family.json':
        'c504aaddf522974ca8f07fb380d3003eb121e94ca48f6055fac317a1592c79f8',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json':
        'df90a204fbb081ad3e07c31d3594a8f9dac72723781babb341d7b37e27772f30',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001B/renamings.json':
        '3471ee351f163a8f488ccd8e410b564d273299f55fb6a6f9080f7acde6be3369',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001B/gate_listing_b.txt':
        '9faa6b48b78233df422f2ca0e1e14d4ae71ecca48144c747d55308e480f334e4',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions.md':
        '3b5378ec013938ae7ac8399dbe91187d36abf510a10e2a512a0d3853fd3f4160',
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
        self.f.flush()

    def close(self):
        self.f.close()
        log('wrote', self.path, os.path.getsize(self.path), 'bytes')


def read_jsonl(name):
    p = out_path(name)
    with (gzip.open if name.endswith('.gz') else open)(p, 'rt') as f:
        for line in f:
            yield json.loads(line)


def load(name):
    with open(os.path.join(TICKET, name)) as f:
        return json.load(f)
