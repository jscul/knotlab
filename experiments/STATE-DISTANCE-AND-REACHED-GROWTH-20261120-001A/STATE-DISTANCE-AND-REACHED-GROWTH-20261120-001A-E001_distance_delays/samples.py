"""Fresh paired measurements of present state readings and shared descent."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from heapq import heappop, heappush
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, count
from math import prod
from pathlib import Path
from random import Random
import json
import sys

import networkx as nx
import numpy as np
from scipy.stats import beta


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREREG = ROOT / "research" / HERE.parent.name / "preregistration.md"
FIXTURES = ROOT / ("experiments/GENERATORS-20261120-001A/"
                   "GENERATORS-20261120-001A-E001_generators/fixtures.py")
RATES = ROOT / ("experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C/"
                "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C-E001_wider_meetings/"
                "census_exact_rates.py")
PARTNER_PROOF = ROOT / ("proofs/WALL-READ-20261119-001A/"
                        "WALL-READ-20261119-001A-P001_partnered/proof.md")
ARMS = ("tree", "edited_tree", "partnered")
LAWS = ("parity", "nae")
N = 64
HORIZON = 2
BIRTH_CAP = 128
BOND_CAP = 512
TERM_CAP = 30_000_000
TENSOR_CAP = 3 ** 13
SEEDS = {"tree": 20261120611, "added_meeting": 20261120612,
         "orientation": 20261120613, "queries": 20261120614, "age_four": 20261120615}
PARTNER_PAIRS = tuple((a, b) for a, b in combinations(range(6), 2) if a // 2 != b // 2)
NAE_FAR = Fraction(1, 81)
PARITY_FAR = 4


@cache
def local(name, path):
    specification = spec_from_file_location(name, path)
    result = module_from_spec(specification)
    sys.modules[name] = result
    specification.loader.exec_module(result)
    return result


def fixture():
    return local("distance_delay_fixture", FIXTURES)


def exact_engine():
    return local("distance_delay_exact_rates", RATES)


def trees():
    sources = Random(SEEDS["tree"])
    edits = Random(SEEDS["added_meeting"])
    for _ in range(N):
        size = sources.randrange(3, 6)
        prufer = tuple(sources.randrange(size) for _ in range(size - 2))
        coins = tuple(sources.randrange(4) == 0 for _ in range(size))
        meetings = tuple(sorted(tuple(sorted(pair))
                                for pair in nx.from_prufer_sequence(prufer).edges))
        absent = sorted(set(combinations(range(size), 2)) - set(meetings))
        yield {"prufer": prufer, "coins": coins, "tree_meetings": meetings,
               "added_meeting": edits.choice(absent), "size": size}


def draw_inputs(arm):
    if arm == "partnered":
        rng = Random(SEEDS["orientation"])
        for _ in range(N):
            yield {"orientations": tuple(rng.randrange(2) for _ in PARTNER_PAIRS)}
    else:
        yield from trees()


def physical_source(arm, raw):
    f = fixture()
    if arm == "partnered":
        meetings = []
        for witness, ((a, b), orientation) in enumerate(zip(PARTNER_PAIRS, raw["orientations"],
                                                              strict=True), 6):
            meetings.extend(((a, witness), (b, witness), ((a, b)[orientation], witness)))
        return f.source_from(meetings, (4,) * 6 + (0,) * len(PARTNER_PAIRS))
    meetings = list(raw["tree_meetings"])
    if arm == "edited_tree":
        meetings.append(raw["added_meeting"])
    degrees = Counter(k for pair in meetings for k in pair)
    openings = [max(3, degrees[k]) - degrees[k] + coin
                for k, coin in enumerate(raw["coins"])]
    return f.source_from(meetings, openings)


def query_seeds():
    rng = Random(SEEDS["queries"])
    return {(arm, i, age): rng.getrandbits(128) for arm in ARMS for i in range(N)
            for age in range(HORIZON + 1)}


@cache
def source_gate(stars, law):
    f = fixture()
    rejected = []
    if len(set(map(frozenset, stars))) != len(stars):
        return {"lawful": False, "duplicate_support": True}
    with f.Minisat22() as solver:
        if law == "nae":
            for support in stars:
                f.nae_add(solver, support)
        for holder, support in enumerate(stars):
            actual = (f.parity_words(stars, support) if law == "parity"
                      else f.nae_words(solver, support))
            if len(support) < 3 or actual != f.expected_words(law, len(support)):
                rejected.append(holder)
            else:
                f.canonical_relation(law, len(support))
    return {"lawful": not rejected, "rejected_holder_projections": rejected}


def cut_plan(stars, law, age):
    f = fixture()
    end = f.from_stars(stars)
    if age < HORIZON:
        plan = f.step(end, law, max_births=BIRTH_CAP)
        return {"status": plan.status, "parents": plan.parents, "fresh": plan.fresh,
                "shortages": plan.shortages, "birth_count_lower": plan.planned_births_lower,
                "implied": plan.implied}
    # At the last materialized cut classify its next funding from the actual
    # proposals. Their fresh counts would require a further complete lookahead.
    operator = sys.modules["end_operator"]
    if not end.opens:
        return {"status": "closed"}
    try:
        multi = operator._proposals(end, BIRTH_CAP)
    except operator._Cap:
        return {"status": "cap", "birth_count_lower": BIRTH_CAP + 1}
    used = Counter(k for row in multi for k in row)
    shortages = [(k, used[k] - avail) for k, avail in end.opens.items() if used[k] > avail]
    if shortages:
        return {"status": "stall", "shortages": shortages}
    births = len(multi) + sum(n - used[k] for k, n in end.opens.items())
    return {"status": "extend" if births <= BIRTH_CAP else "cap", "planned_births": births,
            "implied": births == 1 and law == "parity"}


def literal(stars, law):
    frames = [stars]
    layers = []
    plans = []
    while len(frames) <= HORIZON + 1:
        current = frames[-1]
        plan = cut_plan(current, law, len(frames) - 1)
        plans.append(plan)
        if len(frames) > HORIZON or plan["status"] != "extend":
            break
        status, births, _ = fixture().literal_turn(current, law)
        assert status == plan["status"]
        assert tuple(b.parents for b in births) == plan["parents"]
        assert tuple(len(b.fresh) for b in births) == plan["fresh"]
        layers.append(births)
        frames.append(current + tuple(b.support for b in births))
    return frames, layers, plans


def pair_query(loose, seed):
    rng = Random(seed)
    holders = tuple(sorted(rng.sample(sorted(loose), 2)))
    markers = tuple(loose[k][rng.randrange(len(loose[k]))] for k in holders)
    return holders, markers


def fraction_record(x):
    return [x.numerator, x.denominator]


def nae_value(total, signed):
    correlation = Fraction(signed, total)
    disagreement = (1 - correlation) / 2
    assert total > 0 and -1 <= correlation <= 1 and (total - signed) % 2 == 0
    return {
        "status": "exact", "total_words": total, "signed_sum": signed,
        "disagreement_rate": fraction_record(disagreement),
        "correlation": fraction_record(correlation), "far": abs(correlation) <= NAE_FAR,
        "disagreement_bin": "below_half" if signed > 0 else "above_half" if signed < 0 else "half",
    }


def tree_transfer(stars, holders, ordinary):
    route = nx.shortest_path(ordinary, *holders)
    return Fraction((-1) ** len(route),
                    prod(2 ** (len(stars[v]) - 1) - 1 for v in route))


def small_exact_words(stars, marks):
    names = sorted({d for row in stars for d in row})
    index = {d: 1 << j for j, d in enumerate(names)}
    masks = [sum(index[d] for d in row) for row in stars]
    a, b = (index[d] for d in marks)
    total = signed = 0
    for value in range(1 << len(names)):
        if all(0 < value & mask < mask for mask in masks):
            total += 1
            signed += -1 if bool(value & a) != bool(value & b) else 1
    return total, signed


def nae_plan(stars, newest):
    counter = Counter(exact_engine().owners(stars).values())
    return exact_engine().Elimination(counter, len(stars), newest)


def reusable_contraction(plan, holders, *, control=False):
    a, b = [plan.scope_lookup[(v,)] for v in holders]
    baseline_work = sum(op.volume * len(op.inputs) for op in plan.operations)
    work = baseline_work + plan.work((a, b))
    largest = max(op.volume for op in plan.operations)
    if work > TERM_CAP or largest > TENSOR_CAP:
        return None, None, work, largest
    if not hasattr(plan, "total_words"):
        plan.total_words = plan.contract()
    signed = plan.contract(plan.changes(a, b))
    total = plan.total_words
    if control:
        # Pin the actual two private bits directly. Scaling each pin by two
        # permits integer factors, even when the holder label is unrestricted.
        zero = np.array((1, 2, 0), dtype=object)
        one = np.array((1, 0, 2), dtype=object)
        n00 = plan.contract({a: zero, b: zero})
        n01 = plan.contract({a: zero, b: one})
        assert n00 + n01 == 2 * total and n00 - n01 == 2 * signed
    return total, signed, work, largest


def nae_distance(stars, holders, marks, ordinary, loose, newest):
    plan = nae_plan(stars, newest)
    total, signed, work, largest = reusable_contraction(plan, holders)
    a, b = (len(loose[v]) for v in holders)
    bound = Fraction(1, (2 ** a - 1) * (2 ** b - 1))
    evidence = {"absolute_correlation_upper": fraction_record(bound),
                "baseline_plus_signed_term_bound": work, "largest_tensor": largest}
    if total is None:
        return {**evidence, "status": "bounded", "far": True if bound <= NAE_FAR else None,
                "disagreement_interval": [fraction_record((1 - bound) / 2),
                                          fraction_record((1 + bound) / 2)],
                "disagreement_bin": "unknown"}
    result = nae_value(total, signed)
    assert abs(Fraction(signed, total)) <= bound
    if nx.is_tree(ordinary) and sum(ordinary.degree(v) + len(loose.get(v, ())) == len(row)
                                    for v, row in enumerate(stars)) == len(stars):
        assert Fraction(signed, total) == tree_transfer(stars, holders, ordinary)
        evidence["independent_tree_transfer_check"] = True
    if len({d for row in stars for d in row}) <= 12:
        assert small_exact_words(stars, marks) == (total, signed)
        evidence["independent_allowed_word_check"] = True
    return {**evidence, **result}


def wired_graph(owners, size):
    exterior = size
    graph = nx.Graph()
    graph.add_nodes_from(range(size + 1))
    for a, b in (vs if len(vs) == 2 else (vs[0], exterior) for vs in owners.values()):
        old_capacity = graph[a][b]["capacity"] if graph.has_edge(a, b) else 0
        graph.add_edge(a, b, capacity=old_capacity + 1)
    assert nx.is_connected(graph)
    return graph, exterior


def cut_cost(graph, part):
    return nx.cut_size(graph, part, weight="capacity")


def relaxed_cut(graph, exterior, required):
    auxiliary = graph.copy()
    force = exterior + 1
    wall = 1 + sum(d["capacity"] for _, _, d in graph.edges(data=True))
    auxiliary.add_edges_from((force, v, {"capacity": wall}) for v in required)
    value, (inside, outside) = nx.minimum_cut(auxiliary, force, exterior, capacity="capacity")
    inside.remove(force)
    assert required <= inside and exterior in outside and cut_cost(graph, inside) == value
    return value, inside


def repair_outer_shore(graph, exterior, inside):
    outside = nx.node_connected_component(graph.subgraph(set(graph) - inside), exterior)
    repaired = set(graph) - outside
    assert nx.is_connected(graph.subgraph(repaired))
    return repaired


def connected_cut_search(graph, exterior, holders, ordinary, floor):
    full = set(graph) - {exterior}
    direct = set(nx.shortest_path(ordinary, *holders))
    path = repair_outer_shore(graph, exterior, direct)
    best, witness = min((cut_cost(graph, shore), sorted(shore)) for shore in (path, full))
    serial = count()
    seeds = frozenset(holders)
    queue = [(floor, next(serial), seeds)]
    seen = {seeds}
    tried = 0
    while queue and queue[0][0] < best and tried < BOND_CAP:
        _, _, forced = heappop(queue)
        lower, inside = relaxed_cut(graph, exterior, forced)
        tried += 1
        if lower >= best:
            continue
        parts = list(nx.connected_components(graph.subgraph(inside)))
        if len(parts) == 1:
            assert nx.is_connected(graph.subgraph(set(graph) - inside))
            best, witness = lower, sorted(inside)
            continue
        candidates = []
        for part in parts:
            assert part & forced
            exits = set().union(*(graph[v] for v in part)) - inside - {exterior}
            candidates.append(tuple(sorted(exits)))
        for v in min(candidates, key=lambda row: (len(row), row)):
            mandatory = forced | {v}
            if mandatory not in seen:
                seen.add(mandatory)
                heappush(queue, (lower, next(serial), mandatory))
    lower = min(best, queue[0][0]) if queue else best
    return lower, best, witness, tried


def exhaustive_cut(graph, exterior, holders):
    pins = set(holders)
    others = sorted(set(graph) - pins - {exterior})
    return min(cut_cost(graph, side)
               for mask in range(1 << len(others))
               for side in [pins | {v for i, v in enumerate(others) if mask >> i & 1}]
               if nx.is_connected(graph.subgraph(side))
               and nx.is_connected(graph.subgraph(set(graph) - side)))


def parity_distance(owners, ordinary, holders, loose):
    total_loose = sum(map(len, loose.values()))
    if total_loose == 2:
        if len(ordinary) <= 12:
            graph, exterior = wired_graph(owners, len(ordinary))
            assert exhaustive_cut(graph, exterior, holders) == 2
        return {"status": "no_canonical_bond", "bond_distance": "infinity", "far": True,
                "algebraic_minimal_cut_size": 2, "pair_disagreement_rate": [0, 1],
                "independent_cut_census": len(ordinary) <= 12}
    graph, exterior = wired_graph(owners, len(ordinary))
    floor = sum(len(loose[v]) for v in holders)
    lower, upper, witness, nodes = connected_cut_search(graph, exterior, holders, ordinary, floor)
    assert upper >= 3 and set(holders) <= set(witness)
    brute = len(ordinary) <= 12
    if brute:
        assert lower == upper == exhaustive_cut(graph, exterior, holders)
    return {"status": "exact" if lower == upper else "bounded",
            "bond_distance": upper - 1 if lower == upper else None,
            "bond_distance_interval": [lower - 1, upper - 1], "cut_nodes": nodes,
            "connected_upper_shore": witness, "independent_cut_census": brute,
            "pair_disagreement_rate": [1, 2],
            "far": True if lower - 1 >= PARITY_FAR else False if upper - 1 < PARITY_FAR else None}


def descendant_check(layers, age, holders, predicted):
    left, right = map(lambda v: {v}, holders)
    for delay, layer in enumerate(layers[age:], 1):
        left = {b.knot for b in layer if left.intersection(b.parents)}
        right = {b.knot for b in layer if right.intersection(b.parents)}
        joint = sorted(left & right)
        if joint:
            assert delay == predicted
            return {"delay": delay, "knots": joint}
    assert predicted is None or predicted > len(layers) - age
    return None


def row_at(arm, stars, layers, law, age, plan, seed):
    f = fixture()
    owners, ordinary, loose = f.incidence(stars)
    _, witnessed = f.witnessed_end(ordinary, loose)
    if age:
        layer = layers[age - 1]
        actual = [(b.knot, b.parents, b.inputs, b.fresh) for b in layer]
    else:
        actual = []
    result = {"age": age, "reached": True, "next_step": plan, "query": None,
              "current_loose": loose, "actual_births": actual,
              "witnessed_parts": sorted(tuple(sorted(s)) for s in nx.connected_components(witnessed))}
    if len(loose) < 2:
        result["query_unavailable"] = "fewer_than_two_live_knots"
        return result
    holders, marks = pair_query(loose, seed)
    separation = nx.shortest_path_length(witnessed, *holders) if nx.has_path(witnessed, *holders) else None
    funded = plan["status"] == "extend"
    actual_never = (True if separation is None or plan["status"] == "stall"
                    else False if funded else None)
    delay = separation if actual_never is False else None
    state = (parity_distance(owners, ordinary, holders, loose) if law == "parity"
             else nae_distance(stars, holders, marks, ordinary, loose, sorted(loose) if age else ()))
    if arm == "partnered":
        assert separation in (1, 2) and funded and state["far"] is True
    result["query"] = {"query_seed": seed, "holders": holders, "marks": marks,
                       "ordinary_holder_steps": nx.shortest_path_length(ordinary, *holders),
                       "witnessed_separation": separation, "structurally_separate": separation is None,
                       "actual_never": actual_never, "funded_delay": delay,
                       "literal_first_common_descendant": descendant_check(layers, age, holders, delay),
                       "soon": delay <= 1 if delay is not None else None if actual_never is None else False,
                       "within_two": delay <= 2 if delay is not None else None if actual_never is None else False,
                       "state": state}
    return result


def show_trial(arm, index, raw, seeds):
    source = physical_source(arm, raw)
    by_law = {}
    for law in LAWS:
        gate = source_gate(source, law)
        rows = []
        if gate["lawful"]:
            frames, layers, plans = literal(source, law)
            rows = [row_at(arm, stars, layers, law, age, plans[age], seeds[arm, index, age])
                    for age, stars in enumerate(frames)]
        reason = rows[-1]["next_step"]["status"] if rows else "unlawful_source"
        rows.extend({"age": age, "reached": False, "query": None, "query_unavailable": reason}
                    for age in range(len(rows), HORIZON + 1))
        by_law[law] = {"origin_gate": gate, "cuts": rows}
    return {"draw": index, "input": raw, "original_stars": source, "by_law": by_law}


@cache
def partner_masks():
    counts = [6]
    rosters = {}
    excluded = {1: ()}
    for age in range(1, 5):
        prior = counts[-1]
        everything = (1 << (prior // 2)) - 1
        blocked = set(excluded[age])
        assert blocked == {mask ^ everything for mask in blocked}
        representatives = [mask for mask in range((everything + 1) // 2) if mask not in blocked]
        rosters[age] = tuple(mask for a in representatives for mask in (a, a ^ everything))
        counts.append(len(rosters[age]))
        if age < 4:
            excluded[age + 1] = tuple(sorted({
                sum(1 << i for i, mask in enumerate(representatives) if (mask >> (v // 2) & 1) != v % 2)
                for v in range(prior)
            }))
            assert len(excluded[age + 1]) == prior
    assert counts == [6, 8, 10, 24, 4086]
    return counts, rosters, excluded


def mask_parents(mask, previous):
    return frozenset(previous[2 * i + (mask >> i & 1)] for i in range(len(previous) // 2))


def index_partner_births(layers):
    counts, rosters, _ = partner_masks()
    previous = tuple(range(counts[0]))
    indices = [previous]
    for age, births in enumerate(layers, 1):
        by_parents = {frozenset(b.parents): b for b in births}
        assert len(by_parents) == counts[age]
        previous = tuple(by_parents[mask_parents(mask, previous)].knot for mask in rosters[age])
        indices.append(previous)
    return indices


def orbit_starts(layers, youngest):
    automorphisms = []
    for flips in range(8):
        mapping = {v: v ^ (flips >> (v // 2) & 1) for v in range(6)}
        for layer in layers:
            by_parents = {frozenset(b.parents): b.knot for b in layer}
            mapping = {b.knot: by_parents[frozenset(mapping[v] for v in b.parents)] for b in layer}
        automorphisms.append(mapping)
    remaining = set(combinations(youngest, 2))
    while remaining:
        a, b = min(remaining)
        orbit = {tuple(sorted((m[a], m[b]))) for m in automorphisms}
        remaining -= orbit
        yield (a, b), sorted(orbit)


def partner_exact_control():
    """Full current-pair table, reduced only by physical within-partner swaps."""
    source = physical_source("partnered", {"orientations": (0,) * len(PARTNER_PAIRS)})
    f = fixture()
    frames, layers, _ = literal(source, "nae")
    prior = index_partner_births(layers)
    canonical = {}
    for age in (1, 2):
        frame = frames[age]
        newest = tuple(sorted(prior[age]))
        plan = nae_plan(frame, newest)
        table = []
        for pair, orbit in orbit_starts(layers[:age], newest):
            total, signed, _, _ = reusable_contraction(plan, pair, control=not table)
            assert total is not None
            table.append({"members": orbit, **nae_value(total, signed)})
        assert sum(len(row["members"]) for row in table) == len(newest) * (len(newest) - 1) // 2
        canonical[age] = {"all_current_pairs": table, "explicit_pin_recount_on_first_orbit": True}
    # This verifies the exact age-four roster population without materializing
    # the enormous loose holdings that it will require.
    named_law_checks = {}
    _, rosters, _ = partner_masks()
    for law in LAWS:
        early, before, _ = literal(source, law)
        status, age_three, _ = f.literal_turn(early[-1], law)
        assert status == "extend" and len(age_three) == 24
        age_three_stars = early[-1] + tuple(b.support for b in age_three)
        ordered = index_partner_births([*before, age_three])[-1]
        proposals = sys.modules["end_operator"].proposals(f.from_stars(age_three_stars))
        assert set(map(frozenset, proposals)) == {mask_parents(mask, ordered) for mask in rosters[4]}
        named_law_checks[law] = {"third_rosters": len(age_three), "fourth_rosters": len(proposals)}
    return {"physical_source": source, "age_one_and_two_nae_tables": canonical,
            "literal_deep_roster_check_by_law": named_law_checks}


def at_four():
    counts, rosters, exclude = partner_masks()
    ordered = sorted(rosters[4])
    population = counts[4]
    fresh = (2 ** (population // 2) - counts[3]) // 2
    rng = Random(SEEDS["age_four"])
    bound = Fraction(1, 4095 ** 2)
    outputs = []
    for i in range(N):
        a, b = sorted(rng.sample(range(population), 2))
        masks = (ordered[a], ordered[b])
        marks = (rng.randrange(fresh), rng.randrange(fresh))
        assert all(mask not in exclude[4] for mask in masks)
        paired = masks[0] ^ masks[1] == (1 << (counts[3] // 2)) - 1
        outputs.append({"orientation_draw": i, "birth_ranks": (a, b), "transversal_masks": masks,
                        "private_mark_ranks": marks, "witnessed_separation": 2 if paired else 1,
                        "soon": not paired, "within_two": True,
                        "actual_never": False, "structurally_separate": False})
    return {"age": 4, "all_witnessed_populations_to_current_cut": counts, "pair_population": population,
            "excluded_transversal_masks": exclude[4], "loose_per_holder": fresh,
            "exact_uniform_soon_probability": fraction_record(Fraction(population - 2, population - 1)),
            "state_by_law": {
                "parity": {"status": "bounded", "bond_distance_interval": (2 * fresh - 1, population * fresh - 1),
                           "far": True, "pair_disagreement_rate": [1, 2]},
                "nae": {"status": "bounded", "disagreement_bin": "unknown",
                        "absolute_correlation_upper": fraction_record(bound),
                        "disagreement_interval": [fraction_record((1 - bound) / 2),
                                                  fraction_record((1 + bound) / 2)],
                        "far": True}},
            "draws": outputs, "shares_in_both_laws": {
                outcome: summarized(outputs, lambda q: q[outcome])
                for outcome in ("soon", "within_two", "actual_never", "structurally_separate")}}


def clopper_pearson(k, n):
    if n == 0:
        return [None, None]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n + 1 - k)),
            1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def summarized(rows, event, group=lambda _: True):
    members = [event(q) for q in rows if group(q) is True]
    maybe = [event(q) for q in rows if group(q) is None]
    known = Counter(members)
    n = len(members)
    yes = known[True]
    low_n = n + sum(value is not True for value in maybe)
    low = yes
    extra_high = sum(value is not False for value in maybe)
    high_n = n + extra_high
    high = yes + known[None] + extra_high
    if not low_n and maybe:
        low, low_n = 1, 1
    if not high_n and maybe:
        high, high_n = 0, 1
    return {"certain_denominator": n, "possible_extra_denominator": len(maybe), "yes": yes,
            "no": known[False], "unresolved_among_certain": known[None],
            "proportion_envelope": [low / low_n if low_n else None, high / high_n if high_n else None],
            "marginal_exact_95_endpoint_envelope": [
                clopper_pearson(low, low_n)[0], clopper_pearson(high, high_n)[1]],
            "inference_uses_certain_and_possible_endpoint_assignments": True}


def both(a, b):
    return False if a is False or b is False else None if a is None or b is None else True


def exact_ruler(law, row):
    state = row["state"]
    if law == "parity":
        value = state["bond_distance"]
        return str(value) if value is not None else "unresolved"
    if state["status"] == "exact":
        a, b = state["disagreement_rate"]
        return f"{a}/{b}"
    return "unresolved"


def broad_rates(cuts):
    def event(cut, key):
        q = cut["query"]
        if q is None:
            return None if cut.get("query_unavailable") == "cap" else False
        if key == "far_and_soon":
            return both(q["state"]["far"], q["soon"])
        return q[key]
    return {key: summarized(cuts, lambda cut: event(cut, key))
            for key in ("structurally_separate", "actual_never", "soon", "within_two", "far_and_soon")}


def summary_for(draws, law, age):
    cuts = [r["by_law"][law]["cuts"][age] for r in draws]
    lawful_cuts = [r["by_law"][law]["cuts"][age] for r in draws if r["by_law"][law]["origin_gate"]["lawful"]]
    reached = [c for c in cuts if c["reached"]]
    available = [c["query"] for c in reached if c["query"] is not None]
    funded = [c["query"] for c in reached if c["next_step"]["status"] == "extend"
              and c["query"] is not None]
    all_groups = {}
    for name, source in (("query_eligible", available), ("query_eligible_funded", funded)):
        events = {key: summarized(source, lambda q: q[key])
                  for key in ("structurally_separate", "actual_never", "soon", "within_two")}
        events["far"] = summarized(source, lambda q: q["state"]["far"])
        for label in ("soon", "within_two"):
            events[f"far_and_{label}"] = summarized(source, lambda q: both(q["state"]["far"], q[label]))
            events[f"{label}_given_far"] = summarized(source, lambda q: q[label], lambda q: q["state"]["far"])
            events[f"far_given_{label}"] = summarized(source, lambda q: q["state"]["far"], lambda q: q[label])
        groups = {}
        for key in ("far", "near", "far_unresolved"):
            selected = [q for q in source if q["state"]["far"] is
                        {"far": True, "near": False, "far_unresolved": None}[key]]
            if selected:
                groups[key] = selected
        if law == "nae":
            for key in sorted({q["state"]["disagreement_bin"] for q in source}):
                groups[f"raw:{key}"] = [q for q in source if q["state"]["disagreement_bin"] == key]
        for key in sorted({exact_ruler(law, q) for q in source}):
            groups[f"exact:{key}"] = [q for q in source if exact_ruler(law, q) == key]
        strata = {key: {outcome: summarized(selected, lambda q: q[outcome])
                        for outcome in ("actual_never", "structurally_separate", "soon", "within_two")}
                  for key, selected in groups.items()}
        all_groups[name] = {"outcomes": events, "by_state": strata,
                           "delay_counts": Counter(str(q["funded_delay"]) for q in source),
                           "state_status_counts": Counter(q["state"]["status"] for q in source)}
    return {"all_start_draws": len(draws), "lawful_origins": len(lawful_cuts), "cuts_reached": len(reached),
            "query_eligible": len(available), "query_eligible_funded": len(funded),
            "state_readings_resolved": sum(q["state"]["status"] != "bounded" for q in available),
            "far_decisions_resolved": sum(q["state"]["far"] is not None for q in available),
            "arrival_decisions_resolved": sum(q["actual_never"] is not None for q in available),
            "compound_event_from_all_starts": broad_rates(cuts),
            "compound_event_from_lawful_starts": broad_rates(lawful_cuts),
            "next_step_status_among_reached": Counter(c["next_step"]["status"] for c in reached),
            "no_query_reasons": Counter(c.get("query_unavailable", "none") for c in cuts if not c["query"]),
            "eligibility_cp95_over_all_starts": clopper_pearson(len(available), len(draws)),
            "funded_query_cp95_over_all_starts": clopper_pearson(len(funded), len(draws)),
            "rates": all_groups}


def run(arm):
    seeds = query_seeds()
    evidence = [show_trial(arm, i, raw, seeds) for i, raw in enumerate(draw_inputs(arm))]
    if arm == "partnered":
        for draw in evidence:
            for law in LAWS:
                rows = draw["by_law"][law]["cuts"]
                assert [len(row["current_loose"]) for row in rows] == [6, 8, 10]
                assert [set(map(len, row["current_loose"].values())) for row in rows] == [{4}, {5}, {12}]
    sources = (Path(__file__).resolve(), FIXTURES, RATES, PARTNER_PROOF, HERE / "contract.json", PREREG)
    results = {
        "arm": arm, "scored_ages": tuple(range(HORIZON + 1)), "seed_map": SEEDS, "draws": evidence,
        "limits": {"birth_cap": BIRTH_CAP, "cut_search_nodes": BOND_CAP, "tensor_terms": TERM_CAP,
                   "tensor_entries": TENSOR_CAP},
        "summaries": {law: {age: summary_for(evidence, law, age) for age in range(HORIZON + 1)}
                      for law in LAWS},
        "sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sources},
    }
    if arm == "partnered":
        results["actual_deep_draws"] = at_four()
        results["independent_literal_partner_control"] = partner_exact_control()
    return results


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--arm", choices=ARMS, required=True)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    record = json.dumps(run(args.arm), separators=(",", ":"), sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(record)
    else:
        print(record, end="")


if __name__ == "__main__":
    main()
