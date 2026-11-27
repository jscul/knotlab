"""Replay the small pairs and ordinary growth from their written definitions."""

import argparse
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
import json
from pathlib import Path
import resource
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
ROOT = RESEARCH.parent
START_ARCHIVE = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
GROWTH_ARCHIVE = RESEARCH / "BUILT-BINDING-20261126-001"
RING_ARCHIVE = RESEARCH / "SELECTED-KNOTS-20261127-001" / "referee-R1" / "natural_places.json"


def named_rows(holdings):
    words = [tuple(row.split()) for row in holdings]
    names = sorted({name for row in words for name in row})
    return names, tuple(tuple(names.index(name) for name in row) for row in words)


def from_numbered_meetings(count, meetings, openings):
    rows = [[] for _ in range(count)]
    name = 0
    for left, right, multiplicity in meetings:
        for _ in range(multiplicity):
            rows[left].append(name)
            rows[right].append(name)
            name += 1
    for knot, size in enumerate(openings):
        rows[knot].extend(range(name, name + size))
        name += size
    return tuple(tuple(row) for row in rows)


def holding(rows):
    holders = defaultdict(list)
    for knot, row in enumerate(rows):
        for name in row:
            holders[name].append(knot)
    loose = defaultdict(list)
    meetings = [set() for _ in rows]
    for name, knots in holders.items():
        if len(knots) == 1:
            loose[knots[0]].append(name)
        elif len(knots) == 2 and knots[0] != knots[1]:
            first, second = knots
            meetings[first].add(second)
            meetings[second].add(first)
        else:
            raise ValueError(f"wrong holding for distinction {name}: {knots}")
    return dict(loose), meetings


def candidate_pairs(witnesses):
    return {pair for witness in witnesses for pair in combinations(sorted(witness), 2)}


def joining_groups(witnesses):
    witnesses = {frozenset(witness) for witness in witnesses if len(witness) >= 2}
    pairs = candidate_pairs(witnesses)
    adjacency = defaultdict(set)
    for left, right in sorted(pairs):
        adjacency[left].add(right)
        adjacency[right].add(left)

    def maximal_cliques(included, possible, excluded):
        if not possible and not excluded:
            yield included
            return
        pivot = max(possible | excluded, key=lambda knot: len(adjacency[knot] & possible))
        for knot in sorted(possible - adjacency[pivot]):
            others = adjacency[knot]
            yield from maximal_cliques(included | {knot}, possible & others, excluded & others)
            possible.remove(knot)
            excluded.add(knot)

    larger = [tuple(sorted(group))
              for group in maximal_cliques(set(), set(adjacency), set())
              if len(group) >= 3 and all(not group <= witness for witness in witnesses)]
    covered = {pair for group in larger for pair in combinations(group, 2)}
    return sorted(larger) + sorted(pairs - covered)


def ordinary_round(rows, law):
    """Fund every group and offshoot before computing the next demand."""
    loose, meetings = holding(rows)
    if not loose:
        return "closed", rows, []
    groups = joining_groups([near & loose.keys() for near in meetings])
    debt = Counter(parent for group in groups for parent in group)
    if any(debt[knot] > len(names) for knot, names in loose.items()):
        return "stalled", rows, []
    parent_sets = groups + [(knot,) for knot, names in sorted(loose.items())
                            for _ in range(len(names) - debt[knot])]
    child_rosters = defaultdict(set)
    for child, parents in enumerate(parent_sets):
        for knot in parents:
            child_rosters[knot].add(child)
    demands = Counter(knot for group in joining_groups(child_rosters.values()) for knot in group)
    available = {knot: iter(sorted(names)) for knot, names in loose.items()}
    name = max(max(row) for row in rows) + 1
    new_rows = []
    births = []
    for index, parents in enumerate(parent_sets):
        inputs = tuple(next(available[knot]) for knot in parents)
        takes_all = len(parent_sets) == 1
        implied = law == "parity" and takes_all
        count = 0 if implied else max(1, 3 - len(parents), demands[index])
        fresh = tuple(range(name, name + count))
        name += count
        new_rows.append(inputs + fresh)
        births.append({"parents": list(parents), "inputs": inputs, "fresh": fresh,
                       "p": len(parents), "f": count, "implied": implied, "takes all": takes_all})
    return "funded", rows + tuple(new_rows), births


