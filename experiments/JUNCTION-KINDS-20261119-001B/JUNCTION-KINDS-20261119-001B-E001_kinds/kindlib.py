"""Kinds of junction (JUNCTION-KINDS-20261119-001B).

The growth is the cheapest parity growth of the program's start library (FIRST-KNOT's startlib under FRESH-COUNT's fewest counts),
as in BREAK-EDDIES.  After round t, every junction j carries a label: its age t - round(j), capped at A; its parents; its fresh
distinctions; and its loose distinctions now.  Its kind of depth R is the label refined R times by the multiset of its neighbours'
kinds of depth R - 1 (two junctions are neighbours when they share a distinction; a pair sharing two counts twice).  Kinds are
interned in one table shared by every start and round, so equal kinds are equal local patterns, by the same refinement.

A junction born in round t + 1 with p parents is shared among them, 1/p to each.  The kind of a junction born in round t then has a
signature: the multiset of its children's kinds of depth R (after round t + 1), with those weights.  The kinds of depth R are a
transfer when every kind seen has one signature; then N_{t+1}(k') = sum_k M[k', k] N_t(k) exactly, with M read from the
signatures."""
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue'))
import eddy as E  # noqa: E402

TABLE = {}


def intern(x):
    if x not in TABLE:
        TABLE[x] = len(TABLE)
    return TABLE[x]


def start(st):
    P = E.J.S.from_junctions(E.J.stars_from(st['sizes'], [tuple(x) for x in st['edges']]))
    P.linalg = False
    return P


def kinds(P, R, A=2, only=None):
    """Kinds of depth 0..R of every junction (or of `only` and what they need) after the presentation's last round."""
    t = P.rounds
    n = len(P.bits_of)
    mult = [Counter() for _ in range(n)]
    for b, js in P.owner.items():
        if len(js) == 2:
            mult[js[0]][js[1]] += 1
            mult[js[1]][js[0]] += 1
    need = set(range(n)) if only is None else set(only)
    layers = [need]
    for _ in range(R):
        nxt = set(layers[-1])
        for j in layers[-1]:
            nxt |= set(mult[j])
        layers.append(nxt)
    col = {}
    for j in layers[R]:
        loose = sum(1 for b in P.bits_of[j] if len(P.owner[b]) == 1)
        col[j] = intern(('L', min(t - P.round_of[j], A), P.parents[j], P.fresh[j], loose))
    out = [dict(col)]
    for r in range(1, R + 1):
        new = {}
        for j in layers[R - r]:
            new[j] = intern(('K', col[j], tuple(sorted((col[o], m) for o, m in mult[j].items()))))
        col = new
        out.append(dict(col))
    return out


def grow_kinds(st, rounds, R, A=2, maxj=200000):
    """Grow and record, for every round t >= 1, the depth-R kind of each junction born in round t and, after round t + 1, the
    signature of each: children's kinds with weight 1/p."""
    P = start(st)
    per_round = []          # [(kind of each newborn, {newborn: Counter((child kind, weight))})]
    born_prev = []
    kind_prev = {}
    for t in range(1, rounds + 1):
        r = P.step(E.J.F.fewest, None)
        if r is None or r['new'] == 0:
            break
        born = [j for j in range(len(P.bits_of)) if P.round_of[j] == P.rounds]
        K = kinds(P, R, A, only=born)[R]
        if born_prev:
            sig = {j: Counter() for j in born_prev}
            for c in born:
                par = {o for b in P.bits_of[c][:P.parents[c]] for o in P.owner[b] if o != c}
                for o in par:
                    sig[o][(K[c], Fraction(1, P.parents[c]))] += 1
            per_round.append(({j: kind_prev[j] for j in born_prev}, sig))
        born_prev, kind_prev = born, {j: K[j] for j in born}
        if len(P.bits_of) > maxj:
            break
    return P.counts_by_round(), per_round
