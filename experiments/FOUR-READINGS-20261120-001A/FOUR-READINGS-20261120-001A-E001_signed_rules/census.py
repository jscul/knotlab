"""Independent binary-Pauli, connected-group and theorem checks on twice-held rules."""
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
from math import factorial
from pathlib import Path
import json

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def solve(equations, width):
    """One solution to binary equations, with free bits assigned zero."""
    pivots = {}
    for row, rhs in equations:
        while row:
            j = row.bit_length() - 1
            if j not in pivots:
                pivots[j] = row, rhs
                break
            old, answer = pivots[j]
            row ^= old
            rhs ^= answer
        if not row and rhs:
            return None
    solution = 0
    for j, (row, rhs) in sorted(pivots.items()):
        if (solution & row).bit_count() % 2 != rhs:
            solution |= 1 << j
    return solution


def product(left, right):
    """i^p X^x Z^z multiplication, for an arbitrary number of tensor factors."""
    p, x, z = left
    q, y, w = right
    return (p + q + 2 * (z & y).bit_count()) % 4, x ^ y, z ^ w


def verify_paulis(ends, ops, odd):
    owners = sorted(set(v for pair in ends for v in pair))
    identity = (0, 0, 0)
    for op in ops:
        assert product(op, op) == identity
    for u in owners:
        local = [ops[i] for i, pair in enumerate(ends) if u in pair]
        assert all(product(a, b) == product(b, a) for a, b in combinations(local, 2))
        accum = identity
        for op in local:
            accum = product(accum, op)
        assert accum == (2 * (u in odd), 0, 0)


def pauli_solution(ends, odd):
    """Full class of Pauli commutator forms on independent cycles."""
    graph = nx.Graph(ends)
    n = len(graph)
    assert set(graph) == set(range(n))
    tree = nx.Graph()
    tree.add_nodes_from(graph)
    tree_index = {}
    chords = []
    for i, (a, b) in enumerate(ends):
        if nx.has_path(tree, a, b):
            chords.append(i)
        else:
            tree.add_edge(a, b)
            tree_index[frozenset((a, b))] = i
    c = [0] * len(ends)
    for j, i in enumerate(chords):
        a, b = ends[i]
        path = nx.shortest_path(tree, a, b)
        for h in [i, *(tree_index[frozenset(pair)] for pair in zip(path, path[1:]))]:
            c[h] |= 1 << j
    width = len(chords)
    pairs = list(combinations(range(width), 2))
    @lru_cache(None)
    def bracket(e, f):
        a, b = c[e], c[f]
        return sum(1 << p for p, (i, j) in enumerate(pairs)
                   if ((a >> i & b >> j) ^ (a >> j & b >> i)) & 1)
    stars = [[i for i, pair in enumerate(ends) if u in pair] for u in range(n)]
    equations = [(bracket(e, f), 0) for star in stars for e, f in combinations(star, 2)]
    positions = [[] for _ in ends]
    for pos, e in enumerate(e for star in stars for e in star):
        positions[e].append(pos)
    obstruction = 0
    for e, f in combinations(range(len(ends)), 2):
        a, b = positions[e]
        x, y = positions[f]
        if a < x < b < y or x < a < y < b:
            obstruction ^= bracket(e, f)
    solution = solve([*equations, (obstruction, len(odd) % 2)], len(pairs))
    if solution is None:
        return None
    zgen = [0] * width
    for pos in bits(solution):
        i, j = pairs[pos]
        zgen[j] |= 1 << i
    ops = []
    for x in c:
        z = 0
        for j in bits(x):
            z ^= zgen[j]
        ops.append(((x & z).bit_count() % 4, x, z))
    wrong = set()
    for u, star in enumerate(stars):
        val = (0, 0, 0)
        for e in star:
            val = product(val, ops[e])
        assert val in ((0, 0, 0), (2, 0, 0))
        if (val[0] == 2) != (u in odd):
            wrong.add(u)
    for u in reversed(list(nx.bfs_tree(tree, 0))):
        if u and u in wrong:
            parent = nx.shortest_path(tree, u, 0)[1]
            e = tree_index[frozenset((u, parent))]
            p, x, z = ops[e]
            ops[e] = ((p + 2) % 4, x, z)
            wrong.symmetric_difference_update((u, parent))
    assert not wrong
    verify_paulis(ends, ops, odd)
    return ops


