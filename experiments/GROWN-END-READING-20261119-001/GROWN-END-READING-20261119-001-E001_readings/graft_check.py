"""Replay and audit the two-terminal graft on compact and dense cores."""

from collections import Counter, defaultdict
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

from named import ROOT
from verify import Arrangement, connected, indices, linear_basis, reading, reduce_word, round_replay, start_audit


EXTEND_ROUND = Path("EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend")


def rows_from_edges(edges):
    rows = defaultdict(set)
    for name, u, v in edges:
        rows[u].add(name)
        rows[v].add(name)
    return [sorted(rows[j]) for j in sorted(rows)]


def stage_edges(stage):
    ends, _, _ = stage.holder_graph()
    return [(x, u, v) for x, (u, v) in ends.items()]


def bonds(edges, s, t):
    """Return marked bond supports and whether the cut separates the two terminals."""
    labels = sorted(x for x, _, _ in edges)
    by_label = {x: 1 << i for i, x in enumerate(labels)}
    vertices = {v: j for j, v in enumerate(sorted({z for _, u, v in edges for z in (u, v)}))}
    neighbor = [0] * len(vertices)
    star = [0] * len(vertices)
    for x, u, v in edges:
        a, b = vertices[u], vertices[v]
        neighbor[a] |= 1 << b
        neighbor[b] |= 1 << a
        star[a] ^= by_label[x]
        star[b] ^= by_label[x]
    full = (1 << len(vertices)) - 1
    assert connected(full, neighbor)
    shore = support = 0
    for k in range(1, 1 << (len(vertices) - 1)):
        changed = k & -k
        shore ^= changed
        support ^= star[changed.bit_length() - 1]
        if connected(shore, neighbor) and connected(full ^ shore, neighbor):
            separates = ((shore >> vertices[s]) ^ (shore >> vertices[t])) & 1
            yield tuple(labels[i] for i in indices(support)), bool(separates)


def minima(marked_bonds):
    result = {}
    for support in marked_bonds:
        size = len(support)
        for arity in range(min(3, size) + 1):
            for names in combinations(support, arity):
                if size < result.get(names, float("inf")):
                    result[names] = size
    return result


def least(*values):
    return min((v for v in values if v is not None), default=None)


def plus(a, b):
    return None if a is None or b is None else a + b


def compare_substitution(core, exterior, e, s, t, phi):
    core_without_e = [row for row in core if row[0] != e]
    h_names = {x for x, _, _ in core_without_e}
    q_names = {x for x, _, _ in exterior}
    assert not h_names & q_names and e not in q_names
    h_nodes = {z for _, u, v in core_without_e for z in (u, v)}
    q_nodes = {z for _, u, v in exterior for z in (u, v)}
    assert h_nodes & q_nodes == {s, t}
    original = minima(support for support, _ in bonds(core, s, t))
    interior_sep = minima(support for support, sep in bonds(core_without_e, s, t) if sep)
    exterior_sep = minima(support for support, sep in bonds(exterior, s, t) if sep)
    assert exterior_sep[()] == 1
    # A virtual connector models paths through the uncut part when s and t agree.
    exterior_together = minima(support for support, sep in bonds([*exterior, (e, s, t)], s, t) if not sep)
    entire_bonds = list(bonds([*core_without_e, *exterior], s, t))
    measured = minima(support for support, _ in entire_bonds)
    complete_phi = {x: phi.get(x, x) for x in h_names | q_names}
    assert phi[e] == e and set(complete_phi.values()) == h_names | q_names

    counts = Counter()
    missing = Counter()
    for arity in (1, 2, 3):
        for names in combinations(sorted(h_names | q_names), arity):
            interior = tuple(x for x in names if x in h_names)
            outside = tuple(x for x in names if x in q_names)
            if not outside:
                group = "interior"
                derived = original.get(interior)
            elif not interior:
                group = "exterior"
                derived = least(exterior_together.get(outside), plus(exterior_sep.get(outside), interior_sep[()]))
            else:
                group = "mixed"
                original_marked = original.get(tuple(sorted((*interior, e))))
                h_cost = None if original_marked is None else original_marked - 1
                assert h_cost == interior_sep.get(interior)
                derived = plus(h_cost, exterior_sep.get(outside))
            assert derived == measured.get(names), (names, derived, measured.get(names))
            assert derived == measured.get(tuple(sorted(complete_phi[x] for x in names))), names
            counts[f"{group}_{arity}"] += 1
            if derived is None:
                missing[f"{group}_{arity}"] += 1
    return {"terminal_cut_in_exterior": exterior_sep[()], "terminal_cut_in_interior": interior_sep[()],
            "all_bond_count": len(entire_bonds), "minima_checked_by_type_and_arity": dict(counts),
            "no_common_bond_by_type_and_arity": dict(missing), "bare_core_permutation": sorted(phi.items())}


def graft(core, e, n):
    _, s, t = next(row for row in core if row[0] == e)
    high = max(x for x, _, _ in core) + 1
    u, v, out = n, n + 1, n + 2
    exterior = [(high, s, u), (high + 1, t, v), (high + 2, u, out), (high + 3, u, out),
                (high + 4, v, out), (high + 5, v, out)]
    edges = [row for row in core if row[0] != e] + exterior
    return rows_from_edges(edges)[:-1], s, t