def replay(rows, law, horizon):
    for index in range(1, horizon + 1):
        outcome, rows, births = ordinary_round(rows, law)
        yield index, outcome, rows, births
        if outcome != "funded":
            return


def start_families(rows):
    loose, meetings = holding(rows)
    neighbors = {knot: set() for knot in loose}
    for left, right in candidate_pairs([near & loose.keys() for near in meetings]):
        neighbors[left].add(right)
        neighbors[right].add(left)
    families = []
    unseen = set(loose)
    while unseen:
        todo = {min(unseen)}
        family = set()
        while todo:
            knot = todo.pop()
            family.add(knot)
            unseen.remove(knot)
            todo.update(neighbors[knot] & unseen)
        families.append(sorted(family))
    return families


def mask(distinctions):
    return sum(1 << name for name in distinctions)


def parity_states(rows):
    equations = tuple(map(mask, rows))
    return [word for word in range(1 << (max(max(row) for row in rows) + 1))
            if all((word & equation).bit_count() % 2 == 0 for equation in equations)]


def state_word(word, size):
    return "".join(str((word >> place) & 1) for place in range(size))


def pairs_audit(archive):
    arms = {
        "i": [("x1 x2 y", "y z1 z2 w", "z1 z2 v"),
              ("x1 x2 v w", "y z1 z2 w", "z1 z2 v")],
        "ii": [("r41 r12 l1", "r12 r23 l2", "r23 r34 l3", "r34 r41 l4"),
               ("r12 r23 l2", "r23 r34 l3", "r34 r41 l4", "l1 l2 l3 l4")],
        "iii": [("a1 a2 c l", "b c m", "a1 a2 b"),
                ("b c l", "a1 a2 c m", "a1 a2 b")],
    }
    result = {}
    for pair, pair_arms in arms.items():
        name_sets, words_by_arm, loose_sets, family_sets = [], [], [], []
        for arm in pair_arms:
            names, rows = named_rows(arm)
            name_sets.append(names)
            states = parity_states(rows)
            assert all(len({word & mask(knot) for word in states}) == 2 ** (len(knot) - 1) for knot in rows)
            words_by_arm.append(states)
            loose, _ = holding(rows)
            loose_sets.append(sorted(names[name] for held in loose.values() for name in held))
            family_sets.append(sorted(sorted(names[name] for knot in family for name in loose[knot])
                                      for family in start_families(rows)))
        measured = {"same names": name_sets[0] == name_sets[1],
                    "same allowed states": words_by_arm[0] == words_by_arm[1],
                    "states": [len(states) for states in words_by_arm],
                    "same loose set": loose_sets[0] == loose_sets[1],
                    "loose sets": loose_sets, "families (as loose groups)": family_sets}
        expected = dict(archive[pair])
        expected["families (as loose groups)"] = [sorted(map(sorted, arm))
                                                 for arm in expected["families (as loose groups)"]]
        assert measured == expected, (pair, measured, expected)
        different = {frozenset(row.split()) for row in pair_arms[0]} != {frozenset(row.split()) for row in pair_arms[1]}
        assert different
        measured.update({"different holdings": different,
                         "holdings": pair_arms, "distinction order": name_sets[0],
                         "allowed states": sorted(state_word(word, len(name_sets[0])) for word in words_by_arm[0]),
                         "matches archive": True})
        result[pair] = measured
    return result


def numbered_trace(rows, law, horizon):
    fields = ("parents", "p", "f", "implied", "takes all")
    for index, outcome, _, births in replay(rows, law, horizon):
        for birth in births:
            yield {"round": index, **{field: birth[field] for field in fields}}
        if outcome != "funded":
            yield {"round": index, "end": outcome}


