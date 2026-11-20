"""Independent physical controls for the conditional-information lower bound."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORD = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / ORD / (ORD + "-E001_ordinary")))
from end_operator import from_stars, step


def successor_count(rows):
    """Nonempty maximal rectangles in the binary relation plus uncovered singletons."""
    n = len(rows)
    full = (1 << n) - 1
    columns = [sum(1 << i for i, row in enumerate(rows) if row & (1 << j)) for j in range(n)]
    count = rows.count(0) + columns.count(0)
    right = [full] * (1 << n)
    for subset in range(1, 1 << n):
        bit = subset & -subset
        right[subset] = right[subset ^ bit] & rows[bit.bit_length() - 1]
        partners = right[subset]
        if partners and all((subset & (1 << i)) or (row & partners) != partners for i, row in enumerate(rows)):
            count += 1
    return count


def graph_check(rows):
    """Enumerate actual maximal unheld groups through the marked birth in the sibling graph."""
    n = len(rows)
    center = 2 * n
    left, right = range(n), range(n, 2 * n)
    graph = nx.Graph()
    for group in ([center, *left], [center, *right]):
        graph.add_edges_from(combinations(group, 2))
    for i, choices in enumerate(rows):
        for j in range(n):
            if choices & (1 << j):
                graph.add_edge(i, n + j)
    big = [set(q) for q in nx.find_cliques(graph) if center in q and set(q) & set(left) and set(q) & set(right)]
    covered = set().union(*big) - {center}
    return len(big) + len(set(graph.neighbors(center)) - covered)


def poset_rows(predecessors):
    full = (1 << len(predecessors)) - 1
    return [full ^ p for p in predecessors]


def coded_poset(digits):
    """An independent point doubles the number of downward-closed subsets; a new greatest adds one."""
    pred = []
    for digit in digits:
        pred.append(1 << len(pred))
        if digit:
            pred.append((1 << (len(pred) + 1)) - 1)
    pred.append(1 << len(pred))
    return pred


def physical(predecessors):
    rows = poset_rows(predecessors)
    n = len(rows)
    meetings = {}
    loose = {"U": n + 1, "V": n + 1, "Z": 2}
    bits_per_place = {}
    for i in range(n):
        loose[f"r{i}"] = loose[f"c{i}"] = 1

    def meet(a, b, multiplicity=2):
        key = tuple(sorted((a, b)))
        assert a != b and key not in meetings
        meetings[key] = multiplicity

    def witness(holder, live):
        for point in live:
            meet(holder, point)

    for i in range(n):
        witness(f"R{i}", ["U", "V", *[f"z{i}_{j}" for j in range(n)]])
        witness(f"C{i}", ["U", "V", *[f"z{j}_{i}" for j in range(n)]])
        witness(f"Ur{i}", ["U", f"r{i}"])
        witness(f"Vc{i}", ["V", f"c{i}"])
        for j in range(n):
            cell = f"z{i}_{j}"
            witness(f"er{i}_{j}", [f"r{i}", cell])
            witness(f"ec{i}_{j}", [f"c{j}", cell])
            if rows[i] & (1 << j):
                loose[cell] = 2
            else:
                loose["Z"] += 2

    old = set(loose) | {v for pair in meetings for v in pair}
    for v in sorted(old - {"U", "V"}):
        for router in ("L", "R"):
            via = f"via-{v}-{router}"
            meet(v, via)
            meet(via, router)

    total_loose = sum(loose.values())
    light = sum(meetings.values())
    heavy_width = 1 + total_loose + light
    for cell in ["Z", *[f"z{i}_{j}" for i in range(n) for j in range(n)]]:
        via = f"H-{cell}"
        meet(cell, via, heavy_width)
        meet(via, "K", heavy_width)
    order = sorted({v for pair in meetings for v in pair})
    index = {v: i for i, v in enumerate(order)}
    supports = [[] for _ in order]
    bound = 0
    shadow = nx.Graph()
    for (u, v), copies in sorted(meetings.items()):
        for holder in (u, v):
            supports[index[holder]].extend(range(bound, bound + copies))
        shadow.add_edge(u, v)
        bound += copies

    # Keep the loose identities fixed across preparations, including packets moved to Z.
    for v, number in [("U", n + 1), ("V", n + 1), ("Z", 2),
                      *[(f"r{i}", 1) for i in range(n)], *[(f"c{i}", 1) for i in range(n)]]:
        supports[index[v]].extend(range(bound, bound + number))
        bound += number
    for i, row in enumerate(rows):
        for j in range(n):
            holder = f"z{i}_{j}" if row & (1 << j) else "Z"
            supports[index[holder]].extend([bound, bound + 1])
            bound += 2
    inp = tuple(sorted((index["U"], index["V"])))
    shadow.add_edges_from(("outside", v) for v, count in loose.items() if count)
    assert nx.is_biconnected(shadow)
    assert all(len(s) >= 3 for s in supports)
    marked = [tuple(supports[k]) for k in inp]
    assert all(len(s) == 7 * n + 1 for s in marked)

    # A bond touching the marked supports under NAE must be one of these physical stars.
    by_name = {v: set(supports[index[v]]) for v in order}
    assert all(not (sup < by_name[v]) for u, sup in by_name.items() for v in order if u != v)
    marks = set().union(*map(set, marked))
    for v, support in by_name.items():
        if marks & support:
            bits_per_place[v] = tuple(sorted(support))
    end = from_stars(supports)
    outcomes = {}
    for law in ("parity", "nae"):
        turn = step(end, law=law)
        expect = {inp}
        for i in range(n):
            expect.add(tuple(sorted([index["U"], index[f"r{i}"],
                                    *[index[f"z{i}_{j}"] for j in range(n) if rows[i] & (1 << j)]])))
            expect.add(tuple(sorted([index["V"], index[f"c{i}"],
                                    *[index[f"z{j}_{i}"] for j in range(n) if rows[j] & (1 << i)]])))
        assert expect == set(g for g in turn.parents if len(g) > 1)
        pos = turn.parents.index(inp)
        assert turn.fresh[pos] == turn.demand[pos] == successor_count(rows)
        outcomes[law] = {"wanted_fresh": turn.fresh[pos], "births": len(turn.parents)}
    return ({"knots": len(order), "distinctions": bound, "parent_width": len(marked[0]),
             "light_shared": light, "loose": total_loose, "heavy_width": heavy_width,
             "matrix": rows, "outcomes": outcomes}, marked, bits_per_place)


def reached_family(maximum=9):
    """Read the second update on a doubled five-knot path for each admissible k."""
    sizes = {}
    for h in range(2, maximum + 1):
        values = []
        for k in range(2, h + 2):
            stars = [[] for _ in range(5)]
            next_bit = 0
            for u in range(4):
                for holder in (u, u + 1):
                    stars[holder].extend([next_bit, next_bit + 1])
                next_bit += 2
            for i, slots in enumerate([h + 2 - k, 0, k, 0, h + 2 - k]):
                stars[i].extend(range(next_bit, next_bit + slots))
                next_bit += slots
            for law in ("parity", "nae"):
                first = step(from_stars(stars), law=law)
                roots = tuple(first.parents.index(x) for x in ((0, 2), (2, 4)))
                assert [first.fresh[i] for i in roots] == [h, h]
                second = step(first.end, law=law)
                index = second.parents.index(tuple(sorted(roots)))
                assert second.fresh[index] == 2 * h - k
            values.append(2 * h - k)
        sizes[h] = values
    return sizes


def main():
    graphs = {}
    for n in (1, 2, 3):
        full = (1 << n) - 1
        freq = Counter()
        for sequence in range(1 << (n * n)):
            rows = [(sequence >> (i * n)) & full for i in range(n)]
            value = successor_count(rows)
            assert value == graph_check(rows)
            freq[value] += 1
        graphs[n] = dict(sorted(freq.items()))
    codes = {}
    for length in (2, 4, 6, 8):
        values = []
        for ones in combinations(range(length), length // 2):
            digits = [i in ones for i in range(length)]
            pred = coded_poset(digits)
            value = successor_count(poset_rows(pred))
            expected = 2 * int("1" + "".join(str(int(b)) for b in digits), 2) - 2
            assert value == expected
            values.append(value)
        assert len(set(values)) == len(values)
        codes[length] = dict(indices=len(pred), distinct_counts=len(values), min=min(values), max=max(values))
    # Principal lower sets for 1,2 < 3, and for 1 < 2, with one independent point in each.
    first = physical([1, 2, 7, 8])
    second = physical([1, 3, 4, 8])
    assert first[1:] == second[1:]
    assert [first[0]["outcomes"]["parity"]["wanted_fresh"], second[0]["outcomes"]["parity"]["wanted_fresh"]] == [8, 10]
    record = {"all_small_sibling_relations": graphs, "fixed_weight_binary_codes": codes,
              "second_update_five_knot_path": reached_family(),
              "four_index_physical_pairs": [first[0], second[0]], "equal_root_holdings": True,
              "equal_actual_nae_bonds_touching_roots": True,
              "parity_complete_minima": "all orders on the two parent supports by the rerouting proof, not a full table enumeration"}
    output = ROOT / "artifacts" / HERE.parent.name / HERE.name / "conditional_bits.json"
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record["four_index_physical_pairs"]))


if __name__ == "__main__":
    main()
