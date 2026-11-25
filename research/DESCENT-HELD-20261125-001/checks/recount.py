"""The thread's third count for DESCENT-HELD-20261125-001A, with the round of an earlier study's engine.

Grows every census start (cpcensus.py of COPYING-PARTS-20261123-001A, imported unchanged) with `lr_core.own_round` of
LOCAL-ROUND-20261123-001A (imported unchanged), 8 rounds or the first round after which the structure has more than
3,000 knots or the first round that changes nothing, and counts the starts on which some new knot has two parents at
different parent steps.  It also grows the three witness starts of the note.  It uses neither the drafter's prototype
nor the confirming run's program.  Run from anywhere:  .venv/bin/python -B research/DESCENT-HELD-20261125-001/checks/recount.py
(about 30 seconds on 6 processes).  Writes recount.json beside itself.
"""
import importlib.util
import json
import os
import resource
import sys
import time
import types
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
LR = os.path.join(ROOT, 'experiments', 'LOCAL-ROUND-20261123-001A', 'LOCAL-ROUND-20261123-001A-E001_local_round')
CP = os.path.join(ROOT, 'experiments', 'COPYING-PARTS-20261123-001A', 'COPYING-PARTS-20261123-001A-E001_copies')
sys.dont_write_bytecode = True
sys.path.insert(0, LR)
import lr_core  # noqa: E402

_stub = types.ModuleType('cpcommon')
_stub.ROOT = ROOT
sys.modules['cpcommon'] = _stub
_spec = importlib.util.spec_from_file_location('cpcensus', os.path.join(CP, 'cpcensus.py'))
cpcensus = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cpcensus)

# the laws the earlier round can express: ration, what a short knot does, RELEASE or HOLD
LAWS = {'RATION-3, waiting': ('RATION-3', 'CANCEL-WAIT', 'RELEASE'),
        'FLOOR1, waiting': ('FLOOR1', 'CANCEL-WAIT', 'RELEASE'),
        'FLOOR1, offshoots': ('FLOOR1', 'CANCEL-OFFSHOOT', 'RELEASE'),
        'FLOOR1, retiring': ('FLOOR1', 'CANCEL-RETIRE', 'RELEASE'),
        'RATION-3, waiting, HOLD': ('RATION-3', 'CANCEL-WAIT', 'HOLD'),
        'FLOOR1, offshoots, HOLD': ('FLOOR1', 'CANCEL-OFFSHOOT', 'HOLD'),
        'FLOOR1, retiring, HOLD': ('FLOOR1', 'CANCEL-RETIRE', 'HOLD')}
EXPECTED = {'RATION-3, waiting': 510, 'FLOOR1, waiting': 223, 'FLOOR1, offshoots': 0, 'FLOOR1, retiring': 0,
            'RATION-3, waiting, HOLD': 48, 'FLOOR1, offshoots, HOLD': 462, 'FLOOR1, retiring, HOLD': 369}
WITNESSES = {'W1': ([[0, 1, 2], [0, 3, 5], [1, 3, 4, 6], [2, 4, 7, 8]], 'RATION-3, waiting'),
             'W2': ([[0, 4, 5], [1, 2, 6], [1, 3, 7, 8], [0, 2, 3]], 'FLOOR1, offshoots, HOLD'),
             'W2b': ([[0, 4, 5], [1, 2, 6], [1, 3, 7], [0, 2, 3, 8, 9]], 'FLOOR1, retiring, HOLD')}


def grow(stars, law, rounds=8):
    ration, treatment, release = LAWS[law]
    S = lr_core.Str([list(s) for s in stars])
    for _ in range(rounds):
        before = (len(S.places), sum(S.barred))
        lr_core.own_round(S, ration, treatment, release=release)
        if (len(S.places), sum(S.barred)) == before or len(S.places) > 3000:
            break
    steps = [0] * len(S.places)
    for x in range(len(S.places)):
        if S.parents[x]:
            steps[x] = 1 + max(steps[p] for p in S.parents[x])
    return S, steps


def one(args):
    i, n, stars, law = args
    resource.setrlimit(resource.RLIMIT_AS, (6 << 30, 6 << 30))
    S, steps = grow(stars, law)
    worst = 0  # the greatest of (child's parent steps) - (a parent's), over births with parents that differ
    for x in range(len(S.places)):
        ps = S.parents[x]
        if len(ps) >= 2 and len({steps[p] for p in ps}) > 1:
            worst = max(worst, steps[x] - min(steps[p] for p in ps))
    return i, n, worst


def main():
    t0 = time.time()
    census = [(n, cpcensus.stars(gi, loose)) for n in range(1, 6) for gi, loose in cpcensus.starts(n)]
    out = {'census starts': len(census), 'laws': {}, 'witnesses': {}}
    with Pool(6) as pool:
        for law in LAWS:
            res = pool.map(one, [(i, n, st, law) for i, (n, st) in enumerate(census)], chunksize=8)
            counted = [r for r in res if r[2] > 0]
            by_knots, by_diff = {}, {}
            for _, n, w in counted:
                by_knots[n] = by_knots.get(n, 0) + 1
                by_diff[w] = by_diff.get(w, 0) + 1
            out['laws'][law] = {'counted': len(counted), 'expected': EXPECTED[law], 'by knots of the start': by_knots,
                                'by greatest difference, child less parent': by_diff,
                                'counted census indices': [r[0] for r in counted]}
    for name, (stars, law) in WITNESSES.items():
        S, steps = grow(stars, law, rounds=3)
        out['witnesses'][name] = [{'new knot': x, 'round': S.born[x], 'parents': list(S.parents[x]),
                                   'parent steps of the parents': [steps[p] for p in S.parents[x]]}
                                  for x in range(len(S.places))
                                  if len(S.parents[x]) >= 2 and len({steps[p] for p in S.parents[x]}) > 1]
    out['all as expected'] = all(v['counted'] == v['expected'] for v in out['laws'].values())
    out['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, 'recount.json'), 'w') as f:
        json.dump(out, f, indent=1)
    for law, v in out['laws'].items():
        print(law, v['counted'], v['by knots of the start'], v['by greatest difference, child less parent'])
    print(json.dumps(out['witnesses']))
    print('all as expected:', out['all as expected'], out['seconds'], 's')


if __name__ == '__main__':
    main()
