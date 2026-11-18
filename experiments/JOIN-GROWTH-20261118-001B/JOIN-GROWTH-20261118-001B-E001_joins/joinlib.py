"""Joined starts and their cheapest parity growth (JOIN-GROWTH-20261118-001B).

A start is given as knots and shared distinctions: `edges` lists pairs of knots, one shared distinction per entry.  In the bare
convention every knot gets max(3, shared + round-1 demand) places (the fewest that let round 1 start), plus the surplus distinctions
the start lists for it.  Growth is FIRST-KNOT's start library under the fewest counts (the policy of TOUCH-CENSUS-20261118-001 and
RING-GROWTH-20261118-001), with the joining policy computed by fastlib (same output as freelib's, checked by checks.py).  Every
start here is connected, so the structural implied-parity test of freelib holds (FIRST-KNOT's Lemma 0) and GF(2) elimination is
switched off, as in RING-GROWTH's ring.py."""
import gc
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.append(str(ROOT / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
import startlib as S  # noqa: E402
import fastlib  # noqa: E402

F = S.F
fastlib.install(F)


def stars_from(sizes, edges):
    stars = [[] for _ in sizes]
    b = 0
    for i, j in edges:
        stars[i].append(b)
        stars[j].append(b)
        b += 1
    for i in range(len(sizes)):
        if len(stars[i]) > sizes[i]:
            raise ValueError('a knot holds more shared distinctions than places')
        while len(stars[i]) < sizes[i]:
            stars[i].append(b)
            b += 1
    return stars


def shared_and_demand(n, edges):
    """Shared distinctions and round-1 demand of each knot (every knot given one open distinction, so all are live)."""
    sh = Counter()
    for i, j in edges:
        sh[i] += 1
        sh[j] += 1
    P = S.from_junctions(stars_from([sh[k] + 1 for k in range(n)], edges))
    d = Counter()
    for g in P.groups_among(list(range(n))):
        for j in g:
            d[j] += 1
    return [sh[k] for k in range(n)], [d[k] for k in range(n)]


def bare_sizes(n, edges, surplus=None):
    sh, d = shared_and_demand(n, edges)
    sp = [0] * n
    for k, v in (surplus or {}).items():
        sp[int(k)] += v
    return [max(3, sh[k] + d[k]) + sp[k] for k in range(n)]


def connected(n, edges):
    adj = {k: set() for k in range(n)}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in adj[x] - seen:
            seen.add(y)
            st.append(y)
    return len(seen) == n


def grow(sizes, edges, rounds=80, maxj=400000, tmax=1800.0):
    """Per-round junction counts under the fewest counts, until `rounds`, `maxj` junctions or `tmax` seconds."""
    if not connected(len(sizes), edges):
        raise ValueError('start not connected')
    gc.disable()
    try:
        P = S.from_junctions(stars_from(sizes, edges))
        P.linalg = False
        t0, out = time.time(), 'alive'
        for _ in range(rounds):
            r = P.step(F.fewest, None)
            if r is None:
                out = 'stall'
                break
            if r['new'] == 0:
                out = 'closed'
                break
            if len(P.bits_of) > maxj:
                out = 'cap'
                break
            if time.time() - t0 > tmax:
                out = 'time'
                break
        return {'outcome': out, 'rounds': P.rounds, 'counts': P.counts_by_round(), 'junctions': len(P.bits_of),
                'seconds': round(time.time() - t0, 2)}
    finally:
        gc.enable()


def ring_edges(n, off=0):
    return [(off + i, off + (i + 1) % n) for i in range(n)]
