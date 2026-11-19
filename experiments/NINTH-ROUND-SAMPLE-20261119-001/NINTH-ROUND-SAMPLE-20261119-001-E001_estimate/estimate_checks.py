"""Cross-check the sampler's exact kernels on finite, independently counted inputs."""

import argparse
import itertools
import json
import random
import statistics
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path


def blocks_file(path, n, blocks):
    path.write_text(f"{n} {len(blocks)}\n" + "".join(" ".join(map(str, block)) + "\n" for block in blocks))


def brute_count(n, pairs):
    count = 0
    for mask in range(1, 1 << n):
        inside = [v for v in range(n) if mask & (1 << v)]
        outside = [v for v in range(n) if not mask & (1 << v)]
        if any(pair not in pairs for pair in itertools.combinations(inside, 2)):
            continue
        if any(all(tuple(sorted((a, b))) in pairs for a in inside) for b in outside):
            continue
        count += 1
    return count


def measure(executable, blocks, *options):
    running = subprocess.run((str(executable), str(blocks), *map(str, options)),
                             capture_output=True, text=True, check=True)
    return [json.loads(line) for line in running.stdout.splitlines()[1:]]


def check_synthetic(executable, scratch):
    path = scratch / "small.txt"
    rng = random.Random(20261119094)
    graphs = []
    for n in (7, 8, 10, 12):
        universe = set(itertools.combinations(range(n), 2))
        graphs.append((n, set()))
        graphs.append((n, universe))
        graphs.append((n, {pair for pair in universe if pair[0] // 2 != pair[1] // 2}))
        for probability in (.05, .25, .55, .9):
            for _ in range(4):
                graphs.append((n, {pair for pair in sorted(universe) if rng.random() < probability}))
    factor_runs = 0
    exhaustive_runs = 0
    for i, (n, pairs) in enumerate(graphs):
        blocks_file(path, n, sorted(pairs))
        exact = brute_count(n, pairs)
        runs = [
            measure(executable, path, 0, i, 3, 0, 0, 0)[0],
            measure(executable, path, 0, i, 4, 0, 1, 1)[0],
            measure(executable, path, 1, i, 4, 2, 1, 1, 1, 1, 4096, .5, n)[0],
        ]
        for report in runs:
            if Decimal(report["weight"]) != exact:
                raise AssertionError((n, i, exact, report))
            if report["generated"] != report["retained"]:
                raise AssertionError("exact synthetic control sampled a branch")
            exhaustive_runs += 1
            factor_runs += bool(report["component_splits"])
    if not factor_runs:
        raise AssertionError("synthetic controls did not exercise component factorization")

    n = 12
    pairs = {pair for pair in itertools.combinations(range(n), 2) if pair[0] // 2 != pair[1] // 2}
    blocks_file(path, n, sorted(pairs))
    exact = brute_count(n, pairs)
    samples = measure(executable, path, 4096, 20261119140, 4, 2, 1, 0, 1, 0, 4, .5)
    weights = [float(result["weight"]) for result in samples]
    if not any(result["generated"] > result["retained"] for result in samples):
        raise AssertionError("the random synthetic control never resampled")
    return {
        "distinct_exact_graphs": len(graphs),
        "exact_replays": exhaustive_runs,
        "exact_replays_with_component_splits": factor_runs,
        "sampled_control_truth": exact,
        "sampled_control_replicates": len(samples),
        "sampled_control_mean": statistics.fmean(weights),
        "sampled_control_mc_standard_error": statistics.stdev(weights) / len(samples) ** .5,
    }


def check_stages(executable, stages):
    import networkx as nx

    out = {}
    for age in (5, 6, 7):
        path = stages / f"age{age}.txt"
        lines = path.read_text().splitlines()
        n, _ = map(int, lines[0].split())
        blocks = [list(map(int, line.split())) for line in lines[1:]]
        graph = nx.Graph()
        graph.add_nodes_from(range(n))
        for block in blocks:
            graph.add_edges_from(itertools.combinations(block, 2))
        exact = sum(1 for _ in nx.find_cliques(graph))
        report = measure(executable, path, 0, 20261119094, 24, 10, 1, 0)[0]
        if Decimal(report["weight"]) != exact:
            raise AssertionError((age, exact, report))
        out[age] = {"networkx_count": exact, "estimate_bk": report}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("stages", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="estimate-check-", dir=args.stages) as scratch:
        synthetic = check_synthetic(args.executable, Path(scratch))
    print(json.dumps({"synthetic": synthetic, "stages": check_stages(args.executable, args.stages)}, indent=2))


if __name__ == "__main__":
    main()
