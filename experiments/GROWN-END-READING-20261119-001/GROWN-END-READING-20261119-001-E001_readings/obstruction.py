"""Test the two-pole identity and a marked family with three or four poles."""

from collections import Counter
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "obstruction.json"
LAW = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / LAW / (LAW + "-E001_extend")))
import extend

PREVIOUS = "GROWN-END-SWAP-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_reached")))
import verify


def readings(stars):
    bonds = extend.L.bonds(stars)
    return bond_readings(stars, bonds)


def bond_readings(stars, bonds):
    n = len(extend.L.owners(stars))
    undefined = n + 1
    pair = np.full((n, n), undefined, dtype=np.int16)
    triple = np.full((n, n, n), undefined, dtype=np.int16)
    # Diagonals repeat marks and give the corresponding lower-order readings.
    for bond in sorted(bonds, key=len, reverse=True):
        pair[np.ix_(bond, bond)] = len(bond)
        triple[np.ix_(bond, bond, bond)] = len(bond)
    return pair, triple


def hub_source(right_loose, right_links, middle_link):
    """The two closed centers meet every hub. Three further sites meet hub A."""
    r = len(right_loose)
    hubs = tuple(range(r + 1))
    c, d = r + 1, r + 2
    leaves = range(r + 3, r + 6)
    stars = [[] for _ in range(r + 6)]
    bit = 0

    def add(*sites):
        nonlocal bit
        for site in sites:
            stars[site].append(bit)
        bit += 1

    for middle in (c, d):
        for hub in hubs:
            add(hub, middle)
    if middle_link == "direct":
        add(c, d)
    elif middle_link == "two_new":
        e, f = len(stars), len(stars) + 1
        stars.extend([[], []])
        for endpoint in (c, d):
            for relay in (e, f):
                add(endpoint, relay)
        add(e, f)
    for leaf in leaves:
        add(0, leaf)
    for x, y in right_links:
        add(x + 1, y + 1)
    for leaf in leaves:
        add(leaf)
        add(leaf)
    for site, count in enumerate(right_loose, 1):
        for _ in range(count):
            add(site)
    return [frozenset(row) for row in stars]


def canonical_cases(r):
    links = list(combinations(range(r), 2))
    cases = set()
    for extra in product(range(4 if r == 2 else 2), repeat=r):
        if sum(extra) > (4 if r == 2 else 2):
            continue
        loose = tuple(r - 1 + value for value in extra)
        for flags in product((False, True), repeat=len(links)):
            graph = [edge for edge, keep in zip(links, flags) if keep]
            forms = []
            for perm in permutations(range(r)):
                inv = {old: new for new, old in enumerate(perm)}
                renamed = tuple(sorted(tuple(sorted((inv[x], inv[y]))) for x, y in graph))
                forms.append((tuple(loose[j] for j in perm), renamed))
            cases.add(min(forms))
    return sorted(cases)


def wiring_permutations(hubs, n):
    # Two separately permutable central rows, optionally exchanged as blocks.
    # Every other name, including every current live support, is held fixed.
    for top, bottom in product(permutations(range(hubs)), repeat=2):
        for first, second in ((0, hubs), (hubs, 0)):
            yield tuple(first + j for j in top) + tuple(second + j for j in bottom) + tuple(range(2 * hubs, n))


def preserves(table, p):
    axes = tuple(p for _ in table.shape)
    return np.array_equal(table, table[np.ix_(*axes)])


def carries_equations(stars, p):
    source = [sum(1 << j for j in row) for row in stars]
    image = [sum(1 << p[j] for j in row) for row in stars]
    return extend.L.rank(source) == extend.L.rank(source + image)


