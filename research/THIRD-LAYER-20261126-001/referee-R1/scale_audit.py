"""Replay the two readings and the scale comparison from knot supports.

Each distinction has one or two holders. Give all loose distinctions a
common extra holder. Allowed changes have even incidence everywhere and
are sums of simple cycles, including cycles of two parallel distinctions.
Only the rebuilt growth and the odd-cycle minimum are imported.
"""

import argparse
from collections import Counter, deque
from itertools import combinations, product
import json
from pathlib import Path
import resource
import time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
BUILT_REFEREE = RESEARCH / "BUILT-BINDING-20261126-001" / "referee-R1"


def read_json(path):
    return json.loads(path.read_text())


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def xor_all(masks):
    combined = 0
    for mask in masks:
        combined ^= mask
    return combined


def bit_positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Span:
    def __init__(self, masks=()):
        self.rows = {}
        self.pivots = 0
        for mask in masks:
            self.add(mask)

    def reduce(self, mask):
        while mask & self.pivots:
            pivot = (mask & self.pivots).bit_length() - 1
            mask ^= self.rows[pivot]
        return mask

    def add(self, mask):
        mask = self.reduce(mask)
        if mask:
            pivot = mask.bit_length() - 1
            self.rows[pivot] = mask
            self.pivots |= 1 << pivot

    def __contains__(self, mask):
        return self.reduce(mask) == 0

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows.values())

    def annihilator_on(self, available):
        ordered_pivots = sorted(self.rows)
        for free in bit_positions(available & ~self.pivots):
            value = 1 << free
            for pivot in ordered_pivots:
                if (self.rows[pivot] & value).bit_count() % 2:
                    value |= 1 << pivot
            yield value


