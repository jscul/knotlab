"""Check parent-closed serializations of the completed map on the two seven-knot sources."""

from collections import Counter
from dataclasses import dataclass
from functools import cache
from itertools import combinations, pairwise
from math import comb
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / BASE / f"{BASE}-E001_ordinary"))
from end_operator import from_stars, proposals, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "fixed_map.json"
MAX_SIZE = 4
BUNDLE = 9
SOURCE = ("U", "V", "S", "W", "A", "B", "Z")
MEETINGS = (("U", "S"), ("V", "S"), ("W", "S"), ("S", "A"),
            ("A", "B"), ("B", "W"), ("A", "Z"))


def connected(members, links):
    if not members:
        return False
    seen = {next(iter(members))}
    todo = list(seen)
    while todo:
        knot = todo.pop()
        for pair in links:
            if knot not in pair:
                continue
            others = (set(pair) & members) - seen
            todo.extend(others)
            seen.update(others)
    return seen == members


def order(cluster):
    return len(cluster), tuple(sorted(cluster))


@dataclass(frozen=True)
class Piece:
    roots: frozenset
    links: tuple
    relay: str | None = None
    top: frozenset = frozenset()

    def clusters(self, limit):
        universe = sorted(set().union(*map(set, self.links)))
        for size in range(1, limit + 1):
            for row in combinations(universe, size):
                cluster = frozenset(row)
                if not cluster & self.roots:
                    continue
                if self.relay in cluster and not self.top <= cluster:
                    continue
                if connected(cluster, self.links):
                    yield cluster


def path(*members):
    return tuple(pairwise(members))


def rays(root, name):
    return path(root, *(f"{name}{j}" for j in range(1, MAX_SIZE + 1)))


def pieces(shifted):
    if shifted:
        near_roots = top = frozenset(("U", "V", "W"))
        near = Piece(near_roots, (*combinations(sorted(near_roots), 2),
                                  ("U", "r"), *rays("r", "a"), *rays("r", "b")),
                     relay="r", top=top)
        far = Piece(frozenset(("Z",)), (*rays("Z", "c"), *rays("Z", "d")))
    else:
        near = Piece(frozenset(("U", "V")), (("U", "V"), *rays("U", "a"), *rays("V", "b")))
        leaves = ("c1", "c2", "c3", "c4")
        far = Piece(frozenset(("Z",)), (*(("Z", leaf) for leaf in leaves),
                                       ("Z", "rZ"), *rays("rZ", "e"), *rays("rZ", "f")),
                    relay="rZ", top=frozenset(("Z", *leaves)))
    return near, far


def incidence(piece):
    clusters = set(piece.clusters(MAX_SIZE + 1))
    parents = {}
    successors = {cluster: [] for cluster in clusters}
    for child in sorted(clusters, key=order):
        incoming = sorted((child - {member} for member in child if child - {member} in clusters),
                          key=order)
        parents[child] = tuple(incoming)
        for parent in incoming:
            successors[parent].append(child)
    return parents, successors


def row(cluster):
    return ",".join(sorted(cluster))


def verify_orders(piece, limit, stars, parents, successors, ports):
    events = sorted((cluster for cluster in piece.clusters(limit) if len(cluster) > 1),
                    key=order)
    bit = {cluster: 1 << i for i, cluster in enumerate(events)}
    prerequisites = {child: sum(bit.get(cluster, 0) for cluster in parents[child]) for child in events}
    roots = {frozenset((knot,)) for knot in piece.roots}
    source_stars = [star for cluster, star in stars.items() if len(cluster) == 1]
    full = (1 << len(events)) - 1
    transitions = 0

    @cache
    def count(mask):
        nonlocal transitions
        built = {cluster for cluster, mark in bit.items() if mask & mark}
        holders = Counter(port for star in source_stars for port in star)
        for cluster in built:
            holders.update(stars[cluster])
        assert max(holders.values()) <= 2
        # Even at the truncation boundary, this piece has a physical loose
        # distinction. Outgoing ports to size MAX_SIZE+1 stay allocated.
        assert any(holders[ports[cluster, child]] == 1
                   for cluster in roots | built for child in successors[cluster])
        if mask == full:
            return 1
        total = 0
        for child, mark in bit.items():
            if mask & mark:
                continue
            enabled = mask & prerequisites[child] == prerequisites[child]
            # Each edge gets one distinction; it is available iff its parent is
            # present and its only consumer (this child) is still absent.
            inputs = {ports[parent, child] for parent in parents[child]}
            assert enabled == all(holders[port] == 1 for port in inputs)
            if enabled:
                assert len(inputs) == len(parents[child])
                assert all(holders[port] == int(port in inputs) for port in stars[child])
                transitions += 1
                total += count(mask | mark)
        assert total > 0
        return total

    number = count(0)
    return {"events": len(events), "linear_extensions": number,
            "reachable_ideals": count.cache_info().currsize,
            "enabled_ideal_transitions": transitions}


