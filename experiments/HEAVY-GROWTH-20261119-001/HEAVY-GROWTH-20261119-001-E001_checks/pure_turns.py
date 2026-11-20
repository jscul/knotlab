"""Screen exactly allowed turns of residual pairs; replay the small start-13 proof."""

import argparse
import gzip
import hashlib
import json
import sys
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = "HUB-GUIDED-SAMPLE-20261119-001"
HUB = ROOT / "experiments" / PRIOR / f"{PRIOR}-E001_sampler"
ART = ROOT / "artifacts" / PRIOR / HUB.name
sys.path.insert(0, str(HUB))
import stages as archive
from group_profile import members

FRONTIERS = [14, 10, 9, 8, 8, 9, 7, 7, 9, 6, 7, 7, 7, 7, 8, 8]
LOOPS = [(85, 105, 178, 824, 85, 105), (85, 105, 179, 824, 85, 105)]


def signatures(blocks, size):
    """Block membership at each physical site."""
    masks = [0] * size
    for i, block in enumerate(blocks):
        flag = 1 << i
        for v in block:
            masks[v] |= flag
    return masks


def automaton(sig, pairs):
    incident = defaultdict(list)
    for a, b in pairs:
        assert a < b and sig[a] & sig[b]
        incident[a].append(b)
        incident[b].append(a)
    graph = nx.DiGraph()
    for b, around in incident.items():
        common = sig[around[0]]
        for a in around[1:]:
            common &= sig[a]
        if common:
            continue
        for a, c in combinations(around, 2):
            if not sig[a] & sig[c]:
                graph.add_edge((a, b), (b, c))
                graph.add_edge((c, b), (b, a))
    return graph


def turn_summary(sig, pairs):
    digraph = automaton(sig, pairs)
    cyclic = [group for group in nx.strongly_connected_components(digraph) if len(group) > 1]
    sizes = sorted((len(group), digraph.subgraph(group).number_of_edges()) for group in cyclic)
    longest = None if cyclic else (len(nx.dag_longest_path(digraph)) if digraph else int(bool(pairs)))
    return dict(residual_pairs=len(pairs), all_oriented_states=2 * len(pairs),
                states_on_some_transition=len(digraph), directed_turns=digraph.number_of_edges(),
                recurrent_components_states_and_internal_arcs=sizes, longest_finite_walk_in_old_pairs=longest)


def exact_small_groups(size, blocks):
    graph = nx.Graph()
    graph.add_nodes_from(range(size))
    for block in blocks:
        graph.add_edges_from(combinations(block, 2))
    held = [frozenset(block) for block in blocks]
    large = [frozenset(f) for f in nx.find_cliques(graph) if len(f) >= 3 and not any(set(f) <= h for h in held)]
    residual = {tuple(sorted(pair)) for pair in graph.edges()
                if all(not set(pair) <= h for h in large)}
    return large + [frozenset(p) for p in sorted(residual)], residual


