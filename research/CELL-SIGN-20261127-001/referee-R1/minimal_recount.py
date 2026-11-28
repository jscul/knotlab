"""Recount all bounded choices at the strict-positive grown closures and census types."""

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from random import Random
import resource
from time import monotonic

from minimal_archive import archive_prefix, frozen_backend
from minimal_count import HERE, INPUT, all_words, bits, minimal_words, raw_counts, reconstruct, sources
from minimal_measure import measure_cycles, occurrences, steps


STUDY = HERE.parent
EARLIER = HERE.parents[1] / "ENCODED-READERS-20261127-001/referee-R1/choices.jsonl.gz"
SIZE_LIMIT = 8
RAW_CAP = 2000
SMALL_CODE = 14
CONTROLS = {("closure", 17), ("closure", 24), ("type", 0), ("type", 9)}
SEEDS = (72019, 72031)
BOOLEAN_FIELDS = {
    "exactly two": "covered_twice",
    "one cycle at every knot": "one_cycle_per_knot",
    "orientable": "orientable",
    "two-colourable": "two_colourable",
    "weak even condition": "weak_even",
}
COUNT_FIELDS = {
    "Euler counts": "euler",
    "separated Euler counts": "separated_euler",
    "most at a cross pair": "max_coverage",
}


def read_rows(path):
    with path.open() as stream:
        yield from map(json.loads, stream)


def get_archive():
    return {
        (population, row[key]): row
        for population, filename, key in (
            ("closure", "results.jsonl", "start"), ("type", "census_types.jsonl", "type")
        )
        for row in read_rows(STUDY / filename)
    }


def literal_matching_words(source, code):
    """Tiny exhaustive controls using labelled sets and direct symmetric difference."""
    crossings = [set(map(frozenset, steps(cycle))) for cycle in code.cycles]
    found = set()

    def visit(first, word, values, odd):
        if word and not odd:
            found.add(word)
        for i in range(first, len(crossings)):
            a, b = source["pairs"][i]
            if a not in values and b not in values:
                visit(i + 1, word | (1 << i), values | {a, b}, odd ^ crossings[i])

    visit(0, 0, set(), set())
    minimal = {word for word in found if not any(part != word and part & word == part for part in found)}
    return found, minimal


