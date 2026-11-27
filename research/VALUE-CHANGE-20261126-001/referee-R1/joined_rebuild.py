"""Rebuild the five starts and their reader counts without importing a producer."""

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path


@dataclass(frozen=True)
class Family:
    label: str
    count: int = 3
    size: int = 5
    direct: bool = False
    loose: bool = False


FAMILIES = (
    Family("three rings of five, detour (the referee's 30 knots)"),
    Family("three rings of five, direct links", direct=True),
    Family("three rings of four, detour", size=4),
    Family("two rings of five, detour", count=2),
    Family("three rings of five, detour, one loose distinction at the first chain's middle knot", loose=True),
)


def start(family):
    ring_knots = [list(range(r * family.size, (r + 1) * family.size)) for r in range(family.count)]
    knots = [[] for _ in range(family.count * family.size)]
    lineages = [frozenset([r]) for r in range(family.count) for _ in range(family.size)]
    links = {}
    added_loose = None
    next_name = 0

    def add_distinction(*holders):
        nonlocal next_name
        name = next_name
        next_name += 1
        for holder in holders:
            knots[holder].append(name)
        return name

    for ring in ring_knots:
        for current, following in zip(ring, ring[1:] + ring[:1], strict=True):
            add_distinction(current, following)
    for holder in range(len(knots)):
        add_distinction(holder)
        add_distinction(holder)
    attachments = Counter()
    for first, second in combinations(range(family.count), 2):
        left, right = len(knots), len(knots) + 1
        extra_knots = 2 if family.direct else 5
        knots.extend([] for _ in range(extra_knots))
        lineages.extend(frozenset(["middle"]) for _ in range(extra_knots))
        for r, connector in ((first, left), (second, right)):
            offset = attachments[r]
            ring = ring_knots[r]
            add_distinction(ring[offset], connector)
            add_distinction(ring[(offset + 2) % len(ring)], connector)
            attachments[r] += 1
        links[first, second] = add_distinction(left, right)
        chain = [left, right] if family.direct else [left, left + 2, left + 3, left + 4, right]
        for a, b in zip(chain, chain[1:]):
            add_distinction(a, b)
            if not family.direct:
                add_distinction(a, b)
        if family.loose and (first, second) == (0, 1):
            added_loose = chain[2]
    if added_loose is not None:
        added_loose = add_distinction(added_loose)
    return knots, lineages, ring_knots, links, added_loose


def holders(knots):
    by_name = defaultdict(set)
    for position, knot in enumerate(knots):
        assert len(knot) == len(set(knot))
        for d in knot:
            by_name[d].add(position)
    assert all(len(owners) <= 2 for owners in by_name.values())
    return by_name


def join_groups(witnesses):
    pairs = {pair for witness in witnesses for pair in combinations(sorted(witness), 2)}
    successors = defaultdict(set)
    for a, b in pairs:
        successors[a].add(b)
    larger = []
    for first, options in successors.items():
        for size in range(2, len(options) + 1):
            for rest in combinations(sorted(options), size):
                group = (first, *rest)
                if all(pair in pairs for pair in combinations(rest, 2)):
                    members = set(group)
                    if not any(members <= witness for witness in witnesses):
                        larger.append(group)
    maximal = []
    for group in sorted(larger, key=lambda group: (-len(group), group)):
        if not any(set(group) <= set(other) for other in maximal):
            maximal.append(group)
    used_pairs = {pair for group in maximal for pair in combinations(group, 2)}
    return sorted(maximal + list(pairs - used_pairs))


def mask(names):
    word = 0
    for d in names:
        word |= 1 << d
    return word


def bits(word):
    while word:
        low = word & -word
        yield low
        word ^= low


def bit_parity(word):
    return word.bit_count() % 2


def pivots(rows):
    """Use the lowest set bit as pivot, so solving works in descending order."""
    basis = {}
    for row in rows:
        while row:
            low = row & -row
            if low not in basis:
                basis[low] = row
                break
            row ^= basis[low]
    return basis


def orthogonal(rows, domain):
    basis = pivots(row & domain for row in rows)
    free = domain ^ sum(basis)
    equations = sorted(basis.items(), reverse=True)
    solutions = []
    for name in bits(free):
        word = name
        for low, row in equations:
            if bit_parity(word & row):
                word |= low
        solutions.append(word)
    return solutions