def literal_source(shifted):
    stars = {frozenset((knot,)): [] for knot in SOURCE}
    for i, pair in enumerate(MEETINGS):
        for knot in pair:
            stars[frozenset((knot,))].extend(range(i * BUNDLE, (i + 1) * BUNDLE))
    far = "W" if shifted else "Z"
    for i, knot in enumerate(("U", "U", "V", "V", "Z", "Z", far, far), len(MEETINGS) * BUNDLE):
        stars[frozenset((knot,))].append(i)
    neighbors = {knot: set() for knot in SOURCE}
    for a, b in MEETINGS:
        neighbors[a].add(b)
        neighbors[b].add(a)
    loose = {knot: sum(bit >= len(MEETINGS) * BUNDLE for bit in stars[frozenset((knot,))])
             for knot in SOURCE}
    wired = (*MEETINGS, *((knot, "outside") for knot in SOURCE if loose[knot]))
    assert connected(set(SOURCE), MEETINGS)
    for root in SOURCE:
        assert len(stars[frozenset((root,))]) >= 3
        assert connected((set(SOURCE) - {root}) | {"outside"}, wired)
        # Any allowed assignment on root can extend to the other NAE stars.
        # A surviving full bundle can contain both values. If there is no
        # surviving bundle, the other knot has at least two unpinned opens.
        assert all(neighbors[knot] - {root} or loose[knot] >= 2
                   for knot in SOURCE if knot != root)
    live = [knot for knot in SOURCE if loose[knot]]
    assert all(len(neighbors[a] & neighbors[b]) <= 1 for a, b in combinations(live, 2))
    return stars


def literal_map(shifted, pieces_):
    stars = literal_source(shifted)
    source_width = len(set().union(*map(set, stars.values())))
    parents, successors = {}, {}
    for piece in pieces_:
        incoming, outgoing = incidence(piece)
        parents.update(incoming)
        successors.update(outgoing)
    edge_port = {}
    for cluster, star in stars.items():
        loose = [idx for idx in star if idx >= len(MEETINGS) * BUNDLE]
        children = successors.get(cluster, ())
        assert len(loose) == len(children)
        edge_port.update({(cluster, child): i for child, i in zip(children, loose, strict=True)})
    next_port = source_width
    for cluster in sorted(parents, key=order):
        if not 1 < len(cluster) <= MAX_SIZE:
            continue
        for child in successors[cluster]:
            edge_port[cluster, child] = next_port
            next_port += 1
        old_ports = [edge_port[parent, cluster] for parent in parents[cluster]]
        new_ports = [edge_port[cluster, child] for child in successors[cluster]]
        demand = sum(len(parents[child]) > 1 for child in successors[cluster])
        assert len(new_ports) == max(1, 3 - len(old_ports), demand)
        assert len(old_ports) + len(new_ports) >= 3
        stars[cluster] = old_ports + new_ports
    return stars, parents, successors, edge_port


def compare_layers(stars, parents, successors):
    results = []
    for size in range(1, MAX_SIZE):
        old = [cluster for cluster in sorted(stars, key=order) if len(cluster) <= size]
        old_id = {cluster: i for i, cluster in enumerate(old)}
        new = [cluster for cluster in sorted(stars, key=order) if len(cluster) == size + 1]
        expected = Counter((tuple(sorted(old_id[parent] for parent in parents[child])),
                            sum(len(parents[nxt]) > 1 for nxt in successors[child]),
                            len(successors[child])) for child in new)
        end = from_stars(tuple(stars[cluster] for cluster in old))
        for law in ("parity", "nae"):
            actual = step(end, law)
            assert actual.status == "extend" and not actual.implied
            assert Counter(zip(actual.parents, actual.demand, actual.fresh, strict=True)) == expected
        if size == 1:
            assert all(len(group) == 2 for group in proposals(end))
        results.append({"new_cluster_size": size + 1, "births": len(new),
                        "by_parent_count_and_fresh": [
                            [p, f, n] for (p, f), n in sorted(
                                Counter((len(group), fresh) for group, _, fresh in expected.elements()).items()
                            )]})
    return results


