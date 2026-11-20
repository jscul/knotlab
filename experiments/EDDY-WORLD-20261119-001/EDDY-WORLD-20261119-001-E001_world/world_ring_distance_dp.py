"""Minimum bond meeting two mark sets, by connected-cut dynamic programming."""

from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from time import monotonic

from world_growth import STAGES, load_study


OUT = STAGES.with_name("ring_distance_dp.json")
WIDTH_LIMIT = 12
WORK_LIMIT = 20_000_000
BUCKET_LIMIT = 80_000
TABLE_LIMIT = 1_000_000
TIME_LIMIT = 60
QUERIES = {"all_exclusive": 9, "exclusive_shared": 18, "fixed_c1_c2": 36}


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def bitset(indices):
    return sum(1 << v for v in indices)


def mark_flags(original, roles):
    """Source exclusivity, regardless of who holds each distinction later."""
    owners = defaultdict(set)
    for v, row in enumerate(original):
        for d in row:
            owners[d].add(v)
    flags = {}
    marks = {}
    for i, (ring, ring_edges) in enumerate(zip(roles["rings"], roles["ring_edges"], strict=True)):
        exclusive_junctions = set(ring) - set(roles["seams"])
        exclusive = sorted(d for d, holders in owners.items() if holders <= exclusive_junctions)
        shared = sorted(set(exclusive) & set(ring_edges))
        fixed = ring_edges[1]
        assert owners[fixed] == set(ring[1:3]) and fixed in shared
        suffix = 3 * i
        marks[str(i)] = {"all_exclusive": exclusive, "exclusive_shared": shared, "fixed_c1_c2": fixed}
        for group, bit in ((exclusive, 1), (shared, 2), ([fixed], 4)):
            for d in group:
                flags[d] = flags.get(d, 0) | (bit << suffix)
    return flags, marks


def wired_edges(stars):
    owners = defaultdict(list)
    for v, row in enumerate(stars):
        for d in row:
            owners[d].append(v)
    assert set(owners) == set(range(len(owners)))
    outside = len(stars)
    edges = []
    for d in range(len(owners)):
        ends = owners[d]
        if len(ends) == 1:
            ends.append(outside)
        assert len(ends) == 2 and ends[0] != ends[1]
        edges.append(tuple(ends))
    return len(stars) + 1, edges


def bundles_of(n, edges, flags):
    adjacency = [0] * n
    bundles = defaultdict(dict)
    for d, (u, v) in enumerate(edges):
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
        cost, marks = bundles[u].get(v, (0, 0))
        value = cost + 1, marks | flags.get(d, 0)
        bundles[u][v] = bundles[v][u] = value
    return adjacency, bundles


def reached(first, domain, adjacency):
    visited = pending = first
    while pending:
        v = pending & -pending
        fresh = adjacency[v.bit_length() - 1] & domain & ~visited
        visited |= fresh
        pending = (pending ^ v) | fresh
    return visited


def ordering(graph, direction, ceiling, deadline):
    """Greedy min-fill elimination, with the exterior fixed at the end."""
    n = len(graph)
    mixed = list(graph)
    remaining = set(range(n - 1))
    separators = {}
    widest = 0
    while remaining:
        if monotonic() > deadline:
            raise Limit("time")

        def score(v):
            neighbors = mixed[v]
            missing = sum((neighbors & ~mixed[w]).bit_count() - 1 for w in bits(neighbors))
            return missing, neighbors.bit_count(), v * direction

        v = min(remaining, key=score)
        near = mixed[v]
        widest = max(widest, near.bit_count())
        if widest > ceiling:
            return widest, None
        separators[v] = tuple(bits(near))
        remaining.remove(v)
        for w in bits(near):
            mixed[w] = (mixed[w] | near) & ~((1 << w) | (1 << v))
    separators[n - 1] = ()
    return widest, separators


def decomposition(graph, deadline):
    options = [ordering(graph, direction, WIDTH_LIMIT, deadline) for direction in (1, -1)]
    possible = [x for x in options if x[1] is not None]
    if not possible:
        return min(x[0] for x in options), None
    width, separators = min(possible, key=lambda x: x[0])
    children = defaultdict(list)
    rank = {v: i for i, v in enumerate(separators)}
    for v in separators:
        if separators[v]:
            parent = min(separators[v], key=rank.__getitem__)
            assert set(separators[v]) <= {parent, *separators[parent]}
            children[parent].append(v)
    assert sum(map(len, children.values())) == len(graph) - 1
    return width, (separators, children)


class Limit(RuntimeError):
    pass