class ParityState:
    def __init__(self, knots):
        self.knots = knots
        self.names = sorted({name for knot in knots for name in knot})
        self.index = {name: i for i, name in enumerate(self.names)}
        holders = [[] for _ in self.names]
        for holder, knot in enumerate(knots):
            for name in knot:
                holders[self.index[name]].append(holder)
        self.ends = []
        self.neighbours = [[] for _ in range(len(knots) + 1)]
        for i, holding in enumerate(holders):
            assert len(holding) in (1, 2)
            a = holding[0]
            b = holding[1] if len(holding) == 2 else len(knots)
            self.ends.append((a, b))
            self.neighbours[a].append((b, i))
            self.neighbours[b].append((a, i))
        self.knot_masks = [self.mask(knot) for knot in knots]
        self.laws = Span(self.knot_masks)
        self.allowed_rank = len(self.names) - len(self.laws)

    def mask(self, support):
        return xor_all(1 << self.index[name] for name in support)

    def breadth_first(self, start, *, omitted_holder=-1, omitted_distinction=-1):
        length = {start: 0}
        paths = {start: 0}
        pending = deque([start])
        while pending:
            here = pending.popleft()
            for next_holder, label in self.neighbours[here]:
                if next_holder == omitted_holder or label == omitted_distinction:
                    continue
                if next_holder not in length:
                    length[next_holder] = length[here] + 1
                    paths[next_holder] = paths[here] ^ (1 << label)
                    pending.append(next_holder)
        return length, paths

    def shortest_span(self):
        """Add one shortest return and the differences among tied returns.

        Within the shortest-path DAG, changing one prefix and keeping its
        suffix gives the difference of two full shortest changes. Every tied
        return is obtained modulo these prefix differences.
        """
        span = Span()
        for i, (a, b) in enumerate(self.ends):
            if len(span) == self.allowed_rank:
                break
            distance, path = self.breadth_first(a, omitted_distinction=i)
            if b not in distance:
                continue
            span.add(path[b] ^ (1 << i))
            pending = deque([b])
            seen = {b}
            while pending:
                here = pending.popleft()
                for prior, label in self.neighbours[here]:
                    if label == i or distance.get(prior, -2) != distance[here] - 1:
                        continue
                    span.add(path[here] ^ path[prior] ^ (1 << label))
                    if prior not in seen:
                        seen.add(prior)
                        pending.append(prior)
        return span

    def small_span(self, limit):
        """Enumerate bounded simple cycles from their least holder."""
        span = Span()

        def visit(root, current, seen, used, count):
            if len(span) == self.allowed_rank:
                return
            for next_holder, label in self.neighbours[current]:
                choice = 1 << label
                if choice & used:
                    continue
                if count and next_holder == root:
                    span.add(used | choice)
                elif next_holder > root and next_holder not in seen and count + 1 < limit:
                    visit(root, next_holder, seen | {next_holder}, used | choice, count + 1)

        for start in range(len(self.neighbours)):
            visit(start, start, {start}, 0, 0)
        return span

    def local_pair_minima(self):
        """Find the least allowed cycle using both distinctions at one knot.

        Such a cycle consists of the chosen pair and a shortest return
        between their other holders avoiding the knot. Every change odd on
        a knot's support has an odd simple cycle, which uses a pair with
        exactly one distinction in the support.
        """
        profile = []
        for knot, adjacent in enumerate(self.neighbours[:-1]):
            distances = {other: self.breadth_first(other, omitted_holder=knot)[0]
                         for other in {holder for holder, _ in adjacent}}
            profile.append([(distances[a][b] + 2, i, j)
                            for (a, i), (b, j) in combinations(adjacent, 2)
                            if b in distances[a]])
        return profile

    @staticmethod
    def knot_groups(mask, pairs, limit=None):
        """A support is invariant exactly when it is constant on each group."""
        group_of = {i: 1 << i for i in bit_positions(mask)}
        for length, i, j in pairs:
            if limit is None or length <= limit:
                merged = group_of[i] | group_of[j]
                for member in bit_positions(merged):
                    group_of[member] = merged
        return sorted(set(group_of.values()))

    def reading_of_moves(self, moves):
        knot_bases = []
        occurrences = 0
        for mask in self.knot_masks:
            projected = Span(move & mask for move in moves)
            raw_basis = list(projected.annihilator_on(mask))
            reduced = Span(self.laws.reduce(f) for f in raw_basis)
            occurrences += (1 << len(raw_basis)) - (1 << (len(raw_basis) - len(reduced)))
            knot_bases.append(reduced)
        return Reading(self, knot_bases, occurrences,
                       lambda f: all((v & f).bit_count() % 2 == 0 for v in moves),
                       self.allowed_rank - len(moves))

    def reading_at_scale(self, scale, profile, fixed_group_counts, least):
        knot_bases = []
        occurrences = 0
        for mask, pairs, fixed_count in zip(self.knot_masks, profile, fixed_group_counts, strict=True):
            groups = self.knot_groups(mask, pairs, scale)
            reduced = Span(self.laws.reduce(group) for group in groups)
            assert len(reduced) == len(groups) - fixed_count
            occurrences += (1 << len(groups)) - (1 << fixed_count)
            knot_bases.append(reduced)
        return Reading(self, knot_bases, occurrences,
                       lambda f: least[f] is not None and least[f] > scale)


class Reading:
    def __init__(self, state, knot_bases, occurrences, keep, fact_rank=None):
        self.state = state
        self.knot_bases = knot_bases
        self.occurrences = occurrences
        self.keep = keep
        self.fact_rank = fact_rank
        self.local = Span(value for basis in knot_bases for value in basis)

    def flags(self, supports):
        result = []
        for support in supports:
            value = self.state.mask(support)
            reduced = self.state.laws.reduce(value)
            result.append({
                "class fact": bool(reduced) and self.keep(value),
                "read by one knot": any(reduced in knot for knot in self.knot_bases),
                "a sum of single-knot facts": reduced in self.local,
            })
        return result

    def ranks(self, supports):
        reduced = [self.state.laws.reduce(self.state.mask(s)) for s in supports]
        support_rank = len(Span(reduced))
        return {
            "support rank": support_rank,
            "one parity rule": len(reduced) >= 3 and support_rank == len(reduced) - 1
                               and not xor_all(reduced),
            "support rank modulo single-knot facts": len(Span(self.local.reduce(v) for v in reduced)),
            "single-knot facts counting supports by knot": self.occurrences,
            "single-knot facts rank": len(self.local),
            "knots reading class facts": sum(bool(len(basis)) for basis in self.knot_bases),
            "all class facts rank": self.fact_rank,
        }


