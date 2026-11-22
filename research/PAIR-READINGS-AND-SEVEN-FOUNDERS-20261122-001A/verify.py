"""Recompute the B275 exclusion certificate from the sealed pair table."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = "NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A"
FAMILY = PRIOR + "-E001_newest_knots"
ARTIFACT = ROOT / "artifacts" / PRIOR / FAMILY
sys.path.insert(0, str(ROOT / "experiments" / PRIOR / FAMILY))
from newest_families import read_table, screen


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_array(n, rates):
    moments = [[Fraction(1) for _ in range(n)] for _ in range(n)]
    for (x, y), p in zip(combinations(range(n), 2), rates, strict=True):
        moments[x][y] = moments[y][x] = 1 - 2 * p
    return moments


def previous_families(n, rates):
    branches = screen(n, rates, "uniform")
    expected = json.loads((ARTIFACT / "branches_uniform.json").read_text())
    assert json.loads(json.dumps(branches)) == expected
    choices = branches["branches"]
    costs = Counter()
    winners = []
    for case in choices:
        costs.update(case.get("older_costs", {}))
        survivors = case.get("surviving_assignments", [])
        if survivors:
            roster = survivors[0]["roster"]
            assert all(r["roster"] == roster for r in survivors)
            winners.append(dict(indices=case["selected"], assignments=len(survivors), roster=roster))
    assert sorted((len(w["indices"]), len(w["roster"])) for w in winners) == [(1, 2), (6, 7)]
    return dict(candidate_holdings=branches["options"], disjoint_families=len(choices),
                old_assignments=sum(case["complete_old_assignments"] for case in choices),
                costs=dict(costs), surviving_families=winners)


def fixed_probability(indices, signs, moment):
    """One signed two- or three-name pattern under complement symmetry."""
    return (1 + sum(signs[i] * signs[j] * moment(indices[i], indices[j])
                    for i, j in combinations(range(len(indices)), 2))) / 2**len(indices)


def constant_probability(indices, moment):
    return 2 * fixed_probability(indices, (1,) * len(indices), moment)


def minimum_row(point, population, moment):
    row = {z: moment(point, z) for z in population if z != point}
    lowest = min(row.values())
    return lowest, tuple(k for k, v in row.items() if v == lowest)


def proper_bounds(names, moment, scale, threshold):
    lows = {}
    for width in range(2, len(names)):
        probabilities = [constant_probability(group, moment) / scale for group in combinations(names, width)]
        assert min(probabilities) > threshold
        lows[width] = str(min(probabilities))
    return lows


def incidence_data(moments):
    old = tuple(range(29))
    residual = tuple(z for z in old if z != 8)
    moment = lambda x, y: moments[x][y]
    min8, pins = minimum_row(8, old, moment)
    q = -min8
    assert pins == (3, 5, 6, 7)
    old_bounds = proper_bounds(pins, moment, 1, q)
    corrected = {}
    corrected_rows = []
    for a in pins:
        for z in residual:
            if z != a:
                key = tuple(sorted((a, z)))
                value = (moment(a, z) - moment(8, z)) / (1 + q)
                if key in corrected:
                    assert corrected[key] == value
                corrected[key] = value
    new_moment = lambda x, y: corrected[tuple(sorted((x, y)))]
    for a in pins:
        lowest, companions = minimum_row(a, residual, new_moment)
        bounds = proper_bounds(companions, moment, 1 + q, -lowest)
        corrected_rows.append(dict(name=a, minimum=str(lowest), companions=companions,
                                   proper_constant_mass_lower_bounds=bounds))
    forced = [sorted((*pins, 8))] + [sorted((row["name"], *row["companions"])) for row in corrected_rows]
    assert forced == [[3, 5, 6, 7, 8], [1, 2, 3, 14, 15], [5, 13, 23, 24, 25],
                      [6, 16, 26, 27, 28], [0, 4, 7, 10]]
    denominator = 1
    constant_triples = {}
    for group in combinations(old, 3):
        constant_triples[group] = constant_probability(group, moment)
        for signs in product((-1, 1), repeat=2):
            # The globally opposite signed pattern has the same probability.
            denominator = lcm(denominator, fixed_probability(group, (1, *signs), moment).denominator)
    minimum_constant = min(constant_triples.values())
    assert minimum_constant > 0
    # Four separated wings have only their H companion set; nine names lie outside.
    bound = (2**len(forced[0]) - 2)
    for support in forced[1:]:
        bound *= 2**(len(support) - 1) - 1
    bound *= 2**(len(old) - len(set().union(*map(set, forced))))
    assert 0 < denominator <= bound < 2 * denominator
    residual_count = denominator * (1 + q) / 2
    assert residual_count.denominator == 1
    signed_counts = Counter()
    least_count = {}
    for width in (2, 3):
        for group in combinations(residual, width):
            if not all(pair in corrected for pair in combinations(group, 2)):
                continue
            for signs in product((-1, 1), repeat=width):
                count = residual_count * fixed_probability(group, signs, new_moment)
                assert count.denominator == 1 and count >= 0
                signed_counts[width] += 1
                least_count[width] = min(least_count.get(width, int(count)), int(count))
    return dict(old_names=29, q=str(q), original_minimizers=pins,
                old_proper_constant_mass_lower_bounds=old_bounds, corrected_rows=corrected_rows,
                five_forced_holdings=forced, individually_fixed_correlations=len(corrected),
                corrected_correlations={f"{x},{z}": str(c) for (x, z), c in sorted(corrected.items())},
                signed_count_checks=dict(signed_counts), minimum_corrected_pattern_count=least_count,
                denominator_lcm=denominator, forced_only_upper_bound=bound, word_count=denominator,
                erased_word_count=int(residual_count), positive_triple_count=len(constant_triples),
                smallest_constant_probability=str(minimum_constant),
                smallest_constant_triples=[names for names, value in constant_triples.items()
                                           if value == minimum_constant])


def coincidence_data(moments):
    old = tuple(range(29))
    eq = {(x, y) for x, y in combinations(old, 2)
          if all(moments[x][z] == moments[y][z] for z in old if z != x and z != y)}
    classes = []
    for x in old:
        members = [y for y in old if y == x or tuple(sorted((x, y))) in eq]
        if x == members[0] and len(members) > 1:
            classes.append(members)
            assert all((a, b) in eq for a, b in combinations(members, 2))
    assert classes == [[1, 2], [17, 18], [19, 20], [21, 22], [23, 24, 25], [26, 27, 28]]
    t = (23, 24, 25)
    companions = (5, 13)
    pair = moments[23][24]
    assert all(moments[x][y] == pair for x in t for y in (*companions, *t) if x != y)
    balances = [14 * moments[x][z] + moments[5][z] + moments[13][z]
                for x in t for z in old if z not in t]
    assert balances == [0] * 78
    return dict(exterior_row_classes=classes, indistinguishable_pairs=len(eq),
                max_class=max(map(len, classes)), target_triple=t, named_companions=companions,
                common_signed_moment=str(pair), zero_balance_identities=len(balances))


def run():
    path = ARTIFACT / "target_uniform.json"
    n, rates = read_table(path)
    assert n == 31 and len(rates) == 465
    moments = signed_array(n, rates)
    for y in (29, 30):
        assert all(moments[y][z] == -moments[8][z] / 3 for z in range(29))
    assert moments[29][30] == Fraction(-1, 3)
    return dict(input=str(path.relative_to(ROOT)), input_sha256=digest(path),
                archived_uniform_screen_sha256=digest(ARTIFACT / "branches_uniform.json"),
                comparisons=dict(whole_table=465, old_pairs=406, input_fresh_and_outside_fresh=58,
                                 fresh_fresh=1), screening=previous_families(n, rates),
                erasure_and_cardinality=incidence_data(moments), forced_overlap=coincidence_data(moments))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare regenerated and saved results")
    args = parser.parse_args()
    out = HERE / "results.json"
    serialized = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if serialized != out.read_text():
            raise SystemExit("stored certificate differs")
    else:
        out.write_text(serialized)
    print(f"Verified 465 named pairs, the two preceding families and the sole-loose contradiction. {digest(out)}")
