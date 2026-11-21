"""Exact ordinary event, latch and controlled-choice replay at the registered later rejoin."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
from io import BytesIO
from itertools import combinations, product
import json
from math import isqrt
import os
from pathlib import Path
import resource
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
SIGN = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A"
ERA = "JOINT-PARENTS-AND-ERASURE-20261120-001B"
RULE = "MOTION-LAW-20261119-001"
ARCHIVE = ROOT / "artifacts" / SIGN / f"{SIGN}-E001_sign_records" / "archived_events.json.gz"
ERASURE = ROOT / "artifacts" / ERA / f"{ERA}-E001_erasure" / "physical.json.gz"
RULES = ROOT / "experiments" / RULE / f"{RULE}-E001_rules"
AUDIT = ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001/merger_audit.json"
FORK, INPUTS, TARGET = 11, (12, 13), 32
LAWS = ("parity", "nae")
PREPARATIONS = ("a", "b", "mixture", "plus", "minus")

# These public counterparts change only the path to the guide in the module
# docstring, from docs/KNOT_INTUITION.md to INTUITIONS.md. Each exact public
# digest is accepted alongside its canonical history in the switch archive.
PUBLIC_SOURCE_VARIANTS = {
    "tools/knotlab/__init__.py": "d569505fb5b4ae1e71eae74767fda5db30f559c80b57e8e4c7622b59812da983",
    "tools/knotlab/competition.py": "81459795b3dc6296413b37a5fe7807ebb1fabc1835fee31905cafd8df90715b9",
    "tools/knotlab/knots.py": "dc9a92e8bbf9b6a6a8b48dfa2708ee6d7e43313baadc9abce5d92b08dfe919ac",
}


def mask(places):
    return sum(1 << bit for bit in places)


@cache
def places(word):
    return tuple(i for i in range(word.bit_length()) if word >> i & 1)


def owners(holdings):
    result = defaultdict(list)
    for i, row in enumerate(holdings):
        for bit in row:
            result[bit].append(i)
    return dict(result)


def faults(word, masks, law):
    if law == "parity":
        return [i for i, m in enumerate(masks) if (word & m).bit_count() % 2]
    return [i for i, m in enumerate(masks) if word & m in (0, m)]


def actual_model():
    sys.path.insert(0, str(RULES))
    from sources import cases
    from uniform_exchange import named_fixture

    registered, = (row for row in cases() if row["id"] == "T4")
    model, first, second, _ = named_fixture(registered)
    return model, first, second


def exact_cases(nodes, actual, masks, catalog):
    """Check all archive offers against the unchanged native controller."""
    result = []
    incoming = defaultdict(list)
    for node in nodes:
        ident = node["id"]
        initial = mask(node["word"])
        centers = defaultdict(list)
        for center in sorted(actual.graph):
            for support in actual.enabled_at(center, frozenset(node["word"])):
                centers[str(mask(support))].append(center)
        assert set(centers) == {e["event_id"] for e in node["enabled_events"]}
        legal = {law: faults(initial, masks, law) for law in LAWS}
        assert not legal["parity"] and legal["nae"] == node["failed_nae_knots"]
        attempts = []
        for step in node["enabled_events"]:
            event, target = step["event_id"], step["target"]
            applied = initial ^ int(event)
            assert applied == mask(nodes[target]["word"])
            assert tuple(centers[event]) == tuple(step["at_knots"])
            assert list(places(int(event))) == catalog[event]["distinctions"]
            assert nodes[target]["depth"] == node["depth"] + 1
            assert Fraction(step["chance_given_source"]) == Fraction(1, len(node["enabled_events"]))
            p = Fraction(step["chance_given_source"])
            attempt = dict(event=event, marks=places(int(event)), target=target, post_word=applied,
                           centers=centers[event], conditional_mass=p,
                           launch_mass=Fraction(step["unconditional_chance"]))
            attempts.append(attempt)
            incoming[target].append((ident, attempt))
        result.append(dict(node=ident, depth=node["depth"], word=initial, distinctions=places(initial),
                           failed_knots=legal, launch_mass=Fraction(node["probability_of_visit"]),
                           predecessor_path_count=node["number_of_prefix_paths"], offers=attempts))
    return result, incoming


def assigned_product(full, fork, source_owners, loose):
    """Recover both incoming sibling groups and every actual corrective product block."""
    seed = full[fork]
    groups = defaultdict(set)
    cohort = {}
    for edge in seed["offers"]:
        names = set(edge["marks"]) & loose
        if len(names) != 2 or any(seed["word"] >> bit & 1 for bit in names):
            raise ValueError("the enrolled fork does not add two currently clear loose marks")
        for bit in names:
            held_at, = source_owners[bit]
            groups[held_at].add(bit)
    if sorted(map(len, groups.values())) != [4, 4]:
        raise ValueError("the two incoming holder rosters are not both four-way")
    panels = [tuple(sorted(group)) for _, group in sorted(groups.items())]
    for edge in seed["offers"]:
        if any((edge["post_word"] & mask(panel)).bit_count() != 1 for panel in panels):
            raise ValueError("the incoming occupation is not exactly one alternative per holder")
        coords = tuple(next(b for b in panel if edge["post_word"] >> b & 1) for panel in panels)
        if coords in cohort:
            raise ValueError("more than one fork firing produced an occupied pair")
        cohort[coords] = edge["target"]
    if set(cohort) != set(product(*panels)):
        raise ValueError("the archived source is not the full product of incoming alternatives")
    base = seed["word"] ^ (int(seed["offers"][0]["event"]) & ~mask(loose))
    if any(full[index]["word"] != base | mask(coords) for coords, index in cohort.items()):
        raise ValueError("some complete input words differ outside the two incoming occupations")

    by_center = defaultdict(list)
    for coords, index in cohort.items():
        for edge in full[index]["offers"]:
            if len(edge["centers"]) != 1:
                raise ValueError("a nominated existing correction has multiple literal centers")
            center, = edge["centers"]
            marked = set(edge["marks"]) & loose
            covered = marked & set(coords)
            if len(marked) != 2 or len(covered) != 1:
                raise ValueError("a correction does not replace just one of the two occupied siblings")
            taken, = covered
            placed, = marked - covered
            axis = coords.index(taken)
            other = coords[1-axis]
            if full[index]["word"] >> placed & 1:
                raise ValueError("an outgoing sibling is already occupied in the registered cohort")
            by_center[center].append(dict(edge, input_node=index, input_coordinates=coords, incoming_group=axis,
                                          removed=taken, retained=other, added=placed,
                                          output_base=edge["post_word"] ^ mask((other, placed)),
                                          fixed_change=int(edge["event"]) ^ mask((taken, placed))))
    if len(by_center) != 2:
        raise ValueError("the candidate does not have two corrective sectors")
    partitions = []
    sectors = []
    for center, edges in sorted(by_center.items()):
        axes = {e["incoming_group"] for e in edges}
        bases = {e["output_base"] for e in edges}
        surgery = {e["fixed_change"] for e in edges}
        fresh = tuple(sorted({e["added"] for e in edges}))
        if len(axes) != 1 or len(bases) != 1 or len(surgery) != 1 or len(fresh) != 4:
            raise ValueError("one sector is not a uniform replacement of a single sibling coordinate")
        if len({tuple(source_owners[i]) for i in fresh}) != 1:
            raise ValueError("one outgoing roster has more than one holder")
        if Counter(e["input_node"] for e in edges) != Counter(dict.fromkeys(cohort.values(), 4)):
            raise ValueError("some contemporaneous input lacks one of the four announced offers")
        if any({e["added"] for e in edges if e["input_node"] == i} != set(fresh) for i in cohort.values()):
            raise ValueError("the actual offered marks are not the same roster at each input")
        outputs = set(e["post_word"] for e in edges)
        if len(outputs) != 16:
            raise ValueError("the full words do not factor within the announced sector")
        partitions.append(outputs)
        sectors.append(dict(center=center, axis=next(iter(axes)), fixed_change=next(iter(surgery)),
                            output_base=next(iter(bases)), outgoing=fresh, outgoing_knot=tuple(source_owners[fresh[0]]),
                            original_edges=edges))
    if partitions[0] & partitions[1] or {s["axis"] for s in sectors} != {0, 1}:
        raise ValueError("the two corrections do not give disjoint complementary sectors")
    return dict(incoming_groups=panels, incoming_holders=sorted(groups), common_input_base=base,
                cohort=[dict(coordinates=xy, node=i, word=full[i]["word"]) for xy, i in sorted(cohort.items())],
                centers=sectors)


def prefix_paths(full, incoming, want):
    @cache
    def to(ident):
        if ident == 0:
            return (((), Fraction(1)),)
        return tuple((path + ((prior, edge["event"], ident),), p * edge["conditional_mass"])
                     for prior, edge in incoming[ident] for path, p in to(prior))

    visits = {i: to(i) for i in sorted(want)}
    for i, visits_i in visits.items():
        assert len(visits_i) == full[i]["predecessor_path_count"]
        assert sum(p for _, p in visits_i) == full[i]["launch_mass"]
    return visits


def enrolled_layer(full, incoming):
    fork = full[FORK]
    ids = [r["node"] for r in full if r["depth"] == fork["depth"] + 1]
    assert set(ids) == {e["target"] for e in fork["offers"]}
    outcomes = {e["target"] for i in ids for e in full[i]["offers"]}
    assert outcomes == {r["node"] for r in full if r["depth"] == fork["depth"] + 2}
    prefixes = prefix_paths(full, incoming, {FORK, TARGET, *ids})
    prefix_ids = {0, FORK} | {i for path, _ in prefixes[FORK] for step in path for i in (step[0], step[2])}
    prefix_records = []
    for i, visits in prefixes.items():
        prefix_records.append(dict(node=i, histories=[dict(firings=path, launch_mass=p,
                                   conditional_on_node=p / full[i]["launch_mass"]) for path, p in visits]))
    nodes = [full[i] for i in sorted(prefix_ids | set(ids) | outcomes)]
    picked_mass = sum(full[i]["launch_mass"] for i in INPUTS)
    target_sources = [(i, e) for i in ids for e in full[i]["offers"] if e["target"] == TARGET]
    picked_target = sum(e["launch_mass"] for i, e in target_sources if i in INPUTS)
    other_target = sum(e["launch_mass"] for i, e in target_sources if i not in INPUTS)
    assert picked_target + other_target == full[TARGET]["launch_mass"]
    assert sum(full[i]["launch_mass"] for i in ids) == fork["launch_mass"] == 1
    assert sum(full[i]["launch_mass"] for i in outcomes) == 1
    for i in ids:
        assert sum(e["launch_mass"] for e in full[i]["offers"]) == full[i]["launch_mass"]
    selection = dict(fork_reached=fork["launch_mass"], fork_not_reached=1-fork["launch_mass"],
                     both_input_masses={i: full[i]["launch_mass"] for i in INPUTS},
                     pair_selected=picked_mass, pair_rejected=1-picked_mass,
                     pair_selected_and_target=picked_target, pair_selected_and_complement=picked_mass-picked_target,
                     pair_rejected_and_target=other_target, pair_rejected_and_complement=1-picked_mass-other_target,
                     target_any_intake=full[TARGET]["launch_mass"], complement_any_intake=1-full[TARGET]["launch_mass"],
                     target_given_pair=picked_target/picked_mass, complement_given_pair=1-picked_target/picked_mass,
                     target_given_pair_rejection=other_target/(1-picked_mass), complete_input_layer=ids)
    assert all(full[i]["launch_mass"] / picked_mass == Fraction(1, 2) for i in INPUTS)
    return (dict(nodes=nodes, ancestors_to_fork=sorted(prefix_ids), intake_histories=prefix_records,
                 exact_selection=selection, complete_outcome_layer=sorted(outcomes)), prefixes)


def square_root(value):
    a, b = isqrt(value.numerator), isqrt(value.denominator)
    return Fraction(a, b) if value.numerator == a*a and value.denominator == b*b else None


def crossing(rows, extract, is_target, access, explicit=()):
    """Exact classical crossings and calibration-compatible positive-effect caps."""
    laws = []
    for attempts in rows:
        law = Counter()
        for row in attempts:
            law[extract(row)] += row["p"]
        assert sum(law.values()) == 1
        laws.append(law)
    outcomes = sorted(set(explicit) | set(laws[0]) | set(laws[1]))
    entries, overlap, radicands = [], {True: 0, False: 0}, {True: [], False: []}
    totals = dict.fromkeys(PREPARATIONS, 0)
    for outcome in outcomes:
        a, b = (Fraction(law[outcome]) for law in laws)
        m = (a+b)/2
        target = is_target(outcome)
        entry = dict(outcome=outcome, is_target=target, a=a, b=b, mixture=m, plus=m, minus=m)
        if target:
            for kind in PREPARATIONS:
                totals[kind] += entry[kind]
        if a and b:
            root = square_root(a*b)
            if root is None:
                radicands[target].append(a*b)
            else:
                overlap[target] += root
        entries.append(entry)
    caps = {"target": dict(rational=overlap[True], square_root_radicands=radicands[True]),
            "complement": dict(rational=overlap[False], square_root_radicands=radicands[False])}
    bound = 2*min(overlap.values()) if not any(radicands.values()) else None
    atom_contrast = max(0, *(abs(x["plus"]-x["minus"]) for x in entries))
    return dict(access=access, outcomes=entries, target=totals, complement={k: 1-v for k, v in totals.items()},
                shared_outcomes=[x["outcome"] for x in entries if x["a"] and x["b"]],
                ordinary_sign_contrast=totals["plus"]-totals["minus"],
                maximum_absolute_ordinary_atom_contrast=atom_contrast, calibration_overlap=caps,
                sharp_possible_sign_contrast_from_this_calibration=bound,
                bound_formula="2 min(target overlap, complement overlap)")


def crossing_family(rows, target_word, pointer, retained, *, settings=False):
    def measure(extract, target, description, explicit=()):
        return crossing(rows, extract, target, description, explicit)

    destination = lambda w: w == target_word
    flags = (False, True)
    result = {
        "target_check": measure(lambda e: destination(e["post_word"]), bool,
                                "read-only comparison with the nominated complete ordinary word", flags),
        "reversed_target_labels": measure(lambda e: not destination(e["post_word"]), lambda x: not x,
                                           "the same observer comparison with its two label names exchanged", flags),
        "complement_as_target": measure(lambda e: not destination(e["post_word"]), bool,
                                        "the original complement treated as the target", flags),
        "post_word": measure(lambda e: e["post_word"], destination, "complete unmarked ordinary post-word"),
        "center_only": measure(lambda e: e["center"], lambda c: c == pointer["center"],
                               "coarse record of the corrective center, whose target sector has other words"),
        "center_and_post_word": measure(lambda e: (e["center"], e["post_word"]), lambda x: destination(x[1]),
                                        "corrective center followed by the complete ordinary post-word"),
        "ordinary_target_mark": measure(lambda e: bool(e["post_word"] >> pointer["mark"] & 1), bool,
                                        "occupation of the nominated outgoing loose distinction", flags),
        "ordinary_target_mark_and_retained": measure(lambda e: e["post_word"] & retained == retained, bool,
                                                     "both nominated outgoing and retained loose distinctions", flags),
        "named_firing_and_post_word": measure(lambda e: (e["center"], e["event"], e["post_word"]),
                                              lambda x: destination(x[2]), "simultaneous recorded firing and word"),
        "incoming_firing_and_post_word": measure(lambda e: (e["incoming_firing"], e["post_word"]),
                                                 lambda x: destination(x[1]), "retained original fork firing and word"),
        "discarded_firing": measure(lambda e: e["post_word"], destination, "classical projection after discarding the firing"),
        "full_external_transcript": measure(lambda e: (e["history"], e["input_node"], e["center"], e.get("shift", -1),
                                                      e["event"], e["post_word"]), lambda x: destination(x[-1]),
                                             "external prefix and offer log without writable ordinary memory"),
    }
    if all("latched_word" in e for row in rows for e in row):
        result["physically_latched_firing_and_post_word"] = measure(
            lambda e: (e["latched_word"], e["post_word"]), lambda x: destination(x[1]),
            "held complementary-pair keeper values and complete old post-word")
        result["physical_latch_and_incoming_firing"] = measure(
            lambda e: (e["incoming_firing"], e["latched_word"], e["post_word"]), lambda x: destination(x[2]),
            "both held keeper and retained original firing")
        result["classical_reset_of_latch"] = measure(lambda e: e["reset_old_word"], destination,
                                                    "physical keeper reset and marginalization of its old values")
        assert result["classical_reset_of_latch"]["outcomes"] == result["post_word"]["outcomes"]
    if settings:
        result["center_shift_and_post_word"] = measure(lambda e: (e["center"], e["shift"], e["post_word"]),
                                                      lambda x: destination(x[2]), "prepared center and shift held with word")
        result["center_shift_post_word_and_incoming_firing"] = measure(
            lambda e: (e["center"], e["shift"], e["post_word"], e["incoming_firing"]), lambda x: destination(x[2]),
            "prepared center and shift with both word and literal incoming firing held")
        if "physically_latched_firing_and_post_word" in result:
            result["center_shift_and_physical_latch"] = measure(
                lambda e: (e["center"], e["shift"], e["latched_word"], e["post_word"]), lambda x: destination(x[-1]),
                "prepared center, shift, held keeper and complete old word")
            result["center_shift_physical_latch_and_incoming_firing"] = measure(
                lambda e: (e["center"], e["shift"], e["incoming_firing"], e["latched_word"], e["post_word"]),
                lambda x: destination(x[-1]), "prepared center and shift plus both firing records and word")
    return result


def firing_map(controller, word, translated_centers=None):
    state = frozenset(places(word))
    found = defaultdict(list)
    for v in sorted(controller.graph):
        center = v if translated_centers is None else translated_centers.get(v, -1-v)
        for change in controller.enabled_at(v, state):
            found[str(mask(change))].append(center)
    return {event: tuple(sorted(centers)) for event, centers in sorted(found.items(), key=lambda x: int(x[0]))}


def keeper_search(controller, archives):
    holdings = controller.stage.stars
    physical_owners = owners(holdings)
    always_clear, never_offered = set(controller.stage.loose), set(controller.stage.loose)
    for rows in archives:
        always_clear -= {v for r in rows for v in r["distinctions"]}
        never_offered -= {v for r in rows for e in r["offers"] for v in e["marks"]}
    available = []
    for bit in sorted(always_clear & never_offered):
        holder, = physical_owners[bit]
        companions = sorted(set(holdings[holder]) & set(controller.stage.loose) - {bit})
        if companions:
            available.append((bit, holder, companions))
    if not available:
        return dict(status="no attachment satisfies the frozen search", candidates=available,
                    always_clear=sorted(always_clear), never_offered=sorted(never_offered))
    anchor, parent, other_old_loose = available[0]
    companion = max(physical_owners)+1
    pairs = tuple((companion+1+2*k, companion+2+2*k) for k in range(10))
    groups = pairs[:2], pairs[2:6], pairs[6:]
    parent_neighbors = {i for b in holdings[parent] for i in physical_owners[b]} - {parent}
    keeper = (anchor, companion, *(v for pair in pairs for v in pair))
    return dict(status="physical attachment found", candidates=available, anchor=anchor, original_holder=parent,
                old_holder_other_loose=other_old_loose, original_holder_neighbors=sorted(parent_neighbors),
                private_companion=companion, holding=keeper, groups=groups, ready=mask(b for a, b in pairs),
                standalone_keeper_admission={"parity": 2**21, "nae": 2**22-2},
                one_bit_forgotten_projection_has_all_assignments_under_both_laws=2**21,
                old_parity_extension="Use the same value for attachment and private companion and one occupied member per pair.",
                keeper_parity_extension="The old all-clear word and its flip of the attachment with another old loose mark realize both attachment values.")


def latch_update(keeper, digits):
    chosen = tuple(roster[i] for roster, i in zip(keeper["groups"], digits, strict=True))
    return mask(v for pair in chosen for v in pair)


def read_latch(keeper, word):
    decoded = tuple(tuple(i for i, (a, _) in enumerate(roster) if word >> a & 1) for roster in keeper["groups"])
    if not any(decoded):
        return None
    return tuple(v[0] for v in decoded) if all(len(v) == 1 for v in decoded) else decoded


def keeper_menus(controller, keeper, layers):
    from sources import ReturnRule, co_knotted_pairs
    from uniform_exchange import UniformSwitch

    if "anchor" not in keeper:
        return dict(status="unavailable because no registered attachment exists")
    ready = keeper["ready"]
    digits = list(product(range(2), range(4), range(4)))
    values = [(None, ready)] + [(p, ready ^ latch_update(keeper, p)) for p in digits]
    nh = mask(keeper["holding"])
    for label, w in values:
        assert read_latch(keeper, w) == label
        assert all(not faults(w, (nh,), law) for law in LAWS)
    local_swap_trials = 0
    for label in digits:
        local = ready
        for roster, index in zip(keeper["groups"], label, strict=True):
            a, b = roster[index]
            assert not (local >> a & 1) and local >> b & 1
            local ^= mask((a, b))
            assert all(not faults(local, (nh,), law) for law in LAWS)
            local_swap_trials += 1
        assert read_latch(keeper, local) == label
    checked_words = sorted({r["word"] for layer in layers for r in layer["nodes"]})
    old_holdings = controller.stage.stars
    old_menus = {w: firing_map(controller, w) for w in checked_words}
    clear_anchor_in_all_words = all(not (w >> keeper["anchor"] & 1) for w in checked_words)
    assert clear_anchor_in_all_words
    report = dict(checked_original_words=len(checked_words), checked_old_words=checked_words,
                  unique_keeper_states=len(values), keeper_states=[dict(label=label, values=places(w)) for label, w in values],
                  individually_legal_keeper_pair_updates_under_both_laws=local_swap_trials,
                  old_and_attached_words_ready_differ_only_on_private_keeper_bits=True,
                  keeper_only_reads=keeper["holding"], keeper_local_view_ready=places(ready),
                  unique_local_ready_view_count=1, readable_native_trigger_count=0,
                  local_status="The old event leaves the attachment clear. Every ready local view is identical before and after all old offers.",
                  read_only_comparison="An external read of the actual named event addresses the selected keeper pairs. The old rule runs independently.",
                  explicit_reset="A supplied operation reads the first members and reverses the three recorded complementary pair exchanges.",
                  full_external_log_has_writable_memory=False)
    try:
        aug = UniformSwitch(ReturnRule(co_knotted_pairs((*old_holdings, keeper["holding"]))))
    except (AssertionError, ValueError) as err:
        return dict(report, status="augmented controller rejected", concrete_error=f"{type(err).__name__}: {err}",
                    verified_old_offers_for_every_latch_value=False, differences=[])

    remap = {i: old_holdings.index(row) for i, row in enumerate(aug.stage.stars) if row in old_holdings}
    differences = []
    for old_word in checked_words:
        for label, private in values:
            actual = firing_map(aug, old_word | private, remap)
            if actual != old_menus[old_word]:
                differences.append(dict(word=old_word, latch=label, original=old_menus[old_word], augmented=actual))
    return dict(report, status="augmented controller accepted", exact_tests=len(checked_words)*len(values),
                augmented_old_holder_index=remap, keeper_index=aug.stage.stars.index(keeper["holding"]),
                verified_old_offers_for_every_latch_value=not differences, differences=differences)


def nominate(products, full):
    hits = [e for s in products["centers"] for e in s["original_edges"] if e["target"] == TARGET]
    assert {e["target"] for e in hits} == {TARGET}
    assert all(any(e["input_node"] == i for e in hits) for i in INPUTS)
    mark, = {e["added"] for e in hits}
    retained, = {e["retained"] for e in hits}
    center, = {e["centers"][0] for e in hits}
    then = full[TARGET]["word"]
    marker = []
    for record in products["cohort"]:
        node = record["node"]
        ordinary_outcomes = [e["target"] for e in full[node]["offers"] if e["post_word"] >> mark & 1]
        both = [e["target"] for e in full[node]["offers"] if e["post_word"] & mask((mark, retained)) == mask((mark, retained))]
        actual = [e["target"] for e in full[node]["offers"] if e["post_word"] == then]
        marker.append(dict(node=node, selected=node in INPUTS, outgoing_mark_targets=ordinary_outcomes,
                           joint_mark_targets=both, complete_word_targets=actual))
    assert all(x["joint_mark_targets"] == x["complete_word_targets"] for x in marker)
    return dict(word=then, distinctions=places(then), mark=mark, retained_mark=retained, center=center,
                mark_alone_calibrated_on_inputs=all(x["outgoing_mark_targets"] == x["complete_word_targets"]
                                                   for x in marker if x["selected"]),
                mark_alone_calibrated_on_full_cohort=all(x["outgoing_mark_targets"] == x["complete_word_targets"] for x in marker),
                joint_marks_calibrated_on_full_cohort=True, full_cohort_certification=marker)


def records(products, keeper, full):
    by_input = defaultdict(list)
    declared_names = {}
    old_max_name = max(max(r["distinctions"], default=0) for r in full)
    for c, sector in enumerate(products["centers"]):
        incoming = products["incoming_groups"][sector["axis"]]
        outgoing = sector["outgoing"]
        for edge in sector["original_edges"]:
            i, j = incoming.index(edge["removed"]), outgoing.index(edge["added"])
            actual = dict(edge, center=sector["center"], center_index=c, incoming_index=i, outgoing_index=j)
            by_input[edge["input_node"]].append(actual)
            label = (c, i, j)
            assert edge["event"] not in declared_names or declared_names[edge["event"]] == label
            declared_names[edge["event"]] = label
            if "anchor" in keeper:
                ready = keeper["ready"]
                change = latch_update(keeper, label)
                latched = edge["post_word"] | (ready ^ change)
                actual.update(latch_label=label, latch_change=places(change), latched_word=latched,
                              latched_distinctions=places(latched), reset_old_word=(latched ^ change) & ((1 << (old_max_name+1))-1))
                assert latched ^ change == edge["post_word"] | ready
                assert read_latch(keeper, latched) == label
                assert all(not faults(latched, (mask(keeper["holding"]),), law) for law in LAWS)
                assert actual["reset_old_word"] == edge["post_word"]
    assert len(declared_names) == 32 and len(set(declared_names.values())) == 32
    trials = []
    for node, row in sorted(by_input.items()):
        actual_names = {e["event"] for e in row}
        refused = [dict(event=e, center=products["centers"][c]["center"], incoming_index=i, outgoing_index=j,
                        reason="the named incoming loose distinction is clear")
                   for e, (c, i, j) in sorted(declared_names.items(), key=lambda x: int(x[0])) if e not in actual_names]
        for e in refused:
            sector = next(s for s in products["centers"] if s["center"] == e["center"])
            mark = products["incoming_groups"][sector["axis"]][e["incoming_index"]]
            assert not (full[node]["word"] >> mark & 1)
        trials.append(dict(node=node, pre_word=full[node]["word"], pre_distinctions=full[node]["distinctions"],
                           refused=refused, offered=row))
    return dict(event_addresses=declared_names, attempts=trials), dict(by_input)


def attach_prefix(attempts, node, prefixes, *, p_key):
    z = sum(p for _, p in prefixes[node])
    return [dict(e, p=e[p_key]*p/z, history=firings, incoming_firing=firings[-1][1])
            for firings, p in prefixes[node] for e in attempts]


def limits(readings):
    return {name: table["sharp_possible_sign_contrast_from_this_calibration"] for name, table in readings.items()}


def active_controls(products, by_input, prefixes, pointer, retained):
    fixed_controls = [(c, k) for c in range(2) for k in range(4)]
    schedules = [("independent_uniform_shift", range(4), False), ("fixed_zero_shift", (0,), False),
                 ("fixed_zero_shift_with_reversed_outgoing_roster", (0,), True),
                 ("independent_uniform_shift_with_reversed_outgoing_roster", range(4), True)]
    control_results = {}
    target = pointer["word"]
    cohort = products["cohort"]
    original_cohort_output = Counter()
    for offers in by_input.values():
        for e in offers:
            original_cohort_output[e["post_word"]] += e["conditional_mass"]/len(cohort)
    for label, shifts, reverse in schedules:
        each = Fraction(1, 2*len(shifts))
        selected = defaultdict(list)
        all_trials = []
        cohort_output = Counter()
        pointwise_old_events = True
        for node, offers in sorted(by_input.items()):
            offered_by_center = {c: [e for e in offers if e["center_index"] == c] for c in (0, 1)}
            event_law = Counter()
            for c, k in fixed_controls:
                group = offered_by_center[c]
                incoming, = {e["incoming_index"] for e in group}
                requested = (incoming+k) % 4
                canonical = 3-requested if reverse else requested
                mass = each if k in shifts else Fraction()
                passed, = (e for e in group if e["outgoing_index"] == canonical)
                all_trials.append(dict(node=node, chosen_center_index=c, chosen_center=passed["center"], shift=k,
                                       setting_mass=mass, incoming_mark=passed["removed"], incoming_index=incoming,
                                       selected_outgoing_rank_in_prepared_roster=requested,
                                       selected_event=passed["event"], selected_outgoing_mark=passed["added"],
                                       attempts=[dict(event=e["event"], outgoing=e["added"], post_word=e["post_word"],
                                                      admitted_by_old_menu=True, passes_supplied_choice=e == passed,
                                                      disposition=("selected" if mass else "setting outside scheduled support") if e == passed
                                                      else "different center" if e["center_index"] != c else "different outgoing index",
                                                      unconditional_given_input_mass=mass if e == passed else 0) for e in offers]))
                if k in shifts:
                    selected[node].append(dict(passed, shift=k, mass=mass))
                    cohort_output[passed["post_word"]] += mass/len(cohort)
                    event_law[passed["event"]] += mass
            pointwise_old_events &= event_law == Counter({e["event"]: e["conditional_mass"] for e in offers})
        assert sum(cohort_output.values()) == 1
        assert pointwise_old_events == (len(shifts) == 4)
        assert cohort_output == original_cohort_output
        rows = [attach_prefix(selected[i], i, prefixes, p_key="mass") for i in INPUTS]
        readings = crossing_family(rows, target, pointer, retained, settings=True)
        assert readings["center_shift_and_post_word"]["shared_outcomes"] == []
        assert readings["center_shift_post_word_and_incoming_firing"]["shared_outcomes"] == []
        fixed_pair = []
        for c, k in product(range(2), shifts):
            pair = []
            for i in INPUTS:
                hit, = (e for e in selected[i] if (e["center_index"], e["shift"]) == (c, k))
                pair.append(dict(hit, singleton_mass=1))
            at_setting = [attach_prefix([e], i, prefixes, p_key="singleton_mass") for e, i in zip(pair, INPUTS, strict=True)]
            per_setting = crossing_family(at_setting, target, pointer, retained, settings=True)
            assert per_setting["post_word"]["shared_outcomes"] == []
            assert all(v == 0 for v in limits(per_setting).values())
            fixed_pair.append(dict(center_index=c, center=pair[0]["center"], shift=k, attempts=pair,
                                   readings=per_setting, allowable_contrasts=limits(per_setting)))
        control_results[label] = dict(reversed_outgoing_roster=reverse, active_shifts=tuple(shifts),
                                      preparatory_center_weight=Fraction(1, 2), attempts=all_trials,
                                      pointwise_original_named_event_law=pointwise_old_events,
                                      same_complete_word_distribution_across_uniform_full_cohort=True,
                                      full_cohort_post_word_mass=dict(sorted(cohort_output.items())),
                                      deterministic_conditioned_choices=fixed_pair,
                                      readings=readings, allowable_contrasts_if_only_this_calibration_known=limits(readings),
                                      allowable_contrast_with_classical_control_fixed_before_mixing=0)
    return dict(intervention="Guard on the physically occupied old mark with a supplied roster, center and shift.",
                schedules=control_results,
                sum_after_fixing_settings="All deterministic conditioned positive effects have zero off-diagonal. Classical forgetting cannot change their mixture.")


def transpose(value, a, b):
    return value ^ mask((a, b)) if ((value >> a) ^ (value >> b)) & 1 else value


def permutation_replay(controller, full, layer, products, prefixes, pointer, keeper):
    group, = (s["outgoing"] for s in products["centers"] if s["center"] == pointer["center"])
    common = set.intersection(*({e["post_word"] for e in full[i]["offers"]} for i in INPUTS))
    target = pointer["word"]
    by_word = {x["word"]: x["node"] for x in layer["nodes"]}
    relevant = set(layer["ancestors_to_fork"]) | set(layer["exact_selection"]["complete_input_layer"])
    raw_menus = {r["node"]: {e["event"]: e for e in r["offers"]} for r in layer["nodes"]}
    holdings = [mask(row) for row in controller.stage.stars]
    if "anchor" in keeper:
        holdings.append(mask(keeper["holding"]))
    tests = []
    for a, b in combinations(group, 2):
        change = lambda w: transpose(w, a, b)
        translated = {i: by_word.get(change(full[i]["word"])) for i in sorted(relevant | set(layer["complete_outcome_layer"]))}
        cert = []
        for old in sorted(relevant):
            row = raw_menus[old]
            dest = translated[old]
            tested = firing_map(controller, change(full[old]["word"]))
            local_menu = {str(change(int(e))): tuple(v["centers"]) for e, v in row.items()}
            translated_actual = local_menu == tested
            arcs = []
            for old_event, edge in sorted(row.items(), key=lambda item: int(item[0])):
                new_event = str(change(int(old_event)))
                new_edge = raw_menus.get(dest, {}).get(new_event)
                if new_edge is None:
                    transported_event_weight = False
                else:
                    transported_event_weight = (new_edge["post_word"] == change(edge["post_word"])
                                                and new_edge["conditional_mass"] == edge["conditional_mass"]
                                                and new_edge["launch_mass"] == edge["launch_mass"]
                                                and new_edge["centers"] == edge["centers"])
                arcs.append(dict(event=old_event, relabeled_event=new_event, target=edge["target"],
                                 relabeled_target=translated[edge["target"]], exact=transported_event_weight))
            cert.append(dict(source=old, relabeled_source=dest, actual_complete_center_menu_covariant=translated_actual,
                             probability_weighted_named_firings_transport=arcs))
        histories = []
        for i in (FORK, *INPUTS):
            transformed = []
            for history, p in prefixes[i]:
                h = tuple((translated[u], str(change(int(event))), translated[v]) for u, event, v in history)
                transformed.append((h, p))
            expected = prefixes[i]
            pointwise = all(original == moved for original, moved in zip(expected, transformed, strict=True))
            histories.append(dict(node=i, inherits_same_individual_firings=pointwise,
                                  weighted_history_set_preserved=set(expected) == set(transformed)))
        mapped_target = change(target)
        tests.append(dict(transposition=(a, b), fixes_each_holding=all(change(w) == w for w in holdings),
                          fixes_start=change(full[0]["word"]) == full[0]["word"],
                          fixes_each_selected_input=all(change(full[i]["word"]) == full[i]["word"] for i in INPUTS),
                          fixes_ready_apparatus=change(keeper.get("ready", 0)) == keeper.get("ready", 0),
                          fixes_all_prefix_nodes_to_fork=all(translated[i] == i for i in layer["ancestors_to_fork"]),
                          preparations_and_retained_prefixes=histories,
                          same_machine_literal_menus_covariant=all(row["actual_complete_center_menu_covariant"] for row in cert),
                          full_named_outcome_transport=cert,
                          fixes_complete_word_32=mapped_target == target,
                          fixes_mark_placed_inside_interaction=pointer["mark"] not in (a, b),
                          transformed_target_node=by_word.get(mapped_target), transformed_target_word=mapped_target))
    orbit = {target} | {row["transformed_target_word"] for row in tests}
    for row in tests:
        assert row["fixes_each_holding"] and row["fixes_ready_apparatus"]
        assert row["fixes_start"] and row["fixes_each_selected_input"] and row["fixes_all_prefix_nodes_to_fork"]
        assert all(h["weighted_history_set_preserved"] for h in row["preparations_and_retained_prefixes"])
        assert all(m["exact"] for v in row["full_named_outcome_transport"] for m in v["probability_weighted_named_firings_transport"])
        assert row["same_machine_literal_menus_covariant"]
    return dict(common_output_siblings=group, transposition_certificates=tests, generators=list(zip(group, group[1:])),
                common_output_words=sorted(common), common_word_orbit=sorted(orbit), one_common_orbit=orbit == common,
                target_stabilizer_transpositions=[x["transposition"] for x in tests if x["fixes_complete_word_32"]],
                inside_interaction_mark_stabilizer_transpositions=[x["transposition"] for x in tests if x["fixes_mark_placed_inside_interaction"]],
                posthoc_word_test_leaves_original_group=True,
                keeper_record_relabeling="The native offers transport. A supplied latch indexed by the outgoing rank also requires transport of the corresponding memory addresses.")


def preload_native(controller, full, by_input, pointer, prefixes, retained):
    mark = pointer["mark"]
    old_holdings = controller.stage.stars
    holder, = owners(old_holdings)[mark]
    other = min(set(old_holdings[holder]) & (set(controller.stage.loose) - {mark}))
    double = mask((mark, other))
    masks = tuple(map(mask, old_holdings))
    archive_ids = {r["word"]: r["node"] for r in full}
    new_pairs = {}
    rows = []
    for node, old in sorted(by_input.items()):
        prior = full[node]["word"]
        assert not prior & double
        loaded = prior ^ double
        after_load = {law: faults(loaded, masks, law) for law in LAWS}
        failed_load = {law: dict(status="undefined" if bad else "admitted", failing_holders=bad)
                       for law, bad in after_load.items()}
        assert not after_load["parity"]
        events = firing_map(controller, loaded)
        originals = {e["event"]: e for e in old}
        event_records = []
        offered = []
        for key in sorted(set(events) | set(originals), key=int):
            previous = originals.get(key)
            law_ruling = {}
            if key in events:
                output = loaded ^ int(key)
                for law in LAWS:
                    bad = faults(output, masks, law)
                    if after_load[law] or bad:
                        law_ruling[law] = dict(status="undefined", failed_post_holders=bad, chance=None)
                    else:
                        law_ruling[law] = dict(status="admitted", failed_post_holders=bad, chance=Fraction(1, len(events)))
                center, = events[key]
                applied = dict(event=key, center=center, input_node=node, p_new=Fraction(1, len(events)), post_word=output)
                offered.append(applied)
            else:
                output = None
                law_ruling = {law: dict(status="refused by the literal ordinary menu" if not failed else "undefined",
                                        chance=0 if not failed else None) for law, failed in after_load.items()}
            event_records.append(dict(event=key, support=places(int(key)), old_offer=previous is not None,
                                      old_probability_given_input=previous["conditional_mass"] if previous else 0,
                                      preloaded_offer=key in events, enabled_centers=events.get(key), post_word=output,
                                      post_distinctions=places(output) if output is not None else None,
                                      original_archive_node=archive_ids.get(output), laws=law_ruling))
        rows.append(dict(input_node=node, old_word=prior, preloaded_word=loaded, preloaded_distinctions=places(loaded),
                         loading_legality=failed_load, attempts=event_records, whole_literal_menu_count=len(events),
                         removes_positions_from_original_menu=sorted(set(originals)-set(events), key=int),
                         adds_new_event_names=sorted(set(events)-set(originals), key=int),
                         probability_of_original_complete_target=sum(e["p_new"] for e in offered if e["post_word"] == pointer["word"])))
        new_pairs[node] = offered
    if all(new_pairs[i] for i in INPUTS):
        signed_rows = [attach_prefix(new_pairs[i], i, prefixes, p_key="p_new") for i in INPUTS]
        readings = crossing_family(signed_rows, pointer["word"], pointer, retained)
    else:
        readings = dict(status="no native continuation for at least one enrolled input", affected=[i for i in INPUTS if not new_pairs[i]])
    group = old_holdings[holder]
    outgoing_siblings = sorted(set(group) & set(controller.stage.loose))
    return dict(physically_preoccupied=(mark, other), same_old_holder=holder, holder_positions=group,
                parity_flip_retains_original_holding_law=True,
                initially_preloaded_state_stabilizer_transpositions=[(a, b) for a, b in combinations(outgoing_siblings, 2)
                                                                    if (a in (mark, other)) == (b in (mark, other))],
                original_singleton_target_probability=Fraction(1, 8), cohort=rows, selected_pair_readings=readings)


def earlier_nae_swap(raw, prior):
    from permutation_controls import apply, local_pools

    saved = prior["loose_swap"]
    words = tuple(saved["named_input_pair"])
    holders = tuple(map(tuple, saved["holdings"]))
    pools = local_pools(holders)
    masks = tuple(map(mask, holders))
    expected = tuple(reversed(words))
    assert tuple(mask(apply(frozenset(places(w)), {4}, pools)) for w in words) == expected
    end = saved["named_target"]
    target_bit = lambda r: r["post_word"] == end
    execution = lambda r: r["executed"]
    last_target = lambda x: x[-1] == end
    binary = (False, True)
    readings = {
        "target_only": (target_bit, bool, binary),
        "target_labels_exchanged": (lambda r: not target_bit(r), bool, binary),
        "execution_flag": (execution, bool, binary),
        "execution_labels_exchanged": (lambda r: not execution(r), bool, binary),
        "post_word": (lambda r: r["post_word"], lambda w: w == end, ()),
        "latched_event_target": (lambda r: (r["executed"], r["post_word"]), last_target, ()),
        "post_word_with_old_word_copy": (lambda r: (r["input_word"], r["post_word"]), last_target, ()),
        "external_transcript": (lambda r: (r["input_word"], r["executed"], r["executed"], r["post_word"]), last_target, ()),
    }
    verified = []
    for law in LAWS:
        assert not any(faults(w, masks, law) for w in words)
        raw_rows = raw["loose_swap"]["laws"][law]["fixed_pair_both_orientations"]
        for key, guarded in (("original_swap_offer", False), ("guarded_if_mark_one_occupied", True)):
            table = saved["laws"][law][key]
            independent = []
            for w, after, arc, literal in zip(words, expected, table["attempts"], raw_rows, strict=True):
                assert literal["two_calls"]["states"] == [list(places(w)), list(places(after)), list(places(w))]
                ran = not guarded or bool(w >> 1 & 1)
                assert (arc["input_word"], arc["executed"], arc["post_word"]) == (w, ran, after if ran else w)
                independent.append([dict(input_word=w, executed=ran, post_word=after if ran else w, p=1)])
            for name, (read, selector, explicit) in readings.items():
                fresh = crossing(independent, read, selector, "old loose-sibling replay", explicit)
                saved_reading = table["readings"][name]
                for a, b in zip(fresh["outcomes"], saved_reading["outcomes"], strict=True):
                    assert json.loads(json.dumps(a["outcome"])) == b["outcome"]
                    assert all(a[s] == Fraction(b[s]) for s in PREPARATIONS)
                assert [i for i, row in enumerate(fresh["outcomes"]) if row["is_target"]] == saved_reading["target_pool_indices"]
            verified.append((law, key))
    return dict(citation=ERASURE.relative_to(ROOT), independently_reproduced_policies=verified,
                independently_reproduced_crossing_count=len(verified)*len(readings), archived_table=saved)


def source_hashes(raw):
    files = {Path(__file__).resolve(), ARCHIVE, ERASURE, AUDIT, HERE / "contract.json",
             ROOT / "research" / HERE.parent.name / "preregistration.md"}
    result = {}
    for relative, expected in raw["sources"].items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected and actual != PUBLIC_SOURCE_VARIANTS.get(relative):
            raise ValueError(f"dependency differs from the archive and admitted public counterpart: {relative}")
        result[relative] = expected
    for path in files:
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def law_report(layer):
    grouped = {r["node"]: r for r in layer["nodes"]}
    result = {}
    for law in LAWS:
        failed_nodes = {n: r["failed_knots"][law] for n, r in grouped.items() if r["failed_knots"][law]}
        attempts = []
        for i in (FORK, *layer["exact_selection"]["complete_input_layer"]):
            for edge in grouped[i]["offers"]:
                target = edge["target"]
                failed = i in failed_nodes or target in failed_nodes
                attempts.append(dict(source=i, event=edge["event"], target=target,
                                     status="undefined" if failed else "admitted", source_failed_holders=failed_nodes.get(i, []),
                                     target_failed_holders=failed_nodes.get(target, []),
                                     probability_given_source=None if failed else edge["conditional_mass"]))
        result[law] = dict(failed_nodes=failed_nodes, attempts=attempts,
                           status="undefined" if FORK in failed_nodes else "admitted",
                           weights_for_selected_crossings=dict.fromkeys(PREPARATIONS) if FORK in failed_nodes else "exact tables in original_readings",
                           lawfully_admitted_enrolled_attempts=sum(e["status"] == "admitted" for e in attempts))
    return result


def build():
    with gzip.open(ARCHIVE, "rt") as wf, gzip.open(ERASURE, "rt") as we:
        raw, prior = json.load(wf), json.load(we)
    sources = source_hashes(raw)
    observed = raw["uniform_switch"]
    archived_direction = observed["directions"]
    model, first, second = actual_model()
    start_supports = (first.pulse ^ frozenset(first.ring), second.pulse ^ frozenset(second.ring))
    holdings = model.stage.stars
    ownership = owners(holdings)
    assert holdings == tuple(map(tuple, observed["holdings"]))
    masks = tuple(map(mask, holdings))
    raws = [d["traces"]["loaded"]["nodes"] for d in archived_direction]
    assert [frozenset(x[0]["word"]) for x in raws] == list(start_supports)
    exact = [exact_cases(rows, model, masks, observed["events"]) for rows in raws]
    layers, prefixes = zip(*(enrolled_layer(*row) for row in exact), strict=True)
    keeper = keeper_search(model, [rows for rows, _ in exact])
    attachment_comparison = keeper_menus(model, keeper, layers)
    historic = json.loads(AUDIT.read_text())
    directions = []
    for load, (layer, paths, (full, _), old, near) in enumerate(zip(layers, prefixes, exact, archived_direction, historic, strict=True)):
        early_controls = dict(first_deterministic=near["earliest"], later_coarse_only=near["examples"]["coarse_only"],
                              recorded_fork=near["examples"]["current_word_allows_contrast"], comparison="prior archive lookup only")
        enroll = near["examples"]["current_word_allows_contrast"]
        assert (enroll["fork"], tuple(enroll["inputs"]), enroll["endpoint"]) == (FORK, INPUTS, TARGET)
        report = dict(load=load, original_donor=old["donor_knot"], original_receiver=old["receiver_knot"],
                      original_enrollment=layer, prior_near_controls=early_controls, original_law_status=law_report(layer),
                      complete_original_dag_nodes_replayed=len(full))
        try:
            products = assigned_product(full, FORK, ownership, set(model.stage.loose))
        except ValueError as err:
            report.update(product_structure=dict(status="failed", defect=str(err)),
                          supplied_full_product_interventions=dict(status="unavailable after factorization failure"))
            directions.append(report)
            continue
        pointer = nominate(products, full)
        retained = mask((pointer["mark"], pointer["retained_mark"]))
        attempts, by_input = records(products, keeper, full)
        paired = [attach_prefix(by_input[i], i, paths, p_key="conditional_mass") for i in INPUTS]
        readings = crossing_family(paired, pointer["word"], pointer, retained)
        assert readings["post_word"]["target"]["a"] == readings["post_word"]["target"]["b"] == Fraction(1, 8)
        assert readings["post_word"]["sharp_possible_sign_contrast_from_this_calibration"] == Fraction(1, 4)
        assert not readings["named_firing_and_post_word"]["shared_outcomes"]
        assert not readings["incoming_firing_and_post_word"]["shared_outcomes"]
        if "latched_word" in paired[0][0]:
            assert not readings["physically_latched_firing_and_post_word"]["shared_outcomes"]
        controls = active_controls(products, by_input, paths, pointer, retained)
        folded = controls["schedules"]["independent_uniform_shift"]["readings"]
        for key in ("post_word", "named_firing_and_post_word", "incoming_firing_and_post_word", "target_check"):
            assert readings[key]["outcomes"] == folded[key]["outcomes"]
        report.update(product_structure=dict(products, status="recovered"), named_literal_offers=attempts,
                      target_pointer=pointer, original_readings=readings, active_present_word_control=controls,
                      unmarked_symmetry=permutation_replay(model, full, layer, products, paths, pointer, keeper),
                      active_two_mark_preload=preload_native(model, full, by_input, pointer, paths, retained))
        directions.append(report)
    return dict(schema=1, sources=sources, public_source_variants=PUBLIC_SOURCE_VARIANTS,
                registered_fork=FORK, registered_intermediates=INPUTS,
                registered_complete_target=TARGET, holdings=holdings,
                conventions=dict(words="Integer masks with explicit distinction lists in the ordinary trial records.",
                                 ordinary_preparation="The two signed vectors are mathematical preparations of the same ordinary equal-history law. The old rules act on its diagonal probabilities.",
                                 positive_effect_cap="Caps describe all normalized positive effects compatible with the stated singleton calibration. Each fixed classical control has its own such constraint before it is mixed.",
                                 named_history="A single retained actual incoming firing identifies its own successor. Both sign settings use the same distributions of ordinary histories.",
                                 controls="Center, shift, roster order and event address are supplied. The occupied marks, legal offers and keeper states are ordinary words.",
                                 probability="Fractions are exact. Null is an undefined trial or a bound displayed as a radical formula."),
                altered_keeper_attachment=dict(search=keeper, original_and_augmented_control_comparison=attachment_comparison,
                                               trigger="A supplied external read of the named firing addresses the complementary-pair swaps.",
                                               source_orientation_control="A local keeper reading with the unchanged attachment and all ready bits cannot identify an old firing."),
                directions=directions, separate_two_law_loose_swap=earlier_nae_swap(raw, prior))


def encode(result):
    plain = (json.dumps(result, default=str, sort_keys=True, separators=(",", ":")) + "\n").encode()
    data = BytesIO()
    with gzip.GzipFile(filename="", fileobj=data, mode="wb", mtime=0) as zipper:
        zipper.write(plain)
    return data.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="replay and require the recorded gzip bytes")
    args = parser.parse_args()
    limit = 4 * 1024**3
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (limit if hard == resource.RLIM_INFINITY else min(limit, hard), hard))
    if hasattr(os, "sched_getaffinity") and hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    report = build()
    data = encode(report)
    if args.check:
        if OUT.read_bytes() != data:
            raise SystemExit("recorded artifact differs from exact ordinary replay")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(data)
    print(f"Exact ordinary replay {hashlib.sha256(data).hexdigest()} ({len(data)} gzip bytes)")


if __name__ == "__main__":
    main()
