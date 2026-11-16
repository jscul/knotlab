"""Replay the exact leaf threshold and audit the explicit trees on the original bits."""

import json
import os
import platform
import subprocess
import tempfile
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR_TICKET = "ONE-SIDED-PATH-SKETCH-20261115-001C"
PRIOR = HERE.parents[1] / PRIOR_TICKET / (PRIOR_TICKET + "-P001_affine_controls")
spec = spec_from_file_location("accepted_one_sided_helpers", PRIOR / "solver.py")
prior = module_from_spec(spec)
spec.loader.exec_module(prior)
affine_hull = prior.affine_hull


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(value):
    return value.bit_count() % 2


def raw_products(x, m):
    return sum((int((x >> i & 3) == 3) << i) for i in range(m))


def raw_relations(m, sketches, charge=1):
    n = m + 1
    visible = frozenset(range(1 << (n + 1 + len(sketches))))
    left, right = set(), set()
    for x in range(1 << n):
        outputs = raw_products(x, m)
        checksum = parity(outputs)
        reported = sum(parity(outputs & mask) << j for j, mask in enumerate(sketches))
        left.add(x | (checksum << n) | (reported << (n + 1)))
        for free in range(1 << len(sketches)):
            right.add(x | ((charge ^ checksum) << n) | (free << (n + 1)))
    return visible, left, right


def saturation(cell, left, right):
    sizes = [len(cell)]
    while cell:
        reduced = affine_hull(cell & left) & affine_hull(cell & right)
        if reduced == cell:
            break
        cell = reduced
        sizes.append(len(cell))
    return cell, sizes


def audit_tree(relations, tree):
    visible, left, right = relations

    def visit(cell, node):
        cell, _ = saturation(cell, left, right)
        if node is None:
            require(not cell, "a claimed terminal leaf survived the actual separate affine hulls")
            return 1, 0
        q, zero, one = node
        require(0 < q < len(visible), "the tree queries a missing coordinate")
        hi = frozenset(p for p in cell if parity(q & p))
        lo = cell - hi
        require(hi and lo, "a displayed decision is constant after saturation")
        leaves_lo, depth_lo = visit(lo, zero)
        leaves_hi, depth_hi = visit(hi, one)
        return leaves_lo + leaves_hi, max(depth_lo, depth_hi) + 1

    return visit(visible, tree)


def raw_pair_classes():
    classes = Counter()
    shift = lambda mask: mask ^ (31 if mask & 16 else 0)
    for a, b in product(range(32), repeat=2):
        aa, bb = shift(a), shift(b)
        for x in range(64):
            outputs = raw_products(x, 5)
            checksum = parity(outputs)
            require(parity(a & outputs) == parity(aa & outputs) ^ ((a >> 4) & checksum)
                    and parity(b & outputs) == parity(bb & outputs) ^ ((b >> 4) & checksum),
                    "complement/lift failed on an original assignment")
        classes[tuple(sorted({aa, bb, aa ^ bb} - {0}))] += 1
    rank_counts = Counter()
    for key, count in classes.items():
        rank_counts[{0: 0, 1: 1, 3: 2}[len(key)]] += count
        require(count == {0: 4, 1: 12, 3: 24}[len(key)], "wrong raw ordered multiplicity")
    require(rank_counts == {0: 4, 1: 180, 2: 840}, "raw ordered mask omission")
    require(Counter(map(len, classes)) == {0: 1, 1: 15, 3: 35}, "wrong quotient census")
    return sorted(key for key in classes if len(key) == 3)


def finite_thresholds():
    with tempfile.TemporaryDirectory(prefix="five-products-") as tmp:
        tuning = ["-march=native"] if platform.machine().lower() in {"amd64", "x86_64"} else []

        def run(name):
            binary = Path(tmp) / name
            subprocess.run([os.environ.get("CXX", "c++"), "-O3", *tuning, "-std=c++20",
                            str(HERE / (name + ".cpp")), "-o", str(binary)], check=True)
            return subprocess.run([str(binary)], text=True, capture_output=True, check=True).stdout

        log = run("census")
        enriched = json.loads(run("all_products"))
    graphs, rows = None, {}
    for line in log.splitlines():
        label, *fields = line.split()
        values = tuple(map(int, fields))
        if label == "graphs":
            require(graphs is None and len(values) == 4, "duplicate or malformed affine-graph result")
            graphs = values
        elif label == "pair":
            a, b, c, questions, fits_seven, root_splits = values
            require((a, b, c) not in rows and a < b < c and c == a ^ b, "bad pair roster")
            require(questions == 511 and fits_seven == 0 and root_splits > 0, "pair threshold failed")
            rows[a, b, c] = root_splits
        else:
            raise ValueError("unknown census record")
    require(graphs == (26387, 361600, 75064, 5040), "incomplete affine graph census")
    require(enriched["status"] == "passed" and enriched["nonconstant_honest_questions_up_to_complement"] == 2047
            and enriched["seven_leaves_feasible"] is False and enriched["root_translation_classes"] == 283
            and enriched["maximal_terminal_source_sets"] == graphs[-1]
            and enriched["direct_terminal_crosschecks"] == 64704, "all-products threshold failed")
    return graphs, rows, enriched


