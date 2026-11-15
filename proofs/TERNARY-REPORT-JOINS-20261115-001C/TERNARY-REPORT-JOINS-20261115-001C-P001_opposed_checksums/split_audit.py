"""Independent truth-table affine hull oracle on two contradictory quadratic evaluators."""
from collections import Counter
from functools import cache
from itertools import combinations
import json


def parity(value):
    return value.bit_count() & 1


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def row_spaces(n, rank):
    for pivot in combinations(range(n), rank):
        positions = [(i, j) for i, p in enumerate(pivot) for j in range(p + 1, n)
                     if j not in pivot]
        for data in range(1 << len(positions)):
            rows = [1 << p for p in pivot]
            for k in indices(data):
                i, j = positions[k]
                rows[i] |= 1 << j
            yield rows


def affine_hull(mask):
    if not mask:
        return 0
    points = indices(mask)
    origin = next(points)
    pivots = {}
    for v in points:
        value = v ^ origin
        while value:
            top = value.bit_length() - 1
            if top not in pivots:
                pivots[top] = value
                break
            value ^= pivots[top]
    if mask.bit_count() == 1 << len(pivots):
        return mask
    out = [origin]
    for row in pivots.values():
        out += [x ^ row for x in out]
    return sum(1 << x for x in out)


def source_value(h, v):
    return parity((v & ((1 << h) - 1)) & ((v >> h) & ((1 << h) - 1)))


def audit_public_cells(h):
    n = 2 * h + 1
    points = range(1 << n)
    masks = [sum(parity(w & v) << v for v in points) for w in points]
    all_points = (1 << len(points)) - 1
    # s=Q and t=Q become the two complementary truth sets on t=1+s.
    gate = sum((source_value(h, v) ^ (v >> (n - 1))) << v for v in points)
    partitions = set()
    for raw in range(1, 1 << (n + 1)):
        side = sum(parity(raw & (v | ((1 ^ (v >> (n - 1))) << n))) << v for v in points)
        partitions.add(min(side, all_points ^ side))
    assert partitions == {min(m, all_points ^ m) for m in masks}

    def close(cell):
        while cell:
            next_cell = affine_hull(cell & gate) & affine_hull(cell & ~gate)
            if next_cell == cell:
                return cell
            cell = next_cell
        return 0

    result = {}
    for d in range(1 + (n if h <= 2 else h)):
        stats = Counter()
        for rows in row_spaces(n, d):
            cells = [all_points]
            for row in rows:
                cells = [part for c in cells for part in (c & masks[row], c & ~masks[row])]
            output_constrained = any(r >> (n - 1) for r in rows)
            for C in cells:
                reduced = close(C)
                assert reduced in (0, C)
                stats["cells"] += 1
                stats["empty"] += int(not reduced)
                stats["s_pinned_or_mixed"] += int(output_constrained)
                stats["empty_s_pinned_or_mixed"] += int(output_constrained and not reduced)
                if d < h:
                    assert reduced == C
        result[d] = dict(stats)
    # A fixed choice of all x_i certifies every leaf.
    leaves = [all_points]
    for i in range(h):
        leaves = [part for c in leaves for part in (c & masks[1 << i], c & ~masks[1 << i])]
    assert len(leaves) == 1 << h and not any(map(close, leaves))
    exact_optimum = None
    if h <= 2:
        @cache
        def opt(cell):
            reduced = close(cell)
            if not reduced:
                return 0, 1
            if reduced != cell:
                return opt(reduced)
            depth, leaves = 1 << n, 1 << n
            for m in masks[1:]:
                a, b = cell & m, cell & ~m
                if a and b:
                    x, y = opt(a), opt(b)
                    depth = min(depth, 1 + max(x[0], y[0]))
                    leaves = min(leaves, x[1] + y[1])
            return depth, leaves
        exact_optimum = opt(all_points)
        assert exact_optimum == (h, 1 << h)
    return {"rows": result, "paired_output_partitions_including_trivial": len(partitions),
            "all_input_coordinate_leaves_rejected": len(leaves),
            "exhaustive_adaptive_optimum_depth_leaves": exact_optimum}



