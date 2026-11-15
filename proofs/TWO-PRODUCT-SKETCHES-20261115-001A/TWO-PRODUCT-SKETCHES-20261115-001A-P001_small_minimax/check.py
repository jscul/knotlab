"""Replay the witness trees, enumerate small minimax thresholds, and certify the seven-edge lower bound."""

from collections import Counter
from functools import cache
from itertools import combinations
import json
from pathlib import Path
from shutil import which
import subprocess
from tempfile import TemporaryDirectory

import matching
from solver import Auditor, full_relations, parity, strategy


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


@cache
def orbit(m, a, b):
    full = (1 << m) - 1
    reverse = lambda v: int(f"{v:0{m}b}"[::-1], 2)
    images = set()
    for x in (a, a ^ full):
        for y in (b, b ^ full):
            for p, q in ((x, y), (reverse(x), reverse(y))):
                images.update(((p, q), (q, p)))
    return frozenset(images)


@cache
def representative(m, a, b):
    return min(orbit(m, a, b))


def compress(v, positions):
    return sum(((v >> old) & 1) << new for new, old in enumerate(positions))


def products(xs):
    return sum((p & q) << i for i, (p, q) in enumerate(zip(xs, xs[1:])))


def bits(v, n):
    return tuple((v >> i) & 1 for i in range(n))


def verify_translation():
    m, n = 3, 4
    checked = 0
    for a, b in [(0, 7), (7, 7), (3, 5), (2, 6)]:
        left, right = full_relations(m, a, b)
        for u in range(1 << n):
            for point in range(1 << (n + 3)):
                x, outputs = point & ((1 << n) - 1), point >> n
                h = products(bits(x ^ u, n)) ^ products(bits(x, n))
                translated = (x ^ u) | ((outputs ^ (parity(h) | (parity(h & a) << 1) |
                                                       (parity(h & b) << 2))) << n)
                require((point in left) == (translated in left) and (point in right) == (translated in right),
                        "translation changed an evaluator relation")
                checked += 1
    return checked


def read_budgets(executable, m, budget):
    result = subprocess.run([executable, str(m), str(budget)], check=True, capture_output=True, text=True)
    rows = {}
    for line in result.stdout.splitlines():
        a, b, count, possible = map(int, line.split())
        require((a, b) == representative(m, a, b) and count == len(orbit(m, a, b)), "C++ mask equivalence")
        require((a, b) not in rows, "duplicate C++ mask class")
        rows[a, b] = bool(possible)
    all_reps = {representative(m, i, j) for i in range(1 << m) for j in range(1 << m)}
    require(rows.keys() == all_reps, "missing mask orbit")
    require(sum(len(orbit(m, *p)) for p in rows) == 1 << (2 * m), "incorrect number of ordered pairs")
    return rows


def five_costs(executable):
    base = {}
    for m, budget in [(1, 1), (2, 1), (3, 3), (4, 3), (5, 5)]:
        result = read_budgets(executable, m, budget)
        require(not any(result.values()), f"claimed universal lower bound failed at m={m}")
        base[m] = {"ordered_masks": 1 << (2 * m), "orbits": len(result), "excluded_leaves": budget}
    at_six = read_budgets(executable, 5, 6)
    at_seven = read_budgets(executable, 5, 7)
    require(all(at_seven[p] for p in at_six if at_six[p]), "budget monotonicity")
    costs = {p: 6 if at_six[p] else 7 if at_seven[p] else 8 for p in at_six}
    side = set()
    for a in range(32):
        for b in range(32):
            if a in (0, 31) or b in (0, 31):
                require(costs[representative(5, a, b)] == 8, "one-sided sketch improved five edges")
                side.add((a, b))
    require(len(side) == 124 and costs[6, 14] == 6 and costs[1, 3] == 7 and costs[14, 14] == 8,
            "asymmetric controls")
    histogram = Counter()
    for p, cost in costs.items():
        histogram[cost] += len(orbit(5, *p))
    require(histogram == {6: 92, 7: 72, 8: 860}, "five-edge full cost distribution")
    return base, costs, dict(sorted(histogram.items()))


def verify_contractions():
    total = 0
    for positions in combinations(range(7), 5):
        for a, b in ((0, 127), (43, 84), (46, 91)):
            small_a, small_b = compress(a, positions), compress(b, positions)
            for v in range(64):
                xs = bits(v, 6)
                lifted = [xs[0]]
                j = 0
                for i in range(7):
                    j += i in positions
                    lifted.append(xs[j])
                raw = products(lifted)
                old = products(xs)
                for mask, shortened in ((127, 31), (a, small_a), (b, small_b)):
                    correction = parity(raw & mask) ^ parity(old & shortened)
                    predicted = sum(lifted[i] for i in range(7) if i not in positions and mask >> i & 1) % 2
                    require(correction == predicted, "contracted products did not become the stated affine terms")
                total += 1
    for p in range(64):
        y = bits(p, 6)
        x = (y[2], y[1] ^ y[3], y[4], y[1], y[0], y[5], y[0] ^ y[4])
        require(parity(products(x)) == parity(products(y)) and
                parity(products(x) & 7) == parity(products(y) & 14), "midpoint linear restriction")
    return total