def controls(tree):
    visible, left, right = raw_relations(5, (1, 2))
    require(not left & right and saturation(visible, left, right)[0] == visible,
            "joint constraint and separate inference were confused")
    # x_1=x_3=0, s=u=v=0. Q=x_4*x_5. Each row of the four-point opposite
    # affine hull disappears only on the second application of the separate rule.
    near = frozenset(p for p in visible if p & (2 | 8 | 64 | 128 | 256) == 0)
    survivors, rounds = saturation(near, left, right)
    require(not survivors and len(left & near) == 12 and rounds == [16, 4, 0],
            "lost the two-round terminal case")
    require(not any(p & 2 or p & 8 for p in left & near), "wrong original boundary")
    # Add one of the four remaining x to the honest 12 and span the lifted points.
    # The new affine case retains both kinds of honest points after full iteration.
    extended = affine_hull((left & near) | {p for p in left if p % 64 == 48})
    require(len(extended & left) >= 13 and saturation(extended, left, right)[0] == extended,
            "a one-input enlargement of the 12-point closing case should survive")
    equal = raw_relations(5, (1, 2), charge=0)
    require(len(equal[1] & equal[2]) == 64, "charge mutation has the wrong witnesses")
    rejected = 0
    for relations, candidate in ((equal, tree), ((visible, left, right), [tree[0], None, tree[2]])):
        try:
            audit_tree(relations, candidate)
        except ValueError:
            rejected += 1
    require(rejected == 2, "a broken tree or changed checksum charge was accepted")
    return rounds, len(extended & left), rejected


def check_six_restriction():
    # Embed all five reported product bits, appending x_6=0 and the sixth
    # product coordinate 0 on both sides. The bare evaluator allows that value.
    _, left5, right5 = raw_relations(5, (1, 2, 4, 8, 16))
    six = raw_relations(6, (1, 2, 4, 8, 16, 32))

    def image(word):
        return (word & 63) | ((word >> 6) << 7)

    require({image(p) for p in left5} <= six[1] and {image(p) for p in right5} <= six[2],
            "six-product endpoint extension lost an evaluator")
    return six


def main():
    planes = raw_pair_classes()
    graphs, rows, all_five = finite_thresholds()
    require(list(sorted(rows)) == planes, "finite threshold search missed a quotient plane")
    cert = json.loads((HERE / "certificate.json").read_text())
    tree = cert["public_tree"]
    for a, b, _ in planes:
        require(audit_tree(raw_relations(5, (a, b)), tree) == (8, 3), "public pair tree")
    for mask in range(32):
        require(audit_tree(raw_relations(5, (mask,)), tree) == (8, 3), "one-report public tree")
    require(audit_tree(raw_relations(5, ()), tree) == (8, 3), "bare public tree")
    require(audit_tree(raw_relations(5, (1, 2, 4, 8, 16)), tree) == (8, 3), "five-report tree")
    require(audit_tree(check_six_restriction(), tree) == (8, 3), "six-product upper tree")
    rounds, augmented, rejected = controls(tree)
    result = {
        "status": "passed",
        "five_products": {
            "dimension_of_mask_quotient": 4, "independent_quotient_planes": len(rows),
            "raw_ordered_pairs_by_rank_zero_one_two": [4, 180, 840],
            "independent_plane_leaf_distribution": {"8": len(rows)},
            "raw_ordered_pair_leaf_distribution": {"8": 1024},
            "minimum_depth_for_every_plane": 3,
            "plane_rows_mask_a_b_c_and_surviving_root_partitions_at_budget_seven":
                [[*key, rows[key]] for key in planes],
            "effective_nonconstant_questions_per_plane": 511,
            "fitting_seven_leaf_planes": 0,
            "singleton_masks_with_eight_leaf_public_tree": 32,
            "all_five_individual_products": {
                "effective_nonconstant_questions": all_five["nonconstant_honest_questions_up_to_complement"],
                "fitting_seven_leaves": all_five["seven_leaves_feasible"],
                "root_partition_classes_modulo_translation": all_five["root_translation_classes"],
                "cached_infeasible_input_classes": all_five["cached_infeasible_source_classes"],
                "direct_projected_hull_crosschecks": all_five["direct_terminal_crosschecks"],
                "minimum_leaves": 8, "minimum_depth": 3}
        },
        "closing_sets": {"original_inputs": 64, "affine_input_domains": graphs[0],
                         "distinct_affine_checksum_graphs_over_their_domains": graphs[1],
                         "spanning_honest_graphs_that_close": graphs[2],
                         "maximal_sets": graphs[3], "honest_inputs_per_maximal_set": 12},
        "direct_raw_controls": {"repeated_hull_sizes": rounds, "honest_inputs_in_augmented_case": augmented,
                                "rejected_mutants": rejected},
        "six_product_endpoint_extension_all_reports": {"minimum_leaves": 8, "minimum_depth": 3}
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