def explicit_orientations(cycles, covered_twice):
    """Check the reversal bits directly, fixing the first by global reversal."""
    constraints = [
        (sum(1 << i for i, _ in items), sum(1 << i for i, forward in items if forward), len(items) // 2)
        for items in occurrences(cycles).values()
    ]
    reversals = range(0, 1 << len(cycles), 2)
    orientable = any(
        all(((flip ^ initial) & scope).bit_count() == half for scope, initial, half in constraints)
        for flip in reversals
    )
    weak = orientable or (
        not covered_twice and any(
            all((((flip ^ initial) & scope).bit_count() - half) % 2 == 0 for scope, initial, half in constraints)
            for flip in reversals
        )
    )
    return orientable, weak


def measure_word(code, word, rngs):
    cycles = [code.cycles[i] for i in bits(word)]
    feature = measure_cycles(cycles, rngs=rngs)
    sign = feature["sign"]
    assert sign == (word & code.cost).bit_count() % 2
    assert (feature["orientable"], feature["weak_even"]) == explicit_orientations(cycles, feature["covered_twice"])
    feature["theorem"] = (
        sign == feature["reference_order_count"]
        and all(setting == sign for setting in feature["order_counts"])
        and (not feature["covered_twice"] or sign == feature["same_order_parity"])
    )
    feature["corollaries"] = not sign or not (
        feature["orientable"] or feature["weak_even"] or feature["two_colourable"]
    )
    return feature


def tally(features):
    tally = {
        "choices": len(features),
        "theorem holds": sum(feature["theorem"] for feature in features),
        **{name: sum(bool(f[field]) for f in features) for name, field in BOOLEAN_FIELDS.items()},
        **{name: Counter(str(f[field]) for f in features if f[field] is not None) for name, field in COUNT_FIELDS.items()},
    }
    return tally


def oriented_euler(features):
    """Keep the Euler count joint with orientability after separation."""
    return {
        name: Counter(str(f["separated_euler"]) for f in features
                      if f["orientable"] == orientation and f["separated_euler"] is not None)
        for orientation, name in ((True, "orientable"), (False, "nonorientable"))
    }


def merge_counts(a, b):
    for name, value in b.items():
        if isinstance(value, dict):
            merge_counts(a.setdefault(name, {}), value)
        else:
            a[name] = a.get(name, 0) + value


def signed_counts(words, cost):
    counts = raw_counts(words, cost)
    return {
        name: {str(size): counts[size, sign] for size in range(2, SIZE_LIMIT + 1) if counts[size, sign]}
        for sign, name in ((0, "even"), (1, "odd"))
    }


def recount():
    start_time = monotonic()
    archive = get_archive()
    backend = frozen_backend(STUDY / "cellsign.py")
    with gzip.open(EARLIER, "rt") as stream:
        earlier = {(row["population"], row["id"]): row for row in map(json.loads, stream)}
    assert earlier.keys() == archive.keys()
    rngs = tuple(map(Random, SEEDS))
    disagreements = []
    failures = []
    cap_rows = []
    results = []
    processed = set()
    nonorientable_even = {}

    for source in sources():
        population = {"birth": "closure", "type": "type"}.get(source["population"])
        key = population, source["key"]
        if key not in earlier:
            continue
        assert key not in processed
        processed.add(key)
        previous, archived = earlier[key], archive[key]
        if archived["strict"] != (previous["fewest"] is not None):
            disagreements.append([*key, "strict availability"])
        if previous["fewest"] is None:
            continue
        assert (previous["supports"], previous["pairs"]) == (source["supports"], source["pairs"])
        code = reconstruct(source)
        circuits = set(minimal_words(code, SIZE_LIMIT))
        raw = all_words(code, sorted(circuits, key=lambda x: (x.bit_count(), x)), SIZE_LIMIT)
        odd = {word for word in raw if (word & code.cost).bit_count() % 2}
        previous_odd = {
            sum(1 << i for i in word): is_minimal
            for word, is_minimal in previous["words"] if len(word) <= SIZE_LIMIT
        }
        assert previous_odd == {word: word in circuits for word in odd}, key
        if key in CONTROLS:
            assert literal_matching_words(source, code) == (raw, circuits), key
        fewest = min(map(int.bit_count, odd))
        if (fewest != previous["fewest"] or fewest != archived["fewest strict readers"]
                or archived["fewest listing complete"] is not True):
            disagreements.append([*key, "fewest size or complete listing"])

        by_size_sign = defaultdict(set)
        for word in raw:
            by_size_sign[word.bit_count(), int(word in odd)].add(word)
        computed_caps = sorted((sign, k) for (k, sign), words in by_size_sign.items() if len(words) >= RAW_CAP)
        if computed_caps != sorted(map(tuple, archived.get("sizes at the cap", []))):
            disagreements.append([*key, "capped sizes"])

        features = {word: measure_word(code, word, rngs) for word in sorted(raw)}
        for word, feature in features.items():
            if not (feature["theorem"] and feature["corollaries"]):
                failures.append([*key, list(bits(word)), feature])
            if word in circuits:
                assert feature["components"] == 1
                if feature["covered_twice"]:
                    assert feature["separated_components"] == 1

        omitted = set()
        for sign, k in computed_caps:
            all_at_size = by_size_sign[k, sign]
            listed = archive_prefix(source, code, k, sign, RAW_CAP, backend)
            assert listed <= all_at_size, key
            omitted.update(all_at_size - listed)
            all_minimal = all_at_size & circuits
            listed_minimal = listed & circuits
            cap_rows.append({
                "type": source["key"], "sign": sign, "size": k,
                "raw choices": len(all_at_size), "raw choices listed": len(listed),
                "actual minimal": tally([features[w] for w in all_minimal]),
                "listed minimal": tally([features[w] for w in listed_minimal]),
                "omitted minimal": tally([features[w] for w in all_minimal - listed_minimal]),
                "listed words digest": sha256(json.dumps(sorted(listed)).encode()).hexdigest(),
            })

        # Fewest in the study means a strict odd split. The small-code tallies
        # also use all strict words, including unions of minimal subcollections.
        categories = {
            "fewest strict": {w for w in odd if w.bit_count() == fewest},
            "minimal strict odd": circuits & odd,
            "minimal strict even": circuits - odd,
        }
        even_by_size = {}
        for w in sorted(categories["minimal strict even"]):
            f = features[w]
            size = w.bit_count()
            orientability = "orientable" if f["orientable"] else "nonorientable"
            counts = even_by_size.setdefault(str(size), {"orientable": 0, "nonorientable": 0})
            counts[orientability] += 1
            if population == "type" and not f["orientable"] and size not in nonorientable_even:
                nonorientable_even[size] = {
                    "type": source["key"],
                    "pairs": [source["pairs"][i] for i in bits(w)],
                    "cycles": [code.cycles[i] for i in bits(w)],
                    "separated Euler count": f["separated_euler"],
                }
        if code.dimension <= SMALL_CODE:
            assert len({d for support in source["supports"] for d in support}) // 2 <= SIZE_LIMIT
            categories["small code, strict, odd"] = odd
            categories["small code, strict, even"] = raw - odd

        tallies = {}
        listed_tallies = {}
        euler_by_orientation = {}
        for name, words in categories.items():
            if words:
                group = [features[w] for w in words]
                tallies[name] = tally(group)
                listed_tallies[name] = tally([features[w] for w in words - omitted])
                if name.startswith("minimal "):
                    euler_by_orientation[name] = oriented_euler(group)
        expected = {
            name: entry for name, entry in archived["tallies"].items()
            if name in categories or name.startswith("small code, strict, ")
        }
        if listed_tallies != expected:
            disagreements.append([*key, "choice tallies", listed_tallies, expected])
        coverage_four = {
            "fewest words": sum(features[w]["max_coverage"] >= 4 for w in categories["fewest strict"]),
            "minimal non-fewest words": sum(
                features[w]["max_coverage"] >= 4 for w in categories["minimal strict odd"] if w.bit_count() > fewest
            ),
        }
        if coverage_four != archived["coverage four"]:
            disagreements.append([*key, "coverage four", coverage_four, archived["coverage four"]])
        p1_failures = [
            list(bits(w)) for w in sorted(categories["minimal strict odd"])
            if features[w]["covered_twice"] and features[w]["separated_euler"] not in (0, 1)
        ]
        if p1_failures:
            failures.append([*key, "P1", p1_failures])
        results.append({
            "population": population, "start" if population == "closure" else "type": source["key"],
            "dimension": code.dimension, "fewest strict readers": fewest,
            "coverage four": coverage_four,
            "raw numbers by size": signed_counts(raw, code.cost),
            "minimal numbers by size": signed_counts(circuits, code.cost),
            "tallies": tallies,
            "minimal even by size and orientability": even_by_size,
            "separated Euler counts by orientability": euler_by_orientation,
            **({"frozen capped tallies": listed_tallies} if omitted else {}),
        })

    assert processed == earlier.keys()
    assert CONTROLS <= processed
    summary = {
        "input": str(INPUT.relative_to(HERE.parents[2])),
        "input verification": [
            "Earlier independent reconstruction of the supports and birth-eligible pairs.",
            str((EARLIER.parent / "birth_inputs.json").relative_to(HERE.parents[2])),
            "Every strict odd word through eight and its minimality compared with the earlier independent recount.",
        ],
        "weighting": "One per census start or finished census type for row counts. One per labelled choice for choice counts.",
        "scope": "Fewest strict odd choices and all strict choices through eight failing pairs at the strict-positive rows.",
        "all input rows audited": Counter(population for population, _ in processed),
        "rows with strict odd choices": Counter(row["population"] for row in results),
        "literal matching controls": sorted(CONTROLS),
        "random order seeds": SEEDS,
        "full versus archived capped listing": cap_rows,
        "archive discrepancies": disagreements,
        "gate or P1 failures": failures,
        "census nonorientable minimal even witnesses by size": dict(sorted(nonorientable_even.items())),
        "populations": {},
    }
    for population in ("closure", "type"):
        rows = [row for row in results if row["population"] == population]
        group = {
            "tallies": {}, "numbers by size": {}, "minimal even by size and orientability": {},
            "separated Euler counts by orientability": {}, "coverage four": {},
        }
        for row in rows:
            merge_counts(group["tallies"], row["tallies"])
            merge_counts(group["numbers by size"], row["minimal numbers by size"])
            merge_counts(group["minimal even by size and orientability"], row["minimal even by size and orientability"])
            merge_counts(group["separated Euler counts by orientability"], row["separated Euler counts by orientability"])
        for field in ("fewest words", "minimal non-fewest words"):
            affected = [row for row in rows if row["coverage four"][field]]
            group["coverage four"][field] = {
                "choices": sum(row["coverage four"][field] for row in affected),
                "rows": [
                    [row.get("start", row.get("type")), row["coverage four"][field]]
                    for row in affected
                ],
            }
        group["minimal even by size and orientability"] = dict(
            sorted(group["minimal even by size and orientability"].items(), key=lambda entry: int(entry[0]))
        )
        summary["populations"][population] = group
    summary["seconds"] = round(monotonic() - start_time, 2)
    summary["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for name, record in (("minimal_recount.json", summary), ("minimal_rows.json", results)):
        (HERE / name).write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    recount()
