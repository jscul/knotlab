"""Exact filled-candidate H1 over GF(2) through the smaller block-intersection graph."""
import argparse
from array import array
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts"
ARCHIVE = ARTIFACTS / "HUB-GUIDED-SAMPLE-20261119-001" / "HUB-GUIDED-SAMPLE-20261119-001-E001_sampler"
OUTPUT = ARTIFACTS / HERE.parent.name / HERE.name / "cycles_screen.json"
INITIAL = OUTPUT.with_name("cycles_initial.json")


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def block_graph(n, blocks):
    membership = [0] * n
    for b, block in enumerate(blocks):
        mark = 1 << b
        for u in block:
            membership[u] |= mark
    counts = Counter(membership)
    adjacency = [0] * len(blocks)
    for shared in counts:
        for b in bits(shared):
            adjacency[b] |= shared ^ (1 << b)
    return adjacency, membership, counts


def eliminate_link_forests(adjacency):
    """Parameterize the gauge-fixed cochains satisfying selected triples."""
    n = len(adjacency)
    remaining = set(range(n))
    degrees = [row.bit_count() for row in adjacency]
    placed = 0
    order = []
    parent = [-1] * n
    generators = []
    labels = [{} for _ in adjacency]
    link_components = Counter()
    selected = 0

    while remaining:
        v = max(remaining, key=lambda u: ((adjacency[u] & placed).bit_count(), degrees[u], -u))
        remaining.remove(v)
        order.append(v)
        pending = adjacency[v] & placed
        components = 0
        while pending:
            root_bit = pending & -pending
            pending ^= root_bit
            u = root_bit.bit_length() - 1
            initial = 0
            if components == 0:
                parent[v] = u
            else:
                initial = 1 << len(generators)
                generators.append((v, u))
            components += 1
            todo = [(u, initial)]
            while todo:
                w, value = todo.pop()
                if value:
                    labels[v][w] = labels[w][v] = value
                new = adjacency[w] & pending
                pending ^= new
                selected += new.bit_count()
                todo.extend((x, value ^ labels[w].get(x, 0)) for x in bits(new))
        link_components[components] += 1
        placed |= 1 << v

    assert sum(degrees) // 2 == n - link_components[0] + len(generators) + selected
    return order, parent, generators, labels, link_components, selected


def junction_components(membership_counts, order, parent):
    roots = [-1] * len(parent)
    for b in order:
        roots[b] = b if parent[b] < 0 else roots[parent[b]]
    sites = Counter()
    for code, count in membership_counts.items():
        if not code:
            continue
        own = roots[(code & -code).bit_length() - 1]
        assert all(roots[b] == own for b in bits(code))
        sites[own] += count
    histogram = Counter(sites.values())
    if membership_counts[0]:
        histogram[1] += membership_counts[0]
    return histogram


def add_row(pivots, value):
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            pivots[pivot] = value
            return True
        value ^= pivots[pivot]
    return False


def free_basis(dimension, pivots):
    ordered = sorted(pivots.items())
    for j in range(dimension):
        if j in pivots:
            continue
        value = 1 << j
        for k, equation in ordered:
            if (value & equation).bit_count() % 2:
                value ^= 1 << k
        yield value


def first_violated_triple(q, upper, labels, budget):
    """Return the first wrong triple or certify all triples, within an edge-scan budget."""
    odd = [sum(1 << v for v, col in row.items() if (q & col).bit_count() % 2) for row in labels]
    tested = 0
    for u, neighbors in enumerate(upper):
        for v in bits(neighbors):
            if tested == budget:
                return "capped", None, tested
            tested += 1
            common = neighbors & upper[v]
            disagree = odd[u] ^ odd[v]
            if odd[u] >> v & 1:
                disagree = ~disagree
            wrong = common & disagree
            if wrong:
                w = (wrong & -wrong).bit_length() - 1
                return "violation", (u, v, w), tested
    return "verified", None, tested


