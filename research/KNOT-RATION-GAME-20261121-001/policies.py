"""Controllers that act on the ration game's public observation."""

from collections.abc import Callable, Mapping
import json
from math import isfinite
from pathlib import Path
from random import Random
from types import MappingProxyType

from game import Observation


EAT, MOVE = 0, 1
POLICY_NAMES = ("blind", "random", "sensing", "learner")
SENSOR_POLICIES = frozenset({"sensing", "learner"})
STATE_FIELDS = ("food", "energy", "previous", "slot_count")
ACTION_KINDS = ("eat", "move")
ALPHA_INITIAL = 0.35
ALPHA_VISIT_SCALE = 24
ALPHA_POWER = 0.6
DISCOUNT = 1.0
EPSILON_START = 0.35
EPSILON_END = 0.05
MODEL_SCHEMA = "ration-game-tabular-q-v1"

State = tuple[bool, int, str, int]
Values = tuple[float, float]
Model = Mapping[State, Values]
Policy = Callable[[Observation, Random, Random], int]
ZERO_VALUES = (0.0, 0.0)


def _state(observation: Observation) -> State:
    if observation.food is None:
        raise ValueError("The learner requires the food observation.")
    return observation.food, observation.energy, observation.previous, len(observation.slots)


def _action(kind: int, observation: Observation, move_rng: Random) -> int:
    if kind == EAT or not observation.slots:
        return EAT
    return move_rng.choice(observation.slots) + 1


def _greedy_kind(values: Values) -> int:
    return EAT if values[EAT] > values[MOVE] else MOVE


def _blind(observation: Observation, _decision_rng: Random, move_rng: Random) -> int:
    kind = EAT if observation.previous == "move" else MOVE
    return _action(kind, observation, move_rng)


def _balanced_random(observation: Observation, decision_rng: Random, move_rng: Random) -> int:
    return _action(decision_rng.randrange(2), observation, move_rng)


def _sensing(observation: Observation, _decision_rng: Random, move_rng: Random) -> int:
    if observation.food is None:
        raise ValueError("The sensing script requires the food observation.")
    return _action(EAT if observation.food else MOVE, observation, move_rng)


def get_policy(name: str, model: Model | None = None) -> Policy:
    """Create the public controller for a named comparison arm."""
    if name == "learner":
        if model is None:
            model = load_model()

        def learner(observation: Observation, _decision_rng: Random, move_rng: Random) -> int:
            values = model.get(_state(observation), ZERO_VALUES)
            return _action(_greedy_kind(values), observation, move_rng)

        return learner

    return {"blind": _blind, "random": _balanced_random, "sensing": _sensing}[name]


class QLearner:
    """Fit one value for eating and one for the shared movement rule."""

    def __init__(self):
        self.values: dict[State, Values] = {}
        self.visits: dict[State, tuple[int, int]] = {}

    def choose(self, observation: Observation, decision_rng: Random, move_rng: Random,
               epsilon: float) -> int:
        values = self.values.get(_state(observation), ZERO_VALUES)
        kind = _greedy_kind(values)
        if observation.slots and decision_rng.random() < epsilon:
            kind = decision_rng.randrange(2)
        return _action(kind, observation, move_rng)

    def update(self, observation: Observation, action: int, next_observation: Observation | None):
        state = _state(observation)
        kind = EAT if action == EAT else MOVE
        values = list(self.values.get(state, ZERO_VALUES))
        visits = list(self.visits.get(state, (0, 0)))
        alpha = ALPHA_INITIAL / (1 + visits[kind] / ALPHA_VISIT_SCALE) ** ALPHA_POWER

        target = 1.0  # The terminal turn earns the same reward as any other completed turn.
        if next_observation is not None:
            next_values = self.values.get(_state(next_observation), ZERO_VALUES)
            future = max(next_values) if next_observation.slots else next_values[EAT]
            target += DISCOUNT * future
        values[kind] += alpha * (target - values[kind])
        visits[kind] += 1
        self.values[state] = (values[EAT], values[MOVE])
        self.visits[state] = (visits[EAT], visits[MOVE])

    def record(self) -> dict:
        return {
            "schema": MODEL_SCHEMA,
            "state_fields": list(STATE_FIELDS),
            "action_kinds": list(ACTION_KINDS),
            "q_rows": [
                {"state": list(state), "values": list(values), "visits": list(self.visits[state])}
                for state, values in sorted(self.values.items())
            ],
        }


def load_model(path: str | Path | None = None) -> Model:
    """Read a frozen policy. The default checkpoint is kept beside the game CLI."""
    path = Path(path) if path is not None else Path(__file__).with_name("model.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    if (record["schema"] != MODEL_SCHEMA or tuple(record["state_fields"]) != STATE_FIELDS
            or tuple(record["action_kinds"]) != ACTION_KINDS):
        raise ValueError(f"Unsupported policy checkpoint {path}")

    values = {}
    for row in record["q_rows"]:
        food, energy, previous, slot_count = row["state"]
        eat, move = row["values"]
        key = (food, energy, previous, slot_count)
        if (type(food) is not bool or type(energy) is not int or energy < 1
                or previous not in ("start", "eat", "move")
                or type(slot_count) is not int or slot_count < 0
                or key in values or not all(isfinite(value) for value in (eat, move))):
            raise ValueError(f"Invalid Q row {row!r} in {path}")
        values[key] = (float(eat), float(move))
    return MappingProxyType(values)
