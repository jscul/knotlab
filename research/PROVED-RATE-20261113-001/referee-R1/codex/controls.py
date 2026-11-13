"""Independent finite controls for the fresh referee algorithms.

Only the new referee implementation is imported. No producer module is loaded.
Karp is checked against explicit simple-cycle enumeration; block operations are
checked with direct sets of assignments rather than the implementation's bitsets.
"""
from collections import Counter
from fractions import Fraction
import itertools
import random
import time

import recompute as R


def enumerate_cycle_mean(graph):
    means = []
    for root in range(len(graph)):
        def visit(u, used, cost):
            for v, weight in graph[u]:
                if v == root:
                    means.append(Fraction(cost + weight, len(used)))
                elif v > root and v not in used:
                    visit(v, used | {v}, cost + weight)
        visit(root, {root}, 0)
    return min(means, default=None)


def graph_rate(graph):
    good, comps, _ = R.trim_and_scc(graph, [0] * len(graph))
    rates = [R.karp(graph, comp) for comp in comps]
    return min((rate for rate in rates if rate is not None), default=None)


def direct_image(definitions, F, G, W, terminal):
    k, local_count, calls = definitions[0]
    # Explicit boundary truth sets, independent of the bitset operations.
    boundary = set(range(8))
    def allowed(a, relation, end):
        first = True
        for name, args in calls:
            value = tuple((a >> x) & 1 for x in args)
            encoded = sum(b << i for i, b in enumerate(value))
            if name == 'K' and len(set(value)) == 1:
                return False
            if name == 'SELF':
                if (end or not first) and encoded not in relation:
                    return False
                first = False
        return True
    while True:
        new = {a & 7 for a in range(1 << (k + local_count)) if allowed(a, boundary, True)}
        if new == boundary:
            break
        boundary = new
    assignments = [a for a in range(1 << (k + local_count)) if allowed(a, boundary, terminal)]
    ray = next(args for name, args in calls if name == 'SELF')

    def transform(mask, values, ignored=None):
        output = set()
        for a in assignments:
            if not ((mask >> (a & 7)) & 1):
                continue
            if any(i != ignored and ((a >> w) & 1) != values[i] for i, w in enumerate(W)):
                continue
            output.add(0 if terminal else sum(((a >> x) & 1) << j for j, x in enumerate(ray)))
        return sum(1 << x for x in output)

    newF, newG = set(), set()
    for values in itertools.product((0, 1), repeat=len(W)):
        newF.update(transform(mask, values) for mask in F)
        newG.update(transform(mask, values) for mask in G)
        for ignored in range(len(W)):
            newG.update(transform(mask, values, ignored) for mask in F)
    return newF, newG, sum(1 << x for x in boundary)


def main():
    started = time.monotonic()
    rng = random.Random(20261113)
    out = dict(seed=20261113, cycle_cases=0, cycle_disagreements=[], block_cases=0, block_disagreements=[])
    for n in range(1, 7):
        for _ in range(35):
            graph = [[(v, rng.randrange(5)) for v in range(n) if rng.random() < .32] for u in range(n)]
            a, b = graph_rate(graph), enumerate_cycle_mean(graph)
            out['cycle_cases'] += 1
            if a != b:
                out['cycle_disagreements'].append(dict(graph=graph, karp=str(a), enumerated=str(b)))
    half = [[(1, 0)], [(0, 1)]]
    seventh = [[((u + 1) % 7, int(u == 6))] for u in range(7)]
    out['exact_fraction_controls'] = dict(half=str(graph_rate(half)), seventh=str(graph_rate(seventh)))
    assert graph_rate(half) == Fraction(1, 2)
    assert graph_rate(seventh) == Fraction(1, 7)
    mutated = [[(1, 0)], [(0, 3)]]
    out['weight_mutation_rejects_old_rate'] = graph_rate(mutated) != graph_rate(half)

    families = R.family_definitions()
    for idx in (318, 130, 1042):
        definitions = families[idx]
        dp = R.FreshDP(definitions)
        for terminal, ops in ((False, dp.middle_ops), (True, dp.close_ops)):
            for op in ops:
                for _ in range(8):
                    F = set(rng.sample(range(256), rng.randrange(1, 6)))
                    G = set(rng.sample(range(256), rng.randrange(5)))
                    state = (sum(1 << x for x in F), sum(1 << x for x in G))
                    a = op.apply(state)
                    nF, nG, boundary = direct_image(definitions, F, G, op.W, terminal)
                    b = (sum(1 << x for x in nF), sum(1 << x for x in nG))
                    out['block_cases'] += 1
                    if a != b or boundary != dp.limit_relation:
                        out['block_disagreements'].append(dict(idx=idx, W=op.W, terminal=terminal, state=state, ours=a, direct=b))
        # Start operations include ports and must also preserve forgotten-member semantics.
        allowed_mid = [a for a in dp.assignments if dp.permitted(a, dp.limit_relation, False)]
        for W in ((0,), (0, 3), tuple(range(dp.V))):
            op = R.Operation(W, allowed_mid, dp.ray, False)
            a = op.apply((1 << 255, 0))
            nF, nG, _ = direct_image(definitions, {255}, set(), W, False)
            b = (sum(1 << x for x in nF), sum(1 << x for x in nG))
            out['block_cases'] += 1
            if a != b:
                out['block_disagreements'].append(dict(idx=idx, W=W, ours=a, direct=b))

    cases = {
        'positive_exit_needed': (
            [[(0, 0), (1, 1)], [(2, 0)], [(2, 0)]], [R.INF, 1, R.INF], {0: 1}, False, True),
        'zero_two_cycle_one_accept': (
            [[(1, 0)], [(0, 0)]], [1, R.INF], {0: 1}, False, False),
        'zero_two_cycle_both_accept': (
            [[(1, 0)], [(0, 0)]], [1, 1], {0: 1}, True, True),
        'positive_detour_repairs_odd_residue': (
            [[(1, 0)], [(0, 0), (1, 1)]], [1, R.INF], {0: 1}, False, True),
    }
    out['boundedness_controls'] = {}
    for name, (graph, closes, starts, expected_sufficient, expected_exact) in cases.items():
        good, _, _ = R.trim_and_scc(graph, closes)
        sufficient, cycles = R.bounded_test(graph, closes, good)
        exact = R.exact_eventual_bound(graph, closes, starts, good, cycles)
        assert sufficient['bounded_all'] == expected_sufficient, name
        assert exact['eventually_bounded'] == expected_exact, name
        out['boundedness_controls'][name] = dict(sufficient=sufficient, exact=exact, L_1_to_12=R.replay(graph, closes, starts, 12))
    out['rejected_wrong_necessity_claim'] = (
        not out['boundedness_controls']['positive_exit_needed']['sufficient']['bounded_all']
        and out['boundedness_controls']['positive_exit_needed']['exact']['eventually_bounded'])
    out['rejected_wrong_zero_mean_sufficiency'] = not out['boundedness_controls']['zero_two_cycle_one_accept']['exact']['eventually_bounded']
    assert not out['cycle_disagreements'] and not out['block_disagreements']
    out['seconds'] = time.monotonic() - started
    R.dump(R.HERE / 'controls.json', out)
    print({k: v for k, v in out.items() if k not in ('boundedness_controls',)})


if __name__ == '__main__':
    main()