class Budget:
    def __init__(self, deadline):
        self.deadline = deadline
        self.steps = 0
        self.peak_retained = 0
        self.peak_bucket = 0
        self.rank_tests = 0

    def work(self, count):
        previous = self.steps
        self.steps += count
        if self.steps > WORK_LIMIT:
            raise Limit("work")
        if self.steps // 1024 != previous // 1024 and monotonic() > self.deadline:
            raise Limit("time")

    def check_time(self):
        if monotonic() > self.deadline:
            raise Limit("time")

    def states(self, retained, bucket):
        self.peak_retained = max(self.peak_retained, retained)
        self.peak_bucket = max(self.peak_bucket, bucket)
        if retained > TABLE_LIMIT or bucket > BUCKET_LIMIT:
            raise Limit("states")

    def result(self):
        return {"transitions": self.steps, "peak_retained_states": self.peak_retained,
                "peak_bucket_states": self.peak_bucket, "rank_tests": self.rank_tests}


def join_components(first, second):
    result = list(first)
    for component in second:
        if component.bit_count() <= 1:
            continue
        merged = [part for part in result if part & component]
        if len(merged) > 1:
            result = [part for part in result if not part & component]
            result.append(sum(merged))
    return tuple(sorted(result))


def record_best(table, key, cost, shore):
    old = table.get(key)
    if old is None or (cost, shore) < old:
        table[key] = cost, shore


def representative_rows(table, colors, full, budget):
    """Minimum-cost basis for connectivity compatibility, separately by flags."""
    if len(table) < 24:
        return table
    zeros = full ^ colors
    anchored = (zeros & -zeros) | (colors & -colors)
    vectors = {}
    bases = defaultdict(dict)
    kept = {}
    for key, value in sorted(table.items(), key=lambda item: item[1]):
        parts, sealed, marks = key
        if parts not in vectors:
            word = 1
            # Bit index is the set put opposite each color's canonical anchor.
            for component in parts:
                if not component & anchored:
                    word |= word << component
            vectors[parts] = word
        word = vectors[parts]
        basis = bases[sealed, marks]
        budget.rank_tests += 1
        while word:
            top = word.bit_length() - 1
            if top not in basis:
                basis[top] = word
                kept[key] = value
                break
            word ^= basis[top]
    return kept


def lift_masks(positions):
    mapping = [0]
    for pos in positions:
        mapping += [x | (1 << pos) for x in mapping]
    return mapping


def project_mask(parent_mask, positions):
    return sum(((parent_mask >> p) & 1) << i for i, p in enumerate(positions))


def bag_links(v, separator, bundles):
    return [(1 << (1 + i), *bundles[v][w]) for i, w in enumerate(separator) if w in bundles[v]]


def relaxed_costs(separators, children, bundles, outside, infinity, budget):
    """Exact inside/outside crossing costs when connectivity and marks are erased."""
    inside, outside_cost = {}, {}
    color_rows = {}
    for v, separator in separators.items():
        bag = (v, *separator)
        omega_bit = 1 << bag.index(outside) if outside in bag else 0
        positions = [[bag.index(w) for w in separators[u]] for u in children[v]]
        links = bag_links(v, separator, bundles)
        inside[v] = [infinity] * (1 << len(separator))
        color_rows[v] = []
        for colors in range(1 << len(bag)):
            if colors & omega_bit:
                continue
            peers = [project_mask(colors, row) for row in positions]
            own = sum(cost for bit, cost, _ in links if bool(colors & bit) != bool(colors & 1))
            total = own + sum(inside[u][c] for u, c in zip(children[v], peers, strict=True))
            assert total < infinity
            inside[v][colors >> 1] = min(inside[v][colors >> 1], total)
            color_rows[v].append((colors >> 1, peers, total))
        budget.check_time()
    outside_cost[outside] = [0]
    for v in reversed(separators):
        for u in children[v]:
            outside_cost[u] = [infinity] * (1 << len(separators[u]))
        for colors, peers, total in color_rows[v]:
            cost = outside_cost[v][colors] + total
            for u, c in zip(children[v], peers, strict=True):
                outside_cost[u][c] = min(outside_cost[u][c], cost - inside[u][c])
        budget.check_time()
    return inside, outside_cost


