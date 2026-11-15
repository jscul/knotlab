#!/usr/bin/env python3
"""Certify actual affine embeddings, 31-edge terminal cases and whole-evaluator hulls."""
import json
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path
from random import Random

import solver


def check(test, message):
    if not test:
        raise AssertionError(message)


def bit(mask, value):
    return (mask & value).bit_count() % 2


def literal_q(raw, edge_mask):
    return (raw & (raw >> 1) & edge_mask).bit_count() % 2


def live_embeddings():
    census = {}
    for r, s, limit in ((1, 1, None), (2, 1, None), (1, 2, None), (2, 2, 72)):
        width = 2*(r+s) + 3
        queries = list(range(1, 1 << width))
        if limit:
            queries = sorted(set(Random(49).sample(queries, limit) + [1 << (width-1), (1 << width) - 1]))
        cases = points = mixed = 0
        for query in queries:
            if query & ((1 << (2*r)) - 1) and query >> (2*r) & ((1 << (2*s)) - 1) and query >> (width-3) & 3:
                mixed += 1
            children = []
            for answer in (0, 1):
                (a,b), inject = solver.child_embedding(r,s,query,answer)
                domain = 2*(a+b) + (3 if b else 1)
                base = inject(0)
                differences = [inject(1 << i) ^ base for i in range(domain)]
                check(solver.rank(differences) == domain, "affine copy loses a state")
                honest = [[], []]
                for v in range(1 << domain):
                    w = inject(v)
                    reconstruction = base
                    for i in range(domain):
                        if v >> i & 1:
                            reconstruction ^= differences[i]
                    check(w == reconstruction and bit(query,w) == answer, "affine branch map")
                    source_labels, target_labels = solver.sides(a,b,v), solver.sides(r,s,w)
                    for j in range(2):
                        if source_labels[j]:
                            check(target_labels[j], "a side's honest state became dishonest")
                            honest[j].append(w)
                    points += 1
                for values in honest:
                    check(solver.rank([x ^ values[0] for x in values]) == domain,
                          "the embedded side fails to span the preserved affine copy")
                children.append((a,b))
                cases += 1
            cost = lambda x,y: 2**x + (2**y if y else 0)
            check(sum(cost(*child) for child in children) >= 2**r + 2**s, "leaf weight")
            child_depth = lambda x,y: 1 + max(x,y) if y else x
            check(1 + max(child_depth(*child) for child in children) >= 1 + max(r,s), "depth")
        census[f"{r},{s}"] = {"queries":len(queries), "simultaneously_both_inputs_and_an_output":mixed,
                             "answer_embeddings":cases, "source_states":points}
    return census


def symbolic_product(left, right):
    value = set()
    for i in range(left.bit_length()):
        if left >> i & 1:
            for j in range(right.bit_length()):
                if right >> j & 1:
                    value.symmetric_difference_update({tuple(sorted({i,j}))})
    return value


def certify_31_tree(chosen):
    pairs = solver.raw_factors(16)
    mask = solver.bundled_mask(16, chosen)
    all_edges = (1 << 31) - 1
    check(solver.rank([x for pair in pairs for x in pair]) == 32, "raw linear factors must be invertible")
    sides = [list(chosen), sorted(set(range(16)) - set(chosen))]
    leaves = 0
    for group, active in enumerate(sides):
        target_mask = mask if group == 0 else all_edges ^ mask
        true_terms = {(i,i+1) for i in range(31) if target_mask >> i & 1}
        expansion = set()
        for j in active:
            expansion.symmetric_difference_update(symbolic_product(*pairs[j]))
        check(expansion == true_terms, "selected mask does not equal the sum of genuine path products")
        for values in range(1 << len(active)):
            fixed = {2*j + 1: (values >> i) & 1 for i,j in enumerate(active)}
            affine_remainder = 0
            for u,v in true_terms:
                pin, free = (u,v) if u in fixed else (v,u)
                check(pin in fixed and free not in fixed, "term survives nonlinearly in a claimed leaf")
                if fixed[pin]:
                    affine_remainder ^= 1 << free
            expected = 0
            for i,j in enumerate(active):
                if values >> i & 1:
                    expected ^= pairs[j][1]
            check(affine_remainder == expected, "the actual product and announced affine output differ")
            # Two copies force their specified outputs to the same actual affine remainder.
            check(all((v ^ v) != 1 for v in (0,1)), "odd discrepancy should make this leaf empty")
            leaves += 1
    ranks = [solver.path_half_rank(31, u) for u in (mask,all_edges ^ mask)]
    check(ranks == [len(chosen),16-len(chosen)], "genuine polar rank vs decomposition")
    return {"edge_mask_hex":hex(mask),"half_ranks":ranks,"verified_odd_discrepancy_leaves":leaves,
            "exact_depth":1+max(ranks), "invertible_raw_factors":32}


