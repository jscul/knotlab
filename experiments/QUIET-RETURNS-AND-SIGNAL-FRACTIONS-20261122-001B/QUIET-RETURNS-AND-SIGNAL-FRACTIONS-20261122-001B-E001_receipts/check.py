"""Replay the frozen five-phase receiver and its ordinary physical payments."""

from collections import defaultdict
from dataclasses import dataclass, replace
from functools import cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FREEZE = ROOT / "research/QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001/preregistration.md"
FROZEN_SHA = "3196e71a9161ff5c26876e00db294633c552a778042a7b136b6f6533ddbac0b0"
PREVIOUS = "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B"
PHASE_SCRIPT, = (ROOT / "experiments" / PREVIOUS).glob("*/phase_clocks.py")
PHASE_ARCHIVE, = (ROOT / "artifacts" / PREVIOUS).glob("*/phase_clocks.json")
QUIET_CONTROL, = (ROOT / "artifacts/QUIET-START-AND-FIRST-WRITE-20261122-001A").glob("*/results.json")
PHASE = run_path(str(PHASE_SCRIPT))
NX = PHASE["nx"]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "results.json"
LAWS = ("parity", "nae")
CUTS = 30


@dataclass(frozen=True)
class Frame:
    holdings: tuple
    births: tuple
    reference: tuple
    by_phase: tuple
    words: dict


def bits(word):
    return "".join(map(str, word))


def pick(word, marks):
    return tuple(word[i] for i in marks)


def lawful(law, vals):
    n = sum(vals)
    return n % 2 == 0 if law == "parity" else 0 < n < len(vals)


@cache
def allowed(law, paid):
    return tuple(w for w in product((0, 1), repeat=2) if lawful(law, paid + w))


def check_word(law, word, holdings):
    assert all(lawful(law, pick(word, row)) for row in holdings)


def owner_map(holdings):
    found = defaultdict(list)
    for holder, row in enumerate(holdings):
        for mark in row:
            found[mark].append(holder)
    assert all(len(h) in (1, 2) for h in found.values())
    return {i: tuple(h) for i, h in found.items()}


def source_reference(holdings):
    owners = owner_map(holdings)
    meetings = defaultdict(list)
    for mark, held in sorted(owners.items()):
        if len(held) == 2:
            meetings[held].append(mark)
    assert sorted(map(len, meetings.values())) == [1, 1, 1, 2, 3]
    marked = {marks[0] for marks in meetings.values()}
    ref = tuple(int(i in marked) for i in range(len(owners)))
    assert len(ref) == 18 and len(marked) == 5
    assert all(sum(pick(ref, r)) == 2 for r in holdings)
    return ref


def reference_extension(before, rows):
    result = list(before)
    incoming = {pick(before, row.inputs) for row in rows}
    assert len(incoming) == 1
    x, y = next(iter(incoming))
    assert x == y
    for row in rows:
        assert row.fresh == tuple(range(len(result), len(result) + 2))
        result.extend((1 - x, 1 - x))
    return tuple(result)


def physical_bindings(holdings, births):
    """All 32 lawful allocations given the actual completed parent roster."""
    owners = owner_map(holdings)
    per_parent = defaultdict(list)
    for i, row in enumerate(births):
        for j, parent in enumerate(row.parents):
            per_parent[parent].append((i, j, row.inputs[j]))
    assert len(per_parent) == 5 and all(len(row) == 2 for row in per_parent.values())
    for bits_to_swap in product((0, 1), repeat=5):
        allocations = [list(row.inputs) for row in births]
        for ((i, j, a), (u, v, b)), swap in zip(per_parent.values(), bits_to_swap, strict=True):
            assert owners[a] == owners[b] and len(owners[a]) == 1 and a != b
            if swap:
                allocations[i][j], allocations[u][v] = b, a
        yield tuple(replace(row, inputs=tuple(p)) for row, p in zip(births, allocations, strict=True))


