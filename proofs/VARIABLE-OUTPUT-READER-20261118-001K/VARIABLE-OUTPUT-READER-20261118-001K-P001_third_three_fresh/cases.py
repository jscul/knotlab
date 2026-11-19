"""Replay the two frozen minima and test marked distance-table symmetries."""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import sys


PROOFS = Path(__file__).resolve().parents[2]
J = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001J" / "VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six"
SPEC = spec_from_file_location("third_three_fresh_predecessor", J / "search.py")
reader = module_from_spec(SPEC)
SPEC.loader.exec_module(reader)
literal, prior = reader.literal, reader.prior


def load_source(name):
    return json.loads((J / name).read_text())


def named(rows):
    return tuple((str(i), tuple(row)) for i, row in enumerate(rows))


def choices(history, sizes):
    holders, neighbors = literal.incidence(history)
    loose = sorted(bit for bit, sites in holders.items() if len(sites) == 1)
    return [group for size in sizes for group in combinations(loose, size)
            if literal.legal(tuple(holders[bit][0] for bit in group), neighbors)]


def extend(history, group, outputs):
    return reader.named_step(history, group, outputs, len(literal.incidence(history)[0]))


def exceptional_replay(history):
    trace = reader.replay(history)
    sizes = [(len(step["operands"]), len(step["fresh"])) for step in trace]
    assert sizes[:3] == [(0, 3), (1, 3), (1, 3)]
    exceptional, = (step for step in trace[3:] if len(step["fresh"]) == 3)
    assert len(exceptional["operands"]) == 3
    assert all(p in (2, 3) and h in (2, 3) for p, h in sizes[3:])
    assert all(len(step["frontier"]) <= 7 for step in trace)
    return trace, exceptional


def space_check(table, history):
    through_K5 = {pair: value if value <= 5 else None for pair, value in table.items()}
    width = len(literal.incidence(history)[0])
    short, uncertain, _, _ = prior.force_from_table(through_K5, width, 5)
    physical = prior.span(reader.mask(row) for _, row in history)
    assert short <= physical
    return {"forced_rank_from_D4": prior.rank(short), "unresolved_K5_bonds": len(uncertain),
            **reader.certificate(table, history)}


def table_record(history, is_exceptional=True, independent=True):
    replay, cap = exceptional_replay(history) if is_exceptional else (reader.replay(history), None)
    table, bonds, menu = reader.measure(history, independent=independent)
    width = len(literal.incidence(history)[0])
    assert all(reader.mask(row) in bonds for _, row in history)
    result = {"width": width, "sites": len(history), "history": replay, "exceptional_site": cap,
              "equation_forcing": space_check(table, history), "legal_triples": sorted(menu),
              "pair_count": len(table), "K_histogram": dict(sorted(Counter(table.values()).items())),
              "K_upper_triangle": [table[pair] for pair in combinations(range(width), 2)],
              "isometry_groups": {label: reader.lift_group(reader.matrix(table, cutoff), menu)[1]
                                  for label, cutoff in (("D4", 5), ("D5", 6), ("full", None))}}
    if cap:
        result["input_output_K"] = [(a, b, table[tuple(sorted((a, b)))])
                                    for a in cap["operands"] for b in cap["fresh"]]
    return result, table, menu


def transposition(table, menu, width, swap, mark):
    image = list(range(width))
    a, b = swap
    image[a], image[b] = b, a

    def renamed(group):
        return tuple(sorted(image[x] for x in group))

    forbidden = renamed(mark)
    assert mark in menu and forbidden not in menu
    mismatch = [(pair, table[pair], table[renamed(pair)]) for pair in sorted(table)
                if table[pair] != table[renamed(pair)]]
    counts = {f"D{d}": sum(min(x, d + 2) != min(y, d + 2) for _, x, y in mismatch)
              for d in (3, 4, 5)}
    return {"swap": swap, "permutation": image, "legal_mark": mark, "forbidden_image": forbidden,
            "all_pair_entries_checked": len(table), "changed_entries": {**counts, "full": len(mismatch)},
            "exact_changed_entries": mismatch}


def six_bond_control(prefix, cap, lower_support):
    result = []
    for outputs in (2, 3):
        history = extend(prefix, cap, outputs)
        recorded, table, _ = table_record(history, is_exceptional=outputs == 3)
        support = tuple(lower_support) if outputs == 2 else history[-1][1]
        code = prior.span(reader.mask(row) for _, row in history)
        word = reader.mask(support)
        assert word in code and not any(v not in (0, word) and v & word == v for v in code)
        assert (support == history[-1][1]) == (outputs == 3)
        values = [(pair, table[tuple(sorted(pair))]) for pair in combinations(support, 2)]
        result.append({"fresh_at_cap": outputs, "width": recorded["width"], "support": support,
                       "is_physical_site": support == history[-1][1], "pair_values": values,
                       "K_histogram_within_support": dict(sorted(Counter(k for _, k in values).items())),
                       "rank_forcing": recorded["equation_forcing"]})
    return result


