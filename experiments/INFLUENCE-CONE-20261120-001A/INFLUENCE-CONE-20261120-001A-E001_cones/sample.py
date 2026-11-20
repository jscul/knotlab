"""Matched ordinary growth with one extra loose distinction at a live source holder."""

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
DESIGN = ROOT / "research/INFLUENCE-CONE-20261120-001/preregistration.md"
SEEDS = {"tree": 20261120851, "augmented_tree": 20261120852}
SENDER_SEED = 20261120853
LAWS = ("parity", "nae")
PER_SIZE = 32
LAYERS = 3
CAP = 96


@cache
def archived():
    source = ROOT / ("experiments/GENERATORS-20261120-001A/"
                     "GENERATORS-20261120-001A-E001_generators/sample.py")
    spec = spec_from_file_location("influence_generators_archive", source)
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
                sizes = [max(3, graph.degree(v)) + spare[v] for v in range(n)]
                yield {"draw": f"{name}/{n}/{i:02d}", "weighting": name, "source_knots": n,
                       "prufer": word, "added_meeting": added, "spares": spare,
                       "meetings": meetings, "arities": sizes}


def distances(v, neighbors):
    steps = {v: 0}
    route = [v]
    for u in route:
        for w in neighbors[u] - steps.keys():
            route.append(w)
            steps[w] = steps[u] + 1
    return steps


def source_geometry(p, sender):
    _, ordinary, _ = archived().libraries()
    end = ordinary.from_stars(p.bits_of)
    witnessed = ordinary.neighbors(end)
    exact_two = {u: set() for u in end.opens}
    groups = ordinary.proposals(end)
    for group in groups:
        if len(group) == 2:
            u, v = group
            exact_two[u].add(v)
            exact_two[v].add(u)
    dist_ordinary = distances(sender, p.nbr)
    dist_witnessed = distances(sender, witnessed)
    dist_two = distances(sender, exact_two)
    by_receiver = {r: {"live": r in end.opens, "ordinary_holder_steps": dist_ordinary[r],
                       "witnessed_steps": dist_witnessed.get(r), "exact_two_parent_steps": dist_two.get(r),
                       "common_witness_count": len(p.nbr[r] & p.nbr[sender]) if r in end.opens else None}
                   for r in range(len(p.bits_of)) if r != sender}
    return end, groups, by_receiver


def history(stars, law, lawful):
    if not lawful:
        return {"terminal": "unlawful", "stages": [], "steps": []}
    library = archived()
    _, operator, nae = library.libraries()
    p = nae.S.from_junctions(stars)
    end = operator.from_stars(stars)
    stages = [{"age": 0, "live": end.opens, "written_knots": len(stars), "written_distinctions": len(p.owner)}]
    steps = []
    terminal = "age_limit"
    for age in range(LAYERS):
        assert len(end.opens) <= CAP
        plan = operator.step(end, law, max_births=CAP)
        row = {"age": age + 1, "plan": library.plan_receipt(plan), "births": []}
        steps.append(row)
        if plan.status in ("cap", "closed"):
            terminal = "birth_cap" if plan.status == "cap" else "closed"
            break
        births = library.literal_step(p, law, plan)
        if plan.status == "stall":
            terminal = "stall"
            row["unfunded_multi_parent_proposals"] = operator.proposals(end)
            break
        if any(len(b["parents"]) + b["fresh"] < 3 for b in births):
            assert law == "parity" and len(births) == 1 and plan.implied
            row["rejected_subarity_birth"] = births[0]
            terminal = "legacy_subarity_stop"
            break
        row["births"] = births
        end = operator.from_stars(p.bits_of)
        library.verify_following(plan, births, end)
        stages.append({"age": age + 1, "live": end.opens, "written_knots": len(p.bits_of),
                       "written_distinctions": len(p.owner)})
        if not end.opens:
            terminal = "closed"
            break
    return {"terminal": terminal, "stages": stages, "steps": steps}