def structural_replay(source, law, archive):
    fixture = PHASE["fixture"]()
    order, marker = PHASE["identify_origin"](source)
    assert list(order) == archive["original_witnessed_order"]
    frames = [Frame(source, (), source_reference(source), order, {v: (v,) for v in order})]
    literal = {}
    binding_checks = 0
    for cut in range(CUTS + 1):
        past = frames[-1]
        assert PHASE["certify_cut"](past.holdings, law)
        read = PHASE["read_current"](past.holdings, law)
        assert read.original_order == order and read.cut == cut and read.parents == literal and read.words == past.words
        assert list(past.by_phase) == archive["literal_cuts"][cut]["knots_by_first_endpoint_phase"]
        # Verify the receiver hands off through an actual shared paid distinction.
        if cut < CUTS:
            status, births, _ = fixture.literal_turn(past.holdings, law)
            assert status == "extend" and len(births) == 5 and all(len(b.parents) == len(b.fresh) == 2 for b in births)
            by_group = {frozenset(b.parents): b for b in births}
            words = dict(past.words)
            phase = []
            for i, p in enumerate(past.by_phase):
                q = past.by_phase[(i + 1) % len(order)]
                b = by_group[frozenset((p, q))]
                assert words[p][1:] == words[q][:-1]
                words[b.knot] = (*words[p], words[q][-1])
                phase.append(b.knot)
            assert all(words[v][-1] == order[(i + cut + 1) % len(order)] for i, v in enumerate(phase))
            old_loose = {i for i, held in owner_map(past.holdings).items() if len(held) == 1}
            assert set(past.reference[i] for i in old_loose) == {cut % 2}
            fixed_ref = reference_extension(past.reference, births)
            local = tuple(births)
            new_holdings = past.holdings + tuple(b.support for b in local)
            end = fixture.from_stars(new_holdings)
            for alternate in physical_bindings(past.holdings, births):
                bound = past.holdings + tuple(b.support for b in alternate)
                new_owners = owner_map(bound)
                used = {m for b in alternate for m in b.inputs}
                assert used == old_loose and all(new_owners[m] == (parent, row.knot)
                       for row in alternate for parent, m in zip(row.parents, row.inputs, strict=True))
                assert fixture.from_stars(bound) == end
                assert reference_extension(past.reference, alternate) == fixed_ref
                check_word(law, fixed_ref, bound)
                binding_checks += 1
            literal.update({b.knot: frozenset(b.parents) for b in births})
            frames.append(Frame(new_holdings, local, fixed_ref, tuple(phase), words))
    assert binding_checks == 32 * CUTS
    return order, marker, frames, binding_checks


def receiver_trace(frames, order):
    chain = tuple(f.by_phase[0] for f in frames)
    receipts = []
    handoffs = []
    used = set()
    for i, (older, v) in enumerate(zip(chain[:-1], chain[1:], strict=True), 1):
        frame = frames[i]
        b, = (row for row in frame.births if row.knot == v)
        old, new = owner_map(frames[i - 1].holdings), owner_map(frame.holdings)
        assert frame.words[v][0] == order[0] and older in b.parents
        anchor_payment = b.inputs[b.parents.index(older)]
        assert old[anchor_payment] == (older,) and new[anchor_payment] == (older, v)
        assert all(old[m] == (p,) and new[m] == (p, v) for m, p in zip(b.inputs, b.parents, strict=True))
        handoffs.append({"previous_enrolled_holder": older, "next_enrolled_holder": v, "paid_identity": anchor_payment})
        is_return = frame.words[v][-1] == order[0]
        assert is_return == (len(handoffs) % len(order) == 0)
        if not is_return:
            continue
        assert not used.intersection(b.inputs)
        used.update(b.inputs)
        assert all(new[m] == (v,) for m in b.fresh)
        receipts.append({"handoffs_from_founder": len(handoffs), "new_receiver": v, "actual_parents": b.parents,
                         "actual_paid_names": b.inputs, "fresh_names_disclosed_for_audit": b.fresh,
                         "literal_owned_word_length_in_originals": len(frame.words[v])})
    assert len(receipts) == CUTS // len(order)
    return receipts, handoffs


