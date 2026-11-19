"""Exact finite tests on the live roster and its maximal blocks."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Roster:
    size: int
    blocks: tuple
    opens: tuple | None
    degrees: tuple = ()


@dataclass(frozen=True)
class Component:
    points: tuple
    blocks: tuple


def components(roster):
    parent = list(range(roster.size))
    size = [1] * roster.size

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for block in roster.blocks:
        root = find(block[0])
        for v in block[1:]:
            other = find(v)
            if root != other:
                if size[root] < size[other]:
                    root, other = other, root
                parent[other] = root
                size[root] += size[other]
    points, blocks = defaultdict(list), defaultdict(list)
    for v in range(roster.size):
        points[find(v)].append(v)
    for b in roster.blocks:
        blocks[find(b[0])].append(b)
    return tuple(Component(tuple(p), tuple(blocks[c])) for c, p in points.items())


def partnered(roster, component, *, reached, maximum_order):
    """Test the free or complement-closed held form and exact local supply."""
    points, blocks = component.points, component.blocks
    n = len(points)
    if n < 6 or n % 2:
        return {"status": "wrong_size"}
    k = n // 2
    if any(len(b) > k for b in blocks):
        return {"status": "block_too_large"}
    if any(roster.degrees[v] != n - 2 for v in points):
        return {"status": "wrong_candidate_degree"}
    if k > maximum_order:
        return {"status": "order_limit", "order": k}
    all_names = set(points)
    near = {u: {u} for u in points}
    for block in blocks:
        for u in block:
            near[u].update(block)
    missing = {u: all_names - near[u] for u in points}
    assert all(len(names) == 1 for names in missing.values())
    partners = {u: next(iter(names)) for u, names in missing.items()}
    assert all(partners[partners[u]] == u for u in points)
    held = {tuple(sorted(b)) for b in blocks if len(b) == k}
    h = len(held)
    fact = {"order": k, "held_transversals": h}
    for word in held:
        if tuple(sorted(partners[v] for v in word)) not in held:
            return {**fact, "status": "held_not_complement_closed", "one_held_word": word}
    next_order = ((1 << k) - h) // 2
    if next_order <= k:
        return {**fact, "status": "free_order_does_not_increase", "next_order": next_order}
    # A pair has exactly 2**(k-2) possible transversal extensions.
    extensions = 1 << (k - 2)
    if h >= extensions:
        counts = Counter(pair for word in held for pair in combinations(word, 2))
        if max(counts.values()) >= extensions:
            return {**fact, "status": "pair_has_no_free_extension"}
    if roster.opens is None and not reached:
        return {**fact, "status": "open_supply_unavailable"}
    # For a reached open state, the demand exceeds both fresh-count floors.
    if roster.opens is not None and any(roster.opens[v] != next_order for v in points):
        return {**fact, "status": "wrong_supply", "required": next_order}
    return {**fact, "status": "partnered", "next_order": next_order,
            "pairing": [(v, partners[v]) for v in points if v < partners[v]],
            "held_words": sorted(held), "supply": next_order,
            "supply_from": "literal" if roster.opens is not None else "reached fresh-count law"}


def structural_key(roster):
    return (roster.size, tuple(sorted(map(len, roster.blocks))),
            tuple(sorted(Counter(roster.degrees).items())))


def exact_roster_map(first, second):
    """Return one exact live-point map preserving opens and every maximal block."""
    if structural_key(first) != structural_key(second):
        return None
    assert first.opens is not None and second.opens is not None
    if Counter(first.opens) != Counter(second.opens):
        return None
    if first.blocks == second.blocks and first.opens == second.opens:
        return tuple(range(first.size))

    from networkx import Graph
    from networkx.algorithms.isomorphism import GraphMatcher

    def incidence(roster):
        graph = Graph()
        graph.add_nodes_from((v, {"color": ("point", op)}) for v, op in enumerate(roster.opens))
        for i, block in enumerate(roster.blocks, roster.size):
            graph.add_node(i, color=("block", len(block)))
            graph.add_edges_from((u, i) for u in block)
        return graph

    matcher = GraphMatcher(incidence(first), incidence(second),
                           node_match=lambda a, b: a["color"] == b["color"])
    if not matcher.is_isomorphic():
        return None
    image = tuple(matcher.mapping[v] for v in range(first.size))
    assert set(image) == set(range(second.size))
    assert all(first.opens[v] == second.opens[image[v]] for v in range(first.size))
    assert {tuple(sorted(image[v] for v in b)) for b in first.blocks} == set(second.blocks)
    return image