def node_table(v, separator, descendants, separators, tables, bundles, outside, budget, retained,
               ceiling, relaxed):
    bag = (v, *separator)
    full = (1 << len(bag)) - 1
    own_links = bag_links(v, separator, bundles)
    on_bag = []
    for child in descendants:
        positions = [bag.index(w) for w in separators[child]]
        lifted = lift_masks(positions)
        on_bag.append((positions, lifted, tables[child], child))
    omega_bit = 1 << bag.index(outside) if outside in bag else 0
    output = defaultdict(dict)
    made = 0
    for colors in range(1 << len(bag)):
        if colors & omega_bit:
            continue
        present = (1 if colors != full else 0) | (2 if colors else 0)
        local_color = bool(colors & 1)
        color_code = 2 if local_color else 1
        component = 1
        cost = marks = 0
        for bit, w_cost, w_marks in own_links:
            if bool(colors & bit) == local_color:
                component |= bit
            else:
                cost += w_cost
                marks |= w_marks
        partition = tuple(sorted([component, *(1 << i for i in bits(full ^ component))]))
        current = {(partition, 0, marks): (cost, (1 << v) if local_color else 0)}
        inside, outside_cost = relaxed
        future = outside_cost[v][colors >> 1] if outside_cost else 0
        child_rows = []
        for positions, lift, states, child in on_bag:
            child_colors = project_mask(colors, positions)
            lower = inside[child][child_colors] if inside else 0
            future += lower
            child_rows.append((states.get(child_colors, {}), lift, lower))
        if cost + future > ceiling:
            current = {}
        for children, lift, lower in sorted(child_rows, key=lambda pair: len(pair[0])):
            if not current:
                break
            if not children:
                current = {}
                break
            future -= lower
            joined = {}
            budget.work(len(current) * len(children))
            held = retained + made + len(current)
            merge_cap = min(BUCKET_LIMIT, TABLE_LIMIT - held)
            for (child_parts, sealed, hits), (extra_cost, child_shore) in children.items():
                budget.check_time()
                if sealed & present:
                    continue
                child_parts = tuple(lift[part] for part in child_parts)
                for (parts, done, read), (price, shore) in current.items():
                    if sealed & done or price + extra_cost + future > ceiling:
                        continue
                    combined = join_components(parts, child_parts)
                    record_best(joined, (combined, sealed | done, hits | read),
                                price + extra_cost, shore | child_shore)
                    if len(joined) > merge_cap:
                        budget.states(held + len(joined), len(joined))
            budget.states(held + len(joined), len(joined))
            current = representative_rows(joined, colors, full, budget)
            if not current:
                break
        target = output[colors >> 1]
        old_size = len(target)
        budget.work(len(current))
        for (parts, done, read), (price, shore) in current.items():
            if 1 in parts:
                if done & color_code or (colors >> 1 if local_color else (full ^ colors) >> 1):
                    continue
                done |= color_code
            projected = tuple(part >> 1 for part in parts if part >> 1)
            record_best(target, (projected, done, read), price, shore)
        made += len(target) - old_size
        budget.states(retained + made, len(target))
        if local_color or omega_bit == 1:
            representative = representative_rows(target, colors >> 1, full >> 1, budget)
            output[colors >> 1] = representative
            made += len(representative) - len(target)
    return output, made


def direct_read(shore, edges, flags):
    cut = [d for d, (u, v) in enumerate(edges) if ((shore >> u) ^ (shore >> v)) & 1]
    hit = 0
    for d in cut:
        hit |= flags.get(d, 0)
    return cut, hit


def solve(n, edges, flags, ceiling=None):
    deadline = monotonic() + TIME_LIMIT
    adjacency, bundles = bundles_of(n, edges, flags)
    full = (1 << n) - 1
    assert reached(1, full, adjacency) == full
    budget = Budget(deadline)
    width = None
    try:
        width, tree = decomposition(adjacency, deadline)
        if tree is None:
            return {"status": "width_limit", "tested_width_lower": width}
        separators, children = tree
        tables, sizes = {}, {}
        retained = 0
        outside = n - 1
        if ceiling is None:
            ceiling = len(edges)
            relaxed = None, None
        else:
            relaxed = relaxed_costs(separators, children, bundles, outside, len(edges) + 1, budget)
        for v, separator in separators.items():
            table, size = node_table(v, separator, children[v], separators, tables, bundles,
                                     outside, budget, retained, ceiling, relaxed)
            for child in children[v]:
                retained -= sizes.pop(child)
                del tables[child]
            tables[v], sizes[v] = table, size
            retained += size
        assert set(tables) == {outside}
        root = tables[outside][0]
        rows = {}
        for query, required in QUERIES.items():
            best = min((value for (p, done, m), value in root.items()
                        if not p and done == 3 and m & required == required), default=None)
            if best is None:
                rows[query] = {"bond_distance": "infinity"}
                continue
            cost, shore = best
            assert 0 < shore < 1 << outside
            other = full ^ shore
            assert reached(shore & -shore, shore, adjacency) == shore
            assert reached(1 << outside, other, adjacency) == other
            cut, hits = direct_read(shore, edges, flags)
            assert cost == len(cut) and hits & required == required
            rows[query] = {"bond_distance": cost - 1, "bond": cut, "shore": list(bits(shore))}
        return {"status": "exact", "width": width, "readings": rows, **budget.result()}
    except Limit as exc:
        return {"status": str(exc) + "_limit", "width": width, **budget.result()}


