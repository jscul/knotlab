"""Exact sequential replay of two local scripts, including observed failures."""

from collections import Counter
from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import lcm
from pathlib import Path
import sys

from predict import HOLDS, ROLES, SMALL_HOLDS, SMALL_ROLES, allowed_for

EPIC = 'TWO-KNOTS-ONE-DECISION-20261121-001'
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research' / EPIC))
from literal_read import LiteralReader, total_variation  # noqa: E402
from measurement import QuantumReader, compile_device, law  # noqa: E402

FRESH = ('write', 'write')
CLEAR = ('none', 'none')
HISTORY_FIELD_ORDER = ('request', 'status', 'raw_word', 'displayed_word', 'branch_tag')


@dataclass(frozen=True)
class Catalogue:
    holdings: tuple
    roles: tuple
    allowed: tuple


def catalogue(name):
    holds, roles = (SMALL_HOLDS, SMALL_ROLES) if name.startswith('small_') else (HOLDS, ROLES)
    kind = name.removeprefix('small_')
    expected = allowed_for(holds, kind)
    actual = law(holds, kind='nae' if kind == 'nae' else 'parity', odd=5 if kind == 'signed' else None)
    assert expected == actual
    return Catalogue(holds, roles, actual)


def status_code(req, status, raw=None, displayed=None, tag=None):
    return req, status, raw, displayed, tag


def compact(record):
    return tuple(getattr(record, field) for field in HISTORY_FIELD_ORDER)


def latch_word(bit):
    return '011' if bit else '101'


def output_record(code, c, role, slot, ready, *, tags=None, calibrated=frozenset(), prior=()):
    """Invert the local record code. The public herald is its only shared register."""
    req, status, raw, shown, tag = code
    stock = c.roles[role]
    holds = c.holdings
    defined = type(req) is int and 0 <= req < len(holds)
    fields = holds[req] if defined else ()
    address_pattern = (tuple(req[1]) if isinstance(req, tuple) and req[0] == 'bank'
                       else tuple(int(h == req) for h in stock))
    names = tuple(f'{role}.{slot}.answer.{j}' for j in range(len(fields)))
    bits = () if shown is None else tuple(shown >> j & 1 for j in range(len(fields)))
    raw_bits = () if raw is None else tuple(raw >> j & 1 for j in range(len(fields)))
    snapshots = {name: latch_word(bit) for name, bit in zip(names, bits)}
    exchanges = tuple((f'{name}.{0 if bit else 1}', f'{name}.2') for name, bit in zip(names, bits))
    complete = status == 'success'
    admitted = status in ('success', 'disconnected')
    measurement_schedule = () if not admitted else tuple(
        (mark, 'private auxiliary prepared', 'controlled named read', 'inverse mixing',
         'pointer measured', 'fixed local write opportunity') for mark in fields)
    return dict(local_request=req, actual_ordered_marks=fields,
                one_hot_bank=tuple(latch_word(b) for b in address_pattern), holder_bank_names=stock,
                source_herald=latch_word(ready), local_request_receipt=latch_word(req is not None),
                attempted=req is not None, measurement_admitted=admitted,
                registered_request_pulse=admitted, local_fixed_end_of_slot=True,
                status=status, completed_with_answer=complete, local_detection=complete,
                programmable_answer_capacity=('insufficient' if status == 'not_ready' else 'preallocated'),
                raw_word=raw, raw_bits=tuple(latch_word(bit) for bit in raw_bits),
                calibration_bits=tuple(int((req, e) in calibrated) for e in fields), displayed_word=shown,
                kept_tag=tag, tag_holder=('110' if tag is None else latch_word(tag)), tag_policy=tags,
                local_measurement_sequence=measurement_schedule, actual_fired_pairs=exchanges,
                fresh_allocated_keeper_rows=tuple((name, '110', snapshots.get(name, '110')) for name in names
                                                  if status != 'not_ready'),
                keeper_snapshot={**dict(prior), **snapshots})


def state_code(state):
    if is_dataclass(state):
        return {'representation': type(state).__name__, 'state': asdict(state)}
    return {'representation': 'signed Pauli generators or literal memories', 'state': state}


