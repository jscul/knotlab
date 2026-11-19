"""Referee R1 for RING-READ-20261118-001, the name-free tie rule R3n (CENSUS-READ-20261118-001A's reader3n.py, Amendment 2):
LABELLED CROSS-CHECK that runs reader3n.py read-only on tables the referee computed itself.

  ../../../.venv/bin/python -B r3n_check.py > referee_ringread_r3n.json      (from this directory)

1. 001J's 27-distinction history: R3n under the identity, the transposition (0 24) and 100 random renamings, at D <= 4 and with every
   exact distance.
2. The ring at rounds 10, 15, 20 and 25: R3n under the study's naming and 10 random renamings each.
3. The one place a name could still enter: R3's sum-growth step (`groups`, imported unchanged by R3n) grows connected sums of known
   junctions from the least index and prunes a growth whose running support exceeds s + 2, so whether a sum is reached can depend on
   the order of the known junctions, and that order follows the order in which cliques are accepted.  Test: on the ring's true
   junctions at rounds 20 and 25, the set of sums `groups` returns for every s, under the study's order and 10 random orders.
"""
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(HERE))
import reader3n as R3N  # noqa: E402  (study code, read-only)
import referee_f as F  # noqa: E402
import crosscheck_reader as CR  # noqa: E402

R3 = R3N.R3
R = R3N.R
J27 = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/frontier.json"


def renamed(table, perm):
    return {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}


def read(table, top, perm, truth):
    inv = {v: k for k, v in perm.items()}
    got = R3N.r3n(renamed(table, perm), top)
    back = {frozenset(inv[x] for x in s) for s in got}
    return back == truth


def part_27():
    rows = json.load(open(J27))["closure"]["first_histories_by_shrinking_joins"]["2"]
    n = 1 + max(max(r) for r in rows)
    K, _ = F.bond_table(rows, n)
    truth = {frozenset(r) for r in rows}
    top = max(map(len, rows))
    exact = {(a, b): int(K[a][b]) - 1 for a, b in itertools.combinations(range(n), 2)}
    out = {}
    rng = random.Random(2026)
    for H in (4, max(exact.values())):
        pooled = {p: min(d, H + 1) for p, d in exact.items()}
        tp = H + 1 if H < top else top
        ident = {x: x for x in range(n)}
        swap = dict(ident)
        swap[0], swap[24] = 24, 0
        res = {"identity": read(pooled, tp, ident, truth), "swap 0 24": read(pooled, tp, swap, truth)}
        ok = 0
        for _ in range(100):
            perm = list(range(n))
            rng.shuffle(perm)
            ok += read(pooled, tp, dict(enumerate(perm)), truth)
        res["100 random renamings exact"] = ok
        out[f"D <= {H}"] = res
    return out


def part_ring():
    out = {}
    for T in (10, 15, 20, 25):
        P = R.grow(T)
        st = R.stars_of(P)
        truth = set(st)
        top = max(map(len, st))
        tab = CR.exact_table(st, top)
        labels = sorted({b for s in st for b in s})
        rng = random.Random(3000 + T)
        ok = read(tab, top, {x: x for x in labels}, truth)
        res = []
        for _ in range(10):
            perm = labels[:]
            rng.shuffle(perm)
            res.append(read(tab, top, dict(zip(labels, perm)), truth))
        out[f"round {T}"] = {"study's naming exact": ok, "10 random renamings exact": sum(res)}
        print(T, out[f"round {T}"], file=sys.stderr, flush=True)
    return out


def part_order():
    out = {}
    for T in (20, 25):
        P = R.grow(T)
        st = list(R.stars_of(P))
        top = max(map(len, st))
        rng = random.Random(4000 + T)
        diffs = {}
        for s in range(4, top + 1):
            base = {frozenset(R3.bits_of(x)) for x in R3.groups(st, s)}
            nd = 0
            for _ in range(10):
                order = st[:]
                rng.shuffle(order)
                other = {frozenset(R3.bits_of(x)) for x in R3.groups(order, s)}
                nd += other != base
            diffs[s] = nd
        out[f"round {T}"] = {"orders (of 10) whose set of sums differs from the study's order, by s": diffs}
        print(T, out[f"round {T}"], file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    print(json.dumps({"27-distinction history": part_27(), "the ring": part_ring(), "the order of the known junctions": part_order()}, indent=1))
