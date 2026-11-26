"""Recount the registered run 1 table and screen from the recorded sequences."""

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
import gzip
import itertools
import json
from math import comb, factorial, isclose, lcm
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[3]
TICKET = "KNOTS-WITHIN-REACH-20261125-001A"
STARTS = ROOT / "research" / TICKET
ARTIFACTS = ROOT / "artifacts" / TICKET / (TICKET + "-E001_knots_within_reach")
LAWS = tuple(f"L{i}" for i in range(12))
CAPPED = ("L1", "L6", "L7", "L10", "L11")
MAX_POWER = 3


def difference(values):
    return tuple(right - left for left, right in zip(values, values[1:]))


def power(values, first):
    for phases in (1, 2, 3, 4):
        differences = [values[offset::phases] for offset in range(phases)]
        for degree in range(MAX_POWER + 1):
            previous = []
            for offset, seq in enumerate(differences):
                if len(seq) < 8 or not seq[-1]:
                    break
                last_change = next(
                    (i for i in range(len(seq) - 2, -1, -1) if seq[i] != seq[-1]), -1
                )
                if len(seq) - last_change - 1 < 8:
                    break
                previous.append(offset + phases * last_change)
            else:
                return ("POWER", first + max(-1, *previous) + 1, degree, phases)
            differences = [difference(seq) for seq in differences]
    return None