class Replay:
    def __init__(self, c, mode, *, device=None):
        self.c = c
        self.mode = mode
        self.literal = mode.startswith('literal')
        self.force_erasure = mode == 'erasure'
        self.source = mode if mode in ('dephased', 'independent', 'ordinary') else 'coherent'
        if self.literal:
            self.engine = LiteralReader(c.holdings, c.allowed, bias=(mode == 'literal_biased'))
            self.device = None
            self.acceptance = Fraction(1)
        else:
            self.device = (device if device is not None else
                           compile_device(c.holdings, c.allowed, relaxed=mode == 'relaxed'))
            self.q_cache = {}
            self.acceptance = self.quantum(CLEAR, FRESH).acceptance
        self.transition = lru_cache(maxsize=4096)(self._transition)

    def quantum(self, tag, writer):
        key = tag, writer
        if key not in self.q_cache:
            self.q_cache[key] = QuantumReader(self.device, self.source, tag=tag, writer=writer,
                                              roles=self.c.roles, force_refusal=self.force_erasure)
        return self.q_cache[key]

    def initial(self, on_success=False):
        if self.literal:
            return ((True, self.engine.start(), Fraction(1)),)
        reader = self.quantum(CLEAR, FRESH)
        if on_success:
            return ((True, reader.start(), Fraction(1)),) if self.acceptance else ()
        return tuple((i == 0 and bool(self.acceptance), state, mass)
                     for i, (mass, state) in enumerate(reader.initial()))

    def _route(self, req, i):
        if req is None:
            return req, None
        if isinstance(req, tuple) and req[0] == 'bank':
            options = self.c.roles[i]
            supplied = req[1]
            if len(supplied) != len(options) or any(bit not in (0, 1) for bit in supplied) or not any(supplied):
                return None, 'unfitted_address'
            if sum(supplied) != 1:
                return None, 'duplicate_address'
            return options[supplied.index(1)], None
        if type(req) is not int or not 0 <= req < len(self.c.holdings):
            return None, 'unfitted_address'
        if req not in self.c.roles[i]:
            return None, 'out_of_role'
        return req, None

    def _transition(self, state, requested, tags, writers):
        routed, failures = zip(*(self._route(req, i) for i, req in enumerate(requested)), strict=True)
        if self.literal:
            rows = ((tuple(status_code(r, readout.status, w, w)
                           for r, w, readout in zip(routed, (a, b),
                                                   (self.engine.readout(routed[0], a),
                                                    self.engine.readout(routed[1], b)), strict=True)),
                     mass, after)
                    for a, b, mass, after in self.engine.step(state, *routed))
        else:
            q = self.quantum(tags, writers)
            rows = (((compact(a), compact(b)), mass, after)
                    for a, b, mass, after in q.step_detailed(state, *routed))
        return tuple((tuple(status_code(req, bad) if bad is not None else present
                            for req, present, bad in zip(requested, readouts, failures, strict=True)),
                      mass, after) for readouts, mass, after in rows)

    def run(self, left, right, *, slots=None, on_success=False, tag=CLEAR, writer=FRESH,
            profiles=None, poststates=False):
        """Exact joint laws. Callable scripts receive only their own earlier local records."""
        scripts = tuple(s if callable(s) else tuple(s) for s in (left, right))
        if slots is None:
            slots = len(next(s for s in scripts if not callable(s)))
        assert all(callable(s) or len(s) == slots for s in scripts)
        schedule = ((tag, writer),) * slots if profiles is None else tuple(profiles)
        assert len(schedule) == slots
        paths = Counter({(ready, state, (), (), (state,) if poststates else ()): mass
                         for ready, state, mass in self.initial(on_success)})
        if not paths:
            return None
        for s, (slot_tag, slot_writer) in enumerate(schedule):
            next_rows = Counter()
            for (ready, state, a, b, states), weight in paths.items():
                requests = tuple(script(history) if callable(script) else script[s]
                                 for script, history in zip(scripts, (a, b), strict=True))
                for (ra, rb), prob, after in self.transition(state, requests, slot_tag, slot_writer):
                    post = states + (after,) if poststates else states
                    next_rows[ready, after, a + (ra,), b + (rb,), post] += weight * prob
            paths = next_rows
        result = Counter()
        for (ready, _, a, b, states), weight in paths.items():
            result[(ready, a, b, states) if poststates else (ready, a, b)] += weight
        assert sum(result.values()) == 1
        return result


def encode_law(rows, dimensions=None):
    if rows is None:
        return None
    scale = lcm(*(v.denominator for v in rows.values()))
    return {'dimensions': dimensions, 'positive': len(rows),
            'zero': None if dimensions is None else product_size(dimensions) - len(rows),
            'common_denominator': scale,
            'numerators': [[key, int(value * scale)] for key, value in rows.items()]}


def product_size(dimensions):
    count = 1
    for d in dimensions:
        count *= d
    return count


def private(rows, observer):
    local = Counter()
    for (ready, a, b), mass in rows.items():
        local[ready, (a, b)[observer]] += mass
    return local


def values(path, *, raw=False):
    return tuple(row[2 if raw else 3] for row in path)


def first_difference(first, second):
    if first == second:
        return None
    slots = max(len(path) for _, path in first.keys() | second.keys())
    for length in range(slots + 1):
        prefixes = [Counter() for _ in range(2)]
        for law, target in zip((first, second), prefixes, strict=True):
            for (ready, path), mass in law.items():
                target[ready, path[:length]] += mass
        a, b = prefixes
        if a != b:
            witness = min((k for k in a.keys() | b.keys() if a[k] != b[k]), key=repr)
            return dict(slot=length, prefix=witness, first_mass=a[witness], second_mass=b[witness],
                        prefix_tv=total_variation(a, b))
    raise AssertionError('different laws have identical complete prefixes')


def fixed_one(replay, seq, *, observer=0, **kwargs):
    commands = (tuple(seq), (None,) * len(seq))
    return replay.run(*commands[::1 if observer == 0 else -1], **kwargs)


def shared(holds, left, right):
    if any(type(h) is not int or not 0 <= h < len(holds) for h in (left, right)):
        return ()
    return tuple(sorted(set(holds[left]) & set(holds[right])))


def sharing_fields(holds, left, right):
    return {e: (holds[left].index(e), holds[right].index(e)) for e in shared(holds, left, right)}


def differences(holds, a, b, *, raw=False):
    y, z = a[2 if raw else 3], b[2 if raw else 3]
    if y is None or z is None:
        return ()
    return tuple(e for e, (i, j) in sharing_fields(holds, a[0], b[0]).items() if (y >> i ^ z >> j) & 1)
