"""Reconstruct ordinary births on literal distinctions, without the study runner."""

import argparse
import json
import resource
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cached_property
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
from time import perf_counter

import networkx as nx


RECORD = (
    Path(__file__).resolve().parents[3]
    / "artifacts/FOUR-READINGS-20261120-001A"
    / "FOUR-READINGS-20261120-001A-E001_signed_rules"
)


def connected(neighbors, keep):
    keep = set(keep)
    if not keep:
        return False
    seen = set()
    todo = {next(iter(keep))}
    while todo:
        holder = todo.pop()
        seen.add(holder)
        todo.update((neighbors[holder] & keep) - seen)
    return seen == keep


@dataclass(frozen=True)
class Pattern:
    holders: tuple
    holdings: tuple
    odd: frozenset = frozenset()

    @cached_property
    def stars(self):
        return {
            holder: sum(1 << distinction for distinction, ends in enumerate(self.holdings)
                        if holder in ends)
            for holder in self.holders
        }

    @cached_property
    def neighbors(self):
        neighbors = {holder: set() for holder in self.holders}
        for ends in self.holdings:
            if len(ends) == 2:
                left, right = ends
                neighbors[left].add(right)
                neighbors[right].add(left)
        return neighbors

    @cached_property
    def loose(self):
        loose = defaultdict(list)
        for distinction, ends in enumerate(self.holdings):
            if len(ends) == 1:
                loose[ends[0]].append(distinction)
        return loose

    @property
    def sign_bit(self):
        return 1 << len(self.holdings)

    @cached_property
    def consequences(self):
        rows = {0}
        for holder, star in self.stars.items():
            signed_star = star | (self.sign_bit if holder in self.odd else 0)
            rows |= {row ^ signed_star for row in rows}
        return rows

    def projecting(self, distinctions):
        mask = distinctions | self.sign_bit
        return {row for row in self.consequences if not row & ~mask}

    def full_knots(self):
        return [
            star.bit_count() >= 3 and self.projecting(star) == {0, star}
            for star in self.stars.values()
        ]

    def scalar_count(self):
        if self.sign_bit in self.consequences:
            return 0
        rank = len(self.consequences).bit_length() - 1
        return 1 << (len(self.holdings) - rank)

    def puncture(self, last):
        return Pattern(tuple(holder for holder in self.holders if holder != last),
                       tuple(tuple(holder for holder in ends if holder != last)
                             for ends in self.holdings))


def groups(live, witness_rosters):
    live = tuple(sorted(live))
    witnesses = tuple(set(roster) for roster in witness_rosters)
    pairs = {pair for roster in witnesses for pair in combinations(sorted(roster), 2)}
    selected = []
    for size in range(len(live), 2, -1):
        for candidate in combinations(live, size):
            subset = set(candidate)
            if any(subset <= other for other in witnesses + tuple(selected)):
                continue
            if all(pair in pairs for pair in combinations(candidate, 2)):
                selected.append(subset)
    uncovered = pairs - {
        pair for subset in selected for pair in combinations(sorted(subset), 2)
    }
    return [tuple(sorted(subset)) for subset in selected] + sorted(uncovered)


def ordinary_step(source, parity=True):
    live = set(source.loose)
    rosters = groups(live, (neighbors & live for neighbors in source.neighbors.values()))
    owed = Counter(holder for roster in rosters for holder in roster)
    shortages = {holder: owed[holder] - len(source.loose[holder]) for holder in live
                 if owed[holder] > len(source.loose[holder])}
    if shortages:
        return None, {"status": "stall", "shortages": shortages}
    for holder in sorted(live):
        rosters.extend([(holder,)] * (len(source.loose[holder]) - owed[holder]))

    offsets = Counter()
    children = defaultdict(list)
    for birth, roster in enumerate(rosters):
        for parent in roster:
            children[parent].append(birth)
    next_owed = Counter(birth for group in groups(range(len(rosters)), children.values())
                        for birth in group)

    holdings = list(source.holdings)
    newborns = []
    odd = set(source.odd)
    for birth, roster in enumerate(rosters):
        name = max(source.holders) + birth + 1
        inputs = []
        for parent in roster:
            distinction = source.loose[parent][offsets[parent]]
            offsets[parent] += 1
            inputs.append(distinction)
            holdings[distinction] += (name,)

        mask = sum(1 << distinction for distinction in inputs)
        implied = source.projecting(mask) if parity else {0}
        rhs = int((mask | source.sign_bit) in implied)
        demand = next_owed[birth]
        fresh = max(demand, 3 - len(inputs), 1)
        if parity and not demand and (mask in implied or rhs):
            fresh = 0
        if rhs:
            odd.add(name)
        holdings.extend([(name,)] * fresh)
        newborns.append({"holder": name, "inputs": sorted(inputs),
                         "demand": demand, "fresh": fresh, "odd": bool(rhs)})

    result = Pattern(source.holders + tuple(birth["holder"] for birth in newborns),
                     tuple(holdings), frozenset(odd))
    status = "grown" if result.loose else "closed"
    return result, {"status": status, "newborns": newborns}


