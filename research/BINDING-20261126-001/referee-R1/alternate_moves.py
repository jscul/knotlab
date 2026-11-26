"""Check both small-change rules, their local reads, and the disjoint-cycle test.

Growth and the historical rosters come from the independent replay. The
change spans, local reads, and forced-relation search are rebuilt here.
Each output row is an exact reading of one stage of a stated sample.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import time


HERE = Path(__file__).resolve().parent
LAYERS = HERE.parent.parent / "LAYERS-20261126-001" / "referee-R1"
SAMPLE_SEED = 2026112605
RULES = ("shortest", "at most five")


def positions(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def mask(names):
    return sum(1 << i for i in names)


def dot(left, right):
    return (left & right).bit_count() % 2


def add(pivots, word):
    while word:
        leading = word.bit_length() - 1
        if leading not in pivots:
            pivots[leading] = word
            return
        word ^= pivots[leading]


def span(words):
    pivots = {}
    for word in words:
        add(pivots, word)
    return pivots


def reduce_word(word, descending_rows):
    for lead, row in descending_rows:
        if (word >> lead) & 1:
            word ^= row
    return word


def nullspace(conditions, size):
    pivots = span(conditions)
    ascending = sorted(pivots.items())
    answer = []
    for i in range(size):
        if i in pivots:
            continue
        word = 1 << i
        for lead, row in ascending:
            word |= dot(row, word) << lead
        answer.append(word)
    return answer


def members(basis):
    words = [0]
    for word in basis:
        words.extend([old ^ word for old in words])
    return words


def union(words):
    result = 0
    for word in words:
        result |= word
    return result


def holder_table(supports):
    # Index 0 collects loose distinctions for the incidence calculation only.
    holders = [[] for _ in range(1 + max(x for row in supports for x in row))]
    for knot, row in enumerate(supports, 1):
        for distinction in row:
            holders[distinction].append(knot)
    adjacency = [[] for _ in range(1 + len(supports))]
    loose = 0
    endpoints = []
    for distinction, owners in enumerate(holders):
        bit = 1 << distinction
        if len(owners) == 1:
            left, right = 0, owners[0]
            loose |= bit
        else:
            left, right = owners
        endpoints.append((left, right, bit))
        adjacency[left].append((right, bit))
        adjacency[right].append((left, bit))
    return adjacency, endpoints, loose


def cycles(adjacency, bound=None):
    """Yield each simple cycle once, allowing parallel distinctions."""
    for first, options in enumerate(adjacency):
        for next_knot, first_bit in options:
            if next_knot <= first:
                continue
            pending = [(next_knot, (1 << first) | (1 << next_knot), first_bit, 1)]
            while pending:
                current, seen, change, length = pending.pop()
                for next_knot, last_bit in adjacency[current]:
                    if next_knot == first and last_bit > first_bit:
                        yield change | last_bit
                    elif (
                        next_knot > first and not ((seen >> next_knot) & 1)
                        and (bound is None or length + 1 < bound)
                    ):
                        pending.append((next_knot, seen | (1 << next_knot),
                                        change | last_bit, length + 1))


def shortest_span(adjacency, endpoints):
    """Span all ties via differences of canonical prefixes in shortest paths.

    Delete the distinction at issue. A shortest allowed change containing it
    is that distinction and a shortest path between its holders. A canonical
    shortest path supplies one generator. For every step on any shortest
    path, compare the canonical prefix plus that step with the canonical
    prefix to its destination. Each difference extends to two actual shortest
    paths by appending the same suffix. The differences telescope on any path.
    """
    pivots = {}
    shortest_sizes = []
    for first, last, removed in endpoints:
        depth = [-1] * len(adjacency)
        prefix = [0] * len(adjacency)
        depth[first] = 0
        pending = deque([first])
        while pending and depth[last] == -1:
            current = pending.popleft()
            for other, bit in adjacency[current]:
                if bit != removed and depth[other] == -1:
                    depth[other] = depth[current] + 1
                    prefix[other] = prefix[current] | bit
                    pending.append(other)
        if depth[last] == -1:
            shortest_sizes.append(None)
            continue
        shortest_sizes.append(depth[last] + 1)
        add(pivots, removed | prefix[last])
        pending = [last]
        seen = {last}
        while pending:
            current = pending.pop()
            for other, bit in adjacency[current]:
                if bit == removed or depth[other] < 0 or depth[other] + 1 != depth[current]:
                    continue
                add(pivots, prefix[other] ^ bit ^ prefix[current])
                if other not in seen:
                    pending.append(other)
                    seen.add(other)
    return pivots, shortest_sizes


def bounded_changes(endpoints):
    """Literal support-size recount by parity signatures of two halves."""
    columns = [(1 << a) ^ (1 << b) for a, b, _ in endpoints]
    catalogs = {0: {0: [0]}}
    for count in (1, 2, 3):
        catalog = defaultdict(list)
        for group in combinations(range(len(columns)), count):
            violation = 0
            for i in group:
                violation ^= columns[i]
            catalog[violation].append(mask(group))
        catalogs[count] = catalog
    for count in range(1, 6):
        small, large = catalogs[count // 2], catalogs[(count + 1) // 2]
        for violation, left_words in small.items():
            for right in large.get(violation, ()):
                left_limit = (right & -right).bit_length() - 1
                for left in left_words:
                    if left.bit_length() <= left_limit:
                        yield left | right


def literal_shortest(allowed, size):
    """Compare shortest ties using all allowed difference words on small stages."""
    best = [None] * size
    pivots = {}
    count = 0
    for word in sorted(members(allowed)[1:], key=int.bit_count):
        length = word.bit_count()
        keep = False
        for i in positions(word):
            if best[i] is None:
                best[i] = length
            if best[i] == length:
                keep = True
        if keep:
            count += 1
            add(pivots, word)
    return pivots, best, count


def read_classes(supports, allowed, law_pivots, moves):
    allowed_active = union(allowed)
    move_active = union(moves.values())
    immobile = allowed_active & ~move_active
    bits = len(allowed) - len(moves)
    local_union = set()
    for support in supports:
        restrictions = (mask(j for j, p in enumerate(support) if (m >> p) & 1)
                        for m in moves.values())
        read_basis = span(reduce_word(mask(support[j] for j in positions(word)), law_pivots)
                          for word in nullspace(restrictions, len(support)))
        local_union.update(members(read_basis.values()))
    single_knot_span = len(span(local_union))
    counts = {"class_bits": bits, "class_count": 1 << bits, "move_rank": len(moves),
              "mobile_distinction_count": move_active.bit_count(),
              "distinctions_fixed_under_rule_but_free_in_allowed_states": list(positions(immobile)),
              "bits_read_from_one_immobile_distinction": len(span(
                  reduce_word(1 << i, law_pivots) for i in positions(immobile))),
              "single_knot_span": single_knot_span,
              "bits_beyond_single_knot_span": bits - single_knot_span,
              "individually_readable_labels": len(local_union) - 1,
              "individually_unread_labels": (1 << bits) - len(local_union)}
    assert counts["bits_read_from_one_immobile_distinction"] <= single_knot_span <= bits
    return counts, local_union


def bicycle(rows, loose):
    """Use the law-side Gram equations and one coefficient pin per loose holder."""
    conditions = [mask(j for j, other in enumerate(rows) if dot(row, other)) for row in rows]
    conditions.extend(1 << j for j, row in enumerate(rows) if row & loose)
    basis = {}
    for coefficients in nullspace(conditions, len(rows)):
        word = 0
        for j in positions(coefficients):
            word ^= rows[j]
        add(basis, word)
    return basis


def coverings(word, candidate_cycles):
    """Enumerate exact covers, choosing the distinction with fewest options."""
    choices = {1 << i: [] for i in positions(word)}
    for cycle in candidate_cycles:
        for i in positions(cycle):
            choices[1 << i].append(cycle)

    @cache
    def under(remaining):
        if remaining == 0:
            return ()
        pick = min((choices[1 << i] for i in positions(remaining)), key=len)
        return tuple(cycle for cycle in pick if (cycle & remaining) == cycle)

    def complete(remaining):
        if not remaining:
            yield ()
        else:
            for cycle in under(remaining):
                for tail in complete(remaining ^ cycle):
                    yield (cycle,) + tail

    yield from complete(word)


def projected_image(functions, allowed):
    independent = span(mask(j for j, f in enumerate(functions) if dot(f, v)) for v in allowed)
    return independent


def binding_test(adjacency, elements, allowed, law_pivots, rules, parallel, count_parallel_splits):
    # Complete on the measured supports. A relation from disjoint cycles has a
    # nonzero sum, so all candidates are covered by enumerating this space.
    summary = {"elements": len(elements), "elements_with_three_part_split": 0,
               "elements_with_three_part_split_and_parallel_distinctions": 0,
               "elements_with_parallel_distinctions": 0, "parallel_elements_with_raw_splits_not_run": 0,
               "largest_split": 0, "partitions": 0}
    summaries = {rule: {"three_part_splits_all_unread_labels": 0, "minimal_relations": [],
                        "three_part_splits_all_unread_labels_using_only_mobile_distinctions": 0,
                        "elements_with_three_or_more_unread_candidate_cycles": 0,
                        "most_unread_candidate_cycles": 0}
                 for rule in rules}
    for word in elements:
        has_parallel = bool(word & parallel)
        summary["elements_with_parallel_distinctions"] += has_parallel
        if has_parallel and not count_parallel_splits:
            summary["parallel_elements_with_raw_splits_not_run"] += 1
            continue
        restricted = [tuple((j, bit) for j, bit in near if bit & word) for near in adjacency]
        parts = tuple(cycles(restricted))
        good_by_rule = {}
        for rule, (moves, local_reads) in rules.items():
            good = {part for part in parts
                    if all(not dot(m, part) for m in moves.values())
                    and reduce_word(part, law_pivots) not in local_reads}
            counts = summaries[rule]
            counts["elements_with_three_or_more_unread_candidate_cycles"] += len(good) >= 3
            counts["most_unread_candidate_cycles"] = max(counts["most_unread_candidate_cycles"], len(good))
            good_by_rule[rule] = good
        eligible = False
        for split in coverings(word, parts):
            summary["partitions"] += 1
            summary["largest_split"] = max(summary["largest_split"], len(split))
            if len(split) < 3:
                continue
            eligible = True
            for rule, good in good_by_rule.items():
                if not good.issuperset(split):
                    continue
                assert not has_parallel
                counts = summaries[rule]
                counts["three_part_splits_all_unread_labels"] += 1
                moves = rules[rule][0]
                if not (word & ~union(moves.values())):
                    counts["three_part_splits_all_unread_labels_using_only_mobile_distinctions"] += 1
                image = projected_image(split, allowed)
                if len(image) == len(split) - 1:
                    counts["minimal_relations"].append({"cycle_supports": [list(positions(c)) for c in split],
                                                         "allowed_values": sorted(members(image.values()))})
        summary["elements_with_three_part_split"] += eligible
        summary["elements_with_three_part_split_and_parallel_distinctions"] += eligible and has_parallel
    return summary, summaries


def shortest_change_of_value(adjacency, endpoints, carrier):
    """Search by holder and accumulated parity against the given carrier."""
    seeds = {a for a, b, bit in endpoints if bit & carrier}
    best = None
    for start in seeds:
        pending = deque([(start, 0, 0, 0)])
        seen = {(start, 0)}
        while pending:
            current, parity, length, change = pending.popleft()
            if best is not None and length >= best.bit_count():
                break
            if current == start and parity:
                assert change and dot(change, carrier)
                best = change
                break
            for other, bit in adjacency[current]:
                state = (other, parity ^ int(bool(bit & carrier)))
                if state not in seen:
                    pending.append((*state, length + 1, change ^ bit))
                    seen.add(state)
    return None if best is None else list(positions(best))


def read_stage(supports, verify_literal=False, named_carriers=(), positive_control=False, count_parallel_splits=True):
    adjacency, endpoints, loose = holder_table(supports)
    size = len(endpoints)
    rows = [mask(row) for row in supports]
    allowed = nullspace(rows, size)
    law_pivots = sorted(span(rows).items(), reverse=True)
    bounded = tuple(cycles(adjacency, 5))
    bounded_pivots = span(bounded)
    shortest_pivots, shortest_sizes = shortest_span(adjacency, endpoints)
    assert set(positions(union(allowed))) == {i for i, n in enumerate(shortest_sizes) if n is not None}
    checks = {}
    if verify_literal and size <= 120:
        literal = tuple(bounded_changes(endpoints))
        assert len(set(literal)) == len(literal)
        assert set(bounded) <= set(literal)
        assert len(span(literal)) == len(bounded_pivots)
        checks["all_allowed_changes_at_most_five"] = len(literal)
    if len(allowed) <= 12:
        literal_short, sizes, count = literal_shortest(allowed, size)
        assert shortest_sizes == sizes
        assert len(span([*literal_short.values(), *shortest_pivots.values()])) == len(literal_short) == len(shortest_pivots)
        checks["all_shortest_changes_through_each_distinction"] = count
        assert len(span(v for v in members(allowed) if v.bit_count() <= 5)) == len(bounded_pivots)

    readings = {}
    rules = {}
    for name, moves in zip(RULES, (shortest_pivots, bounded_pivots)):
        counts, local_reads = read_classes(supports, allowed, law_pivots, moves)
        readings[name] = counts
        rules[name] = moves, local_reads
        if named_carriers:
            readings[name]["named_carriers"] = [
                {"distinctions": list(positions(f)), "kept_by_moves": all(not dot(f, m) for m in moves.values()),
                 "read_by_one_knot": bool(reduce_word(f, law_pivots) in local_reads)} for f in named_carriers]

    basis = bicycle(rows, loose)
    joint_rank = len(span([*shortest_pivots.values(), *bounded_pivots.values()]))
    counts = Counter((a, b) for a, b, _ in endpoints if a)
    parallel = union(bit for a, b, bit in endpoints if counts[a, b] > 1)
    if positive_control:
        target = union(named_carriers)
        assert not reduce_word(target, sorted(basis.items(), reverse=True))
        elements = [target]
    else:
        elements = members(basis.values())[1:]
    relation_counts, binding = binding_test(adjacency, elements, allowed, law_pivots, rules, parallel,
                                            count_parallel_splits)
    for name in RULES:
        readings[name]["binding_test"] = binding[name]
    result = {"knots": len(supports), "distinctions": size, "allowed_bits": len(allowed),
              "loose_distinctions": loose.bit_count(),
              "distinctions_fixed_in_all_allowed_states": [i for i, n in enumerate(shortest_sizes) if n is None],
              "shortest_sizes_by_distinction": dict(Counter(n for n in shortest_sizes if n is not None)),
              "simple_cycles_at_most_five": len(bounded),
              "at_most_five_span_contains_shortest_span": joint_rank == len(bounded_pivots),
              "shortest_span_contains_at_most_five_span": joint_rank == len(shortest_pivots),
              "dim B": len(basis), "forced_supports": relation_counts, "literal_checks": checks,
              "readings": readings}
    if named_carriers:
        result["named_carrier_allowed_values"] = sorted(members(projected_image(named_carriers, allowed).values()))
        result["shortest_changes_flipping_named_carriers"] = []
        for carrier in named_carriers:
            change = shortest_change_of_value(adjacency, endpoints, carrier)
            if change is not None:
                assert dot(mask(change), carrier) and all(not dot(mask(change), row) for row in rows)
            result["shortest_changes_flipping_named_carriers"].append(change)
    return result


def json_file(path):
    return json.loads(path.read_text())


def construction_sources():
    records = json_file(LAYERS / "moves_certificates.json")
    for key in ("joining_two_five_knot_rings", "joining_two_four_knot_rings"):
        record = records[key]
        yield record["meaning"], tuple(map(tuple, record["source"]))


def named_carriers(name):
    if name.startswith("three four-knot rings whose alternating holders"):
        return tuple(mask(range(first, first + 4)) for first in (0, 4, 8))
    if name.startswith("two four-knot rings joined"):
        return mask(range(4)), mask(range(4, 8))
    if name.startswith("two five-knot rings with one shared distinction at the two holders"):
        return mask((*range(5), 10)), mask((*range(5, 10), 10))
    built_ring_counts = {"referee built 0 (9 knots)": 2, "referee built 17 (13 knots)": 3,
                         "referee built 20 (17 knots)": 4}
    if name in built_ring_counts:
        return tuple(mask(range(first, first + 4)) for first in range(0, 4 * built_ring_counts[name], 4))
    return ()


def binding_control():
    """A pre-existing three-value parity law with all carrier distinctions mobile."""
    supports = [[] for _ in range(16)]
    name = 0

    def share(first, last):
        nonlocal name
        supports[first].append(name)
        supports[last].append(name)
        name += 1

    for first in (0, 4, 8):
        for offset in range(4):
            share(first + offset, first + (offset + 1) % 4)
    for parity in (0, 1):
        for original in range(parity, 12, 2):
            share(original, 12 + 2 * parity)
            share(original, 13 + 2 * parity)
    return tuple(map(tuple, supports))


def archive_enrichment(records):
    by_rank = defaultdict(list)
    for record in records:
        for row in record["rounds"]:
            if row["round"] == 2 and "dim B" in row:
                by_rank[row["dim B"]].append(record["start"])
    chooser = random.Random(SAMPLE_SEED)
    names = {name for rank, labels in by_rank.items() if rank >= 3 for name in labels}
    for rank in (0, 1, 2):
        names.update(chooser.sample(by_rank[rank], min(32, len(by_rank[rank]))))
    return names


def stages(group, pilot):
    if group == "positive-control":
        name = "three four-knot rings whose alternating holders each meet the same two additional knots"
        supports = binding_control()
        yield name, len(supports), 0, supports, None, None
        return
    if group == "recorded-certificate":
        records = json_file(LAYERS / "moves_certificates.json")
        record = records["joining_two_four_knot_rings"]
        keys = ("after_two",) if pilot else ("source", "after_one", "after_two")
        rounds = {"source": 0, "after_one": 1, "after_two": 2}
        for key in keys:
            yield record["meaning"], 9, rounds[key], record[key], None, None
        return

    from replay_growth import grow, input_rows, sampled, start_items

    expected = {}
    if group == "witnesses":
        sources = [*construction_sources(), *start_items("witnesses")]
        if pilot:
            sources = [sources[1], sources[-1]]
        policy_rounds = 5
    elif group == "larger-draws":
        sources = []
        for size in (9, 10, 12, 16):
            for i, start in enumerate(sampled(size, 2 if pilot else 32, SAMPLE_SEED + size,
                                               max_distinctions=4 * size)):
                sources.append((f"labelled draw {size}-{i}", input_rows(*start)))
        policy_rounds = 4
    else:
        records = [json.loads(line) for path in ("forced_census.jsonl", "forced_heldout.jsonl")
                   for line in (HERE.parent / path).read_text().splitlines()]
        expected = {record["start"]: {row["round"]: row.get("dim B") for row in record["rounds"]}
                    for record in records}
        selected = archive_enrichment(records)
        for case in json_file(LAYERS / "moves_archive.json")["cases"]:
            name = case["archive"].replace("census-", "census ").replace("heldout-", "held out ")
            if name != "held out 7-239":
                selected.add(name)
        if group == "archive":
            selected = set(expected)
        sources = [(name, source) for catalog in ("census", "heldout")
                   for name, source in start_items(catalog) if name in selected]
        if pilot:
            chooser = random.Random(SAMPLE_SEED)
            sources = chooser.sample(sources, min(30, len(sources)))
        policy_rounds = 2 if group == "archive" else 4

    for name, supports in sources:
        source_knots = len(supports)
        for round_index in range(policy_rounds + 1):
            size = 1 + max(x for row in supports for x in row)
            if size > 600:
                yield name, source_knots, round_index, None, f"not read ({size} distinctions)", None
                break
            yield name, source_knots, round_index, supports, None, expected.get(name, {}).get(round_index)
            if round_index == policy_rounds:
                break
            supports, status = grow(supports)
            if status != "funded":
                yield name, source_knots, round_index + 1, None, status, None
                break


def archive_summary(cases):
    totals = {}
    exceptions = []
    for case in cases:
        round_counts = totals.setdefault(case["round"], Counter())
        if "end" in case:
            round_counts[case["end"]] += 1
            continue
        round_counts["measured stages"] += 1
        round_counts["stages with B nonzero"] += case["dim B"] > 0
        round_counts["B dimension mismatches"] += case.get("recorded_dim_B") != case["dim B"]
        round_counts["stages with three-part splits"] += case["forced_supports"]["largest_split"] >= 3
        round_counts.update(case["forced_supports"] | {"largest_split": 0})
        round_counts["largest_split"] = max(round_counts["largest_split"], case["forced_supports"]["largest_split"])
        for rule in RULES:
            reads = case["readings"][rule]
            round_counts[f"{rule}: class bits={reads['class_bits']}"] += 1
            round_counts[f"{rule}: bits beyond single-knot span={reads['bits_beyond_single_knot_span']}"] += 1
            round_counts[f"{rule}: stages with at least one individually unread label"] += bool(reads["individually_unread_labels"])
            round_counts[f"{rule}: stages with distinctions immobilized by this rule"] += bool(
                reads["distinctions_fixed_under_rule_but_free_in_allowed_states"])
            for metric in ("three_part_splits_all_unread_labels", "elements_with_three_or_more_unread_candidate_cycles"):
                round_counts[f"{rule}: {metric}"] += reads["binding_test"][metric]
        if case["dim B"] > 0 and max(r["bits_beyond_single_knot_span"] for r in case["readings"].values()) >= 2:
            exceptions.append(case)
    return totals, exceptions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=("positive-control", "recorded-certificate", "witnesses", "challenge", "archive", "larger-draws"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    begin = time.monotonic()
    cases = []
    for name, source_knots, round_index, supports, reason, expected_b in stages(args.group, args.pilot):
        identity = {"start": name, "source_knots": source_knots, "round": round_index}
        if supports is None:
            cases.append({**identity, "end": reason})
            continue
        started = time.monotonic()
        record = read_stage(supports, args.group in ("witnesses", "recorded-certificate", "positive-control"),
                            named_carriers(name), args.group == "positive-control", args.group != "larger-draws")
        if expected_b is not None:
            record["recorded_dim_B"] = expected_b
        cases.append({**identity, **record,
                      "measured_seconds": round(time.monotonic() - started, 5)})
    root = {"group": args.group, "pilot": args.pilot, "sample_seed": SAMPLE_SEED,
            "measured_seconds": round(time.monotonic() - begin, 4),
            "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.group == "archive":
        summary, exceptions = archive_summary(cases)
        root.update({"start_count": len({case["start"] for case in cases}), "counts_by_round": summary,
                     "B_nonzero_and_two_bits_beyond_single_knot_span": exceptions})
    else:
        root["cases"] = cases
    args.output.write_text(json.dumps(root, indent=1) + "\n")
    print(json.dumps({key: root[key] for key in ("group", "pilot", "sample_seed", "measured_seconds", "peak_resident_KiB")}))


if __name__ == "__main__":
    main()
