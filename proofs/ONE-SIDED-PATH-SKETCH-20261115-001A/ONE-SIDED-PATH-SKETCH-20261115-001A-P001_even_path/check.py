#!/usr/bin/env python3
"""Independent finite gates and literal path replays for a one-sided sketch."""
import json
from collections import Counter
from functools import cache
from itertools import combinations
from pathlib import Path

import pinned_six_check


def require(test, reason):
    if not test:
        raise AssertionError(reason)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            i = x.bit_length() - 1
            if i not in pivots:
                pivots[i] = x
                break
            x ^= pivots[i]
    return len(pivots)


def xor(rows):
    answer = 0
    for v in rows:
        answer ^= v
    return answer


def form_table(n, term_masks):
    return sum((sum((x & m) == m for m in term_masks) % 2) << x for x in range(1 << n))


def half_rank(n, tab):
    def value(x):
        return tab >> x & 1
    return rank([sum((value(0) ^ value(1 << i) ^ value(1 << j) ^ value((1 << i) ^ (1 << j))) << j
                     for j in range(n)) for i in range(n)]) // 2


@cache
def hull(table):
    if not table:
        return 0
    points = bits(table)
    o = next(points)
    span = {0}
    for point in points:
        v = point ^ o
        if v not in span:
            span |= {w ^ v for w in span}
    return sum(1 << (o ^ w) for w in span)


def close(cell, left, right, trace=False):
    sizes = [cell.bit_count()]
    while cell:
        after = hull(cell & left) & hull(cell & right)
        if after == cell:
            break
        cell = after
        sizes.append(cell.bit_count())
    return sizes if trace else cell


def four_variable_gate():
    n = 4
    all_x, all_xs = (1 << 16) - 1, (1 << 32) - 1
    q = form_table(4, [3, 12])
    right = q | ((all_x ^ q) << 16)
    question = [sum(((w & form).bit_count() % 2) << w for w in range(32)) for form in range(1,32)]
    terms = [0] + [1 << i for i in range(4)] + [1 << i | 1 << j for i,j in combinations(range(4),2)]
    tables = [form_table(n,[m]) for m in terms]
    positive = Counter()
    short = Counter()
    for code in range(1 << len(terms)):
        f = xor(tables[i] for i in bits(code))
        if half_rank(n,q^f) != 2:
            continue
        allowed = all_x ^ f
        left = (allowed & (all_x ^ q)) | ((allowed & q) << 16)
        cell = close(all_xs,left,right)
        if not cell:
            cost = 1
        elif any(cell & row and cell & ~row and not close(cell & row,left,right)
                 and not close(cell & ~row,left,right) for row in question):
            cost = 2
        else:
            cost = 3  # lower bound, sufficient for the finite gate
        r = half_rank(n,f)
        if allowed.bit_count() > 8:
            require(cost == 3, ("positive four-bit counterexample",code))
            positive[r] += 1
        if cost <= 2:
            short[r,allowed.bit_count(),cost] += 1
    require(short[1,4,1] > 0 and short[1,8,2] > 0 and short[2,6,2] > 0, "low-bias short controls")
    return {"all_quadratics":2048,"positive_with_nonsingular_sum_by_F_half_rank":dict(positive),
            "all_short_by_F_half_rank_zero_set_size_and_leaves":{str(k):v for k,v in short.items()}}


def six_variable_gate():
    report = pinned_six_check.audit()
    expected = {(0,3):2,(1,3):2520,(2,3):249984,(3,3):737280}
    require(not report["failures"] and report["census"] == {str(k):v for k,v in expected.items()},
            "positive six-variable fixed-output gate")
    return {"all_alternating_matrices":1 << 15,"checked_positive_cases":sum(expected.values()),
            "by_F_half_rank_and_cost_at_least":report["census"],"relevant_generator_orbits":len(report["orbits"])}


def compare_pencils(k):
    # Even reports are rows and odd reports columns. J is the one-based even-edge matrix.
    identity = [1 << i for i in range(k)]
    J = [0] + [1 << (i-1) for i in range(1,k)]
    Q = [u ^ v for u,v in zip(identity,J)]
    def multiply(left, right):
        return [xor(right[j] for j in bits(row)) for row in left]
    inv = [sum(1 << j for j in range(i+1)) for i in range(k)]
    require(multiply(Q,inv) == identity and multiply(inv,Q) == identity, "bipartite total inverse")
    operator = multiply(inv,J)
    power = identity
    ranks = []
    for _ in range(k+1):
        ranks.append(rank(power))
        power = multiply(power,operator)
    require(ranks == list(range(k,-1,-1)), "wrong Jordan length")
    require([rank(Q),rank(J),rank([q^j for q,j in zip(Q,J)])] == [k,k-1,k], "literal bipartite ranks")
    return {"edges":2*k-1,"half_ranks":[k,k-1,k],"Jordan_power_ranks":ranks,
            "minimum_leaves":2**k,"minimum_worst_depth":k}