def inverse(target, last):
    parents = target.neighbors[last]
    arity = target.stars[last].bit_count()
    if arity < 2 or len(parents) != arity:
        return False
    if any(target.stars[h].bit_count() < 3 for h in target.holders if h != last):
        return False
    for removed in target.holders:
        if not connected(target.neighbors, set(target.holders) - {removed}):
            return False
    witnesses = [neighbors for holder, neighbors in target.neighbors.items() if holder != last]
    if arity > 2 and any(parents <= witness for witness in witnesses):
        return False
    return all(any(set(pair) <= witness for witness in witnesses)
               for pair in combinations(parents, 2))


def rebuild(target, last):
    source = target.puncture(last)
    source_connected = connected(source.neighbors, source.holders)
    projection = source.full_knots()
    returned, step = (ordinary_step(source) if source_connected and all(projection)
                      else (None, {"status": "inadmissible"}))
    restored = step["status"] == "closed"
    if restored:
        newborn, = step["newborns"]
        assert not newborn["fresh"] and not newborn["odd"] and not returned.odd
        renamed = tuple(tuple(sorted(last if holder == newborn["holder"] else holder
                                     for holder in ends))
                        for ends in returned.holdings)
        assert renamed == tuple(tuple(sorted(ends)) for ends in target.holdings)
        assert returned.scalar_count() == 1 << (len(target.holdings) - len(target.holders) + 1)
        assert returned.scalar_count() == source.scalar_count()
        edited = Pattern(returned.holders, returned.holdings, frozenset({newborn["holder"]}))
        assert edited.scalar_count() == 0
    assert restored == inverse(target, last), (target, last)
    return restored, source_connected, projection, returned, step


def compare_saved(last, restored, source_connected, projection, returned, step, saved, size):
    assert [last, restored, source_connected, projection] == [
        saved["last"], saved["restored"], saved["source_connected"], saved["source_full_knots"]
    ]
    saved_step = saved["step"]
    if saved_step is None:
        assert step == {"status": "inadmissible"}
        return
    assert saved_step["status"] == step["status"]
    if returned is None:
        shortages = {str(holder - (holder > last)): extra
                     for holder, extra in step["shortages"].items()}
        assert shortages == saved_step["shortages"]
        return
    assert [len(returned.holders), len(returned.holdings), sum(map(len, returned.loose.values()))] == [
        saved_step["holders"], saved_step["distinctions"], saved_step["loose"]
    ]
    fresh_bundles = sorted((birth["inputs"], birth["demand"], birth["fresh"])
                           for birth in step["newborns"])
    saved_bundles = sorted((sorted(place for place in birth["places"] if place < size),
                            birth["demand"], birth["fresh"]) for birth in saved_step["new"])
    assert len(fresh_bundles) == saved_step["births"] and fresh_bundles == saved_bundles


def orbits(target):
    same_degree = defaultdict(list)
    for holder in target.holders:
        same_degree[target.stars[holder].bit_count()].append(holder)
    classes = list(same_degree.values())
    old = [holder for degree_class in classes for holder in degree_class]
    reached = {holder: set() for holder in old}
    distinctions = {tuple(sorted(ends)) for ends in target.holdings}
    for image in product(*(permutations(degree_class) for degree_class in classes)):
        match = dict(zip(old, (holder for group in image for holder in group)))
        if all(tuple(sorted((match[left], match[right]))) in distinctions
               for left, right in distinctions):
            for holder in old:
                reached[holder].add(match[holder])
    return sorted({tuple(sorted(reached[holder])) for holder in reached})


