"""Bounded packet continuation and anonymous end readings in the jump archive."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "archive.json"
PRIOR = ROOT / "experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators"
PRIOR_RESULT = ROOT / "artifacts/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/explosive.json"
IDENTIFIED_SOURCES_SHA256 = "b4281bc1948cfe612a3a02d3c320cec5f33cfbad02476de543f1717b2e7241e0"
MAX_PACKET_WIDTH = 2
DESIGN_FREEZE = "fe65cd3c2"


@dataclass
class Stage:
    stars: tuple
    parents: dict
    fresh: dict


def replay(core, literal, operator, source, law, receipt):
    stages = [Stage(source, {}, {})]
    for old in receipt["ages"][1:]:
        stars = stages[-1].stars
        width = len(literal.owners(stars))
        end = operator.from_stars(stars)
        plan = core.bounded_plan(operator, end, law, core.MAX_KNOTS - len(stars),
                                 core.MAX_DISTINCTIONS - width)
        assert "stop" not in plan and not plan["implied"]
        rows = core.allocate(literal, stars, plan)
        after = core.replay_cohort(literal, stars, rows, range(len(rows)))
        start = len(stars)
        parents = {start + i: frozenset(p) for i, p in enumerate(plan["parents"])}
        fresh = {start + i: f for i, f in enumerate(plan["fresh"])}
        assert (len(after), len(literal.owners(after)), len(parents), max(map(len, parents.values()))) == (
            old["knots"], old["distinctions"], old["births"], old["largest_parent_set"])
        stages.append(Stage(after, parents, fresh))
    assert len(stages) <= core.MAX_ROUNDS + 1
    return stages


def physical_read(literal, operator, stars):
    """Infer the immediate input relation and one deeper slice from literal current holdings."""
    end = operator.from_stars(stars)
    ordinary = literal.holder_graph(stars)
    live = end.opens.keys()
    # At a funded positive cut, no live knot meets a knot of its own layer.
    # We only grade the deeper relation where two complete cuts are present.
    parents = {v: frozenset(ordinary[v]) for v in live}
    assert all(parents[v] and parents[v].isdisjoint(live) for v in live)
    older = set().union(*parents.values())
    previous_parents = {p: frozenset(ordinary[p] - live) for p in older}
    blocks = Counter(tuple(sorted(ordinary[p] & live)) for p in older)
    witnessed_degree = {v: len(r) for v, r in operator.neighbors(end).items()}
    coarse = {v: (end.opens[v], witnessed_degree[v]) for v in live}
    immediate = {v: (*coarse[v], len(parents[v])) for v in live}
    deeper = {v: (immediate[v], tuple(sorted(len(previous_parents[p]) for p in parents[v]))) for v in live}
    return end, parents, previous_parents, blocks, coarse, immediate, deeper


def same_signatures(signatures):
    groups = defaultdict(list)
    for v, value in signatures.items():
        groups[value].append(v)
    return {value: tuple(sorted(group)) for value, group in groups.items()}


def packets(operator, end, signature):
    witnessed = operator.neighbors(end)
    groups = same_signatures(signature)
    return {
        value: group for value, group in sorted(groups.items())
        if len(group) <= MAX_PACKET_WIDTH and (len(group) == 1 or group[1] in witnessed[group[0]])
    }


def local_packet_type(opens, parents, group):
    # The retained boundary names are anonymous. Live knots have no shared
    # distinction with each other, and each meets an older holder once.
    local_rows = tuple(sorted((opens[v], len(parents[v])) for v in group))
    shared_older_holders = len(parents[group[0]] & parents[group[1]]) if len(group) == 2 else 0
    return local_rows, shared_older_holders


def end_graph(opens, blocks):
    """Collapse repeated copies of a witness set with its exact multiplicity as color."""
    graph = nx.Graph()
    graph.add_nodes_from((v, {"kind": (0, n)}) for v, n in sorted(opens.items()))
    for i, (row, number) in enumerate(sorted(blocks.items())):
        witness = -1 - i
        graph.add_node(witness, kind=(1, number))
        graph.add_edges_from((witness, v) for v in row)

    # Refinement only rules out images. The remaining maps are exact isomorphisms.
    colors = nx.get_node_attributes(graph, "kind")
    while True:
        signatures = {v: (colors[v], tuple(sorted(colors[n] for n in graph[v]))) for v in graph}
        palette = {c: i for i, c in enumerate(sorted(set(signatures.values())))}
        refined = {v: palette[s] for v, s in signatures.items()}
        if len(set(refined.values())) == len(set(colors.values())):
            nx.set_node_attributes(graph, refined, "refined")
            return graph
        colors = refined


def hidden_change(opens, blocks, hidden, *, bounded_members=None):
    """Decide whether some anonymous-end automorphism changes the claimed readout."""
    graph = end_graph(opens, blocks)
    left, right = graph.copy(), graph.copy()
    trials = 0
    for a, b in combinations(sorted(opens), 2):
        if hidden[a] == hidden[b]:
            continue
        if bounded_members is not None and a not in bounded_members and b not in bounded_members:
            continue
        color = graph.nodes[a]["refined"]
        if color != graph.nodes[b]["refined"]:
            continue
        if set(graph[a]) == set(graph[b]):
            images = {v: (b if v == a else a if v == b else v) for v in opens}
        else:
            left.nodes[a]["refined"] = right.nodes[b]["refined"] = -1
            mapping = nx.vf2pp_isomorphism(left, right, node_label="refined")
            left.nodes[a]["refined"] = right.nodes[b]["refined"] = color
            trials += 1
            if mapping is None:
                continue
            images = {v: mapping[v] for v in opens}
        assert len(set(images.values())) == len(images) and images[a] == b
        assert all(opens[v] == opens[image] for v, image in images.items())
        assert Counter({tuple(sorted(images[v] for v in row)): count for row, count in blocks.items()}) == blocks
        return {"exact_pairs_checked": trials, "moves": [a, b], "hidden_values": [hidden[a], hidden[b]],
                "permutation": [[v, image] for v, image in images.items() if v != image]}
    return {"exact_pairs_checked": trials, "moves": None}


def validate_renaming(literal, operator, stage, physical):
    rng = Random(20261120051 + len(stage.stars))
    knot_names = list(range(len(stage.stars)))
    distinction_names = sorted(literal.owners(stage.stars))
    moved_distinctions = distinction_names[:]
    rng.shuffle(knot_names)
    rng.shuffle(moved_distinctions)
    mapping = dict(zip(distinction_names, moved_distinctions, strict=True))
    recoded = [()] * len(stage.stars)
    for v, star in enumerate(stage.stars):
        recoded[knot_names[v]] = tuple(sorted(mapping[d] for d in star))
    renamed = physical_read(literal, operator, recoded)
    for original, result in zip(physical[-3:], renamed[-3:], strict=True):
        assert {knot_names[v]: value for v, value in original.items()} == result
    for original, result in zip(physical[1:3], renamed[1:3], strict=True):
        assert {knot_names[v]: frozenset(knot_names[p] for p in ps) for v, ps in original.items()} == result


def observe(literal, operator, stages, age):
    stage = stages[age]
    physical = physical_read(literal, operator, stage.stars)
    end, parents, previous, all_witnesses, coarse, immediate, deeper = physical
    assert parents == stage.parents
    if age >= 2:
        assert previous == stages[age - 1].parents
    validate_renaming(literal, operator, stage, physical)
    named = packets(operator, end, immediate)
    coarse_classes = same_signatures(coarse)
    members = frozenset(v for group in named.values() for v in group)
    basic_witnesses = Counter(end.blocks)
    immediate_flip = hidden_change(end.opens, basic_witnesses, immediate, bounded_members=members)
    assert all(len(parents[v]) == sum(count for row, count in all_witnesses.items() if v in row) for v in parents)
    readings = {"maximal_blocks_packet_flip": immediate_flip}
    if age >= 2:
        readings.update({
            "maximal_blocks_deeper_flip": hidden_change(end.opens, basic_witnesses, deeper),
            "all_last_holders_deeper_flip": hidden_change(end.opens, all_witnesses, deeper),
        })
    return end, list(named.values()), {
        "age": age,
        "knots": len(stage.stars),
        "distinctions": len(literal.owners(stage.stars)),
        "live_rows": [{"holder": v, "signature": immediate[v],
                       "grandparent_signature": deeper[v][1] if age >= 2 else None,
                       "parents": sorted(parents[v]), "incoming": {
                           str(p): sorted(d for d in stage.stars[v] if d in stage.stars[p]) for p in sorted(parents[v])
                       }} for v in end.opens],
        "packet_classes": [{"signature": signature, "members": group,
                            "same_coarse_class": group == coarse_classes[signature[:2]],
                            "current_with_boundary_type": local_packet_type(end.opens, parents, group)}
                           for signature, group in named.items()],
        "end_symmetry": readings,
    }


def pure(parents, packet):
    return frozenset(v for v, ps in parents.items() if ps <= packet)


def both(parents, a, b):
    return frozenset(v for v, ps in parents.items() if ps & a and ps & b)


def reaches(parents, packet):
    return frozenset(v for v, ps in parents.items() if ps & packet)


def details(following, a, b):
    first = following[0].parents
    pure_a, pure_b = pure(first, a), pure(first, b)
    direct = both(first, a, b)
    pair_only = frozenset(v for v in direct if first[v] <= a | b)
    row = {"pure_at_one": [sorted(pure_a), sorted(pure_b)],
           "direct": sorted(direct), "direct_only_these_parties": sorted(pair_only)}
    if len(following) == 1:
        return row
    second = following[1].parents
    any_a, any_b = reaches(first, a), reaches(first, b)
    mixed_ancestry = reaches(second, any_a) & reaches(second, any_b)
    assert not both(second, pure_a, pure_b)
    row.update({"pure_at_two": [sorted(pure(second, pure_a)), sorted(pure(second, pure_b))],
                "mixed_ancestry_at_two": sorted(mixed_ancestry),
                "mediated_at_two": [sorted(both(second, direct, pure_a)), sorted(both(second, direct, pure_b))],
                "mixed_without_direct_carrier_at_two": sorted(mixed_ancestry - reaches(second, direct))})
    return row


def compare_without(core, operator, end, law, stage, produced, parties, remove):
    """Keep surviving holdings and their boundary witnesses. Compare the whole proposed roster."""
    restricted = operator.restricted(end, end.opens.keys() - remove)
    plan = core.bounded_plan(operator, restricted, law, core.MAX_KNOTS - len(stage.stars),
                             core.MAX_DISTINCTIONS - len(end_distinctions(stage)))
    if "stop" in plan:
        return {"status": plan["stop"]}
    before, after = [], []
    for party in parties:
        before.append(Counter((tuple(sorted(ps)), produced.fresh[v])
                              for v, ps in produced.parents.items() if ps <= party))
        after.append(Counter((ps, f) for ps, f in zip(plan["parents"], plan["fresh"], strict=True)
                             if party.issuperset(ps)))
    return {"status": "implied" if plan["implied"] else "funded",
            "pure_counts": [list(map(sum, (a.values(), b.values()))) for a, b in zip(before, after, strict=True)],
            "pure_fresh_sums": [[sum(f * n for (_, f), n in row.items()) for row in (a, b)]
                                for a, b in zip(before, after, strict=True)],
            "pure_roster_and_fresh_changed": [a != b for a, b in zip(before, after, strict=True)]}


def end_distinctions(stage):
    return {d for row in stage.stars for d in row}


def pair_panel(core, operator, law, age, stages, ends, choices, *, compare_removal):
    counts, examples = Counter(), {}
    for field in ("pairs", "pairs_with_two_followups", "both_pure_at_one", "both_pure_at_two",
                  "direct_and_both_pure_at_two", "mediated_and_both_pure_at_two"):
        counts[field] = 0
    if compare_removal:
        counts["removal_comparisons"] = 0
        counts["one_receiver_removal_comparisons"] = 0
    following = stages[age + 1:age + 3]
    for a, b in combinations(choices, 2):
        a, b = frozenset(a), frozenset(b)
        assert not a & b
        counts["pairs"] += 1
        row = details(following, a, b)
        row.update({"launch": [sorted(a), sorted(b)], "age": age})
        flags = {
            "both_pure_at_one": all(row["pure_at_one"]),
            "direct": bool(row["direct"]),
            "pair_only_direct": bool(row["direct_only_these_parties"]),
            "direct_and_both_pure_at_one": bool(row["direct"] and all(row["pure_at_one"])),
        }
        if len(following) == 2:
            counts["pairs_with_two_followups"] += 1
            flags.update({
                "both_pure_at_two": all(row["pure_at_two"]),
                "mixed_ancestry_at_two": bool(row["mixed_ancestry_at_two"]),
                "ancestry_without_direct_carrier_at_two": bool(row["mixed_without_direct_carrier_at_two"]),
                "direct_and_both_pure_at_two": bool(row["direct"] and all(row["pure_at_two"])),
                "mediated_and_both_pure_at_two": bool(any(row["mediated_at_two"]) and all(row["pure_at_two"])),
            })
            if compare_removal and flags["direct_and_both_pure_at_two"]:
                counts["removal_comparisons"] += 1
                remove = frozenset(row["direct"])
                parties = tuple(map(frozenset, row["pure_at_one"]))
                mate = compare_without(core, operator, ends[age+1], law, stages[age+1], following[1], parties, remove)
                row["without_direct_children"] = mate
                counts[f"removal_{mate['status']}"] += 1
                flags["valid_removal_changes_pure_fresh_or_roster"] = (
                    mate["status"] == "funded" and any(mate["pure_roster_and_fresh_changed"]))
            if compare_removal:
                for receiver, mediated in enumerate(row["mediated_at_two"]):
                    if not mediated or not row["pure_at_two"][receiver]:
                        continue
                    direct_coparents = frozenset(row["direct"]) & set().union(
                        *(following[1].parents[child] for child in mediated))
                    receiver_packet = frozenset(row["pure_at_one"][receiver])
                    mate = compare_without(core, operator, ends[age + 1], law, stages[age + 1], following[1],
                                           (receiver_packet,), direct_coparents)
                    counts["one_receiver_removal_comparisons"] += 1
                    counts[f"one_receiver_removal_{mate['status']}"] += 1
                    if mate["status"] == "funded" and mate["pure_roster_and_fresh_changed"][0]:
                        counts["one_receiver_removal_changes_pure_fresh_or_roster"] += 1
                        examples.setdefault("one_receiver_removal_changes_pure_fresh_or_roster", {
                            **row, "receiver_side": receiver, "removed_coparents": sorted(direct_coparents),
                            "reduced_end_comparison": mate,
                        })
        for key, passed in flags.items():
            if passed:
                counts[key] += 1
                examples.setdefault(key, row)
    return {"counts": dict(counts), "first_examples": examples}


def end_distances(operator, end):
    graph = nx.Graph(operator.neighbors(end))
    return dict(nx.all_pairs_shortest_path_length(graph))


def distance_between(distances, a, b):
    if not a or not b:
        return None
    return min(distances[x][y] for x in a for y in b)


def inclusive_and_pure(stages, age, packet):
    inclusive, only_own = [frozenset(packet)], [frozenset(packet)]
    for stage in stages[age + 1:]:
        inclusive.append(reaches(stage.parents, inclusive[-1]))
        only_own.append(pure(stage.parents, only_own[-1]))
    return inclusive, only_own


def parent_path(stages, age, depth, child, family):
    path = [child]
    for step in range(depth, 0, -1):
        path.append(min(stages[age + step].parents[path[-1]] & family[step - 1]))
    return list(reversed(path))


def overlap_panel(stages, ages_distances, age, choices):
    """Compare every available subsequent overlap with the launch step distance."""
    trajectories = {group: inclusive_and_pure(stages, age, group) for group in choices}
    counts, examples = Counter(), {}
    counts["pure_vs_inclusive_retreats"] = 0
    for a, b in combinations(choices, 2):
        inc_a, pure_a = trajectories[a]
        inc_b, pure_b = trajectories[b]
        separation = distance_between(ages_distances[age], a, b)
        assert separation > 0
        counts[f"launch_step_distance_{separation}"] += 1
        horizon = len(inc_a) - 1
        expected = separation if separation <= horizon else None
        earliest = None
        previous_pure_distances = [separation, separation]
        for step in range(1, horizon + 1):
            counts["inclusive_continuation_comparisons"] += 1
            current = ages_distances[age + step]
            assert distance_between(current, inc_a[step], inc_b[step]) == max(separation - step, 0)
            common = inc_a[step] & inc_b[step]
            if common and earliest is None:
                earliest = step
                child = min(common)
                examples.setdefault(f"first_common_at{step}", {
                    "launch_age": age, "launch": [a, b], "separation": separation,
                    "preceding_inclusive": [sorted(inc_a[step - 1]), sorted(inc_b[step - 1])],
                    "joint_child": child,
                    "two_parent_paths": [parent_path(stages, age, step, child, family)
                                         for family in (inc_a, inc_b)],
                })
            for i, (own, other, other_pure) in enumerate((
                (pure_a, inc_b, pure_b), (pure_b, inc_a, pure_a),
            )):
                assert not own[step] & other[step]
                if own[step]:
                    counts["nonempty_pure_vs_inclusive_comparisons"] += 1
                    delta = distance_between(current, own[step], other[step])
                    assert delta >= previous_pure_distances[i]
                    if delta > previous_pure_distances[i]:
                        counts["pure_vs_inclusive_retreats"] += 1
                    previous_pure_distances[i] = delta
                if step >= 2 and own[step - 1]:
                    counts["later_pure_vs_inclusive_coparent_comparisons"] += 1
                    parents = stages[age + step].parents
                    result = both(parents, own[step - 1], other[step - 1])
                    # The entirely pure subset of the donor cannot provide that co-parent.
                    assert not both(parents, own[step - 1], other_pure[step - 1])
                    if result:
                        assert separation == 1
                        assert result == both(parents, own[step - 1], other[step - 1] - other_pure[step - 1])
                        counts["later_pure_has_other_inclusive_coparent"] += 1
                        counts["such_coparent_with_next_pure_still_present"] += bool(own[step])
                        examples.setdefault("later_pure_has_other_inclusive_coparent", {
                            "launch_age": age, "launch": [a, b], "receiver_side": i,
                            "step": step, "receiver_pure": sorted(own[step - 1]),
                            "donor_collateral": sorted(other[step - 1] - other_pure[step - 1]),
                            "children": sorted(result), "pure_continuation_at_same_step": sorted(own[step]),
                        })
        assert earliest == expected
        counts[f"first_common_at_{earliest}" if earliest else "first_common_outside_observed_horizon"] += 1
    return {"pair_count": sum(n for label, n in counts.items() if label.startswith("launch_step_distance_")),
            "horizon": len(stages) - age - 1, "counts": dict(counts), "first_examples": examples}


def candidate_coverage(operator, end, following):
    neighbors = operator.neighbors(end)
    candidates = {(v, w) for v, row in neighbors.items() for w in row if v < w}
    actual = Counter(pair for ps in following.parents.values() for pair in combinations(sorted(ps), 2))
    assert set(actual) == candidates
    return {"witnessed_pairs": len(candidates), "distinct_pairs_used_together": len(actual),
            "two_parent_births": sum(len(ps) == 2 for ps in following.parents.values()),
            "input_pair_incidences": sum(actual.values())}


def main():
    import sys
    sys.path.insert(0, str(PRIOR))
    import explosive as core

    raw = PRIOR_RESULT.read_bytes()
    assert sha256(raw).hexdigest() == IDENTIFIED_SOURCES_SHA256
    prior = json.loads(raw)
    archived = json.loads(core.AUDIT.read_text())["named_archive_starts"]
    controls = core.load("projected_law", core.SCAFFOLDS)
    literal = controls.load("literal_sampler", controls.BOND / "scaffolds.py")
    operator = controls.load("whole_step", controls.ORDINARY / "end_operator.py")
    assert set(prior["catalogue"]) == set(archived) and len(archived) == 16
    results = {}
    summary = {law: Counter() for law in core.LAWS}
    observed_types = {law: Counter() for law in core.LAWS}
    repeated_types_within_source = {law: Counter() for law in core.LAWS}
    for case, data in sorted(prior["catalogue"].items()):
        source = tuple(map(tuple, data["source"]))
        reference = archived[case]
        assert data["source"] == reference["gate"]["literal_supports"]
        assert data["original_identifier"] == reference["identifier"]
        assert core.source_gate(controls, literal, source, reference["gate"]["canonical"]) == data["source_gate"]
        readings = {}
        for law in core.LAWS:
            totals = summary[law]
            totals["archived_sources"] += 1
            if not data["source_gate"][law]["lawful"]:
                readings[law] = {"status": "unlawful_source"}
                continue
            totals["qualified_sources"] += 1
            stages = replay(core, literal, operator, source, law, data["laws"][law]["complete"])
            age_rows, ends, proposals = [], {0: operator.from_stars(stages[0].stars)}, {}
            ages_by_type = defaultdict(set)
            for age in range(1, len(stages)):
                ends[age], proposals[age], row = observe(literal, operator, stages, age)
                age_rows.append(row)
                totals["positive_cuts"] += 1
                totals["bounded_packet_classes"] += len(proposals[age])
                totals["bounded_packet_classes_matching_basic_signature"] += sum(
                    p["same_coarse_class"] for p in row["packet_classes"])
                for packet in row["packet_classes"]:
                    shape = packet["current_with_boundary_type"]
                    observed_types[law][shape] += 1
                    ages_by_type[shape].add(age)
                for label, flip in row["end_symmetry"].items():
                    totals[f"cuts_tested_{label}"] += 1
                    totals[f"cuts_with_{label}"] += flip["moves"] is not None
            ages_distances = {age: end_distances(operator, end) for age, end in ends.items()}
            for row in age_rows[:-1]:
                age = row["age"]
                row["candidate_coverage"] = candidate_coverage(operator, ends[age], stages[age+1])
                for k, v in row["candidate_coverage"].items():
                    totals[f"positive_cut_candidate_coverage_{k}"] += v
                cases = {"singletons": [(v,) for v in ends[age].opens], "packets": proposals[age]}
                row["pair_panels"] = {
                    panel: pair_panel(core, operator, law, age, stages, ends, choices, compare_removal=panel == "packets")
                    for panel, choices in cases.items()
                }
                for panel, value in row["pair_panels"].items():
                    totals.update({f"{panel}_{k}": n for k, n in value["counts"].items()})
                row["overlap_panels"] = {
                    panel: overlap_panel(stages, ages_distances, age, choices) for panel, choices in cases.items()
                }
                for panel, value in row["overlap_panels"].items():
                    totals.update({f"overlap_positive_{panel}_{k}": n for k, n in value["counts"].items()})
            source_overlap = overlap_panel(stages, ages_distances, 0, [(v,) for v in ends[0].opens])
            totals.update({f"overlap_source_cut_{k}": n for k, n in source_overlap["counts"].items()})
            for shape, ages in ages_by_type.items():
                if len(ages) > 1:
                    repeated_types_within_source[law][shape] += 1
            readings[law] = {"status": "replayed", "cuts": age_rows, "source_overlap": source_overlap,
                             "source_candidate_coverage": candidate_coverage(operator, ends[0], stages[1])}
        results[case] = {"original_identifier": data["original_identifier"],
                         "source": source, "source_gate": data["source_gate"], "laws": readings}
    record = {"design_freeze": DESIGN_FREEZE, "source_receipt_sha256": IDENTIFIED_SOURCES_SHA256,
              "source_audit_sha256": sha256(core.AUDIT.read_bytes()).hexdigest(),
              "weighting": "One per archived jump-selected cap-seven draw, including equivalent starts.",
              "caps": {"knots": core.MAX_KNOTS, "distinctions": core.MAX_DISTINCTIONS,
                       "complete_steps": core.MAX_ROUNDS, "packet_width": MAX_PACKET_WIDTH,
                       "pair_panel_followups": 2, "overlap_panel_followups": "all available through step four"},
              "summary": summary, "cases": results,
              "current_packet_types": {
                  law: [{"type": shape, "classes": n, "sources_repeating_at_distinct_cuts": repeated[shape]}
                        for shape, n in sorted(shapes.items())]
                  for law, shapes in observed_types.items()
                  for repeated in (repeated_types_within_source[law],)
              }}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=OUT.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(record, out, separators=(",", ":"), sort_keys=True)
        out.write("\n")
    temporary.replace(OUT)


if __name__ == "__main__":
    main()
