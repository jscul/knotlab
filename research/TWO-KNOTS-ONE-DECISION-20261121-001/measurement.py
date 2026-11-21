"""Compile named reversible changes and compute complete probabilities for local holding readings.

A local answer is an integer whose bit j refers to the j-th mark in the written holding.
A physical word is an integer in increasing physical mark-name order. All probabilities are exact.
This module accepts a local relation or a caller's own controls and never reads archived outcomes.
"""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product


def parity(value):
    return value.bit_count() & 1


def positions(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def law(holdings, kind="parity", odd=None):
    """Give the physical local word catalogues, using the slots in each holder's own order."""
    if kind not in ("parity", "nae", "not-all-equal"):
        raise ValueError("expected parity or ordinary not-all-equal")
    odd_holders = set() if odd is None else ({odd} if isinstance(odd, int) else set(odd))
    if kind != "parity" and odd_holders:
        raise ValueError("ordinary not-all-equal has no supplied odd polarity")
    return tuple(
        tuple(
            w
            for w in range(1 << len(h))
            if (parity(w) == (i in odd_holders) if kind == "parity" else 0 < w < (1 << len(h)) - 1)
        )
        for i, h in enumerate(holdings)
    )


class BinarySystem:
    """Highest-column pivots make zeroing natural-order free bits lexicographically minimal."""

    def __init__(self):
        self.equations = []
        self.by_equation = {}
        self.origins = []
        self.pivots = {}
        self.conflict = None

    def add(self, mask, target, origin, aliases=()):
        key = (mask, target)
        if key in self.by_equation:
            origins = self.origins[self.by_equation[key]]
            for item in (origin, *aliases):
                if item not in origins:
                    origins.append(item)
            return
        index = len(self.equations)
        self.by_equation[key] = index
        self.equations.append((mask, target, origin))
        self.origins.append(list(dict.fromkeys((origin, *aliases))))
        sources = 1 << index
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in self.pivots:
                self.pivots[pivot] = mask, target, sources
                return
            old, rhs, provenance = self.pivots[pivot]
            mask ^= old
            target ^= rhs
            sources ^= provenance
        if target and self.conflict is None:
            self.conflict = sources

    def solve(self):
        if self.conflict is not None:
            indices = tuple(positions(self.conflict))
            left, right = 0, 0
            for i in indices:
                left ^= self.equations[i][0]
                right ^= self.equations[i][1]
            assert (left, right) == (0, 1)
            return None, indices
        solution = 0
        for pivot, (row, rhs, _) in sorted(self.pivots.items()):
            if parity(row & solution) != rhs:
                solution |= 1 << pivot
        assert all(parity(row & solution) == rhs for row, rhs, _ in self.equations)
        return solution, ()


def independent_binary(values):
    basis = {}
    for value in values:
        while value:
            position = value.bit_length() - 1
            if position not in basis:
                basis[position] = value
                break
            value ^= basis[position]
    return tuple(basis[i] for i in sorted(basis))


def identity_rows(holds, permitted, labels):
    place = {e: i for i, e in enumerate(labels)}
    rows = []
    for h, (names, states) in enumerate(zip(holds, permitted, strict=True)):
        if not states:
            continue
        for local in range(1, 1 << len(names)):
            signs = {parity(local & w) for w in states}
            if len(signs) == 1:
                fields = tuple(names[j] for j in positions(local))
                lifted = sum(1 << place[e] for e in fields)
                rows.append((h, lifted, signs.pop()))
    return rows


def setup_equations(holds, labels, local_rows, endpoint):
    index = {e: i for i, e in enumerate(labels)}
    n = len(labels)

    # Column e's bit f is the physical mark toggled at f by a request for e.
    def direction(e, f):
        return 1 << (n * e + f)

    def sign(e):
        return 1 << (n * n + e)

    system = BinarySystem()
    normals = sorted({row for _, row, _ in local_rows})
    normal_origins = {
        row: tuple(("homogeneous_row_from", h, row, b) for h, local, b in local_rows if local == row)
        for row in normals
    }
    for i, e in enumerate(labels):
        system.add(direction(i, i), 0, ("involution", e))
        for row in normals:
            system.add(
                sum(direction(i, j) for j in positions(row)),
                0,
                ("preserve_carrier", e, row),
                normal_origins[row],
            )
    for h, names in enumerate(holds):
        for e, f in combinations(names, 2):
            i, j = index[e], index[f]
            system.add(direction(i, j) ^ direction(j, i), 0, ("compatible", h, e, f))
    for h, row, b in local_rows:
        places = tuple(positions(row))
        for f in range(n):
            system.add(sum(direction(e, f) for e in places), 0, ("product_returns", h, row, labels[f]))
        rhs = b
        for i in places:
            if (h, labels[i]) in endpoint:
                rhs ^= 1
        ordered = sum(sign(e) for e in places)
        ordered ^= sum(direction(e, f) for e, f in combinations(places, 2))
        system.add(ordered, rhs, ("ordered_sign", h, row, b))
    return system


@dataclass
class Device:
    holdings: tuple
    allowed: tuple
    marks: tuple
    identities: tuple
    carrier: tuple
    status: str
    reason: str
    flips: dict
    signs: dict
    reversed_occurrences: frozenset
    accepted_words: tuple
    affine_case: bool
    source_weight: Fraction
    attempts: tuple
    minimum_masks: tuple
    strict_failure: object

    @property
    def n(self):
        return len(self.marks)

    @property
    def diagonal(self):
        return not any(self.flips.values())

    def named_mask(self, value):
        return tuple(self.marks[i] for i in positions(value))

    def ordinary_output(self, h, word):
        index = {e: i for i, e in enumerate(self.marks)}
        return sum(
            (((word >> index[e]) & 1) ^ self.signs[e] ^ int((h, e) in self.reversed_occurrences)) << slot
            for slot, e in enumerate(self.holdings[h])
        )

    def raw_local_word(self, h, displayed):
        if displayed is None or h is None:
            return None
        return displayed ^ sum(
            1 << j for j, e in enumerate(self.holdings[h]) if (h, e) in self.reversed_occurrences
        )

    def certificate(self):
        owners = {e: [h for h, marks in enumerate(self.holdings) if e in marks] for e in self.marks}
        systems = []
        for attempt in self.attempts:
            selected = tuple(attempt["reversed_marks"])
            ends = frozenset((owners[e][-1], e) for e in selected)
            system = setup_equations(self.holdings, self.marks, self.identities, ends)
            rows = tuple(
                dict(row=i, coefficients=mask, rhs=b, origins=tuple(origins))
                for i, ((mask, b, _), origins) in enumerate(
                    zip(system.equations, system.origins, strict=True)
                )
            )
            systems.append(dict(reversed_marks=selected, rows=rows))
        return dict(
            status=self.status,
            reason=self.reason,
            physical_marks=self.marks,
            holdings=self.holdings,
            allowed=self.allowed,
            affine_constraints=self.identities,
            ordinary_homogeneous_words=self.carrier,
            local_flips={str(e): self.named_mask(d) for e, d in self.flips.items()},
            local_signs=self.signs,
            reversed_occurrences=sorted(self.reversed_occurrences),
            source_accepted_words=self.accepted_words,
            acceptance=str(self.source_weight),
            solver_attempts=self.attempts,
            deduplicated_equations_and_all_origins=systems,
            minimum_reversal_masks=self.minimum_masks,
            strict_failure=self.strict_failure,
        )


def compile_device(holdings, allowed, *, relaxed=False):
    """Strict shared operations, or the separately labelled minimum endpoint-reversal calibration."""
    holds = tuple(tuple(h) for h in holdings)
    permitted = tuple(tuple(sorted(set(a))) for a in allowed)
    if len(holds) != len(permitted) or any(len(set(h)) != len(h) for h in holds):
        raise ValueError("supply a distinct list of mark names and one relation for every holding")
    if any(not isinstance(e, int) for h in holds for e in h):
        raise ValueError("mark names must be integers")
    for h, states in zip(holds, permitted, strict=True):
        if any(w < 0 or w >= 1 << len(h) for w in states):
            raise ValueError("answer label outside its holder")
    names = tuple(sorted({e for h in holds for e in h}))
    n = len(names)
    rows = tuple(identity_rows(holds, permitted, names))
    normals = independent_binary(row for _, row, _ in rows)
    words = tuple(w for w in range(1 << n) if not any(parity(a & w) for a in normals))
    owners = {e: tuple(i for i, h in enumerate(holds) if e in h) for e in names}
    if any(len(hs) > 2 for hs in owners.values()) and relaxed:
        raise ValueError("endpoint-reversal gauge is defined for at most two occurrences")
    eligible = tuple(e for e in names if len(owners[e]) == 2)
    affine = all(
        len(a) == 1 << (len(h) - len(independent_binary(row for u, row, b in rows if u == i)))
        for i, (h, a) in enumerate(zip(holds, permitted, strict=True))
    )
    attempts = []
    first = None
    strict_failure = None
    found = []
    if all(permitted):
        for size in range(len(eligible) + 1 if relaxed else 1):
            for chosen in combinations(eligible, size):
                endpoints = frozenset((owners[e][-1], e) for e in chosen)
                eq = setup_equations(holds, names, rows, endpoints)
                solution, conflict = eq.solve()
                witness = tuple(
                    dict(
                        coefficients=eq.equations[j][0],
                        rhs=eq.equations[j][1],
                        origin=eq.equations[j][2],
                    )
                    for j in conflict
                )
                if not chosen and solution is None:
                    strict_failure = witness
                attempts.append(
                    dict(
                        reversed_marks=chosen,
                        solvable=solution is not None,
                        equations=len(eq.equations),
                        rank=len(eq.pivots),
                        contradiction_rows=conflict,
                    )
                )
                if solution is not None:
                    found.append(chosen)
                    if first is None:
                        first = (solution, endpoints)
            if first is not None:
                break
    base = dict(
        holdings=holds,
        allowed=permitted,
        marks=names,
        identities=rows,
        carrier=words,
        affine_case=affine,
        attempts=tuple(attempts),
        minimum_masks=tuple(found),
        strict_failure=strict_failure,
    )
    if first is None:
        return Device(
            **base,
            status="refused",
            reason="empty local relation" if not all(permitted) else "signed equation contradiction",
            flips={},
            signs={},
            reversed_occurrences=frozenset(),
            accepted_words=(),
            source_weight=Fraction(),
        )
    solution, endpoints = first
    flips = {e: (solution >> (n * i)) & ((1 << n) - 1) for i, e in enumerate(names)}
    signs = {e: (solution >> (n * n + i)) & 1 for i, e in enumerate(names)}
    device = Device(
        **base,
        status="ready",
        reason="",
        flips=flips,
        signs=signs,
        reversed_occurrences=endpoints,
        accepted_words=words,
        source_weight=Fraction(1),
    )
    if device.diagonal:
        device.accepted_words = tuple(
            w for w in words if all(device.ordinary_output(h, w) in a for h, a in enumerate(permitted))
        )
        device.source_weight = Fraction(len(device.accepted_words), len(words))
        if not device.accepted_words:
            device.status, device.reason = "refused", "no accepted source state"
    elif not affine:
        device.status, device.reason = (
            "unsupported",
            "non-diagonal, non-affine invariant closure requires a separate finite subspace implementation",
        )
        device.accepted_words = ()
        device.source_weight = None
    return device


@lru_cache(maxsize=131072)
def _canonical_generators(num_bits, supplied):
    """Row-reduce commuting signed permutations without dropping their product signs."""
    bare = (1 << (2 * num_bits)) - 1
    basis = {}
    for item in supplied:
        while item & bare:
            place = (item & bare).bit_length() - 1
            if place not in basis:
                basis[place] = item
                break
            item = _multiply(num_bits, item, basis[place])
        else:
            if item:
                raise ValueError("inconsistent signed stabilizers")
    for p, row in sorted(basis.items()):
        for q in basis:
            if q > p and basis[q] >> p & 1:
                basis[q] = _multiply(num_bits, basis[q], row)
    return tuple(basis[i] for i in sorted(basis))


def _multiply(k, left, right):
    """Apply right then left; the sign is read on the word after the first applied change."""
    low = (1 << k) - 1
    extra = parity((left >> k) & (right & low))
    return (left ^ right) ^ (extra << (2 * k))


def _anticommutes(k, left, right):
    low = (1 << k) - 1
    return parity(((left >> k) & (right & low)) ^ ((right >> k) & (left & low)))


@lru_cache(maxsize=131072)
def _project(k, state, observable):
    """Return each binary eigenvalue, probability (one or one half) and conditional mixed state."""
    extra = 1 << (2 * k)
    bare = extra - 1
    offenders = [g for g in state if _anticommutes(k, g, observable)]
    if offenders:
        pivot = offenders[0]
        kept = tuple(_multiply(k, g, pivot) if g in offenders else g for g in state if g != pivot)
    else:
        remainder = observable
        for g in reversed(state):
            pos = (g & bare).bit_length() - 1
            if remainder >> pos & 1:
                remainder = _multiply(k, remainder, g)
        if not remainder & bare:
            return ((int(bool(remainder & extra)), Fraction(1), state),)
        kept = state
    return tuple(
        (bit, Fraction(1, 2), _canonical_generators(k, kept + (observable ^ (bit * extra),)))
        for bit in (0, 1)
    )


@dataclass(frozen=True)
class WordState:
    """Linked or independent diagonal support. The masks retain coherent diagonal phases when needed."""

    left: int
    right: int
    linked: bool
    left_phase: int = 0
    right_phase: int = 0


@dataclass(frozen=True)
class MissingState:
    reason: str


@dataclass(frozen=True)
class LocalRecord:
    request: object
    status: str
    raw_word: object
    displayed_word: object
    branch_tag: object
    latch_words: tuple
    fired_pairs: tuple


READY, ZERO, ONE = 0b110, 0b101, 0b011


def latch_write(bit):
    """The three entries use the displayed left-to-right ternary names (0,1,2)."""
    final = ONE if bit else ZERO
    swapped = tuple(2 - i for i in reversed(tuple(positions(READY ^ final))))
    return final, swapped


class QuantumReader:
    """Exact local sequences. The two role restrictions are set by the calling experiment.

    initial() includes every preparation failure. start() is the state on a heralded success,
    or the actual no-source record if setup never succeeds. A None request means idle.
    step() matches LiteralReader.step(). step_detailed() adds the physically available registers.
    """

    def __init__(
        self,
        device,
        source="coherent",
        *,
        tag=(False, False),
        writer=("write", "write"),
        roles=None,
        force_refusal=False,
    ):
        self.device = device
        self.source = source
        if source not in ("coherent", "dephased", "independent", "ordinary"):
            raise ValueError("unknown preparation")
        if device.status == "unsupported":
            raise NotImplementedError(device.reason)
        if source == "ordinary" and not device.diagonal and device.status == "ready":
            raise ValueError("the ordinary scalar control requires diagonal operators")
        if (
            len(tag) != 2
            or len(writer) != 2
            or any(w not in ("write", "not_ready", "disconnected") for w in writer)
        ):
            raise ValueError("supply two local tag and writing policies")
        tag_names = {
            False: "none",
            True: "held",
            "none": "none",
            "held": "held",
            "ignored": "ignored",
            "uncomputed": "uncomputed",
        }
        self.tag = tuple(tag_names[mode] for mode in tag)
        self.writer = tuple(writer)
        self.force_refusal = force_refusal
        self.roles = None if roles is None else tuple(frozenset(v) for v in roles)
        self.acceptance = (
            Fraction(1) if source == "ordinary" and device.status == "ready" else device.source_weight
        )
        if force_refusal:
            self.acceptance = Fraction()
        self.index = {e: i for i, e in enumerate(device.marks)}
        self.allowed_mask = sum(1 << w for w in device.accepted_words)
        self._mark_ones = {}
        if device.diagonal and device.status == "ready":
            for i, e in enumerate(device.marks):
                self._mark_ones[e] = sum(1 << w for w in device.accepted_words if w >> i & 1)

    def start(self):
        d = self.device
        if not self.acceptance:
            return MissingState(d.reason or "preparation refused")
        if d.diagonal:
            return WordState(self.allowed_mask, self.allowed_mask, self.source != "independent")
        n = d.n
        k = 2 * n
        generators = []
        row_basis = independent_binary(row for _, row, _ in d.identities)
        if self.source == "independent":
            for c in row_basis:
                generators.extend((c << k, (c << n) << k))
        else:
            for i in range(n):
                generators.append(((1 << i) | (1 << (n + i))) << k)
            for c in row_basis:
                generators.append(c << k)
            if self.source == "coherent":
                for v in independent_binary(d.carrier):
                    generators.append(v | (v << n))
        return _canonical_generators(k, tuple(generators))

    def initial(self):
        weight = self.acceptance
        if weight:
            yield weight, self.start()
        if weight != 1:
            yield 1 - weight, MissingState(self.device.reason or "intake rejected")

    def _operator(self, wing, h, j):
        d = self.device
        e = d.holdings[h][j]
        offset = wing * d.n
        k = 2 * d.n
        sign = d.signs[e]
        return (d.flips[e] << offset) | (1 << (k + offset + self.index[e])) | (sign << (2 * k))

    def _one_mark(self, state, wing, h, j, tag):
        d = self.device
        e = d.holdings[h][j]
        if isinstance(state, WordState):
            if tag:
                for b, bit in product((0, 1), repeat=2):
                    if b and self.source == "coherent":
                        # The sign of the marked Z changes relative phases, even though all future reads here are diagonal.
                        phase = 1 << self.index[e]
                        updated = WordState(
                            state.left,
                            state.right,
                            state.linked,
                            state.left_phase ^ (phase if wing == 0 else 0),
                            state.right_phase ^ (phase if wing == 1 else 0),
                        )
                    else:
                        updated = state
                    yield bit, b, Fraction(1, 4), updated
                return
            current = state.right if wing else state.left
            negate = d.signs[e]
            for bit in (0, 1):
                ones = self._mark_ones[e]
                rest = current & (ones if bit ^ negate else ~ones)
                if not rest:
                    continue
                left = rest if state.linked or wing == 0 else state.left
                right = rest if state.linked or wing == 1 else state.right
                yield (
                    bit,
                    None,
                    Fraction(rest.bit_count(), current.bit_count()),
                    WordState(left, right, state.linked, state.left_phase, state.right_phase),
                )
            return
        k = 2 * d.n
        obs = self._operator(wing, h, j)
        if tag:
            for b in (0, 1):
                changed = tuple(g ^ (int(b and _anticommutes(k, g, obs)) << (2 * k)) for g in state)
                for bit in (0, 1):
                    yield bit, b, Fraction(1, 4), changed
        else:
            for bit, prob, updated in _project(k, state, obs):
                yield bit, None, prob, updated

    def _status(self, state, wing, h):
        if h is None:
            return "idle"
        if not isinstance(h, int) or not 0 <= h < len(self.device.holdings):
            return "invalid"
        if self.roles is not None and h not in self.roles[wing]:
            return "out_of_role"
        if isinstance(state, MissingState):
            return "no_source"
        if self.writer[wing] == "not_ready":
            return "not_ready"
        return self.writer[wing]

    def _one_holder(self, state, wing, h):
        status = self._status(state, wing, h)
        if status not in ("write", "disconnected"):
            yield None, None, Fraction(1), state, status
            return
        active = [(0, None, Fraction(1), state)]
        for j in range(len(self.device.holdings[h])):
            next_rows = []
            for word, tag_before, p, before in active:
                for bit, tag, weight, after in self._one_mark(
                    before, wing, h, j, j == 0 and self.tag[wing] in ("held", "ignored")
                ):
                    if self.tag[wing] == "ignored":
                        tag = None
                    e = self.device.holdings[h][j]
                    displayed = bit ^ int((h, e) in self.device.reversed_occurrences)
                    next_rows.append(
                        (word | (displayed << j), tag if j == 0 else tag_before, p * weight, after)
                    )
            active = next_rows
        for word, tag, prob, after in active:
            yield (None if status == "disconnected" else word), tag, prob, after, status

    def _record(self, h, word, tag, status):
        defined = isinstance(h, int) and 0 <= h < len(self.device.holdings)
        fields = len(self.device.holdings[h]) if defined else 0
        if word is None:
            return LocalRecord(h, status, None, None, tag, (READY,) * fields, ())
        values = [latch_write((word >> j) & 1) for j in range(fields)]
        return LocalRecord(
            h,
            "success",
            self.device.raw_local_word(h, word),
            word,
            tag,
            tuple(v for v, swap in values),
            tuple((j, swap) for j, (v, swap) in enumerate(values)),
        )

    def physical_fields(self, record, wing):
        """Expand the lossless private code to ordinary named register words, including a failed request."""
        h = record.request
        offered = (
            tuple(range(len(self.device.holdings)))
            if self.roles is None
            else tuple(sorted(self.roles[wing]))
        )
        requested = h is not None
        fresh = record.status == "success"
        raw_latches = (
            ()
            if record.raw_word is None
            else tuple(
                latch_write((record.raw_word >> j) & 1)[0] for j in range(len(self.device.holdings[h]))
            )
        )
        calibration = (
            ()
            if not isinstance(h, int) or h not in offered
            else tuple(int((h, e) in self.device.reversed_occurrences) for e in self.device.holdings[h])
        )
        return dict(
            wing=wing,
            local_address=h,
            address_bank=tuple((j, ONE if j == h else ZERO) for j in offered),
            attempted=ONE if requested else ZERO,
            end_of_slot=ONE,
            local_status=record.status,
            physical_write=ONE if fresh else ZERO,
            displayed_bit_holders=record.latch_words,
            actual_written_place_pairs=record.fired_pairs,
            measured_raw_holder_words=raw_latches,
            local_calibrations=calibration,
            before_mixing_tag_policy=self.tag[wing],
            readable_tag_holder=READY
            if record.branch_tag is None
            else latch_write(record.branch_tag)[0],
            disconnected_auxiliary="unread after the projection"
            if record.status == "disconnected"
            else None,
        )

    def step_detailed(self, state, left, right):
        for y, t, p, half, ls in self._one_holder(state, 0, left):
            for z, u, q, after, rs in self._one_holder(half, 1, right):
                yield self._record(left, y, t, ls), self._record(right, z, u, rs), p * q, after

    def step(self, state, left, right):
        for y, t, p, half, ls in self._one_holder(state, 0, left):
            for z, u, q, after, rs in self._one_holder(half, 1, right):
                yield y, z, p * q, after


def trace_probability(reader, left, right, *, on_success=False):
    """Each side is an iterable of (request, observed_answer); idle/missing is None."""
    left, right = tuple(left), tuple(right)
    if len(left) != len(right):
        raise ValueError("the local slot lists differ in length")
    if on_success and not reader.acceptance:
        return None
    rows = (
        Counter({reader.start(): Fraction(1)})
        if on_success
        else Counter({s: p for p, s in reader.initial()})
    )
    for (h, y), (k, z) in zip(left, right, strict=True):
        next_rows = Counter()
        for state, p in rows.items():
            for a, b, q, after in reader.step(state, h, k):
                if (a, b) == (y, z):
                    next_rows[after] += p * q
        rows = next_rows
    return sum(rows.values(), Fraction())


def joint_table(reader, h, k, *, on_success=False):
    """Sparse positive entries on local displayed answers; use zero for all unlisted cells."""
    if on_success and not reader.acceptance:
        return None
    out = Counter()
    initial = ((Fraction(1), reader.start()),) if on_success else reader.initial()
    for prior, state in initial:
        for a, b, p, after in reader.step(state, h, k):
            out[(a, b)] += prior * p
    assert sum(out.values()) == 1
    return out


def check_returned_operations(device):
    """Multiply on actual named words before comparing to the structural equations."""
    if device.status != "ready":
        left = right = 0
        for row in device.strict_failure or ():
            left ^= row["coefficients"]
            right ^= row["rhs"]
        return dict(
            reason=device.reason,
            signed_contradiction=bool(device.strict_failure) and (left, right) == (0, 1),
            contradiction_row_count=len(device.strict_failure or ()),
            contradiction=device.strict_failure,
        )
    position = {e: i for i, e in enumerate(device.marks)}
    carriers = set(device.carrier)
    counts = Counter()

    def sequence(w, ordered, context=None):
        sign = 0
        for e in ordered:
            sign ^= (w >> position[e]) & 1
            sign ^= device.signs[e]
            sign ^= int((context, e) in device.reversed_occurrences)
            w ^= device.flips[e]
            assert w in carriers
        return w, sign

    for w in device.carrier:
        for e in device.marks:
            assert sequence(w, (e, e)) == (w, 0)
            counts["involutions"] += 1
        for h, marks in enumerate(device.holdings):
            for e, f in combinations(marks, 2):
                assert sequence(w, (e, f), h) == sequence(w, (f, e), h)
                counts["same_holder_commutations"] += 1
        for h, row, b in device.identities:
            assert sequence(w, device.named_mask(row), h) == (w, b)
            counts["signed_products"] += 1
    return dict(counts, carrier_words=len(device.carrier), accepted_words=len(device.accepted_words))


def pointer_and_growth_checks():
    from pathlib import Path
    import gzip, json, os, subprocess, sys

    root = Path(__file__).resolve().parents[2]
    canonical = {}
    for name, cnf in (
        ("parity", "a b -c; a -b c; -a b c; -a -b -c"),
        ("not_all_equal", "a b c; -a -b -c"),
    ):
        config = [
            sys.executable,
            "-B",
            "-m",
            "knotlab",
            "check",
            "--cnf",
            cnf,
            "--loops",
            "a",
            "b",
            "--contact",
            "c",
            "--json",
        ]
        raw = json.loads(
            subprocess.check_output(
                config, cwd=root, env={**os.environ, "PYTHONPATH": str(root / "tools")}
            )
        )
        assert raw["binding"] and raw["invisible_in_parts"] and raw["coexistence"]
        assert all(format(w, "03b") in raw["allowed"] for w in (READY, ZERO, ONE))
        canonical[name] = raw["allowed"]
    write = {}
    for bit in (0, 1):
        record, pair = latch_write(bit)
        toggled = READY ^ sum(1 << (2 - j) for j in pair)
        assert toggled == record and all(format(record, "03b") in words for words in canonical.values())
        write[bit] = dict(ready=format(READY, "03b"), fired_places=pair, new=format(record, "03b"))
    # Actual funded pair 0 and 2 share neighbour 1. Two different allowed valuations are never
    # parameters to the pre-existing paid growth rule. Rerun it for every allowed word.
    previous = "NAE-GROWTH-20261119-001B"
    sys.path.insert(0, str(root / "experiments" / previous / (previous + "-E001_nae")))
    import naelib

    source = ((0, 2, 3), (0, 1, 4), (1, 5, 6))
    signature = {}
    for kind in ("parity", "nae"):
        valid = law(source, kind)
        ordinary = [
            w
            for w in range(128)
            if all(
                sum(((w >> e) & 1) << j for j, e in enumerate(h)) in rel
                for h, rel in zip(source, valid, strict=True)
            )
        ]
        distinct = {}
        for word in ordinary:
            state = naelib.J.S.from_junctions(source)
            groups = state.groups_among(state.live)
            native_rule = (naelib.parity_rule if kind == "parity" else naelib.nae_rule)(naelib.F.fewest)
            step = state.step(native_rule, None)
            assert step is not None
            raw = tuple(
                dict(
                    child=i,
                    paying_parents=tuple(
                        next(k for k in state.owner[b] if k < i)
                        for b in state.bits_of[i][: state.parents[i]]
                    ),
                    paid_distinctions=tuple(state.bits_of[i][: state.parents[i]]),
                    fresh_names=tuple(state.bits_of[i][state.parents[i] :]),
                    grant=state.fresh[i],
                )
                for i in range(3, len(state.bits_of))
            )
            distinct[word] = raw
            assert frozenset((0, 2)) in [frozenset(g) for g in groups]
        assert len({repr(v) for v in distinct.values()}) == 1
        signature[kind] = dict(
            ordinary_words=ordinary,
            identical_funded_table=next(iter(distinct.values())),
            distinct_native_outcomes=1,
        )
    prior = "JOINT-PARENTS-AND-ERASURE-20261120-001B"
    archive = root / "artifacts" / prior / (prior + "-E001_erasure") / "physical.json.gz"
    raw = json.loads(gzip.decompress(archive.read_bytes()))

    # Resolve the already-published physical guards by structure, then recompute their two records.
    def find_guards(value):
        if not isinstance(value, dict):
            return None
        if {
            "actual_loose_distinctions",
            "guarded_control_distinction",
            "laws",
            "named_input_pair",
        } <= value.keys():
            return value
        for item in value.values():
            result = find_guards(item)
            if result is not None:
                return result

    control = find_guards(raw)
    assert control is not None
    words = control["named_input_pair"]
    mark = control["guarded_control_distinction"]
    a, b = control["actual_loose_distinctions"]
    guards = []
    for w in words:
        fired = bool((w >> mark) & 1)
        new = w ^ ((1 << a) | (1 << b)) if fired else w
        guards.append(
            dict(
                old_word=w, actual_guard=fired, actual_event_marks=(a, b) if fired else (), new_word=new
            )
        )
    assert (
        guards[0]["actual_guard"] != guards[1]["actual_guard"]
        and len({row["new_word"] for row in guards}) == 1
    )
    switch = "SHARED-DONOR-AND-SIGN-RESPONSE-20261121-001B"
    swfile = root / "artifacts" / switch / (switch + "-E001_later_rejoin") / "physical.json.gz"
    recorded = json.loads(gzip.decompress(swfile.read_bytes()))["altered_keeper_attachment"][
        "original_and_augmented_control_comparison"
    ]
    assert recorded["readable_native_trigger_count"] == 0 and recorded["exact_tests"] == 3960
    return dict(
        canonical_ternary=canonical,
        latch_writes=write,
        physical_funded_pair_source=source,
        funded_births_at_all_values=signature,
        actual_native_guard_control=guards,
        unchanged_keeper_no_trigger=recorded["readable_native_trigger_count"],
    )


def auxiliary_circuit_check(device, e):
    """Mix the binary auxiliary, change the data, physically toggle a route flag, mix and inspect."""
    d = device.flips[e]
    assert d and not d >> device.marks.index(e) & 1
    results = {}
    for relative in (1, -1):
        original = {0: 1, d: relative}
        by_method = {}
        for method in ("clean", "held", "uncomputed"):
            amplitudes = Counter()
            for w, p in original.items():
                for branch in (0, 1):
                    bit = ((w >> device.marks.index(e)) & 1) ^ device.signs[e]
                    changed = w ^ (d if branch else 0)
                    amplitude = p * (-1 if branch and bit else 1)
                    tag = 0
                    if method in ("held", "uncomputed"):
                        tag ^= branch
                    if method == "uncomputed":
                        tag ^= branch
                    for answer in (0, 1):
                        amplitudes[answer, tag, changed] += amplitude * (-1 if answer and branch else 1)
            denominator = 4 * sum(p * p for p in original.values())
            states = {
                (a, t): {w: c for (res, tag, w), c in amplitudes.items() if res == a and tag == t and c}
                for a, t in product((0, 1), repeat=2)
            }
            probabilities = {
                f"{a}/{t}": str(Fraction(sum(v * v for v in state.values()), denominator))
                for (a, t), state in states.items()
            }
            assert sum(map(Fraction, probabilities.values())) == 1
            by_method[method] = dict(
                denominator=denominator,
                post_data_by_answer_and_tag={f"{a}/{t}": state for (a, t), state in states.items()},
                probabilities=probabilities,
            )
        assert by_method["clean"] == by_method["uncomputed"]
        assert set(by_method["held"]["probabilities"].values()) == {"1/4"}
        results[str(relative)] = by_method
    return dict(physical_mark=e, data_change_mask=d, crossed_inputs=results)


def shared_checks():
    duplicate_holding = ((0, 1, 2), (0, 1, 2))
    opposed = compile_device(duplicate_holding, law(duplicate_holding, "parity", 1))
    duplicate_rows = opposed.certificate()["deduplicated_equations_and_all_origins"][0]["rows"]
    assert len({(row["coefficients"], row["rhs"]) for row in duplicate_rows}) == len(duplicate_rows)
    multiple = [row for row in duplicate_rows if len(row["origins"]) > 1]
    assert any(
        {v[1] for v in q["origins"] if v[0] == "homogeneous_row_from"} == {0, 1} for q in multiple
    )
    assert any(len([v for v in q["origins"] if v[0] == "compatible"]) == 2 for q in multiple)
    square = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8))
    eight = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (3, 5, 7), (2, 8, 9), (4, 8, 10), (6, 9, 11), (7, 10, 11))
    pair = ((0, 1, 2), (0, 3, 4))
    benches = {}
    for label, hs in (("six", square), ("eight", eight), ("lawful_two", pair)):
        cases = {}
        setups = [("even", "parity", None, False), ("nae", "nae", None, False)]
        if label != "lawful_two":
            setups.extend(
                (
                    ("strict", "parity", len(hs) - 1, False),
                    ("changed_display", "parity", len(hs) - 1, True),
                )
            )
        for name, kind, odd, relaxed in setups:
            device = compile_device(hs, law(hs, kind, odd), relaxed=relaxed)
            quantities = check_returned_operations(device)
            if device.status == "ready":
                reader = QuantumReader(device)
                ordinary = QuantumReader(device, source="ordinary") if device.diagonal else None
                first, second = 0, (3 if label == "six" else 1)
                tab = joint_table(reader, first, second)
                quantities.update(
                    on_launch_herald=str(reader.acceptance),
                    source_weight=str(device.source_weight),
                    ordinary_direct_acceptance=str(ordinary.acceptance) if ordinary else None,
                    tested_input=(first, second),
                    number_positive_displayed_events=len(tab),
                )
                for wing in (0, 1):
                    admitted = QuantumReader(device, roles=((0,), (1,)))
                    for state_prob, state in admitted.initial():
                        request = [None, None]
                        request[wing] = 1 - wing
                        for left, right, weight, _ in admitted.step_detailed(state, *request):
                            local = (left, right)[wing]
                            assert local.status == "out_of_role" and all(
                                w == READY for w in local.latch_words
                            )
                stamp = tuple(device.flips.values())
                quantities.update(
                    flip_masks=stamp,
                    signs=tuple(device.signs.values()),
                    calibrated_occurrences=sorted(device.reversed_occurrences),
                )
            cases[name] = quantities
        benches[label] = cases
    example = compile_device(square, law(square, "parity", 5))
    primary = QuantumReader(example)
    writing = {}
    for status in ("not_ready", "disconnected", "write"):
        middle = QuantumReader(example, writer=(status, "write"))
        same = Fraction()
        mid_received = Counter()
        for a, _, p, sa in primary.step(primary.start(), 0, None):
            for b, _, q, sb in middle.step(sa, 1, None):
                mid_received[b] += p * q
                for c, _, v, sc in primary.step(sb, 0, None):
                    if a == c:
                        same += p * q * v
        writing[status] = dict(
            full_original_word_repeated=str(same),
            middle_delivered_chance=str(1 - mid_received.get(None, 0)),
        )
    assert writing["not_ready"]["full_original_word_repeated"] == "1"
    assert (
        writing["disconnected"]["full_original_word_repeated"]
        == writing["write"]["full_original_word_repeated"]
        == "1/4"
    )
    tag_stats = {}
    for mode in ("none", "held", "ignored", "uncomputed"):
        observed = QuantumReader(example, tag=(mode, False))
        joint = Counter()
        for x, y, p, _ in observed.step_detailed(observed.start(), 0, 3):
            joint[x.branch_tag, x.displayed_word, y.displayed_word] += p
        tag_stats[mode] = dict(
            legal_local_and_agree=str(
                sum(
                    p
                    for (tag, a, b), p in joint.items()
                    if a in example.allowed[0] and b in example.allowed[3] and a & 1 == b & 1
                )
            ),
            readable_tag_chances={
                str(v): str(sum(p for (tag, a, b), p in joint.items() if tag == v)) for v in (None, 0, 1)
            },
        )
    assert tag_stats["none"] == tag_stats["uncomputed"]
    assert (
        tag_stats["held"]["legal_local_and_agree"]
        == tag_stats["ignored"]["legal_local_and_agree"]
        == "1/2"
    )
    from dataclasses import replace

    mutations = {}
    for name, mutant in (
        ("toggle_calibrated_sign", replace(example, signs={**example.signs, 8: example.signs[8] ^ 1})),
        (
            "toggle_currently_read_mark",
            replace(example, flips={**example.flips, 0: example.flips[0] ^ 1}),
        ),
    ):
        try:
            check_returned_operations(mutant)
        except AssertionError:
            mutations[name] = "rejected on literal word actions"
        else:
            raise AssertionError(f"material mutation passed: {name}")
    return dict(
        provenance_control=dict(
            unique_equations=len(duplicate_rows),
            multiple_origin_rows=len(multiple),
            repeated_holders=duplicate_holding,
            retained_origin_map=duplicate_rows,
        ),
        structural_and_latch_controls=pointer_and_growth_checks(),
        devices=benches,
        six_repeat_control_0_1_0=writing,
        matched_which_branch_on_six_0_3=tag_stats,
        auxiliary_circuit=auxiliary_circuit_check(example, 3),
        wrong_source_controls=mutations,
    )


def main():
    import argparse, json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="recompute the common part of the proof receipt"
    )
    args = parser.parse_args()
    if not args.check:
        parser.print_help()
        return
    home = Path(__file__).resolve().parent
    ticket = home.name + "P"
    proof = home.parents[1] / "proofs" / ticket / (ticket + "-P001_measurement") / "result.json"
    calculated = json.loads(json.dumps(shared_checks(), sort_keys=True))
    if calculated != json.loads(proof.read_text())["common_checks"]:
        raise SystemExit("common physical or signed-measurement checks differ from the proof result")
    print(
        "Signed changes, physical ternary records, native births and refused preparations reproduce exactly."
    )


if __name__ == "__main__":
    main()
