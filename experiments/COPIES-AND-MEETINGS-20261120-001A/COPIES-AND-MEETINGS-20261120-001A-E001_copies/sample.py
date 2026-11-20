"""Frozen sample of singleton lineages and indirect common ancestry under ordinary growth."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample.json"
DESIGN = ROOT / "research/COPIES-AND-MEETINGS-20261120-001/preregistration.md"
SEEDS = {"tree": 20261120741, "augmented_tree": 20261120742}
LAWS = ("parity", "nae")
PER_SIZE = 48
LAYERS = 4
CAP = 128


@cache
def archive():
    source = ROOT / ("experiments/GENERATORS-20261120-001A/"
                     "GENERATORS-20261120-001A-E001_generators/sample.py")
    spec = spec_from_file_location("copies_generators_archive", source)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_draws():
    for name, seed in SEEDS.items():
        rng = random.Random(seed)
        for n in range(4, 9):
            for i in range(PER_SIZE):
                word = [rng.randrange(n) for _ in range(n - 2)]
                graph = nx.from_prufer_sequence(word)
                added = None
                if name == "augmented_tree":
                    added = rng.choice([g for g in combinations(range(n), 2) if not graph.has_edge(*g)])
                    graph.add_edge(*added)
                meetings = sorted(tuple(sorted(g)) for g in graph.edges)
                spare = [int(rng.randrange(4) == 0) for _ in range(n)]
                arities = [max(3, graph.degree(v)) + spare[v] for v in range(n)]
                yield {"draw": f"{name}/{n}/{i:02d}", "weighting": name, "source_knots": n,
                       "prufer": word, "added_meeting": added, "extra_loose": spare,
                       "meetings": meetings, "arities": arities}


def frame(presentation, prior_births):
    end, observation = archive().readings(presentation, prior_births)
    opens, witness_rows = observation["loose"], observation["witnesses"]
    direct = [pair for pair in combinations(opens, 2) if pair[1] in presentation.nbr[pair[0]]]
    return end, {"loose": opens, "witnesses": witness_rows, "components": observation["witnessed_end"]["components"],
                 "direct_meetings": direct, "arity": {v: len(presentation.bits_of[v]) for v in opens}}


def actual_history(stars, law, lawful):
    if not lawful:
        return {"status": "unlawful_source", "frames": [], "transitions": []}
    old = archive()
    _, oracle, nae = old.libraries()
    physical = nae.S.from_junctions(stars)
    state, snapshot = frame(physical, None)
    frames, steps = [snapshot], []
    terminal = "formation_limit"
    for age in range(LAYERS):
        assert len(state.opens) <= CAP
        planned = oracle.step(state, law, max_births=CAP)
        step = {"age": age, "ordinary_plan": old.plan_receipt(planned), "births": []}
        steps.append(step)
        if planned.status in {"closed", "cap"}:
            terminal = "closed" if planned.status == "closed" else "birth_cap"
            break
        births = old.literal_step(physical, law, planned)
        if planned.status == "stall":
            step["unfunded_multi_parent_proposals"] = oracle.proposals(state)
            terminal = "stall"
            break
        if any(len(b["parents"]) + b["fresh"] < 3 for b in births):
            assert law == "parity" and len(births) == 1 and planned.implied
            step["rejected_legacy_closer"] = births[0]
            terminal = "legacy_subarity_stop"
            break
        step["births"] = births
        state, snapshot = frame(physical, births)
        old.verify_following(planned, births, state)
        frames.append(snapshot)
        if not state.opens:
            terminal = "closed"
            break
    return {"status": terminal, "frames": frames, "transitions": steps}


def distance_from(first, graph):
    steps = {first: 0}
    route = [first]
    for v in route:
        for w in graph[v] - steps.keys():
            steps[w] = steps[v] + 1
            route.append(w)
    return steps


def witness_features(snapshot):
    opens, witnesses = snapshot["loose"], snapshot["witnesses"]
    graph, pair_counts = archive().graph_from_witnesses(opens, witnesses)
    distances = {v: distance_from(v, graph) for v in graph}
    local = {v: (opens[v], len(graph[v]), tuple(sorted(len(w) for w in witnesses.values() if v in w))) for v in graph}
    return graph, pair_counts, distances, local


def min_distance(left, right, distances):
    return min((distances[v][w] for v in left for w in right if w in distances[v]), default=None)


def pure_and_ancestry(layers, geometries, first, second):
    """Track each next birth using only its immutable literal parent set."""
    desc_a, desc_b = {first}, {second}
    pure_a, pure_b = {first}, {second}
    results = []
    for age, births in enumerate(layers):
        next_desc_a, next_desc_b, next_pure_a, next_pure_b = set(), set(), set(), set()
        direct, mediated, mixed_ancestry = [], [], []
        for b in births:
            child = b["knot"]
            ps = set(b["parents"])
            assert ps
            has_a, has_b = bool(ps & desc_a), bool(ps & desc_b)
            pure_parent_a, pure_parent_b = bool(ps & pure_a), bool(ps & pure_b)
            if has_a:
                next_desc_a.add(child)
            if has_b:
                next_desc_b.add(child)
            if has_a and has_b:
                mixed_ancestry.append(child)
            if pure_parent_a and pure_parent_b:
                direct.append(child)
            elif (pure_parent_a and has_b) or (pure_parent_b and has_a):
                mediated.append(child)
            if b["fresh"] and ps <= pure_a:
                next_pure_a.add(child)
            if b["fresh"] and ps <= pure_b:
                next_pure_b.add(child)
        before, after = geometries[age][2], geometries[age + 1][2]
        inclusive_distance, pure_distances = None, []
        if after:
            prior = min_distance(desc_a, desc_b, before)
            following = min_distance(next_desc_a, next_desc_b, after)
            assert following == (None if prior is None else max(0, prior - 1))
            inclusive_distance = (prior, following)
            for name, pure, other, next_pure, next_other in (
                ("A", pure_a, desc_b, next_pure_a, next_desc_b), ("B", pure_b, desc_a, next_pure_b, next_desc_a),
            ):
                if next_pure:
                    far_before = min_distance(pure, other, before)
                    far_after = min_distance(next_pure, next_other, after)
                    assert far_after is None or (far_before is not None and far_before <= far_after)
                    pure_distances.append((name, far_before, far_after))
        desc_a, desc_b = next_desc_a, next_desc_b
        pure_a, pure_b = next_pure_a, next_pure_b
        assert not pure_a & pure_b
        assert pure_a <= desc_a and pure_b <= desc_b
        results.append({"pure_sizes": (len(pure_a), len(pure_b)), "ancestry_sizes": (len(desc_a), len(desc_b)),
                        "direct": direct, "indirect_with_one_pure_parent": mediated, "both_ancestries": mixed_ancestry,
                        "inclusive_distance": inclusive_distance, "pure_vs_other_inclusive_distances": pure_distances})
    return results


def one_knot_signature(snapshot, knot):
    return snapshot["arity"][knot], snapshot["loose"][knot]


def same_type_singleton_run(frames, layers, first, second):
    """Existence of a further width-one pure path on each side with the same holding type."""
    old_a, old_b = {first}, {second}
    code_a = one_knot_signature(frames[0], first)
    code_b = one_knot_signature(frames[0], second)
    if code_a != code_b:
        return None
    extra = 0
    for snapshot, births in zip(frames[1:], layers, strict=True):
        a, b = set(), set()
        for v in births:
            knot = v["knot"]
            if not v["fresh"] or len(v["parents"]) != 1 or one_knot_signature(snapshot, knot) != code_a:
                continue
            parent, = v["parents"]
            if parent in old_a:
                a.add(knot)
            if parent in old_b:
                b.add(knot)
        if not a or not b:
            break
        old_a, old_b = a, b
        extra += 1
    return extra


def new_counters():
    return {"opportunities": 0, "with_at_least_one_followup": 0, "with_at_least_two_followups": 0,
            "with_any_common_ancestry": 0, "with_delayed_common_ancestry": 0,
            "both_pure_live_at_first_common_ancestry": 0, "both_pure_live_after_first_common_ancestry": 0,
            "both_pure_live_at_first_common_with_one_more_layer_observed": 0,
            "with_direct_pure_child": 0, "with_mediated_birth": 0, "with_mediated_birth_and_both_pure_live": 0,
            "with_mediated_birth_and_both_pure_one_further_step": 0,
            "both_pure_live_at_two_steps": 0, "same_holding_type": 0, "same_type_width_one_continues_one": 0,
            "same_type_width_one_continues_two": 0, "same_type_width_one_continues_three": 0,
            "same_type_width_one_continues_four": 0, "inclusive_step_distance_tests": 0,
            "inclusive_step_finite_decreases": 0, "pure_vs_inclusive_distance_tests": 0,
            "pure_vs_inclusive_distance_increases": 0, "pure_vs_inclusive_finite_to_infinite": 0,
            "terminal_birth_layers_without_live_distance": 0}


def pair_result(frames, layers, geometries, pair, distance, co_witnesses):
    if layers:
        continuation = pure_and_ancestry(layers, geometries, *pair)
        combined = next((i for i, step in enumerate(continuation, 1) if step["both_ancestries"]), None)
        direct = next((i for i, step in enumerate(continuation, 1) if step["direct"]), None)
        mediated = next((i for i, step in enumerate(continuation, 1) if step["indirect_with_one_pure_parent"]), None)
        two_pure = next((i for i, step in enumerate(continuation, 1)
                         if step["indirect_with_one_pure_parent"] and all(step["pure_sizes"])), None)
        assert direct == (1 if co_witnesses else None)
        assert all(not row["direct"] for row in continuation[1:])
        expected = distance if distance is not None and distance <= len(layers) else None
        assert combined == expected
        assert mediated is None or mediated >= 2
    else:
        continuation, combined, direct, mediated, two_pure = [], None, None, None, None
    same_type = same_type_singleton_run(frames, layers, *pair)
    return {"steps_observed": len(layers), "candidate_step_distance": distance, "common_witnesses": co_witnesses,
            "first_common_ancestry": combined, "first_direct_pure_child": direct,
            "first_mediated_birth": mediated, "first_mediated_birth_and_both_pure_live": two_pure,
            "same_type_width_one_steps": same_type, "continuation": continuation}


def update_counts(target, receipt):
    steps = receipt["steps_observed"]
    combined = receipt["first_common_ancestry"]
    same_type = receipt["same_type_width_one_steps"]
    target["opportunities"] += 1
    target["with_at_least_one_followup"] += steps >= 1
    target["with_at_least_two_followups"] += steps >= 2
    target["with_any_common_ancestry"] += combined is not None
    target["with_delayed_common_ancestry"] += combined is not None and combined >= 2
    pure_at_common = combined is not None and all(receipt["continuation"][combined - 1]["pure_sizes"])
    target["both_pure_live_at_first_common_ancestry"] += pure_at_common
    target["both_pure_live_at_first_common_with_one_more_layer_observed"] += pure_at_common and steps > combined
    target["both_pure_live_after_first_common_ancestry"] += combined is not None and steps > combined and all(
        receipt["continuation"][combined]["pure_sizes"])
    target["with_direct_pure_child"] += receipt["first_direct_pure_child"] is not None
    target["with_mediated_birth"] += receipt["first_mediated_birth"] is not None
    coexistence = receipt["first_mediated_birth_and_both_pure_live"]
    target["with_mediated_birth_and_both_pure_live"] += coexistence is not None
    target["with_mediated_birth_and_both_pure_one_further_step"] += coexistence is not None and steps > coexistence and all(
        receipt["continuation"][coexistence]["pure_sizes"])
    target["both_pure_live_at_two_steps"] += steps >= 2 and all(receipt["continuation"][1]["pure_sizes"])
    target["same_holding_type"] += same_type is not None
    target["same_type_width_one_continues_one"] += same_type is not None and same_type >= 1
    target["same_type_width_one_continues_two"] += same_type is not None and same_type >= 2
    target["same_type_width_one_continues_three"] += same_type is not None and same_type >= 3
    target["same_type_width_one_continues_four"] += same_type is not None and same_type >= 4
    for row in receipt["continuation"]:
        transferred = row["inclusive_distance"]
        if transferred is None:
            target["terminal_birth_layers_without_live_distance"] += 1
            continue
        target["inclusive_step_distance_tests"] += 1
        target["inclusive_step_finite_decreases"] += transferred[0] is not None and transferred[1] < transferred[0]
        for _, old, new in row["pure_vs_other_inclusive_distances"]:
            target["pure_vs_inclusive_distance_tests"] += 1
            target["pure_vs_inclusive_distance_increases"] += old is not None and new != old
            target["pure_vs_inclusive_finite_to_infinite"] += old is not None and new is None


def coarse_signature(local, pair, distance, witness_count, steps):
    return (*sorted(local[v] for v in pair), witness_count, distance, steps)


def pair_panel(run):
    frames, steps = run["frames"], run["transitions"]
    layers = [s["births"] for s in steps if s["births"]]
    assert len(layers) == len(frames) - 1 or not frames
    geometries = [witness_features(s) for s in frames]
    records = []
    for age, snapshot in enumerate(frames):
        _, witnesses, distances, local = geometries[age]
        parentage = {b["knot"]: b["parents"] for b in layers[age - 1]} if age else {}
        smallest = {part[0] for part in snapshot["components"] if len(part) == 1}
        actual_meetings = set(snapshot["direct_meetings"])
        census = defaultdict(new_counters)
        ancestor_delays, mediated_delays = Counter(), Counter()
        visible_profiles = defaultdict(Counter)
        examples = {}
        for a, b in combinations(snapshot["loose"], 2):
            pair = (a, b)
            d = distances[a].get(b)
            witness_count = witnesses[pair]
            shared_distinction = pair in actual_meetings
            unary_siblings = a in parentage and len(parentage[a]) == 1 and parentage.get(b) == parentage[a]
            receipt = pair_result(frames[age:], layers[age:], geometries[age:], pair, d, witness_count)
            families = ["all", "with_witness" if witness_count else "no_witness"]
            if not witness_count and not shared_distinction:
                families.append("neither_witness_nor_shared_distinction")
            if d is None:
                families.append("different_whole_components")
            if a in smallest and b in smallest:
                families.append("both_whole_component_singletons")
            if unary_siblings:
                families.append("same_parent_unary_siblings")
            if not witness_count and receipt["steps_observed"] >= 2:
                families.append("delayed_eligible")
                if d is not None:
                    families.append("delayed_eligible_same_component")
                if not shared_distinction:
                    families.append("delayed_eligible_no_ordinary_meeting")
            for family in families:
                update_counts(census[family], receipt)
            if not witness_count and receipt["first_common_ancestry"] is not None:
                ancestor_delays[receipt["first_common_ancestry"]] += 1
                examples.setdefault("delayed_common_ancestry", {"pair": pair, "had_ordinary_meeting": shared_distinction, **receipt})
            if not witness_count and receipt["first_mediated_birth"] is not None:
                mediated_delays[receipt["first_mediated_birth"]] += 1
                examples.setdefault("delayed_mediated", {"pair": pair, "had_ordinary_meeting": shared_distinction, **receipt})
                if receipt["first_mediated_birth_and_both_pure_live"] is not None:
                    examples.setdefault("delayed_mediated_both_pure_live", {"pair": pair, "had_ordinary_meeting": shared_distinction, **receipt})
            if unary_siblings and receipt["same_type_width_one_steps"]:
                examples.setdefault("same_parent_width_one", {"pair": pair, "shared_parent": parentage[a][0], **receipt})
            if receipt["steps_observed"] >= 2 and not witness_count:
                signature = coarse_signature(local, pair, d, witness_count, receipt["steps_observed"])
                key = json.dumps(signature, separators=(",", ":"))
                visible_profiles[key]["outcome_yes" if all(receipt["continuation"][1]["pure_sizes"]) else "outcome_no"] += 1
        records.append({"anchor_age": age, "observed_steps_after_frame": len(layers) - age,
                        "pair_families": {k: {m: v for m, v in counts.items() if v} for k, counts in census.items()},
                        "delays_common_ancestry": dict(ancestor_delays),
                        "delays_mediated": dict(mediated_delays), "witness_count_profiles": dict(visible_profiles),
                        "examples": examples})
    return records


def singleton_releases(run):
    """Each event here is a pair of same-type unary births from one actual parent."""
    groups = []
    for step in run["transitions"]:
        by_parent_and_type = defaultdict(list)
        for b in step["births"]:
            if len(b["parents"]) == 1 and b["fresh"]:
                p, = b["parents"]
                by_parent_and_type[p, (1 + b["fresh"], b["fresh"])].append(b["knot"])
        for (parent, kind), children in sorted(by_parent_and_type.items()):
            if len(children) >= 2:
                groups.append({"age": step["age"] + 1, "parent": parent, "same_type_unary_births": children,
                               "type": kind, "unordered_sibling_pairs": len(children) * (len(children) - 1) // 2})
    by_type = defaultdict(set)
    for g in groups:
        by_type[g["type"]].add(g["age"])
    return {"release_groups": groups,
            "same_type_released_at_multiple_ages": [{"type": kind, "ages": sorted(ages)} for kind, ages in sorted(by_type.items())
                                                   if len(ages) > 1]}


def witnessed_graph(snapshot, pair=()):
    graph = nx.Graph()
    graph.add_nodes_from((("holder", v), {"kind": ("live", opens, v in pair)}) for v, opens in snapshot["loose"].items())
    for witness, members in snapshot["witnesses"].items():
        w = ("witness", witness)
        graph.add_node(w, kind=("witness",))
        graph.add_edges_from((w, ("holder", v)) for v in members)
    return graph


def end_forecast_two(snapshot, pair, law):
    """No physical history or holder arity enters the complete witnessed-end forecast."""
    _, operator, _ = archive().libraries()
    state = operator.End(snapshot["loose"], tuple(snapshot["witnesses"].values()))
    inclusive = [{v} for v in pair]
    for _ in range(2):
        turn = operator.step(state, law, max_births=CAP)
        assert turn.status == "extend"
        inclusive = [{i for i, group in enumerate(turn.parents) if set(group) & arm} for arm in inclusive]
        if set.intersection(*inclusive):
            return True
        state = turn.end
    return False


def anonymous_counterexample(draws, law):
    """Compare weak pair readings while fixing even the entire unpointed current holding pattern."""
    _, _, nae = archive().libraries()
    for draw in draws:
        run = draw["laws"][law]
        layers = [s["births"] for s in run["transitions"] if s["births"]]
        for age, snapshot in enumerate(run["frames"][:max(0, len(layers) - 1)]):
            frames = run["frames"][age:age + 3]
            geometries = [witness_features(f) for f in frames]
            _, witnesses, distances, local = geometries[0]
            directly_shared = set(snapshot["direct_meetings"])
            by_counts = defaultdict(dict)
            for pair in combinations(local, 2):
                if witnesses[pair] or pair in directly_shared:
                    continue
                summary = pure_and_ancestry(layers[age:age + 2], geometries, *pair)
                observed = any(z["both_ancestries"] for z in summary)
                key = tuple(sorted(snapshot["loose"][v] for v in pair))
                by_counts[key].setdefault(observed, pair)
            chosen = next(((key, row) for key, row in by_counts.items() if len(row) > 1), None)
            if chosen is None:
                continue
            key, pair_by_outcome = chosen
            with_marks = nx.is_isomorphic(witnessed_graph(snapshot, pair_by_outcome[False]),
                                          witnessed_graph(snapshot, pair_by_outcome[True]), node_match=lambda x, y: x == y)
            assert not with_marks
            stars = draw["source_stars"] + [b["inputs"] + b["introduced"] for s in layers[:age] for b in s]
            top_d, top_holder = max(d for support in stars for d in support), len(stars) - 1
            renamed = [sorted(top_d - d for d in support) for support in reversed(stars)]
            _, recoded = frame(nae.S.from_junctions(renamed), None)
            answers = []
            for observed, pair in sorted(pair_by_outcome.items()):
                assert end_forecast_two(snapshot, pair, law) == observed
                recoded_pair = tuple(sorted(top_holder - v for v in pair))
                assert nx.is_isomorphic(witnessed_graph(snapshot, pair), witnessed_graph(recoded, recoded_pair),
                                        node_match=lambda x, y: x == y)
                assert end_forecast_two(recoded, recoded_pair, law) == observed
                answers.append({"marked_pair": pair, "candidate_step_distance": distances[pair[0]].get(pair[1]),
                                "common_ancestry_by_two": observed})
            return {"draw": draw["draw"], "age": age, "loose_by_marked_holder": key, "common_witnesses": 0,
                    "directly_shared_distinctions": 0, "same_anonymous_unpointed_end": True,
                    "same_anonymous_pointed_end": with_marks, "joint_renaming_verified": True,
                    "actual_and_witnessed_forecast": answers}
    return None


def score_source(spec):
    prior, _, nae = archive().libraries()
    stars = nae.J.stars_from(spec["arities"], spec["meetings"])
    lawful = prior.source_lawfulness(nae.S.from_junctions(stars))
    runs = {law: actual_history(stars, law, lawful[law]["lawful"]) for law in LAWS}
    for run in runs.values():
        run["pair_panels"] = pair_panel(run)
        run["singleton_releases"] = singleton_releases(run)
    return {**spec, "source_stars": stars, "lawfulness": lawful, "laws": runs}


def panel_summary(draws, law):
    histories = [draw["laws"][law] for draw in draws]
    ages = {}
    for age in range(LAYERS + 1):
        snapshots = [h["frames"][age] for h in histories if len(h["frames"]) > age]
        plans = [h["transitions"][age] for h in histories if len(h["transitions"]) > age]
        panels = [h["pair_panels"][age] for h in histories if len(h["pair_panels"]) > age]
        shapes, first_mix, first_mediation, followups, families = defaultdict(Counter), Counter(), Counter(), Counter(), defaultdict(Counter)
        for panel in panels:
            first_mix.update(panel["delays_common_ancestry"])
            first_mediation.update(panel["delays_mediated"])
            followups[panel["observed_steps_after_frame"]] += panel["pair_families"].get("all", {}).get("opportunities", 0)
            for family, counts in panel["pair_families"].items():
                families[family].update(counts)
            for sig, counts in panel["witness_count_profiles"].items():
                shapes[sig].update(counts)
        colliding = {sig: outcomes for sig, outcomes in shapes.items() if len(outcomes) > 1}
        all_births = [b for s in plans for b in s["births"]]
        releases = [group for h in histories for group in h["singleton_releases"]["release_groups"] if group["age"] == age]
        ages[age] = {"reached_frames": len(snapshots), "max_live": max((len(v["loose"]) for v in snapshots), default=0),
                     "attempt_statuses": dict(Counter(p["ordinary_plan"]["status"] for p in plans)),
                     "funded_materialized_steps": sum(bool(p["births"]) for p in plans),
                     "actual_born": len(all_births), "zero_fresh": sum(not b["fresh"] for b in all_births),
                     "same_type_unary_release_groups": len(releases),
                     "same_type_unary_release_pairs": sum(r["unordered_sibling_pairs"] for r in releases),
                     "unfunded_proposed_multis": sum(len(p.get("unfunded_multi_parent_proposals", ())) for p in plans),
                     "families": {k: dict(v) for k, v in families.items()}, "opportunities_by_followup_depth": dict(followups),
                     "first_common_ancestry_delays": dict(first_mix), "first_mediated_delays": dict(first_mediation),
                     "anonymous_profiles": {"observed_profiles": len(shapes), "ambiguous_profiles": len(colliding),
                                            "episodes_with_ambiguous_profiles": sum(c.total() for c in colliding.values()),
                                            "minimum_pooled_lookup_errors": sum(min(c.values()) for c in colliding.values()),
                                            "total_episodes": sum(v.total() for v in shapes.values()),
                                            "examples": dict(list(sorted(colliding.items()))[:3])}}
    return {"draws": len(draws), "lawful": sum(d["lawfulness"][law]["lawful"] for d in draws),
            "status_at_stopping": dict(Counter(h["status"] for h in histories)),
            "funded_at_source": sum(bool(h["transitions"]) and bool(h["transitions"][0]["births"]) for h in histories),
            "histories_with_same_type_unary_release_at_multiple_ages": sum(bool(h["singleton_releases"]["same_type_released_at_multiple_ages"]) for h in histories),
            "by_anchor_age": ages}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Disposable replay of leading draws")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use a scratch output with --limit")
    draws = []
    for i, spec in enumerate(source_draws()):
        if args.limit is not None and i >= args.limit:
            break
        draws.append(score_source(spec))
    groups = {k: [d for d in draws if d["weighting"] == k] for k in SEEDS}
    aggregate = {law: panel_summary(draws, law) for law in LAWS}
    record = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "sources_per_size_and_weighting": PER_SIZE,
              "max_layers": LAYERS, "live_birth_cap": CAP, "seeds": SEEDS, "draws": draws,
              "individual_pair_family_counts_omit_zeros": True,
              "anonymous_control": {law: anonymous_counterexample(draws, law) for law in LAWS},
              "summary": {"all": aggregate,
                          "by_weighting": {k: {law: panel_summary(v, law) for law in LAWS} for k, v in groups.items()},
                          "by_weighting_and_size": {k: {n: {law: dict(Counter(d["laws"][law]["status"] for d in v if d["source_knots"] == n))
                                                           for law in LAWS} for n in range(4, 9)} for k, v in groups.items()}}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as stream:
        json.dump(record, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")


if __name__ == "__main__":
    main()
