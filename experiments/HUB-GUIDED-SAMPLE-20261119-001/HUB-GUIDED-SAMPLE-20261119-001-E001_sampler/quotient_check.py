"""Independently count the candidate graph's maximal cliques for starts 09, 10, 11."""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
import subprocess
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
TARGETS = (
    ("start-09", 6, 55_000_000),
    ("start-10", 7, 6_000_000),
    ("start-11", 7, 5_000_000),
)


def encode(n, blocks):
    return (f"{n} {len(blocks)}\n" + "".join(" ".join(map(str, row)) + "\n" for row in blocks)).encode()


def decode(data):
    header, *rest = data.splitlines()
    n, b = map(int, header.split())
    blocks = [tuple(map(int, row.split())) for row in rest]
    assert len(blocks) == b
    assert all(len(b) >= 2 and len(set(b)) == len(b) and all(0 <= v < n for v in b) for b in blocks)
    return n, blocks


def native(binary, data, cap):
    result = subprocess.run([binary, str(cap)], input=data, check=True, capture_output=True)
    size, leaves, calls, complete = map(int, result.stdout.split())
    assert 0 <= leaves <= calls <= cap and complete in (0, 1)
    assert complete or calls == cap
    return size, leaves, calls, bool(complete)


def literal_graph(blocks):
    return {pair for block in blocks for pair in combinations(sorted(block), 2)}


def brute(n, edges):
    # Check each literal subset for compatibility and each omitted point for extension.
    neighbor = [{v} for v in range(n)]
    for u, v in edges:
        neighbor[u].add(v)
        neighbor[v].add(u)
    twin_classes = len({frozenset(row) for row in neighbor})
    maxima = 0
    for bits in range(1, 1 << n):
        chosen = {v for v in range(n) if bits >> v & 1}
        compatible = set.intersection(*(neighbor[v] for v in chosen))
        maxima += compatible == chosen
    return twin_classes, maxima


def validate(binary):
    def check(n, blocks):
        reference = brute(n, literal_graph(blocks))
        q, leaves, _, complete = native(binary, encode(n, blocks), 100_000)
        assert complete and (q, leaves) == reference, (n, blocks, q, leaves, reference)

    graph_count = 0
    for n in range(1, 6):
        possible = list(combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            check(n, [pair for bit, pair in enumerate(possible) if mask >> bit & 1])
            graph_count += 1

    seed = 871_4639
    rng = Random(seed)
    hypergraph_count = 0
    for n in range(6, 11):
        for _ in range(64):
            blocks = {
                frozenset(rng.sample(range(n), rng.randint(2, n)))
                for _ in range(rng.randrange(2 * n))
            }
            maximal = sorted(tuple(sorted(b)) for b in blocks if not any(b < c for c in blocks))
            check(n, maximal)
            hypergraph_count += 1

    partial = native(binary, encode(3, []), 2)
    assert partial == (3, 1, 2, False)
    return {"labelled_graphs_exhausted_on_1_to_5_vertices": graph_count,
            "hypergraphs_sampled_on_6_to_10_vertices": hypergraph_count,
            "hypergraph_seed": seed, "partial_edgeless_graph": partial}


def structural_counts(n, blocks):
    rows = [1 << v for v in range(n)]
    encoded_blocks = [sum(1 << v for v in block) for block in blocks]
    for block, mask in zip(blocks, encoded_blocks):
        for v in block:
            rows[v] |= mask
    full = (1 << n) - 1
    held = 0
    for block, mask in zip(blocks, encoded_blocks):
        extensions = full ^ mask
        for v in block:
            extensions &= rows[v]
            if not extensions:
                break
        held += extensions == 0

    remaining = full
    component_sizes = []
    while remaining:
        explore = remaining & -remaining
        remaining ^= explore
        discovered = 0
        while explore:
            bit = explore & -explore
            explore ^= bit
            new = remaining & ~rows[bit.bit_length() - 1]
            explore |= new
            remaining ^= new
            discovered += 1
        component_sizes.append(discovered)
    return rows, held, sorted(component_sizes, reverse=True)


def score(binary, input_dir, stage, cap):
    file = stage["files"]["blocks"]
    data = (input_dir / file["name"]).read_bytes()
    assert sha256(data).hexdigest() == file["sha256"]
    n, blocks = decode(data)
    assert (n, len(blocks)) == (stage["live"], stage["blocks"])
    q, leaves, calls, complete = native(binary, data, cap)
    rows, held, components = structural_counts(n, blocks)
    assert q == len(set(rows))
    isolated = sum(row.bit_count() == 1 for row in rows)
    candidates = sum(row.bit_count() - 1 for row in rows) // 2
    assert (isolated, candidates) == (stage["isolated"], stage["candidate_pairs"])

    case = stage["case"]
    cover_path = ARTIFACTS / f"cover_pairs{case[-2:]}.json"
    cover_data = cover_path.read_bytes()
    cover = json.loads(cover_data)
    assert (cover["live"], cover["inspected_candidate_pairs"]) == (n, candidates)
    residuals = {tuple(pair) for pair in cover["pairs"]}
    assert len(residuals) == len(cover["pairs"]) == cover["residual_pairs"]
    assert all(0 <= u < v < n and rows[u] >> v & 1 for u, v in residuals)
    offshoots = stage["exact_offshoots"]
    # The residual count comes from the separate exhaustive covering-group receipt.
    births = leaves - held - isolated + offshoots + len(residuals)
    return {"case": case, "age": stage["age"], "birth_round": stage["target_round"],
            "blocks_file": file, "live": n, "closed_neighborhood_classes": q,
            "literal_conflict_components": components, "candidate_pairs": candidates,
            "node_limit": cap, "visited_nodes": calls, "complete": complete,
            "counted_candidate_maxima": leaves,
            "held_maxima": held, "isolated_maxima": isolated, "offshoots": offshoots,
            "residual_pairs": len(residuals), "residual_receipt": cover_path.name,
            "residual_receipt_sha256": sha256(cover_data).hexdigest(),
            "births" if complete else "births_lower_bound": births}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="directory of literal block rosters exported by stages.py")
    args = parser.parse_args()
    manifest = json.loads((ARTIFACTS / "stages.json").read_text())
    stages = {(row["case"], row["age"]): row for row in manifest["stages"]}
    source = HERE / "quotient_check.cpp"
    with TemporaryDirectory(prefix="hub-quotient-check-") as work:
        executable = Path(work) / "count"
        subprocess.run(["c++", "-O3", "-march=native", "-std=c++20", "-Wall", "-Wextra",
                        source, "-o", executable], check=True)
        controls = validate(executable)
        rows = [score(executable, args.input_dir, stages[case, age], cap) for case, age, cap in TARGETS]
    result = {"method": "Closed-neighborhood true-twin quotient followed by exact pivoted maximal clique count.",
              "count_source_sha256": sha256(source.read_bytes()).hexdigest(),
              "controls": controls, "targets": rows}
    (ARTIFACTS / "quotient_check.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for row in rows:
        print(row["case"], row["age"], row["counted_candidate_maxima"], row["complete"],
              row.get("births", row.get("births_lower_bound")))


if __name__ == "__main__":
    main()