def grow(knots, lineages):
    ownership = holders(knots)
    loose = {i: deque(d for d in knot if len(ownership[d]) == 1) for i, knot in enumerate(knots)}
    live = {i for i in loose if loose[i]}
    witnesses = [set() for _ in knots]
    for owners in ownership.values():
        if len(owners) != 2:
            continue
        a, b = sorted(owners)
        if a in live:
            witnesses[b].add(a)
        if b in live:
            witnesses[a].add(b)
    parents = join_groups(witnesses)
    spent = Counter(parent for group in parents for parent in group)
    assert live and all(spent[i] <= len(loose[i]) for i in live)
    for i in sorted(live):
        parents.extend([(i,)] * (len(loose[i]) - spent[i]))
    newborn_inputs = [[loose[i].popleft() for i in group] for group in parents]
    assert all(not names for names in loose.values())

    children = {i: set() for i in live}
    for child, group in enumerate(parents):
        for parent in group:
            children[parent].add(child)
    future = join_groups(list(children.values()))
    demand = Counter(child for group in future for child in group)
    laws = [mask(knot) for knot in knots]
    old_allowed = orthogonal(laws, mask(ownership))
    next_name = max(ownership) + 1
    next_knots = list(knots)
    next_lineages = list(lineages)
    for child, (group, inputs) in enumerate(zip(parents, newborn_inputs, strict=True)):
        # Every birth here has a nonimplied input parity. Check that premise before using the floor.
        assert any(bit_parity(change & mask(inputs)) for change in old_allowed)
        count = max(demand[child], 3 - len(group), 1)
        next_knots.append(inputs + list(range(next_name, next_name + count)))
        next_lineages.append(frozenset().union(*(lineages[i] for i in group)))
        next_name += count
    return next_knots, next_lineages


def reader_roster(knots, lineages, family):
    ownership = holders(knots)
    roster = {}
    for r in range(family.count):
        members = {i for i, labels in enumerate(lineages) if labels == {r}}
        places = {d for i in members for d in knots[i]}
        own = {d for d in places if ownership[d] <= members}
        roster[r] = {"places": places, "own": own}
    return roster


def pairing_rank(changes, values, side):
    products = (
        sum(bit_parity(x & z & side) << i for i, z in enumerate(values))
        for x in changes
    )
    return len(pivots(products))


class CountingState:
    def __init__(self, knots):
        self.laws = [mask(knot) for knot in knots]
        self.ownership = holders(knots)
        self.domain = mask(self.ownership)
        self.changes = orthogonal(self.laws, self.domain)
        self.law_rank = len(pivots(self.laws))
        assert len(self.changes) + self.law_rank == self.domain.bit_count()

    def value_components(self, domain):
        """A law sum avoiding the outside uses both or neither holder of each outside pair."""
        neighbors = [set() for _ in self.laws]
        loose = [set() for _ in self.laws]
        for d, owners in self.ownership.items():
            if domain & (1 << d):
                continue
            if len(owners) == 2:
                a, b = sorted(owners)
                neighbors[a].add(b)
                neighbors[b].add(a)
            else:
                loose[next(iter(owners))].add(d)
        visited = set()
        answer = []
        for first in range(len(self.laws)):
            if first in visited:
                continue
            visited.add(first)
            pending = [first]
            for knot in pending:
                for other in sorted(neighbors[knot] - visited):
                    visited.add(other)
                    pending.append(other)
            outside_loose = set().union(*(loose[knot] for knot in pending))
            parity = 0
            for knot in pending:
                parity ^= self.laws[knot]
            assert parity & ~domain == mask(outside_loose)
            answer.append((set(pending), outside_loose, parity))
        return answer

    def loose_chain_check(self, A, B, link):
        a, b = mask(A), mask(B)
        components = self.value_components(a | b)
        link_holders = self.ownership[link]
        chain_component = [(knots, loose) for knots, loose, _ in components if link_holders <= knots]
        assert len(chain_component) == 1
        knots, loose = chain_component[0]
        assert loose
        assert all(not (value & a and value & b) for _, outside, value in components if not outside)
        return {"shared link": link, "link holders": sorted(link_holders),
                "law group containing both link holders": sorted(knots), "outside loose distinctions": sorted(loose)}

    def reads(self, A, B, link=None):
        a, b = mask(A), mask(B)
        assert a & b == 0
        readers = a | b
        read_changes = orthogonal(self.laws, readers)
        read_values = orthogonal(self.changes, readers)
        holds_a = {k for k, law in enumerate(self.laws) if law & a}
        holds_b = {k for k, law in enumerate(self.laws) if law & b}
        separated = holds_a.isdisjoint(holds_b)
        e = {
            "unread": pairing_rank(read_changes, read_values, a),
            "changes": pairing_rank(self.changes, read_values, a),
            "values": pairing_rank(read_changes, self.laws, a),
        }
        if link is not None:
            assert (readers >> link) & 1 == 0
            with_link = orthogonal(self.laws, readers | (1 << link))
            e["only link"] = pairing_rank(with_link, read_values, a)

        ranks = {}
        for name, domain in (("A", a), ("B", b), ("AB", readers)):
            ranks[name] = {
                "changes": domain.bit_count() - len(pivots(law & domain for law in self.laws)),
                "values": self.law_rank - len(pivots(law & ~domain for law in self.laws)),
            }
            group_laws = (parity for _, loose, parity in self.value_components(domain) if not loose)
            assert ranks[name]["values"] == len(pivots(group_laws))
        rank_changes = ranks["AB"]["values"] - ranks["A"]["values"] - ranks["B"]["values"]
        rank_values = ranks["AB"]["changes"] - ranks["A"]["changes"] - ranks["B"]["changes"]
        assert (rank_changes, rank_values) == (e["changes"], e["values"])
        holders_overlap = any(owners & holds_a and owners & holds_b for owners in self.ownership.values())
        return {"separated": separated, "held": [len(A), len(B)], "e": e, "local dimensions": ranks,
                "holders meet": holders_overlap}