def compare_archive(starts, sample, law):
    archive = GROWTH_ARCHIVE / f"closing_census_{law}.jsonl"
    result = []
    two_place = Counter()
    archive_starts = 0
    with archive.open() as stream:
        for line in stream:
            row = json.loads(line)
            if not row.get("start", "").startswith("census "):
                continue
            archive_starts += 1
            index = int(row["start"].split()[-1])
            for birth in row["births"]:
                if "end" not in birth and birth["p"] + birth["f"] == 2:
                    two_place[(birth["round"], birth["implied"])] += 1
            if index not in sample:
                continue
            start = from_numbered_meetings(*starts[index])
            recorded = row["births"]
            measured = list(numbered_trace(start, law, 3))
            assert measured == recorded, (index, law, measured, recorded)
            result.append({"census index": index, "starting knots": len(start),
                           "loose counts at their holders": sorted(map(len, holding(start)[0].values())),
                           "births": sum("p" in event for event in measured),
                           "two-place births": sum("p" in event and event["p"] + event["f"] == 2 for event in measured),
                           "final recorded event": measured[-1]})
    assert len(result) == len(sample)
    assert archive_starts == len(starts)
    return {"archive": str(archive.relative_to(ROOT)), "archived starts": archive_starts, "compared starts": result,
            "archive two-place counts": [{"round": index, "implied": implied, "births": count}
                                         for (index, implied), count in sorted(two_place.items())]}


def recursion_tree(archive):
    start = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))
    events = []
    details = []
    for index, outcome, stage, births in replay(start, "parity", 3):
        sizes = Counter(str(birth["p"] + birth["f"]) for birth in births)
        if outcome == "funded":
            events.append({"round": index, "births": len(births), "places of births": dict(sizes),
                           "two-place births": sizes["2"]})
        else:
            events.append({"round": index, "end": outcome})
        details.append({"round": index, "loose distinctions after round":
                        sum(map(len, holding(stage)[0].values())), "births": births})
    assert list(map(list, start)) == archive["start"]
    assert events == archive["rounds"], (events, archive["rounds"])
    return {"start": start, "rounds": events, "details": details, "matches archive": True}


def binary_closing_control():
    names, start = named_rows(("a b l", "c d m", "a b c d"))
    outcome, after, births = ordinary_round(start, "parity")
    assert outcome == "funded" and len(births) == 1 and births[0]["implied"]
    assert set(births[0]["inputs"]) == {names.index("l"), names.index("m")}
    assert births[0]["f"] == 0 and not holding(after)[0]
    words = parity_states(start)
    assert words == parity_states(after)
    assert all(len(parity_image(start, [1 << name for name in knot])) == 2 ** (len(knot) - 1)
               for knot in start)
    two_places = [1 << names.index(name) for name in ("l", "m")]
    return {"names": names, "start": start, "births": births, "old state count": len(words),
            "new state count": len(parity_states(after)), "same allowed states": True,
            "loose pair before and after": sorted(state_word(word, 2) for word in parity_image(start, two_places))}


def span_basis(equations):
    pivots = {}
    for row in equations:
        while row:
            leading = row.bit_length() - 1
            if leading not in pivots:
                pivots[leading] = row
                break
            row ^= pivots[leading]
    return tuple((1 << index, pivots[index]) for index in sorted(pivots, reverse=True))


def reduce(equation, basis):
    for bit, row in basis:
        if equation & bit:
            equation ^= row
    return equation


def parity_image(rows, expressions):
    basis = span_basis(map(mask, rows))
    forms = [reduce(expr, basis) for expr in expressions]
    variation = span_basis(sum(1 << index for index, form in enumerate(forms) if form & (1 << bit))
                           for bit in range(max(forms, default=0).bit_length()))
    words = {0}
    for _, row in variation:
        words |= {word ^ row for word in words}
    return words


def relations(words, size):
    equations = [form for form in range(1, 1 << size)
                 if all((form & word).bit_count() % 2 == 0 for word in words)]
    minimal = []
    for equation in sorted(equations, key=int.bit_count):
        if all(equation & old != old for old in minimal):
            minimal.append(equation)
    return equations, minimal


def canonical_parity_check(words, names):
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.cli import check

    clauses = [" ".join(("~" if excluded & (1 << place) else "") + name
                        for place, name in enumerate(names))
               for excluded in range(1 << len(names)) if excluded not in words]
    output = StringIO()
    with redirect_stdout(output):
        check("; ".join(clauses), names[:-1], names[-1], (), True)
    verdict = json.loads(output.getvalue())
    assert verdict["is_knot"], verdict
    return verdict


