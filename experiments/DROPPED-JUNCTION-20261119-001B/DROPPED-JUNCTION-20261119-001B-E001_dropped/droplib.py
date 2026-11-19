"""Parity over the dropped junction (DROPPED-JUNCTION-20261119-001B).

A parity presentation in which every distinction lies in at most two junctions is a graph: junctions are points and distinctions
lines, a loose distinction a line to the implied junction 'out' that holds every loose distinction (the completed system G*).
The allowed states are G*'s cycle space, so every choice of the dropped point v of G* gives a presentation with the same states:
the other points are the junctions, and v's lines are the loose distinctions.  `rechoices(stars)` lists them (one per point; the
original is the choice v = out)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import joinlib as J  # noqa: E402


def completed_lines(stars):
    own = {}
    for j, s in enumerate(stars):
        for b in s:
            own.setdefault(b, []).append(j)
    return [(js[0], js[1] if len(js) == 2 else 'out') for b, js in sorted(own.items())]


def rechoice(stars, v):
    lines = completed_lines(stars)
    points = [j for j in range(len(stars))] + ['out']
    keep = [p for p in points if p != v]
    idx = {p: i for i, p in enumerate(keep)}
    new = [[] for _ in keep]
    for b, (x, y) in enumerate(lines):
        for p in (x, y):
            if p != v:
                new[idx[p]].append(b)
    return new


def rechoices(stars):
    return {str(v): rechoice(stars, v) for v in list(range(len(stars))) + ['out']}


def grow(stars, rounds=30, maxj=60000):
    P = J.S.from_junctions([list(s) for s in stars])
    P.linalg = False
    out = 'alive'
    for _ in range(rounds):
        r = P.step(J.F.fewest, None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if len(P.bits_of) > maxj:
            out = 'cap'
            break
    return P.counts_by_round(), out
