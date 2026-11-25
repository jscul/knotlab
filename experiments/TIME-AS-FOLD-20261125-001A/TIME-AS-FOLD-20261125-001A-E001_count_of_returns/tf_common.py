"""Paths, frozen inputs, the memory cap, output helpers and the reference engines' import (gates only)."""
from __future__ import annotations

import gzip
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
RESEARCH = os.path.join(ROOT, 'research', 'TIME-AS-FOLD-20261125-001A')
OUT = os.path.join(ROOT, 'artifacts', 'TIME-AS-FOLD-20261125-001A', 'TIME-AS-FOLD-20261125-001A-E001_count_of_returns')
PM_DIR = os.path.join(ROOT, 'experiments', 'PARTS-MEET-AGAIN-20261124-001A', 'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
PM_ART = os.path.join(ROOT, 'artifacts', 'PARTS-MEET-AGAIN-20261124-001A', 'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
RING_A = os.path.join(ROOT, 'experiments', 'RING-IN-BALANCE-20261123-001A', 'RING-IN-BALANCE-20261123-001A-E001_ring')
RING_B = os.path.join(ROOT, 'experiments', 'RING-IN-BALANCE-20261123-001B', 'RING-IN-BALANCE-20261123-001B-E001_reference')

MEM_GB = 6


def cap_memory(gb=MEM_GB):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def starts():
    return load_json(os.path.join(RESEARCH, 'starts.json'))


def named_stars():
    return starts()['named']


def ring227():
    """The ring study's 227 starts: (name, stars).  Names as run 5b's list: 'atlas <a> loose <l1,l2,...>'."""
    out = []
    for r in starts()['ring_study_returning_starts']:
        nm = 'atlas %d loose %s' % (r['atlas_index'], ','.join(str(x) for x in r['loose']))
        out.append((nm, r['stars']))
    return out


def rules():
    return load_json(os.path.join(RESEARCH, 'rules.json'))


def compare():
    return load_json(os.path.join(RESEARCH, 'compare.json'))


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def write_json(name, obj, gz=False):
    p = out_path(name)
    if gz:
        with gzip.open(p, 'wt') as f:
            json.dump(obj, f, sort_keys=True, default=_default)
    else:
        with open(p, 'w') as f:
            json.dump(obj, f, indent=1, sort_keys=True, default=_default)
    return p


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def jdump(o):
    return json.dumps(o, sort_keys=True, default=_default)


def import_pm():
    """The engine of the study of parts that meet again, imported unchanged (gates only)."""
    if PM_DIR not in sys.path:
        sys.path.append(PM_DIR)
    import pm  # noqa
    return pm


def import_bref():
    if RING_B not in sys.path:
        sys.path.append(RING_B)
    import bref  # noqa
    return bref


T0 = time.time()


def log(*a):
    print('[%8.1fs]' % (time.time() - T0), *a, flush=True)


def jsonl(name):
    """The JSON lines of an output file; a file kept in parts (name_part1.jsonl.gz, ...: run 1's output, split to keep
    each file under about 20 MB) is read part by part, in order."""
    p = out_path(name)
    paths = [p] if os.path.exists(p) else []
    if not paths:
        i = 1
        while os.path.exists(out_path(name.replace('.jsonl.gz', '_part%d.jsonl.gz' % i))):
            paths.append(out_path(name.replace('.jsonl.gz', '_part%d.jsonl.gz' % i)))
            i += 1
    for q in paths:
        with gzip.open(q, 'rt') as f:
            for line in f:
                yield json.loads(line)
