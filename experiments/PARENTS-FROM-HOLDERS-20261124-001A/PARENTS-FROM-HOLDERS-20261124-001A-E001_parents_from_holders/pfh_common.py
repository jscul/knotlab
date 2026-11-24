"""Paths, the reference engine and the earlier study's modules (read-only), and the twenty pairs of start and law.

The reference engine (RING-IN-BALANCE-20261123-001A, engine.py) is loaded by the one-birth-at-a-time study's
lr_reference.py, which checks its SHA-256 sum on every import.  Nothing in either folder is changed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LR_DIR = ROOT / 'experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round'
LR_ART = ROOT / 'artifacts/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round'
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
if os.environ.get('PFH_OUT'):
    OUT = Path(os.environ['PFH_OUT'])     # development runs only; registered runs leave it unset
SCRATCH = Path(os.environ.get('PFH_SCRATCH', '/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/7d6e7b9e-634d-564b-a5b8-21bd756b246b/scratchpad/pfh_impl'))
PREREG = ROOT / 'research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md'
SHARED = ROOT / 'research/RING-IN-BALANCE-20261123-001/definitions.md'
PREREG_SHA = '55a86f0886883b16a7ddfd4962c0200e4fb2091a10082b05fd3843d1ff05bab8'
SHARED_SHA = 'e7c001a446d16565181d5805c73c68bbcaff82022b37412463b545e95cb52648'

if str(LR_DIR) not in sys.path:
    sys.path.insert(0, str(LR_DIR))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lr_core as LRC        # noqa: E402  starts (start_stars)
import lr_reference as LRR   # noqa: E402  the reference engine, checked
E = LRR.E

LAW_NAMES = {
    ('RATION-3', 'CANCEL-WAIT'): 'RATION-3/CANCEL-WAIT/RELEASE',
    ('FLOOR1', 'CANCEL-OFFSHOOT'): 'FLOOR1/CANCEL-OFFSHOOT/RELEASE',
    ('FLOOR1', 'CANCEL-RETIRE'): 'FLOOR1/CANCEL-RETIRE/RELEASE',
    ('ORD', 'STALL'): 'ORD/STALL/RELEASE',
}
LAW_SHORT = {
    ('RATION-3', 'CANCEL-WAIT'): 'R3W',
    ('FLOOR1', 'CANCEL-OFFSHOOT'): 'F1O',
    ('FLOOR1', 'CANCEL-RETIRE'): 'F1R',
    ('ORD', 'STALL'): 'ORD',
}
SHORT_LAW = {v: k for k, v in LAW_SHORT.items()}


def check_frozen():
    for p, h in ((PREREG, PREREG_SHA), (SHARED, SHARED_SHA)):
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != h:
            raise RuntimeError('frozen text changed: %s %s' % (p, got))
    c = json.loads((HERE / 'contract.json').read_text())
    if c['preregistration_sha256'] != PREREG_SHA or c['shared_definitions_sha256'] != SHARED_SHA:
        raise RuntimeError('contract.json does not match')
    return True


def gate_pairs():
    """The twenty pairs of the earlier study's gate.json: (start, (ration, treatment), rounds_checked)."""
    g = json.loads((LR_ART / 'gate.json').read_text())
    out = []
    for p in g['pairs']:
        out.append((p['start'], tuple(p['law']), p['rounds_checked']))
    if len(out) != 20:
        raise RuntimeError('gate.json does not list twenty pairs')
    return out


def ref_law(fam):
    return E.Law(ration=fam[0], treatment=fam[1])


def start_struct(start):
    return E.from_stars(LRC.start_stars(start))


def write_json(path, obj, gz_over=15_000_000):
    import gzip
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, indent=None, separators=(',', ':'), default=_default)
    if len(data) > gz_over:
        with gzip.open(str(path) + '.gz', 'wt') as fh:
            fh.write(data)
        return str(path) + '.gz'
    path.write_text(data)
    return str(path)


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(repr(type(o)))