def cohort(arm, age):
    """Distinguish a formed terminal birth, a known absent cohort and resource censoring."""
    if not arm["stages"]:
        return "unlawful", ()
    if len(arm["stages"]) > age:
        return ("positive" if arm["stages"][age]["live"] else "closing"), arm["steps"][age - 1]["births"]
    return arm["terminal"], ()


def index_history(stars, arm, added):
    n = len(stars)
    terms = {r: (0, r) for r in range(n)}
    ancestors = {r: 1 << r for r in range(n)}
    supports = {r: tuple(support) for r, support in enumerate(stars)}
    ages = dict.fromkeys(range(n), 0)
    release = None
    for step in arm["steps"]:
        for birth in step["births"]:
            v = birth["knot"]
            terms[v] = (1, tuple(sorted(terms[p] for p in birth["parents"])))
            mask = 0
            for p in birth["parents"]:
                mask |= ancestors[p]
            if step["age"] == 1 and added in birth["inputs"]:
                assert release is None
                release = {"knot": v, "parents": birth["parents"], "fresh": birth["fresh"]}
                mask |= 1 << n
            ancestors[v] = mask
            supports[v] = tuple(birth["inputs"] + birth["introduced"])
            ages[v] = step["age"]
    return {"terms": terms, "ancestors": ancestors, "supports": supports, "ages": ages, "release": release}


def incidence(supports, holder_translation):
    result = defaultdict(list)
    for old, new in holder_translation.items():
        for d in supports[old]:
            result[d].append(new)
    return {d: tuple(sorted(holders)) for d, holders in result.items()}


def verify_incidence(base_index, augmented_index, translation, initial_shared):
    old = incidence(base_index["supports"], translation)
    new = incidence(augmented_index["supports"], {v: v for v in translation.values()})
    assert all(old[d] == new[d] for d in initial_shared)
    counts = Counter(old.values())
    available = Counter(new.values())
    return not (counts - available)


def match_layers(stars, starts, indices):
    """Construct a physical inclusion if exact immediate parent groups can be matched."""
    old = Counter(d for support in stars for d in support)
    initial_shared = {d for d, multiplicity in old.items() if multiplicity == 2}
    translated = {v: v for v in range(len(stars))}
    comparisons = []
    may_continue = True
    for age in range(1, LAYERS + 1):
        left_status, left = cohort(starts["base"], age)
        right_status, right = cohort(starts["plus"], age)
        if not left or not right:
            comparisons.append({"age": age, "status": "missing_observed_birth_cohort"})
            may_continue = False
            continue
        if not may_continue:
            comparisons.append({"age": age, "status": "not_attempted_after_failed_match"})
            continue
        available = defaultdict(list)
        for b in right:
            available[b["parents"]].append(b)
        within = []
        for b in sorted(left, key=lambda row: (-row["fresh"], row["knot"])):
            wanted = tuple(sorted(translated[p] for p in b["parents"]))
            possible = [b2 for b2 in available[wanted] if b2["fresh"] >= b["fresh"]]
            if not possible:
                comparisons.append({"age": age, "status": "constructed_match_failed", "base_knot": b["knot"],
                                    "mapped_parents": wanted, "required_fresh": b["fresh"],
                                    "available_fresh": sorted(row["fresh"] for row in available[wanted])})
                may_continue = False
                break
            chosen = min(possible, key=lambda b2: (b2["fresh"], b2["knot"]))
            available[wanted].remove(chosen)
            within.append((b["knot"], chosen["knot"], b["fresh"], chosen["fresh"]))
        if may_continue:
            translated.update({a: b for a, b, _, _ in within})
            assert verify_incidence(indices["base"], indices["plus"], translated, initial_shared)
            comparisons.append({"age": age, "status": "verified_incidence_inclusion", "cohort_knot_pairs": within,
                                "extra_augmented_births": sorted(row["knot"] for remaining in available.values() for row in remaining),
                                "both_positive": left_status == right_status == "positive"})
    return comparisons


