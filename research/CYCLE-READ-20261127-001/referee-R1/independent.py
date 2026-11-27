"""Compare both birth readings on a separately seeded series of starts."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'LOOK-ALIKE-20261126-001'))
from alike import grow
from core import build_core
from reader import predict_core
from sample import sample


class Cutoff(Exception):
    pass


def expire(*_):
    raise Cutoff()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def evaluate(index, rounds, bound):
    stars = sample(index)
    c = build_core(stars)
    twins = min((p.twin_rank for p in c.pieces if p.twin_rank is not None), default=None)
    row = dict(index=index, knots=len(stars), start_hash=digest(stars),
               cyclic=any(p.cycle for p in c.pieces), twin=twins,
               pieces=[dict(stop=p.stop, rank=max(p.ranks), births=len(p.nodes),
                            chains=sum(p.chains.values()), twin=p.twin_rank) for p in c.pieces])
    for law in ('nae', 'parity'):
        cl = c if law == 'nae' else build_core(stars, law)
        pre, status = predict_core(cl, rounds, law)
        if pre is None:
            row[law] = dict(status=status)
            continue
        g = grow(stars, rounds, bound, law)
        actual = g['rows']
        first = {}
        for view in ('n', 'sig0', 'sig1'):
            first[view] = next((t for t, (p, a) in enumerate(zip(pre, actual), 1)
                                if p[view] != a[view]), None)
        row[law] = dict(status=status, rounds=len(actual), end=g['end'], first=first,
                        growth_hash=digest(actual), prediction_hash=digest(pre[:len(actual)]))
        earliest = min((v for v in first.values() if v is not None), default=None)
        if earliest is not None:
            a, p = actual[earliest-1], pre[earliest-1]
            def counts(entry):
                return collections.Counter({json.dumps(k): v for k, v in entry['sig0']})
            row[law]['difference'] = dict(grown_n=a['n'], predicted_n=p['n'],
                                            extra=dict(counts(a)-counts(p)),
                                            missing=dict(counts(p)-counts(a)))
    return row


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('first', type=int)
    ap.add_argument('last', type=int)
    ap.add_argument('--rounds', type=int, default=9)
    ap.add_argument('--bound', type=int, default=480)
    ap.add_argument('--seconds', type=float, default=3)
    args = ap.parse_args()
    signal.signal(signal.SIGALRM, expire)
    resource.setrlimit(resource.RLIMIT_AS, (1500 << 20, 1500 << 20))
    for index in range(args.first, args.last + 1):
        t = time.perf_counter()
        signal.setitimer(signal.ITIMER_REAL, args.seconds)
        try:
            row = evaluate(index, args.rounds, args.bound)
        except (Cutoff, MemoryError, RecursionError) as exc:
            row = dict(index=index, cut=type(exc).__name__)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        row['seconds'] = round(time.perf_counter()-t, 5)
        print(json.dumps(row), flush=True)