def controls():
    examples = {
        "square_with_universal_cone_and_all_faces_held": (5, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]),
        "partnered_order_three_on_pair_blocks": (6, [p for p in combinations(range(6), 2) if p[0] // 2 != p[1] // 2]),
        "single_held_block": (5, [tuple(range(5))]),
        "path": (5, [(0, 1), (1, 2), (2, 3), (3, 4)]),
    }
    rows = {}
    for name, (n, blocks) in examples.items():
        children, pairs = exact_small_groups(n, blocks)
        graph = automaton(signatures(blocks, n), pairs)
        child_blocks = [[i for i, p in enumerate(children) if x in p] for x in range(n)]
        _, new_pairs = exact_small_groups(len(children), child_blocks)
        new_graph = automaton(signatures(child_blocks, len(children)), new_pairs)
        pair_index = {tuple(sorted(p)): i for i, p in enumerate(children) if len(p) == 2}
        def lift(state):
            return pair_index[tuple(sorted(state))]
        expected_nodes = {(lift(a), lift(b)) for a, b in graph.edges()}
        actual_nodes = {(a, b) for a, b in new_pairs if len(children[a]) == len(children[b]) == 2}
        actual_nodes |= {(b, a) for a, b in actual_nodes}
        assert actual_nodes == expected_nodes
        expected_arcs = {((lift(a), lift(b)), (lift(b), lift(c)))
                         for a, b in graph.edges() for c in graph.successors(b)}
        actual_arcs = {(x, y) for x, y in new_graph.edges() if x in actual_nodes and y in actual_nodes}
        assert actual_arcs == expected_arcs
        rows[name] = dict(live=n, all_groups=len(children), old_turns=graph.number_of_edges(),
                          new_all_binary_turns=len(actual_arcs),
                          recurrent=not nx.is_directed_acyclic_graph(graph))
    return rows


def witness():
    captured = {}
    archive.archive_replay("start-13", [6], lambda _, frame: captured.update(frame=frame))
    frame = captured["frame"]
    sig = signatures(frame.blocks, frame.size)
    single_parent_count = sum(mask.bit_count() == 1 for mask in frame.parent_masks)
    assert single_parent_count == 0
    names = sorted(set(v for loop in LOOPS for v in loop))
    raw = (f"{frame.size} {len(frame.blocks)}\n"
           + "".join(" ".join(map(str, block)) + "\n" for block in frame.blocks)).encode("ascii")
    named_pairs = sorted({tuple(sorted((a, b))) for loop in LOOPS for a, b in zip(loop, loop[1:])})
    secured = []
    for a, b in named_pairs:
        together = sig[a] & sig[b]
        containing = [i for i in members(together)]
        assert len(containing) == 1
        joint = [v for v, mask in enumerate(sig) if mask & sig[a] and mask & sig[b]]
        holder, = containing
        assert set(joint) == set(frame.blocks[holder])
        secured.append(dict(pair=[a, b], common_block=holder, size_of_joint_neighborhood=len(joint)))
    admissible = automaton(sig, named_pairs)
    for loop in LOOPS:
        states = list(zip(loop, loop[1:]))
        assert states[-1] == states[0] == (85, 105)
        assert all(admissible.has_edge(x, y) for x, y in zip(states, states[1:]))
        assert (105, 85) not in states
    codes = {}
    for k in range(1, 7):
        words = set()
        for code in product(range(2), repeat=k):
            word = (85, 105)
            for symbol in code:
                word += LOOPS[symbol][2:]
            words.add(min(word, word[::-1]))
        assert len(words) == 2 ** k
        codes[k] = len(words)
    return dict(start="start-13", age=6, live=frame.size, maximal_blocks=len(frame.blocks),
                canonical_stage_sha256=hashlib.sha256(raw).hexdigest(), single_parent_sites=single_parent_count,
                literal_complete_returns=LOOPS, sites_with_parent_counts=[
                    [v, frame.parent_masks[v].bit_count()] for v in names],
                all_used_pairs=secured, unoriented_codes_small_check=codes, toy_controls=controls())


def latest_partial_14(folder, meta, small_limit=300):
    name = "start-14"
    previous = load_blocks(folder, meta[name, 7])
    parents = load_parents(folder, meta[name, 8])
    n, old_blocks = previous
    digits = [bytearray((len(parents) + 7) // 8) for _ in range(n)]
    for j, row in enumerate(parents):
        for a in row:
            digits[a][j // 8] |= 1 << (j % 8)
    blocks = [int.from_bytes(row, "little") for row in digits]
    del digits
    parent_masks = [sum(1 << x for x in row) for row in parents]
    old_sig = signatures(old_blocks, n)
    old_hood = [sum(1 << j for j, sj in enumerate(old_sig) if si & sj) | (1 << v)
                for v, si in enumerate(old_sig)]
    pairs = set()
    for j, row in enumerate(parents):
        if len(row) != 2:
            continue
        a, b = row
        for c, x in ((a, b), (b, a)):
            forbidden = old_hood[x] & ~(1 << c)
            for t in members(blocks[c]):
                if not parent_masks[t] & forbidden:
                    pairs.add(tuple(sorted((j, t))))
    binary = len(pairs)
    @lru_cache(maxsize=8192)
    def closed(j):
        hood = 0
        for c in parents[j]:
            hood |= blocks[c]
        return hood
    inspected, eligible = 0, 0
    for block in blocks:
        size = block.bit_count()
        if not 2 <= size <= small_limit:
            continue
        eligible += 1
        sites = list(members(block))
        outside = [closed(x) & ~block for x in sites]
        for i, a in enumerate(sites):
            for j in range(i):
                if not outside[i] & outside[j]:
                    pairs.add((sites[j], a))
        inspected += size * (size - 1) // 2
    result = turn_summary(parent_masks, pairs)
    # Close any walk in the known subgraph by ONE extra residual pair. A path
    # of three or more edges is needed for the strict noncandidate corner tests.
    digraph = automaton(parent_masks, pairs)
    assert nx.is_directed_acyclic_graph(digraph)
    queries = set()
    def visit(first, path):
        a, b = first
        c, d = path[-1]
        if (len(path) >= 3 and a != d and parent_masks[a] & parent_masks[d]
                and not parent_masks[a] & parent_masks[c] and not parent_masks[b] & parent_masks[d]):
            queries.add(tuple(sorted((a, d))))
        for successor in digraph.successors(path[-1]):
            visit(first, path + [successor])
    for state in digraph:
        visit(state, [state])
    counterexamples = []
    for a, b in sorted(queries):
        common_parents = parent_masks[a] & parent_masks[b]
        all_holding = 0
        for x in members(common_parents):
            all_holding |= blocks[x]
        outsider = closed(a) & closed(b) & ~all_holding
        assert outsider
        counterexamples.append([a, b, (outsider & -outsider).bit_length() - 1])
    result.update(age=8, live=len(parents), complete=False, method="binary-parent endpoints or small common block",
                  binary_endpoint_pairs_exact=binary, binary_parent_sites=sum(len(row) == 2 for row in parents),
                  small_block_size_cap=small_limit, nontrivial_raw_blocks_in_range=eligible,
                  raw_within_block_pair_tests=inspected,
                  possible_single_closing_pair_and_actual_unheld_triangle=counterexamples)
    return result


def file_for(folder, meta, kind):
    info = meta["files"][kind]
    path = folder / info["name"]
    assert archive.digest(path) == info["sha256"], path
    return path


def load_blocks(folder, meta):
    with file_for(folder, meta, "blocks").open() as stream:
        n, nb = map(int, next(stream).split())
        blocks = [list(map(int, line.split())) for line in stream]
    assert len(blocks) == nb
    return n, blocks


def load_parents(folder, meta):
    with gzip.open(file_for(folder, meta, "parents"), "rt") as stream:
        return json.load(stream)


def small_and_exported(name, last, folder, meta):
    ages = [t for tag, t in meta if tag == name and "parents" in meta[tag, t]["files"]]
    stop = min([last] + ages)
    previous = None
    output = []
    def record(age, n, blocks, edges):
        row = turn_summary(signatures(blocks, n), edges)
        row.update(age=age, live=n, complete=True, method="all two-parent births in next recorded round")
        output.append(row)
    def step(age, frame):
        nonlocal previous
        if age:
            edges = [tuple(members(mask)) for mask in frame.parent_masks if mask.bit_count() == 2]
            record(age-1, previous.size, previous.blocks, edges)
        previous = frame
    archive.archive_replay(name, range(stop + 1), step)
    for t in range(stop, last):
        n, blocks = load_blocks(folder, meta[name, t])
        rows = load_parents(folder, meta[name, t + 1])
        record(t, n, blocks, [tuple(row) for row in rows if len(row) == 2])
    return output


def screen(folder):
    data = json.loads((ART / "stages.json").read_text())
    meta = {(item["case"], item["age"]): item for item in data["stages"]}
    apps = {row["case"]: row for row in json.loads((ART / "applications.json").read_text())}
    output = {}
    for index, last in enumerate(FRONTIERS):
        name = f"start-{index:02d}"
        rows = small_and_exported(name, last, folder, meta)
        if index in (0, 4):
            tail = dict(first_layer=last, held_full_block_size=9 if index == 0 else 781,
                        last_birth=22 if index == 0 else 788,
                        criterion="all later turns absent by explicit subset layers")
        elif index == 14:
            rows.append(latest_partial_14(folder, meta))
            tail = None
        else:
            n, blocks = load_blocks(folder, meta[name, last])
            if index in (3, 6, 7, 12, 13, 15):
                path = ART / f"literal_residual{index:02d}.json"
                pairs = json.loads(path.read_text())["residual_pairs"]
            elif index in (9, 10):
                path = ART / f"cover_pairs{index:02d}.json"
                pairs = json.loads(path.read_text())["pairs"]
            else:
                path = ART / "applications.json"
                assert apps[name]["exact_residual"] == 0
                pairs = []
            row = turn_summary(signatures(blocks, n), [tuple(pair) for pair in pairs])
            row.update(age=last, live=n, complete=True, method="previous exhaustive residual result",
                       residual_source=path.name)
            if index in (6, 7, 12, 15):
                deg_path = file_for(folder, meta[name, last], "degrees")
                with gzip.open(deg_path, "rt") as stream:
                    degrees = json.load(stream)
                assert len(degrees) == n
                universal = [v for v, degree in enumerate(degrees) if degree == n - 1]
                row["universal_sites"] = universal
                row["common_to_all_next_children"] = [v for v in universal if all(v in e for e in pairs)]
            rows.append(row)
            tail = None
        output[name] = dict(canonical_source=index not in (8, 15), rows=rows, finite_tail=tail)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen", action="store_true", help="screen the sixteen fixed archived histories")
    parser.add_argument("--exports", type=Path, default=Path("/var/tmp/hub-sample-20261119"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = screen(args.exports) if args.screen else witness()
    raw_json = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.write_text(raw_json)
    else:
        print(raw_json, end="")
