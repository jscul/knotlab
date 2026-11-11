"""Does a knot space read its own relation? (research/OWN-RELATION-20261111-001/preregistration.md, ticket A).

A decided total map of four held points (all 16 patterns occur among the floor states, the output has one value at each) is self-dual
(theorem D of IN-OUT-20261110-001). The self-dual maps that use all four held points fall into exactly four classes under permuting and
negating inputs and negating the output (HOLD-COUNT-20261111-001, by exhaustion of the 256 self-dual maps):
  A  the weighted majority [2a + b + c + d >= 3];
  B  maj(a, b, a + c + d);
  C  the switch: parity of a, b, c when d = a, their majority otherwise;
  D  a + NAE(b, c, d), the knot's own relation read against a fourth point.
Only C and D restrict, at one input held fixed, to a bit a count mod 3 needs. Spaces: UNATE-20261111-001's random knot spaces steered
to a genus as in PARITY-NEEDS-20261111-001 (needs_lib.steered), every class, all floor states by brute force (unate_lib)."""
import itertools
import signal
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed"))
import needs_lib as N  # noqa: E402

U, SL = N.U, N.SL
SPACE_CAP = 1200
P16 = np.arange(16)


def bit(t, p):
    return (t >> p) & 1


def table(f):
    """truth table of f(a, b, c, d); bit p is the value at pattern p = 8a + 4b + 2c + d"""
    return sum(int(f(*[(p >> (3 - i)) & 1 for i in range(4)])) << p for p in range(16))


def transform(t, perm, neg, oneg):
    out = 0
    for p in range(16):
        x = [(p >> (3 - i)) & 1 for i in range(4)]
        y = [x[perm[i]] ^ ((neg >> i) & 1) for i in range(4)]
        out |= (bit(t, sum(y[i] << (3 - i) for i in range(4))) ^ oneg) << p
    return out


def _npn(t):
    return min(transform(t, perm, neg, o) for perm in itertools.permutations(range(4)) for neg in range(16) for o in (0, 1))


def essential(t):
    return sum(1 for i in range(4) if any(bit(t, p) != bit(t, p ^ (1 << (3 - i))) for p in range(16)))


REPS = {"A": table(lambda a, b, c, d: 2 * a + b + c + d >= 3),
        "B": table(lambda a, b, c, d: a + b + (a ^ c ^ d) >= 2),
        "C": table(lambda a, b, c, d: (a ^ b ^ c) if d == a else int(a + b + c >= 2)),
        "D": table(lambda a, b, c, d: a ^ int(len({b, c, d}) > 1))}
CANON = {_npn(t): k for k, t in REPS.items()}
KIND = {}


def kind(t):
    """'A'..'D' for a self-dual map using all four inputs, else the number of inputs it uses"""
    if t not in KIND:
        e = essential(t)
        KIND[t] = CANON[_npn(t)] if e == 4 else "%d inputs" % e
    return KIND[t]


def four_sets(rows, n, tally, first, where):
    """every free four-point set of this class's floor states: tally the kind of every decided output"""
    for Q in itertools.combinations(range(n), 4):
        key = rows[:, Q[0]].astype(np.int64) * 8 + rows[:, Q[1]] * 4 + rows[:, Q[2]] * 2 + rows[:, Q[3]]
        order = np.argsort(key, kind="stable")
        ks = key[order]
        if len(np.unique(ks)) < 16:
            continue
        tally["free four-point sets"] += 1
        starts = np.searchsorted(ks, P16)
        R = rows[order]
        lo, hi = np.minimum.reduceat(R, starts, axis=0), np.maximum.reduceat(R, starts, axis=0)
        dec = np.all(lo == hi, axis=0)
        tab = (lo.astype(np.int64) << P16[:, None]).sum(axis=0)
        for o in np.nonzero(dec)[0]:
            if o in Q:
                continue
            k = kind(int(tab[o]))
            tally[k] += 1
            if k in "ABCD" and k not in first:
                first[k] = dict(where, held=list(Q), out=int(o), table=int(tab[o]))


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def read_space(K, cap=SPACE_CAP):
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    try:
        tally, first = Counter(), {}
        for ci, s in enumerate(U.all_classes(K)):
            rows = U.floor_states(K, s)
            if len(rows):
                four_sets(rows, K.n, tally, first, {"class index": ci, "floor states": int(len(rows))})
        signal.alarm(0)
        return tally, first
    except Timeout:
        return None


def positive_control(seed=0):
    """synthetic floor states realising each class at point 4 over held points 0..3, with three free extra points: the reader must
    report that class, first at point 4 over points 0..3, and no other of the four classes (D also reads point 0 from points 1..4,
    since a + NAE(b, c, d) is symmetric in a and the output)"""
    rng = np.random.default_rng(seed)
    out = {}
    for k, t in REPS.items():
        rows = []
        for p in range(16):
            x = [(p >> (3 - i)) & 1 for i in range(4)]
            for e in range(8):
                rows.append(x + [bit(t, p)] + [(e >> j) & 1 for j in range(3)])
        rows = np.array(rows, dtype=np.uint8)[rng.permutation(128)]
        tally, first = Counter(), {}
        four_sets(rows, 8, tally, first, {})
        others = sum(tally[j] for j in "ABCD" if j != k)
        out[k] = {"reported": dict(tally), "ok": first.get(k, {}).get("out") == 4 and first[k]["held"] == [0, 1, 2, 3] and others == 0}
    return out


def export(K, label):
    return {"label": label, "n": K.n, "lines": [list(map(int, p)) for p in K.pt],
            "classes": [list(map(int, s)) for s in U.all_classes(K)]}