def all_local_pin_checks(law):
    report = {}
    for paid in product((0, 1), repeat=2):
        legal = allowed(law, paid)
        assert legal
        alternatives = {}
        for i in (0, 1):
            for value in (0, 1):
                fibers = [bits(bank) for bank in legal if bank[i] == value]
                assert fibers
                alternatives[f"{i}|{value}"] = fibers
        report[bits(paid)] = {"whole_bank_support": list(map(bits, legal)), "focal_slot_and_desired_value": alternatives}
    return report


def extend(law, before, frame, pins):
    """Fill all actual births, with supplied pins only on the two designated banks."""
    word = list(before)
    for row in frame.births:
        independent_bank = allowed(law, pick(before, row.inputs))
        quiet = pick(frame.reference, row.fresh)
        eligible = tuple(bank for bank in independent_bank
                         if all(pins.get(i, value) == value for i, value in zip(row.fresh, bank, strict=True)))
        assert eligible
        chosen = min(eligible, key=lambda bank: (sum(a != b for a, b in zip(bank, quiet, strict=True)), bank))
        assert row.fresh == tuple(range(len(word), len(word) + 2))
        word.extend(chosen)
    after = tuple(word)
    assert after[:len(before)] == before and all(after[i] == v for i, v in pins.items())
    check_word(law, after, frame.holdings)
    return after


def signal_history(law, frames, receipts, targets):
    pins_by_cut = {}
    for entry, bit in zip(receipts, targets, strict=True):
        stage = entry["handoffs_from_founder"]
        p, q = entry["actual_paid_names"]
        ref_bit = frames[stage].reference[p]
        assert ref_bit == frames[stage].reference[q] and bit in (0, 1)
        pins_by_cut[stage - 1] = {p: ref_bit, q: ref_bit ^ bit}
    words = [frames[0].reference]
    for i, frame in enumerate(frames[1:], 1):
        words.append(extend(law, words[-1], frame, pins_by_cut.get(i, {})))
    recorded = []
    for row in receipts:
        i, marked = row["handoffs_from_founder"], row["actual_paid_names"]
        on_birth, again = pick(words[i], marked), pick(words[-1], marked)
        assert on_birth == again
        recorded.append({**row, "incoming_values": bits(on_birth), "signal": on_birth[0] ^ on_birth[1],
                         "own_fresh_values_for_audit_only": bits(pick(words[i], row["fresh_names_disclosed_for_audit"])),
                         "reread_same_pair_in_final_holdings": bits(again), "additional_returns_by_reread": 0})
    assert tuple(read["signal"] for read in recorded) == tuple(targets)
    return words, {"actual_complete_words_by_consecutive_cut": list(map(bits, words)), "receipts": recorded}


def pair_support(law, frames, receipts, valued_history):
    entries = []
    for row in receipts:
        i = row["handoffs_from_founder"]
        before = valued_history[i - 2]
        early, now = frames[i - 1], frames[i]
        p, q = row["actual_paid_names"]
        payers = {mark: birth for birth in early.births for mark in birth.fresh}
        assert payers[p].knot != payers[q].knot
        assert set((payers[p].knot, payers[q].knot)) == set(row["actual_parents"])
        local = {b.knot: allowed(law, pick(before, b.inputs)) for b in early.births}
        total = 1
        for support in local.values():
            total *= len(support)
        fibers = {}
        for x, y in product((0, 1), repeat=2):
            pins = {p: x, q: y}
            count = 1
            for birth in early.births:
                count *= sum(all(pins.get(mark, v) == v for mark, v in zip(birth.fresh, w, strict=True))
                             for w in local[birth.knot])
            assert count
            through_parent_birth = extend(law, before, early, pins)
            through_actual_receipt = extend(law, through_parent_birth, now, {})
            assert pick(through_actual_receipt, (p, q)) == (x, y)
            fibers[bits((x, y))] = {"number_of_joint_payer_cohort_words": count,
                                   "actual_word_at_both_payers_birth": bits(through_parent_birth),
                                   "actual_word_at_receipt": bits(through_actual_receipt)}
        assert sum(f["number_of_joint_payer_cohort_words"] for f in fibers.values()) == total
        entries.append({"handoffs_to_receipt": i, "actual_fixed_prefix_before_payers_birth": bits(before),
                        "pledged_outgoing_marks_from_distinct_fresh_banks": (p, q),
                        "full_joint_payer_cohort_support": total, "receipt_pair_support": fibers})
    return entries


