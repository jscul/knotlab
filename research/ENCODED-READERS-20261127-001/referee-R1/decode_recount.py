"""Recount every merge order from the independent word listing in choices.jsonl.gz."""
import gzip
import json
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement
from pathlib import Path

from merges import (Search, active_counts, base_kind, checks, first_decoding,
                    label_word, moves, normalized, proper_commuting_part,
                    signed_checks, unlabel)


HERE = Path(__file__).resolve().parent
EARLIER = HERE.parents[1] / "READER-SPLIT-20261127-001" / "referee-R1"


def lines(path):
    with path.open() as source:
        yield from map(json.loads, source)


def put_row(target, row):
    print(json.dumps(row, separators=(",", ":")), file=target)


def save(filename, record):
    (HERE / filename).write_text(json.dumps(record, indent=2) + "\n")


def count_steps(route):
    return (sum(f and not d for _, f, d in route),
            sum(not f and not d for _, f, d in route),
            sum(d for _, _, d in route))


def tallies(counts):
    return [[list(key) if isinstance(key, tuple) else key, count] for key, count in sorted(counts.items())]


def search_summary():
    return {"words": 0, "reachable_base": 0, "all_routes_one_base_kind": 0, "already_base": 0,
            "no_initial_merge": 0, "several_routes": 0, "several_labelled_endings": 0,
            "any_doubled": 0, "greatest_state_count": 0, "greatest_route_count": 0,
            "greatest_bound_on_original_search_calls": 0}


def add_search(s, game, search):
    outcomes = search.outcomes[game]
    ends = {e for e, _ in outcomes}
    kinds = {base_kind(e) for e in ends}
    s["words"] += 1
    s["reachable_base"] += any(k is not None for k in kinds)
    s["all_routes_one_base_kind"] += len(kinds) == 1 and None not in kinds
    s["already_base"] += base_kind(game) is not None
    s["no_initial_merge"] += not search.steps[game]
    s["several_routes"] += search.path_count[game] > 1
    s["several_labelled_endings"] += len(ends) > 1
    s["any_doubled"] += any(d for _, route in outcomes for _, _, d in route)
    s["greatest_state_count"] = max(s["greatest_state_count"], len(search.reached[game]))
    s["greatest_route_count"] = max(s["greatest_route_count"], search.path_count[game])
    # The original implementation charges even a repeated visit. It expands
    # each non-base holder multiset once and tries each concrete pair at most
    # once per expansion. Early success can only reduce this bound.
    raw_bound = 1 + sum(len(moves(state)) for state in search.reached[game])
    s["greatest_bound_on_original_search_calls"] = max(s["greatest_bound_on_original_search_calls"], raw_bound)


def measures(game, profiles, sizes):
    """One entry per attainable (base, c, move counts, full knot sizes) per word."""
    c = len(active_counts(game)) - len(game)
    return {(len(game), base_kind(end) or "irreducible outside the two base games", c,
             *count_steps(route), tuple(sorted(sizes[w] for w, _, _ in route)))
            for end, route in profiles}


