"""Replay the registered eight-holding experiment on the shared physical reader."""

import argparse
from collections import Counter
from dataclasses import replace
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from math import lcm
from pathlib import Path
import sys

from derive import CHARGES, FREEZE, HOLDINGS, LEFT, RIGHT, MARK_OWNERS, local_word


EPIC = "TWO-KNOTS-ONE-DECISION-20261121-001"
ROOT = Path(__file__).resolve().parents[3]
SHARED = ROOT / "research" / EPIC
sys.path.insert(0, str(SHARED))

from histories import (Engine, Record, RecordCodes, bits, branch_metrics, differences,
                       displayed_table, first_visible, full_record, marginal, sweep, total_variation)
from literal_read import LiteralReader
from measurement import MissingState, QuantumReader, WordState, compile_device, latch_write, law


ROLES = (LEFT, RIGHT)
SETTINGS = tuple(product(*ROLES))
MIXED_SETTINGS = tuple(product((*LEFT, None), (*RIGHT, None)))


def dumps(value):
    return json.dumps(value, separators=(",", ":"), default=str)


def write_json(path, value):
    with path.open("x") as output:
        json.dump(value, output, default=str, indent=2)
        output.write("\n")


def codebook(codes, holdings):
    return {"record_codes": codes.codebook(holdings),
            "record_format": (
                "A row contains status, local address or idle, raw and displayed words, and optional tag. "
                "Slots set a preallocated local address bank to 101 on every offered address except the supplied "
                "holder, where it is 011. A pre-setting herald is present on each transcript. Each completed "
                "write fills a fresh ready bank, preserving all older banks and their receipts. The preset end "
                "mark occurs at the same slot on all branches, including idle, with no far-triggered tick. A "
                "calibration bit for each address is the fixed indicator of its named reversed occurrence. "
                "An unused or coherently cleared tag bank stays at 110. An ignored tag is present in physical "
                "storage exactly as in the corresponding held-tag panel, then omitted from the observed law. "
                "Literal trials obtain the local records through a central communication step. That evaluator's "
                "eligibility, random choice and joint trace are absent from the local record. In those trials "
                "the completed-detection field means delivery of the selected ordinary word and the raw-holder "
                "fields describe that received word, with no separate coherent pointer interaction."
            ),
            "denominator_format": (
                "For each distribution the integer numerator is the last entry of a row. Its denominator "
                "is stated once. A missing row has zero mass. An absent accepted-source distribution is null."
            )}


def physical_checks(device):
    if device.status != "ready":
        rows = device.strict_failure
        lhs = rhs = 0
        for r in rows:
            lhs ^= r["coefficients"]
            rhs ^= r["rhs"]
        assert (lhs, rhs) == (0, 1)
        return {"shared_solver_certificate_xor": [lhs, rhs], "rows": len(rows)}
    carrier = set(device.carrier)
    place = {e: i for i, e in enumerate(device.marks)}

    def step(w, e, sign):
        return w ^ device.flips[e], sign ^ (w >> place[e] & 1) ^ device.signs[e]

    counts = Counter()
    for e in device.marks:
        for w in carrier:
            after, sign = step(w, e, 0)
            assert after in carrier and step(after, e, sign) == (w, 0)
            counts["involutions"] += 1
    for h, marks in enumerate(device.holdings):
        for a, b in combinations(marks, 2):
            for w in carrier:
                assert step(*in_physical_order(step(w, a, 0), b)) == step(*in_physical_order(step(w, b, 0), a))
                counts["local_commutators"] += 1
        for holder, normal, charge in device.identities:
            if holder != h:
                continue
            involved = [e for e in device.marks if normal >> place[e] & 1]
            reversed_sign = sum((h, e) in device.reversed_occurrences for e in involved) & 1
            for w in carrier:
                current, sign = w, 0
                for e in involved:
                    current, sign = step(current, e, sign)
                assert (current, sign ^ reversed_sign) == (w, charge)
                counts["ordered_products"] += 1
    assert device.diagonal
    assert set(device.accepted_words) == {
        w for w in carrier if all(device.ordinary_output(h, w) in a for h, a in enumerate(device.allowed))
    }
    counts["postherald_all_local_support_checks"] = len(device.accepted_words) * len(device.holdings)
    return dict(counts)


def in_physical_order(result, mark):
    word, sign = result
    return word, mark, sign


def quantum_reader(device, **kwargs):
    return Engine(QuantumReader(device, **kwargs), device.holdings, device.allowed)


