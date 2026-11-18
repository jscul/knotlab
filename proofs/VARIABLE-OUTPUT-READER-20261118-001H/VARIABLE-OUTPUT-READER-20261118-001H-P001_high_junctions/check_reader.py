"""Measure every cut through K=6 on close mixed exceptions and replay the anonymous reader."""

from collections import Counter
from itertools import combinations, product
from pathlib import Path
from random import Random
import json

import networkx as nx

# Reuse the history and incidence oracle independently of the reader below.
from importlib import util
proofs = Path(__file__).resolve().parents[2]
spec = util.spec_from_file_location("finite_oracle", next((proofs/"VARIABLE-OUTPUT-READER-20261118-001F").glob("*/audit.py")))
oracle = util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def strip(exceptions):
    end = (1, 1, exceptions + 2)
    positions = sorted((p for p in product(*(range(i+1) for i in end)) if p != end),
                       key=lambda p:(sum(p), p))
    rows, supplied, width = [], {}, 0
    for p in positions:
        old = []
        for axis, v in enumerate(p):
            if v:
                other = list(p)
                other[axis] -= 1
                old.append(supplied[tuple(other)][axis])
        axes = (1, 2) if p[0:2] == (1, 1) and 1 <= p[2] <= exceptions else (0, 1, 2)
        supplied[p] = {k: width+i for i,k in enumerate(axes)}
        width += len(axes)
        rows.append((*old,*supplied[p].values()))
    mark = []
    for axis in range(3):
        q = list(end)
        q[axis] -= 1
        mark.append(supplied[tuple(q)][axis])
    return rows, tuple(sorted(mark)), width


def measured_short_bonds(rows, width, cutoff):
    exterior = len(rows)
    holders = [[] for _ in range(width)]
    for i, row in enumerate(rows):
        for bit in row:
            holders[bit].append(i)
    loose = [0]*exterior
    older = [0]*exterior
    near = [0]*(exterior+1)
    for sites in holders:
        a = sites[0]
        b = sites[1] if len(sites)==2 else exterior
        near[a] |= 1 << b
        near[b] |= 1 << a
        if b == exterior:
            loose[a] += 1
        else:
            older[b] |= 1 << a
    stars = [oracle.mask(row) for row in rows]
    entire = (1 << (exterior+1))-1
    measurements = {}
    bonds = []
    shore_sizes = Counter()

    def connected(side):
        pending = seen = side & -side
        while pending:
            bit = pending & -pending
            new = near[bit.bit_length()-1] & side & ~seen
            pending = (pending ^ bit) | new
            seen |= new
        return bool(side) and side == seen

    def visit(i, side, boundary, fixed):
        # A loose bit or an ordinary bit with both ends assigned never changes again.
        if fixed > cutoff:
            return
        if i == exterior:
            if side and connected(side) and connected(entire ^ side):
                assert fixed == boundary.bit_count()
                bonds.append(boundary)
                shore_sizes[side.bit_count()] += 1
                for pair in combinations(oracle.active_bits(boundary), 2):
                    measurements[pair] = min(measurements.get(pair, cutoff+1), fixed)
            return
        visit(i+1, side, boundary, fixed+(older[i]&side).bit_count())
        visit(i+1, side|(1<<i), boundary^stars[i], fixed+loose[i]+(older[i]&~side).bit_count())

    visit(0,0,0,0)
    return measurements, bonds, dict(sorted(shore_sizes.items()))


def anonymous_reader(width, measured, cutoff=6):
    stars = set()
    for k in range(3,cutoff+1):
        near = nx.Graph()
        near.add_nodes_from(range(width))
        near.add_edges_from(pair for pair,v in measured.items() if v <= k)
        for a,b in combinations(stars,2):
            if a&b and len(a^b) <= k:
                near.remove_edges_from(product(a-b,b-a))
        stars = {frozenset(c) for c in nx.find_cliques(near) if len(c)>=3}
    return stars


def verify(exception_count):
    rows, mark, width = strip(exception_count)
    oracle.replay_history(rows, tuple(range(len(rows))))
    legal = oracle.permissions(rows)
    assert mark in legal
    measured, bonds, shores = measured_short_bonds(rows,width,6)
    actual = set(map(frozenset,rows))
    assert anonymous_reader(width,measured)==actual
    rng = Random(6177+exception_count)
    perm = list(range(width))
    rng.shuffle(perm)
    mapped = {tuple(sorted((perm[i],perm[j]))):k for (i,j),k in measured.items()}
    read = anonymous_reader(width,mapped)
    assert {frozenset(perm[b] for b in group) for group in actual} == read
    mapped_menu = {tuple(sorted(perm[b] for b in group)) for group in legal}
    assert oracle.permissions(list(read)) == mapped_menu
    assert not any(n>2 for n in shores)
    return {"two_fresh_three_parent_sites":exception_count, "width":width,"sites":len(rows),
            "arity_counts":dict(sorted(Counter(map(len,rows)).items())), "legal_mark":mark, "legal_triples":len(legal),
            "K_through":6,"total_table_entries":width*(width-1)//2,"visible_pair_entries":len(measured),
            "short_bonds":len(bonds),"short_bonds_by_ordinary_shore_size":shores,"every_junction_and_mark_renamed_correctly":True}