def classify_record(row, archived, previous_rings, tables, mismatches, failures):
    population, index = row["population"], row["id"]
    result = {"population": population, "id": index}
    low = row["fewest"]
    state_search = Search()
    fewest, all_words = [], []
    p1 = defaultdict(lambda: {"choices": 0, "minimal": 0, "decode": 0, "kinds": Counter()})
    p2 = Counter()
    archive_comparison = {}
    local_failures = set()
    sizes = [len(s) for s in row["supports"]]
    first_sizes, any_sizes = set(), set()
    first_steps, any_steps, few_kinds, few_cs = set(), set(), set(), set()
    multi = Counter()
    for word, marked_minimal in row["words"]:
        labelled = label_word(row["supports"], row["pairs"], word)
        game = unlabel(labelled)
        state_search.explore(game)
        outcomes = state_search.outcomes[game]
        minimal = proper_commuting_part(game) is None
        assert marked_minimal == minimal
        ends = {end for end, _ in outcomes}
        kinds = {base_kind(end) for end in ends}
        decoded = any(k is not None for k in kinds)
        all_words.append((word, game))
        first_end, first_route = first_decoding(labelled, state_search)
        assert (first_end is not None) == decoded
        first = [(first_end, first_route)] if decoded else [(game, ())]
        c = len(active_counts(game)) - len(game)
        scopes = []
        if len(word) == low:
            assert minimal
            fewest.append((word, game))
            few_cs.add(c)
            few_kinds.update(k for k in kinds if k is not None)
            first_steps.add(count_steps(first_route)[:2])
            first_sizes.update(sizes[w] for w, _, _ in first_route)
            for end, route in outcomes:
                forced, shared, doubled = count_steps(route)
                if base_kind(end):
                    assert doubled == 0 and shared == 1 - c
                    any_sizes.update(sizes[w] for w, _, _ in route)
                    any_steps.add((forced, shared))
            scopes.append("fewest")
            if state_search.path_count[game] > 1:
                multi["several_routes"] += 1
            if len(ends) > 1:
                multi["several_labelled_endings"] += 1
            if population == "closure" and previous_rings[index] is None:
                tables["no_odd_ring_fewest_counts"][index] += 1
        if len(word) <= 8:
            counts = p1[len(word)]
            counts["choices"] += 1
            if minimal:
                counts["minimal"] += 1
                counts["decode"] += decoded
                counts["kinds"].update({k: 1 for k in kinds if k is not None})
                scopes.append("minimal through eight")
                if not decoded:
                    assert not state_search.steps[game]
                    local_failures.add(game)
                    put_row(failures, dict(population=population, id=index, word=word, game=game))
            else:
                scopes.append("nonminimal through eight")
                end, = state_search.forced_ends[game]
                tables["nonminimal_forced_remainders"][(population, len(word), len(end), base_kind(end))] += 1
        if row["dimension"] <= 14:
            p2["strict"] += 1
            p2["minimal"] += minimal
            p2["minimal decoding"] += minimal and decoded
            scopes.append("dimension through fourteen")
        for scope in scopes:
            section = f"{population}: {scope}"
            add_search(tables["search"].setdefault(section, search_summary()), game, state_search)
            for order, profiles in [("all", outcomes), ("first", first)]:
                table = tables["path_measurements"].setdefault((section, order), Counter())
                table.update(measures(game, profiles, sizes))
    for name, values in [("first", first_steps), ("all", any_steps)]:
        tables["fewest_move_counts"].setdefault((population, name), Counter()).update(values)
    for name, values in [("first", first_sizes), ("all", any_sizes)]:
        tables["fewest_sizes"].setdefault((population, name), Counter()).update(values)
    if fewest:
        tables["fewest_base_kinds"].setdefault(population, Counter())[tuple(sorted(few_kinds))] += 1
        for criterion in multi:
            tables["fewest_multiple_rosters"][f"{population}: {criterion}"] += 1
        archive_comparison.update({
            "fewest splits listed": len(fewest), "fewest: every one decodes":
                all(any(base_kind(e) for e, _ in state_search.outcomes[g]) for _, g in fewest),
            "fewest: kinds": sorted(few_kinds), "fewest: merges": [list(p) for p in sorted(first_steps)],
            "fewest: sizes merged through": sorted(first_sizes), "fewest: c": sorted(few_cs),
            "fewest: no doubled pair met": all(not d for _, g in fewest for _, r in state_search.outcomes[g] for _, _, d in r),
            "fewest: forced merges same under three orders": all(len(state_search.forced_ends[g]) == 1 for _, g in fewest),
            "fewest: checks hold": all(signed_checks(state) == (True, 1, 1)
                                       for _, g in fewest for state in state_search.reached[g]),
            "fewest: counting identity": all(count_steps(r)[1] == 1 + len(g) - len(active_counts(g))
                                             for _, g in fewest for e, r in state_search.outcomes[g] if base_kind(e)),
        })
        by_size = {str(k): p1[k] for k in range(low, 9)}
        archive_comparison.update({"P1 by pairs": by_size,
                                   "P1 minimal choices": sum(v["minimal"] for v in by_size.values()),
                                   "P1 decoding": sum(v["decode"] for v in by_size.values())})
        archived_failures = {normalized(g) for g in archived["P1 failures (holder pairs)"]}
        assert archived_failures <= local_failures
        if len(archived["P1 failures (holder pairs)"]) < 5:
            assert archived_failures == local_failures
        if row["dimension"] <= 14:
            archive_comparison.update({"small code: strict odd choices": p2["strict"],
                                       "small code: minimal": p2["minimal"],
                                       "small code: minimal decoding": p2["minimal decoding"]})
        for k, vals in by_size.items():
            dest = tables["by_size"].setdefault((population, int(k)), Counter())
            dest.update({key: vals[key] for key in ("choices", "minimal", "decode")})
            dest.update(vals["kinds"])
    archive_comparison["strict"] = low is not None
    for field, observed in archive_comparison.items():
        if archived[field] != observed:
            mismatches.append({"population": population, "id": index, "field": field,
                               "archive": archived[field], "recount": observed})

    # Keeping the whole decreasing search here makes every terminal remainder
    # recoverable, including ties on the reader word and on the order of merges.
    ordered = sorted(state_search.steps, key=lambda g: (len(g), g))
    lookup = {g: i for i, g in enumerate(ordered)}
    result["states"] = [[game, base_kind(game),
                         [[w, forced, doubled, lookup[child]] for w, forced, doubled, child in state_search.steps[game]]]
                        for game in ordered]
    result["words"] = [[word, lookup[g]] for word, g in all_words]
    result["fewest_routes"] = {"full_sizes_frozen_order": sorted(first_sizes),
                               "full_sizes_all_orders": sorted(any_sizes),
                               "move_counts_frozen_order": sorted(first_steps), "move_counts_all_orders": sorted(any_steps),
                               "base_kinds": sorted(few_kinds), "c": sorted(few_cs)}
    if population == "closure" and first_sizes != any_sizes:
        tables["closure_size_differences"].append([index, sorted(first_sizes), sorted(any_sizes)])
    if population == "closure" and first_steps != any_steps:
        tables["closure_move_differences"].append([index, sorted(first_steps), sorted(any_steps)])
    if population == "closure" and index == 786:
        tables["fixture_786"] = {"word_count": len(fewest), "routes": result["fewest_routes"],
                                  "words": [[w, [list(t) for t in state_search.outcomes[g]]] for w, g in fewest]}
    if population == "closure" and index == 6188:
        for w, g in fewest:
            matching = [(e, r) for e, r in state_search.outcomes[g] if any(sizes[v] == 7 for v, _, _ in r)]
            if matching:
                labelled = label_word(row["supports"], row["pairs"], w)
                first_end, first_route = first_decoding(labelled, state_search)
                end, r = min(matching)
                tables["size_seven_example"] = {"census_start_id": index, "word": w, "holders": g, "sizes": sizes,
                                               "first": [first_end, first_route],
                                               "alternative": [end, state_search.route(g, end, r)]}
                break
    return result


