"""Shared-runner job for R5 (added before any registered result was read): certified rigidity of the seven alternating patterns at
their living levels 4..16, and of #2's pattern without the two special knots at even levels 4..16."""
import gzip, json, os, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
from certify import certify_rigid, pattern
KEYS = os.path.join(ROOT, 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz')
ALT = []
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
def prof(r): return ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])
def setup(params):
    global ALT
    recs = [json.loads(l) for l in gzip.open(KEYS, 'rt')]
    ALT = sorted((r for r in recs if r['return'] and prof(r)[4:] in ('10101010', '01010101')), key=lambda r: r['key_id'])
def cases():
    for i, r in enumerate(ALT):
        live = 0 if prof(r)[9] == '1' else 1
        for n in range(4, 17):
            if n % 2 == live: yield f'{r["key_id"][:16]}-L{n:02d}', {'i': i, 'n': n, 'kind': 'alt'}
    for n in range(4, 17, 2):
        yield f'R5-two-reduced-L{n:02d}', {'n': n, 'kind': 'reduced'}
def run(case_id, payload):
    n = payload['n']
    if payload['kind'] == 'alt':
        r = ALT[payload['i']]; K = pattern(r['key'], n); meta = dict(key_id=r['key_id'], census_profile=prof(r))
    else:
        K = pattern(TWO, n); X = np.arange(1 << n)
        par = np.array([bin(int(t)).count('1') & 1 for t in X]); V = par[K]; K = K[V.min(1) != V.max(1)]; meta = {}
    with tempfile.TemporaryDirectory() as d:
        c = certify_rigid(K, 1 << n, d, 2400)
    return dict(case=case_id, n=n, kind=payload['kind'], knots=int(len(K)), **meta, **c)
