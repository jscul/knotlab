"""Construct exact reader-local states using one qubit per failing pair."""

import json
from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations, permutations
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "MOST-FAILING-20261127-001/referee-R1/codes.jsonl"


@dataclass(frozen=True)
class Read:
    """On input |x>, flip bits in flip and multiply by (-1)^parity(x & phase)."""

    flip: int
    phase: int

    def apply(self, x):
        return x ^ self.flip, 1 - 2 * ((x & self.phase).bit_count() % 2)


def columns(holders):
    return [[d for d, pair in enumerate(holders) if k in pair]
            for k in range(1 + max(max(pair) for pair in holders))]


def grown_samples():
    # Distinction and knot numbers come from the prior independent growth recount.
    descriptions = {
        17: ("Four knots meeting once each", [(0, 5), (1, 4), (2, 3)],
             [(0, 5), (1, 4), (2, 3)]),
        168: ("Eight knots with a strict choice on four of them", [(0, 7), (1, 5), (3, 4)],
              [(0, 7), (1, 5), (3, 4)]),
        5127: ("Six knots with three settings at each of three readers",
               [(0, 6), (0, 9), (2, 4), (2, 10), (5, 7), (5, 8)],
               [(0, 6, 9), (2, 4, 10), (5, 7, 8)]),
        5484: ("Six knots with reader sizes two, two, three and two",
               [(0, 7), (2, 6), (3, 5), (3, 9), (4, 8)],
               [(0, 7), (2, 6), (3, 5, 9), (4, 8)]),
    }
    with PREVIOUS.open() as file:
        for row in map(json.loads, file):
            start = row.get("start")
            if start in descriptions:
                name, failing, readers = descriptions[start]
                assert set(failing) <= set(map(tuple, row["pairs"]))
                yield f"{name} (census index {start})", row["supports"], failing, readers