def literal_reader(holdings, allowed, bias=False):
    return Engine(LiteralReader(holdings, allowed, bias=bias), holdings, allowed, literal=True)


def state_descriptor(state):
    if isinstance(state, MissingState):
        return ["no preparation", state.reason]
    assert isinstance(state, WordState)
    return ["word support indexed by physical word", hex(state.left), hex(state.right),
            state.linked, state.left_phase, state.right_phase]


def physical_poststates(engine, h, k, codes):
    transitions = Counter()
    for p, state in engine.launches:
        for a, b, q, after in engine.transitions(state, h, k):
            transitions[engine.preparation(state), a, b, tuple(state_descriptor(after))] += p * q
    denominator = lcm(*(p.denominator for p in transitions.values()))
    assert sum(transitions.values()) == 1
    return {"denominator": denominator,
            "digits": [[herald, codes.encode(a), codes.encode(b), state, int(mass * denominator)]
                       for (herald, a, b, state), mass in transitions.items()]}


def fresh(engine, settings, codes, *, states=False):
    rows = []
    for h, k in settings:
        dist = engine.distribution((h,), (k,))
        ok = engine.distribution((h,), (k,), accepted=True)
        rows.append(dict(settings=[h, k], shared=sorted(set(engine.holdings[h]) & set(engine.holdings[k])),
                         launch=displayed_table(dist), accepted=displayed_table(ok),
                         launch_records=codes.pack(dist), accepted_records=codes.pack(ok),
                         score=branch_metrics(engine, dist),
                         poststates=physical_poststates(engine, h, k, codes) if states else None))
    return {"acceptance": engine.acceptance, "uniform_independent_settings_weights": f"1/{len(settings)}",
            "ordinary_cells": 64 * len(settings), "failure_augmented_cells": 81 * len(settings), "rows": rows}


def reversals_and_recodings(device):
    assert device.diagonal
    # Passive change of physical names, keeping the actual local slot order and the compiled instrument.
    rename = {e: len(device.marks) - 1 - e for e in device.marks}

    def move(w):
        return sum((w >> e & 1) << f for e, f in rename.items())

    names_reversed = tuple(tuple(rename[e] for e in holding) for holding in device.holdings)
    transported = replace(device, holdings=names_reversed,
                          identities=tuple((h, move(mask), b) for h, mask, b in device.identities),
                          carrier=tuple(sorted(map(move, device.carrier))),
                          accepted_words=tuple(sorted(map(move, device.accepted_words))),
                          flips={rename[e]: move(mask) for e, mask in device.flips.items()},
                          signs={rename[e]: s for e, s in device.signs.items()},
                          reversed_occurrences=frozenset((h, rename[e]) for h, e in device.reversed_occurrences))
    recompiled = compile_device(names_reversed, device.allowed, relaxed=True)
    reordered = compile_device(tuple(h[::-1] for h in device.holdings), device.allowed, relaxed=True)

    def reverse_slots(word):
        return ((word & 1) << 2) | (word & 2) | ((word & 4) >> 2)

    def plain_table(candidate, transform):
        engine = quantum_reader(candidate, roles=ROLES)
        result = {}
        for h, k in SETTINGS:
            law = displayed_table(engine.distribution((h,), (k,)))
            assert 16 % law["denominator"] == 0
            factor = 16 // law["denominator"]
            result[f"{h}/{k}"] = [[transform(a), transform(b), n * factor] for a, b, n in law["cells"]]
        return result

    original = plain_table(device, lambda value: value)
    fixed_transport = plain_table(transported, lambda value: value)
    resolution = plain_table(recompiled, lambda value: value)
    permuted = {key: sorted(cells) for key, cells in plain_table(reordered, reverse_slots).items()}
    assert fixed_transport == original == permuted
    changed = [key for key in original if original[key] != resolution[key]]
    assert changed == ["0/1", "6/7"]

    # A shared sign-frame change reverses its raw reading at both owners. This leaves equality
    # invariant and changes both local parities if the charged catalogue and auxiliary stay fixed.
    e = min(device.marks)
    sign_changed = replace(device, signs=device.signs | {e: 1 ^ device.signs[e]})
    changed_local = [h for h, permitted in enumerate(device.allowed)
                     if all(sign_changed.ordinary_output(h, w) not in permitted for w in device.accepted_words)]
    assert tuple(changed_local) == MARK_OWNERS[e]
    return {"passively_transported_occurrences": sorted(transported.reversed_occurrences),
            "recompiled_reversed_name_occurrences": sorted(recompiled.reversed_occurrences),
            "recompiled_new_to_original_marks": rename,
            "recompiled_changed_settings": changed, "recompiled_tables_with_numerators_of": 16,
            "recompiled_displayed_tables": resolution,
            "reordered_holder_lists": reordered.holdings, "holder_bit_slots_transport": [2, 1, 0],
            "all_cells_fixed_device_transport_equal": 1024, "all_cells_reordered_slots_equal": 1024,
            "global_raw_sign_flip_illegal_holders": changed_local, "shared_equality_after_global_raw_sign_flip": True,
            "global_raw_sign_flipped_mark": e}


