"""Replay the M-to-one branch using the published law and a second group checker."""

from collections import Counter
from contextlib import nullcontext
from itertools import product
import json
from pathlib import Path
import sys
from unittest.mock import patch

import networkx as nx

from boundary_checks import ROOT, extend, verify

POLICY = 'JOIN-GROWTH-20261118-001B'
sys.path.insert(0, str(ROOT / 'experiments' / POLICY / (POLICY + '-E001_joins')))
import fastlib


def build(m, shields=None, use_two_leaves=False):
    stars = []
    next_name = 0

    def site():
        stars.append(set())
        return len(stars) - 1

    def add(*holders):
        nonlocal next_name
        for u in holders:
            stars[u].add(next_name)
        next_name += 1

    if shields is None:
        poles = [site(), site()]
        core = [*poles, site(), site()]
        for i, u in enumerate(core):
            for v in core[:i]:
                add(u, v)
    else:
        nanchors, s, l = shields
        anchors = [site() for _ in range(nanchors)]
        hubs = [site(), site()]
        tests = [site() for _ in range(4)]
        poles = [site() for _ in range(2 * s)]
        for i, u in enumerate(tests):
            for _ in range(l):
                add(u, anchors[0])
                add(u, hubs[i // 2])
            for v in anchors[1:]:
                add(u, v)
        for i, u in enumerate(poles):
            for v in anchors:
                add(u, v)
            for _ in range(m):
                add(u, hubs[i // s])
    fixed = next_name
    for pole in poles:
        rs = [site() for _ in range(m)]
        z = site()
        u, v = rs[1:3] if use_two_leaves else (site(), site())
        for r in rs:
            add(pole, r)
        for i, r in enumerate(rs[1:]):
            if not use_two_leaves or r not in (u, v):
                add(r, u if i % 2 == 0 else v)
            add(r)
            add(r)
        add(u, z)
        add(v, z)
        add(u, v)
        add(z)
        for _ in range(m - 1):
            add(rs[0])
    return list(map(frozenset, stars)), poles, fixed


def check(m, shields=None, use_two_leaves=False):
    start, poles, fixed = build(m, shields, use_two_leaves)
    group_engine = (patch.object(extend.C.F.Presentation, 'groups_among', fastlib.groups_among)
                    if m >= 12 else nullcontext())
    with group_engine:
        first = extend.grow1(start)
        second = extend.grow1(first)
    stages = [verify.Arrangement.parse([sorted(s) for s in state])
              for state in (start, first, second)]
    audits = [verify.start_audit(stage) for stage in stages]
    assert all(row['census_open_legal'] for row in audits)
    assert all(row['meets_once'] == (shields is None) for row in audits)
    assert all(len(s) >= 3 for s in stages[0].stars)
    for previous, current in zip(stages, stages[1:]):
        assert current.stars[:len(previous.stars)] == previous.stars
    expected = [Counter({(2, 1, 1): len(poles) * (m - 1), (m, 1, 1): len(poles)}),
                Counter({(m, 1, 0): len(poles)})]
    histogram = []
    for previous, current, wanted in zip(stages, stages[1:], expected):
        records = verify.round_replay(previous, current)
        assert all(not row['implied'] for row in records)
        actual = Counter((len(r['taken']), len(r['fresh']), r['demand']) for r in records)
        assert actual == wanted
        histogram.append([dict(parents=p, fresh=f, demand=d, sites=n)
                          for (p, f, d), n in sorted(actual.items())])
    prices = []
    for stage in stages[1:]:
        network = nx.Graph()
        ends, _, outside = stage.holder_graph()
        for name, (u, v) in ends.items():
            if name < fixed:
                continue
            if network.has_edge(u, v):
                network[u][v]['capacity'] += 1
            else:
                network.add_edge(u, v, capacity=1)
        # Beyond the outside the other branches attach only to the outside.
        prices.append(sorted(set(int(nx.minimum_cut_value(network, pole, outside))
                                 for pole in poles)))
    assert prices == [[m], [1]]
    widths = [[len(stage.stars), len(stage.labels)] for stage in stages]
    if shields is None:
        expected_start = [4 + len(poles) * (m + 3), 6 + len(poles) * 5 * m]
    else:
        nanchors, s, l = shields
        expected_start = [nanchors + 6 + 2 * s * (m + 4),
                          8 * l + 4 * (nanchors - 1) + 2 * s * (6 * m + nanchors)]
    if use_two_leaves:
        expected_start = [value - 2 * len(poles) for value in expected_start]
    assert widths[0] == expected_start
    assert widths[1] == [old + len(poles) * m for old in widths[0]]
    assert widths[2] == [old + len(poles) for old in widths[1]]
    return dict(M=m, poles=len(poles), shield_parameters=shields, two_leaves_as_witnesses=use_two_leaves,
                first_group_engine=('JOIN-GROWTH maximal cliques' if m >= 12 else 'FRESH-COUNT subsets'),
                full_projection_at_all_three_ages=True, no_forced_distinctions_at_all_three_ages=True,
                start_meets_once=audits[0]['meets_once'], junctions_and_width=widths,
                distinct_branch_terminal_minima=prices, parent_fresh_demand=histogram)


def pair_readings(i, s, l, m, attachment_price):
    """Exact connected cuts through two named pairs with the measured branch price."""
    h0, h1, outside, v = range(4)
    tests = list(range(4, 8))
    weak = list(range(8, 8 + i - 1))
    left = list(range(weak[-1] + 1, weak[-1] + 1 + s))
    right = list(range(left[-1] + 1, left[-1] + 1 + s))
    adjacent = [0] * (right[-1] + 1)

    def link(a, b):
        adjacent[a] |= 1 << b
        adjacent[b] |= 1 << a

    for j, t in enumerate(tests):
        for u in [h0 if j < 2 else h1, v, *weak]:
            link(t, u)
    for u, shield in ((h0, left), (h1, right)):
        for sh in shield:
            for a in [u, outside, v, *weak]:
                link(sh, a)
    universe = (1 << len(adjacent)) - 1
    answers = [float('inf'), float('inf')]
    cases = 0
    # The individual weak anchors and shields of each color are interchangeable.
    for h, exterior, strong, *mids in product((0, 1), repeat=7):
        qualifies = (mids[0] and mids[1], mids[1] and mids[2] != h)
        if not any(qualifies):
            continue
        f = sum(mids)
        heavy = l * (mids[0] + mids[1] + sum(b != h for b in mids[2:])
                     + sum(b != strong for b in mids))
        for w, n0, n1 in product(range(i), range(s + 1), range(s + 1)):
            cases += 1
            n = n0 + n1
            cost = (heavy + w * (4 - f) + (i - 1 - w) * f
                    + m * (n0 + (s - n1 if h else n1))
                    + (2 * s - n if strong else n)
                    + w * (2 * s - n) + (i - 1 - w) * n
                    + attachment_price * (2 * s - n if exterior else n))
            if all(not valid or cost >= best for valid, best in zip(qualifies, answers)):
                continue
            sites = [u for u, color in zip([h1, outside, v, *tests],
                                          [h, exterior, strong, *mids]) if color]
            shore = sum(1 << u for u in sites + weak[:w] + left[:n0] + right[:n1])
            if verify.connected(shore, adjacent) and verify.connected(universe ^ shore, adjacent):
                for j, valid in enumerate(qualifies):
                    if valid:
                        answers[j] = min(answers[j], cost)
    expected_image = 4 * l + 2 * s + 2 * (i - 1)
    assert answers == [2 * l + s * (i + 1) if attachment_price == 1 else expected_image,
                       expected_image]
    return dict(I=i, s=s, L=l, M=m, branch_price=attachment_price,
                tested_orbits_containing_a_marked_pair=cases,
                same_hub_minimum=answers[0], image_minimum=answers[1])


def run():
    return {'two_branches_on_simple_core': [check(m) for m in (3, 4, 5, 8, 28)],
            'complete_shield_starts': [check(4, (3, 2, 4)), check(28, (5, 9, 28))],
            'two_leaf_variant': [check(3, use_two_leaves=True), check(28, (5, 9, 28), True),
                                 check(23, (5, 8, 25), True)],
            'exact_named_pairs_at_both_ages': [pair_readings(5, s, l, m, price)
                                               for s, l, m in ((9, 28, 28), (8, 25, 23))
                                               for price in (m, 1)]}


if __name__ == '__main__':
    report = json.dumps(run(), indent=2) + '\n'
    path = Path(__file__).with_suffix('.json')
    if sys.argv[1:] == ['--check']:
        assert path.read_text() == report
    else:
        path.write_text(report)
