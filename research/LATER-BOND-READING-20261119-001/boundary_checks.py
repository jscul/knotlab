"""Check prescribed complete-round terminal cuts and exact clipped readings."""

from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAW = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / LAW / (LAW + "-E001_extend")))
import extend

AUDIT = "GROWN-END-SWAP-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / AUDIT / (AUDIT + "-E001_reached")))
import verify


def source(m, k):
    stars = [set() for _ in range(4)]
    name = 0

    def fresh_site():
        stars.append(set())
        return len(stars) - 1

    def add(*owners):
        nonlocal name
        for owner in owners:
            stars[owner].add(name)
        name += 1

    for x, y in ((0, 2), (1, 2), (0, 3), (1, 3), (2, 3)):
        add(x, y)

    def unit(pole):
        u, v, w = (fresh_site() for _ in range(3))
        for pair in ((pole, u), (u, v), (u, w), (v, w)):
            add(*pair)
        add(v)
        add(w)

    def shrink(pole, val):
        if val == 1:
            unit(pole)
        elif val == 2:
            u, v, s, t, w = (fresh_site() for _ in range(5))
            for pair in ((pole, u), (pole, v), (u, s), (u, t), (v, s), (v, w), (t, w)):
                add(*pair)
            for site in (s, s, t, w):
                add(site)
        elif val == 3:
            for _ in range(3):
                leaf = fresh_site()
                add(pole, leaf)
                add(leaf)
                add(leaf)
        else:
            r = {pair: fresh_site() for pair in combinations(range(val), 2)}
            for subset in combinations(range(val), 3):
                t = fresh_site()
                add(pole, t)
                for pair in combinations(subset, 2):
                    add(r[pair], t)
            for site in r.values():
                add(site)
                add(site)

    shrink(0, m - k + 1)
    for _ in range(k - 1):
        unit(0)
    for _ in range(m):
        unit(1)
    return list(map(frozenset, stars))


def terminal_cut(stage):
    network = nx.Graph()
    outside = len(stage)
    for bit, owners in extend.L.owners(stage).items():
        if bit < 5:
            continue
        a, b = owners if len(owners) == 2 else (owners[0], outside)
        if network.has_edge(a, b):
            network[a][b]['capacity'] += 1
        else:
            network.add_edge(a, b, capacity=1)
    return int(nx.minimum_cut_value(network, 0, 1, capacity='capacity'))


def certified(m, k):
    raw = [source(m, k)]
    for _ in range(2):
        raw.append(extend.grow1(raw[-1]))
    stages = [verify.Arrangement.parse([sorted(row) for row in stage]) for stage in raw]
    start = verify.start_audit(stages[0])
    assert start['census_open_legal'] and start['meets_once']
    assert all(len(row) >= 3 for row in raw[0])
    records = [verify.round_replay(a, b) for a, b in zip(stages, stages[1:])]
    assert all(not row['implied'] for new in records for row in new)
    assert all(len(row['fresh']) >= 1 for new in records for row in new)
    assert all(stages[i].stars[:4] == stages[0].stars[:4] for i in (1, 2))
    assert all(stages[i].live.isdisjoint(range(4)) for i in (0, 1, 2))
    assert (terminal_cut(raw[1]), terminal_cut(raw[2])) == (m, k)
    return {'from': m, 'to': k, 'junctions': list(map(len, raw)),
            'widths': [len(stage.labels) for stage in stages],
            'parent_fresh': [[list(pair) for pair in sorted((len(row['taken']), len(row['fresh'])) for row in new)]
                             for new in records]}


def three_terminal_control():
    terminals = (0, 1, 2)
    rows = []
    for profile in ((4, 2, 3), (3, 2, 4)):
        # Intact parallel bundles to a single ordinary center. Closing the
        # three Q spokes at the exterior gives the full two-star calculation.
        stars = [set() for _ in range(4)]
        next_bit = 0
        x = None
        for terminal, weight in enumerate(profile):
            for _ in range(weight):
                stars[terminal].add(next_bit)
                stars[3].add(next_bit)
                if terminal == 1 and x is None:
                    x = next_bit
                next_bit += 1
        qbits = tuple(range(next_bit, next_bit + 3))
        for terminal, bit in zip(terminals, qbits):
            stars[terminal].add(bit)
        bonds = [set(row) for row in extend.L.bonds(stars)]
        marked, pure = [], []
        for k in range(4):
            for ys in combinations(qbits, k):
                with_x = {x, *ys}
                marked.append(min((len(b) for b in bonds if with_x <= b), default=None))
                if ys:
                    pure.append(min((len(b) for b in bonds if set(ys) <= b), default=None))
        allowed = set([0])
        # a is the lone terminal and x must cross, hence the center is with a
        # and both b,c bundles cross. Check by the two possible center sides.
        relaxed = min(sum(weight for terminal, weight in enumerate(profile)
                          if (terminal in allowed) != center_on_a)
                      for center_on_a in (True, False) if (1 in allowed) != center_on_a)

        simple = [set() for _ in range(4)]
        bit = 0
        def site():
            simple.append(set())
            return len(simple) - 1
        def add(*owners):
            nonlocal bit
            for owner in owners:
                simple[owner].add(bit)
            bit += 1
        for terminal, weight in enumerate(profile):
            add(3, terminal)
            for _ in range(weight - 1):
                pp, rr, ss, tt = (site() for _ in range(4))
                for ends in ((3, pp), (pp, ss), (pp, tt), (rr, ss),
                             (rr, tt), (ss, tt), (rr, terminal)):
                    add(*ends)
        for terminal in terminals:
            u, v, w = (site() for _ in range(3))
            for ends in ((terminal, u), (u, v), (u, w), (v, w)):
                add(*ends)
            add(v)
            add(w)
        simple = list(map(frozenset, simple))
        reached = extend.grow1(simple)
        before, after = [verify.Arrangement.parse([sorted(row) for row in stage]) for stage in (simple, reached)]
        audit = verify.start_audit(before)
        assert audit['census_open_legal'] and audit['meets_once']
        new = verify.round_replay(before, after)
        assert len(new) == 3 and all(len(r['taken']) == 2 and len(r['fresh']) == 1 for r in new)
        rows.append({'ordinary_bundle_weights': profile, 'all_exterior_subsets_with_x': marked,
                     'all_nonempty_pure_exterior_subsets': pure, 'relaxed_a_cost': relaxed,
                     'simple_sites_at_start_and_age_one': [len(simple), len(reached)]})
    assert rows[0]['all_exterior_subsets_with_x'] == rows[1]['all_exterior_subsets_with_x'] == [
        3, 4, 3, 4, None, 4, None, None]
    assert all(row['all_nonempty_pure_exterior_subsets'] == [3] * 7 for row in rows)
    assert [r['relaxed_a_cost'] for r in rows] == [5, 6]
    return rows


def run():
    return {'capacities': [certified(m, k) for m in range(1, 8) for k in range(1, m + 1)],
            'three_terminal_anchor_control': three_terminal_control()}


if __name__ == '__main__':
    report = json.dumps(run(), indent=2) + '\n'
    path = HERE / 'boundary_checks.json'
    if sys.argv[1:] == ['--check']:
        assert path.read_text() == report
    else:
        path.write_text(report)
