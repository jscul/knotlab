"""Shared-runner job for CENSUS-READ-20261118-001A-E001, Amendment 2: names.  On every census stage and mixed stage (the same
stages and tables as job.py), the name-free reader R3n at the full table and pooled above largest - 1 and largest - 2, and both
R3 and R3n under three renamings of the distinctions (seeded by the stage)."""
import json
import random
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import reader3n as N  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A


def setup(params):
    job.setup(params)


def cases():
    yield from job.cases()


def renamed(reader, table, perm, top):
    t = {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}
    inv = {v: k for k, v in perm.items()}
    return {frozenset(inv[x] for x in s) for s in reader(t, top)}


def read_names(stars, seed):
    stars = [frozenset(s) for s in stars]
    truth = set(stars)
    own = R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    n = len(stars)
    K = max(map(len, stars))
    H = K + 2
    table, _ = R.bond_table(stars, n if n <= 14 else 6, H)
    flags = __import__('collections').Counter()
    out = {'junctions': n, 'largest': K, 'loose': len(loose), 'connectivity': job.connectivity(stars),
           'max_shared': max([c for c in __import__('collections').Counter(
               tuple(sorted(js)) for js in own.values() if len(js) == 2).values()] or [0])}
    out['r3n'] = job.verdict(N.r3n(table, H + 1, flags), truth, loose)
    out['flags'] = dict(flags)
    for h in (K - 1, K - 2):
        if h >= 1:
            out[f'r3n_h{h - K + 1:+d}'] = job.verdict(N.r3n(R.pooled(table, h), h + 1), truth, loose)
    labels = sorted(own)
    rng = random.Random(seed)
    perms = []
    for _ in range(3):
        img = list(labels)
        rng.shuffle(img)
        perms.append(dict(zip(labels, img)))
    out['r3_renamed'] = [job.verdict(renamed(R3.r3, table, p, H + 1), truth, loose) for p in perms]
    out['r3n_renamed'] = [job.verdict(renamed(N.r3n, table, p, H + 1), truth, loose) for p in perms]
    return out


def census_stages(key):
    P = S.from_junctions(A.stars_of(key))
    stages = []
    tag = json.dumps([list(key[0]), list(key[1])])
    for r in range(job.RMAX + 1):
        if len(P.bits_of) > job.JCAP:
            break
        st = read_names(P.bits_of, zlib.crc32(f'{tag}/{r}'.encode()))
        st['round'] = r
        stages.append(st)
        if r == job.RMAX:
            break
        res = P.step(S.gf2(F.fewest), None)
        if res is None or res['new'] == 0:
            break
    return {'key': [list(key[0]), list(key[1])], 'stages': stages}


def mixed_stages(seed):
    rng = random.Random(seed)
    a = rng.choice([3, 4])
    q = rng.choice([0.1, 0.2, 0.4])
    P = F.Presentation(a)
    stages = []
    for _ in range(6):
        if len(P.bits_of) > 16:
            break
        st = read_names(P.bits_of, zlib.crc32(f'mixed/{seed}/{P.rounds}'.encode()))
        st['round'] = P.rounds
        stages.append(st)
        s = P.step(F.surplus(q), None, rng)
        if s is None or s['new'] == 0:
            break
    return {'seed': seed, 'stages': stages}


def run(case_id, p):
    if p['part'] == 'mixed':
        return mixed_stages(p['seed'])
    data = job._ARR if job._ARR is not None else job.load()
    return {'arrangements': [census_stages(k) for k in data[p['lo']:p['hi']]]}