def elementary_writes():
    states = (0b110, 0b101, 0b011)

    def swap(state, pair):
        a, b = (1 << (2 - i) for i in pair)
        return state ^ (a | b) if bool(state & a) != bool(state & b) else state

    rows = []
    for pair in combinations(range(3), 2):
        after = tuple(swap(state, pair) for state in states)
        assert set(after) == set(states) and tuple(swap(state, pair) for state in after) == states
        rows.append(dict(local_pair=pair, before=[f"{s:03b}" for s in states],
                         after=[f"{s:03b}" for s in after]))
    assert latch_write(0) == (0b101, (1, 2)) and latch_write(1) == (0b011, (0, 2))
    return {"legal_swap_permutations": rows, "controlled_data_bit_pair": (0, 1),
            "data_transposition_applied_in_calibrated_device": [],
            "calibration_exchange_roles": ["raw 0 -> recorded 1", "raw 1 -> recorded 0"]}


def prove_amplitude_rows():
    # Use integer numerators in units of one half, for both pointer outputs and the two tag branches.
    rows = []
    for eigenvalue, bit in product((1, -1), (0, 1)):
        components = (1, eigenvalue * (-1 if bit else 1))
        retained = tuple(Fraction(c * c, 4) for c in components)
        traced = sum(retained)
        clean = Fraction(sum(components) ** 2, 4)
        assert traced == Fraction(1, 2) and clean == int(eigenvalue == (-1 if bit else 1))
        rows.append(dict(eigenvalue=eigenvalue, pointer_bit=bit, branch_amplitude_numerators=components,
                         amplitude_denominator=2, retained_tag_joint_probabilities=retained,
                         traced_tag_pointer_probability=traced, clean_pointer_probability=clean))
    return rows


def missing_write_and_admission(device, codes):
    h, k = 0, 1
    plain = quantum_reader(device, roles=ROLES)
    outcomes = {}
    states_by_mode = {}
    for mode in ("write", "not_ready", "disconnected"):
        engine = quantum_reader(device, writer=(mode, "write"), roles=ROLES)
        first = engine.distribution((h,), (None,))
        states = physical_poststates(engine, h, None, codes)
        states_by_mode[mode] = states
        rows = Counter()
        for p, start in engine.launches:
            for a, b, q, after in engine.transitions(start, h, None):
                for a2, b2, r, _ in plain.transitions(after, h, k):
                    rows[engine.preparation(start), (a, a2), (b, b2)] += p * q * r
        assert sum(rows.values()) == 1
        outcomes[mode] = dict(launch=codes.pack(first), poststates=states, next_successful_request=codes.pack(rows))

    accepted = device.accepted_words
    u, v = next((u, v) for u, v in combinations(accepted, 2) if local_word(u, HOLDINGS[h]) != local_word(v, HOLDINGS[h]))

    def off_diagonal(mode):
        result = Fraction()
        states = states_by_mode[mode]
        for herald, _ar, _br, state, numerator in states["digits"]:
            if herald != "ready":
                continue
            _, mask, _, linked, lphase, rphase = state
            support = int(mask, 16)
            assert linked and lphase == rphase == 0
            if support >> u & 1 and support >> v & 1:
                result += Fraction(numerator, states["denominator"] * support.bit_count())
        return result

    assert off_diagonal("not_ready") == Fraction(1, 32) and off_diagonal("disconnected") == 0
    invalid = {}
    for request in (1, -1, (0, 0), (0, 3)):
        rows = plain.distribution((h, request, h), (None, k, None))
        assert all(left[0].answer == left[2].answer for _, left, _ in rows)
        malformed = [r for _, left, _ in rows for r in left if r.holder == request]
        assert all(r.status == ("out_of_role" if request == 1 else "invalid") for r in malformed)
        invalid[str(request)] = codes.pack(rows)
    return {"writer_controls": outcomes, "invalid_duplicate_multiple_and_role_controls": invalid,
            "off_diagonal_matrix_entry": dict(words=[u, v], not_ready=off_diagonal("not_ready"),
                                              disconnected=off_diagonal("disconnected"))}


