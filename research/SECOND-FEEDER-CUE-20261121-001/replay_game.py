"""Replay supplied public action prefixes through the archived feeder game."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ARCHIVE = Path(__file__).resolve().parents[1] / "FEEDER-MEMORY-20261121-001"
if str(ARCHIVE) not in sys.path:
    sys.path.append(str(ARCHIVE))

from feeder_game import (  # noqa: E402
    CAPACITY,
    RATION_GAIN,
    FeederGame,
    Observation,
    Transition,
    World,
    action_rngs,
)


PREVIOUS = {"start": 0, "eat": 1, "move": 2, "refused": 3}


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def public_view(observation: Observation) -> list[bool | int]:
    return [observation.feeder, observation.energy, PREVIOUS[observation.previous], len(observation.slots)]


def public_action(transition: Transition) -> int:
    if transition.bit:
        return 0
    if transition.outgoing_slot is None:
        return -2
    return transition.outgoing_slot + 1


@dataclass(frozen=True)
class ReplayTurn:
    before: dict
    receipt: Transition
    event: dict

    def public_row(self) -> list[bool | int]:
        return [*public_view(self.receipt.observation), public_action(self.receipt)]


def take_turn(game: FeederGame, world: World, bit: int) -> ReplayTurn:
    """Check both the public receipt and the separate spectator move ledger."""
    observation = game.observe()
    before = game.snapshot()
    receipt = game.step(bit)
    event = game.last_event
    turn = before["turns"] + 1
    at = f"{world.law} seed {world.seed} at turn {turn}"
    origin = before["holder"]
    has_ration = origin in before["available"]
    consumed = bool(bit and has_ration)
    energy = min(CAPACITY, observation.energy - 1 + RATION_GAIN * consumed)

    require(receipt.observation == observation and receipt.bit == bit, f"Public receipt differs at {at}")
    require(event["turn"] == turn and event["holder_before"] == origin, f"Wrong starting knot at {at}")
    require(event["bit"] == bit and event["food_before"] == has_ration, f"Game ledger differs at {at}")
    require(event["consumed"] == consumed, f"Ration depletion differs at {at}")
    require(event["rations_remaining"] == len(before["available"]) - consumed, f"Ration count differs at {at}")
    require(event["energy_before"] == observation.energy, f"Energy before action differs at {at}")
    require(receipt.energy_after == event["energy_after"] == energy, f"Energy after action differs at {at}")
    require(event["terminal"] == (energy == 0) == game.done, f"Terminal record differs at {at}")
    require(event["slot"] == receipt.outgoing_slot, f"Move slot differs between records at {at}")
    require(len(before["ports"]) == len(observation.slots), f"Menu size differs at {at}")

    if not bit and observation.slots:
        rng = action_rngs(before["tape"], turn)[1]
        slot = rng.choice(observation.slots)
        distinction, destination = before["ports"][slot]
        require(event["action"] == "move", f"Move was not applied at {at}")
        require(event["slot"] == slot, f"Move did not use the seeded tie at {at}")
        require((event["distinction"], event["holder_after"]) == (distinction, destination),
                f"Move did not follow the chosen shared distinction at {at}")
        holdings = world.stages[before["formation"]].holdings
        owners = {holder for holder, row in enumerate(holdings) if distinction in row}
        require(owners == {origin, destination} and len(owners) == 2,
                f"Moved distinction is not shared by both knots at {at}")
    else:
        require(event["action"] == ("eat" if bit else "refused"), f"Incorrect stay action at {at}")
        require(event["holder_after"] == origin and event["slot"] is None and event["distinction"] is None,
                f"Stay action changed the cursor or recorded a move at {at}")
    return ReplayTurn(before, receipt, event)


@dataclass
class ReplayPrefix:
    game: FeederGame
    rows: list[ReplayTurn]
    observation: Observation

    def public_history(self) -> list[list[bool | int]]:
        return [*(row.public_row() for row in self.rows), [*public_view(self.observation), -1]]

    def route(self) -> list[int]:
        initial = self.rows[0].event["holder_before"] if self.rows else self.game.snapshot()["holder"]
        return [initial, *(row.event["holder_after"] for row in self.rows)]

    def paid_holders(self) -> list[int]:
        return [row.event["holder_before"] for row in self.rows if row.event["consumed"]]


def play_prefix(world: World, tape: int, attempts: list[int], decision_turn: int,
                *, original_labels=None) -> ReplayPrefix:
    require(attempts == sorted(set(attempts)) and all(1 <= turn < decision_turn for turn in attempts),
            "Supplied attempts must be distinct, ordered, and precede the decision")
    game = FeederGame(world, tape=tape, original_labels=original_labels)
    scheduled = set(attempts)
    rows = []
    for turn in range(1, decision_turn):
        require(not game.done, f"The supplied prefix reached death before turn {turn}")
        rows.append(take_turn(game, world, int(turn in scheduled)))
    require(not game.done, "The supplied prefix reached death before the paired decision")
    return ReplayPrefix(game, rows, game.observe())