def solve(equations):
    rows = [list(map(Fraction, row)) for row in equations]
    order = len(rows)
    for column in range(order):
        pivot = next((i for i in range(column, order) if rows[i][column]), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        denominator = rows[column][column]
        rows[column] = [value / denominator for value in rows[column]]
        for i, row in enumerate(rows):
            if i != column and row[column]:
                rows[i] = [a - row[column] * b for a, b in zip(row, rows[column])]
    return tuple(row[-1] for row in rows)


def linear_recurrence(values, first):
    for order in (1, 2, 3):
        if len(values) < 2 * order + 8:
            break
        equations = [
            tuple(values[i - lag] for lag in range(1, order + 1)) + (values[i],)
            for i in range(len(values) - order, len(values))
        ]
        coefficients = solve(equations)
        if coefficients is None:
            continue
        first_valid = order
        for i in range(len(values) - order - 1, order - 1, -1):
            if values[i] != sum(
                coefficient * values[i - lag]
                for lag, coefficient in enumerate(coefficients, 1)
            ):
                first_valid = i + 1
                break
        start = first_valid - order
        if len(values) - start >= 2 * order + 8:
            return ("LINREC", first + start, order, coefficients)
    return None


@lru_cache(maxsize=8192)
def earliest_bound_starts(values, degree, first=0):
    """At each end, find the least start satisfying the factor-of-two bound."""
    end = first + len(values) - 1
    weights = [i**degree for i in range(end + 1)]
    smallest, largest = deque(), deque()
    a = 4
    fits = [None] * (end + 1)
    for z in range(4, end + 1):
        v = values[z - first]
        while smallest and v * weights[smallest[-1]] <= values[smallest[-1] - first] * weights[z]:
            smallest.pop()
        while largest and v * weights[largest[-1]] >= values[largest[-1] - first] * weights[z]:
            largest.pop()
        smallest.append(z)
        largest.append(z)
        while (
            values[largest[0] - first] * weights[smallest[0]]
            > 2 * values[smallest[0] - first] * weights[largest[0]]
        ):
            if smallest[0] == a:
                smallest.popleft()
            if largest[0] == a:
                largest.popleft()
            a += 1
        if z >= 8 * a:
            fits[z] = a
    return tuple(fits)


def exact(values, first):
    return power(values, first) or linear_recurrence(values, first)


@lru_cache(maxsize=8192)
def read_sequence(values, first, ended, floor=Fraction(5, 4), earlier=False):
    if ended:
        return (("ENDED", first), ())
    end = first + len(values) - 1
    verdict = exact(values, first)
    if not verdict and end >= 32:
        bounds = []
        for degree in range(MAX_POWER + 1):
            a = earliest_bound_starts(values, degree, first)[end]
            if a is not None:
                bounds.append(("BOUND", a, degree))
        if bounds:
            verdict = min(bounds, key=lambda candidate: candidate[1])
    if not verdict:
        increments = values if first == 1 else difference(values)
        a = len(increments) - 1
        ratio = None
        while a > 0 and increments[a - 1] > 0:
            candidate = Fraction(increments[a], increments[a - 1])
            if candidate < floor:
                break
            ratio = candidate if ratio is None else min(ratio, candidate)
            a -= 1
        verdict = ("RATIO", a + 1, ratio) if len(increments) - a >= 9 else ("UNDECIDED", None)
    previous = []
    if earlier:
        prior_end = verdict[1]
        while prior_end is not None and prior_end > first:
            disp = exact(values[:prior_end - first], first)
            if disp is None:
                break
            previous.append((disp, prior_end - 1))
            prior_end = disp[1]
    return verdict, tuple(previous)


def stored_signature(reading):
    if reading is None:
        return ("ENDED", None)
    verdict = reading["verdict"]
    a = reading["segment"][0] if reading.get("segment") else None
    if verdict == "POWER":
        return (verdict, a, reading["j"], reading.get("m", 1))
    if verdict == "LINREC":
        return (verdict, a, reading["k"])
    if verdict == "BOUND":
        return (verdict, a, reading["j"])
    if verdict == "RATIO":
        return (verdict, a)
    return (verdict, None)


def comparable(reading):
    verdict = reading[0]
    if verdict == "LINREC":
        return reading[:3]
    if verdict == "RATIO":
        return reading[:2]
    if verdict == "ENDED":
        return (verdict, None)
    return reading


@lru_cache(maxsize=1024)
def integer_polynomial(serialized):
    coefficients = [Fraction(value.strip()) for value in serialized.strip("[]").split(",")]
    denominator = lcm(*(value.denominator for value in coefficients))
    return tuple(int(value * denominator) for value in coefficients), denominator


def parameters_match(verdict, reading, values, first):
    name, start, *details = verdict
    if name == "POWER":
        degree, phases = details
        saved = [reading["poly"]] if phases == 1 else reading["poly_by_phase"]
        polynomials = [integer_polynomial(poly) for poly in saved]
        for r in range(start, first + len(values)):
            phase = r % phases
            x = (r - phase) // phases
            coeffs, denominator = polynomials[phase]
            if len(coeffs) != degree + 1 or not coeffs[-1]:
                return False
            result = 0
            for coefficient in reversed(coeffs):
                result = result * x + coefficient
            if result != values[r - first] * denominator:
                return False
    if name == "LINREC":
        _, coefficients = details
        if tuple(map(Fraction, reading["coeffs"])) != coefficients:
            return False
    if name == "RATIO" and Fraction(reading["x_exact"]) != details[0]:
        return False
    if name == "BOUND":
        degree = details[0]
        series = [values[r - first] / r**degree for r in range(start, first + len(values))]
        if not (isclose(min(series), reading["c"]) and isclose(max(series), reading["C"])):
            return False
    return True


def category(reading):
    verdict = reading[0]
    return f"{verdict}({reading[2]})" if verdict in ("POWER", "BOUND", "LINREC") else verdict


def screen(curves):
    furthest = min(len(counts) - 1 for counts in curves)
    if furthest < 32:
        return ("undecided (range)", None, None)
    fitted = []
    for degree in range(MAX_POWER + 1):
        possible = {z: 4 for z in range(32, furthest + 1)}
        for counts in curves:
            starts = earliest_bound_starts(counts, degree)
            possible = {
                z: max(a, starts[z]) for z, a in possible.items() if starts[z] is not None
            }
            if not possible:
                break
        if possible:
            z = max(possible)
            fitted.append((z, possible[z], degree))
    if not fitted:
        return ("no j", None, None)
    z, a, degree = min(fitted, key=lambda item: (-item[0], item[1], item[2]))
    return (f"holds j={degree}", a, z)


def doubling(values):
    low_scale, high_scale = 2**(-0.3), 2**0.3
    hits = []
    z = (len(values) - 1) // 2
    while z >= 4:
        j = next(
            (j for j in range(4) if low_scale <= values[2*z] / (values[z] * 2**j) <= high_scale),
            None,
        )
        if j is None:
            z -= 1
            continue
        a = z
        while a > 4 and low_scale <= values[2*(a-1)] / (values[a-1] * 2**j) <= high_scale:
            a -= 1
        if z >= 2 * a:
            hits.append({"j": j, "range": [a, 2 * z]})
        z = a - 1
    return hits


def parity_passes(stars):
    masks = [sum(1 << x for x in star) for star in stars]
    span = {0}
    for mask in masks:
        span |= {other ^ mask for other in span}
    return all(
        not any(other and other != mask and other & mask == other for other in span)
        for mask in masks
    )


def labelled_weight(start):
    stars = [set(x) for x in start["stars"]]
    n = len(stars)
    common = [[0 if i == j else len(stars[i] & stars[j]) for j in range(n)] for i in range(n)]
    loose = tuple(map(len, (star - set.union(*(stars[:i] + stars[i + 1:])) for i, star in enumerate(stars))))
    assert loose == tuple(start["loose"])
    automorphisms = sum(
        all(loose[i] == loose[p[i]] for i in range(n))
        and all(common[i][j] == common[p[i]][p[j]] for i in range(n) for j in range(i))
        for p in itertools.permutations(range(n))
    )
    return factorial(n) // automorphisms


def display_fraction(value):
    return {"exact": str(value), "decimal": float(value)}


def share_interval(small_hits, hits, size, total, sample, n_population, divisor=40):
    """Equal-tailed finite-population interval, inverting exact hypergeometric tails."""
    denominator = comb(size, sample)

    def tail(count, upper):
        low = max(0, sample - (size - count))
        high = min(sample, count)
        support = range(max(low, hits), high + 1) if upper else range(low, min(high, hits) + 1)
        return sum(comb(count, i) * comb(size - count, sample - i) for i in support)

    lo, hi = hits, size - (sample - hits)
    while lo < hi:
        mid = (lo + hi) // 2
        if divisor * tail(mid, True) >= denominator:
            hi = mid
        else:
            lo = mid + 1
    low = lo
    lo, hi = hits, size - (sample - hits)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if divisor * tail(mid, False) >= denominator:
            lo = mid
        else:
            hi = mid - 1
    assert total + size == n_population
    return [(small_hits + x) / n_population for x in (low, lo)]


def weighted_tables(classified, starts, weights, allowed, scratch, expected_five, complete):
    tables = {}
    for family in ("nae", "parity"):
        for exclude in (False, True):
            key = family + (" without disclosed 64 sample starts" if exclude else "")
            population = {i for i in allowed[family] if not exclude or i not in scratch}
            options = {}
            for law in LAWS:
                cells = {
                    i: r for (i, other), r in classified.items() if other == law and i in population
                }
                if not cells:
                    continue
                small = {i: r for i, r in cells.items() if starts[i]["n"] < 5}
                five = {i: r for i, r in cells.items() if starts[i]["n"] == 5}
                counts = Counter(cells.values())
                details = {"raw_counts": dict(sorted(counts.items()))}
                options[law] = details
                if not complete:
                    continue
                law_population = {i for i in population if law != "L8" or starts[i]["n"] < 5}
                target_five = sum(starts[i]["n"] == 5 for i in law_population)
                expected_multiplier = Fraction(3157, expected_five) if five else Fraction(0)
                multiplier = Fraction(target_five, len(five)) if five else Fraction(0)
                details["raw_small_counts"] = dict(sorted(Counter(small.values()).items()))
                details["raw_five_counts"] = dict(sorted(Counter(five.values()).items()))
                details["n_population"] = len(law_population)
                details["conditional_five_multiplier"] = str(multiplier)
                details["labelled_five_effective_n"] = (
                    sum(weights[i] for i in five)**2 / sum(weights[i]**2 for i in five) if five else None
                )
                estimators = defaultdict(dict)
                for label in sorted(counts):
                    sample_small = sum(r == label for r in small.values())
                    sample_five = sum(r == label for r in five.values())
                    exact_population = Fraction(sample_small + multiplier * sample_five, len(law_population))
                    registered = Fraction(
                        sample_small + expected_multiplier * sample_five, len(law_population)
                    )
                    estimators["census_ratio_conditional_on_eligible_sample"][label] = display_fraction(exact_population)
                    estimators["census_registered_multiplier_fixed_population"][label] = display_fraction(registered)
                    for name, factor in (
                        ("labelled_registered_ratio", expected_multiplier),
                        ("labelled_conditional_ratio", multiplier),
                        ("census_registered_multiplier_ratio", expected_multiplier),
                    ):
                        mass = weights if name.startswith("labelled") else dict.fromkeys(cells, 1)
                        numerator = sum(mass[i] for i, r in small.items() if r == label) + factor * sum(
                            mass[i] for i, r in five.items() if r == label
                        )
                        denominator = sum(mass[i] for i in small) + factor * sum(mass[i] for i in five)
                        estimators[name][label] = display_fraction(Fraction(numerator, denominator))
                details["estimators"] = dict(estimators)
                if law in ("L6", "L9") and family == "nae" and not exclude:
                    details["degree_1_95_percent_finite_population_interval"] = share_interval(
                        sum(r == "POWER(1)" for r in small.values()),
                        sum(r == "POWER(1)" for r in five.values()),
                        target_five, len(small), len(five), len(law_population),
                    )
            tables[key] = options
    return tables


def check_trajectory(row, problems):
    rounds = row["rounds_done"]
    births = row["births"]
    parts = row["part_sizes_per_round"]
    key = (row["index"], row["law"])
    if len(births) != rounds or len(parts) != rounds + 1:
        problems["round ledger length"].append(key)
    if row["knots"] != len(row["classes"]["a"]) + sum(births):
        problems["birth ledger sum"].append(key)
    for t, saved in enumerate(row["births_by_part"]):
        if sum(saved) != births[t]:
            if len(saved) == 8 and row["parts_per_round"][t] > 8 and sum(saved) < births[t]:
                problems["truncated birth split"].append((key, t + 1, len(saved), births[t], sum(saved)))
            else:
                problems["births by part sum"].append((key, t + 1))
    for t, saved in enumerate(parts):
        if len(saved) != row["parts_per_round"][t]:
            if len(saved) == 8 and row["parts_per_round"][t] > 8:
                problems["truncated member split"].append((key, t, row["parts_per_round"][t], sum(saved)))
                continue
            problems["part count sum"].append((key, t))
        if sum(saved) != row["members_per_round"][t]:
            problems["member count sum"].append((key, t))


def p4_reading(row):
    parts = row["part_sizes_per_round"]
    n = [len(members) for members in parts]
    largest = [max(members, default=0) for members in parts]
    gains_a = difference(largest[36:41])
    gains_b = difference(largest[96:101])
    return {
        "same_checkpoint_parts": n[36] == n[40] and n[96] == n[100],
        "same_parts_at_every_round_36_to_100": len(set(n[36:101])) == 1,
        "more_parts_at_100": n[100] > n[40],
        "any_multiplication_after_40": any(a < b for a, b in zip(n[40:], n[41:])),
        "constant_gains_within_each_span": len(set(gains_a)) == 1 and len(set(gains_b)) == 1,
        "same_gain_in_both_spans": len(set(gains_a + gains_b)) == 1,
        "constant_gain_at_every_round_36_to_100": len(set(difference(largest[36:101]))) == 1,
        "gains": (gains_a[0], gains_b[0]),
    }


def replay(limit):
    starts = json.loads((STARTS / "census_starts.json").read_text())
    saved_order = json.loads((STARTS / "five_knot_order.json").read_text())
    small_ids = [i for i, s in enumerate(starts) if s["n"] in (3, 4)]
    large_ids = [i for i, s in enumerate(starts) if s["n"] == 5]
    Random(202611251).shuffle(large_ids)
    assert saved_order["order"] == large_ids
    scratch = set(Random(20261125).sample(small_ids + sorted(large_ids), 64))
    assert saved_order["in_scratch_64"] == [i in scratch for i in large_ids]
    replay_ids = set(small_ids + large_ids[:250])
    all_ids = set(small_ids + large_ids)
    weights = {i: labelled_weight(starts[i]) for i in all_ids}
    assert all(starts[i]["w_labelled"] == w for i, w in weights.items())
    admissible = {i for i in all_ids if parity_passes(starts[i]["stars"])}
    expected = [
        (i, law)
        for i in small_ids + large_ids[:250]
        for law in LAWS
        if law != "L8" or starts[i]["n"] < 5
    ]
    pairs_seen = set()
    problems = defaultdict(list)
    classifications = {}
    parity = {}
    high_births = defaultdict(list)
    classifications_by_round_limit = defaultdict(Counter)
    birth_recurrences = defaultdict(Counter)
    screens = defaultdict(Counter)
    screens_nonconstant = defaultdict(Counter)
    history = defaultdict(Counter)
    changes_from_swaps = defaultdict(Counter)
    p4 = defaultdict(list)
    p4_parity_eligible = []
    counts = Counter()
    record_statuses = defaultdict(Counter)
    replay_rows = 0
    with gzip.open(ARTIFACTS / "run1.jsonl.gz", "rt") as source:
        for record in map(json.loads, itertools.islice(source, limit)):
            replay_rows += 1
            index = record["index"]
            law = record["law"]
            key = index, law
            assert key not in pairs_seen and expected[record["item"]] == key
            pairs_seen.add(key)
            assert record["start"] == f"census:{index}"
            assert record["small"] == (starts[index]["n"] < 5)
            birth_list = tuple(record["births"])
            ended = record["ended"] is not None
            check_trajectory(record, problems)
            record_statuses[law][record["ended"] or record["stop"] or "round 100"] += 1
            birth_verdict, previous = read_sequence(birth_list, 1, ended, earlier=True)
            births = category(birth_verdict)
            classifications[key] = births
            recorded = stored_signature(record["births_reading"])
            if comparable(birth_verdict) != recorded:
                problems["births verdict or segment"].append((key, str(birth_verdict), str(recorded)))
            elif not parameters_match(birth_verdict, record["births_reading"], birth_list, 1):
                problems["births reading parameters"].append(key)
            if not ended:
                recorded_previous = [
                    (stored_signature(x), x["segment"][1]) for x in record["births_reading"].get("earlier", ())
                ]
                if [(comparable(v), end) for v, end in previous] != recorded_previous:
                    problems["earlier births segments"].append(key)
            if birth_verdict[0] == "LINREC":
                birth_recurrences[law][str(tuple(map(str, birth_verdict[3])))] += 1
            if law in CAPPED and (births in ("POWER(2)", "POWER(3)", "RATIO") or birth_verdict[0] == "LINREC"):
                high_births[law].append({
                    "census_file_index": index,
                    "reading": births,
                    "rounds": record["rounds_done"],
                    "knots": record["knots"],
                    "segment_start": birth_verdict[1],
                    "stop": record["stop"],
                    "values_first_five": birth_list[:5],
                    "values_last_five": birth_list[-5:],
                })
            for floor in (Fraction(11, 10), Fraction(3, 2)):
                revised, _ = read_sequence(birth_list, 1, ended, floor)
                actual = stored_signature(record["births_reading_swaps"][f"ratio_{float(floor)}"])
                if comparable(revised) != actual:
                    problems[f"births floor {floor}"].append(key)
                if category(revised) != births:
                    changes_from_swaps[str(floor)][f"{law} births {births} to {category(revised)}"] += 1
            if index in admissible:
                parity[key] = "ENDED" if record["parity_closing_round"] is not None else births
                if record["parity_closing_round"] is not None:
                    counts["recorded parity closings on eligible starts"] += 1
            if law == "L6":
                if record["rounds_done"] == 100:
                    stable = p4_reading(record)
                    p4["reached_round_100"].append(stable)
                    if index in admissible and (
                        record["parity_closing_round"] is None or record["parity_closing_round"] == 100
                    ):
                        p4_parity_eligible.append(stable if record["parity_closing_round"] is None else None)
                else:
                    largest = [max(sizes, default=0) for sizes in record["part_sizes_per_round"]]
                    p4["before_round_100"].append({
                        "census_file_index": index,
                        "rounds_done": record["rounds_done"],
                        "stop": record["stop"],
                        "ended": record["ended"],
                        "largest_part_gains_over_rounds_36_to_40": difference(largest[36:41]),
                    })
            all_counts = []
            for label in ("a", "b", "c"):
                for knot in record["classes"][label]:
                    name = str(knot)
                    raw = tuple(record["H"][name])
                    assert len(raw) - 1 == record["ell"][name]
                    all_counts.append(raw)
                    verdict, previous = read_sequence(raw, 0, ended, earlier=True)
                    category_h = category(verdict)
                    history[f"{law}:{label}"][category_h] += 1
                    actual = stored_signature(record["reading"][name])
                    if comparable(verdict) != actual:
                        problems["H verdict or segment"].append((key, knot, str(verdict), str(actual)))
                    elif not parameters_match(verdict, record["reading"][name], raw, 0):
                        problems["H reading parameters"].append((key, knot))
                    if not ended:
                        recorded_previous = [
                            (stored_signature(x), x["segment"][1]) for x in record["reading"][name].get("earlier", ())
                        ]
                        if [(comparable(v), end) for v, end in previous] != recorded_previous:
                            problems["earlier H segments"].append((key, knot))
                    swaps = record["reading_swaps"][name]
                    for floor in (Fraction(11, 10), Fraction(3, 2)):
                        changed, _ = read_sequence(raw, 0, ended, floor)
                        after = category(changed)
                        given = swaps[f"ratio_{float(floor)}"]
                        report_category = given.split()[0]
                        if given.startswith("LINREC"):
                            report_category = "LINREC"
                        if ("LINREC" if after.startswith("LINREC") else after) != report_category:
                            problems[f"H floor {floor}"].append((key, knot, after, given))
                        if after != category_h:
                            changes_from_swaps[str(floor)][f"{law} H {category_h} to {after}"] += 1
                    if doubling(raw) != swaps["doubling"]:
                        problems["H doubling swap"].append((key, knot))
            screen_label, a, z = screen(all_counts)
            screens[law][screen_label] += 1
            want = record["screen"]
            got = (screen_label, a, z)
            if want["holds"]:
                desired = (f"holds j={want['j']}", *want["range"])
            elif want["zmax"] < 32:
                desired = ("undecided (range)", None, None)
            else:
                desired = ("no j", None, None)
            if got != desired:
                problems["screen verdict or range"].append((key, got, desired))
            if screen_label == "holds j=1" and births != "POWER(0)":
                screens_nonconstant[law][births] += 1
            counts["nonempty authored E failures"] += bool(record["check_E"])
            counts["authored parent steps differ"] += bool(record["parent_steps_differ"])
            counts["H readings across classes"] += len(all_counts)
            counts["distinct H sequences keyed by run and knot"] += len(record["H"])
            counts["runs with overlap of classes b and c"] += bool(
                set(record["classes"]["b"]).intersection(record["classes"]["c"])
            )
            classifications_by_round_limit[law][f"{births}, {record['stop'] or 'round 100'}"] += 1
    if limit is None:
        assert set(expected) == pairs_seen
    p4_complete = p4["reached_round_100"]
    p4_results = {
        "reached_round_100": len(p4_complete),
        "counts": dict(Counter(flag for row in p4_complete for flag, passed in row.items() if flag != "gains" and passed)),
        "gain_pairs": {str(gains): n for gains, n in Counter(row["gains"] for row in p4_complete).items()},
        "before_round_100": p4["before_round_100"],
        "parity_with_unchanged_trajectory_at_round_100": sum(row is not None for row in p4_parity_eligible),
        "parity_closings_in_round_100": sum(row is None for row in p4_parity_eligible),
    }
    cross = {}
    for before, after in [("L0", law) for law in ("L6", "L7", "L1", "L9", "L10", "L11")] + [
        ("L9", law) for law in ("L6", "L10", "L11")
    ]:
        cross[f"{before} to {after}"] = dict(sorted(Counter(
            f"{classifications[i, before]} to {classifications[i, after]}"
            for i in replay_ids if (i, before) in classifications and (i, after) in classifications
        ).items()))
    tables = weighted_tables(
        classifications, starts, weights, {"nae": all_ids, "parity": admissible}, scratch, 250, limit is None
    )
    parity_tables = weighted_tables(
        parity, starts, weights, {"nae": set(), "parity": admissible}, scratch, 250, limit is None
    )
    tables.update({key: value for key, value in parity_tables.items() if value})
    return {
        "processed_run1": replay_rows,
        "counts": counts,
        "five_knot_sample": {
            "prefix": 250,
            "registered_size_before_cut": 1000,
            "population": len(large_ids),
            "overlap_with_disclosed_64": len(scratch & replay_ids),
            "eligible_parity_large_starts_population": len(admissible & set(large_ids)),
            "eligible_parity_large_starts_prefix": len(admissible & set(large_ids[:250])),
            "parity_failures_small_and_large": [len(set(group) - admissible) for group in (small_ids, large_ids)],
        },
        "births": tables,
        "status_by_law": record_statuses,
        "births_by_law_and_round_limit": classifications_by_round_limit,
        "birth_recurrence_coefficients": birth_recurrences,
        "degree_2_no_cap_counted_starts": sorted(i for (i, law), tag in classifications.items() if law == "L9" and tag == "POWER(2)"),
        "above_linear_on_caps": high_births,
        "p4": p4_results,
        "cross_start_table": cross,
        "screen": screens,
        "nonconstant_births_at_screen_power_1": screens_nonconstant,
        "history_verdicts_by_law_and_class": history,
        "ratio_threshold_swaps": changes_from_swaps,
        "different_from_author_or_ledger_problem": {
            key: {"count": len(samples), "runs_affected": len({entry[0] for entry in samples})
                  if key.startswith("truncated") else None,
                  "by_law": dict(Counter(entry[0][1] for entry in samples)) if key.startswith("truncated") else None,
                  "first_examples": samples[:12]}
            for key, samples in sorted(problems.items()) if samples
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(replay(args.limit), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
