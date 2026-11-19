"""Structural certificates for finite wired parity stages. Distinction names are integers."""

from collections import defaultdict
from itertools import combinations
from math import comb, inf


def _incidences(stars):
    rows = [tuple(row) for row in stars]
    owners = defaultdict(list)
    for v, row in enumerate(rows):
        if len(set(row)) != len(row):
            raise ValueError("a junction repeats one name")
        for name in row:
            owners[name].append(v)
    neighbors = [dict() for _ in rows]
    loose = [0] * len(rows)
    for name, ends in owners.items():
        if len(ends) == 1:
            loose[ends[0]] += 1
        elif len(ends) == 2:
            u, v = ends
            bundle = neighbors[u].setdefault(v, [])
            bundle.append(name)
            neighbors[v][u] = bundle
        else:
            raise ValueError("a distinction must have one or two holders")
    return rows, owners, neighbors, loose


def _tree_order(neighbors):
    if not neighbors or sum(map(len, neighbors)) != 2 * (len(neighbors) - 1):
        return [], {}
    order = [0]
    parent = {0: None}
    for v in order:
        for w in neighbors[v]:
            if w not in parent:
                parent[w] = v
                order.append(w)
    return (order, parent) if len(order) == len(neighbors) else ([], {})


def tree_certificate(stars):
    """Decide pair safety on a wired ordinary tree. None means outside the theorem.

    Input is the full list of literal ordinary supports at an open reached stage.
    A negative verdict has an explicit pair-reading-preserving transposition
    that changes the old equation space. A future reading needs a lawful successor.
    """
    rows, _, neighbors, loose = _incidences(stars)
    order, parent = _tree_order(neighbors)
    result = {"ordinary_tree": bool(order), "pair_sufficient": None,
              "harmful_swap": None, "ambiguous_corridors": 0}
    if not order or min(map(len, rows)) < 3 or not any(loose):
        return result
    if any(len(neighbors[v]) == 1 and not loose[v] for v in order):
        return result

    # offer[v,w] is the cheapest way to stop the w side of that branch.
    offer = {}
    for v in reversed(order[1:]):
        u = parent[v]
        below = loose[v] + sum(offer[v, w] for w in neighbors[v] if w != u)
        offer[u, v] = min(len(neighbors[u][v]), below)
    total = {}
    for v in order:
        total[v] = loose[v] + sum(offer[v, w] for w in neighbors[v])
        for w, bundle in neighbors[v].items():
            if parent[w] == v:
                offer[w, v] = min(len(bundle), total[v] - offer[v, w])

    def sealed(v):
        return not loose[v] and len(neighbors[v]) == 2

    visited = set()
    for start in order:
        if sealed(start):
            continue
        for first in neighbors[start]:
            if (start, first) in visited:
                continue
            free_at_minimum = defaultdict(list)
            u, v = start, first
            while True:
                visited.update(((u, v), (v, u)))
                bundle = neighbors[u][v]
                h = len(bundle)
                alternative = min(total[u] - offer[u, v], total[v] - offer[v, u])
                if not loose[u] and not loose[v] and h >= 2 and h == alternative:
                    free_at_minimum[h].append(min(bundle))
                if not sealed(v):
                    break
                w = next(w for w in neighbors[v] if w != u)
                u, v = v, w
            for candidates in free_at_minimum.values():
                if len(candidates) >= 2:
                    result["ambiguous_corridors"] += 1
                    if result["harmful_swap"] is None:
                        result["harmful_swap"] = candidates[:2]
    result["pair_sufficient"] = result["harmful_swap"] is None
    return result


def cherry_start(stars):
    """Recognize the unbounded sampled-start family with least order two at age one."""
    _, _, neighbors, loose = _incidences(stars)
    order, _ = _tree_order(neighbors)
    if not order or any(len(bundle) != 1 for row in neighbors for bundle in row.values()):
        return False
    if any(loose[v] != max(0, 3 - len(neighbors[v])) for v in order):
        return False
    leaves = {v for v in order if len(neighbors[v]) == 1}
    core = set(order) - leaves
    if len(core) < 2:
        return False
    for v in core:
        old_degree = sum(w in core for w in neighbors[v])
        added_leaves = len(neighbors[v]) - old_degree
        if old_degree == 1:
            if added_leaves not in (2, 3):
                return False
        elif old_degree < 3 or added_leaves:
            return False
    return True


def degree_two_free_start(stars):
    """Test the exact-age-one, order-two family under minimum-loose initialization.

    At least one nonleaf site and at most three leaf neighbors per site are
    required. The three-leaf star is the allowed one-nonleaf case.
    """
    _, _, neighbors, loose = _incidences(stars)
    order, _ = _tree_order(neighbors)
    if not order or any(len(bundle) != 1 for row in neighbors for bundle in row.values()):
        return False
    if any(loose[v] != max(0, 3 - len(neighbors[v])) for v in order):
        return False
    degrees = [len(row) for row in neighbors]
    if 2 in degrees or max(degrees) < 3:
        return False
    return all(sum(degrees[w] == 1 for w in neighbors[v]) <= 3 for v in order)


