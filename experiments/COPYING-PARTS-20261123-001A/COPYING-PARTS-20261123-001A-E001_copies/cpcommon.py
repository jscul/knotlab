"""Shared helpers of COPYING-PARTS-20261123-001A-E001.

Imports ticket A's engine (experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py)
without copying or changing it: ticket A's folder is appended to sys.path and only `engine` is imported from it.
Readings: deviations.md of this folder (C0 to C15) and ticket A's D1-D22.

Contents: output folder (COPYING_OUT overrides it, for the determinism rerun), JSON writing, the starts of this study,
the nine laws, two-knot parts and N(t), shapes of parts, parts that copy themselves.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
ENGINE_DIR = os.path.join(ROOT, 'experiments', 'RING-IN-BALANCE-20261123-001A',
                          'RING-IN-BALANCE-20261123-001A-E001_ring')
OUT = os.environ.get('COPYING_OUT') or os.path.join(ROOT, 'artifacts', 'COPYING-PARTS-20261123-001A',
                                                     'COPYING-PARTS-20261123-001A-E001_copies')
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if ENGINE_DIR not in sys.path:
    sys.path.append(ENGINE_DIR)          # appended: nothing of ticket A shadows this folder's modules

import engine as E  # noqa: E402

T0 = time.time()


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


ENGINE_SHA = sha256(os.path.join(ENGINE_DIR, 'engine.py'))
ENGINE_SHA_EXPECTED = '2c6eac5645658a2992d54c63205156f22c45489ef0bd5eea0c8b5fcee2917671'
if ENGINE_SHA != ENGINE_SHA_EXPECTED:
    raise SystemExit('engine.py has changed: %s' % ENGINE_SHA)
if os.path.dirname(os.path.abspath(E.__file__)) != ENGINE_DIR:
    raise SystemExit('imported the wrong engine: %s' % E.__file__)


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def resources():
    return {'seconds': round(time.time() - T0, 1), 'peak_rss_mb': peak_mb()}


def write(name, obj, gz=False):
    os.makedirs(OUT, exist_ok=True)
    obj = dict(obj)
    obj['engine_sha256'] = ENGINE_SHA
    path = os.path.join(OUT, name + ('.gz' if gz else ''))
    data = json.dumps(obj, indent=1, sort_keys=True).encode()
    if gz:
        with gzip.GzipFile(path, 'wb', mtime=0) as f:
            f.write(data)
    else:
        with open(path, 'wb') as f:
            f.write(data)
    print('wrote', path, len(data), 'bytes', resources(), flush=True)
    return path


def load(name):
    path = os.path.join(OUT, name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    with gzip.open(path + '.gz', 'rt') as f:
        return json.load(f)


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


# ===================================================================================================  starts

TWO_KNOT_STARS = [[0, 1, 2], [0, 3, 4]]
THREE_KNOT_STARS = [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 6, 7]]


def two_knot_start():
    """Two three-place knots sharing one distinction (pre-registration, 'Definitions added')."""
    return E.from_stars(TWO_KNOT_STARS)


def three_knot_start():
    """A dead knot [0,1,2,3] with two knots [0,1,4,5] and [2,3,6,7], each sharing two distinctions with it."""
    return E.from_stars(THREE_KNOT_STARS)


SMALL_STARTS = (('two-knot', two_knot_start), ('three-knot', three_knot_start))
RUN1_STARTS = SMALL_STARTS + (('Ring(5,3)', lambda: E.ring(5, 3)),)

# ===================================================================================================  laws

RATIONS3 = ('FLOOR0', 'FLOOR1', 'ONE-FEWER')
TREATMENTS3 = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
TSHORT = {'CANCEL-RETIRE': 'retire', 'CANCEL-OFFSHOOT': 'offshoot', 'CANCEL-WAIT': 'wait'}


def nine_laws(**kw):
    return [E.Law(r, t, **kw) for r in RATIONS3 for t in TREATMENTS3]


def law_literal(ration, treatment, release='RELEASE', no_offshoot=False, fillers=False, knot_law='parity'):
    """deviations.md C8-b: a law the engine's constructor refuses (NO-OFFSHOOT with CANCEL-OFFSHOOT), built with an
    admitted treatment and then given its treatment; the engine's round code is unchanged."""
    if not (no_offshoot and treatment == 'CANCEL-OFFSHOOT'):
        return E.Law(ration, treatment, release, no_offshoot, fillers, knot_law)
    L = E.Law(ration, 'CANCEL-WAIT', release, no_offshoot, fillers, knot_law)
    L.treatment = 'CANCEL-OFFSHOOT'
    return L