def exact_triple_rank(adjacency, labels, dimension, budget):
    upper = [row >> (u + 1) << (u + 1) for u, row in enumerate(adjacency)]
    pivots = {}
    equations = []
    scanned = 0
    verified = set()
    while True:
        proposals = list(free_basis(dimension, pivots))
        for q in proposals:
            if q in verified:
                continue
            status, wrong, used = first_violated_triple(q, upper, labels, budget - scanned)
            scanned += used
            if status == "capped":
                independent = {}
                lower = [q for q in sorted(verified) if add_row(independent, q)]
                return False, lower, equations, scanned
            if status == "verified":
                verified.add(q)
                continue
            u, v, w = wrong
            row = labels[u].get(v, 0) ^ labels[v].get(w, 0) ^ labels[u].get(w, 0)
            assert (q & row).bit_count() % 2 and add_row(pivots, row)
            equations.append({"blocks": wrong, "free_row_hex": hex(row)})
            break
        else:
            return True, proposals, equations, scanned


def forest_route(u, v, parent):
    first = []
    while u >= 0:
        first.append(u)
        u = parent[u]
    positions = {u: i for i, u in enumerate(first)}
    other = []
    while v not in positions:
        assert v >= 0
        other.append(v)
        v = parent[v]
    return first[:positions[v] + 1] + list(reversed(other))


def positive_certificates(basis, generators, parent, labels, blocks, membership):
    witness = {}

    def common_junction(u, v):
        key = tuple(sorted((u, v)))
        if key not in witness:
            witness[key] = min(set(blocks[u]).intersection(blocks[v]))
        return witness[key]

    def cyclic_pairs(route):
        return zip(route, route[1:] + route[:1])

    certificates = []
    for q in basis:
        chord = generators[(q & -q).bit_length() - 1]
        block_cycle = forest_route(*chord, parent)
        sites = [common_junction(u, v) for u, v in cyclic_pairs(block_cycle)]
        odd = [sum(1 << v for v, col in row.items() if (q & col).bit_count() % 2) for row in labels]

        block_parity = sum(odd[u] >> v & 1 for u, v in cyclic_pairs(block_cycle)) % 2
        literal_parity = 0
        for u, v in cyclic_pairs(sites):
            a, b = membership[u], membership[v]
            shared = a & b
            assert shared
            root_u, root_v, hold = ((j & -j).bit_length() - 1 for j in (a, b, shared))
            literal_parity ^= (odd[root_u] >> hold ^ odd[root_v] >> hold) & 1
        assert block_parity == literal_parity == 1
        certificates.append({"free_cochain_hex": hex(q),
                             "block_cocycle_rows_hex": [hex(row) for row in odd],
                             "block_cycle": block_cycle, "junction_walk": sites,
                             "block_and_junction_pairing": literal_parity})
    return certificates


def solve(n, blocks, budget):
    adjacency, membership, counts = block_graph(n, blocks)
    order, parent, generators, labels, links, chosen = eliminate_link_forests(adjacency)
    dimension = len(generators)
    exact, basis, extra, scanned = exact_triple_rank(adjacency, labels, dimension, budget)
    components = junction_components(counts, order, parent)
    lower, upper = len(basis), dimension - len(extra)
    assert 0 <= lower <= upper and (not exact or lower == upper)
    return {"live": n, "blocks": len(blocks), "incidence_signatures": len(counts),
            "block_intersection_pairs": sum(a.bit_count() for a in adjacency) // 2,
            "components": sum(components.values()), "component_size_histogram": dict(components),
            "isolated_junctions": counts[0], "block_order": order, "block_forest_parents": parent,
            "lower_link_component_histogram": dict(links), "selected_link_triples": chosen,
            "gauged_free_pairs": generators, "extra_triangle_pivots": extra, "tested_pairs": scanned,
            "h1_lower": lower, "h1_upper": upper, "exact": exact,
            "positive_certificates": positive_certificates(basis, generators, parent, labels, blocks, membership)}


