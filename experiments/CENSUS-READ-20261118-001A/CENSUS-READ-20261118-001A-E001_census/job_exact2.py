"""Shared-runner job for CENSUS-READ-20261118-001A-E001, Amendment 4: pass 3 continued at a cost that finishes.

Pass 3 (`job_exact.py`) ran at about 400 seconds a shard of 25 arrangements, nine hours in all.  This job reads the arrangements no
completed pass-3 shard covered, one shard of 10 at a time, with the same exact table and stages:
- every arrangement, every stage of at most 40 junctions: exactly as pass 3 (R1, R3, R3m, R3n, renamings, horizons);
- stages of 41 to 120 junctions, of every 4th arrangement in sorted order only: R3 and R3n with renamings and horizons; R1 and R3m
  are skipped there.
Arrangements outside the sample keep their stages up to 40 junctions.  --param done=0,1,... names the completed pass-3 shards.
"""
import json
import sys
import zlib
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import job_exact as JE  # noqa: E402
R, R3, S, F, A, N, X = job.R, job.R3, job.S, job.F, job.A, JE.N, JE.X
SHARD = 10
SMALL = 40
EVERY = 4
_DONE = set()


def setup(params):
    global _DONE
    job.setup(params)
    _DONE = {int(x) for x in params.get('done', '').split(',') if x}


def covered(i):
    return i // JE.SHARD in _DONE


def cases():
    data = job._ARR
    todo = [i for i in range(len(data)) if not covered(i)]
    for s in range(0, len(todo), SHARD):
        yield f'census2-{s // SHARD:05d}', {'part': 'census', 'idx': todo[s:s + SHARD]}
    for s in range(60):
        yield f'mixed-{s:02d}', {'part': 'mixed', 'seed': 700000 + s}


def read_large(stars, seed):
    """Pass 3's reading without R1 and R3m."""
    saved = JE.job.r3m, JE.R.r1
    try:
        JE.job.r3m = lambda t, top: set()   # placeholders, removed from the output below
        JE.R.r1 = lambda t, top: set()
        out = JE.read_stage(stars, seed)
    finally:
        JE.job.r3m, JE.R.r1 = saved
    for k in [k for k in out if k.startswith('r1') or k.startswith('r3m')]:
        del out[k]
    out['large_sampled'] = True
    return out


def census_stages(i):
    key = job._ARR[i]
    sampled = i % EVERY == 0
    P = S.from_junctions(A.stars_of(key))
    stages, outcome = [], 'alive'
    tag = json.dumps([list(key[0]), list(key[1])])
    for r in range(job.RMAX + 1):
        n = len(P.bits_of)
        if n > job.JCAP:
            outcome = 'cap'
            break
        if n > SMALL and not sampled:
            outcome = 'not_sampled_beyond_40'
            break
        seed = zlib.crc32(f'{tag}/{r}'.encode())
        st = JE.read_stage(P.bits_of, seed) if n <= SMALL else read_large(P.bits_of, seed)
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
    return {'key': [list(key[0]), list(key[1])], 'index': i, 'knots': len(key[0]), 'outcome': outcome,
            'sampled_beyond_40': sampled, 'stages': stages}


def run(case_id, p):
    if p['part'] == 'mixed':
        return JE.mixed_stages(p['seed'])
    return {'arrangements': [census_stages(i) for i in p['idx']]}
