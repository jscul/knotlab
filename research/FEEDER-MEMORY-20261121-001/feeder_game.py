"""Supply a persistent feeder cue and a one-bit action to the archived ration game."""

from copy import copy, deepcopy
from dataclasses import dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Literal


PRIOR = Path(__file__).resolve().parents[1] / "KNOT-RATION-GAME-20261121-001"
if str(PRIOR) not in sys.path:
    sys.path.append(str(PRIOR))

from game import CAPACITY, GROWTH_TURNS, INITIAL_ENERGY, RATION_GAIN, Game, _ports, action_rngs
from world import World, sample_world, source_key  # Re-export the archived founder API.


@dataclass(frozen=True, slots=True)
class Observation:
    feeder: bool
    energy: int
    previous: Literal["start", "eat", "move", "refused"]
    slots: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Transition:
    observation: Observation
    bit: int
    outgoing_slot: int | None
    energy_after: int
    next_observation: Observation | None


def recode_world(world: World, rename=None):
    """Rename reached distinctions and return the new-to-original names for move transport."""
    names = {name for stage in world.stages for holding in stage.holdings for name in holding}
    if rename is None:
        ceiling = max(names)
        rename = {name: ceiling - name for name in names}
    if set(rename) != names or len(set(rename.values())) != len(names):
        raise ValueError("A recoding must assign distinct names to all reached distinctions.")

    def recode_names(row):
        return tuple(rename[name] for name in row)

    def recode_birth(birth):
        return replace(birth, payments=tuple((holder, rename[name]) for holder, name in birth.payments),
                       grants=recode_names(birth.grants))

    stages = tuple(replace(stage,
                           holdings=tuple(map(recode_names, stage.holdings)),
                           loose=tuple(map(recode_names, stage.loose)),
                           links=tuple(tuple((rename[name], other) for name, other in row)
                                       for row in stage.links))
                   for stage in world.stages)
    attempts = tuple(replace(attempt, births=tuple(map(recode_birth, attempt.births)))
                     for attempt in world.attempts)
    recoded = replace(world, stages=stages, attempts=attempts, births=tuple(map(recode_birth, world.births)))
    return recoded, {new: old for old, new in rename.items()}


class _Engine(Game):
    def __init__(self, world, tape, original_labels):
        super().__init__(world, tape=tape, sensor=False)
        self.original_labels = MappingProxyType(dict(original_labels)) if original_labels is not None else None
        self.recoded_labels = (MappingProxyType({old: new for new, old in original_labels.items()})
                               if original_labels is not None else None)

    def _local_ports(self):
        if self.original_labels is None:
            return super()._local_ports()
        links = self.world.stages[self.formation].links[self.holder]
        original_links = tuple((self.original_labels[name], other) for name, other in links)
        ordered = _ports(self.world.seed, self.tape, self.holder, original_links)
        return tuple((self.recoded_labels[name], other) for name, other in ordered)

    def refuse_move(self):
        self._prepare()
        if self._local_ports():
            raise RuntimeError("A move is available at the current holder.")
        energy, previous = self.energy, self.previous
        self.energy -= 1
        self.turns += 1
        self.previous = "refused"
        self._prepared = False
        return {
            "turn": self.turns, "energy_after": self.energy, "terminal": self.done,
            "growth": self._growth_event(), "holder_before": self.holder, "holder_after": self.holder,
            "food_sensor": None, "food_before": self.holder in self.available, "previous": previous,
            "available_slots": 0, "action": "refused", "slot": None, "distinction": None,
            "consumed": False, "energy_before": energy, "wasted": 0,
            "rations_remaining": len(self.available),
        }