def rebuild(families, rounds):
    stages = []
    square = []
    for family in families:
        knots, lineages, ring_knots, links, added_loose = start(family)
        for stage in range(rounds + 1):
            state = CountingState(knots)
            rosters = reader_roster(knots, lineages, family)
            rows = []
            for choice in ("places", "own"):
                for pair, link in links.items():
                    a, b = (rosters[r][choice] for r in pair)
                    data = state.reads(a, b, link)
                    if choice == "own":
                        data["own with only link read"] = data["e"].pop("only link")
                    assert data["separated"]
                    if family.loose and pair == (0, 1):
                        data["loose chain check"] = state.loose_chain_check(a, b, link)
                    rows.append({"case": "pair", "rings": pair, "choice": choice, **data})
                if family.count == 3:
                    a = rosters[0][choice] | rosters[2][choice]
                    b = rosters[1][choice]
                    data = state.reads(a, b)
                    assert data["separated"]
                    rows.append({"case": "union", "choice": choice, **data})
                    if data["e"]["changes"] == 2:
                        square.append({"family": family.label, "round": stage, "choice": choice,
                                       "knots": knots, "A": sorted(a), "B": sorted(b)})
            u, v = ring_knots[0][:2]
            a = set(knots[u])
            b = set(knots[v]) - a
            rows.append({"case": "adjacent", **state.reads(a, b)})
            stages.append({"family": family.label, "round": stage, "knot count": len(knots),
                           "distinction count": state.domain.bit_count(), "extra loose at start": added_loose,
                           "rows": rows})
            if stage < rounds:
                knots, lineages = grow(knots, lineages)
    return stages, square


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    if args.pilot:
        stages, square = rebuild(FAMILIES[2:3], 2)
        assert len(stages) == 3 and len(square) == 6
    else:
        stages, square = rebuild(FAMILIES, 2)
        output = Path(__file__).resolve().parent
        for name, data in (("joined_results.json", stages), ("joined_square_inputs.json", square)):
            encoded = "[\n" + ",\n".join(json.dumps(row, separators=(",", ":")) for row in data) + "\n]\n"
            temporary = output / (name + ".tmp")
            temporary.write_text(encoded)
            temporary.replace(output / name)
    print(f"{len(stages)} family stages, {sum(len(stage['rows']) for stage in stages)} reader rows, "
          f"{len(square)} inputs for the signed square")


if __name__ == "__main__":
    main()