def literal_controls():
    fixtures = (
        ((0, 1, 2), (0, 1, 3), (2, 3, 4), (4, 5, 6)),
        ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)),
        ((0, 1, 2), (0, 1, 3), (4, 5, 6), (4, 5, 7)),
    )
    for knots in fixtures:
        state = ParityState(knots)
        changes = sorted((z for z in range(1, 1 << len(state.names))
                          if all((z & row).bit_count() % 2 == 0 for row in state.knot_masks)),
                         key=int.bit_count)
        through = [[z for z in changes if z & (1 << i)] for i in range(len(state.names))]
        shortest = [z for options in through if options for z in options
                    if z.bit_count() == options[0].bit_count()]
        expected_short = Span(shortest)
        actual_short = state.shortest_span()
        assert len(actual_short) == len(expected_short)
        assert all(z in actual_short for z in shortest)
        profile = state.local_pair_minima()
        for knot, pairs in zip(knots, profile, strict=True):
            for count in range(len(knot) + 1):
                for support in combinations(knot, count):
                    value = state.mask(support)
                    actual = min((n for n, i, j in pairs
                                  if ((value >> i) ^ (value >> j)) & 1), default=None)
                    expected = next((z.bit_count() for z in changes if (value & z).bit_count() % 2), None)
                    assert actual == expected
        for scale in range(2, 6):
            small = [z for z in changes if z.bit_count() <= scale]
            actual_small = state.small_span(scale)
            assert len(actual_small) == len(Span(small)) and all(z in actual_small for z in small)
            fixed = [len(state.knot_groups(mask, pairs))
                     for mask, pairs in zip(state.knot_masks, profile, strict=True)]
            local_by_pairs = state.reading_at_scale(scale, profile, fixed, {})
            local_by_moves = state.reading_of_moves(actual_small)
            assert local_by_pairs.occurrences == local_by_moves.occurrences
            assert len(local_by_pairs.local) == len(local_by_moves.local)
            assert all(v in local_by_moves.local for v in local_by_pairs.local)
    return len(fixtures)


def ordinary_stages(start, rounds):
    import growth

    state = start
    yield 0, state, ()
    for round_index in range(1, rounds + 1):
        state, status, births = growth.grow(state)
        if status != "funded":
            break
        yield round_index, state, births


def built_roster():
    for number, size, attachment, link in product((3, 4), range(4, 8), ("split", "paired"), ("double", "detour")):
        yield f"{number} rings of {size}, {attachment}, {link}", number, size, attachment, link


def connecting_attachments(start, rings):
    ring_knots = {knot for ring in rings for knot in ring}
    groups = []
    for ring in rings:
        ring_names = {name for knot in ring for name in start[knot]}
        group = []
        for i, knot in enumerate(start):
            if i not in ring_knots:
                support = sorted(ring_names.intersection(knot))
                if support:
                    assert len(support) == 2
                    group.append((i, support))
        assert len(group) == len(rings) - 1
        groups.append(group)
    return groups


def attachment_witnesses(state, readings, supports, groups):
    summary = {tag: [] for tag in readings}
    for support, attachment in zip(supports, groups, strict=True):
        knot_supports = [s for _, s in attachment]
        discrepancy = xor_all(state.mask(s) for s in [support, *knot_supports])
        assert discrepancy in state.laws, (support, attachment)
        for tag, reader in readings.items():
            flags = reader.flags(knot_supports)
            assert all(f["read by one knot"] and f["a sum of single-knot facts"] for f in flags
                       if f["class fact"])
            summary[tag].append(all(f["class fact"] for f in flags))
    return summary