def ring_start():
    """Three four-knot rings, split attachments and doubled connecting links."""
    holders = [(offset + j, offset + (j + 1) % 4)
               for offset in (0, 4, 8) for j in range(4)]
    holders.extend((knot,) for knot in range(12) for _ in range(2))
    for pair_number, (left, right) in enumerate(combinations(range(3), 2)):
        left_link = 12 + 2 * pair_number
        right_link = left_link + 1
        other_ring = 3 - left - right
        left_offset = int(other_ring < right)
        right_offset = int(other_ring < left)
        holders.extend(((4 * left + left_offset, left_link), (4 * left + left_offset + 2, left_link),
                        (4 * right + right_offset, right_link), (4 * right + right_offset + 2, right_link),
                        (left_link, right_link), (left_link, right_link)))
    return tuple(tuple(name for name, knots in enumerate(holders) if knot in knots) for knot in range(18))


def least_flip(held_group, loose, meetings):
    targets = {knot for knot, names in loose.items() if set(names) - held_group}
    sources = {knot for knot, names in loose.items() if set(names) & held_group}
    todo = deque((knot, 0) for knot in sorted(sources))
    seen = set(sources)
    while todo:
        knot, steps = todo.popleft()
        if knot in targets:
            return steps + 2
        for other in meetings[knot] - seen:
            seen.add(other)
            todo.append((other, steps + 1))
    raise ValueError("no allowed change flips this parity")


def has_single_reader(rows, parities):
    laws = span_basis(map(mask, rows))
    reduced_parities = [reduce(form, laws) for form in parities]
    covered = [False] * len(parities)
    for holdings in rows:
        local = span_basis(reduce(1 << name, laws) for name in holdings)
        for index, form in enumerate(reduced_parities):
            covered[index] |= reduce(form, local) == 0
    return covered


def count_relations(minimal):
    return dict(sorted(Counter(str(form.bit_count()) for form in minimal).items()))