def condition_readouts(engine, full, observer, shared_marks, codes):
    """Conditional new far answers, including refusal and no shared mark."""
    joints = {}
    for (herald, left, right), p in full.items():
        a, b = (left, right) if observer == 0 else (right, left)
        assert b[0] == Record(None, "idle", None, None, None)
        joints.setdefault((herald, a[0]), Counter())[b[1]] += p
    projected = []
    for (herald, near), dist in joints.items():
        near_mass = sum(dist.values())
        complete_answers, raw_answers = Counter(), Counter()
        for far, p in dist.items():
            complete_answers[far.answer] += p / near_mass
            raw_answers[far.raw] += p / near_mass
        possible = {word: p for word, p in complete_answers.items() if word is not None}
        entries = {e: {"raw": Counter(), "recorded": Counter()} for e in shared_marks}
        for far, p in dist.items():
            for e in shared_marks:
                entries[e]["raw"][bits(engine.holdings, far, raw=True).get(e)] += p / near_mass
                entries[e]["recorded"][bits(engine.holdings, far).get(e)] += p / near_mass
        projected.append(dict(herald=herald, near=codes.encode(near), near_mass=near_mass,
                              far_word_law=encode_value_law(complete_answers), far_raw_word_law=encode_value_law(raw_answers),
                              max_guess_of_whole_far_word=max(possible.values(), default=None),
                              far_refusal_or_missing=complete_answers[None],
                              far_shared_bits={str(e): {mode: encode_value_law(rows) for mode, rows in v.items()}
                                               for e, v in entries.items()}))
    return projected


def encode_value_law(law):
    assert sum(law.values()) == 1
    return [[value, weight] for value, weight in law.items()]


def unilateral(engine, settings, codes):
    rows = []
    for (h, k), observer in product(settings, (0, 1)):
        policies = ((h, None), (None, k)) if observer == 0 else ((None, h), (k, None))
        marks = sorted(set(engine.holdings[h]) & set(engine.holdings[k]))
        full = engine.distribution(*policies)
        accepted = engine.distribution(*policies, accepted=True)
        far_policies = ((None, None), (None, k)) if observer == 0 else ((None, h), (None, None))
        without_near = engine.distribution(*far_policies)
        far_variation = total_variation(marginal(full, 1-observer), marginal(without_near, 1-observer))
        rows.append(dict(settings=[h, k], near_role=observer, shared_marks=marks, launched=codes.pack(full),
                         accepted=codes.pack(accepted),
                         conditional_launch=condition_readouts(engine, full, observer, marks, codes),
                         conditional_accepted=(condition_readouts(engine, accepted, observer, marks, codes)
                                               if accepted is not None else None),
                         nonselective_far_variation=far_variation))
    return {"rows": rows, "idle_protocol": "no address, no receipt, no read or answer/tag write, "
            "no change attributable to the near reader, only the preset local end mark"}


def persistence(engine, dist):
    result = Counter()
    witnesses = {}
    for (_herald, view, _), p in dist.items():
        for i, j in combinations(range(len(view)), 2):
            a, b = view[i], view[j]
            if a.answer is None or b.answer is None:
                result[f"{i}/{j}/missing"] += p
                continue
            old = bits(engine.holdings, a)
            new = bits(engine.holdings, b)
            diff = differences(engine.holdings, a, b)
            raw_diff = differences(engine.holdings, a, b, raw=True)
            for e in sorted(old.keys() & new.keys()):
                result[f"{i}/{j}/shared/{e}/retained"] += p * (e not in diff)
                result[f"{i}/{j}/shared/{e}/changed"] += p * (e in diff)
                result[f"{i}/{j}/shared/{e}/raw_changed"] += p * (e in raw_diff)
            result[f"{i}/{j}/any_change"] += p * bool(diff)
            if diff and f"{i}/{j}" not in witnesses:
                witnesses[f"{i}/{j}"] = {"full_records": view, "weight": p, "changed_marks": diff}
    return {"observed_probabilities": result, "first_changed_record_witnesses": witnesses}