def carrier_summary(readings, supports):
    return {reading: {"facts": reader.flags(supports), **reader.ranks(supports)}
            for reading, reader in readings.items()}


def read_two(state):
    return {"SHORT": state.reading_of_moves(state.shortest_span()),
            "UPTO5": state.reading_of_moves(state.small_span(5))}


def replay_exploratory(pilot):
    import growth

    reference = {(row["start"], row["round"], row["carriers"]): row
                 for row in read_rows(STUDY / "jointly_explore.jsonl")}
    found = {}
    omitted = []
    baseline = []

    def add(start, when, kind, state, readings, supports, attachments=None):
        key = (start, when, kind)
        assert key not in found and key in reference, key
        numbers = carrier_summary(readings, supports)
        assert all(numbers[tag]["facts"] == reference[key][tag] for tag in numbers), (key, numbers)
        found[key] = {"start": start, "round": when, "carriers": kind,
                      "distinctions": len(state.names), "supports": supports, **numbers}
        if attachments is not None:
            found[key]["attachment sums of class facts"] = attachment_witnesses(state, readings, supports, attachments)

    start, carriers = growth.fourteen_start()
    if not pilot:
        for when, knots, _ in ordinary_stages(start, 3):
            state = ParityState(knots)
            add("the 14-knot start", when, "ring parities", state, read_two(state), carriers)

    for idx, (label, number, size, attachment, link) in enumerate(built_roster()):
        if pilot and idx not in (0, 6, 9, 25):
            continue
        start, rings, loose = growth.ring_start(number, size, attachment, link)
        attachments = connecting_attachments(start, rings)
        lineage = {knot: group for group, ring in enumerate(rings) for knot in ring}
        previous = {}
        for when, knots, births in ordinary_stages(start, 3):
            state = ParityState(knots)
            if not when:
                readings = read_two(state)
                baseline.append({"start": label, "supports": loose, **carrier_summary(readings, loose),
                                 "connecting knot attachment supports": attachments,
                                 "attachment sums of class facts": attachment_witnesses(state, readings, loose, attachments)})
                continue
            if len(state.names) > 400:
                omitted.append([label, when, len(state.names)])
                break
            born = {}
            for birth in births:
                parents = {lineage.get(p) for p in birth["parents"]}
                if len(parents) == 1 and None not in parents:
                    group = parents.pop()
                    born.setdefault(group, []).extend(birth["fresh"])
                    lineage[birth["knot"]] = group
            readings = read_two(state)
            add(label, when, "start groups", state, readings, loose, attachments)
            if len(previous) == len(rings):
                add(label, when, "new", state, readings, [previous[r] for r in range(len(rings))], attachments)
            previous = born

    path = read_json(RESEARCH / "BINDING-20261126-001" / "referee-R1" / "path_certificate.json")
    path_source = read_json(RESEARCH / "LAYERS-20261126-001" / "referee-R1" / "extended_witness.json")[0]
    assert path_source["sample index"] == path["source"]
    _, path_state, _ = list(ordinary_stages(tuple(map(tuple, path_source["start supports"])), 3))[-1]
    assert path_state == tuple(map(tuple, path["grown_knots"]))
    state = ParityState(path_state)
    add("the ten-knot path witness", 3, "paths", state, read_two(state), path["path_supports"])

    heldout = read_json(BUILT_REFEREE / "heldout_certificate.json")
    source = read_json(BUILT_REFEREE / "unrestricted_heldout.json")["examples"]["at most five"][0]
    assert source["round"] == 2
    state = ParityState(tuple(map(tuple, source["knots"])))
    readings = read_two(state)
    add("the held-out eight-knot witness", 2, "start readers", state, readings, heldout["carriers"])
    add("the held-out eight-knot witness", 2, "new readers", state, readings, heldout["new_distinction_carriers"])
    if not pilot:
        assert found.keys() == reference.keys()
    return list(found.values()), omitted, baseline