def replay(stars, parents, edge_port, serial):
    present = {cluster for cluster in stars if len(cluster) == 1}
    counts = Counter(bit for cluster in present for bit in stars[cluster])
    for child in serial:
        incoming = parents[child]
        assert child not in present and set(incoming) <= present
        inputs = {edge_port[parent, child] for parent in incoming}
        assert len(inputs) == len(incoming) and all(counts[bit] == 1 for bit in inputs)
        assert all(counts[bit] == int(bit in inputs) for bit in stars[child])
        assert any(owners == 1 and bit not in inputs for bit, owners in counts.items())
        counts.update(stars[child])
        present.add(child)
    return present


def measure(shifted):
    components = pieces(shifted)
    stars, parents, successors, ports = literal_map(shifted, components)
    common = frozenset(("U", "V"))
    assert len(successors[common]) == (1 if shifted else 2)
    assert all(len(parents[child]) >= 2 for child in successors[common])
    archive = compare_layers(stars, parents, successors)
    controls = []
    for size in range(2, MAX_SIZE + 1):
        near, far = [verify_orders(piece, size, stars, parents, successors, ports)
                     for piece in components]
        total = near["events"] + far["events"]
        ways = comb(total, near["events"]) * near["linear_extensions"] * far["linear_extensions"]
        assert total == sum(1 < len(cluster) <= size for cluster in stars)
        controls.append({"max_cluster_size": size, "near": near, "far": far,
                         "joint_events": total, "joint_linear_extensions": ways,
                         "joint_reachable_ideals": near["reachable_ideals"] * far["reachable_ideals"]})
    serial = tuple(map(frozenset, (("U", "V"), ("U", "W"), ("V", "W"), ("U", "V", "W")))) if shifted else (
        frozenset(("U", "a1")), common, frozenset(("U", "V", "a1")))
    present = replay(stars, parents, ports, serial)
    assert any(len(cluster) == 2 and cluster not in present for cluster in stars)
    remainder = sorted((cluster for cluster in stars if cluster not in present), key=order)
    assert replay(stars, parents, ports, (*serial, *remainder)) == set(stars)
    try:
        replay(stars, parents, ports, reversed(serial))
    except AssertionError:
        refused = True
    else:
        refused = False
    assert refused

    # Read the newborn with only UV emitted, granting every currently open
    # holder. Its immediate roster has no group through it in either arm.
    old = [cluster for cluster in sorted(stars, key=order) if len(cluster) == 1]
    source_stars = tuple(stars[cluster] for cluster in old)
    canonical_input_ports = [ports[parent, common] for parent in parents[common]]
    provisional_port = 1 + max(bit for star in source_stars for bit in star)
    provisional = from_stars((*source_stars, (*canonical_input_ports, provisional_port)))
    immediate = sum(len(old) in group for group in proposals(provisional))
    assert immediate == 0
    return {"source_knots": len(old), "source_distinctions": provisional_port,
            "common_used_source_ports": canonical_input_ports, "same_compare_parents": row(common),
            "common_fresh": len(successors[common]), "successor_inventory": [
                {"cluster": row(child), "parents": [row(parent) for parent in parents[child]]}
                for child in successors[common]], "near_source_opens": [
                    [row(cluster), len(successors[cluster])] for cluster in old
                    if cluster in successors and cluster != frozenset(("Z",))],
            "far_source_opens": len(successors[frozenset(("Z",))]),
            "common_first_present_snapshot": {"demand": immediate, "fresh": max(1, immediate)},
            "ordinary_both_laws_by_layer": archive, "finite_linear_extension_counts": controls,
            "mixed_size_prefix": [row(cluster) for cluster in serial],
            "inverted_mixed_prefix_refused": refused}


def main():
    quiet, shifted = measure(False), measure(True)
    assert quiet["common_used_source_ports"] == shifted["common_used_source_ports"]
    results = {"method": "direct cluster enumeration; exact ideal DP with independent-component interleaving",
               "counting": "structural events with fixed slot allocation; source knots already present",
               "lookahead_size": MAX_SIZE + 1, "checked_size": MAX_SIZE, "parallel_multiplicity": BUNDLE,
               "quiet": quiet, "shifted": shifted}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
