"""Replay selected attachments of the two competing four-distinction stars."""

from itertools import combinations
import json

from targeted_countermodel import ROOT, adjoin, ambiguity, continuation


R, W, B, C, WB, WC, _BC, X = range(7, 15)
CASES = (
    ("three unary joins", None, None, (2, 2, 2)),
    ("one additional old parent", None, 1, (2, 2, 2)),
    ("two additional old parents", 1, 2, (2, 2, 2)),
    ("two old parents and three-output pair joins", 1, 2, (3, 3, 3)),
)


def fixture(gluing, extra_b, extra_c, pair_counts):
    checks = ((0, 1, 2),)
    for site, parents in enumerate(continuation.CUBE_PARENTS, 1):
        count = 3 if site in (R, extra_b, extra_c) else 2
        checks, _ = adjoin(gluing, checks, parents, count)
    for extra in (None, extra_b, extra_c):
        checks, _ = adjoin(gluing, checks, (R,) if extra is None else (R, extra), 3)
    for parents, count in zip(((W, B), (W, C), (B, C), (WB, WC)), (*pair_counts, 2), strict=True):
        checks, _ = adjoin(gluing, checks, parents, count)
    gluing.replay(checks)
    return checks


def marked_match(api, matrix, source, target):
    left = api.ColoredMatrix.make(matrix, tuple(i in source for i in range(len(matrix))))
    right = api.ColoredMatrix.make(matrix, tuple(i in target for i in range(len(matrix))))
    return next(api.isometries(left, right), None)


def compare(api, gluing, label, extra_b, extra_c, pair_counts):
    checks = fixture(gluing, extra_b, extra_c, pair_counts)
    holders, _ = gluing.incidence(checks)

    def shared(first, second):
        bit, = set(checks[first]) & set(checks[second])
        return bit

    w, b, c = (next(bit for bit in checks[j] if holders[bit] == [j]) for j in (W, B, C))
    x, y = (bit for bit in checks[X] if holders[bit] == [X])
    t, s = shared(R, W), shared(R, B)
    legal, forbidden = frozenset((y, b, c)), frozenset((w, b, c))
    menu = ambiguity.triples(gluing, checks)
    assert legal in menu and forbidden not in menu

    bonds = continuation.cut_supports(gluing, checks)
    mask = [sum(1 << bit for bit in row) for row in checks]
    expected = {mask[X]} | {mask[X] ^ mask[j] for j in (WB, WC) if len(checks[j]) == 4}
    assert all({word for word in bonds if word.bit_count() <= 6 and word & (1 << bit)} == expected
               for bit in (x, y))
    matrix = continuation.dense(gluing.scalar_table(bonds, len(holders)), len(holders))
    capped = tuple(tuple(min(d, 6) for d in row) for row in matrix)
    for table in (matrix, capped):
        assert marked_match(api, table, legal, legal) is not None
        assert marked_match(api, table, legal, forbidden) is None

    swaps = ((t, x), (w, y), (shared(W, WB), shared(X, WB)), (shared(W, WC), shared(X, WC)))
    move = list(range(len(matrix)))
    for p, q in swaps:
        move[p], move[q] = q, p
    assert frozenset(move[bit] for bit in legal) == forbidden
    assert matrix[t][s] <= 5 < matrix[x][s]
    differences = sum(matrix[i][j] != matrix[move[i]][move[j]]
                      for i, j in combinations(range(len(matrix)), 2))
    order, _, generators = api.Quotient.make(matrix).automorphisms()
    assert all(api.disagreement(matrix, matrix, move) is None for move in generators)
    assert all(api.transported(menu, move) == menu for move in generators)
    mark_distances = [sorted(matrix[i][j] for i, j in combinations(sorted(marks), 2))
                      for marks in (legal, forbidden)]
    return {"case": label, "junction_supports": checks, "width": len(matrix),
            "legal_marks": sorted(legal), "forbidden_marks": sorted(forbidden),
            "within_mark_distances": mark_distances, "literal_exchange": swaps,
            "distinguishing_pairs": ((t, s), (x, s)), "distances": (matrix[t][s], matrix[x][s]),
            "literal_exchange_changed_entries": differences, "full_table_automorphism_order": order,
            "full_table_generators_checked": len(generators), "legal_triples": len(menu),
            "marked_match_at_full_distance_or_capped_through_five": False}


if __name__ == "__main__":
    api, gluing = (continuation.load(ROOT, *source) for source in continuation.SOURCES[1:])
    print(json.dumps([compare(api, gluing, *case) for case in CASES], indent=2))
