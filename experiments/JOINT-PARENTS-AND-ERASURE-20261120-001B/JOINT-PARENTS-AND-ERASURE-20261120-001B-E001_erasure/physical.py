"""Replay the frozen spending, closing and ordinary merging examples."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
from importlib import util
from io import BytesIO
from itertools import combinations
import json
from math import isqrt, prod
import os
from pathlib import Path
import resource
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
FREEDOM = "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A"
SIGNS = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A"
MOTION = "MOTION-LAW-20261119-001"
ORDINARY = ROOT / "experiments" / FREEDOM / f"{FREEDOM}-E001_freedom" / "ordinary.py"
ARCHIVE = ROOT / "artifacts" / SIGNS / f"{SIGNS}-E001_sign_records" / "archived_events.json.gz"
ARCHIVE_CODE = ROOT / "experiments" / SIGNS / f"{SIGNS}-E001_sign_records" / "archived_events.py"
MOTION_CODE = ROOT / "experiments" / MOTION / f"{MOTION}-E001_rules"
LAWS = ("parity", "nae")
GROWTH_FIXTURES = (
    ("one_ternary", ((0, 1, 2),), (3, 5), 1),
    ("three_mutual_ternaries", ((0, 1, 3), (0, 2, 4), (1, 2, 5)), (7, 30), 3),
    ("three_knots_with_extra_loose_mark", ((0, 1, 3, 6), (0, 2, 4), (1, 2, 5)), (7, 30), 3),
)
PREPARATIONS = {"a": (1, 0), "b": (0, 1), "plus": (1, 1), "minus": (1, -1)}


def bitmask(names):
    return sum(1 << i for i in names)


def names(word):
    return [i for i in range(word.bit_length()) if word >> i & 1]


def sign(word):
    return 1 - 2 * (word.bit_count() % 2)


def owners(holdings):
    owned = defaultdict(list)
    for knot, support in enumerate(holdings):
        for mark in support:
            owned[mark].append(knot)
    return dict(owned)


def faults(word, masks, law):
    if law == "parity":
        return [i for i, m in enumerate(masks) if sign(word & m) < 0]
    if law == "nae":
        return [i for i, m in enumerate(masks) if (word & m) in (0, m)]
    raise ValueError(law)


def full_support(holdings, law):
    masks = tuple(map(bitmask, holdings))
    return [w for w in range(1 << (1 + max(map(max, holdings)))) if not faults(w, masks, law)]


def projection_checks(holdings, support, law):
    records = []
    for i, place in enumerate(holdings):
        local = tuple(sorted({sum(((word >> b) & 1) << j for j, b in enumerate(place)) for word in support}))
        n = len(place)
        own = tuple(x for x in range(1 << n) if not faults(x, ((1 << n) - 1,), law))
        k2 = all(len({w & ~(1 << j) for w in local}) == 1 << (n-1) for j in range(n))
        assert local == own and k2 and 0 < len(local) < 1 << n, (i, local, own)
        records.append(dict(knot=i, distinctions=place, allowed_local_words=local, K1=True, K2=True, K3=True))
    return records


@cache
def ordinary_engine():
    sys.path.insert(0, str(ORDINARY.parent))
    spec = util.spec_from_file_location("erasure_archived_growth", ORDINARY)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def crossed(first, second, *, access, target=None, explicit=()):
    """Push forward singleton laws, keeping all the crossed ordinary preparations."""
    assert sum(first.values()) == sum(second.values()) == 1
    all_outcomes = sorted(set(first) | set(second) | set(explicit))
    rows = []
    common_keys = []
    for outcome in all_outcomes:
        a = first.get(outcome, Fraction(0))
        b = second.get(outcome, Fraction(0))
        m = (a+b) / 2
        if a and b:
            common_keys.append(outcome)
        rows.append(dict(outcome=outcome, a=a, b=b, mixture=m, plus=m, minus=m))
    pooled = [i for i, o in enumerate(all_outcomes) if target(o)] if target is not None else None
    return dict(access=access, outcomes=rows, target_pool_indices=pooled, shared_outcomes=common_keys,
                ordinary_sign_contrast=Fraction(0), singleton_tv=sum(abs(r["a"]-r["b"]) for r in rows)/2)


def both_weightings(lists, key, *, access, target=None, explicit=()):
    laws = []
    for i, items in enumerate(lists):
        totals = Counter(key(i, item) for item in items)
        laws.append({o: Fraction(count, len(items)) for o, count in totals.items()})
    return crossed(*laws, access=access, target=target, explicit=explicit)


def exchange_binary_labels(record):
    tables = [{not r["outcome"]: r[k] for r in record["outcomes"]} for k in ("a", "b")]
    return crossed(*tables, access="same ordinary observations, exchanged answer labels", target=bool, explicit=(False, True))


def exact_radical(rational_part, coefficient, radicand):
    """Represent rational_part + coefficient / sqrt(radicand) without rounding."""
    root = isqrt(radicand)
    exact = rational_part if not coefficient else rational_part + coefficient / root if root**2 == radicand else None
    return dict(rational_part=rational_part, sqrt_denominator=radicand, coefficient=coefficient, rational_value=exact)


def binary_ports(overlap, counts):
    half = Fraction(1, 2)
    result = {}
    for label, coefficient in (("a", 0), ("b", 0), ("mixture", 0), ("plus", overlap), ("minus", -overlap)):
        result[label] = [exact_radical(half, Fraction(c, 2), prod(counts)) for c in (coefficient, -coefficient)]
    return result


def verify_literal_ports(groups, change, records, *, copied=False):
    supports = {(word, i if copied else 0): i for i, group in enumerate(groups) for word in group}
    counts = list(map(len, groups))
    assert len(supports) == sum(counts)
    full = supports.keys() | {(word ^ change, address) for word, address in supports}
    for label, weights in PREPARATIONS.items():
        normalization = 4 * sum(v*v for v in weights)
        for orientation, predicted in zip((1, -1), records[label], strict=True):
            diagonal = Fraction(0)
            off_diagonal = 0
            for key in full:
                word, address = key
                contributions = [0, 0]
                if key in supports:
                    i = supports[key]
                    contributions[i] += weights[i]
                partner = (word ^ change, address)
                if partner in supports:
                    j = supports[partner]
                    contributions[j] += orientation * weights[j]
                diagonal += sum(Fraction(v*v, counts[i]) for i, v in enumerate(contributions))
                off_diagonal += 2 * prod(contributions)
            assert exact_radical(diagonal/normalization, Fraction(off_diagonal, normalization), prod(counts)) == predicted
    assert all(row["rational_value"] == Fraction(1, 2) for row in records["mixture"])


def complementary_copy_read(overlap, counts):
    """Read the supplied orthogonal copy in its complementary basis and relabel ports."""
    ports = binary_ports(overlap, counts)
    half = Fraction(1, 2)
    branches = {}
    for label, original in ports.items():
        pair = []
        for outcome in (0, 1):
            conditional = original if outcome == 0 else list(reversed(original))
            joint = [exact_radical(half*q["rational_part"], half*q["coefficient"], q["sqrt_denominator"])
                     for q in conditional]
            pair.append(dict(copy_character=outcome, character_mass=half, conditional_ports=conditional,
                             joint_character_and_ports=joint, exchange_port_labels=bool(outcome)))
        branches[label] = pair
    return dict(character_records=branches, corrected_ports=ports)


def erased_source_pair(old_words, erased):
    """Complete supplied character instrument, in the original ordinary basis."""
    removed = tuple(sorted(erased))
    erase_mask = bitmask(removed)
    dimension = 1 << len(erased)
    remaining = tuple(sorted({w & ~erase_mask for w in old_words}))
    reports = {}
    for label, coefficients in PREPARATIONS.items():
        source_mass = sum(c*c for c in coefficients)
        outputs = []
        for r in range(dimension):
            lifted = bitmask(b for i, b in enumerate(removed) if r >> i & 1)
            amplitudes = tuple(sum(c * sign(w & lifted) for w, c in zip(old_words, coefficients, strict=True)
                                   if w & ~erase_mask == y) for y in remaining)
            norm = sum(c*c for c in amplitudes)
            outputs.append(dict(character=r, probability=Fraction(norm, dimension * source_mass),
                                unnormalized_remaining_coefficients=amplitudes,
                                conditional_coefficient_sqrt_denominator=norm if norm else None))
        assert sum(o["probability"] for o in outputs) == 1
        for i, y in enumerate(remaining):
            for j, y2 in enumerate(remaining):
                ignored_outcome = sum(Fraction(o["unnormalized_remaining_coefficients"][i] *
                                              o["unnormalized_remaining_coefficients"][j], dimension * source_mass)
                                      for o in outputs)
                traced_directly = sum(Fraction(c1*c2, source_mass)
                                      for w1, c1 in zip(old_words, coefficients, strict=True)
                                      for w2, c2 in zip(old_words, coefficients, strict=True)
                                      if w1 & erase_mask == w2 & erase_mask and w1 & ~erase_mask == y and w2 & ~erase_mask == y2)
                assert ignored_outcome == traced_directly
        reports[label] = outputs
    mixture = []
    for i, (a, b) in enumerate(zip(reports["a"], reports["b"], strict=True)):
        weight = (a["probability"] + b["probability"]) / 2
        conditional = [Fraction(int(y == old_words[0] & ~erase_mask) + int(y == old_words[1] & ~erase_mask), 2)
                       for y in remaining]
        mixture.append(dict(character=i, probability=weight, conditional_diagonal=conditional if weight else None))
    reports["mixture"] = mixture
    assert sum(o["probability"] for o in mixture) == 1
    return dict(erased=removed, retained_ordinary_words=remaining, effects=reports)


def growth_trial(label, old, selected, mark, law):
    source = full_support(old, law)
    assert all(w in source for w in selected) and bool((selected[0] ^ selected[1]) & (1 << mark))
    source_projections = projection_checks(old, source, law)
    turn, raw = ordinary_engine().advance([list(s) for s in old], law, cap=False)
    grown = tuple(map(tuple, raw))
    assert turn["status"] in ("grown", "closed") and grown[:len(old)] == old
    previous_width = 1 + max(map(max, old))
    width = 1 + max(map(max, grown))
    old_mask = (1 << previous_width)-1
    full_mask = (1 << width)-1
    fresh = full_mask ^ old_mask
    reached = full_support(grown, law)
    reached_projections = projection_checks(grown, reached, law)
    by_old = defaultdict(list)
    for w in reached:
        by_old[w & old_mask].append(w)
    assert set(by_old) == set(source)
    extensions = [by_old[w] for w in selected]
    assert not set(extensions[0]) & set(extensions[1])
    before_owners, after_owners = map(owners, (old, grown))
    assert len(before_owners[mark]) == 1 and len(after_owners[mark]) == 2
    spent = sorted(b for b in before_owners if len(before_owners[b]) == 1 and len(after_owners[b]) == 2)
    paid = sorted({b for child in grown[len(old):] for b in child if b < previous_width})
    assert spent == paid and mark in paid
    loose = bitmask(b for b, held in after_owners.items() if len(held) == 1)
    assert (turn["status"] == "closed") == (loose == 0)
    differing = selected[0] ^ selected[1]
    mark_mask = 1 << mark

    reading_masks = {
        "full_word": full_mask,
        "forget_named_mark": full_mask ^ mark_mask,
        "forget_paid_marks": full_mask ^ bitmask(paid),
        "forget_differing_marks": full_mask ^ differing,
        "only_post_cut_loose": loose,
        "only_fresh_marks": fresh,
    }
    reads = {}
    for name, observed in reading_masks.items():
        access = "complete literal post-word" if name == "full_word" else "observer projection of the retained physical word"
        test = (lambda w: bool(w & mark_mask)) if observed & mark_mask else None
        reads[name] = both_weightings(extensions, lambda _, w: w & observed, access=access, target=test)
        copy_test = (lambda row: bool(row[1] & mark_mask)) if test is not None else None
        reads[name + "_with_old_word_copy"] = both_weightings(
            extensions, lambda i, w: (selected[i], w & observed), access="supplied retained old-word copy", target=copy_test)
    reads["named_mark_value"] = both_weightings(extensions, lambda _, w: bool(w & mark_mask),
                                                 access="ordinary read of the retained mark", target=bool, explicit=(False, True))
    reads["born_holder_and_spending"] = crossed({True: Fraction(1)}, {True: Fraction(1)},
                                                access="same funded cut observed on either word", target=bool, explicit=(False, True))
    reads["mark_changed_by_growth"] = crossed({False: Fraction(1)}, {False: Fraction(1)},
                                               access="ordinary value before and after the cut", target=bool, explicit=(False, True))
    reads["named_mark_value_labels_exchanged"] = exchange_binary_labels(reads["named_mark_value"])

    fresh_words = [{w & fresh for w in group} for group in extensions]
    counts = list(map(len, extensions))
    overlap = len(fresh_words[0] & fresh_words[1])
    assert list(map(len, fresh_words)) == counts
    assert all(sum((w ^ differing) in extensions[1-i] for w in extensions[i]) == overlap for i in (0, 1))
    before = binary_ports(1, (1, 1))
    coherent = binary_ports(overlap, counts)
    copied = binary_ports(0, counts)
    verify_literal_ports([[w] for w in selected], differing, before)
    verify_literal_ports(extensions, differing, coherent)
    verify_literal_ports(extensions, differing, copied, copied=True)
    attempted = []
    masks = tuple(map(bitmask, grown))
    for word, group in zip(selected, extensions, strict=True):
        failures = []
        for tail in range(1 << (width-previous_width)):
            post = word | (tail << previous_width)
            bad = faults(post, masks, law)
            assert (post in group) == (not bad)
            if bad:
                failures.append(dict(attempted_word=post, failed_knots=bad))
        attempted.append(dict(source_word=word, source_mass=Fraction(1, 2), extensions=group,
                              conditional_mass_per_extension=Fraction(1, len(group)),
                              joint_mass_per_extension=Fraction(1, 2*len(group)), rejected_completions=failures))

    return dict(case=label, law=law, source_words=selected, target_mark=mark,
                source_holdings=old, reached_holdings=grown, turn=turn, paid_marks=paid,
                holders_of_target_before=before_owners[mark], holders_of_target_after=after_owners[mark],
                source_projections=source_projections, reached_projections=reached_projections,
                extensions=attempted, extension_counts=counts, all_extension_groups=dict(sorted(by_old.items())),
                fresh_overlap_count=overlap, matched_fresh_words=sorted(fresh_words[0] & fresh_words[1]),
                fresh_overlap=exact_radical(Fraction(0), Fraction(overlap), prod(counts)),
                ports=dict(complete_pair_difference=names(differing), before_growth=before,
                           coherent_uniform_conditional_extensions=coherent,
                           copied_orthogonal_old_word=copied,
                           erased_orthogonal_record_with_supplied_complementary_read_and_feed_forward=complementary_copy_read(overlap, counts),
                           native_ports=None),
                supplied_eraser_on_source=dict(named_mark=erased_source_pair(selected, (mark,)),
                                               all_differing_marks=erased_source_pair(selected, names(differing))),
                reading_masks=reading_masks, readings=reads)


def dag_adjacency(nodes):
    outgoing = {}
    incoming = defaultdict(list)
    for node in nodes:
        ident = node["id"]
        choices = node["enabled_events"]
        outgoing[ident] = {edge["target"]: edge for edge in choices}
        assert len(outgoing[ident]) == len(choices)
        for edge in choices:
            dst = edge["target"]
            assert nodes[dst]["depth"] == node["depth"]+1
            incoming[dst].append((ident, edge))
    for row in incoming.values():
        row.sort(key=lambda r: (r[0], r[1]["event_id"]))
    return outgoing, incoming


def first_diamond(nodes, outgoing, incoming):
    for record in sorted(nodes, key=lambda row: (row["depth"], row["id"])):
        parent = record["id"]
        for a, b in combinations(sorted(outgoing[parent]), 2):
            shared = sorted(outgoing[a].keys() & outgoing[b].keys())
            if shared:
                return dict(fork=parent, a=a, b=b, target=shared[0], selection="first two-event fork")
    for target in sorted(incoming, key=lambda t: (nodes[t]["depth"], t)):
        candidates = sorted({src for src, _ in incoming[target]})
        if len(candidates) >= 2:
            a, b = candidates[:2]
            assert nodes[a]["depth"] == nodes[b]["depth"]
            return dict(fork=None, a=a, b=b, target=target, selection="first equal-depth common next target")
    return None


def complete_ordinary_two_ports():
    ports = binary_ports(1, (1, 1))
    selected = {}
    for label, branch in ports.items():
        p, q = (term["rational_value"] for term in branch)
        assert p + q == 1
        selected[label] = dict(selection_mass=p, joint_selection_and_target_mass=p,
                               conditional_target_given_selection=Fraction(1) if p else None,
                               complement_mass=q)
    return {
        "ideal_ordinary_merge_without_path_mixing": {
            k: [Fraction(1), Fraction(0)] for k in (*PREPARATIONS, "mixture")},
        "incorrect_copy_to_one_amplitude": {
            k: Fraction((a+b)**2, a*a+b*b) for k, (a, b) in PREPARATIONS.items()} | {"mixture": Fraction(1)},
        "normalized_supplied_sum_difference": ports,
        "postselected_supplied_positive_port": selected,
    }


@cache
def archive_switch_model():
    sys.path.insert(0, str(MOTION_CODE))
    from sources import cases
    from uniform_exchange import named_fixture

    fixture, = (row for row in cases() if row["id"] == "T4")
    model, _, _, _ = named_fixture(fixture)
    return model


def switch_diamond(direction, stage, events, direction_index):
    trace = direction["traces"]["loaded"]
    nodes = trace["nodes"]
    assert all(i == row["id"] for i, row in enumerate(nodes))
    outgoing, incoming = dag_adjacency(nodes)
    picked = first_diamond(nodes, outgoing, incoming)
    if picked is None:
        return dict(direction=direction_index, selection="exhausted complete physical loaded DAG")
    a, b, target = (picked[k] for k in ("a", "b", "target"))
    fork = picked["fork"]
    target_word = bitmask(nodes[target]["word"])
    admit = {}
    inputs = {}
    masks = tuple(map(bitmask, stage))
    model = archive_switch_model()
    assert tuple(map(tuple, stage)) == model.stage.stars

    checked = {a, b, target, *outgoing[a], *outgoing[b]}
    if fork is not None:
        checked.add(fork)
    for node_id in sorted(checked):
        w = bitmask(nodes[node_id]["word"])
        old_events = {frozenset(events[edge["event_id"]]["distinctions"]) for edge in outgoing[node_id].values()}
        assert old_events == model.enabled(frozenset(names(w)))
        by_law = {law: faults(w, masks, law) for law in LAWS}
        assert not by_law["parity"] and by_law["nae"] == nodes[node_id]["failed_nae_knots"]
        admit[node_id] = dict(word=w, failed_knots=by_law)
    assert all(admit[i]["failed_knots"]["nae"] for i in (a, b))

    @cache
    def paths_to(node):
        if node == 0:
            return (((), Fraction(1)),)
        histories = []
        for ancestor, e in incoming[node]:
            for prefix, p in paths_to(ancestor):
                histories.append((prefix + ((ancestor, e["event_id"], node),), p * Fraction(e["chance_given_source"])))
        assert len(histories) == nodes[node]["number_of_prefix_paths"]
        assert sum(p for _, p in histories) == Fraction(nodes[node]["probability_of_visit"])
        return tuple(histories)

    local_audit = {}
    for label, node_id in (("a", a), ("b", b)):
        word = bitmask(nodes[node_id]["word"])
        attempts = []
        for successor, edge in sorted(outgoing[node_id].items()):
            observed = bitmask(nodes[successor]["word"])
            event = edge["event_id"]
            mask = bitmask(events[event]["distinctions"])
            assert word ^ mask == observed
            assert Fraction(edge["chance_given_source"]) == Fraction(1, len(outgoing[node_id]))
            attempts.append(dict(event_id=event, flipped_distinctions=names(mask), actual_post_word=observed,
                                 target=successor == target, conditional_probability=Fraction(edge["chance_given_source"]),
                                 inverse_input_from_word_and_event=observed ^ mask,
                                 same_event_enabled_at_image=event in {e["event_id"] for e in outgoing[successor].values()},
                                 ordinary_word_faults=admit[successor]["failed_knots"]))
        assert sum(e["conditional_probability"] for e in attempts) == 1
        initial_mass = Fraction(nodes[node_id]["probability_of_visit"])
        from_fork = Fraction(outgoing[fork][node_id]["unconditional_chance"]) if fork is not None else None
        inputs[label] = dict(state=node_id, word=word, attempts=attempts, mass_from_original_load=initial_mass,
                             mass_from_chosen_fork=from_fork,
                             mass_from_other_sources=initial_mass-from_fork if from_fork is not None else None,
                             immediate_predecessors=incoming[node_id])
        local_audit[label] = [dict(history=prefix, ordinary_mass_before_choice=p, conditional_to_word=p/initial_mass,
                                  extends_chosen_fork=(prefix[-1][0] == fork if prefix and fork is not None else None))
                              for prefix, p in paths_to(node_id)]
    distribution = [inputs[k]["attempts"] for k in ("a", "b")]

    def singleton_record(items, key):
        law = defaultdict(Fraction)
        for row in items:
            law[key(row)] += row["conditional_probability"]
        return law

    def read(key, tag, target_fn, explicit=()):
        return crossed(*(singleton_record(rows, key) for rows in distribution), access=tag, target=target_fn, explicit=explicit)

    readings = {
        "target_only": read(lambda row: row["target"], "read-only target comparison", bool, (False, True)),
        "post_word": read(lambda row: row["actual_post_word"], "complete literal post-word", lambda w: w == target_word),
        "latched_event_target": read(lambda row: (row["event_id"], row["actual_post_word"]),
                                     "supplied latch of the actual event with the post-word", lambda row: row[1] == target_word),
    }
    complete = []
    for label in ("a", "b"):
        outcomes = {}
        for past in local_audit[label]:
            for e in inputs[label]["attempts"]:
                record = (past["history"], e["event_id"], e["actual_post_word"])
                assert record not in outcomes
                outcomes[record] = past["conditional_to_word"] * e["conditional_probability"]
        complete.append(outcomes)
    readings["external_transcript"] = crossed(
        *complete, access="external history audit conditioned at the intermediate word", target=lambda row: row[2] == target_word)
    readings["target_labels_exchanged"] = exchange_binary_labels(readings["target_only"])
    assert not readings["latched_event_target"]["shared_outcomes"] and not readings["external_transcript"]["shared_outcomes"]
    assert readings["post_word"]["shared_outcomes"] == [target_word] or target_word in readings["post_word"]["shared_outcomes"]
    successes = [next(e for e in inputs[label]["attempts"] if e["target"]) for label in ("a", "b")]
    assert successes[0]["event_id"] != successes[1]["event_id"]
    assert not any(e["same_event_enabled_at_image"] for e in successes)
    history_control = {}
    if fork is not None:
        route_attempts = [dict(edge, selected=(i in (a, b))) for i, edge in sorted(outgoing[fork].items())]
        # The archive carries unconditional edge probabilities under the original launch measure.
        mass = sum(item["mass_from_chosen_fork"] for item in inputs.values())
        assert sum(Fraction(e["unconditional_chance"]) for e in outgoing[fork].values()) == Fraction(nodes[fork]["probability_of_visit"])
        history_control = dict(fork_mass=Fraction(nodes[fork]["probability_of_visit"]), attempt_edges=route_attempts,
                               mass_of_selected_input_history=mass,
                               singleton_mass_conditional_on_selected={label: o["mass_from_chosen_fork"]/mass for label, o in inputs.items()},
                               fork_predecessors=incoming[fork],
                               target_predecessors=incoming[target])
    return dict(direction=direction_index, source_donor_knot=direction["donor_knot"], source_receiver_knot=direction["receiver_knot"],
                selection=picked, inputs=inputs, target_word=target_word, law_admission=admit,
                nae_trial="inapplicable: both enrolled input words fail the literal law",
                prefix_paths_from_original_load=local_audit, original_launch_selection=history_control,
                introduced_ports=complete_ordinary_two_ports(), readings=readings)


def swap_readings(attempts, target_word):
    rows = [[row] for row in attempts]

    def read(extract, access, select, explicit=()):
        return both_weightings(rows, extract, access=access, target=select, explicit=explicit)

    readings = {
        "target_only": read(lambda i, e: e["target"], "read-only comparison with the stipulated target", bool, (False, True)),
        "post_word": read(lambda i, e: e["post_word"], "complete literal post-word", lambda w: w == target_word),
        "execution_flag": read(lambda i, e: e["executed"], "instruction execution indicator, recorded by a supplied latch", bool,
                               (False, True)),
        "latched_event_target": read(lambda i, e: (e["executed"], e["post_word"]),
                                     "supplied simultaneous action flag and complete post-word",
                                     lambda record: record[1] == target_word),
        "post_word_with_old_word_copy": read(lambda i, e: (e["input_word"], e["post_word"]),
                                              "supplied retained old-word copy", lambda record: record[1] == target_word),
        "external_transcript": read(lambda i, e: (e["input_word"], e["offered"], e["changed"], e["post_word"]),
                                    "external audit of input, offer, actual change and output", lambda record: record[3] == target_word),
    }
    readings["target_labels_exchanged"] = exchange_binary_labels(readings["target_only"])
    readings["execution_labels_exchanged"] = exchange_binary_labels(readings["execution_flag"])
    return readings


def replay_loose_swap(archive):
    archive_switch_model()
    from permutation_controls import apply, local_pools

    at = archive["loose_swap"]
    holdings = ((0, 1, 2), (0, 3, 4, 5))
    assert holdings == tuple(map(tuple, at["holdings"]))
    pools = local_pools(holdings)
    source = (bitmask((0, 1, 3)), bitmask((0, 2, 3)))
    flip = bitmask((1, 2))
    masks = tuple(map(bitmask, holdings))
    reports = {}
    for law in LAWS:
        old = at["laws"][law]["fixed_pair_both_orientations"]
        assert [bitmask(x["start"]) for x in old] == list(source)
        assert all(not faults(w, masks, law) for w in source)
        trials = {}
        for supplied_guard in (False, True):
            rows = []
            for i, w in enumerate(source):
                archived_twice = old[i]["two_calls"]["states"]
                swapped = bitmask(apply(frozenset(names(w)), {4}, pools))
                assert archived_twice == [names(w), names(swapped), names(w)]
                assert swapped == w ^ flip == source[1-i]
                ready = not supplied_guard or bool(w & (1 << 1))
                out = swapped if ready else w
                assert not faults(out, masks, law)
                moved = out != w
                assert moved == ready  # The enrolled pair has unequal loose values.
                rows.append(dict(input_word=w, mark_one_before=int(bool(w & 2)), offered=ready, executed=ready,
                                 changed=moved, post_word=out, target=out == source[1],
                                 actual_change=names(w ^ out), inverse_determined_by_latched_flag=out ^ (flip if ready else 0),
                                 reversed_next_offer=(not supplied_guard or bool(out & 2)),
                                 ready_target_and_complement_are_observer_readouts=True))
            readings = swap_readings(rows, source[1])
            assert not readings["latched_event_target"]["shared_outcomes"]
            assert not readings["post_word_with_old_word_copy"]["shared_outcomes"]
            assert not readings["external_transcript"]["shared_outcomes"]
            assert readings["post_word"]["shared_outcomes"] == ([source[1]] if supplied_guard else [])
            trials["guarded_if_mark_one_occupied" if supplied_guard else "original_swap_offer"] = dict(
                attempts=rows, readings=readings,
                introduced_ports=complete_ordinary_two_ports() if supplied_guard else None)
        reports[law] = trials
    return dict(holdings=holdings, named_input_pair=source, actual_loose_distinctions=(1, 2),
                guarded_control_distinction=1, named_target=source[1], laws=reports)


def source_hashes():
    files = {Path(__file__).resolve(), HERE / "contract.json",
             ROOT / "research" / HERE.parent.name / "preregistration.md",
             ORDINARY, ARCHIVE, ARCHIVE_CODE,
             ROOT / "docs/prompts/postulate_leads_checks/ways_squared.py",
             ROOT / "proofs" / SIGNS / f"{SIGNS}-P001_record_obstruction" / "proof.md"}
    for module in tuple(sys.modules.values()):
        original = getattr(module, "__file__", None)
        if original:
            path = Path(original).resolve()
            if path.is_relative_to(ROOT) and not path.is_relative_to(HERE):
                rel = path.relative_to(ROOT)
                if rel.parts[0] in ("experiments", "tools") and path.suffix == ".py":
                    files.add(path)
    previous = json.loads(gzip.decompress(ARCHIVE.read_bytes()))["sources"]
    for relative, expected in previous.items():
        path = ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
        files.add(path)
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}


def json_value(x):
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, dict):
        return {str(key): json_value(value) for key, value in x.items()}
    if isinstance(x, (tuple, list)):
        return [json_value(item) for item in x]
    return x


def encoded_artifact(record):
    payload = (json.dumps(json_value(record), sort_keys=True, separators=(",", ":")) + "\n").encode()
    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", filename="", mtime=0) as writer:
        writer.write(payload)
    return out.getvalue()


def run():
    archive = json.loads(gzip.decompress(ARCHIVE.read_bytes()))
    growth = [growth_trial(case, old, inputs, mark, law) for case, old, inputs, mark in GROWTH_FIXTURES for law in LAWS]
    switch = archive["uniform_switch"]
    diamonds = [switch_diamond(r, switch["holdings"], switch["events"], i) for i, r in enumerate(switch["directions"])]
    swaps = replay_loose_swap(archive)
    summary = dict(growth=[{k: row[k] for k in ("case", "law", "extension_counts", "fresh_overlap_count")} |
                            {"status": row["turn"]["status"], "retains_target_mark": bool(row["holders_of_target_after"]),
                             "complete_post_word_overlap": len(row["readings"]["full_word"]["shared_outcomes"])} for row in growth],
                   diamonds=[d["selection"] for d in diamonds],
                   supplied_guarded_same_post_word={law: swaps["laws"][law]["guarded_if_mark_one_occupied"]["readings"]["post_word"]["shared_outcomes"] for law in LAWS})
    return dict(schema=1, sources=source_hashes(), summary=summary, growth_cases=growth, switch_diamonds=diamonds,
                loose_swap=swaps,
                conventions=dict(ordinary_word="bits in little-endian order, integers encode the full named word",
                                 crossed_probabilities="a and b are full physical singletons, mixture is equal; plus and minus are independent externally signed comparisons on the same input pair",
                                 target_pool_indices="complement consists of the remaining indices; null when the named target is unavailable in that reading",
                                 weights="one half per crossed source word; uniform legal extensions or uniform enabled literal events as applicable",
                                 instrument_scope="separate explicit supplied projections supply all coherent ports; the ordinary interventions and guard menus only act on literal words"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require a byte-identical replay of the saved physical record.")
    args = parser.parse_args()
    for thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[thread_variable] = "1"
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = 4 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (limit if soft == resource.RLIM_INFINITY else min(limit, soft), hard))
    result = run()
    encoded = encoded_artifact(result)
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != encoded:
            print("Saved physical erasure receipt differs from this replay.", file=sys.stderr)
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(encoded)
    print(json.dumps(json_value(dict(receipt=str(OUT.relative_to(ROOT)), sha256=hashlib.sha256(encoded).hexdigest(), **result["summary"])), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