def necessary_type_inclusion(starts, indices, age):
    measured = {}
    for arm in ("base", "plus"):
        _, births = cohort(starts[arm], age)
        if not births:
            return None
        table = defaultdict(list)
        for b in births:
            table[indices[arm]["terms"][b["knot"]]].append(b["fresh"])
        measured[arm] = {term: sorted(fresh, reverse=True) for term, fresh in table.items()}
    old, new = measured["base"], measured["plus"]
    same_types_possible = all(len(fresh) <= len(new.get(term, ())) for term, fresh in old.items())
    enough_fresh_possible = same_types_possible and all(all(a <= b for a, b in zip(fresh, new[term]))
                                                        for term, fresh in old.items())
    return {"parent_multiset_types_contain_base": same_types_possible,
            "parent_types_and_fresh_capacity_contain_base": enough_fresh_possible}


def reading(index, births, age, bit, outside=False):
    ancestors = index["ancestors"]
    chosen = [b for b in births if bool(ancestors[b["knot"]] & bit) != outside]
    shapes = Counter(index["terms"][b["knot"]] for b in chosen)
    priced = Counter((index["terms"][b["knot"]], b["fresh"]) for b in chosen)
    current = [index["supports"][b["knot"]] for b in chosen]
    reached = [support for v, support in index["supports"].items()
               if index["ages"][v] <= age and bool(ancestors[v] & bit) != outside]
    numbers = {"births": len(chosen), "live_children": sum(b["fresh"] > 0 for b in chosen),
               "fresh_total": sum(b["fresh"] for b in chosen), "present_held_places": sum(map(len, current)),
               "written_family_knots": len(reached), "written_family_distinctions": len(set().union(*reached)),
               "written_family_holdings": sum(map(len, reached)),
               "fresh_histogram": dict(sorted(Counter(b["fresh"] for b in chosen).items())),
               "parent_arity_histogram": dict(sorted(Counter(len(b["parents"]) for b in chosen).items())),
               "physical_arity_histogram": dict(sorted(Counter(map(len, current)).items()))}
    return chosen, shapes, priced, numbers


def compare_outputs(starts, indices, age, mask, outside=False, exact_match=None):
    states, grounded = {}, {}
    for arm in ("base", "plus"):
        status, births = cohort(starts[arm], age)
        states[arm] = status
        grounded[arm] = reading(indices[arm], births, age, mask, outside=outside)
    records = {arm: result[3] for arm, result in grounded.items()}
    absent = {"birth_cap", "unlawful", "legacy_subarity_stop"}
    compared = all(status not in absent for status in states.values())
    a, b = grounded["base"], grounded["plus"]
    different_number = a[-1]["births"] != b[-1]["births"]
    different_shape = a[1] != b[1]
    different_prices = a[2] != b[2]
    structural_matches = (a[1] & b[1]).total()
    priced_matches = (a[2] & b[2]).total()
    exact = None
    if exact_match is not None and exact_match["status"] == "verified_incidence_inclusion":
        exact_pairs = exact_match["cohort_knot_pairs"]
        base_newborns = {child["knot"] for child in a[0]}
        plus_newborns = {child["knot"] for child in b[0]}
        together = [(u, v, old_fresh, new_fresh) for u, v, old_fresh, new_fresh in exact_pairs if u in base_newborns]
        assert all(v in plus_newborns for _, v, _, _ in together) and len(together) == len(base_newborns)
        extras = plus_newborns - {v for _, v, _, _ in together}
        exact = {"physical_matches": len(together), "fresh_count_changes": sum(f != g for _, _, f, g in together),
                 "extra_augmented_births": len(extras)}
    return {"statuses": states, "compared": compared, "arms": records,
            "different_current_birth_count": different_number if compared else None,
            "different_parent_multiset": different_shape if compared else None,
            "different_priced_parent_multiset": different_prices if compared else None,
            "matched_parent_multiset_births": structural_matches if compared else None,
            "matched_births_with_different_prices": structural_matches - priced_matches if compared else None,
            "exact_parentage_matching": exact,
            "different_held_places": (a[-1]["present_held_places"] != b[-1]["present_held_places"]) if compared else None,
            "different_written_distinctions": (a[-1]["written_family_distinctions"] != b[-1]["written_family_distinctions"]) if compared else None}


