"""Classify the saturated nine-site shores without a growth census."""

from collections import Counter
from dataclasses import dataclass
from importlib import util
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import sys


PROOFS = Path(__file__).resolve().parents[2]


def load(ticket, filename):
    path, = (PROOFS / ticket).glob("*/" + filename)
    spec = util.spec_from_file_location("suffix_" + path.stem, path)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RULES = load("CUBIC-FROM-A-KNOT-20261117-001", "check.py")
TABLES = load("VARIABLE-OUTPUT-READER-20261118-001A", "check_classes.py")
FRESH_TEST = ("a-new-name", "another-new-name", "third-new-name")
INFINITY = 255


@dataclass(frozen=True)
class Shape:
    first: str
    second: str
    edges: tuple[str, ...]
    latest: str = "x"

    def adjacency(self):
        graph = {site: set() for site in self.first + self.second}
        for a, b in self.edges:
            graph[a].add(b)
            graph[b].add(a)
        return graph


SHAPES = {
    "latest_on_four_site_side": Shape(
        "abcx", "uvpqr",
        (*tuple(a + b for a, b in product("abc", "uv")), "ap", "bp", "aq", "cq", "br", "cr",
         "xp", "xq", "xr"),
    ),
    "latest_on_five_site_side": Shape(
        "abcz", "pqrsx",
        ("zp", "zq", "zr", "zs", "bp", "cp", "aq", "cq", "ar", "br", "as", "bs", "ax", "bx", "cx"),
    ),
}


def contains_k33(first, neighbors):
    return any(len(neighbors[a] & neighbors[b] & neighbors[c]) >= 3
               for a, b, c in combinations(first, 3))


def admissible_latest(graph, site):
    parents = graph[site]
    return len(parents) <= 3 and (
        len(parents) < 3 or not any(parents <= neighbors for other, neighbors in graph.items() if other != site)
    )


def check_eight():
    first, second = "abcd", "pqrs"
    potential = tuple(a + b for a, b in product(first, second))
    candidates = k33_free = possible_latest = 0
    for present in combinations(potential, 13):
        candidates += 1
        graph = Shape(first, second, present).adjacency()
        if contains_k33(first, graph):
            continue
        k33_free += 1
        possible_latest += sum(admissible_latest(graph, site) for site in graph)
    assert possible_latest == 0
    return {"labeled_4_by_4_graphs_with_13_edges": candidates, "K33_free": k33_free,
            "admissible_last_sites": possible_latest}


def check_nine_shapes():
    first, second = "abcd", "pqrst"
    potential = tuple(a + b for a, b in product(first, second))
    counts = Counter()
    for present in combinations(potential, 15):
        counts["labeled_4_by_5_graphs_with_15_edges"] += 1
        graph = Shape(first, second, present).adjacency()
        if contains_k33(first, graph):
            continue
        counts["K33_free"] += 1
        for latest in graph:
            if len(graph[latest]) != 3 or not admissible_latest(graph, latest):
                continue
            if any(not 3 <= len(nearby) <= 4 for site, nearby in graph.items() if site != latest):
                continue
            current = first if latest in first else second
            opposite = set(second if latest in first else first)
            parents = graph[latest]
            older = tuple(site for site in current if site != latest)
            assert all(opposite - parents <= graph[site] and len(parents - graph[site]) == 1 for site in older)
            omitted = Counter(a for site in older for a in parents - graph[site])
            assert sorted(omitted.values()) == ([1, 1, 1] if latest in first else [1, 1, 2])
            counts["latest_on_four_site_side" if latest in first else "latest_on_five_site_side"] += 1
    return dict(counts)


def loose_bits(rows):
    users, _ = RULES.incidence(rows)
    return tuple(sorted(bit for bit, holders in users.items() if len(holders) == 1))


