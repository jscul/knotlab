"""Reconstruct the registered draws in their original sequence."""

from collections import Counter
from dataclasses import dataclass
import gzip
import heapq
import json
import math
from pathlib import Path
import random

from growth import Roster, joins


HOME = Path(__file__).resolve().parents[1]
PREVIOUS = HOME.parent / "LATE-VIEWS-20261126-001"
HORIZONS = {"tree40": 8, "treeplus25": 7, "census6": 10}
SEEDS = {"tree40": 20261201, "treeplus25": 20261202, "census6": 20261203}


def census_indices(rng, count):
    population = range(82_656)
    used = set(random.Random(20261126).sample(population, 1000))
    unused = [i for i in population if i not in used]
    used.update(random.Random(20261127).sample(unused, 2000))
    unused = [i for i in population if i not in used]
    pool = random.Random(20261128).sample(unused, 2000)
    return rng.sample(pool, count)


def census_archive(law):
    with gzip.open(PREVIOUS / f"held_out_{law}.jsonl.gz", "rt") as stream:
        return {r["index"]: r for r in map(json.loads, stream)}


def tree_roster(n, plus, rng):
    # Uniform labelled trees via the literature's Prüfer sequence.
    code = [rng.randrange(n) for _ in range(n - 2)]
    counts = Counter(code)
    leaves = [k for k in range(n) if not counts[k]]
    heapq.heapify(leaves)
    shared = []
    for k in code:
        small = heapq.heappop(leaves)
        shared.append(tuple(sorted((small, k))))
        counts[k] -= 1
        if counts[k] == 0:
            heapq.heappush(leaves, k)
    shared.append(tuple(sorted(leaves)))
    if plus:
        have = set(shared)
        possible = [(a, b) for a in range(n) for b in range(a + 1, n) if (a, b) not in have]
        product = rng.random()
        extra = 0
        while product > math.exp(-1):
            product *= rng.random()
            extra += 1
        shared.extend(rng.sample(possible, min(len(possible), extra)))
    # Bare sizes in the weighting use first-round demand with every knot live.
    neighbours = [set() for _ in range(n)]
    for a, b in shared:
        neighbours[a].add(b)
        neighbours[b].add(a)
    all_demand = Counter(k for g in joins(range(n), neighbours) for k in g)
    sizes = [max(3, len(near) + all_demand[k]) for k, near in enumerate(neighbours)]
    return Roster.from_graph(sizes, shared)


@dataclass
class Case:
    population: str
    index: int
    roster: Roster
    reader: int
    steps: dict
    h2: list
    admissions: list
    record: dict

    def within(self, n):
        return frozenset(k for k, s in self.steps.items() if s <= n)


def cases(population):
    rng = random.Random(SEEDS[population])
    lines = (HOME / f"results_{population}.jsonl").read_text().splitlines()
    records = [json.loads(line) for line in lines]
    if population == "census6":
        saved = census_archive("nae")
        ids = census_indices(rng, len(records))
        rosters = (Roster.from_holdings(saved[i]["stars"]) for i in ids)
    else:
        ids = range(len(records))
        rosters = (tree_roster(40 if population == "tree40" else 25,
                               population == "treeplus25", rng) for _ in ids)
    for roster, record, index in zip(rosters, records, ids, strict=True):
        if index != record["index"]:
            raise AssertionError("reconstructed draw order")
        live = sorted(roster.loose)
        reader = rng.choice(live)
        if reader != record["reader"]:
            raise AssertionError("reconstructed reader")
        steps = roster.steps_from(reader)
        rounds = [rng.randint(1, HORIZONS[population]) for _ in range(3)]
        rosters_at = [frozenset(k for k, s in steps.items() if s <= t + 1) for t in rounds]
        h2 = []
        for t, reached in zip(rounds, rosters_at):
            extras = {k for k in live if k not in reached and rng.random() < .5}
            h2.append((t, reached | extras))
        rest = sorted(set(live) - rosters_at[0])
        rng.shuffle(rest)
        admissions = [(rounds[0], region) for region in
                      (rosters_at[0], rosters_at[0] | set(rest[:len(rest) // 2]), frozenset(live))]
        yield Case(population, index, roster, reader, steps, h2, admissions, record)
