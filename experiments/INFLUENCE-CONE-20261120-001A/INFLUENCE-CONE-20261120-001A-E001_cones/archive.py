"""Paired additions of one loose distinction to the admitted jump archive."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import chain
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
PRIOR_SHA256 = "b4281bc1948cfe612a3a02d3c320cec5f33cfbad02476de543f1717b2e7241e0"
MAX_LAYERS, MAX_BIRTHS = 3, 128
DESIGN_FREEZE = "745710806"


@dataclass
class Stage:
    stars: tuple
    origins: dict
    births: dict


def union_origins(previous, parents):
    mask = 0
    for parent in parents:
        mask |= previous[parent]
    return mask


def replay(core, literal, operator, serial, source, law, *, receipt=None):
    stages = [Stage(source, {v: 1 << v for v in range(len(source))}, {})]
    end = {"status": "layer_limit"}
    for age in range(1, MAX_LAYERS + 1):
        old = stages[-1]
        turn = operator.step(operator.from_stars(old.stars), law, max_births=MAX_BIRTHS)
        if turn.status != "extend":
            end = {"status": turn.status, "next_age": age, "shortages": turn.shortages,
                   "plan_births_lower": turn.planned_births_lower}
            break
        plan = {"parents": turn.parents, "fresh": turn.fresh, "demand": turn.demand}
        allocated = core.allocate(literal, old.stars, plan)
        stars = core.replay_cohort(literal, old.stars, allocated, range(len(allocated)))
        core.archive_turn(serial, old.stars, law, plan, stars)
        births = {}
        origins = {}
        owner = literal.owners(old.stars)
        for i, (parents, demand, (spent, fresh)) in enumerate(
            zip(turn.parents, turn.demand, allocated, strict=True), start=len(old.stars)
        ):
            assert all(tuple(owner[d]) == (p,) for p, d in zip(parents, spent, strict=True))
            assert all(d not in owner for d in fresh)
            births[i] = {"parents": parents, "demand": demand, "spent": spent, "fresh": fresh}
            origins[i] = union_origins(old.origins, parents)
        stages.append(Stage(stars, origins, births))
        if receipt is not None:
            before = receipt["ages"][age]
            assert (len(stars), len(literal.owners(stars)), len(births)) == (
                before["knots"], before["distinctions"], before["births"]
            )
        if turn.implied:
            end = {"status": "closed_after_birth", "age": age}
            break
    return stages, end


def edited_source(source, holder):
    extra = max(chain.from_iterable(source)) + 1
    after = list(source)
    after[holder] = (*after[holder], extra)
    return tuple(after), extra


def exact_source_gate(core, controls, literal, stars):
    valid = all(rank == 1 and len(star) >= 3
                for rank, star in zip(controls.parity_profile(stars), stars, strict=True))
    return core.source_gate(controls, literal, stars, valid)


def source_rulers(literal, operator, source):
    end = operator.from_stars(source)
    common = nx.Graph(operator.neighbors(end))
    exact_pair = nx.Graph()
    exact_pair.add_nodes_from(end.opens)
    exact_pair.add_edges_from(group for group in operator.proposals(end) if len(group) == 2)
    physical = nx.Graph(dict(enumerate(literal.holder_graph(source))))
    return {
        name: dict(nx.all_pairs_shortest_path_length(graph))
        for name, graph in (("witnessed", common), ("two_inputs_only", exact_pair), ("physical", physical))
    }


def birth_graph(stages, age, chosen, *, fresh=False, original_names=None):
    """Complete ancestors of chosen outputs, with original knot identities fixed."""
    graph = nx.DiGraph()
    open_nodes = set(chosen)
    for generation in range(age, -1, -1):
        earlier = set()
        for v in sorted(open_nodes):
            if generation == 0:
                label = (generation, original_names[v] if original_names is not None else v)
            elif generation == age and fresh:
                label = (generation, len(stages[generation].births[v]["fresh"]))
            else:
                label = (generation,)
            graph.add_node(v, color=label)
            if generation > 0:
                parents = stages[generation].births[v]["parents"]
                graph.add_edges_from((p, v) for p in parents)
                earlier.update(parents)
        open_nodes = earlier
    return graph


def same_birth_graph(base, edit, age, left, right, *, fresh=False):
    if len(left) != len(right):
        return False
    if not left:
        return True
    first, second = (birth_graph(a, age, group, fresh=fresh) for a, group in ((base, left), (edit, right)))
    return nx.vf2pp_is_isomorphic(first, second, node_label="color")


def receiver_births(stage, receiver, *, pure=False):
    token = 1 << receiver
    return tuple(v for v, ancestry in stage.origins.items() if (ancestry == token if pure else ancestry & token))


def output_summary(stage, chosen):
    budgets = [len(stage.births[v]["fresh"]) for v in chosen]
    return {"births": len(chosen), "fresh_total": sum(budgets), "fresh_counts": sorted(budgets),
            "arity_counts": dict(sorted(Counter(len(stage.births[v]["parents"]) for v in chosen).items()))}


def joint_children(stage, b, u):
    mask = (1 << b) | (1 << u)
    return tuple(v for v, origins in stage.origins.items() if origins & mask == mask)


def layer_compare(base, edit, age, receiver):
    stages = base[age], edit[age]
    births = tuple(receiver_births(stage, receiver) for stage in stages)
    pure = tuple(receiver_births(stage, receiver, pure=True) for stage in stages)
    if age == 1:
        # Every parent is a named original holder at the first step. Compare
        # exact multisets directly, including identical unary placements.
        row_sets = [Counter(stage.births[v]["parents"] for v in names)
                    for stage, names in zip(stages, births, strict=True)]
        roster_agrees = row_sets[0] == row_sets[1]
        multi_agrees = ({p: n for p, n in row_sets[0].items() if len(p) > 1} ==
                        {p: n for p, n in row_sets[1].items() if len(p) > 1})
        priced = [Counter((stage.births[v]["parents"], len(stage.births[v]["fresh"])) for v in names)
                  for stage, names in zip(stages, births, strict=True)]
        priced_agrees = priced[0] == priced[1]
    else:
        roster_agrees = same_birth_graph(base, edit, age, *births)
        multi_births = [tuple(v for v in names if len(stage.births[v]["parents"]) >= 2)
                        for stage, names in zip(stages, births, strict=True)]
        multi_agrees = roster_agrees or same_birth_graph(base, edit, age, *multi_births)
        priced_agrees = roster_agrees and same_birth_graph(base, edit, age, *births, fresh=True)
    readouts = [output_summary(stage, names) for stage, names in zip(stages, births, strict=True)]
    pure_readouts = [output_summary(stage, names) for stage, names in zip(stages, pure, strict=True)]
    return {
        "age": age, "compared_receiver_births": births,
        "compared_pure_births": pure, "all_outputs": readouts, "pure_outputs": pure_readouts,
        "same_parent_roster": roster_agrees, "same_multi_parent_roster": multi_agrees,
        "same_roster_with_fresh_counts": priced_agrees,
        "fresh_only_change": roster_agrees and not priced_agrees,
    }


def contact_age(stages, edited_holder, receiver):
    for age, stage in enumerate(stages[1:], 1):
        common = joint_children(stage, edited_holder, receiver)
        if common:
            return age, common
    return None, ()


def episode(base, edit, edited_holder, receiver, rulers):
    distances = {name: data[edited_holder].get(receiver) for name, data in rulers.items()}
    compared = min(len(base), len(edit)) - 1
    contacts = [contact_age(stages, edited_holder, receiver) for stages in (base, edit)]
    levels = [layer_compare(base, edit, age, receiver) for age in range(1, compared + 1)]
    first_change = next((row["age"] for row in levels if not row["same_roster_with_fresh_counts"]), None)
    return {
        "receiver": receiver, "original_distances": distances,
        "first_joint_age": [row[0] for row in contacts], "first_joint_children": [row[1] for row in contacts],
        "first_change": first_change, "layers": levels,
    }


def source_budget_control(before, after, b):
    if len(before) < 2 or len(after) < 2:
        return None
    known = before[1].births.values()
    predicted = Counter()
    for row in known:
        group = row["parents"]
        demand = row["demand"] + (b in group)
        predicted[(group, max(demand, 3 - len(group), 1))] += 1
    predicted[((b,), max(sum(b in row["parents"] for row in known), 2))] += 1
    measured = Counter((row["parents"], len(row["fresh"])) for row in after[1].births.values())
    return predicted == measured


def stage_receipt(stages, stop):
    return {"stop": stop, "layers": [
        {"age": age, "knots": len(stage.stars), "distinctions": len(set(chain.from_iterable(stage.stars))),
         "births": stage.births}
        for age, stage in enumerate(stages)
    ]}


def episode_counts(row, totals, levels):
    if not row["layers"]:
        totals["uncompared_episodes"] += 1
    if len(row["layers"]) < MAX_LAYERS:
        totals["censored_episodes"] += 1
    times = row["original_distances"]
    totals["episodes_with_no_exact_binary_route"] += times["two_inputs_only"] is None
    depth = len(row["layers"])
    for end_age in row["first_joint_age"]:
        expected = times["witnessed"] if times["witnessed"] is not None and times["witnessed"] <= depth else None
        if end_age is not None and end_age <= depth and end_age != expected:
            totals["contact_distance_disagreements"] += 1
        if end_age is None and expected is not None:
            totals["contact_distance_disagreements"] += 1
    first = row["first_change"]
    if first is None:
        totals["no_change_observed"] += 1
    else:
        totals[f"first_change_{first}"] += 1
        if all(contact is None or first < contact for contact in row["first_joint_age"]):
            totals["first_change_before_actual_contact"] += 1
    for level in row["layers"]:
        age = level["age"]
        count = levels[age]
        count["compared"] += 1
        if level["same_roster_with_fresh_counts"]:
            continue
        count["any_change"] += 1
        count["fresh_only_change"] += level["fresh_only_change"]
        count["roster_change"] += not level["same_parent_roster"]
        count["multi_parent_roster_change"] += not level["same_multi_parent_roster"]
        count["inclusive_birth_count_change"] += level["all_outputs"][0]["births"] != level["all_outputs"][1]["births"]
        count["pure_output_totals_change"] += level["pure_outputs"][0] != level["pure_outputs"][1]
        count["before_actual_joint_descendant"] += all(contact is None or age < contact for contact in row["first_joint_age"])
        count["roster_change_no_later_than_witnessed_distance"] += (
            not level["same_parent_roster"] and times["witnessed"] is not None and age <= times["witnessed"])
        count["before_binary_step_distance"] += times["two_inputs_only"] is not None and age < times["two_inputs_only"]
        count["no_binary_step_route"] += times["two_inputs_only"] is None
        count["before_source_physical_step_distance"] += times["physical"] is not None and age < times["physical"]


def renaming_control(core, literal, operator, serial, baseline, edited, b, law):
    """Replay both arms after one independent knot and distinction permutation."""
    source = baseline[0].stars
    rng = Random(20261120854)
    names = list(range(len(source)))
    places = sorted(literal.owners(source))
    new_places = places[:]
    rng.shuffle(names)
    rng.shuffle(new_places)
    recode = dict(zip(places, new_places, strict=True))
    inverted = {v: u for u, v in enumerate(names)}
    moved = [()] * len(names)
    for old, row in enumerate(source):
        moved[names[old]] = tuple(sorted(recode[d] for d in row))
    recoded_rulers = source_rulers(literal, operator, tuple(moved))
    rulers = source_rulers(literal, operator, source)
    original_live = operator.from_stars(source).opens
    for label, all_distances in rulers.items():
        for p in original_live:
            for q in original_live:
                assert all_distances[p].get(q) == recoded_rulers[label][names[p]].get(names[q])
    plans = [tuple(moved), edited_source(tuple(moved), names[b])[0]]
    for original, recoded in zip((baseline, edited), plans, strict=True):
        after, stop = replay(core, literal, operator, serial, recoded, law)
        assert stop["status"] == "layer_limit" and len(original) == len(after)
        for age in range(1, len(after)):
            left = birth_graph(original, age, original[age].births, fresh=True)
            right = birth_graph(after, age, after[age].births, fresh=True, original_names=inverted)
            assert nx.vf2pp_is_isomorphic(left, right, node_label="color")
    return {"checked_layers_per_arm": len(baseline) - 1, "two_arms": True,
            "both_kinds_of_name_changed": True, "preserves_all_three_initial_rulers": True}


def main():
    import sys
    sys.path.insert(0, str(PRIOR))
    import explosive as core

    old_data = PRIOR_RESULT.read_bytes()
    assert sha256(old_data).hexdigest() == PRIOR_SHA256
    prior = json.loads(old_data)["catalogue"]
    audited = json.loads(core.AUDIT.read_text())["named_archive_starts"]
    controls = core.load("law_checks", core.SCAFFOLDS)
    literal = controls.load("physical_holdings", controls.BOND / "scaffolds.py")
    operator = controls.load("complete_rule", controls.ORDINARY / "end_operator.py")
    serial = core.load("archived_complete_growth", core.SERIAL)
    assert set(prior) == set(audited) and len(prior) == 16
    cases = {}
    zero_fields = ("first_change_before_actual_contact", "contact_distance_disagreements", "censored_episodes",
                   "uncompared_episodes", "edit_law_failure", "base_not_admitted")
    totals = {law: Counter(dict.fromkeys(zero_fields, 0)) for law in core.LAWS}
    layers = {law: {i: Counter() for i in range(1, MAX_LAYERS + 1)} for law in core.LAWS}
    distance_histograms = {law: {name: Counter() for name in ("witnessed", "two_inputs_only", "physical")}
                           for law in core.LAWS}
    recoding = {}
    for case, old in sorted(prior.items()):
        source = tuple(map(tuple, old["source"]))
        assert old["source"] == audited[case]["gate"]["literal_supports"]
        assert old["original_identifier"] == audited[case]["identifier"]
        gate = exact_source_gate(core, controls, literal, source)
        assert gate == old["source_gate"]
        live = tuple(operator.from_stars(source).opens)
        readouts = {}
        cases[case] = {"identifier": old["original_identifier"], "source": source,
                       "live": live, "law_gate": gate, "laws": readouts}
        if not any(status["lawful"] for status in gate.values()):
            for law in core.LAWS:
                totals[law]["base_not_admitted"] += 1
                readouts[law] = {"status": "unlawful_baseline"}
            continue
        rulers = source_rulers(literal, operator, source)
        edit_gates = {}
        for b in live:
            edited, extra = edited_source(source, b)
            edit_gates[b] = (edited, extra, exact_source_gate(core, controls, literal, edited))
            new_end = operator.from_stars(edited)
            assert tuple(new_end.opens) == live and new_end.blocks == operator.from_stars(source).blocks
        for law in core.LAWS:
            if not gate[law]["lawful"]:
                totals[law]["base_not_admitted"] += 1
                readouts[law] = {"status": "unlawful_baseline"}
                continue
            totals[law]["admitted_sources"] += 1
            baseline, stop = replay(core, literal, operator, serial, source, law, receipt=old["laws"][law]["complete"])
            totals[law][f"baseline_stop_{stop['status']}"] += 1
            edits = {}
            readouts[law] = {"status": "admitted", "baseline": stage_receipt(baseline, stop), "edits": edits}
            for b, (edited, extra, edited_gate) in edit_gates.items():
                totals[law]["edit_trials"] += 1
                if not edited_gate[law]["lawful"]:
                    totals[law]["edit_law_failure"] += 1
                    edits[b] = {"status": "unlawful_edit", "law_gate": edited_gate}
                    continue
                changed, edited_stop = replay(core, literal, operator, serial, edited, law)
                totals[law][f"edit_stop_{edited_stop['status']}"] += 1
                prediction = source_budget_control(baseline, changed, b)
                totals[law]["first_round_prediction_trials"] += prediction is not None
                totals[law]["first_round_prediction_matches"] += prediction is True
                episodes = {}
                edits[b] = {"status": "admitted", "extra_distinction": extra, "law_gate": edited_gate,
                            "stages": stage_receipt(changed, edited_stop),
                            "first_round_budget_prediction_match": prediction, "episodes": episodes}
                if law not in recoding and stop["status"] == edited_stop["status"] == "layer_limit":
                    recoding[law] = {"case": case, "original_edited_holder": b,
                                     **renaming_control(core, literal, operator, serial, baseline, changed, b, law)}
                for u in live:
                    if u == b:
                        continue
                    row = episode(baseline, changed, b, u, rulers)
                    episodes[u] = row
                    totals[law]["receiver_episodes"] += 1
                    for name, distance in row["original_distances"].items():
                        distance_histograms[law][name][str(distance) if distance is not None else "disconnected"] += 1
                    episode_counts(row, totals[law], layers[law])
    record = {"design_freeze": DESIGN_FREEZE, "bounds": {"layers": MAX_LAYERS, "births_per_layer": MAX_BIRTHS},
              "archived_descriptions": len(prior), "source_receipt_sha256": PRIOR_SHA256,
              "weighting": "One per cap-seven archived jump description, with all ordered distinct live root pairs.",
              "summary": totals, "by_layer": layers, "source_distance_histograms": distance_histograms,
              "literal_renaming_control": recoding,
              "cases": cases}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=OUT.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(record, handle, separators=(",", ":"), sort_keys=True)
        handle.write("\n")
    temporary.replace(OUT)


if __name__ == "__main__":
    main()
