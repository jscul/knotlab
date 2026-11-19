"""Independently replay explicit support lineages and check their exact tables."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def connected(nodes, adjacent):
    pending = nodes & -nodes
    remaining = nodes ^ pending
    while pending and remaining:
        v = (pending & -pending).bit_length() - 1
        pending ^= 1 << v
        found = remaining & adjacent[v]
        pending |= found
        remaining ^= found
    return not remaining


@dataclass
class Arrangement:
    stars: tuple

    @classmethod
    def parse(cls, raw):
        require(isinstance(raw, list) and raw, "an arrangement needs at least one support")
        for star in raw:
            require(isinstance(star, list) and star, "supports must be nonempty lists")
            require(all(type(x) is int and x >= 0 for x in star), "labels must be nonnegative integers")
            require(len(set(star)) == len(star), "a support repeats a distinction")
        return cls(tuple(frozenset(star) for star in raw))

    def __post_init__(self):
        owners = defaultdict(list)
        for j, star in enumerate(self.stars):
            for x in star:
                owners[x].append(j)
        self.owners = dict(owners)
        self.labels = tuple(sorted(owners))
        require(all(len(holders) in (1, 2) for holders in owners.values()),
                "each distinction must have one or two holders")
        self.loose = {x: holders[0] for x, holders in owners.items() if len(holders) == 1}
        self.live = frozenset(self.loose.values())
        self.neighbors = [set() for _ in self.stars]
        for holders in owners.values():
            if len(holders) == 2:
                u, v = holders
                self.neighbors[u].add(v)
                self.neighbors[v].add(u)
        require(connected((1 << len(self.stars)) - 1, self.neighbor_masks()),
                "the junctions must be connected before adding the outside holder")
        label_bits = {x: 1 << i for i, x in enumerate(self.labels)}
        self.masks = [sum(label_bits[x] for x in star) for star in self.stars]
        self.label_bits = label_bits

    def neighbor_masks(self):
        return [sum(1 << u for u in neighbors) for neighbors in self.neighbors]

    def holder_graph(self):
        """Use the outside holder only if some distinction has an outside end."""
        outside = len(self.stars) if self.loose else None
        ends = {x: tuple(holders) if len(holders) == 2 else (holders[0], outside)
                for x, holders in self.owners.items()}
        adjacent = [0] * (len(self.stars) + bool(self.loose))
        for u, v in ends.values():
            adjacent[u] |= 1 << v
            adjacent[v] |= 1 << u
        return ends, adjacent, outside


def reduce_word(word, basis):
    while word and (pivot := word.bit_length()) in basis:
        word ^= basis[pivot]
    return word


def linear_basis(masks):
    basis = {}
    for word in masks:
        if word := reduce_word(word, basis):
            basis[word.bit_length()] = word
    return basis


def start_audit(start):
    require(all(len(star) >= 3 for star in start.stars), "a start support has fewer than three distinctions")
    ends, adjacent, outside = start.holder_graph()
    universe = (1 << len(adjacent)) - 1
    cut_holders = [u for u in range(len(start.stars)) if not connected(universe ^ (1 << u), adjacent)]
    counts = Counter(tuple(sorted(pair)) for pair in ends.values())
    forced = []
    for x, (u, v) in sorted(ends.items()):
        if counts[tuple(sorted((u, v)))] == 1:
            removed = adjacent.copy()
            removed[u] ^= 1 << v
            removed[v] ^= 1 << u
            if not connected(universe, removed):
                forced.append(x)
    return {"open": outside is not None, "non_outside_cut_holders": cut_holders,
            "forced_distinctions": forced, "meets_once": all(count == 1 for count in
            Counter(tuple(owners) for owners in start.owners.values() if len(owners) == 2).values()),
            "census_open_legal": outside is not None and not cut_holders and not forced}


def maximal_sets(family):
    return {members for members in family if not any(members < other for other in family)}


def common_meeters(neighbors, live):
    # Their downward closure is the literal family of sets met by one junction.
    return {frozenset(members & live) for members in neighbors}


def groups(neighbors, live):
    common = common_meeters(neighbors, live)
    pairs = {frozenset(pair) for members in common for pair in combinations(members, 2)}
    candidates = {u: {v for v in live - {u} if frozenset((u, v)) in pairs} for u in live}
    valid = set()

    def cliques(chosen, remaining, excluded):
        if not (remaining or excluded):
            if len(chosen) >= 3 and not any(chosen <= members for members in common):
                valid.add(frozenset(chosen))
            return
        pivot = max(remaining | excluded, key=lambda v: len(remaining & candidates[v]))
        for u in sorted(remaining - candidates[pivot]):
            cliques(chosen | {u}, remaining & candidates[u], excluded & candidates[u])
            remaining.remove(u)
            excluded.add(u)

    cliques(set(), set(live), set())
    return valid | {pair for pair in pairs if not any(pair <= members for members in valid)}


def round_replay(previous, following):
    require(bool(previous.live), "a closed stage has no following complete round")
    inherited = Counter(previous.stars)
    actual = Counter(following.stars)
    require(not inherited - actual, "the round changed an old junction's support")
    additions = list((actual - inherited).elements())

    expected = Counter(groups(previous.neighbors, previous.live))
    available = Counter(previous.loose.values())
    used = Counter(u for members in expected for u in members)
    require(not used - available, "a live junction has fewer loose distinctions than its groups demand")
    for u, offshoots in (available - used).items():
        expected[frozenset((u,))] = offshoots

    old = set(previous.labels)
    records = []
    all_taken = Counter()
    all_fresh = Counter()
    for star in additions:
        taken = star & old
        fresh = star - old
        require(taken <= previous.loose.keys(), "a new junction took a non-loose old distinction")
        parents = {previous.loose[x]: x for x in taken}
        require(len(parents) == len(taken), "a new junction took twice from one parent")
        all_taken.update(taken)
        all_fresh.update(fresh)
        records.append({"taken": parents, "fresh": sorted(fresh)})
    require(all_taken == Counter(previous.loose.keys()), "the round must take each loose distinction exactly once")
    require(all(count == 1 for count in all_fresh.values()), "fresh distinctions must have one holder")
    require(Counter(frozenset(row["taken"]) for row in records) == expected,
            "the round's parent sets differ from the complete groups and offshoots")

    neighbors = [set(neighbors) for neighbors in previous.neighbors] + [set() for _ in records]
    next_live = frozenset(range(len(previous.stars), len(neighbors)))
    for j, row in enumerate(records, len(previous.stars)):
        neighbors[j].update(row["taken"])
        for u in row["taken"]:
            neighbors[u].add(j)
    demand = Counter(j for members in groups(neighbors, next_live) for j in members)
    basis = linear_basis(previous.masks)
    for j, row in enumerate(records, len(previous.stars)):
        take_mask = sum(previous.label_bits[x] for x in row["taken"].values())
        implied = reduce_word(take_mask, basis) == 0
        require(implied == (len(row["taken"]) == len(previous.loose)),
                "GF(2) implication and the connected-stage criterion disagree")
        count = demand[j] if implied else max(demand[j], 3 - len(row["taken"]), 1)
        require(len(row["fresh"]) == count, "the round used a different fresh count from the fewest rule")
        row.update(demand=demand[j], implied=implied)
    return records


def lineage(obj):
    current = Arrangement.parse(obj["current"])
    following = Arrangement.parse(obj["next"])
    start = obj.get("start")
    previous_rounds = []
    audit = None
    if start is not None:
        stages = [Arrangement.parse(stage) for stage in [start, *obj.get("intermediate", [])]]
        audit = start_audit(stages[0])
        for left, right in zip(stages, [*stages[1:], current]):
            previous_rounds.append(round_replay(left, right))
    else:
        require(not obj.get("intermediate"), "an intermediate stage needs a starting arrangement")
        audit = start_audit(current)
    return current, following, round_replay(current, following), {"start": audit, "rounds": previous_rounds}


def exact_table(arrangement, shore_limit):
    """Scan shores by a Gray traversal and retain only cuts with both sides connected."""
    _, adjacent, _ = arrangement.holder_graph()
    shore_count = (1 << (len(adjacent) - 1)) - 1
    require(shore_count <= shore_limit, f"exact table needs {shore_count} shores, limit {shore_limit}")
    all_vertices = (1 << len(adjacent)) - 1
    lower = {}
    witness = {}
    shore = cut = 0
    bonds = 0
    for step in range(1, shore_count + 1):
        changed = step & -step
        shore ^= changed
        cut ^= arrangement.masks[changed.bit_length() - 1]
        if not connected(shore, adjacent) or not connected(all_vertices ^ shore, adjacent):
            continue
        bonds += 1
        distance = cut.bit_count() - 1
        for pair in combinations((arrangement.labels[i] for i in indices(cut)), 2):
            if distance < lower.get(pair, float("inf")):
                lower[pair] = distance
                witness[pair] = shore
    table = {pair: lower.get(pair) for pair in combinations(arrangement.labels, 2)}
    return table, witness, {"shores_examined": shore_count, "bonds": bonds, "entries": len(table)}


def reading(a, b, phi):
    loose = {phi[x] for x in a.loose} == set(b.loose)
    supports_b = {b.stars[j]: j for j in b.live}
    psi = {}
    for j in a.live:
        dest = supports_b.get(frozenset(phi[x] for x in a.stars[j]))
        if dest is not None:
            psi[j] = dest
    live_stars = set(psi) == set(a.live) and set(psi.values()) == set(b.live)
    family = maximal = False
    if live_stars:
        source = common_meeters(a.neighbors, a.live)
        transported = {frozenset(psi[j] for j in star) for star in source}
        target = common_meeters(b.neighbors, b.live)
        family = (all(any(s <= t for t in target) for s in transported)
                  and all(any(t <= s for s in transported) for t in target))
        maximal = maximal_sets(transported) == maximal_sets(target)
    return psi, {"loose_set": loose, "all_live_stars": live_stars,
                 "whole_family": family, "maximal_family": maximal,
                 "keeps_reading": loose and live_stars and family and maximal}


def pair_key(x, y):
    return (x, y) if x < y else (y, x)


def mismatches(table_a, table_b, mapping):
    return [((x, y), value, table_b[pair_key(mapping[x], mapping[y])])
            for (x, y), value in table_a.items() if x in mapping and y in mapping
            and value != table_b[pair_key(mapping[x], mapping[y])]]


def find_matching(table_a, table_b, allowed, fixed, row_a=None, row_b=None):
    if len(allowed) != len({x for pair in table_b for x in pair}):
        return None
    if mismatches(table_a, table_b, fixed):
        return None
    labels_b = sorted({x for pair in table_b for x in pair})
    sig_a = {x: Counter(table_a[pair_key(x, y)] for y in allowed if x != y) for x in allowed}
    sig_b = {x: Counter(table_b[pair_key(x, y)] for y in labels_b if x != y) for x in labels_b}
    domains = {x: {y for y in choices if sig_a[x] == sig_b[y]} for x, choices in allowed.items()}
    if any(y not in domains[x] for x, y in fixed.items()):
        return None
    assigned = dict(fixed)
    unused = set(labels_b) - set(fixed.values())

    def compatible(x, y):
        for u, v in assigned.items():
            if table_a[pair_key(x, u)] != table_b[pair_key(y, v)]:
                return False
            if row_a is not None and x in row_a and u in row_a:
                if (row_a[x] == row_a[u]) != (row_b[y] == row_b[v]):
                    return False
        return True

    def search():
        if len(assigned) == len(allowed):
            if row_a is not None:
                for x, u in combinations(row_a, 2):
                    if (row_a[x] == row_a[u]) != (row_b[assigned[x]] == row_b[assigned[u]]):
                        return None
            return dict(assigned)
        choices = [(tuple(y for y in sorted(domains[x] & unused) if compatible(x, y)), x)
                   for x in allowed.keys() - assigned.keys()]
        targets, x = min(choices, key=lambda item: (len(item[0]), item[1]))
        for y in targets:
            assigned[x] = y
            unused.remove(y)
            if solution := search():
                return solution
            unused.add(y)
            del assigned[x]
        return None

    return search()


def round_domains(records_a, records_b, psi, allowed):
    groups_b = defaultdict(list)
    for row in records_b:
        groups_b[frozenset(row["taken"]), len(row["fresh"])].append(row)
    domains = {x: set(values) for x, values in allowed.items()}
    for row in records_a:
        targets = groups_b[frozenset(psi[u] for u in row["taken"]), len(row["fresh"])]
        for u, x in row["taken"].items():
            domains[x] &= {target["taken"][psi[u]] for target in targets}
        for x in row["fresh"]:
            domains[x] &= {y for target in targets for y in target["fresh"]}
    membership = [{x: j for j, row in enumerate(records)
                   for x in [*row["taken"].values(), *row["fresh"]]}
                  for records in (records_a, records_b)]
    return domains, membership


def cut_certificate(arrangement, pair, distance, shore):
    ends, adjacent, _ = arrangement.holder_graph()
    full = (1 << len(adjacent)) - 1
    require(0 < shore < full and connected(shore, adjacent) and connected(full ^ shore, adjacent),
            "a claimed bond does not have two connected nonempty shores")
    cut = [x for x, (u, v) in ends.items() if bool(shore & (1 << u)) != bool(shore & (1 << v))]
    require(set(pair) <= set(cut) and len(cut) - 1 == distance, "claimed bond has the wrong support or size")
    return {"pair": pair, "distance": distance, "shore": list(indices(shore)), "cut": sorted(cut)}


def check(case, shore_limit, unrestricted=False):
    a, next_a, records_a, lineage_a = lineage(case["a"])
    b, next_b, records_b, lineage_b = lineage(case["b"]) if "b" in case else (a, next_a, records_a, lineage_a)
    pairs = case["permutation"]
    inputs = [(int(x), y) for x, y in pairs.items()] if isinstance(pairs, dict) else pairs
    require(all(type(x) is int and type(y) is int for x, y in inputs),
            "permutation labels must be integers")
    phi = dict(inputs)
    require(len(phi) == len(pairs) and set(phi) == set(a.labels) and set(phi.values()) == set(b.labels)
            and len(a.labels) == len(b.labels), "permutation must give exactly one image for each old distinction")

    snapshots = dict(current_a=a, current_b=b, next_a=next_a, next_b=next_b)
    exact = {}
    computed = {}
    for key, stage in snapshots.items():
        if stage.stars not in computed:
            computed[stage.stars] = exact_table(stage, shore_limit)
        exact[key] = computed[stage.stars]
    ta, tb, na, nb = [exact[key][0] for key in snapshots]
    for cert in case.get("certificates", []):
        name = cert["stage"]
        pair = tuple(sorted(cert["pair"]))
        distance = cert["distance"]
        require(pair in exact[name][0] and exact[name][0][pair] == distance,
                "a claimed distance differs from the exact minimum")
        if "shore" in cert:
            shore = cert["shore"]
            size = len(snapshots[name].stars) + bool(snapshots[name].loose)
            require(all(type(j) is int and 0 <= j < size for j in shore), "invalid junction in claimed shore")
            require(len(set(shore)) == len(shore), "claimed shore repeats a junction")
            cut_certificate(snapshots[name], pair, distance, sum(1 << j for j in shore))

    psi, keeps = reading(a, b, phi)
    current_failures = mismatches(ta, tb, phi)
    rank_a = len(linear_basis(a.masks))
    rank_b = len(linear_basis(b.masks))
    rank_joint = len(linear_basis([*b.masks, *(sum(b.label_bits[phi[x]] for x in star) for star in a.stars)]))
    fixed = {x: y for x, y in phi.items() if x not in a.loose}
    fixed_failures = mismatches(na, nb, fixed)
    decisive = None
    if fixed_failures:
        pair, left, right = fixed_failures[0]
        pair_b = tuple(sorted(phi[x] for x in pair))
        decisive = {}
        for name, p, d in [("current_a", pair, ta[pair]), ("current_b", pair_b, tb[pair_b]),
                           ("next_a", pair, left), ("next_b", pair_b, right)]:
            decisive[name] = ({"pair": p, "distance": None} if d is None else
                              cut_certificate(snapshots[name], p, d, exact[name][1][p]))

    extensions = {}
    if keeps["keeps_reading"] and not current_failures:
        old_a, old_b = set(a.labels), set(b.labels)
        fresh_b = set(next_b.labels) - old_b
        exact_allowed = {x: {phi[x]} if x in old_a else fresh_b for x in next_a.labels}
        loose_b = defaultdict(set)
        for y, j in b.loose.items():
            loose_b[j].add(y)
        repair_allowed = {x: (loose_b[psi[a.loose[x]]] if x in a.loose else exact_allowed[x])
                          for x in next_a.labels}
        rounds_allowed, membership = round_domains(records_a, records_b, psi, repair_allowed)
        for name, domains, given, rows in [
            ("fixes_given_old_mapping", exact_allowed, phi, (None, None)),
            ("allows_within_parent_repair", repair_allowed, fixed, (None, None)),
            ("also_matches_round_junctions", rounds_allowed, fixed, membership),
        ]:
            match = None if decisive else find_matching(na, nb, domains, given, *rows)
            extensions[name] = None if match is None else sorted(match.items())
    if unrestricted:
        match = find_matching(na, nb, {x: set(next_b.labels) for x in next_a.labels}, {})
        extensions["unrestricted_next_matching"] = None if match is None else sorted(match.items())

    return {"current_tables_match": not current_failures,
            "current_table_mismatch_count": len(current_failures),
            "first_current_mismatch": current_failures[0] if current_failures else None,
            "reading": keeps, "carries_equations": rank_a == rank_b == rank_joint,
            "reachable_a": bool(lineage_a["rounds"]), "reachable_b": bool(lineage_b["rounds"]),
            "lineage_a": lineage_a, "lineage_b": lineage_b, "next_round_a": records_a, "next_round_b": records_b,
            "exact_tables": {key: info for key, (_, _, info) in exact.items()},
            "next_non_loose_mismatch_count": len(fixed_failures), "decisive_bonds": decisive,
            "extensions": extensions, "supplied_certificates_checked": len(case.get("certificates", []))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--max-shores", type=int, default=(1 << 22) - 1,
                        help="maximum number of shores to scan per distinct arrangement")
    parser.add_argument("--unrestricted", action="store_true", help="also look for any next table matching")
    args = parser.parse_args()
    result = check(json.loads(args.case.read_text()), args.max_shores, args.unrestricted)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
