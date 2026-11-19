"""Trace exact rare paths for the plain uniform-child BK estimator."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import islice, takewhile
import json
from math import prod
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory

from parts import members, read_stage


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name


def mask_of(values):
    output = 0
    for value in values:
        output |= 1 << value
    return output


def closed_masks(size, blocks):
    rows = [0] * size
    for block in blocks:
        mask = mask_of(block)
        for v in block:
            rows[v] |= mask
    return tuple(row | (1 << v) for v, row in enumerate(rows))


@dataclass(frozen=True)
class Graph:
    adjacent: tuple
    order: tuple
    lift: tuple
    held_blocks: tuple

    @property
    def full(self):
        return (1 << len(self.order)) - 1

    def literal(self, bitset):
        return sorted(i for v in members(bitset) for i in self.lift[v])


def reorder(original_blocks, original_closed, quotient):
    """Same true-twin representatives and fixed stable ordering as estimate_bk.cpp."""
    twins = {}
    classes = {}
    for v, row in enumerate(original_closed):
        rep = twins.setdefault(row, v) if quotient else v
        classes.setdefault(rep, []).append(v)
    order = tuple(sorted(classes, key=lambda v: -original_closed[v].bit_count()))
    rank = {v: i for i, v in enumerate(order)}
    reduced = [tuple(sorted(rank[v] for v in block if v in rank)) for block in original_blocks]
    closed = closed_masks(len(order), reduced)
    adjacent = tuple(row ^ (1 << v) for v, row in enumerate(closed))
    return Graph(adjacent, order, tuple(classes[v] for v in order), tuple(map(mask_of, original_blocks)))


def greedy(graph, priority):
    chosen, remaining = 0, graph.full
    for v in priority:
        if remaining & (1 << v):
            chosen |= 1 << v
            remaining &= graph.adjacent[v]
        if not remaining:
            break
    assert not remaining
    return chosen


def guard_maximal(graph, target):
    closure = graph.full
    for v in members(target):
        closure &= graph.adjacent[v] | (1 << v)
    assert closure == target, "The named target is not a maximal clique"


def pivot_branches(graph, candidates, excluded, pool):
    best = candidates.bit_count() + 1
    pivot = None
    for available in (excluded, candidates):
        for x in islice(members(available), pool):
            misses = (candidates & ~graph.adjacent[x]).bit_count()
            if misses < best:
                best, pivot = misses, x
                if misses == 0:
                    return x, 0
    return pivot, candidates & ~graph.adjacent[pivot]


def strip_forced(graph, candidates, excluded, target):
    forced = 0
    count = 0
    for v in members(candidates):
        if not (candidates & ~(graph.adjacent[v] | (1 << v))):
            forced |= 1 << v
            excluded &= graph.adjacent[v]
            count += 1
            if count == 4096:
                break
    assert forced & target == forced
    return candidates ^ forced, excluded, forced


def trace(graph, target, *, pool, cutoff):
    """Route one maximal clique down the exact estimator tree up to its suffix."""
    guard_maximal(graph, target)
    current, excluded = graph.full, 0
    remaining = target
    product = 1
    steps = []
    while current.bit_count() > cutoff:
        assert remaining & current == remaining and not (remaining & excluded)
        pivot, branches = pivot_branches(graph, current, excluded, pool)
        assert branches, "A true target cannot follow a blocked branch"
        fanout = branches.bit_count()
        before = (current.bit_count(), excluded.bit_count())
        if fanout == 1 and before[0] > 8:
            next_p, next_x, forced = strip_forced(graph, current, excluded, remaining)
            if forced:
                steps.append({"P": before[0], "X": before[1], "pivot": pivot, "fanout": 1,
                              "forced": list(members(forced))})
                current, excluded = next_p, next_x
                remaining ^= forced
                continue
        options = branches & remaining
        assert options
        first = options & -options
        v = first.bit_length() - 1
        earlier = branches & (first - 1)
        steps.append({"P": before[0], "X": before[1], "pivot": pivot, "fanout": fanout,
                      "child": v, "child_rank": earlier.bit_count()})
        product *= fanout
        current = (current ^ earlier) & graph.adjacent[v]
        excluded = (excluded | earlier) & graph.adjacent[v]
        remaining ^= first
    assert not remaining & ~current and not remaining & excluded
    assert not any(remaining & ~graph.adjacent[x] == 0 for x in members(excluded))
    return product, steps, {"P": list(members(current)), "X": list(members(excluded)),
                            "target_remaining": list(members(remaining))}


def suffix_leaves(graph, target, suffix):
    """Brute-force the small exact suffix without following the pivot rule."""
    candidates = mask_of(suffix["P"])
    excluded = mask_of(suffix["X"])
    prefix = target ^ mask_of(suffix["target_remaining"])
    valid = leaves = 0
    sub = candidates
    while True:
        common = candidates | excluded
        for v in members(sub):
            common &= graph.adjacent[v] | (1 << v)
        if common == sub:
            leaves += 1
            lift = mask_of(graph.literal(prefix | sub))
            if lift.bit_count() >= 3 and not any(lift & b == lift for b in graph.held_blocks):
                valid += 1
        if not sub:
            return leaves, valid
        sub = (sub - 1) & candidates


NATIVE_DRIVER = r"""
#define main original_estimator_main
#include "estimate_bk.cpp"
#undef main