def ring_audit(horizon):
    recorded = json.loads(RING_ARCHIVE.read_text())["three_rings_of_four"]
    start = ring_start()
    families = start_families(start)
    assert families == recorded["start families"]
    names_by_knot = {knot: family for family, knots in enumerate(families) for knot in knots}
    loose, _ = holding(start)
    first_carriers = [set().union(*(loose[knot] for knot in group)) for group in families]
    ring_carriers = [first_carriers[index] | first_carriers[index + 1] for index in (0, 2, 4)]
    generations = [first_carriers]
    stage_counts = [[len(start), max(max(row) for row in start) + 1]]
    transitions = []
    example = None
    for index, outcome, rows, births in replay(start, "parity", horizon):
        assert outcome == "funded"
        next_carriers = [set() for _ in families]
        for knot, birth in enumerate(births, len(rows) - len(births)):
            memberships = {names_by_knot[parent] for parent in birth["parents"]}
            assert len(memberships) == 1 and birth["f"] == 2
            family, = memberships
            names_by_knot[knot] = family
            next_carriers[family].update(birth["fresh"])
        loose, meetings = holding(rows)
        assert all(set().union(*(loose[knot] for knot in loose if names_by_knot[knot] == family)) == carrier
                   for family, carrier in enumerate(next_carriers))
        assert all(len(carrier) == 2 * (index + 2) for carrier in next_carriers)
        stages = [near & loose.keys() for near in meetings]
        pairs = candidate_pairs(stages)
        assert all(len(group) == 2 for group in joining_groups(stages))
        assert sum(map(len, loose.values())) == 12 * (index + 2)
        for family in range(len(families)):
            live = {knot for knot in loose if names_by_knot[knot] == family}
            neighbor_counts = Counter(knot for pair in pairs if set(pair) <= live for knot in pair)
            assert sorted(neighbor_counts.values()) == [1, 1] + [2] * index
        left = generations[-1]
        previous = left + ring_carriers
        all_carriers = previous + next_carriers
        previous_values = parity_image(rows, list(map(mask, previous)))
        values = parity_image(rows, list(map(mask, all_carriers)))
        assert len(values) == len(previous_values) == 32
        previous_eqs, previous_minimal = relations(previous_values, 9)
        equations, minimal = relations(values, 15)
        copies = [(1 << family) | (1 << (9 + family)) for family in range(6)]
        exact_basis = span_basis(previous_eqs + copies)
        previous_rank = len(span_basis(previous_eqs))
        enlarged_rank = len(span_basis(equations))
        assert previous_rank == 4 and len(exact_basis) == enlarged_rank == 10
        assert all(reduce(eq, exact_basis) == 0 for eq in equations)
        assert all(all((word & copy).bit_count() == 0 or (word & copy).bit_count() == 2 for word in values)
                   for copy in copies)
        newest = [eq for eq in minimal if eq >> 9]
        costs = [least_flip(group, loose, meetings) for group in next_carriers]
        costs += [least_flip(next_carriers[first] | next_carriers[first + 1], loose, meetings)
                  for first in (0, 2, 4)]
        kept = [place for place, cost in enumerate(costs) if cost > 12]
        kept_names = mask(kept)
        kept_readers = has_single_reader(rows, [mask(previous[place]) for place in kept])
        transitions.append({"round": index, "births": len(births),
                            "loose distinctions per family": list(map(len, next_carriers)),
                            "old minimal relations by places": count_relations(previous_minimal),
                            "inclusion-minimal relations on both generations by places": count_relations(minimal),
                            "inclusion-minimal relations mentioning a new carrier by places": count_relations(newest),
                            "old and enlarged ranks of forced equations": [previous_rank, enlarged_rank],
                            "independent copy equalities": enlarged_rank - previous_rank,
                            "new independent equations beyond copies": enlarged_rank - len(exact_basis),
                            "old and enlarged allowed word counts": [len(previous_values), len(values)],
                            "least changing size, six families then three rings": costs,
                            "facts kept by all changes of size at most twelve": {
                                "fact positions": kept,
                                "joint word count": len({word & kept_names for word in previous_values}),
                                "single-knot readers exist": kept_readers,
                            },
                            "pairwise disjoint carriers": sum(map(len, all_carriers)) == len(set().union(*all_carriers))})
        generations.append(next_carriers)
        stage_counts.append([len(rows), max(max(row) for row in rows) + 1])
        if index == 5:
            recorded_carriers = generations[1] + ring_carriers
            assert [sorted(carrier) for carrier in recorded_carriers] == recorded["disjoint carriers as distinction numbers"]
            assert parity_image(rows, list(map(mask, recorded_carriers))) == set(recorded["allowed words"])
            assert costs == recorded["least changes"]
            triple = [ring_carriers[0], next_carriers[0], next_carriers[1]]
            expressions = list(map(mask, triple))
            triple_words = parity_image(rows, expressions)
            assert not any(has_single_reader(rows, expressions))
            example = {"round": index, "carriers": [sorted(carrier) for carrier in triple],
                       "allowed words": sorted(state_word(word, 3) for word in triple_words),
                       "canonical check": canonical_parity_check(triple_words, ("R1", "p1new", "q1new")),
                       "minimum flip sizes": [costs[6], costs[0], costs[1]], "any one-knot reader": False}
    expected_counts = recorded["knots and distinctions through rounds"][:horizon + 1]
    assert stage_counts[:len(expected_counts)] == expected_counts
    return {"start": start, "families": families, "knots and distinctions through rounds": stage_counts,
            "matching recorded stages (including start)": len(expected_counts), "transitions": transitions,
            "new minimal ternary relation certificate": example}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    begin = perf_counter()
    pairs = json.loads((HERE.parent / "checks_a.json").read_text())["a4"]
    recursion = json.loads((HERE.parent / "recursion_c.json").read_text())
    starts = json.loads(START_ARCHIVE.read_text())
    sample = {0, 959} if args.pilot else {*range(0, len(starts), 337), 959, len(starts) - 1}
    result = {"pairs": pairs_audit(pairs), "tree": recursion_tree(recursion),
              "ordinary parity binary closing control": binary_closing_control(),
              "sample selection": "Every 337th archived census start from zero, census 959, and the final start",
              "archive sample": {law: compare_archive(starts, sample, law) for law in ("parity", "nae")},
              "three rings of four": ring_audit(5 if args.pilot else 7)}
    result["runtime"] = {"elapsed seconds": round(perf_counter() - begin, 3),
                         "peak memory KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         "memory limit bytes": 2 * 1024**3, "processes": 1, "pilot": args.pilot}
    print(json.dumps(result["runtime"]))
    if not args.pilot:
        (HERE / "growth_counts.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
