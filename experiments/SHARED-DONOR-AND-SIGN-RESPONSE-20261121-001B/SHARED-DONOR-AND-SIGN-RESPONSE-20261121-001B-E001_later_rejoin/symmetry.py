"""Stabilizers of the actual histories and complete output effects."""

from collections import defaultdict
from fractions import Fraction
from itertools import permutations
from functools import lru_cache
import gzip
import json
import numpy as np

from completed_menu import ARCHIVE, AUDIT, geometry, full_operations, census, mask, labelled_recodings


def rename(word, old, new):
    ans = word & ~mask(old)
    for a, b in zip(old, new):
        if word & (1 << a):
            ans |= 1 << b
    return ans


def inversions(order):
    return sum(order[i] > order[j] for i in range(len(order)) for j in range(i + 1, len(order)))


def certificates(nodes, holdings, geom, operations):
    mids, outs, coords, oc, old, new, centers, arcs = geom
    active = oc[32][0]
    g = new[active]
    bit_words = [mask(n["word"]) for n in nodes]
    id_of = {w: i for i, w in enumerate(bit_words)}
    assert len(id_of) == len(nodes)
    successors = [{e["target"]: e for e in n["enabled_events"]} for n in nodes]
    predecessors = defaultdict(list)
    for j, offers in enumerate(successors):
        for target, e in offers.items():
            predecessors[target].append((j, e))

    @lru_cache(None)
    def prefixes(y):
        if y == 0:
            return [((), Fraction(1))]
        return [
            (hist + ((i, int(e["event_id"]), y),), weight * Fraction(e["chance_given_source"]))
            for i, e in predecessors[y]
            for hist, weight in prefixes(i)
        ]

    hist = {j: prefixes(j) for j in (11, 12, 13)}
    for i, rows in hist.items():
        assert sum(p for _, p in rows) == Fraction(nodes[i]["probability_of_visit"])
        assert len(rows) == nodes[i]["number_of_prefix_paths"]
    fixed_prefix_nodes = sorted(
        {q for rows in hist.values() for events, prob in rows for i, e, j in events for q in (i, j)}
    )
    fixed_prefix_arcs = {
        (i, e, j) for rows in hist.values() for events, prob in rows for i, e, j in events
    }
    early_nodes = {n["id"] for n in nodes if n["depth"] <= 10}
    early_arcs = {
        (n["id"], int(e["event_id"]), e["target"])
        for n in nodes
        if n["depth"] < 10
        for e in n["enabled_events"]
    }
    input_pair = (12, 13)
    common = sorted(successors[12].keys() & successors[13].keys())
    assert common == [32, 33, 34, 35]
    subgroup = []
    for order in permutations(range(4)):
        moved = [g[k] for k in order]
        translate = lambda value: rename(value, g, moved)
        assert all(translate(mask(h)) == mask(h) for h in holdings)
        images = [id_of[translate(old_word)] for old_word in bit_words]
        assert all(images[j] == j for j in fixed_prefix_nodes) and all(
            images[j] == j for j in early_nodes
        )
        assert all(translate(e) == e for i, e, j in fixed_prefix_arcs | early_arcs)
        assert all(images[k] == k for k in input_pair)
        for i, outs_i in enumerate(successors):
            matches = successors[images[i]]
            assert len(outs_i) == len(matches)
            for j, e in outs_i.items():
                new_e = matches[images[j]]
                assert int(new_e["event_id"]) == translate(int(e["event_id"]))
                assert (
                    new_e["chance_given_source"] == e["chance_given_source"]
                    and new_e["at_knots"] == e["at_knots"]
                )
        action = [images[j] for j in common]
        subgroup.append(
            dict(
                mark_order=order,
                images_of_common_words=action,
                odd=bool(inversions(order) % 2),
                transposition=sum(i != n for i, n in enumerate(order)) == 2,
                fixes_target=images[32] == 32,
            )
        )
    orbit = sorted({perm["images_of_common_words"][0] for perm in subgroup})
    stabilizer = [perm for perm in subgroup if perm["fixes_target"]]
    assert orbit == common and len(stabilizer) == 6 and any(perm["odd"] for perm in stabilizer)
    for j in common:
        assert any(
            perm["odd"] and perm["images_of_common_words"][common.index(j)] == j for perm in subgroup
        )
    common_intervals = [
        (
            Fraction(successors[12][y]["chance_given_source"]),
            Fraction(successors[13][y]["chance_given_source"]),
        )
        for y in common
    ]
    assert common_intervals == [(Fraction(1, 8), Fraction(1, 8))] * 4
    # Direct transport of squared and signed records: transpositions generate all 24.
    readout = operations["matched_reflection"]["reports"]["fine_outputs"]
    by_word = {row["word"]: row for row in readout}
    conflicting = [
        perm["mark_order"]
        for perm in subgroup
        if any(
            by_word[old_y]["plus"] != by_word[new_y]["plus"]
            for old_y, new_y in zip(common, perm["images_of_common_words"])
        )
    ]
    assert conflicting
    return dict(
        renamed_marks=g,
        physical_holders=[i for i, h in enumerate(holdings) if g[0] in h],
        fixed_local_holdings=len(holdings),
        original_history_weights={
            str(j): [dict(prefix=[list(v) for v in path], weight=str(p)) for path, p in rows]
            for j, rows in hist.items()
        },
        prefix_node_ids=fixed_prefix_nodes,
        prefix_named_arcs=len(fixed_prefix_arcs),
        all_nodes_through_depth_ten=len(early_nodes),
        all_earlier_offers_fixed=len(early_arcs),
        archived_word_states=len(nodes),
        archived_transitions=sum(map(len, successors)),
        permutations=subgroup,
        common_orbit=orbit,
        chosen_word_stabilizer_size=len(stabilizer),
        odd_permutations_fixing_target=sum(g["odd"] for g in stabilizer),
        anonymous_covariant_bounds=dict(ordinary_permutation="0", alternating_relative_character="0"),
        fixed_matching_broken_by_output_renamings=conflicting,
    )


