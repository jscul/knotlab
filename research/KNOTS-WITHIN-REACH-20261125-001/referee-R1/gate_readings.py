"""Exact gate and count readings using the frozen range and degree definitions."""

from collections import deque
from fractions import Fraction
from functools import lru_cache
from itertools import pairwise


FIRST_STEP = 4
DEGREES = range(4)


def smallest_start(counts, powers, end, ratio):
    """Earliest valid start for each right endpoint, by moving the extrema."""
    low = deque()
    high = deque()
    start = FIRST_STEP
    left = [start] * (end + 1)
    for r in range(start, end + 1):
        value = counts[r]
        denominator = powers[r]
        while low and counts[low[-1]] * denominator >= value * powers[low[-1]]:
            low.pop()
        while high and counts[high[-1]] * denominator <= value * powers[high[-1]]:
            high.pop()
        low.append(r)
        high.append(r)
        while counts[high[0]] * powers[low[0]] > ratio * counts[low[0]] * powers[high[0]]:
            if low[0] == start:
                low.popleft()
            if high[0] == start:
                high.popleft()
            start += 1
        left[r] = start
    return left


def limits(counts, a, z, j):
    normalized = [Fraction(counts[r], r**j) for r in range(a, z + 1)]
    return min(normalized), max(normalized)


