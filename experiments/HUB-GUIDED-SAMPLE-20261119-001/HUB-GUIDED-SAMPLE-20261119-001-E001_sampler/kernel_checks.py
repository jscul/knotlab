"""Independent finite controls for exact and sampled binary partitions."""

import argparse
import itertools
import json
import random
import statistics
import subprocess
import tempfile
from pathlib import Path


def emit(path, n, blocks):
    path.write_text(
        f"{n} {len(blocks)}\n"
        + "".join(" ".join(str(v) for v in block) + "\n" for block in blocks)
    )


def count_by_subsets(n, blocks):
    compatible = [1 << v for v in range(n)]
    for block in blocks:
        words = sum(1 << v for v in block)
        for v in block:
            compatible[v] |= words
    full = (1 << n) - 1
    total = 0
    for chosen in range(1, full + 1):
        candidates = full
        remaining = chosen
        while remaining:
            bit = remaining & -remaining
            candidates &= compatible[bit.bit_length() - 1]
            remaining ^= bit
        total += candidates == chosen
    return total


def run(kernel, path, samples, seed, width, policy, order, local, factor, quotient):
    command = (kernel, path, samples, seed, width, policy, order, 32, local, factor, 16, quotient)
    result = subprocess.run(tuple(map(str, command)), check=True, capture_output=True, text=True)
    header, *rows = map(json.loads, result.stdout.splitlines())
    if len(rows) != samples or header["first_seed"] != seed:
        raise AssertionError(result.stdout)
    return rows


def small_cases(kernel, scratch):
    rng = random.Random(202611197100)
    configurations = (
        ("partner", "coverage", 22, 1024, 1),
        ("hub", "shuffle", 3, 1024, 0),
        ("block", "coverage", 0, 0, 1),
        ("block", "reverse", 5, 1024, 1),
    )
    cases = [
        (6, [(0, 1, 2), (0, 1, 3), (2, 4), (3, 5)]),
        (10, [(i, j) for i, j in itertools.combinations(range(10), 2) if j - i not in (1, 9)]),
        (12, [(i, j) for i, j in itertools.combinations(range(12), 2) if j - i != 1]),
        (13, [tuple(range(10)), (8, 10, 11), (7, 11, 12), (9, 10, 12), (0, 11)]),
    ]
    for n in (5, 8, 10, 12):
        pairs = list(itertools.combinations(range(n), 2))
        for probability in (0.0, .15, .35, .65, .85, 1.0):
            cases.extend((n, [pair for pair in pairs if rng.random() < probability]) for _ in range(4))
    path = scratch / "small.txt"
    events = {}
    for index, (n, blocks) in enumerate(cases):
        expected = count_by_subsets(n, blocks)
        emit(path, n, blocks)
        for configuration in configurations:
            row, = run(kernel, path, 1, 202611197100 + index, 4096, *configuration)
            if row["merges"] or int(row["weight"]) != expected:
                raise AssertionError((n, blocks, configuration, expected, row))
            for name in ("forced", "components", "local_twins", "local_forests", "local_bipartite", "block_fringe"):
                events[name] = events.get(name, 0) + row.get(name, 0)
    if not all(events.values()):
        raise AssertionError(events)
    return {"inputs": len(cases), "exact_replays": len(cases) * len(configurations), "events": events}


def many_partner_pairs(kernel, scratch):
    n = 280
    path = scratch / "partner140.txt"
    emit(path, n, [(a, b) for a, b in itertools.combinations(range(n), 2) if a // 2 != b // 2])
    expected = 2 ** (n // 2)
    exact, = run(kernel, path, 1, 202611197210, 1, "partner", "coverage", 18, 512, 0)
    merged, = run(kernel, path, 1, 202611197211, 1, "partner", "coverage", 0, 0, 0)
    if int(exact["weight"]) != expected or int(merged["weight"]) != expected:
        raise AssertionError((expected, exact, merged))
    if exact["merges"] or int(merged["largest_terminal_mass"]) <= 2 ** 64:
        raise AssertionError((exact, merged))
    return {"truth": str(expected), "exact": exact, "merged": merged}


def sampled_case(kernel, scratch):
    n = 14
    path = scratch / "sampled.txt"
    rng = random.Random(202611197220)
    pairs = [pair for pair in itertools.combinations(range(n), 2) if rng.random() < .72]
    emit(path, n, pairs)
    expected = count_by_subsets(n, pairs)
    rows = run(kernel, path, 4096, 202611192000, 2, "partner", "coverage", 3, 0, 0)
    merged = sum(row["merges"] for row in rows)
    if not merged:
        raise AssertionError("sampled control did not merge")
    values = [int(row["weight"]) for row in rows]
    return {"truth": expected, "runs": len(rows), "mean": statistics.fmean(values),
            "empirical_standard_error": statistics.stdev(values) / len(rows) ** .5, "merges": merged}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernel", type=Path)
    parser.add_argument("scratch", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(dir=args.scratch, prefix="kernel-controls-") as directory:
        path = Path(directory)
        output = {
            "small_cases": small_cases(args.kernel, path),
            "arbitrary_precision": many_partner_pairs(args.kernel, path),
            "sampled_control": sampled_case(args.kernel, path),
        }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
