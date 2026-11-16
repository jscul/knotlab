"""Recheck a historical local bit on an edited parent, with exact fallback.

The caller supplies a location. All bit values, physical paths, residuals and
alternative widths come from the shared parent engine. A two-bit repair may
retain h precisely when neither h-class contains more than two residuals;
its global minimality still requires excluding every eligible one-bit group.
"""

from parent_engine import _finish, _local_sources, _measure, _ordinary, _partition, _reuse, _select


COUNTERS = (
    "fold_piece_lookups", "fold_history_matches", "fold_history_wire_locality_checks",
    "fold_history_wire_value_checks", "fold_current_history_wires", "fold_existing_cut_trials",
    "fold_existing_cut_returns", "fold_old_partition_trials", "fold_old_partition_failures",
    "fold_old_partition_passes", "fold_within_class_masks", "fold_prescribed_code_builds",
    "fold_source_bit_build_requests", "fold_ordinary_fallbacks", "fold_completed_without_global_scan",
    "fold_two_bit_feasibility_tests", "fold_two_bit_impossible_with_old_bit",
    "fold_one_bit_alternative_same_group", "fold_two_bit_global_exclusions", "fold_narrower_other_group",
    "fold_extra_source_tests", "fold_legal_extra_sources", "fold_distinct_extra_truth_tests",
    "fold_distinct_legal_extra_truths", "fold_extra_bytes_constructed",
    "fold_two_source_cut_trials", "fold_two_source_cut_returns", "fold_two_bit_prescribed_builds",
    "fold_width_two_returns", "fold_width_two_old_bit_retained", "fold_width_two_old_bit_discarded",
    "fold_width_two_old_physical_source_retained", "fold_width_two_extra_source_retained",
    "fold_two_bit_generic_code_selections_avoided", "fold_attribution_packed_gates",
    "fold_width_one_old_bit_retained", "fold_width_one_old_physical_source_retained",
)


def _old_classes(labels, byte):
    """Return the local assignments in each distinct residual within each h-class."""
    sides = {}, {}
    for local, residual in enumerate(labels):
        side = sides[(byte >> local) & 1]
        side[residual] = side.get(residual, 0) | (1 << local)
    return tuple(tuple(side.values()) for side in sides)


def _can_separate(byte, constraints):
    # A bit may split an unconstrained side, allowing more actual source
    # wires than the four elementary class-to-code assignments.
    for a, b in constraints:
        x, y = byte & a, byte & b
        if not ((x == 0 and y == b) or (x == a and y == 0)):
            return False
    return True


def _cheap_extra(sides):
    choices = [(0, side[0]) if len(side) == 1 else side for side in sides]
    codes = {a | b for a in choices[0] for b in choices[1]}

    def key(byte):
        # Prefer few essential local pins if physical lookup failed. The
        # tie breaker favors a constant-biased cofactor, then byte order.
        zeros = (85, 51, 15)
        pins = sum(bool((byte ^ (byte >> (1 << i))) & mask) for i, mask in enumerate(zeros))
        return pins, min(byte.bit_count(), 8 - byte.bit_count()), byte

    return min(codes, key=key), len(codes)


