"""The supplied ration game on a read-only trace of ordinary knot growth."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import blake2s
import random

from world import World


INITIAL_ENERGY = 6
CAPACITY = 10
RATION_GAIN = 4
GROWTH_TURNS = (1, 5)


def _seed(domain, *values):
    line = "|".join([domain, *(str(n) for n in values)])
    return int.from_bytes(blake2s(line.encode("ascii"), digest_size=8, person=b"RATGAME1").digest(), "big")


def action_rngs(tape, turn):
    """Independent public-choice and move-tie draws, paired across controllers."""
    return random.Random(_seed("decision", tape, turn)), random.Random(_seed("port", tape, turn))


@dataclass(frozen=True, slots=True)
class Observation:
    food: bool | None
    energy: int
    slots: tuple[int, ...]
    previous: str


@lru_cache(maxsize=8192)
def _ports(seed, tape, holder, links):
    # A marked local port is not a destination ID. Preserve the order of old
    # ports relative to one another as new shared distinctions become available.
    return tuple(sorted(links, key=lambda link: (_seed("slot", seed, tape, holder, link[0]), link[0])))


class Game:
    """One resettable episode. Sources are immutable; ledgers belong to this copy."""

    def __init__(self, world: World, *, tape=0, sensor=True):
        self.world = world
        self.tape = tape
        self.sensor = sensor
        self.formation = 0
        self.start_holder = random.Random(_seed("cursor", world.seed)).randrange(len(world.stages[0].holdings))
        self.holder = self.start_holder
        self.energy = INITIAL_ENERGY
        self.turns = 0
        self.meals = 0
        self.wasted = 0
        self.previous = "start"
        self.available = set()
        self._prepared = False
        self._growth = None

    @property
    def done(self):
        return self.energy == 0

    def _prepare(self):
        if self.done:
            raise RuntimeError("This episode ended at zero energy.")
        if self._prepared:
            return
        self._growth = None
        turn = self.turns + 1
        if turn in GROWTH_TURNS:
            index = GROWTH_TURNS.index(turn)
            if index < len(self.world.attempts):
                attempt = self.world.attempts[index]
                self.formation = attempt.stage
                self._growth = attempt
                self.available.update(birth.holder for birth in attempt.births)
        self._prepared = True

    def _local_ports(self):
        links = self.world.stages[self.formation].links[self.holder]
        return _ports(self.world.seed, self.tape, self.holder, links)

    def observe(self):
        self._prepare()
        slots = tuple(range(len(self._local_ports())))
        return Observation(self.holder in self.available if self.sensor else None, self.energy, slots, self.previous)

    def _growth_event(self):
        if self._growth is None:
            return None
        a = self._growth
        holdings = self.world.stages[self.formation].holdings
        return {
            "status": a.status, "formation": a.stage,
            "shortages": [list(s) for s in a.shortages],
            "births": [
                {"holder": b.holder, "formation": b.formation, "payments": [list(p) for p in b.payments],
                 "grants": list(b.grants), "demand": b.demand, "holdings": list(holdings[b.holder])}
                for b in a.births
            ],
        }

    def step(self, action, *, detail=True):
        self._prepare()
        ports = self._local_ports()
        if type(action) is not int or not 0 <= action <= len(ports):
            raise ValueError(f"Action must be eat (0) or a local move in 1..{len(ports)}")
        before, energy, previous = self.holder, self.energy, self.previous
        food = before in self.available
        consumed = action == 0 and food
        slot = action-1 if action else None
        distinction = None
        if action:
            distinction, self.holder = ports[slot]
        elif consumed:
            self.available.remove(before)
            self.meals += 1
        gross = energy-1+RATION_GAIN*consumed
        self.energy = min(CAPACITY, gross)
        self.wasted += gross-self.energy
        self.turns += 1
        self.previous = "move" if action else "eat"
        self._prepared = False
        event = {"turn": self.turns, "energy_after": self.energy, "terminal": self.done}
        if detail:
            event.update(
                growth=self._growth_event(), holder_before=before, holder_after=self.holder,
                food_sensor=food if self.sensor else None, food_before=food, previous=previous,
                available_slots=len(ports), action=self.previous, slot=slot, distinction=distinction,
                consumed=consumed, energy_before=energy, wasted=gross-self.energy,
                rations_remaining=len(self.available),
            )
        return event


def episode(world, policy, *, tape=0, sensor=True, trace=False):
    """Let a controller play to death. No growth or action waits for human input."""
    game = Game(world, tape=tape, sensor=sensor)
    events = []
    budget = INITIAL_ENERGY + RATION_GAIN * sum(len(a.births) for a in world.attempts[:len(GROWTH_TURNS)])
    while not game.done:
        obs = game.observe()
        decision, move = action_rngs(tape, game.turns+1)
        event = game.step(policy(obs, decision, move), detail=trace)
        if trace:
            events.append(event)
        if game.turns > budget:
            raise RuntimeError("Turn count exceeded the total available energy.")
    assert game.turns == INITIAL_ENERGY + RATION_GAIN*game.meals - game.wasted
    return {
        "schema_version": 1, "law": world.law, "seed": world.seed, "tape": tape,
        "source_key": world.source_key, "start_holder": game.start_holder,
        "policy": getattr(policy, "__name__", type(policy).__name__), "sensor_enabled": sensor,
        "initial_energy": INITIAL_ENERGY, "max_energy": CAPACITY, "ration_gain": RATION_GAIN,
        "growth_turns": list(GROWTH_TURNS), "initial_holdings": [list(x) for x in world.stages[0].holdings],
        "turns": game.turns, "meals": game.meals, "energy": game.energy,
        "wasted": game.wasted, "reason": "death", "events": events,
    }
