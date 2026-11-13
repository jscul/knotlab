"""Shared-runner job for LEVEL-RETURN-20261113-001A: certified verdicts of the 48 returning patterns at levels 1..16, plus the
advisor's R4 cases (description #2 at even levels without the two knots at 0^(n-2)1b of placement [0, 8, 10])."""
import gzip, json, os, sys, tempfile, hashlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex'))
from certify import certify, pattern
KEYS = os.path.join(ROOT, 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz')
TIMEOUT = 1800
RET = []
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
THREE_SW = ([1, 0, 1], [0, 2, 1], [0, 1, 1])


def setup(params):
    global RET
    recs = [json.loads(l) for l in gzip.open(KEYS, 'rt')]
    RET = sorted((r for r in recs if r['return']), key=lambda r: r['key_id'])


def prof(r):
    return ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])


def cases():
    for i, r in enumerate(RET):
        for n in range(1, 17):
            yield f'{r["key_id"][:16]}-L{n:02d}', {'i': i, 'n': n, 'kind': 'level'}
    for n in range(4, 17, 2):
        yield f'R4-two-L{n:02d}', {'n': n, 'kind': 'R4'}


def khash(K):
    return hashlib.sha256(np.ascontiguousarray(K, dtype=np.int64).tobytes()).hexdigest()


def run(case_id, payload):
    import addr  # Codex's generator, the independent second pattern builder
    n = payload['n']
    if payload['kind'] == 'level':
        r = RET[payload['i']]; key = r['key']
    else:
        key = TWO
    K = pattern(key, n)
    K2 = np.asarray(addr.level_pattern(key, n), dtype=np.int64).reshape(-1, 3)
    second = bool(K.shape == K2.shape and np.array_equal(K, K2))
    out = dict(case=case_id, n=n, kind=payload['kind'], knots=int(len(K)), second_generator_agrees=second)
    if payload['kind'] == 'level':
        out.update(key_id=r['key_id'], census_profile=prof(r), census_knots=r['knots_n'][n - 1] if n <= 12 else None)
    X = np.arange(1 << n)
    par = np.array([bin(int(t)).count('1') & 1 for t in X]) if n <= 16 else None
    if [list(key[1]), list(key[2]), list(key[3])] == TWO[1:4]:
        V = par[K]; bad = K[V.min(1) == V.max(1)]
        out['parity_violations'] = [[format(int(a), f'0{n}b') for a in k] for k in bad.tolist()][:8]
        out['parity_violation_count'] = int(len(bad))
    if [list(key[1]), list(key[2]), list(key[3])] == [list(v) for v in THREE_SW]:
        fl = ((X >> (n - 1)) & 1) ^ (X & 1); V = fl[K]
        out['first_last_violation_count'] = int(np.sum(V.min(1) == V.max(1)))
    if payload['kind'] == 'R4':
        V = par[K]; keep = V.min(1) != V.max(1)
        out['removed'] = [[format(int(a), f'0{n}b') for a in k] for k in K[~keep].tolist()]
        K = K[keep]
        out['knots_after_removal'] = int(len(K))
    with tempfile.TemporaryDirectory() as d:
        c = certify(K, 1 << n, d, TIMEOUT)
    out.update(verdict=c['verdict'], certificate=c['certificate'], seconds=c['seconds'], pattern_sha256=khash(K))
    return out