def run_case(loose, links, middle_link):
    stars = hub_source(loose, links, middle_link)
    r = len(loose)
    initial = verify.Arrangement.parse([sorted(s) for s in stars])
    audit = verify.start_audit(initial)
    assert audit["census_open_legal"] and audit["meets_once"]
    current = extend.grow1(stars)
    assert current is not None
    successor = extend.grow1(current)
    assert successor is not None
    old = len(extend.L.owners(current))
    live, _, _ = extend.reading(current)
    fixed = set().union(*(current[j] for j in live))
    assert not fixed & set(range(2 * (r + 1)))
    # All moved bits are singly represented ordinary meetings. Thus they have
    # no true pair flips, irrespective of the other fixed names.
    owners = extend.L.owners(current)
    ends = Counter(tuple(sorted(v)) for v in owners.values())
    assert all(len(owners[j]) == 2 and ends[tuple(sorted(owners[j]))] == 1 for j in range(2 * (r + 1)))
    pair, triple = readings(current)
    pair_group = [p for p in wiring_permutations(r + 1, old) if preserves(pair, p)]
    full_group = [p for p in pair_group if preserves(triple, p)]
    pair_changes = [p for p in pair_group if not carries_equations(current, p)]
    full_changes = [p for p in full_group if not carries_equations(current, p)]
    result = {
        "right_loose": loose, "extra_right_meetings": links, "center_link": middle_link,
        "stages": [len(stars), len(current), len(successor)], "old_width": old,
        "pair_preservers": len(pair_group), "pair_code_changing": len(pair_changes),
        "pair_triple_preservers": len(full_group), "pair_triple_code_changing": len(full_changes),
    }
    if full_changes:
        next_pair, _ = readings(successor)
        result["candidates"] = []
        for p in full_changes:
            fail = [(x, y) for x, y in combinations(range(old), 2)
                    if next_pair[x, y] != next_pair[p[x], p[y]]]
            result["candidates"].append({"permutation": p, "old_pair_difference": fail[:1]})
    return result


def control():
    stem = "GROWN-END-MEET-ONCE-20261119-001"
    src = ROOT / "artifacts" / stem / (stem + "-E001_rounds") / "structure.json"
    saved = json.loads(src.read_text())
    old = [frozenset(s) for s in saved["start"]]
    marked = extend.grow1(old)
    nxt = extend.grow1(marked)
    assert marked == old + list(map(frozenset, saved["first"]))
    assert nxt == marked + list(map(frozenset, saved["second"]))
    pair, triple = readings(marked)
    p = (1, 0, *range(2, len(pair)))
    assert preserves(pair, p) and not preserves(triple, p)
    assert preserves(triple, tuple(range(len(pair))))
    assert triple[0, 2, 4] == len(pair) + 1 and triple[1, 2, 4] == 5
    after, _ = readings(nxt)
    assert (after[0, 2], after[1, 2]) == (3, 4)
    # An outside anchor also separates a pair in the same four-wire example.
    # All Q names are outside the five-bit fixed piece.
    anchors = [
        [q, int(triple[0, 2, q]), int(triple[1, 2, q])]
        for q in range(5, len(pair)) if triple[0, 2, q] != triple[1, 2, q]
    ]
    assert anchors
    return {"source": str(src.relative_to(ROOT)), "inside_odd_triple": [[0, 2, 4], None],
            "inside_other_triple": [[1, 2, 4], 5], "outside_witnesses": anchors,
            "successor_pair_sizes": [int(after[0, 2]), int(after[1, 2])]}


def port_fixed_isometries(pair, ordinary):
    m = len(pair)
    locked = tuple(range(ordinary, m))
    classes = {}
    for edge in range(ordinary):
        sig = tuple(int(pair[edge, q]) for q in locked) + tuple(sorted(map(int, pair[edge, :ordinary])))
        classes.setdefault(sig, []).append(edge)
    blocks = list(classes.values())
    block_images = []

    def visit(i):
        if i == len(blocks):
            p = list(range(m))
            for block, image in zip(blocks, block_images):
                for before, after in zip(block, image):
                    p[before] = after
            if np.array_equal(pair, pair[np.ix_(p, p)]):
                yield tuple(p)
            return
        for image in permutations(blocks[i]):
            block_images.append(image)
            yield from visit(i + 1)
            block_images.pop()

    yield from visit(0)


def survives_three_poles(wired):
    # Already known biconnected. Deleting any vertex must leave a
    # biconnected graph for the augmented core to be three-connected.
    if min(dict(wired.degree()).values()) < 3:
        return False
    return all(nx.is_biconnected(wired.subgraph(set(wired) - {v})) for v in wired)


