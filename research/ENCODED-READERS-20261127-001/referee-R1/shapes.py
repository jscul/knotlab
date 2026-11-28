"""Exact relabelling of terminal games and the independent cell reading."""

import gzip
import json
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import chain, combinations, permutations, product
from pathlib import Path


DIRECTORY = Path(__file__).resolve().parent


def unordered(left, right):
    return (left, right) if left < right else (right, left)


def game_from_pairs(pairs):
    game = []
    for left, right in pairs:
        assert len(left) == len(right) == 2 and len({*left, *right}) == 4
        game.append(unordered(unordered(*left), unordered(*right)))
    return tuple(sorted(game))


def relabel(game, labels):
    return game_from_pairs(
        ((labels[a], labels[c]), (labels[b], labels[d]))
        for (a, c), (b, d) in game
    )


@lru_cache(maxsize=None)
def canonical(game):
    """Try every permutation within each invariant class, compare full pair lists."""
    at_knot = defaultdict(list)
    for (a, c), (b, d) in game:
        for knot, opposite, near1, near2 in ((a, c, b, d), (c, a, b, d),
                                             (b, d, a, c), (d, b, a, c)):
            at_knot[knot].append((opposite, near1, near2))
    colors = dict.fromkeys(at_knot, 0)
    while True:
        signatures = {}
        for knot, triples in at_knot.items():
            local = sorted((colors[o], unordered(colors[b], colors[d])) for o, b, d in triples)
            signatures[knot] = (colors[knot], tuple(local))
        palette = {s: i for i, s in enumerate(sorted(set(signatures.values())))}
        refined = {knot: palette[s] for knot, s in signatures.items()}
        if len(palette) == len(set(colors.values())):
            colors = refined
            break
        colors = refined
    groups = defaultdict(list)
    for knot, color in sorted(colors.items()):
        groups[color].append(knot)
    best = None
    witness = None
    for order in product(*(permutations(groups[color]) for color in sorted(groups))):
        labels = {knot: i for i, knot in enumerate(chain.from_iterable(order))}
        candidate = relabel(game, labels)
        if best is None or candidate < best:
            best = candidate
            witness = tuple(sorted(labels.items()))
    return best, witness


def knots_of(game):
    return sorted({knot for pair in game for setting in pair for knot in setting})


def ring(size):
    assert size >= 3 and size % 2 == 1
    shift = size // 2
    return game_from_pairs(((size, i), ((i + shift) % size, (i - shift) % size))
                           for i in range(size))


@lru_cache(maxsize=None)
def is_base(game):
    size = len(game)
    if size < 3 or size % 2 == 0 or len(knots_of(game)) != size + 1:
        return False
    return canonical(game)[0] == canonical(ring(size))[0]


@lru_cache(maxsize=None)
def admits_merge(game):
    mates = defaultdict(list)
    for left, right in game:
        mates[left].append(right)
        mates[right].append(left)
    return any(set(x) & set(y) for choices in mates.values() for x, y in combinations(choices, 2))


def pauli_sign(game, order):
    """Accumulate the exponent when commuting Z past X in the check product."""
    x_settings = Counter()
    z_settings = Counter()
    for reader, (x, z) in enumerate(game):
        for knot in x:
            x_settings[knot] |= 1 << reader
        for knot in z:
            z_settings[knot] |= 1 << reader
    seen_x = seen_z = sign = 0
    for knot in order:
        assert not (x_settings[knot] & z_settings[knot])
        sign ^= (seen_z & x_settings[knot]).bit_count() % 2
        seen_x ^= x_settings[knot]
        seen_z ^= z_settings[knot]
    assert seen_x == seen_z == 0
    return sign


def commutation_subsets(game):
    """Enumerate every subcollection using the four covered knot pairs of each reader."""
    sums = Counter({frozenset(): 1})
    for left, right in game:
        column = frozenset(unordered(a, b) for a, b in product(left, right))
        sums.update({key ^ column: count for key, count in sums.items()})
    whole = set()
    for left, right in game:
        whole.symmetric_difference_update(unordered(a, b) for a, b in product(left, right))
    return not whole, sums[frozenset()] - 1 - (not whole)


def walks_of(game):
    return [(a, b, c, d) for (a, c), (b, d) in game]


def components(adjacencies):
    remaining = set(adjacencies)
    parts = []
    while remaining:
        start = min(remaining)
        reached = {start}
        todo = [start]
        while todo:
            fresh = set(adjacencies[todo.pop()]) - reached
            reached.update(fresh)
            todo.extend(fresh)
        parts.append(sorted(reached))
        remaining -= reached
    return parts