def brute_read(n, edges, flags, *, all_loose_at_source=False):
    adjacency, _ = bundles_of(n, edges, flags)
    outside = 1 << (n - 1)
    ordinary = outside - 1
    minima = {k: float("inf") for k in QUERIES}
    if all_loose_at_source:
        assert adjacency[-1] == ordinary
        seen = set(1 << v for v in range(n - 1))
        todo = list(seen)
        for shore in todo:
            reachable = 0
            for v in bits(shore):
                reachable |= adjacency[v]
            for v in bits(reachable & ordinary & ~shore):
                enlarged = shore | (1 << v)
                if enlarged not in seen:
                    seen.add(enlarged)
                    todo.append(enlarged)
        subsets = todo
    else:
        subsets = range(1, outside)
    connected = 0
    for shore in subsets:
        other = (ordinary | outside) ^ shore
        if not all_loose_at_source and (reached(shore & -shore, shore, adjacency) != shore
                                        or reached(outside, other, adjacency) != other):
            continue
        connected += 1
        cut, hit = direct_read(shore, edges, flags)
        for label, required in QUERIES.items():
            if hit & required == required:
                minima[label] = min(minima[label], len(cut) - 1)
    return {k: v if isinstance(v, int) else "infinity" for k, v in minima.items()}, connected


def values(row):
    assert row["status"] == "exact", row
    return {q: r["bond_distance"] for q, r in row["readings"].items()}


def controls():
    star = [(0, 2), (1, 2)]
    two_marks = {0: 7, 1: 56}
    rejected = values(solve(3, star, two_marks))
    assert set(rejected.values()) == {"infinity"}
    parallel = [(0, 1), (0, 1), (0, 1)]
    assert set(values(solve(2, parallel, two_marks)).values()) == {2}
    rng = Random(20261119)
    for i in range(48):
        n = 4 + i % 5
        edges = [(v, rng.randrange(v)) for v in range(1, n)]
        edges += [tuple(rng.sample(range(n), 2)) for _ in range(i % 12)]
        fl = {d: rng.choice((0, 1, 3, 7, 8, 24, 56)) for d in range(len(edges))}
        truth = brute_read(n, edges, fl)[0]
        assert values(solve(n, edges, fl)) == truth
        ceiling = max((dist + 1 for dist in truth.values() if isinstance(dist, int)), default=0)
        assert values(solve(n, edges, fl, ceiling)) == truth
    return {"small_exhaustive_multigraphs": 48, "disconnected_shore_control": rejected,
            "three_parallel_distinctions_distance": 2, "checked_with_and_without_cost_pruning": True}


def run(stage_file, age_limit):
    study = load_study(path=stage_file)
    result = {"stage_sha256": sha256(stage_file.read_bytes()).hexdigest(),
              "caps": {"width": WIDTH_LIMIT, "work": WORK_LIMIT, "bucket": BUCKET_LIMIT,
                       "states": TABLE_LIMIT, "seconds": TIME_LIMIT},
              "controls": controls(), "cases": {}}
    for case in ("T4", "T8"):
        raw = study["cases"][case]
        flags, marks = mark_flags(raw["stages"]["0"]["stars"], raw["input"]["roles"])
        stages = {}
        prior_witnesses = None
        for a, snapshot in raw["stages"].items():
            if int(a) > age_limit:
                break
            n, edges = wired_edges(snapshot["stars"])
            incumbent = None
            if prior_witnesses:
                adjacency, _ = bundles_of(n, edges, flags)
                incumbent = {}
                for query, witness in prior_witnesses.items():
                    shore = bitset(witness["shore"])
                    other = ((1 << n) - 1) ^ shore
                    assert reached(shore & -shore, shore, adjacency) == shore
                    assert reached(1 << (n - 1), other, adjacency) == other
                    cut, hit = direct_read(shore, edges, flags)
                    assert hit & QUERIES[query] == QUERIES[query]
                    assert cut == witness["bond"]
                    incumbent[query] = len(cut) - 1
            answer = solve(n, edges, flags, max(incumbent.values()) + 1 if incumbent else None)
            if incumbent:
                answer["previous_witness_upper"] = incumbent
                if answer["status"] == "exact":
                    assert all(values(answer)[q] <= upper for q, upper in incumbent.items())
            if a == "0":
                direct, connected = brute_read(n, edges, flags, all_loose_at_source=True)
                assert values(answer) == direct
                answer["independent_source_shores"] = connected
            stages[a] = {"wired_vertices": n, "literal_distinctions": len(edges), **answer}
            if answer["status"] != "exact":
                break
            prior_witnesses = answer["readings"]
        result["cases"][case] = {"marks": marks, "ages": stages}
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--stages", type=Path, default=STAGES)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--age-limit", type=int, default=5)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if args.controls_only:
        print(json.dumps(controls(), indent=2))
        return
    result = run(args.stages, args.age_limit)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