def replay(source, number, grow1, core_count):
    stages = [Arrangement.parse(source)]
    origin_audit = start_audit(stages[0])
    assert origin_audit["census_open_legal"] and origin_audit["meets_once"]
    assert all(len(stage_star) >= 3 for stage_star in stages[0].stars)
    assert stages[0].live == {core_count, core_count + 1}
    branch = {core_count: 0, core_count + 1: 1}
    trace = []
    for _ in range(number):
        fresh = grow1(stages[-1].stars)
        following = Arrangement.parse([sorted(row) for row in fresh])
        previous = stages[-1]
        assert following.stars[:len(previous.stars)] == previous.stars
        records = round_replay(previous, following)
        for j, record in enumerate(records, len(previous.stars)):
            tags = {branch[i] for i in record["taken"]}
            assert len(tags) == 1 and record["fresh"] and not record["implied"]
            branch[j] = next(iter(tags))
        assert {branch[j] for j in following.live} == {0, 1}
        trace.append(records)
        stages.append(following)
    return stages, trace, origin_audit


def small_control(grow1):
    ends = list(combinations(range(4), 2))
    core = [(i, u, v) for i, (u, v) in enumerate(ends)]
    e = ends.index((0, 1))
    # Swap the terminals in the core, while the actual exterior names stay fixed.
    sigma = {0: 1, 1: 0, 2: 2, 3: 3}
    phi = {x: ends.index(tuple(sorted((sigma[u], sigma[v])))) for x, u, v in core}
    start, s, t = graft(core, e, 4)
    stages, literal_rounds, audit = replay(start, 2, grow1, 4)
    core_labels = {x for x, _, _ in core} - {e}
    result = []
    for age, stage in enumerate(stages):
        new_labels = set(stage.labels) - core_labels
        marking = {x: phi.get(x, x) for x in stage.labels}
        assert reading(stage, stage, marking)[1]["keeps_reading"]
        span = linear_basis(stage.masks)
        assert all(reduce_word(sum(stage.label_bits[marking[x]] for x in row), span) == 0 for row in stage.stars)
        result.append({"age": age, "ordinary_junctions": len(stage.stars), "distinctions": len(stage.labels),
                       "equation_span_preserved_in_compact_control": True,
                       **compare_substitution(core, [row for row in stage_edges(stage) if row[0] in new_labels],
                                              e, s, t, phi)})
    # The closed path has neither loose names nor an exterior holder. It tests the same identities without wiring.
    closed_example = [(6, s, 4), (7, 4, 5), (8, 5, t)]
    closed = compare_substitution(core, closed_example, e, s, t, phi)
    return {"ordinary_closed_core": core, "stage_comparisons": result, "rounds": literal_rounds,
            "start_audit": audit, "no_loose_exterior_control": closed}


def dense_control(grow1):
    n = 21
    mids = list(combinations(range(n), 2))
    dark_hub, light_hub = n + len(mids), n + len(mids) + 1
    names = {}
    core = []
    for j, (u, v) in enumerate(mids, n):
        hub = dark_hub if min(v - u, n + u - v) <= 5 else light_hub
        for selector, end in ((u, u), (v, v), ("hub", hub)):
            label = len(core)
            core.append((label, j, end))
            names[(u, v, selector)] = label
    sigma = {2: 3, 3: 2}
    phi = {}
    for (u, v, selector), x in names.items():
        a, b = sorted((sigma.get(u, u), sigma.get(v, v)))
        phi[x] = names[a, b, sigma.get(selector, selector)]
    e = names[0, 1, 0]
    assert phi[e] == e
    separating_state = {names[2, 8, "hub"], names[2, 8, 8], names[0, 8, 8], names[0, 8, "hub"]}
    assert e not in separating_state
    start, s, t = graft(core, e, n + len(mids) + 2)
    stages, trace, audit = replay(start, 2, grow1, n + len(mids) + 2)
    checked = []
    for age, stage in enumerate(stages):
        legality = start_audit(stage)
        assert legality["census_open_legal"] and legality["meets_once"]
        permutation = {x: phi.get(x, x) for x in stage.labels}
        assert set(permutation.values()) == set(stage.labels)
        live_support = set().union(*(stage.stars[j] for j in stage.live))
        assert all(permutation[x] == x for x in live_support)
        assert reading(stage, stage, permutation)[1]["keeps_reading"]
        owners = {x: tuple(holders) for x, holders in stage.owners.items()}
        assert all((owners[x] == owners[y]) == (owners[permutation[x]] == owners[permutation[y]])
                   for x, y in combinations(stage.labels, 2))
        basis = linear_basis(stage.masks)
        image = {permutation[x] for x in stage.stars[dark_hub]}
        syndrome = reduce_word(sum(stage.label_bits[x] for x in image), basis)
        assert syndrome
        assert all(len(row & separating_state) % 2 == 0 for row in stage.stars)
        assert len(image & separating_state) == 1
        checked.append({"age": age, "ordinary_junctions": len(stage.stars), "distinctions": len(stage.labels),
                        "rank": len(basis), "pair_flips_checked": comb(len(stage.labels), 2),
                        "legality": legality,
                        "all_live_supports_fixed": sorted(live_support), "old_equation": sorted(stage.stars[dark_hub]),
                        "image_not_in_equation_span": sorted(image), "nonzero_reduced_remainder":
                            [stage.labels[i] for i in indices(syndrome)]})
    return {"indices": n, "deleted_distinction": e, "terminals": (s, t), "start_audit": audit,
            "start": start, "rounds": trace, "marked_checks": checked,
            "literal_allowed_state_rejecting_image_equation": sorted(separating_state),
            "pair_and_triple_minima": "Use the separate dense-core bound and substitution proof"}


def main():
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    from extend import grow1

    print(json.dumps({"compact": small_control(grow1), "dense": dense_control(grow1)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
