"""Check the count fibers directly using repeated crossings of original pairs."""

import json
from collections import defaultdict
from itertools import combinations
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def queries(p):
    observations = [0] * (p * p)
    difference_classes = [0] * p
    for state in range(p * p):
        original = divmod(state, p)
        x, y = original
        difference_classes[(y - x) % p] |= 1 << state
        for k in range(p):
            observations[p * k + x] |= 1 << state
            x, y = y, (2 * y - x) % p
        require((x, y) == original, "crossing period differs")
    return observations, difference_classes


def sums(table, masks):
    return tuple((table & mask).bit_count() for mask in masks)


def parity(counts):
    return tuple(count % 2 for count in counts)


def support(counts):
    return tuple(count > 0 for count in counts)


def union(masks):
    result = 0
    for mask in masks:
        result |= mask
    return result


def toggle_masks(rows):
    return [union(group) for size in range(0, len(rows) + 1, 2)
            for group in combinations(rows, size)]


def exact_class(table, rows):
    constant = [row for row in rows if (table & row) in (0, row)]
    copies = sum((table & row) == row for row in constant)
    partial_entries = table & ~union(constant)
    return {partial_entries | union(full) for full in combinations(constant, copies)}


def keeps_support(table, changed, observations):
    if not changed:
        return True
    for query in observations:
        if table & query & ~changed:
            continue
        selected = query & changed
        if not (table & selected) or (table & selected) == selected:
            return False
    return True


def changes_leaving_empty_queries(table, observations, rows):
    excluded = set()
    for query in observations:
        selected = [row for row in rows if row & table & query]
        if len(selected) % 2 == 0:
            excluded.add(union(selected))
    return excluded


def binary_rank(masks):
    basis = {}
    for row in masks:
        while row:
            leading = row.bit_length() - 1
            if leading not in basis:
                basis[leading] = row
                break
            row ^= basis[leading]
    return len(basis)


def check_exhaustive(p):
    observed, rows = queries(p)
    toggles = toggle_masks(rows)
    groups = defaultdict(lambda: defaultdict(set))
    for table in range(1 << (p * p)):
        counted = sums(table, observed)
        missing = sums(table, rows)
        pairs = {
            "exact": counted,
            "parity": parity(counted),
            "support_parity": (support(counted), parity(counted)),
            "exact_missing_support": (counted, support(missing)),
            "parity_missing_support": (parity(counted), support(missing)),
            "parity_missing_parity": (parity(counted), parity(missing)),
            "parity_missing_exact": (parity(counted), missing),
        }
        for name, key in pairs.items():
            groups[name][key].add(table)

    for family in groups["exact"].values():
        table = next(iter(family))
        require(family == exact_class(table, rows), "exact class differs")
    for family in groups["parity"].values():
        table = next(iter(family))
        require(family == {table ^ change for change in toggles}, "parity class differs")
        excluded = changes_leaving_empty_queries(table, observed, rows)
        incomplete = {f for f in family if any((f & q) == 0 for q in observed)}
        require(incomplete == {table ^ change for change in excluded},
                "incorrect count of incompletely supported tables in a parity class")
    require(all(len(family) == 1 for family in groups["exact_missing_support"].values()),
            "missing presence failed to complete exact counts")
    for family in groups["parity_missing_support"].values():
        table = next(iter(family))
        partial = [r for r in rows if (table & r) not in (0, r)]
        require(family == {table ^ change for change in toggle_masks(partial)},
                "missing presence changed the wrong parity class")
    for name in ("parity_missing_parity", "parity_missing_exact"):
        for family in groups[name].values():
            table = next(iter(family))
            if p != 2:
                expected = {table}
            elif name == "parity_missing_parity":
                expected = {table ^ change for change in toggles}
            else:
                balanced = all((table & row).bit_count() == 1 for row in rows)
                expected = {table, table ^ union(rows)} if balanced else {table}
            require(family == expected, f"incompatible augmented profile {name}")

    odd_unions = {union(subset) for size in range(1, p + 1, 2)
                  for subset in combinations(rows, size)}
    tied_at_threshold = set()
    for (presence, _), family in groups["support_parity"].items():
        table = next(iter(family))
        expected = {table ^ d for d in toggles if keeps_support(table, d, observed)}
        require(family == expected, "support-plus-parity test on toggled rows differs")
        require(len(family) == 1 or all(presence), "a negative answer left a mixed tie")
        threshold_members = {m for m in family if m.bit_count() == p}
        if len(family) > 1 and threshold_members:
            require(family == odd_unions, "unexpected mixed-reader tie at the threshold")
            tied_at_threshold.update(threshold_members)
    require(tied_at_threshold == set(rows), "threshold row missing, or spurious one")

    q = (1 << p) - 1
    exact_profiles = len(groups["exact"])
    parity_profiles = len(groups["parity"])
    require(exact_profiles == q**p + p * q**(p - 1), "exact profile count differs")
    require(parity_profiles == 1 << (p*p - p + 1), "parity profile count differs")
    return {
        "prime": p,
        "tables": 1 << (p*p),
        "exact_profiles": exact_profiles,
        "parity_profiles": parity_profiles,
        "threshold_tables_checked": comb(p*p, p),
        "threshold_tables_with_mixed_ties": len(tied_at_threshold),
        "mixed_profiles": len(groups["support_parity"]),
        "parity_plus_missing_exact_profiles": len(groups["parity_missing_exact"]),
    }