def live_triples(k, point):
    triple_bits = [(point >> (3*i)) & 7 for i in range(k)]
    deltas = [(point >> (3*k+i)) & 1 for i in range(k-1)]
    deltas.append(1 ^ (sum(deltas) & 1))
    return triple_bits, deltas


def matching_relations(k):
    values = []
    whole_left = whole_right = 0
    for u in range(1 << (4*k-1)):
        triples, delta = live_triples(k, u)
        valid = [(t >> 2) ^ int(t & 3 == 3) for t in triples]
        if not any(valid):
            whole_left |= 1 << u
        if not any(a ^ b for a, b in zip(valid, delta)):
            whole_right |= 1 << u
        values.append((triples, delta))
    return (whole_left, whole_right), values


def matched_embedding(k, row, answer):
    """Map every point of a smaller odd-mismatch copy into one chosen root answer."""
    local = [(row >> (3*i)) & 7 for i in range(k)]
    defect = [(row >> (3*k+i)) & 1 for i in range(k-1)] + [0]
    if any(local):
        j = next(i for i, val in enumerate(local) if val)
        live = [i for i in range(k) if i != j]
        # Bit order in a packed triple is x, y, p. All four states below obey p=xy.
        one = next(t for t in (0, 1, 2, 7) if parity(t & local[j]))
    else:
        j = None
        live = [i for i in range(k) if defect[i] == answer]
    assert live
    cell = 0
    for u in range(1 << (4*len(live)-1)):
        values, d = live_triples(len(live), u)
        point = 0
        for h, (val, mismatch) in zip(live, zip(values, d)):
            point |= val << (3*h)
            if h < k-1:
                point |= mismatch << (3*k+h)
        if j is not None and parity(row & point) != answer:
            point |= one << (3*j)
        assert parity(row & point) == answer
        cell |= 1 << point
    assert cell.bit_count() == 1 << (4*len(live)-1)
    return live, cell


def close_matching(cell, both):
    while cell:
        new = affine_hull(cell & both[0]) & affine_hull(cell & both[1])
        if new == cell:
            return cell
        cell = new
    return 0


def search_tree(k, relations, values):
    """Run the actual balanced mismatch-parity tree to true rejection at every leaf."""
    width = 4*k-1
    def f(indices, cell):
        if len(indices) == 1:
            e = indices[0]
            m = sum((t[e] & 1) << p for p,(t,_) in enumerate(values))
            assert not close_matching(cell & m, relations)
            assert not close_matching(cell & ~m, relations)
            return 1, 2
        mid = len(indices)//2
        left, right = indices[:mid], indices[mid:]
        odd = sum((sum(d[j] for j in left) & 1) << p for p,(_, d) in enumerate(values))
        a, b = f(left, cell & odd), f(right, cell & ~odd)
        return 1+max(a[0], b[0]), a[1]+b[1]
    return f(list(range(k)), (1 << (1 << width))-1)


def audit_matching(k):
    if k not in (1, 2, 3):
        raise ValueError("the whole-table audit is bounded to three independent groups")
    relations, values = matching_relations(k)
    width = 4*k-1
    all_points = (1 << (1 << width))-1
    assert close_matching(all_points, relations) == all_points
    optimal_tree = search_tree(k, relations, values)
    assert optimal_tree == ((k-1).bit_length()+1, 2*k)
    if k == 1:
        return {"binary_search_depth_and_leaves": list(optimal_tree), "root_fixed": True}

    stats = Counter()
    for row in range(1, 1 << width):
        # The redundant odd checksum was eliminated, hence both answers are realizable.
        yes = sum(parity(row & x) << x for x in range(1 << width))
        sizes = []
        for answer, full_cell in ((0, all_points ^ yes), (1, yes)):
            I, K = matched_embedding(k, row, answer)
            sizes.append(len(I))
            assert K & ~full_cell == 0
            assert affine_hull(K) == affine_hull(K & relations[0]) == affine_hull(K & relations[1]) == K
            stats["whole_evaluator_fixed_subspaces"] += 1
            if k == 2:
                # This is a separate full-cell closure, independent of the embedding.
                reduced = close_matching(full_cell, relations)
                assert reduced
                stats["full_children_with_nonempty_closure"] += 1
                stats["full_children_pruned_but_nonempty"] += int(reduced != full_cell)
        if row & ((1 << (3*k))-1):
            assert sizes == [k-1, k-1]
            stats["queries_using_products_or_inputs"] += 1
        else:
            assert sum(sizes) == k
            stats["pure_mismatch_queries"] += 1
        stats["distinct_nontrivial_public_partitions"] += 1
    # k=2: every possible first query has two nonrefuted children, each needing at least
    # two leaves. The four-leaf tree above gives the exact unrestricted minimax there.
    return {**stats, "binary_search_depth_and_leaves": list(optimal_tree)}


