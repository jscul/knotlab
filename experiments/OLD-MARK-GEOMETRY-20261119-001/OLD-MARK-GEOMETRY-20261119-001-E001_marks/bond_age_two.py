"""Literal J1 age-two all-pair distances by shared separator subproblems."""

from argparse import ArgumentParser
from collections import OrderedDict
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

from bond_distances import OUTPUT, Wiring, pair_groups
from bond_later import initial_rows
import sources
import world_ring_distance_dp as partitions


STAGE_SECONDS = 110
QUERY_TRANSITIONS = 2_000_000
CACHE_STATES = 225_000


class PairPartitions:
    def __init__(self, wire, ceiling, wall_deadline):
        self.wire = wire
        self.ceiling = ceiling
        self.deadline = wall_deadline
        self.graph, self.bundles = partitions.bundles_of(wire.total, list(wire.edge.values()), {})
        self.width, tree = partitions.decomposition(self.graph, wall_deadline)
        if tree is None:
            raise partitions.Limit(f"width {self.width}")
        self.separators, self.children = tree
        self.order = {v: rank for rank, v in enumerate(self.separators)}
        self.owner = {d: min(ends, key=self.order.__getitem__) for d, ends in wire.edge.items()}
        self.subtree = {}
        for v in self.order:
            descendant_mask = 1 << v
            for child in self.children[v]:
                descendant_mask |= self.subtree[child]
            self.subtree[v] = descendant_mask
        any_budget = partitions.Budget(wall_deadline)
        self.relaxed = partitions.relaxed_costs(self.separators, self.children, self.bundles,
                                               wire.exterior, len(wire.edge) + 1, any_budget)
        self.cache = OrderedDict()
        self.retained = self.peak_cached = 0

    def read_table(self, v, marks, budget):
        if (key := (v, marks)) in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        if monotonic() >= self.deadline:
            raise partitions.Limit("stage seconds")
        tables, active = {}, 0
        for child in self.children[v]:
            sub = tuple(d for d in marks if self.subtree[child] & (1 << self.owner[d]))
            table, rows = self.read_table(child, sub, budget)
            tables[child] = table
            active += rows
        local = tuple(d for d in marks if self.owner[d] == v)
        if local:
            weights = dict(self.bundles)
            weights[v] = dict(weights[v])
            for i, d in enumerate(local):
                a, b = self.wire.edge[d]
                peer = a if b == v else b
                cost, status = weights[v][peer]
                weights[v][peer] = cost, status | 1 << i
        else:
            weights = self.bundles
        raw, count = partitions.node_table(v, self.separators[v], self.children[v], self.separators,
                                           tables, weights, self.wire.exterior, budget, active,
                                           self.ceiling, self.relaxed)
        if local:
            needed = (1 << len(local)) - 1
            raw = {colors: {(shape, sealed, 0): item
                            for (shape, sealed, hits), item in choices.items() if hits == needed}
                   for colors, choices in raw.items()}
            count = sum(map(len, raw.values()))
        while self.cache and self.retained + count > CACHE_STATES:
            _, (_, size) = self.cache.popitem(last=False)
            self.retained -= size
        if count <= CACHE_STATES:
            self.cache[key] = raw, count
            self.retained += count
            self.peak_cached = max(self.retained, self.peak_cached)
        return raw, count

    def solve(self, pair):
        budget = partitions.Budget(self.deadline)
        table, _ = self.read_table(self.wire.exterior, pair, budget)
        cost, mask = table[0][((), 3, 0)]
        return cost - 1, self.wire.witness(mask, pair, cost), budget.steps


def solve_frame(wire, queries, old, target, seconds):
    partitions.WORK_LIMIT = QUERY_TRANSITIONS
    deadline = monotonic() + seconds
    ceiling = 0
    for pair in queries:
        cert = wire.witness(old[pair], pair)
        ceiling = max(ceiling, len(cert["distinctions"]))
    try:
        solver = PairPartitions(wire, ceiling, deadline)
    except partitions.Limit as error:
        return {"knots": wire.n, "distinctions": len(wire.edge), "tested_width": None,
                "exact_pairs": 0, "peak_cached_states": 0, "pairs": [],
                "caps": [[*p, str(error)] for p in queries], "witnesses": []}
    cases, caps, witnesses = [], [], {}
    for pair in queries:
        try:
            value, certificate, transitions = solver.solve(pair)
        except partitions.Limit as error:
            caps.append([*pair, str(error)])
            continue
        side = tuple(certificate["knots"])
        if side not in witnesses:
            witnesses[side] = len(witnesses), certificate
        if target is not None:
            assert value == target[pair]
        cases.append([*pair, value, witnesses[side][0], transitions])
    return {"knots": wire.n, "distinctions": len(wire.edge), "tested_width": solver.width,
            "exact_pairs": len(cases), "peak_cached_states": solver.peak_cached,
            "pairs": cases, "caps": caps, "witnesses": [item[1] for item in witnesses.values()]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--first", type=Path, default=OUTPUT / "bond_first.json")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--later-endpoints", action="store_true",
                        help="try only the oldest endpoints at ages three and four")
    args = parser.parse_args()
    raw = args.first.read_bytes()
    first = json.loads(raw)["cases"]["J1"]
    spec = sources.cases()["J1"]
    queries = sorted(pair for rows in pair_groups(spec).values() for pair in rows)
    ages = (1, 2)
    seconds = STAGE_SECONDS
    destination = "bond_age_two_partitions.json"
    if args.later_endpoints:
        path = spec["roles"]["anchors"]
        queries = [tuple(sorted((path[0], path[-1])))]
        ages = (3, 4)
        seconds = 35
        partitions.WIDTH_LIMIT = 14
        destination = "bond_later_endpoints.json"
    result = {}
    for code, occupied in sources.loads(spec).items():
        arm = first["age_one_by_activity"][first["assignments"][code]["activity_id"]]
        target = {(a, b): value for a, b, value, _ in arm["pairs"]}
        seeds = initial_rows(first, occupied)
        result[code] = {}
        for age, frame in sources.generate(spec, occupied, max(ages)):
            if age not in ages:
                continue
            checked = target if age == 1 else None
            reading = solve_frame(Wiring(frame["stars"]), queries, seeds, checked, seconds)
            result[code][str(age)] = reading
            print(code, age, reading["exact_pairs"], "width", reading["tested_width"],
                  "total transitions", sum(row[-1] for row in reading["pairs"]), flush=True)
    output = args.out or OUTPUT / destination
    output.write_text(json.dumps({"schema": 1, "unit": "bond size minus one",
                                    "first_sha256": sha256(raw).hexdigest(),
                                    "limits": {"wall_seconds_per_frame": seconds,
                                               "transitions_per_query": QUERY_TRANSITIONS,
                                               "cache_states": CACHE_STATES},
                                    "pair_columns": ["first", "second", "bond_distance",
                                                     "witness_index", "transitions"],
                                    "cases": result}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
