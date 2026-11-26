"""Independent exact checks of the closed-pattern census and controls."""

import argparse
from collections import Counter
from itertools import chain, combinations, permutations, product
import json
from math import factorial
from pathlib import Path
import random

import networkx as nx


STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parents[1]
PRIOR_CENSUS = (
    REPO / "artifacts/FOUR-READINGS-20261120-001A"
    / "FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
)


def knot_words(knots, holders):
    return [tuple(i for i, ends in enumerate(holders) if u in ends) for u in range(knots)]


def word_phase(word, variables):
    """Normal order the word and keep its sign as a linear GF(2) expression."""
    active = set()
    phase = 0
    for label in word:
        for earlier in active:
            if earlier < label:
                phase ^= variables.get((earlier, label), 0)
        active.symmetric_difference_update((label,))
    return phase


def binary_solution(equations):
    """Solve with free variables zero, returning None on contradiction."""
    pivots = {}
    for row, target in equations:
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = (row, target)
                break
            replacement, flip = pivots[bit]
            row ^= replacement
            target ^= flip
        else:
            if target:
                return None
    answer = 0
    for bit, (row, target) in sorted(pivots.items()):
        if (row & answer).bit_count() % 2 != target:
            answer |= 1 << bit
    assert all((row & answer).bit_count() % 2 == target for row, target in equations)
    return answer


def state_witness(words, unheld, assignment, closing_sign):
    """Build a common eigenstate as a signed sum of basis words."""
    signs = [0] * (1 + max(chain.from_iterable(words)))
    for i, (a, b) in enumerate(unheld):
        if assignment >> i & 1:
            signs[a] |= 1 << b

    def act(word, basis):
        phase = 0
        for letter in reversed(word):
            phase ^= (signs[letter] & basis).bit_count() % 2
            basis ^= 1 << letter
        return basis, 1 - 2 * phase

    state = {0: 1}
    for word in words[:-1]:
        projected = state.copy()
        for basis, coefficient in state.items():
            changed, phase = act(word, basis)
            assert changed not in projected, "older knot supports were dependent"
            projected[changed] = phase * coefficient
        state = projected

    for u, word in enumerate(words):
        eigenvalue = 1 - 2 * closing_sign if u == len(words) - 1 else 1
        for basis, coefficient in state.items():
            changed, phase = act(word, basis)
            assert coefficient * phase == eigenvalue * state[changed]
    return len(state)


def has_outer_embedding(knots, holders, unheld):
    """Search circular knot orders for one with no interleaving unheld pairs."""
    endpoints = [(holders[a], holders[b]) for a, b in unheld]
    for order in permutations(range(1, knots)):
        positions = [0] * knots
        for i, u in enumerate(order, start=1):
            positions[u] = i
        for (u, v), (s, t) in endpoints:
            left, right = sorted((positions[u], positions[v]))
            if (left < positions[s] < right) != (left < positions[t] < right):
                break
        else:
            return True
    return False


