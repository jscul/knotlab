"""Independent physical holdings, projections and paid rosters for B259."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import gzip
import io
import json
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURES = ROOT / ("experiments/GENERATORS-20261120-001A/"
                   "GENERATORS-20261120-001A-E001_generators/fixtures.py")
PREREGISTRATION = ROOT / "research" / HERE.parent.name / "preregistration.md"
ARCHIVED_FRAME = ROOT / "research/GENERATORS-20261120-001/meeting.md"
ARCHIVED_RECEIVER = ROOT / "research/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/receiver_proof.md"
END_OPERATOR = ROOT / ("experiments/ORDINARY-DYNAMICS-20261120-001A/"
                       "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py")
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
BASELINE_ARCS = (("v", "r1"), ("r1", "r2"), ("r2", "r3"), ("r3", "v"),
                 ("v", "s"), ("t", "v"), ("s", "b0"), ("t", "b0"), ("s", "b1"),
                 ("b1", "t"), ("t", "b2"), ("b2", "s"))
CAP = 8192
PREFIX_LIMIT = 256
HORIZON = 2
LAWS = ("parity", "nae")
PRIMARY_D = 32
COMMON_LENGTH = 46
REFERENCE_SWITCH = 23
C_SWITCH = 48
SWITCH_MULTIPLICITY = 4
RENAME_SEEDS = (20261120959, 20261120989)


@cache
def fixture():
    spec = spec_from_file_location("b259_physical_fixtures", FIXTURES)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class Preparation:
    stars: list[list[int]]
    role_id: dict[str, int]
    arc_witness: dict[tuple[str, str], int]
    new_name: int = 0

    def holder(self, label):
        if label not in self.role_id:
            self.role_id[label] = len(self.stars)
            self.stars.append([])
        return self.role_id[label]

    def new_distinction(self, *holders):
        for holder in holders:
            self.stars[holder].append(self.new_name)
        self.new_name += 1

    def candidate_pair(self, tail, head, doubled=2):
        a, b = self.holder(tail), self.holder(head)
        assert a != b and (tail, head) not in self.arc_witness and (head, tail) not in self.arc_witness
        witness = self.holder(f"witness {tail} → {head}")
        self.arc_witness[tail, head] = witness
        self.new_distinction(a, witness)
        for _ in range(doubled):
            self.new_distinction(b, witness)
        self.new_distinction(a)
        self.new_distinction(b)

    def passage(self, labels, switch=None):
        for a, b in zip(labels, labels[1:]):
            self.candidate_pair(a, b, doubled=SWITCH_MULTIPLICITY if a == switch else 2)

    def switch_witness_heads(self, first, second):
        """Exchange only the name sets at the heads of the two existing witnesses."""
        fw, sw = self.arc_witness.pop(first), self.arc_witness.pop(second)
        left_names = sorted(set(self.stars[fw]) & set(self.stars[self.role_id[first[1]]]))
        right_names = sorted(set(self.stars[sw]) & set(self.stars[self.role_id[second[1]]]))
        assert len(left_names) == len(right_names) == SWITCH_MULTIPLICITY
        for witness, donor, receiver, new_names in [(fw, first, second, right_names), (sw, second, first, left_names)]:
            old_names = set(self.stars[self.role_id[donor[1]]])
            self.stars[witness] = [d for d in self.stars[witness] if d not in old_names] + new_names
            self.role_id.pop(f"witness {donor[0]} → {donor[1]}")
            replacement = (donor[0], receiver[1])
            self.arc_witness[replacement] = witness
            self.role_id[f"witness {replacement[0]} → {replacement[1]}"] = witness

    def immutable(self):
        return tuple(tuple(row) for row in self.stars)


def closed_frame(zone):
    return tuple((f"{zone}.{a}", f"{zone}.{b}", 3 if zone == "R" and (a, b) == ("t", "b2") else 2)
                 for a, b in BASELINE_ARCS)


def frame_holders(prepared, zone):
    arcs = closed_frame(zone)
    live = {prepared.role_id[v] for a, b, _ in arcs for v in (a, b)}
    spent = {prepared.arc_witness[a, b] for a, b, _ in arcs}
    assert len(live) == 9 and len(spent) == 12
    return live | spent


def build(kind, d=PRIMARY_D):
    p = Preparation([], {}, {})
    for tag in ("R", "S"):
        for tail, head, multiplicity in closed_frame(tag):
            p.candidate_pair(tail, head, multiplicity)
    p.candidate_pair("R.r1", "S.b2")
    p.candidate_pair("R.b2", "a")
    p.candidate_pair("b", "S.b2")
    p.passage(["a", *(f"p{i}" for i in range(1, COMMON_LENGTH)), "b"], switch=f"p{REFERENCE_SWITCH}")
    common = p.immutable()
    if kind == "absent":
        return p, common
    p.candidate_pair("a", "c0", doubled=3)
    if kind == "inert_short":
        p.passage([f"c{i}" for i in range(d + 1)])
        p.candidate_pair(f"c{d}", "b")
    elif kind in ("active", "active_sham", "rewired"):
        switch = f"c{C_SWITCH}" if 2 * d > C_SWITCH else None
        p.passage([*(f"c{i}" for i in range(2 * d + 1)), "c0"], switch=switch)
        if kind in ("active", "rewired"):
            p.candidate_pair(f"c{d}", "b")
        if kind == "rewired":
            first = (f"c{C_SWITCH}", f"c{C_SWITCH + 1}")
            second = (f"p{REFERENCE_SWITCH}", f"p{REFERENCE_SWITCH + 1}")
            p.switch_witness_heads(first, second)
    else:
        raise ValueError(kind)
    return p, common


@dataclass
class PhysicalReading:
    arrows: nx.DiGraph
    witness: dict[tuple[int, int], int]
    opens: dict[int, list[int]]


def read_physical(stars):
    f = fixture()
    owners, ordinary, loose = f.incidence(stars)
    pairs = Counter(tuple(sorted(hs)) for hs in owners.values() if len(hs) == 2)
    assert nx.is_connected(ordinary)
    arrows = nx.DiGraph()
    arrows.add_nodes_from(loose)
    witness = {}
    for w in set(ordinary) - loose.keys():
        assert len(ordinary[w]) == 2 and set(ordinary[w]) <= loose.keys()
        tail, head = sorted(ordinary[w], key=lambda v: pairs[tuple(sorted((v, w)))])
        ta, he = (pairs[tuple(sorted((v, w)))] for v in (tail, head))
        assert ta == 1 and he in (2, 3, SWITCH_MULTIPLICITY)
        assert not arrows.has_edge(tail, head) and not arrows.has_edge(head, tail)
        arrows.add_edge(tail, head, multiplicity=he)
        witness[tail, head] = w
    for v, openings in loose.items():
        assert len(openings) == arrows.degree(v)
        assert set(ordinary[v]).isdisjoint(loose.keys())
        assert sum(pairs[tuple(sorted((v, w)))] > 1 for w in ordinary[v]) >= 1
    ordinary_candidates = arrows.to_undirected()
    assert nx.is_connected(ordinary_candidates)
    assert min(dict(ordinary_candidates.degree).values()) >= 2
    assert sum(nx.triangles(ordinary_candidates).values()) == 0
    _, measured = f.witnessed_end(ordinary, loose)
    assert set(map(frozenset, measured.edges)) == set(map(frozenset, ordinary_candidates.edges))
    assert len(witness) == len(stars) - len(loose)
    return PhysicalReading(arrows, witness, loose)


def decode_frames(reading):
    result = {}
    for tag in ("R", "S"):
        pattern = nx.DiGraph()
        for a, b, multiple in closed_frame(tag):
            pattern.add_edge(a, b, multiplicity=multiple)
        compare = nx.algorithms.isomorphism.DiGraphMatcher(
            reading.arrows, pattern, edge_match=nx.algorithms.isomorphism.categorical_edge_match("multiplicity", 0))
        all_matches = [{v: k for k, v in m.items()} for m in compare.subgraph_isomorphisms_iter()]
        assert len(all_matches) == 1, (tag, all_matches)
        result.update(all_matches[0])
    assert len(set(result.values())) == 18
    return result


def stable_origins(stars, reading, role_map):
    originals = set(role_map.values())
    for tag in ("R", "S"):
        for a, b, _ in closed_frame(tag):
            originals.add(reading.witness[role_map[a], role_map[b]])
    return {h: (stars[h], tuple(reading.opens.get(h, ()))) for h in sorted(originals)}


def rooted_line(start, next_roles):
    """Walk a nonbranching directed chain from its identifiable first role."""
    sequence = [start]
    seen = {start}
    while successors := tuple(next_roles(sequence[-1])):
        end, = successors
        if end in seen:
            assert end == start
            return sequence, True
        sequence.append(end)
        seen.add(end)
    return sequence, False


def decode_connectors(reading, frame_roles):
    """Locate the portals and paths using the observed witnesses alone."""
    arrows = reading.arrows
    old_live = set(frame_roles.values())
    a, = set(arrows.successors(frame_roles["R.b2"])) - old_live
    b, = set(arrows.predecessors(frame_roles["S.b2"])) - old_live
    middle = arrows.subgraph(set(arrows) - old_live)
    first, = (v for v in middle.successors(a) if middle[a][v]["multiplicity"] == 2)
    c_start = tuple(v for v in middle.successors(a) if middle[a][v]["multiplicity"] == 3)
    assert len(set(middle.successors(a))) == 1 + len(c_start) and len(c_start) <= 1
    marked_arcs = [(u, v) for u, v, multiple in middle.edges(data="multiplicity")
                   if multiple == SWITCH_MULTIPLICITY]
    trimmed = middle.copy()
    trimmed.remove_edges_from(marked_arcs)
    prefix, is_closed = rooted_line(first, trimmed.successors)
    assert not is_closed and len(prefix) == REFERENCE_SWITCH
    trim_no_entry = trimmed.subgraph(set(trimmed) - {a, *c_start})
    resume, = {end for _, end in marked_arcs if nx.has_path(trim_no_entry, end, b)}
    suffix, is_closed = rooted_line(resume, trimmed.successors)
    assert not is_closed and suffix[-1] == b
    reference = [a, *prefix, *suffix]
    assert len(reference) == COMMON_LENGTH + 1
    assert len(set(reference)) == len(reference)
    reference_unbroken = middle.has_edge(prefix[-1], suffix[0])
    reference_read = {"reference_roles": len(reference), "reference_pair_present": reference_unbroken}
    address = {"a": a, "b": b, **{f"p{i}": v for i, v in enumerate(reference[1:-1], 1)}}

    c = middle.subgraph(set(middle) - set(reference))
    if not c:
        assert reference_unbroken and not c_start
        return address, reference_read | {"kind": "absent"}
    start, = c_start
    assert start in c
    sequence, is_closed = rooted_line(start, c.successors)
    if is_closed:
        assert reference_unbroken
        c_order = sequence
    else:
        reverse_sequence, reverse_closed = rooted_line(start, c.predecessors)
        assert not reverse_closed
        c_order = sequence + list(reversed(reverse_sequence[1:]))
    assert set(c_order) == set(c) and len(c_order) == len(c)
    sequence = c_order
    b_exits = [i for i, v in enumerate(sequence) if arrows.has_edge(v, b)]
    if is_closed:
        assert len(b_exits) in (0, 1)
        kind = "active" if b_exits else "active_sham"
    elif not reference_unbroken:
        assert len(b_exits) == 1
        kind = "rewired"
    else:
        assert b_exits == [len(sequence) - 1]
        kind = "inert_short"
    c_labels = {v: f"c{i}" for i, v in enumerate(sequence)}
    address.update({name: v for v, name in c_labels.items()})
    pure_start = start if is_closed else next(v for v in c if not c.in_degree(v))
    pure_order, pure_closed = rooted_line(pure_start, c.successors)
    assert pure_closed == is_closed and set(pure_order) == set(c)
    return address, reference_read | {
        "kind": kind, "c_roles": len(c), "c_closed_return": is_closed, "c_exit_indices": b_exits,
        "pure_c_order": [c_labels[v] for v in pure_order],
    }


def read_addresses(reading):
    frames = decode_frames(reading)
    connectors, details = decode_connectors(reading, frames)
    live = frames | connectors
    assert set(live.values()) == set(reading.opens)
    labels = {v: k for k, v in live.items()}
    candidate_witnesses = {f"witness {labels[a]} → {labels[b]}": w for (a, b), w in reading.witness.items()}
    return live | candidate_witnesses, details


def expected_rosters(graph, previous):
    """Build first pairs and second endpoint deletions directly from original incidence."""
    if previous is None:
        words = [(u, v) for u, v in graph.edges]
        parents = [tuple(sorted(word)) for word in words]
    else:
        words = [(u, v, w) for v in graph for u, w in combinations(sorted(graph[v]), 2)]
        parents = [tuple(sorted((previous[tuple(sorted((u, v)))], previous[tuple(sorted((v, w)))])))
                   for u, v, w in words]
    fresh = [2 + sum(graph.degree(k) - 2 for k in word) for word in words]
    result = dict(zip(parents, zip(words, fresh, strict=True), strict=True))
    assert len(result) == len(words)
    return result


def certify_inputs(stars, births, law):
    f = fixture()
    owners, _, loose = f.incidence(stars)
    assert Counter(d for b in births for d in b.inputs) == Counter(d for row in loose.values() for d in row)
    new_names = [d for b in births for d in b.fresh]
    assert len(set(new_names)) == len(new_names) and not set(new_names) & owners.keys()
    with f.Minisat22() as solver:
        if law == "nae":
            for row in stars:
                f.nae_add(solver, row)
        for birth in births:
            assert all(owners[d] == [p] for d, p in zip(birth.inputs, birth.parents, strict=True))
            if law == "parity":
                rows = f.parity_words(stars, birth.inputs)
            else:
                rows = f.nae_words(solver, birth.inputs)
            assert rows == (0, 1, 2, 3)


@cache
def canonical_row_count(law, arity):
    """Check K1–K3 without computing a minimum clause width."""
    words = fixture().expected_words(law, arity)
    assert arity >= 3 and 0 < len(words) < (1 << arity)
    for i in range(arity):
        assert len({word & ~(1 << i) for word in words}) == 1 << (arity - 1)
    return len(words)


def projections(stars, age, law):
    fixture().certify_source(stars, law)
    arities = Counter(map(len, stars))
    return {"age": age, "whole_stars": len(stars), "arity_counts": sorted(arities.items()),
            "exact_allowed_rows_by_arity": [[n, canonical_row_count(law, n)] for n in sorted(arities)]}


def key(word):
    return min(tuple(word), tuple(reversed(word)))


def stage(stars, graph, previous, law, age, labels):
    f = fixture()
    expected = expected_rosters(graph, previous)
    assert 2 <= len(expected) <= PREFIX_LIMIT <= CAP
    approval = f.step(f.from_stars(stars), law, max_births=CAP)
    assert approval.status == "extend" and not approval.implied
    status, births, multi = f.literal_turn(stars, law)
    assert status == "extend" and set(multi) == expected.keys() and len(multi) == len(expected)
    assert len(births) == len(multi) and {b.parents for b in births} == expected.keys()
    certify_inputs(stars, births, law)
    by_word = {}
    ancestry = {}
    receipt = []
    for birth in births:
        word, price = expected[birth.parents]
        assert len(birth.fresh) == price and price >= 2
        by_word[key(word)] = birth.knot
        ancestry[birth.knot] = frozenset(birth.parents)
        receipt.append({"knot": birth.knot, "parents": birth.parents, "inputs": birth.inputs,
                        "fresh": birth.fresh, "fresh_count": price,
                        "original_word": [labels[k] for k in word]})
    evolved = stars + tuple(b.support for b in births)
    _, _, new_loose = f.incidence(evolved)
    assert new_loose == {b.knot: list(b.fresh) for b in births}
    assert len(by_word) == len(expected)
    return evolved, by_word, ancestry, {
        "age": age, "birth_count": len(births), "all_input_projections": [0, 1, 2, 3],
        "output_projections": projections(evolved, age, law), "roster": receipt,
    }


def window_checks(addresses, ancestry, words_by_age, details):
    """Require actual deletions for the original return words and C-only words."""
    def replay(word):
        ids = [addresses[role] for role in word]
        age = len(word) - 1
        knot = words_by_age[age - 1][key(ids)]
        if age == 1:
            parents = ids
        else:
            parents = [words_by_age[age - 2][key(parent)] for parent in (ids[:-1], ids[1:])]
        assert len(set(parents)) == 2 and ancestry[knot] == frozenset(parents)
        return {"original_word": word, "age": age, "actual_knot": knot, "actual_deletions": parents}

    archived = {}
    for tag in ("R", "S"):
        neutral = ("v", "r1", "r2", "r3")
        u0 = neutral + ("v", "s", "b0", "t")
        u1 = neutral + ("v", "s", "b1", "t")
        doubled_return = tuple(f"{tag}.{role}" for role in (*u0, *u1))
        archived[tag] = [replay((doubled_return + doubled_return)[i:i + size])
                         for size in (2, 3) for i in range(len(doubled_return))]
    archived["R_port"] = [replay(("R.b1", "R.t", "R.b2")), replay(("R.t", "R.b2", "a"))]
    c = tuple(details.get("pure_c_order", ()))
    c_words = c + c if details.get("c_closed_return") else c
    third = [replay(c_words[i:i + size]) for size in (2, 3)
             for i in range(len(c) if details.get("c_closed_return") else max(0, len(c) - size + 1))]
    return archived | {"pure_c": third}


def reconstruct(stars, n_originals, law, seed, all_parents, addresses):
    f = fixture()
    renamed, new_to_old = f.rename(stars, seed)
    recovered, parents, _, depth = f.peel(renamed, law)
    assert depth == HORIZON
    recovered_originals = sorted(recovered)
    assert {new_to_old[i] for i in recovered_originals} == set(range(n_originals))
    restored_parents = {new_to_old[k]: frozenset(new_to_old[i] for i in row) for k, row in parents.items()}
    assert restored_parents == all_parents
    origin = tuple(renamed[k] for k in recovered_originals)
    reading = read_physical(origin)
    restored_addresses, details = read_addresses(reading)
    assert {label: new_to_old[recovered_originals[i]] for label, i in restored_addresses.items()} == addresses
    return {"seed": seed, "recovered_cuts": depth, "recovered_originals": len(recovered_originals),
            "recovered_actual_parent_lists": len(parents), "recovered_original_roles": len(restored_addresses),
            "recovered_connectors": details, "recovered_original_indices_in_recoding": recovered_originals,
            "recoded_to_original_holder_index": new_to_old, "recoded_full_stars": renamed}


def standalone_reference(matched):
    standalone = Preparation([], {}, {})
    for a, b in BASELINE_ARCS:
        standalone.candidate_pair(a, b)
    isolated_stars = standalone.immutable()
    match_stars = matched.immutable()
    reading = read_physical(isolated_stars)
    assert len(isolated_stars) == 21 and len(reading.opens) == 9 and len(reading.witness) == 12
    assert len({d for row in isolated_stars for d in row}) == 60
    assert sum(map(len, reading.opens.values())) == 24
    expected = {"R.r1": 2, "R.b2": 3, "witness R.t → R.b2": 1, "S.b2": 6}
    matched_arity_changes = {}
    for tag in ("R", "S"):
        pairs = [(f"{tag}.{role}", role) for role in ("v", "r1", "r2", "r3", "s", "t", "b0", "b1", "b2")]
        pairs.extend((f"witness {tag}.{a} → {tag}.{b}", f"witness {a} → {b}") for a, b in BASELINE_ARCS)
        for labelled, old in pairs:
            difference = len(match_stars[matched.role_id[labelled]]) - len(isolated_stars[standalone.role_id[old]])
            assert difference == expected.get(labelled, 0)
            if difference:
                matched_arity_changes[labelled] = difference
    assert matched_arity_changes == expected
    return {"physical_knots": len(isolated_stars), "physical_distinctions": 60, "loose_distinctions": 24,
            "unattached_arities": {label: len(isolated_stars[i]) for label, i in standalone.role_id.items()},
            "matched_arity_increments": matched_arity_changes, "standalone_stars": isolated_stars,
            "output_projections": {law: projections(isolated_stars, 0, law) for law in LAWS}}


def local_match(case):
    """Compare actual open inputs and the new state types at the fixed old roles."""
    origins = {k for k, h in case["addresses"].items() if str(h) in case["common_original_holdings"]}
    result = {}
    for law, trajectory in case["laws"].items():
        original_roster = trajectory["stages"][0]["roster"]
        read = {(key(b["original_word"])): (tuple(b["inputs"]), b["fresh_count"])
                for b in original_roster if all(k in origins for k in b["original_word"])}
        result[law] = read, {
            key(b["original_word"]): b["fresh_count"] for b in trajectory["stages"][1]["roster"]
            if all(k in origins for k in b["original_word"])
        }
    return result


def witnessed_pairs(stars, reading, labels):
    rows = []
    for (a, b), w in reading.witness.items():
        a_names = sorted(set(stars[a]) & set(stars[w]))
        b_names = sorted(set(stars[b]) & set(stars[w]))
        rows.append({"tail": labels[a], "head": labels[b], "witness": w,
                     "tail_names": a_names, "head_names": b_names})
    return sorted(rows, key=lambda row: (row["tail"], row["head"]))


def one_case(kind, d, seeds):
    prepared, common = build(kind, d)
    stars = prepared.immutable()
    reading = read_physical(stars)
    addresses, details = read_addresses(reading)
    assert addresses == prepared.role_id and details["kind"] == kind
    frame_roles = {label: i for label, i in addresses.items() if label.startswith(("R.", "S."))}
    original_holds = stable_origins(stars, reading, frame_roles)
    assert len(original_holds) == 42
    assert set(original_holds) == frame_holders(prepared, "R") | frame_holders(prepared, "S")
    assert all(stars[i] == common[i] for i in original_holds)
    if kind != "absent":
        assert details["c_roles"] == (d + 1 if kind == "inert_short" else 2 * d + 1)
        assert details["c_exit_indices"] == ([d] if kind in ("inert_short", "active", "rewired") else [])
    assert details["reference_pair_present"] == (kind != "rewired")
    graph = reading.arrows.to_undirected()
    label_map = {i: role for role, i in addresses.items()}
    by_law = {}
    for law in LAWS:
        group = {}
        frames = stars
        previous = None
        stages = []
        words_by_age = []
        initial_projections = projections(stars, 0, law)
        for age in range(1, HORIZON + 1):
            frames, previous, new_parents, trace = stage(frames, graph, previous, law, age, label_map)
            words_by_age.append(previous)
            group.update(new_parents)
            stages.append(trace)
        by_law[law] = {
            "initial_projections": initial_projections, "stages": stages,
            "return_word_checks": window_checks(addresses, group, words_by_age, details),
            "recodings": [reconstruct(frames, len(stars), law, seed, group, addresses) for seed in seeds],
        }
    assert by_law["parity"]["return_word_checks"] == by_law["nae"]["return_word_checks"]
    assert [trace["roster"] for trace in by_law["parity"]["stages"]] == [
        trace["roster"] for trace in by_law["nae"]["stages"]
    ]
    return {
        "variant": kind, "d": d, "connectors": details, "addresses": addresses,
        "physical_originals": len(stars), "candidate_originals": len(graph),
        "candidate_pair_count": len(graph.edges),
        "candidate_pairs": sorted(tuple(sorted((label_map[a], label_map[b]))) for a, b in graph.edges),
        "witnessed_pairs": witnessed_pairs(stars, reading, label_map),
        "candidate_degrees": {label_map[i]: deg for i, deg in graph.degree()},
        "original_degree_counts": sorted(Counter(dict(graph.degree()).values()).items()),
        "portal_loose_counts": {k: len(reading.opens[addresses[k]]) for k in ("a", "b")},
        "original_distinctions": len(set(d for row in stars for d in row)),
        "common_original_holdings": {str(i): row for i, row in original_holds.items()},
        "original_stars": stars, "laws": by_law,
    }


def digest(paths):
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths}


def physical_exchange(active, rewired):
    a, b = active["original_stars"], rewired["original_stars"]
    assert len(a) == len(b)
    assert active["candidate_degrees"] == rewired["candidate_degrees"]
    assert active["original_distinctions"] == rewired["original_distinctions"]
    pa = {(record["tail"], record["head"]): record for record in active["witnessed_pairs"]}
    pb = {(record["tail"], record["head"]): record for record in rewired["witnessed_pairs"]}
    before = (f"c{C_SWITCH}", f"c{C_SWITCH + 1}"), (f"p{REFERENCE_SWITCH}", f"p{REFERENCE_SWITCH + 1}")
    after = (before[0][0], before[1][1]), (before[1][0], before[0][1])
    keep = pa.keys() & pb.keys()
    assert pa.keys() - keep == set(before) and pb.keys() - keep == set(after)
    assert all(pa[pair] == pb[pair] for pair in keep)
    changed = {h for h, (x, y) in enumerate(zip(a, b, strict=True)) if x != y}
    assert changed == {pa[pair]["witness"] for pair in before}
    assert all(ia == ib for ia, ib in zip(map(len, a), map(len, b), strict=True))
    np = fixture().incidence
    assert np(a)[2] == np(b)[2]
    for prior, post, opposite in zip(before, after, reversed(before), strict=True):
        p, q, other = pa[prior], pb[post], pa[opposite]
        assert p["witness"] == q["witness"] and p["tail_names"] == q["tail_names"]
        assert len(p["head_names"]) == SWITCH_MULTIPLICITY and other["head_names"] == q["head_names"]
    return {
        "originals_with_identical_holdings": len(a) - len(changed),
        "originals_with_identical_arity": len(a),
        "live_originals_with_identical_holdings_and_loose_names": len(active["candidate_degrees"]),
        "changed_witness_ids": sorted(changed), "removed_pairs": [pa[pair] for pair in before],
        "replacement_pairs": [pb[pair] for pair in after],
    }


def frozen_inputs():
    contract = HERE / "contract.json"
    manifest = json.loads(contract.read_text())
    paths = {PREREGISTRATION: manifest["preregistration_sha256"],
             ROOT / manifest["advisor_receipt"]: manifest["advisor_sha256"]}
    paths.update({PREREGISTRATION.with_name(name): sha for name, sha in manifest["design_bindings"].items()})
    assert all(sha256(path.read_bytes()).hexdigest() == sha for path, sha in paths.items())
    return [contract, *paths]


def build_receipt():
    frozen = frozen_inputs()
    variants = [("absent", PRIMARY_D), ("active", PRIMARY_D), ("inert_short", PRIMARY_D),
                ("active_sham", PRIMARY_D), ("rewired", PRIMARY_D)]
    variants.extend((kind, d) for d in (8, 20, 44) for kind in ("active", "inert_short"))
    physical_cases = [one_case(kind, d, tuple(seed + i for seed in RENAME_SEEDS))
                      for i, (kind, d) in enumerate(variants)]
    original_rows = physical_cases[0]["common_original_holdings"]
    reference_rosters = local_match(physical_cases[0])
    for case in physical_cases[1:]:
        assert case["common_original_holdings"] == original_rows
        assert local_match(case) == reference_rosters
    source = build("absent")[0]
    archive = standalone_reference(source)
    input_files = [Path(__file__).resolve(), FIXTURES, END_OPERATOR, ARCHIVED_FRAME, ARCHIVED_RECEIVER, *frozen]
    return {
        "scope": HERE.parent.name, "schema": "physical-v1", "literal_horizon": HORIZON, "literal_birth_cap": CAP,
        "implemented_prefix_limit": PREFIX_LIMIT,
        "laws": LAWS, "standalone_comparison": archive, "same_original_holding_count": len(original_rows),
        "same_core_roster_sizes": {law: [len(r) for r in rows] for law, rows in reference_rosters.items()},
        "active_rewired_exact_name_exchange": physical_exchange(physical_cases[1], physical_cases[4]),
        "source_digests": digest(input_files), "cases": physical_cases,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    receipt = build_receipt()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as payload:
                json.dump(receipt, payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
