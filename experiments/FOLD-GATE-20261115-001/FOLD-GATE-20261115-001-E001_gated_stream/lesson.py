"""A common stream of checker feedback, plus a separate adaptive reference.

Only this module's referee reads the target truth. Each call to the search
backend receives an immutable prefix of the labels revealed so far.
"""

from hashlib import sha256
import json
from time import perf_counter_ns, process_time_ns

from gate import decision


STAGES = (8, 12, 16, 24, 32, 48, 64)
ALL_ROWS = frozenset(range(64))


class _Referee:
    __slots__ = ("_target",)

    def __init__(self, truth):
        if type(truth) is not int or not 0 <= truth < (1 << 64):
            raise ValueError("the referee needs a 64-bit target truth column")
        self._target = truth

    def label(self, row):
        return (self._target >> row) & 1

    def reference_disagrees(self, row, prediction):
        return self.label(row) != prediction

    def exact(self, submitted):
        # The backend validated this packed column against its physical program.
        return submitted == self._target

    def first_disagreement(self, submitted):
        # Each visited row incurs a scalar comparison, including the final
        # complete scan when the physical submission agrees everywhere.
        for row in range(63, -1, -1):
            label = self.label(row)
            if ((submitted >> row) & 1) != label:
                return (row, label), 64 - row
        return None, 64


def _shared(backend, state, referee, order, initial, try_fold, trace):
    observations = list(initial)
    failed_submissions = set()
    accepted = None
    previous = len(initial)
    for stage in STAGES:
        for pos in range(previous, stage):
            row = order[pos]
            reference = row & 1
            disagreement = referee.reference_disagrees(row, reference)
            observations.append((row, reference ^ disagreement))
            trace["teacher_mismatch_mask"] |= disagreement << row
        previous = stage
        if accepted is not None:
            continue

        visible = tuple(observations)
        candidate = None
        if try_fold and stage == STAGES[0]:
            trace["fold_lookups"] += 1
            candidate = backend.fold_candidate(visible, state)
            trace["used_fold"] = candidate is not None
        if candidate is None:
            trace["median_lookups"] += 1
            candidate = backend.default_candidate(visible, state)
        submitted = candidate["truth"]
        trace["proposal_stages"].append(stage)
        trace["proposal_truths"].append(submitted)
        if submitted in failed_submissions:
            trace["repeated_proposals"] += 1
            continue
        trace["verifier_packed_checks"] += 1
        if referee.exact(submitted):
            accepted = candidate
        else:
            failed_submissions.add(submitted)
    if accepted is None:
        raise AssertionError("no exact physical submission after all 64 public examples")
    trace["teacher_rows"] = len(observations) - len(initial)
    return accepted


def _adaptive(backend, state, referee, initial, trace):
    observations = list(initial)
    known = {row for row, _ in initial}
    while True:
        trace["median_lookups"] += 1
        candidate = backend.default_candidate(tuple(observations), state)
        submitted = candidate["truth"]
        trace["proposal_stages"].append(len(observations))
        trace["proposal_truths"].append(submitted)
        correction, scanned = referee.first_disagreement(submitted)
        trace["verifier_rows"] += scanned
        if correction is None:
            return candidate
        row, _ = correction
        if row in known:
            raise AssertionError("a median submission contradicts a known example")
        trace["adaptive_feedback"].append(correction)
        # Earlier rows in this descending scan agree with the submitted table.
        # Retain the order of old evidence for the incremental backend.
        for equal_row in range(63, row, -1):
            if equal_row not in known:
                observations.append((equal_row, (submitted >> equal_row) & 1))
                known.add(equal_row)
        observations.append(correction)
        known.add(row)


def _program_record(candidate):
    circuit = candidate["circuit"]
    # Constant addresses are fixed by the number of inputs. Gate order and
    # both operand addresses are included in the physical identity.
    encoded = json.dumps([circuit["inputs"], circuit["output"], circuit["gates"]],
                         separators=(",", ":")).encode("ascii")
    return {
        "route": candidate["route"],
        "candidate_index": candidate["candidate_index"],
        "expanded_NANDs": candidate["expanded_NANDs"],
        "macro_uses": candidate["macro_uses"],
        "physical_sha256": sha256(encoded).hexdigest(),
        "circuit": circuit,
    }


def run_task(backend, target_truth, order, mode, checkpoint=None):
    """Run one rule using independent backend state and the arm's local cache.

    prefix_labels is a bitword in the first eight positions of order. The
    shared modes' teacher_mismatch_mask has bit x set when the teacher
    corrected the public reference on input x among the remaining 56.
    Together with order these reproduce the full delivered transcript.
    Adaptive feedback records each first disagreement. proposal_stages
    gives the number of distinct labels available before each proposal,
    including any equal rows implied by an adaptive check.

    All proposals pay a lookup. In the shared modes, a per-rule record of
    failed truth columns avoids paying a second exact check for a repetition.
    verifier_rows counts scalar comparisons; verifier_packed_checks counts
    packed all-64 comparisons. search_work reports nonzero per-task backend
    counter differences, including empty fold lookups and fresh task state.
    """
    start = perf_counter_ns()
    cpu_start = process_time_ns()
    if mode not in ("median", "always", "gated", "adaptive"):
        raise ValueError(f"unknown mode {mode!r}")
    if mode == "gated" and checkpoint is None:
        raise ValueError("gated mode requires a frozen checkpoint")
    if len(order) != 64 or frozenset(order) != ALL_ROWS or any(type(row) is not int for row in order):
        raise ValueError("the public order must be a permutation of all 64 rows")
    referee = _Referee(target_truth)
    initial = tuple((row, referee.label(row)) for row in order[:STAGES[0]])
    try_fold = mode == "always" or (mode == "gated" and decision(checkpoint, initial))
    before = backend.work_counters()
    state = backend.new_task()
    trace = {
        "mode": mode,
        "prefix_labels": sum(label << pos for pos, (_, label) in enumerate(initial)),
        "try_fold": try_fold,
        "used_fold": False,
        "fold_lookups": 0,
        "median_lookups": 0,
        "proposal_stages": [],
        "proposal_truths": [],
        "repeated_proposals": 0,
        "verifier_rows": 0,
        "verifier_packed_checks": 0,
        "teacher_rows": 0,
        "teacher_mismatch_mask": None if mode == "adaptive" else 0,
        "adaptive_feedback": [],
    }
    if mode == "adaptive":
        accepted = _adaptive(backend, state, referee, initial, trace)
    else:
        accepted = _shared(backend, state, referee, order, initial, try_fold, trace)
    trace["accepted_stage"] = trace["proposal_stages"][-1]
    trace["accepted_program"] = _program_record(accepted)
    trace["verifier_calls"] = len(trace["proposal_truths"]) - trace["repeated_proposals"]
    trace["search_work"] = {key: count - before[key] for key, count in backend.work_counters().items()
                            if count != before[key]}
    trace["cpu_ns"] = process_time_ns() - cpu_start
    trace["elapsed_ns"] = perf_counter_ns() - start
    return trace