def global_inputs(arms, geom_list):
    """One-step kernels on all actually observed old words, with an explicit absorbing convention."""
    transitions = {}
    layers = []
    cohorts = []
    per_arm = []
    for arm, geo in zip(arms, geom_list):
        nodes = arm["traces"]["loaded"]["nodes"]
        words = [mask(n["word"]) for n in nodes]
        support = set(words)
        cohorts.append({words[j] for j in geo[0]})
        slice_counts = {}
        for depth in sorted({n["depth"] for n in nodes}):
            layer = [n for n in nodes if n["depth"] == depth]
            next_ids = {e["target"] for n in layer for e in n["enabled_events"]}
            slice_counts[depth] = dict(inputs=len(layer), outputs=len(next_ids))
        for j, n in enumerate(nodes):
            row = {words[e["target"]]: e["chance_given_source"] for e in n["enabled_events"]} or {
                words[j]: "1"
            }
            if words[j] in transitions:
                assert transitions[words[j]] == row
            transitions[words[j]] = row
        terminals = [n["id"] for n in nodes if not n["enabled_events"]]
        assert len(terminals) == 1
        y = terminals[0]
        ending = [
            n["id"]
            for n in nodes
            if len(n["enabled_events"]) == 1 and n["enabled_events"][0]["target"] == y
        ]
        assert len(ending) >= 2
        per_arm.append(support)
        layers.append(
            dict(
                layer_sizes=slice_counts,
                terminal_id=y,
                unit_columns_sharing_the_terminal=ending,
                two_column_obstruction=ending[:2],
                silent_word_as_identity=words[y],
            )
        )
    assert not cohorts[0] & cohorts[1]
    assert all(sum(map(Fraction, row.values())) == 1 for row in transitions.values())
    others = set(transitions) - set.union(*cohorts)
    # Every unselected input contributes a diagonal one-dimensional block in the complete word-effects extension.
    return dict(
        total_distinct_physical_inputs=len(transitions),
        overlap_of_load_domains=len(per_arm[0] & per_arm[1]),
        two_cohorts=[len(c) for c in cohorts],
        other_diagonal_columns=len(others),
        normalized_fine_entries_outside_cohorts=sum(len(transitions[x]) for x in others),
        loads=layers,
        other_columns={
            str(w): {str(y): p for y, p in sorted(transitions[w].items())} for w in sorted(others)
        },
    )