def minimum_arm(record):
    prefix = named((row["inputs"] + row["fresh"] for row in record["history"][:-1]))
    caps = choices(prefix, (3,))
    assert len(literal.incidence(prefix)[0]) == 19
    assert caps == [tuple(group) for group in record["legal_triples_before"]]
    layer = [((cap,), extend(prefix, cap, 3)) for cap in caps]
    by_depth = []
    for depth in range(3):
        force_counts, permits = Counter(), Counter()
        named_sets = set()
        tables = sha256()
        renamed_entries = 0
        successors = []
        for route, history in layer:
            trace, cap = exceptional_replay(history)
            assert cap == trace[8]
            table, _, menu = reader.measure(history)
            renamed_entries += reader.relabel_control(history, table, menu)["all_pair_entries_checked"]
            force = space_check(table, history)
            key = tuple(force[k] for k in ("forced_rank_from_D4", "unresolved_K5_bonds",
                                           "forced_rank_from_K6", "unresolved_short_bonds",
                                           "spaces_matching_K6", "spaces_matching_full_table"))
            force_counts[key] += 1
            permits[len(menu)] += 1
            named_sets.add(frozenset(reader.mask(row) for _, row in history))
            code = [route, sorted(table.items()), sorted(menu)]
            tables.update(json.dumps(code, separators=(",", ":")).encode() + b"\n")
            if depth < 2:
                successors.extend(((*route, group), extend(history, group, 2))
                                  for group in choices(history, (2, 3)))
        by_depth.append({"two_fresh_steps_after_cap": depth, "width": 22 + 2 * depth,
                         "literal_histories": len(layer), "distinct_named_support_sets": len(named_sets),
                         "summary_by_legal_triple_count": dict(sorted(permits.items())),
                         "ranks_and_rival_spaces": [(*values, count) for values, count in sorted(force_counts.items())],
                         "renamed_pair_entries_checked": renamed_entries,
                         "paths_and_tables_sha256": tables.hexdigest()})
        layer = successors
    return {"prefix_supports": [row for _, row in prefix], "cap_operand_choices": caps,
            "named_six_bond_control": six_bond_control(prefix, tuple(record["initial_triple_join"]),
                                                       record["after"]["large_short_cuts"][0]["boundary"]),
            "by_depth": by_depth}


def physical_realizations(code):
    bonds = []
    for word in sorted(code - {0}, key=lambda w: (w.bit_count(), w)):
        if word.bit_count() > 6:
            break
        if all(word & smaller != smaller for smaller in bonds):
            bonds.append(word)
    seed, = (word for word in bonds if word.bit_count() == 3)
    stars = [word for word in bonds if word != seed and (word & seed).bit_count() <= 1]
    initial = frozenset((seed,))
    queue = [initial]
    seen = {initial: (seed,)}
    completed = []
    rank = prior.rank(code)
    for state in queue:
        if len(state) == rank:
            assert prior.span(state) == code
            finished = named(reader.bits(word) for word in seen[state])
            literal.replay(finished)
            completed.append(finished)
            continue
        holders, neighbors = literal.incidence(named(reader.bits(word) for word in sorted(state)))
        for word in stars:
            if word in state:
                continue
            old = tuple(bit for bit in reader.bits(word) if bit in holders)
            if word.bit_count() - len(old) not in (2, 3) or any(len(holders[i]) != 1 for i in old):
                continue
            if not literal.legal(tuple(holders[i][0] for i in old), neighbors):
                continue
            nxt = state | {word}
            if nxt not in seen:
                seen[nxt] = (*seen[state], word)
                queue.append(nxt)
    return completed, {"candidate_nonseed_stars": len(stars), "reachable_prefix_sets": len(queue),
                       "largest_prefix_rank": max(map(len, queue)), "completed_support_sets": len(completed)}


