"""Shared-runner job for MANY-VALUED-20261119-001B-E001.

Part P: every one of STATES-GROWTH's 146 undefined points (rebuilt by its own trajectory code), with every admissible irredundant
presentation of its allowed states, from two pools: M(S) alone (states-only) and M(S) with the stage's junctions (reads the stage);
presentations grouped up to renaming, one of each grown 3 rounds by the cheapest growth under not-all-equal.
Part X: the advisor's pair of presentations of the same states, one with a non-minimal five-place member.
Part T: the refined states-only growth along every census trajectory of one to four knots (up to 18 distinctions, 6 rounds): on a
saturated stage, grow its presentation; otherwise grow its admissible irredundant presentation from M(S) if it is unique up to
renaming; undefined if there are several or none.  Compared round by round with the cheapest growth; each trajectory records whether a
redundant knot occurred."""
import importlib.util
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import manylib as ML  # noqa: E402
ROOT = ML.ROOT
spec = importlib.util.spec_from_file_location('sg_job', ROOT / 'experiments/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states/job.py')
SG = importlib.util.module_from_spec(spec)
sys.modules['sg_job'] = SG
spec.loader.exec_module(SG)
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def start_of(key):
    a, b = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(a)), 2), b):
        e += [(i, j)] * m
    return SG.J.stars_from(list(a), e)


def redundant(stars, n):
    st = ML.B.states(n, stars, 'nae')
    return any(len(ML.B.states(n, stars[:j] + stars[j + 1:], 'nae')) == len(st) for j in range(len(stars)))


def describe(stars, n=None):
    row = {}
    for pool in ('M', 'stage'):
        pres, nc = ML.presentations(stars, n, pool=pool)
        if pres is None:
            row[pool] = {'candidates': nc, 'too_many': True}
            continue
        cls = ML.iso_classes(pres)
        own = sorted(map(sorted, stars)) in [sorted(map(sorted, p)) for p in pres]
        row[pool] = {'candidates': nc, 'presentations': len(pres), 'classes': len(cls), 'own_in_list': own,
                     'counts_by_class': [ML.grow(c[0]) for c in cls]}
    return row


def part_p(keys):
    out = []
    for key, k in keys:
        stars = start_of(key)
        for _ in range(k):
            n = 1 + max(x for s in stars for x in s)
            _, M = SG.core_of(stars, n)
            v = SG.SL.verdict(stars, M)
            stars, _ = SG.step(SG.renumber(M) if v != 'saturated' else stars)
        out.append(dict(describe(stars), key=key, round=k))
    return {'points': out}


def part_x():
    """The advisor's pair: NAE(a,b,p), NAE(c,d,q), NAE(p,q,r), NAE(a,b,c,d,r) (A, all distinctions held twice) against the same
    with the five-place member replaced by NAE(a,b,c,d) (B); a..d = 0..3, p, q, r = 4, 5, 6."""
    A = [[0, 1, 4], [2, 3, 5], [4, 5, 6], [0, 1, 2, 3, 6]]
    Bp = [[0, 1, 4], [2, 3, 5], [4, 5, 6], [0, 1, 2, 3]]
    sa, sb = ML.B.states(7, A, 'nae'), ML.B.states(7, Bp, 'nae')
    return {'same_states': sorted(sa.tolist()) == sorted(sb.tolist()), 'A': describe(A, 7), 'B': describe(Bp, 7),
            'grow_A': ML.grow(A), 'grow_B': ML.grow(Bp)}


def part_t(keys):
    out = []
    for key in keys:
        stars = start_of(key)
        cheap, so, verdicts, agree, red = stars, stars, [], [], False
        for t in range(SG.CROUNDS):
            n = 1 + max(x for s in so for x in s)
            if n > SG.BMAX:
                break
            red = red or redundant(so, n)
            _, M = SG.core_of(so, n)
            v = SG.SL.verdict(so, M)
            if v == 'saturated':
                use = so
            else:
                pres, _ = ML.presentations(so, n, pool='M')
                cls = ML.iso_classes(pres) if pres else []
                if len(cls) != 1:
                    verdicts.append('several' if cls else 'none')
                    break
                use = cls[0][0]
                v = 'unique'
            verdicts.append(v)
            nxt_s, ns = SG.step(SG.renumber(use))
            nxt_c, nc = SG.step(cheap)
            agree.append(ns == nc)
            if nxt_s is None or nxt_c is None:
                break
            so, cheap = nxt_s, nxt_c
        out.append({'key': key, 'verdicts': verdicts, 'agree': agree, 'redundant': red})
    return {'trajectories': out}


def cases():
    R = load_results(str(ROOT / 'runs/states-growth'))
    T = [t for c, r in sorted(R.items()) if c.startswith('C-') for t in r['result']['trajectories']]
    und = [(t['key'], t['verdicts'].index('undefined')) for t in T if 'undefined' in t['verdicts']]
    for s in range(0, len(und), 15):
        yield f'P-{s // 15:02d}', {'part': 'P', 'keys': und[s:s + 15]}
    yield 'X', {'part': 'X'}
    allk = [t['key'] for t in T]
    for s in range(0, len(allk), 100):
        yield f'T-{s // 100:02d}', {'part': 'T', 'keys': allk[s:s + 100]}


def run(case_id, payload):
    if payload['part'] == 'X':
        return part_x()
    return part_p(payload['keys']) if payload['part'] == 'P' else part_t(payload['keys'])
