"""Enumerate exact complete local reports along fixed or adaptive request histories."""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import lcm
from typing import NamedTuple

from literal_read import first_difference, total_variation
from measurement import MissingState, latch_write


class Record(NamedTuple):
    holder: int | None
    status: str
    raw: int | None
    answer: int | None
    tag: int | None


def full_record(holdings, record):
    holder, status, raw, answer, tag = record
    valid = isinstance(holder, int) and 0 <= holder < len(holdings)
    marks = holdings[holder] if valid else ()
    writes = [] if answer is None else [latch_write(answer >> i & 1) for i in range(len(marks))]
    raw_writes = [] if raw is None else [latch_write(raw >> i & 1) for i in range(len(marks))]
    flips = [] if raw is None else [(i, (0, 1)) for i in range(len(marks)) if (raw ^ answer) >> i & 1]
    tag_write = latch_write(tag) if tag is not None else None
    return dict(
        address=holder, named_marks=marks, local_request_receipt=holder is not None,
        clock_mark="preset local end-of-slot",
        status=status, raw_mask=raw, recorded_mask=answer, pre_branch_tag=tag,
        measured_auxiliary_completed=status in ("success", "disconnected"),
        recorded_answer_completed=answer is not None,
        ready_word="110", answer_words=[f"{word:03b}" for word, _ in writes] if writes else ["110"] * len(marks),
        raw_auxiliary_words=[f"{word:03b}" for word, _ in raw_writes],
        raw_exit_write_pairs=[(i, pair) for i, (_, pair) in enumerate(raw_writes)],
        calibration_auxiliary_exchange_pairs=flips,
        fired_answer_pairs=[(i, pair) for i, (_, pair) in enumerate(writes)],
        tag_word=f"{tag_write[0]:03b}" if tag_write else None,
        fired_tag_pair=tag_write[1] if tag_write else None,
        local_sequence={
            "success": ["request", "address", "read", "detect", "write", "end"],
            "disconnected": ["request", "address", "read", "detect", "missed-write", "end"],
            "not_ready": ["request", "address", "keeper-admission-refusal", "end"],
            "no_source": ["request", "address", "source-refusal", "end"],
            "invalid": ["request", "address-refusal", "end"],
            "invalid_address": ["request", "address-refusal", "end"],
            "out_of_role": ["request", "out-of-role-refusal", "end"],
            "no_eligible_union": ["request", "central controller refusal delivered", "end"],
            "idle": [],
        }[status],
        keeper_snapshot="append the new answer and its fixed receipt only on success; existing answers remain",
    )


class Engine:
    def __init__(self, reader, holdings, allowed, *, literal=False):
        self.reader = reader
        self.holdings = holdings
        self.allowed = allowed
        self.literal = literal
        self.acceptance = Fraction(1) if literal else reader.acceptance
        if literal:
            self.launches = ((Fraction(1), reader.start()),)
        else:
            self.launches = tuple(reader.initial())
        self.transitions = lru_cache(maxsize=4096)(self._transitions)

    def preparation(self, state):
        if self.literal:
            return "central controller ready"
        return "refused" if isinstance(state, MissingState) else "ready"

    def _transitions(self, state, left, right):
        if self.literal:
            return tuple((Record(left, self.reader.readout(left, a).status, a, a, None),
                          Record(right, self.reader.readout(right, b).status, b, b, None), mass, after)
                         for a, b, mass, after in self.reader.step(state, left, right))
        out = []
        for a, b, mass, after in self.reader.step_detailed(state, left, right):
            converted = tuple(Record(record.request, record.status, record.raw_word,
                                     record.displayed_word, record.branch_tag) for record in (a, b))
            out.append((*converted, mass, after))
        return tuple(out)

    def distribution(self, left, right, *, slots=None, accepted=False):
        """Map public pre-question herald and both histories to probability."""
        n = slots if slots is not None else len(left)
        initial = ((Fraction(1), self.reader.start()),) if accepted and self.acceptance else self.launches
        if accepted and not self.acceptance:
            return None
        frontier = {(self.preparation(state), (), (), state): mass for mass, state in initial}
        for i in range(n):
            updated = Counter()
            for (herald, a, b, state), mass in frontier.items():
                h = left(i, a) if callable(left) else left[i]
                k = right(i, b) if callable(right) else right[i]
                for ar, br, pm, after in self.transitions(state, h, k):
                    updated[herald, a + (ar,), b + (br,), after] += mass * pm
            frontier = updated
        reduced = Counter()
        for (herald, a, b, _state), mass in frontier.items():
            reduced[herald, a, b] += mass
        assert sum(reduced.values()) == 1
        return reduced


