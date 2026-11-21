"""Independently invert the two named 29-place pair tables."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb, isqrt
from pathlib import Path
import gzip
import json


ROOT = Path(__file__).resolve().parents[3]
TICKET = "LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A"
OUTPUT = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_loose_roles"


def correlation_table(reading):
    rates = json.loads((OUTPUT / f"{reading}_rates.json").read_text())
    width = (1 + isqrt(1 + 8 * len(rates))) // 2
    assert comb(width, 2) == len(rates)
    rows = [[Fraction(1) for _ in range(width)] for _ in range(width)]
    for (x, y), rate in zip(combinations(range(width), 2), rates, strict=True):
        rows[x][y] = rows[y][x] = 1 - 2 * Fraction(rate)
    return rows


def twin(rows, x, y):
    return all(rows[x][z] == rows[y][z] for z in range(len(rows)) if z not in (x, y))


def ordinary_groups(holders, witnesses):
    witnessed_pairs = {frozenset(pair) for w in witnesses for pair in combinations(w, 2)}
    unheld = []
    for size in range(3, len(holders) + 1):
        for group in combinations(holders, size):
            group = frozenset(group)
            if all(frozenset(pair) in witnessed_pairs for pair in combinations(group, 2)):
                if not any(group <= w for w in witnesses):
                    unheld.append(group)
    maximal = [g for g in unheld if not any(g < other for other in unheld)]
    return maximal + [pair for pair in witnessed_pairs if not any(pair <= g for g in maximal)]


def forced_roster(options):
    parents = range(len(options))
    # The demand-four argument forces a common witness for all five.
    births = sorted(tuple(sorted(pair)) for pair in ordinary_groups(parents, [set(parents)]))
    assert len(births) == comb(5, 2) and all(len(pair) == 2 for pair in births)
    birth_witnesses = [{j for j, pair in enumerate(births) if i in pair} for i in parents]
    next_groups = ordinary_groups(range(len(births)), birth_witnesses)
    demands = Counter(j for group in next_groups for j in group)
    assert len(next_groups) == comb(5, 3) and all(len(group) == 3 for group in next_groups)
    assert all(demands[j] == 3 for j in range(len(births)))
    return [[[list(options[i][0]) for i in pair], max(3 - len(pair), 1, demands[j])]
            for j, pair in enumerate(births)]


def classify(reading):
    rows = correlation_table(reading)
    names = set(range(len(rows)))
    verdicts = []
    options = set()
    for f in sorted(names):
        m = min(rows[f])
        support = {f} | {z for z in names if rows[f][z] == m}
        fresh = {z for z in support if twin(rows, f, z)}
        inputs = support - fresh
        p, q = len(inputs), len(fresh)
        entry = {"marked": f, "support": sorted(support), "fresh": sorted(fresh), "inputs": sorted(inputs)}
        if len(support) < 3 or not inputs:
            entry["reject"] = "arity or no parent"
        elif p <= 2:
            residual = {
                z: rows[f][z] + sum(rows[u][z] for u in inputs) / (p * (2 ** q - 1))
                for z in sorted(names - fresh)
            }
            wrong = next((z for z, value in residual.items() if value), None)
            if wrong is not None:
                entry.update(reject="one/two-input conditional mean", witness=wrong,
                             residual=str(residual[wrong]))
        if "reject" not in entry:
            witnesses = [(u, v) for u, v in combinations(sorted(inputs), 2) if twin(rows, u, v)]
            if witnesses:
                u, v = witnesses[0]
                entry.update(reject="two old inputs cannot be twins", witness=[u, v],
                             mutual_correlation=str(rows[u][v]), loose_correlation=str(rows[f][u]))
                if reading == "inherited":
                    assert rows[u][v] < 0
                    eligible = [z for z in names - support if rows[u][z] <= min(rows[u][i] for i in inputs - {u})]
                    entry["possible_exterior_old_companions"] = sorted(eligible)
                    assert len(eligible) < 2
                else:
                    assert rows[u][v] <= rows[f][u]
                    possible = []
                    for u in sorted(inputs):
                        differences = {z: rows[u][z] - rows[f][z] for z in names - {u, f}}
                        lower = min(differences.values())
                        possible.append(sorted(z for z in names - support if differences[z] == lower))
                    entry["possible_exterior_old_companions_per_input"] = possible
                    assert possible == [[6, 7]] * 4
            else:
                options.add((tuple(sorted(support)), tuple(sorted(fresh))))
        verdicts.append(entry)
    options = sorted(options)
    assert len(options) == 5 and all(len(f) == 4 and 1 <= len(h) - len(f) <= 2 for h, f in options)
    assert all(not (set(a) & set(b)) for (a, _), (b, _) in combinations(options, 2))
    return {
        "individual_indices": verdicts,
        "exclusion_histogram": dict(Counter(item.get("reject", "admissible mark") for item in verdicts)),
        "possible_latest_supports_and_private_groups": options,
        "actual_loose_names": sorted(z for _, fresh in options for z in fresh),
        "complete_parent_supports_and_fresh": forced_roster(options),
    }


def old_companion_control():
    """Test the forcing lemma on all connected archived cases through ten."""
    small = "READS-HOLDERS-SOURCES-20261120-001B"
    ten = "THREE-READERS-AND-GROWTH-20261120-001B"
    with gzip.open(ROOT / "artifacts" / small / f"{small}-E001_irredundant" / "census_cases.json.gz", "rt") as stream:
        cases = json.load(stream)
    with gzip.open(ROOT / "artifacts" / ten / f"{ten}-E001_state_recovery" / "census_cases.json.gz", "rt") as stream:
        cases["10"] = json.load(stream)
    by_width = {}
    for name_count, data in cases.items():
        n = int(name_count)
        zero = [sum(1 << w for w in range(1 << n) if not w >> i & 1) for i in range(n)]
        totals = Counter()
        for case in data["nae"]:
            words = int(case["state_words_hex"], 16)
            for item in case["presentations"]:
                holders = list(map(set, item["supports"]))
                incidence = Counter(x for h in holders for x in h)
                checks = []
                for h in holders:
                    for u in h:
                        if incidence[u] != 1:
                            continue
                        a = h - {u}
                        event = words
                        for z in a:
                            event &= zero[z]
                        checks.append((h, a, event))
                totals["presentations"] += 1
                for (h, a, ea), (k, b, eb) in combinations(checks, 2):
                    if h == k:
                        continue
                    totals["different_loose_holders"] += 1
                    if ea & ~eb == 0:
                        assert len(a-b) >= 4 * len(b-a)
                        totals["first_forces_second_same_colour"] += 1
                    if eb & ~ea == 0:
                        assert len(b-a) >= 4 * len(a-b)
                        totals["second_forces_first_same_colour"] += 1
                    if ea == eb:
                        assert a == b and len(holders) == 2
                        totals["equal_events"] += 1
        by_width[n] = dict(totals)
    return by_width


def repeated_old_control():
    support = [(0, 2, 3), (1, 2, 3)]
    words = [w for w in product((-1, 1), repeat=4) if all(len({w[i] for i in h}) == 2 for h in support)]
    c01 = Fraction(sum(w[0] * w[1] for w in words), len(words))
    c02 = Fraction(sum(w[0] * w[2] for w in words), len(words))
    assert (len(words), c01, c02) == (10, Fraction(1, 5), Fraction(-1, 5))
    return {"holders": support, "state_count": len(words), "distinct_private_twin_correlation": str(c01),
            "minimum_correlation_to_companion": str(c02), "third_witnesses": 0}


def tight_one_way_control():
    holders = [(0, 1, 2, 3, 4, 5), (6, 1, 7), (2, 3, 8), (4, 5, 9), (8, 9, 7)]
    a = set(holders[0]) - {0}
    b = set(holders[1]) - {6}
    states = []
    projections = [set() for _ in holders]
    essential = [False] * len(holders)
    for w in product((0, 1), repeat=10):
        local = [tuple(w[i] for i in h) for h in holders]
        violations = [i for i, word in enumerate(local) if len(set(word)) == 1]
        if not violations:
            states.append(w)
            for projection, loc in zip(projections, local, strict=True):
                projection.add(loc)
        elif len(violations) == 1:
            essential[violations[0]] = True
    assert all(essential) and all(len(proj) == 2 ** len(h) - 2
                                  for h, proj in zip(holders, projections, strict=True))
    ea = {w for w in states if all(w[i] == 0 for i in a)}
    eb = {w for w in states if all(w[i] == 0 for i in b)}
    assert ea and ea < eb and len(a-b) == 4 * len(b-a)
    return {"holders": holders, "first_companions": sorted(a), "second_companions": sorted(b),
            "states": len(states), "first_all_zero": len(ea), "second_all_zero": len(eb),
            "exclusive_companion_counts": [len(a-b), len(b-a)]}


def main():
    results = {reading: classify(reading) for reading in ("uniform", "inherited")}
    assert results["uniform"]["complete_parent_supports_and_fresh"] == results["inherited"]["complete_parent_supports_and_fresh"]
    reference = json.loads((OUTPUT / "selection.json").read_text())
    assert results["uniform"]["complete_parent_supports_and_fresh"] == reference["reference_named_roster"]
    assert results["uniform"]["actual_loose_names"] == results["inherited"]["actual_loose_names"] == reference["actual_loose"]
    results["old_companion_forcing_checks"] = old_companion_control()
    results["two_distinct_old_loose_twins"] = repeated_old_control()
    results["sharp_one_way_factor_four"] = tight_one_way_control()
    path = OUTPUT / "role_proof.json"
    path.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({key: results[key]["exclusion_histogram"] for key in ("uniform", "inherited")}))


if __name__ == "__main__":
    main()
