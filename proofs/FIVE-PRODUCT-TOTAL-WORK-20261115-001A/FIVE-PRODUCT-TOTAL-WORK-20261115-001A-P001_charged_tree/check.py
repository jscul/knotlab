"""Replay the charged trees, small exhaustive optimizers and affine restrictions."""

import json
from collections import Counter
from itertools import product
from math import inf
from pathlib import Path

from charged import (affine_hull, audit_tree, exact_costs, full_space, parity,
                     partitions, path_sources, public_tree, query_points, require)


HERE = Path(__file__).resolve().parent


def small_census():
    counts = Counter()
    for colors in product(range(3), repeat=8):
        rich = sum((color == 1) << j for j, color in enumerate(colors))
        plain = sum((color == 2) << j for j, color in enumerate(colors))
        if not rich or not plain:
            continue
        costs = exact_costs(3, rich, plain)
        require(costs.weighted == costs.normalized >= 3 * costs.free_leaves - 1,
                "unrestricted small optimum disagrees with normalization or the lower bound")
        counts[costs.free_leaves, costs.weighted] += 1
    require(counts == {(1, 2): 5098, (1, 3): 896, (2, 5): 56}, "incomplete small census")
    require(exact_costs(3, 13, 50).weighted == 3, "three-check single-leaf control")
    require(exact_costs(2, 7, 8).weighted == exact_costs(3, 7, 8).weighted == 2
            and affine_hull(7) == 15 != full_space(3), "geometry-only check changed the cost")
    return [[free, work, count] for (free, work), count in sorted(counts.items())]


def early_check_control():
    # Bits from low to high are a,b,c,d,y,t. At t=0, P is the union of two
    # planes. At t=1 every point belongs to the plain evaluator only.
    rich = 0
    for x in range(32):
        plane = (not x & 16 and not x & 12) or (x & 16 and not x & 3)
        if not plane:
            rich |= 1 << x
    full = full_space(6)
    plain = full ^ rich
    base = affine_hull(rich)
    require((rich.bit_count(), plain.bit_count(), base.bit_count(), affine_hull(plain)) == (24, 40, 32, full),
            "wrong early-check setup")
    q_count = 0
    for low in partitions(6, full):
        if not low & base or not (full ^ low) & base:
            continue
        q_count += 1
        for part in (low, full ^ low):
            require((part & rich).bit_count() >= 9 and affine_hull(part & rich) == part & base
                    and affine_hull(part & plain) == part and part & base & plain,
                    "a first question bypassed the early-check obstruction")
    require(q_count == 62, "omitted one of the nonconstant base questions")
    tails = ["plain", "rich"]
    early = audit_tree(6, rich, plain, ["rich", [16, tails, tails]])
    late = audit_tree(6, rich, plain, [32, [16, tails, tails], "rich"])
    costs = exact_costs(6, rich, plain)
    require((costs.weighted, costs.normalized, costs.checks_only_at_leaves, costs.free_leaves, costs.checks_only)
            == (6, 6, 7, 2, inf), "all-cell dynamic program disagrees on strategic placement")
    require(early["total_work"] == costs.weighted and late["total_work"] == costs.checks_only_at_leaves,
            "a matched explicit control fails to attain the stated bound")
    return {"optimum": costs.weighted, "checks_only_at_leaves_optimum": costs.checks_only_at_leaves,
            "free_leaves": costs.free_leaves, "tested_first_questions_nonconstant_at_t_zero": q_count}


def canonical_sources(r):
    rich = plain = 0
    status = []
    for word in range(1 << (3 * r)):
        errors = 0
        for i in range(r):
            triple = word >> (3 * i) & 7
            errors |= ((triple >> 2) ^ int(triple & 3 == 3)) << i
        label = (errors == 0, bool(parity(errors)))
        status.append(label)
        if label[0]:
            rich |= 1 << word
        if label[1]:
            plain |= 1 << word
    return rich, plain, status


def insert_triple(rest, i, triple):
    low_mask = (1 << (3 * i)) - 1
    return (rest & low_mask) | (triple << (3 * i)) | ((rest & ~low_mask) << 3)


def check_all_question_restrictions(r, prior, larger):
    # Two honest points suffice for every local nonzero linear form. Interpolation
    # between the chosen points is affine in one bit of the remaining coordinates.
    witnesses = (0, 1, 2, 7)
    pairs = {mask: [next(v for v in witnesses if parity(mask & v) == answer)
                    for answer in (0, 1)] for mask in range(1, 8)}
    tested = 0
    for q in range(1, 1 << (3 * r)):
        block = ((q & -q).bit_length() - 1) // 3
        local = q >> (3 * block) & 7
        mask = (1 << (3 * block)) - 1
        rest_q = (q & mask) | ((q >> 3) & ~mask)
        for z, label in enumerate(prior):
            contribution = parity(rest_q & z)
            for answer in (0, 1):
                point = insert_triple(z, block, pairs[local][contribution ^ answer])
                require(parity(q & point) == answer and larger[point] == label,
                        "affine child embedding changed its answer or one of the two evaluators")
                tested += 1
    return tested