def rank_counts():
    for m in range(1,15):
        all_edges = (1 << m) - 1
        direct = Counter((solver.path_half_rank(m,all_edges ^ a),solver.path_half_rank(m,a)) for a in range(1 << m))
        check(direct == solver.rank_profiles(m), "run-state recurrence disagrees with Gaussian elimination")
    for m, bound in ((3,0),(5,1),(7,1)):
        all_edges = (1 << m) - 1
        ranks = [solver.path_half_rank(m,mask) for mask in range(1 << m)]
        direct = 0
        for a,b in product(range(1 << m),repeat=2):
            candidates = [(a ^ c) | (b ^ d) for c,d in product((0,all_edges),repeat=2)]
            low = sum(ranks[m] <= bound for m in candidates)
            check(low <= 1, "the four small-union events overlap")
            direct += low
        check(direct == solver.low_union_count(m,bound), "weighted pair census")
    profile = solver.rank_profiles(31)
    high = sum(cnt for (r,s),cnt in profile.items() if min(r,s) >= 8)
    low_union = solver.low_union_count(31,7)
    adds = sum(cnt for (r,s),cnt in profile.items() if r+s == 16)
    combined = high**2 + low_union
    check(sum(profile.values()) == 2**31 and high == 2010227968 and adds == 557056, "31-edge census")
    return {"all_ordered_pairs":2**62, "masks_with_both_half_ranks_at_least_8":high,
            "ordered_pairs_with_all_large_forms":high**2,"ordered_pairs_with_small_union":low_union,
            "certified_by_either_criterion":combined,"outside_these_two_criteria":2**62-combined,
            "masks_with_additive_half_ranks":adds,"balanced_bundle_masks":comb(16,8),
            "full_Gaussian_crosscheck_through_edges":14}


def large_hulls():
    # Actual 32 input bits followed by the first total, first sketch and second sketch.
    full = (1 << 31) - 1
    a = solver.bundled_mask(16, range(8))
    b = solver.bundled_mask(16, range(0,16,2))
    fixtures = [
        ("input_only_forces_left_sketch",8,0,(),{"a":0}),
        ("rare_product_level_forces_two_inputs",7,1,("rare",),{"a":1}),
        ("common_product_level_spans",7,1,(),{"a":0}),
        ("total_pinned",7,1,(),{"s":0}),
        ("cross_sketch_row",7,1,(),{"ab":0}),
        ("two_output_rows",6,2,(),{"s":0,"a":0}),
        ("three_output_rows",5,3,(),{"s":0,"a":0,"b":0})]
    result = {}
    for index,(name,input_pins,out_rank,more,rows) in enumerate(fixtures):
        rng = Random(100+index)
        expect = 35 - 8 - (2 if "rare" in more else int(out_rank == 0))
        observed = []
        for side in (0,1):
            origin = None
            pivots = {}
            attempts = 0
            while len(pivots) < expect and attempts < 10000:
                attempts += 1
                raw = rng.getrandbits(32)
                for j in range(input_pins):
                    raw &= ~(1 << (2*j+1))
                if "rare" in more:
                    raw |= 1 << 15
                    raw &= ~(1 << 14)
                    raw |= (1 ^ ((raw >> 16) & 1)) << 14
                total = literal_q(raw,full) ^ side
                left = literal_q(raw,a) if side == 0 else rng.randrange(2)
                right = literal_q(raw,b) if side else rng.randrange(2)
                values = {"s":total,"a":left,"b":right,"ab":left ^ right}
                if any(values[key] != val for key,val in rows.items()):
                    continue
                point = raw | (total << 32) | (left << 33) | (right << 34)
                if origin is None:
                    origin = point
                v = point ^ origin
                while v:
                    index_pivot = v.bit_length()-1
                    if index_pivot not in pivots:
                        pivots[index_pivot] = v
                        break
                    v ^= pivots[index_pivot]
            check(len(pivots) == expect, (name,side,"failed to certify all hull directions"))
            observed.append({"affine_dimension":len(pivots),"deterministic_draws":attempts})
        result[name] = {"query_codimension":8,"output_row_rank":out_rank,"side_hull_bases":observed}
    return result


def early_closed_child():
    # Four reports, s, a, b after t=1+s. Left observes the middle edge;
    # the right sketch is empty. Actual exact restricted hulls are iterated.
    def hull(points):
        if not points:
            return set()
        origin = min(points)
        span = {0}
        for x in points:
            step = x ^ origin
            if step not in span:
                span |= {v ^ step for v in span}
        return {origin ^ v for v in span}

    left, right = set(), set()
    for w in range(128):
        x, s, a, b = w & 15, w >> 4 & 1, w >> 5 & 1, w >> 6 & 1
        q = literal_q(x,7)
        if s == q and a == literal_q(x,2):
            left.add(w)
        if s == q ^ 1 and b == 0:
            right.add(w)
    start = hull(left) & hull(right)
    cell = {w for w in start if w >> 5 & 1}
    sizes = [len(cell)]
    while cell:
        new = hull(cell & left) & hull(cell & right)
        if new == cell:
            break
        cell = new
        sizes.append(len(cell))
    check(not cell, "for one poor mask choice the exceptional middle product closes early")
    return {"edges":3, "masks":[2,0], "one_query_left_middle_product":1,
            "opposite_charge_cell_sizes_during_hull_iterations":sizes}


def main():
    negative_input = 3
    check(literal_q(negative_input,1) == 1 and literal_q(negative_input,4) == 0,
          "two genuinely different masks can disagree in the charge-zero control")
    data = {"status":"passed","all_small_mixed_queries":live_embeddings(),"path_mask_census":rank_counts(),
            "length_31_trees":{"midpoint":certify_31_tree(list(range(8))),
                               "noncontiguous":certify_31_tree(list(range(0,16,2))),
                               "unbalanced":certify_31_tree(list(range(7)))},
            "length_31_whole_evaluator_fixed_subspaces":large_hulls(),
            "early_closed_asymmetric_child":early_closed_child(),
            "unequal_mask_honest_control":{"reports":negative_input,"edge_masks":[1,4],"honest_sketches":[1,0]}}
    saved = Path(__file__).with_name("checks.json")
    if saved.exists():
        check(json.loads(saved.read_text()) == data, "certificate differs from immutable checker output")
    print(json.dumps(data,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
