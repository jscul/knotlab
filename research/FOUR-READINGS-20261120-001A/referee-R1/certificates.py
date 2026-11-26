"""Replay signed holdings using only the frozen record and exact arithmetic."""

import argparse
import hashlib
import json
import random
import resource
import time
from collections import Counter, deque
from itertools import combinations
from math import prod
from pathlib import Path


TICKET = "FOUR-READINGS-20261120-001A"
FAMILY = f"{TICKET}-E001_signed_rules"
ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "research" / TICKET
ARTIFACTS = ROOT / "artifacts" / TICKET / FAMILY
EXPERIMENT = ROOT / "experiments" / TICKET / FAMILY
SEED = 20261126

MATRICES = (
    (1, 0, 0, 1),
    (0, 1, 1, 0),
    (0, -1j, 1j, 0),
    (1, 0, 0, -1),
)
PHASES = (1, 1j, -1, -1j)


def matrix_product(left, right):
    return tuple(
        sum(left[2 * row + middle] * right[2 * middle + col] for middle in (0, 1))
        for row in (0, 1) for col in (0, 1)
    )


def multiplication_table():
    labelled = {
        tuple(phase * coefficient for coefficient in matrix): (phase, letter)
        for phase in PHASES for letter, matrix in enumerate(MATRICES)
    }
    return {
        (i, j): labelled[matrix_product(left, right)]
        for i, left in enumerate(MATRICES) for j, right in enumerate(MATRICES)
    }


TENSOR_PRODUCTS = multiplication_table()