def opposing_terminal_groups():
    rows = [(0, 1, 2)]
    available = [[0, 1, 2]]
    width = 3

    def add(parents, count):
        nonlocal width
        chosen = [available[p].pop(0) for p in parents]
        outputs = list(range(width, width + count))
        width += count
        rows.append((*chosen, *outputs))
        available.append(outputs)
        return len(rows) - 1

    groups = []
    for _ in range(2):
        root = add([0], 3)
        unary = [add([root], 2) for _ in range(3)]
        top = [add(pair, 2) for pair in combinations(unary, 2)]
        groups.append(tuple(available[i][0] for i in top))
    assert width == 33
    reports = []
    for h in (2, 3):
        current_width = width + h
        d = h + 3
        fresh = tuple(range(width, current_width))
        values = []
        menus = []
        for chosen in groups:
            growth = [*rows, (*chosen, *fresh)]
            oracle.replay_history(growth, tuple(range(len(growth))))
            table, _, _ = measured_short_bonds(growth, current_width, d)
            values.append(table)
            menus.append(oracle.permissions(growth))
        mark = tuple(sorted(groups[0]))
        assert mark not in menus[0] and mark in menus[1]
        def clipped(table, cutoff):
            return {pair: val for pair, val in table.items() if val <= cutoff}
        assert clipped(values[0], d-1) == clipped(values[1], d-1)
        disputed = (mark[0], fresh[0])
        assert values[0][disputed] == d and disputed not in values[1]
        reports.append({"width":current_width, "fresh_count":h,"first_K_for_identity":d,
                        "all_named_pairs":current_width*(current_width-1)//2,
                        "prefix_history":rows,"competing_groups":groups,"mark":mark,
                        "K_on_input_and_fresh_output":[d,f">{d}"],
                        "full_menus_by_count":[len(m) for m in menus]})
    return reports


def check_all_small_downsets():
    # Every omitted direction would otherwise be a loose distinction. Suppressing one
    # wherever possible simultaneously minimizes every shore, irrespective of the axis.
    points = list(product(range(2), range(3), range(3)))
    index = {point: i for i, point in enumerate(points)}
    predecessors = []
    successors = []
    for point in points:
        nearby = []
        for delta in (-1, 1):
            bits = 0
            for axis in range(3):
                neighbor = list(point)
                neighbor[axis] += delta
                if tuple(neighbor) in index:
                    bits |= 1 << index[tuple(neighbor)]
            nearby.append(bits)
        predecessors.append(nearby[0])
        successors.append(nearby[1])
    cases = tested = attained = 0
    for downset in range(1, 1 << len(points)):
        members = tuple(oracle.active_bits(downset))
        if any(predecessors[v] & ~downset for v in members):
            continue
        cases += 1
        degrees = []
        links = []
        for v in members:
            parents = predecessors[v].bit_count()
            children = (successors[v] & downset).bit_count()
            degrees.append(parents + 3 - int(parents == 3 and children < 3))
            links.append(predecessors[v] | successors[v])
        last_gray = occupied = boundary_size = 0
        for step in range(1, 1 << len(members)):
            gray = step ^ (step >> 1)
            local = (gray ^ last_gray).bit_length() - 1
            bit = 1 << members[local]
            diff = degrees[local] - 2 * (occupied & links[local]).bit_count()
            boundary_size += -diff if occupied & bit else diff
            occupied ^= bit
            last_gray = gray
            if gray.bit_count() >= 3:
                assert boundary_size >= 7
                tested += 1
                attained += boundary_size == 7
    return {"ambient_box": [2, 3, 3], "nonempty_downsets": cases,
            "ordinary_subsets_of_size_at_least_three": tested, "cuts_of_size_seven": attained}


if __name__=="__main__":
    print(json.dumps({"coordinate_sources":[verify(5),verify(6)],
                      "opposing_terminal_groups":opposing_terminal_groups(),
                      "all_small_downsets":check_all_small_downsets()},indent=2))