class FeederGame:
    """One resettable episode. Only observations and transitions go to its reader."""

    def __init__(self, world: World, *, tape=0, original_labels=None):
        self._game = _Engine(world, tape, original_labels)
        scheduled = world.attempts[:len(GROWTH_TURNS)]
        self._feeders = frozenset(birth.holder for attempt in scheduled for birth in attempt.births)
        self._last_event = None
        self.turn_bound = INITIAL_ENERGY + RATION_GAIN * len(self._feeders)

    @property
    def done(self):
        return self._game.done

    @property
    def last_event(self):
        """Return a detached spectator record of the completed action."""
        return deepcopy(self._last_event)

    def observe(self) -> Observation:
        local = self._game.observe()
        return Observation(self._game.holder in self._feeders, local.energy, local.previous, local.slots)

    def step(self, bit) -> Transition:
        if type(bit) not in (bool, int) or bit not in (0, 1):
            raise ValueError("A decision must be one bit: OFF (0) or ON (1).")
        bit = int(bit)
        current = self.observe()
        if bit:
            event = self._game.step(0)
        elif current.slots:
            _, move_rng = action_rngs(self._game.tape, self._game.turns + 1)
            event = self._game.step(1 + move_rng.choice(current.slots))
        else:
            event = self._game.refuse_move()
        if self._game.turns > self.turn_bound:
            raise RuntimeError("Episode exceeded its total available energy.")
        event["bit"] = bit
        self._last_event = event
        next_observation = None if self.done else self.observe()
        return Transition(current, bit, event["slot"], event["energy_after"], next_observation)

    def clone(self):
        """Fork the ledger at the same prepared observation and movement tape."""
        branch = copy(self)
        branch._game = copy(self._game)
        branch._game.available = self._game.available.copy()
        return branch

    def snapshot(self):
        """Return private, serializable game state without preparing another turn."""
        current = self._game
        growth = current._growth
        return {
            "seed": current.world.seed, "tape": current.tape, "law": current.world.law,
            "holder": current.holder, "start_holder": current.start_holder, "available": sorted(current.available),
            "ports": [list(port) for port in current._local_ports()], "prepared": current._prepared,
            "pending_growth": None if growth is None else [growth.status, growth.stage],
            "formation": current.formation, "turns": current.turns,
            "energy": current.energy, "meals": current.meals, "wasted": current.wasted, "previous": current.previous,
        }


def _public_observation(observation):
    if observation is None:
        return None
    return {"feeder": observation.feeder, "energy": observation.energy,
            "previous": observation.previous, "slots": list(observation.slots)}


def episode(world, reader, *, tape=0, prefix=(), trace=False, original_labels=None):
    """Run a fresh reader to death, with an optional supplied prefix of action bits."""
    current = FeederGame(world, tape=tape, original_labels=original_labels)
    prefix = tuple(prefix)
    if any(type(bit) not in (bool, int) or bit not in (0, 1) for bit in prefix):
        raise ValueError("A preparation prefix must consist of action bits.")
    public_history, events, apparatus = [], [], []
    unsuccessful_eats = passed_fresh = refusals = applied_prefix = 0
    while not current.done:
        observation = current.observe()
        index = len(public_history)
        forced = index < len(prefix)
        memory_before = getattr(reader, "memory_word", None) if trace else None
        bit = prefix[index] if forced else reader.decide(observation)
        action_word = getattr(reader, "action_word", None) if trace and not forced else None
        transition = current.step(bit)
        receipt = reader.advance(transition)
        public_history.append({
            "observation": _public_observation(transition.observation), "bit": transition.bit,
            "outgoing_slot": transition.outgoing_slot, "energy_after": transition.energy_after,
            "next_observation": _public_observation(transition.next_observation), "supplied": forced,
        })
        event = current._last_event
        unsuccessful_eats += event["action"] == "eat" and not event["consumed"]
        passed_fresh += event["bit"] == 0 and event["food_before"]
        refusals += event["action"] == "refused"
        applied_prefix += forced
        if trace:
            events.append(current.last_event)
            apparatus.append(None if memory_before is None else {
                "memory_before": memory_before, "action_word": action_word, "receipt": receipt,
            })

    final = current.snapshot()
    turns, meals, wasted = final["turns"], final["meals"], final["wasted"]
    if turns != INITIAL_ENERGY + RATION_GAIN * meals - wasted:
        raise RuntimeError("Death disagrees with the turn and energy ledger.")
    encoded = json.dumps(public_history, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    result = {
        "schema_version": 1, "seed": world.seed, "law": world.law, "tape": tape,
        "source_key": world.source_key, "start_holder": final["start_holder"],
        "turns": turns, "meals": meals, "energy": final["energy"], "wasted": wasted,
        "reason": "death", "turn_bound": current.turn_bound, "unsuccessful_eats": unsuccessful_eats,
        "passes_on_fresh_feeder": passed_fresh, "refusals": refusals,
        "public_history_sha256": sha256(encoded.encode("ascii")).hexdigest(),
    }
    if trace:
        result.update(prefix=list(map(int, prefix)), prefix_applied=applied_prefix,
                      public_history=public_history, events=events, apparatus=apparatus,
                      initial_energy=INITIAL_ENERGY, max_energy=CAPACITY, ration_gain=RATION_GAIN,
                      growth_turns=list(GROWTH_TURNS), sensor_enabled=False,
                      initial_holdings=[list(row) for row in world.stages[0].holdings])
    return result