def law_key(law):
    return law.name()


# ===============================================================================================  two-knot parts

def part_maxsets(roster, members):
    ms = set(members)
    return [M for M in roster.maxsets if next(iter(M)) in ms]


def is_two_knot_part(roster, i):
    """deviations.md C1."""
    P = roster.parts[i]
    if len(P) != 2 or not roster.part_past_start[i]:
        return False
    if any(roster.h[u] != 2 or roster.k[u] != 0 for u in P):
        return False
    ms = roster.part_maxsets(i)
    return len(ms) == 1 and ms[0] == frozenset(P)


def two_knot_parts(roster):
    return [i for i in range(len(roster.parts)) if is_two_knot_part(roster, i)]


def N_series(run):
    return [len(two_knot_parts(r)) for r in run.rosters]


def part_shape(roster, members):
    msets = part_maxsets(roster, members)
    return {'n': len(members), 'h': sorted(roster.h[u] for u in members), 'k': sorted(roster.k[u] for u in members),
            'metset_sizes': sorted(len(M) for M in msets)}


def shape_key(sh):
    return 'n%d h%s k%s m%s' % (sh['n'], ','.join(map(str, sh['h'])), ','.join(map(str, sh['k'])),
                                ','.join(map(str, sh['metset_sizes'])))


def part_detail(run, s, members):
    """Members with h and k, inclusion-maximal met sets with their common knots."""
    ros = run.rosters[s]
    ms = set(members)
    sets = []
    for M, com in zip(ros.maxsets, ros.commons):
        if next(iter(M)) in ms:
            sets.append({'members': sorted(M), 'common_knots': list(com)})
    return {'round': s, 'members': [[u, ros.h[u], ros.k[u]] for u in sorted(members)], 'met_sets': sets,
            'past_start': not any(u in ros.meets_member for u in members)}


# ===========================================================================================  copying parts

def copy_returns(run):
    """Every return (A-D6) that gives off at least one part the same as the returning part (deviations.md C7).
    Each item: the engine's return record plus 'same_off' (indices into off_parts that are the same as Y)."""
    out = []
    for r in run.find_returns():
        if r['n_off'] == 0:
            continue
        ros_s = run.rosters[r['s']]
        ros_t = run.rosters[r['t']]
        Y = tuple(r['part'])
        same = [j for j, P in enumerate(r['off_parts']) if run.cache.same(ros_s, Y, ros_t, tuple(P))]
        if same:
            rr = dict(r)
            rr['same_off'] = same
            out.append(rr)
    return out


def brief_return(run, r):
    ros_s = run.rosters[r['s']]
    ros_t = run.rosters[r['t']]
    return {'s': r['s'], 't': r['t'], 'period': r['period'], 'part': r['part'],
            'shape': part_shape(ros_s, r['part']), 'n_off': r['n_off'],
            'off': [part_shape(ros_t, P) for P in r['off_parts']],
            'n_same_off': len(r.get('same_off', []))}


def copying_summary(run, crs=None):
    """Distinct kinds of part that copy themselves: by shape and period, with count and first (s, t)."""
    crs = copy_returns(run) if crs is None else crs
    by = {}
    for r in crs:
        sh = part_shape(run.rosters[r['s']], r['part'])
        key = shape_key(sh) + ' p%d' % r['period']
        b = by.get(key)
        if b is None:
            by[key] = {'shape': sh, 'period': r['period'], 'count': 1, 'first_s': r['s'], 'first_t': r['t'],
                       'first_part': r['part'], 'n_off_first': r['n_off']}
        else:
            b['count'] += 1
    return {'copies': bool(crs), 'n_copy_returns': len(crs),
            'smallest': (min(len(r['part']) for r in crs) if crs else None),
            'kinds': [by[k] for k in sorted(by, key=lambda k: (by[k]['shape']['n'], by[k]['first_s'], k))]}