def reconstruct_tally(law, holdings, values):
    info = PHASE["read_current"](holdings, law)
    anchor = info.original_order[0]
    chain = sorted((len(word), holder) for holder, word in info.words.items() if word[0] == anchor)
    assert [n for n, _ in chain] == list(range(1, info.cut + 2))
    result = []
    for (length, receiver), (_, old_receiver) in zip(chain[1:], chain[:-1], strict=True):
        ds = info.parents[receiver]
        assert len(ds) == 2 and old_receiver in ds
        paid = []
        for old in sorted(ds):
            one, = set(holdings[old]) & set(holdings[receiver])
            paid.append(one)
        is_return = info.words[receiver][-1] == anchor
        assert is_return == ((length - 1) % len(info.original_order) == 0)
        if is_return:
            x, y = pick(values, paid)
            result.append({"handoffs_from_founder": length - 1, "new_receiver": receiver, "actual_parents": sorted(ds),
                           "actual_paid_names": sorted(paid), "signal": x ^ y})
    return result


def check_tally(law, frames, words, receipts):
    last = frames[-1]
    expected = [{key: (sorted(row[key]) if isinstance(row[key], tuple) else row[key])
                 for key in ("handoffs_from_founder", "new_receiver", "actual_parents", "actual_paid_names", "signal")}
                for row in receipts]
    ordinary = reconstruct_tally(law, last.holdings, words[-1])
    assert ordinary == expected
    knots = tuple(reversed(range(len(last.holdings))))
    largest = len(words[-1]) - 1
    renamed = tuple(tuple(largest - m for m in last.holdings[k]) for k in knots)
    renamed_tally = reconstruct_tally(law, renamed, words[-1][::-1])
    reflected = [{**r, "new_receiver": knots[r["new_receiver"]],
                  "actual_parents": sorted(knots[k] for k in r["actual_parents"]),
                  "actual_paid_names": sorted(largest - m for m in r["actual_paid_names"])} for r in renamed_tally]
    assert reflected == ordinary
    return {"reconstructed_from_final_retained_holdings": ordinary,
            "reconstructed_totals": {"new_returns": len(ordinary), "signal_returns": sum(r["signal"] for r in ordinary)},
            "coherent_renaming_of_holders_and_marks": True}


def local_view(frame, word, radius):
    graph = NX.Graph()
    own = owner_map(frame.holdings)
    root = ("holder", frame.by_phase[0])
    for m, holders in own.items():
        mark = ("distinction", m)
        graph.add_node(mark, color=("distinction", word[m], len(holders)))
        for h in holders:
            holder = ("holder", h)
            graph.add_node(holder, color=("holder", holder == root))
            graph.add_edge(holder, mark)
    view = graph.subgraph(NX.single_source_shortest_path_length(graph, root, cutoff=2 * radius + 1)).copy()
    return view


def local_view_controls(frames, words, receipts):
    recognized = {r["handoffs_from_founder"] for r in receipts}
    appearances = []
    for a, b in ((10, 12), (10, 20)):
        rows = []
        for radius in range(5):
            left, right = (local_view(frames[i], words[i], radius) for i in (a, b))
            match = NX.algorithms.isomorphism.GraphMatcher(left, right, node_match=lambda p, q: p["color"] == q["color"])
            assert match.is_isomorphic()
            rows.append({"radius_in_holder_shared_steps": radius, "matching_valued_physical_incidence": True,
                         "holder_count": sum(v[0] == "holder" for v in left),
                         "distinction_count": sum(v[0] == "distinction" for v in left)})
        appearances.append({"actual_newborn_holders": [frames[i].by_phase[0] for i in (a, b)],
                            "replayed_handoff_positions": (a, b), "is_return": [i in recognized for i in (a, b)],
                            "different_complete_history_return_tallies": [sum(j <= i for j in recognized) for i in (a, b)],
                            "matched_views": rows})
    return appearances


