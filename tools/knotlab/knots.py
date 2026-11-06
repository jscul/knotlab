"""The knot definition and the facts around it.

Each loop contributes one open distinction, a variable it leaves free, and the
contact is one more variable. Erasing a loop removes it, so its variable is no
longer constrained by anything (the forgetting reading, canonical since
2026-10-19). A knot of loops L1..Ln with contact c is a relation over exactly
those variables such that:

- K1 binding: the relation is constrained as a whole;
- K2 loss on erasure: forgetting any one variable, a loop or the contact,
  leaves the others unconstrained;
- K3 coexistence: some joint state is allowed.

In short: constrained as a whole, unconstrained in every part. The earlier
absence reading (erasure="absence") treats a loop's variable as its presence
and erasing as setting it to absent; it keeps only the atom.

See INTUITIONS.md for the intuition this formalizes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .relations import Clause, Relation, format_row

READINGS = ("forgetting", "absence")


@dataclass(frozen=True)
class KnotReport:
    loops: tuple[str, ...]
    contact: str
    erasure: str
    binding: bool
    loss_on_erasure: bool
    coexistence: bool
    invisible_in_parts: bool
    pairwise_definable: bool
    minimum_width: int
    notes: tuple[str, ...]

    @property
    def is_knot(self) -> bool:
        return self.binding and self.loss_on_erasure and self.coexistence

    def as_dict(self) -> dict[str, object]:
        return {**asdict(self), "is_knot": self.is_knot}


def check_knot(
    relation: Relation, loops: Iterable[str], contact: str, erasure: str = "forgetting"
) -> KnotReport:
    """Test K1-K3 under a reading of erasure and report the facts behind the verdict."""
    if erasure not in READINGS:
        raise ValueError(f"erasure must be one of {READINGS}")
    loops = tuple(loops)
    if len(loops) < 2:
        raise ValueError("a knot binds at least two loops")
    if contact in loops:
        raise ValueError("the contact must differ from every loop")
    if set(relation.variables) != set(loops) | {contact}:
        raise ValueError(
            "the relation must range over exactly the loops and the contact; "
            "declare every other variable as a witness"
        )
    notes: list[str] = []
    if erasure == "forgetting":
        binding = not relation.is_full()
        coexistence = not relation.is_empty()
        if not binding:
            notes.append("the relation allows every joint state, so nothing binds")
        if not coexistence:
            notes.append("the relation allows no state, so the loops cannot coexist")
        loss_on_erasure = True
        for dropped in (*loops, contact):
            rest = relation.project([name for name in relation.variables if name != dropped])
            if rest.is_full():
                continue
            loss_on_erasure = False
            row = format_row(rest.variables, rest.excluded()[0])
            notes.append(
                f"with the contact {dropped} forgotten, {row} is still excluded, "
                "so the loops are tied without it"
                if dropped == contact else
                f"with {dropped} forgotten, {row} is still excluded, "
                "so a binding survives without that loop"
            )
    else:
        present = relation.restrict({loop: True for loop in loops})
        binding = not present.is_full()
        coexistence = not present.is_empty()
        if not binding:
            notes.append("with every loop present, every contact value is allowed, so nothing binds")
        if not coexistence:
            notes.append("the loops can never all be present together")
        loss_on_erasure = True
        for loop in loops:
            rest = relation.restrict({loop: False})
            if not rest.is_full():
                loss_on_erasure = False
                notes.append(
                    f"with {loop} absent, {format_row(rest.variables, rest.excluded()[0])} "
                    "is still excluded, so a binding survives without that loop"
                )
    invisible_in_parts = all(
        relation.project([name for name in relation.variables if name != dropped]).is_full()
        for dropped in relation.variables
    )
    return KnotReport(
        loops=loops,
        contact=contact,
        erasure=erasure,
        binding=binding,
        loss_on_erasure=loss_on_erasure,
        coexistence=coexistence,
        invisible_in_parts=invisible_in_parts,
        pairwise_definable=relation.is_majority_closed(),
        minimum_width=relation.minimum_width(),
        notes=tuple(notes),
    )


def knot_relation(loops: Iterable[str], contact: str) -> Relation:
    """The atom: the single clause ¬L1 ∨ … ∨ ¬Ln ∨ c, the knot that hides the least.

    It excludes one joint state, every loop true with the contact false. It is
    also the only knot under the absence reading, up to the contact's polarity.
    """
    loops = tuple(loops)
    return Relation.from_predicate(
        loops + (contact,),
        lambda value: not all(value[loop] for loop in loops) or value[contact],
    )


def witness_chain(
    loops: Iterable[str], contact: str
) -> tuple[tuple[Clause, ...], tuple[str, ...]]:
    """Clauses of exactly three literals, plus witnesses, that bind every loop.

    Two loops need the single clause ¬L1 ∨ ¬L2 ∨ c. For more loops, witness
    w1 is forced when L1 and L2 are both present; it is the witness that the
    pair is bound, and it takes part in the next binding.
    """
    loops = tuple(loops)
    if len(loops) < 2:
        raise ValueError("a knot binds at least two loops")
    if len(loops) == 2:
        return (((loops[0], False), (loops[1], False), (contact, True)),), ()
    witnesses = tuple(f"w{index}" for index in range(1, len(loops) - 1))
    clash = set(witnesses) & (set(loops) | {contact})
    if clash:
        raise ValueError(f"rename variables that clash with witnesses: {sorted(clash)}")
    clauses: list[Clause] = [((witnesses[0], True), (loops[0], False), (loops[1], False))]
    for index in range(1, len(witnesses)):
        clauses.append(
            ((witnesses[index], True), (witnesses[index - 1], False), (loops[index + 1], False))
        )
    clauses.append(((witnesses[-1], False), (loops[-1], False), (contact, True)))
    return tuple(clauses), witnesses
