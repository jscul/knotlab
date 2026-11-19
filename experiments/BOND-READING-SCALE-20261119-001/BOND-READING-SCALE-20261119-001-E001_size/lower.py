"""Check every residual marked map in a small-width rooted support shard."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
MEET_ONCE = Path("GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds")
EXTEND_ROUND = Path("EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend")
sys.path.insert(0, str(ROOT / "experiments" / MEET_ONCE))
from readings import bond_readings  # noqa: E402
from verify import (Arrangement, exact_table, find_matching, groups, indices, linear_basis, mismatches, pair_key,  # noqa: E402
                    reduce_word, round_replay, start_audit)


DEFAULT_GENG = "/tmp/bond-reading-lower-nauty/usr/bin/nauty-geng"
DEFAULT_LIBRARY = "/tmp/bond-reading-lower-nauty/usr/lib/x86_64-linux-gnu:/tmp/bond-reading-lower-nauty/usr/lib"


def marked_maps(stage, pairs, triples, order):
    """One representative per coset of permutations within source incidence columns."""
    fixed = sorted(set().union(*(stage.stars[j] for j in stage.live)))
    fixed_set = set(fixed)
    movable = set(stage.labels) - fixed_set
    fixed_pairs = list(combinations(fixed, 2)) if order >= 3 else []
    signatures = {}
    allies = defaultdict(list)
    for x in movable:
        signatures[x] = (Counter(pairs[pair_key(x, y)] for y in stage.labels if x != y),
                         tuple(pairs[pair_key(x, y)] for y in fixed),
                         tuple(triples[tuple(sorted((x, y, z)))] for y, z in fixed_pairs))
        allies[tuple(stage.owners[x])].append(x)
    domains = {x: {y for y in movable if signatures[x] == signatures[y]} for x in movable}
    fixed_map = {x: x for x in fixed}
    assigned = {}

    def fits(x, y):
        if any(v in assigned and (v < x) != (assigned[v] < y) for v in allies[tuple(stage.owners[x])]):
            return False
        for p, q in assigned.items():
            if pairs[pair_key(x, p)] != pairs[pair_key(y, q)]:
                return False
            if order >= 3 and any(triples[tuple(sorted((x, p, z)))] != triples[tuple(sorted((y, q, z)))] for z in fixed):
                return False
        return order < 3 or all(triples[tuple(sorted((x, p, q)))] == triples[tuple(sorted((y, assigned[p], assigned[q])))]
                                for p, q in combinations(assigned, 2))

    def search(used):
        if len(assigned) == len(movable):
            yield fixed_map | assigned
            return
        possible = {x: [y for y in sorted(domains[x] - used) if fits(x, y)] for x in movable - assigned.keys()}
        x = min(possible, key=lambda z: (len(possible[z]), z))
        for y in possible[x]:
            assigned[x] = y
            yield from search(used | {y})
            del assigned[x]

    yield from search(set())


def native_predecessor(stage):
    try:
        old = Arrangement.parse([sorted(star) for j, star in enumerate(stage.stars) if j not in stage.live])
        if not start_audit(old)["census_open_legal"]:
            return None
        round_replay(old, stage)
    except ValueError:
        return None
    return old


def pair_lifetime_condition(stage):
    if not stage.live:
        return "closed"
    if len(stage.live) == 2:
        return "two_live_junctions"
    live_groups = groups(stage.neighbors, stage.live)
    loose_count = Counter(stage.loose.values())
    if live_groups == {stage.live} and all(n == 1 for n in loose_count.values()):
        return "one_implied_closing_group"
    active = Counter(p for members in live_groups for p in members)
    if (max(active.values(), default=0) <= 1 and
        all(len(group) == 2 and len({frozenset(stage.neighbors[p]) for p in group}) == 1
            and all(len(stage.neighbors[p]) == 1 and loose_count[p] == 2 for p in group)
            for group in live_groups)):
        assert max(loose_count.values()) <= 2
        return "independent_unit_or_two_route_attachments"
    return None


def next_stage(stage):
    from extend import grow1

    result = grow1(stage.stars)
    if result is None:
        return None
    successor = Arrangement.parse([sorted(row) for row in result])
    round_replay(stage, successor)
    return successor


def permanent_two_port_capacity(stage, following):
    from networkx import Graph, has_path, minimum_cut_value

    closed = set(range(len(stage.stars))) - stage.live
    ports = set().union(*(stage.neighbors[j] for j in stage.live))
    if not ports <= closed or len(ports) != 2:
        return False
    a, b = sorted(ports)

    def graph(arrangement, ordinary):
        ends, _, outside = arrangement.holder_graph()
        piece = Graph()
        piece.add_nodes_from(ports)
        for u, v in ends.values():
            if u in closed and v in closed or ordinary and outside in (u, v):
                continue
            cost = piece.get_edge_data(u, v, {}).get("capacity", 0) + 1
            piece.add_edge(u, v, capacity=cost)
        return piece

    before = graph(stage, False)
    later = graph(following, True)
    return (has_path(before, a, b) and has_path(later, a, b)
            and minimum_cut_value(later, a, b) >= minimum_cut_value(before, a, b))


def boundary_pair_profiles(stage):
    """Exact static-core cut minima with terminal positions and connectivity retained."""
    core = sorted(set(range(len(stage.stars))) - stage.live)
    stored = {j: i for i, j in enumerate(core)}
    ports = set().union(*(stage.neighbors[j] for j in stage.live))
    assert ports <= set(core)
    port_mask = sum(1 << stored[j] for j in ports)
    adjacent = [0] * len(core)
    edges = []
    for x, owners in stage.owners.items():
        if not set(owners) <= set(core):
            continue
        u, v = [stored[j] for j in owners]
        adjacent[u] |= 1 << v
        adjacent[v] |= 1 << u
        edges.append((x, 1 << u, 1 << v))

    def partition(side):
        residue = side
        terminal_blocks = []
        without_terminal = 0
        while residue:
            component = 0
            todo = residue & -residue
            while todo:
                b = todo & -todo
                todo ^= b
                component |= b
                todo |= adjacent[b.bit_length() - 1] & residue & ~component
            if component & port_mask:
                terminal_blocks.append(component & port_mask)
            else:
                without_terminal += 1
            residue ^= component
        return tuple(sorted(terminal_blocks)), without_terminal

    all_sites = (1 << len(core)) - 1
    values = defaultdict(dict)
    for shore in range(1 << len(core)):
        record = partition(shore), partition(all_sites ^ shore)
        crossing = sorted(x for x, u, v in edges if bool(shore & u) != bool(shore & v))
        cost = len(crossing)
        for order in (1, 2):
            for marks in combinations(crossing, order):
                table = values[marks]
                table[record] = min(cost, table.get(record, float("inf")))
    return values


def permanently_symmetric_centers(stage):
    from networkx import Graph, has_path, minimum_cut_value

    closed = set(range(len(stage.stars))) - stage.live
    demand = Counter(p for group in groups(stage.neighbors, stage.live) for p in group)
    loose = Counter(stage.loose.values())
    continuing = {p: loose[p] - demand[p] for p in stage.live
                  if loose[p] <= 2 and (loose[p] == 2 or demand[p] == 0) and loose[p] > demand[p]}
    permanent = []
    for middle in closed:
        neighbors = stage.neighbors[middle]
        if len(neighbors) != 2 or not neighbors <= closed:
            continue
        a, b = sorted(neighbors)
        w = sum(a in stage.owners[x] for x in stage.stars[middle])
        if 2*w != len(stage.stars[middle]):
            continue
        graph = Graph()
        graph.add_nodes_from([a, b])
        for holders in stage.owners.values():
            if len(holders) != 2 or middle in holders:
                continue
            s, t = holders
            capacity = graph.get_edge_data(s, t, {}).get("capacity", 0) + 1
            graph.add_edge(s, t, capacity=capacity)
        outside = len(stage.stars)
        for u, capacity in continuing.items():
            graph.add_edge(u, outside, capacity=capacity)
        if has_path(graph, a, b) and minimum_cut_value(graph, a, b) >= w:
            permanent.append(stage.stars[middle])
    return permanent


def changes_only_permanent_centers(phi, centers):
    remaining = {x for x, y in phi.items() if x != y}
    while remaining:
        x = first = min(remaining)
        orbit = set()
        while x not in orbit:
            orbit.add(x)
            x = phi[x]
        assert x == first
        if not any(orbit <= center for center in centers):
            return False
        remaining -= orbit
    return True


def full_pair_extension(stage, following, exact_next, phi):
    if changed := mismatches(exact_next, exact_next, phi):
        return False, changed[0]
    identity_fresh = {x: phi.get(x, x) for x in following.labels}
    if not mismatches(exact_next, exact_next, identity_fresh):
        return True, None
    fresh = set(following.labels) - set(stage.labels)
    allowed = {x: {phi[x]} if x in phi else fresh for x in following.labels}
    return find_matching(exact_next, exact_next, allowed, phi) is not None, None


def expand(row):
    outside, n, e = row[:3]
    supports = [[] for _ in range(n)]
    weights = []
    label = 0
    for i in range(e):
        a, b, amount = row[3 + 3*i:6 + 3*i]
        for x in range(label, label + amount):
            supports[a].append(x)
            supports[b].append(x)
        label += amount
        if outside not in (a, b):
            weights.append(amount)
    return Arrangement.parse([s for j, s in enumerate(supports) if j != outside]), max(weights, default=1)


def classify(row, order, mode):
    stage, max_multiplicity = expand(row)
    chosen = native_predecessor(stage) if mode == "native" else None
    if mode == "native":
        assert chosen is not None, row
    (_, pairs, triples), bonds, span = bond_readings(stage)
    literal, _, _ = exact_table(stage, 5_000_000)
    assert literal == pairs
    bond_set = set(bonds)
    basis = linear_basis(stage.masks)
    tally = Counter()
    witness = {}
    lifetime = pair_lifetime_condition(stage) if chosen is not None else None
    following = exact_next = None
    profiles = None
    centers = None

    for phi in marked_maps(stage, pairs, triples, order):
        tally["maps"] += 1
        kept = (all(reduce_word(sum(stage.label_bits[phi[x]] for x in support), basis) == 0 for support in stage.stars))
        # Check membership of every transported support independently of the row reduction.
        image = lambda word: sum(stage.label_bits[phi[stage.labels[i]]] for i in indices(word))
        assert all(image(word) in bond_set for word in bonds) == kept
        if kept:
            tally["equations"] += 1
            continue
        tally["changes_equations"] += 1
        old_bond = next(word for word in bonds if image(word) not in span)
        old_mark = [stage.labels[i] for i in indices(old_bond)]
        if "any_arity" not in witness:
            witness["any_arity"] = {"permutation": sorted(phi.items()), "bond": old_mark,
                                    "image_outside_the_old_span": [phi[x] for x in old_mark]}
        if chosen is None:
            continue
        if lifetime:
            tally[f"lifetime_{lifetime}"] += 1
            continue
        if centers is None:
            centers = permanently_symmetric_centers(stage)
        if changes_only_permanent_centers(phi, centers):
            tally["lifetime_permanent_symmetric_center"] += 1
            continue
        if profiles is None:
            profiles = boundary_pair_profiles(stage)
        if all(profiles.get(tuple(sorted(phi[x] for x in marks)), {}) == values for marks, values in profiles.items()):
            tally["lifetime_invariant_static_boundary_profile"] += 1
            continue
        if following is None:
            following = next_stage(stage)
            assert following is not None
            if permanent_two_port_capacity(stage, following):
                lifetime = "permanent_ordinary_two_port_capacity"
            else:
                exact_next, _, _ = exact_table(following, 5_000_000)
        if lifetime:
            tally[f"lifetime_{lifetime}"] += 1
            continue
        extends, changed = full_pair_extension(stage, following, exact_next, phi)
        fixed_fresh = {x: phi.get(x, x) for x in following.labels}
        successor_certificate = pair_lifetime_condition(following)
        if extends and successor_certificate and not mismatches(exact_next, exact_next, fixed_fresh):
            tally[f"lifetime_after_next_{successor_certificate}"] += 1
        else:
            tally["next_pair_fails" if not extends else "next_pair_extends_lifetime_open"] += 1
        if not extends and "pair" not in witness:
            witness["pair"] = {"permutation": sorted(phi.items()), "changed_old_pair": changed}
    output = {"current_width": len(stage.labels), "ordinary_junctions": len(stage.stars),
              "max_ordinary_meeting_multiplicity": max_multiplicity, "maps_by_outcome": dict(tally)}
    if witness:
        output["witness"] = witness | {"rooted_allocation": row,
                                      "predecessor": None if chosen is None else [sorted(s) for s in chosen.stars],
                                      "current": [sorted(s) for s in stage.stars],
                                      "next": None if following is None else [sorted(s) for s in following.stars]}
    return output


def run_shard(ordinary, order, min_width, max_width, mode, geng, library, part=0, parts=1):
    wired = ordinary + 1
    env = os.environ.copy()
    if library:
        env["LD_LIBRARY_PATH"] = library
    with tempfile.TemporaryDirectory(prefix="bond-lower-") as temp:
        tool = Path(temp) / "lower"
        subprocess.run(["c++", "-std=c++20", "-O3", str(Path(__file__).with_suffix(".cpp")), "-o", str(tool)], check=True)
        command = [str(tool), str(order), str(min_width), str(max_width), mode]
        max_edges = min(max_width, wired*(wired-1)//2)
        if wired == 2 or max_edges < wired:
            graph = "A_\n" if wired == 2 and part == 0 else ""
            scan = subprocess.run(command, input=graph, capture_output=True, text=True, check=True)
        else:
            cmd = [geng, "-Cq", str(wired), f"0:{max_edges}", f"{part}/{parts}"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env) as source:
                scan = subprocess.run(command, stdin=source.stdout, capture_output=True, text=True, check=True)
                source.stdout.close()
                assert source.wait() == 0
    observations = {}
    supports = None
    residual = []
    for line in scan.stdout.splitlines():
        key, *raw = line.split()
        fields = list(map(int, raw))
        if key == "R":
            residual.append(classify(fields, order, mode))
        elif key == "T":
            w, eligible, early, marked, pending = fields
            observations[w] = {"rooted_allocations": eligible, "rank_before_marking": early,
                               "rank_after_marking": marked, "exact_group_checks": pending}
        else:
            assert key == "C"
            supports = fields
    assert supports is not None and sum(row["exact_group_checks"] for row in observations.values()) == len(residual)
    return {"ordinary_junctions": ordinary, "mode": mode, "order": order, "partition": [part, parts],
            "graph6_supports": supports[0], "rooted_shapes_before_arity_and_width_filter": supports[1],
            "widths": observations, "residual": residual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, choices=(2, 3), required=True)
    parser.add_argument("--min-width", type=int, default=1)
    parser.add_argument("--max-width", type=int, required=True)
    parser.add_argument("--min-junctions", type=int, default=1)
    parser.add_argument("--max-junctions", type=int)
    parser.add_argument("--mode", choices=("static", "native"), required=True)
    parser.add_argument("--geng", default=DEFAULT_GENG)
    parser.add_argument("--library", default=DEFAULT_LIBRARY)
    args = parser.parse_args()
    cap = args.max_junctions or ((2*args.max_width + 1)//3 - 1)
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    rows = [run_shard(j, args.order, args.min_width, args.max_width, args.mode, args.geng, args.library)
            for j in range(args.min_junctions, cap + 1)]
    print(json.dumps({"rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