def adaptive(engine, roles, codes):
    panels = []
    for observer in (0, 1):
        local, remote = roles[observer], roles[1-observer]
        h = local[0]
        k = local[1] if len(local) > 1 else h
        remote_marks = set().union(*(set(engine.holdings[r]) for r in remote))
        e = min(set(engine.holdings[h]) & remote_marks)
        bit_index = engine.holdings[h].index(e)
        ask = next((r for r in remote if e in engine.holdings[r]), None)
        omit = next((r for r in remote if e not in engine.holdings[r]), None)

        def observing(slot, reports):
            if slot < 3:
                return (h, None, h)[slot]
            return k if (reports[0].answer is not None and reports[0].answer >> bit_index & 1 and
                         reports[2].answer is not None) else h

        def observations(policies):
            ordered = policies if observer == 0 else policies[::-1]
            return engine.distribution(*ordered, slots=4)

        present = observations((observing, (None, ask, None, None)))
        absent = observations((observing, (None, omit, None, None)))
        present_law, absent_law = (marginal(x, observer) for x in (present, absent))

        primary = remote[0]
        alternative = remote[-1]

        def other(slot, records):
            if slot == 1 and records[0].answer is not None and records[0].answer & 1:
                return alternative
            return primary

        observing_sweep = tuple(local[i % len(local)] for i in range(4))
        changed = observations((observing_sweep, other))
        fixed = observations((observing_sweep, (primary,) * 4))
        changed_law, fixed_law = (marginal(x, observer) for x in (changed, fixed))
        assert ask != omit
        # A supplied far-address record has disjoint support under the two choices.
        with_far_present = Counter({(ask, *prefix): weight for prefix, weight in present_law.items()})
        with_far_absent = Counter({(omit, *prefix): weight for prefix, weight in absent_law.items()})
        positive = total_variation(with_far_present, with_far_absent)
        assert positive == 1
        panels.append(dict(observer=observer, h=h, e=e, k=k, far_containing=ask, far_omitting=omit,
                           unilateral_then_adapt=dict(
                               full_records=[codes.pack(dist) for dist in (present, absent)],
                               one_sided_records=[codes.pack_private(law) for law in (present_law, absent_law)],
                               variation=total_variation(present_law, absent_law),
                               first_unequal_prefix=first_visible(present_law, absent_law)),
                           remote_adapts_to_own_first_bit=dict(
                               alternate_holder=alternative, baseline_holder=primary,
                               full_records=[codes.pack(dist) for dist in (changed, fixed)],
                               one_sided_records=[codes.pack_private(law) for law in (changed_law, fixed_law)],
                               variation=total_variation(changed_law, fixed_law),
                               first_unequal_prefix=first_visible(changed_law, fixed_law)),
                           deliberate_far_setting_readout_variation=positive))
    return panels


def single_reader_controls(engine, codes, write):
    holders = range(len(engine.holdings))
    maxima = {}
    for h, k in product(holders, repeat=2):
        for seq, panel in (((h, k), "single_reader_pair"), ((h, k, h), "single_reader_return")):
            dist = engine.distribution(seq, (None,) * len(seq))
            checks = persistence(engine, dist)
            write(panel, seq, codes.pack(dist), checks)
            for event, value in checks["observed_probabilities"].items():
                if event.endswith("/any_change") and value and (event not in maxima or value > maxima[event][0]):
                    maxima[event] = (value, seq)
    return maxima


def joint_controls(engine, codes, write):
    laws = ({}, {})
    max_mismatches = Counter()
    for (h, k), (i, j) in product(MIXED_SETTINGS, repeat=2):
        paths = (h, i), (k, j)
        dist = engine.distribution(*paths)
        stats = branch_metrics(engine, dist)
        write("joint_two_slots", paths, codes.pack(dist), stats)
        for name, value in stats.items():
            if name.endswith("mismatch"):
                max_mismatches[name] = max(max_mismatches[name], Fraction(value))
        for observer in (0, 1):
            own, other = paths[observer], paths[1-observer]
            laws[observer].setdefault(own, {})[other] = marginal(dist, observer)
    privacy = []
    for observer, panels in enumerate(laws):
        maximum, witness = Fraction(), None
        total = divergent = 0
        for own, alternatives in panels.items():
            for far1, far2 in combinations(alternatives, 2):
                total += 1
                a, b = alternatives[far1], alternatives[far2]
                variation = total_variation(a, b)
                if variation:
                    divergent += 1
                    current = dict(local=own, far=[far1, far2], witness=first_visible(a, b))
                    write("two_slot_privacy_witness", dict(observer=observer, local=own, far=[far1, far2]),
                          None, current["witness"])
                    if variation > maximum:
                        maximum, witness = variation, current
        privacy.append(dict(observer=observer, comparisons=total, divergent=divergent,
                            maximum_variation=maximum, first_unequal_prefix=witness))
    return dict(ordered_two_slot_setting_sequences=len(MIXED_SETTINGS)**2,
                from_joint_legal_pairs=len(SETTINGS)**2, mixed_sequences=len(MIXED_SETTINGS)**2-len(SETTINGS)**2,
                immediate_joint_repeats=len(SETTINGS), mismatch_maxima=max_mismatches, privacy=privacy)