def operator_possible(target):
    # Repeated meetings reduce to their product in the signed operator rules.
    sharing = nx.Graph()
    sharing.add_nodes_from(target.holders)
    sharing.add_edges_from(target.holdings)
    return not nx.check_planarity(sharing)[0]


def closed(size, holdings):
    return Pattern(tuple(range(size)), tuple(tuple(sorted(ends)) for ends in holdings))


def census(pilot):
    saved_census = json.loads((RECORD / "census.json").read_text())
    saved_punctures = {row["atlas"]: row["punctures"] for row in
                       json.loads((RECORD / "all_punctures.json").read_text())}
    rows = saved_census[-8:] if pilot else saved_census
    stats = defaultdict(Counter)
    types = []
    for row in rows:
        name, size = row["atlas"], row["n"]
        target = closed(size, row["sharing"])
        operator = operator_possible(target)
        assert operator == row["operator"]
        counts = stats[size]
        counts["types"] += 1
        counts["operator_types"] += operator
        reconstructed = []
        type_orbits = orbits(target)
        counts["marked_orbits"] += len(type_orbits)
        for last, original in zip(target.holders, saved_punctures[name], strict=True):
            result = rebuild(target, last)
            compare_saved(last, *result, original, len(target.holdings))
            counts["marks"] += 1
            counts["step_" + result[-1]["status"]] += 1
            if result[0]:
                assert original["step"]["operator_after_one_supplied_odd"] == operator
                reconstructed.append(last)
                counts["operator_restorations"] += operator
        successful_orbits = [orbit for orbit in type_orbits if orbit[0] in reconstructed]
        assert {h for orbit in successful_orbits for h in orbit} == set(reconstructed)
        counts["restored_orbits"] += len(successful_orbits)
        counts["operator_restored_orbits"] += operator * len(successful_orbits)
        assert reconstructed == row["restored_last_holders"]
        if reconstructed:
            counts["reached_types"] += 1
            counts["reached_operator_types"] += operator
            types.append({"record_id": name, "holders": size, "distinctions": len(target.holdings),
                          "operator": operator, "restored_marks": reconstructed,
                          "restored_orbits": successful_orbits})
    total = sum(stats.values(), Counter())
    if not pilot:
        assert [total[key] for key in ("types", "marks", "step_closed", "reached_types",
                                       "reached_operator_types")] == [173, 1183, 397, 121, 79]
    positives = [row for row in types if row["operator"]]
    return {"by_size": dict(stats), "total": total, "exact_reached_types": types,
            "smallest_reached_operator_holding": min(
                (row["holders"], row["distinctions"]) for row in positives
            )}


def degree_completions(remaining):
    active = [holder for holder in remaining if remaining[holder]]
    if not active:
        yield ()
        return
    first, *others = active
    for neighbors in combinations_with_replacement(others, remaining[first]):
        residual = dict(remaining)
        residual[first] = 0
        for other in neighbors:
            residual[other] -= 1
        if all(value >= 0 for value in residual.values()):
            for tail in degree_completions(residual):
                yield tuple((first, other) for other in neighbors) + tail


def cubic_completions(outside_count):
    parents = (1, 2, 3)
    witnesses = (4, 5, 6)
    core = [(0, parent) for parent in parents]
    core += [(parent, w) for w, pair in zip(witnesses, combinations(parents, 2))
             for parent in pair]
    outside = tuple(range(7, 7 + outside_count))
    attachments = [tuple(zip(witnesses, destinations)) for destinations in product(outside, repeat=3)]
    attachments.extend((pair, (next(w for w in witnesses if w not in pair), other))
                       for pair in combinations(witnesses, 2) for other in outside)
    for attachment in attachments:
        used = Counter(end for ends in attachment for end in ends if end in outside)
        remaining = {holder: 3 - used[holder] for holder in outside}
        for more in degree_completions(remaining):
            yield closed(7 + outside_count, core + list(attachment) + list(more))