def pendant_join_start(stars):
    """Exact order two at age one if every multi-parent join uses only leaves."""
    _, _, neighbors, loose = _incidences(stars)
    order, _ = _tree_order(neighbors)
    if len(order) < 3 or any(len(bundle) != 1 for row in neighbors for bundle in row.values()):
        return False
    if any(loose[v] != max(0, 3 - len(neighbors[v])) for v in order):
        return False
    joined_leaves = False
    for v in order:
        live_neighbors = [w for w in neighbors[v] if loose[w]]
        if len(live_neighbors) >= 2:
            if len(live_neighbors) > 3 or any(len(neighbors[w]) != 1 for w in live_neighbors):
                return False
            joined_leaves = True
    return joined_leaves


def _basis_remainder(word, basis):
    for pivot in sorted(basis, reverse=True):
        if word >> pivot & 1:
            word ^= basis[pivot]
    return word


def _add_row(word, basis):
    residual = _basis_remainder(word, basis)
    if residual:
        basis[residual.bit_length() - 1] = residual


def pair_certificate(stars, single, pair, *, max_candidates=0):
    """Use a complete pair table and two callables single(x), pair(x,y).

    Values are least bond cardinalities (math.inf for no bond), not cardinality
    minus one. The code calls pair only on distinct names. max_candidates caps
    the subsets per request used by the optional codimension-one certificate.
    The returned bounds concern stages with at least one lawful successor.
    """
    rows, owners, _, loose = _incidences(stars)
    labels = sorted(owners)
    position = {name: i for i, name in enumerate(labels)}
    n = len(labels)
    degree_one = [single(name) for name in labels]
    table = [[0] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        table[i][j] = table[j][i] = pair(labels[i], labels[j])
    fixed = {position[name] for v, row in enumerate(rows) if loose[v] for name in row}
    movable = sorted(set(range(n)) - fixed)

    def safe(i, j):
        return owners[labels[i]] == owners[labels[j]] or table[i][j] == 2

    def safe_cells(cells):
        return all(all(safe(cell[0], j) for j in cell[1:]) for cell in cells)

    def cells_by(items, key):
        answer = defaultdict(list)
        for item in items:
            answer[key(item)].append(item)
        return list(answer.values())

    zero_safe = safe_cells([movable]) if movable else True
    single_cells = cells_by(movable, lambda i: degree_one[i])
    one_safe = safe_cells(single_cells)
    anchors = sorted(fixed)
    cells = cells_by(movable, lambda i: (degree_one[i], tuple(table[i][j] for j in anchors)))
    anchored_safe = safe_cells(cells)
    while not safe_cells(cells):
        next_cells = []
        for part in cells:
            def signature(i):
                return tuple(tuple(sorted(table[i][j] for j in cell if i != j)) for cell in cells)
            next_cells.extend(cells_by(part, signature))
        if len(next_cells) == len(cells):
            break
        cells = next_cells
    color_safe = safe_cells(cells)
    harmful = None
    if not color_safe:
        for cell in cells:
            for i, j in combinations(cell, 2):
                if not safe(i, j) and all(table[i][k] == table[j][k] for k in range(n) if k != i and k != j):
                    harmful = [labels[i], labels[j]]
                    break
            if harmful is not None:
                break

    basis = {}
    for v, row in enumerate(rows):
        if loose[v]:
            _add_row(sum(1 << position[name] for name in row), basis)
    exterior = sum(1 << i for i, name in enumerate(labels) if len(owners[name]) == 1)
    _add_row(exterior, basis)
    thresholds = []
    for i in range(n):
        levels = defaultdict(int)
        for j, size in enumerate(table[i]):
            if i != j and size != inf:
                levels[size] |= 1 << j
        seen = 1 << i
        cumulative = {}
        for size in sorted(levels):
            seen |= levels[size]
            cumulative[size] = seen
        thresholds.append(cumulative)
        m = degree_one[i]
        if m < inf:
            neighborhood = cumulative.get(m, 1 << i)
            if neighborhood.bit_count() == m:
                _add_row(neighborhood, basis)
    envelopes = []
    for i, j in combinations(range(n), 2):
        m = table[i][j]
        if m == inf:
            continue
        pool = thresholds[i][m] & thresholds[j][m]
        if pool.bit_count() == m:
            _add_row(pool, basis)
        elif max_candidates and comb(pool.bit_count() - 2, m - 2) <= max_candidates:
            envelopes.append((i, j, m, pool))

    forced_rank = len(basis)
    single_coset = False
    if len(rows) - forced_rank == 1 and envelopes:
        common = None
        for i, j, m, pool in envelopes:
            other = [k for k in range(n) if k not in (i, j) and pool >> k & 1]
            residues = set()
            for completion in combinations(other, m - 2):
                marking = (i, j, *completion)
                if all(table[a][b] <= m for a, b in combinations(marking, 2)):
                    word = sum(1 << k for k in marking)
                    residues.add(_basis_remainder(word, basis))
            if 0 not in residues:
                common = residues if common is None else common & residues
        single_coset = common is not None and len(common) == 1

    positive = color_safe or forced_rank == len(rows) or single_coset
    if positive and harmful is not None:
        raise AssertionError("inconsistent structural certificate on supplied table")
    return {"zero_sufficient": zero_safe, "one_sufficient": one_safe,
            "anchored_pair_sufficient": anchored_safe, "refined_pair_sufficient": color_safe,
            "forced_pair_rank": forced_rank, "full_rank": len(rows),
            "rank_one_coset_sufficient": single_coset, "harmful_pair_swap": harmful,
            "pair_sufficient": True if positive else False if harmful is not None else None}
