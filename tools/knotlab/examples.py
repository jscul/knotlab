"""Reference cases for the knot definition, each with its expected verdict."""

from __future__ import annotations

from dataclasses import dataclass

from .executor import GuardedSystem
from .knots import witness_chain
from .relations import Relation


@dataclass(frozen=True)
class Example:
    name: str
    description: str
    relation: Relation
    loops: tuple[str, ...]
    contact: str
    expected_knot: bool
    expected_under_absence: bool


def examples() -> list[Example]:
    ab = ("A", "B")
    abc = ("A", "B", "c")
    chain, chain_witnesses = witness_chain(("A", "B", "C"), "d")
    return [
        Example(
            "knot",
            "one clause: c must hold when A and B are both present",
            Relation.from_cnf(["-A -B c"], abc),
            ab, "c", True, True,
        ),
        Example(
            "knot via witnesses",
            "the same relation written through witnesses w and x",
            Relation.from_cnf(["w -A -B", "-w c x", "-w c -x"], abc, ("w", "x")),
            ab, "c", True, True,
        ),
        Example(
            "common hub",
            "A-c and B-c attached separately: (¬A ∨ c) ∧ (¬B ∨ c)",
            Relation.from_cnf(["-A c", "-B c"], abc),
            ab, "c", False, False,
        ),
        Example(
            "parity",
            "A ⊕ B ⊕ c = 0: hides one full bit from every pair, the most possible",
            Relation.from_predicate(abc, lambda v: not (v["A"] ^ v["B"] ^ v["c"])),
            ab, "c", True, False,
        ),
        Example(
            "three positive literals",
            "A ∨ B ∨ c: one clause, the atom with every variable negated",
            Relation.from_cnf(["A B c"], abc),
            ab, "c", True, False,
        ),
        Example(
            "parity of a fixed value",
            "c = A ⊕ B with A fixed true: the input is not open, so A is constrained alone",
            Relation.from_cnf(["A", "-B -c", "B c"], abc),
            ab, "c", False, False,
        ),
        Example(
            "loops tied directly",
            "A ≠ B with c free: the loops are tied without the contact",
            Relation.from_cnf(["A B", "-A -B"], abc),
            ab, "c", False, False,
        ),
        Example(
            "earlier Lean kernel's accepted case",
            "(A ↔ B) ∧ (A → c): accepted by CONTACT-FORMAL-KERNEL-001A's CompleteWitness",
            Relation.from_cnf(["-A B", "A -B", "-A c"], abc),
            ab, "c", False, False,
        ),
        Example(
            "three-loop knot",
            "A, B, C bound to d by two 3-literal clauses and witness w1",
            Relation.from_cnf(chain, ("A", "B", "C", "d"), chain_witnesses),
            ("A", "B", "C"), "d", True, True,
        ),
    ]


def guarded_examples() -> dict[str, GuardedSystem]:
    return {
        "cross-wired 2-clause guards": GuardedSystem(
            ("A", "B"), "c", {"A": ("-B c",), "B": ("-A c",)}
        ),
        "knot clause as both guards": GuardedSystem(
            ("A", "B"), "c", {"A": ("-A -B c",), "B": ("-A -B c",)}
        ),
    }
