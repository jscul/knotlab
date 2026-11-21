"""Measure physical ring turns and verify the formulas for the two records."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from math import comb, lcm
from pathlib import Path
from typing import NamedTuple
import json
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / "research" / HERE.parent.name
FIXTURE = ROOT / ("experiments/GENERATORS-20261120-001A/"
                  "GENERATORS-20261120-001A-E001_generators/fixtures.py")
ARCHIVE = ROOT / ("artifacts/FOUR-READINGS-20261120-001D/"
                  "FOUR-READINGS-20261120-001D-E001_unbuilt_sources/explosive.json")
LAWS = ("parity", "nae")
HORIZON = 32
CAP = 128


@cache
def fixture():
    spec = spec_from_file_location("ring_clock_fixtures", FIXTURE)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Winding:
    holders: tuple[int, ...]
    extras: tuple[int, ...]
    hung: int | None = None
    hung_gap: int | None = None


class Cluster(NamedTuple):
    phase: int
    originals: int
    selected: tuple[tuple[str, int, int], ...]


def rings_on(holders, extras, hung_host=None, hung=None):
    n = len(holders)
    length = n if n % 2 else n // 2
    for phase in range(n // length):
        order = tuple(holders[(phase + 2 * i) % n] for i in range(length))
        marker = tuple(extras.get(v, 0) for v in order)
        gap = None
        if hung_host is not None:
            preceding = holders[(hung_host - 1) % n]
            following = holders[(hung_host + 1) % n]
            if preceding in order:
                gap = order.index(following)
                assert order[(gap - 1) % length] == preceding
        yield Winding(order, marker, hung if gap is not None else None, gap)


def starting_stars(meetings, extras):
    neighbors = nx.Graph(meetings)
    count = len(neighbors)
    assert set(neighbors) == set(range(count))
    openings = [sum(neighbors.degree(w) - 1 for w in neighbors[v]) + extras.get(v, 0)
                for v in range(count)]
    return fixture().source_from(meetings, openings)


def attached_ring(n, marks, hung_host=None):
    extras = dict.fromkeys(marks, 1)
    link = [(i, (i + 1) % n) for i in range(n)]
    stars = starting_stars(link, extras)
    if hung_host is not None:
        old = stars
        next_name = max(d for support in old for d in support) + 1
        grown = [list(row) for row in old]
        grown[hung_host].append(next_name)
        grown[(hung_host - 1) % n].append(next_name + 1)
        grown[(hung_host + 1) % n].append(next_name + 2)
        grown.append([next_name, next_name + 3, next_name + 4])
        stars = tuple(map(tuple, grown))
        assert all(row[:len(before)] == before for before, row in zip(old, stars[:n], strict=True))
    return stars, tuple(rings_on(tuple(range(n)), extras, hung_host, n))


def joined_rings(bridge_length):
    first, second = tuple(range(5)), tuple(range(5, 12))
    extras = {0: 1, 5: 1}
    path = (2, *range(12, 11 + bridge_length), 8)
    meetings = [*zip(first, first[1:] + first[:1], strict=True),
                *zip(second, second[1:] + second[:1], strict=True), *zip(path, path[1:])]
    return starting_stars(meetings, extras), tuple([*rings_on(first, extras), *rings_on(second, extras)])


@cache
def available(winding, phase, length):
    period = len(winding.holders)
    spares = [("leftover", i, k) for i in range(length)
              for k in range(winding.extras[(phase + i) % period])]
    hungs = [("hung", i, 0) for i in range(length + 1)
             if (phase + i) % period == winding.hung_gap]
    return tuple(sorted(spares + hungs))


def blocked_end(option, length):
    kind, offset, _ = option
    if offset == 0:
        return 0
    if kind == "leftover" and offset == length - 1 or kind == "hung" and offset == length:
        return 1
    return None


def model_cohort(winding, size):
    if size == 1 and winding.hung is not None:
        yield Cluster(0, 0, ())
    for phase in range(len(winding.holders)):
        for length in range(1, size + 1):
            for chosen in combinations(available(winding, phase, length), size - length):
                yield Cluster(phase, length, chosen)


def model_parents(winding, cluster):
    phase, length, chosen = cluster
    parents = [Cluster(phase, length, tuple(x for x in chosen if x != removed))
               for removed in chosen]
    if length == 1:
        if len(chosen) == 1 and chosen[0][0] == "hung":
            parents.append(Cluster(0, 0, ()))
    elif length >= 2:
        occupied_ends = {blocked_end(option, length) for option in chosen}
        if 0 not in occupied_ends:
            parents.append(Cluster((phase + 1) % len(winding.holders), length - 1,
                                   tuple((kind, pos - 1, k) for kind, pos, k in chosen)))
        if 1 not in occupied_ends:
            parents.append(Cluster(phase, length - 1, chosen))
    assert len(set(parents)) == len(parents)
    return parents


def model_fresh(winding, cluster):
    phase, length, chosen = cluster
    return 2 + len(available(winding, phase, length)) - len(chosen) if length else 2


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def count_profile(winding, age):
    """Count by parents and fresh distinctions without listing every subset."""
    size = age + 1
    counts = Counter()
    for phase in range(len(winding.holders)):
        for length in range(1, size + 1):
            options = available(winding, phase, length)
            taken = size - length
            if taken > len(options):
                continue
            fresh = 2 + len(options) - taken
            if length == 1:
                hung = sum(kind == "hung" for kind, _, _ in options)
                assert hung <= 1
                spares = len(options) - hung
                counts[(taken, fresh)] += choose(spares, taken)
                if hung and taken:
                    counts[(2 if taken == 1 else taken, fresh)] += choose(spares, taken - 1)
                continue
            endpoints = Counter(blocked_end(option, length) for option in options)
            for first in range(endpoints[0] + 1):
                for last in range(endpoints[1] + 1):
                    selected_ends = int(first > 0) + int(last > 0)
                    multiplicity = (comb(endpoints[0], first) * comb(endpoints[1], last)
                                    * choose(endpoints[None], taken - first - last))
                    counts[(2 + taken - selected_ends, fresh)] += multiplicity
    return +counts


def observables(histogram):
    return {"births": sum(histogram.values()),
            "two_parent_births": sum(count for (p, _), count in histogram.items() if p == 2),
            "maximum_arity": max(p + f for p, f in histogram),
            "maximum_parents": max(p for p, _ in histogram)}


def least_period(word):
    return next(p for p in range(1, len(word) + 1)
                if all(value == word[(i + p) % len(word)] for i, value in enumerate(word)))


def clean_two_count(winding, age):
    w = winding.extras
    length = len(w)
    if age == 1:
        return length
    if age == 2:
        return length + 2 * sum(w) + sum(comb(x, 2) for x in w)
    return length + 2 * sum(w) + sum(value * w[(i + age - 2) % length]
                                     for i, value in enumerate(w))


def attached_two_count(winding, age):
    if winding.hung is None:
        return clean_two_count(winding, age)
    n = len(winding.holders)
    if age == 1:
        return n + 2
    if age == 2:
        return n + 2 + 2 * sum(winding.extras)
    gap = winding.hung_gap
    left = [a + int(i == gap) for i, a in enumerate(winding.extras)]
    right = [a + int((i + 1) % n == gap) for i, a in enumerate(winding.extras)]
    return n + 2 + 2 * sum(winding.extras) + sum(a * right[(i + age - 2) % n]
                                                for i, a in enumerate(left))


def max_run_weight(weights, length):
    n = len(weights)
    turns, remaining = divmod(length, n)
    return turns * sum(weights) + max(sum(weights[j % n] for j in range(i, i + remaining))
                                      for i in range(n))


def recurrence_from_weights(winding, age):
    weights = winding.extras
    max_parent = max([2] + [k + 2 for k in range(1, age) if
                          max_run_weight(weights, age - k - 1) >= k])
    return 4 + max_run_weight(weights, age + 1), max_parent


def impulse(cluster):
    phase, length, chosen = cluster
    return length >= 2 and chosen == (("leftover", 0, 0), ("leftover", length - 1, 0))


def analytic_panel(windings):
    observations = []
    for age in range(1, HORIZON + 1):
        profiles = [count_profile(winding, age) for winding in windings]
        row = observables(sum(profiles, Counter()))
        assert row["two_parent_births"] == sum(attached_two_count(w, age) for w in windings)
        for w, profile in zip(windings, profiles, strict=True):
            if w.hung is None:
                by_piece = observables(profile)
                assert (by_piece["maximum_arity"], by_piece["maximum_parents"]) == recurrence_from_weights(w, age)
        observations.append({"age": age, **row})
    period = lcm(*(len(w.holders) for w in windings))
    tail = tuple(sum(attached_two_count(w, age) for w in windings)
                 for age in range(3, 3 + period))
    if all(w.hung is None for w in windings):
        assert least_period(tail) == lcm(*(least_period(w.extras) for w in windings))
    return {"profile": observations, "eventual_two_parent_profile": tail,
            "eventual_two_parent_least_period": least_period(tail)}


def recovered_origin(stars):
    drops = 0
    while stars:
        _, ordinary, loose = fixture().incidence(stars)
        live = set(loose)
        if any(live.intersection(ordinary[v]) for v in live):
            return stars, drops
        assert live
        stars = tuple(row for v, row in enumerate(stars) if v not in live)
        drops += 1
    raise AssertionError("the physical original boundary disappeared")


def collect_model_labels(winding):
    names = {Cluster(phase, 1, ()): holder for phase, holder in enumerate(winding.holders)}
    if winding.hung is not None:
        names[Cluster(0, 0, ())] = winding.hung
    return names


def physical_end_profile(stars, births):
    physical = fixture()
    _, ordinary, loose = physical.incidence(stars)
    witnessed = physical.from_stars(stars)
    counts = Counter(v for row in witnessed.blocks for v in row)
    assert set(loose) == {birth.knot for birth in births}
    observed = Counter((counts[v], len(loose[v])) for v in loose)
    for birth in births:
        assert set(ordinary[birth.knot]) == set(birth.parents)
        assert counts[birth.knot] == len(birth.parents)
        assert len(stars[birth.knot]) == len(birth.parents) + len(birth.fresh)
    return observables(observed)


def advance_indices(winding, old, by_roster, age, whole):
    current = {}
    histogram = Counter()
    exact_model_fresh = True
    physical_impulses = []
    for cluster in model_cohort(winding, age + 1):
        parents = frozenset(old[c] for c in model_parents(winding, cluster))
        born = by_roster[parents]
        assert born.knot not in current.values()
        current[cluster] = born.knot
        immutable_inputs = len(born.inputs)
        assert immutable_inputs == len(parents)
        fresh = len(born.fresh)
        exact_model_fresh &= fresh == model_fresh(winding, cluster)
        histogram[(immutable_inputs, fresh)] += 1
        if sum(winding.extras) == 1 and impulse(cluster):
            assert immutable_inputs == 2
            physical_impulses.append(born.knot)
    if whole:
        assert exact_model_fresh
    return current, histogram, physical_impulses, exact_model_fresh


def literal_panel(source, windings, law, *, complete=True, horizon=HORIZON):
    physical = fixture()
    physical.certify_source(source, law)
    states = [source]
    indices = [tuple(collect_model_labels(w) for w in windings)]
    all_rows = []
    for age in range(1, horizon + 1):
        stars = states[-1]
        plan = physical.step(physical.from_stars(stars), law, max_births=CAP)
        if plan.status == "cap":
            break
        assert plan.status == "extend" and not plan.implied
        _, births, _ = physical.literal_turn(stars, law)
        frames = stars + tuple(birth.support for birth in births)
        states.append(frames)
        assert plan.parents == tuple(birth.parents for birth in births)
        by_roster = {frozenset(birth.parents): birth for birth in births}
        assert len(by_roster) == len(births) <= CAP
        track_ids, histograms, rows = [], [], []
        for winding, old in zip(windings, indices[-1], strict=True):
            fresh, hist, ticks, stable = advance_indices(winding, old, by_roster, age, complete)
            row = observables(hist)
            row["both_ends_selected_leftovers"] = ticks
            row["all_fresh_counts_equal_isolated"] = stable
            track_ids.append(fresh)
            histograms.append(hist)
            rows.append(row)
        indices.append(tuple(track_ids))
        witnessed = physical_end_profile(frames, births)
        literal = observables(Counter((len(b.parents), len(b.fresh)) for b in births))
        assert literal == witnessed
        if complete:
            assert literal == observables(sum(histograms, Counter()))
        original, discovered = recovered_origin(frames)
        assert original == source and discovered == age
        _, ordinary, _ = physical.incidence(frames)
        distance = nx.multi_source_dijkstra_path_length(ordinary, range(len(source)))
        assert all(distance[birth.knot] == age for birth in births)
        all_rows.append({"age": age, "whole_cut": literal, "selected_windings": rows,
                         "witnessed_end_recovers_whole_count_and_records": True,
                         "age_recovered_without_supplied_count": discovered})

    renamed, _ = physical.rename(states[-1], 20261120426)
    original, age_from_holdings = recovered_origin(renamed)
    assert age_from_holdings == len(all_rows)
    assert sorted(map(len, original)) == sorted(map(len, source))
    return {
        "through": len(all_rows),
        "full_origin_recovered_after_independent_knot_and_distinction_renaming": True,
        "complete_replay": len(all_rows) == horizon,
        "rows": all_rows,
    }, states, indices


def rooted_chart(stars, root, radius):
    owners, ordinary, loose = fixture().incidence(stars)
    reached = nx.single_source_shortest_path_length(ordinary, root, cutoff=radius)
    chart = nx.Graph()
    for holder in reached:
        holder_role = ("knot", holder)
        chart.add_node(holder_role, color=(
            "knot", holder == root, len(stars[holder]), len(loose.get(holder, ()))))
        for bit in stars[holder]:
            distinction_role = ("distinction", bit)
            chart.add_node(distinction_role, color=("distinction", len(owners[bit])))
            chart.add_edge(holder_role, distinction_role)
    return chart


def possible_ages(period, total_arity, parents):
    feasible = set()
    for blocked in range(3):
        available_count = total_arity - 4 + blocked
        selected_count = parents - 2 + blocked
        if not 0 <= blocked <= selected_count <= available_count:
            continue
        minimum = max(2, (available_count - 1) * period + 1)
        maximum = (available_count + 1) * period - 1
        for length in range(minimum, maximum + 1):
            for phase in range(period):
                actual = (phase + length - 1) // period - (phase - 1) // period
                if actual != available_count:
                    continue
                eligible_ends = int(phase == 0) + int((phase + length - 1) % period == 0)
                if blocked <= eligible_ends and selected_count - blocked <= actual - eligible_ends:
                    feasible.add(length + selected_count - 1)
    return sorted(feasible)


def local_cases(name, stars_by_law, model_by_law):
    # Ages differ by one. Both roots have at least two originals through the
    # entire rooted six-step view. Only the long marked ring has the proof
    # that no marked original can occur inside either view.
    seeded = {"marked_23": 7, "plain_5": 0, "marked_5": 1}
    if name not in seeded:
        return {}
    cases = {}
    for law in LAWS:
        traces = stars_by_law[law]
        old_lift = model_by_law[law]
        phase = seeded[name]
        roots = []
        charts = []
        for age in (7, 8):
            root = old_lift[age][0][Cluster(phase, age + 1, ())]
            frame = traces[age]
            _, ordinary, loose = fixture().incidence(frame)
            local_parents = len(frame[root]) - len(loose[root])
            assert local_parents == len(ordinary[root]) == 2
            entry = {"age": age, "root": root,
                     "direct_inputs": local_parents, "arity": len(frame[root]), "loose": len(loose[root])}
            if name != "plain_5":
                bound = possible_ages(23 if name == "marked_23" else 5,
                                      entry["arity"], entry["direct_inputs"])
                assert age in bound
                entry["feasible_ages_from_arity_and_inputs"] = bound
            charts.append(rooted_chart(frame, root, 6))
            roots.append(entry)
        equal = nx.is_isomorphic(*charts, node_match=lambda a, b: a["color"] == b["color"])
        if name in {"marked_23", "plain_5"}:
            assert equal
        assert roots[0]["direct_inputs"] == roots[1]["direct_inputs"] == 2
        cases[law] = {"roots": roots, "radius": 6, "rooted_holding_charts_isomorphic": equal,
                      "chart_knots": [sum(role[0] == "knot" for role in chart) for chart in charts]}
        if name == "marked_5":
            incomplete = Cluster(0, 5, (("leftover", 0, 0),))
            complete = Cluster(0, 6, (("leftover", 0, 0), ("leftover", 5, 0)))
            first = old_lift[5][0][incomplete]
            second = old_lift[7][0][complete]
            assert not impulse(incomplete) and impulse(complete)
            assert nx.is_isomorphic(rooted_chart(traces[5], first, 0),
                                    rooted_chart(traces[7], second, 0),
                                    node_match=lambda a, b: a["color"] == b["color"])
            cases[law]["same_single_holder_record_at_pulse_and_nonpulse"] = {
                "without_pulse_age": 5, "with_pulse_age": 7, "arity": 4, "loose": 2,
                "actual_knot_labels_for_replay_only": [first, second],
            }
    return cases


def count_growth_root(winding):
    n = len(winding.holders)
    multiplicity = sum(winding.extras) + (winding.hung is not None)
    if not multiplicity:
        return 1.0
    low, high = 1.0, 2.0
    for _ in range(56):
        middle = (low + high) / 2
        if middle ** n < (1 + 1 / middle) ** multiplicity:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def ring_case(name, source, windings, *, complete=True):
    study = analytic_panel(windings)
    literal, frames, indices = {}, {}, {}
    for law in LAWS:
        replay, frames[law], indices[law] = literal_panel(source, windings, law, complete=complete)
        for row in replay["rows"]:
            age = row["age"]
            if complete:
                expected = {k: value for k, value in study["profile"][age - 1].items() if k != "age"}
                assert row["whole_cut"] == expected
            for winding, selected in zip(windings, row["selected_windings"], strict=True):
                if sum(winding.extras) == 1:
                    n = len(winding.holders)
                    pulse = age >= n + 2 and (age - 2) % n == 0
                    assert len(selected["both_ends_selected_leftovers"]) == int(pulse)
        literal[law] = replay
    assert literal["parity"] == literal["nae"]
    study["literal_replay_by_law"] = literal
    study["source_supports"] = source
    study["winding_originals"] = [w.holders for w in windings]
    study["leftover_counts_in_winding_order"] = [w.extras for w in windings]
    study["hung_original_and_gap"] = [(w.hung, w.hung_gap) for w in windings]
    study["classification_unit"] = "whole_cut" if complete else "two_selected_parent_closed_windings"
    if complete:
        study["total_birth_growth_factor"] = max(map(count_growth_root, windings))
    local = local_cases(name, frames, indices)
    if local:
        study["rooted_local_readings"] = local
    return study


def long_comparison():
    rows = []
    for age in range(4097):
        lap = [max(0, (age - 2) // n) for n in (5, 7)]
        records = [0 if age < 3 else 1 + (age - 3) // (n + 1) for n in (5, 7)]
        rows.append([age, *lap, *records])
    return {"columns": ["age", "five_turns", "seven_turns", "five_parent_records",
                        "seven_parent_records"],
            "limiting_five_over_seven_turn_ratio": [7, 5],
            "limiting_five_over_seven_parent_record_ratio": [8, 6],
            "counts": rows}


def checked_archive_control():
    receipt = json.loads(ARCHIVE.read_bytes())
    partnered = receipt["hosts"]["partnered"]
    assert partnered["roster_counts_through_age_four"] == [6, 8, 10, 24, 4086]
    assert all(n // 2 > 2 for n in partnered["roster_counts_through_age_four"])
    return {"description": "known order-three partnered runaway",
            "cohort_sizes_through_age_four": partnered["roster_counts_through_age_four"],
            "two_parent_births": "zero at every positive cut by the whole roster theorem",
            "derived_from_earlier_exact_actual_parent_replay": True}


def result():
    specs = (
        ("plain_5", 5, (), None),
        ("marked_5", 5, (0,), None),
        ("marked_7", 7, (0,), None),
        ("marked_8", 8, (0,), None),
        ("marked_9", 9, (0,), None),
        ("marked_10", 10, (0,), None),
        ("marked_23", 23, (0,), None),
        ("all_marked_5", 5, tuple(range(5)), None),
        ("period_two_8", 8, (0, 4), None),
        ("same_winding_attachment_8", 8, (0,), 3),
        ("other_winding_attachment_8", 8, (0,), 2),
    )
    cases = {name: ring_case(name, *attached_ring(n, marks, hung))
             for name, n, marks, hung in specs}
    assert cases["marked_8"]["eventual_two_parent_least_period"] == 4
    assert cases["period_two_8"]["eventual_two_parent_least_period"] == 2
    same = cases["same_winding_attachment_8"]
    other = cases["other_winding_attachment_8"]
    assert same["eventual_two_parent_profile"] == (13, 13, 13, 13)
    assert other["eventual_two_parent_profile"] == (12, 12, 13, 13)
    standalone = cases["marked_8"]["literal_replay_by_law"]["parity"]["rows"]
    for attached in (same, other):
        tested = attached["literal_replay_by_law"]["parity"]["rows"]
        for before, after in zip(standalone, tested):
            assert bool(before["selected_windings"][0]["both_ends_selected_leftovers"]) == (
                bool(after["selected_windings"][0]["both_ends_selected_leftovers"]))
    joined = {}
    for length in (1, 2):
        source, tracks = joined_rings(length)
        _, physical, loose = fixture().incidence(source)
        _, witnessed = fixture().witnessed_end(physical, loose)
        assert nx.is_connected(witnessed)
        joined[length] = ring_case("joined_5_and_7", source, tracks, complete=False)
        joined[length]["one_witnessed_part_at_origin"] = True

    files = (Path(__file__).resolve(), FIXTURE, ARCHIVE, HERE / "contract.json",
             RESEARCH / "preregistration.md")
    return {"scope": "deterministic ring fixtures, each replayed under both knot laws",
            "analytic_cut": HORIZON, "literal_cohort_cap": CAP, "cases": cases,
            "joined_pair_by_bridge_length": joined, "long_ring_comparison": long_comparison(),
            "past_explosive_control": checked_archive_control(),
            "sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    raw = json.dumps(result(), separators=(",", ":"), sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as receipt:
            receipt.write(raw)
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
