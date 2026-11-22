"""Build the actual common word, orient physical instruments, and pay two growth cuts."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from random import Random
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = 'LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001B'
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
LAWS = ('parity', 'nae')


@cache
def archive():
    path = ROOT / 'experiments' / PRIOR / (PRIOR + '-E001_private_pulses') / 'physical.py'
    spec = spec_from_file_location('existing_private_pulse_grows', path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def mask(marks):
    return sum(1 << mark for mark in marks)


def read(word, marks):
    return ''.join(str((word >> mark) & 1) for mark in marks)


def allowed(count, size, law):
    return count % 2 == 0 if law == 'parity' else 0 < count < size


@dataclass(frozen=True)
class Device:
    source: int
    witness: int
    receiver: int
    offer: tuple
    stage: tuple
    receipt: tuple
    memory: tuple
    donor_bundle: tuple

    def orient(self, reverse):
        if not reverse:
            return self
        return Device(self.source, self.witness, self.receiver, self.offer[::-1], self.stage,
                      self.receipt[::-1], self.memory, self.donor_bundle)

    def rename(self, holders, names):
        def marks(row):
            return tuple(names[d] for d in row)
        return Device(holders[self.source], holders[self.witness], holders[self.receiver],
                      marks(self.offer), marks(self.stage), marks(self.receipt), marks(self.memory),
                      marks(self.donor_bundle))


def memberships(stars):
    owners = defaultdict(list)
    for h, row in enumerate(stars):
        for d in row:
            owners[d].append(h)
    return {d: tuple(h) for d, h in owners.items()}


def build(crossed):
    old = archive()
    p, edits = old.prepare(old.Case('shunted' if crossed else 'intact', (8,) if crossed else ()))
    stars = p.immutable()
    def shared(h, w):
        return tuple(sorted(set(stars[h]).intersection(stars[w])))
    devices = []
    for r, donor, peer, width in [('c8', 'h' if crossed else 'p', 'q', 3),
                                 ('u8', 'p' if crossed else 'h', 'k', 5)]:
        receiver, source = p.role_id[r], p.role_id[donor]
        witness = p.arc_witness[r, donor]
        memory_holder = p.arc_witness[peer, r]
        outgoing, incoming = shared(receiver, witness), shared(source, witness)
        previous = shared(receiver, memory_holder)
        assert len(incoming) == 9 and len(outgoing) == width and len(previous) >= 2
        assert set(stars[source]).isdisjoint(stars[receiver])
        devices.append(Device(source, witness, receiver, incoming[:3], incoming[3:5],
                              outgoing[:3], previous[:2], incoming))
    return stars, tuple(devices), p.role_id['p'], edits


def parity_solution(equations):
    basis = {}
    for row, target in equations:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (row, target)
                break
            other, rhs = basis[pivot]
            row, target = row ^ other, target ^ rhs
        else:
            if target:
                raise ValueError('no common parity refinement')
    result = 0
    for pivot, (row, target) in sorted(basis.items()):
        if ((result & row).bit_count() % 2) != target:
            result |= 1 << pivot
    return result


def common_word(starts, devices, law):
    pins = {}
    for device in devices:
        for row, values in [(device.offer, '100'), (device.stage, '10'),
                            (device.receipt, '100'), (device.memory, '10')]:
            for name, value in zip(row, values, strict=True):
                assert name not in pins
                pins[name] = int(value)
    equal = tuple(zip(devices[0].donor_bundle, devices[1].donor_bundle, strict=True))
    rows = set(tuple(sorted(star)) for stars in starts for star in stars)
    if law == 'parity':
        result = parity_solution([(mask(row), 0) for row in sorted(rows)] +
                                 [(mask(pair), 0) for pair in equal] +
                                 [(1 << name, value) for name, value in sorted(pins.items())])
    else:
        with Minisat22() as solver:
            for row in sorted(rows):
                solver.add_clause([d + 1 for d in row]); solver.add_clause([-d - 1 for d in row])
            for a, b in equal:
                solver.add_clause([-a - 1, b + 1]); solver.add_clause([a + 1, -b - 1])
            for name, value in sorted(pins.items()):
                solver.add_clause([name + 1 if value else -name - 1])
            if not solver.solve():
                raise ValueError('no common not-all-equal refinement')
            result = mask(d - 1 for d in solver.get_model() if d > 0)
    assert all(allowed((result & mask(row)).bit_count(), len(row), law) for row in rows)
    assert all(read(result, [a]) == read(result, [b]) for a, b in equal)
    assert all((result >> d & 1) == v for d, v in pins.items())
    return result


def grow(original, law):
    old = archive()
    reading = old.read_source(original)
    knot_checks = old.previous().certify_source(original, reading, law)
    stages = [original]
    cuts = []
    for age in (1, 2):
        stars, step = old.literal_cut(stages[-1], law, age)
        assert step['status'] == 'extend' and step['old_assignments_extend']
        cuts.append({k: step[k] for k in ('births', 'age', 'status', 'old_assignments_extend',
                                          'newborn_local_knot_checks')})
        stages.append(stars)
    return stages, cuts, knot_checks


def extend(word, cuts, law):
    for cut in cuts:
        for b in cut['births']:
            fresh = b['fresh_names']
            assert fresh and not word & mask(fresh)
            count = (word & mask(b['consumed_names'])).bit_count()
            if not allowed(count, len(b['consumed_names']) + len(fresh), law):
                word |= 1 << fresh[0]
    return word


def prepare_map(n, kind, rng):
    seq = list(range(n))
    if kind == 'reverse':
        seq.reverse()
    elif kind == 'shuffle':
        rng.shuffle(seq)
    return seq


def recoding(stars, kind):
    rng = Random(202611220305)
    holders = prepare_map(len(stars), kind, rng)
    names = prepare_map(max(max(row) for row in stars) + 1, kind, rng)
    other = [None] * len(holders)
    for h, row in enumerate(stars):
        other[holders[h]] = tuple(names[d] for d in row)
    return tuple(other), holders, names


def transform(word, names):
    return mask(names[d] for d in range(len(names)) if (word >> d) & 1)


def local_prefix(stages, word, device):
    row = stages[0][device.receiver]
    value_bank = read(word, row)
    records = []
    for stars in stages:
        owners = memberships(stars)
        # The receiver can recognize repeated unnamed coholders of its own marks.
        local_numbering = {}
        local = []
        for d in row:
            peers = tuple(h for h in owners[d] if h != device.receiver)
            local.append([local_numbering.setdefault(h, len(local_numbering)) for h in peers])
        sample = {'values': value_bank, 'coholders_at_each_own_mark': local}
        if not records or sample != records[-1]:
            records.append(sample)
    return records
