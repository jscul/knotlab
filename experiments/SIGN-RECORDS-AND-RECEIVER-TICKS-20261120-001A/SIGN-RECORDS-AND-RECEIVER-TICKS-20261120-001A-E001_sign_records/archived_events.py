"""Exact physical replay of the archived returning switch and the two-loose-bit swap."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
import hashlib
from io import BytesIO
from itertools import product
import json
import os
from pathlib import Path
import resource
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "archived_events.json.gz"
RULES = "MOTION-LAW-20261119-001"
MOTION = "MOTION-AT-EDDY-20261119-001"
READS = "READS-HOLDERS-SOURCES-20261120-001A"
EDDY = "EDDY-WORLD-20261119-001"
RULE_EXPERIMENT = ROOT / "experiments" / RULES / f"{RULES}-E001_rules"
MOTION_EXPERIMENT = ROOT / "experiments" / MOTION / f"{MOTION}-E001_motion"
RULE_ARCHIVE = ROOT / "artifacts" / RULES / f"{RULES}-E001_rules"
READ_ARCHIVE = ROOT / "artifacts" / READS / f"{READS}-E001_reads_changes"
LAWS = ("parity", "nae")
LITERAL_NODE_CAP = 20_000


def mask(names):
    return sum(1 << name for name in names)


def names(word):
    bits = []
    while word:
        bit = word & -word
        bits.append(bit.bit_length() - 1)
        word ^= bit
    return bits


def failed_holders(word, holdings_masks, law):
    if law == "parity":
        return [i for i, support in enumerate(holdings_masks) if (word & support).bit_count() % 2]
    if law == "nae":
        return [i for i, support in enumerate(holdings_masks) if (word & support) in (0, support)]
    raise ValueError(law)


def physical_menu(model):
    @cache
    def menu(word):
        state = frozenset(names(word))
        by_event = defaultdict(list)
        for center in sorted(model.graph):
            for event in model.enabled_at(center, state, audit=True):
                by_event[event].append(center)
        assert set(by_event) == model.enabled(state)
        return tuple((mask(event), tuple(by_event[event])) for event in sorted(by_event, key=lambda s: tuple(sorted(s))))

    return menu


def literal_graph(start, menu, holdings_masks, event_catalog, stage):
    """Discover physical words, then count schedules on the observed firing-depth DAG."""
    queue = [start]
    ids = {start: 0}
    depths = [0]
    arcs = []
    predecessors = Counter()
    event_ids = set()
    for i, word in enumerate(queue):
        assert not failed_holders(word, holdings_masks, "parity"), ("literal word", names(word))
        outgoing = []
        for event, centers in menu(word):
            after = word ^ event
            if event not in event_catalog:
                places = frozenset(names(event))
                assert event.bit_count() == 4 and not failed_holders(event, holdings_masks, "parity")
                marked = min(places - stage.loose)
                assert places in stage.minimum_response(marked).supports
                event_catalog[event] = dict(distinctions=sorted(places), kind="loose correction" if places & stage.loose else "ordinary four-distinction change")
            event_ids.add(event)
            successor = ids.setdefault(after, len(queue))
            if successor == len(queue):
                queue.append(after)
                depths.append(depths[i] + 1)
            assert depths[successor] == depths[i] + 1, ("non-advancing event", names(word), names(after))
            predecessors[successor] += 1
            outgoing.append((event, centers, successor))
        arcs.append(outgoing)
        if len(queue) > LITERAL_NODE_CAP:
            raise ValueError("The registered four-step controller exceeded the literal node limit")

    path_denominators = [Counter() for _ in queue]
    path_denominators[0][1] = 1
    arrivals = [Fraction(0) for _ in queue]
    arrivals[0] = Fraction(1)
    terminal_ids = []
    backwards = [0] * len(queue)
    rows = []
    for i, (word, outgoing) in enumerate(zip(queue, arcs, strict=True)):
        degree = len(outgoing)
        edges = []
        if degree:
            conditional = Fraction(1, degree)
            marginal = conditional * arrivals[i]
            for event, centers, successor in outgoing:
                for denominator, count in path_denominators[i].items():
                    path_denominators[successor][denominator * degree] += count
                arrivals[successor] += marginal
                edges.append(dict(event_id=str(event), at_knots=centers, target=successor,
                                  chance_given_source=conditional, unconditional_chance=marginal))
        else:
            terminal_ids.append(i)
        rows.append(dict(id=i, word=names(word), depth=depths[i], number_of_prefix_paths=path_denominators[i].total(),
                         probability_of_visit=arrivals[i], enabled_events=edges))
    for i in reversed(range(len(queue))):
        backwards[i] = sum(backwards[j] for _, _, j in arcs[i]) if arcs[i] else 1
        rows[i]["number_of_suffix_paths"] = backwards[i]

    assert sum(arrivals[i] for i in terminal_ids) == 1
    assert sum(path_denominators[i].total() for i in terminal_ids) == backwards[0]
    for counts, weight in zip(path_denominators, arrivals, strict=True):
        assert sum((Fraction(n, d) for d, n in counts.items()), Fraction(0)) == weight
    summary = dict(states=len(queue), transitions=sum(map(len, arcs)), distinct_named_events=len(event_ids),
                   states_with_multiple_predecessors=sum(n > 1 for n in predecessors.values()),
                   terminal_depths=[depths[i] for i in terminal_ids], terminals=[names(queue[i]) for i in terminal_ids])
    return dict(summary=summary, nodes=rows, terminal_nodes=terminal_ids,
                complete_paths=backwards[0], terminal_path_denominator_histograms=[sorted(path_denominators[i].items()) for i in terminal_ids])


def occupancy_by_depth(graph, donor, receiver):
    by_depth = defaultdict(Counter)
    for row in graph["nodes"]:
        word = set(row["word"])
        state = (len(word & donor), len(word & receiver))
        by_depth[row["depth"]][state] += row["probability_of_visit"]
    return [dict(depth=i, donor_receiver_occupancies=[(k, mass) for k, mass in sorted(weights.items())])
            for i, weights in sorted(by_depth.items())]


def reversal_checks(graph):
    nodes = graph["nodes"]
    transitions = reverse_enabled = 0
    first = None
    for source in nodes:
        for edge in source["enabled_events"]:
            target = nodes[edge["target"]]
            event = int(edge["event_id"])
            assert mask(source["word"]) ^ event == mask(target["word"])
            assert mask(target["word"]) ^ event == mask(source["word"])
            reverse = edge["event_id"] in {e["event_id"] for e in target["enabled_events"]}
            transitions += 1
            reverse_enabled += int(reverse)
            if not reverse and first is None:
                first = dict(original=source["word"], event=names(event), after=target["word"],
                             enabled_after=[names(int(e["event_id"])) for e in target["enabled_events"]],
                             idle_if_same_event_is_attempted_after=target["word"])
    return dict(algebraically_reversible_xor_transitions=transitions, same_event_enabled_at_image=reverse_enabled,
                first_firing_vs_idle_collision=first)


def two_word_masses(a, b):
    """Pointer masses for the supplied sum/difference map, on real integer inputs."""
    denominator = 2 * (a*a + b*b)
    return Fraction((a+b)**2, denominator), Fraction((a-b)**2, denominator)


def collision_controls():
    inputs = dict(plus=(1, 1), minus=(1, -1), singleton_loaded=(1, 0), singleton_preloaded=(0, 1))
    results = {}
    for name, (a, b) in inputs.items():
        p, q = two_word_masses(a, b)
        loaded = Fraction(a*a, a*a+b*b)
        results[name] = dict(ordinary_endpoint_mass_with_separate_histories=Fraction(1),
                             ordinary_joint_endpoint_and_18_firings_mass=loaded,
                             ordinary_joint_endpoint_and_zero_firings_mass=1-loaded,
                             unscaled_coherent_merge_mass=Fraction((a+b)**2, a*a+b*b),
                             selected_mass=p, joint_selection_and_endpoint_mass=p,
                             conditional_endpoint_mass_if_selected=Fraction(1) if p else None,
                             normalized_instrument_pointer=[p, q])
    # In an incoherent mixture compute each constituent's effects separately.
    results["dephased"] = {
        key: (Fraction(1, 2), Fraction(1, 2)) if key == "normalized_instrument_pointer" else
             (results["singleton_loaded"][key] + results["singleton_preloaded"][key]) / 2
        for key in results["singleton_loaded"]
    }
    plus, minus = (1, 1), (1, -1)
    effects = [[[Fraction(row[i]*row[j], 2) for j in range(2)] for i in range(2)] for row in (plus, minus)]
    assert [[effects[0][i][j] + effects[1][i][j] for j in range(2)] for i in range(2)] == [[1, 0], [0, 1]]
    return dict(ordinary_goal_effect=[[1, 0], [0, 1]], supplied_success_effect=effects[0],
                supplied_complement_effect=effects[1], records=results)


def replay_switch(prior, earlier):
    sys.path.insert(0, str(RULE_EXPERIMENT))
    import sources
    import uniform_exchange

    spec, = (row for row in sources.cases() if row["id"] == "T4")
    model, first, second, _ = uniform_exchange.named_fixture(spec)
    stage = model.stage
    masks = tuple(map(mask, stage.stars))
    assert len(stage.stars) == prior["stage_knots"] == earlier["size_two_knots"]
    assert len(stage.owners) == prior["stage_distinctions"] == earlier["size_two_distinctions"]
    menu = physical_menu(model)
    catalog = {}
    directions = []
    for donor, receiver, historic in zip((first, second), (second, first), prior["directions"], strict=True):
        pulse = mask(donor.pulse)
        d, r = frozenset(donor.ring), frozenset(receiver.ring)
        donor_mask, receiver_mask = mask(d), mask(r)
        start = pulse ^ donor_mask
        goal = pulse ^ receiver_mask
        assert names(pulse) == historic["returning_pulse"]
        assert sorted(d) == historic["donor_ring"] and sorted(r) == historic["receiver_ring"]
        if donor == first:
            assert names(start) == earlier["initial"] and names(goal) == earlier["target"]
        variants = (("unloaded", pulse), ("loaded", start), ("preloaded_receiver", goal))
        typed = {label: literal_graph(w, menu, masks, catalog, stage) for label, w in variants}
        for label, trace in typed.items():
            assert trace["summary"] == historic[label], (donor.center, label, trace["summary"], historic[label])
            trace["occupancy_by_depth"] = occupancy_by_depth(trace, d, r)
        loaded, preloaded = typed["loaded"], typed["preloaded_receiver"]
        arrival, = loaded["terminal_nodes"]
        postcut = preloaded["nodes"][0]
        endpoint = loaded["nodes"][arrival]
        assert endpoint["word"] == postcut["word"] == names(goal)
        assert endpoint["enabled_events"] == postcut["enabled_events"] == []
        assert loaded["summary"]["terminal_depths"] == [18] and preloaded["summary"]["terminal_depths"] == [0]
        assert start ^ goal == donor_mask ^ receiver_mask

        named_checks = {}
        for label, word in (*variants, ("restored_loaded_endpoint", goal)):
            bad = {law: failed_holders(word, masks, law) for law in LAWS}
            named_checks[label] = dict(word=names(word), failed_knots=bad, allowed={law: not rows for law, rows in bad.items()})
        nae_failures = Counter()
        for trace in typed.values():
            for row in trace["nodes"]:
                row["failed_nae_knots"] = failed_holders(mask(row["word"]), masks, "nae")
                nae_failures[len(row["failed_nae_knots"])] += 1
        assert all(not checks["allowed"]["nae"] for checks in named_checks.values())

        marks = []
        for name, ring in (("donor", d), ("receiver", r)):
            for bit in sorted(ring):
                minimal = stage.minimum_response(bit)
                marks.append(dict(store=name, distinction=bit, value_at_shared_cut=(goal >> bit) & 1,
                                  own_knots=stage.owners[bit], enabled_events_using_it=[],
                                  allowed_minimum_change_size=minimal.minimum_size,
                                  allowed_minimum_change_count=minimal.count,
                                  allowed_minimum_change_supports=[tuple(sorted(s)) for s in minimal.supports]))
        truths = []
        for x, y in product((0, 1), repeat=2):
            word = pulse ^ (donor_mask if x else 0) ^ (receiver_mask if y else 0)
            out = word ^ donor_mask ^ receiver_mask
            assert out == pulse ^ (donor_mask if not x else 0) ^ (receiver_mask if not y else 0)
            truths.append(dict(input=[x, y], output=[1-x, 1-y], source_word=names(word), target_word=names(out),
                               source_failed_nae=failed_holders(word, masks, "nae"),
                               target_failed_nae=failed_holders(out, masks, "nae")))
        assert [dict(input=row["input"], output=row["output"]) for row in truths] == historic["prescribed_translation_truth_table"]
        # Test reversing the whole role assignment with the original pulse kept.
        assert not menu(goal)
        directions.append(dict(donor_knot=donor.center, receiver_knot=receiver.center, donor_ring=sorted(d),
                               receiver_ring=sorted(r), pulse=names(pulse), protected_approach=sorted(donor.marker),
                               traces=typed, named_word_admission=named_checks,
                               checked_nae_failed_knots_histogram_over_inventory=dict(sorted(nae_failures.items())),
                               nae_replay="inapplicable: the literal prepared words fail the law",
                               reversibility=reversal_checks(loaded), unconditional_translation=truths,
                               restored_cut=dict(word=names(goal), full_holding_same=True, stored_marks=marks,
                                                 enabled_events=[], future_words=[names(goal)], future_firing_counts=[0],
                                                 actual_loaded_past_firings=18, preloaded_past_firings=0,
                                                 loaded_receiver_bits_initially_on=0, preloaded_receiver_bits_initially_on=len(r),
                                                 full_current_word_total_variation=Fraction(0),
                                                 retained_full_history_total_variation=Fraction(1))))
    quotient = earlier["all_sibling_quotient_outcomes"]
    assert directions[0]["traces"]["loaded"]["summary"]["states"] == quotient["direct_literal_states"]
    assert directions[0]["traces"]["loaded"]["summary"]["transitions"] == quotient["direct_literal_transitions"]
    return dict(fixture=spec["id"], stage_knots=len(stage.stars), stage_distinctions=len(stage.owners),
                holdings=stage.stars, directions=directions, events=catalog,
                authority=dict(holding="first ordinary reached stage of the fixed archival source",
                               primitive_events="allowed parity changes verified against the minimum supports",
                               enabled_menu="archived supplied UniformSwitch controller with protected pulse marks",
                               weighing_schedules="independent uniform choice on the current literal menu"),
                collision_as_supplied_coherent_recombination=collision_controls())


def literal_swap(word, pair):
    a, b = pair
    apart = ((word >> a) ^ (word >> b)) & 1
    return word ^ mask(pair) if apart else word


def projection_support(holdings, permitted):
    output = []
    for local in holdings:
        words = {sum(((x >> n) & 1) << i for i, n in enumerate(local)) for x in permitted}
        k1 = len(words) < 1 << len(local)
        k2 = all(len({x & ~(1 << i) for x in words}) == 1 << (len(local) - 1) for i in range(len(local)))
        output.append(dict(places=local, size=len(words), binding=k1, loss_on_erasure=k2, coexistence=bool(words)))
    return output


def trace_swap(start, choices, updates):
    actual = start
    states = [names(actual)]
    calls = []
    for choice in choices:
        following = updates[choice][actual]
        calls.append(dict(threshold=choice, before=names(actual), after=names(following),
                          invoked=True, changed=following != actual, changed_distinctions=names(actual ^ following)))
        actual = following
        states.append(names(actual))
    return dict(states=states, calls=calls)


def integer_measurement(vector, image):
    vectors = [tuple(a + s*b for a, b in zip(vector, image, strict=True)) for s in (1, -1)]
    absolute = [sum(map(abs, row)) for row in vectors]
    squared = [sum(a*a for a in row) for row in vectors]
    den = sum(squared)
    assert den == 4 * sum(a*a for a in vector)
    return dict(squared_numerators=squared, squared_denominator=den,
                squared=[Fraction(n, den) for n in squared], absolute=[Fraction(n, sum(absolute)) for n in absolute],
                unnormalized_answer_vectors=vectors)


def archive_phase_test(allowed, swaps, idle, old, phase_mark):
    assert len(allowed) == old["allowed_states"] == old["physical_transition_pairs"]
    assert old["identical_ordinary_record_weights"]
    records = []
    phase_records = {}
    for phase_changed in (False, True):
        f = tuple((-1 if phase_changed and w & phase_mark else 1) if w in allowed else 0 for w in range(64))
        ordinary = {w: Fraction(f[w]**2, len(allowed)) for w in allowed}
        histories = {(w, swaps[w], swaps[swaps[w]], idle[w]): p for w, p in ordinary.items()}
        phase_records[phase_changed] = dict(initial_vector=f, ordinary_word_and_history_weights=
                                             [(key, value) for key, value in sorted(histories.items())])
        for row in old["supplied_change_read"]:
            if row["phase_changed"] != phase_changed:
                continue
            flip = mask(row["change"])
            image = tuple(f[w ^ flip] for w in range(64))
            measured = integer_measurement(f, image)
            assert measured["squared_numerators"] == row["numerators"] and measured["squared_denominator"] == row["denominator"]
            assert all(w ^ flip in allowed for w in allowed) == row["constant_allowed_change"]
            records.append(dict(phase_changed=phase_changed, change=row["change"], sign_outcome_order=[1, -1],
                                is_globally_allowed=row["constant_allowed_change"], **measured))
    assert phase_records[False]["ordinary_word_and_history_weights"] == phase_records[True]["ordinary_word_and_history_weights"]
    return dict(same_input_word_and_all_tested_physical_transcripts=True, preparations=phase_records,
                supplied_sign_readings=records)


def pair_controls(first, second, permitted, swaps):
    assert first in permitted and second in permitted and swaps[first] == second and swaps[second] == first
    preparations = {"positive": (1, 1), "opposite_relative_sign": (1, -1), "global_minus": (-1, -1),
                    "first_singleton": (1, 0), "second_singleton": (0, 1)}
    by_name = {}
    for key, pair in preparations.items():
        a, b = pair
        norm = a*a + b*b
        ordinary = [Fraction(a*a, norm), Fraction(b*b, norm)]
        externally_read = two_word_masses(a, b)
        assert externally_read == tuple(integer_measurement(pair, (b, a))["squared"])
        by_name[key] = dict(integer_initial_coefficients=pair, same_after_two_swaps=pair,
                            coefficients_after_one_swap=(b, a),
                            ordinary_before=ordinary, ordinary_after_one=list(reversed(ordinary)),
                            ordinary_after_two=ordinary,
                            change_sign_projector_probabilities=externally_read,
                            supplied_sum_difference_pointer_chances=externally_read)
    by_name["dephased_equal_mixture"] = dict(ordinary_before=[Fraction(1, 2)]*2, ordinary_after_one=[Fraction(1, 2)]*2,
                                             ordinary_after_two=[Fraction(1, 2)]*2,
                                             change_sign_projector_probabilities=[Fraction(1, 2)]*2,
                                             supplied_sum_difference_pointer_chances=[Fraction(1, 2)]*2)
    assert by_name["positive"]["ordinary_before"] == by_name["opposite_relative_sign"]["ordinary_before"]
    assert by_name["positive"]["ordinary_after_one"] == by_name["opposite_relative_sign"]["ordinary_after_one"]
    assert by_name["positive"]["change_sign_projector_probabilities"] == by_name["global_minus"]["change_sign_projector_probabilities"]
    return dict(words=[names(first), names(second)], supplied_fixed_change=names(first ^ second), preparations=by_name)


def replay_swap(previous, prior_phases, origin):
    from permutation_controls import apply, local_pools

    holdings = ((0, 1, 2), (0, 3, 4, 5))
    assert [list(row) for row in holdings] == previous["swap_source"] == prior_phases["source"]
    assert prior_phases["phase_read"] == [1]
    pair = (1, 2)
    pools = local_pools(holdings)
    assert pools == [(frozenset((4,)), pair)]
    earlier, = (r for r in origin["two_knot_controls"] if r["arity"] == 4)
    masks = tuple(map(mask, holdings))
    result = {}
    first, second = mask((0, 1, 3)), mask((0, 2, 3))
    for law in LAWS:
        permitted = tuple(x for x in range(64) if not failed_holders(x, masks, law))
        swaps = {x: literal_swap(x, pair) for x in permitted}
        idle = {x: x for x in permitted}
        for x, target in swaps.items():
            assert names(target) == sorted(apply(frozenset(names(x)), {4}, pools))
            assert names(x) == sorted(apply(frozenset(names(x)), {5}, pools))
            assert not failed_holders(target, masks, law) and swaps[target] == x
        stats = dict(allowed=len(permitted), distinct_images=len(set(swaps.values())),
                     allowed_images=sum(y in permitted for y in swaps.values()), changed=sum(x != y for x, y in swaps.items()),
                     inverse_on_allowed=all(swaps[y] == x for x, y in swaps.items()), whole_uniform_fixed=set(permitted) == set(swaps.values()))
        before = previous["laws"][law]["two_loose_swap"]
        assert all(before[key] == value for key, value in stats.items())
        if law == "parity":
            assert stats["allowed"] == earlier["allowed_assignments"] and stats["changed"] == earlier["assignments_changed"]
        projections = projection_support(holdings, permitted)
        for a, b in zip(projections, before["old_knot_checks"], strict=True):
            assert (a["size"], a["binding"], a["loss_on_erasure"], a["coexistence"]) == (
                b["allowed_words"], b["binding"], b["loss_on_erasure"], b["coexistence"])
        updates = {4: swaps, 5: idle}
        histories = [dict(initial_word=names(w), uniform_initial_mass=Fraction(1, len(permitted)),
                          two_calls=trace_swap(w, (4, 4), updates), idle_once=trace_swap(w, (5,), updates)) for w in permitted]
        fixed = [dict(start=names(w), two_calls=trace_swap(w, (4, 4), updates), idle_once=trace_swap(w, (5,), updates))
                 for w in (first, second)]
        phase = archive_phase_test(set(permitted), swaps, idle, prior_phases["laws"][law], 1 << 1)
        result[law] = dict(summary=stats, projections=projections, histories=histories, fixed_pair_both_orientations=fixed,
                           signed_comparators=pair_controls(first, second, permitted, swaps), archived_phase_comparison=phase)
    return dict(holdings=holdings, static_swap_trigger_neighbor_arity=4, absent_neighbor_arity_control=5,
                swap_pair=pair, laws=result)


def replay_witness(archived):
    cancellation = []
    for w in range(8):
        terms = tuple((-1)**(lo + hi) if (not lo or w == 0) and (not hi or w == 7) else 0
                      for lo, hi in product((0, 1), repeat=2))
        assert sum(terms) == int(w not in (0, 7))
        cancellation.append(dict(word=w, terms=terms, sum=sum(terms), unsigned_path_count=sum(map(abs, terms))))
    assert [dict(word=r["word"], terms=list(r["terms"]), sum=r["sum"]) for r in cancellation] == archived["october"]

    parity_control = []
    for w in range(8):
        terms = (1, (-1)**w.bit_count())
        assert sum(terms) == 2 * int(w.bit_count() % 2 == 0)
        parity_control.append(dict(word=w, terms=terms, sum=sum(terms), unsigned_path_count=sum(map(abs, terms))))
    readings = []
    for old in archived["readings"]:
        flip, read, phase = old["word"]
        vector = tuple(int(w not in (0, 7)) for w in range(8))
        image = tuple(phase * (-1)**((w ^ flip) & read).bit_count() * vector[w ^ flip] for w in range(8))
        measured = integer_measurement(vector, image)
        assert measured["absolute"] == list(map(Fraction, old["absolute"]))
        assert measured["squared"] == list(map(Fraction, old["squared"]))
        readings.append(dict(operator=old["word"], **measured))
    return dict(nae_clause_witnesses=cancellation, parity_single_character_witness=parity_control,
                archived_nae_controls=readings, witness_signs_an_explicit_arithmetic_supply=True)


def source_hashes(explicit_paths):
    files = set(explicit_paths)
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT) and path.relative_to(ROOT).parts[0] in ("tools", "experiments"):
                files.add(path)
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}


def compressed(data):
    content = (json.dumps(data, sort_keys=True, default=str, separators=(",", ":")) + "\n").encode()
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", filename="", mtime=0) as writer:
        writer.write(content)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require byte-identical replay of the saved receipt.")
    args = parser.parse_args()
    for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[variable] = "1"
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = 4 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap if soft == resource.RLIM_INFINITY else min(cap, soft), hard))

    source_paths = (READ_ARCHIVE / "motion.json", READ_ARCHIVE / "signed_counts.json",
                    RULE_ARCHIVE / "uniform_exchange.json", RULE_ARCHIVE / "permutation_controls.json")
    prior, signed, earlier, permutations = (json.loads(path.read_bytes()) for path in source_paths)
    switch = replay_switch(prior["restored_switch"], earlier["cases"]["T4"])
    swap = replay_swap(prior["permutations"], prior["phase_test"], permutations)
    witness = replay_witness(signed)

    inputs = source_hashes((*source_paths, Path(__file__).resolve(), HERE / "contract.json",
                           ROOT / "research" / HERE.parent.name / "preregistration.md",
                           MOTION_EXPERIMENT / "inputs.json", MOTION_EXPERIMENT / "holdout.json",
                           ROOT / "experiments" / EDDY / f"{EDDY}-E001_world" / "world_growth.py",
                           ROOT / "proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md"))
    summary = dict(switch_loaded_directions=[dict(summary=d["traces"]["loaded"]["summary"],
                                                   complete_paths=d["traces"]["loaded"]["complete_paths"],
                                                   source_nae_violations=len(d["named_word_admission"]["loaded"]["failed_knots"]["nae"]),
                                                   restored_nae_violations=len(d["named_word_admission"]["restored_loaded_endpoint"]["failed_knots"]["nae"]))
                                              for d in switch["directions"]],
                   swap={law: swap["laws"][law]["summary"] for law in LAWS},
                   signed_cancellation_nae_forbidden=[r["word"] for r in witness["nae_clause_witnesses"] if not r["sum"]])
    data = dict(schema=1, sources=inputs, summary=summary,
                conventions=dict(word="ascending names assigned one; all other physical distinctions are zero",
                                 events="one exposed literal change at a time, uniform on the current menu when weight is used",
                                 depth="number of actual firings from the supplied fixed input",
                                 signs="ordinary comparisons and signed arithmetic or projectors are separate operations"),
                uniform_switch=switch, loose_swap=swap, signed_witness=witness)
    result = compressed(data)
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != result:
            print("Saved archived-events receipt differs from its replay.", file=sys.stderr)
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(result)
    print(json.dumps(dict(receipt=str(OUT.relative_to(ROOT)), sha256=hashlib.sha256(result).hexdigest(), **summary),
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