def literal_h1(n, blocks):
    pairs = sorted({pair for block in blocks for pair in combinations(sorted(block), 2)})
    pair_ids = {pair: i for i, pair in enumerate(pairs)}
    boundary_one, boundary_two = {}, {}
    for u, v in pairs:
        add_row(boundary_one, (1 << u) ^ (1 << v))
    for u, v, w in combinations(range(n), 3):
        triangle = ((u, v), (u, w), (v, w))
        if all(pair in pair_ids for pair in triangle):
            add_row(boundary_two, sum(1 << pair_ids[pair] for pair in triangle))
    return n - len(boundary_one), len(pairs) - len(boundary_one) - len(boundary_two)


def reduce_word(word, cyclic=False):
    result = []
    for letter in word:
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    lower, upper = 0, len(result)
    while cyclic and upper - lower > 1 and result[lower] == -result[upper - 1]:
        lower += 1
        upper -= 1
    return tuple(result[lower:upper])


def inverse(word):
    return tuple(-letter for letter in reversed(word))


def presentation(n, blocks):
    adjacency = [0] * n
    for block in blocks:
        mask = sum(1 << v for v in block)
        for v in block:
            adjacency[v] |= mask ^ (1 << v)
    _, parent, _, _, _, _ = eliminate_link_forests(adjacency)
    forest = {tuple(sorted((u, v))) for v, u in enumerate(parent) if u >= 0}
    generators = [(u, v) for u, row in enumerate(adjacency) for v in bits(row) if u < v and (u, v) not in forest]
    lookup = {pair: j + 1 for j, pair in enumerate(generators)}
    relators = {}
    for u, row in enumerate(adjacency):
        higher = (v for v in bits(row) if u < v)
        for v, w in combinations(higher, 2):
            if not adjacency[v] >> w & 1:
                continue
            word = (lookup.get((u, v), 0), lookup.get((v, w), 0), -lookup.get((u, w), 0))
            word = tuple(x for x in word if x)
            if word:
                relators[u, v, w] = word
    return parent, sorted(forest), generators, relators


def pi1_certificate(n, blocks):
    """Eliminate generators that occur exactly once in a remaining relator."""
    parents, forest, generators, original = presentation(n, blocks)
    relators = original.copy()
    active = set(range(1, len(generators) + 1))
    moves = []
    while active:
        choice = None
        for triple in sorted(relators, key=lambda t: (len(relators[t]), t)):
            word = relators[triple]
            counts = Counter(map(abs, word))
            single = next((j for j, letter in enumerate(word) if counts[abs(letter)] == 1), None)
            if single is not None:
                letter = word[single]
                rest = word[single+1:] + word[:single]
                choice = triple, abs(letter), inverse(rest) if letter > 0 else rest
                break
        if choice is None:
            break
        triple, generator, replacement = choice
        active.remove(generator)
        del relators[triple]
        opposite = inverse(replacement)
        for label, word in list(relators.items()):
            expanded = tuple(y for x in word
                             for y in (replacement if x == generator else opposite if x == -generator else (x,)))
            relators[label] = reduce_word(expanded, cyclic=True)
        moves.append({"triple": triple, "generator": generator, "replacement": replacement})
    remaining = [word for word in relators.values() if word]
    free_ranks = None
    if not remaining:
        free_ranks = dict.fromkeys((u for u, p in enumerate(parents) if p < 0), 0)
        for generator in active:
            u, _ = generators[generator - 1]
            while parents[u] >= 0:
                u = parents[u]
            free_ranks[u] += 1
    return {"trivial_in_every_component": not active, "forest_pairs": forest,
            "generator_pairs_in_order": generators, "initial_relators": list(original.items()),
            "eliminations": moves, "remaining_generators": sorted(active),
            "remaining_relators": remaining, "free_ranks_by_component_forest_root": free_ranks}