def first_joint(starts, indices, arm, first, second):
    if first is None or second is None:
        return None
    marked = first | second
    ancestry = indices[arm]["ancestors"]
    return next((step["age"] for step in starts[arm]["steps"] if any(ancestry[b["knot"]] & marked == marked for b in step["births"])), None)


def birth_examples(starts, indices, age, mask):
    by_arm = {}
    for arm in ("base", "plus"):
        _, births = cohort(starts[arm], age)
        _, shapes, priced, _ = reading(indices[arm], births, age, mask)
        by_arm[arm] = {"types": sorted(shapes.items()), "priced_types": sorted(priced.items())}
    return by_arm


def receiver_receipts(starts, indices, geometry, sender, num_roots, matches):
    scored = {}
    witnesses = {}
    releases = indices["plus"]["release"]
    for receiver, attributes in geometry.items():
        mask = 1 << receiver
        first = {arm: first_joint(starts, indices, arm, 1 << sender, mask) for arm in ("base", "plus")}
        for arm, found in first.items():
            distance = attributes["witnessed_steps"]
            if attributes["live"]:
                steps = len(starts[arm]["stages"]) - 1
                assert found == (distance if distance is not None and distance <= steps else None)
        any_anchor_joint = min((t for t in first.values() if t is not None), default=None)
        added_joint = first_joint(starts, indices, "plus", 1 << num_roots, mask) if releases is not None else None
        ages = []
        for age in range(1, LAYERS + 1):
            v = compare_outputs(starts, indices, age, mask, exact_match=matches[age - 1])
            v.update(age=age, earlier_or_current_original_joint=any_anchor_joint is not None and any_anchor_joint <= age,
                     earlier_or_current_added_input_joint=added_joint is not None and added_joint <= age)
            v["original_receiver_loose"] = {arm: start["stages"][min(age, len(start["stages"]) - 1)]["live"].get(receiver, 0)
                                            if start["stages"] and v["statuses"][arm] not in ("birth_cap", "legacy_subarity_stop")
                                            else None for arm, start in starts.items()}
            ages.append(v)
            actual_different = v["different_priced_parent_multiset"]
            if actual_different and v["statuses"] == {"base": "positive", "plus": "positive"}:
                if not v["earlier_or_current_original_joint"]:
                    witnesses.setdefault("positive_difference_before_original_joint", {"receiver": receiver, "age": age,
                        "geometry": attributes, "case": v, "types": birth_examples(starts, indices, age, mask)})
                if releases and not v["earlier_or_current_added_input_joint"]:
                    witnesses.setdefault("positive_difference_before_added_input_joint", {"receiver": receiver, "age": age,
                        "geometry": attributes, "case": v, "types": birth_examples(starts, indices, age, mask)})
        scored[receiver] = {"source": attributes, "first_original_joint": first,
                            "first_edited_distinction_joint": added_joint, "by_age": ages}
    return scored, witnesses


