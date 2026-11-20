"""Sample literal ordinary partial cohorts and enumerate bounded competing origins."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache, lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import random

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample_origins.json"
DESIGN = ROOT / "research/READ-ORIGIN-20261120-001/preregistration.md"
SEEDS = {"tree": 20261120601, "unicyclic": 20261120602, "prefix": 20261120603, "mark": 20261120604}
PER_SIZE = 64
MAX_REVERSE_KNOTS = 9
LAWS = ("parity", "nae")


@cache
def archive():
    path = ROOT / ("experiments/FRESH-DEMAND-20261120-001A/"
                   "FRESH-DEMAND-20261120-001A-E001_orders/sample_starts.py")
    spec = spec_from_file_location("read_origin_source_archive", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_draws():
    for kind in ("tree", "unicyclic"):
        rng = random.Random(SEEDS[kind])
        for n in range(4, 9):
            for i in range(PER_SIZE):
                word = [rng.randrange(n) for _ in range(n - 2)]
                holder_graph = nx.from_prufer_sequence(word)
                extra_meeting = None
                if kind == "unicyclic":
                    possible = [g for g in combinations(range(n), 2) if not holder_graph.has_edge(*g)]
                    extra_meeting = rng.choice(possible)
                    holder_graph.add_edge(*extra_meeting)
                meetings = sorted(tuple(sorted(g)) for g in holder_graph.edges)
                spare = [int(rng.randrange(4) == 0) for _ in range(n)]
                arities = [max(3, holder_graph.degree(v)) + spare[v] for v in range(n)]
                yield {"draw": f"{kind}/{n}/{i:02d}", "weighting": kind, "source_knots": n, "prufer": word,
                       "extra_meeting": extra_meeting, "spare": spare, "meetings": meetings, "arities": arities}


@lru_cache(maxsize=4096)
def lawful(stars):
    nae, _, _ = archive().libraries()
    return archive().source_lawfulness(nae.S.from_junctions(stars))


def make_presentation(stars):
    nae, _, _ = archive().libraries()
    return nae.S.from_junctions(stars)


def frozen_stars(p):
    return tuple(map(tuple, p.bits_of))


def exact_nae_inputs(solver, inputs):
    count = 1 << len(inputs)
    return [word for word in range(count)
            if solver.solve(assumptions=[d + 1 if word >> i & 1 else -(d + 1) for i, d in enumerate(inputs)])]


def complete_step(p, law):
    """Advance the actual ordinary implementation, retaining its immediate receipts."""
    nae, _, _ = archive().libraries()
    n = len(p.bits_of)
    live = [j for j in p.live if p.loose(j)]
    groups = tuple(tuple(sorted(g)) for g in p.groups_among(live))
    use = Counter(v for g in groups for v in g)
    shortage = {v: use[v] - len(p.loose(v)) for v in live if use[v] > len(p.loose(v))}
    stamp = {"proposed_multi": groups, "shortages": shortage, "births": []}
    rule = nae.parity_rule(nae.F.fewest) if law == "parity" else nae.nae_rule(nae.F.fewest)
    # The wrapper applies the underlying law first, then records the literal old-input projection.
    birth_checks = []

    def record(pres, info, argument):
        counts = rule(pres, info, argument)
        solver = nae._solver(pres, n) if law == "nae" else None
        try:
            for item, count in zip(info, counts, strict=True):
                inputs = tuple(pres.bits_of[item["j"]][:item["p"]])
                parents = tuple(next(v for v in pres.owner[d] if v < n) for d in inputs)
                arity = len(inputs) + count
                if law == "nae":
                    allowed = exact_nae_inputs(solver, inputs)
                    implied = 0 not in allowed and (1 << len(inputs)) - 1 not in allowed
                    allowed_count = len(allowed)
                    assert implied == item["implied"]
                    expected = (1 << len(inputs)) - (0 if count else 2)
                else:
                    allowed_count = (1 << len(inputs)) >> item["implied"]
                    expected = (1 << len(inputs)) >> (not count)
                birth_checks.append({"parents": parents, "inputs": inputs, "fresh": count, "demand": item["d"],
                                     "implied": item["implied"], "input_states": allowed_count,
                                     "knot": arity >= 3 and allowed_count == expected})
        finally:
            if solver is not None:
                solver.delete()
        return counts

    result = p.step(record)
    if result is None:
        assert shortage
        return {**stamp, "status": "stall"}
    if result["new"] == 0:
        assert not live
        return {**stamp, "status": "closed"}
    assert not shortage and result["new"] == len(birth_checks) == len(p.bits_of) - n
    if not all(b["knot"] for b in birth_checks):
        return {**stamp, "status": "non_knot_stop", "rejected_births": [b for b in birth_checks if not b["knot"]]}
    for i, record in enumerate(birth_checks, n):
        record["star"] = tuple(p.bits_of[i])
    return {**stamp, "status": "formed", "births": birth_checks}


def forecast(stars, law, *, live=None):
    p = make_presentation(stars)
    if live is not None:
        p.live = list(live)
    return complete_step(p, law)


def menu(births):
    return Counter((b["parents"], b["fresh"]) for b in births)


def menu_key(counts):
    return tuple((g, f, n) for (g, f), n in sorted(counts.items()) if n > 0)


def parents_only(counts):
    result = Counter()
    for (g, _), value in counts.items():
        result[g] += value
    return result


def target_values(counts, target):
    return tuple((f, n) for (g, f), n in sorted(counts.items()) if g == target and n > 0)


def compare_menus(reference, alternative, target):
    true_menu, restart_menu = menu(reference["births"]), menu(alternative["births"])
    true_parents, restart_parents = parents_only(true_menu), parents_only(restart_menu)
    overlap = (true_parents & restart_parents).total()
    same = (true_menu & restart_menu).total()
    return {"true_status": reference["status"], "restart_status": alternative["status"],
            "same_menu_and_status": reference["status"] == alternative["status"] and true_menu == restart_menu,
            "same_parent_multiplicities": true_parents == restart_parents,
            "true_births": true_menu.total(), "restart_births": restart_menu.total(),
            "common_events": overlap, "common_events_with_different_fresh": overlap - same,
            "true_only_events": (true_parents - restart_parents).total(),
            "restart_only_events": (restart_parents - true_parents).total(),
            "true_mark": target_values(true_menu, target), "restart_mark": target_values(restart_menu, target)}


def holder_view(stars):
    p = make_presentation(stars)
    g = nx.Graph()
    g.add_nodes_from((v, {"loose": len(p.loose(v))}) for v in range(len(stars)))
    meetings = Counter(tuple(sorted(vs)) for vs in p.owner.values() if len(vs) == 2)
    g.add_edges_from((v, w, {"distinctions": count}) for (v, w), count in meetings.items())
    return p, g


def intrinsic_profiles(p, actual):
    profiles = [(len(star), len(p.nbr[v]), len(p.loose(v))) for v, star in enumerate(p.bits_of)]
    guesses = {
        "spent": {v for v, (_, _, l) in enumerate(profiles) if l == 0},
        "spent_or_degree_above_two": {v for v, (_, d, l) in enumerate(profiles) if l == 0 or d > 2},
        "arity_above_three": {v for v, (a, _, _) in enumerate(profiles) if a > 3},
    }
    existing = {profiles[v] for v in actual}
    newborn = {profiles[v] for v in range(len(profiles)) if v not in actual}
    return {"profiles": profiles, "same_profile_opposite_membership": sorted(existing & newborn),
            "guesses": {k: {"guessed_originals": sorted(g), "false_positive": len(g - actual),
                             "false_negative": len(actual - g)} for k, g in guesses.items()}}


def add_orbit(view, key, value, bases, classes):
    for representative, k in bases[key]:
        matcher = nx.algorithms.isomorphism.GraphMatcher(view, representative, node_match=lambda a, b: a == b,
                                                        edge_match=lambda a, b: a == b)
        if matcher.is_isomorphic():
            f = matcher.mapping
            assert len(f) == len(set(f.values())) == len(view) == len(representative)
            assert all(view.nodes[v] == representative.nodes[f[v]] for v in view)
            assert all({f[w]: attrs for w, attrs in view[v].items()} == dict(representative[f[v]]) for v in view)
            classes[k].append(value)
            return
    bases[key].append((view, len(classes)))
    classes.append([value])


def origin_orbits(graph, alternatives, target=()):
    """Exact quotient under holder automorphisms lifting to literal distinctions."""
    bases = defaultdict(list)
    classes = []
    anchors = set(target)
    for option in alternatives:
        members = set(option["originals"])
        view = graph.copy()
        for v, row in view.nodes(data=True):
            row["member"] = v in members
            row["anchor"] = v in anchors
        cache_key = (len(members), tuple(sorted((view.nodes[v]["loose"], view.degree(v), v in anchors)
                                                 for v in members)))
        add_orbit(view, cache_key, option["originals"], bases, classes)
    return classes


def response_orbits(graph, responses, target=()):
    bases = defaultdict(list)
    classes = []
    anchors = set(target)
    for status, events in sorted(responses):
        view = graph.copy()
        for v, row in view.nodes(data=True):
            row["anchor"] = v in anchors
        for i, (parents, fresh, count) in enumerate(events):
            address = ("event", i)
            view.add_node(address, fresh=fresh, multiplicity=count)
            view.add_edges_from((address, p, {"parent": True}) for p in parents)
        cache_key = (status, tuple(sorted((len(g), f, k) for g, f, k in events)))
        add_orbit(view, cache_key, (status, events), bases, classes)
    return classes


def forward_membership(stars, p, originals, law, restart):
    """The exact birth menu assuming the supplied holder subset is the origin."""
    n = len(stars)
    included = set(originals)
    newer = set(range(n)) - included
    if not newer:
        return {"origin_status": "fresh_source", "menu_status": restart["status"],
                "events": menu_key(menu(restart["births"]))}
    if any(not p.nbr[v] or p.nbr[v] & newer for v in newer):
        return None
    if any(sum(len(p.owner[d]) == 2 for d in stars[v]) != len(p.nbr[v]) for v in newer):
        return None
    if not archive().connected(included, p.nbr):
        return None
    origin = tuple(stars[v] for v in originals)
    plan = forecast(origin, law)
    if plan["status"] != "formed":
        return None
    full = Counter((tuple(originals[v] for v in b["parents"]), b["fresh"]) for b in plan["births"])
    physical = Counter((tuple(sorted(p.nbr[v])), len(p.loose(v))) for v in newer)
    if physical - full:
        return None
    remaining = full - physical
    if not remaining:
        # All old loose distinctions have been spent. This is a true complete boundary.
        assert all(not p.loose(v) for v in originals)
        return {"origin_status": "complete_boundary", "menu_status": restart["status"],
                "events": menu_key(menu(restart["births"]))}
    return {"origin_status": "unfinished", "menu_status": "formed", "events": menu_key(remaining)}


def mark_result(events, target):
    return tuple(f for g, f, _ in events if g == target)


def exact_origins(stars, law, actual, target, truth, restart, snapshot_lawful):
    n = len(stars)
    if n > MAX_REVERSE_KNOTS:
        return {"status": "over_bound", "written_knots": n}
    if not snapshot_lawful:
        # The entire stage carries the exact intended projection at every written holder.
        # Deleting whole knot constraints preserves this full projection on each retained row.
        return {"status": "lawfulness_failed", "written_knots": n}
    p, g = holder_view(stars)
    alternatives = []
    for size in range(1, n + 1):
        for originals in combinations(range(n), size):
            choice = forward_membership(stars, p, originals, law, restart)
            if choice is not None:
                alternatives.append({"originals": originals, **choice,
                                     "target_fresh_options": mark_result(choice["events"], target)})
    recovery = next(a for a in alternatives if set(a["originals"]) == actual)
    assert (recovery["menu_status"], recovery["events"]) == (truth["status"], menu_key(menu(truth["births"])))
    responses = {(a["menu_status"], a["events"]) for a in alternatives}
    selected_answers = {a["target_fresh_options"] for a in alternatives}
    assert len(alternatives) >= len(responses) >= len(selected_answers) >= 1
    common_witnesses = set.intersection(*(p.nbr[v] for v in target)) if target else set()
    tagged = set(target) | common_witnesses
    filters = {"one_known_original": {min(target)} if target else {min(actual)},
               "marked_parents": set(target), "marked_parents_and_common_holders": tagged,
               "all_original_membership": set(range(n))}
    marks = {}
    for name, flags in filters.items():
        consistent = [a for a in alternatives if set(a["originals"]) & flags == actual & flags]
        retained_menus = {(a["menu_status"], a["events"]) for a in consistent}
        retained_marks = {a["target_fresh_options"] for a in consistent}
        marks[name] = {"queried_holders": sorted(flags), "literal_origins": len(consistent),
                       "next_menus": len(retained_menus), "mark_responses": len(retained_marks)}
    assert marks["all_original_membership"]["literal_origins"] == 1
    disclosed = {}
    for given, compatible in (
        ("phase", [a for a in alternatives if a["origin_status"] == recovery["origin_status"]]),
        ("phase_and_source_size", [a for a in alternatives if a["origin_status"] == recovery["origin_status"]
                                  and len(a["originals"]) == len(actual)]),
    ):
        menus = {(a["menu_status"], a["events"]) for a in compatible}
        targets = {a["target_fresh_options"] for a in compatible}
        disclosed[given] = {"literal_origins": len(compatible), "next_menus": len(menus), "mark_responses": len(targets)}
    unpointed_menus = response_orbits(g, responses)
    pointed_menus = response_orbits(g, responses, target)
    return {"status": "exact_zero_or_one_layer", "written_knots": n, "examined_subsets": (1 << n) - 1,
            "alternatives": alternatives, "by_initial_size": dict(Counter(len(a["originals"]) for a in alternatives)),
            "by_phase": dict(Counter(a["origin_status"] for a in alternatives)),
            "origin_classes_unpointed": origin_orbits(g, alternatives),
            "origin_classes_preserving_mark": origin_orbits(g, alternatives, target),
            "next_menus": len(responses), "next_menus_unpointed_orbits": len(unpointed_menus),
            "next_menus_mark_preserving_orbits": len(pointed_menus), "target_responses": len(selected_answers),
            "next_menu_bits": (len(responses) - 1).bit_length(),
            "target_bits": (len(selected_answers) - 1).bit_length(), "membership_marks": marks,
            "disclosed_phase_controls": disclosed}


def completed_interpretations(source, first, carry, order, law):
    original_count = len(source)
    current = source + tuple(first["births"][i]["star"] for i in order)
    map_to_current = {i: i for i in range(original_count)}
    map_to_current.update({original_count + k: original_count + i for i, k in enumerate(order)})
    known_loose_owners = [v for v in range(len(carry.bits_of)) if carry.loose(v)]
    assert carry.live == known_loose_owners
    next_carried = complete_step(carry, law)
    next_carried = {**next_carried,
                    "births": [{**b, "parents": tuple(sorted(map_to_current[v] for v in b["parents"]))}
                               for b in next_carried["births"]]}
    restart = forecast(current, law)
    comparison = compare_menus(next_carried, restart, ())
    assert comparison["same_menu_and_status"]
    return current, next_carried, restart, comparison


def literal_restart_mark(p, restart, chosen):
    """Move a restart allocation onto the same marked physical loose inputs."""
    candidate = next((b for b in restart["births"] if b["parents"] == chosen["parents"]), None)
    if candidate is None:
        return None
    perm = {}
    for v, a, b in zip(chosen["parents"], candidate["inputs"], chosen["inputs"], strict=True):
        assert p.owner[a] == p.owner[b] == [v]
        perm.update({a: b, b: a})
    assert all({perm.get(d, d) for d in support} == set(support) for support in p.bits_of)
    spends = [perm.get(d, d) for event in restart["births"] for d in event["inputs"]]
    assert len(spends) == len(set(spends))
    assert tuple(perm[d] for d in candidate["inputs"]) == chosen["inputs"]
    return {"fresh": candidate["fresh"], "inputs": chosen["inputs"],
            "exchanged_loose_distinctions": sorted((a, b) for a, b in perm.items() if a < b)}


def score_source(spec, prefix_rng, mark_rng):
    nae, _, _ = archive().libraries()
    source = tuple(map(tuple, nae.J.stars_from(spec["arities"], spec["meetings"])))
    source_n = len(source)
    actual = set(range(source_n))
    lawfulness = lawful(source)
    ps, ms = prefix_rng.getrandbits(64), mark_rng.getrandbits(64)
    results = {}
    for law in LAWS:
        if not lawfulness[law]["lawful"]:
            results[law] = {"source_status": "unlawful"}
            continue
        carry = make_presentation(source)
        first = complete_step(carry, law)
        result = {"source_status": first["status"], "first_complete": first}
        results[law] = result
        if first["status"] != "formed":
            continue
        roster = first["births"]
        order = list(range(len(roster)))
        rng = random.Random(ps)
        rng.shuffle(order)
        current, next_carried, restart, comparison = completed_interpretations(source, first, carry, order, law)
        law_at_boundary = lawful(current)[law]["lawful"]
        assert law_at_boundary
        result.update(shuffle=order, complete_boundary={"stars": current, "lawful": law_at_boundary,
                      "comparison": comparison, "next_menus": menu_key(menu(restart["births"])),
                      "origin_census": exact_origins(current, law, actual, (), next_carried, restart, law_at_boundary)})
        if len(roster) < 2:
            continue
        cut = rng.randrange(1, len(roster))
        middle = current[:source_n + cut]
        pending = [roster[i] for i in order[cut:]]
        chosen = random.Random(ms).choice(pending)
        target = chosen["parents"]
        old_pending = {"status": "formed", "births": pending}
        law_at_middle = lawful(middle)[law]["lawful"]
        assert law_at_middle
        fresh_source = forecast(middle, law)
        p = make_presentation(middle)
        assert all(d in p.loose(v) for v, d in zip(target, chosen["inputs"], strict=True))
        record = {"proper_prefix_length": cut, "stars": middle, "lawful": law_at_middle,
                  "target_parents": target, "target_inputs": chosen["inputs"], "target_fresh": chosen["fresh"],
                  "remaining": menu_key(menu(pending)), "restart": fresh_source,
                  "comparison": compare_menus(old_pending, fresh_source, target), "intrinsic_profiles": intrinsic_profiles(p, actual),
                  "restart_on_same_target_inputs": literal_restart_mark(p, fresh_source, chosen),
                  "origin_census": exact_origins(middle, law, actual, target, old_pending, fresh_source, law_at_middle)}
        # All parents of all pending births must still hold their own unspent literal inputs.
        assert all(d in p.loose(v) for b in pending for v, d in zip(b["parents"], b["inputs"], strict=True))
        result["proper_middle"] = record
    return {**spec, "source_stars": source, "source_lawfulness": lawfulness,
            "prefix_seed": ps, "mark_seed": ms, "by_law": results}


def summarize_census(phase):
    states = [v["origin_census"] for v in phase]
    result = {"statuses": dict(Counter(c["status"] for c in states)), "by_written_knots": {}}
    for n in sorted({c["written_knots"] for c in states if c["status"] == "exact_zero_or_one_layer"}):
        samples = [c for c in states if c["status"] == "exact_zero_or_one_layer" and c["written_knots"] == n]
        marked = defaultdict(Counter)
        for c in samples:
            for name, mark in c["membership_marks"].items():
                marked[name]["unique_origin"] += mark["literal_origins"] == 1
                marked[name]["unique_next_menu"] += mark["next_menus"] == 1
                marked[name]["unique_marked_query"] += mark["mark_responses"] == 1
        result["by_written_knots"][n] = {
            "snapshots": len(samples), "literal_subsets_examined": sum(c["examined_subsets"] for c in samples),
            "compatible_subsets": sum(len(c["alternatives"]) for c in samples),
            "max_compatible_subsets": max(len(c["alternatives"]) for c in samples),
            "max_unpointed_orbits": max(len(c["origin_classes_unpointed"]) for c in samples),
            "max_mark_preserving_orbits": max(len(c["origin_classes_preserving_mark"]) for c in samples),
            "max_distinct_literal_next_menus": max(c["next_menus"] for c in samples),
            "max_unpointed_next_menu_orbits": max(c["next_menus_unpointed_orbits"] for c in samples),
            "max_mark_preserving_next_menu_orbits": max(c["next_menus_mark_preserving_orbits"] for c in samples),
            "max_target_responses": max(c["target_responses"] for c in samples),
            "highest_next_menu_bits": max(c["next_menu_bits"] for c in samples),
            "highest_target_bits": max(c["target_bits"] for c in samples),
            "literal_origin_ambiguous": sum(len(c["alternatives"]) > 1 for c in samples),
            "origin_ambiguous_up_to_symmetry": sum(len(c["origin_classes_unpointed"]) > 1 for c in samples),
            "different_next_menus": sum(c["next_menus"] > 1 for c in samples),
            "different_target_responses": sum(c["target_responses"] > 1 for c in samples),
            "partial_marks": {k: dict(v) for k, v in marked.items()},
            "disclosed_phase_controls": {kind: {"different_next_menus": sum(c["disclosed_phase_controls"][kind]["next_menus"] > 1 for c in samples),
                                                 "different_marked_responses": sum(c["disclosed_phase_controls"][kind]["mark_responses"] > 1 for c in samples),
                                                 "max_next_menus": max(c["disclosed_phase_controls"][kind]["next_menus"] for c in samples)}
                                        for kind in ("phase", "phase_and_source_size")},
        }
    return result


def summarize(draws, law):
    rows = [d["by_law"][law] for d in draws]
    mid = [d["proper_middle"] for d in rows if "proper_middle" in d]
    complete = [d["complete_boundary"] for d in rows if "complete_boundary" in d]
    totals = Counter()
    marks = Counter()
    by_arity = defaultdict(Counter)
    surrogates = defaultdict(Counter)
    for v in mid:
        result = v["comparison"]
        for key in ("same_menu_and_status", "same_parent_multiplicities", "true_births", "restart_births",
                    "common_events", "common_events_with_different_fresh", "true_only_events", "restart_only_events"):
            totals[key] += result[key]
        totals["snapshots_with_common_events"] += result["common_events"] > 0
        totals["snapshots_with_changed_common_fresh"] += result["common_events_with_different_fresh"] > 0
        if not result["restart_mark"]:
            outcome = "restart_" + ("missing_group" if result["restart_status"] == "formed" else result["restart_status"])
        elif v["target_fresh"] in {f for f, _ in result["restart_mark"]}:
            outcome = "same_fresh"
        else:
            outcome = "different_fresh"
        marks[outcome] += 1
        by_arity[len(v["target_parents"])][outcome] += 1
        for name, guess in v["intrinsic_profiles"]["guesses"].items():
            surrogates[name]["all_literal_memberships_correct"] += not (guess["false_positive"] or guess["false_negative"])
            surrogates[name]["false_positive"] += guess["false_positive"]
            surrogates[name]["false_negative"] += guess["false_negative"]
    return {"draws": len(draws), "first_source_statuses": dict(Counter(d["source_status"] for d in rows)),
            "sampled_middle": len(mid), "written_holder_occurrences_at_middle": sum(len(s["stars"]) for s in mid),
            "restart_at_middle_statuses": dict(Counter(d["restart"]["status"] for d in mid)),
            "middle_totals": dict(totals), "middle_mark_outcomes": dict(marks),
            "middle_mark_outcomes_by_parent_count": {k: dict(v) for k, v in by_arity.items()},
            "middle_membership_surrogates": {k: dict(v) for k, v in surrogates.items()},
            "middle_same_profile_opposite_membership": sum(bool(d["intrinsic_profiles"]["same_profile_opposite_membership"]) for d in mid),
            "middle_census": summarize_census(mid), "complete_boundary_checks": len(complete),
            "complete_boundary_next_status": dict(Counter(d["comparison"]["restart_status"] for d in complete)),
            "complete_boundary_exact_agreement": sum(d["comparison"]["same_menu_and_status"] for d in complete),
            "complete_boundary_census": summarize_census(complete)}


def check_renamings(draws):
    verified = []
    for weighting in ("tree", "unicyclic"):
        for law in LAWS:
            for d in draws:
                mid = d["by_law"][law].get("proper_middle")
                if d["weighting"] == weighting and mid and mid["origin_census"]["status"] == "exact_zero_or_one_layer":
                    break
            else:
                continue
            stars = mid["stars"]
            holder_hi = len(stars) - 1
            distinction_hi = max(d for star in stars for d in star)
            renamed = tuple(tuple(sorted(distinction_hi - d for d in star)) for star in reversed(stars))

            def rename(group):
                return tuple(sorted(holder_hi - v for v in group))

            pending = [{"parents": rename(g), "fresh": f} for g, f, k in mid["remaining"] for _ in range(k)]
            restart = forecast(renamed, law)
            recovered = exact_origins(renamed, law, set(rename(range(d["source_knots"]))), rename(mid["target_parents"]),
                                      {"status": "formed", "births": pending}, restart, lawful(renamed)[law]["lawful"])
            original = mid["origin_census"]
            expected = {(rename(a["originals"]), a["origin_status"], a["menu_status"],
                         tuple(sorted((rename(g), f, k) for g, f, k in a["events"]))) for a in original["alternatives"]}
            seen = {(a["originals"], a["origin_status"], a["menu_status"], a["events"]) for a in recovered["alternatives"]}
            assert expected == seen
            assert original["next_menus_mark_preserving_orbits"] == recovered["next_menus_mark_preserving_orbits"]
            assert original["target_responses"] == recovered["target_responses"]
            verified.append({"draw": d["draw"], "law": law, "literal_subsets": len(expected)})
    return verified


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Disposable replay of the first draws")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use a scratch output with --limit")
    prefix_rng = random.Random(SEEDS["prefix"])
    mark_rng = random.Random(SEEDS["mark"])
    trials = []
    for i, spec in enumerate(source_draws()):
        if args.limit is not None and i >= args.limit:
            break
        trials.append(score_source(spec, prefix_rng, mark_rng))
    grouped = {kind: [d for d in trials if d["weighting"] == kind] for kind in ("tree", "unicyclic")}
    result = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "seeds": SEEDS,
              "draws_per_size": PER_SIZE, "max_reverse_knots": MAX_REVERSE_KNOTS, "draws": trials,
              "renaming_checks": check_renamings(trials),
              "summary": {"overall": {law: summarize(trials, law) for law in LAWS},
                          "by_weighting": {kind: {law: summarize(group, law) for law in LAWS}
                                           for kind, group in grouped.items()},
                          "source_status_by_size": {kind: {n: {law: dict(Counter(d["by_law"][law]["source_status"]
                                                    for d in group if d["source_knots"] == n)) for law in LAWS}
                                                    for n in range(4, 9)} for kind, group in grouped.items()}}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as receipt:
        json.dump(result, receipt, sort_keys=True, separators=(",", ":"))
        receipt.write("\n")


if __name__ == "__main__":
    main()