def relative_character_control():
    """Interchanging two outcomes can detect a phase when the stabilizer is trivial."""
    action = np.diag([1, -1])
    vectors = np.array([[1, 1], [1, -1]])
    effects = np.einsum("oi,oj->oij", vectors, vectors)
    assert np.array_equal(action @ effects[0] @ action, effects[1])
    assert np.array_equal(effects.sum(axis=0), 2 * np.eye(2, dtype=int))
    chances = [[str(Fraction(int(v @ e @ v), 4)) for e in effects] for v in vectors]
    assert chances == [["1", "0"], ["0", "1"]]
    return dict(
        group_action="Input rays are fixed. The second changes sign and the output words exchange.",
        effects_numerators=effects.tolist(),
        denominator=2,
        plus_word_probabilities=chances[0],
        minus_word_probabilities=chances[1],
        target_stabilizer="identity",
    )


def marked_extremes():
    """All incoming names are interchangeable and one of four outcomes is marked."""
    p = Fraction(1, 8)
    endpoints = []
    for x in (-p / 3, p):
        other = -x / 3
        spectra = [[p + 3 * t, p - t, p - t, p - t] for t in (x, other)]
        assert all(min(spectrum) >= 0 for spectrum in spectra)
        assert x + 3 * other == 0 and 4 * p == Fraction(1, 2)
        endpoints.append(
            dict(
                contrast=str(2 * x),
                target_off_diagonal=str(x),
                each_other_off_diagonal=str(other),
                target_spectrum=list(map(str, spectra[0])),
                other_spectrum=list(map(str, spectra[1])),
            )
        )
    return endpoints


def run():
    archive = json.loads(gzip.decompress(ARCHIVE.read_bytes()))["uniform_switch"]
    previous = json.loads(AUDIT.read_text())
    result = []
    geom_list = []
    for arm, old_result in zip(archive["directions"], previous):
        old = old_result["examples"]["current_word_allows_contrast"]
        assert (
            old["depth"] == 9
            and old["fork"] == 11
            and old["inputs"] == [12, 13]
            and old["endpoint"] == 32
        )
        assert str(old["bounds"]["word"]) == "0.25"
        nodes = arm["traces"]["loaded"]["nodes"]
        geo = geometry(archive["holdings"], nodes)
        geom_list.append(geo)
        algebra = full_operations(geo)
        source = {e["target"]: Fraction(e["chance_given_source"]) for e in nodes[11]["enabled_events"]}
        selected = source[12] + source[13]
        assert source[12] == source[13] and selected == Fraction(1, 8)
        preparation = dict(
            fork_probability=nodes[11]["probability_of_visit"],
            unfiltered_intakes={i: str(v) for i, v in source.items()},
            pair_selection=str(selected),
            selection_failure=str(1 - selected),
            mathematical_preparations={
                str(sign): {
                    "selected_amplitude_numerators": [1, sign],
                    "selected_squared_denominator": 2,
                    "unselected_intakes": [w for w in source if w not in (12, 13)],
                    "unconditional_probability_per_other_word": "1/16",
                }
                for sign in (1, -1)
            },
            native_independent_signed_input_operation=None,
        )
        for key, candidate in algebra["operations"].items():
            if "reports" in candidate:
                reports = candidate["reports"]
                reports["original_launch_selected_and_target"] = {
                    k: str(selected * Fraction(v)) for k, v in reports["target"].items()
                }
                reports["original_launch_selected_and_other"] = {
                    k: str(selected * Fraction(v)) for k, v in reports["complement"].items()
                }
        result.append(
            dict(
                full_cohort=algebra,
                symmetry=certificates(nodes, archive["holdings"], geo, algebra["operations"]),
                same_ordinary_history_cross=preparation,
            )
        )
    return dict(
        loads=result,
        global_archived_columns=global_inputs(archive["directions"], geom_list),
        stencils=census(),
        input_and_output_recodings=labelled_recodings(),
        two_output_relative_character_control=relative_character_control(),
        one_mark_incoming_permutation_invariant_oriented_extremes=marked_extremes(),
    )
