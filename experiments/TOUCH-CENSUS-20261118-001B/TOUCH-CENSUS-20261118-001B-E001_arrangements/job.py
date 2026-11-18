"""Shared-runner job for TOUCH-CENSUS-20261118-001B-E001: every distinct arrangement of up to five touching knots under the fewest
counts.  Shards of the sorted arrangement list."""
import pickle
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arrlib as A  # noqa: E402

SHARD = 100
_ARR = None


def setup(params):
    global _ARR
    _ARR = load()


def load():
    cache = HERE / 'arrangements.pkl'
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    arr = A.arrangements(5, labelled=True)
    keys = sorted(arr)
    data = [(k, arr[k]) for k in keys]
    cache.write_bytes(pickle.dumps(data))
    return data


def cases():
    data = _ARR if _ARR is not None else load()
    for s in range(0, len(data), SHARD):
        yield f'shard-{s // SHARD:04d}', {'lo': s, 'hi': min(len(data), s + SHARD)}


def one(key):
    import time
    P, o, births = A.grow_tracked(A.stars_of(key))
    d = A.measured_dimension(P, o)
    rerun = False
    if d is None and o in ('alive', 'big'):
        # amendment (2026-11-18 21:06 UTC): the rerun stops at 12,000 junctions, 40 rounds or 600 seconds
        P2, o2, b2 = A.grow_tracked(A.stars_of(key), rounds=40, maxj=12000, deadline=time.time() + 600)
        d2 = A.measured_dimension(P2, o2 if o2 != 'timed' else 'big')
        P, o, births, d = P2, o2, b2, d2
        rerun = True
    classes = [c for b in births for c in b]
    birth_rounds = [r + 1 for r, b in enumerate(births) if b]
    c = P.counts_by_round()[1:]
    odd, even = c[0::2][-5:], c[1::2][-5:]
    return {'key': [list(key[0]), list(key[1])], 'outcome': o, 'rounds': P.rounds,
            'stall_round': P.rounds + 1 if o == 'stall' else None, 'dim': d, 'rerun': rerun,
            'rule': max(classes) if classes else 0, 'any_birth': bool(classes), 'birth_rounds': birth_rounds[:8],
            'births': [b for b in births if b][:6], 'last': P.counts_by_round()[-5:], 'forced': len(P.forced_bits()),
            'junctions': len(P.bits_of), 'odd_tail': odd, 'even_tail': even}


def run(case_id, p):
    data = _ARR if _ARR is not None else load()
    out = []
    for key, labelled in data[p['lo']:p['hi']]:
        r = one(key)
        r['labelled'] = labelled
        out.append(r)
    return {'arrangements': out}