def diagonal_audit(m, a, b, ops):
    model = matching.diagonal_profile(m, a, b, ops)
    if model is None:
        return None
    types, lower = model
    r = (m + 1) // 2
    spanning = {0}
    columns = []
    labels = []
    for i, j in types:
        for v in range(1 << r):
            if v in spanning or matching.apply(ops[a], v) != i * v or matching.apply(ops[b], v) != j * v:
                continue
            spanning.update([w ^ v for w in spanning])
            columns.append(v)
            labels.append((i, j))
    require(len(spanning) == 1 << r, "missing common eigenbasis")
    diag_a = sum(i << k for k, (i, j) in enumerate(labels))
    diag_b = sum(j << k for k, (i, j) in enumerate(labels))
    full = matching.columns(m, (1 << m) - 1)
    for even in range(1 << r):
        right_even = sum(parity(even & matching.apply(full, v)) << j for j, v in enumerate(columns))
        for t in range(1 << r):
            odd = matching.apply(columns, t)
            x = tuple(k for e, o in zip(bits(even, r), bits(odd, r)) for k in (e, o))
            p = products(x)
            active = right_even & t
            require((parity(p), parity(p & a), parity(p & b))
                    == (parity(active), parity(active & diag_a), parity(active & diag_b)),
                    "simultaneous matching failed an original input")
    return lower


def check_seven(five):
    keeps = list(combinations(range(7), 5))
    ops = matching.operators(7)
    classes = Counter()
    diag_bounds = Counter()
    examples = {}
    reps = {representative(7, a, b) for a in range(128) for b in range(128)}
    for a, b in sorted(reps):
        mult = len(orbit(7, a, b))
        lb = diagonal_audit(7, a, b, ops)
        if lb is not None:
            require(lb >= 8, "seven-edge matching did not meet the target")
            diag_bounds[lb] += mult
        chosen = next((p for p in keeps if five[representative(5, compress(a, p), compress(b, p))] >= 8), None)
        require(lb is not None or chosen is not None, f"no seven-edge lower certificate for {(a, b)}")
        mode = "both" if lb is not None and chosen is not None else "matching_only" if lb is not None else "contraction_only"
        classes[mode] += mult
        examples.setdefault(mode, {"a": a, "b": b, "matching_bound": lb, "keep": chosen,
                                   "five_edge_masks": None if chosen is None else [compress(a, chosen), compress(b, chosen)]})
    require(sum(classes.values()) == 16384 and sum(diag_bounds.values()) == 832, "seven-edge ordered coverage")
    require(diag_bounds == {8: 36, 10: 40, 12: 600, 16: 156}, "diagonal seven-edge classes")
    ops = matching.operators(5)
    diag5 = Counter()
    for p, cost in five.items():
        lb = diagonal_audit(5, *p, ops)
        if lb is not None:
            require(cost >= lb, "finite optimum violates diagonal lower bound")
            diag5[lb] += len(orbit(5, *p))
    require(diag5 == {6: 28, 8: 132}, "five-edge diagonal color counts")
    return dict(classes), dict(sorted(diag_bounds.items())), dict(sorted(diag5.items())), examples, len(reps)


def verify_trees(executable):
    fixtures = json.loads((HERE / "trees.json").read_text())
    results = {}
    for name, instance in fixtures.items():
        m, a, b = instance["m"], instance["a"], instance["b"]
        tree = instance["tree"]
        result = Auditor(m, a, b).verify_tree(tree)
        require(list(result) == instance["leaves_depth"], f"witness mismatch for {name}")
        results[name] = list(result)
        common = full_relations(m, a, b, charge=0)
        require(len(common[0] & common[1]) == 1 << (m + 1), "matched charge lost honest inputs")
    direct = Auditor(2, 1, 2).optimum()
    require(direct == (2, 1), "direct minimum over literal point sets")
    for a in range(8):
        for b in range(8):
            require(not Auditor(3, a, b).within(3), "unreduced direct point-set minimax")
    # Ask the compiled minimax for its own arbitrary-form witness on genuinely unequal masks.
    cmd = [executable, "5", "6", "6", "14", "--tree"]
    raw = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.split(maxsplit=4)
    require(raw[:4] == ["6", "14", "16", "1"], "C++ witness request")
    require(Auditor(5, 6, 14).verify_tree(json.loads(raw[4]))[0] == 6, "C++ witness failed independent tree replay")
    # Absorbing at just one oracle round would leave live assignments in these terminal cells.
    model = Auditor(5, 6, 14)
    fixed_points = {}
    for u in (0, 1):
        cell = model.plane(384) & (model.plane(10) if u else model.visible - model.plane(10))
        sizes = [len(cell)]
        from solver import affine_hull
        while cell:
            nxt = affine_hull(cell & model.left) & affine_hull(cell & model.right)
            sizes.append(len(nxt))
            if nxt == cell:
                break
            cell = nxt
        require(sizes[-1] == 0 and sizes[1] > 0, "the fixed-point feedback control changed")
        fixed_points[str(u)] = sizes
    return results, fixed_points