def recount():
    archive = {(p, r[key]): r for p, file, key in [("closure", "results.jsonl", "start"), ("type", "census_types.jsonl", "type")]
               for r in lines(HERE.parent / file)}
    rings = {r["key"]: r["length"] for r in lines(EARLIER / "ring_rows.jsonl") if r["population"] == "birth"}
    ref = {r["start"]: sum(r["all minimum strict words by shape"].values())
           for r in json.loads((EARLIER / "shapes.json").read_text())["by census start"]}
    tables = {"search": {}, "by_size": {}, "path_measurements": {}, "fewest_sizes": {}, "fewest_move_counts": {},
              "fewest_base_kinds": {}, "fewest_multiple_rosters": Counter(), "no_odd_ring_fewest_counts": Counter(),
              "closure_size_differences": [], "closure_move_differences": [], "fixture_786": None,
              "nonminimal_forced_remainders": Counter()}
    mismatches = []
    visited = set()
    with (HERE / "merge_rows.jsonl").open("w") as rows, (HERE / "merge_failures.pending").open("w") as failures:
        with gzip.open(HERE / "choices.jsonl.gz", "rt") as source:
            for row in map(json.loads, source):
                key = row["population"], row["id"]
                assert key not in visited
                visited.add(key)
                put_row(rows, classify_record(row, archive[key], rings, tables, mismatches, failures))
    (HERE / "merge_failures.pending").replace(HERE / "merge_failures.jsonl")
    assert visited == set(archive)
    no_ring = tables.pop("no_odd_ring_fewest_counts")
    assert no_ring == ref
    records = {"word_source": "choices.jsonl.gz; one vote per labelled word unless noted",
               "merge_rows_schema": {"states": "list indexed from zero; each entry [holder terms, base kind or null, legal steps]",
                                     "step": "[knot, forced, doubled, following state index]",
                                     "words": "[selected candidate-pair indices, initial state index]",
                                     "fewest_routes": "one entry per occurring size, move count or base kind across every fewest word"},
               "rosters_compared": dict(sorted(Counter(p for p, _ in visited).items())),
               "archive_field_differences": mismatches,
               "fewest_no_odd_ring": {"rosters": len(no_ring), "words": sum(no_ring.values()),
                                      "every_roster_matches_earlier_referee": no_ring == ref},
               "by_size": {f"{pop} {n} pairs": v for (pop, n), v in sorted(tables.pop("by_size").items())}}
    paths = tables.pop("path_measurements")
    records["path_measures_fields"] = ["pairs", "base or other ending", "c", "forced ordinary merges", "other ordinary merges",
                                       "doubled removals", "full sizes at all knots merged through, repeated per step"]
    records["path_measures_weighting"] = ("One vote per word admitting the given profile. A word can have multiple profiles "
                                          "in the all-orders table. The first table selects by original knot and setting labels.")
    records["path_measurements"] = {f"{section}, {order}": tallies(v) for (section, order), v in sorted(paths.items())}
    for key in ("fewest_sizes", "fewest_move_counts"):
        records[key + "_one_vote_per_roster_per_value"] = {
            f"{p}, {o}": tallies(v) for (p, o), v in sorted(tables.pop(key).items())}
    records["fewest_base_kinds_one_vote_per_roster"] = {p: tallies(v) for p, v in tables.pop("fewest_base_kinds").items()}
    records["nonminimal_forced_remainders_population_initial_pairs_terminal_pairs_kind"] = tallies(tables.pop("nonminimal_forced_remainders"))
    records.update(tables)
    save("merge_summary.json", records)
    return records


