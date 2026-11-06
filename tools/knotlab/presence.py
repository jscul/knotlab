"""Where a loop's presence comes from (ticket KNOT-FOUNDATION-20261019-001B, retired).

This exploration belongs to the absence reading of K1-K3, which took each
loop's presence as a given variable; it tests whether presence can instead be
computed from the loop itself. Under the canonical forgetting reading presence
is not a variable, so the question no longer arises.

Static semantics: a loop written as constraints collapses to one free bit
(see loops.py), so its presence can only be that bit.

Dynamic semantics: a loop is a ring of bits under a declared update. The loop
is *running* when its state lies on a cycle of length at least two and
*frozen* at a fixed point. For the copy ring (each bit takes its neighbor's
value) running is conserved by the ring's own update and can be read at every
instant by comparing neighboring points: for two points, 01/10 is running and
00/11 is frozen. A contact that is set when both loops run and otherwise keeps
its value then gives exactly the K1-K3 knot over the computed presences.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable

from .relations import Relation

State = tuple[bool, ...]
Update = Callable[[State], State]


def copy_ring(state: State) -> State:
    """Each bit takes the value of the bit before it: the pattern rotates."""
    return state[-1:] + state[:-1]


def inverter_ring(state: State) -> State:
    """Each bit takes the negation of the bit before it."""
    return tuple(not bit for bit in copy_ring(state))


def cycle_length(update: Update, state: State) -> int:
    """The length of the cycle the state eventually reaches."""
    seen: dict[State, int] = {}
    step = 0
    while state not in seen:
        seen[state] = step
        state = update(state)
        step += 1
    return step - seen[state]


def running(update: Update, state: State) -> bool:
    return cycle_length(update, state) >= 2


def neighbors_differ(state: State) -> bool:
    """Instantaneous reader for the copy ring: some neighboring points differ."""
    return any(a != b for a, b in zip(state, state[1:] + state[:1]))


CONTACTS = ("latch", "driven", "hub", "single point")


@dataclass(frozen=True)
class TwoLoops:
    """Two copy rings and a contact bit under one synchronous update.

    contact:
    - "latch": c' = c or (A running and B running); the dynamic atom
    - "driven": c' = A running and B running; a gate, not a requirement
    - "hub": c' = c or A running or B running
    - "single point": c' = c or (a1 and b1); reads one point of each ring
    """

    size_a: int
    size_b: int
    contact: str = "latch"

    def __post_init__(self) -> None:
        if self.contact not in CONTACTS:
            raise ValueError(f"unknown contact rule {self.contact!r}")
        if min(self.size_a, self.size_b) < 2:
            raise ValueError("a ring needs at least two points")

    def step(self, a: State, b: State, c: bool) -> tuple[State, State, bool]:
        run_a, run_b = neighbors_differ(a), neighbors_differ(b)
        if self.contact == "latch":
            c = c or (run_a and run_b)
        elif self.contact == "driven":
            c = run_a and run_b
        elif self.contact == "hub":
            c = c or run_a or run_b
        else:
            c = c or (a[0] and b[0])
        return copy_ring(a), copy_ring(b), c

    def settled_contact(self, a: State, b: State, c: bool) -> bool:
        """The contact after every joint pattern has come around."""
        for _ in range(2 * self.size_a * self.size_b + 2):
            a, b, c = self.step(a, b, c)
        return c

    def outcomes(self) -> list[tuple[State, State, bool, bool]]:
        """(ring A, ring B, initial contact, settled contact) for every initial state."""
        return [
            (a, b, c, self.settled_contact(a, b, c))
            for a in product((False, True), repeat=self.size_a)
            for b in product((False, True), repeat=self.size_b)
            for c in (False, True)
        ]

    def relation(self) -> Relation:
        """Allowed (A running, B running, settled contact) over all initial states."""
        return Relation(
            ("A", "B", "c"),
            frozenset(
                (running(copy_ring, a), running(copy_ring, b), settled)
                for a, b, _, settled in self.outcomes()
            ),
        )

    def erasure_leaves_contact_free(self) -> bool:
        """Stricter K2: whatever is left of a frozen ring, the contact stays free.

        For every frozen state of one ring and every state of the other, both
        settled contact values occur.
        """
        settled: dict[tuple[State, State], set[bool]] = {}
        for a, b, _, value in self.outcomes():
            settled.setdefault((a, b), set()).add(value)
        return all(
            values == {False, True}
            for (a, b), values in settled.items()
            if not running(copy_ring, a) or not running(copy_ring, b)
        )


def conserved(update: Update, size: int) -> bool:
    """Whether running versus frozen never changes along the update."""
    return all(
        running(update, state) == running(update, update(state))
        for state in product((False, True), repeat=size)
    )


def reader_is_exact(size: int) -> bool:
    """Whether comparing neighbors tells running from frozen for the copy ring."""
    return all(
        neighbors_differ(state) == running(copy_ring, state)
        for state in product((False, True), repeat=size)
    )


def frozen_states(update: Update, size: int) -> list[State]:
    return [state for state in product((False, True), repeat=size)
            if not running(update, state)]