def analyze(knots, raw_holders, shuffle):
    holders = [frozenset(ends) for ends in raw_holders]
    words = knot_words(knots, holders)
    unheld = [
        (a, b) for a, b in combinations(range(len(holders)), 2)
        if holders[a].isdisjoint(holders[b])
    ]
    variables = {pair: 1 << i for i, pair in enumerate(unheld)}
    signs = [word_phase(a + b, variables) ^ word_phase(b + a, variables)
             for a, b in combinations(words, 2)]
    closure = word_phase(chain.from_iterable(words), variables)
    r1 = all(row.bit_count() % 2 == 0 for row in signs)
    r2 = closure.bit_count() % 2 if r1 else None
    r3_witness = binary_solution([(row, 0) for row in signs] + [(closure, 1)])
    r3 = r3_witness is not None
    if r1:
        r_assignment = (1 << len(unheld)) - 1
        assert state_witness(words, unheld, r_assignment, r2) == 1 << (knots - 1)
    if r3:
        assert state_witness(words, unheld, r3_witness, 1) == 1 << (knots - 1)

    shuffles = 0
    if r1 and shuffle is not None:
        for _ in range(20):
            names = list(range(len(holders)))
            shuffle.shuffle(names)
            word_lists = [[names[x] for x in word] for word in words]
            shuffle.shuffle(word_lists)
            for word in word_lists:
                shuffle.shuffle(word)
            renamed = {tuple(sorted((names[a], names[b]))): bit
                       for (a, b), bit in variables.items()}
            new_phase = word_phase(chain.from_iterable(word_lists), renamed)
            assert new_phase.bit_count() % 2 == r2
            shuffles += 1

    central = sum(
        all((word_phase(word + (a,), variables) ^ word_phase((a,) + word, variables))
            .bit_count() % 2 == 0 for a in range(len(holders)))
        for word in words
    )
    sharing = nx.Graph()
    sharing.add_nodes_from(range(knots))
    sharing.add_edges_from(holders)
    columns = {
        "knots": knots,
        "distinctions": len(holders),
        "unheld pairs": len(unheld),
        "R1 knots commute under R": r1,
        "R2 sum forced under R": ("odd" if r2 else "even") if r1 else None,
        "R3 odd attainable": r3,
        "knots commuting with every value under R": central,
        "planar": nx.check_planarity(sharing)[0],
        "outerplanar": has_outer_embedding(knots, holders, unheld),
        "cut knots": len(list(nx.articulation_points(sharing))),
    }
    assert r3 != columns["outerplanar"]
    return columns, sharing, shuffles, r3_witness


def analytic_r1(sharing):
    neighbours = {u: set(sharing[u]) for u in sharing}
    for u, v in combinations(sharing, 2):
        joined = int(v in neighbours[u])
        degree_product = (len(neighbours[u]) - joined) * (len(neighbours[v]) - joined)
        if (degree_product - len(neighbours[u] & neighbours[v])) % 2:
            return False
    return True


def ordinary_closing_knots(sharing):
    """Apply the prior study's general last-birth criterion to each puncture."""
    # If a cut knot is removed, the start is disconnected. If it remains,
    # its own projection in the closed pattern wired through the exterior fails.
    if next(nx.articulation_points(sharing), None) is not None:
        return []
    survivors = []
    for removed in sharing:
        old = sharing.copy()
        old.remove_node(removed)
        neighbours = {u: set(old[u]) for u in old}
        parents = set(sharing[removed])
        if (all(neighbours[a] & neighbours[b] for a, b in combinations(parents, 2))
                and all(not parents <= neighbours[u] for u in old)):
            survivors.append(removed)
    return sorted(survivors)


def controls():
    rows = {
        "three readers": (4, list(combinations(range(4), 2)), (True, "odd", True, 0)),
        "five-knot all-pairs pattern": (
            5, list(combinations(range(5), 2)), (True, "odd", True, 5)
        ),
        "nine-distinction square": (
            6, list(product(range(3), range(3, 6))), (True, "odd", True, 6)
        ),
        "two readers": (
            4, [(0, 1), (0, 1), (2, 3), (2, 3), (0, 2), (1, 3)],
            (False, None, False, 0)
        ),
        "eight-knot closure": (
            8, [(u, u ^ (1 << p)) for u in range(8) for p in range(3) if not u >> p & 1],
            (False, None, True, 0)
        ),
    }
    for knots, times in [(3, 2), (4, 2), (5, 2), (4, 3)]:
        ends = [(u, (u + 1) % knots) for u in range(knots) for _ in range(times)]
        expected = (True, "even", False, knots) if times == 2 else (False, None, False, 0)
        rows[f"ring of {knots} with {times} distinctions per meeting"] = knots, ends, expected
    for name, (knots, ends, expected) in rows.items():
        columns, _, _, witness = analyze(knots, ends, None)
        assert tuple(columns[key] for key in (
            "R1 knots commute under R", "R2 sum forced under R", "R3 odd attainable",
            "knots commuting with every value under R"
        )) == expected, (name, columns)
        print(json.dumps({"control": name, **columns,
                          "R3 anticommuting pairs in witness": witness_pairs(ends, witness)}))


def witness_pairs(ends, witness):
    if witness is None:
        return None
    eligible = [(a, b) for a, b in combinations(ends, 2) if set(a).isdisjoint(b)]
    return [pair for i, pair in enumerate(eligible) if witness >> i & 1]