def three_on(a, b, c, d):
    return normalized([((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))])


def all_base_parts(game):
    parts = []
    for i in range(3, len(game) + 1, 2):
        for subset in combinations(range(len(game)), i):
            if base_kind(tuple(game[j] for j in subset)) is not None:
                parts.append(sum(1 << j for j in subset))
    return parts


def base_partitions(game):
    parts = all_base_parts(game)

    def cover(left):
        if not left:
            yield ()
            return
        first = left & -left
        for p in parts:
            if (first & p) and (p & left) == p:
                for rest in cover(left ^ p):
                    yield (p, *rest)

    return list(cover((1 << len(game)) - 1))


def nonconfluent_example():
    p, q, a, b, c, d, e, f, w = range(9)
    all_three = normalized([*three_on(p, q, a, b), *three_on(p, q, c, d), *three_on(p, q, e, f)])
    terms = list(all_three)
    for i, j in ((a, b), (c, d)):
        terms.remove(((p, q), (i, j)))
        terms.extend([((p, q), (w, i)), ((p, q), (w, j))])
    game = normalized(terms)
    s = Search()
    s.explore(game)
    endpoints = []
    for end in sorted({end for end, _ in s.outcomes[game]}):
        parts = all_base_parts(end)
        covers = base_partitions(end)
        single_base = base_kind(end)
        assert len(end) == 9 and not s.steps[end] and single_base is None
        residue = None
        if len(parts) == 1:
            rest = tuple(t for j, t in enumerate(end) if not (parts[0] >> j) & 1)
            residue = {"terms": rest, "commuting_and_two_signs": signed_checks(rest),
                       "proper_commuting_part": proper_commuting_part(rest),
                       "number_of_legal_moves": len(moves(rest)), "base_partitions": base_partitions(rest)}
            assert len(rest) == 6 and signed_checks(rest) == (True, 0, 0) and not moves(rest) and not base_partitions(rest)
        endpoints.append({"terms": end, "equals_three_original_games": end == all_three, "base_parts": len(parts),
                          "single_base": single_base, "partitions_into_bases": len(covers), "six_pair_part": residue})
    assert sorted(e["partitions_into_bases"] for e in endpoints) == [0, 0, 1]
    return {"initial": game, "commuting_and_two_signs": signed_checks(game), "distinct_states": len(s.steps),
            "routes": s.path_count[game], "terminal_remainders": endpoints}


