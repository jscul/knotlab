"""Reconstruct complete parity-game records before reading the saved tables.

The six-knot Born calculation applies local filters directly to an integer
bipartite vector. The eight-knot calculation checks the inputs to a word
cancellation. No study code or archived numeric result enters either calculation.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, islice, product
import json
from math import prod
from pathlib import Path
import resource
from time import perf_counter


WORDS = tuple(product((0, 1), repeat=3))
ANSWERS = tuple(product(WORDS, repeat=2))
SIX = tuple(tuple(range(3 * i, 3 * i + 3)) for i in range(3)) + tuple(
    tuple(range(i, 9, 3)) for i in range(3)
)
SIX_INPUTS = tuple(product(range(3), range(3, 6)))
PAULI_PAIRS = ("XI", "IX", "XX", "IZ", "ZI", "ZZ", "XZ", "ZX", "YY")
ARCHIVE = (
    Path(__file__).resolve().parents[3] / "artifacts" / "FOUR-READINGS-20261120-001A"
    / "FOUR-READINGS-20261120-001A-E001_signed_rules"
)


def word_text(word):
    return "".join(map(str, word))


def held_distinctions(meetings, count):
    return tuple(tuple(i for i, pair in enumerate(meetings) if knot in pair)
                 for knot in range(count))


def bits(mask, distinctions):
    return tuple((mask >> i) & 1 for i in distinctions)


def supported_rows(knots, odd, pairs, *, double_one=False):
    rows = []
    for x, y in pairs:
        shared = sorted(set(knots[x]) & set(knots[y]))
        positions = [(knots[x].index(i), knots[y].index(i)) for i in shared]
        weights = []
        for a, b in ANSWERS:
            permitted = (sum(a) % 2 == (x == odd) and sum(b) % 2 == (y == odd)
                         and all(a[i] == b[j] for i, j in positions))
            weight = int(permitted)
            if double_one and a[positions[0][0]]:
                weight *= 2
            weights.append(weight)
        rows.append({"inputs": [x, y], "shared": shared, "numerator": weights,
                     "denominator": sum(weights)})
    return rows


def marginal_records(rows, *, odd=None):
    largest = []
    for side in (0, 1):
        groups = {}
        for row in rows:
            counts = row["numerator"]
            inputs = row["inputs"]
            if side == 0:
                totals = [sum(counts[8 * i:8 * (i + 1)]) for i in range(8)]
            else:
                totals = [sum(counts[i::8]) for i in range(8)]
            dist = tuple(Fraction(n, row["denominator"]) for n in totals)
            if odd is not None:
                uniform = tuple(Fraction(1, 4) if sum(w) % 2 == (inputs[side] == odd)
                                else Fraction(0) for w in WORDS)
                require(dist == uniform, f"Nonuniform complete marginal at {inputs}, reader {side}")
            groups.setdefault(inputs[side], []).append(dist)
        largest.append(max((sum(abs(a - b) for a, b in zip(first, second)) / 2
                            for group in groups.values() for first, second in combinations(group, 2)),
                           default=Fraction(0)))
    return [str(value) for value in largest]


def pauli_action(letters):
    # Each column has a single nonzero entry. Powers of i encode the phase
    # before combining the two factors, so no floating point enters.
    action = []
    for source in WORDS[:4]:
        destination = phase = 0
        for bit, letter in zip(source[1:], letters):
            destination = 2 * destination + (bit ^ (letter in "XY"))
            if letter == "Y":
                phase += 1 + 2 * bit
            elif letter == "Z":
                phase += 2 * bit
        require(phase % 2 == 0, f"Nonreal action for {letters}")
        action.append((destination, (-1) ** ((phase // 2) % 2)))
    return tuple(action)


def compose(left, right):
    return tuple((left[j][0], coefficient * left[j][1]) for j, coefficient in right)


def transpose(action):
    return tuple(sorted((target, source, sign) for source, (target, sign) in enumerate(action)))


def six_operators():
    identity = tuple((i, 1) for i in range(4))
    operators = tuple(map(pauli_action, PAULI_PAIRS))
    for action in operators:
        require(compose(action, action) == identity, "Pauli action is not an involution")
        require(tuple((i, sign) for _, i, sign in transpose(action)) == action,
                "Pauli action is not self-adjoint")
    for x, context in enumerate(SIX):
        first, second, third = (operators[i] for i in context)
        for left, right in combinations((first, second, third), 2):
            require(compose(left, right) == compose(right, left), f"Noncommuting setting {x}")
        require(compose(first, compose(second, third)) ==
                tuple((j, (-1) ** (x == 5)) for j in range(4)), f"Wrong product in setting {x}")
    return operators


def joint_born_numerators(operators, inputs):
    transposes = [tuple((i, sign) for _, i, sign in transpose(a)) for a in operators]
    numerators = []
    for a, b in ANSWERS:
        vector = [int(i == j) for i, j in product(range(4), repeat=2)]
        for side, (x, answer) in enumerate(zip(inputs, (a, b))):
            for bit, distinction in zip(answer, SIX[x]):
                action = (operators, transposes)[side][distinction]
                filtered = vector.copy()
                for i, j in product(range(4), repeat=2):
                    target, coefficient = action[(i, j)[side]]
                    index = 4 * target + j if side == 0 else 4 * i + target
                    filtered[index] += (-1) ** bit * coefficient * vector[4 * i + j]
                vector = filtered
        # The unit preparation divides by 2 and the six filters each divide by 2.
        numerator, residue = divmod(sum(value ** 2 for value in vector), 64)
        require(residue == 0, f"A Born weight at {inputs} needs a denominator other than 256")
        numerators.append(numerator)
    require(sum(numerators) == 256, f"Unnormalized Born table at {inputs}")
    return numerators


def six_born(rows):
    operators = six_operators()
    for row in rows:
        numerators = joint_born_numerators(operators, row["inputs"])
        require(all(n * row["denominator"] == 256 * w
                    for n, w in zip(numerators, row["numerator"])),
                f"Born weights differ from uniform compatible records at {row['inputs']}")
        row["born_numerators_over_256"] = numerators


def scalar_scores(limit):
    scores = Counter()
    for mask in range(limit):
        legal = tuple(sum(bits(mask, context)) % 2 == (x == 5)
                      for x, context in enumerate(SIX))
        scores[sum(legal), sum(legal[x] and legal[y] for x, y in SIX_INPUTS)] += 1
    return scores


def local_score(answers):
    return sum(answers[x][y - 3] == answers[y][x] for x, y in SIX_INPUTS)


def local_scores(limit):
    choices = [tuple(w for w in WORDS if sum(w) % 2 == (x == 5)) for x in range(6)]
    return Counter(local_score(a) for a in islice(product(*choices), limit))


def classical_record(scalar, local):
    return {"scalar_best_rules": max(rules for rules, _ in scalar),
            "scalar_best_game": max(trials for _, trials in scalar),
            "scalar_histograms": {f"{r}_rules_{g}_pairs": count for (r, g), count in scalar.items()},
            "local_best": max(local),
            "local_wins_histogram": {str(wins): count for wins, count in local.items()}}


def check_local_example(example, best):
    require(len(example) == 6 and all(s in tuple(map(word_text, WORDS)) for s in example),
            "Saved classical witness has malformed words")
    answers = tuple(tuple(map(int, word)) for word in example)
    require(all(sum(word) % 2 == (x == 5) for x, word in enumerate(answers)),
            "Saved classical witness has an illegal answer")
    require(local_score(answers) == best, "Saved classical witness has the wrong score")


def eight_cancellation(meetings, knots):
    odd = 7
    groups = ((0, 1, 3, 2), (4, 5, 7, 6))
    matched = [meetings.index((u, v)) for u, v in zip(*groups)]
    products = []
    for group in groups:
        within = [meetings.index(tuple(sorted((group[i], group[(i + 1) % 4])))) for i in range(4)]
        word = []
        for i, knot in enumerate(group):
            pair = (within[i - 1], within[i])
            require(set(knots[knot]) == set((*pair, matched[i])), f"Wrong three operators at {knot}")
            for letter in pair:
                if word and word[-1] == letter:
                    word.pop()
                else:
                    word.append(letter)
        require(not word, "An ordered product of paired involutions did not cancel")
        products.append(prod((-1) ** (knot == odd) for knot in group))
    require(products[0] == -products[1], "The two ordered products do not contradict")
    return {"matched_distinctions_in_order": matched, "forced_products": products}


def four_instructions(variables, limit):
    outgoing = tuple(tuple(i for i, (u, _) in enumerate(variables) if u == x) for x in range(4))
    incoming = tuple(tuple(i for i, (_, v) in enumerate(variables) if v == y) for y in range(4))
    instructions = {}
    for mask in range(limit):
        left = tuple(bits(mask, owned) for owned in outgoing)
        right = tuple(bits(mask, owned) for owned in incoming)
        if all(sum(w) % 2 == (i == 3) for reader in (left, right) for i, w in enumerate(reader)):
            instructions[mask] = (left, right)
    return instructions


def check_four_mixture(instructions, rows):
    for row in rows:
        x, y = row["inputs"]
        counts = Counter((left[x], right[y]) for left, right in instructions.values())
        require(all(counts[a] * row["denominator"] == weight * len(instructions)
                    for a, weight in zip(ANSWERS, row["numerator"])),
                f"The rebuilt instructions give a different four-knot row at {(x, y)}")


def require(condition, problem):
    if not condition:
        raise ValueError(problem)


def compare(label, observed, expected):
    require(type(observed) is type(expected), f"{label}: wrong type")
    if isinstance(expected, dict):
        require(observed.keys() == expected.keys(), f"{label}: wrong keys")
        for key, value in expected.items():
            compare(f"{label}.{key}", observed[key], value)
    elif isinstance(expected, list):
        require(len(observed) == len(expected), f"{label}: wrong length")
        for i, (actual, wanted) in enumerate(zip(observed, expected)):
            compare(f"{label}[{i}]", actual, wanted)
    else:
        require(observed == expected, f"{label}: saved {observed!r}, rebuilt {expected!r}")


def read_archive():
    data = (ARCHIVE / "games.json").read_bytes()
    digest = sha256(data).hexdigest()
    receipt = json.loads((ARCHIVE / "receipt.json").read_bytes())
    compare("receipt.games.json SHA-256", receipt["output_sha256"]["games.json"], digest)
    return json.loads(data), digest


def compare_archive(saved, rebuilt):
    classical = dict(saved["classical"])
    check_local_example(classical.pop("local_eight_example"), rebuilt["classical"]["local_best"])
    compare("games.json", {**saved, "classical": classical}, rebuilt)


def check_corruptions(saved, rebuilt):
    attacks = []
    bad = deepcopy(saved)
    for index, change in ((0, 1), (3, -1), (24, -1), (27, 1)):
        bad["six"][0]["born_numerators_over_256"][index] += change
    attacks.append(("marginal-preserving Born weight change", bad, "six[0].born_numerators_over_256[0]"))

    bad = deepcopy(saved)
    bad["cube_all_pairs"][3]["inputs"] = [0, 4]
    attacks.append(("disjoint input replaced with meeting input", bad, "cube_all_pairs[3].inputs[1]"))

    bad = deepcopy(saved)
    bad["symmetric_four"]["exact_local_hidden_states"][0] = 0
    attacks.append(("illegal four-knot instructions in a list of unchanged size", bad,
                    "symmetric_four.exact_local_hidden_states[0]"))

    rejected = {}
    for label, bad, path in attacks:
        try:
            compare_archive(bad, rebuilt)
        except ValueError as error:
            require(path in str(error), f"{label} failed at an unexpected field: {error}")
            rejected[label] = str(error)
        else:
            raise ValueError(f"Accepted corruption: {label}")
    return rejected


def run(sample):
    six = supported_rows(SIX, 5, SIX_INPUTS[:1] if sample else SIX_INPUTS)
    six_born(six)
    biased = supported_rows(SIX, 5, SIX_INPUTS[:1] if sample else SIX_INPUTS, double_one=True)
    scalar = scalar_scores(64 if sample else 512)
    local = local_scores(128 if sample else 4096)

    meetings = tuple((x, y) for x, y in combinations(range(8), 2) if (x ^ y).bit_count() == 1)
    eight = held_distinctions(meetings, 8)
    alice = tuple(i for i in range(8) if i.bit_count() % 2 == 0)
    bob = tuple(i for i in range(8) if i.bit_count() % 2 == 1)
    eight_pairs = tuple(product(alice, bob))
    eight_full = supported_rows(eight, 7, eight_pairs[:4] if sample else eight_pairs)
    eight_meeting = [row for row in eight_full if row["shared"]]
    cancellation = eight_cancellation(meetings, eight)

    four = held_distinctions(tuple(combinations(range(4), 2)), 4)
    four_pairs = tuple(product(range(4), repeat=2))
    four_distinct = tuple((x, y) for x, y in four_pairs if x != y)
    equal_allowed = supported_rows(four, 3, four_pairs[:2] if sample else four_pairs)
    distinct_only = supported_rows(four, 3, four_distinct[:1] if sample else four_distinct)
    instructions = four_instructions(four_distinct, 1024 if sample else 4096)

    saved, digest = read_archive()
    if sample:
        compare("six sample", saved["six"][:1], six)
        compare("eight sample", saved["cube_all_pairs"][:4], eight_full)
        compare("four sample", saved["symmetric_four"]["includes_equal"][:2], equal_allowed)
        compare("instruction sample", [i for i in saved["symmetric_four"]["exact_local_hidden_states"]
                                       if i < 1024], list(instructions))
        return {"timing_sample": True, "Born_entries": 64, "scalar_assignments": sum(scalar.values()),
                "local_strategies": sum(local.values()), "eight_knot_settings": 4,
                "four_knot_instruction_candidates": 1024}

    check_four_mixture(instructions, distinct_only)
    rebuilt = {
        "precedence": "in every cell, the left output varies more slowly than the right output",
        "order": list(map(word_text, WORDS)),
        "six_sharing": list(map(list, SIX)),
        "six": six,
        "six_TV": marginal_records(six, odd=5),
        "biased_six": biased,
        "biased_TV": marginal_records(biased),
        "classical": classical_record(scalar, local),
        "cube_sharing": list(map(list, meetings)),
        "cube_stars": list(map(list, eight)),
        "cube_all_pairs": eight_full,
        "cube_promised_TV": marginal_records(eight_meeting, odd=7),
        "cube_TV": marginal_records(eight_full, odd=7),
        "symmetric_four": {
            "stars": list(map(list, four)), "distinct_only": distinct_only,
            "TV_distinct": marginal_records(distinct_only, odd=3),
            "includes_equal": equal_allowed, "TV_with_equal": marginal_records(equal_allowed, odd=3),
            "hidden_variables": list(map(list, four_distinct)),
            "exact_local_hidden_states": list(instructions),
        },
    }
    compare_archive(saved, rebuilt)
    born_hist = Counter(n for row in six for n in row["born_numerators_over_256"])
    return {
        "archive_sha256": digest,
        "six": {"Born_entries": sum(born_hist.values()), "Born_numerators_over_256": dict(born_hist),
                "complete_marginals": 2 * len(six), "full_record_TV": rebuilt["six_TV"],
                "biased_full_record_TV": rebuilt["biased_TV"],
                "scalar_assignments": sum(scalar.values()), "legal_local_strategies": sum(local.values()),
                **rebuilt["classical"]},
        "eight": {"meeting_settings": len(eight_meeting), "disjoint_settings": len(eight_full) - len(eight_meeting),
                  "events_per_meeting_setting": 8, "events_per_disjoint_setting": 16,
                  "meeting_full_record_TV": rebuilt["cube_promised_TV"], "full_record_TV": rebuilt["cube_TV"],
                  "ordered_cancellation": cancellation},
        "four": {"distinct_settings": len(distinct_only), "settings_including_equal": len(equal_allowed),
                 "classical_instruction_lists": len(instructions), "instructions_tested": 4096,
                 "distinct_full_record_TV": rebuilt["symmetric_four"]["TV_distinct"],
                 "full_record_TV_with_equal": rebuilt["symmetric_four"]["TV_with_equal"]},
        "adversarial_checks": check_corruptions(saved, rebuilt),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="Time prefixes before the full replay")
    args = parser.parse_args()
    start = perf_counter()
    result = run(args.sample)
    result["elapsed_seconds"] = perf_counter() - start
    result["peak_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
