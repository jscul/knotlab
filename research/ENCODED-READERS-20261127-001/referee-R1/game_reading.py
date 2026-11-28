"""Compare the operational reading on three marked fewest words under one question weighting."""

from collections import Counter
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / "READER-SPLIT-20261127-001" / "referee-R1"


def compare(supports, pairs):
    # As in the earlier certificate, choose one X and one Z per reader.
    questions = []
    for knot, support in enumerate(supports):
        x = sum(1 << i for i, (a, _) in enumerate(pairs) if a in support)
        z = sum(1 << i for i, (_, b) in enumerate(pairs) if b in support)
        assert not (x & z)
        if x or z:
            questions.append((knot, x, z))
    masks = [x | (z << len(pairs)) for _, x, z in questions]
    targets = [int(i == 0) for i in range(len(questions))]
    best = max(sum((answers & mask).bit_count() % 2 == target
                   for mask, target in zip(masks, targets))
               for answers in range(1 << (2 * len(pairs))))
    # Trace of product of the commuting signed projectors. Expand exactly
    # on computational basis states, including every subset of checks.
    assert all(((x & v).bit_count() + (z & u).bit_count()) % 2 == 0
               for _, x, z in questions for _, u, v in questions)
    trace_sum = 0
    for subset in range(1 << len(questions)):
        for start in range(1 << len(pairs)):
            state, sign = start, 0
            for i, (_, x, z) in enumerate(questions):
                if subset & (1 << i):
                    sign ^= ((z & state).bit_count() % 2) ^ targets[i]
                    state ^= x
            if state == start:
                trace_sum += (-1) ** sign
    dimension, remainder = divmod(trace_sum, 1 << len(questions))
    assert not remainder and dimension > 0
    return {"pairs": pairs, "questions": [k for k, _, _ in questions], "best_fixed_list": best,
            "question_count": len(questions), "winning_subspace_dimension": dimension}


def main():
    keys = (17, 786, 6171)
    def records(filename):
        return {r["key"]: r for r in map(json.loads, (PRIOR / filename).open())
                if r["population"] == "birth" and r["key"] in keys}
    inputs = records("rebuilt_inputs.jsonl")
    prior = records("split_rows.jsonl")
    by_start = {k: compare(inputs[k]["supports"], prior[k]["strict_witness"]["failing_pairs"]) for k in keys}
    result = {"weighting": "equal weight per knot holding at least one reader setting",
              "target": "negative at the first active knot, positive at all others, outside signs positive",
              "construction": "one reader bit per failing pair, first setting X, second Z",
              "witness_source": "one independently checked fewest word per named grown closure",
              "by_census_start": by_start}
    words_by_c = Counter()
    starts_by_c = Counter()
    mixed = []
    with gzip.open(HERE / "choices.jsonl.gz", "rt") as stream:
        for row in map(json.loads, stream):
            if row["population"] != "closure" or not row["words"]:
                continue
            offsets = set()
            for word, minimal in row["words"]:
                if len(word) != row["fewest"]:
                    continue
                assert minimal
                marked = {d for i in word for d in row["pairs"][i]}
                k = sum(not marked.isdisjoint(support) for support in row["supports"])
                c = k - len(word)
                offsets.add(c)
                words_by_c[c] += 1
            starts_by_c[",".join(map(str, sorted(offsets)))] += 1
            if len(offsets) > 1:
                mixed.append(row["id"])
    result["fewest_labelled_words_by_c"] = words_by_c
    result["census_starts_by_set_of_c_values"] = starts_by_c
    result["census_starts_with_mixed_c"] = mixed
    (HERE / "game_reading.json").write_text(json.dumps(result, indent=1) + "\n")
    print([(k, r["best_fixed_list"], r["question_count"], r["winning_subspace_dimension"])
           for k, r in by_start.items()])


if __name__ == "__main__":
    main()
