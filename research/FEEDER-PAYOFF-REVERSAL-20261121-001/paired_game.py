"""Supply opposite three-exit ration openings in the archived feeder game."""

import sys
from dataclasses import replace
from hashlib import blake2s
from pathlib import Path


HERE = Path(__file__).resolve().parent
B306 = HERE.parent / "FEEDER-MEMORY-20261121-001"
if str(B306) not in sys.path:
    sys.path.append(str(B306))

from feeder_game import FeederGame, Observation, Transition, recode_world, sample_world, source_key  # noqa: E402


def current_only(observation: Observation) -> int:
    """The unchanged one-bit action of the B306 current-only reader."""
    return int(observation.feeder and observation.previous != "eat")


def derive_clue(observation_before_move: Observation, outgoing_slot: int | None) -> int | None:
    """Return the supported public A/B clue, using only the departure menu."""
    slots = observation_before_move.slots
    if outgoing_slot is None or outgoing_slot not in slots or (outgoing_slot ^ 1) not in slots:
        return None
    return outgoing_slot % 2


def accepted_approach(seed: int, tape: int, holder: int, version: int, *, exception=None) -> int:
    """Compute the private, paired opening for one holder."""
    if exception is None:
        key = f"{seed}|{tape}|{holder}".encode("ascii")
        first = blake2s(key, digest_size=1, person=b"FDRGATE1").digest()[0]
        exception = (first & 3) == 0
    return version ^ int(exception)


class ReversalGame(FeederGame):
    """B306's one-bit game with one private approach check per eligible bite."""

    def __init__(self, world, *, tape=0, version, mirror=False, training_exception=None,
                 original_labels=None):
        super().__init__(world, tape=tape, original_labels=original_labels)
        if version is not None and (type(version) is not int or version not in (0, 1)):
            raise ValueError("A supplied version must be 0 or 1.")
        if type(mirror) is not bool:
            raise ValueError("The mirrored labeling option must be Boolean.")
        if training_exception is not None and type(training_exception) is not bool:
            if (type(training_exception) is not tuple or len(training_exception) != 2
                    or type(training_exception[0]) is not int or training_exception[0] not in self._feeders
                    or type(training_exception[1]) is not bool):
                raise ValueError("A targeted training override must supply a feeder holder and a Boolean exception.")
        if version is None and training_exception is not None:
            raise ValueError("A training override requires a supplied access version.")
        self._version = version
        self._mirror = mirror
        self._training_exception = training_exception
        self._arrival_slot = None
        self._approach = None

    def _exception_at(self, holder):
        exception = self._training_exception
        if isinstance(exception, tuple):
            return exception[1] if exception[0] == holder else None
        return exception

    def step(self, bit) -> Transition:
        if type(bit) not in (bool, int) or bit not in (0, 1):
            raise ValueError("A decision must be one bit: OFF (0) or ON (1).")
        if self._version is None and not self._mirror:
            return super().step(bit)

        observation = self.observe()
        game = self._game
        holder = game.holder
        arrival_slot = self._arrival_slot
        approach = self._approach
        eligible = (self._version is not None and observation.feeder and
                    approach is not None and len(observation.slots) == 3)
        opening = (accepted_approach(game.world.seed, game.tape, holder, self._version,
                                     exception=self._exception_at(holder)) if eligible else None)
        denied = bool(bit and holder in game.available and eligible and approach != opening)
        if denied:
            # Use the archived unsuccessful-eat transition and then restore the
            # suspended stock. Its public receipt is exactly one charged turn.
            game.available.remove(holder)
        try:
            transition = super().step(bit)
        finally:
            if denied:
                game.available.add(holder)

        event = self._last_event
        if denied:
            event["food_before"] = True
            event["rations_remaining"] += 1
        physical_slot = transition.outgoing_slot
        if physical_slot is not None:
            clue = derive_clue(observation, physical_slot)
            public_slot = physical_slot ^ 1 if self._mirror and clue is not None else physical_slot
            self._arrival_slot = public_slot
            self._approach = derive_clue(observation, public_slot)
            event["slot"] = public_slot
            transition = replace(transition, outgoing_slot=public_slot)
        event.update(
            arrival_slot=arrival_slot, approach=approach, eligible=eligible,
            accepted_approach=opening, denied=denied, physical_slot=physical_slot,
        )
        return transition

    def snapshot(self):
        snapshot = super().snapshot()
        if self._version is not None or self._mirror:
            snapshot.update(version=self._version, arrival_slot=self._arrival_slot,
                            approach=self._approach, mirror=self._mirror)
        if self._mirror:
            ports = snapshot["ports"]
            snapshot["ports"] = [ports[i ^ 1] if (i ^ 1) < len(ports) else port
                                 for i, port in enumerate(ports)]
        return snapshot