@lru_cache(None)
def group_plans(n, k):
    """Unordered nonempty groups; members left out are allowed."""
    plans = []
    def visit(u, blocks):
        if len(blocks) + n - u < k:
            return
        if u == n:
            plans.append(tuple(blocks))
            return
        visit(u + 1, blocks)
        for j in range(len(blocks)):
            old = blocks[j]
            blocks[j] |= 1 << u
            visit(u + 1, blocks)
            blocks[j] = old
        if len(blocks) < k:
            visit(u + 1, [*blocks, 1 << u])
    visit(0, [])
    return plans


def group_witness(graph):
    n = len(graph)
    neighbors = [sum(1 << v for v in graph[u]) for u in range(n)]
    @lru_cache(None)
    def reach(mask):
        touched = 0
        for u in bits(mask):
            touched |= neighbors[u]
        return touched
    @lru_cache(None)
    def linked(mask):
        seen = mask & -mask
        while True:
            more = seen | (reach(seen) & mask)
            if more == seen:
                return seen == mask
            seen = more
    for k in (5, 6):
        for groups in group_plans(n, k):
            if not all(linked(g) for g in groups):
                continue
            if k == 5:
                choices = [((i, j) for i, j in combinations(range(k), 2))]
            else:
                choices = [tuple((i, j) for i in half for j in range(k) if j not in half)
                           for half in combinations(range(k), 3) if 0 in half]
            for needed in choices:
                needed = tuple(needed)
                if all(reach(groups[i]) & groups[j] for i, j in needed):
                    return dict(groups=[list(bits(g)) for g in groups], required=needed)
    return None


def closure_candidates(graph):
    """Deleting the final knot wires its distinctions to the exterior."""
    if not nx.is_biconnected(graph):
        return []
    answers = []
    for u in graph:
        parents = set(graph[u])
        witnesses = [set(graph[w]) & parents for w in graph if w != u]
        joined = all(any(a in h and b in h for h in witnesses) for a, b in combinations(parents, 2))
        if joined and all(h != parents for h in witnesses):
            answers.append(u)
    return sorted(answers)


def labelled_denominator(n):
    inc = [0] * n
    edges = list(combinations(range(n), 2))
    for i, (u, v) in enumerate(edges):
        inc[u] |= 1 << i
        inc[v] |= 1 << i
    return Counter(mask.bit_count() for mask in range(1 << len(edges))
                   if all((mask & star).bit_count() >= 3 for star in inc))
    # At most seven holders: two disconnected components of min-degree three need eight.


def run():
    rows = []
    weighted = defaultdict(Counter)
    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        n = len(graph)
        if n < 4 or min(dict(graph.degree).values()) < 3 or not nx.is_connected(graph):
            continue
        ends = sorted(tuple(sorted(pair)) for pair in graph.edges)
        ops = pauli_solution(ends, {n - 1})
        group = group_witness(graph)
        planar, cert = nx.check_planarity(graph)
        assert (ops is not None) == (group is not None) == (not planar)
        if planar:
            cert.check_structure()
        assert not nx.has_bridges(graph)
        aut = sum(1 for _ in nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
        mult = factorial(n) // aut
        weighted[n][len(ends)] += mult
        degrees = sorted(dict(graph.degree).values())
        relaxed_fano = any(all(graph.degree(u) == 3 and
                               all(graph.has_edge(u, v) for v in four if v != u)
                               for u in four) for four in combinations(graph, 4))
        rows.append(dict(atlas=atlas_index, n=n, m=len(ends), sharing=ends, arities=degrees,
                         labelled=mult, charge=1, loop_count=len(ends)-n+1,
                         has_odd_holder_loop=not nx.is_bipartite(graph), literal_Fano_piece=False,
                         relaxed_Fano_four_triples=relaxed_fano, classical_states=0,
                         states_after_one_rule_deleted=1 << (len(ends)-n+1),
                         deleted_star_implies_full_opposite_rule_for_every_choice=nx.is_biconnected(graph),
                         operator=not planar, pauli_i_phase_X_bits_Z_bits=ops, groups=group,
                         cyclic_orders=cert.get_data() if planar else None,
                         restored_last_holders=closure_candidates(graph)))
    direct = {n:labelled_denominator(n) for n in range(4, 8)}
    assert direct == weighted
    save('census.json', rows)
    save('labelled_denominators.json', direct)
    return rows


if __name__ == '__main__':
    rows = run()
    print(Counter((r['n'], r['operator']) for r in rows))
