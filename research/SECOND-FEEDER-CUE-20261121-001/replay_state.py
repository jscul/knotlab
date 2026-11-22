"""Independent public-history and detector reference for the seed replay."""

from __future__ import annotations

from dataclasses import dataclass, replace

from replay_game import Observation, Transition, require


SECOND_FIELDS = ("x_here", "x_departed", "x_paid_from", "x_paid_menu", "x_paid_slot")
SELECTED_FIELD = {
    "strict_return": "x_here",
    "approach_feeder": "x_paid_from",
    "approach_menu": "x_paid_menu",
    "approach_slot": "x_paid_slot",
}
ARRIVAL_FIELDS = {"x_paid_from": "arr_from", "x_paid_menu": "arr_menu", "x_paid_slot": "arr_slot"}
FIELD_WIDTHS = {"x_here": 2, "x_departed": 2, "x_paid_from": 3, "x_paid_menu": 4, "x_paid_slot": 3}
DETECTORS = tuple(SELECTED_FIELD)
MENU_MEMORY = ("110", "101", "011")


def one_hot(place: int, width: int) -> str:
    require(0 <= place < width, f"Place {place} is outside a {width}-mark word")
    return "0" * place + "1" + "0" * (width - place - 1)


def neutral_words() -> dict[str, str]:
    return {name: one_hot(0, width) for name, width in FIELD_WIDTHS.items()}


def offered_menu(observation: Observation) -> int:
    return min(2, len(observation.slots))


@dataclass(frozen=True)
class Approach:
    feeder: int = 0
    menu: int = 0
    slot: int = 0

    @classmethod
    def from_departure(cls, observation: Observation, chosen_slot: int) -> Approach:
        return cls(1 + int(observation.feeder), 1 + offered_menu(observation), 1 + chosen_slot % 2)

    def words(self, prefix) -> dict[str, str]:
        return {f"{prefix}_from": one_hot(self.feeder, 3), f"{prefix}_menu": one_hot(self.menu, 4),
                f"{prefix}_slot": one_hot(self.slot, 3)}


@dataclass(frozen=True)
class PublicMemory:
    """Use only the public receipt fields from the executed action."""

    completed: int = 0
    m: str = "110"
    here: bool = False
    departed: bool = False
    paid: Approach = Approach()
    arrival: Approach = Approach()

    def words(self) -> dict[str, str]:
        return {"m": self.m, "phase": one_hot(min(self.completed, 4), 5),
                "x_here": one_hot(int(self.here), 2), "x_departed": one_hot(int(self.departed), 2),
                **self.paid.words("x_paid"), **self.arrival.words("arr")}

    def advance(self, turn: Transition) -> PublicMemory:
        observation = turn.observation
        if turn.outgoing_slot is not None:
            stable = self.completed >= 4
            return replace(self, completed=self.completed + 1,
                           here=self.departed and len(observation.slots) == 1 and stable,
                           departed=self.here and stable,
                           arrival=Approach.from_departure(observation, turn.outgoing_slot))
        payment = bool(turn.bit and turn.energy_after > observation.energy - 1)
        if not payment:
            return replace(self, completed=self.completed + 1)
        menu = offered_menu(observation)
        return replace(self, completed=self.completed + 1, m=MENU_MEMORY[menu] if menu else self.m,
                       here=True, paid=self.arrival)


def current_choice(observation: Observation) -> int:
    return int(observation.feeder and observation.previous != "eat")


def empty_votes(observation: Observation, words: dict[str, str]) -> dict[str, bool]:
    """Classify each declared candidate from recorded names, without a stock input."""
    menu = offered_menu(observation)
    votes = dict.fromkeys(DETECTORS, False)
    if not current_choice(observation) or not menu or words["m"] != MENU_MEMORY[menu]:
        return votes
    votes["strict_return"] = words["x_here"] == "01"
    for detector, past in SELECTED_FIELD.items():
        present = ARRIVAL_FIELDS.get(past)
        if present is not None:
            old = words[past]
            votes[detector] = old[0] == "0" and old == words[present]
    return votes


def expected_bit(observation: Observation, words: dict[str, str], selector: str) -> int:
    require(selector == "none" or selector in SELECTED_FIELD, f"Unknown selector {selector!r}")
    return current_choice(observation) * (not empty_votes(observation, words).get(selector, False))


def selected_from_score(scores: dict[str, int]) -> str:
    best = max(DETECTORS, key=scores.__getitem__)
    return best if scores[best] > 0 else "none"
