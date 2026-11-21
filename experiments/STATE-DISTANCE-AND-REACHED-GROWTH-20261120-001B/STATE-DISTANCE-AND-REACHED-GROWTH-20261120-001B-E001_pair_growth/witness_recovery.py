"""Check the predecessor and four-birth certificate on the archived named table."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from math import gcd, lcm
from pathlib import Path
import gzip
import json


ROOT = Path(__file__).resolve().parents[3]
TICKET = "STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B"
PREVIOUS = "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C"
HOLDERS = [set(r) for r in ((0, 4, 5, 6), (1, 7, 8, 9), (2, 10, 11, 12), (3, 13, 14, 15))]
PARENTS = list(combinations(range(4), 2))
SUPPORTS = [set(r) for r in ((4, 7, 16, 17), (5, 10, 18, 19), (6, 13, 20, 21),
                             (8, 11, 22, 23), (9, 14, 24, 25), (12, 15, 26, 27))]


def word_count(width, rows):
    """Include/exclude the events that all names of a row are equal."""
    totals = 0
    for mask in range(1 << len(rows)):
        blocks = [1 << i for i in range(width)]
        for i, row in enumerate(rows):
            if not mask >> i & 1:
                continue
            merged = sum(1 << x for x in row)
            untouched = []
            for block in blocks:
                if block & merged:
                    merged |= block
                else:
                    untouched.append(block)
            blocks = [*untouched, merged]
        sign = -1 if mask.bit_count() % 2 else 1
        totals += sign * (1 << len(blocks))
    return totals


def exact_table():
    path = ROOT / "artifacts" / PREVIOUS / f"{PREVIOUS}-E001_wider_meetings" / "census_rate_tables.json.gz"
    with gzip.open(path, "rt") as source:
        record = next(row for row in json.load(source)["nae"]["records"]
                      if row["source_index"] == 1 and row["age"] == 2)
    count = record["allowed_states"]
    assert record["width"] == 28
    values = record["disagreement_counts"]
    corr = [[count if i == j else None for j in range(28)] for i in range(28)]
    for (i, j), value in zip(combinations(range(28), 2), values, strict=True):
        corr[i][j] = corr[j][i] = count - 2 * value
    return corr, count, lcm(*(count // gcd(k, count) for k in values))


def admissible_rosters():
    result = []
    for mask in range(1, 1 << 6):
        chosen = [pair for j, pair in enumerate(PARENTS) if mask >> j & 1]
        neighbours = [set() for _ in range(4)]
        for i, j in chosen:
            neighbours[i].add(j)
            neighbours[j].add(i)
        if all(len(neighbours[i] | neighbours[j]) - 2 == 2 for i, j in chosen):
            result.append(chosen)
    return result


def remaining_rows(chosen, links):
    # Each of the two non-input positions of each H goes to a different
    # witness, one at each incident selected pair. Their names have no
    # further use, so exchanging them cannot affect the word count.
    chosen_rows = [SUPPORTS[PARENTS.index(pair)] for pair in chosen]
    remaining = [set() for _ in chosen_rows]
    for holder_index, holder in enumerate(HOLDERS):
        other = sorted(holder - set.union(*chosen_rows))
        witnesses = [j for j, pair in enumerate(chosen) if holder_index in pair]
        assert len(other) == len(witnesses) == 2
        for name, witness in zip(other, witnesses, strict=True):
            remaining[witness].add(name)
    unknown = sorted(set(range(28)) - set.union(*HOLDERS, *chosen_rows))
    assert len(unknown) == len(links) == 4
    for name, (i, j) in zip(unknown, links, strict=True):
        remaining[i].add(name)
        remaining[j].add(name)
    assert all(len(row) == 4 for row in remaining)
    return [*HOLDERS, *chosen_rows, *remaining]


def repeated_meeting_control():
    seed = [(0, 1, 2, 3, 4), (1, 2, 5), (3, 4, 6), (5, 6, 7)]
    birth = (0, 7, 8)
    rows = [*seed, birth]

    def words(width, support):
        return [w for w in range(1 << width)
                if all(0 < sum((w >> name) & 1 for name in h) < len(h) for h in support)]

    def check(width, support):
        allowed = words(width, support)
        for i, h in enumerate(support):
            assert len({tuple((w >> name) & 1 for name in h) for w in allowed}) == (1 << len(h)) - 2
            assert len(words(width, support[:i] + support[i+1:])) > len(allowed)
        return allowed

    before = check(8, seed)
    after = check(9, rows)

    def correlation(i, j):
        return Fraction(sum(1 - 2 * (((w >> i) ^ (w >> j)) & 1) for w in after), len(after))

    differences = {z: correlation(0, z) - correlation(8, z) for z in range(1, 8)}
    minimizers = [z for z, value in differences.items() if value == min(differences.values())]
    assert minimizers == [1, 2, 3, 4, 7]
    return {"seed": seed, "birth": birth, "seed_words": len(before), "reached_words": len(after),
            "true_preceding_holder": seed[0], "corrected_minimum": str(min(differences.values())),
            "all_older_minimizers": minimizers}


def main():
    corr, total, denominator = exact_table()
    assert total == word_count(28, [set(range(4)), *HOLDERS, *SUPPORTS])
    # Every triple admits a constant word, by its three pair probabilities.
    triple_masses = [
        Fraction(total + corr[a][b] + corr[a][c] + corr[b][c], 4 * total)
        for a, b, c in combinations(range(28), 3)
    ]
    assert min(triple_masses) > 0
    differences = []
    for child, pair in zip(SUPPORTS, PARENTS, strict=True):
        loose = sorted(x for x in child if x >= 16)
        assert all(corr[loose[0]][z] == corr[loose[1]][z] for z in set(range(28)) - set(loose))
        for index in pair:
            (u,) = HOLDERS[index] & child
            for fresh in loose:
                values = {z: corr[u][z] - corr[fresh][z]
                          for z in range(28) if z not in (fresh, u)}
                minimum = min(values.values())
                minimizers = {z for z, value in values.items() if value == minimum}
                assert minimizers == HOLDERS[index] - {u}
                differences.append({"input": u, "fresh": fresh, "minimum": str(Fraction(minimum, total)),
                                    "names_at_minimum": sorted(minimizers)})

    rosters = admissible_rosters()
    # All four-cycles give the same unlabelled count possibilities.
    cycle = next(chosen for chosen in rosters if len(chosen) == 4)
    counts = []
    for links in combinations_with_replacement(PARENTS, 4):
        degrees = Counter(name for pair in links for name in pair)
        if len(degrees) != 4 or set(degrees.values()) != {2}:
            continue
        rows = remaining_rows(cycle, links)
        count = word_count(28, rows)
        assert count % denominator != 0
        counts.append({"meeting_pairs_between_the_four_witnesses": links, "allowed_words": count,
                       "remainder_on_required_divisor": count % denominator})
    assert len(counts) == 6
    profile = [
        {"parents": [sorted(SUPPORTS[PARENTS.index(pair)]) for pair in combinations(triple, 2)],
         "fresh": 1}
        for triple in combinations(range(4), 3)
    ]
    evidence = {
        "uniform_words": total, "necessary_word_count_divisor": denominator,
        "smallest_constant_probability_over_every_named_triple": str(min(triple_masses)),
        "tested_named_triples": len(triple_masses), "corrected_rows": differences,
        "possible_demand_two_parent_graphs_on_four_indices": rosters,
        "number_by_edges": dict(sorted(Counter(map(len, rosters)).items())),
        "four_cycle_rivals": counts, "next_named_profiles": profile,
        "repeated_meeting_source_counterexample_to_strictness": repeated_meeting_control(),
    }
    path = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_pair_growth" / "witness_recovery.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"denominator": denominator, "triple_minimum": str(min(triple_masses)),
                      "number_by_edges": evidence["number_by_edges"],
                      "alternative_counts": [c["allowed_words"] for c in counts]}))


if __name__ == "__main__":
    main()
