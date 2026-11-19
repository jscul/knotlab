"""Shared-runner job for BREAK-EDDIES-20261119-001B-E001: the self-feeding starts in the cluster rule's break shapes, grown long.

Population (population.json): the 122 starts of LOOP-CATALOGUE's part U (main run) that grew exponentially, 30 of them marked
provisionally minimal there.  Each is grown in its own child process (6 GB of address space, 1,500 s) to 60 rounds or 300,000
junctions, printing after every round its counts, the largest number of parents of one new junction (the largest group), and the
most fresh distinctions one new junction took.  Then Berlekamp-Massey (reclib.minimal_recurrence) reads the least recurrence from
the counts, and the factor holding the largest root is turned into W(y) = sum a_k y^k (annihilator x^d - sum a_k x^(d-k)).
Part S: each start's stage after s = 0..3 rounds read by the cluster rule (stagelib), recording whether any stage is in scope and
free of known breaks."""
import json
import resource
import subprocess
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stagelib as SL  # noqa: E402
sys.path.insert(0, str(SL.ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import reclib as RC  # noqa: E402

LC = SL.ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue'
CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import eddy as E
st = json.loads(sys.argv[2])
P = E.J.S.from_junctions(E.J.stars_from(st['sizes'], [tuple(x) for x in st['edges']]))
P.linalg = False
stats = {}
def rule(P, info, rng):
    ks = E.J.F.fewest(P, info, rng)
    stats['group'] = max((i['p'] for i in info), default=0)
    stats['fresh'] = max(ks, default=0)
    return ks
groups, fresh = [], []
for _ in range(60):
    r = P.step(rule, None)
    if r is None or r['new'] == 0:
        break
    groups.append(stats['group']); fresh.append(stats['fresh'])
    print(json.dumps({'counts': P.counts_by_round(), 'group': groups, 'fresh': fresh}), flush=True)
    if len(P.bits_of) > 300000:
        break
'''


def grow(st):
    lim = lambda: resource.setrlimit(resource.RLIMIT_AS, (6 * 2 ** 30, 6 * 2 ** 30))  # noqa: E731
    for attempt in range(3):
        try:
            p = subprocess.run([sys.executable, '-B', '-c', CHILD, str(LC), json.dumps(st)], capture_output=True, text=True,
                               timeout=1500, preexec_fn=lim)
            lines = p.stdout.strip().splitlines()
            if p.returncode < 0:
                continue                                # a signal from outside: grow it again
            stop = 'end' if p.returncode == 0 else 'memory'
        except subprocess.TimeoutExpired as ex:
            out = ex.stdout.decode() if isinstance(ex.stdout, bytes) else (ex.stdout or '')
            lines, stop = out.strip().splitlines(), 'time'
        last = json.loads(lines[-1]) if lines else {'counts': [len(st['sizes'])], 'group': [], 'fresh': []}
        return dict(last, stop=stop)
    return {'counts': [len(st['sizes'])], 'group': [], 'fresh': [], 'stop': 'killed from outside'}


def read_w(c):
    x = sp.symbols('x')
    rec = RC.minimal_recurrence(c, starts=range(1, 14), spare=2)
    if rec is None:
        return None
    L, st, p = rec
    P = sum(sp.Integer(q) * x ** k for k, q in enumerate(p))
    best = None
    for f, _ in sp.factor_list(P)[1]:
        poly = sp.Poly(f, x)
        roots = [complex(r) for r in poly.nroots(n=30)]
        real = [r.real for r in roots if abs(r.imag) < 1e-12]
        if real and (best is None or max(real) > best[0]):
            best = (max(real), poly)
    if best is None:
        return {'order': L, 'start': st}
    co = best[1].all_coeffs()                          # x^d + c1 x^(d-1) + ... + cd
    lead = co[0]
    W = [0] + [int(-cc / lead) if (cc / lead) == int(cc / lead) else float(-cc / lead) for cc in co[1:]]
    return {'order': L, 'start': st, 'rate': round(best[0], 6), 'factor': str(best[1].as_expr()), 'W': W}


def cases():
    pop = json.loads((HERE / 'population.json').read_text())
    for i, st in enumerate(pop):
        yield f'G-{i:03d}', {'start': st}


def run(case_id, payload):
    st = payload['start']
    g = grow(st)
    out = {'start': st, **g, 'recurrence': read_w(g['counts']) if len(g['counts']) >= 12 else None}
    stages = []
    for s in range(4):
        try:
            status, _ = SL.stage_rule(st['sizes'], [tuple(x) for x in st['edges']], s, 2)
        except Exception as ex:                        # noqa: BLE001
            status = f'error: {type(ex).__name__}'
        stages.append(status)
        if status in ('eddy', 'no eddy', 'ended'):
            break
    out['stages'] = stages
    return out