def port_tests(limit):
    """Simultaneous drops independently supplied at three or four junctions."""
    totals = Counter()
    examples = []
    hits = []
    unresolved = []
    for graph in nx.graph_atlas_g():
        n = len(graph)
        if n != limit or not nx.is_connected(graph):
            continue
        edges = list(graph.edges)
        e = len(edges)
        for count in (3, 4):
            if count > n:
                continue
            for ports in combinations(range(n), count):
                if any(graph.degree(v) < 3 and v not in ports for v in graph):
                    continue
                wired = graph.copy()
                wired.add_edges_from((v, n) for v in ports)
                if not nx.is_biconnected(wired):
                    continue
                stars = [set() for _ in range(n)]
                for bit, (x, y) in enumerate(edges):
                    stars[x].add(bit)
                    stars[y].add(bit)
                for j, v in enumerate(ports, e):
                    stars[v].add(j)
                bonds = extend.L.bonds(stars)
                m = e + count
                membership = np.zeros((len(bonds), m), dtype=np.int16)
                for j, bond in enumerate(bonds):
                    membership[j, bond] = 1
                variants = np.array(list(product((1, 2, 3), repeat=count)), dtype=np.int16)
                # Each pole's ordinary arity must remain at least three. The
                # 1 -> 1 branch supplies one pole distinction, 2 -> 1 supplies
                # two, and 3 -> 1 supplies three in the literal realizations.
                enabled = np.ones(len(variants), dtype=bool)
                for j, v in enumerate(ports):
                    enabled &= variants[:, j] + graph.degree(v) >= 3
                weights = membership[:, :e].sum(axis=1)[:, None] + membership[:, e:] @ variants.T
                infinity = 2 * m + count + 1
                pair = np.full((len(variants), m, m), infinity, dtype=np.int16)
                cache = {}
                ordinary = np.arange(e)
                for x, y in combinations(range(m), 2):
                    include = (membership[:, x] & membership[:, y]).astype(bool)
                    if np.any(include):
                        pair[:, x, y] = pair[:, y, x] = weights[include].min(axis=0)
                robust = survives_three_poles(wired)
                totals['three_connected_port_arrangements'] += int(robust)
                totals['three_connected_weighted'] += int(enabled.sum()) * int(robust)
                totals['port_arrangements'] += 1
                totals['weighted_arrangements'] += int(enabled.sum())
                totals['tested_transpositions'] += int(enabled.sum()) * e * (e - 1) // 2

                def through(x, y, z):
                    key = tuple(sorted((x, y, z)))
                    if key not in cache:
                        keep = (membership[:, x] & membership[:, y] & membership[:, z]).astype(bool)
                        cache[key] = weights[keep].min(axis=0) if np.any(keep) else infinity
                    return cache[key]

                for a, b in combinations(range(e), 2):
                    others = [v for v in range(m) if v not in (a, b)]
                    both = np.all(pair[:, a, others] == pair[:, b, others], axis=1) & enabled
                    if not np.any(both):
                        continue
                    totals['pair_preserving'] += int(both.sum())
                    # In a simple wired graph, the transposition of two
                    # ordinary names preserves the cut space exactly when
                    # the two-name vector is itself a cut.
                    row_masks = [sum(1 << bit for bit in row) for row in stars]
                    two_cut = extend.L.rank(row_masks + [(1 << a) | (1 << b)]) == extend.L.rank(row_masks)
                    if two_cut:
                        continue
                    totals['pair_preserving_code_changing'] += int(both.sum())
                    if robust:
                        totals['three_connected_pair_preserving_code_changing'] += int(both.sum())
                    witnesses = [v for v in ordinary if v not in (a, b) and pair[0, a, v] != pair[0, b, v]]
                    if witnesses:
                        totals['pair_preserving_next_ordinary_disagreement'] += int(both.sum())
                        if robust:
                            totals['three_connected_pair_preserving_next_disagreement'] += int(both.sum())
                    survivors = both.copy()
                    first_witness = None
                    for z, w in combinations(others, 2):
                        ok = through(a, z, w) == through(b, z, w)
                        if first_witness is None and np.any(survivors & ~np.asarray(ok)):
                            j = np.flatnonzero(survivors & ~np.asarray(ok))[0]
                            first_witness = {
                                'weights': variants[j].tolist(), 'marks': [int(a), int(z), int(w)],
                                'old_marks_image': [int(b), int(z), int(w)],
                            }
                        survivors &= ok
                        if not np.any(survivors):
                            break
                    descriptor = {'ordinary_edges': edges, 'ports': ports, 'swap': [a, b]}
                    if witnesses and first_witness and len(examples) < 3:
                        examples.append(dict(descriptor, ordinary_reading_witness=int(witnesses[0]), **first_witness))
                    totals['triple_preserving_code_changing'] += int(survivors.sum())
                    for j in np.flatnonzero(survivors):
                        item = dict(descriptor, weights=variants[j].tolist())
                        if len(unresolved) < 10:
                            unresolved.append(item)
                        if witnesses:
                            hits.append(dict(item, ordinary_reading_witness=int(witnesses[0])))
                if limit <= 6:
                    for j in np.flatnonzero(enabled):
                        for p in port_fixed_isometries(pair[j], e):
                            totals['all_port_fixed_pair_permutations'] += 1
                            if carries_equations(stars, p):
                                continue
                            totals['all_port_fixed_pair_code_changing'] += 1
                            perm_edges = np.array(p[:e])
                            if not np.array_equal(pair[0, :e, :e], pair[0][np.ix_(perm_edges, perm_edges)]):
                                totals['all_port_fixed_pair_next_disagreement'] += 1
                            for a, b, c in combinations(range(m), 3):
                                before = through(a, b, c)
                                after = through(p[a], p[b], p[c])
                                if np.broadcast_to(before, (len(variants),))[j] != np.broadcast_to(after, (len(variants),))[j]:
                                    break
                            else:
                                totals['all_port_fixed_triple_code_changing'] += 1
                                hits.append({'ordinary_edges': edges, 'ports': ports, 'permutation': p,
                                             'weights': variants[j].tolist(), 'type': 'check later pairs'})
    return {'ordinary_vertices': limit, 'counts': dict(totals),
            'old_triple_rejection_examples': examples, 'code_change_samples': unresolved, 'unrejected': hits}


