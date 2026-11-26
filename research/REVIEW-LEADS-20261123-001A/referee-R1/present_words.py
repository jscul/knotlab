"""Exact replay of a two-shared-distinction reference and its 18-knot realization."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import lcm
from pathlib import Path
import resource

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, eye, hstack, vstack


LEFT = ("x1", "x2", "x3")
RIGHT = ("y1", "y2", "y3")
SHARED = ("s1", "s2")
SETTINGS = tuple(product(range(2), repeat=2))
OLD_RECORDS = tuple(product(range(2), repeat=3))
SIGNS = np.array([signs for signs in product((1, -1), repeat=4) if np.prod(signs) == -1])
PARITY = np.array([[(-1) ** (mask & record).bit_count() for record in range(16)]
                   for mask in range(16)])

# The named fixture from the post hoc record. E and O require even and odd parity.
ALICE = "E x1 a b; E c1 a b; E k1 a b; E x2 d e; O x3 d e; E c2 d e; O c3 d e; N c1 c2 n2; N k1 c3 n1; E n2 g h; O s2 g h; E n1 u v; O s1 u v"
BOB = "E y1 p q; E s1 p q; E y2 r t; E s2 r t; O y3 r t"


def knots(specification):
    return tuple((law, tuple(names)) for law, *names in (line.split() for line in specification.split(";")))


def allowed(law, values):
    ones = sum(values)
    return {"E": ones % 2 == 0, "O": ones % 2 == 1, "N": 0 < ones < len(values)}[law]


def truth_table(laws, left_record, right_record, fixed=None):
    """Assign each distinction once, rejecting a rule as soon as its last value is set."""
    counts = Counter(name for _, names in laws for name in names)
    ordering = []
    while len(ordering) < len(counts):
        unassigned = counts.keys() - set(ordering)

        def precedence(name):
            nearby = sum(8 // len(set(names) & unassigned) for _, names in laws if name in names)
            return (nearby, counts[name], name)

        ordering.append(max(unassigned, key=precedence))
    positions = {name: index for index, name in enumerate(ordering)}
    scheduled = [[] for name in ordering]
    for law, names in laws:
        places = tuple(positions[name] for name in names)
        scheduled[max(places)].append((law, places))
    word = [0] * len(ordering)
    table = np.zeros((2 ** len(left_record), 2 ** len(right_record)), dtype=np.int64)
    left = tuple(positions[name] for name in left_record)
    right = tuple(positions[name] for name in right_record)
    choices = tuple((fixed[name],) if fixed and name in fixed else (0, 1) for name in ordering)

    def visit(index):
        if index == len(ordering):
            table[pack(word[place] for place in left), pack(word[place] for place in right)] += 1
            return
        for value in choices[index]:
            word[index] = value
            if all(allowed(law, [word[place] for place in places]) for law, places in scheduled[index]):
                visit(index + 1)

    visit(0)
    return table


def pack(values):
    result = 0
    for value in values:
        result = 2 * result + value
    return result


def reference():
    left = np.zeros((8, 4), dtype=np.int64)
    right = np.zeros((8, 4), dtype=np.int64)
    for row, (u, v, w) in enumerate(OLD_RECORDS):
        for index, (s1, s2) in enumerate(SETTINGS):
            left[row, index] = v != w and (s2 == v if u != w else s1 == u)
            right[row, index] = v != w and (s1, s2) == (u, v)
    old = left @ right.T
    for (x1, x2, x3), (y1, y2, y3) in product(OLD_RECORDS, repeat=2):
        expected = x2 != x3 and y2 != y3 and x1 ^ y1 == ((x1 ^ x3) & (y1 ^ y2))
        assert old[pack((x1, x2, x3)), pack((y1, y2, y3))] == expected
    return left, right, old


def completions(old, setting, number=1):
    inputs = old[0], old[setting + 1]
    return tuple(fresh for fresh in product(range(2), repeat=number)
                 if all(allowed("N", (*inputs, value)) for value in fresh))


def finish(old, number=1, control=False):
    tables = {}
    for a, b in SETTINGS:
        size = 2 ** (3 + number)
        table = np.zeros((size, size), dtype=np.int64)
        for x, y in product(OLD_RECORDS, repeat=2):
            x_completions = completions(x, a, number)
            y_completions = completions(y, b, number)
            weight = int(old[pack(x), pack(y)])
            if control:
                # A common integer denominator gives every old word equal total weight.
                weight *= 4 ** number // (len(x_completions) * len(y_completions))
            for za, zb in product(x_completions, y_completions):
                table[pack((*x, *za)), pack((*y, *zb))] += weight
        tables[a, b] = table
    return tables


def total_variation(first, second):
    p = [Fraction(int(value), int(first.sum())) for value in first]
    q = [Fraction(int(value), int(second.sum())) for value in second]
    return sum(abs(x - y) for x, y in zip(p, q)) / 2


def marginal(tables, observer, own, far):
    if observer == 0:
        return tables[own, far].sum(axis=1)
    return tables[far, own].sum(axis=0)


def hiding(tables):
    return [[str(total_variation(marginal(tables, observer, setting, 0),
                                 marginal(tables, observer, setting, 1))) for setting in range(2)]
            for observer in range(2)]


def integer_correlations(tables, responses):
    common_denominator = lcm(*(int(table.sum()) for table in tables.values()))
    numerators = [(responses @ table @ responses.T) * (common_denominator // int(table.sum()))
                  for table in tables.values()]
    return common_denominator, numerators


def best_parity(tables, responses=PARITY):
    denominator, scores = integer_correlations(tables, responses)
    e00, e01, e10, e11 = scores
    e00 = e00[:, None, :, None]
    e01 = e01[:, None, None, :]
    e10 = e10[None, :, :, None]
    e11 = e11[None, :, None, :]
    best = -1
    for signs in SIGNS:
        signed = signs[0] * e00 + signs[1] * e01 + signs[2] * e10 + signs[3] * e11
        value = int(signed.max())
        if value > best:
            best = value
            witness = tuple(map(int, np.unravel_index(signed.argmax(), signed.shape)))
            best_signs = signs.tolist()
    x0, x1, y0, y1 = witness
    selected = (scores[0][x0, y0], scores[1][x0, y1], scores[2][x1, y0], scores[3][x1, y1])
    return {"score": str(Fraction(best, denominator)), "masks": witness, "signs": best_signs,
            "correlations": [str(Fraction(int(num), denominator)) for num in selected]}


def supports(tables):
    return [[np.flatnonzero(marginal(tables, observer, setting, 0)) for setting in range(2)]
            for observer in range(2)]


def best_boolean(tables):
    """Exhaust both Bob response functions; Alice's optimal signs are termwise."""
    left, right = supports(tables)
    denominator = lcm(*(int(table.sum()) for table in tables.values()))
    counts = {key: table[np.ix_(left[key[0]], right[key[1]])] * (denominator // int(table.sum()))
              for key, table in tables.items()}
    bob0, bob1 = (np.array(tuple(product((1, -1), repeat=len(records)))) for records in right)
    contributions = []
    for a in range(2):
        from_bob0 = bob0 @ counts[a, 0].T
        from_bob1 = bob1 @ counts[a, 1].T
        contributions.append(from_bob0[:, None] + (-1) ** a * from_bob1[None, :])
    scores = sum(abs(column).sum(axis=2) for column in contributions)
    return {"score": str(Fraction(int(scores.max()), denominator)), "bob_function_pairs": int(scores.size),
            "record_support_sizes": [[len(records) for records in side] for side in (left, right)]}


def local_lp(tables, normalized):
    """Reconstruct exact feasible primal and dual certificates for the L1 objective."""
    left, right = supports(tables)
    rows = [(a, b, x, y) for a, b in SETTINGS for x, y in product(left[a], right[b])]
    index = {row: position for position, row in enumerate(rows)}
    strategies = list(product(*left, *right))
    strategy_rows = [[index[a, b, strategy[a], strategy[2 + b]] for a, b in SETTINGS]
                     for strategy in strategies]
    indices = np.array(strategy_rows)
    incidence = coo_matrix((np.ones(indices.size), (indices.ravel(), np.repeat(np.arange(len(strategies)), 4))),
                           shape=(len(rows), len(strategies))).tocsc()
    identity = eye(len(rows), format="csc")
    matrix = hstack((incidence, identity, -identity), format="csc")
    target = [Fraction(int(tables[a, b][x, y]), int(tables[a, b].sum())) for a, b, x, y in rows]
    objective = [0] * len(strategies) + [1] * (2 * len(rows))
    if normalized:
        matrix = vstack((matrix, [1] * len(strategies) + [0] * (2 * len(rows))), format="csc")
        target.append(Fraction(1))
    solution = linprog(objective, A_eq=matrix, b_eq=list(map(float, target)), method="highs",
                       options={"threads": 1})
    assert solution.success
    primal = [Fraction(float(value)).limit_denominator(100_000) for value in solution.x]
    dual = [Fraction(float(value)).limit_denominator(100_000) for value in solution.eqlin.marginals]
    assert all(value >= 0 for value in primal)
    obtained = [Fraction(0) for _ in target]
    for column, (coefficient, value) in enumerate(zip(objective, primal)):
        entries = slice(matrix.indptr[column], matrix.indptr[column + 1])
        indices, values = matrix.indices[entries], matrix.data[entries]
        assert sum(int(entry) * dual[row] for row, entry in zip(indices, values)) <= coefficient
        for row, entry in zip(indices, values):
            obtained[row] += int(entry) * value
    assert obtained == target
    optimum = sum(coefficient * value for coefficient, value in zip(objective, primal))
    assert optimum == sum(a * b for a, b in zip(target, dual))
    return {"l1": str(optimum), "strategy_count": len(strategies),
            "strategy_mass": str(sum(primal[:len(strategies)])),
            "primal_nonzero": [[index, str(value)] for index, value in enumerate(primal) if value],
            "dual_nonzero": [[index, str(value)] for index, value in enumerate(dual) if value]}


def keyed(old, tables):
    result = {}
    for observer in range(2):
        for own_setting in range(2):
            keyings = []
            fixed = marginal(tables, observer, own_setting, 0)
            for mask in range(256):
                weights = np.zeros(16, dtype=np.int64)
                for x, y in product(OLD_RECORDS, repeat=2):
                    own, far = (x, y) if observer == 0 else (y, x)
                    far_setting = (mask >> pack(far)) & 1
                    count = int(old[pack(x), pack(y)]) * len(completions(far, far_setting))
                    for fresh in completions(own, own_setting):
                        weights[pack((*own, *fresh))] += count
                keyings.append(weights)
            by_tuple = {tuple(weights): mask for mask, weights in reversed(list(enumerate(keyings)))}
            change, against_fixed = max((total_variation(weights, fixed), mask)
                                        for mask, weights in enumerate(keyings))
            contrast, key1, key2 = max((total_variation(np.array(first), np.array(second)), mask1, mask2)
                                       for (first, mask1), (second, mask2) in combinations(by_tuple.items(), 2))
            first_value_mask = sum((value[0] << pack(value)) for value in OLD_RECORDS)
            result[f"observer_{observer}_setting_{own_setting}"] = {
                "policies": len(keyings), "distinct_marginals": len(by_tuple),
                "max_change_from_fixed": str(change), "maximizing_mask": against_fixed,
                "max_change_between_keys": str(contrast), "maximizing_mask_pair": [key1, key2],
                "first_value_change_from_fixed": str(total_variation(keyings[first_value_mask], fixed)),
                "first_value_policy_counts": keyings[first_value_mask].tolist()}
    return result


def births(a, b, number):
    left_new = tuple(f"za{j}" for j in range(number))
    right_new = tuple(f"zb{j}" for j in range(number))
    new_knots = []
    for triple, setting, fresh_names in ((LEFT, a, left_new), (RIGHT, b, right_new)):
        for index, fresh in enumerate(fresh_names):
            inputs = (triple[0], triple[setting + 1])
            if index:
                inputs = tuple(f"{name}_copy{index}" for name in inputs)
            new_knots.append(("N", (*inputs, fresh)))
    return tuple(new_knots), (*LEFT, *left_new), (*RIGHT, *right_new)


def copies(source, left, right, number):
    """Each added parity rule gives its own copy the value of the original."""
    projection_rules = [(law, names) for law, names in source if names[0] in (*left, *right)]
    assert len(projection_rules) == 6
    return tuple((law, (f"{names[0]}_copy{index}", *names[1:]))
                 for index in range(1, number) for law, names in projection_rules)


def law_counts():
    verdicts = {}
    for law in "EON":
        words = [word for word in OLD_RECORDS if allowed(law, word)]
        projections = [len({word[:position] + word[position + 1:] for word in words}) for position in range(3)]
        assert 0 < len(words) < 8 and projections == [4, 4, 4]
        verdicts[law] = {"words": ["".join(map(str, word)) for word in words],
                         "erasure_projection_sizes": projections}
    return verdicts


def write_output(path, data):
    data["resources"] = {"cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime
                           + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                         "peak_memory_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    left, right, old = reference()
    tables = finish(old)
    left_knots, right_knots = knots(ALICE), knots(BOB)
    specimen = left_knots + right_knots
    fixed = {"x1": 0} if args.pilot else None
    left_actual = truth_table(left_knots, LEFT, SHARED, fixed)
    right_actual = truth_table(right_knots, RIGHT, SHARED)
    specimen_old = truth_table(specimen, LEFT, RIGHT, fixed)
    assert np.array_equal(specimen_old, left_actual @ right_actual.T)
    direct = {}
    old_from_completions = finish(specimen_old)
    for a, b in SETTINGS:
        new_knots, left_record, right_record = births(a, b, 1)
        direct[a, b] = truth_table(specimen + new_knots, left_record, right_record, fixed)
        assert np.array_equal(direct[a, b], old_from_completions[a, b])
    raw_lp = local_lp(tables, False)
    normalized_lp = local_lp(tables, True)
    result = {"pilot": args.pilot, "specimen_prefix": fixed,
              "record_encoding": "Binary, listed distinctions from most to least significant; settings 00, 01, 10, 11.",
              "reference": {"left": left.tolist(), "right": right.tolist(), "old": old.tolist(),
                            "old_words": int(old.sum()),
                            "finished_words": [int(table.sum()) for table in tables.values()],
                            "hiding_total_variation": hiding(tables), "best_parity_including_constant": best_parity(tables),
                            "best_parity_nonempty": best_parity(tables, PARITY[1:]),
                            "best_boolean": best_boolean(tables), "control": best_parity(finish(old, control=True)),
                            "local_lp_free_mass": raw_lp, "local_lp_normalized": normalized_lp},
              "specimen": {"left": left_actual.tolist(), "right": right_actual.tolist(), "old": specimen_old.tolist(),
                           "knots_by_observer": [len(left_knots), len(right_knots)],
                           "holders": dict(sorted(Counter(name for _, names in specimen for name in names).items())),
                           "old_words": int(specimen_old.sum()), "finished_words": [int(table.sum()) for table in direct.values()],
                           "isolated_laws": law_counts()}}
    result["reference"]["best_parity_nonempty"]["masks"] = [mask + 1 for mask in result["reference"]["best_parity_nonempty"]["masks"]]
    if not args.pilot:
        assert np.array_equal(left_actual, 16 * left)
        assert np.array_equal(right_actual, 4 * right)
        for setting, table in direct.items():
            assert np.array_equal(table, 64 * tables[setting])
        result["reference"]["joint_record_counts"] = [table.tolist() for table in tables.values()]
        result["reference"]["keyed_setting"] = keyed(old, tables)
        result["specimen"]["joint_record_counts_scale_from_reference"] = 64
        result["specimen"]["hiding_total_variation"] = hiding(direct)
        result["specimen"]["best_parity"] = best_parity(direct)
    for number in (1, 2, 3):
        more = finish(old, number)
        responses = np.array([[(-1) ** (mask & record).bit_count() for record in range(2 ** (3 + number))]
                              for mask in range(2 ** (3 + number))])
        score = best_parity(more, responses)
        ratio = 2 ** number
        assert Fraction(score["score"]) == 4 - Fraction(8 * ratio, (1 + ratio) ** 2)
        extended = specimen + copies(specimen, LEFT, RIGHT, number)
        specimen_more = {}
        for a, b in SETTINGS:
            new_knots, left_record, right_record = births(a, b, number)
            specimen_more[a, b] = truth_table(extended + new_knots, left_record, right_record, fixed)
            if not args.pilot:
                assert np.array_equal(specimen_more[a, b], 64 * more[a, b])
        old_holders = Counter(name for _, names in extended for name in names)
        result.setdefault("repeat_births_on_loose_copies", []).append({
            "births_per_setting": number, "weight_ratio": ratio, "score": score,
            "hiding_total_variation_all_fresh_values_retained": hiding(more),
            "above_2sqrt2": Fraction(score["score"]) ** 2 > 8,
            "specimen_finished_words": [int(table.sum()) for table in specimen_more.values()],
            "specimen_extra_holders": sum(count - 2 for count in old_holders.values() if count > 2),
            "specimen_holders_above_two": dict(sorted((name, count) for name, count in old_holders.items()
                                                       if count > 2))})
    write_output(args.out, result)


if __name__ == "__main__":
    main()