def cell_data(walks):
    coverage = defaultdict(list)
    links = defaultdict(lambda: defaultdict(list))
    for index, walk in enumerate(walks):
        for j, knot in enumerate(walk):
            previous, following = walk[j - 1], walk[(j + 1) % 4]
            coverage[unordered(knot, following)].append((index, knot < following))
            links[knot][previous].append(following)
            links[knot][following].append(previous)
    return coverage, links


def read_cells(walks, normalize=True):
    coverage, links = cell_data(walks)
    histogram = Counter(map(len, coverage.values()))
    assert histogram == {2: len(coverage)}
    assert all(len(mates) == 2 for local in links.values() for mates in local.values())
    local_parts = {knot: components(local) for knot, local in sorted(links.items())}
    pairs = []
    dual = {i: set() for i in range(len(walks))}
    for (a, asc), (b, bsc) in coverage.values():
        pairs.append((a, b, asc == bsc))
        dual[a].add(b)
        dual[b].add(a)
    reversals = Counter()
    for flip in range(1 << len(walks)):
        same = sum(equal ^ ((flip >> a) & 1) ^ ((flip >> b) & 1) for a, b, equal in pairs)
        reversals[same] += 1
    same_parities = sorted({n % 2 for n in reversals})
    faces = len(walks)
    chi = len(links) - len(coverage) + faces
    data = {
        "knots": len(links), "covered_pairs": len(coverage), "cells": faces,
        "cover_count_histogram": dict(histogram), "euler_characteristic": chi,
        "cells_connected_through_covered_pairs": len(components(dual)) == 1,
        "link_cycle_lengths_by_knot": {k: list(map(len, p)) for k, p in local_parts.items()},
        "orientable": bool(reversals[0]), "orientations_tried": 1 << faces,
        "least_number_of_same_direction_covered_pairs": min(reversals),
        "same_direction_parities_over_all_orientations": same_parities,
    }
    if normalize and any(len(p) > 1 for p in local_parts.values()):
        labels = {}
        split = {}
        for knot, parts in local_parts.items():
            for i, part in enumerate(parts):
                label = len(labels)
                labels[knot, i] = label
                for neighbor in part:
                    split[knot, neighbor] = label
        lifted = []
        for walk in walks:
            corners = []
            for j, knot in enumerate(walk):
                label = split[knot, walk[j - 1]]
                assert label == split[knot, walk[(j + 1) % 4]]
                corners.append(label)
            lifted.append(tuple(corners))
        normalized = read_cells(lifted, normalize=False)
        assert all(len(p) == 1 for p in normalized["link_cycle_lengths_by_knot"].values())
        data["splitting_disconnected_links"] = {
            "original_knots_and_neighbors_in_separate_cycles": {
                k: p for k, p in local_parts.items() if len(p) > 1
            },
            "new_label_to_original_knot_and_link_index": {
                v: k for k, v in labels.items()
            },
            "walks": lifted, "reading": normalized,
        }
    return data


def inspect_game(game):
    knots = knots_of(game)
    walks = walks_of(game)
    descents = [sum(x > w[(i + 1) % 4] for i, x in enumerate(w)) for w in walks]
    sign = pauli_sign(game, knots)
    assert sign == pauli_sign(game, knots[::2] + knots[1::2])
    closed, subcollections = commutation_subsets(game)
    cells = read_cells(walks)
    assert sum(descents) % 2 == sign
    assert cells["same_direction_parities_over_all_orientations"] == [sign]
    return {
        "paired_holder_lists": game, "cyclic_holder_lists": walks, "commutes": closed,
        "nonempty_proper_commuting_subcollections": subcollections,
        "admits_merge": admits_merge(game), "closing_sign_exponent": sign,
        "descents_per_cell_in_knot_order": descents, "cell_reading": cells,
    }


def controls():
    even = game_from_pairs(
        (holders, match) for holders, matches in zip(combinations(range(3), 2), (
            ((3, 4), (5, 6)), ((3, 5), (4, 6)), ((3, 6), (4, 5))
        )) for match in matches
    )
    nine = game_from_pairs((
        ((0, 4), (1, 3)), ((1, 5), (2, 4)), ((2, 3), (0, 5)),
        ((3, 7), (4, 6)), ((4, 8), (5, 7)), ((5, 6), (3, 8)),
        ((2, 6), (0, 7)), ((1, 7), (2, 8)), ((0, 8), (1, 6)),
    ))
    return {"even seven-knot replacement": even, "nine-knot design fixture": nine}