def holds_sweep(engine, codes, write, odd):
    summaries = []
    for observer, order in product((0, 1), (1, -1)):
        local, columns, marginal_laws, bounds = sweep(engine, ROLES, observer, order)
        outcomes = []
        for (fixed, full, score, assembled, failures_per_slot), law in zip(columns, marginal_laws, strict=True):
            write("held_reader_sweep", dict(observer=observer, local=local, fixed=fixed),
                  codes.pack(full), dict(local_marginal=codes.pack_private(law), events=score,
                                         per_slot=failures_per_slot, assembled_bad_by_holder=assembled))
            outcomes.append(dict(fixed=fixed, events=score, per_slot=failures_per_slot))
        if odd:
            assert all(Fraction(row["counted"]) >= 1 and Fraction(row["assembled_union"]) == 1 for row in bounds)
        summaries.append(dict(observer=observer, order=order, odd_charge_hypothesis=odd, per_hold=outcomes,
                              full_privacy=all(not any(Fraction(p) for p in row["tv"]) for row in bounds),
                              bound_rows=bounds))
    return summaries


def repeat_tagged(device, codes):
    choices = [(0, None), (None, 1)]
    rows = []
    for first_policy, second_policy in product(("none", "held", "ignored", "uncomputed"), repeat=2):
        for h, k in choices:
            directions = 0 if h is not None else 1
            tags_before = (first_policy, "none") if directions == 0 else ("none", first_policy)
            tags_after = (second_policy, "none") if directions == 0 else ("none", second_policy)
            reader = quantum_reader(device, tag=tags_before, roles=ROLES)
            again = quantum_reader(device, tag=tags_after, roles=ROLES)
            dist, branches = Counter(), Counter()
            changed, both = Fraction(), Fraction()
            for mass, start in reader.launches:
                for a, b, pa, interim in reader.transitions(start, h, k):
                    for c, d, pb, after in again.transitions(interim, h, k):
                        p = mass * pa * pb
                        dist[reader.preparation(start), (a, c), (b, d)] += p
                        states = tuple(tuple(state_descriptor(s)) for s in (start, interim, after))
                        branches[reader.preparation(start), (a, c), (b, d), states] += p
                        old, new = (a, c) if directions == 0 else (b, d)
                        if old.answer is None or new.answer is None:
                            continue
                        both += p
                        differences_here = differences(device.holdings, old, new)
                        assert all(e == device.holdings[old.holder][0] for e in differences_here)
                        changed += p * bool(differences_here)
            assert sum(dist.values()) == 1
            assert changed == both * Fraction(int(first_policy in ("held", "ignored") or
                                                   second_policy in ("held", "ignored")), 2)
            denominator = lcm(*(mass.denominator for mass in branches.values()))
            trace = [[herald, [codes.encode(r) for r in a], [codes.encode(r) for r in b], states,
                      int(mass * denominator)] for (herald, a, b, states), mass in branches.items()]
            rows.append(dict(first_policy=first_policy, second_policy=second_policy, role=directions, settings=[h, k],
                             launch_distribution=codes.pack(dist), both_outputs_present=both,
                             probability_different=changed,
                             conditional_probability_different=changed/both if both else None,
                             physical_state_sequence={"denominator": denominator, "digits": trace}))
    return rows


def tagged(device, codes):
    results = {}
    primary = quantum_reader(device, roles=ROLES)
    for selected_policy, marked in product(("held", "ignored", "uncomputed"), ((0,), (1,), (0, 1))):
        policies = tuple(selected_policy if i in marked else "none" for i in range(2))
        engine = quantum_reader(device, tag=policies, roles=ROLES)
        results["/".join(policies)] = fresh(engine, SETTINGS, codes, states=True)
        if selected_policy == "uncomputed":
            assert all(engine.distribution((h,), (k,)) == primary.distribution((h,), (k,)) for h, k in SETTINGS)
            assert all(physical_poststates(engine, h, k, codes) == physical_poststates(primary, h, k, codes)
                       for h, k in SETTINGS)
        if selected_policy == "ignored":
            previous = results["/".join("held" if i in marked else "none" for i in range(2))]
            for saved, current in zip(previous["rows"], results["/".join(policies)]["rows"], strict=True):
                assert saved["launch"] == current["launch"] and saved["accepted"] == current["accepted"]
    return {"fresh_panels": results, "targeted_repeat_panels": repeat_tagged(device, codes)}