def hidden_coordinate_check():
    h = 3
    M = (3, 5, 7)
    inverse_transpose = []
    for j in range(h):
        rhs = 1 << j
        col = next(x for x in range(1 << h)
                   if sum(parity(row & x) << i for i, row in enumerate(M)) == rhs)
        inverse_transpose.append(col)
    for x in range(1 << h):
        for y in range(1 << h):
            p = sum(parity(row & x) << i for i, row in enumerate(M))
            q = sum(parity(row & y) << i for i, row in enumerate(inverse_transpose))
            assert parity(p & q) == parity(x & y)
    return {"left_rows": M, "right_rows": inverse_transpose, "canonical_identity_checks": 64}


def auxiliary_wires(k):
    # A running parity over raw outputs defines each wire affinely in live coordinates.
    width = 4*k-1
    outputs = []
    for v in range(1 << width):
        triples, deltas = live_triples(k, v)
        s = t = 0
        values = []
        for triple, delta in zip(triples, deltas):
            p = triple >> 2
            s ^= p
            t ^= p ^ delta
            values.extend((s,t))
        assert s ^ t == 1
        # In the strict source each binary checksum condition has its own free padding bit.
        for u in (0,1):
            for w in (0,1):
                assert all((s or t or aux) for aux in (u,1-u))
                assert all((1-s or 1-t or aux) for aux in (w,1-w))
        outputs.append(values)
    for j in range(2*k):
        constant = outputs[0][j]
        slope = sum((outputs[1 << i][j] ^ constant) << i for i in range(width))
        assert all(row[j] == (constant ^ parity(slope & i)) for i, row in enumerate(outputs))
    return {"visible_xor_wires": 2*k, "whole_source_points": len(outputs),
            "valid_free_terminal_pad_completions_per_point": 4}


def compare_groupings():
    # Comparisons xy and yz when the source-only split has fixed x=z.
    # A complete evaluator can enforce equality of its two products on this cell.
    domain = 0
    relations = [0]*4
    for w in range(128):
        x, y, z, p, pp, q, qq = [(w >> i)&1 for i in range(7)]
        if x == z and p ^ pp ^ q ^ qq:
            domain |= 1 << w
        for j, ok in enumerate((p == x*y, pp == y*z, q == x*y, qq == y*z)):
            if ok:
                relations[j] |= 1 << w
    assert all(affine_hull(domain & r) == domain for r in relations)
    assert not close_matching(domain, (relations[0]&relations[1], relations[2]&relations[3]))
    return {"source_path_edges": 2, "initial_cell_size": domain.bit_count(),
            "single_gate_fixed": True, "whole_evaluator_rejected": True}


def run_checks():
    return {"status": "passed",
            "whole_public_evaluators": {r: audit_public_cells(r) for r in (1,2,3)},
            "output_visible_matching": {k: audit_matching(k) for k in (1,2,3)},
            "affine_recoding": hidden_coordinate_check(), "xor_wires": auxiliary_wires(3),
            "matched_source_only_groupings": compare_groupings()}


if __name__ == "__main__":
    print(json.dumps(run_checks(), sort_keys=True))