def minima(pilot):
    all_five = closed(5, combinations(range(5), 2))
    three_against_three = closed(6, product(range(3), range(3, 6)))
    core = [(0, parent) for parent in (1, 2, 3)]
    core += [(parent, witness) for witness, pair in
             zip((4, 5, 6), combinations((1, 2, 3), 2)) for parent in pair]
    ternary = closed(12, core + [(4, 7), (5, 8), (6, 9)] + list(product((7, 8, 9), (10, 11))))
    assert operator_possible(ternary) and all(star.bit_count() == 3 for star in ternary.stars.values())
    assert rebuild(ternary, 0)[0] and rebuild(all_five, 0)[0]
    assert operator_possible(all_five) and operator_possible(three_against_three)

    doubled_away = closed(5, all_five.holdings + ((1, 2),))
    doubled_at = closed(5, all_five.holdings + ((0, 1),))
    assert rebuild(doubled_away, 0)[0]
    at = rebuild(doubled_at, 0)
    assert not at[0] and at[-1]["status"] == "grown"
    assert sorted(new["fresh"] for new in at[-1]["newborns"]) == [1, 2]

    tie_counts = []
    for base in (three_against_three, all_five):
        assert all(rebuild(base, holder)[0] == (base is all_five) for holder in base.holders)
        last = len(base.holders)
        accepted = 0
        for position, (left, right) in enumerate(base.holdings):
            split = closed(last + 1, base.holdings[:position] + base.holdings[position + 1:]
                           + ((left, last), (right, last)))
            assert operator_possible(split)
            accepted += rebuild(split, last)[0]
        assert accepted == (len(base.holdings) if base is all_five else 0)
        tie_counts.append({"holders": last + 1, "distinctions": len(base.holdings) + 1,
                           "marks": len(base.holdings), "restored": accepted})

    unary = closed(3, [(0, 1)] * 3 + [(0, 2)])
    reached, connected_source, projection, _, _ = rebuild(unary, 2)
    assert not reached and connected_source and projection == [False, True]

    four = closed(4, combinations(range(4), 2))
    assert not operator_possible(four) and rebuild(four, 0)[0]
    cubic_counts = {}
    for outside_count in ((1,) if pilot else (1, 3)):
        stats = Counter()
        for target in cubic_completions(outside_count):
            assert all(star.bit_count() == 3 for star in target.stars.values())
            stats["completions"] += 1
            stats["repeated_old_meetings"] += len(set(target.holdings)) < len(target.holdings)
            stats["joined_witness_places"] += any(
                left in (4, 5, 6) and right in (4, 5, 6) for left, right in target.holdings
            )
            assert not operator_possible(target)
            stats["lawful_and_restored"] += rebuild(target, 0)[0]
        cubic_counts[7 + outside_count] = stats

    nae_controls = {}
    for target in (all_five, ternary):
        source = target.puncture(0)
        result, step = ordinary_step(source, parity=False)
        assert step["status"] == "grown" and len(step["newborns"]) == 1
        assert step["newborns"][0]["fresh"] == 1 and sum(map(len, result.loose.values())) == 1
        nae_controls[len(target.holders)] = 1
    starts = {}
    for width, expected in ((3, [3, 3, 1]), (4, [4, 6, 4, 1])):
        pattern = Pattern((0,), ((0,),) * width)
        births = []
        for _ in expected:
            assert all(pattern.full_knots())
            pattern, step = ordinary_step(pattern)
            births.append(len(step["newborns"]))
        assert births == expected and step["status"] == "closed"
        assert [len(pattern.holders), len(pattern.holdings)] == [1 << width, width << (width - 1)]
        positive = operator_possible(pattern)
        assert positive == (width == 4)
        starts[width] = {"births": births, "holders": len(pattern.holders),
                         "distinctions": len(pattern.holdings), "operator": positive}
    return {"all_ternary_witness": ternary.holdings,
            "below_twelve_degree_completions": cubic_counts,
            "ordinary_two_place_exceptions": tie_counts,
            "doubled_last_meeting_step": at[-1],
            "not_all_equal_fresh_on_matched_proposals": nae_controls,
            "single_knot_starts_by_initial_distinction_count": starts,
            "scalar_counts_before_after_sign_supply": {
                len(target.holders): [target.scalar_count(),
                                      Pattern(target.holders, target.holdings,
                                              frozenset({0})).scalar_count()]
                for target in (all_five, ternary)
            }}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    census_start = perf_counter()
    census_result = census(args.pilot)
    minima_start = perf_counter()
    minima_result = minima(args.pilot)
    report = {"pilot": args.pilot, "census": census_result, "minima": minima_result,
              "seconds": {"census": minima_start - census_start,
                          "minima": perf_counter() - minima_start},
              "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value if key != "census" else value["total"]
                      for key, value in report.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
