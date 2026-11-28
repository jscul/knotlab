"""Exact counts at the least number of failing pairs of an odd birth choice."""

import argparse
import itertools
import json
import resource
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
INPUT = HERE / "rebuilt_inputs.jsonl"


def json_lines(path):
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def position_forms(checks, cost, size):
    """Express each position as an affine function of independent binary choices.

    Bit zero of a form is its constant. All other bits name free positions.
    Two distinct positional conditions 'value is one' can hold together unless
    either form is zero or the two forms are complements.
    """
    constant = 1 << size
    below_constant = constant - 1
    pivots = {}
    for row in [*checks, cost | constant]:
        while row & below_constant:
            pivot = (row & below_constant).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
        else:
            if row:
                raise ValueError("This code cannot close odd.")

    forms = []
    for position in range(size):
        if position not in pivots:
            forms.append(1 << (position + 1))
            continue
        row = pivots[position]
        form = int(bool(row & constant))
        terms = row & ((1 << position) - 1)
        while terms:
            term = terms & -terms
            form ^= forms[term.bit_length() - 1]
            terms ^= term
        forms.append(form)
    return forms


def partial_subsets(items, count):
    """Yield the check sum and positional mask of every subset of a fixed size."""
    if count == 0:
        yield 0, 0
    elif count == 1:
        yield from items
    elif count == 2:
        for (a, i), (b, j) in itertools.combinations(items, 2):
            yield a ^ b, i | j
    elif count == 3:
        for (a, i), (b, j), (c, k) in itertools.combinations(items, 3):
            yield a ^ b ^ c, i | j | k
    else:
        for subset in itertools.combinations(items, count):
            total = 0
            mask = 0
            for column, position in subset:
                total ^= column
                mask |= position
            yield total, mask


def choices_at_weight(items, target, weight):
    """Join subsets by check sum; the earlier half has strictly smaller indices.

    The first pair in the later half determines a unique join for every choice.
    Occurrences of equal columns retain their individual pair identities.
    """
    earlier = weight // 2
    later = weight - earlier
    by_sum = {} if earlier else {0: [0]}
    for split in range(earlier, len(items) - later + 1):
        if earlier:
            column, position = items[split - 1]
            for subtotal, mask in partial_subsets(items[: split - 1], earlier - 1):
                by_sum.setdefault(column ^ subtotal, []).append(position | mask)
        column, position = items[split]
        needed = target ^ column
        for subtotal, mask in partial_subsets(items[split + 1 :], later - 1):
            for match in by_sum.get(needed ^ subtotal, ()):
                yield match | position | mask


def names_of_pairs(word, pairs):
    if word is None:
        return None
    return [pair for i, pair in enumerate(pairs) if word & (1 << i)]


def verify_witness(failures, supports, weight, strict):
    """Read commutation and sign from the holders, independently of the check sums."""
    failed_checks = set()
    odd = False
    distinctions = set()
    for a, b in failures:
        left = [k for k, knot in enumerate(supports) if a in knot]
        right = [k for k, knot in enumerate(supports) if b in knot]
        i, j = left
        p, q = right
        odd ^= i < p < j < q or p < i < q < j
        for u, v in itertools.product(left, right):
            failed_checks.symmetric_difference_update([(min(u, v), max(u, v))])
        distinctions.update([a, b])
    if failed_checks or not odd or len(failures) != weight or (len(distinctions) == 2 * weight) != strict:
        raise ValueError("A minimum witness fails its holder check.")


def recount_one(code):
    pairs = code["pairs"]
    size = len(pairs)
    checks = code["checks"]
    # A set bit in the last equation is the required odd sign.
    equations = [*checks, code["cost"]]
    target = 1 << len(checks)
    forms = position_forms(checks, code["cost"], size)
    items = []
    incidence = {}
    for i, pair in enumerate(pairs):
        bit = 1 << i
        column = sum(1 << j for j, equation in enumerate(equations) if equation & bit)
        items.append((column, bit))
        for distinction in pair:
            incidence.setdefault(distinction, []).append(i)
    can_be_non_strict = any(
        forms[i] and forms[j] and (forms[i] ^ forms[j]) != 1
        for positions in incidence.values()
        for i, j in itertools.combinations(positions, 2)
    )
    incident_masks = [sum(1 << i for i in positions) for positions in incidence.values()]
    supports = list(map(set, code["supports"]))
    if any(any(a in knot and b in knot for knot in supports) for a, b in pairs):
        raise ValueError("A knot holds a decidable pair.")
    four_meet = any(
        all(a & b for a, b in itertools.combinations(four, 2))
        for four in itertools.combinations(supports, 4)
    )

    minimum = None
    strict_count = non_strict_count = 0
    strict_example = non_strict_example = None
    minimum_non_strict = None
    for weight in range(1, size + 1):
        for word in choices_at_weight(items, target, weight):
            if minimum is None:
                minimum = weight
            non_strict = any((word & mask).bit_count() >= 2 for mask in incident_masks)
            if non_strict:
                if not can_be_non_strict:
                    raise AssertionError("Affine feasibility disagrees with the witness.")
                if minimum_non_strict is None:
                    minimum_non_strict = weight
                    non_strict_example = word
                if weight == minimum:
                    non_strict_count += 1
                else:
                    break  # The unrestricted minimum has already been counted in full.
            elif weight == minimum:
                strict_count += 1
                if strict_example is None:
                    strict_example = word
        if minimum is not None and (minimum_non_strict is not None or not can_be_non_strict):
            break
    if minimum is None or can_be_non_strict != (minimum_non_strict is not None):
        raise ValueError("The feasibility and minimum checks did not agree.")
    strict_failures = names_of_pairs(strict_example, pairs)
    non_strict_failures = names_of_pairs(non_strict_example, pairs)
    if strict_failures is not None:
        verify_witness(strict_failures, supports, minimum, True)
    if non_strict_failures is not None:
        verify_witness(non_strict_failures, supports, minimum_non_strict, False)

    return {
        "start": code["start"],
        "round": code["round"],
        "fewest failing pairs, odd": minimum,
        "fewest failing pairs, odd, not strict": minimum_non_strict,
        "strict odd choices at minimum": strict_count,
        "non-strict odd choices at minimum": non_strict_count,
        "every fewest odd is strict": non_strict_count == 0,
        "four mutually meeting knots": four_meet,
        "strict witness at minimum": strict_failures,
        "non-strict witness at its own minimum": non_strict_failures,
    }


