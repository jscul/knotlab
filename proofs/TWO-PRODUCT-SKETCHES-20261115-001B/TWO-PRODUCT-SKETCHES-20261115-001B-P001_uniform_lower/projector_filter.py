"""Direct polar-matrix checks for the rank-seven restriction on an odd path."""
from collections import Counter


def apply_matrix(rows, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(rows))


def basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            index = vector.bit_length() - 1
            if index not in pivots:
                pivots[index] = vector
                break
            vector ^= pivots[index]
    return list(pivots.values())


def kernel(rows, size):
    pivots = {row.bit_length() - 1: row for row in basis(rows)}
    result = []
    for free in sorted(set(range(size)) - pivots.keys()):
        vec = 1 << free
        for i in sorted(pivots):
            if (pivots[i] & vec).bit_count() % 2:
                vec |= 1 << i
        result.append(vec)
    return result


def polar(mask, n):
    rows = [0] * n
    for i in range(n - 1):
        if mask >> i & 1:
            rows[i] ^= 1 << (i + 1)
            rows[i + 1] ^= 1 << i
    return rows


def restricted_rank(rows, vectors):
    forms = [apply_matrix(rows, vec) for vec in vectors]
    return len(basis(apply_matrix(vectors, form) for form in forms))


def solve_covector(full, covector):
    n = len(full)
    augmented = [row | ((covector >> i & 1) << n) for i, row in enumerate(full)]
    for column in range(n):
        pivot = next(i for i in range(column, n) if augmented[i] >> column & 1)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for i in range(n):
            if i != column and augmented[i] >> column & 1:
                augmented[i] ^= augmented[column]
    return sum((row >> n) << i for i, row in enumerate(augmented))


def check_mask(n, mask):
    full = polar((1 << (n - 1)) - 1, n)
    part = polar(mask, n)
    a = len(basis(part)) // 2
    kjk = [apply_matrix(part, solve_covector(full, row)) for row in part]
    if not any(kjk):
        assert a <= 1
        return "square_zero", a
    if kjk == part:
        assert a + len(basis(i ^ j for i, j in zip(full, part))) // 2 == n // 2
        return "projector", a

    # Kx and Ky span an isotropic pair for the induced form on im K,
    # with nonzero pairing for the inverse total polar form.
    units = [1 << i for i in range(n)]
    probes = units + [x ^ y for i, x in enumerate(units) for y in units[:i]]
    selected = None
    for x in probes:
        kx, k2x = apply_matrix(part, x), apply_matrix(kjk, x)
        for y in probes:
            if (kx & y).bit_count() % 2 == 0 and (k2x & y).bit_count() % 2:
                selected = [kx, apply_matrix(part, y)]
                break
        if selected is not None:
            break
    assert selected is not None
    while len(selected) < a:
        possible = (apply_matrix(part, x) for x in kernel(selected, n))
        new = next(form for form in possible if len(basis(selected + [form])) > len(selected))
        selected.append(new)
    space = kernel(selected, n)
    assert len(space) == n - a and restricted_rank(part, space) == 0
    residual = restricted_rank(full, space) // 2
    assert residual >= n // 2 - a + 1
    return "improved", residual


def audit():
    counts = Counter(check_mask(n, mask)[0] for n in (2, 4, 6, 8, 10)
                     for mask in range(1 << (n - 1)))
    long_mask = sum(1 << (i - 1) for i in (2, 4, 6, 8, 10, 12, 14))
    long_result = check_mask(32, long_mask)
    assert long_result[0] == "improved" and long_result[1] >= 10
    return {"small_masks": dict(sorted(counts.items())),
            "31_edge_nonprojector_mask": hex(long_mask),
            "31_edge_residual_half_rank": long_result[1]}


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), sort_keys=True))