def gate(curves, span, ratio, start_knots=()):
    size = len(curves)
    end = min((len(curve) - 1 for curve in curves.values()), default=0)
    if end < span * FIRST_STEP:
        return {"state": "short", "K": size, "least_l": end}
    start_knots = set(start_knots)
    widest_support = {}
    peak_support = {}
    profiles = {}
    for j in DEGREES:
        powers = [r**j for r in range(end + 1)]
        earliest = [FIRST_STEP] * (end + 1)
        support = [0] * (end + 1)
        widest_support[j] = 0
        for curve in curves.values():
            left = smallest_start(curve, powers, end, ratio)
            widest_support[j] += left[end] <= end // span
            for z in range(FIRST_STEP * span, end + 1):
                earliest[z] = max(earliest[z], left[z])
                support[z] += left[z] <= z // span
        profiles[j] = {
            z: earliest[z]
            for z in range(FIRST_STEP * span, end + 1)
            if support[z] == size
        }
        most = max(range(FIRST_STEP * span, end + 1), key=lambda z: (support[z], z))
        peak_support[j] = {"k": support[most], "range": [most // span, most]}
    alternatives = {j: [profile[max(profile)], max(profile)] for j, profile in profiles.items() if profile}
    record = {
        "state": "no gate", "K": size, "least_l": end,
        "reported partial support range": [end // span, end],
        "widest_support": widest_support, "peak_support": peak_support,
        "each_degree": alternatives,
    }
    if not alternatives:
        return record
    # At the swapped width and tolerance, different degrees can share an endpoint.
    z = max(segment[1] for segment in alternatives.values())
    options = sorted((j, profile[z]) for j, profile in profiles.items() if z in profile)
    j, a = options[0]
    normalized = {knot: limits(curve, a, z, j) for knot, curve in curves.items()}
    groups = {"all": normalized, "start": {}, "made": {}}
    for knot, value in normalized.items():
        groups["start" if knot in start_knots else "made"][knot] = value
    spread = {}
    for label, values in groups.items():
        if values:
            value = max(high for low, high in values.values()) / min(low for low, high in values.values())
            spread[label] = {"spread": float(value), "exact": str(value), "n": len(values),
                             "band": "at most 2" if value <= 2 else "at most 4" if value <= 4 else "above 4"}
    earlier = []
    end = a - 1
    while end >= FIRST_STEP * span:
        options_earlier = [(end_at, start_at, degree) for degree, profile in profiles.items()
                           for end_at, start_at in profile.items() if end_at <= end]
        if not options_earlier:
            break
        end_at, start_at, degree = min(options_earlier, key=lambda entry: (-entry[0], entry[2], entry[1]))
        earlier.append({"j": degree, "range": [start_at, end_at]})
        end = start_at - 1
    return {**record, "state": "holds", "j": j, "range": [a, z], "spread": spread,
            "at_canonical_end": options, "earlier": earlier}


def power_tail(counts, degree):
    """Return the first index of an exact suffix of this degree, if any."""
    if len(counts) < degree + 8:
        return None
    differences = counts
    for _ in range(degree):
        differences = [right - left for left, right in pairwise(differences)]
    constant = differences[-1]
    if not constant:
        return None
    first = len(differences) - 1
    while first > 0 and differences[first - 1] == constant:
        first -= 1
    return first if len(counts) - first >= degree + 8 else None


def power(counts):
    for phase in range(1, 5):
        strands = [counts[residue::phase] for residue in range(phase)]
        for degree in DEGREES:
            first = [power_tail(strand, degree) for strand in strands]
            if any(a is None for a in first):
                continue
            a = max((residue + (i - 1) * phase + 1 for residue, i in enumerate(first) if i), default=0)
            if all(len(counts[residue::phase]) - max(0, (a - residue + phase - 1) // phase) >= degree + 8
                   for residue in range(phase)):
                return degree, phase, a
    return None


def recurrence(counts):
    for order in range(1, 4):
        if len(counts) < 2 * order + 8:
            break
        equations = [[Fraction(counts[r - shift]) for shift in range(1, order + 1)] + [Fraction(counts[r])]
                     for r in range(len(counts) - order, len(counts))]
        for column in range(order):
            pivot = next((row for row in range(column, order) if equations[row][column]), None)
            if pivot is None:
                break
            equations[column], equations[pivot] = equations[pivot], equations[column]
            divisor = equations[column][column]
            equations[column] = [v / divisor for v in equations[column]]
            for row in range(order):
                if row != column and equations[row][column]:
                    factor = equations[row][column]
                    equations[row] = [v - factor * p for v, p in zip(equations[row], equations[column])]
        else:
            coefficients = [equation[-1] for equation in equations]
            r = len(counts) - order - 1
            while r >= order and counts[r] == sum(c * counts[r - lag] for lag, c in enumerate(coefficients, 1)):
                r -= 1
            a = r - order + 1
            if len(counts) - a >= 2 * order + 8:
                return order, a, coefficients
    return None


def ratio_tail(counts):
    increments = [right - left for left, right in pairwise(counts)]
    smallest = None
    a = len(increments) - 1
    while a > 0 and increments[a - 1] > 0 and 4 * increments[a] >= 5 * increments[a - 1]:
        ratio = Fraction(increments[a], increments[a - 1])
        smallest = ratio if smallest is None else min(smallest, ratio)
        a -= 1
    if len(increments) - 1 - a >= 8:
        return a + 1, smallest
    return None


def bound_tail(counts):
    z = len(counts) - 1
    if z < 8 * FIRST_STEP:
        return None
    for j in DEGREES:
        powers = [r**j for r in range(z + 1)]
        high = low = z
        a = z
        for r in range(z - 1, FIRST_STEP - 1, -1):
            next_high = r if counts[r] * powers[high] > counts[high] * powers[r] else high
            next_low = r if counts[r] * powers[low] < counts[low] * powers[r] else low
            if counts[next_high] * powers[next_low] > 2 * counts[next_low] * powers[next_high]:
                break
            high, low, a = next_high, next_low, r
        if a <= z // 8:
            return j, a, Fraction(counts[low], powers[low]), Fraction(counts[high], powers[high])
    return None


def doubling(counts):
    """The ±0.3 tolerance stated as two integer comparisons on tenth powers."""
    tenth_powers = [count**10 for count in counts]
    intervals = []
    previous = None
    first = FIRST_STEP
    end = (len(counts) - 1) // 2
    for r in range(FIRST_STEP, end + 2):
        j = None
        if r <= end:
            numerator = tenth_powers[2*r]
            denominator = tenth_powers[r]
            bit_difference = numerator.bit_length() - denominator.bit_length()
            nearest = (bit_difference + 5) // 10
            if numerator << 3 >= denominator << (10 * nearest) and numerator <= denominator << (10 * nearest + 3):
                j = nearest
        if j != previous:
            if previous is not None and r - 1 >= 2 * first:
                intervals.append({"j": previous, "range": [first, 2 * (r - 1)]})
            previous = j
            first = r
    return intervals[::-1]


@lru_cache(maxsize=8192)
def history_readings(counts, ended):
    """Return final readings and the two individual-count swaps."""
    z = len(counts) - 1
    bound = bound_tail(counts)
    swap = doubling(counts)
    if ended:
        return ("ENDED", None, [0, z]), bound, swap
    polynomial = power(counts)
    if polynomial is not None:
        j, _, a = polynomial
        return ("POWER", j, [a, z]), bound, swap
    linear = recurrence(counts)
    if linear is not None:
        k, a, _ = linear
        return ("LINREC", k, [a, z]), bound, swap
    if bound is not None:
        j, a, _, _ = bound
        return ("BOUND", j, [a, z]), bound, swap
    ratio = ratio_tail(counts)
    if ratio is not None:
        a, _ = ratio
        return ("RATIO", None, [a, z]), bound, swap
    return ("UNDECIDED", None, None), bound, swap


def roster_reading(counts):
    if len(counts) < 8:
        return "ALL WITHIN r", None
    exact = power(counts)
    if exact is not None:
        j, phase, first = exact
        return f"POWER({j})", [first, len(counts) - 1]
    recurrent = recurrence(counts)
    if recurrent is not None:
        order, first, _ = recurrent
        return f"LINREC({order})", [first, len(counts) - 1]
    ratio = ratio_tail(counts)
    if ratio is not None:
        first, _ = ratio
        return "RATIO", [first, len(counts) - 1]
    return "UNDECIDED", None