class RecordCodes:
    def __init__(self):
        self._codes = {}

    def encode(self, record):
        if record not in self._codes:
            self._codes[record] = len(self._codes)
        return self._codes[record]

    def codebook(self, holdings):
        return [full_record(holdings, record) for record in self._codes]

    def pack(self, distribution):
        if distribution is None:
            return None
        denominator = lcm(*(mass.denominator for mass in distribution.values()))
        return {"denominator": denominator,
                "digits": [[herald, [self.encode(r) for r in left], [self.encode(r) for r in right],
                            int(mass * denominator)] for (herald, left, right), mass in distribution.items()]}

    def pack_private(self, private_law):
        denominator = lcm(*(mass.denominator for mass in private_law.values()))
        return {"denominator": denominator,
                "digits": [[herald, [self.encode(r) for r in records], int(mass * denominator)]
                           for (herald, *records), mass in private_law.items()]}


def marginal(distribution, observer):
    """The common pre-setting herald is an observed prefix of each full transcript."""
    view = Counter()
    for (herald, left, right), mass in distribution.items():
        view[(herald,) + (left if observer == 0 else right)] += mass
    return view


def first_visible(first, second):
    witness = first_difference(first, second)
    if witness is not None:
        # The pre-setting herald occupies index zero before either request slot.
        witness["slot"] -= 1
    return witness


def displayed_table(distribution):
    if distribution is None:
        return None
    fail = 8
    view = Counter()
    for (_herald, left, right), mass in distribution.items():
        view[(left[0].answer if left[0].answer is not None else fail,
              right[0].answer if right[0].answer is not None else fail)] += mass
    denominator = lcm(*(mass.denominator for mass in view.values()))
    return dict(denominator=denominator, cells=[[a, b, int(weight * denominator)]
                                               for (a, b), weight in sorted(view.items())],
                ordinary_zero_cells=64 - sum(a < fail and b < fail for a, b in view),
                all_zero_cells=81 - len(view))


def bits(holdings, readout, raw=False):
    if readout.answer is None or readout.holder is None:
        return {}
    word = readout.raw if raw else readout.answer
    return {e: word >> i & 1 for i, e in enumerate(holdings[readout.holder])}


def differences(holdings, x, y, raw=False):
    a, b = bits(holdings, x, raw), bits(holdings, y, raw)
    return tuple(sorted(e for e in a.keys() & b.keys() if a[e] != b[e]))


def branch_metrics(engine, distribution):
    metrics = Counter()
    for (_herald, a, b), p in distribution.items():
        for i, records in enumerate((a, b)):
            for record in records:
                metrics[(i, record.status)] += p
                if record.answer is not None and record.answer not in engine.allowed[record.holder]:
                    metrics[(i, "wrong_word")] += p
            for old, new in zip(records, records[1:]):
                if old.holder == new.holder and old.answer is not None and new.answer is not None:
                    metrics[(i, "immediate_repeat_flips")] += p * len(differences(engine.holdings, old, new))
        for slot, (ar, br) in enumerate(zip(a, b)):
            metrics[(slot, "mismatch")] += p * len(differences(engine.holdings, ar, br))
            metrics[(slot, "raw_mismatch")] += p * len(differences(engine.holdings, ar, br, raw=True))
    return {f"{i}/{label}": str(count) for (i, label), count in metrics.items()}