def restrict_edges(m, edge_mask, pins):
    constant = 0
    linear = 0
    quadratic = set()
    for i in range(m):
        if not edge_mask >> i & 1:
            continue
        u,v = i,i+1
        if u in pins and v in pins:
            constant ^= pins[u] & pins[v]
        elif u in pins:
            if pins[u]:
                linear ^= 1 << v
        elif v in pins:
            if pins[v]:
                linear ^= 1 << u
        else:
            quadratic.add((u,v))
    return constant,linear,quadratic


def early_tree():
    # Reduced ambient bits a,b,c,d,s,u, with t=1+s already eliminated.
    all_points = (1 << 64) - 1
    left = right = matched = 0
    for w in range(64):
        a,b,c,d,s,u = [(w >> j) & 1 for j in range(6)]
        q = (a & b) ^ (b & c) ^ (c & d)
        if s == q and u == b*c:
            left |= 1 << w
        if s != q:
            right |= 1 << w
        if s == q:
            matched |= 1 << w
    def pin(cell, form, value):
        return sum(1 << p for p in bits(cell) if (form & p).bit_count()%2 == value)
    branches = [((32,1),),((32,0),(6,0)),((32,0),(6,1),(2,0)),((32,0),(6,1),(2,1))]
    trace = []
    for branch in branches:
        cell = all_points
        for linear,value in branch:
            cell = pin(close(cell,left,right),linear,value)
        sizes = close(cell,left,right,True)
        require(sizes[-1] == 0, "genuine unbalanced branch failed to close")
        trace.append({"questions":list(map(list,branch)),"last_hull_sizes":sizes})
    require(close(all_points,left,matched) and (left&matched).bit_count()==16, "matched charge")
    n,m = 18,17
    full = (1 << m)-1
    even = sum(1 << i for i in range(1,m,2))
    coordinates = list(range(4,17,2))
    observed = Counter()
    for pins_value in range(128):
        pins = {j:(pins_value >> i) & 1 for i,j in enumerate(coordinates)}
        q0,q1,q2 = restrict_edges(m,full,pins)
        a0,a1,a2 = restrict_edges(m,even,pins)
        require(q2 == {(0,1),(1,2),(2,3)} and a2 == {(1,2)} and not(q0 or a0), "raw tail recoding")
        free = [j for j in range(n) if j not in pins]
        fixed = sum(v << j for j,v in pins.items())
        for p in range(1 << len(free)):
            x = fixed | sum(((p >> i)&1) << j for i,j in enumerate(free))
            rawq = (x & (x>>1) & full).bit_count()%2
            rawa = (x & (x>>1) & even).bit_count()%2
            qcore = (x & (x>>1) & 7).bit_count()%2
            acore = (x>>1) & (x>>2) & 1
            require(rawq == qcore ^ ((x&q1).bit_count()%2) and rawa == acore ^ ((x&a1).bit_count()%2),
                    "literal raw products failed to match the reduced problem")
            observed[pins_value,acore] += 1
    require(all(observed[i,0] == 1536 and observed[i,1] == 512 for i in range(128)), "exact nu weights")
    for v in range(1 << 9):
        pins = {i:(v >> (i//2)) & 1 for i in range(0,n,2)}
        require(not restrict_edges(m,full,pins)[2], "balanced path upper bound")
    return {"original_pinned_coordinates":coordinates,"all_source_assignments":1 << n,
            "balanced_tree_leaves":512,"balanced_tree_depth":9,"unbalanced_leaves_by_total_depth":{"8":128,"9":128,"10":256},
            "nu_numerators_per_sketch_half_over_512":[3,1],"unbalanced_tail_closures":trace}


def pinned_hull_control():
    # Nonspanning joint levels in the doubly pinned case still can have live saturation.
    all_x = (1 << 64)-1
    base = form_table(6,[3,12,48])
    fixtures = [(0, base, form_table(6,[3,9,6])),
                (1, all_x ^ base, form_table(6,[0,1,2,17,6]))]
    out = {}
    for expected,q,f in fixtures:
        require(half_rank(6,f)==2 and half_rank(6,q^f)==3, "raw pinned-pencil control")
        z = (all_x ^ q) & (all_x ^ f)
        projected = hull(z)
        codim = 6-(projected.bit_count().bit_length()-1)
        require(codim == expected and close(all_x,z,q) == projected and hull(projected & q)==projected,
                "pinned nonempty fixed space")
        out[str(codim)] = {"left_points":z.bit_count(),"fixed_space_size":projected.bit_count(),
                           "left_AND_right_true":(z&q).bit_count()}
    return out


def main():
    result = {"status":"passed","four_variable_gate":four_variable_gate(),"six_variable_gate":six_variable_gate(),
              "alternating_pencils":[compare_pencils(k) for k in (3,4,5,8,9,10,12)],
              "literal_17_edge_trees":early_tree(),"nontrivial_pinned_hulls":pinned_hull_control()}
    result = json.loads(json.dumps(result))
    saved = Path(__file__).with_name("checks.json")
    if saved.exists():
        require(result == json.loads(saved.read_text()), "mismatch with the saved certificate")
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