def tally(rows, field):
    counts = Counter(r[field] for r in rows)
    return {str(key) if key is not None else "none": counts[key]
            for key in sorted(counts, key=lambda key: -1 if key is None else key)}


def summary(rows, archived_path):
    # Read the study's results only after producing the independent minima.
    archived = {r["start"]: r for r in json_lines(archived_path)}
    if archived.keys() != {r["start"] for r in rows}:
        raise ValueError("Grown start rosters differ.")
    fields = [
        "fewest failing pairs, odd",
        "fewest failing pairs, odd, not strict",
        "every fewest odd is strict",
        "four mutually meeting knots",
    ]
    differences = {field: [] for field in fields}
    strict_differences = []
    categories = Counter()
    cheaper = Counter()
    for row in rows:
        start = row["start"]
        record = archived[start]
        for field in fields:
            if row[field] != record[field]:
                differences[field].append(start)
        strict_min = record["fewest strict readers"]
        minimum = row["fewest failing pairs, odd"]
        has_min_strict = bool(row["strict odd choices at minimum"])
        if (strict_min == minimum) != has_min_strict or (strict_min is not None and strict_min < minimum):
            strict_differences.append(start)
        if strict_min is None:
            categories["no strict split in study"] += 1
        elif not has_min_strict:
            categories["strict split in study, all unrestricted minima cheaper"] += 1
            cheaper[minimum, strict_min] += 1
        elif row["non-strict odd choices at minimum"]:
            categories["strict and non-strict tie at unrestricted minimum"] += 1
        else:
            categories["all unrestricted minima strict"] += 1
    return {
        "population": "Grown closures admitting an odd birth choice, one vote per census start.",
        "count": len(rows),
        "strict witnesses at the unrestricted minimum checked from holders": sum(
            r["strict witness at minimum"] is not None for r in rows
        ),
        "non-strict witnesses at their own minimum checked from holders": sum(
            r["non-strict witness at its own minimum"] is not None for r in rows
        ),
        "fewest failing pairs among odd choices": tally(rows, "fewest failing pairs, odd"),
        "fewest failing pairs among non-strict odd choices": tally(rows, "fewest failing pairs, odd, not strict"),
        "all minimum odd choices strict": sum(r["every fewest odd is strict"] for r in rows),
        "all minimum odd choices strict differs from four mutually meeting knots": [
            r["start"] for r in rows if r["every fewest odd is strict"] != r["four mutually meeting knots"]
        ],
        "failing-pair minima against strict existence in archived rows": dict(sorted(categories.items())),
        "unrestricted minimum below archived strict minimum, one vote per census start": [
            {"unrestricted minimum": m, "strict minimum": s, "closures": n}
            for (m, s), n in sorted(cheaper.items())
        ],
        "differences from archived rows, by field": differences,
        "archived strict minimum ties or beats the independent minimum inconsistently": strict_differences,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codes", type=Path, default=INPUT)
    parser.add_argument("--sample", type=int, nargs="+", help="Print selected census starts, writing no files.")
    args = parser.parse_args()
    # This process never needs more than the single-process review allowance.
    memory, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = 1_750_000_000
    resource.setrlimit(resource.RLIMIT_AS, (min(value for value in (cap, memory, hard) if value > 0), hard))
    inputs = []
    for code in json_lines(args.codes):
        if code.get("population") == "birth" and code["odd"]:
            inputs.append(dict(code, start=code["key"]))
        elif "start" in code and code["odd attainable"]:
            inputs.append(code)  # The earlier pair-count referee's file format.
    if args.sample:
        wanted = set(args.sample)
        outcomes = [recount_one(r) for r in inputs if r["start"] in wanted]
        if {r["start"] for r in outcomes} != wanted:
            raise ValueError("Unknown sample start.")
        for row in outcomes:
            print(json.dumps(row))
        return
    rows = [recount_one(r) for r in inputs]
    status = summary(rows, STUDY / "results.jsonl")
    with (HERE / "failure_rows.jsonl").open("w") as handle:
        for row in rows:
            print(json.dumps(row, separators=(",", ":")), file=handle)
    (HERE / "failure_counts.json").write_text(json.dumps(status, indent=2) + "\n")


if __name__ == "__main__":
    main()