def save(name, value):
    (DIRECTORY / name).write_text(json.dumps(value, indent=2) + "\n")


def failure_keys():
    failures = {}
    with (DIRECTORY / "merge_failures.jsonl").open() as stream:
        for line in stream:
            entry = json.loads(line)
            key = entry["population"], entry["id"], tuple(entry["word"])
            assert key not in failures
            failures[key] = game_from_pairs(entry["game"])
    return failures


def coverage_of(game):
    return Counter(unordered(a, b) for left, right in game for a, b in product(left, right))


def collect_games():
    classified = {}
    groups = defaultdict(lambda: defaultdict(Counter))
    first = {}
    checked = Counter()
    counts = Counter()
    locations = defaultdict(set)
    example = None
    with gzip.open(DIRECTORY / "choices.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            population, identifier = row["population"], row["id"]
            holders = defaultdict(list)
            for knot, support in enumerate(row["supports"]):
                for distinction in support:
                    holders[distinction].append(knot)
            for indices, minimal in row["words"]:
                values = [row["pairs"][i] for i in indices]
                assert len(set(chain.from_iterable(values))) == 2 * len(values)
                game = game_from_pairs((holders[a], holders[b]) for a, b in values)
                covered = coverage_of(game)
                assert all(nb % 2 == 0 for nb in covered.values())
                least = len(game) == row["fewest"]
                high = max(covered.values())
                key = population, minimal, least, high
                counts[key] += 1
                locations[key].add(identifier)
                if example is None and minimal and least and high > 2:
                    n = len(knots_of(game))
                    example = {
                        "population": population, "id": identifier, "word": indices,
                        "distinction_pairs": values, "holder_lists": game, "knots": n,
                        "covered_pairs": len(covered), "cells": len(game),
                        "higher_cover_counts": [[k, v] for k, v in covered.items() if v > 2],
                        "euler_characteristic": n - len(covered) + len(game),
                        "knots_minus_failing_pairs": n - len(game),
                    }
                if not minimal:
                    continue
                checked[population] += 1
                if admits_merge(game) or is_base(game):
                    continue
                key = population, identifier, tuple(indices)
                assert key not in classified, key
                classified[key] = game
                representative, mapping = canonical(game)
                assert relabel(game, dict(mapping)) == representative
                groups[representative][population][identifier] += 1
                if representative not in first:
                    first[representative] = {
                        "population": population, "id": identifier, "word": indices,
                        "holder_lists": game, "relabel_to_representative": mapping,
                    }
    coverage = {
        "rows": [{"population": p, "minimal": m, "fewest": f, "highest_cover_count": h,
                  "labelled_words": total, "distinct_locations": len(locations[p, m, f, h])}
                 for (p, m, f, h), total in sorted(counts.items())],
        "first_fewest_word_with_some_coverage_above_two": example,
    }
    return classified, groups, first, checked, coverage


def classify():
    classified, groups, first, checked, coverage = collect_games()
    failures = failure_keys()
    assert classified == failures
    classes = []
    readings = []
    for representative in sorted(groups, key=lambda g: (len(g), len(knots_of(g)), g)):
        by_location = groups[representative]
        detail = inspect_game(representative)
        assert detail["commutes"] and detail["closing_sign_exponent"] == 1
        assert not (detail["nonempty_proper_commuting_subcollections"] or detail["admits_merge"]
                    or is_base(representative))
        classes.append({
            "representative": representative, "one_original_witness": first[representative],
            "word_counts_by_population": {p: c.total() for p, c in by_location.items()},
            "word_counts_by_population_and_id": {p: dict(sorted(c.items()))
                                                for p, c in by_location.items()},
            "not_a_base": True, "minimal": True, "admits_merge": False,
        })
        readings.append(detail)
    save("shapes.json", {
        "weighting": "One per distinct labelled failing word at each census start or census type.",
        "isomorphism": "Retain each reader, its two settings, and the two knots holding each setting. Forget other distinctions and idle knots. Refine knot colors by opposite and adjacent colors at reader cells. Permute every knot independently within each final color class and take the least full sorted holder list.",
        "all_minimal_words_scanned": checked, "matched_every_merge_failure_by_word_and_holders": True,
        "classes": classes,
    })
    return readings, coverage


def check_larger_witnesses(frozen):
    stress = json.loads((DIRECTORY / "choices_size_stress.json").read_text())
    frozen_games = {canonical(r["paired_holder_lists"])[0] for r in frozen}
    samples = defaultdict(list)
    for population, rows in stress["eligible cases"].items():
        for row in rows:
            sample = row["first_minimal"]
            if sample is None:
                continue
            game = game_from_pairs(sample["holders"])
            representative, mapping = canonical(game)
            assert len(game) > 8 and relabel(game, dict(mapping)) == representative
            samples[representative].append({
                "population": population, "id": row["id"], "original_pairs": sample["pairs"],
                "holder_lists": game, "relabel_to_representative": mapping,
            })
    classes = []
    for representative, witnesses in samples.items():
        detail = inspect_game(representative)
        assert detail["commutes"] and detail["closing_sign_exponent"] == 1
        assert not (detail["nonempty_proper_commuting_subcollections"] or detail["admits_merge"]
                    or is_base(representative) or representative in frozen_games)
        source = witnesses[0]
        direct = []
        for witness in witnesses[1:]:
            inverse = {lab: knot for knot, lab in witness["relabel_to_representative"]}
            mapping = {knot: inverse[lab] for knot, lab in source["relabel_to_representative"]}
            assert relabel(source["holder_lists"], mapping) == witness["holder_lists"]
            direct.append({"from_id": source["id"], "to_id": witness["id"], "map": mapping})
        classes.append({
            "witnesses": witnesses, "direct_relabellings": direct,
            "reading": detail, "outside_frozen_classes": True,
        })
    save("shapes_size_stress.json", {
        "weighting": "One supplied minimal witness per positive type beyond eight pairs. These are post-study witnesses, not an enumeration of all choices at these sizes.",
        "classes": classes,
    })


def main():
    readings, coverage = classify()
    fixtures = {k: inspect_game(g) for k, g in controls().items()}
    assert fixtures["even seven-knot replacement"]["closing_sign_exponent"] == 0
    assert fixtures["nine-knot design fixture"]["closing_sign_exponent"] == 1
    rings = {n: inspect_game(ring(n)) for n in (3, 5, 7, 9, 11)}
    for outcome in (*fixtures.values(), *rings.values()):
        assert outcome["commutes"] and outcome["nonempty_proper_commuting_subcollections"] == 0
        assert not outcome["admits_merge"]
    for n, outcome in rings.items():
        cells = outcome["cell_reading"]
        assert outcome["closing_sign_exponent"] == 1
        assert cells["euler_characteristic"] == 1 and not cells["orientable"]
        assert cells["link_cycle_lengths_by_knot"][n] == [n]
        assert all(cells["link_cycle_lengths_by_knot"][i] == [3] for i in range(n))
    save("cells.json", {
        "reading": "Each reader gives a cyclic list of four knots, its two settings joining opposite holders. One covered knot pair is used for each unordered pair, with every incidence retained. Cell counts and orientation are the literature's square-complex reading.",
        "parity": "In total knot order the two settings interleave exactly when the cyclic list has an odd number of descents. With every covered pair used twice, total descents and the number of same-direction covered pairs have the same parity because there are twice as many covered pairs as cells. Consistent orientation therefore forces even sign. For the literature's parity of quadrangulations see Mohar, Simonyi and Tardos, section 1 and Lemma 6.1, https://real.mtak.hu/9875/1/mst2012.pdf.",
        "ring_family": "For n=2k+1, take each walk in the order common knot, i+k, i, i−k modulo n. Covered pairs involving the common knot are traversed oppositely and the n covered pairs among the other knots in the same direction, so the sign is odd. The common knot's link steps by 2k, equal to −1 modulo n, and every other link is a single cycle of three. Connected with counts (n+1,2n,n), each is the literature's projective plane.",
        "base_and_ring_controls": rings, "terminal_game_classes": readings,
        "coverage_of_all_listed_words": coverage,
        "control_provenance": "The nine-knot holder lists come from design item 7. The record mentions an even seven-knot control without giving its holder lists. Here each of the three pairs from three knots is assigned a different perfect matching of four other knots. This supplies a separate reproducible control.",
        "other_controls": fixtures,
    })
    check_larger_witnesses(readings)
    print(f"Verified {len(readings)} frozen failure classes, two further controls, five ring sizes and the larger witnesses.")


if __name__ == "__main__":
    main()
