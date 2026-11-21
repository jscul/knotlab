"""Replay fresh starts under real funding and the two frozen join rules."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from fractions import Fraction
from math import prod
from pathlib import Path
from random import Random
import json
import sys

import networkx as nx
from scipy.stats import beta


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODEL = HERE / "model.py"
PREREGISTRATION = ROOT / "research" / HERE.parent.name / "preregistration.md"
FIXTURES = ROOT / ("experiments/GENERATORS-20261120-001A/"
                   "GENERATORS-20261120-001A-E001_generators/fixtures.py")
PRIOR_DISTANCES = ROOT / ("experiments/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/"
                          "STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A-E001_distance_delays/samples.py")
ARMS = ("trees", "partnered", "spent_paths")
LAWS = ("parity", "nae")
RULES = ("ordinary", "spent")
N = 64
HORIZON = 4
CAP = 256
FORECAST_CAP = 8192
SEEDS = {"trees": 20261120721, "partnered": 20261120722,
         "spent_paths": 20261120723, "queries": 20261120724}
NONPARTNERS = tuple((a, b) for a, b in combinations(range(6), 2) if a // 2 != b // 2)


@cache
def load(name, path):
    spec = spec_from_file_location(name, path)
    result = module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def fixture():
    return load("spent_join_sample_fixtures", FIXTURES)


def step(stars, law, rule):
    model = load("spent_join_sample_model", MODEL)
    return model.step(stars, law, rule, cap=CAP, forecast_cap=FORECAST_CAP)


def query_rngs():
    rng = Random(SEEDS["queries"])
    return {(a, i): rng.getrandbits(128) for a in ARMS for i in range(N)}


def tree_start(rng):
    size = rng.randrange(3, 9)
    prufer = tuple(rng.randrange(size) for _ in range(size - 2))
    graph = nx.from_prufer_sequence(prufer)
    pairs = sorted(tuple(sorted(pair)) for pair in graph.edges)
    coins = [rng.randrange(4) == 0 for _ in range(size)]
    supply = [max(0, 3 - degree) + coin
              for (_, degree), coin in zip(sorted(graph.degree), coins, strict=True)]
    return {"original_size": size, "prufer": prufer, "shared_pairs": pairs,
            "surplus_coins": coins, "loose_supplies": supply}


def partner_start(rng):
    directions = [rng.randrange(2) for _ in NONPARTNERS]
    pairs = []
    for w, ((a, b), direction) in enumerate(zip(NONPARTNERS, directions, strict=True), 6):
        pairs.extend(((a, w), (b, w), ((a, b)[direction], w)))
    return {"original_size": 18, "orientations": directions, "shared_pairs": pairs,
            "loose_supplies": [4] * 6 + [0] * 12}


def path_start(rng):
    length = rng.randrange(2, 7)
    widths = [rng.randrange(3, 5) for _ in range(length)]
    pairs = [(i, i + 1) for i in range(length - 1)]
    supply = [0] * length
    leaves = []
    for center, width in enumerate(widths):
        attached = list(range(len(supply), len(supply) + width))
        leaves.append(attached)
        pairs.extend((center, v) for v in attached)
        supply.extend([width - 1 + (1 if center in (0, length - 1) else 2)] * width)
    short = rng.randrange(length, len(supply))
    return {"original_size": len(supply), "spent_length": length, "live_by_spent_holder": leaves,
            "boundary_widths": widths, "shared_pairs": pairs, "loose_supplies": supply,
            "shorted_holder": short}


def query_for(seed, raw, common_source):
    rng = Random(seed)
    if "live_by_spent_holder" in raw:
        arms = raw["live_by_spent_holder"]
        pair = rng.choice(arms[0]), rng.choice(arms[-1])
    else:
        pair = tuple(sorted(rng.sample([i for i, n in enumerate(raw["loose_supplies"]) if n], 2)))
    _, _, loose = fixture().incidence(common_source)
    return pair, tuple(rng.choice(loose[v]) for v in pair)


def sources_for(raw):
    source = fixture().source_from(raw["shared_pairs"], raw["loose_supplies"])
    result = {"prepared": source}
    if "shorted_holder" in raw:
        changed = raw["shorted_holder"]
        _, _, loose = fixture().incidence(source)
        bit = loose[changed][-1]
        assert len(source[changed]) >= 4
        result["short_one"] = tuple(tuple(d for d in row if d != bit) if i == changed else row
                                    for i, row in enumerate(source))
    return result


@cache
def lawful(stars, law):
    f = fixture()
    if len(set(map(frozenset, stars))) != len(stars) or any(len(row) < 3 for row in stars):
        return False
    with f.Minisat22() as solver:
        if law == "nae":
            for star in stars:
                f.nae_add(solver, star)
        for star in stars:
            actual = f.parity_words(stars, star) if law == "parity" else f.nae_words(solver, star)
            if actual != f.expected_words(law, len(star)):
                return False
            f.canonical_relation(law, len(star))
    return True


def physical_bridge_records(stars):
    """Independent check by removing each eligible physical shared distinction."""
    owners, ordinary, loose = fixture().incidence(stars)
    result = []
    multiplicity = Counter(tuple(sorted(vs)) for vs in owners.values() if len(vs) == 2)
    for bit, holders in sorted(owners.items()):
        if len(holders) != 2 or any(v in loose for v in holders):
            continue
        left, right = sorted(holders)
        a, b = (tuple(sorted(set(ordinary[v]) & loose.keys())) for v in (left, right))
        if not a or not b or multiplicity[left, right] != 1:
            continue
        ordinary.remove_edge(left, right)
        if not nx.has_path(ordinary, left, right):
            assert not set(a) & set(b)
            result.append((bit, left, right, a, b))
        ordinary.add_edge(left, right)
    return tuple(result)


def names_and_count(bits):
    if not bits:
        return {"count": 0}
    if tuple(bits) == tuple(range(bits[0], bits[0] + len(bits))):
        return {"count": len(bits), "first": bits[0]}
    return {"count": len(bits), "names": bits}


def check_actual(old, move, law):
    assert move.stars[:len(old)] == old
    owners, _, loose = fixture().incidence(old)
    consumed, born = [], []
    for parents, inputs, new, support in zip(move.parents, move.inputs, move.fresh,
                                              move.stars[len(old):], strict=True):
        assert tuple(support) == tuple(inputs) + tuple(new) or set(support) == set(inputs) | set(new)
        assert len(parents) == len(inputs) and all(v in loose for v in parents)
        assert {owners[d][0] for d in inputs} == set(parents)
        assert all(len(owners[d]) == 1 for d in inputs)
        assert not set(new) & owners.keys()
        consumed.extend(inputs)
        born.extend(new)
    assert sorted(consumed) == sorted(d for row in loose.values() for d in row)
    assert len(born) == len(set(born))
    closing = len(move.parents) == 1 and law == "parity"
    assert all(new or closing for new in move.fresh)
    assert all(len(g) + len(new) >= 3 or closing
               for g, new in zip(move.parents, move.fresh, strict=True))
    if not born:
        assert closing and len(move.parents) == 1
    return bool(born), closing


def witnessed_separation(stars, left, right):
    _, ordinary, loose = fixture().incidence(stars)
    _, witnessed = fixture().witnessed_end(ordinary, loose)
    sources, targets = left & loose.keys(), right & loose.keys()
    if not sources or not targets:
        return None
    reached = nx.multi_source_dijkstra_path_length(witnessed, sources)
    return min((reached[v] for v in targets if v in reached), default=None)


@dataclass
class History:
    rows: list
    first_common: int | None
    arrival_decided: bool
    certificate: str
    observed_first_common: int | None


def co_input_distance(groups, live, pair):
    connected = nx.Graph()
    connected.add_nodes_from(live)
    for group in groups:
        connected.add_edges_from(combinations(group, 2))
    return nx.shortest_path_length(connected, *pair) if nx.has_path(connected, *pair) else None


def replay(arm, source, pair, law, rule):
    stars = source
    rows = []
    left, right = ({v} for v in pair)
    first = None
    decided = False
    certificate = "bounded_prefix"
    observed = None
    for age in range(HORIZON):
        model = step(stars, law, rule)
        physical = physical_bridge_records(stars)
        physical_rosters = {tuple(sorted((*a, *b))) for _, _, _, a, b in physical}
        assert len(physical_rosters) == len(physical)
        assert not physical or age < 2
        if rule == "ordinary":
            assert not model.added
        elif model.status != "cap" or model.added:
            assert set(map(tuple, model.added)) == physical_rosters
        entry = {"attempt_after_age": age, "status": model.status, "funded": model.funded,
                 "physical_eligible": physical, "added": model.added,
                 "model_bridge_records": model.bridges, "shortages": model.shortages,
                 "specified_multi_groups": model.groups, "forecast_added": model.next_added,
                 "planned_parents": model.parents, "planned_inputs": model.inputs,
                 "planned_births_lower": model.planned_births_lower,
                 "actual_births": None}
        if rows and not rows[-1]["closed_after_step"]:
            previous = rows[-1]
            assert tuple(previous["forecast_added"]) == model.added
            if model.status != "cap" or model.funded is True:
                actual_demand = Counter(v for g in model.groups for v in g)
                assert all(actual_demand[item["id"]] == item["next_demand"]
                           for item in previous["actual_births"])
                entry["previous_forecast_matches_actual_demand"] = True
        rows.append(entry)
        if age == 0 and model.funded and (rule == "ordinary" or arm in ("spent_paths", "partnered")):
            _, _, live = fixture().incidence(stars)
            if model.groups or model.parents or model.status == "extend":
                first = co_input_distance(model.groups, live, pair)
                decided, certificate = True, "paid_origin_then_ordinary"
        if model.status != "extend":
            assert model.stars == stars
            if rule == "ordinary" and age == 0 and model.funded and not decided:
                first = witnessed_separation(stars, left, right)
                decided, certificate = True, "ordinary_paid_initial_relation"
            if model.status in ("closed", "stall") and not decided:
                decided, certificate = True, model.status
            break
        nonclosing, closing = check_actual(stars, model, law)
        entry["actual_births"] = [
            {"id": i, "parents": g, "inputs": taken, "fresh": names_and_count(new), "next_demand": demand}
            for i, (g, taken, new, demand) in enumerate(
                zip(model.parents, model.inputs, model.fresh, model.demand, strict=True), len(stars))]
        entry["total_actual_fresh"] = sum(map(len, model.fresh))
        entry["total_actual_births"] = len(model.parents)
        entry["max_actual_parent_count"] = max(map(len, model.parents))
        entry["protected_old_words_extend"] = True
        entry["closed_after_step"] = not nonclosing
        stars = model.stars
        if model.added:
            _, ordinary, _ = fixture().incidence(stars)
            for _, a, b, _, _ in physical:
                ordinary.remove_edge(a, b)
                assert nx.has_path(ordinary, a, b)
                ordinary.add_edge(a, b)
            entry["every_paid_authorizing_name_now_has_an_alternate_connection"] = True
        left = {i for i, g in enumerate(model.parents, len(stars) - len(model.parents)) if left.intersection(g)}
        right = {i for i, g in enumerate(model.parents, len(stars) - len(model.parents)) if right.intersection(g)}
        entry["query_descendants"] = [sorted(left), sorted(right)]
        if left & right and observed is None:
            observed = age + 1
            if decided:
                assert first == observed
            else:
                first, decided, certificate = age + 1, True, "literal"
        elif not decided and closing:
            decided, certificate = True, "closed"
        elif not decided and age == 1:
            d = witnessed_separation(stars, left, right)
            first = age + 1 + d if d is not None else None
            decided, certificate = True, "ordinary_from_second_reached_cut"
    completed = sum(r["status"] == "extend" for r in rows)
    if decided and first is not None and first <= completed:
        assert first == observed
    return History(rows, first, decided, certificate, observed)


def paired_comparison(ordinary, spent, originals):
    """Match outputs across rules by the whole transported parent roster."""
    previous = {i: i for i in range(originals)}
    tables = []
    for step_number, (old, changed) in enumerate(zip(ordinary.rows, spent.rows), 1):
        a, b = (step_row["actual_births"] for step_row in (old, changed))
        if a is None or b is None:
            tables.append({"cut": step_number, "both_materialized": False,
                           "statuses": (old["status"], changed["status"])})
            break
        pending = defaultdict(list)
        for item in b:
            pending[tuple(sorted(item["parents"]))].append(item)
        matched, prices, old_only = {}, [], []
        for item in a:
            g = item["parents"]
            key = tuple(sorted(previous[v] for v in g)) if set(g) <= previous.keys() else ()
            if not pending[key]:
                old_only.append(item["id"])
                continue
            counterpart = pending[key].pop(0)
            matched[item["id"]] = counterpart["id"]
            price = item["fresh"]["count"], counterpart["fresh"]["count"]
            if price[0] != price[1]:
                prices.append((item["id"], counterpart["id"], *price))
        rival_only = sorted(item["id"] for pending_roster in pending.values() for item in pending_roster)
        tables.append({"cut": step_number, "both_materialized": True, "matched_count": len(matched),
                       "ordinary_only": old_only, "spent_only": rival_only, "price_differences": prices,
                       "total_fresh_difference": changed["total_actual_fresh"] - old["total_actual_fresh"],
                       "birth_count_difference": len(b) - len(a)})
        previous = matched
    return tables


def origin_rulers(stars, pair, markers):
    owners, ordinary, loose = fixture().incidence(stars)
    prior = load("prior_distance_measurement", PRIOR_DISTANCES)
    result = {"ordinary_holder_steps": nx.shortest_path_length(ordinary, *pair)}
    if nx.is_tree(ordinary) and all(ordinary.degree(v) + len(loose.get(v, ())) == len(row)
                                   for v, row in enumerate(stars)):
        route = nx.shortest_path(ordinary, *pair)
        arities = [len(stars[v]) for v in route]
        c = Fraction((-1) ** len(route), prod((1 << (arity - 1)) - 1 for arity in arities))
        bond = sum(arities) - 2 * (len(route) - 1) - 1
        result.update(
            nae={"status": "exact", "correlation": [c.numerator, c.denominator],
                 "disagreement_rate": prior.fraction_record((1 - c) / 2),
                 "holder_transfer_distance": {"log_base": 3, "argument": c.denominator, "offset": -1},
                 "far": abs(c) <= prior.NAE_FAR},
            parity={"status": "exact", "bond_distance": bond, "far": bond >= prior.PARITY_FAR,
                    "pair_disagreement_rate": [1, 2]},
            original_route=route, route_arities=arities,
        )
        if len(ordinary) <= 8:
            graph, exterior = prior.wired_graph(owners, len(ordinary))
            assert prior.exhaustive_cut(graph, exterior, pair) == bond + 1
            result["literal_parity_cut_verified"] = True
        if len(owners) <= 12:
            total, signed = prior.small_exact_words(stars, markers)
            assert Fraction(signed, total) == c
            result["literal_nae_words_verified"] = True
    else:
        result["nae"] = prior.nae_distance(stars, pair, markers, ordinary, loose, ())
        result["parity"] = prior.parity_distance(owners, ordinary, pair, loose)
        result["private_correlation_bound"] = [1, 225]
        result["private_bond_distance_lower"] = 7
        assert result["nae"]["far"] and result["parity"]["far"]
    return result


def relabel_check(source):
    mapping = tuple(reversed(range(len(source))))
    names = sorted({d for row in source for d in row})
    renamed_bit = dict(zip(names, reversed(names), strict=True))
    renamed = tuple(tuple(sorted(renamed_bit[d] for d in source[v])) for v in mapping)
    law_checks = []
    for law in LAWS:
        for rule in RULES:
            first = step(source, law, rule)
            other = step(renamed, law, rule)
            assert first.status == other.status and first.funded == other.funded
            assert sorted(first.shortages) == sorted((mapping[v], n) for v, n in other.shortages)
            assert sorted(first.added) == sorted(tuple(sorted(mapping[v] for v in g)) for g in other.added)
            if first.status == "extend":
                a = Counter((g, len(new)) for g, new in zip(first.parents, first.fresh, strict=True))
                b = Counter((tuple(sorted(mapping[v] for v in g)), len(new))
                            for g, new in zip(other.parents, other.fresh, strict=True))
                assert a == b
            law_checks.append((law, rule, first.status))
    return law_checks


def read_trial(arm, raw, index, query_seed):
    sources = sources_for(raw)
    pair, marks = query_for(query_seed, raw, sources.get("short_one", sources["prepared"]))
    trials = {}
    for tag, source in sources.items():
        lawful_by_law = {law: lawful(source, law) for law in LAWS}
        trials[tag] = {"initial_holdings": source, "lawful_by_law": lawful_by_law,
                       "original_rulers": origin_rulers(source, pair, marks), "by_law": {}}
        for law, admitted in lawful_by_law.items():
            if not admitted:
                continue
            ordinary, rival = [replay(arm, source, pair, law, r) for r in RULES]
            matched = paired_comparison(ordinary, rival, len(source))
            if matched[0]["both_materialized"]:
                width = sum(len(g) - 1 for g in rival.rows[0]["added"])
                assert matched[0]["birth_count_difference"] == -width
            if arm == "partnered":
                assert ordinary == rival and ordinary.arrival_decided
                assert ordinary.first_common == (2 if pair[0] // 2 == pair[1] // 2 else 1)
                assert [r.get("total_actual_births") for r in ordinary.rows] == [8, 10, 24, None]
                assert ordinary.rows[-1]["status"] == "cap"
            if arm == "spent_paths":
                assert ordinary.rows[0]["funded"] and ordinary.arrival_decided and ordinary.first_common is None
                origin = rival.rows[0]
                assert len(origin["added"]) == raw["spent_length"] - 1
                assert rival.arrival_decided
                if tag == "short_one":
                    assert origin["status"] == "stall" and rival.first_common is None
                    assert origin["shortages"] == ((raw["shorted_holder"], 1),)
                else:
                    assert origin["funded"] and rival.first_common == raw["spent_length"] - 1
            trials[tag]["by_law"][law] = {
                "ordinary": vars(ordinary), "spent": vars(rival), "matched_outputs": matched,
                "proved_identical_at_all_ages": arm == "partnered"}
        if index == 0:
            trials[tag]["physical_renaming_checks"] = relabel_check(source)
    return {"index": index, "raw_start": raw, "query_seed": query_seed,
            "query_holders": pair, "query_marks": marks, "preparations": trials}


def cp(k, n):
    if not n:
        return [None, None]
    return [float(beta.ppf(.025, k, n - k + 1)) if k else 0.0,
            float(beta.ppf(.975, k + 1, n - k)) if k < n else 1.0]


def interval(votes):
    bins = Counter(votes)
    n = sum(bins.values())
    k, missing = bins[True], bins[None]
    return {"denominator": n, "yes": k, "no": bins[False], "unresolved": missing,
            "proportion_bounds": [k / n, (k + missing) / n] if n else [None, None],
            "marginal_exact_95_envelope": [cp(k, n)[0], cp(k + missing, n)[1]]}


def recorded_special_birth(history):
    if any(r["added"] and r["actual_births"] for r in history["rows"]):
        return True
    for row in history["rows"][:2]:
        if row["status"] in ("stall", "closed"):
            return False
        if row["status"] in ("cap", "forecast_cap"):
            return None
    return False


def first_common(history):
    if not history["arrival_decided"]:
        return None
    return history["first_common"] is not None


def comparison_changed(row, field):
    if row["proved_identical_at_all_ages"]:
        return False
    prefix_identical = True
    for cut in row["matched_outputs"]:
        if not cut["both_materialized"]:
            if cut["cut"] >= 3 and prefix_identical:
                return False
            if any(s in ("cap", "forecast_cap") for s in cut["statuses"]):
                return None
            if field == "roster" and cut["statuses"].count("extend") == 1:
                return True
            return False
        roster_differs = bool(cut["ordinary_only"] or cut["spent_only"])
        prices_differ = bool(cut["price_differences"])
        prefix_identical &= not (roster_differs or prices_differ)
        if field == "roster" and roster_differs:
            return True
        if field == "price" and prices_differ:
            return True
    return False


def paired_values(paired):
    result = []
    for v in paired:
        m = v["matched_outputs"][0]
        if not m["both_materialized"]:
            continue
        a, b = (v[r]["rows"][0] for r in RULES)
        result.append({"spent_groups": len(b["added"]),
                       "spent_parent_slots": sum(map(len, b["added"])),
                       "max_spent_parent_count": max(map(len, b["added"]), default=0),
                       "ordinary_births": a["total_actual_births"], "spent_births": b["total_actual_births"],
                       "ordinary_fresh": a["total_actual_fresh"], "spent_fresh": b["total_actual_fresh"],
                       "matched_fresh_changes": len(m["price_differences"]),
                       "birth_difference": m["birth_count_difference"],
                       "fresh_difference": m["total_fresh_difference"]})
    return {key: {"min": min(r[key] for r in result), "max": max(r[key] for r in result),
                  "counts": dict(sorted(Counter(r[key] for r in result).items()))}
            for key in result[0]} if result else {}


def panel_summary(draws, tag, law):
    eligible = [d["preparations"][tag] for d in draws]
    lawful = [p["by_law"][law] for p in eligible if p["lawful_by_law"][law]]
    ordinary_funded = [v for v in lawful if v["ordinary"]["rows"][0]["funded"] is True]
    both_funded = [v for v in ordinary_funded if v["spent"]["rows"][0]["funded"] is True]
    rule_summaries = {}
    for rule in RULES:
        histories = [v[rule] for v in lawful]
        first_funded = [h for h in histories if h["rows"][0]["funded"] is True]
        activated = [h for h in histories if h["rows"][0]["physical_eligible"]]
        stages = {}
        for age in range(HORIZON):
            rows = [h["rows"][age] for h in histories if len(h["rows"]) > age]
            qualified = [r for r in rows if r["physical_eligible"]]
            forecast = [r for r in rows if r["status"] in ("extend", "forecast_cap")]
            completed = [r for r in rows if r["status"] == "extend"]
            stages[age] = {
                "attempts_in_lawful_starts": len(rows), "statuses": Counter(r["status"] for r in rows),
                "physical_eligible_trigger": interval(bool(r["physical_eligible"]) for r in rows),
                "funded": interval(r["funded"] for r in rows if r["status"] != "closed"),
                "funded_given_trigger": interval(r["funded"] for r in qualified),
                "actual_extension": interval(r["status"] == "extend" if r["status"] not in ("cap", "forecast_cap")
                                             else None for r in rows),
                "forecast_reports_new_groups": interval(bool(r["forecast_added"]) for r in forecast),
                "materialized_width_counts": Counter(r["total_actual_births"] for r in completed),
                "maximum_parent_number_counts": Counter(r["max_actual_parent_count"] for r in completed),
            }
        rule_summaries[rule] = {
            "lawful_histories": len(histories), "first_funded": interval(h["rows"][0]["funded"] for h in histories),
            "actual_first_extension": interval(h["rows"][0]["status"] == "extend" for h in histories),
            "any_special_birth": interval(recorded_special_birth(h) for h in histories) if rule == "spent"
            else interval(False for _ in histories),
            "first_common_descendant_among_lawful": interval(first_common(h) for h in histories),
            "first_common_descendant_among_first_funded": interval(first_common(h) for h in first_funded),
            "first_common_descendant_among_origin_eligible": interval(first_common(h) for h in activated),
            "literal_first_common_counts": Counter(str(h["observed_first_common"]) for h in histories),
            "exact_first_common_counts": Counter(
                "unknown" if not h["arrival_decided"] else str(h["first_common"]) for h in histories),
            "stages": stages,
        }
    return {
        "attempted_draws": len(eligible), "marked_pair_present": len(eligible),
        "lawful_origins": interval(p["lawful_by_law"][law] for p in eligible),
        "original_size_counts": Counter(len(p["initial_holdings"]) for p in eligible),
        "two_rules_first_funded": len(both_funded),
        "origin_ruler_statuses": Counter(p["original_rulers"][law]["status"] for p in eligible),
        "rules": rule_summaries, "joint_literal_first_step_costs": paired_values(both_funded),
        "rule_differences": {
            "new_paid_veto_given_ordinary_funding": interval(
                False if v["spent"]["rows"][0]["funded"] else True if
                v["spent"]["rows"][0]["status"] == "stall" else None for v in ordinary_funded),
            "changed_actual_birth_roster": interval(comparison_changed(v, "roster") for v in lawful),
            "changed_matched_price": interval(comparison_changed(v, "price") for v in lawful),
            "new_finite_arrival_given_both_funded": interval(
                first_common(v["spent"]) if first_common(v["ordinary"]) is False else
                False if first_common(v["ordinary"]) is True else None for v in both_funded),
        },
    }


def absence_tag(distance):
    return distance if distance is not None else "never"


def matched_shortage(draws):
    def same_state(a, b):
        return (a["nae"]["disagreement_rate"] == b["nae"]["disagreement_rate"]
                and a["parity"]["bond_distance"] == b["parity"]["bond_distance"])
    equal_rulers = []
    comparison = defaultdict(Counter)
    path_scope = Counter()
    for d in draws:
        a, b = (d["preparations"][tag] for tag in ("prepared", "short_one"))
        match = same_state(a["original_rulers"], b["original_rulers"])
        assert match == (d["raw_start"]["shorted_holder"] not in d["query_holders"])
        equal_rulers.append(match)
        length = d["raw_start"]["spent_length"]
        path_scope[length] += 1
        for law in LAWS:
            av = a["by_law"][law]["spent"]
            bv = b["by_law"][law]["spent"]
            assert av["arrival_decided"] and bv["arrival_decided"]
            comparison[law][f"{absence_tag(av['first_common'])} / {absence_tag(bv['first_common'])}"] += 1
    return {"same_pair_state_rulers": interval(equal_rulers),
            "first_common_paid_vs_short_by_law": comparison, "spent_path_length_counts": path_scope}


def run(arm):
    seeds = query_rngs()
    rng = Random(SEEDS[arm])
    generator = {"trees": tree_start, "partnered": partner_start, "spent_paths": path_start}[arm]
    draws = [read_trial(arm, generator(rng), i, seeds[arm, i]) for i in range(N)]
    tags = tuple(draws[0]["preparations"])
    source_paths = (Path(__file__).resolve(), HERE / "contract.json", PREREGISTRATION,
                    MODEL, FIXTURES, PRIOR_DISTANCES)
    result = {
        "arm": arm, "seeds": SEEDS, "draws": draws,
        "scopes": {tag: {law: panel_summary(draws, tag, law) for law in LAWS} for tag in tags},
        "limits": {"attempted_cuts": HORIZON, "birth_cap": CAP, "forecast_multi_group_cap": FORECAST_CAP},
        "sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in source_paths},
    }
    if arm == "spent_paths":
        result["paired_shortage"] = matched_shortage(draws)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = json.dumps(run(args.arm), sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(record)
    else:
        print(record, end="")


if __name__ == "__main__":
    main()
