"""Replay present-readable width-one clocks on physically marked bare cycles."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREREGISTRATION = ROOT / "research" / HERE.parent.name / "preregistration.md"
FIXTURE = ROOT / ("experiments/GENERATORS-20261120-001A/"
                  "GENERATORS-20261120-001A-E001_generators/fixtures.py")
LAWS = ("parity", "nae")
OBSERVE_THROUGH = 32
REPLAY_THROUGH = OBSERVE_THROUGH + 4
RENAME_SEED = 20261120524


@cache
def fixture():
    spec = spec_from_file_location("phase_clock_fixtures", FIXTURE)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def holdings(size, shared, live):
    """Two loose distinctions at each live holder and no loose at the others."""
    rows = [[] for _ in range(size)]
    distinction = 0
    for a, b, multiplicity in shared:
        for _ in range(multiplicity):
            rows[a].append(distinction)
            rows[b].append(distinction)
            distinction += 1
    for knot in live:
        rows[knot].extend((distinction, distinction + 1))
        distinction += 2
    return tuple(map(tuple, rows))


def source_cases():
    five = [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 3)]
    five_source = holdings(5, five, range(5))
    extra = max(d for row in five_source for d in row) + 1
    five_edit = tuple((*row, extra) if v in (2, 3) else row
                      for v, row in enumerate(five_source))
    six = [(0, 1, 1), (1, 2, 1), (2, 3, 1),
           (4, 0, 2), (4, 1, 1), (5, 2, 2), (5, 3, 1)]
    eight = [(4 + i, i, 3 if i == 0 else 2) for i in range(4)]
    eight.extend((4 + i, (i + 1) % 4, 1) for i in range(4))
    return {
        "five_odd": five_source,
        "five_added_sharing": five_edit,
        "four_mixed_witnesses": holdings(6, six, range(4)),
        "four_spent_witnesses": holdings(8, eight, range(4)),
    }


def identify_origin(stars):
    """Read the marked order from actual holdings, with no original names supplied."""
    f = fixture()
    owners, ordinary, loose = f.incidence(stars)
    blocks, witnessed = f.witnessed_end(ordinary, loose)
    assert all(len(ds) == 2 for ds in loose.values())
    assert all(len(ds) >= 3 for ds in stars)
    assert nx.is_connected(witnessed)
    assert all(d == 2 for _, d in witnessed.degree)
    assert len(witnessed) >= 4
    multiplicities = Counter(frozenset(vs) for vs in owners.values() if len(vs) == 2)

    if len(loose) == len(stars):
        triple, = (pair for pair, count in multiplicities.items() if count == 3)
        (start, towards), = ((v, other) for v in triple for other in ordinary[v]
                             if multiplicities[frozenset((v, other))] == 2)
        first, = set(ordinary[towards]) - {start}
        marker = "end of the tripled sharing with a doubled sharing"
    else:
        spent = set(ordinary) - loose.keys()
        if len(spent) == 2:
            choices = []
            for witness in spent:
                live_pair = set(ordinary[witness]) & loose.keys()
                for v in live_pair:
                    if (multiplicities[frozenset((witness, v))] == 2
                            and len(set(ordinary[v]) & loose.keys()) == 1):
                        other, = live_pair - {v}
                        choices.append((v, other))
            (start, first), = choices
            marker = "doubled end of the spent witness with one live neighbour there"
        else:
            witness, = (v for v in spent if len(stars[v]) == 4)
            start, = (v for v in ordinary[witness]
                      if multiplicities[frozenset((witness, v))] == 3)
            first, = set(ordinary[witness]) - {start}
            marker = "tripled end of the unique four-distinction spent witness"

    order = [start, first]
    while len(order) < len(witnessed):
        following, = set(witnessed[order[-1]]) - {order[-2]}
        assert following not in order
        order.append(following)
    assert witnessed.has_edge(order[-1], order[0])
    pairs = f.multi_groups(blocks, witnessed)
    assert {frozenset(pair) for pair in pairs} == {
        frozenset((order[i], order[(i + 1) % len(order)])) for i in range(len(order))}
    assert all(sum(v in pair for pair in pairs) == 2 for v in order)
    return tuple(order), marker


@dataclass(frozen=True)
class Readout:
    original_order: tuple[int, ...]
    marker: str
    cut: int
    words: dict[int, tuple[int, ...]]
    parents: dict[int, frozenset[int]]


def read_current(stars, law):
    """Peel the current holdings and reconstruct actual words by parent unions."""
    originals, parents, _, cut = fixture().peel(stars, law)
    original_names = sorted(originals)
    original_order, marker = identify_origin(tuple(stars[k] for k in original_names))
    order = tuple(original_names[k] for k in original_order)
    words = {v: (v,) for v in order}
    previous = order
    lookup = {roster: v for v, roster in parents.items()}
    assert len(lookup) == len(parents) == cut * len(order)
    for _ in range(cut):
        current = []
        for a, b in zip(previous, previous[1:] + previous[:1], strict=True):
            first, second = words[a], words[b]
            assert first[1:] == second[:-1]
            child = lookup[frozenset((a, b))]
            assert child not in words and child not in current
            words[child] = (*first, second[-1])
            current.append(child)
        previous = tuple(current)
    return Readout(order, marker, cut, words, parents)


@cache
def canonical_shape(law, size):
    f = fixture()
    labels = tuple(f"d{i}" for i in range(size))
    rows = frozenset(tuple(bool(word >> i & 1) for i in range(size))
                     for word in f.expected_words(law, size))
    assert f.check_knot(f.Relation(labels, rows), labels[:-1], labels[-1]).is_knot
    return size


def certify_cut(stars, law):
    fixture().certify_source(stars, law)
    return {canonical_shape(law, len(star)) for star in stars}


def phase_number(order, knot):
    return order.index(knot)


def endpoint_members(current_words, role, original_order):
    side = 0 if role == "first" else -1
    return {phase_number(original_order, word[side]): k for k, word in current_words.items()}


@dataclass(frozen=True)
class Current:
    by_phase: tuple[int, ...]
    words: dict[int, tuple[int, ...]]
    first: dict[int, int]
    last: dict[int, int]
    parents: dict[int, frozenset[int]]
    fresh: dict[int, int]
    witnessed_distances: dict[int, dict[int, int]]


def observe_current(stars, law, age, literal_parents, original_order):
    f = fixture()
    read = read_current(stars, law)
    assert read.cut == age and read.original_order == original_order
    assert read.parents == literal_parents
    renamed, new_to_old = f.rename(stars, RENAME_SEED + age)
    other = read_current(renamed, law)
    assert other.cut == read.cut and other.marker == read.marker
    assert tuple(new_to_old[k] for k in other.original_order) == read.original_order
    assert {new_to_old[v]: tuple(new_to_old[k] for k in word)
            for v, word in other.words.items()} == read.words
    assert {new_to_old[v]: frozenset(new_to_old[k] for k in parents)
            for v, parents in other.parents.items()} == literal_parents
    _, ordinary, loose = f.incidence(stars)
    _, witnessed = f.witnessed_end(ordinary, loose)
    end = f.from_stars(stars)
    words = {v: read.words[v] for v in loose}
    by_phase = tuple(sorted(words, key=lambda k: phase_number(original_order, words[k][0])))
    first = endpoint_members(words, "first", original_order)
    last = endpoint_members(words, "last", original_order)
    assert len(first) == len(last) == len(by_phase) == len(original_order)
    parents = {v: read.parents[v] for v in by_phase} if age else {}
    fresh = {v: len(loose[v]) for v in by_phase}
    assert set(fresh.values()) == {2}
    assert end.opens == fresh
    assert {frozenset(block) for block in end.blocks} == {
        frozenset(pair) for pair in zip(by_phase, by_phase[1:] + by_phase[:1], strict=True)}
    if age:
        assert all(len(row) == 2 for row in parents.values())
        assert set(map(lambda v: len(stars[v]), by_phase)) == {4}
    distances = dict(nx.all_pairs_shortest_path_length(witnessed))
    length = len(original_order)
    for i, a in enumerate(by_phase):
        for j, b in enumerate(by_phase):
            assert distances[a][b] == circular_steps(i - j, length)
    return Current(by_phase, words, first, last, parents, fresh, distances)


def materialize(source, law):
    f = fixture()
    original_order, marker = identify_origin(source)
    stars = source
    literal_parents = {}
    cuts = []
    canonical_arities = set()
    checked_projections = 0
    for age in range(REPLAY_THROUGH + 1):
        canonical_arities.update(certify_cut(stars, law))
        checked_projections += len(stars)
        cuts.append(observe_current(stars, law, age, literal_parents, original_order))
        if age < REPLAY_THROUGH:
            status, births, _ = f.literal_turn(stars, law)
            assert status == "extend" and len(births) == len(original_order)
            stars += tuple(b.support for b in births)
            literal_parents.update({b.knot: frozenset(b.parents) for b in births})
    return original_order, marker, checked_projections, sorted(canonical_arities), cuts


def circular_steps(offset, period):
    residue = offset % period
    return min(residue, period - residue)


def opposite_visits(cuts, order, fixed, marker, target):
    times = []
    opposite = -1 if fixed == "first" else 0
    for age, current in enumerate(cuts[1:OBSERVE_THROUGH + 1], 1):
        knot = getattr(current, fixed)[marker]
        if current.words[knot][opposite] == order[target]:
            times.append(age)
    return times


def timing(cuts, order):
    period = len(order)
    comparisons = []
    for side in ("first", "last"):
        for marker in range(period):
            for target in range(period):
                observed = opposite_visits(cuts, order, side, marker, target)
                offset = (target - marker) if side == "first" else (marker - target)
                first = offset % period or period
                expected = list(range(first, OBSERVE_THROUGH + 1, period))
                assert observed == expected
                comparisons.append({"fixed_end": side, "anchor_phase": marker,
                                    "target_phase": target, "first_tick": first,
                                    "tick_ages": observed})
    return comparisons


def distances_by_role(cuts, period):
    rows = []
    for fixed_a, fixed_b in (("first", "first"), ("last", "last"), ("first", "last")):
        for a in range(period):
            for b in range(period):
                observed = []
                for age, current in enumerate(cuts[:OBSERVE_THROUGH + 1]):
                    one = getattr(current, fixed_a)[a]
                    two = getattr(current, fixed_b)[b]
                    d = current.witnessed_distances[one][two]
                    shift = age if fixed_a != fixed_b else 0
                    assert d == circular_steps(b - a - shift, period)
                    observed.append(d)
                changes = sorted({later - old for old, later in zip(observed, observed[1:])})
                rows.append({"fixed_ends": (fixed_a, fixed_b), "anchor_phases": (a, b),
                             "witnessed_separations": observed, "one_cut_changes": changes})
    return rows


def children_of(current, parents):
    return {v for v, row in current.parents.items() if parents & row}


def follow(cuts, age, first):
    descendants = [{first}]
    for new_cut in cuts[age + 1:age + len(cuts[age].by_phase)]:
        descendants.append(children_of(new_cut, descendants[-1]))
    return descendants


def role_for(current, side, knot):
    roles = getattr(current, side)
    anchor, = (mark for mark, v in roles.items() if v == knot)
    return anchor


def receipt_child(current, child, sender_only, receiver_only):
    parents = current.parents[child]
    s, = parents & sender_only
    r, = parents & receiver_only
    assert s != r
    return {"child": child, "sender_branch_parent": s, "receiver_branch_parent": r,
            "fresh": current.fresh[child]}


def receipt_row(cuts, age, receiver, sender, traces):
    current = cuts[age]
    l = len(current.by_phase)
    p, q = (phase_number(current.by_phase, v) for v in (receiver, sender))
    own, incoming = traces[receiver], traces[sender]
    d = current.witnessed_distances[receiver][sender]
    meetings = []
    for h, (left, right) in enumerate(zip(own, incoming, strict=True)):
        later = cuts[age + h]
        new_d = min(later.witnessed_distances[a][b] for a in left for b in right)
        assert new_d == max(d - h, 0)
        if h == d and d:
            meetings = [receipt_child(later, v, incoming[h - 1], own[h - 1])
                        for v in sorted(left & right)]
    if d:
        assert len(meetings) == (2 if 2 * d == l else 1)

    next_cut = cuts[age + 1]
    own_children = children_of(next_cut, {receiver})
    prices = sorted(next_cut.fresh[v] for v in own_children)
    direct = own_children & children_of(next_cut, {sender}) if d else set()
    assert prices == [2, 2] and len(direct) == int(d == 1)
    registration = {}
    for side, sign in (("first", 1), ("last", -1)):
        anchor = role_for(current, side, receiver)
        strict = next(h for h, cohort in enumerate(incoming)
                      if getattr(cuts[age + h], side)[anchor] in cohort)
        assert strict == sign * (q - p) % l
        successor = getattr(next_cut, side)[anchor]
        assert receiver in next_cut.parents[successor]
        assert len(next_cut.parents[successor] - {receiver}) == 1
        event = None
        if strict:
            later = cuts[age + strict]
            child = getattr(later, side)[anchor]
            predecessor = getattr(cuts[age + strict - 1], side)[anchor]
            event = receipt_child(later, child, incoming[strict - 1], {predecessor})
            assert predecessor not in incoming[strict - 1]
        assert (successor in direct) == (strict == 1)
        registration[side] = {"strict_ancestry_delay": strict,
                              "direct_intake_into_next_member": successor in direct,
                              "first_strict_receipt": event}
    return {"launch_age": age, "receiver_phase": p, "sender_phase": q,
            "launch_knots": {"receiver": receiver, "sender": sender},
            "witnessed_separation": d, "first_inclusive_delay": d,
            "first_inclusive_births": meetings,
            "direct_intake_children": sorted(direct),
            "receiver_own_child_prices": prices,
            "strict_by_receiver_end": registration}


def reception(cuts, order):
    receipts = []
    sample = {}
    period = len(order)
    for age, current in enumerate(cuts[:OBSERVE_THROUGH + 1]):
        traces = {v: follow(cuts, age, v) for v in current.by_phase}
        for p, receiver in enumerate(current.by_phase):
            for q, sender in enumerate(current.by_phase):
                row = receipt_row(cuts, age, receiver, sender, traces)
                receipts.append(row)
                sample[age, p, q] = row
    examples = []
    for sender in (1, period - 1):
        ages = opposite_visits(cuts, order, "first", sender, sender)
        selected = [sample[age, 0, sender] for age in ages]
        inclusive = [age + row["first_inclusive_delay"] for age, row in zip(ages, selected)]
        strict = [age + row["strict_by_receiver_end"]["first"]["strict_ancestry_delay"]
                  for age, row in zip(ages, selected)]
        assert inclusive == [age + 1 for age in ages]
        assert strict == [age + sender for age in ages]
        examples.append({"sender_anchor": sender, "receiver_first_anchor": 0,
                         "send_ages": ages, "first_inclusive_ages": inclusive,
                         "first_strict_ages": strict})
    return receipts, examples


def case_result(source, law):
    order, marker, projections, arities, cuts = materialize(source, law)
    receipts, timed_receipts = reception(cuts, order)
    return {
        "original_witnessed_order": order,
        "physical_marker": marker,
        "per_cut_projection_checks_counting_repeated_stars": projections,
        "canonical_projected_arities": arities,
        "literal_cuts": [
            {"age_from_current_holdings": age,
             "knots_by_first_endpoint_phase": c.by_phase,
             "opposite_endpoint_phases": [order.index(c.words[v][-1]) for v in c.by_phase],
             "actual_parents_by_first_endpoint_phase": [sorted(c.parents.get(v, ())) for v in c.by_phase],
             "loose_counts_by_first_endpoint_phase": [c.fresh[v] for v in c.by_phase]}
            for age, c in enumerate(cuts)],
        "all_first_and_last_clock_roles": timing(cuts, order),
        "all_current_pair_roles": distances_by_role(cuts, len(order)),
        "receipts": receipts,
        "two_actual_ticking_sender_examples": timed_receipts,
        "peeling_parentage_and_role_recognition_under_independent_renaming": True,
        "anonymous_witnessed_ends_have_one_cycle_and_constant_loose_counts": True,
    }


def run():
    cases = {}
    for name, source in source_cases().items():
        results = {law: case_result(source, law) for law in LAWS}
        a, b = results.values()
        assert {k: v for k, v in a.items() if k != "canonical_projected_arities"} == {
            k: v for k, v in b.items() if k != "canonical_projected_arities"}
        cases[name] = {"original_supports": source,
                       "original_distinction_count": len({d for row in source for d in row}),
                       "by_law": results}
    base = cases["five_odd"]["by_law"]["parity"]
    edited = cases["five_added_sharing"]["by_law"]["parity"]
    for key in ("literal_cuts", "all_first_and_last_clock_roles", "all_current_pair_roles",
                "receipts", "two_actual_ticking_sender_examples"):
        assert base[key] == edited[key]
    sources = Path(__file__).resolve(), FIXTURE, HERE / "contract.json", PREREGISTRATION
    return {"scope": "deterministic bare cycles with physically recognized phase order",
            "last_launch_age": OBSERVE_THROUGH, "last_complete_replay_age": REPLAY_THROUGH,
            "independent_knot_and_distinction_rename_seed_start": RENAME_SEED,
            "cases": cases,
            "five_matched_edit_preserves_counts_roles_and_every_positive_parent_roster": True,
            "sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = json.dumps(run(), separators=(",", ":"), sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(record)
    else:
        print(record, end="")


if __name__ == "__main__":
    main()