def replay(order, shape):
    graph = shape.adjacency()
    used = {}
    rows = {}
    events = []
    cursor = 0
    for index, site in enumerate(order):
        parents = tuple(sorted(p for p in graph[site] if p in rows))
        future = tuple(sorted(graph[site] - rows.keys()))
        arity = 3 if index == 0 else (5 if site == shape.latest else 4)
        fresh_count = arity - len(parents)
        inputs = tuple(used[p, site] for p in parents)
        fresh = tuple(range(cursor, cursor + fresh_count))
        assert fresh_count == 3 if index == 0 else fresh_count in (2, 3)
        assert len(future) <= fresh_count
        if parents:
            assert RULES.legal_local_move(rows, inputs, FRESH_TEST)
        else:
            assert not rows
        used.update({(site, later): port for later, port in zip(future, fresh[:len(future)], strict=True)})
        rows[site] = (*inputs, *fresh)
        events.append({"site": site, "parents": parents, "inputs": inputs, "fresh": fresh})
        cursor += fresh_count
    assert cursor == 21
    return rows, events


def order_count(shape):
    graph = shape.adjacency()
    closed_by_seed = Counter()
    incoming_profiles = Counter()
    for seed in sorted(graph):
        if seed == shape.latest or len(graph[seed]) != 3:
            continue
        for middle in permutations(sorted(graph.keys() - {seed, shape.latest})):
            order = (seed, *middle, shape.latest)
            order_index = {site: i for i, site in enumerate(order)}
            internal_parents = {site: sum(order_index[p] < order_index[site] for p in graph[site])
                                for site in middle}
            if any(p > 2 for p in internal_parents.values()):
                continue
            exterior_slots = frozenset(site for site in middle if len(graph[site]) == 3)
            assert len(exterior_slots) == 4
            for count in (0, 1, 2):
                for receivers in combinations(sorted(exterior_slots), count):
                    if any(not 1 <= p + (site in receivers) <= 2
                           for site, p in internal_parents.items()):
                        continue
                    first_out = min(order_index[site] for site in exterior_slots.difference(receivers))
                    if any(order_index[site] <= first_out for site in receivers):
                        continue
                    incoming_profiles[count] += 1
                    if count == 0:
                        replay(order, shape)
                        closed_by_seed[seed] += 1
    assert incoming_profiles[0] == sum(closed_by_seed.values())
    assert incoming_profiles[1] == incoming_profiles[2] == 0
    return {"orders_by_seed": dict(sorted(closed_by_seed.items())),
            "possible_orders_and_input_receiver_sets_by_incoming_count": {
                count: incoming_profiles[count] for count in (0, 1, 2)
            }}


def masks(rows):
    return tuple(sum(1 << bit for bit in word) for word in rows.values())


def xor_subsets(stars):
    words = [0]
    for star in stars:
        words += [word ^ star for word in words]
    assert len(words) == len(set(words))
    return tuple(words)


def members(word):
    return tuple(i for i in range(word.bit_length()) if word >> i & 1)


def bond_table(rows):
    words = xor_subsets(masks(rows))
    width = 1 + max(bit for scope in rows.values() for bit in scope)
    table = [bytearray([INFINITY] * width) for _ in range(width)]
    for i, row in enumerate(table):
        row[i] = 0
    minimal = []
    for word in sorted(words[1:], key=lambda support: (support.bit_count(), support)):
        if any(word & bond == bond for bond in minimal):
            continue
        minimal.append(word)
        for a, b in combinations(members(word), 2):
            table[a][b] = table[b][a] = min(table[a][b], word.bit_count())
    return tuple(map(bytes, table)), frozenset(minimal), words


def triples(rows):
    return frozenset(frozenset(action) for action in combinations(loose_bits(rows), 3)
                     if RULES.legal_local_move(rows, action, FRESH_TEST))


def named_actions(menu):
    return tuple(sorted(map(tuple, map(sorted, menu))))


def boundary(rows, chosen):
    support = 0
    for site, star in zip(rows, masks(rows), strict=True):
        if site in chosen:
            support ^= star
    return support


def audit_cut_tables(rows):
    table, bonds, cuts = bond_table(rows)
    names = tuple(rows)
    by_size = Counter()
    records = []
    for sites, word in enumerate(cuts):
        if sites.bit_count() < 3 or word.bit_count() > 6:
            continue
        shore = frozenset(names[index] for index in members(sites))
        assert boundary(rows, shore) == word
        by_size[len(shore)] += 1
        records.append({"shore": tuple(site for site in names if site in shore),
                        "boundary": members(word), "is_bond": word in bonds})
    return table, {"width": len(table), "total_cuts": len(cuts) - 1,
                   "minimal_supports": len(bonds), "large_short_cuts": records,
                   "number_of_large_short_cuts_by_shore_size": dict(sorted(by_size.items()))}


