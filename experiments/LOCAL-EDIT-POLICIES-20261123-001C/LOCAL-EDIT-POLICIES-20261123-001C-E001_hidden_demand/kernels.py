"""Contract the literal prepared knots at both detector and guard cuts."""

from functools import cache
from itertools import product
from math import prod
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
BITS = (0, 1)
PAIRS = tuple(product(BITS, repeat=2))
WORDS = tuple(product(BITS, repeat=3))
IDENTITY, P, Q = (0, 1, 2), (1, 0, 2), (0, 2, 1)


def law_passes(law, values):
    if law == "parity":
        return sum(values) % 2 == 0
    if law == "nae":
        return min(values) != max(values)
    raise ValueError(law)


@cache
def hidden(law, active, c):
    """Tally the two shared middle bits and the active H's two private inputs."""
    allowed = []
    for middle, loose in product(PAIRS, repeat=2):
        high = (c[active], *middle, *loose)
        low = (c[1 - active], *middle)
        if law_passes(law, high) and law_passes(law, low):
            allowed.append((middle, loose))
    return tuple(allowed)


@cache
def address_factor(law, c, w):
    return sum(law_passes(law, (*meet, opening)) and law_passes(law, (*meet, c, w))
               for meet in PAIRS for opening in BITS)


def device(law, active, terminals):
    ways = 0
    for c, w in product(PAIRS, repeat=2):
        detector = sum(law_passes(law, (*w, *terminals, *private)) for private in WORDS)
        addresses = prod(address_factor(law, ci, wi) for ci, wi in zip(c, w, strict=True))
        ways += len(hidden(law, active, c)) * addresses * detector
    return ways


def one_ternary_pair(law):
    return [[sum(law_passes(law, (a, *middle)) and law_passes(law, (b, *middle))
                 for middle in PAIRS) for b in BITS] for a in BITS]


def route(u, v, commuting=False):
    second = P if commuting else Q
    destinations = IDENTITY
    for permutation in (P if u else IDENTITY, second if v else IDENTITY) * 2:
        destinations = tuple(permutation[lane] for lane in destinations)
    return destinations


def power(matrix, n):
    previous = [[1, 0], [0, 1]]
    for _ in range(n):
        previous = [[sum(previous[a][c] * matrix[c][b] for c in BITS) for b in BITS] for a in BITS]
    return previous


def correspondence(matrix, left, right, permutation=IDENTITY):
    return prod(matrix[left[lane]][right[destination]] for lane, destination in enumerate(permutation))


def law_kernels(law):
    near = [[device(law, active, terminals) for terminals in WORDS] for active in BITS]
    assert near[0] == near[1]
    for c in PAIRS:
        assert len(hidden(law, 0, c)) == len(hidden(law, 1, c))
    one = one_ternary_pair(law)
    terminal_guard = [[mass * correspondence(one, terminals, z) for z in WORDS]
                      for terminals, mass in zip(WORDS, near[0], strict=True)]
    guard = list(map(sum, zip(*terminal_guard, strict=True)))
    ends = {"terminal": near[0], "guard": guard}
    pairs = {}
    for left_name, left_mass in ends.items():
        for right_name, right_mass in ends.items():
            layers = 8 - (left_name == "guard") - (right_name == "guard")
            transfer = power(one, layers)
            output = {}
            for u, v in PAIRS:
                permutation = route(u, v)
                table = [[left_mass[i] * right_mass[j] * correspondence(transfer, a, b, permutation)
                          for j, b in enumerate(WORDS)] for i, a in enumerate(WORDS)]
                output[f"{u}{v}"] = table
            pairs[f"{left_name}_{right_name}"] = output
    totals = {sum(map(sum, table)) for pair in pairs.values() for table in pair.values()}
    assert len(totals) == 1
    return {
        "source_total_each": totals.pop(),
        "H_completion_counts": {f"{c[0]}{c[1]}": len(hidden(law, 0, c)) for c in PAIRS},
        "one_piece": one,
        "local_weights_at_terminal": near[0],
        "local_weights_at_guard": guard,
        "local_terminal_guard": terminal_guard,
        "pair_kernels": pairs,
    }


def main():
    result = {
        "word_order": ["".join(map(str, w)) for w in WORDS],
        "type_order": ["00", "01", "10", "11"],
        "row_side": "Alice",
        "column_side": "Bob",
        "joint_units": "Complete allowed old presentations per stipulated type; type priors each 1/4.",
        "guard_location": "The triple beyond the nearest complete fixed correspondence.",
        "local_terminal_guard": "Rows detector triples, columns outer guard triples, before other end is attached.",
        "laws": {law: law_kernels(law) for law in ("parity", "nae")},
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "kernels.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")
    for law, measurement in result["laws"].items():
        print(law, measurement["source_total_each"], measurement["local_weights_at_terminal"])


if __name__ == "__main__":
    main()