def sweep(engine, roles, observer, order):
    local = roles[observer][::order]
    far = roles[1-observer][::order]
    count = len(local)
    columns, laws = [], []
    for fixed in far:
        policies = (local, (fixed,) * count)
        full = engine.distribution(*(policies if observer == 0 else policies[::-1]))
        law = marginal(full, observer)
        laws.append(law)
        score, failures_per_slot = Counter(), [Counter() for _ in local]
        for (_, first, second), p in full.items():
            a, b = (first, second) if observer == 0 else (second, first)
            missing_a = any(r.answer is None for r in a)
            missing_b = any(r.answer is None for r in b)
            illegal_a = any(r.answer is not None and r.answer not in engine.allowed[r.holder] for r in a)
            illegal_b = any(r.answer is not None and r.answer not in engine.allowed[r.holder] for r in b)
            unstable = any(x.answer is not None and y.answer is not None and x.answer != y.answer
                           for x, y in zip(b, b[1:]))
            mismatch = [differences(engine.holdings, x, y) for x, y in zip(a, b)]
            mismatch_count = sum(map(len, mismatch))
            for slot, (x, y, diff) in enumerate(zip(a, b, mismatch)):
                failures_per_slot[slot]["missing_a"] += p * (x.answer is None)
                failures_per_slot[slot]["missing_b"] += p * (y.answer is None)
                failures_per_slot[slot]["unstable_b"] += p * (slot > 0 and y.answer is not None and
                                                             b[slot-1].answer is not None and
                                                             y.answer != b[slot-1].answer)
                failures_per_slot[slot]["illegal_a"] += p * (x.answer is not None and
                                                             x.answer not in engine.allowed[x.holder])
                failures_per_slot[slot]["illegal_b"] += p * (y.answer is not None and
                                                             y.answer not in engine.allowed[y.holder])
                for e in diff:
                    failures_per_slot[slot][f"mismatch/{e}"] += p
            predicates = dict(missing_a=missing_a, missing_b=missing_b, wrong_a=illegal_a, wrong_b=illegal_b,
                              unstable_b=unstable, setup_failure=any(r.status == "no_source" for r in a + b),
                              a_bad=missing_a or illegal_a, b_bad=missing_b or illegal_b or unstable,
                              any_mismatch=bool(mismatch_count),
                              mismatch_or_b_bad=mismatch_count > 0 or missing_b or illegal_b or unstable,
                              mismatch_count=mismatch_count)
            for name, value in predicates.items():
                score[name] += p * value
        assembled = Counter()
        for (herald, *reports), p in law.items():
            if any(r.answer is None or r.answer not in engine.allowed[r.holder] for r in reports):
                continue
            named = {}
            for r in reports:
                named.update(bits(engine.holdings, r))
            for h in far:
                word = sum(named[e] << i for i, e in enumerate(engine.holdings[h]))
                assembled[h] += p * (word not in engine.allowed[h])
        columns.append((fixed, full, score, dict(assembled), failures_per_slot))
    bounds = []
    for (fixed, _full, row, assembled, _failures), law in zip(columns, laws, strict=True):
        distances = [total_variation(law, other) for other in laws]
        counted = row["a_bad"] + sum(other["mismatch_count"] + other["b_bad"] + variation
                                      for (_, _, other, _, _), variation in zip(columns, distances, strict=True))
        union_bound = row["a_bad"] + sum(other["mismatch_or_b_bad"] + variation
                                          for (_, _, other, _, _), variation in zip(columns, distances, strict=True))
        assembled_union = row["a_bad"]
        for (herald, *reports), p in law.items():
            if any(r.answer is None or r.answer not in engine.allowed[r.holder] for r in reports):
                continue
            named = {}
            for r in reports:
                named.update(bits(engine.holdings, r))
            if any(sum(named[e] << i for i, e in enumerate(engine.holdings[h])) not in engine.allowed[h] for h in far):
                assembled_union += p
        bounds.append(dict(reference=fixed, tv=list(map(str, distances)), counted=str(counted),
                           within_run_union_bound=str(union_bound), assembled_union=str(assembled_union),
                           assembled_bad_by_holder={str(h): str(assembled[h]) for h in assembled},
                           first_prefix_differences=[first_visible(law, other) for other in laws]))
    return local, columns, laws, bounds
