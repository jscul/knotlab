"""Shared-runner job for CENSUS-READ-20261118-001A-E001, Amendment 3: every stage of passes 1 and 2 read again on the exact table
(exact_table.py, no limit on either side), because the gate's side-6-against-side-8 check failed on 199 of 200 large stages.

Per stage: R1, R3 (census naming), R3m and R3n at the full table (exact to largest + 2); R3 and R3n under three seeded renamings;
for R3 and R3n where exact, the verdict at each horizon from largest + 1 down to the first failure and at least down to
largest - 2; the stage's tags (connectivity, two shared, loose, largest).  Shards of 25 arrangements.
"""
import json
import random
import sys
import zlib
from collections import Counter
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import reader3n as N  # noqa: E402
import exact_table as X  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A
SHARD = 25


def setup(params):
    job.setup(params)


def cases():
    data = job._ARR if job._ARR is not None else job.load()
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:04d}', {'part': 'census', 'lo': s, 'hi': min(len(data), s + SHARD)}
    for s in range(60):
        yield f'mixed-{s:02d}', {'part': 'mixed', 'seed': 700000 + s}


def renamed(reader, table, perm, top):
    t = {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}
    inv = {v: k for k, v in perm.items()}
    return {frozenset(inv[x] for x in s) for s in reader(t, top)}


def horizons(reader, table, truth, K, H):
    by_h = {}
    for h in range(H - 1, 0, -1):
        by_h[h] = reader(R.pooled(table, h), h + 1) == truth
        if not by_h[h] and h <= K - 2:
            break
    least = None
    for h in range(H - 1, 0, -1):
        if by_h.get(h):
            least = h
        else:
            break
    return least, {str(h): v for h, v in by_h.items()}


def read_stage(stars, seed, fresh_reader=None):
    stars = [frozenset(s) for s in stars]
    truth = set(stars)
    own = R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    n = len(stars)
    K = max(map(len, stars))
    H = K + 2
    table = X.exact_table(stars, H)
    shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
    out = {'junctions': n, 'distinctions': len(own), 'largest': K, 'loose': len(loose),
           'max_shared': max(shared.values()) if shared else 0, 'connectivity': job.connectivity(stars),
           'min_distance': min(table.values()) if table else None}
    flags = Counter()
    readers = (('r1', lambda t, top: R.r1(t, top)), ('r3', R3.r3), ('r3m', job.r3m),
               ('r3n', lambda t, top: N.r3n(t, top, flags)))
    for name, reader in readers:
        got = reader(table, H + 1)
        out[name] = job.verdict(got, truth, loose)
        if out[name] != 'exact':
            out[name + '_missed'] = len(truth - got)
            out[name + '_extra'] = len(got - truth)
    out['r3n_flags'] = dict(flags)
    if fresh_reader is not None:
        out['fresh_reader'] = fresh_reader(stars)
    labels = sorted(own)
    rng = random.Random(seed)
    perms = []
    for _ in range(3):
        img = list(labels)
        rng.shuffle(img)
        perms.append(dict(zip(labels, img)))
    out['r3_renamed'] = [job.verdict(renamed(R3.r3, table, p, H + 1), truth, loose) for p in perms]
    out['r3n_renamed'] = [job.verdict(renamed(N.r3n, table, p, H + 1), truth, loose) for p in perms]
    for name, reader in (('r3', R3.r3), ('r3n', N.r3n)):
        if out[name] == 'exact':
            least, by_h = horizons(reader, table, truth, K, H)
            out[name + '_least_horizon'] = least
            out[name + '_by_horizon'] = by_h
    return out


def census_stages(key):
    P = S.from_junctions(A.stars_of(key))
    stages, outcome = [], 'alive'
    tag = json.dumps([list(key[0]), list(key[1])])
    for r in range(job.RMAX + 1):
        if len(P.bits_of) > job.JCAP:
            outcome = 'cap'
            break
        st = read_stage(P.bits_of, zlib.crc32(f'{tag}/{r}'.encode()))
        st['round'] = r
        stages.append(st)
        if r == job.RMAX:
            break
        res = P.step(S.gf2(F.fewest), None)
        if res is None:
            outcome = 'stall'
            break
        if res['new'] == 0:
            outcome = 'closed'
            break
    return {'key': [list(key[0]), list(key[1])], 'knots': len(key[0]), 'outcome': outcome, 'stages': stages}


def mixed_stages(seed):
    rng = random.Random(seed)
    a = rng.choice([3, 4])
    q = rng.choice([0.1, 0.2, 0.4])
    P = F.Presentation(a)
    stages = []
    for _ in range(6):
        if len(P.bits_of) > 16:
            break
        st = read_stage(P.bits_of, zlib.crc32(f'mixed/{seed}/{P.rounds}'.encode()), job.fresh_reader())
        st['round'] = P.rounds
        stages.append(st)
        s = P.step(F.surplus(q), None, rng)
        if s is None or s['new'] == 0:
            break
    return {'seed': seed, 'a': a, 'q': q, 'stages': stages}


def run(case_id, p):
    if p['part'] == 'mixed':
        return mixed_stages(p['seed'])
    data = job._ARR if job._ARR is not None else job.load()
    return {'arrangements': [census_stages(k) for k in data[p['lo']:p['hi']]]}