def replay_examples(pilot):
    import growth

    reference = {(row["file"], row["found under"], row["start"], row["round"]): row
                 for row in read_rows(STUDY / "jointly_examples.jsonl")}
    found = {}
    for group in ("heldout", "sampled"):
        filename = f"unrestricted_{group}.json"
        source_examples = read_json(BUILT_REFEREE / filename)["examples"]
        if pilot:
            source_examples = {reading: rows[:1] for reading, rows in source_examples.items()}
        largest_round = {}
        for rows in source_examples.values():
            for row in rows:
                name, when = row["start"], row["round"]
                largest_round[name] = max(largest_round.get(name, 0), when)
        rebuilt = {}
        for name, start in growth.load_starts(group):
            if name in largest_round:
                rebuilt[name] = {t: knots for t, knots, _ in ordinary_stages(start, largest_round[name])}
                if len(rebuilt) == len(largest_round):
                    break
        for original_reading, source_rows in source_examples.items():
            for source in source_rows:
                key = (filename, original_reading, source["start"], source["round"])
                assert key not in found
                knots = tuple(map(tuple, source["knots"]))
                assert knots == rebuilt[source["start"]][source["round"]], key
                state = ParityState(knots)
                readings = read_two(state)
                kinds = {"supports": source["supports"]}
                if "new distinctions only" in source:
                    kinds["new"] = source["new distinctions only"]
                record = {"file": filename, "found under": original_reading, "start": source["start"],
                          "round": source["round"], "distinctions": len(state.names)}
                for kind, supports in kinds.items():
                    assert not any(set(a).intersection(b) for a, b in combinations(supports, 2))
                    support_reads = carrier_summary(readings, supports)
                    assert all(support_reads[tag]["facts"] == reference[key][kind][tag]
                               for tag in support_reads), (key, kind, support_reads)
                    record[kind] = {"exact supports": supports, **support_reads}
                if "new" in kinds:
                    residues = [sorted(state.laws.reduce(state.mask(s)) for s in supports)
                                for supports in kinds.values()]
                    record["new supports give the same class facts"] = residues[0] == residues[1]
                found[key] = record
    if not pilot:
        assert found.keys() == reference.keys()
    return list(found.values())


def stress_stage(knots, supports, ring_supports, attachments, last_scale=5):
    from minima import Incidence

    state = ParityState(knots)
    incidence = Incidence(knots)
    assert state.index == incidence.index
    profiles = state.local_pair_minima()
    fixed = [len(state.knot_groups(mask, pairs))
             for mask, pairs in zip(state.knot_masks, profiles, strict=True)]
    least = {state.mask(support): incidence.least(support) for support in supports + ring_supports}
    family_least = [least[state.mask(support)] for support in supports]
    assert all(n is not None for n in family_least)
    attachment_least = []
    for knot, support in attachments:
        mask = state.mask(support)
        flip = min((length for length, i, j in profiles[knot]
                    if ((mask >> i) ^ (mask >> j)) & 1), default=None)
        assert flip == incidence.least(support)
        attachment_least.append({"knot": knot, "support": support, "least flip": flip})
    window = min(family_least) - 1
    ring_least = [least[state.mask(s)] for s in ring_supports]
    by_scale = {}
    last_scale = max([last_scale, *(n for n in family_least + ring_least if n is not None)])
    for scale in range(2, last_scale + 1):
        reader = state.reading_at_scale(scale, profiles, fixed, least)
        by_scale[scale] = {"facts": reader.flags(supports), "ring facts": reader.flags(ring_supports),
                           "ring support rank modulo single-knot facts":
                               reader.ranks(ring_supports)["support rank modulo single-knot facts"],
                           **reader.ranks(supports)}
    short = state.reading_of_moves(state.shortest_span())
    direct_five = state.reading_of_moves(state.small_span(5))
    assert direct_five.flags(supports) == by_scale[5]["facts"]
    assert direct_five.flags(ring_supports) == by_scale[5]["ring facts"]
    assert direct_five.occurrences == by_scale[5]["single-knot facts counting supports by knot"]
    assert len(direct_five.local) == by_scale[5]["single-knot facts rank"]
    return {"knots": len(knots), "distinctions": len(state.names), "family supports": supports,
            "ring supports": ring_supports, "least flips": family_least,
            "ring least flips": ring_least,
            "connecting knot attachment parities": attachment_least,
            "one-below-minimum scale": window,
            "shortest": {"facts": short.flags(supports), "ring facts": short.flags(ring_supports),
                         **short.ranks(supports)},
            "by scale": by_scale}


