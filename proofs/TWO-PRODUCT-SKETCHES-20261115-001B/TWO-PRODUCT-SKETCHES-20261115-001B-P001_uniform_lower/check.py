"""Independent finite checks of the uniform two-sketch lower bound."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations
import json
from math import ceil, comb
from random import Random

from projector_filter import audit as restricted_polar_audit


def parity(x):
    return x.bit_count() & 1


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def basis(values):
    pivots = {}
    for value in values:
        while value:
            top = value.bit_length() - 1
            if top not in pivots:
                pivots[top] = value
                break
            value ^= pivots[top]
    return tuple(pivots.values())


def left_kernel(rows):
    """Left-nullspace basis of a binary matrix, as input coefficient masks."""
    pivots, kernel = {}, []
    for index, value in enumerate(rows):
        coeff = 1 << index
        while value:
            top = value.bit_length() - 1
            if top not in pivots:
                pivots[top] = value, coeff
                break
            vec, src = pivots[top]
            value ^= vec
            coeff ^= src
        if not value:
            kernel.append(coeff)
    return kernel


def combine(rows, coeff):
    value = 0
    for bit in bits(coeff):
        value ^= rows[bit]
    return value


def path_matrix(m, mask):
    rows = [0] * (m // 2 + 1)
    for i in bits(mask):
        left, right = (i+1)//2, i//2
        rows[left] ^= 1 << right
    return rows


def rank_histogram(m, joint=False):
    # Accumulate one unit of rank on the first, third, ... edge of each run.
    states = {(-1, 0, 0, 0): 1}
    for _ in range(m):
        after = Counter()
        for (last, odd, zero_rank, one_rank), count in states.items():
            for new in (0, 1):
                new_odd = 1 - odd if new == last else 1
                after[new, new_odd, zero_rank + (new == 0)*new_odd,
                      one_rank + (new == 1)*new_odd] += count
        states = after
    hist = Counter()
    for (_, _, r, s), count in states.items():
        hist[(r,s) if joint else min(r,s)] += count
    return hist


def rank_audit():
    raw_masks = 0
    for m in range(1, 13):
        k = (m+1)//2
        full = (1 << m) - 1
        q = path_matrix(m, full)
        assert len(basis(q)) == k
        hist = Counter()
        for mask in range(full+1):
            one, other = path_matrix(m, mask), path_matrix(m, full ^ mask)
            b = min(len(basis(one)), len(basis(other)))
            hist[b] += 1
            low = min((one, other), key=lambda rows: len(basis(rows)))
            kernel = left_kernel(low)
            assert len(kernel) == len(q)-b
            assert all(combine(low, v) == 0 for v in kernel)
            assert len(basis(combine(q, v) for v in kernel)) >= k-b
        assert hist == rank_histogram(m)
        raw_masks += full+1
    hist = rank_histogram(31)
    assert sum(hist.values()) == 1 << 31
    def one_side_bound(k, b):
        r = min(k, b)
        mass = Fraction(1, 1 << r) + Fraction(1, 1 << (k+1))
        base = max(ceil(1/mass), ceil(Fraction(2,3) * (1 << max(0,k-b))))
        if b >= 9 and k == 16:
            base = max(base, ceil(1/(Fraction(1,512)+Fraction(1,1 << 18))))
        return base
    bounds = {b:one_side_bound(16,b) for b in sorted(hist)}
    assert min(bounds.values()) == 256
    assert [b for b in bounds if bounds[b] < 512] == [7,8]
    for k in range(1,71):
        for b in range(k+1):
            assert one_side_bound(k,b) >= ceil(Fraction(2,3)*(1 << ((k+1)//2)))
    return {'small_path_masks_checked':raw_masks,'31_edge_rank_distribution':dict(sorted(hist.items())),
            '31_edge_one_side_leaf_bounds':bounds,'individual_masks_passing_below_512_filter':hist[7]+hist[8]}


def projector_counts():
    checked = 0
    for k in range(1,8):
        m = 2*k-1
        by_rank = Counter()
        for mask in range(1 << m):
            e = path_matrix(m,mask)
            t = []
            for row in e:
                t.append(row ^ (t[-1] if t else 0))
            project = all(combine(t,row) == row for row in t)
            odd = [(mask >> (2*j)) & 1 for j in range(k)]
            even = [(mask >> (2*j+1)) & 1 for j in range(k-1)]
            cuts = any(all(value == odd[j + (j >= cut)] for j,value in enumerate(even))
                       for cut in range(k))
            low_rank = len(basis(e))
            comp_rank = len(basis(path_matrix(m, ((1 << m)-1) ^ mask)))
            assert project == cuts == (low_rank+comp_rank == k)
            if project:
                assert low_rank == sum(odd)
                by_rank[low_rank] += 1
        for a in range(k+1):
            expected = comb(k,a)
            if 0 < a < k:
                expected += 2*(k-1)*comb(k-2,a-1)
            assert by_rank[a] == expected
        checked += 1 << m
    hist = rank_histogram(31,joint=True)
    expected = comb(16,7)+30*comb(14,6)
    assert hist[7,9] == hist[9,7] == expected == 101530
    return {'direct_small_masks':checked,'31_edge_rank_seven_projectors':expected,
            '31_edge_rank_pairs_7_9_in_either_order':2*expected}


def quadratic_regularization():
    rng = Random(20261115)
    counts = Counter()
    for m in (7,13,17,31,43):
        full = (1 << m)-1
        masks = [(0,full), (full//3,full//5),
                 ((1 << (m//3))-1, ((1 << (m//3))-1) << (m//3))]
        masks += [(rng.getrandbits(m),rng.getrandbits(m)) for _ in range(160)]
        k = (m+1)//2
        target = (k+2)//3
        for a,b in masks:
            vectors = [path_matrix(m,mask) for mask in (full,a,b)]
            killed = lost = 0
            while True:
                low = None
                for c in range(1,8):
                    mat = [combine(v,c) for v in zip(*vectors)]
                    rank = len(basis(mat))
                    if 0 < rank < target:
                        low = mat
                        break
                if low is None:
                    break
                kernel = left_kernel(low)
                lost += len(low)-len(kernel)
                killed += 1
                vectors = [[combine(rows,v) for v in kernel] for rows in vectors]
            assert killed <= 2 and lost <= killed*(target-1)
            assert len(basis(vectors[0])) >= target
            relations = [c for c in range(8) if not any(combine(v,c) for v in zip(*vectors))]
            directions = [d for d in (1,3,5,7) if all(parity(d & c) == 0 for c in relations)]
            assert directions
            counts[killed] += 1
    return dict(sorted(counts.items()))


def many_sketch_checks():
    rng = Random(42061)
    trials = 0
    for m in (15,31,45):
        k = (m+1)//2
        full = (1 << m)-1
        for h in range(8):
            for trial in range(5):
                masks = [full]
                for i in range(h):
                    if trial % 2:
                        masks.append(rng.getrandbits(m))
                    else:
                        small = 1 << rng.randrange(m)
                        masks.append(small ^ (full if i % 2 else 0))
                vectors = [path_matrix(m,v) for v in masks]
                target = (k+h)//(h+1)
                lost = elim = 0
                while True:
                    combinations = [[combine(v,c) for v in zip(*vectors)] for c in range(1 << (h+1))]
                    low = next((mat for mat in combinations if 0 < len(basis(mat)) < target),None)
                    if low is None:
                        break
                    source = left_kernel(low)
                    lost += len(low)-len(source)
                    elim += 1
                    vectors = [[combine(mat,v) for v in source] for mat in vectors]
                assert elim <= h and lost <= h*(target-1) and len(basis(vectors[0])) >= target
                relations = [c for c,mat in enumerate(combinations) if not any(mat)]
                assert any(all(not parity(c & delta) for c in relations) for delta in range(1,1 << (h+1),2))
                trials += 1
    sequences = 0
    for blocks in range(1,13):
        possibilities = set()
        for raw in range(1 << (blocks-1)):
            flags = [0]+[(raw >> i)&1 for i in range(blocks-1)]+[1]
            lo,hi = 0,blocks
            while hi-lo > 1:
                mid = (lo+hi)//2
                if flags[lo] != flags[mid]:
                    hi = mid
                else:
                    lo = mid
            assert flags[lo] != flags[hi]
            possibilities.add(lo)
            sequences += 1
        assert possibilities == set(range(blocks))
    return {'varying_output_rank_restrictions':trials,'maximum_quadratic_outputs':8,
            'all_prefix_disagreement_sequences_through_twelve_blocks':sequences}


def row_spaces(n, codim):
    for pivot in combinations(range(n),codim):
        free = [(i,j) for i,p in enumerate(pivot) for j in range(p+1,n) if j not in pivot]
        for setting in range(1 << len(free)):
            rows = [1 << i for i in pivot]
            for b in bits(setting):
                i,j = free[b]
                rows[i] |= 1 << j
            yield rows


def point_hyperplanes(n):
    return [sum(parity(w & v) << v for v in range(1 << n)) for w in range(1 << n)]


def all_cells(n, codim, hypers):
    for rows in row_spaces(n, codim):
        cells = [(1 << (1 << n))-1]
        for row in rows:
            cells = [s for c in cells for s in (c & hypers[row], c & ~hypers[row])]
        yield from cells


def graph_rank(mask):
    if not mask:
        return -1
    points = bits(mask)
    origin = next(points)
    return len(basis(x ^ origin for x in points))


def field_product(a,b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 0b1011
    return value


def graph_audit():
    n = 9
    graph = sum(1 << (a | (b<<3) | (field_product(a,b)<<6)) for a in range(8) for b in range(8))
    for coeff in range(1,8):
        rows = [sum(parity(coeff & field_product(1 << i,1 << j)) << j for j in range(3)) for i in range(3)]
        assert len(basis(rows)) == 3
    hypers = point_hyperplanes(n)
    counts = []
    for codim in (0,1,2):
        seen = 0
        for cell in all_cells(n,codim,hypers):
            assert graph_rank(graph & cell) == n-codim
            seen += 1
        counts.append(seen)
    sharp = sum(1 << v for v in range(1 << n) if v & 7 == 0)
    assert graph_rank(sharp) == 6 and graph_rank(sharp & graph) == 3
    return {'all_cells_by_codimension':counts,'codimension_3_control_cell_and_graph_dimensions':[6,3]}


@cache
def hull(mask):
    if not mask:
        return 0
    pts = bits(mask)
    origin = next(pts)
    span = [origin]
    for row in basis(v ^ origin for v in pts):
        span += [v ^ row for v in span]
    return sum(1 << v for v in span)


def frontier_audit():
    # Four source bits, then s,u,v; the right total is 1+s. Queries mix these coordinates.
    m,n = 3,4
    width = n+3
    full = (1 << (1 << width))-1
    parity_masks = point_hyperplanes(width)
    rng = Random(19)
    totals = Counter()
    for a in range(8):
        for b in range(8):
            left = right = 0
            for point in range(1 << width):
                x = point & 15
                products = x & (x >> 1)
                s,u,v = ((point >> (n+i)) & 1 for i in range(3))
                left |= int((s,u) == (parity(products),parity(products&a))) << point
                right |= int((1^s,v) == (parity(products),parity(products&b))) << point
            k = 2
            r = min(k, len(basis(path_matrix(m,b))),len(basis(path_matrix(m,b^7))))
            for order in range(2):
                queries = list(range(1,1 << width))
                rng.shuffle(queries)
                frontier_mass = frontier_count = leaves = 0
                def visit(cell, reached, seq):
                    nonlocal frontier_mass,frontier_count,leaves
                    while cell:
                        cell = hull(cell & left)
                        next_cell = hull(cell & right)
                        if next_cell != cell and not reached:
                            reached = True
                            projected = {((v & 31) | ((v >> 1) & 32)) for v in bits(cell)}
                            assert projected and len(projected).bit_count() == 1
                            codim = n+2-(len(projected).bit_length()-1)
                            assert codim >= r
                            mass = (cell & left).bit_count()
                            assert Fraction(mass,left.bit_count()) <= Fraction(1,1 << codim) + Fraction(1,1 << (k+1))
                            frontier_mass += mass
                            frontier_count += 1
                        if not next_cell or next_cell == cell:
                            cell = next_cell
                            break
                        cell = next_cell
                    if not cell:
                        leaves += 1
                        return
                    for j in range(seq,len(queries)):
                        h = parity_masks[queries[j]]
                        up,down = cell & h, cell & ~h
                        if up and down:
                            visit(up,reached,j+1)
                            visit(down,reached,j+1)
                            return
                    raise AssertionError('a singleton cannot satisfy both evaluators')
                visit(full,False,0)
                assert frontier_mass == left.bit_count() and 1 <= frontier_count <= leaves
                totals['complete_mixed_query_trees'] += 1
                totals['first_right_shrinks'] += frontier_count
                totals['tree_leaves'] += leaves
    return dict(totals)


def main():
    result = {'path_rank_audit':rank_audit(), 'regularization_eliminations':quadratic_regularization(),
              'full_rank_three_output_graph':graph_audit(), 'left_honest_frontiers':frontier_audit(),
              'rank_seven_polar_filter':restricted_polar_audit(),'projector_count':projector_counts(),
              'many_sketches':many_sketch_checks()}
    print(json.dumps({'status':'passed',**result},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