def score_pair(stars, edited, sender, slot):
    prior, _, nae = archived().libraries()
    lawfulness = {arm: prior.source_lawfulness(nae.S.from_junctions(source))
                  for arm, source in (("base", stars), ("plus", edited))}
    baseline_end, groups, geometry = source_geometry(nae.S.from_junctions(stars), sender)
    edited_end, other_groups, other_geometry = source_geometry(nae.S.from_junctions(edited), sender)
    assert groups == other_groups and geometry == other_geometry
    assert baseline_end.blocks == edited_end.blocks and baseline_end.opens.keys() == edited_end.opens.keys()
    assert edited_end.opens == {u: opening + (u == sender) for u, opening in baseline_end.opens.items()}
    results = {}
    for law in LAWS:
        starts = {arm: history(s, law, lawfulness[arm][law]["lawful"])
                  for arm, s in (("base", stars), ("plus", edited))}
        indices = {arm: index_history(s, starts[arm], slot if arm == "plus" else None)
                   for arm, s in (("base", stars), ("plus", edited))}
        extra = indices["plus"]["release"]
        if cohort(starts["plus"], 1)[1]:
            assert extra is not None
        if cohort(starts["base"], 1)[1] and cohort(starts["plus"], 1)[1]:
            assert extra["parents"] == (sender,)
        matches = match_layers(stars, starts, indices)
        for comparison in matches:
            comparison["necessary_types"] = necessary_type_inclusion(starts, indices, comparison["age"])
        scored, witnesses = receiver_receipts(starts, indices, geometry, sender, len(stars), matches)
        outside = [compare_outputs(starts, indices, age, 1 << sender, outside=True, exact_match=matches[age - 1])
                   for age in range(1, LAYERS + 1)]
        results[law] = {"literal_arms": starts, "new_input_first_birth": extra, "receivers": scored,
                        "matched_incidence": matches, "outside_sender_inclusive_family": outside,
                        "illustrative_receivers": witnesses}
    return {"lawfulness": lawfulness, "initial_live_loose_base": baseline_end.opens, "initial_live_loose_plus": edited_end.opens,
            "initial_groups": groups, "initial_witness_sets": baseline_end.blocks, "laws": results}


def score_source(spec, rng):
    _, _, nae = archived().libraries()
    stars = nae.J.stars_from(spec["arities"], spec["meetings"])
    p = nae.S.from_junctions(stars)
    candidates = tuple(v for v in range(len(stars)) if p.loose(v))
    check = {**spec, "source_stars": stars, "possible_senders": candidates}
    if not candidates:
        return {**check, "sender": None, "status": "no_live_sender"}
    sender = rng.choice(candidates)
    slot = p.nbits
    plus = [row + [slot] if v == sender else row[:] for v, row in enumerate(stars)]
    return {**check, "sender": sender, "edited_added_distinction": slot, **score_pair(stars, plus, sender, slot)}


def benchmarks(draws):
    # Match one paired lawful funded example under an independent reversal of both name sets.
    chosen = next((d for d in draws if all(d.get("laws", {}).get(law, {}).get("literal_arms", {}).get(arm, {}).get("steps", ())
                  and d["laws"][law]["literal_arms"][arm]["steps"][0]["births"]
                  for law in LAWS for arm in ("base", "plus"))), None)
    if chosen is None:
        return None
    stars, slot = chosen["source_stars"], chosen["edited_added_distinction"]
    sender = len(stars) - 1 - chosen["sender"]
    reverse = [sorted(slot - 1 - d for d in row) for row in reversed(stars)]
    recoded = [row + [slot] if v == sender else row[:] for v, row in enumerate(reverse)]
    other = score_pair(reverse, recoded, sender, slot)
    for law in LAWS:
        old = chosen["laws"][law]
        new = other["laws"][law]
        for r, result in old["receivers"].items():
            assert new["receivers"][len(stars) - 1 - r] == result
        assert new["outside_sender_inclusive_family"] == old["outside_sender_inclusive_family"]
        # Sham edit leaves the actual birth receipts unchanged.
        sham = history(stars, law, True)
        assert sham == old["literal_arms"]["base"]
    return {"draw": chosen["draw"], "both_laws_joint_receiver_renaming": True, "both_laws_no_op_replay": True}


def active_distance(geometry, ruler):
    d = geometry[ruler]
    if d is not None:
        return str(d)
    return "infinite" if geometry["live"] else "inactive"