def witness(shape, order):
    rows, events = replay(order, shape)
    prefix = dict(tuple(rows.items())[:-1])
    _, prefix_cuts = audit_cut_tables(prefix)
    table, cut_report = audit_cut_tables(rows)
    assert len(loose_bits(prefix)) == 7 and len(loose_bits(rows)) == 6
    assert not prefix_cuts["large_short_cuts"]
    assert cut_report["number_of_large_short_cuts_by_shore_size"] == {9: 1}
    assert cut_report["large_short_cuts"][0]["is_bond"]
    event = frozenset(events[-1]["inputs"])
    assert event in triples(prefix)
    outside_pair = next(pair for pair in combinations(loose_bits(rows), 2)
                        if RULES.legal_local_move(rows, pair, FRESH_TEST))
    attachment_name = "outside_binary"
    attached = {**rows, attachment_name: (*outside_pair, 21, 22)}
    _, proper = audit_cut_tables(attached)
    assert cut_report["large_short_cuts"][0] in proper["large_short_cuts"]
    permutation = list(range(21))
    Random(7816).shuffle(permutation)
    renamed_rows = {site: tuple(permutation[bit] for bit in scope) for site, scope in rows.items()}
    renamed, _, _ = bond_table(renamed_rows)
    assert TABLES.disagreement(table, renamed, permutation) is None
    assert TABLES.transported(triples(rows), permutation) == triples(renamed_rows)
    full_hex = bytes(table[a][b] for a, b in combinations(range(21), 2)).hex()
    record = {"history": events, "junction_supports": rows, "initial_triple_join": tuple(sorted(event)),
              "legal_triples_before": named_actions(triples(prefix)), "legal_triples_after": named_actions(triples(rows)),
              "before": prefix_cuts, "after": cut_report,
              "proper_shore_control": {"outside_binary_support": attached[attachment_name], **proper},
              "full_K_upper_triangle_hex": full_hex,
              "verified_relabeling": tuple(permutation)}
    return table, triples(rows), record


def compare_tables(examples):
    names = tuple(examples)
    quotients = {tag: TABLES.Quotient.make(entry[0]) for tag, entry in examples.items()}
    result = {"self": {}}
    for tag, (table, menu, _) in examples.items():
        size, blocks, generators = quotients[tag].automorphisms()
        assert all(TABLES.disagreement(table, table, g) is None for g in generators)
        conflicting = next((g for g in generators if TABLES.transported(menu, g) != menu), None)
        result["self"][tag] = {"automorphisms": size, "quotient_automorphisms": blocks,
                              "permutes_triple_menu": conflicting is None,
                              "first_adverse_permutation": conflicting}
    left, right = (quotients[tag] for tag in names)
    crossing = next(TABLES.isometries(left.colored, right.colored), None)
    result["cross"] = {"full_table_isometry_exists": crossing is not None}
    if crossing is not None:
        mapping = left.lift(right, crossing)
        ta, ma, _ = examples[names[0]]
        tb, mb, _ = examples[names[1]]
        assert TABLES.disagreement(ta, tb, mapping) is None
        result["cross"].update({"left_to_right": mapping, "sends_left_menu_to_right": TABLES.transported(ma, mapping) == mb})
    return result


def run():
    orders = {
        "latest_on_four_site_side": tuple("uabvcpqrx"),
        "latest_on_five_site_side": tuple("pbrzsaqcx"),
    }
    examples = {tag: witness(shape, orders[tag]) for tag, shape in SHAPES.items()}
    return {
        "eight_site_edge_control": check_eight(),
        "nine_site_shape_coverage": check_nine_shapes(),
        "saturated_order_counts": {tag: order_count(shape) for tag, shape in SHAPES.items()},
        "minimum_shore_sites": 9, "minimum_source_width": 21, "minimum_proper_source_width": 23,
        "pair_encoding": "hexadecimal K in lexicographic upper-triangle order, ff for infinity",
        "replayed_minimum_sources": {tag: fixture[2] for tag, fixture in examples.items()},
        "full_scalar_comparison_of_minimum_sources": compare_tables(examples),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
