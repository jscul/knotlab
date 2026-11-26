"""Core of FOLLOWS-THE-FORM-20261125-001A-E001: an independent reading on the shared growth engine.

Written from the frozen texts alone (the drafter's probe programs were not seen):
  research/FOLLOWS-THE-FORM-20261125-001/claim.md, definitions.md   (FF n)
  research/FOLLOWS-THE-FORM-20261125-001A/preregistration.md, seeds.json, disclosed.json
  research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md        (BD2, for the growth only)
Readings taken where the texts leave a choice are numbered in deviations.md of this folder (cited "dev n").

Here: the starts (FF 2: start, bare start, unlinked start), the registered order of runs (dev 1, 2), the descent
(FF 4), what the first seed's descent makes (FF 5), the wider record (FF 5b), the second seed's own births (FF 11) and
start knots in the roster (FF 8).  The growth is ticket B's engine `eng.py`, imported unchanged and read-only.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import gzip
import hashlib
import json
import os
import resource
import time
from collections import Counter

ROOT = '/home/jscul/p-vs-np-contact-first'
HERE = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(ROOT, 'experiments', 'WHAT-A-BIRTH-CARRIES-20261125-001B',
                       'WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
FOLD_DIR = os.path.join(ROOT, 'experiments', 'PARTS-MEET-AGAIN-20261124-001A',
                        'PARTS-MEET-AGAIN-20261124-001A-E001_meet_again')
OUT = os.path.join(ROOT, 'artifacts', 'FOLLOWS-THE-FORM-20261125-001A',
                   'FOLLOWS-THE-FORM-20261125-001A-E001_place_fixed_form_changed')
TICKET = os.path.join(ROOT, 'research', 'FOLLOWS-THE-FORM-20261125-001A')

# the engine's folder is appended, not inserted, so that nothing of ours is shadowed; our modules are named ff_*
if ENG_DIR not in sys.path:
    sys.path.append(ENG_DIR)
import eng  # noqa: E402  (ticket B's engine, unchanged, read-only)

FROZEN = {
    'research/FOLLOWS-THE-FORM-20261125-001A/preregistration.md':
        'f4400f1aa2bd5965c2120c2f758be38616638618e2718a5c1b0b7f4561aa2719',
    'research/FOLLOWS-THE-FORM-20261125-001/definitions.md':
        '437b419adc09f5f3b040bf311f71f415710617236ea3c0a2e0055c54ef6ae60a',
    'research/FOLLOWS-THE-FORM-20261125-001/claim.md':
        '3e6b903de39ce5b22d1c62baa8ef5f72eb63e404c2571571892f889229d53d8d',
    'research/FOLLOWS-THE-FORM-20261125-001A/seeds.json':
        'a1a91894082c2876fc3e98b6d197b8e0e3aa90e65afcecf90bf74bdee504f62d',
    'research/FOLLOWS-THE-FORM-20261125-001A/disclosed.json':
        '79a46181d37aeee53e63505be1f13394ded737ede2856463045f03cebac28c7d',
    'experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/'
    'eng.py': '09017631d84ea56182230be5a4345ae8fbfcc504ae244ad4b34d74c282803a40',
    'research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md':
        'd1af2cf45f6f3d1a4594d98e4762be5d9b4543e8b727c18c28ff0c7369ccae78',
    'experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py':
        '3aa69b5b96505f24f28640ef483c09d8831440ab7ebfcdc4849785ead818dde7',
}


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_frozen():
    for rel, h in FROZEN.items():
        got = sha256(os.path.join(ROOT, rel))
        assert got == h, 'frozen file changed: %s (%s)' % (rel, got)


def cap_memory(gb=6):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


T0 = time.time()


def log(*a):
    print('[%8.1fs]' % (time.time() - T0), *a, flush=True)


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def load_seeds():
    with open(os.path.join(TICKET, 'seeds.json')) as f:
        return json.load(f)


def load_disclosed():
    with open(os.path.join(TICKET, 'disclosed.json')) as f:
        return json.load(f)


class JsonLines:
    def __init__(self, path):
        self.path = path
        self.f = gzip.open(path, 'wt') if path.endswith('.gz') else open(path, 'w')

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True) + '\n')
        self.f.flush()

    def close(self):
        self.f.close()


def read_jsonl(path):
    with (gzip.open(path, 'rt') if path.endswith('.gz') else open(path)) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


# ---------------------------------------------------------------------------------------------------------- FF 2
def seed_names(knots):
    names = sorted({d for k in knots for d in k})
    assert names == list(range(len(names))), ('a seed names its distinctions 0, 1, 2, ...', names)
    return len(names)


def build_start(F, S=None, linked=True):
    """FF 2.  F: {'knots', 'site'}; S: {'knots', 'at'} or None for the bare start.  Returns (stars, n_first, n_second):
    F's knots first, then S's; the first n_first knots are the first seed's, the next n_second the second seed's."""
    nF = seed_names(F['knots'])
    link = nF                                    # the link: the number of F's names
    stars = [list(k) for k in F['knots']]
    stars[F['site']].append(link)                # appended to the site knot's place list
    n_first = len(stars)
    if S is None:                                # the bare start: the link loose on the site knot
        _check_three(stars)
        return stars, n_first, 0
    nS = seed_names(S['knots'])
    off = nF + 1                                 # S's names raised by the number of F's names plus one
    sk = [[d + off for d in k] for k in S['knots']]
    if linked:
        sk[S['at']].append(link)
    else:                                        # the unlinked start: a new name of its own on the held knot
        largest = max([link] + [d for k in sk for d in k])
        assert largest == nF + nS
        sk[S['at']].append(largest + 1)
    stars = stars + sk
    _check_three(stars)
    return stars, n_first, len(sk)


def _check_three(stars):
    # FF 2: every knot of every start has three or more places once the link (or its replacement) is added
    for k in stars:
        assert len(k) >= 3, ('a knot with fewer than three places', stars)
        assert len(set(k)) == len(k)


def held_profile(S):
    """FF 11, the held knot: (places in the start, loose count in the seed, partners in the seed)."""
    knots = S['knots']
    a = S['at']
    cnt = Counter(d for k in knots for d in k)
    loose = sum(1 for d in knots[a] if cnt[d] == 1)
    partners = sum(1 for j, k in enumerate(knots) if j != a and set(k) & set(knots[a]))
    return (len(knots[a]) + 1, loose, partners)


def seed_loose_counts(S):
    knots = S['knots']
    cnt = Counter(d for k in knots for d in k)
    return [sum(1 for d in k if cnt[d] == 1) for k in knots]


def chain_counts(S):
    """For a seed of the family `chains`: its loose counts in row order from the held knot, after checking that it is
    a chain (FF 0) held at its first knot and that the counts are the ones its name lists."""
    knots = S['knots']
    assert S['at'] == 0
    n = len(knots)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            c = len(set(knots[i]) & set(knots[j]))
            assert c == (1 if abs(i - j) == 1 else 0), ('not a chain', S['name'])
    lc = seed_loose_counts(S)
    assert S['name'] == 'chain:' + ','.join(str(x) for x in lc), (S['name'], lc)
    return lc


# ------------------------------------------------------------------------------------------- laws and run order
RATIONS = ('FLOOR1', 'CAP-3', 'ORD')                       # FF 1's order
TREATMENTS = ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')
TAKES = (None, 'MET-SOLE')                                 # no taking rule first


def laws():
    """The 18 laws in the registered order (dev 1): taking rule, then ration, then treatment."""
    return [(take, r, t) for take in TAKES for r in RATIONS for t in TREATMENTS]


def take_label(take):
    return 'none' if take is None else 'sole'


def rounds_for(family):
    return 10 if family == 'chains' else 9          # FF 1


RUNSETS = {
    # runset: (knot law, [(family, first seeds)], linked)
    'R1': ('nae', None, True),
    'R2': ('nae', [('fresh', 'KLMNO')], True),
    'R2u': ('nae', [('fresh', 'KLMNO')], False),
    'R3': ('nae', [('chains', 'KLMNO')], True),
    'R4': ('parity', [('fresh', 'KLMNO')], True),
}


def runset_runs(runset):
    """Every run of a run set in the registered order (dev 2): first seeds in alphabetical order; for R1 within a first
    seed the families as listed (mixed, then chains); laws (dev 1); within a study the bare start, then the second
    seeds in the order of the data file.  A run is a dict of plain values."""
    seeds = load_seeds()
    kl, fams, linked = RUNSETS[runset]
    if runset == 'R1':
        plan = [(f, fam) for f in 'ABCDEFGHIJ' for fam in (('mixed', 'chains') if f in 'ABCDE' else ('second',))]
    else:
        plan = [(f, fam) for fam, fs in fams for f in fs]
        plan.sort(key=lambda x: x[0])
    out = []
    for first, fam in plan:
        for take, ration, treat in laws():
            for sec in [None] + [s['name'] for s in seeds['second'][fam]]:
                out.append({'runset': runset, 'knot_law': kl, 'family': fam, 'first': first, 'take': take,
                            'ration': ration, 'treatment': treat, 'second': sec, 'linked': linked})
    return out


def run_key(r):
    return '|'.join(str(r[k]) for k in ('runset', 'knot_law', 'family', 'first', 'take', 'ration', 'treatment',
                                        'second', 'linked'))


def study_key(r):
    return (r['runset'], r['knot_law'], r['family'], r['first'], take_label(r['take']), r['ration'], r['treatment'])


_SEEDS = None


def seeds_cached():
    global _SEEDS
    if _SEEDS is None:
        s = load_seeds()
        _SEEDS = {'first': s['first'], 'second': {fam: {x['name']: x for x in lst} for fam, lst in s['second'].items()}}
    return _SEEDS


def start_of(r):
    sd = seeds_cached()
    F = sd['first'][r['first']]
    S = None if r['second'] is None else sd['second'][r['family']][r['second']]
    return build_start(F, S, linked=r['linked'])


# ------------------------------------------------------------------------------------------------ FF 4, 5, 5b, 8, 11
def read_run(run, n_first, n_second, first_knots=None, second_knots=None):
    """The per-run record: for each round read, what the first seed's descent makes (FF 5), the wider record (FF 5b),
    the births of the second only (FF 11), the counts by descent; the last round a start knot is a member (FF 8).
    The first seed's start knots are 0..n_first-1 and the second's the next n_second, unless the sets are given (a
    renumbered start, FF 10)."""
    S = run.S
    n_start = n_first + n_second
    assert S.n_start == n_start
    if first_knots is None:
        first_knots = range(n_first)
        second_knots = range(n_first, n_start)
    assert len(set(first_knots)) == n_first and len(set(second_knots)) == n_second
    first = [False] * S.n_knots
    second = [False] * S.n_knots
    for u in first_knots:
        first[u] = True
    for u in second_knots:
        second[u] = True
    make, wider, sec_only, n_own, n_of_first, n_both = [], [], [], [], [], []
    last_member = 0
    for t in range(1, run.rounds_read + 1):
        rec = run.recs[t - 1]
        assert rec['round'] == t
        if any(u < n_start for u in rec['members']):
            last_member = t
        mk, wd = Counter(), Counter()
        so = own = ofirst = both = 0
        for b in rec['births']:
            x = b['id']
            ps = b['parents']
            # FF 4: the parents are the knots that give the birth a loose distinction (one each, checked)
            assert len(ps) == len(b['loose']) and len(set(ps)) == len(ps)
            assert (b['kind'] == 'offshoot') == (len(ps) == 1)
            f1 = any(first[p] for p in ps)
            f2 = any(second[p] for p in ps)
            first[x], second[x] = f1, f2
            places = S.places[x]
            assert places == list(b['inputs']) + list(b['fresh']) and len(b['fresh']) == b['f']
            assert len(places) == len(b['loose']) + len(b['takes']) + b['f']
            entry = ('j' if b['kind'] == 'join' else 'o', len(ps), len(places), b['f'], len(b['takes']))
            is_own = f1 and not f2
            if is_own:
                mk[entry] += 1
                own += 1
            if f1:
                wd[entry + (1 if is_own else 0,)] += 1
                ofirst += 1
            if f1 and f2:
                both += 1
            if f2 and not f1:
                so += 1
        make.append(sorted([list(k) + [v] for k, v in mk.items()]))
        wider.append(sorted([list(k) + [v] for k, v in wd.items()]))
        sec_only.append(so)
        n_own.append(own)
        n_of_first.append(ofirst)
        n_both.append(both)
    # the roster the next round would start with, read on the final structure (dev 6)
    member_final = any(S.hk(u)[0] > 0 for u in range(n_start))
    return {'rounds_read': run.rounds_read, 'stop': run.stop, 'guard': run.guard, 'knots': S.n_knots,
            'make': make, 'wider': wider, 'sec_only': sec_only, 'n_own': n_own, 'n_of_first': n_of_first,
            'n_both': n_both, 'last_member_round': last_member, 'start_member_final': member_final}


def grow(r):
    """Grow one run of the registered list; return (engine Run, n_first, n_second)."""
    stars, n_first, n_second = start_of(r)
    law = eng.Law(ration=r['ration'], treatment=r['treatment'], take=r['take'], knot_law=r['knot_law'])
    run = eng.Run(law, stars=stars, rounds=rounds_for(r['family']), knot_bound=3000)
    return run, n_first, n_second


def do_run(r):
    t0 = time.time()
    run, n_first, n_second = grow(r)
    rec = read_run(run, n_first, n_second)
    rec.update({k: r[k] for k in ('runset', 'knot_law', 'family', 'first', 'take', 'ration', 'treatment', 'second',
                                  'linked')})
    rec['take'] = take_label(r['take'])
    rec['sec'] = round(time.time() - t0, 4)
    return rec