def resolve_short_table(history, table):
    width = len(literal.incidence(history)[0])
    visible = {pair: value if value <= 6 else None for pair, value in table.items()}
    known, residual, allowed, _ = prior.force_from_table(visible, width, 6)
    spaces, full, _ = prior.all_compatible_spaces(table, width, known, residual, allowed)
    assert len(spaces) == 10 and len(full) == 1
    physical = prior.span(reader.mask(row) for _, row in history)
    results = []
    for code in spaces:
        histories, tested = physical_realizations(code)
        completed = []
        for realized in histories:
            result, alt_table, menu = table_record(realized)
            assert all(min(k, 7) == min(alt_table[p], 7) for p, k in table.items())
            assert not menu
            completed.append({"source": result, "compared_to_original": reader.difference(table, alt_table),
                              "exact_changed_entries": [(p, k, alt_table[p])
                                                        for p, k in sorted(table.items()) if k != alt_table[p]]})
        results.append({"physical_source_space": code == physical,
                        "new_equation": reader.bits(min(code - known, key=lambda w: (w.bit_count(), w))),
                        "all_rival_ranks": tested, "realizations": completed})
    assert sum(bool(result["realizations"]) for result in results) == 2
    assert all(len(result["realizations"]) <= 1 for result in results)
    return results


def descendants_of_short_table_mates(source, rival):
    spec = spec_from_file_location("third_three_fresh_frontier", J / "frontier.py")
    frontiers = module_from_spec(spec)
    spec.loader.exec_module(frontiers)
    results = []
    for history in (source, rival):
        rows = tuple(row for _, row in history)
        initial, _, _ = frontiers.literal_snapshot(rows)
        queue = [initial]
        reached = {initial: rows}
        tally = Counter()
        live = []
        for node in queue:
            current = reached[node]
            normalized, active, loose = frontiers.literal_snapshot(current)
            assert normalized == node
            legal = frontiers.old.verify_literal_moves(current, node, active, loose)
            parents = [group for group in sorted(legal) if len(group) in (2, 3)]
            tally.update(map(len, parents))
            if any(len(group) == 3 for group in parents):
                live.append(current)
            for group in parents:
                nxt = frontiers.step(node, group, 2)
                grown = frontiers.advance(current, tuple(active[i] for i in group), 2)
                assert frontiers.literal_snapshot(grown)[0] == nxt
                if nxt not in reached:
                    reached[nxt] = grown
                    queue.append(nxt)
        results.append({"reachable_normalized_frontiers": len(queue), "legal_moves_by_parent_count": dict(tally),
                        "frontiers_with_legal_triples": len(live),
                        "first_live": table_record(named(live[0]), independent=False)[0] if live else None})
    return results


def short_table(history, width):
    dual = prior.span(reader.mask(row) for _, row in history)
    words = {word for word in dual if word.bit_count() <= 6}
    table, _ = prior.pair_minima(words, tuple(combinations(range(width), 2)), cutoff=6)
    return {pair: value if value is not None else 7 for pair, value in table.items()}


def two_parent_successors(history):
    holders, neighbors = literal.incidence(history)
    first_loose = {}
    for bit, users in sorted(holders.items()):
        if len(users) == 1:
            first_loose.setdefault(users[0], bit)
    # Exchanging two loose bits at the same holder fixes every old support.
    return [extend(history, tuple(first_loose[site] for site in parents), 2)
            for parents in combinations(first_loose, 2) if literal.legal(parents, neighbors)]


def compare_path_to_live(source, rival, live):
    target = named(row["support"] for row in live["history"])
    assert target[:len(source)] == source
    layer = [(rival, True)]
    results = []
    first_separation = None
    for sites in range(len(source), len(target) + 1):
        current = target[:sites]
        width = len(literal.incidence(current)[0])
        primary = short_table(current, width)
        row = Counter(histories=len(layer), named_D5_matches=0, continuously_D5_matching=0)
        next_layer = []
        for option, previously_matched in layer:
            alternate = short_table(option, width)
            for k in (3, 4, 5, 6):
                image = reader.one_isometry(primary, alternate, k)
                row[f"D{k - 1}_isometric"] += image is not None
            agrees = image is not None
            row["named_D5_matches"] += primary == alternate
            row["continuously_D5_matching"] += agrees and previously_matched
            if sites < len(target):
                next_layer.extend((nxt, agrees and previously_matched) for nxt in two_parent_successors(option))
        results.append({"width": width, "two_fresh_steps": sites - len(source), **dict(row)})
        if not row["D5_isometric"] and first_separation is None:
            (option, _), = layer
            full_original = reader.measure(current)[0]
            full_alternate = reader.measure(option)[0]
            assert primary == {pair: min(k, 7) for pair, k in full_original.items()}
            assert alternate == {pair: min(k, 7) for pair, k in full_alternate.items()}

            def profile(table):
                matrix = reader.matrix(table, 6)
                return Counter(tuple(row.count(k) for k in range(3, 8)) for row in matrix)

            left, right = profile(primary), profile(alternate)
            first_separation = {"width": width, "last_source_support": current[-1][1],
                                "last_rival_support": option[-1][1],
                                "named_D5_differences_with_exact_K": [(p, full_original[p], full_alternate[p])
                                                                       for p in sorted(primary) if primary[p] != alternate[p]],
                                "row_profile_K_values_in_order": (3, 4, 5, 6, "pooled larger"),
                                "source_row_profiles_in_excess": sorted((left - right).items()),
                                "rival_row_profiles_in_excess": sorted((right - left).items()),
                                "full_pair_comparison": reader.difference(full_original, full_alternate)}
        layer = next_layer
    assert [row["histories"] for row in results] == [1, 1, 1, 1, 2, 6, 10]
    assert first_separation["width"] == 30
    assert all(row["D3_isometric"] == 0 for row in results[2:])
    return {"along_first_live_path": results, "first_short_table_separation": first_separation}


