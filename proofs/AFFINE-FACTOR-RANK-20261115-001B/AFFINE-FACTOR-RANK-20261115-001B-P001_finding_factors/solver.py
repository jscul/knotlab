"""Find a minimum static span of eligible, formally original product factors."""

from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


@cache
def named_kernel():
    scope = "PRODUCT-NAME-TRANSFER-20261115-001A"
    source = Path(__file__).resolve().parents[3] / "proofs" / scope
    source = source / (scope + "-P001_named_substitution") / "solver.py"
    spec = spec_from_file_location("factor_rank_named_kernel", source)
    kernel = module_from_spec(spec)
    spec.loader.exec_module(kernel)
    return kernel


def _eligible_rows(n, pairs):
    if type(n) is not int or n < 0:
        raise ValueError("invalid base-variable count")
    rows = []
    for i, pair in enumerate(pairs):
        if len(pair) != 2:
            raise ValueError("each product declaration has two factors")
        row = []
        for raw in pair:
            form = named_kernel().affine(raw, n+i)
            support = frozenset(term[0] for term in form if term)
            if any(v > n for v in support):
                row.append(None)
            else:
                row.append((support, int(() in form)))
        rows.append(tuple(row))
    return rows


def _reduce(slope, echelon):
    """Return the residual and a mask of generators whose XOR was removed."""
    coordinates = 0
    for pivot, vector, mask in echelon:
        if pivot in slope:
            slope = slope ^ vector
            coordinates ^= mask
    return slope, coordinates


def _bounded(rows, budget):
    stack = [((), ())]
    while stack:
        generators, echelon = stack.pop()
        for gate, row in enumerate(rows):
            extensions = {}
            for side, option in enumerate(row):
                if option is None:
                    continue
                slope, _ = option
                residual, mask = _reduce(slope, echelon)
                if not residual:
                    break
                extensions.setdefault(residual, (side, slope, mask))
            else:
                if len(generators) < budget:
                    for residual, (side, slope, mask) in reversed(tuple(extensions.items())):
                        entry = (max(residual), residual, mask ^ (1 << len(generators)))
                        new_echelon = tuple(sorted((*echelon, entry), key=lambda v: -v[0]))
                        stack.append(((*generators, (gate, side, slope)), new_echelon))
                break  # This gate is uncovered. Every extending solution hits one of its options.
        else:
            return _certificate(rows, generators, echelon)
    return None


def _certificate(rows, generators, echelon):
    orientations, coordinates, offsets = [], [], []
    selected = {gate: side for gate, side, _ in generators}
    for gate, row in enumerate(rows):
        choices = (selected[gate],) if gate in selected else range(2)
        for side in choices:
            option = row[side]
            if option is not None:
                residual, mask = _reduce(option[0], echelon)
                if not residual:
                    orientations.append(side)
                    coordinates.append(mask)
                    offsets.append(option[1])
                    break
        else:
            raise AssertionError("certificate has an uncovered declaration")
    return {"rank": len(generators),
            "basis": [[[v] for v in sorted(slope)] for _, _, slope in generators],
            "basis_gates": [gate for gate, _, _ in generators],
            "orientations": orientations, "coordinates": coordinates, "offsets": offsets}


def minimum_span(n, declaration_factor_pairs, budget=None):
    """Minimum covering span on raw sequential factors, or None if no span fits.

    Each of the two raw factors is a list of monomials in the named kernel's
    format. Original variables are numbered 1..n. The kth gate may refer to
    original variables and earlier names. Constants cost zero rank.
    """
    if budget is not None and (type(budget) is not int or budget < 0):
        raise ValueError("the rank budget must be a nonnegative integer")
    rows = _eligible_rows(n, declaration_factor_pairs)
    if any(all(option is None for option in row) for row in rows):
        return None
    maximum = len(rows) if budget is None else min(budget, len(rows))
    for limit in range(maximum+1):
        result = _bounded(rows, limit)
        if result is not None:
            return result
    return None


def minimum_proof_span(n, cnf, proof, budget=None, *, convention="multiset"):
    """Validate the full named refutation and measure every supplied declaration."""
    named_kernel().verify(n, cnf, proof, convention=convention)
    pairs = (row["factors"] for row in proof if row["rule"] == "define")
    return minimum_span(n, pairs, budget)
