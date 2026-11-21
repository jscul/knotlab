"""Use only the observed inherited pair table to exclude incorrect birth rosters."""
from collections import Counter
from itertools import combinations
from fractions import Fraction
from hashlib import sha256
from math import isqrt, lcm
from pathlib import Path
import json
import sys


def signed_rows(n, total, disagreements):
    table = [[total if a == b else None for b in range(n)] for a in range(n)]
    for (a, b), count in zip(combinations(range(n), 2), disagreements, strict=True):
        table[a][b] = table[b][a] = total - 2 * count
    return table


def equal_rows(table, a, b, names):
    return all(table[a][z] == table[b][z] for z in names if z not in (a, b))


def options(table):
    total = table[0][0]
    names = set(range(len(table)))
    eligible = set()
    for f, row in enumerate(table):
        m = min(row)
        near = {z for z in names - {f} if row[z] == m}
        if m >= 0 or len(near) < 2:
            continue
        if len(near) == 2:
            a, b = sorted(near)
            if -2 * m != total + table[a][b]:
                continue
        triples = (total + sum(table[a][b] for a, b in combinations(triple, 2))
                   for triple in combinations(near, 3))
        if len(near) == 3 and next(triples) != -4 * m:
            continue
        if len(near) > 3 and any(prob <= -4 * m for prob in triples):
            continue
        fresh = {f} | {z for z in near if equal_rows(table, f, z, names)}
        inputs = near - fresh
        if not inputs or len(fresh) < max(1, 3 - len(inputs)):
            continue
        if any(equal_rows(table, a, b, names) for a, b in combinations(inputs, 2)):
            continue
        if len(inputs) <= 2:
            scale = len(inputs) * (2 ** len(fresh) - 1)
            if any(scale * row[z] != -sum(table[i][z] for i in inputs) for z in names - fresh):
                continue
        eligible.add((tuple(sorted(fresh)), tuple(sorted(inputs))))
    return sorted(eligible)


def disjoint_packs(opts):
    def extend(start, picked, used):
        if picked:
            yield picked
        for j in range(start, len(opts)):
            f, i = opts[j]
            h = set(f) | set(i)
            if not used & h:
                yield from extend(j + 1, [*picked, j], used | h)
    yield from extend(0, [], set())


def partition_inputs(table, old, inputs):
    # Exchangeable previous loose names in different parents cannot have a negative mutual mean.
    return {a: tuple(sorted(b for b in inputs if (a == b or
            (table[a][b] < 0 and equal_rows(table, a, b, old))))) for a in inputs}


def groups(blocks, active):
    # Independent, literal enumeration of the ordinary proposal definition.
    neighbors = {frozenset(pair) for block in blocks for pair in combinations(block, 2)}
    complete = []
    for size in range(3, len(active) + 1):
        for candidate in combinations(active, size):
            if all(frozenset(pair) in neighbors for pair in combinations(candidate, 2)):
                complete.append(frozenset(candidate))
    unheld = [h for h in complete if not any(h < other for other in complete)
              and not any(h <= block for block in blocks)]
    return unheld + [pair for pair in neighbors if not any(pair <= h for h in unheld)]


def inspect_pack(table, opts, pack):
    names = set(range(len(table)))
    fresh = {x for j in pack for x in opts[j][0]}
    inputs = {x for j in pack for x in opts[j][1]}
    old = names - fresh
    partition = partition_inputs(table, old, inputs)
    if any(partition[a] != partition[b] for a in inputs for b in partition[a]):
        return "partition", None
    parents = sorted(set(partition.values()))
    blocks = []
    for h in parents:
        minima = {x: min(table[x][z] for z in old - {x}) for x in h}
        if any(table[x][y] != minima[x] for x in h for y in h if x != y):
            return "old_minimum", None
        companions = {z for z in old - inputs if all(table[x][z] == minima[x] for x in h)}
        if len(h) + len(companions) < 3:
            return "old_arity", None
        witness = set()
        for j in pack:
            count = len(set(h) & set(opts[j][1]))
            if count > 1:
                return "two_inputs_one_parent", None
            if count:
                witness.add(j)
        blocks.append(frozenset(witness))
    proposals = groups(blocks, pack)
    demand = Counter(j for group in proposals for j in group)
    if any(len(opts[j][0]) != max(1, 3 - len(opts[j][1]), demand[j]) for j in pack):
        return "price", None
    reps = [tuple(sorted(row)) for row in proposals]
    for j in pack:
        reps.extend([(j,)] * (len(opts[j][0]) - demand[j]))
    reps.sort()
    child_blocks = [frozenset(i for i, g in enumerate(reps) if j in g) for j in pack]
    child_demand = Counter(i for group in groups(child_blocks, list(range(len(reps)))) for i in group)
    grants = [max(1, 3 - len(g), child_demand[i]) for i, g in enumerate(reps)]
    return "survives", dict(pack=pack, old_loose_groups=parents, parents=reps, fresh_counts=grants)


def from_table(n, total, counts):
    table = signed_rows(n, total, counts)
    opts = options(table)
    stages, survivors = Counter(), []
    for pack in disjoint_packs(opts):
        reason, result = inspect_pack(table, opts, pack)
        stages[reason] += 1
        if result:
            survivors.append(result)
    return dict(options=opts, packs=sum(stages.values()), dispositions=dict(stages), survivors=survivors)


if __name__ == "__main__":
    input_path = (Path(sys.argv[1]) if len(sys.argv) > 1 else
                  next(Path(__file__).resolve().parents[2].glob(
                      "artifacts/NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A/*/target_inherited.json")))
    raw = input_path.read_bytes()
    pairs = [Fraction(value) for value in json.loads(raw)]
    n = (1 + isqrt(1 + 8 * len(pairs))) // 2
    assert n * (n - 1) == 2 * len(pairs)
    total = lcm(*(p.denominator for p in pairs))
    result = from_table(n, total, [int(total * p) for p in pairs])
    result["input_sha256"] = sha256(raw).hexdigest()
    print(json.dumps(result, indent=2))