def check_larger(p):
    observed, rows = queries(p)
    measured_rank = binary_rank(observed)
    augmented_rank = binary_rank(observed + rows)
    require(measured_rank == p*p - p + 1, "unexpected parity rank")
    require(augmented_rank == p*p, "missing direction failed to restore odd-prime rank")
    toggles = toggle_masks(rows)

    # Arbitrary partial classes and the uniform tables exercise both sorts of tie.
    seed = sum(1 << i for i in range(p*p) if (i*i + 3*i + 1) % 11 < 5)
    cases = {seed, 0, rows[0], rows[0] | rows[1], union(rows)}
    differences = [(y-x) % p for x in range(p) for y in range(p)]
    minimum_fully_supported = len(toggles)
    for table in cases:
        counted = sums(table, observed)
        population = table.bit_count()
        missing = sums(table, rows)
        for i, d in enumerate(differences):
            incident_sum = sum(c for c, query in zip(counted, observed) if query & (1 << i))
            require(incident_sum + missing[d] - population == p * ((table >> i) & 1),
                    "incidence inversion failed")
        excluded = changes_leaving_empty_queries(table, observed, rows)
        fully_supported = 0
        for changed in toggles:
            other = table ^ changed
            other_counts = sums(other, observed)
            require((changed in excluded) == (not all(other_counts)), "bad empty-query toggle")
            fully_supported += int(all(other_counts))
            require(parity(counted) == parity(other_counts), "whole-class toggle changed parity")
            require((counted == other_counts) == (other in exact_class(table, rows)),
                    "toggle gave wrong exact classification")
            require((support(counted) == support(other_counts))
                    == keeps_support(table, changed, observed), "wrong support under a toggle")
            if changed:
                require((support(counted) == support(other_counts))
                        == (all(counted) and all(other_counts)), "full support equivalence failed")
            require(not changed or parity(missing) != parity(sums(other, rows)),
                    "missing parity failed to distinguish the toggle")
        require(fully_supported == len(toggles) - len(excluded), "wrong mixed fiber cardinality")
        minimum_fully_supported = min(minimum_fully_supported, fully_supported)
    if p >= 7:
        require(minimum_fully_supported >= len(toggles) - p*p,
                "too few fully supported tables in a parity class")

    require(parity(sums(0, observed)) == parity(sums(rows[0] | rows[1], observed)),
            "zero and two rows must have equal parity")
    require(support(sums(0, observed)) != support(sums(rows[0] | rows[1], observed)),
            "zero and two rows must have different existence answers")
    # One changed state at size p ties under existence alone, and parity splits it.
    common = rows[0] & ~(1 << 0)
    first = common | (1 << 1)
    second = common | (1 << 2)
    require(support(sums(first, observed)) == support(sums(second, observed)),
            "previous shared-state tie was lost")
    require(parity(sums(first, observed)) != parity(sums(second, observed)),
            "parity failed to separate the previous shared-state tie")
    odd_rows = {rows[0] ^ toggle for toggle in toggles}
    odd_weights = {size: sum(table.bit_count() == p*size for table in odd_rows)
                   for size in range(1, p + 1, 2)}
    require(all(count == comb(p, size) for size, count in odd_weights.items()),
            "odd-class ambiguity has unexpected weights")
    report = {"prime": p, "observed_rank": measured_rank, "augmented_rank": augmented_rank,
              "base_tables": len(cases), "tested_toggles_per_table": len(toggles),
              "minimum_fully_supported_in_tested_parity_fibers": minimum_fully_supported}
    report["full_row_mixed_fiber_by_size"] = {p*size: count for size, count in odd_weights.items()}
    if p == 5:
        # The measured rank and the independent whole-class vectors exhaust
        # the possible parity twins, including tables of unrestricted size.
        rows_set = set(rows)
        tied = set()
        examined = 0
        for members in combinations(range(p*p), p):
            table = sum(1 << i for i in members)
            present = tuple(bool(table & query) for query in observed)
            for changed in toggles[1:]:
                other = table ^ changed
                if all(bool(other & q) == bit for q, bit in zip(observed, present)):
                    require(table in rows_set, "larger mixed tie survived outside a full row")
                    tied.add(table)
            examined += 1
        require(tied == rows_set, "larger threshold class was incomplete")
        report.update(threshold_tables_checked=examined, threshold_tables_with_mixed_ties=len(tied))
    return report


if __name__ == "__main__":
    exhaustive = [check_exhaustive(p) for p in (2, 3)]
    larger = [check_larger(p) for p in (5, 7)]
    print(json.dumps({"status": "passed", "exhaustive": exhaustive, "larger": larger}))