def initial_roster(source):
    meeting = [set() for _ in source["sizes"]]
    degrees = Counter()
    for a, b in source["edges"]:
        meeting[a].add(b)
        meeting[b].add(a)
        degrees[a] += 1
        degrees[b] += 1
    live = [a for a, size in enumerate(source["sizes"]) if size > degrees[a]]
    normalized = {a: i for i, a in enumerate(live)}
    subsets = {frozenset(normalized[a] for a in row if a in normalized) for row in meeting}
    blocks = sorted(tuple(sorted(s)) for s in subsets if len(s) >= 2 and not any(s < t for t in subsets))
    return live, [source["sizes"][a] - degrees[a] for a in live], blocks


def initial_screen(archive, input_dir, budget):
    rows = []
    staged = {(r["case"], r["age"]): r for r in archive["stages"]}
    for case, source in sorted(archive["literal_starts"].items()):
        live, opens, blocks = initial_roster(source)
        control_map = None
        if row := staged.get((case, 0)):
            n, prior_blocks = read_stage(input_dir, row)
            assert n == len(live)
            target = {frozenset(b) for b in prior_blocks}
            open_file = row["files"]["opens"]
            compressed_opens = (input_dir / open_file["name"]).read_bytes()
            assert sha256(compressed_opens).hexdigest() == open_file["sha256"]
            target_opens = json.loads(gzip.decompress(compressed_opens))
            control_map = next(p for p in permutations(range(n))
                               if [target_opens[p[v]] for v in range(n)] == opens
                               and {frozenset(p[v] for v in block) for block in blocks} == target)
        result = solve(len(live), blocks, budget)
        assert result["exact"]
        assert literal_h1(len(live), blocks) == (result["components"], result["h1_lower"])
        pi1 = pi1_certificate(len(live), blocks)
        assert not pi1["trivial_in_every_component"] or result["h1_upper"] == 0
        result.update({"case": case, "age": 0, "literal_live_junctions": live, "blocks_literal": blocks,
                       "loose_counts": opens, "archived_control_relabeling": control_map, "pi1": pi1})
        rows.append(result)
        print(case, 0, len(live), len(blocks), result["components"],
              result["h1_lower"], result["h1_upper"], pi1["trivial_in_every_component"], flush=True)
    return rows