def read_json(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_binding():
    ticket = read_json(ROOT / "tickets" / f"{TICKET}.json")["fields"]
    receipt = read_json(ARTIFACTS / "receipt.json")
    for path, recorded, required in (
        (RECORD / "preregistration.md", receipt["design_sha256"], ticket["design_sha256"]),
        (EXPERIMENT / "contract.json", receipt["contract_sha256"], ticket["frozen_contract_sha256"]),
    ):
        assert digest(path) == recorded == required, path
    for filename, expected in receipt["output_sha256"].items():
        assert digest(ARTIFACTS / filename) == expected, filename
    supplemental_design = RECORD / "supplemental_stress_freeze.md"
    supplemental_digest = digest(supplemental_design)
    supplemental_record = read_json(ARTIFACTS / "supplemental_stress.json")
    recorded_design = ticket["additional_designs"][str(supplemental_design.relative_to(ROOT))]
    assert supplemental_digest == recorded_design == supplemental_record["supplemental_freeze_sha256"]
    return {"receipt_outputs": len(receipt["output_sha256"]), "supplemental_design": supplemental_digest}


def indexed(filename):
    rows = read_json(ARTIFACTS / filename)
    by_id = {row["atlas"]: row for row in rows}
    assert len(rows) == len(by_id), filename
    return by_id


def incidence(row):
    size = row["n"]
    sharing = [tuple(pair) for pair in row["sharing"]]
    assert 4 <= size <= 7
    assert len(sharing) == row["m"] == len(set(sharing))
    incident = [[] for _ in range(size)]
    neighbors = [dict() for _ in range(size)]
    for distinction, (a, b) in enumerate(sharing):
        assert 0 <= a < b < size
        incident[a].append(distinction)
        incident[b].append(distinction)
        neighbors[a][b] = distinction
        neighbors[b][a] = distinction
    assert all(len(word) >= 3 for word in incident)
    assert sorted(map(len, incident)) == row["arities"]
    assert set(path_search(neighbors, 0)) == set(range(size))
    assert row["loop_count"] == len(sharing) - size + 1
    assert row["charge"] == 1
    return incident, neighbors


def path_search(neighbors, first):
    paths = {first: ()}
    pending = deque([first])
    while pending:
        knot = pending.popleft()
        for other, distinction in neighbors[knot].items():
            if other not in paths:
                paths[other] = (*paths[knot], distinction)
                pending.append(other)
    return paths


def tensor_reading(certificate):
    width = max(x.bit_length() for _, x, _ in certificate)
    width = max(width, max(z.bit_length() for _, _, z in certificate))
    tensors = []
    for phase, x, z in certificate:
        assert 0 <= phase < 4 and 0 <= x and 0 <= z
        letters = [0] * width
        for index in range(width):
            has_x, has_z = (x >> index) & 1, (z >> index) & 1
            if has_x and has_z:
                letters[index] = 2
                phase -= 1  # XZ is -iY.
            elif has_x:
                letters[index] = 1
            elif has_z:
                letters[index] = 3
        tensors.append((PHASES[phase % 4], tuple(letters)))
    return width, tensors


def times(left, right):
    scalar_l, letters_l = left
    scalar_r, letters_r = right
    phase_and_letter = [TENSOR_PRODUCTS[pair] for pair in zip(letters_l, letters_r, strict=True)]
    return scalar_l * scalar_r * prod(phase for phase, _ in phase_and_letter), tuple(
        letter for _, letter in phase_and_letter
    )


def with_sign(tensor, sign):
    scalar, letters = tensor
    return sign * scalar, letters


def check_operators(tensors, incident, signs, identity):
    for tensor in tensors:
        assert tensor[0] in (-1, 1), "non-Hermitian factor"
        assert times(tensor, tensor) == identity, "non-involution factor"
        assert any(tensor[1]), "one-eigenvalue factor"
    for knot, word in enumerate(incident):
        for a, b in combinations(word, 2):
            assert times(tensors[a], tensors[b]) == times(tensors[b], tensors[a]), "noncommuting held pair"
        answer = identity
        for distinction in word:
            answer = times(answer, tensors[distinction])
        assert answer == with_sign(identity, signs[knot]), f"wrong product at knot {knot}"


def check_positive(row, incident, neighbors):
    stored = row["pauli_i_phase_X_bits_Z_bits"]
    assert len(stored) == row["m"]
    width, tensors = tensor_reading(stored)
    identity = (1, (0,) * width)
    last = row["n"] - 1
    paths = path_search(neighbors, last)
    for destination, path in paths.items():
        transported = [with_sign(tensor, -1) if i in path else tensor for i, tensor in enumerate(tensors)]
        signs = [-1 if knot == destination else 1 for knot in range(row["n"])]
        check_operators(transported, incident, signs, identity)

    bad = [with_sign(tensors[0], -1), *tensors[1:]]
    try:
        check_operators(bad, incident, [1] * last + [-1], identity)
    except AssertionError as error:
        assert str(error).startswith("wrong product"), error
    else:
        raise AssertionError("single-factor sign change passed without transporting the target signs")
    return {"dimension": 2**width, "odd_positions": len(paths), "bad_factor_sign_rejected": True}


def rotate_first(word, distinction):
    assert word.count(distinction) == 1
    start = word.index(distinction)
    return word[start:] + word[:start]


def check_negative(row, certificate, incident, neighbors, odd):
    live = {}
    for knot, lookup in enumerate(neighbors):
        order = row["cyclic_orders"][str(knot)]
        word = [lookup[other] for other in order]
        assert sorted(word) == incident[knot], f"word differs from holders at knot {knot}"
        live[knot] = (word, -1 if knot == odd else 1)

    # If U V equals a scalar, then V U equals that scalar by conjugation
    # with U. This uses only invertibility, even for a merged word.
    for a, b, shared in certificate["merged"]:
        assert a != b and a in live and b in live
        word_a, sign_a = live.pop(a)
        word_b, sign_b = live.pop(b)
        first_a = rotate_first(word_a, shared)
        first_b = rotate_first(word_b, shared)
        # Put the identical factors at the boundary and cancel their square.
        live[a] = (first_a[1:] + first_b[1:], sign_a * sign_b)
    assert len(live) == 1
    word, sign = next(iter(live.values()))
    assert word == certificate["final_word"], "recorded final word differs from live equations"
    for index, distinction in certificate["removed_adjacent"]:
        assert (
            len(word) >= 2 and 0 <= index < len(word)
            and word[index] == word[(index + 1) % len(word)] == distinction
        ), (
            f"invalid adjacent square cancellation: {row['atlas']=}, "
            f"{index=}, {distinction=}, {word=}"
        )
        # The next offset is relative to the first factor after the pair.
        word = (word[index:] + word[:index])[2:]
    assert word == [], "replay did not reduce to the empty word"
    return sign


def check_row(row, refutations):
    incident, neighbors = incidence(row)
    identity = row["atlas"]
    if row["operator"]:
        outcome = check_positive(row, incident, neighbors)
    else:
        certificate = refutations[identity]
        for odd in range(row["n"]):
            assert check_negative(row, certificate, incident, neighbors, odd) == -1
        assert check_negative(row, certificate, incident, neighbors, None) == 1
        index, distinction = certificate["removed_adjacent"][0]
        bad = {
            **certificate,
            "removed_adjacent": [[index, distinction + row["m"]], *certificate["removed_adjacent"][1:]],
        }
        try:
            check_negative(row, bad, incident, neighbors, row["n"] - 1)
        except AssertionError as error:
            assert str(error).startswith("invalid adjacent square cancellation"), error
        else:
            raise AssertionError("corrupted adjacent cancellation passed")
        outcome = {
            "odd_positions": row["n"],
            "bad_adjacent_cancellation_rejected": True,
            "even_reduction_sign": 1,
        }
    return {
        "archive_id": identity, "knots": row["n"], "distinctions": row["m"],
        "operator": row["operator"], **outcome,
    }


def choose_representatives(census):
    rng = random.Random(SEED)
    return [
        rng.choice(stratum)
        for verdict in (True, False) for size in range(4, 8)
        if (stratum := [row for _, row in sorted(census.items()) if row["operator"] == verdict and row["n"] == size])
    ]


def main():
    if not __debug__:
        raise RuntimeError("certificate replay requires enabled assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("smoke", "sample", "full"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    binding = check_binding()
    census = indexed("census.json")
    refutations = indexed("arbitrary_operator_refutations.json")
    assert set(refutations) == {identity for identity, row in census.items() if not row["operator"]}
    sample = choose_representatives(census)
    if args.mode == "smoke":
        rows = [next(row for row in reversed(sample) if row["operator"]), sample[-1]]
    elif args.mode == "sample":
        rows = sample
    else:
        rows = list(census.values())
    evaluated = [check_row(row, refutations) for row in rows]
    record = {
        "mode": args.mode,
        "seed": SEED,
        "sample_rule": "one uniformly drawn archive type per nonempty knot-count and verdict group, sorted by archive identifier",
        "binding": binding,
        "positive": sum(row["operator"] for row in evaluated),
        "negative": sum(not row["operator"] for row in evaluated),
        "total_odd_positions": sum(row["odd_positions"] for row in evaluated),
        "positive_dimensions": dict(sorted(Counter(row["dimension"] for row in evaluated if row["operator"]).items())),
        "rows": evaluated,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    result = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.output:
        assert args.output.resolve().parent == Path(__file__).resolve().parent
        args.output.write_text(result)
    summary = {key: value for key, value in record.items() if key != "rows"}
    if args.mode != "full":
        summary["archive_ids"] = [row["archive_id"] for row in evaluated]
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
