"""Independent census using ternary truth tables and relations on four columns."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache, reduce
import hashlib
from itertools import combinations, permutations
import json
from math import gcd
from operator import or_
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR = "FRESH-THREE-20261117-001"
SOURCE = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_projection") / "results.json"


@cache
def projected(words):
    """One representative from each antipodal projected row pair."""
    other = (1 << len(words)) - 1
    mask = 0
    for i in range(6):
        row = sum(((word >> i) & 1) << j for j, word in enumerate(words))
        mask |= 1 << min(row, row ^ other)
    return mask


def read_old_columns(rows, cut_index):
    # Change the order and the representative of some complementary pairs.
    # These arbitrary computational choices must leave every reading invariant.
    reps = sorted(r for r in rows if r < (r ^ 255))
    assert len(reps) == 6 and len(rows) == 12
    reps = reps[cut_index % 6:] + reps[:cut_index % 6]
    reps = [r ^ 255 if (i + cut_index) % 3 == 0 else r for i, r in enumerate(reps)]
    words = [sum(((r >> j) & 1) << i for i, r in enumerate(reps)) for j in range(8)]
    columns = tuple(sorted(min(word, word ^ 63) for word in words))
    assert len(set(columns)) == 8
    return columns


@cache
def covers_for_pair(a, b):
    """Compatible knots force a target column on certain old row pairs."""
    answer = [0] * 32
    for new in set(range(32)) - {a, b}:
        table = projected((a, b, new))
        if table.bit_count() == 4:
            continue
        assert table.bit_count() == 3
        excluded = next(x for x in range(4) if not ((table >> x) & 1))
        cover = 0
        for i in range(6):
            # Try the opposite fresh value. It is forced out precisely if
            # this ternary assignment belongs to the excluded pair.
            wrong = ((a >> i) & 1) | (((b >> i) & 1) << 1) | ((((new >> i) & 1) ^ 1) << 2)
            if min(wrong, wrong ^ 7) == excluded:
                cover |= 1 << i
        answer[new] = 1 << cover
    return answer


SUPERSETS = [sum(1 << m for m in range(1, 64) if m & need == need) for need in range(64)]


@cache
def can_force(available):
    masks = [i for i in range(1, 64) if available & (1 << i)]
    return any(available & SUPERSETS[63 ^ (a | b)]
               for j, a in enumerate(masks) for b in masks[j:])


@cache
def options(columns):
    pair_covers = [covers_for_pair(a, b) for a, b in combinations(columns, 2)]
    choices = [q for q in range(32) if q not in columns
               and can_force(reduce(or_, (pair[q] for pair in pair_covers), 0))]
    assert choices, "a fill must exist for this cost-zero enumeration"
    return choices


def transform_pair_mask(mask, perm, flip):
    result = 0
    for row in range(8):
        if (mask >> row) & 1:
            new = sum(((row >> i) & 1) << perm[i] for i in range(4)) ^ flip
            result |= 1 << min(new, new ^ 15)
    return result


@cache
def features(mask):
    rows = [r for r in range(16) if (mask >> min(r, r ^ 15)) & 1]
    marked = min(transform_pair_mask(mask, p + (3,), f)
                 for p in permutations(range(3)) for f in range(8))
    anonymous = min(transform_pair_mask(mask, p, f)
                    for p in permutations(range(4)) for f in range(8))
    old_size = len({r & 7 for r in rows})
    pairs_bound = sum(len({r & ((1 << a) | (1 << b) | 8) for r in rows}) == 6
                      for a, b in combinations(range(3), 2))
    parity = len(rows) == 8 and len({r.bit_count() % 2 for r in rows}) == 1
    assert old_size in (6, 8)
    return marked, anonymous, old_size, pairs_bound, len(rows) == old_size, parity


def reached(old):
    law = {(): Fraction(1)}
    for _ in range(3):
        after = defaultdict(Fraction)
        for new, weight in law.items():
            choices = options(tuple(sorted(old + new)))
            share = weight / len(choices)
            for q in choices:
                after[tuple(sorted(new + (q,)))] += share
        assert sum(after.values()) == 1
        law = after
    return law


def reduced_law(counts):
    factor = gcd(*counts.values())
    return tuple(sorted((k, v // factor) for k, v in counts.items()))


def independent_census():
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == "2ad9a1f8824ef5649a6a1e6ed9cbf485d77b2125c77a3f8cb3eccd2737235d7f"
    prior = json.loads(data)
    signatures = defaultdict(set)
    frequencies = defaultdict(Fraction)
    counts = Counter()
    extremes = defaultdict(set)
    for record in prior["per_cut_class"]:
        old = read_old_columns(record["cut_rows"], record["cut_class"])
        cut_mass = sum(Fraction(s) for s in record["cut_probabilities"].values()) / 2
        at_eleven = reached(old)
        assert len(at_eleven) == record["stages"][-1]["distinct_column_sets_after"]
        by_type = defaultdict(Fraction)
        for new, chance in at_eleven.items():
            size = 2 * projected(new).bit_count()
            by_type[size] += chance
            counts[size] += 1
            choices = options(tuple(sorted(old + new)))
            marked, anonymous, events = Counter(), Counter(), Counter()
            for q in choices:
                m, u, old_size, k, determined, parity = features(projected(new + (q,)))
                assert old_size == size
                marked[m] += 1
                anonymous[u] += 1
                events["at_least_one"] += k > 0
                events["determined"] += determined
                events["parity"] += parity
            if size == 6:
                parity_column = reduce(int.__xor__, new)
                assert events["determined"] == (min(parity_column, parity_column ^ 63) not in old + new)
            for observation, counter in (("marked", marked), ("unmarked", anonymous)):
                signatures[size, observation, "laws"].add(reduced_law(counter))
                signatures[size, observation, "supports"].add(tuple(sorted(counter)))
            mass = cut_mass * chance
            frequencies[size, "total"] += mass
            for event, count in events.items():
                probability = Fraction(count, len(choices))
                extremes[size, event].add(probability)
                frequencies[size, event] += mass * probability
        assert all(p == Fraction(record["projection_probabilities"][str(s)]) for s, p in by_type.items())
    assert counts.total() == 22475 and sum(frequencies[s, "total"] for s in counts) == 1
    return {
        str(s): {
            "contexts": count,
            "law_counts": {reading: {key: len(signatures[s, reading, key]) for key in ("laws", "supports")}
                           for reading in ("marked", "unmarked")},
            "events": {event: {"pooled": str(frequencies[s, event] / frequencies[s, "total"]),
                              "range": [str(min(extremes[s, event])), str(max(extremes[s, event]))]}
                       for event in ("at_least_one", "determined", "parity")},
        } for s, count in sorted(counts.items())
    }


def compare(measured, checked):
    names = {"at_least_one": "k_at_least_one", "determined": "determined_by_three", "parity": "four_place_parity"}
    for size, part in checked.items():
        primary = measured["by_triple_support_size"][size]
        assert primary["context_count"] == part["contexts"]
        for mode, counts in part["law_counts"].items():
            assert counts["laws"] == primary[mode]["distinct_conditional_laws"]
            assert counts["supports"] == primary[mode]["distinct_possible_outcome_sets"]
        for event, values in part["events"].items():
            name = names[event]
            limits = primary["events"][name]["conditional_probability_range"]
            assert values["range"] == [limits["min"], limits["max"]]
            assert values["pooled"] == primary["pooled"]["equal_prior_mixture"][name]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", type=Path, help="Verify equality to the primary result")
    args = parser.parse_args()
    census = independent_census()
    if args.compare:
        compare(json.loads(args.compare.read_text()), census)
    report = json.dumps(census, indent=2) + "\n"
    if args.output:
        args.output.write_text(report)
    else:
        print(report, end="")