int main(int argc, char** argv) {
    if (argc != 5) return 1;
    std::mt19937_64 rng(0);
    Graph graph(argv[1], std::stoi(argv[2]) != 0, false, rng);
    const int cutoff = std::stoi(argv[4]);
    Search search{graph, std::stoi(argv[3]), cutoff, rng, {}, {}, false, 0};
    Mask p(graph.width), x(graph.width), target(graph.width);
    for (int v = 0; v < graph.size; ++v) set(p, v);
    for (int v; std::cin >> v;) {
        if (v < 0 || v >= graph.size) return 2;
        set(target, v);
    }
    std::cout << graph.size << '\n';
    while (popcount(p) > cutoff) {
        auto branches = search.children(p, x);
        if (branches.empty()) return 3;
        std::cout << popcount(p) << ' ' << popcount(x) << ' ' << branches.size();
        if (branches.size() == 1 && popcount(p) > 8) {
            Mask old = p;
            if (search.strip_forced(p, x, 4096)) {
                std::cout << " -1 -1";
                for (int w = 0; w < graph.width; ++w) {
                    old[w] ^= p[w];
                    if (old[w] & ~target[w]) return 4;
                    target[w] ^= old[w];
                }
                for_each(old, [](int v) { std::cout << ' ' << v; });
                std::cout << '\n';
                continue;
            }
        }
        int rank = 0, selected = -1;
        for (const auto v : branches) {
            if (target[v / 64] >> (v % 64) & 1) {
                selected = v;
                break;
            }
            erase(p, v);
            set(x, v);
            ++rank;
        }
        if (selected < 0) return 5;
        std::cout << ' ' << selected << ' ' << rank << '\n';
        for (int w = 0; w < graph.width; ++w) {
            p[w] &= graph.adjacent[selected][w];
            x[w] &= graph.adjacent[selected][w];
        }
        erase(target, selected);
    }
    for (const auto* mask : {&p, &x, &target}) {
        for_each(*mask, [](int v) { std::cout << ' ' << v; });
        std::cout << '\n';
    }
}
"""


def native_replay(binary, stage, quotient, pool, cutoff, size, target, steps, suffix):
    replay = subprocess.run([binary, stage, str(int(quotient)), str(pool), str(cutoff)],
                            input=" ".join(map(str, target)) + "\n", text=True,
                            capture_output=True, check=True)
    recorded = [list(map(int, line.split())) for line in replay.stdout.splitlines()]
    expected = [[size]]
    for row in steps:
        expected.append([row["P"], row["X"], row["fanout"], row.get("child", -1), row.get("child_rank", -1),
                         *row.get("forced", ())])
    expected.extend(suffix[k] for k in ("P", "X", "target_remaining"))
    assert recorded == expected, "Native estimator and Python path disagree"


def tiny_control():
    """Brute-force the maximal cliques and independently enumerate all routes."""
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    graph = reorder(edges, closed_masks(5, edges), False)
    subsets = [frozenset(members(q)) for q in range(1, 1 << 5)]
    cliques = [q for q in subsets if all((graph.adjacent[u] | (1 << u)) & mask_of(q) == mask_of(q) for u in q)]
    maximal = {q for q in cliques if not any(q < other for other in cliques)}
    assert maximal == set(map(frozenset, edges))
    neighbors = [set(members(row)) for row in graph.adjacent]

    def distribution(chosen, possible, shelved, probability, cutoff):
        if len(possible) <= cutoff:
            suffix_count = sum(chosen <= q <= chosen | possible for q in maximal)
            yield probability, suffix_count / probability
            return
        available = sorted(shelved)[:2] + sorted(possible)[:2]
        pivot = min(available, key=lambda v: len(possible - neighbors[v]))
        branches = sorted(possible - neighbors[pivot])
        if not branches:
            yield probability, Fraction(0)
            return
        for v in branches:
            yield from distribution(chosen | {v}, possible & neighbors[v], shelved & neighbors[v],
                                    probability / len(branches), cutoff)
            possible.remove(v)
            shelved.add(v)

    output = {}
    for cutoff in (0, 2):
        logs = list(distribution(set(), set(range(5)), set(), Fraction(1), cutoff))
        mean = sum(p * z for p, z in logs)
        second = sum(p * z * z for p, z in logs)
        assert sum(p for p, _ in logs) == 1 and mean == 5
        weights = [trace(graph, mask_of(q), pool=2, cutoff=cutoff)[0] for q in maximal]
        assert second >= max(weights)
        if cutoff == 0:
            assert second == sum(weights)
        output[str(cutoff)] = {"terminal_events": len(logs), "mean": str(mean), "second_moment": str(second),
                               "inverse_probabilities_to_targets": sorted(weights)}
    return {"graph": "cycle on five vertices", "maximal_cliques_by_powerset": len(maximal), "cutoffs": output}


def draws_bound(second_moment, mean_upper, rms):
    mean_squared = mean_upper**2
    denominator = rms**2 * mean_squared
    return max(0, (second_moment - mean_squared + denominator - 1) // denominator)


def record(stage, binary, configurations):
    n, blocks, _, original = read_stage(stage)
    closed = tuple(row | (1 << i) for i, row in enumerate(original))
    del original
    results = []
    for quotient, pools in configurations:
        graph = reorder(blocks, closed, quotient)
        target = greedy(graph, range(len(graph.order)))
        literal = graph.literal(target)
        target_names = list(members(target))
        literal_mask = mask_of(literal)
        held = any(literal_mask & block == literal_mask for block in graph.held_blocks)
        for pool in pools:
            cutoff = 10
            weight, steps, suffix = trace(graph, target, pool=pool, cutoff=cutoff)
            native_replay(binary, stage, quotient, pool, cutoff, len(graph.order), target_names, steps, suffix)
            leaves, free = suffix_leaves(graph, target, suffix)
            assert leaves >= 1 and (held or free >= 1)
            prefix_bound = weight * leaves**2
            positive_bound = weight * free**2
            cut_sizes = [{"T_at_most_10_to": exponent,
                          "minimum_draws_for_relative_rms_at_most_one": str(draws_bound(prefix_bound, 10**exponent, 1)),
                          "minimum_draws_for_relative_rms_at_most_nine": str(draws_bound(prefix_bound, 10**exponent, 9))}
                         for exponent in (10, 18, 50, 100, 150)]
            earlier = [{"exact_cutoff": wide, "inverse_prefix_probability": str(prod(
                row["fanout"] for row in takewhile(lambda row: row["P"] > wide, steps)))}
                       for wide in (32, 128, 512, 4096, 8192)]
            results.append({"quotient": quotient, "graph_order": len(graph.order), "pivot_pool": pool,
                            "exact_cutoff": cutoff, "target_held": held, "target_literal_names": literal,
                            "target_estimator_indices": target_names, "path": steps, "exact_suffix": suffix,
                            "inverse_prefix_probability": str(weight), "factor_decimal_digits": len(str(weight)),
                            "prefix_probability_is_exact": True, "native_replay": True,
                            "nontrivial_draws": sum(s["fanout"] > 1 for s in steps),
                            "suffix_maximal_cliques": leaves, "suffix_unheld_groups": free,
                            "lower_second_moment_count_all": str(prefix_bound),
                            "lower_second_moment_count_unheld": str(positive_bound),
                            "earlier_exact_cutoffs": earlier, "conditional_rms_thresholds": cut_sizes})
    return {"source_name": stage.name, "sha256": sha256(stage.read_bytes()).hexdigest(),
            "literal_order": n, "block_count": len(blocks), "configurations": results}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("stage_directory", type=Path)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "path_risk.json")
    args = parser.parse_args()
    control = tiny_control()
    estimator = (HERE / "estimate_bk.cpp").read_bytes()
    with TemporaryDirectory(prefix="prespatial-path-risk-") as scratch:
        (Path(scratch) / "estimate_bk.cpp").write_bytes(estimator)
        driver = Path(scratch) / "driver.cpp"
        driver.write_text(NATIVE_DRIVER)
        binary = Path(scratch) / "driver"
        subprocess.run(["c++", "-std=c++20", "-O3", "-Wno-return-type", "-I", str(HERE),
                        str(driver), "-o", str(binary)], check=True)
        eight = record(args.stage_directory / "age8.txt", binary, ((True, (24, 64)), (False, (128,))))
        seven = record(args.stage_directory / "age7.txt", binary, ((False, (24,)),))
    assert (eight["literal_order"], eight["block_count"]) == (28065, 365)
    assert (seven["literal_order"], seven["block_count"]) == (386, 105)
    payload = {"proposal": "uniform children, fixed original degree order, no component factoring or rank bias",
               "estimator_sha256": sha256(estimator).hexdigest(),
               "age8": eight, "age7": seven, "tiny_control": control}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent,
                            prefix="path_risk_pending_", delete=False) as pending:
        json.dump(payload, pending, separators=(",", ":"))
        pending.write("\n")
    Path(pending.name).replace(args.output)
    print(json.dumps({"age8": [{k: r[k] for k in ("quotient", "pivot_pool", "factor_decimal_digits",
                                                  "nontrivial_draws", "suffix_maximal_cliques",
                                                  "suffix_unheld_groups")} for r in eight["configurations"]],
                      "tiny_control": control}, sort_keys=True))


if __name__ == "__main__":
    main()
