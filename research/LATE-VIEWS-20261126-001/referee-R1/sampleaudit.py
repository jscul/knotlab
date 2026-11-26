"""Reconstruct the frozen samples and their structural exposure from the start holdings."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from hashlib import sha256
from itertools import combinations, islice, permutations, product
import json
from math import prod
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter

from networkx.generators.atlas import graph_atlas_g


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ROOT = RESEARCH.parent
AT_LEAST_FOUR = "a group cell of four or more"
FOUR_WITH_CHAINS = AT_LEAST_FOUR + ", with chains"
SEPARATE = "two disjoint group cells"
SHARE_ONE = "group cells sharing a knot"
SHARE_TWO = "group cells sharing two knots"
BLOCK_WITH_CHAINS = "a block meeting a group cell, with chains"
EXTRA_EXPOSURES = ("a group cell of four or more, without chains",
                   "a block meets a cell of four or more in its own piece with chains",
                   "a block meets a cell of four or more without chains in its piece",
                   "a block meets a cell of four or more",
                   "a block meets a cell in at least three knots")


def read_rows(path):
    with (gzip.open if path.suffix == ".gz" else open)(path, "rt") as source:
        yield from map(json.loads, source)


def digest(value):
    return sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def neighbour_masks(n, meetings):
    adjacency = [0] * n
    for left, right in meetings:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    return tuple(adjacency)


def joins_all(adjacency):
    found, pending = 1, 1
    while pending:
        new = adjacency[next(members(pending))] & ~found
        pending = (pending & (pending - 1)) | new
        found |= new
    return found.bit_count() == len(adjacency)


def holdings_of(shared, loose):
    holdings = [[] for _ in loose]
    for distinction, (left, right) in enumerate(shared):
        holdings[left].append(distinction)
        holdings[right].append(distinction)
    fresh = len(shared)
    for row, open_count in zip(holdings, loose, strict=True):
        row.extend(range(fresh, fresh + open_count))
        fresh += open_count
    return holdings


def parse_holdings(holdings):
    by_distinction = defaultdict(list)
    for knot, distinctions in enumerate(holdings):
        assert len(distinctions) >= 3 and len(set(distinctions)) == len(distinctions)
        for distinction in distinctions:
            by_distinction[distinction].append(knot)
    loose = [0] * len(holdings)
    shared = []
    for holders in by_distinction.values():
        if len(holders) == 1:
            loose[holders[0]] += 1
        else:
            assert len(holders) == 2
            shared.append(tuple(holders))
    assert joins_all(neighbour_masks(len(loose), shared))
    return tuple(sorted(shared)), tuple(loose)


class Census:
    """Use the atlas for historical labels. Check every numbered meeting pattern independently."""

    def __init__(self, atlas, n):
        self.n = n
        self.entries = []
        self.patterns = {}
        self.weights = []
        self.numberings = {}
        self.symmetries = {}
        pairs = tuple(combinations(range(n), 2))
        self.pair_bits = {pair: 1 << i for i, pair in enumerate(pairs)}
        orders = tuple(permutations(range(n)))
        for number, pattern in enumerate(atlas):
            if len(pattern) != n:
                continue
            shared = tuple(sorted(tuple(sorted(pair)) for pair in pattern.edges))
            adjacent = neighbour_masks(n, shared)
            if not joins_all(adjacent):
                continue
            self.patterns[number] = (shared, adjacent)
            original = self.encoded(shared)
            images, symmetries = {}, []
            for order in orders:
                moved = self.encoded(tuple(sorted((order[a], order[b]))) for a, b in shared)
                images[moved] = order
                if moved == original:
                    symmetries.append(order)
            assert self.numberings.keys().isdisjoint(images), number
            self.numberings.update((moved, (number, order)) for moved, order in images.items())
            self.symmetries[number] = symmetries
            seen = set()
            domains = [range(max(0, 3 - mask.bit_count()), 4) for mask in adjacent]
            for loose in product(*domains):
                if loose in seen or not any(loose):
                    continue
                orbit = {tuple(loose[knot] for knot in order) for order in symmetries}
                assert loose == min(orbit)
                seen.update(orbit)
                self.entries.append((number, loose))
                self.weights.append(len(images) * len(orbit))
        numbered_total = 0
        connected_count = 0
        for mask in range(1 << len(pairs)):
            adjacent = neighbour_masks(n, (pairs[i] for i in members(mask)))
            if joins_all(adjacent):
                assert mask in self.numberings
                connected_count += 1
                degree = [links.bit_count() for links in adjacent]
                numbered_total += prod(min(4, d + 1) for d in degree) - all(d >= 3 for d in degree)
        assert connected_count == len(self.numberings) and numbered_total == sum(self.weights)
        self.index_of = {entry: index for index, entry in enumerate(self.entries)}
        self.stats = {"meeting patterns up to renaming": len(self.patterns),
                      "numbered meeting patterns checked": 1 << len(pairs),
                      "connected numbered meeting patterns": connected_count,
                      "starts up to renaming": len(self.entries),
                      "starts with knots numbered": numbered_total,
                      "historical roster digest": digest(self.entries)}

    def encoded(self, pairs):
        return sum(self.pair_bits[pair] for pair in pairs)

    def holdings(self, index):
        number, loose = self.entries[index]
        return holdings_of(self.patterns[number][0], loose)

    def lookup(self, shared, loose):
        if not any(loose) or max(loose) > 3 or len(shared) != len(set(shared)):
            return None
        number, numbering = self.numberings[self.encoded(shared)]
        presented = tuple(loose[index] for index in numbering)
        least = min(tuple(presented[index] for index in order) for order in self.symmetries[number])
        return self.index_of[number, least]


def groups_for(adjacency, live):
    # Test validity on all live subsets. Discard a valid set precisely when a
    # larger valid set contains it. Common-neighbour witnesses can be dead.
    candidates = {}
    pairs = []
    for a in members(live):
        candidates[a] = 0
        for b in members(live & ~(1 << a)):
            if adjacency[a] & adjacency[b]:
                candidates[a] |= 1 << b
                if a < b:
                    pairs.append((1 << a) | (1 << b))
    valid = []
    subset = live
    while subset:
        if subset.bit_count() >= 3:
            common = (1 << len(adjacency)) - 1
            for knot in members(subset):
                common &= adjacency[knot]
            if not common and all(not (subset & ~(candidates[knot] | (1 << knot)))
                                  for knot in members(subset)):
                valid.append(subset)
        subset = (subset - 1) & live
    cells = tuple(group for group in valid if not any(group != big and group & big == group for big in valid))
    groups = cells + tuple(pair for pair in pairs if not any(pair & cell == pair for cell in cells))
    demand = tuple(sum(bool(group & (1 << knot)) for group in groups) for knot in range(len(adjacency)))
    blocks = tuple(mask & live for mask in adjacency if (mask & live).bit_count() >= 2)
    return groups, cells, demand, blocks, any(sum(pair & block == pair for block in blocks) >= 2 for pair in pairs)


@dataclass(frozen=True)
class Structure:
    read: str
    stratum: str
    dimension: int | None
    groups: tuple
    cells: tuple
    meetings: tuple
    memberships: tuple
    larger_exposures: tuple
    size_by_cell_chains: tuple


def classify(adjacency, loose, roster_cache):
    live = sum(1 << knot for knot, count in enumerate(loose) if count)
    key = (adjacency, live)
    if key not in roster_cache:
        roster_cache[key] = groups_for(adjacency, live)
    groups, cells, demand, original_blocks, repeated_neighbours = roster_cache[key]
    overlap = [(a & b).bit_count() for a, b in combinations(cells, 2)]
    stalled = any(d > open_count for d, open_count in zip(demand, loose, strict=True))
    block_set = set(original_blocks)
    blocks = [block for block in block_set if not any(big != block and block & big == block for big in block_set)
              and not any(block & cell == block for cell in cells)]
    meetings = tuple((block, cell, (block & cell).bit_count()) for block in blocks for cell in cells
                     if (block & cell).bit_count() >= 2)
    total_loose = sum(loose)
    if not stalled and not cells and not repeated_neighbours and total_loose >= 2:
        stratum = "proved class"
    elif not stalled and total_loose == 1:
        stratum = "one loose distinction"
    elif not cells:
        stratum = "repeated blocks only"
    elif any(count >= 2 for count in overlap):
        stratum = SHARE_TWO
    elif meetings:
        stratum = "a block meeting a group cell in two knots"
    elif 1 in overlap:
        stratum = SHARE_ONE
    else:
        stratum = "group cells"
    if stalled or not live:
        return Structure("stall" if stalled else "none", stratum, None, groups, cells, meetings, (), (), ())

    # Join components by the reduced blocks and the cells. Each offshoot adds
    # one point and one attachment, leaving the incidence surplus unchanged.
    pieces = [1 << knot for knot in members(live)]
    collections = blocks + list(cells)
    for part in collections:
        touched = [piece for piece in pieces if piece & part]
        if len(touched) > 1:
            pieces = [piece for piece in pieces if not piece & part] + [sum(touched)]
    chains_at = {knot: (loose[knot] - demand[knot]) * max(0, 3 - loose[knot]) for knot in members(live)}
    chains_of_piece = {}
    rejected = False
    for piece in pieces:
        attached = [part for part in collections if part & piece]
        surplus = 1 - piece.bit_count() + sum(part.bit_count() - 1 for part in attached)
        filled = sum(size - 1 for block, _, size in meetings if block & piece)
        rejected |= surplus != filled
        chain_count = sum(chains_at[knot] for knot in members(piece))
        chains_of_piece.update((knot, chain_count) for knot in members(piece))
    cell_chains = tuple((cell.bit_count(), chains_of_piece[next(members(cell))]) for cell in cells)
    if rejected:
        return Structure("a piece with a cycle", stratum, None, groups, cells, meetings, (), (), cell_chains)
    tags = []
    if any(count >= 4 and chains for count, chains in cell_chains):
        tags.append(FOUR_WITH_CHAINS)
    if any(count >= 4 for count, _ in cell_chains):
        tags.append(AT_LEAST_FOUR)
    if len(cells) >= 2 and not any(overlap):
        tags.append(SEPARATE)
    if 1 in overlap:
        tags.append(SHARE_ONE)
    if any(count >= 2 for count in overlap):
        tags.append(SHARE_TWO)
    if meetings and any(chains for _, chains in cell_chains):
        tags.append(BLOCK_WITH_CHAINS)
    extra = [bool(any(count >= 4 and not chains for count, chains in cell_chains)),
             bool(any(cell.bit_count() >= 4 and chains_of_piece[next(members(cell))] for _, cell, _ in meetings)),
             bool(any(cell.bit_count() >= 4 and not chains_of_piece[next(members(cell))] for _, cell, _ in meetings)),
             bool(any(cell.bit_count() >= 4 for _, cell, _ in meetings)),
             bool(any(size >= 3 for _, _, size in meetings))]
    dimension = max(chains_of_piece[next(members(piece))] or 2 for piece in pieces)
    return Structure("accepted", stratum, dimension, groups, cells, meetings, tuple(tags),
                     tuple(tag for tag, holds in zip(EXTRA_EXPOSURES, extra) if holds), cell_chains)


def roster_check(censuses, rosters, pilot):
    # Only this comparison imports the shared growth engine. The other side
    # and all classifications use the explicit valid-subset definition above.
    sys.path.insert(0, str(ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
                           / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"))
    import eng

    result = {}
    for n, census in censuses.items():
        count, stalls, nonempty = 0, 0, 0
        indices = range(len(census.entries))
        if pilot:
            indices = sorted(set(list(indices[:48]) + list(indices[-48:])))
        for index in indices:
            state = eng.from_stars(census.holdings(index))
            roster = eng.build_roster(state, eng.live_members(state), "roster", eng.Guard(100))
            found = {sum(1 << knot for knot in group) for group in roster.groups}
            _, loose = census.entries[index]
            assert tuple(roster.h.get(knot, 0) for knot in range(n)) == loose
            value = rosters[n][index]
            assert found == set(value.groups), (n, index, found, value.groups)
            assert any(d > roster.h[knot] for knot, d in Counter(k for group in roster.groups for k in group).items()) == (value.read == "stall")
            count += 1
            stalls += value.read == "stall"
            nonempty += bool(found)
        result[n] = {"starts compared exactly": count, "with nonempty groups": nonempty, "stalling": stalls}
    return result


def summaries(structures, indices, weights):
    coverage, by_stratum, named, extra = Counter(), Counter(), Counter(), Counter()
    meeting_types, intersections = Counter(), Counter()
    theorem_class, maximum_cells = Counter(), Counter()
    for index in indices:
        status = structures[index]
        weight = weights[index]
        coverage[status.read] += weight
        if status.read != "accepted":
            if status.read == "a piece with a cycle" and status.stratum == "proved class":
                theorem_class[status.read] += weight
            intersections[(status.read, max(((a & b).bit_count() for a, b in combinations(status.cells, 2)), default=0))] += weight
            continue
        by_stratum[status.stratum] += weight
        if status.stratum == "proved class":
            theorem_class[status.read] += weight
        for tag in status.memberships:
            named[tag] += weight
        for tag in status.larger_exposures:
            extra[tag] += weight
        if status.meetings:
            meeting_types[max(size for _, _, size in status.meetings)] += weight
        maximum_cells[max((cell.bit_count() for cell in status.cells), default=0)] += weight
        intersections[(status.read, max(((a & b).bit_count() for a, b in combinations(status.cells, 2)), default=0))] += weight
    return {"coverage": coverage, "accepted primary strata": by_stratum, "accepted supplement memberships": named,
            "accepted narrower exposures": extra, "accepted largest block and cell overlap": meeting_types,
            "accepted largest cell size": maximum_cells, "original proved class by coverage": theorem_class,
            "largest cell and cell overlap across nonstalling strata": {f"{key[0]} / {key[1]}": value for key, value in intersections.items()}}


def seeds(census, structures):
    ready = list(range(len(census.entries)))
    initial, previous, uniform = [], [], []
    for seed, count, target in ((20261126, 1000, initial), (20261127, 2000, previous), (20261128, 2000, uniform)):
        target.extend(Random(seed).sample(ready, count))
        used = set(target)
        ready = [index for index in ready if index not in used]
    pools = defaultdict(list)
    for index in ready:
        for name in structures[index].memberships:
            pools[name].append(index)
    draw = Random(20261130)
    labels, raw_draws = {}, {}
    for name, pool in sorted(pools.items()):
        raw_draws[name] = draw.sample(pool, min(40, len(pool)))
        for index in raw_draws[name]:
            labels.setdefault(index, name)
    stratified = sorted(labels)
    assert len(set(initial + previous + uniform + stratified)) == 5199
    eligible = [i for i in uniform if structures[i].dimension is not None and structures[i].dimension <= 2]
    stored = [row["index"] for row in read_rows(STUDY / "horizon.jsonl")]
    variants = {"census index order": sorted(eligible), "uniform draw order": eligible}
    matches = [name for name, pool in variants.items() if sorted(Random(20261131).sample(pool, 100)) == stored]
    by_membership = {
        name: {"all in census": sum(name in m.memberships for m in structures), "remaining pool": len(pool),
               "first prior sample": sum(name in structures[i].memberships for i in initial),
               "second prior sample": sum(name in structures[i].memberships for i in previous),
               "uniform membership": sum(name in structures[i].memberships for i in uniform),
               "raw selections": len(raw_draws[name]), "assigned purpose": sum(v == name for v in labels.values()),
               "supplement membership": sum(name in structures[i].memberships for i in stratified),
               "meeting patterns in the supplement membership":
                   Counter(census.entries[i][0] for i in stratified if name in structures[i].memberships)}
        for name, pool in sorted(pools.items())}
    return (initial, previous, uniform, stratified, labels, stored,
            {"frame sizes before uniform draws": [len(census.entries), len(census.entries) - 1000, len(census.entries) - 3000],
             "six knot uniform draws in storage order": {"first prior": digest(initial), "second prior": digest(previous), "frozen uniform": digest(uniform)},
             "eligible census after the three draws": len(ready), "supplement": by_membership,
             "supplement cardinality after retaining first label": len(stratified),
             "raw supplement draw order digests": {name: digest(ids) for name, ids in raw_draws.items()},
             "horizon eligible": len(eligible), "horizon seed orders reproducing the recorded sample": matches,
             "horizon from the uniform sample": set(stored) <= set(eligible),
             "horizon sorted output index digest": digest(stored),
             "hypotheses for a seed order that did not reproduce": {name: digest(sorted(Random(20261131).sample(pool, 100)))
                                                                    for name, pool in variants.items() if name not in matches}})


def growth_weighted_draws(count, n, seed):
    rng = Random(seed)
    emitted, retries = [], 0
    while len(emitted) < count:
        places = [rng.randrange(3, 6)]
        remaining = places.copy()
        shared = []
        for knot in range(1, n):
            places.append(rng.randrange(3, 6))
            remaining.append(places[-1])
            available = {k for k in range(knot) if remaining[k]}
            if not available:
                retries += 1
                break
            links = 1 + (rng.random() < 1 / 3)
            for _ in range(min(links, len(available))):
                # Weighted selection over the accumulated open places, with
                # the first holder removed before a second selection.
                ranked = sorted(available)
                cut = rng.random() * sum(remaining[k] for k in ranked)
                running = 0
                for prior in ranked:
                    running += remaining[prior]
                    if cut < running:
                        break
                available.remove(prior)
                shared.append((prior, knot))
                remaining[prior] -= 1
                remaining[knot] -= 1
        else:
            emitted.append({"sizes": places, "edges": [list(pair) for pair in shared],
                            "stars": holdings_of(shared, remaining)})
    return emitted, retries


def hand_cases():
    out = []

    def record(places, shared):
        shared = list(shared)
        degrees = Counter(knot for pair in shared for knot in pair)
        loose = [size - degrees[knot] for knot, size in enumerate(places)]
        out.append({"sizes": places, "edges": [list(pair) for pair in shared], "stars": holdings_of(shared, loose)})

    for n, loose in product((4, 5, 6), (1, 2, 3)):
        record([n - 1 + loose] * n, combinations(range(n), 2))
    record([5, 5, 6, 6, 7], combinations(range(5), 2))
    record([6, 6, 6, 6, 7, 7], combinations(range(6), 2))
    two_at_one = list(combinations(range(3), 2)) + list(combinations(range(2, 5), 2))
    record([3, 3, 5, 3, 3], two_at_one)
    record([4, 4, 6, 4, 4], two_at_one)
    record([5, 5, 8, 6, 8, 5, 5], list(combinations(range(3), 2)) + [(2, 3), (3, 4)] + list(combinations(range(4, 7), 2)))
    record([8] * 4 + [4] * 4, list(combinations(range(4), 2)) + [(knot, knot + 4) for knot in range(4)])
    record([7, 7, 7, 7, 9, 6], list(combinations(range(5), 2)) + [(4, 5)])
    record([3] * 6 + [7], [pair for knot in (0, 2, 4) for pair in ((knot, knot + 1), (knot, 6), (knot + 1, 6))])
    return out


def canonical_start(shared, loose):
    """Renumbering invariant, with exact permutation checks within refined classes."""
    n = len(loose)
    counts = Counter(shared)
    matrix = [[counts[tuple(sorted((i, j)))] for j in range(n)] for i in range(n)]
    colors = loose
    while True:
        profiles = [(colors[i], tuple(sorted((colors[j], matrix[i][j]) for j in range(n) if matrix[i][j])))
                    for i in range(n)]
        table = {value: color for color, value in enumerate(sorted(set(profiles)))}
        next_colors = tuple(table[value] for value in profiles)
        old_count = len(set(colors))
        colors = next_colors
        if len(table) == old_count:
            break
    groups = defaultdict(list)
    for knot, color in enumerate(colors):
        groups[color].append(knot)
    ordered = [groups[color] for color in sorted(groups)]
    candidates = (tuple(knot for group in groups for knot in group)
                  for groups in product(*(permutations(group) for group in ordered)))
    return min((tuple(loose[knot] for knot in order), tuple(matrix[a][b] for a, b in combinations(order, 2)))
               for order in candidates)


def first_difference(predicted, grown):
    if grown["end"].startswith("stalls"):
        return len(grown["rows"]) + 1
    for t, actual in enumerate(grown["rows"], 1):
        row = predicted[t - 1]
        for read in ("sig0", "sig1"):
            if sorted(actual[read]) != sorted(row[read]):
                return t
    if grown["end"].startswith("closes"):
        return next((t for t in range(len(grown["rows"]) + 1, len(predicted) + 1) if predicted[t - 1]["n"]), None)
    return None


def archive_name(which, law):
    if which == "uniform":
        return f"held_out_{law}.jsonl.gz"
    return f"grown_{which}_{law}.jsonl.gz"


def exact_census_details(census, row, index):
    number, loose = census.entries[index]
    assert (row["index"], row["graph"], tuple(row["loose"])) == (index, number, loose), index
    assert row["stars"] == census.holdings(index), (index, row["stars"])


def check_inputs(censuses, by_n, pilot, cache):
    six = censuses[6]
    initial, previous, uniform, stratified, labels, horizon, sampling = seeds(six, by_n[6])
    seven, retries = growth_weighted_draws(1000, 7, 20261129)
    built = hand_cases()
    inputs = {"uniform": uniform, "stratified": stratified, "handbuilt": range(len(built)),
              "grow7": range(len(seven)), "horizon": horizon}
    if pilot:
        inputs = {name: list(indices[:64]) for name, indices in inputs.items()}
    for path, order, label in (("horizon", horizon, False), ("stratified", stratified, True)):
        for row, index in zip(read_rows(STUDY / (path + ".jsonl")), order, strict=True):
            exact_census_details(six, row, index)
            if label:
                assert row["drawn for"] == labels[index]
    for cases, paths in ((initial, [RESEARCH / "SETTLE-BOUND-20261126-001" / f"grown_g6_{law}.jsonl.gz" for law in ("nae", "par")]),
                         (previous, [RESEARCH / "LAST-MERGE-20261126-001" / f"grown_fresh_{law}.jsonl.gz" for law in ("nae", "parity")])):
        for path in paths:
            count = min(len(cases), 64) if pilot else len(cases)
            archive = read_rows(path)
            if pilot:
                archive = islice(archive, count)
            for row, entry in zip(archive, cases[:count], strict=True):
                exact_census_details(six, row, entry)

    names = {}
    built_structures, seven_structures = {}, {}
    for kind, template, structures in (("handbuilt", built, built_structures), ("grow7", seven, seven_structures)):
        for index, record in enumerate(template):
            shared, loose = parse_holdings(record["stars"])
            structures[index] = classify(neighbour_masks(len(loose), shared), loose, cache)
        if kind == "handbuilt":
            for index, (stored, expected) in enumerate(zip(read_rows(STUDY / "handbuilt.jsonl"), template, strict=True)):
                assert stored["index"] == index and all(stored[key] == value for key, value in expected.items()), index
                names[index] = stored["name"]

    archived_predictions = read_rows(STUDY / "predictions.jsonl.gz")
    result, structures_by_set, relations = {}, {}, {}
    for which, indices in inputs.items():
        rows_for_law = {}
        structures_by_set[which] = {}
        relations[which] = {}
        for law in (("nae",) if which == "horizon" else ("nae", "parity")):
            rows_for_law[law] = {}
            source_archive = read_rows(STUDY / archive_name(which, law))
            for index in (uniform if which == "uniform" else stratified if which == "stratified" else
                          range(len(built)) if which == "handbuilt" else range(len(seven)) if which == "grow7" else horizon):
                predicted = next(archived_predictions)
                assert (predicted["set"], predicted["index"], predicted["knot law"]) == (which, index, law)
                if pilot and len(rows_for_law[law]) >= len(indices):
                    continue
                grown = next(source_archive)
                assert (grown["index"], grown["knot law"]) == (index, law)
                if which in ("handbuilt", "grow7"):
                    template = (built if which == "handbuilt" else seven)[index]
                    assert all(grown[key] == value for key, value in template.items()), (which, index)
                    shape = (built_structures if which == "handbuilt" else seven_structures)[index]
                else:
                    exact_census_details(six, grown, index)
                    shape = by_n[6][index]
                structures_by_set[which][index] = shape
                relations[which][index] = parse_holdings(grown["stars"])
                meaning = ("one loose" if shape.read == "accepted" and law == "parity" and shape.stratum == "one loose distinction"
                           else "predicted" if shape.read == "accepted" else shape.read)
                assert predicted["read"] == meaning, (which, index, law, meaning)
                assert predicted["stratum"] == shape.stratum or shape.read == "stall", (which, index, law, shape)
                assert predicted["rare strata"] == list(shape.memberships), (which, index, law, shape)
                if meaning == "predicted":
                    if law == "nae":
                        assert shape.dimension == predicted["D"], (which, index, law, shape)
                    rows_for_law[law][index] = (meaning, first_difference(predicted["rows"], grown), len(grown["rows"]))
                else:
                    rows_for_law[law][index] = (meaning, None, len(grown["rows"]))
                    if meaning == "stall":
                        assert grown["end"] == "stalls at round 1", (which, index, law)
            if not pilot:
                assert next(source_archive, None) is None
        result[which] = rows_for_law
    assert next(archived_predictions, None) is None
    return result, structures_by_set, relations, names, labels, sampling, (initial, previous), retries


def record_exposure(cases, structures, relations, labels, names, censuses):
    details, exposure = {}, {}
    tested, accepted = set(), set()
    for which, laws in cases.items():
        by_law = {}
        ids = {}
        for index, (shared, loose) in relations[which].items():
            ids[index] = canonical_start(shared, loose)
        for law, rows in laws.items():
            groups = defaultdict(Counter)
            pattern_counts = defaultdict(set)
            failures = []
            for index, (read, miss, rounds) in rows.items():
                shape = structures[which][index]
                outcome = ("differ" if miss is not None else "agree") if read == "predicted" else read
                groups["all rows"][outcome] += 1
                if read != "predicted":
                    continue
                tags = [shape.stratum, *("membership: " + member for member in shape.memberships), *shape.larger_exposures]
                if which == "stratified":
                    tags.append("draw purpose: " + labels[index])
                for tag in tags:
                    groups[tag][outcome] += 1
                    pattern_counts[tag].add(ids[index])
                if miss is not None:
                    record = {"index": index, "stratum": shape.stratum, "memberships": shape.memberships,
                              "narrower exposures": shape.larger_exposures, "earliest difference": miss,
                              "cells": [list(members(mask)) for mask in shape.cells],
                              "block-cell meetings": [[list(members(block)), list(members(cell)), size] for block, cell, size in shape.meetings],
                              "cell sizes and chains in their pieces": shape.size_by_cell_chains, "saved rounds": rounds}
                    if which == "handbuilt":
                        record["description"] = names[index]
                    if which == "stratified":
                        record["drawn for"] = labels[index]
                    failures.append(record)
            by_law[law] = {"outcomes by membership and draw purpose": groups,
                           "distinct starts for each grouping": {tag: len(seen) for tag, seen in pattern_counts.items()},
                           "misses": failures}
        tested.update(ids.values())
        accepted.update(ids[index] for index, row in cases[which]["nae"].items() if row[0] == "predicted")
        counts = Counter(ids.values())
        numbered = Counter(relations[which].values())
        grouped = defaultdict(list)
        for index, identity in ids.items():
            grouped[identity].append(index)
        details[which] = {"knots held at start": Counter(len(loose) for _, loose in relations[which].values()),
                          "draws": len(ids), "distinct up to renaming": len(counts), "numbered starts": len(numbered),
                          "draws in repeated classes": sum(n for n in counts.values() if n > 1),
                          "start multiplicities": Counter(counts.values()),
                          "repeated accepted groups": [indices for indices in grouped.values() if len(indices) > 1 and
                                                       cases[which]["nae"][indices[0]][0] == "predicted"],
                          "accepted draws up to renaming": len({ids[index] for index, row in cases[which]["nae"].items() if row[0] == "predicted"})}
        exposure[which] = by_law
    built = []
    for index, (shared, loose) in relations["handbuilt"].items():
        n = len(loose)
        census_index = censuses[n].lookup(shared, loose) if n in censuses else None
        built.append({"name": names[index], "hand-built index": index, "knots": n, "census index": census_index,
                      "which current six-knot sets include this start": [which for which in ("uniform", "stratified", "horizon")
                                                                         if n == 6 and census_index in relations[which]],
                      "in the up-to-five fitting census": n <= 5 and census_index is not None,
                      "cell sizes and chains in their pieces": structures["handbuilt"][index].size_by_cell_chains,
                      "result": cases["handbuilt"]["nae"][index]})
    identities = {which: {canonical_start(shared, loose) for shared, loose in starts.values()} for which, starts in relations.items()}
    overlaps = {f"{a} / {b}": len(identities[a] & identities[b]) for a, b in combinations(identities, 2)}
    return {"sample identities": details, "distinct recorded identities including nonaccepted across all sets": len(tested),
            "distinct accepted identities across all sets under not-all-equal": len(accepted),
            "identity intersections between current sets": overlaps, "hand-built detail": built, "exposure": exposure}


def main(pilot):
    start = perf_counter()
    timings = {}
    atlas = graph_atlas_g()
    cache = {}
    censuses = {n: Census(atlas, n) for n in range(1, 7)}
    by_n = {n: [classify(census.patterns[number][1], loose, cache) for number, loose in census.entries]
            for n, census in censuses.items()}
    timings["reconstruct census and all structural strata"] = perf_counter() - start
    six = censuses[6]
    baseline = summaries(by_n[6], range(len(six.entries)), [1] * len(six.entries))
    recorded = json.loads((STUDY / "strata_census6.json").read_text())
    assert baseline["coverage"] == recorded["read"]
    assert baseline["accepted primary strata"] == recorded["accepted, by stratum"]
    assert baseline["accepted supplement memberships"] == recorded["accepted, rare strata"]
    numbered = summaries(by_n[6], range(len(six.entries)), six.weights)
    checkpoint = perf_counter()
    round_one = roster_check(censuses, by_n, pilot)
    timings["compare independent round-one groups with shared growth roster"] = perf_counter() - checkpoint
    checkpoint = perf_counter()
    cases, structures, relations, names, labels, sampling, priors, retries = check_inputs(censuses, by_n, pilot, cache)
    sampling["seven-knot rejected generation histories"] = retries
    exposure = record_exposure(cases, structures, relations, labels, names, censuses)
    timings["replay seeds, test archive identities, recreate comparisons, and count exposure"] = perf_counter() - checkpoint
    from sampleaudit_admission import check_admission_and_prior_overlap
    checkpoint = perf_counter()
    admission = check_admission_and_prior_overlap(censuses, by_n, cases, relations, priors, pilot)
    timings["whole-start admission and prior identity overlap"] = perf_counter() - checkpoint
    return {"scope": "timing pilot on archive and roster prefixes" if pilot else "complete frozen sample and structural census review",
            "census by knot count": {n: census.stats for n, census in censuses.items()}, "round one": round_one,
            "six knot structural census, equal weight up to renaming": baseline,
            "six knot structural census, equal weight with knots numbered": numbered, "sampling": sampling,
            **exposure, "admission and overlaps with prior work": admission,
            "seconds by stage": {label: round(seconds, 3) for label, seconds in timings.items()},
            "seconds": round(perf_counter() - start, 3), "peak resident KiB": getrusage(RUSAGE_SELF).ru_maxrss}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    pilot = parser.parse_args().pilot
    result = main(pilot)
    path = HERE / ("sampleaudit_pilot.json" if pilot else "sampleaudit.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path.name, result["seconds"], result["peak resident KiB"])