def fixture_samples():
    n = 5
    ring = columns([(0, 1 + j) for j in range(n)] +
                   [(1 + j, 1 + (j + 1) % n) for j in range(n)])
    pairs = [(j, n + (j + n // 2) % n) for j in range(n)]
    yield "One knot meeting all five knots of a ring", ring, pairs, pairs

    joined = columns([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5),
                      (0, 3), (1, 4), (2, 5)])
    readers = [(0, 3, 8), (1, 4, 6), (2, 5, 7)]
    for middle in (0, 1):
        failing = [tuple(sorted((reader[middle], d)))
                   for reader in readers for d in reader if d != reader[middle]]
        which = "first" if middle == 0 else "second"
        yield f"Two joined rings of three, failures centered on the {which} ring", joined, failing, readers


def make_questions(knots, failing, readers, reverse):
    owner = {d: i for i, reader in enumerate(readers) for d in reader}
    assert len(owner) == sum(map(len, readers))
    assert set(owner) == {d for pair in failing for d in pair}
    assert all(owner[a] == owner[b] for a, b in failing)
    assert all(len({owner[d] for d in k if d in owner}) == len(set(k) & owner.keys())
               for k in knots)
    all_distinctions = {d for knot in knots for d in knot}
    assert all(sum(d in knot for knot in knots) == 2 for d in all_distinctions)
    # A qubit is shared by exactly its pair of values, both in the same reader.
    settings = {d: Read(0, 0) for d in owner}
    for i, pair in enumerate(failing):
        a, b = reversed(pair) if reverse else pair
        settings[a] = Read(settings[a].flip | 1 << i, settings[a].phase)
        settings[b] = Read(settings[b].flip, settings[b].phase | 1 << i)
    questions = []
    for knot in knots:
        flip = phase = 0
        for d in knot:
            if d not in settings:
                continue
            value = settings[d]
            # Distinct settings at a knot act on disjoint qubits.
            assert not ((flip | phase) & (value.flip | value.phase))
            flip |= value.flip
            phase |= value.phase
        questions.append(Read(flip, phase))
    return settings, questions, sorted(all_distinctions - owner.keys())


def check_commutation(left, right, expected_sign, dimension):
    for seed in range(dimension):
        a, sa = left.apply(seed)
        ab, sab = right.apply(a)
        b, sb = right.apply(seed)
        ba, sba = left.apply(b)
        assert ab == ba and sa * sab == expected_sign * sb * sba


def product_sign(questions, order, seed=0):
    x, sign = seed, 1
    for k in order:
        x, factor = questions[k].apply(x)
        sign *= factor
    assert x == seed
    return sign


def find_state(questions, targets, dimension):
    # Solve the amplitude equalities on each orbit of flips. A consistent orbit
    # gives an explicit pure state, with a common normalization left out.
    seen = set()
    for seed in range(dimension):
        if seed in seen:
            continue
        amplitudes = {seed: 1}
        pending = deque([seed])
        consistent = True
        while pending:
            x = pending.popleft()
            for read, target in zip(questions, targets):
                dest, sign = read.apply(x)
                amp = target * sign * amplitudes[x]
                if dest in amplitudes:
                    consistent &= amplitudes[dest] == amp
                else:
                    amplitudes[dest] = amp
                    pending.append(dest)
        seen.update(amplitudes)
        if consistent:
            return amplitudes
    return None


def verify_state(questions, targets, amplitudes, dimension):
    for read, target in zip(questions, targets):
        for x in range(dimension):
            dest, sign = read.apply(x)
            assert amplitudes.get(dest, 0) == target * sign * amplitudes.get(x, 0)


def classical_scores(knots, active, targets):
    active = sorted(active)
    questions = [sum(1 << i for i, d in enumerate(active) if d in k) for k in knots]
    errors = Counter()
    for answer_bits in range(1 << len(active)):
        local_signs = [1 - 2 * ((answer_bits & q).bit_count() % 2) for q in questions]
        errors[sum(s != target for s, target in zip(local_signs, targets))] += 1
    assert 0 not in errors
    assert all(e % 2 == 1 for e in errors)
    return dict(sorted(errors.items()))


def check_sample(knots, failing, readers):
    failing = sorted(failing)
    failing_set = set(failing)
    assert len(failing_set) == len(failing)
    dimension = 1 << len(failing)
    orientations = []
    for reverse in (False, True):
        settings, questions, outside = make_questions(knots, failing, readers, reverse)
        for a, b in combinations(sorted(settings), 2):
            check_commutation(settings[a], settings[b], -1 if (a, b) in failing_set else 1, dimension)
        for left, right in combinations(questions, 2):
            check_commutation(left, right, 1, dimension)
        for seed in range(dimension):
            assert product_sign(questions, range(len(questions)), seed) == -1
        orders = Counter(product_sign(questions, order) for order in permutations(range(len(knots))))
        assert set(orders) == {-1}
        free_knots = []
        for free in range(len(knots)):
            # Enumerate outside signs in order of their negative count, keeping
            # the first actual state. The empty choice tests all signs positive.
            found = False
            for count in range(len(outside) + 1):
                for negatives in combinations(outside, count):
                    targets = [(-1) ** ((k == free) + len(set(knot).intersection(negatives)))
                               for k, knot in enumerate(knots)]
                    state = find_state(questions, targets, dimension)
                    if state is None:
                        continue
                    verify_state(questions, targets, state, dimension)
                    errors = classical_scores(knots, settings, targets)
                    free_knots.append({
                        "free knot": free,
                        "negative outside distinctions": negatives,
                        "reader product signs by knot": targets,
                        "positive basis amplitudes": sorted(x for x, sign in state.items() if sign == 1),
                        "negative basis amplitudes": sorted(x for x, sign in state.items() if sign == -1),
                        "squared normalization divisor": len(state),
                        "classical lists by number of failed questions": errors,
                    })
                    found = True
                    break
                if found:
                    break
            assert found
        orientations.append({
            "X on the lower numbered distinction of each pair": not reverse,
            "orders with product minus identity": orders[-1],
            "one state per free knot": free_knots,
        })
    return {
        "knots in order": knots, "qubits in order (the failing pairs)": failing, "readers": readers,
        "distinctions outside readers": outside,
        "knots asking no reader": [k for k, knot in enumerate(knots) if not set(knot) & settings.keys()],
        "orientations": orientations,
    }


def component_sets(pairs):
    groups = []
    for a, b in pairs:
        joined = {a, b}
        separate = []
        for group in groups:
            if group & {a, b}:
                joined.update(group)
            else:
                separate.append(group)
        groups = [*separate, joined]
    return sorted(tuple(sorted(group)) for group in groups)


def word_details(knots, show_collisions=False):
    # These fixtures have at most 18 unheld pairs. Inspect all subsets directly.
    distinctions = sorted({d for knot in knots for d in knot})
    holder = {d: [k for k, knot in enumerate(knots) if d in knot] for d in distinctions}
    pairs = [(a, b) for a, b in combinations(distinctions, 2) if not set(holder[a]) & set(holder[b])]
    tests = [sum(1 << j for j, (a, b) in enumerate(pairs)
                 if (k in holder[a] and l in holder[b]) or (k in holder[b] and l in holder[a]))
             for k, l in combinations(range(len(knots)), 2)]
    alternating = 0
    for j, (a, b) in enumerate(pairs):
        left, right = holder[a]
        if (left < holder[b][0] < right) != (left < holder[b][1] < right):
            alternating |= 1 << j
    parities = Counter()
    splits, collisions = [], []
    for word in range(1 << len(pairs)):
        if any((word & test).bit_count() % 2 for test in tests):
            continue
        parity = (word & alternating).bit_count() % 2
        parities[parity] += 1
        failing = [pair for j, pair in enumerate(pairs) if word & (1 << j)]
        groups = component_sets(failing)
        repeat = next(((k, sorted(set(knot) & set(g))) for k, knot in enumerate(knots)
                       for g in groups if len(set(knot) & set(g)) > 1), None)
        if repeat is None:
            splits.append({"odd": bool(parity), "failing pairs": failing, "groups": groups})
        elif parity and show_collisions:
            collisions.append({"failing pairs": failing, "knot and its distinctions in one group": repeat})
    return {"knots": knots, "commuting choices by sign bit": dict(sorted(parities.items())),
            "choices permitting readers (includes empty choice)": splits,
            **({"witness against a split for each odd choice": collisions} if show_collisions else {})}


def representations(columns, target):
    """How many subsets have the required parity vector?"""
    basis = {}
    for col in columns:
        while col:
            pos = col.bit_length()
            if pos not in basis:
                basis[pos] = col
                break
            col ^= basis[pos]
    while target:
        pos = target.bit_length()
        if pos not in basis:
            return 0
        target ^= basis[pos]
    return 1 << (len(columns) - len(basis))


def bare_ring(n):
    # Every ring meeting in an odd split must fail with one meeting of the
    # common knot. Record its reader by the ring knot that holds that meeting.
    parity_for_pair = {pair: 1 << i for i, pair in enumerate(combinations(range(n), 2))}
    adjacent = [(i, (i + 1) % n) for i in range(n)]
    options = [[(j, sum(parity_for_pair[tuple(sorted((j, k)))] for k in held)) for j in range(n) if j not in held]
               for held in adjacent]
    between = {(i, j): sum(parity_for_pair[tuple(sorted((k, l)))] for k in adjacent[i] for l in adjacent[j])
               for i, j in combinations(range(n), 2) if not set(adjacent[i]) & set(adjacent[j])}
    examined = words = strict = 0
    first = None

    def assign(owners, total, extra):
        nonlocal examined, words, strict, first
        i = len(owners)
        if i == n:
            examined += 1
            count = representations(extra, total) if extra else int(total == 0)
            words += count
            if count:
                strict += int(len(set(owners)) == n)
                if first is None:
                    first = owners
            return
        for j, parity in options[i]:
            if owners and (owners[-1] == j or (i == n - 1 and j == owners[0])):
                continue
            added = [between[k, i] for k, earlier_owner in enumerate(owners) if earlier_owner == j]
            assign((*owners, j), total ^ parity, extra + added)

    assign((), 0, [])
    return {"ring knots": n, "reader assignments checked": examined, "odd choices with a split": words,
            "strict odd choices": strict, "first feasible assignment": first}


def main():
    samples = dict((name, check_sample(knots, failing, readers))
                   for name, knots, failing, readers in [*grown_samples(), *fixture_samples()])
    assert len(samples) == 7
    two_rings = columns([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)])
    three_by_three = columns([(i, 3 + j) for i in range(3) for j in range(3)])
    five_knots = [[0, 1, 2], [0, 3, 4], [1, 3, 5], [2, 4, 6], [5, 6]]
    document = {
        "sample": "Four named grown closures and three choices on two named fixtures, selected for coverage.",
        "basis convention": "Bit i is qubit i starting with the least significant bit. Divide signed unit "
                            "amplitudes by the square root of the listed squared normalization divisor. All "
                            "unlisted amplitudes are zero.",
        "classical convention": "One fixed sign per distinction with a reader. Each knot is one question.",
        "samples": samples,
        "hand fixture details": {
            "Two rings of three joined knot to knot": word_details(two_rings),
            "Three knots each meeting each of three others": word_details(three_by_three),
            "Five knots obtained by closing two loose distinctions": word_details(five_knots, show_collisions=True),
            "A common knot and a bare ring, no other meetings": [bare_ring(n) for n in range(3, 9)],
        },
    }
    (HERE / "certificate.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"{len(samples)} constructed choices, "
          f"{sum(len(o['one state per free knot']) for s in samples.values() for o in s['orientations'])} states")


if __name__ == "__main__":
    main()