def live_arms(old):
    original = named(old["junction_supports"])
    prefix = original[:-1]
    cap = original[-1][1][:3]
    upgraded = extend(prefix, cap, 3)
    source, table, menu = table_record(upgraded)
    matched, control_table, control_menu = table_record(original, is_exceptional=False)
    swap = tuple(old["transposition"])
    mark = tuple(old["legal_mark"])
    defect = transposition(table, menu, source["width"], swap, mark)
    control = transposition(control_table, control_menu, matched["width"], swap, mark)
    assert defect["changed_entries"] == {"D3": 0, "D4": 0, "D5": 10, "full": 10}
    assert control["changed_entries"] == {"D3": 0, "D4": 8, "D5": 16, "full": 24}
    assert defect["forbidden_image"] == tuple(old["forbidden_image"])
    assert not source["isometry_groups"]["D5"]["opposing"]
    assert source["equation_forcing"]["spaces_matching_K6"] == 1
    users, _ = literal.incidence(upgraded)
    a, b = swap
    assert users[a] == [users[b][0], source["exceptional_site"]["site"]]

    # The other live case uses the same cap immediately before one binary continuation.
    earlier_cap = extend(prefix[:-1], cap, 3)
    alternate = extend(earlier_cap, (12, 20), 2)
    live_after, other_table, other_menu = table_record(alternate)
    assert (14, 21, 24) in other_menu
    control_record = {"source": matched, "transposition_test": control}
    mark_record = {"source": source, "transposition_test": defect}
    successors = []
    for group in sorted(menu):
        grown = extend(upgraded, group, 2)
        recorded, grown_table, _ = table_record(grown)
        ambiguity = resolve_short_table(grown, grown_table)
        successors.append({"source": recorded, "matching_D5_space_realizations": ambiguity})

    first_successor = extend(upgraded, min(menu), 2)
    # The replay of this mate registers its preserved labels in reverse birth order.
    rival = (*prefix, ("10", (*min(menu), 26, 27)), ("11", (10, 19, 22, 23, 24, 25)))
    first_dual = prior.span(reader.mask(row) for _, row in first_successor)
    rival_dual = prior.span(reader.mask(row) for _, row in rival)
    assert first_dual != rival_dual
    mates = [item for item in successors[0]["matching_D5_space_realizations"]
             if not item["physical_source_space"] and item["realizations"]]
    mate, = mates[0]["realizations"]
    assert {frozenset(step["support"]) for step in mate["source"]["history"]} == {frozenset(row) for _, row in rival}
    future = descendants_of_short_table_mates(first_successor, rival)
    assert future[1]["frontiers_with_legal_triples"] == 0
    comparison = compare_path_to_live(first_successor, rival, future[0]["first_live"])
    return {"upgraded_late_cap": mark_record, "predecessor_matched_control": control_record,
            "earlier_cap_with_binary_continuation": live_after,
            "two_live_tables_compared": reader.difference(table, other_table),
            "late_cap_legal_triple_successors": successors,
            "future_reachability_of_named_width28_mates": future, "continuation_table_comparison": comparison}


def main():
    old = load_source("frontier.json")["sharp_distance_four"]
    live = live_arms(old)
    original = load_source("suffix_windows.json")["replayed_minimum_sources"]
    minimum = {}
    for name, record in original.items():
        minimum[name] = minimum_arm(record)
        count = [d["literal_histories"] for d in minimum[name]["by_depth"]]
        print(f"{name}: {count}", file=sys.stderr, flush=True)
    print(json.dumps({"frozen_prediction_commit": "6cdf479753",
                      "K_definition": "K is the minimum bond support size, equal to D+1.",
                      "ranks_and_rival_spaces_columns": ["forced_rank_D4", "unresolved_bonds_D4",
                                                         "forced_rank_D5", "unresolved_bonds_D5",
                                                         "spaces_compatible_D5", "full_compatible_spaces", "histories"],
                      "distance_table_order": "Lexicographic unordered distinction pairs, starting at 0.",
                      "minimum_arms": minimum, "live_arms": live}, indent=2))


if __name__ == "__main__":
    main()
