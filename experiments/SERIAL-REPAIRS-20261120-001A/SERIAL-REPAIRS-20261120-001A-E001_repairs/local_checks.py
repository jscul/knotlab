"""Check the spent-witness and boundary rules on anonymous physical partial stages."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "local_checks.json"
ORIGINAL = ("U", "V", "S", "W", "A", "B", "Z")
MEETINGS = (("U", "S"), ("V", "S"), ("W", "S"), ("S", "A"), ("A", "B"), ("B", "W"), ("A", "Z"))
WIDTH = 7
CROSSED_WIDTH = 3


class Template:
    """Evaluator only: names and indices define the expected laws, never the reader."""

    def __init__(self, shifted):
        self.shifted = shifted
        self.parents = {}
        self.fresh = {}
        self.depth = dict.fromkeys(ORIGINAL, 0)
        self.position = {}
        self.grid = {}
        self.finite = {}
        self.top, self.relay = "finite top", "relay base"
        if shifted:
            roots = {1: "U", 2: "V", 4: "W"}
            for mask in (3, 5, 6, 7):
                child = self.top if mask == 7 else str(mask) + " finite"
                self.finite[mask] = child
                roots[mask] = child
                self.add(child, (roots[mask ^ (1 << i)] for i in range(3) if mask & (1 << i)), 1)
            self.add(self.relay, (self.top,), 2)
            self.make_grid("direct", {(0, 0): "Z"})
        else:
            roots = {0: "Z"}
            for mask in range(1, 16):
                child = self.top if mask == 15 else str(mask) + " finite"
                self.finite[mask] = child
                roots[mask] = child
                self.add(child, (roots[mask ^ (1 << i)] for i in range(4) if mask & (1 << i)), max(1, 4 - mask.bit_count()))
            self.add(self.relay, (self.top,), 2)
            self.make_grid("direct", {(1, 0): "U", (0, 1): "V"})
        self.make_grid("relayed", {(0, 0): self.relay})

        support = {h: [] for h in (*ORIGINAL, *self.parents)}
        for bit, (a, b) in enumerate(MEETINGS):
            for h in (a, b):
                support[h].extend(range(9 * bit, 9 * (bit + 1)))
        distinction = 9 * len(MEETINGS)
        for child, parents in self.parents.items():
            for parent in parents:
                support[parent].append(distinction)
                support[child].append(distinction)
                distinction += 1
        source_counts = {"U": 2, "V": 2, "S": 0, "W": 2 if shifted else 0, "A": 0, "B": 0, "Z": 2 if shifted else 4}
        for h, n in source_counts.items():
            assert sum(h in ps for ps in self.parents.values()) == n
        for h, n in self.fresh.items():
            # Position WIDTH is outside the tested window. Its predecessor
            # still retains the actual output leading to it.
            if h not in self.position or max(self.position[h][1:]) < WIDTH:
                assert len(support[h]) == len(self.parents[h]) + n
        self.maximum_name = distinction
        self.support = {k: tuple(row) for k, row in support.items()}

    def add(self, key, parents, fresh):
        parents = tuple(parents)
        self.parents[key] = parents
        self.fresh[key] = fresh
        self.depth[key] = max(self.depth[p] for p in parents) + 1

    def make_grid(self, name, bases):
        missing_origin = (0, 0) not in bases
        self.grid[name] = grid = {}
        for i, j in sorted(product(range(WIDTH + 1), repeat=2), key=lambda p: (sum(p), p)):
            if missing_origin and (i, j) == (0, 0):
                continue
            key = bases.get((i, j), f"{name} {i}:{j}")
            grid[i, j] = key
            self.position[key] = (name, i, j)
            if (i, j) not in bases:
                self.add(key, (grid[p] for p in ((i - 1, j), (i, j - 1)) if p in grid), 2)

    def place_set(self, branch, ideal):
        return {self.grid[branch][p] for p in ideal if p in self.grid[branch]}

    def expected(self, built, number):
        return Counter((tuple(sorted(number[p] for p in ps)), self.fresh[child])
                       for child, ps in self.parents.items() if child not in built and all(p in built for p in ps))


def ideals(width):
    """All downsets in the square, including the empty one."""
    def extend(heights, bound):
        if len(heights) == width:
            yield frozenset((i, j) for i, h in enumerate(heights) for j in range(h))
            return
        for h in range(bound + 1):
            yield from extend((*heights, h), h)
    yield from extend((), width)


def finite_ideals(plan):
    masks = tuple(plan.finite)
    for selected in range(1 << len(masks)):
        used = {m for i, m in enumerate(masks) if selected & (1 << i)}
        if all(all(y in used for y in masks if x & y == y) for x in used):
            yield {plan.finite[m] for m in used}


class Physical:
    def __init__(self, supports):
        self.arity = tuple(map(len, supports))
        held = defaultdict(list)
        for j, row in enumerate(supports):
            for distinction in row:
                held[distinction].append(j)
        self.neighbours = [set() for _ in supports]
        self.loose = [0] * len(supports)
        shares = Counter()
        for owners in held.values():
            if len(owners) == 1:
                self.loose[owners[0]] += 1
            else:
                a, b = owners
                assert a != b
                self.neighbours[a].add(b)
                self.neighbours[b].add(a)
                shares[a, b] += 1
        self.heavy = [set() for _ in supports]
        self.original_opens = list(self.arity)
        for (a, b), mult in shares.items():
            if mult > 1:
                self.heavy[a].add(b)
                self.heavy[b].add(a)
                self.original_opens[a] -= mult
                self.original_opens[b] -= mult
        self.source_ids = {j for j, h in enumerate(self.heavy) if h}
        self.live = {j for j, h in enumerate(self.loose) if h}

def original_births(P, moves):
    pair_quota = Counter()
    for j in P.source_ids:
        members = sorted(h for h in P.heavy[j] if P.original_opens[h])
        for a, b in combinations(members, 2):
            pair_quota[a] += 1
            pair_quota[b] += 1
            if {a, b} <= P.live and not ((P.neighbours[a] & P.neighbours[b]) - P.source_ids):
                count = P.original_opens[a] + P.original_opens[b] - len(members)
                moves[((a, b), count)] += 1
    for j in P.source_ids:
        used = sum((P.neighbours[k] & P.source_ids) == {j} for k in P.neighbours[j] - P.source_ids)
        remaining = P.original_opens[j] - pair_quota[j] - used
        assert 0 <= remaining <= P.loose[j]
        if remaining:
            moves[((j,), max(2, P.original_opens[j] - 1))] += remaining


def three_original_pairs(P, moves):
    marked = {k: frozenset(P.neighbours[k] & P.source_ids) for k, a in enumerate(P.arity)
              if a == 3 and k not in P.source_ids and len(P.neighbours[k] & P.source_ids) == 2}
    for group in combinations(sorted(marked.keys() & P.live), 3):
        witnesses = {marked[j] for j in group}
        if len(witnesses) == 3 and len(set.union(*(set(s) for s in witnesses))) == 3:
            moves[(group, 1)] += 1
    top = {j for k in marked for j in P.neighbours[k] - P.source_ids if P.arity[j] == 4}
    assert len(top) <= 1
    return set(marked), top


def four_branches(P, moves):
    centres = {j for j in P.source_ids if P.original_opens[j] == 4}
    if not centres:
        return set(), set()
    z, = centres
    singletons = P.neighbours[z] - P.source_ids
    representatives = {frozenset((j,)): j for j in singletons}
    excluded = {z} | singletons | (set().union(*(P.neighbours[j] for j in singletons)) - P.source_ids)
    for size in range(2, 5):
        for child in map(frozenset, combinations(sorted(singletons), size)):
            leaves = [child - {j} for j in child]
            if not all(s in representatives for s in leaves):
                continue
            parents = tuple(sorted(representatives[s] for s in leaves))
            already = set.intersection(*(P.neighbours[j] for j in parents)) - {z}
            if already:
                representative, = already
                representatives[child] = representative
            else:
                assert set(parents) <= P.live
                moves[(parents, max(1, 4 - size))] += 1
    if len(singletons) == 4 and frozenset(singletons) in representatives:
        return excluded, {representatives[frozenset(singletons)]}
    return excluded, set()


def read_unlabelled(supports):
    P = Physical(supports)
    moves = Counter()
    original_births(P, moves)
    exceptional_pairs, three_top = three_original_pairs(P, moves)
    excluded_common, four_top = four_branches(P, moves)
    tops = three_top | four_top
    live_relays = set()
    for j in tops:
        if j in P.live:
            assert P.loose[j] == 1
            moves[((j,), 2)] += 1
        else:
            relay, = (h for h in P.neighbours[j] if P.arity[h] == 3 and h not in exceptional_pairs)
            if relay in P.live:
                live_relays.add(relay)

    activity = P.live - P.source_ids - exceptional_pairs
    boundary = {h for h, size in enumerate(P.arity) if size == 3} | P.source_ids
    identified_live_relays = set()
    for h in sorted(activity & boundary):
        count = 2 - len(P.neighbours[h] & boundary)
        assert 0 <= count <= P.loose[h]
        if count:
            moves[((h,), 2)] += count
        if any(j not in boundary and not P.loose[j] for j in P.neighbours[h]):
            identified_live_relays.add(h)
    assert identified_live_relays == live_relays

    wrong_without_finite_exclusion = 0
    pairs = [h for h in sorted(activity) if P.arity[h] in (3, 4)]
    for a, b in combinations(pairs, 2):
        common = P.neighbours[a] & P.neighbours[b]
        if len(common) != 1:
            continue
        c, = common
        if P.loose[c]:
            continue
        if c in excluded_common:
            wrong_without_finite_exclusion += ((a, b), 2) not in moves
        else:
            assert ((a, b), 2) not in moves
            moves[((a, b), 2)] = 1
    return moves, P, {"live_relays_identified": len(live_relays),
                     "extra_binary_without_finite_witness_exclusion": wrong_without_finite_exclusion}


def panels(plan):
    roots = set(ORIGINAL)
    finite_full = set(plan.finite.values())
    square = [i for i in ideals(WIDTH) if i and (plan.shifted or {(1, 0), (0, 1)} <= i)]
    yield "direct", WIDTH, [(roots | plan.place_set("direct", i), "direct") for i in square]
    square = [i for i in ideals(WIDTH) if i]
    yield "relayed", WIDTH, [(roots | finite_full | plan.place_set("relayed", i), "relayed") for i in square]
    small = [i for i in ideals(CROSSED_WIDTH) if i and (plan.shifted or {(1, 0), (0, 1)} <= i)]
    yield "finite_crossed_with_direct", CROSSED_WIDTH, [(roots | f | plan.place_set("direct", i), "direct")
                                                       for f in finite_ideals(plan) for i in small]


def check_panel(plan, observation_window, rows, salt):
    rng = Random(salt)
    names = list(range(plan.maximum_name))
    rng.shuffle(names)
    counts = Counter()
    for built, branch in rows:
        order = sorted(built)
        rng.shuffle(order)
        number = {name: j for j, name in enumerate(order)}
        supports = tuple(tuple(names[d] for d in reversed(plan.support[x])) for x in order)
        expected = plan.expected(built, number)
        actual, P, local_counts = read_unlabelled(supports)
        if actual != expected:
            raise AssertionError({"shifted": plan.shifted, "built": sorted(built), "order": order,
                                  "missing": expected - actual, "unplanned": actual - expected})
        counts["fragments"] += 1
        ready = [c for c, parents in plan.parents.items() if c not in built and all(p in built for p in parents)]
        counts["genuinely_mixed_fragments"] += min(plan.depth[c] for c in ready) < max(plan.depth[h] for h in built)
        counts["live_roots"] += len(P.live)
        counts["roots_offered_a_birth"] += len({j for parents, _ in actual for j in parents})
        counts["births"] += sum(actual.values())
        counts["rooted_births"] += sum(len(parents) * n for (parents, _), n in actual.items())
        counts["unaries"] += sum(n for (p, _), n in actual.items() if len(p) == 1)
        counts["binary_births"] += sum(n for (p, _), n in actual.items() if len(p) == 2)
        counts["larger_births"] += sum(n for (p, _), n in actual.items() if len(p) >= 3)
        counts.update(local_counts)
        counts["ready_outside_window"] += sum(c in plan.position and plan.position[c][0] == branch and
                                              max(plan.position[c][1:]) >= observation_window for c in ready)
    return {**counts, "failures": 0, "rank_mixture_test": "a ready unbuilt birth has lower depth than some built holder"}


def incorrect_spent_only():
    plan = Template(True)
    chosen = {(0, 0), (1, 0), (0, 1), (1, 1)}
    built = set(ORIGINAL) | plan.place_set("direct", chosen)
    order = sorted(built)
    actual, P, _ = read_unlabelled(tuple(plan.support[x] for x in order))
    grid = plan.grid["direct"]
    pair = tuple(sorted(order.index(grid[p]) for p in ((1, 0), (0, 1))))
    common = P.neighbours[pair[0]] & P.neighbours[pair[1]]
    assert len(common) == 2 and sum(P.loose[j] == 0 for j in common) == 1
    assert all(P.loose[j] for j in pair) and (pair, 2) not in actual
    return {"coordinates_for_evaluator_only": sorted(chosen), "common_holder_count": 2, "spent_common_count": 1,
            "false_pair_if_counting_only_spent_holders": True}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    data = {"main_window_per_direction": WIDTH, "crossed_window_per_direction": CROSSED_WIDTH, "arms": {},
            "incorrect_counting_only_spent_control": incorrect_spent_only(),
            "reader_input": "Renamed physical supports only. Whole-stage measurements do not attest an optimal observation radius.",
            "unique_reference_fragments_after_panel_overlaps": {}}
    for shifted, arm in ((False, "W_spent"), (True, "W_live")):
        plan = Template(shifted)
        experiments = list(panels(plan))
        data["arms"][arm] = {panel: check_panel(plan, width, rows, 2026112097 + i)
                             for i, (panel, width, rows) in enumerate(experiments)}
        distinct = {frozenset(built) for _, _, rows in experiments for built, _ in rows}
        data["unique_reference_fragments_after_panel_overlaps"][arm] = len(distinct)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