def replay_large_scale(pilot):
    import growth

    reference = {row["family"]: row for row in read_rows(STUDY / "frozen_scale_read.jsonl")}
    cases = []
    for idx, (label, number, size, attachment, link) in enumerate(built_roster()):
        if number != 3 or (pilot and idx not in (0, 6, 9)):
            continue
        start, rings, ring_supports = growth.ring_start(number, size, attachment, link)
        _, supports = growth.families(start)
        supports = list(supports)
        ring_supports = list(ring_supports)
        attachments = [pair for group in connecting_attachments(start, rings) for pair in group]
        end = 4 if size == 6 or attachment == "split" else 6
        for when, knots, _ in ordinary_stages(start, end):
            if when < 4:
                continue
            stage = stress_stage(knots, supports, ring_supports, attachments)
            stage.update({"start": label, "round": when})
            if when == 4:
                archival = reference[label]
                stage["in archived read"] = "end" not in archival
                if "end" in archival:
                    assert archival["end"] == f"not read: {stage['distinctions']} distinctions", stage
                else:
                    scale = stage["one-below-minimum scale"]
                    reading = stage["by scale"][scale]
                    flags = [{"class fact at k": f["class fact"],
                              "held by no part at k": not f["a sum of single-knot facts"]}
                             for f in reading["facts"]]
                    assert archival["families"] == len(supports)
                    assert archival["least flips"] == stage["least flips"] and archival["scale"] == scale
                    assert archival["single-knot facts at k"] == reading["single-knot facts counting supports by knot"]
                    assert archival["facts"] == flags, (label, flags)
            cases.append(stage)
    if not pilot:
        assert {case["start"] for case in cases if case["round"] == 4} == reference.keys()
    return cases


def exploratory_scale_trace():
    import growth

    start, rings, ring_supports = growth.ring_start(3, 5, "split", "double")
    _, supports = growth.families(start)
    attachments = [pair for group in connecting_attachments(start, rings) for pair in group]
    trace = []
    for when, knots, _ in ordinary_stages(start, 4):
        stage = stress_stage(knots, list(supports), list(ring_supports), attachments, last_scale=12)
        trace.append({"round": when, "distinctions": stage["distinctions"], "least flips": stage["least flips"],
                      "connecting knot attachment parities": stage["connecting knot attachment parities"],
                      "scale 5": stage["by scale"][5], "scale 12": stage["by scale"][12]})
    return trace


def count_readings(panels):
    tallies = Counter()
    for supports_read in panels:
        flags = supports_read["facts"]
        tallies["carrier sets"] += 1
        tallies["carrier sets with one parity rule"] += supports_read["one parity rule"]
        for f in flags:
            tallies["tested supports"] += 1
            if f["class fact"]:
                tallies["class facts"] += 1
                tallies["class facts read by one knot"] += f["read by one knot"]
                tallies["class facts in joint span"] += f["a sum of single-knot facts"]
                tallies["class facts outside joint span"] += not f["a sum of single-knot facts"]
        if supports_read["one parity rule"] and all(f["class fact"] for f in flags):
            tallies["bindings of class facts"] += 1
            tallies["bindings with all facts outside joint span"] += all(
                not f["a sum of single-knot facts"] for f in flags)
    return dict(tallies)


