"""The strict return writes its vote independently of the last paid menu.

The unchanged first-study device supplies every other physical read, operation
and register. Both implementations can be loaded in one process.
"""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


FIRST_SOURCE = Path(__file__).resolve().parents[1] / "device.py"
FIRST_SHA256 = "6c65130f278deab87acd2a7365880367beb4008b2884a66b13a4ec1197f735bf"
if sha256(FIRST_SOURCE.read_bytes()).hexdigest() != FIRST_SHA256:
    raise ImportError("The first feeder-cue apparatus differs from its registered source.")

# Use the already loaded first apparatus when normal imports put it under
# 'device'; a distinct module name also permits running the repair on its own.
first = sys.modules.get("device")
if getattr(first, "__file__", None) != str(FIRST_SOURCE):
    module_name = "_first_feeder_cue_device_6c65130f"
    first = sys.modules.get(module_name)
    if first is None:
        spec = spec_from_file_location(module_name, FIRST_SOURCE)
        first = module_from_spec(spec)
        sys.modules[module_name] = first
        spec.loader.exec_module(first)

NAMES = first.NAMES
OWNERS = first.OWNERS
STARS = first.STARS
CUES = first.CUES
CATALOGUE = first.CATALOGUE
SECOND_FIELDS = first.SECOND_FIELDS
SELECTED_FIELD = first.SELECTED_FIELD
old = first.old

original_strict = first.DETECTORS[0]
original_offer, = original_strict
guard_removed = first.literal("paid", 1)
if guard_removed not in original_offer.guard:
    raise ValueError("The registered old menu-match guard is missing.")
strict_offer = first.offer(original_offer.label, original_offer.holder,
                           original_offer.operands,
                           tuple(test for test in original_offer.guard if test != guard_removed))
DETECTORS = ((strict_offer,), *first.DETECTORS[1:])


class LearnedKnotBot(first.LearnedKnotBot):
    """Run the original schedule with its single changed fixed offer."""

    __slots__ = ()

    def _run(self, seq, connected=True, trace=None):
        # This choice is between two fixed programs, independent of the
        # physical state or game outcome. All writes run the same guard engine.
        if seq is original_strict:
            seq = DETECTORS[0]
        return super()._run(seq, connected, trace)
