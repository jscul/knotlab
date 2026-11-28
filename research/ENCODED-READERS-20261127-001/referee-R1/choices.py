"""List labelled strict odd choices from the earlier referee's reconstructed inputs."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import resource
from time import monotonic

from pysat.solvers import Minicard


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PRIOR = STUDY.parent / "READER-SPLIT-20261127-001"
SIZE_LIMIT = 8
DIMENSION_LIMIT = 14


def read_jsonl(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def binary_dependencies(columns):
    basis = {}
    dependencies = []
    for i, column in enumerate(columns):
        combination = 1 << i
        while column:
            pivot = column.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (column, combination)
                break
            previous, indices = basis[pivot]
            column ^= previous
            combination ^= indices
        else:
            dependencies.append(combination)
    return dependencies


def reconstruct(source):
    holders = defaultdict(list)
    for knot, support in enumerate(source["supports"]):
        for distinction in support:
            holders[distinction].append(knot)
    assert all(len(ends) == 2 for ends in holders.values())

    meetings = {
        pair: i for i, pair in enumerate(combinations(range(len(source["supports"])), 2))
    }
    checks = [0] * len(meetings)
    columns = []
    incidence = defaultdict(int)
    cost = 0
    for i, (a, b) in enumerate(source["pairs"]):
        aa, bb = holders[a], holders[b]
        assert len({*aa, *bb}) == 4
        crossings = [meetings[tuple(sorted((u, v)))] for u in aa for v in bb]
        columns.append(sum(1 << j for j in crossings))
        for j in crossings:
            checks[j] |= 1 << i
        cost |= ((sum(u > v for u in aa for v in bb) % 2) << i)
        incidence[a] |= 1 << i
        incidence[b] |= 1 << i
    dependencies = binary_dependencies(columns)
    assert (checks, cost, len(dependencies)) == (
        source["checks"], source["cost"], source["dimension"]
    )
    assert any((word & cost).bit_count() % 2 for word in dependencies) == source["odd"]
    return columns, checks, cost, list(incidence.values()), len(holders), dependencies


def projected_odd_words(dependencies, cost, incidence):
    """Enumerate the affine odd half of the commutation code."""
    odd = [word for word in dependencies if (word & cost).bit_count() % 2]
    if not odd:
        return
    offset, *remaining = odd
    even = [word for word in dependencies if not (word & cost).bit_count() % 2]
    directions = [*even, *(word ^ offset for word in remaining)]
    word = offset
    for turn in range(1 << len(directions)):
        if turn:
            word ^= directions[(turn & -turn).bit_length() - 1]
        if all((at & word).bit_count() < 2 for at in incidence):
            yield word


def add_parity(solver, literals, odd, next_variable):
    """Use a binary sum at each step and a final two-variable parity constraint."""
    if not literals:
        if odd:
            solver.add_clause([])
        return next_variable
    accumulator, *rest = literals
    for literal in rest[:-1]:
        new = next_variable
        next_variable += 1
        solver.add_clause([accumulator, literal, -new])
        solver.add_clause([accumulator, -literal, new])
        solver.add_clause([-accumulator, literal, new])
        solver.add_clause([-accumulator, -literal, -new])
        accumulator = new
    if not rest:
        solver.add_clause([accumulator if odd else -accumulator])
    elif odd:
        solver.add_clause([accumulator, rest[-1]])
        solver.add_clause([-accumulator, -rest[-1]])
    else:
        solver.add_clause([accumulator, -rest[-1]])
        solver.add_clause([-accumulator, rest[-1]])
    return next_variable


def bounded_words(
    width, checks, cost, incidence, limit, maximum, *, minimum=0, even_part=None
):
    """Exact projected solutions, using native at-most constraints."""
    with Minicard() as solver:
        next_variable = width + 1
        # Limit duplicate clauses from zero and repeated commutation checks.
        for row in sorted(set(checks) - {0}):
            next_variable = add_parity(
                solver, [j + 1 for j in bits(row)], False, next_variable
            )
        add_parity(solver, [j + 1 for j in bits(cost)], True, next_variable)
        for row in incidence:
            if row.bit_count() > 1:
                solver.add_atmost([j + 1 for j in bits(row)], 1)
        if limit < maximum:
            solver.add_atmost(list(range(1, width + 1)), limit)
        if minimum:
            solver.add_atmost(list(range(-width, 0)), width - minimum)

        while solver.solve():
            signed_choices = solver.get_model()[:width]
            assert [abs(literal) for literal in signed_choices] == list(range(1, width + 1))
            word = sum(1 << (i - 1) for i in signed_choices if i > 0)
            yield word
            even = even_part(word) if even_part else None
            if even is None:
                # Eliminate this assignment alone, including all unspecified auxiliary values.
                solver.add_clause([-literal for literal in signed_choices])
            else:
                # No choice containing a proper even commuting subcollection is minimal.
                solver.add_clause([-(i + 1) for i in bits(even)])


def list_choices(source):
    columns, checks, cost, incidence, distinctions, dependencies = reconstruct(source)
    width = len(columns)
    maximum = min(distinctions // 2, width)
    dimension = len(dependencies)

    if dimension <= DIMENSION_LIMIT:
        words = list(projected_odd_words(dependencies, cost, incidence))
    else:
        words = []
        for bound in range(min(SIZE_LIMIT, maximum), maximum + 1):
            words = list(bounded_words(width, checks, cost, incidence, bound, maximum))
            if words:
                break

    result = []
    for word in words:
        indices = tuple(bits(word))
        assert (word & cost).bit_count() % 2
        assert all(not (word & check).bit_count() % 2 for check in checks)
        assert all((word & row).bit_count() < 2 for row in incidence)
        minimal = len(binary_dependencies(columns[i] for i in indices)) == 1
        result.append((indices, minimal))
    assert len({indices for indices, _ in result}) == len(result)
    result.sort(key=lambda item: (len(item[0]), item[0]))
    fewest = len(result[0][0]) if result else None
    assert all(minimal for indices, minimal in result if len(indices) == fewest)
    population = "closure" if source["population"] == "birth" else "type"
    return dict(
        population=population, id=source["key"], dimension=dimension,
        supports=source["supports"], pairs=source["pairs"], fewest=fewest, words=result,
    )


def brute_choice_words(source):
    """Independent, tiny controls using explicit sets of met knot pairs."""
    holders = {
        d: tuple(i for i, support in enumerate(source["supports"]) if d in support)
        for pair in source["pairs"] for d in pair
    }
    meetings = [
        {tuple(sorted((u, v))) for u in holders[a] for v in holders[b]}
        for a, b in source["pairs"]
    ]
    odd = [
        sum(min(holders[a]) < u < max(holders[a]) for u in holders[b]) == 1
        for a, b in source["pairs"]
    ]
    words = set()

    def visit(start, used, checks, sign, indices):
        if not checks and sign:
            words.add(indices)
        for i in range(start, len(meetings)):
            a, b = source["pairs"][i]
            if a not in used and b not in used:
                visit(i + 1, used | {a, b}, checks ^ meetings[i], sign != odd[i], (*indices, i))

    visit(0, set(), set(), False, ())
    return words


def archived_rows(folder):
    rows = {}
    for population, name, key in (
        ("closure", "results.jsonl", "start"), ("type", "census_types.jsonl", "type")
    ):
        for row in read_jsonl(folder / name):
            index = population, row[key]
            assert index not in rows
            rows[index] = row
    return rows


def compare(row, archive, readers, earlier):
    counts = Counter(len(indices) for indices, _ in row["words"])
    minima = Counter(len(indices) for indices, minimal in row["words"] if minimal)
    strict = row["fewest"] is not None
    errors = []
    if strict != archive["strict"] or strict != readers["strict"]:
        errors.append("strict availability")
    if row["fewest"] != archive.get("fewest strict readers") or (
        row["fewest"] != readers["fewest strict readers"]
    ):
        errors.append("fewest strict readers")
    if strict:
        if counts[row["fewest"]] != archive["fewest splits listed"]:
            errors.append("fewest listing")
        indexed_pairs = {tuple(pair): i for i, pair in enumerate(row["pairs"])}
        witness = tuple(sorted(indexed_pairs[tuple(sorted(p))] for p in readers["strict readers"]))
        if not any(witness == indices and len(indices) == row["fewest"] for indices, _ in row["words"]):
            errors.append("archived readers' witness")
        if readers["strict: integer program and satisfiability agree"] is not True:
            errors.append("archive reported disagreement between solvers")
        if archive["integer program's split among them"] is not True:
            errors.append("study reported a missing integer-program witness")
    for size, listing in archive.get("P1 by pairs", {}).items():
        if (counts[int(size)], minima[int(size)]) != (listing["choices"], listing["minimal"]):
            errors.append(f"bounded listing at {size} pairs")
    if "free choices" in archive and row["dimension"] != archive["free choices"]:
        errors.append("archived code dimension")
    small = row["dimension"] <= DIMENSION_LIMIT
    if small:
        if (row["dimension"], sum(counts.values()), sorted(counts)) != (
            readers["free choices"], readers["strict odd choices"], readers["strict sizes"]
        ):
            errors.append("readers' small-code enumeration")
        if strict and (sum(counts.values()), sum(minima.values())) != (
            archive["small code: strict odd choices"], archive["small code: minimal"]
        ):
            errors.append("small-code listing")
    old = earlier.get(row["id"]) if row["population"] == "closure" else None
    if old is not None and counts[row["fewest"]] != sum(old["all minimum strict words by shape"].values()):
        errors.append("earlier referee's fewest list")
    return errors, counts, minima, old is not None


def search_above_eight(sources):
    """Post-frozen existence checks for strict odd choices above the size limit."""
    started = monotonic()
    with gzip.open(HERE / "choices.jsonl.gz", "rt") as stream:
        minima = {
            (row["population"], row["id"]): row["fewest"]
            for row in map(json.loads, stream)
        }
    eligible = defaultdict(list)
    cases = Counter()
    natural_bounds = defaultdict(Counter)
    strict_bounds = defaultdict(Counter)
    for source in sources:
        population = "closure" if source["population"] == "birth" else "type"
        distinctions = len({d for support in source["supports"] for d in support})
        maximum = min(distinctions // 2, len(source["pairs"]))
        natural_bounds[population][maximum] += 1
        if minima[population, source["key"]] is not None:
            strict_bounds[population][maximum] += 1
        if maximum <= SIZE_LIMIT:
            continue

        columns, checks, cost, incidence, _, _ = reconstruct(source)

        def even_part(word):
            indices = tuple(bits(word))
            dependencies = binary_dependencies(columns[i] for i in indices)
            assert dependencies
            if len(dependencies) == 1:
                return None
            proper = next(
                sum(1 << indices[i] for i in bits(subset))
                for subset in dependencies if subset.bit_count() < len(indices)
            )
            even = word ^ proper if (cost & proper).bit_count() % 2 else proper
            assert 0 < even < word and not (cost & even).bit_count() % 2
            assert all(not (check & even).bit_count() % 2 for check in checks)
            return even

        holders = {
            d: tuple(i for i, support in enumerate(source["supports"]) if d in support)
            for pair in source["pairs"] for d in pair
        }

        def witness(word):
            pairs = [source["pairs"][i] for i in bits(word)]
            assert word.bit_count() > SIZE_LIMIT and word.bit_count() <= maximum
            assert (word & cost).bit_count() % 2
            assert all(not (word & check).bit_count() % 2 for check in checks)
            assert all((word & row).bit_count() < 2 for row in incidence)
            return dict(pairs=pairs, holders=[(holders[a], holders[b]) for a, b in pairs])

        by_size = {}
        for size in range(SIZE_LIMIT + 1, maximum + 1):
            first, minimal = None, None
            considered = 0
            for word in bounded_words(
                len(columns), checks, cost, incidence, size, maximum,
                minimum=size, even_part=even_part,
            ):
                considered += 1
                assert word.bit_count() == size
                if first is None:
                    first = witness(word)
                if even_part(word) is None:
                    minimal = witness(word)
                    break
            by_size[size] = dict(first_odd=first, first_minimal=minimal, models_considered=considered)
        first_odd = next((row["first_odd"] for row in by_size.values() if row["first_odd"]), None)
        first_minimal = next((row["first_minimal"] for row in by_size.values() if row["first_minimal"]), None)
        eligible[population].append(
            dict(id=source["key"], distinctions=distinctions, maximum=maximum,
                 first_odd=first_odd, first_minimal=first_minimal, by_size=by_size)
        )
        cases[(population, "any")] += first_odd is not None
        cases[(population, "minimal")] += first_minimal is not None
        for size, verdict in by_size.items():
            print(population, source["key"], size, bool(verdict["first_odd"]),
                  bool(verdict["first_minimal"]), flush=True)

    result = {
        "scope": "Post-frozen existence of a strict odd choice of at least nine pairs, and of a minimal one",
        "natural size bounds": natural_bounds,
        "natural size bounds in strict-positive codes": strict_bounds,
        "eligible cases": eligible,
        "codes with a strict odd choice above eight": {p: cases[p, "any"] for p in natural_bounds},
        "codes with a minimal strict odd choice above eight": {p: cases[p, "minimal"] for p in natural_bounds},
        "seconds": round(monotonic() - started, 2),
        "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (HERE / "choices_size_stress.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Seconds:", result["seconds"], "peak KiB:", result["peak KiB"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true", help="Time representative cases without writing files.")
    parser.add_argument("--size-stress", action="store_true", help="Check for strict odd choices of at least nine pairs.")
    args = parser.parse_args()
    started = monotonic()
    sources = [
        row for row in read_jsonl(PRIOR / "referee-R1" / "rebuilt_inputs.jsonl")
        if row["population"] in {"birth", "type"}
    ]
    if args.probe:
        for source in sources:
            control = source["population"] == "birth" and source["key"] in {17, 24, 5136, 6787, 2422}
            control |= source["population"] == "type" and source["key"] in {0, 9, 77, 149, 171, 172}
            if control:
                at = monotonic()
                row = list_choices(source)
                if len(source["pairs"]) <= 30:
                    assert {p for p, _ in row["words"]} == brute_choice_words(source)
                print(
                    row["population"], row["id"], len(source["pairs"]), row["dimension"],
                    row["fewest"], len(row["words"]), round(monotonic() - at, 3), flush=True,
                )
        print("Peak KiB:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return
    if args.size_stress:
        search_above_eight(sources)
        return

    archive = archived_rows(STUDY)
    readers = archived_rows(PRIOR)
    earlier = {
        row["start"]: row
        for row in json.loads((PRIOR / "referee-R1" / "shapes.json").read_text())["by census start"]
    }
    observed = set()
    mismatches = []
    limits = defaultdict(Counter)
    population_counts = defaultdict(Counter)
    by_size = defaultdict(Counter)
    by_size_minimal = defaultdict(Counter)
    fewest_sizes = defaultdict(Counter)
    earlier_checked = 0
    earlier_choices = 0
    controls = []
    scratch = HERE / "choices.tmp.jsonl.gz"
    with gzip.open(scratch, "wt", compresslevel=6) as output:
        for source in sources:
            row = list_choices(source)
            population = row["population"]
            index = population, row["id"]
            assert index not in observed
            observed.add(index)
            errors, counts, minima, old = compare(row, archive[index], readers[index], earlier)
            if errors:
                mismatches.append([*index, errors])
            stats = population_counts[population]
            stats["codes"] += 1
            stats["strict codes"] += row["fewest"] is not None
            if row["fewest"] is not None:
                min_count = counts[row["fewest"]]
                stats["fewest choices"] += min_count
                stats["archived strict witness comparisons"] += 1
                fewest_sizes[population][row["fewest"]] += 1
                limits[population]["largest fewest listing"] = max(
                    limits[population]["largest fewest listing"], min_count
                )
                limits[population]["largest listing through eight"] = max(
                    limits[population]["largest listing through eight"],
                    *(counts[k] for k in range(3, SIZE_LIMIT + 1)),
                )
            if old:
                earlier_checked += 1
                earlier_choices += counts[row["fewest"]]
            if row["dimension"] <= DIMENSION_LIMIT:
                stats["small codes"] += 1
                stats["small codes with strict odd choices"] += bool(counts)
                stats["small strict odd choices"] += sum(counts.values())
                stats["small minimal choices"] += sum(minima.values())
            for size in range(3, SIZE_LIMIT + 1):
                by_size[population][size] += counts[size]
                by_size_minimal[population][size] += minima[size]
            if index in {("closure", 17), ("closure", 24), ("type", 0), ("type", 9)}:
                assert {p for p, _ in row["words"]} == brute_choice_words(source)
                controls.append(index)
            print(json.dumps(row, separators=(",", ":")), file=output)
    assert observed == archive.keys() == readers.keys()
    assert earlier_checked == len(earlier)
    scratch.replace(HERE / "choices.jsonl.gz")
    summary = {
        "method": (
            "Reconstruct every parity column and the sign from holders, then enumerate the "
            "affine space through dimension 14 and exact projected bounded solutions elsewhere."
        ),
        "inputs": [
            "../../READER-SPLIT-20261127-001/referee-R1/rebuilt_inputs.jsonl",
            "../results.jsonl",
            "../census_types.jsonl",
            "../../READER-SPLIT-20261127-001/results.jsonl",
            "../../READER-SPLIT-20261127-001/census_types.jsonl",
            "../../READER-SPLIT-20261127-001/referee-R1/shapes.json",
        ],
        "weighting": "One vote per census start, census type, or labelled choice as named.",
        "closure and census comparisons disagreeing": mismatches,
        "earlier referee's closure comparisons": earlier_checked,
        "earlier referee's fewest choices": earlier_choices,
        "independent brute force controls": controls,
        "populations": population_counts,
        "fewest sizes by code": fewest_sizes,
        "listed choices by size": by_size,
        "minimal choices by size": by_size_minimal,
        "listing maxima": limits,
        "seconds": round(monotonic() - started, 2),
        "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (HERE / "choices_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