def branch_fixture(edges, ports, branch_types):
    ordinary = max(max(edge) for edge in edges) + 1
    stars = [[] for _ in range(ordinary)]
    bits = 0

    def add(*sites):
        nonlocal bits
        for j in sites:
            stars[j].append(bits)
        bits += 1

    for edge in edges:
        add(*edge)
    for hub, kind in zip(ports, branch_types):
        first = len(stars)
        if kind == 1:
            stars.append([])
            add(hub, first)
            add(first)
            add(first)
        elif kind == 2:
            stars.extend([[] for _ in range(5)])
            u, v, s, t, w = range(first, first + 5)
            for left, right in ((hub, u), (hub, v), (u, s), (u, t), (v, s), (v, w), (t, w)):
                add(left, right)
            for live in (s, s, t, w):
                add(live)
        else:
            stars.extend([[] for _ in range(3)])
            for leaf in range(first, first + 3):
                add(hub, leaf)
                add(leaf)
                add(leaf)
    return [frozenset(row) for row in stars]


def small_bond(stars, marks, cap):
    # A cycle basis supplies the syndromes of all candidate supports. The
    # minimum over candidates through marks still needs a proper-subset test.
    n, edges = extend.L.graph_of(stars)
    adj = [[] for _ in range(n)]
    for name, a, b in edges:
        adj[a].append((b, name))
        adj[b].append((a, name))
    parent = {0: (-1, -1)}
    todo = [0]
    for a in todo:
        for b, name in adj[a]:
            if b not in parent:
                parent[b] = (a, name)
                todo.append(b)
    tree = {bit for site, bit in parent.values() if bit >= 0}
    symbols = [0] * len(edges)
    cycle = 1
    for name, a, b in edges:
        if name in tree:
            continue
        symbols[name] ^= cycle
        for endpoint in (a, b):
            while endpoint:
                endpoint, edge = parent[endpoint]
                symbols[edge] ^= cycle
        cycle *= 2
    def zero(mask):
        value = 0
        for bit in mask:
            value ^= symbols[bit]
        return value == 0

    rest = sorted(set(range(len(edges))) - set(marks))
    for size in range(len(marks), cap + 1):
        for other in combinations(rest, size - len(marks)):
            support = tuple(marks) + other
            if zero(support) and all(not zero(subset) for k in range(1, size)
                                     for subset in combinations(support, k)):
                return sorted(support)
    return None


