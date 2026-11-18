import sys, time, json
from pathlib import Path
ROOT = Path('/home/jscul/p-vs-np-contact-first')
sys.path.append(str(ROOT / 'experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots'))
sys.path.append(str(ROOT / 'experiments/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings'))
import startlib as S
from bm import berlekamp_massey
F = S.F


def stars_from(sizes, edges):
    stars = [[] for _ in sizes]; b = 0
    for i, j in edges:
        stars[i].append(b); stars[j].append(b); b += 1
    for i in range(len(sizes)):
        if len(stars[i]) > sizes[i]:
            raise ValueError('over')
        while len(stars[i]) < sizes[i]:
            stars[i].append(b); b += 1
    return stars


def grow(stars, rounds=40, maxj=40000, tmax=120, progress=None, linalg=True):
    P = S.from_junctions(stars)
    t0 = time.time(); out = 'alive'
    rule = S.gf2(F.fewest) if linalg else F.fewest
    if not linalg:
        P.linalg = False
    for _ in range(rounds):
        r = P.step(rule, None)
        if progress:
            progress(P)
        if r is None: out = 'stall'; break
        if r['new'] == 0: out = 'closed'; break
        if len(P.bits_of) > maxj: out = 'big'; break
        if time.time() - t0 > tmax: out = 'timed'; break
    return P, out


def ring_edges(n, off=0):
    return [(off + i, off + (i + 1) % n) for i in range(n)]