def short_odd_games():
    result = {}
    for k in (1, 2, 3):
        tried, odd = Counter(), Counter()
        # Fewer than four holders cannot support even one strict pair. Once
        # singleton holders are excluded, 4k appearances give at most 2k knots.
        for n in range(4, 2 * k + 1):
            terms = [t for fours in combinations(range(n), 4) for t in three_on(*fours)]
            for game in combinations_with_replacement(sorted(terms), k):
                counts = active_counts(game)
                if len(counts) != n or min(counts.values()) < 2:
                    continue
                tried[n] += 1
                if signed_checks(game) == (True, 1, 1):
                    odd[n] += 1
                    assert base_kind(game) == "three-reader game"
        result[str(k)] = {"labelled_holder_multisets_with_every_knot_used_at_least_twice": dict(tried),
                          "odd_commuting": dict(odd)}
    return result


def odd_ring_around_a_knot(game):
    adjacent = defaultdict(set)
    for term in game:
        for u, v in term:
            adjacent[u].add(v)
            adjacent[v].add(u)
    for centre, inner in adjacent.items():
        colour = {}
        for start in inner:
            if start in colour:
                continue
            colour[start] = 0
            todo = [start]
            while todo:
                v = todo.pop()
                for u in adjacent[v] & inner:
                    if u not in colour:
                        colour[u] = 1 - colour[v]
                        todo.append(u)
                    elif colour[u] == colour[v]:
                        return centre
    return None


def nine_knot_example():
    terms = [((0, 4), (1, 3)), ((1, 5), (2, 4)), ((2, 3), (0, 5)),
             ((3, 7), (4, 6)), ((4, 8), (5, 7)), ((5, 6), (3, 8)),
             ((2, 6), (0, 7)), ((1, 7), (2, 8)), ((0, 8), (1, 6))]
    game = normalized(terms)
    search = Search()
    search.explore(game)
    assert proper_commuting_part(game) is None and not moves(game) and base_kind(game) is None
    assert odd_ring_around_a_knot(game) is None
    return {"terms": game, "active_sizes": sorted(active_counts(game).values()),
            "commuting_and_two_signs": signed_checks(game), "proper_commuting_part": proper_commuting_part(game),
            "moves": len(moves(game)), "base": base_kind(game), "odd_ring_common_knot": odd_ring_around_a_knot(game)}


def ring_fixtures():
    result = {}
    for row in lines(EARLIER / "rebuilt_inputs.jsonl"):
        if row["population"] != "fixture" or row["key"] not in ("ring of three's closure", "ring of five's closure"):
            continue
        # Enumerate distinct matchings of actual distinctions in the two fixture
        # holdings. Both the empty choice and leaving a setting unused are legal.
        data = row["supports"], row["pairs"]
        by_first = defaultdict(list)
        distinctions = sorted({d for knot in row["supports"] for d in knot})
        for i, (a, b) in enumerate(row["pairs"]):
            by_first[min(a, b)].append((i, max(a, b)))
        accepted = []

        def match(left, word):
            if left:
                first, *later = left
                match(later, word)
                for i, other in by_first[first]:
                    if other in later:
                        match([d for d in later if d != other], (*word, i))
            else:
                game = unlabel(label_word(*data, word))
                if signed_checks(game) == (True, 1, 1):
                    accepted.append({"word": sorted(word), "holders": game, "base": base_kind(game),
                                     "moves": len(moves(game))})

        match(distinctions, ())
        assert len(accepted) == 1 and accepted[0]["base"] and accepted[0]["moves"] == 0
        result[row["key"]] = accepted
    assert len(result) == 2
    return result