def audit_sacrifice():
    # Independently check the claimed smaller affine copy on every visible point, for both answers.
    labels = ((0, 0), (1, 0), (0, 1))

    def accepts(v, types):
        r = len(types)
        pair_values = [(v >> (2 * i)) & 3 == 3 for i in range(r)]
        s, a, b = bits(v >> (2 * r), 3)
        q = sum(pair_values) & 1
        pa = sum(t[0] * p for t, p in zip(types, pair_values)) & 1
        pb = sum(t[1] * p for t, p in zip(types, pair_values)) & 1
        return (s == q and a == pa, s != q and b == pb)

    def states(i, types):
        c, d = types[i]
        outputs = 1 | (c << 1) | (d << 2)
        return [(raw << (2 * i)) | (int(raw == 3) * outputs << (2 * len(types))) for raw in range(4)]

    for q in range(1, 512):
        i, state = next((i, v) for i in range(3) for v in states(i, labels) if parity(q & v))
        keep = [j for j in range(3) if j != i]
        smaller = tuple(labels[j] for j in keep)
        for answer in (0, 1):
            def embed(v):
                inputs = sum(((v >> (2 * j)) & 3) << (2 * k) for j, k in enumerate(keep))
                base = inputs | ((v >> 4) << 6)
                return base ^ (state if parity(q & base) != answer else 0)
            zero = embed(0)
            directions = [embed(1 << j) ^ zero for j in range(7)]
            for v in range(128):
                out = embed(v)
                require(out == (matching.apply(directions, v) ^ zero) and parity(q & out) == answer,
                        "smaller matching embedding is nonlinear or has the wrong query answer")
                lo, ro = accepts(out, labels)
                li, ri = accepts(v, smaller)
                require((not li or lo) and (not ri or ro), "an honest matching side failed under embedding")
    two_labels = ((0, 0), (1, 1), (1, 1))
    residual = [q for q in range(1, 512) if not any(parity(q & v)
                for i in range(3) for v in states(i, two_labels))]
    require(residual == [384], "two-label matching has the wrong unabsorbed query")
    require(matching.diagonal_lower({(0, 0): 6, (1, 0): 5, (0, 1): 5}) == 768
            and matching.diagonal_lower({(0, 0): 8, (1, 1): 8}) == 512, "sixteen-pair bounds")
    return {"nonconstant_three_pair_queries": 511, "both_child_embeddings": 1022,
            "points_replayed_per_embedding": 128, "two_label_unabsorbed_forms": residual,
            "sixteen_pairs_three_label_lower": 768, "sixteen_pairs_balanced_common_exact": 512}


def main():
    compiler = which("g++") or which("c++")
    require(compiler, "a C++20 compiler is needed for the finite exhaustive census")
    with TemporaryDirectory(prefix="two-sketch-check-") as tmp:
        executable = str(Path(tmp) / "minimax")
        subprocess.run([compiler, "-std=c++20", "-O3", "-march=native", str(HERE / "minimax.cpp"),
                        "-o", executable], check=True)
        thresholds, five, histogram = five_costs(executable)
        trees, rounds = verify_trees(executable)
    modes, diag7, diag5, examples, orbit_count = check_seven(five)
    contractions = verify_contractions()
    translations = verify_translation()
    sacrifice = audit_sacrifice()
    minima = [[2, 1], [2, 1], [4, 2], [4, 2], [6, 3], [6, 3], [8, 3], [8, 3]]
    print(json.dumps({"status": "passed", "path_minimum_leaves_depth_for_m_1_through_8": minima,
                      "public_only_leaves_for_m_1_through_8": [2, 2, 4, 4, 8, 8, 16, 16],
                      "all_mask_lower_thresholds": thresholds, "five_edge_leaves_ordered_histogram": histogram,
                      "five_edge_mask_orbits_by_exact_leaves": {str(k): [list(p) for p in sorted(five) if five[p] == k]
                                                                  for k in (6, 7, 8)},
                      "five_edge_one_sided_pairs_at_eight": 124, "five_edge_diagonal_lower_counts": diag5,
                      "seven_edge_mask_orbits": orbit_count, "seven_edge_coverage_modes": modes,
                      "seven_edge_diagonal_lower_counts": diag7, "seven_edge_cover_examples": examples,
                      "eight_edge_ordered_masks_covered_by_restriction": 65536,
                      "diagonal_pair_embedding_checks": sacrifice,
                      "point_set_three_edge_unreduced_pairs": 64, "checked_small_contractions": contractions,
                      "checked_midpoint_embedding_x_inputs": 64, "checked_translation_states": translations,
                      "tree_replays_leaves_depth": trees, "asymmetric_fixed_point_sizes": rounds},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