def original_image(r, word):
    x = s = u = v = previous_odd = 0
    for i in range(r):
        triple = word >> (3 * i) & 7
        a, b, w = triple & 1, (triple >> 1) & 1, triple >> 2
        previous_odd ^= b
        x |= a << (2 * i)
        x |= previous_odd << (2 * i + 1)
        s ^= w
        if i == 0:
            u = w
        if i == 1:
            v = w
    return x | (s << (2 * r)) | (u << (2 * r + 1)) | (v << (2 * r + 2))


def grouped_controls():
    result = []
    prior = None
    for r in range(1, 5):
        rich, plain, current = canonical_sources(r)
        full = full_space(3 * r)
        require(affine_hull(rich) == affine_hull(plain) == full, "a source reduces the grouped root")
        checked = 0
        if prior is not None:
            checked = check_all_question_restrictions(r, prior, current)
        else:
            require(exact_costs(3, rich, plain).weighted == 5, "rank-one base changed")
        row = {"groups": r, "minimum_work": 3 * 2 ** r - 1, "embedded_word_answer_checks": checked}
        if r >= 3:
            n, raw_rich, raw_plain = path_sources(2 * r - 1)
            mapped_rich = mapped_plain = 0
            columns = [original_image(r, 1 << i) for i in range(3 * r)]
            for word, (left, right) in enumerate(current):
                dest = original_image(r, word)
                linear = 0
                for i, col in enumerate(columns):
                    if word & (1 << i):
                        linear ^= col
                require(dest == linear, "the reduction used a nonlinear visible recoding")
                if left:
                    mapped_rich |= 1 << dest
                if right:
                    mapped_plain |= 1 << dest
            require(mapped_rich == raw_rich and mapped_plain == raw_plain,
                    "the grouped image lost a side or admitted a spurious evaluator row")
            row["original_path_products"] = 2 * r - 1
            score = audit_tree(n, raw_rich, raw_plain, public_tree(tuple(range(1, 2 * r, 2))))
            require(score["total_work"] == row["minimum_work"], "the original interfaces miss the grouped upper")
            row["verified_original_work"] = score["total_work"]
        result.append(row)
        prior = current
    return result


def fixed_controls(certificate):
    n, rich, plain = path_sources(5)
    require((rich.bit_count(), plain.bit_count(), rich & plain) == (64, 256, 0), "wrong fixed evaluator")
    tree = certificate["charged_tree"]
    require(tree == public_tree((1, 3, 5)), "fixed certificate lost an operation")
    score = audit_tree(n, rich, plain, tree)
    require((score["total_work"], score["splits"], score["rich_calls"], score["plain_calls"],
             score["leaves"], score["maximum_paid_path"]) == (23, 7, 8, 8, 8, 5), "wrong fixed total")
    # In this guard the affine consequence s=0 follows from the rich evaluator.
    # Refute its negation under this guard and continue on its positive side.
    guard = full_space(n)
    for q in (2, 8, 32):
        guard &= ~query_points(n, q)
    inline = audit_tree(n, rich, plain, [64, "plain", "rich"], initial=guard)
    negated = audit_tree(n, rich, plain, "rich", initial=guard & query_points(n, 64))
    continuation = audit_tree(n, rich, plain, "plain", initial=guard & ~query_points(n, 64))
    original_charge = negated["total_work"] + 1 + continuation["total_work"]
    require(inline["total_work"] == original_charge == 3 and rich & query_points(n, 64),
            "the contextual scalar consequence failed its guarded expansion")
    _, equal_rich, equal_plain = path_sources(5, charge=0)
    require((equal_rich & equal_plain).bit_count() == 64, "equal-charge common witnesses missing")
    rejected = 0
    for l, p, raw in ((equal_rich, equal_plain, tree), (rich, plain, [tree[0], "plain", tree[2]]),
                      (rich, plain, [1 << n, tree[1], tree[2]])):
        try:
            audit_tree(n, l, p, raw)
        except ValueError:
            rejected += 1
    require(rejected == 3, "a false certificate was accepted")
    return score, {"contextual_once_used_scalar": original_charge, "inlined_scalar": inline["total_work"],
                   "equal_charge_joint_witnesses": 64, "rejected_mutations": rejected}


def main():
    cert = json.loads((HERE / "certificate.json").read_text())
    fixed, controls = fixed_controls(cert)
    census = small_census()
    early = early_check_control()
    grouped = grouped_controls()
    print(json.dumps({"status": "passed", "fixed_pair": fixed, "raw_controls": controls,
                      "small_disjoint_nonempty_pairs": sum(row[2] for row in census),
                      "small_distribution_free_leaves_paid_work_count": census,
                      "early_check_control": early, "grouped_path_checks": grouped}, indent=2))


if __name__ == "__main__":
    main()
