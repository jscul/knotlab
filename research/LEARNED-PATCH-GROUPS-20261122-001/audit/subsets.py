"""Independent exhaustive subset projections for the patch-group audit."""

from itertools import product


def subset_projections(rows):
    """Yield each subset and its totals in the supplied count rows."""
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Every count row must expose the same bin set")
    middle = width // 2

    def partial_projections(columns):
        column_ids = tuple(columns)
        for choices in product((0, 1), repeat=len(column_ids)):
            members = tuple(index for index, selected in zip(column_ids, choices, strict=True) if selected)
            row_totals = tuple(sum(row[index] for index in members) for row in rows)
            yield members, row_totals

    lower = list(partial_projections(range(middle)))
    upper = list(partial_projections(range(middle, width)))
    for (left_ids, left_totals), (right_ids, right_totals) in product(lower, upper):
        yield left_ids + right_ids, tuple(left + right for left, right in zip(left_totals, right_totals, strict=True))