def tally_receivers(draws, law, age, ruler):
    tests = defaultdict(Counter)
    for d in draws:
        for receiver in d.get("laws", {}).get(law, {}).get("receivers", {}).values():
            geom = receiver["source"]
            exact = active_distance(geom, ruler)
            if not geom["live"]:
                exact = "inactive" if ruler != "ordinary_holder_steps" else "inactive_at_step_" + exact
            counter = tests[exact]
            row = receiver["by_age"][age - 1]
            status = row["statuses"]
            both_positive = all(s == "positive" for s in status.values())
            counter["source_receiver_pairs"] += 1
            counter["compared"] += row["compared"]
            counter["both_positive"] += both_positive
            counter["one_positive_and_other_stalled"] += set(status.values()) == {"positive", "stall"}
            counter["a_closing_birth_in_either_arm"] += "closing" in status.values()
            counter["neither_arm_has_a_birth"] += all(k not in {"positive", "closing"} for k in status.values())
            counter["any_receiver_births"] += any(a["births"] for a in row["arms"].values())
            if not row["compared"]:
                continue
            counter["with_any_priced_roster_difference"] += row["different_priced_parent_multiset"]
            counter["positive_with_birth_count_difference"] += both_positive and row["different_current_birth_count"]
            counter["positive_with_roster_difference"] += both_positive and row["different_parent_multiset"]
            counter["positive_with_any_priced_roster_difference"] += both_positive and row["different_priced_parent_multiset"]
            counter["positive_with_matched_price_difference"] += both_positive and row["matched_births_with_different_prices"] > 0
            if both_positive and row["exact_parentage_matching"] is not None:
                counter["positive_with_exact_parentage_match"] += 1
                counter["positive_with_price_difference_in_exact_parent_match"] += row["exact_parentage_matching"]["fresh_count_changes"] > 0
            counter["positive_with_held_places_difference"] += both_positive and row["different_held_places"]
            counter["positive_with_written_distinction_count_difference"] += both_positive and row["different_written_distinctions"]
            counter["positive_difference_before_original_joint"] += both_positive and row["different_priced_parent_multiset"] and not row["earlier_or_current_original_joint"]
            counter["positive_difference_before_added_input_joint"] += both_positive and row["different_priced_parent_multiset"] and not row["earlier_or_current_added_input_joint"]
            numeric = geom[ruler]
            if both_positive and geom["live"]:
                counter["positive_matched_price_before_ruler_bound"] += (numeric is None or age < numeric) and row["matched_births_with_different_prices"] > 0
                counter["positive_roster_before_ruler_bound"] += (numeric is None or age <= numeric) and row["different_parent_multiset"]
    return {k: dict(v) for k, v in tests.items()}