def local_signal_tally_control(law, frames, quiet, receipts):
    """One early signal, then a wholly quiet future boundary on the same allocation."""
    first = receipts[0]
    at = first["handoffs_from_founder"]
    _, changed_mark = first["actual_paid_names"]
    source_payer, = (b for b in frames[at - 1].births if changed_mark in b.fresh)
    value = frames[at - 1].reference[changed_mark]
    actual = quiet[:at - 1]
    actual.append(extend(law, actual[-1], frames[at - 1], {changed_mark: 1 - value}))
    source_output = [i for i in source_payer.fresh if actual[-1][i] != frames[at - 1].reference[i]]
    next_pins = {}
    absorber = None
    if law == "parity":
        assert len(source_output) == 2
        two_parents = {b.knot for b in frames[at].births if set(b.inputs).intersection(source_output)}
        assert len(two_parents) == 2
        absorber, = (b for b in frames[at + 1].births if set(b.parents) == two_parents)
        next_pins = {i: 1 - frames[at].reference[i] for i in absorber.inputs}
    else:
        assert source_output == [changed_mark]
    actual.append(extend(law, actual[-1], frames[at], next_pins))
    for frame in frames[at + 1:]:
        actual.append(extend(law, actual[-1], frame, {}))
    earlier_deviations = [i for i, (x, y) in enumerate(zip(actual[-1], quiet[-1], strict=True)) if x != y]
    first_restored_boundary = at + 1 if law == "parity" else at
    assert earlier_deviations and max(earlier_deviations) < len(quiet[first_restored_boundary - 1])
    totals = [sum(row["signal"] for row in reconstruct_tally(law, frames[-1].holdings, h[-1])) for h in (quiet, actual)]
    assert totals == [0, 1]
    for radius in range(5):
        left, right = (local_view(frames[-1], w[-1], radius) for w in (quiet, actual))
        assert left.nodes.keys() == right.nodes.keys() and left.edges.keys() == right.edges.keys()
        assert all(left.nodes[v] == right.nodes[v] for v in left)
    return {"same_holder_same_handoff_count": frames[-1].by_phase[0], "matching_valued_views_through_radius": 4,
            "actual_signal_tallies_quiet_then_early_signal": totals,
            "same_retained_holdings_at_comparison": True, "remaining_old_differences": earlier_deviations,
            "first_restored_quiet_fresh_bank_cut": first_restored_boundary,
            "parity_receiving_child_for_two_deviations": absorber.knot if absorber else None,
            "early_signal_actual_complete_words_by_cut": list(map(bits, actual))}


def block_prefix(length):
    prefix = []
    block = 0
    while len(prefix) < length:
        count = 1 if block == 0 else 1 << (1 << (block - 1))
        prefix.extend((block % 2,) * min(count, length - len(prefix)))
        block += 1
    return tuple(prefix)


def quiet_missing_control(document):
    controls = {}
    for setting, replay in document["replay"].items():
        trace = replay["completely_quiet_M_physical_trace"]
        assert trace["target_read"]["outcome"] == "missing"
        assert trace["third_cut"]["status"] == "extend"
        controls[setting] = {"archived_named_target": trace["target_read"], "new_returns_added_to_tally": 0,
                             "genuinely_quiet_earlier_cut_completes": True}
    return controls


def audit_geometry(frames):
    return [{"enrolled_holder": f.by_phase[0], "cohort_by_phase": f.by_phase,
             "births": [{"knot": b.knot, "parents": b.parents, "paid": b.inputs, "fresh": b.fresh} for b in f.births]}
            for f in frames]


