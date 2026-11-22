"""Ration certificates from the feeder game's public history."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from feeder_game import Observation, Transition


PublicRow = tuple[bool, int, int, int, int]
Verdict = Literal["full", "empty", "unknown", "nonfeeder"]

TRY = 0
CURRENT = -1
PASS_WITHOUT_MOVE = -2
AFTER_GROWTH = 4  # Public row zero is the observation before turn one.
CAPACITY = 10
RATION_GAIN = 4
PREVIOUS_CODE = {"start": 0, "eat": 1, "move": 2, "refused": 3}


def _join(holders: list[int], first: int, second: int) -> None:
    first_holder = holders[first]
    second_holder = holders[second]
    if first_holder == second_holder:
        return
    keep, replace = sorted((first_holder, second_holder))
    for visit, holder in enumerate(holders):
        if holder == replace:
            holders[visit] = keep


def _same_menu(holder: int, old: dict[int, int], new: dict[int, int]) -> bool:
    return holder in old and old[holder] == new.get(holder)


def _known_moves(
    holders: list[int], moves: list[tuple[int, int]], old: dict[int, int], new: dict[int, int]
) -> Iterator[tuple[int, int, int, int]]:
    """Yield (period, source holder, action, destination visit) facts."""
    for visit, action in moves:
        source = holders[visit]
        arrival = visit + 1
        target = holders[arrival]
        period = int(visit >= AFTER_GROWTH)
        yield period, source, action, arrival

        same_source_menu = _same_menu(source, old, new)
        if same_source_menu:
            # Old slots preserve their order. Equal counts rule out insertions.
            yield 1 - period, source, action, arrival

        if new.get(target) == 1:
            # Both an old arrival and a new arrival have a usable return here.
            yield 1, target, 1, visit

        used_old_slot = period == 0 or same_source_menu or _same_menu(target, old, new)
        if used_old_slot and (old.get(target) == 1 or new.get(target) == 1):
            # An old move supplies at least one old slot at its arrival holder.
            yield 0, target, 1, visit


def _close(
    public: Sequence[PublicRow],
    holders: list[int],
    moves: list[tuple[int, int]],
    attempts: list[tuple[int, bool]],
) -> str | None:
    """Propagate forced equalities in place and return any contradiction."""
    while True:
        feeders: dict[int, bool] = {}
        degrees: tuple[dict[int, int], dict[int, int]] = ({}, {})
        for visit, (feeder, _, _, degree, _) in enumerate(public):
            holder = holders[visit]
            if feeders.setdefault(holder, feeder) != feeder:
                return "different feeder signals at a single holder"
            menu = degrees[int(visit >= AFTER_GROWTH)]
            if menu.setdefault(holder, degree) != degree:
                return "different menu counts in a stable period"

        old, new = degrees
        if any(new.get(holder, degree) < degree for holder, degree in old.items()):
            return "menu count fell after growth"
        if any(holders[visit] == holders[visit + 1] for visit, _ in moves):
            return "a realized move joined a holder to itself"

        spent: set[int] = set()
        for visit, paid in attempts:
            holder = holders[visit]
            if paid and holder in spent:
                return "a ration paid after that holder was already empty"
            spent.add(holder)

        destinations: dict[tuple[int, int, int], int] = {}
        forced = []
        for period, holder, action, arrival in _known_moves(holders, moves, old, new):
            earlier = destinations.setdefault((period, holder, action), arrival)
            if holders[earlier] != holders[arrival]:
                forced.append((earlier, arrival))

        if not forced:
            return None
        for first, second in forced:
            _join(holders, first, second)


def _evaluate(public: Sequence[PublicRow]) -> tuple[Verdict, str]:
    if not public or public[-1][4] != CURRENT or public[0][2] != PREVIOUS_CODE["start"]:
        return "unknown", "history must run from the start through the current observation"
    if not public[-1][0]:
        return "nonfeeder", "current feeder signal is off"

    holders = list(range(len(public)))
    moves: list[tuple[int, int]] = []
    attempts: list[tuple[int, bool]] = []
    for visit, (feeder, energy, _, degree, action) in enumerate(public[:-1]):
        after = public[visit + 1][1]

        # At every playable energy, the cap leaves the two receipts distinct.
        paid = action == TRY and feeder and after == min(CAPACITY, energy - 1 + RATION_GAIN)
        if not paid and after != energy - 1:
            return "unknown", f"inconsistent energy receipt on turn {visit + 1}"

        if 1 <= action <= degree:
            moves.append((visit, action))
        elif action == TRY or (action == PASS_WITHOUT_MOVE and degree == 0):
            _join(holders, visit, visit + 1)
            if action == TRY and feeder:
                attempts.append((visit, paid))
        else:
            return "unknown", f"inconsistent action on turn {visit + 1}"

    paid_visits = [visit for visit, paid in attempts if paid]
    if not attempts:
        return "full", "no earlier attempt at any feeder"
    if not paid_visits:
        return "unknown", "a refusal has no recorded earlier successful eat"

    conflict = _close(public, holders, moves, attempts)
    if conflict is not None:
        return "unknown", f"inconsistent history ({conflict})"

    current = len(public) - 1
    for visit, paid in reversed(attempts):
        if holders[visit] == holders[current]:
            receipt = "successful eat" if paid else "refused eat"
            return "empty", f"same feeder as the {receipt} on turn {visit + 1}"

    excluded = []
    for visit in paid_visits:
        hypothesis = holders.copy()
        _join(hypothesis, current, visit)
        conflict = _close(public, hypothesis, moves, attempts)
        if conflict is None:
            return "unknown", f"history does not settle a match to the successful eat on turn {visit + 1}"
        excluded.append((visit + 1, conflict))

    reason = ", ".join(f"turn {turn} ({conflict})" for turn, conflict in excluded)
    return "full", f"excluded every earlier successful eat: {reason}"


def history_verdict(public: Sequence[PublicRow]) -> Verdict:
    """Classify a complete public history, including its current observation.

    Rows are (feeder, energy, previous_code, degree, action_code). Previous
    codes 0, 1, 2 and 3 mean start, eat, move and refused. Action codes 0 and
    slot+1 mean try and a realized pass. Use -2 for a pass with no available
    control and -1 for the current undecided row.
    """
    return _evaluate(public)[0]


def history_reason(public: Sequence[PublicRow]) -> str:
    """Summarize the public evidence used for the verdict."""
    return _evaluate(public)[1]


def _row(observation: Observation, action: int) -> PublicRow:
    return (
        observation.feeder,
        observation.energy,
        PREVIOUS_CODE[observation.previous],
        len(observation.slots),
        action,
    )


class PublicHistoryReader:
    """Read the public fields of a feeder-game episode."""

    def __init__(self) -> None:
        self._public: list[PublicRow] = []

    def reset(self) -> None:
        self._public.clear()

    def advance(self, transition: Transition) -> None:
        slot = transition.outgoing_slot
        if slot is not None:
            action = slot + 1
        else:
            action = TRY if transition.bit else PASS_WITHOUT_MOVE
        self._public.append(_row(transition.observation, action))

    def verdict(self, observation: Observation) -> Verdict:
        return history_verdict([*self._public, _row(observation, CURRENT)])

    def reason(self, observation: Observation) -> str:
        return history_reason([*self._public, _row(observation, CURRENT)])

    def decide(self, observation: Observation) -> int:
        """Attempt on full or unresolved feeders and pass otherwise."""
        return int(self.verdict(observation) in ("full", "unknown"))
