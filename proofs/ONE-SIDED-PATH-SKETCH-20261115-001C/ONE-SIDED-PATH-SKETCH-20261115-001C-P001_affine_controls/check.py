"""Replay small conditional trees, exhaustive minimax thresholds, and model-preserving affine restrictions."""

from collections import Counter
import json
from pathlib import Path
from shutil import which
import subprocess
from tempfile import TemporaryDirectory

import solver as S

HERE = Path(__file__).resolve().parent


def run_tables(executable, inputs, budget, tables):
    table_list = list(tables)
    completed = subprocess.run([executable, "tables", str(inputs), str(budget)], check=True,
                               input="".join(f"{t}\n" for t in table_list), text=True, capture_output=True)
    results = [tuple(map(int, l.split())) for l in completed.stdout.splitlines()]
    S.require([t for t, _ in results] == table_list and all(ok == 0 for _, ok in results),
              "finite lower threshold was incomplete or an alleged lower bound failed")
    return len(results)


def fibre_subset_audit():
    n, size = 4, 16
    points = frozenset(range(2 * size))
    left = frozenset(p for p in points if S.checksum(p & 15) == p >> n)
    opposite = [x | ((1 ^ S.checksum(x)) << n) for x in range(size)]
    stats = Counter()
    for code in range(1 << size):
        right = frozenset(p for x, p in enumerate(opposite) if code >> x & 1)
        graph = S.affine_hull(right)
        t = frozenset(p & 15 for p in graph)
        if not graph:
            reason = "empty"
            predicted_live = False
        elif len(t) < len(graph):
            reason = "free_checksum"
            predicted_live = True
        else:
            left_x = frozenset(p & 15 for p in graph & left)
            predicted_live = S.affine_hull(left_x) == t
            reason = "affine_spanning_opposite" if predicted_live else "affine_deficient_opposite"
        cell = points
        while cell:
            nxt = S.affine_hull(cell & left) & S.affine_hull(cell & right)
            if nxt == cell:
                break
            cell = nxt
        S.require(bool(cell) == predicted_live and (not cell or cell == graph),
                  "raw fibre saturation disagrees with the quadratic level criterion")
        stats[reason] += 1
    S.require(sum(stats.values()) == 65536, "incomplete arbitrary right-subset control")
    return dict(stats)


def main():
    classes4 = S.arbitrary_four_tables()
    sketches6, orbit_sizes = S.quadratic_six_classes()
    S.require(orbit_sizes == [1, 336, 315, 5040, 4032, 3780, 2880], "changed polar orbit census")
    even8 = sum(S.parity(x & (x >> 1) & 42) << x for x in range(256))
    cubic = sum(int(not (((x & 1) ^ ((x >> 2) & 1)) |
                          (((x >> 2) & 1) ^ ((x >> 4) & 1)) | ((x >> 4) & 1))) << x for x in range(64))
    fixtures = json.loads((HERE / "trees.json").read_text())
    replay = {}
    for name, item in fixtures.items():
        n, charge = item["original_bits"], item["fixed_b"]
        truth = even8 if n == 8 else cubic
        actual = S.audit_tree(n, truth, item["tree"], charge)
        S.require(list(actual) == item["leaves_depth"], f"tree mismatch for {name}")
        replay[name] = list(actual)
    compiler = which("g++") or which("c++")
    S.require(compiler, "a C++20 compiler is required")
    shallow = {}
    with TemporaryDirectory(prefix="one-sided-controls-") as tmp:
        binary = str(Path(tmp) / "minimax")
        subprocess.run([compiler, "-O3", "-std=c++20", "-march=native", str(HERE / "minimax.cpp"), "-o", binary],
                       check=True)
        a = run_tables(binary, 4, 3, classes4)
        b = run_tables(binary, 6, 7, sketches6)
        run_tables(binary, 6, 7, [cubic])
        for fixed, budget, counts in [(0, 8, [173740, 0, 0]), (1, 6, [173740, 7, 476])]:
            out = subprocess.run([binary, "fiber", str(fixed), str(budget)], check=True,
                                 text=True, capture_output=True).stdout
            total, empty, live_changed, accepted = map(int, out.split())
            S.require([total, empty, live_changed] == counts and not accepted, "incorrect exhaustive fibre budget")
            shallow[str(fixed)] = {"codimension_two": total, "empty": empty, "changed_live": live_changed,
                                   "excluded_leaves": budget}
    forms = S.embedding_audit()
    rank_trace = S.transfer_checks()
    constructive_maps = S.rank_nine_maps()
    subsets = fibre_subset_audit()
    print(json.dumps({"status": "passed", "arbitrary_four_bit_tables": 65536, "four_bit_representatives": a,
                      "four_bit_arbitrary_optimum": 4, "six_bit_boolean_quadratics": 1 << 22,
                      "six_bit_normalized_polars": 1 << 14, "six_bit_representatives": b,
                      "six_bit_polar_orbit_sizes": orbit_sizes, "six_bit_quadratic_optimum": 8,
                      "nonquadratic_zero_indicator_truth": cubic, "nonquadratic_zero_indicator_optimum": 8,
                      "raw_subset_fibre_classification": subsets, "seven_edge_even_first_bit": [9, 7],
                      "seven_edge_even_full_leaves_depth": [16, 4], "seven_edge_first_form_classes": forms,
                      "seven_edge_root_b_fibres": shallow, "even_sketch_optima_through_eight_edges": [2,2,4,4,8,8,16,16],
                      "conditional_trees": replay, "31_edge_ranks_Q_A_QplusA_B_QplusB": rank_trace,
                      "canonical_17_edge_restriction": True, "17_to_7_affine_prefix_cases": 32,
                      "constructive_rank_nine_restrictions": constructive_maps,
                      "17_edge_prefix_strategy_leaves": 512, "radical_affine_normalization_checked": True},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