def run_law(source, law, archive):
    order, marker, frames, binding_checks = structural_replay(source, law, archive)
    receipts, handoffs = receiver_trace(frames, order)
    assert [r["handoffs_from_founder"] for r in receipts] == list(range(len(order), CUTS + 1, len(order)))
    patterns = {"quiet": (0,) * len(receipts), "every_return_signals": (1,) * len(receipts),
                "mixed_alternating": tuple(k % 2 for k in range(len(receipts))),
                "initial_nonconvergent_block_schedule": block_prefix(len(receipts))}
    signals = {}
    for scenario, pattern in patterns.items():
        words, trace = signal_history(law, frames, receipts, pattern)
        signals[scenario] = {**trace, "no_log_tally_and_rename": check_tally(law, frames, words, trace["receipts"])}
        if scenario == "quiet":
            quiet = words
            assert quiet == [f.reference for f in frames]
            signals[scenario]["unique_minimum_filling_agrees"] = True
        elif scenario in ("every_return_signals", "mixed_alternating"):
            signals[scenario]["joint_support_at_each_receipt_from_its_own_fixed_predecessor"] = pair_support(law, frames, receipts, words)
    return {"marked_order_recovered_from_actual_holdings": order, "anchor_identification": marker,
            "named_funded_ordinary_cohorts": audit_geometry(frames), "actual_enrolled_handoffs": handoffs,
            "birth_order_cross_checks_against_archived_peeler": len(frames),
            "tested_structural_allocations_with_lawful_quiet_extension": binding_checks,
            "quiet_founder_absolute_and_reference_word": bits(frames[0].reference),
            "physical_positive_returns": receipts, "one_named_fresh_slot_support": all_local_pin_checks(law),
            "quiet_history_joint_support_at_each_receipt_from_same_fixed_predecessor": pair_support(law, frames, receipts, quiet),
            "quiet_bounded_valued_local_view_controls": local_view_controls(frames, quiet, receipts),
            "same_age_local_signal_tally_control": local_signal_tally_control(law, frames, quiet, receipts),
            "continuous_valued_histories": signals}


def main():
    assert sha256(FREEZE.read_bytes()).hexdigest() == FROZEN_SHA
    archive = json.loads(PHASE_ARCHIVE.read_text())["cases"]["five_odd"]
    source = PHASE["source_cases"]()["five_odd"]
    assert source == tuple(map(tuple, archive["original_supports"]))
    results = {law: run_law(source, law, archive["by_law"][law]) for law in LAWS}
    for key in ("named_funded_ordinary_cohorts", "actual_enrolled_handoffs", "physical_positive_returns",
                "quiet_founder_absolute_and_reference_word", "quiet_bounded_valued_local_view_controls"):
        assert results["parity"][key] == results["nae"][key]
    output = {"schema": "five-phase-ordinary-signal-receipts-v1", "archived_five_odd_source": source, "laws": results,
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in (FREEZE, PHASE_SCRIPT, PHASE_ARCHIVE, PHASE["FIXTURE"], QUIET_CONTROL)},
              "archived_missing_one_shot_target_control": quiet_missing_control(json.loads(QUIET_CONTROL.read_text())),
              "value_convention": {"common_complement_preserves_disagreement": True,
                                   "flipping_only_one_name_in_the_read_convention_changes_disagreement": True},
              "nonconvergent_schedule_prefix_rule": "Alternating constant blocks of lengths 1,2,4,16,256,...; each length after the second is the square of the previous one.",
              "compatible_stream_construction": "Fix the value-independent physical allocation. One cut before each actual return, fix one fresh coordinate at each of its distinct payers to equal or unequal values as desired. Complete each bank lawfully, using a reference-nearest then lexical choice for the displayed continuation. Every other cut permits a legal local extension. A return's pair uses a different pair of physical names from all other returns.",
              "enrolled_founder_positive_returns": 0, "weighting": None}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