def lawful_pair():
    holdings = ((0, 1, 2), (0, 3, 4))
    settings = tuple(product(range(2), repeat=2))
    code = RecordCodes()
    report = {}
    for name, a in (("all_even", law(holdings)), ("not_all_equal", law(holdings, "nae"))):
        device = compile_device(holdings, a)
        relaxed = compile_device(holdings, a, relaxed=True)
        assert relaxed.minimum_masks == ((),)
        primary = quantum_reader(device)
        literal = literal_reader(holdings, a)
        cases = {"paired": primary, "literal": literal, "independent": quantum_reader(device, source="independent"),
                 "equal_word_mixture": quantum_reader(device, source="dephased"),
                 "direct_legal_word": quantum_reader(device, source="ordinary")}
        controls = {}
        for key, engine in cases.items():
            single = []

            def write(panel, seq, dist, scores):
                single.append(dict(panel=panel, sequence=seq, records=dist, scores=scores))

            summary = single_reader_controls(engine, code, write)
            controls[key] = {"fresh": fresh(engine, settings, code), "unilateral": unilateral(engine, settings, code),
                             "single_reader": single, "single_reader_maxima": summary,
                             "adaptive": adaptive(engine, ((0,), (1,)), code)}
        assert all(row["score"].get("0/mismatch", "0") == "0"
                   for row in controls["paired"]["fresh"]["rows"] if row["settings"][0] == row["settings"][1])
        report[name] = dict(compiler=device.certificate(), physical_check_counts=physical_checks(device), trials=controls,
                            selected_minimum_reversal=relaxed.minimum_masks)
    return {"holdings": holdings, **report, **codebook(code, holdings)}


def setup_cases():
    signed = law(HOLDINGS, odd=7)
    even = law(HOLDINGS)
    nae = law(HOLDINGS, "nae")
    devices = {
        "strict": compile_device(HOLDINGS, signed),
        "calibrated": compile_device(HOLDINGS, signed, relaxed=True),
        "all_even": compile_device(HOLDINGS, even),
        "not_all_equal": compile_device(HOLDINGS, nae),
    }
    cases = {key: quantum_reader(device) for key, device in devices.items()}
    cases.update(literal_uniform=literal_reader(HOLDINGS, signed), literal_biased=literal_reader(HOLDINGS, signed, True),
                 literal_all_even=literal_reader(HOLDINGS, even), literal_not_all_equal=literal_reader(HOLDINGS, nae),
                 literal_nae_biased=literal_reader(HOLDINGS, nae, True))
    return devices, cases


def compare_full_launch_to_accepted():
    return "To recover the conditional law from any launch history, restrict it to the ready herald and divide " \
           "by the displayed source acceptance. For no ready herald it is undefined. Proof of privacy uses the " \
           "complete local instruments (including the idle identity and refusal), with each opposite-wing " \
           "policy's branch-summed operation trace preserving. An adaptive choice is a local channel controlled " \
           "only by that wing's previous local record. Consequently no finite adaptive tree changes the " \
           "nonselective local transcript law when the other wing's policy is changed."