def verify_signed_identity(record):
    signs = []
    for word in knot_words(record["n"], record["sharing"]):
        phase, x, z = 0, 0, 0
        for label in word:
            p, a, b = record["pauli_i_phase_X_bits_Z_bits"][label]
            phase += p + 2 * (z & a).bit_count()
            x ^= a
            z ^= b
        assert (x, z) == (0, 0)
        assert phase % 2 == 0
        signs.append(phase // 2 % 2)
    assert sum(signs) % 2 == 1
    return signs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="prefix of the raw census for timing")
    args = parser.parse_args()
    census = json.loads(PRIOR_CENSUS.read_text())
    reported = [json.loads(line) for line in (STUDY / "rule_census.jsonl").read_text().splitlines()]
    assert len(census) == len(reported) == 173
    rng = random.Random(20261127)

    named_types = {
        22: ("six knots all pairs", nx.complete_graph(6), "odd", True),
        42: ("three by four", nx.complete_bipartite_graph(3, 4), "even", False),
        133: ("one knot meeting all of three by three", nx.complete_multipartite_graph(1, 3, 3),
              "odd", False),
        172: ("seven knots all pairs", nx.complete_graph(7), "odd", True),
    }

    tallies = Counter()
    rebuilt = 0
    shuffles = 0
    for index, record in enumerate(census[:args.limit]):
        ends = record["sharing"]
        columns, sharing, shuffled, witness = analyze(record["n"], ends, rng)
        closing = ordinary_closing_knots(sharing)
        assert closing == sorted(record["restored_last_holders"]), (index, closing)
        labelled = factorial(len(sharing)) // sum(
            1 for _ in nx.isomorphism.GraphMatcher(sharing, sharing).isomorphisms_iter()
        )
        assert labelled == record["labelled"], (index, labelled)
        assert analytic_r1(sharing) == columns["R1 knots commute under R"], index
        assert columns["planar"] == (not record["operator"]), index
        columns.update({
            "type": index,
            "atlas": record["atlas"],
            "labelled": labelled,
            "operator (signed identities)": record["operator"],
            "reached by ordinary growth": bool(closing),
        })
        assert columns == reported[index], (index, columns, reported[index])
        rebuilt += 1
        shuffles += shuffled
        r2 = columns["R2 sum forced under R"]
        if index in named_types:
            name, expected_graph, expected_sign, expected_reached = named_types[index]
            assert nx.is_isomorphic(sharing, expected_graph)
            assert (r2, bool(closing), record["operator"]) == (expected_sign, expected_reached, True)
            print(json.dumps({"named pattern": name, **columns, "restored knots": closing,
                              "stored signed-identity signs": verify_signed_identity(record),
                              "R3 anticommuting pairs in witness": witness_pairs(ends, witness)}))
        if r2 == "even":
            print(json.dumps({"even under R": index, "arities": record["arities"],
                              "atlas": record["atlas"], "restored knots": closing,
                              "stored signed-identity signs":
                                  verify_signed_identity(record) if record["operator"] else None}))
        populations = {
            "all": True,
            "reached": bool(closing),
            "reached, operator-positive": bool(closing) and record["operator"],
            "reached, operator-negative": bool(closing) and not record["operator"],
            "operator-negative": not record["operator"],
        }
        for population, included in populations.items():
            if included:
                for weighting, weight in (("by type", 1), ("by labelled pattern", labelled)):
                    for metric, applicable in {
                        "total": True,
                        "R1": r2 is not None,
                        "R2 odd": r2 == "odd",
                        "R2 even": r2 == "even",
                        "R3": columns["R3 odd attainable"],
                    }.items():
                        tallies[weighting, population, metric] += weight * applicable

    controls()
    for (weighting, population) in sorted({key[:2] for key in tallies}):
        values = {metric: value for (w, p, metric), value in tallies.items()
                  if (w, p) == (weighting, population)}
        print(json.dumps({"weighting": weighting, "population": population, **values}))
    print(json.dumps({"matching rows": rebuilt, "shuffles with unchanged R2": shuffles,
                      "closed form R1 agreements": rebuilt, "planarity agreements": rebuilt}))


if __name__ == "__main__":
    main()
