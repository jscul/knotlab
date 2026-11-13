"""Plain independent controls for the addressed census validation gates.

These controls do not import addr or NumPy.  Address integers are read with
their first letter most significant; an ordinary word acts right to left.
"""

from collections import deque
import math


def automaton_parts(aut):
    """Return Python integer tuples, independently of the producer's storage."""
    if isinstance(aut, dict):
        aut = (aut["sw"], aut["d0"], aut["d1"])
    sw, d0, d1 = (tuple(map(int, part)) for part in aut)
    if not sw or len(sw) != len(d0) or len(sw) != len(d1):
        raise ValueError("invalid automaton component lengths")
    if any(bit not in (0, 1) for bit in sw):
        raise ValueError("nonbinary root permutation")
    if any(q < 0 or q >= len(sw) for q in d0 + d1):
        raise ValueError("successor outside the state set")
    return sw, d0, d1


def words(s):
    return ((),) + tuple((q,) for q in range(s)) + tuple(
        (q, r) for q in range(s) for r in range(s)
    )


def _state_at(sw, d0, d1, q, address, n):
    if n == 0:
        return 0
    first = address >> (n - 1)
    rest = address & ((1 << (n - 1)) - 1)
    successor = d1[q] if first else d0[q]
    return ((first ^ sw[q]) << (n - 1)) | _state_at(
        sw, d0, d1, successor, rest, n - 1
    )


def recursive_action(aut, word, n):
    """Evaluate every address with direct recursive letter processing."""
    sw, d0, d1 = automaton_parts(aut)
    image = []
    for address in range(1 << n):
        y = address
        for q in reversed(tuple(word)):
            y = _state_at(sw, d0, d1, int(q), y, n)
        image.append(y)
    return tuple(image)


def inverse_permutation(permutation):
    inverse = [None] * len(permutation)
    for source, target in enumerate(permutation):
        target = int(target)
        if target < 0 or target >= len(inverse) or inverse[target] is not None:
            raise ValueError("not a permutation")
        inverse[target] = source
    return tuple(inverse)


def relative_permutation(aut, wi, wj, n):
    """Compute gj gi^-1 by explicit permutations and array inversion."""
    left = recursive_action(aut, wi, n)
    right = recursive_action(aut, wj, n)
    inverse = inverse_permutation(left)
    return tuple(right[inverse[x]] for x in range(len(inverse)))


def unpack_key(key):
    if isinstance(key, dict):
        if "key" in key:
            return unpack_key(key["key"])
        return (
            int(key["s"]), tuple(map(int, key["sw"])),
            tuple(map(int, key["d0"])), tuple(map(int, key["d1"])),
            tuple(tuple(map(int, p)) for p in key["placements"]),
        )
    s, sw, d0, d1, placements = key
    return (
        int(s), tuple(map(int, sw)), tuple(map(int, d0)),
        tuple(map(int, d1)),
        tuple(sorted(set(tuple(sorted(map(int, p))) for p in placements))),
    )


def level_pattern(key, n):
    """Build triples without vectorized producer operations."""
    s, sw, d0, d1, placements = unpack_key(key)
    vocabulary = words(s)
    used = {w for placement in placements for w in placement}
    permutations = {
        w: recursive_action((sw, d0, d1), vocabulary[w], n) for w in used
    }
    result = set()
    for placement in placements:
        for address in range(1 << n):
            image = tuple(sorted(permutations[w][address] for w in placement))
            if len(set(image)) == 3:
                result.add(image)
    return tuple(sorted(result))


def brute_force_nae(pattern, n):
    """Read all 2^(2^n) assignments; report truth and the exact model count."""
    masks = tuple(sum(1 << int(v) for v in triple) for triple in pattern)
    model_count = 0
    first_model = None
    assignments = 1 << (1 << n)
    for assignment in range(assignments):
        allowed = True
        for mask in masks:
            selected = assignment & mask
            if selected == 0 or selected == mask:
                allowed = False
                break
        if allowed:
            model_count += 1
            if first_model is None:
                first_model = assignment
    return {
        "verdict": int(model_count > 0), "model_count": model_count,
        "assignments_read": assignments, "first_model": first_model,
    }


def model_satisfies(pattern, model, n):
    if model is None or len(model) != (1 << n):
        return False
    return all(len({bool(model[int(v)]) for v in triple}) == 2 for triple in pattern)


def nontrivial_states(aut):
    """A state is nonidentity exactly when a reachable state swaps a letter."""
    sw, d0, d1 = automaton_parts(aut)
    predecessors = [set() for _ in sw]
    for q in range(len(sw)):
        predecessors[d0[q]].add(q)
        predecessors[d1[q]].add(q)
    nontrivial = {q for q, bit in enumerate(sw) if bit}
    pending = deque(nontrivial)
    while pending:
        for q in predecessors[pending.popleft()]:
            if q not in nontrivial:
                nontrivial.add(q)
                pending.append(q)
    return frozenset(nontrivial)