def controls(budget):
    named = {
        "four_cycle": (4, [(0, 1), (1, 2), (2, 3), (3, 0)], 1, 1),
        "four_cycle_filled_by_diagonal": (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], 1, 0),
        "triple_with_no_common_block": (3, [(0, 1), (1, 2), (0, 2)], 1, 0),
        "single_block": (7, [tuple(range(7))], 1, 0),
        "two_four_cycles_and_an_isolate": (9, [(x+u, x+v) for x in (0, 4)
                                               for u, v in ((0, 1), (1, 2), (2, 3), (3, 0))], 3, 2),
    }
    for t in (2, 3, 4):
        pairs = [(u, v) for u, v in combinations(range(2*t), 2) if u // 2 != v // 2]
        named[f"partnered_{t}"] = (2*t, pairs, 1, int(t == 2))

    # Four tripled classes with consecutive joins, and a last block joining
    # one member of each class. Its triangles fill the remaining relation.
    joined = [(u, v) for u, v in combinations(range(12), 2)
              if (u // 3 - v // 3) % 4 in (0, 1, 3)]
    joined.extend((3*j, 12) for j in range(4))
    incidence = [tuple(j for j, pair in enumerate(joined) if i in pair) for i in range(13)]
    named["late_triple_pivot"] = (len(joined), incidence, 1, 0)

    report = {}
    for name, (n, blocks, b0, b1) in named.items():
        row = solve(n, blocks, budget)
        assert literal_h1(n, blocks) == (b0, b1)
        assert row["exact"] and (row["components"], row["h1_lower"]) == (b0, b1)
        if name != "late_triple_pivot":
            row["pi1"] = pi1_certificate(n, blocks)
            assert row["pi1"]["trivial_in_every_component"] == (b1 == 0)
        report[name] = row
    assert report["late_triple_pivot"]["extra_triangle_pivots"]
    cap_control = solve(len(joined), incidence, 0)
    assert not cap_control["exact"] and cap_control["h1_lower"] == 0 and cap_control["h1_upper"] > 0

    def compare(n, blocks):
        row = solve(n, blocks, budget)
        answer = (row["components"], row["h1_lower"])
        assert row["exact"] and answer == literal_h1(n, blocks), (n, blocks, answer)
        return len(row["extra_triangle_pivots"])

    graphs = 0
    largest_residual = 0
    for n in range(1, 6):
        possible = list(combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            largest_residual = max(largest_residual, compare(n, [possible[i] for i in bits(mask)]))
            graphs += 1
    rng = Random(202611197108)
    samples = 0
    for n in range(6, 11):
        for _ in range(96):
            blocs = {frozenset(rng.sample(range(n), rng.randint(2, n))) for _ in range(rng.randrange(2*n))}
            blocks = sorted(tuple(sorted(b)) for b in blocs if not any(b < other for other in blocs))
            largest_residual = max(largest_residual, compare(n, blocks))
            samples += 1
    return {"named": report, "literal_labelled_graph_count": graphs, "literal_hypergraph_samples": samples,
            "largest_residual_rank_on_small_panels": largest_residual,
            "late_pivot_zero_budget_range": [cap_control["h1_lower"], cap_control["h1_upper"]]}


def read_stage(input_dir, row):
    source = row["files"]["blocks"]
    path = input_dir / source["name"]
    digest = sha256()
    with path.open("rb") as f:
        header = f.readline()
        digest.update(header)
        n, size = map(int, header.split())
        blocks = []
        for line in f:
            digest.update(line)
            blocks.append(array("I", map(int, line.split())))
    assert digest.hexdigest() == source["sha256"]
    assert (n, size, len(blocks)) == (row["live"], row["blocks"], size)
    return n, blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--pair-budget", type=int, default=20_000_000)
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--initial-only", action="store_true")
    parser.add_argument("--stage", action="append", help="archived stage to replay, e.g. start-03-age08")
    args = parser.parse_args()
    assert args.pair_budget >= 0
    control = controls(args.pair_budget)
    if args.controls_only:
        print(control["literal_labelled_graph_count"], control["literal_hypergraph_samples"],
              len(control["named"]["late_triple_pivot"]["extra_triangle_pivots"]))
        return

    manifest = ARCHIVE / "stages.json"
    manifest_bytes = manifest.read_bytes()
    archive = json.loads(manifest_bytes)
    metadata = {"source_manifest": str(manifest.relative_to(HERE.parents[2])),
                "source_manifest_sha256": sha256(manifest_bytes).hexdigest(),
                "algorithm_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "pair_budget_per_case": args.pair_budget}
    initial = initial_screen(archive, args.input_dir, args.pair_budget)
    INITIAL.write_text(json.dumps({**metadata, "controls": control, "stages": initial}, indent=2) + "\n")
    if args.initial_only:
        return

    requested = set(args.stage or ("start-03-age08",))
    stage_map = {f'{row["case"]}-age{row["age"]:02d}': row for row in archive["stages"]}
    assert requested <= stage_map.keys(), requested - stage_map.keys()
    rows = []
    for stage in sorted(requested):
        source = stage_map[stage]
        n, blocks = read_stage(args.input_dir, source)
        result = solve(n, blocks, args.pair_budget)
        assert result["isolated_junctions"] == source["isolated"]
        result.update({"case": source["case"], "age": source["age"], "role": source["role"],
                       "blocks_file": source["files"]["blocks"]})
        rows.append(result)
        print(result["case"], result["age"], n, len(blocks), result["components"],
              result["h1_lower"], result["h1_upper"], result["exact"], flush=True)

    OUTPUT.write_text(json.dumps({**metadata, "stages": rows}, indent=2) + "\n")


if __name__ == "__main__":
    main()