def _returned_bit_tables(answer, work):
    """Read actual returned taps if the ordinary engine omitted their truth bytes."""
    m, taps, dag = answer["n"], answer["summary_wires"], answer["circuit"]
    full = (1 << (1 << m)) - 1
    values = [full ^ (full // ((1 << (1 << i)) + 1)) for i in range(m)] + [0, full]
    needed = max(0, max(taps) - (m + 2) + 1)
    for a, b in dag["gates"][:needed]:
        values.append(full ^ (values[a] & values[b]))
    work["fold_attribution_packed_gates"] += needed
    return tuple(values[t] for t in taps)


def _receipt(answer, work, piece=None):
    width = answer.get("width")
    if piece is not None and width in (1, 2):
        taps = answer.get("retained_source_wires") or ()
        byte = piece["bit_truth"]
        if tuple(answer["triple"]) != tuple(piece["inputs"]):
            # Parent checked that its old bit is essential in ALL THREE
            # inputs. A tap local to a different triple cannot equal it.
            truths, previous = (), byte
        elif answer.get("summary_truths") is not None:
            truths, previous = answer["summary_truths"], byte
        else:
            truths, previous = _returned_bit_tables(answer, work), piece["bit_table"]
        old_slot = next((j for j, truth in enumerate(truths) if truth == previous), None)
        retained = old_slot is not None
        if width == 1:
            work["fold_width_one_old_bit_retained"] += int(retained)
            physical = retained and len(taps) == 1 and taps[0] == piece["bit"]
            work["fold_width_one_old_physical_source_retained"] += int(physical)
        else:
            work["fold_width_two_returns"] += 1
            work["fold_width_two_old_bit_retained" if retained else "fold_width_two_old_bit_discarded"] += 1
            if retained and len(taps) == 2:
                work["fold_width_two_old_physical_source_retained"] += int(taps[old_slot] == piece["bit"])
                work["fold_width_two_extra_source_retained"] += int(taps[1 - old_slot] is not None)
    return answer


def fold(state, hint):
    """Return (stage answer, query work). The harness lifts the stage DAG to raw inputs."""
    # Ordinary and fold each pay for ONE pair of underlying counter snapshots
    # per edit. All abandoned checks and all shared helper work accrue here.
    return _measure(state, _fold, hint)


def _fold(state, work, hint):
    work.update(dict.fromkeys(COUNTERS, 0))
    if hint is not None:
        hint = tuple(hint)
        if (len(hint) != 3 or any(type(i) is not int or not 0 <= i < state.m for i in hint)
                or not hint[0] < hint[1] < hint[2]):
            raise ValueError("hint must be three sorted, distinct stage input indices")
    piece = None
    if hint is not None:
        for candidate in state.parent.pieces:
            work["fold_piece_lookups"] += 1
            if tuple(candidate["inputs"]) == hint:
                piece = candidate
                break

    def fallback(ordinary_hint=hint):
        work["fold_ordinary_fallbacks"] += 1
        answer = _ordinary(state, work, ordinary_hint)
        return _receipt(answer, work, piece)

    if piece is None:
        return fallback()
    work["fold_history_matches"] += 1
    bit, byte = piece["bit"], piece["bit_truth"]
    work["fold_history_wire_value_checks"] += 1
    work["fold_history_wire_locality_checks"] += 1
    # reuse/finish independently check the current wire's semantics and
    # physical locality. A changed identity alone cannot certify the old bit.
    group_mask = sum(1 << i for i in hint)
    available = state.values[bit] == piece["bit_table"] and not (state.supports[bit] & ~group_mask)
    if available:
        work["fold_current_history_wires"] += 1
        work["fold_existing_cut_trials"] += 1
        answer = _reuse(state, work, hint, (bit,))
        if answer is not None:
            work["fold_existing_cut_returns"] += 1
            work["fold_completed_without_global_scan"] += 1
            return _receipt(answer, work, piece)

    # A physical bypass may still be a function of the old bit. Read each
    # joint residual from the common per-edit partition cache, including
    # unchanged output components. A prior port certificate alone cannot
    # certify a downstream edited output.
    work["fold_old_partition_trials"] += 1
    info = _partition(state, work, hint)
    if not info["eligible"]:
        return fallback(None)
    sides = _old_classes(info["classes"], byte)
    work["fold_within_class_masks"] += 8
    size = max(map(len, sides))
    if size == 1:
        work["fold_old_partition_passes"] += 1
        work["fold_prescribed_code_builds"] += 1
        work["fold_source_bit_build_requests"] += int(available)
        sources = (bit,) if available else None
        answer = _finish(state, work, hint, (byte,), source_wires=sources)
        work["fold_completed_without_global_scan"] += 1
        return _receipt(answer, work, piece)

    work["fold_old_partition_failures"] += 1
    work["fold_two_bit_feasibility_tests"] += 1
    if info["count"] <= 2:
        # A different bit suffices already on this triple. Retaining h would
        # increase width, even when two bits could encode these residuals.
        work["fold_one_bit_alternative_same_group"] += 1
        answer = _finish(state, work, hint)
        work["fold_completed_without_global_scan"] += 1
        return _receipt(answer, work, piece)
    if size > 2:
        work["fold_two_bit_impossible_with_old_bit"] += 1
        return fallback()

    # The known triple has 3 or 4 distinct joint classes. Its cached exact
    # partition supplies a width-two incumbent. Select checks every eligible
    # competitor that could improve this bound, without first compiling a
    # disposable width-two circuit.
    work["fold_two_bit_global_exclusions"] += 1
    chosen = _select(state, work, hint, incumbent=info)
    if chosen["width"] == 1:
        work["fold_narrower_other_group"] += 1
        answer = _finish(state, work, tuple(chosen["triple"]))
        return _receipt(answer, work, piece)
    if chosen["width"] != 2:
        raise AssertionError("global search missed a verified width-two incumbent")

    constraints = tuple(side for side in sides if len(side) == 2)
    sources = _local_sources(state, work, hint)
    found_by_truth, tested = {}, {}
    new_source = None if state.edit is None else state.edit["to"]
    for source in sources:
        work["fold_extra_source_tests"] += 1
        auxiliary = source["truth"]
        if auxiliary in tested:
            work["fold_legal_extra_sources"] += int(tested[auxiliary])
            if tested[auxiliary] and source["wire"] == new_source:
                found_by_truth[auxiliary] = new_source
            continue
        valid = tested[auxiliary] = _can_separate(auxiliary, constraints)
        work["fold_distinct_extra_truth_tests"] += 1
        if not valid:
            continue
        work["fold_legal_extra_sources"] += 1
        found_by_truth[auxiliary] = source["wire"]
    # A newly wired source that is itself an admissible local auxiliary
    # already has a physical route into the changed consumer.
    found = sorted(found_by_truth.items(), key=lambda item: item[1] != new_source)
    work["fold_distinct_legal_extra_truths"] += len(found)

    # At most four distinct fully determined encodings arise when both old
    # classes split. Use the same bounded front of the available sources
    # when one side can be coded freely. Every try pays the shared DAG walk.
    if available:
        for auxiliary, wire in found[:4]:
            work["fold_two_source_cut_trials"] += 1
            answer = _reuse(state, work, hint, (bit, wire))
            if answer is not None:
                work["fold_two_source_cut_returns"] += 1
                work["fold_two_bit_generic_code_selections_avoided"] += 1
                return _receipt(answer, work, piece)
    if found:
        auxiliary, wire = found[0]
    else:
        auxiliary, k = _cheap_extra(sides)
        work["fold_extra_bytes_constructed"] += k
        wire = None
    work["fold_prescribed_code_builds"] += 1
    work["fold_two_bit_prescribed_builds"] += 1
    work["fold_source_bit_build_requests"] += int(available)
    answer = _finish(state, work, hint, (byte, auxiliary), source_wires=(bit if available else None, wire))
    work["fold_two_bit_generic_code_selections_avoided"] += 1
    return _receipt(answer, work, piece)
