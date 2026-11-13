"""Check the period-four supports for sample_0.jsonl.gz, line 4710.

Only this record is read.  The finite relation calculation uses the majority
description after checking it against all raw local words.  A separate SAT
calculation builds the raw positive NAE clauses along the first-child branch;
it imports no producer, predecessor checker, or ray optimisation routine.
The command writes no files and prints a JSON receipt.

Replay: .venv/bin/python -B <this-file> --max-depth 32
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / (
    "artifacts/LIMIT-ONLY-20261112-001A/"
    "LIMIT-ONLY-20261112-001A-E001_limit_only/sample_0.jsonl.gz"
)
LINE = 4710


def bitword(values):
    return sum(value << i for i, value in enumerate(values))


def extract(word, variables):
    return bitword([(word >> variable) & 1 for variable in variables])


def source_definition():
    with gzip.open(SOURCE, "rt") as stream:
        row = next(json.loads(line) for number, line in enumerate(stream, 1)
                   if number == LINE)
    definition, = row["defs"]
    ports, own, body = definition
    assert (ports, own) == (3, 2)
    knots = [tuple(args) for kind, args in body if kind == "K"]
    children = [tuple(args) for kind, args in body if kind == "SELF"]
    assert children == [(3, 0, 4), (2, 1, 4), (4, 2, 1)]
    assert set(map(frozenset, knots)) == {
        frozenset((4, 3, 1)), frozenset((1, 3, 2)), frozenset((2, 4, 1))
    }
    assert len(knots) == len(children) == 3
    assert all(len(set(args)) == 3 for args in knots + children)
    return definition, knots, children


def raw_local_words(knots):
    return [word for word in range(32)
            if all(extract(word, args) not in (0, 7) for args in knots)]


def greatest_ports(knots, children):
    """Direct descending finite relation iteration, starting from all triples."""
    local = raw_local_words(knots)
    allowed = set(range(8))
    rounds = []
    while True:
        kept = [word for word in local
                if all(extract(word, child) in allowed for child in children)]
        new_allowed = {word & 7 for word in kept}
        rounds.append(sorted(new_allowed))
        if new_allowed == allowed:
            return new_allowed, kept, rounds
        allowed = new_allowed


class MarkedRelation:
    """Scalar relation calculation on (x[i-1], x[i-2], y[i-1])."""

    def __init__(self):
        # This path uses the mathematical majority equation, not NAE clauses.
        self.words = [(a, b, c, x, y)
                      for a, b, c, x, y in product(range(2), repeat=5)
                      if b != (x + y + c >= 2)]

    def image(self, mask, marker=None):
        out = set()
        for a, b, c, x, y in self.words:
            if (mask >> bitword((a, b, c))) & 1:
                if marker is None or y == marker:
                    out.add(bitword((x, a, y)))
        return sum(1 << word for word in out)

    def free_steps(self, mask, count):
        for _ in range(count):
            mask = self.image(mask)
        return mask

    @staticmethod
    def seed(previous, current):
        return sum(1 << bitword((current, previous, y)) for y in range(2))

    @staticmethod
    def projected(mask, positions):
        return sorted({extract(word, positions)
                       for word in range(8) if (mask >> word) & 1})

    def certificate(self, raw_words):
        assert {bitword(word) for word in self.words} == set(raw_words)
        base = {}
        for previous, current, marker in product(range(2), repeat=3):
            mask = self.image(self.image(self.seed(previous, current)), marker)
            base[previous, current, marker] = mask
        assert base == {
            (0, 0, 0): 10, (0, 0, 1): 240,
            (0, 1, 0): 13, (0, 1, 1): 64,
            (1, 0, 0): 2, (1, 0, 1): 176,
            (1, 1, 0): 15, (1, 1, 1): 80,
        }
        states = sorted(set(base.values()))
        block = {mask: [self.image(self.free_steps(mask, 3), marker)
                        for marker in range(2)] for mask in states}
        assert block[2] == [2, 176] and block[64] == [13, 64]
        ordinary = set(states) - {2, 64}
        assert all(block[mask] == [15, 240] for mask in ordinary)
        tails = {
            mask: dict(
                one_x=self.projected(self.free_steps(mask, 1), (0,)),
                two_x=self.projected(self.free_steps(mask, 2), (0,)),
                three_xy=self.projected(self.free_steps(mask, 3), (0, 2)),
            ) for mask in states
        }
        assert tails[2] == dict(one_x=[1], two_x=[0], three_xy=[0, 1, 2])
        assert tails[64] == dict(one_x=[0], two_x=[1], three_xy=[1, 2, 3])
        assert all(tails[mask] == dict(one_x=[0, 1], two_x=[0, 1],
                                       three_xy=[0, 1, 2, 3])
                   for mask in ordinary)
        # Check the j=0 seed directly in the raw local relation: selecting
        # a=previous and x0=current leaves exactly the required free y0.
        for previous, current in product(range(2), repeat=2):
            initial = sum(1 << word for word in range(8)
                          if (word & 1) == current and ((word >> 1) & 1) == previous)
            assert initial == self.seed(previous, current)
            actual = sum(1 << q for q in {
                extract(word, (3, 0, 4)) for word in raw_words
                if (word & 1) == previous and ((word >> 3) & 1) == current
            })
            assert actual == self.seed(previous, current)
        return dict(
            mask_convention="bit q of mask, q=u+2*v+4*w for outgoing (u,v,w)",
            base=[dict(previous=p, current=c, marker=z, mask=mask)
                  for (p, c, z), mask in sorted(base.items())],
            four_step_marked=block,
            terminal_tails=tails,
        )


def x_name(index):
    return {-2: "b", -1: "a"}.get(index, f"x{index}")


def support(depth):
    """Ordered raw distinctions and exactly the two predicted excluded words."""
    if depth < 1:
        raise ValueError("the construction covers positive depths")
    if depth == 1:
        return ["a", "x1", "y1"], [0, 7], dict(special="NAE")
    residue = depth % 4
    if residue == 2:
        start, count, tail = -1, (depth + 2) // 4, 1
    elif residue == 3:
        start, count, tail = 0, (depth + 1) // 4, 1
    elif residue == 0:
        start, count, tail = 0, depth // 4, 2
    else:
        start, count, tail = 0, (depth - 1) // 4, 3
    markers = [start + 2 + 4 * i for i in range(count)]
    names = [x_name(start - 1), x_name(start)]
    names += [f"y{i}" for i in markers]
    names += [f"x{depth}"]
    if tail == 3:
        names.append(f"y{depth}")
    forbidden = []
    for value in range(2):
        values = [1 - value, value] + [value] * count
        values += [value] if tail == 1 else [1 - value]
        if tail == 3:
            values.append(1 - value)
        forbidden.append(bitword(values))
    assert len(names) == len(set(names)) == (depth + 3) // 4 + 3
    return names, sorted(forbidden), dict(start=start, markers=markers, tail=tail)


def ray_cnf(depth, knots, children):
    """Raw NAE clauses; unopened infinite calls have the checked full relation."""
    labels = ["a", "b", "c"]
    ports = [0, 1, 2]
    clauses = []
    for level in range(depth + 1):
        env = ports + [len(labels), len(labels) + 1]
        labels.extend((f"x{level}", f"y{level}"))
        for args in knots:
            triple = [env[index] + 1 for index in args]
            clauses.extend((triple, [-variable for variable in triple]))
        ports = [env[index] for index in children[0]]
    return clauses, {name: index + 1 for index, name in enumerate(labels)}


def sat_projection(depth, names, knots, children):
    clauses, variables = ray_cnf(depth, knots, children)
    answer = set()
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        for word in range(1 << len(names)):
            assumptions = [variables[name] if (word >> bit) & 1 else -variables[name]
                           for bit, name in enumerate(names)]
            if solver.solve(assumptions=assumptions):
                answer.add(word)
    return answer


def erasures(allowed, size):
    projections = []
    for deleted in range(size):
        positions = [index for index in range(size) if index != deleted]
        projections.append(len({extract(word, positions) for word in allowed}))
    return projections


def bond(allowed, size):
    return (size >= 3 and 0 < len(allowed) < (1 << size)
            and all(count == (1 << (size - 1)) for count in erasures(allowed, size)))


def knotlab_check(names, forbidden, expect):
    """Invoke the real canonical interface for the computed finite relation."""
    variables = [f"Z{i}" for i in range(len(names))]
    clauses = [" ".join(("~" if (word >> i) & 1 else "") + variable
                        for i, variable in enumerate(variables))
               for word in forbidden]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tools")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
         "--loops", *variables[:-1], "--contact", variables[-1], "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    receipt = json.loads(result.stdout)
    # This is the existing canonical CLI's schema, not a local syntax test.
    assert receipt["is_knot"] == expect, receipt
    return receipt


def run(max_depth=32, canonical=True):
    definition, knots, children = source_definition()
    allowed, local, rounds = greatest_ports(knots, children)
    assert allowed == set(range(8))
    assert len(local) == 16
    finite_certificate = MarkedRelation().certificate(local)
    checked = []
    for depth in range(1, max_depth + 1):
        names, forbidden, description = support(depth)
        actual = sat_projection(depth, names, knots, children)
        missing = sorted(set(range(1 << len(names))) - actual)
        assert missing == forbidden, (depth, names, missing, forbidden)
        assert bond(actual, len(names))
        assert forbidden[0] ^ forbidden[1] == (1 << len(names)) - 1
        checked.append(dict(depth=depth, variables=names, size=len(names),
                            allowed=len(actual), forbidden=missing,
                            single_erasure_sizes=erasures(actual, len(names)),
                            **description))
    # Change mathematical content: erase exactly NAE(b,x,y) from each copy.
    # The proposed period-four support then becomes entirely free.
    control_depth = 4
    control_names, control_forbidden, _ = support(control_depth)
    weakened_knots = [args for args in knots if set(args) != {1, 3, 4}]
    weakened_allowed, _, _ = greatest_ports(weakened_knots, children)
    assert weakened_allowed == set(range(8))
    weakened = sat_projection(control_depth, control_names, weakened_knots, children)
    assert len(weakened) == 1 << len(control_names)
    assert not bond(weakened, len(control_names))
    # Adding an unselected top distinction preserves a constrained proper part.
    spectator_names = control_names + ["c"]
    spectator = sat_projection(control_depth, spectator_names, knots, children)
    assert not bond(spectator, len(spectator_names))
    assert erasures(spectator, len(spectator_names))[-1] < 1 << len(control_names)
    canonical_receipts = {}
    if canonical:
        canonical_receipts["period_four"] = knotlab_check(
            control_names, control_forbidden, True)
        canonical_receipts["spectator_rejection"] = knotlab_check(
            spectator_names,
            sorted(set(range(1 << len(spectator_names))) - spectator), False)
    return dict(
        source=str(SOURCE.relative_to(ROOT)), source_line=LINE,
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        definition=definition, greatest_port_relation=sorted(allowed),
        greatest_fixed_point_rounds=rounds, local_words=len(local),
        local_majority_equivalence=True,
        finite_relation_certificate=finite_certificate,
        raw_cnf_sat_checks=checked,
        controls=dict(dropped_NAE_is_free=len(weakened),
                      spectator_allowed=len(spectator),
                      spectator_erasure_sizes=erasures(spectator, len(spectator_names))),
        canonical_checks=canonical_receipts,
        claim_scope="Uniform upper construction; no unrestricted or ray minimum claimed.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--skip-canonical", action="store_true")
    args = parser.parse_args()
    if args.max_depth < 1:
        parser.error("--max-depth must be positive")
    print(json.dumps(run(args.max_depth, canonical=not args.skip_canonical), indent=2))