def exact_activity_counts(aut, starts=None, limit=160):
    """Exact integer DP counts active sections, rather than graph cycles."""
    sw, d0, d1 = automaton_parts(aut)
    starts = tuple(range(len(sw))) if starts is None else tuple(map(int, starts))
    if not starts:
        raise ValueError("activity needs at least one starting map")
    nontrivial = nontrivial_states((sw, d0, d1))
    counts = [int(q in nontrivial) for q in range(len(sw))]
    theta = []
    for _ in range(limit):
        counts = [counts[d0[q]] + counts[d1[q]] for q in range(len(sw))]
        theta.append(max(counts[q] for q in starts))
    return tuple(theta)


def activity_label(theta):
    if len(theta) != 160:
        raise ValueError("the frozen finite check uses lengths 1 through 160")
    if theta[159] == 0:
        return "finitary"
    if theta[79] > 0 and theta[159] >= 1000 * theta[79]:
        return "exponential"
    if max(theta[80:]) <= max(theta[:80]):
        return "bounded"
    return "polynomial"


def gamma_probability(n):
    if n < 1:
        return 0.0
    return math.ldexp(1.0, -(2 * (int(n).bit_length() - 1) + 1))


def _gamma_q(a, x):
    """Regularized upper incomplete gamma; only a dependency fallback."""
    if x < 0 or a <= 0:
        raise ValueError("invalid incomplete gamma arguments")
    if x == 0:
        return 1.0
    scale = math.exp(a * math.log(x) - x - math.lgamma(a))
    eps, tiny = 2e-14, 1e-300
    if x < a + 1:
        term = total = 1.0 / a
        ap = a
        for _ in range(10000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) <= abs(total) * eps:
                return min(1.0, max(0.0, 1.0 - total * scale))
        raise ArithmeticError("incomplete gamma series did not converge")
    b = x + 1.0 - a
    c, d = 1.0 / tiny, 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) <= eps:
            return min(1.0, max(0.0, h * scale))
    raise ArithmeticError("incomplete gamma fraction did not converge")


def gamma_chisquare(samples, alpha=0.01):
    """Test exact cells with E>=5 and pool the remaining upper tail."""
    samples = tuple(map(int, samples))
    if not samples or min(samples) < 1:
        raise ValueError("positive gamma samples required")
    count = len(samples)
    cutoff = 1
    while count * gamma_probability(cutoff) >= 5:
        cutoff += 1
    observed = [0] * cutoff
    for value in samples:
        observed[value - 1 if value < cutoff else cutoff - 1] += 1
    probabilities = [gamma_probability(n) for n in range(1, cutoff)]
    probabilities.append(1.0 - math.fsum(probabilities))
    expected = [count * p for p in probabilities]
    if min(expected) < 5:
        raise ValueError("sample too small for the pooled-tail rule")
    statistic = math.fsum((o - e) ** 2 / e for o, e in zip(observed, expected))
    df = len(observed) - 1
    try:
        from scipy.stats import chi2
        pvalue = float(chi2.sf(statistic, df))
        method = "scipy.stats.chi2.sf"
    except ImportError:
        pvalue = _gamma_q(df / 2.0, statistic / 2.0)
        method = "independent regularized-upper-gamma fallback"
    cells = [
        {"value": n, "observed": observed[n - 1], "expected": expected[n - 1]}
        for n in range(1, cutoff)
    ]
    cells.append({"tail_from": cutoff, "observed": observed[-1], "expected": expected[-1]})
    return {
        "sample_count": count, "statistic": statistic, "degrees_of_freedom": df,
        "pvalue": pvalue, "alpha": alpha, "passed": pvalue >= alpha,
        "survival_method": method,
        "pooling": "Each exact value with expected count >=5; all remaining values in one upper-tail cell.",
        "cells": cells,
    }


def first_letter_settled(key):
    s, sw, _d0, _d1, placements = unpack_key(key)
    vocabulary = words(s)
    root_swap = [sum(sw[q] for q in word) % 2 for word in vocabulary]
    return all(len({root_swap[w] for w in p}) > 1 for p in placements)


def independent_fate(verdicts, knot_counts):
    if len(verdicts) != len(knot_counts):
        raise ValueError("one count per verdict is required")
    if all(int(k) == 0 for k in knot_counts):
        return "F0"
    if any(v is None for v in verdicts):
        return "FU"
    first = next(i for i, count in enumerate(knot_counts) if count)
    if int(verdicts[first]) == 0:
        return "F1"
    if any(int(v) == 0 for v in verdicts[first + 1:]):
        return "F2"
    return "F3"
