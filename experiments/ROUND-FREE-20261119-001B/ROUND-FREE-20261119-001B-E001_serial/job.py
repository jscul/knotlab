"""Shared-runner job for ROUND-FREE-20261119-001B-E001.

Part A: two serial laws that read only the current presentation (serial.py), uniform over all moves and joins first, 20 random
orders each (seeds 0-19), on the starts below, to 400 junctions or closure.  Recorded per order: whether it closed, junctions,
the count of junctions by rank (rank = 1 + the largest parent rank, read from the presentation), the (parents, fresh) histogram.
The complete-round growth of each start is recorded for comparison (to 400 junctions)."""
import importlib.util
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import serial as SR  # noqa: E402
J = SR.J

def starts():
    R = J.ring_edges
    out = {
        'pair33': ([3, 3], [(0, 1)]), 'pair44': ([4, 4], [(0, 1)]), 'chain333': ([3, 3, 3], [(0, 1), (1, 2)]),
        'lone4': ([4], []), 'ring44445': ([4, 4, 4, 4, 5], R(5)), 'ring55555': ([5] * 5, R(5)),
    }
    e = R(5) + [(0, 5), (5, 6)]
    out['ring-pair'] = (J.bare_sizes(7, e, {'5': 2, '6': 1}), e)
    e = R(5) + R(5, 5) + [(0, 5)]
    out['two-rings'] = (J.bare_sizes(10, e), e)
    return out


def cases():
    for name in starts():
        yield f'{name}-round', {'start': name, 'law': 'round'}
        for law in ('uniform', 'joins-first'):
            for seed in range(20):
                yield f'{name}-{law}-{seed:02d}', {'start': name, 'law': law, 'seed': seed}


def run(case_id, payload):
    sz, e = starts()[payload['start']]
    if payload['law'] == 'round':
        g = J.grow(sz, e, rounds=40, maxj=400)
        return {'outcome': g['outcome'], 'junctions': g['junctions'], 'by_rank': g['counts']}
    P, rank, out = SR.grow_serial(sz, e, 10 ** 6, payload['seed'], payload['law'], maxj=400)
    hist = Counter((P.parents[j], P.fresh[j]) for j in range(len(P.bits_of)))
    return {'outcome': out, 'junctions': len(P.bits_of), 'by_rank': SR.by_rank(rank),
            'parents_fresh': sorted([list(k), v] for k, v in hist.items())}
