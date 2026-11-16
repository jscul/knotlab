"""Check saved runs against parity counts and exhaustive one-bit encoders."""

from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TICKET = "STRAND-RETURN-20261114-001"
OUT = ROOT / "artifacts" / TICKET


def saved(suffix):
    path = OUT / (TICKET + suffix) / "results.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert all(row["status"] == "ok" for row in records)
    return {row["case"]: row["result"] for row in records}


def from_signs(signs, unary):
    if sum(signs) % 2:
        return 0
    if sum(signs[:len(signs) // 2]) % 2:
        return ((unary & 1) << 1) | (unary >> 1)
    return unary


def verify_lengths(record):
    for key, row in record["single_strands"]["lengths"].items():
        length = int(key)
        counts = Counter()
        for word in product((0, 1), repeat=length):
            observed = [value if i % 2 == 1 or i == length - 1 else 0
                        for i, value in enumerate(word)]
            for unary in range(4):
                counts["cases"] += 1
                counts["blind_correct"] += from_signs(word, unary) == from_signs(observed, unary)
        expected = dict(counts, one_correct=counts["cases"], two_correct=counts["cases"])
        assert row["tally"] == expected
    for schedule, result in record["steering"]["per_schedule"].items():
        assert result["exactly_wired_names"] == result["same_state_as_direct"] == 256 * 12
        assert result["link_reads"] == 2 * 8 * 256 * 12
        assert result["moves"] == result["link_reads"] // (2 if schedule == "alternating_two" else 1)
        assert result["queries"] == 55296 and result["correct"] == 54144


def verify_readout(row):
    # Build the unique inverse by indexing the forward point table. Derive both
    # future answers, then exhaust encoders; the producer enumerates decoders.
    mapping = {tuple(point["forward"]): tuple(point["input"]) for point in row["point_rows"]}
    states = sorted(mapping)
    signatures = [(int(u == 0), int(mapping[u, v][0] == 0)) for u, v in states]
    best = 0
    for messages in product(range(2), repeat=len(states)):
        counts = defaultdict(Counter)
        for message, signature in zip(messages, signatures):
            for query, value in enumerate(signature):
                counts[message, query][value] += 1
        best = max(best, sum(max(count.values()) for count in counts.values()))
    delayed = row["point_reader"]["choice_announced_after_encoding"]
    assert best == delayed["best_one_bit_individual_answers"]
    assert len(set(signatures)) == delayed["distinct_signatures"] == 4
    distinct = defaultdict(Counter)
    for presence in product((False, True), repeat=len(states)):
        allowed = [point for point, keep in zip(states, presence) if keep]
        marginal = tuple(frozenset(p[axis] for p in allowed) for axis in (0, 1))
        original = frozenset(mapping[p][0] for p in allowed)
        distinct[marginal][original] += 1
    relations = row["allowed_relations"]
    unique = sum(sum(c.values()) for c in distinct.values() if len(c) == 1)
    best_marginal = sum(max(c.values()) for c in distinct.values())
    assert unique == relations["subsets_where_marginals_uniquely_determine_old_x"]
    assert best_marginal == relations["best_possible_exact_old_x_count_from_marginals_uniform_subsets"]
    return {"best_one_bit_answers": best, "marginal_message_guaranteed_for": unique,
            "best_marginal_answer_count": best_marginal}


def main():
    cursor = saved("-E001_cursor_reduction")["closed-strands"]
    verify_lengths(cursor)
    braid = saved("-E002_braid_readers")
    verified = {name: verify_readout(braid[name]) for name in ("binary-signed-swap", "ternary-mixing")}
    print(json.dumps({"lengths_verified": sorted(map(int, cursor["single_strands"]["lengths"])),
                      "steering_schedules_verified": 3, "readouts_verified": verified}, indent=2))


if __name__ == "__main__":
    main()