def summarize(exploratory, examples, scale, baseline):
    descriptions = sorted({row["carriers"] for row in exploratory})
    summary_exploratory = {kind: {tag: count_readings(row[tag] for row in exploratory if row["carriers"] == kind)
                                  for tag in ("SHORT", "UPTO5")} for kind in descriptions}
    summary_examples = {}
    for source_reading, tag in (("shortest", "SHORT"), ("at most five", "UPTO5")):
        selected = [row for row in examples if row["found under"] == source_reading]
        summary_examples[source_reading] = {
            "in discovered reading": count_readings(row["supports"][tag] for row in selected),
            "in discovered reading, new distinctions only": count_readings(row["new"][tag]
                                                                           for row in selected if "new" in row),
            "by source file": dict(Counter(row["file"] for row in selected)),
            "distinct starts": len({row["start"] for row in selected}),
        }
    summary_examples["cross-reading"] = {kind: {tag: count_readings(row[kind][tag] for row in examples if kind in row)
                                                  for tag in ("SHORT", "UPTO5")} for kind in ("supports", "new")}
    summary_examples["new supports giving the same class facts"] = sum(
        row.get("new supports give the same class facts", False) for row in examples)
    summary_scale = {}
    for title, selected in (
        ("round 4, in archived read", [r for r in scale if r.get("in archived read")]),
        ("round 4, exceeded archived cap", [r for r in scale if r.get("in archived read") is False]),
        ("round 5, paired attachments", [r for r in scale if r["round"] == 5]),
        ("round 6, paired attachments", [r for r in scale if r["round"] == 6]),
    ):
        summary_scale[title] = {"one below minimum flip": count_readings(
            r["by scale"][r["one-below-minimum scale"]] for r in selected),
                               "shortest": count_readings(r["shortest"] for r in selected),
                               "by named start": [r["start"] for r in selected]}
    summary_attachment = {}
    for label, selected in (
        ("round 0 ring parities", baseline),
        ("archived ring parities", [r for r in exploratory if r["carriers"] == "start groups"]),
        ("archived new carriers", [r for r in exploratory if r["carriers"] == "new"]),
    ):
        summary_attachment[label] = {tag: {"counts": count_readings(r[tag] for r in selected),
                                          "explicit attachment sums of class facts":
                                              sum(sum(r["attachment sums of class facts"][tag]) for r in selected)}
                                     for tag in ("SHORT", "UPTO5")}
    return {"exploratory": summary_exploratory, "examples": summary_examples, "scale": summary_scale,
            "assignment to connecting knots": summary_attachment}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    start = time.perf_counter()
    controls = literal_controls()
    timings = {}
    before = time.perf_counter()
    exploratory, omitted_exploratory, baseline = replay_exploratory(args.pilot)
    timings["exploratory"] = round(time.perf_counter() - before, 3)
    before = time.perf_counter()
    examples = replay_examples(args.pilot)
    timings["examples"] = round(time.perf_counter() - before, 3)
    before = time.perf_counter()
    scale = replay_large_scale(args.pilot)
    trace = exploratory_scale_trace()
    timings["scale"] = round(time.perf_counter() - before, 3)
    summary = summarize(exploratory, examples, scale, baseline)
    envelope = {"pilot": args.pilot, "literal controls": controls,
                "wall seconds": round(time.perf_counter() - start, 3),
                "wall seconds by panel": timings,
                "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "workers": 1, "address space limit GiB": 2,
                "exploratory rows": len(exploratory), "example rows": len(examples), "start rows": len(baseline),
                "scale rows": len(scale), "exploratory scale rounds": len(trace)}
    print(json.dumps(envelope, sort_keys=True), flush=True)
    if args.output is not None:
        result = {"run": envelope, "summary": summary, "exploratory rows": exploratory,
                  "exploratory states excluded by the recorded 400 cap": omitted_exploratory,
                  "example rows": examples, "large-scale rows": scale, "built start rows": baseline,
                  "exploratory three rings of five, split, double scale trace": trace}
        args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