def summarize(draws, law):
    arms = {arm: [d["laws"][law]["literal_arms"][arm] for d in draws if "laws" in d] for arm in ("base", "plus")}
    by_arm = {}
    for arm, items in arms.items():
        by_arm[arm] = {"terminal_status": dict(Counter(a["terminal"] for a in items)),
                       "lawful": sum(a["terminal"] != "unlawful" for a in items),
                       "materialized_birth_cohorts": {age: sum(bool(cohort(a, age)[1]) for a in items) for age in range(1, LAYERS + 1)},
                       "positive_cohorts": {age: sum(cohort(a, age)[0] == "positive" for a in items) for age in range(1, LAYERS + 1)},
                       "max_current_live": max((len(s["live"]) for a in items for s in a["stages"]), default=0)}
    cases = [d["laws"][law] for d in draws if "laws" in d]
    receiver_counts = Counter("live" if r["source"]["live"] else "inactive" for d in cases for r in d["receivers"].values())
    return {"draws": len(draws), "no_live_sender": sum(d["sender"] is None for d in draws), "arms": by_arm,
            "initial_receivers": dict(receiver_counts),
            "first_actual_shared_ages": {arm: dict(Counter(str(r["first_original_joint"][arm]) for d in cases for r in d["receivers"].values()
                                                         if r["source"]["live"])) for arm in ("base", "plus")},
            "incidence_inclusion_status_at_each_age": {age: dict(Counter(d["matched_incidence"][age - 1]["status"] for d in cases)) for age in range(1, LAYERS + 1)},
            "necessary_parent_type_coverage_at_each_age": {age: dict(Counter(
                ("parent_types" if not d["matched_incidence"][age - 1]["necessary_types"]["parent_multiset_types_contain_base"] else
                 "fresh_capacity" if not d["matched_incidence"][age - 1]["necessary_types"]["parent_types_and_fresh_capacity_contain_base"]
                 else "passes") for d in cases if d["matched_incidence"][age - 1]["necessary_types"] is not None))
                for age in range(1, LAYERS + 1)},
            "outside_sender_inclusive_differences": {age: {
                "both_positive": sum(set(d["outside_sender_inclusive_family"][age - 1]["statuses"].values()) == {"positive"} for d in cases),
                "positive_priced_multiset_differences": sum(set(d["outside_sender_inclusive_family"][age - 1]["statuses"].values()) == {"positive"}
                    and bool(d["outside_sender_inclusive_family"][age - 1]["different_priced_parent_multiset"]) for d in cases),
                "positive_with_a_physical_match": sum(set(d["outside_sender_inclusive_family"][age - 1]["statuses"].values()) == {"positive"}
                    and d["outside_sender_inclusive_family"][age - 1]["exact_parentage_matching"] is not None for d in cases),
                "positive_with_a_physically_matched_outside_difference": sum(
                    set(d["outside_sender_inclusive_family"][age - 1]["statuses"].values()) == {"positive"}
                    and d["outside_sender_inclusive_family"][age - 1]["exact_parentage_matching"] is not None
                    and (bool(d["outside_sender_inclusive_family"][age - 1]["exact_parentage_matching"]["fresh_count_changes"])
                         or bool(d["outside_sender_inclusive_family"][age - 1]["exact_parentage_matching"]["extra_augmented_births"]))
                    for d in cases)}
                for age in range(1, LAYERS + 1)},
            "by_age_and_ruler": {age: {ruler: tally_receivers(draws, law, age, ruler)
                     for ruler in ("witnessed_steps", "exact_two_parent_steps", "ordinary_holder_steps")} for age in range(1, LAYERS + 1)}}


def intern_receiver_rows(draws):
    codes, unique = {}, []

    def indices(rows):
        result = []
        for row in rows:
            key = json.dumps(row, separators=(",", ":"), sort_keys=True)
            if key not in codes:
                codes[key] = len(unique)
                unique.append(row)
            result.append(codes[key])
        return result

    for d in draws:
        for law in d.get("laws", {}).values():
            for r in law["receivers"].values():
                r["by_age_row_ids"] = indices(r.pop("by_age"))
            law["outside_sender_inclusive_row_ids"] = indices(law.pop("outside_sender_inclusive_family"))
    return unique


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Disposable replay of leading draws")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use a scratch output with --limit")
    rng = random.Random(SENDER_SEED)
    draws = []
    for i, spec in enumerate(source_draws()):
        if args.limit is not None and i >= args.limit:
            break
        draws.append(score_source(spec, rng))
    weights = {k: [d for d in draws if d["weighting"] == k] for k in SEEDS}
    summary = {"overall": {law: summarize(draws, law) for law in LAWS},
               "by_weighting": {kind: {law: summarize(rows, law) for law in LAWS} for kind, rows in weights.items()},
               "by_weighting_and_size": {k: {n: {law: {arm: dict(Counter(d["laws"][law]["literal_arms"][arm]["terminal"]
                         for d in rows if "laws" in d and d["source_knots"] == n)) for arm in ("base", "plus")} for law in LAWS}
                         for n in range(4, 9)} for k, rows in weights.items()}}
    calibration = benchmarks(draws)
    unique_receiver_rows = intern_receiver_rows(draws)
    record = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "seeds": SEEDS,
              "sender_seed": SENDER_SEED, "max_layers": LAYERS, "birth_cap": CAP, "draws_by_weight_and_size": PER_SIZE,
              "calibration": calibration, "summary": summary, "receiver_age_rows": unique_receiver_rows, "draws": draws}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as out:
        json.dump(record, out, sort_keys=True, separators=(",", ":"))
        out.write("\n")


if __name__ == "__main__":
    main()
