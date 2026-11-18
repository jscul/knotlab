"""Direct cuts on reachable high-degree examples and an unrestricted cographic control."""

from itertools import combinations


def indices(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def grow(history):
    edges = []
    neighbors = []
    outputs = []
    for vertex, (parents, fresh) in enumerate(history):
        assert (not parents and fresh == 3) if not vertex else (
            1 <= len(parents) <= 3 and fresh in (2, 3)
        )
        assert len(set(parents)) == len(parents)
        assert all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2))
        if len(parents) == 3:
            assert not set.intersection(*(neighbors[p] for p in parents))
        neighbors.append(set(parents))
        for parent in parents:
            edge = next(e for e in outputs[parent] if edges[e][1] is None)
            edges[edge] = (parent, vertex)
            neighbors[parent].add(vertex)
        outputs.append(tuple(range(len(edges), len(edges) + fresh)))
        edges.extend([(vertex, None)] * fresh)
    outside = len(history)
    return [(a, outside if b is None else b) for a, b in edges], outside


def component(start, allowed, neighbors):
    reached = start
    todo = start
    while todo:
        low = todo & -todo
        todo ^= low
        new = neighbors[low.bit_length() - 1] & allowed & ~reached
        reached |= new
        todo |= new
    return reached


def cuts(edges, outside):
    neighbors = [0] * (outside + 1)
    stars = [0] * (outside + 1)
    for e, (a, b) in enumerate(edges):
        neighbors[a] |= 1 << b
        neighbors[b] |= 1 << a
        stars[a] |= 1 << e
        stars[b] |= 1 << e
    full = (1 << (outside + 1)) - 1
    boundary = [0] * (1 << outside)
    bonds = []
    for side in range(1, 1 << outside):
        low = side & -side
        boundary[side] = boundary[side ^ low] ^ stars[low.bit_length() - 1]
        if component(low, side, neighbors) == side and (
            component(1 << outside, full ^ side, neighbors) == full ^ side
        ):
            bonds.append(boundary[side])
    return boundary, bonds, stars


def sizes(bonds, width):
    table = [[width + 1] * width for _ in range(width)]
    for word in bonds:
        weight = word.bit_count()
        for x, y in combinations(indices(word), 2):
            table[x][y] = table[y][x] = min(table[x][y], weight)
    assert all(3 <= table[x][y] <= width for x, y in combinations(range(width), 2))
    return table


def partition(links, available):
    groups = []
    while available:
        group = component(available & -available, available, links)
        groups.append(tuple(indices(group)))
        available ^= group
    return tuple(groups)


def partitions(edges, outside, table, t):
    width = len(edges)
    left = [0] * width
    right = [0] * width
    available = ((1 << width) - 1) ^ (1 << t)
    for x, y in combinations(indices(available), 2):
        if table[x][y] != table[x][t] + table[t][y] - 2:
            left[x] |= 1 << y
            left[y] |= 1 << x
        if (set(edges[x]) & set(edges[y])) - {outside}:
            right[x] |= 1 << y
            right[y] |= 1 << x
    return partition(left, available), partition(right, available)


def reachable_controls():
    # At 7 the three parents 1,2,6 use distinct pair witnesses 0,5,4.
    # Vertex 1 is trivalent. Vertex 8 then becomes a trivalent child of 7.
    prefix = [((), 3), ((0,), 2), ((0,), 3), ((0,), 2), ((2, 3), 2),
              ((1, 3), 2), ((4, 5), 2)]
    outcomes = []
    for fresh in (2, 3):
        history = [*prefix, ((1, 2, 6), fresh), ((7,), 2), ((8,), 2)]
        edges, outside = grow(history)
        boundary, bonds, stars = cuts(edges, outside)
        table = sizes(bonds, len(edges))
        for t, edge in enumerate(edges):
            scalar, actual = partitions(edges, outside, table, t)
            assert scalar == actual
            for vertex, (_, count) in enumerate(history):
                if vertex in edge or count != 3 or stars[vertex].bit_count() < 5:
                    continue
                reached_outputs = sum(
                    table[t][y] <= 4 for y, (a, _) in enumerate(edges) if a == vertex
                )
                assert reached_outputs <= 2
        # Check every true dual support, including nonminimal sums.
        for side, word in enumerate(boundary):
            if side.bit_count() >= 3:
                origins = (edges[e][0] for e in indices(word))
                leaving = [origin for origin in origins if side >> origin & 1]
                assert len(leaving) >= 4
                if len(leaving) == 4:
                    last = tuple(indices(side))[-3:]
                    assert all(history[a][1] == 2 for a in last)
                    assert set(leaving) <= set(last)
            if fresh == 3 and side >> 7 & 1 and word.bit_count() <= 5:
                assert not any(b == 7 and word >> e & 1 for e, (_, b) in enumerate(edges))
        x = edges.index((7, 8))
        witnesses = {}
        for t, (a, b) in enumerate(edges):
            if a != 8:
                continue
            for y, (p, v) in enumerate(edges):
                if v != 7:
                    continue
                candidates = [word.bit_count() for word in boundary
                              if word >> t & 1 and word >> y & 1 and not word >> x & 1]
                minimum = min(candidates)
                assert minimum >= fresh + 3
                witnesses[(p, b)] = minimum
        assert len(witnesses) == 6
        outcomes.append((fresh, len(edges), min(witnesses.values()), len(boundary)))
    return outcomes


def unrestricted_control():
    # Two depth-two binary trees; each of the eight bottom vertices meets
    # the two copies of the terminal, or meets the same terminal twice.
    results = []
    for split in (False, True):
        outside = 14 + int(split)
        edges = [(0, 7)]
        for root in (0, 7):
            edges.extend((root + (j - 1) // 2, root + j) for j in range(1, 7))
            for leaf in range(root + 3, root + 7):
                edges.extend(((leaf, 14), (leaf, outside)))
        _, bonds, _ = cuts(edges, outside)
        table = sizes(bonds, len(edges))
        scalar, physical = partitions(edges, outside, table, 0)
        assert sorted(map(len, scalar)) == [14, 14]
        assert sorted(map(len, physical)) == ([28] if split else [14, 14])
        results.append((table, len(bonds)))
    assert results[0][0] == results[1][0]
    return tuple(count for _, count in results)


if __name__ == "__main__":
    print("fresh, width, minimum tested cut, all dual supports:", reachable_controls())
    print("bond counts before and after the unrestricted split:", unrestricted_control())