def run(output, group):
    if sha256((SHARED / "preregistration.md").read_bytes()).hexdigest() != FREEZE:
        raise ValueError("research design does not match the frozen file")
    output.mkdir(parents=True)
    initial_hashes = {path: sha256((SHARED / path).read_bytes()).hexdigest() for path in ("measurement.py", "literal_read.py")}
    devices, cases = setup_cases()
    codes = RecordCodes()
    if group in ("all", "fresh"):
        source_controls = {f"{key}/{source}": quantum_reader(device, source=source, roles=ROLES)
                           for key, device in devices.items() if key != "strict"
                           for source in ("dephased", "independent", "ordinary")}
        metadata = {"design_sha256": FREEZE, "sha256_of_common_readers": initial_hashes,
                    "physical_holding_mark_names": HOLDINGS, "roles": ROLES, "mark_owners": MARK_OWNERS,
                    "original_charge_by_holder": CHARGES,
                    "compiler_certificates": {key: device.certificate() for key, device in devices.items()},
                    "physical_validation": {key: physical_checks(device) for key, device in devices.items()},
                    "minimum_reversal_search_on_lawful_catalogues": {
                        key: compile_device(device.holdings, device.allowed, relaxed=True).minimum_masks
                        for key, device in devices.items() if key in ("all_even", "not_all_equal")
                    },
                    "fresh": {key: fresh(engine, SETTINGS, codes, states=key in devices) for key, engine in cases.items()},
                    "source_controls": {key: fresh(engine, SETTINGS, codes) for key, engine in source_controls.items()},
                    "source_control_unilateral": {key: unilateral(engine, SETTINGS, codes)
                                                  for key, engine in source_controls.items()},
                    "unilateral": {key: unilateral(engine, SETTINGS, codes) for key, engine in cases.items()},
                    "explicit_no_source_control": fresh(quantum_reader(devices["all_even"], force_refusal=True, roles=ROLES),
                                                        SETTINGS, codes, states=True),
                    "recoding": reversals_and_recodings(devices["calibrated"]),
                    "elementary_ordinary_writes": elementary_writes(),
                    "tagged_pointer_joint_amplitudes": prove_amplitude_rows(),
                    "tag_controls": {key: tagged(device, codes) for key, device in devices.items()},
                    "postmeasurement_write_and_pre_read_admission": missing_write_and_admission(devices["calibrated"], codes),
                    "independent_lawful_two_holder_controls": lawful_pair(),
                    "conditional_history_and_privacy": compare_full_launch_to_accepted(),
                    "physical_poststate_code": (
                        "For diagonal controls, bit i of each support mask selects data word i. In a linked coherent "
                        "branch all listed paired |w,w> have equal modulus and phase (-1)^(w dot (left_phase XOR "
                        "right_phase)), ignoring global signs. For an incoherent mixture use uniform weights on this "
                        "support; the independent control is the product of separate uniform mixtures. A hidden "
                        "outcome in a disconnected writer is a traced-out instrument branch, never a local record."
                    )}
        metadata.update(codebook(codes, HOLDINGS))
        with (output / "fresh.json.gz").open("xb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
            gz.write((dumps(metadata) + "\n").encode())
    if group in ("all", "histories"):
        codes = RecordCodes()
        summary = {}
        history_cases = cases | {f"{key}_independent": quantum_reader(device, source="independent")
                                 for key, device in devices.items() if key != "strict"}
        with (output / "histories.jsonl.gz").open("xb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
            for key, engine in history_cases.items():
                def write(panel, inputs, records, scores):
                    payload = dict(case=key, panel=panel, inputs=inputs, records=records, scores=scores)
                    gz.write((dumps(payload) + "\n").encode())

                print(f"Reading histories for {key}", flush=True)
                odd = key in ("strict", "calibrated", "calibrated_independent", "literal_uniform", "literal_biased")
                summary[key] = dict(
                    source_acceptance=engine.acceptance,
                    single_reader_maxima=single_reader_controls(engine, codes, write),
                    two_slots=joint_controls(engine, codes, write),
                    held_reader_sweeps=holds_sweep(engine, codes, write, odd),
                )
                panels = adaptive(engine, ROLES, codes)
                for panel in panels:
                    for kind in ("unilateral_then_adapt", "remote_adapts_to_own_first_bit"):
                        trial = panel[kind]
                        write(kind, dict(observer=panel["observer"]), trial.pop("full_records"),
                              dict(local_marginals=trial.pop("one_sided_records"), **trial))
                summary[key]["adaptive"] = panels
        write_json(output / "history_index.json", {
            "design_sha256": FREEZE, "sha256_of_common_readers": initial_hashes,
            "roles": ROLES, "holdings": HOLDINGS, **codebook(codes, HOLDINGS),
            "summary": summary, "conditional_history_and_privacy": compare_full_launch_to_accepted(),
            "dephased_and_direct_source_history_replay": (
                "All accepted branches here are diagonal. Reading a history is multiplication by "
                "indicators of observed local words. Thus the coherent and dephased accepted-state "
                "histories coincide exactly. For direct preparation from accepted ordinary words, use "
                "that same conditional law at launch with acceptance one."
            )
          })
    assert initial_hashes == {path: sha256((SHARED / path).read_bytes()).hexdigest() for path in initial_hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--group", choices=("all", "fresh", "histories"), default="all")
    args = parser.parse_args()
    run(args.output, args.group)


if __name__ == "__main__":
    main()