def sector_dimensions():
    # Readers 0/1 and 2/3 duplicate the two original X settings. Both pairs
    # of Z copies contribute to the check at knot 4. Keep this setting order.
    terms = (((0, 1), (2, 4)), ((0, 1), (3, 4)), ((0, 2), (1, 4)), ((0, 2), (3, 4)), ((0, 3), (1, 2)))
    assert signed_checks(terms) == (True, 1, 1)
    at = checks(terms)
    # Multiply exact projectors (I ± P)/2 and take their trace. Here the
    # commuting check signs are minus at 0 and plus elsewhere.
    signed = [(x, z, -1 if u == 0 else 1) for u, (x, z) in sorted(at.items())]

    def dimension(constraints):
        trace = 0
        for basis in range(1 << len(terms)):
            vector = [0] * (1 << len(terms))
            vector[basis] = 1
            for x, z, sign in constraints:
                next_v = vector.copy()
                for j, a in enumerate(vector):
                    next_v[j ^ x] += a * sign * (-1 if (j & z).bit_count() % 2 else 1)
                vector = next_v
            trace += vector[basis]
        divisor = 1 << len(constraints)
        assert trace % divisor == 0
        return trace // divisor

    joint = dimension(signed)
    sectors = {str(direction): dimension([*signed, (0, 3, direction)]) for direction in (1, -1)}
    assert joint == 2 and list(sectors.values()) == [1, 1]
    return {"readers_X_then_Z": terms, "shared_knot": 4, "joint_check_signs": [-1, 1, 1, 1, 1],
            "joint_dimension": joint, "dimensions_by_Z0_Z1_eigenvalue": sectors}


def cap_witnesses():
    source = json.loads((HERE / "choices_size_stress.json").read_text())
    result = []
    for pop, rows in source["eligible cases"].items():
        for row in rows:
            sample = row.get("first_minimal")
            if not sample:
                continue
            game = normalized(sample["holders"])
            s = Search()
            s.explore(game)
            assert proper_commuting_part(game) is None
            result.append({"population": pop, "id": row["id"], "pairs": len(game), "knots": len(active_counts(game)),
                           "holders": game, "proper_commuting_part": proper_commuting_part(game),
                           "initial_moves": len(s.steps[game]),
                           "terminal_base_kinds": sorted({base_kind(e) for e, _ in s.outcomes[game]}, key=lambda k: k or ""),
                           "commuting_and_two_signs": signed_checks(game)})
    return result


def controls():
    ring = normalized([((5, j), ((j + 2) % 5, (j + 3) % 5)) for j in range(5)])
    wrong = normalized([((5, j), ((j + 1) % 5, (j + 2) % 5)) for j in range(5)])
    assert base_kind(ring) == "ring game of 5"
    assert active_counts(ring) == active_counts(wrong) and base_kind(wrong) is None
    assert not signed_checks(wrong)[0]
    duplicate = normalized([((0, 1), (2, 3))] * 2)
    assert signed_checks(duplicate) == (True, 0, 0)
    assert len(moves(duplicate)) == 4 and all(m.doubled and m.child == () for m in moves(duplicate))
    try:
        label_word([[0, 2], [0, 2], [1, 3], [1, 3]], [(0, 1), (0, 3)], [0, 1])
    except ValueError:
        rejected_reused_setting = True
    else:
        raise AssertionError("a repeated setting passed the strictness test")
    try:
        checks(normalized([((0, 1), (1, 2))]))
    except ValueError:
        rejected_joint_holding = True
    else:
        raise AssertionError("a reader had both settings at one knot")
    return {"ring_with_wrong_partners": {"same_active_counts": active_counts(ring) == active_counts(wrong),
                                         "base": base_kind(wrong), "commuting_and_two_signs": signed_checks(wrong)},
            "two_equal_terms": {"active_knots": len(active_counts(duplicate)), "pairs": len(duplicate), "moves": len(moves(duplicate)),
                                "all_drop_both": all(m.doubled and not m.child for m in moves(duplicate))},
            "same_distinction_reused_in_two_terms_rejected": rejected_reused_setting,
            "two_settings_at_one_knot_rejected": rejected_joint_holding}


def main():
    record = recount()
    fixtures = {"order_changes_the_remainder": nonconfluent_example(), "through_three_pairs": short_odd_games(),
                "nine_knots_nine_pairs": nine_knot_example(), "archived_ring_fixtures": ring_fixtures(),
                "grown_fixture_at_census_index_786": record["fixture_786"], "operator_sectors": sector_dimensions(),
                "post_frozen_cap_witnesses": cap_witnesses(), "negative_controls": controls()}
    save("merge_fixtures.json", fixtures)
    print(json.dumps({"compared": record["rosters_compared"], "archive_field_differences": len(record["archive_field_differences"]),
                      "closures_with_more_knot_sizes_in_other_orders": len(record["closure_size_differences"])}))


if __name__ == "__main__":
    main()
