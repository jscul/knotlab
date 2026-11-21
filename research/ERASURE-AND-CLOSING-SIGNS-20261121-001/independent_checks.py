"""Independent checks on the two frozen experiments. Run with the repository .venv.

The growth check exhausts the indexed structural inputs of three small panels.
The erasure check uses matrices on a single two-word orbit and both ordinary
records of its pointer. It never loads the investigators' new simulation code.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse
import gzip
import json
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]


def holdings_with_offsets(parts):
    combined = []
    first = 0
    for part in parts:
        combined.extend(tuple(i + first for i in row) for row in part)
        first += max(max(row) for row in part) + 1
    return tuple(combined)


def closed_components(rows):
    by_name = defaultdict(list)
    sharing = nx.Graph()
    sharing.add_nodes_from(range(len(rows)))
    for holder, row in enumerate(rows):
        for mark in row:
            by_name[mark].append(holder)
    loose_holders = set()
    for holds in by_name.values():
        assert len(holds) in (1, 2)
        if len(holds) == 2:
            sharing.add_edge(*holds)
        else:
            loose_holders.add(holds[0])
    return {
        frozenset(part): not nx.check_planarity(sharing.subgraph(part))[0]
        for part in nx.connected_components(sharing)
        if part.isdisjoint(loose_holders)
    }


def four_cuts(founder, law, advance, allow_stall=False):
    rows = founder
    closed = closed_components(rows)
    assert not closed
    events = []
    for step in range(1, 5):
        status, following, births = advance(rows, law)
        if status != "births":
            assert status == "closed" or (allow_stall and status == "stall")
            break
        assert len(following) <= 512
        assert max(max(row) for row in following) < 4096
        current = closed_components(following)
        for component, positive in current.items():
            if component in closed:
                continue
            recent = [h for h in component if h >= len(rows)]
            assert len(recent) == 1 and births[recent[0] - len(rows)][1] == 0
            distinct = len({i for h in component for i in following[h]})
            events.append((step, positive, len(component), distinct))
        rows, closed = following, current
    whole = sum(len(c) for c in closed) == len(rows)
    return tuple(sorted(events)), whole


def four_founders(extra_mask):
    rows = [[] for _ in range(4)]
    next_mark = 0
    for k, (a, b) in enumerate(combinations(range(4), 2)):
        count = 1 + ((extra_mask >> k) & 1)
        for _ in range(count):
            rows[a].append(next_mark)
            rows[b].append(next_mark)
            next_mark += 1
    for holder, row in enumerate(rows):
        row.append(next_mark + holder)
    return tuple(map(tuple, rows))


def check_populations():
    prior = "STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B"
    sys.path.insert(0, str(ROOT / "experiments" / prior / (prior + "-E001_pair_growth")))
    from explosive_stages import advance, indexed_rings, ring_source

    rings = [ring_source(r).rows for r in indexed_rings()]
    assert len(rings) == 40
    outcomes = {}
    for law in ("parity", "nae"):
        ring_count = Counter()
        mixtures = Counter()
        repetitions = Counter()
        for ring in rings:
            events, whole = four_cuts(ring, law, advance)
            ring_count[len(events), whole] += 1
            for a, b in product((3, 4), repeat=2):
                source = holdings_with_offsets((ring, (tuple(range(a)),), (tuple(range(b)),)))
                events, whole = four_cuts(source, law, advance)
                mixtures[len(events), sum(v[1] for v in events), whole] += 1
                if law == "parity":
                    assert [(age, positive, n) for age, positive, n, _ in events] == sorted(
                        (arity, arity == 4, 2**arity) for arity in (a, b))
        for mask in range(64):
            events, whole = four_cuts(four_founders(mask), law, advance)
            repetitions[len(events), sum(v[1] for v in events), whole] += 7**(6-mask.bit_count())
            if law == "parity":
                assert events == ((1, True, 5, 10+mask.bit_count()),)
        assert ring_count == {(0, False): 40}
        if law == "parity":
            assert mixtures == {(2, 0, False): 40, (2, 1, False): 80, (2, 2, False): 40}
            assert repetitions == {(1, 1, True): 8**6}
        else:
            assert mixtures == {(0, 0, False): 160}
            assert repetitions == {(0, 0, False): 8**6}
        outcomes[law] = (dict(ring_count), dict(mixtures), dict(repetitions))
    print("Four-cut exact indexed outcomes (rings, mixtures, supplementary integer weights):", outcomes)


def check_five_knot_receipt():
    """A three-qubit certificate independent of the signed-word compiler."""
    import numpy as np
    from math import prod

    # Each key names the two physical holders of the same distinction.
    labels = {
        (0, 1): "XII", (0, 2): "IXI", (0, 3): "IIX", (0, 4): "XXX",
        (1, 2): "IIZ", (1, 3): "IZI", (1, 4): "XZZ",
        (2, 3): "ZII", (2, 4): "ZXZ", (3, 4): "ZZX",
    }
    matrices = {"I": np.eye(2, dtype=int), "X": np.array([[0, 1], [1, 0]]),
                "Z": np.diag([1, -1])}
    operations = {mark: np.kron(np.kron(matrices[a], matrices[b]), matrices[c])
                  for mark, (a, b, c) in labels.items()}
    identity = np.eye(8, dtype=int)
    contexts = [[op for mark, op in operations.items() if holder in mark] for holder in range(5)]
    all_effects = []
    for holder, ops in enumerate(contexts):
        total = identity
        for op in ops:
            total = total @ op
        assert np.array_equal(total, (-1 if holder == 4 else 1) * identity)
        for a, b in combinations(ops, 2):
            assert np.array_equal(a @ b, b @ a)
        effects = []
        for signs in product((1, -1), repeat=4):
            effect = identity
            for sign, op in zip(signs, ops, strict=True):
                effect = effect @ (identity + sign * op)
            if prod(signs) != (-1 if holder == 4 else 1):
                assert not effect.any()
            effects.append(effect)  # 16 times the joint projection
        all_effects.append(effects)
    outcomes = Counter()
    for i, j in product(range(5), repeat=2):
        counts = Counter(Fraction(int(np.trace(a @ b)), 8 * 16**2)
                         for a, b in product(all_effects[i], all_effects[j]))
        expected = {0: 248, Fraction(1, 8): 8} if i == j else {0: 224, Fraction(1, 32): 32}
        assert counts == expected
        outcomes.update(counts)
    parity_counts = Counter()
    for w in product((0, 1), repeat=10):
        charges = tuple(sum(w[k] for k, mark in enumerate(labels) if h in mark) % 2
                        for h in range(5))
        parity_counts[charges] += 1
    assert parity_counts[(0, 0, 0, 0, 0)] == 64
    assert parity_counts[(0, 0, 0, 0, 1)] == 0
    for omitted in range(5):
        assert sum(n for charges, n in parity_counts.items()
                   if all(charges[h] == (h == 4) for h in range(5) if h != omitted)) == 64
    print("Five-knot check: 64 ordinary even words, zero odd, and signed tables (outcome mass: cells)", outcomes)


def check_recorded_draws():
    """Recompute the registered headline on all founder words saved by the investigator."""
    from scipy.stats import beta
    from math import log, sqrt
    prior = "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C"
    sys.path.insert(0, str(ROOT / "experiments" / prior / (prior + "-E001_wider_meetings")))
    from census_stages import advance

    ticket = "ERASURE-AND-CLOSING-SIGNS-20261121-001B"
    path = ROOT / "artifacts" / ticket / (ticket + "-E001_closures") / "panels_histories.json.gz"
    with gzip.open(path, "rt") as stream:
        draws = json.load(stream)
    actual = defaultdict(Counter)
    for draw in draws:
        for law in ("parity", "nae"):
            found, whole = four_cuts(draw["source_rows"], law, advance, allow_stall=True)
            tot = actual[draw["panel"], law]
            positives = sum(v[1] for v in found)
            tot.update(draws=1, with_closure=bool(found), whole=whole, with_positive=bool(positives),
                       closures=len(found), positive=positives)
    expected = {"T": (256, 6, 6, 1, 6, 1), "E": (128, 0, 0, 0, 0, 0),
                "M": (128, 128, 0, 97, 256, 129), "S": (32, 32, 32, 32, 32, 32)}
    def clopper_pearson(k, n):
        lo = 0 if k == 0 else beta.ppf(.025, k, n-k+1)
        hi = 1 if k == n else beta.ppf(.975, k+1, n-k)
        return round(100 * float(lo), 3), round(100 * float(hi), 3)
    for panel, entries in expected.items():
        fields = ("draws", "with_closure", "whole", "with_positive", "closures", "positive")
        assert tuple(actual[panel, "parity"][key] for key in fields) == entries
        assert tuple(actual[panel, "nae"][key] for key in fields) == (entries[0],0,0,0,0,0)
        n, closed, whole, partly_positive, total, positive = entries
        if not total:
            conditional = "undefined"
        elif panel != "M":
            conditional = clopper_pearson(positive, total)
        else:
            margin = 3 * sqrt(n * log(40) / 2)
            conditional = tuple(round(100*y/total, 3) for y in (positive-margin, positive+margin))
        print(panel, entries, "95% intervals in percent (any closure, whole, any admitting, per closure)",
              clopper_pearson(closed, n), clopper_pearson(whole, n), clopper_pearson(partly_positive, n), conditional)


def check_pulses():
    from sympy import I, Matrix, eye, sqrt, diag, kronecker_product, simplify
    identity = eye(2)
    exchange = Matrix([[0, 1], [1, 0]])
    b = (identity + I * exchange) / sqrt(2)
    h = diag(1, -I) * b * diag(1, -I)
    assert h == Matrix([[1, 1], [1, -1]]) / sqrt(2)
    assert (b**2 * exchange).applyfunc(simplify) == I * identity
    singleton = [Matrix([1, 0]), Matrix([0, 1])]
    def norm(v):
        return simplify((v.conjugate().T*v)[0])
    def read(state, signbit, balanced):
        # q is the leading index; the data is one complete two-word orbit.
        mixer = h if balanced else b
        controlled = diag(identity, (-1)**signbit*exchange if balanced else exchange)
        local = kronecker_product(mixer, identity)
        out = local * controlled * local * kronecker_product(singleton[0], state)
        return tuple(norm(out[k:k+2, 0]) for k in (0, 2))
    for signbit in (0, 1):
        for state in singleton:
            assert read(state, signbit, True) == (Fraction(1, 2),)*2
            assert read(state, signbit, False) == (Fraction(1, 2),)*2
        for sign in (1, -1):
            physical = diag(1, -I*sign) * b * singleton[0]
            assert physical == Matrix([1, sign]) / sqrt(2)
            clean = read(physical, signbit, True)
            assert clean == ((1, 0) if sign == (-1)**signbit else (0, 1))
            # In the idle-phase rival the guarded phase sleeve is a global phase.
            assert read(-I*sign*b*singleton[0], signbit, False) == (Fraction(1, 2),)*2
    # Starting from a fixed complete singleton, selecting the final pointer
    # gives an escape from the unconditioned, reversible preparation theorem.
    half_on_q = kronecker_product(b, identity)
    word_and_ready = kronecker_product(singleton[0], singleton[0])
    herald = half_on_q * diag(identity, exchange) * half_on_q * word_and_ready
    assert (herald - Matrix([1, -1, I, I]) / 2).applyfunc(simplify).is_zero_matrix
    # In the rival, every involution, guarded or otherwise, fixes the uniform
    # vector. A pulse maps it to exp(±i*pi/4) times itself. This also holds
    # as a left-eigenvector statement and composes through an arbitrary circuit.
    p = Matrix([[0,1,0],[1,0,0],[0,0,1]])
    ones = Matrix([[1,1,1]])
    rival = (eye(3) + I*p) / sqrt(2)
    alternate = diag(b, 1)
    # Two pulses followed by the classical exchange leave the words fixed.
    # Only the first calibration gives a relative phase between the eligible
    # pair and the unaddressed word. The rival gives one global phase.
    assert (alternate**2 * p - diag(I, I, 1)).applyfunc(simplify).is_zero_matrix
    assert (rival**2 * p - I * eye(3)).applyfunc(simplify).is_zero_matrix
    eigenrow = (1 + I) * ones / sqrt(2)
    assert (ones * rival - eigenrow).applyfunc(simplify).is_zero_matrix
    assert (ones * alternate - eigenrow).applyfunc(simplify).is_zero_matrix is False
    assert abs(sum(singleton[0])) == 1
    assert sum(Matrix([1,-1])/sqrt(2)) == 0
    print("Verified both singleton chances, known phase ports, two real preparations and the idle-phase rival.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", choices=("eraser", "closures", "both"), default="both")
    parser.add_argument("--draws", action="store_true", help="also replay the 544 recorded founders under both laws")
    args = parser.parse_args()
    if args.study in ("both", "eraser"):
        check_pulses()
    if args.study in ("both", "closures"):
        check_populations()
        check_five_knot_receipt()
        if args.draws:
            check_recorded_draws()


if __name__ == "__main__":
    main()