def checked_weighted_example():
    edges = [(0, 1), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    ports = (0, 1, 2)
    kinds = (2, 1, 2)
    source = branch_fixture(edges, ports, kinds)
    raw = [source, extend.grow1(source)]
    raw.append(extend.grow1(raw[-1]))
    parsed = [verify.Arrangement.parse([sorted(row) for row in stage]) for stage in raw]
    audit = verify.start_audit(parsed[0])
    assert audit['census_open_legal'] and audit['meets_once']
    for before, after in zip(parsed, parsed[1:]):
        verify.round_replay(before, after)
    central = [set() for _ in range(5)]
    for i, (u, v) in enumerate(edges):
        central[u].add(i)
        central[v].add(i)
    for i, u in enumerate(ports, len(edges)):
        central[u].add(i)
    bonds = extend.L.bonds(central)
    measured = []
    for age, queries in ((1, [(1, 2), (3, 2), (1, 0, 2), (3, 0, 2)]), (2, [(1, 2), (3, 2)])):
        weights = [1] * len(edges) + list(kinds if age == 1 else (1, 1, 1))
        for marks in queries:
            expected = min(sum(weights[q] for q in bond) for bond in bonds if set(marks) <= set(bond))
            witnessed = small_bond(raw[age], marks, expected)
            assert witnessed is not None and len(witnessed) == expected
            measured.append({'age': age, 'marks': marks, 'minimum_size': expected, 'bond': witnessed})
    values = [r['minimum_size'] for r in measured]
    assert values[0] == values[1] and values[2] != values[3] and values[4] != values[5]
    return {'ordinary_edges': edges, 'ports': ports, 'weights': kinds, 'site_counts': list(map(len, raw)),
            'literal_stages': [[sorted(row) for row in stage] for stage in raw], 'minima': measured}


def three_terminal_control():
    terminals = {0, 1, 2}
    left = [(hub, center) for hub in sorted(terminals) for center in (3, 4)] + [(3, 4)]
    right = [(0, 5), (1, 5), (2, 6), (5, 6), (0, 6)]
    combined = left + right
    stars = [{j for j, edge in enumerate(combined) if v in edge} for v in range(6)]
    whole = [set(bond) for bond in extend.L.bonds(stars)]
    infinite = float('inf')

    def feasible(edges, first):
        graph = nx.Graph(edges)
        extra = set(graph) - terminals
        states = {t: [] for t in terminals}
        for t in terminals:
            for k in range(len(extra) + 1):
                for members in combinations(extra, k):
                    one = {t, *members}
                    if not nx.is_connected(graph.subgraph(one)):
                        continue
                    comps = list(nx.connected_components(graph.subgraph(set(graph) - one)))
                    if any(part.isdisjoint(terminals) for part in comps):
                        continue
                    cut = {j for j, (u, v) in enumerate(edges, first) if (u in one) != (v in one)}
                    states[t].append((cut, len(comps) == 1))
        return states

    def cost(items, marks, strict):
        return min((len(cut) for cut, joined in items if (joined or not strict) and marks <= cut),
                   default=infinite)

    ls, rs = feasible(left, 0), feasible(right, len(left))
    total = needs_relaxed = 0
    for k in (2, 3):
        for marked_tuple in combinations(range(len(combined)), k):
            marked = set(marked_tuple)
            x = {j for j in marked if j < len(left)}
            y = marked - x
            if not x or not y:
                continue
            expected = min((len(b) for b in whole if marked <= b), default=infinite)
            strict = min(cost(ls[t], x, True) + cost(rs[t], y, True) for t in terminals)
            joint = min(min(cost(ls[t], x, True) + cost(rs[t], y, False),
                            cost(ls[t], x, False) + cost(rs[t], y, True)) for t in terminals)
            assert joint == expected
            total += 1
            needs_relaxed += strict > expected
    assert needs_relaxed
    return {'left': left, 'right': right, 'all_mixed_pairs_and_triples': total,
            'requiring_a_relaxed_shore_for_the_minimum': needs_relaxed}


def run():
    data = [run_case(loose, links, link) for r in (2, 3)
            for loose, links in canonical_cases(r) for link in ("none", "direct", "two_new")]
    return {"two_pole_control": control(), "three_terminal_profile_control": three_terminal_control(),
            "literal_port_control": checked_weighted_example(), "families": data,
            "independent_port_drops": [port_tests(n) for n in (4, 5, 6, 7)],
            "totals": {key: sum(x[key] for x in data) for key in
                       ("pair_preservers", "pair_code_changing", "pair_triple_preservers",
                        "pair_triple_code_changing")}}


if __name__ == "__main__":
    result = json.dumps(run(), indent=2) + "\n"
    if sys.argv[1:] == ["--check"]:
        assert OUTPUT.read_text() == result
    else:
        OUTPUT.write_text(result)
