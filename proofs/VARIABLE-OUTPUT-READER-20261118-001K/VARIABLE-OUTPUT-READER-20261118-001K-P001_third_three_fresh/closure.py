"""Close the loose-holder state space with one distinguished three-output triple."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib import util
from itertools import chain, permutations, product
import json
from math import prod
from pathlib import Path
import sys


PROOFS = Path(__file__).resolve().parents[2]
PREDECESSOR = (
    PROOFS / "VARIABLE-OUTPUT-READER-20261118-001J"
    / "VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six"
)
EXPECTED = {
    "frontier.py": "ef602d7b51ed1c5e3bcdf738ce3cd291bba6143e985d7feb4ac088edbec85773",
    "frontier.json": "84624e514dd16a36a177c8730e426d188c0ad6e5cac91b17a66aab555fed5605",
    "suffix_windows.json": "2e9a313ffd5cba05fef09b7ac5e79718a619be4123947ddc36e6349cac9a8dde",
}
NOT_YET = -1
NO_LIVE_MARKER = -1


def verified(filename):
    path = PREDECESSOR / filename
    data = path.read_bytes()
    assert sha256(data).hexdigest() == EXPECTED[filename]
    return data


verified("frontier.py")
spec = util.spec_from_file_location("third_fresh_predecessor", PREDECESSOR / "frontier.py")
J = util.module_from_spec(spec)
sys.modules[spec.name] = J
spec.loader.exec_module(J)
OLD = J.old
RULE = OLD.original_rule()


@dataclass(frozen=True, order=True)
class State:
    prior_shrinks: int
    frontier: OLD.Frontier
    high_holder: int = NO_LIVE_MARKER

    @property
    def loose(self):
        return sum(self.frontier.loose)

    @property
    def shrinks(self):
        return 7 - self.loose

    def project(self):
        return State(self.prior_shrinks, J.canon(self.frontier)[0])

    def description(self):
        return {
            "prior_shrinks": None if self.prior_shrinks == NOT_YET else self.prior_shrinks,
            "loose_counts": self.frontier.loose,
            "adjacency_masks": self.frontier.adjacent,
            "retired_neighborhood_masks": self.frontier.retired,
            "marked_high_holder": None if self.high_holder == NO_LIVE_MARKER else self.high_holder,
        }


@cache
def canonical(front, marked):
    if marked == NO_LIVE_MARKER:
        ordinary, order = J.canon(front)
        return ordinary, NO_LIVE_MARKER, order
    colors = []
    for site, count in enumerate(front.loose):
        sizes = sorted(group.bit_count() for group in front.retired if group & (1 << site))
        colors.append((count, front.adjacent[site].bit_count(), tuple(sizes), site == marked))
    classes = [tuple(i for i, color in enumerate(colors) if color == key)
               for key in sorted(set(colors))]
    orders = (tuple(chain.from_iterable(blocks))
              for blocks in product(*(permutations(group) for group in classes)))
    return min((front.restrict(order), order.index(marked), order) for order in orders)


def snapshot(rows, prior, high):
    ordinary, names, loose = J.literal_snapshot(rows)
    marked = names.index(high) if high in names else NO_LIVE_MARKER
    front, marked, order = canonical(ordinary, marked)
    return State(prior, front, marked), tuple(names[i] for i in order), loose


def turn(state, parents, outputs):
    front = state.frontier
    new_site = len(front.loose)
    loose = tuple(count - (site in parents) for site, count in enumerate(front.loose))
    adjacent = tuple(row | ((1 << new_site) if site in parents else 0)
                     for site, row in enumerate(front.adjacent))
    retired = (*front.retired, *(adjacent[site] for site, count in enumerate(loose) if count == 0))
    remain = (*tuple(site for site, count in enumerate(loose) if count), new_site)
    raw = OLD.Frontier((*loose, outputs), (*adjacent, OLD.mask(parents)), retired).restrict(remain)
    holder = new_site if outputs == 3 else state.high_holder
    marked = remain.index(holder) if holder in remain else NO_LIVE_MARKER
    updated, marked, _ = canonical(raw, marked)
    prior = state.shrinks if outputs == 3 else state.prior_shrinks
    assert J.canon(updated)[0] == J.step(front, parents, outputs)
    return State(prior, updated, marked)


def actions(state, allowed):
    for parents in sorted(allowed):
        size = len(parents)
        if size >= 2:
            yield parents, 2
        if size == 3 and state.prior_shrinks == NOT_YET:
            yield parents, 3


def literal_options(rows, state, high):
    same, names, loose = snapshot(rows, state.prior_shrinks, high)
    assert same == state
    return names, loose, OLD.verify_literal_moves(rows, state.frontier, names, loose)


def encode(rows, high, mark=None):
    _, _, loose = J.literal_snapshot(rows)
    result = {
        "width": 1 + max(chain.from_iterable(rows)),
        "site_count": len(rows), "junction_supports": rows, "exceptional_site": high,
        "loose_bits": tuple(sorted(chain.from_iterable(loose.values()))),
    }
    if mark is not None:
        assert RULE.legal_local_move(dict(enumerate(rows)), mark, OLD.FRESH_FOR_PARENT_TEST)
        result["legal_mark"] = mark
    return result


def named_bits(parents, names, loose):
    return tuple(sorted(min(loose[names[i]]) for i in parents))


def explore():
    representatives = {}
    starters = {}
    queue = deque()
    for label, rows in zip(("siblings", "chain"), J.initial_histories(), strict=True):
        state = snapshot(rows, NOT_YET, None)[0]
        starters[label] = state
        assert state not in representatives
        representatives[state] = (rows, None)
        queue.append(state)
    arcs = {}
    earliest = defaultdict(dict)
    counts = defaultdict(Counter)
    while queue:
        state = queue.popleft()
        rows, high = representatives[state]
        assert 2 <= state.loose <= 7
        assert state.shrinks == sum(len(scope) == 5 for scope in rows)
        assert tuple(i for i, support in enumerate(rows) if len(support) == 6) == (() if high is None else (high,))
        names, loose, allowed = literal_options(rows, state, high)
        triples = tuple(group for group in sorted(allowed) if len(group) == 3)
        through_high = tuple(group for group in triples if state.high_holder in group)
        tag = (state.prior_shrinks, state.shrinks)
        counts[tag].update(states=1, states_with_triples=bool(triples), triple_holder_groups=len(triples),
                           states_with_live_high_output=state.high_holder != NO_LIVE_MARKER,
                           states_with_triples_through_high=bool(through_high))
        if high is not None:
            entry = earliest[tag]
            if "first_history" not in entry:
                entry["first_history"] = encode(rows, high)
            for field, groups in (("first_with_a_legal_triple", triples),
                                  ("first_with_a_legal_triple_using_high_output", through_high)):
                if groups and field not in entry:
                    entry[field] = encode(rows, high, named_bits(groups[0], names, loose))
        moves = []
        for parents, outputs in actions(state, allowed):
            following = turn(state, parents, outputs)
            physical = J.advance(rows, tuple(names[i] for i in parents), outputs)
            now_high = len(rows) if outputs == 3 else high
            assert snapshot(physical, following.prior_shrinks, now_high)[0] == following
            moves.append((parents, outputs, following))
            if following not in representatives:
                representatives[following] = physical, now_high
                queue.append(following)
        arcs[state] = tuple(moves)
    return starters, representatives, arcs, counts, earliest


def projected_arcs(representatives):
    projected = {}
    for state, (rows, high) in representatives.items():
        plain = state.project()
        if plain not in projected:
            projected[plain] = rows, high
    arcs = {}
    allowed_groups = {}
    for state, (rows, _) in projected.items():
        # J's literal canonicalization independently checks every projected
        # parent set, including the unary candidates used for complements.
        front, names, loose = J.literal_snapshot(rows)
        assert front == state.frontier
        allowed = OLD.verify_literal_moves(rows, front, names, loose)
        allowed_groups[state] = allowed
        moves = []
        for parents, outputs in actions(state, allowed):
            before = state.shrinks if outputs == 3 else state.prior_shrinks
            following = State(before, J.step(front, parents, outputs))
            assert following in projected
            moves.append((parents, outputs, following))
        arcs[state] = tuple(moves)
    return projected, arcs, allowed_groups


def fixed_point_digest(arcs):
    indices = {state: i for i, state in enumerate(sorted(arcs))}
    receipt = [(state.description(), [(parents, outputs, indices[following])
                                      for parents, outputs, following in arcs[state]]) for state in sorted(arcs)]
    return sha256(json.dumps(receipt, separators=(",", ":")).encode()).hexdigest()


def original_control(arcs):
    before = sorted(state for state in arcs if state.prior_shrinks == NOT_YET)
    indices = {state: i for i, state in enumerate(before)}
    receipt = [[(state.frontier.loose, state.frontier.adjacent, state.frontier.retired),
                [(parents, indices[following]) for parents, outputs, following in arcs[state] if outputs == 2]]
               for state in before]
    digest = sha256(json.dumps(receipt, separators=(",", ":")).encode()).hexdigest()
    archived = json.loads(verified("frontier.json"))["closure"]
    n = len(before)
    m = sum(len(row[1]) for row in receipt)
    assert (n, m, digest) == (archived["reachable_states"], archived["transitions"], archived["fixed_point_sha256"])
    return {"states": n, "transitions": m, "exact_predecessor_fixed_point_sha256": digest}


def known_prefixes(representatives, arcs):
    source = json.loads(verified("suffix_windows.json"))["replayed_minimum_sources"]
    controls = {}
    for tag, item in source.items():
        scopes = tuple(map(tuple, item["junction_supports"].values()))[:-1]
        assert 1 + max(chain.from_iterable(scopes)) == 19
        before, names, loose = snapshot(scopes, NOT_YET, None)
        assert before in representatives
        approved = set(item["initial_triple_join"])
        parents = tuple(i for i, holder in enumerate(names) if set(loose[holder]) & approved)
        assert len(parents) == 3
        after = (*scopes, (*sorted(approved), 19, 20, 21))
        assert RULE.legal_local_move(dict(enumerate(scopes)), tuple(approved), OLD.FRESH_FOR_PARENT_TEST)
        following = snapshot(after, 0, len(scopes))[0]
        assert (parents, 3, following) in arcs[before]
        controls[tag] = {"known_width_19_prefix_in_closure": True, "exceptional_inputs": tuple(sorted(approved)),
                         "width_22_snapshot": following.description()}
    return controls


def complement(front, parents, allowed):
    remainder = tuple(count - (i in parents) for i, count in enumerate(front.loose))
    if not all(count in (0, 1) for count in remainder):
        return None
    other = tuple(i for i, count in enumerate(remainder) if count)
    return other if other in allowed else None


def actual_triples(rows):
    front, names, loose = J.literal_snapshot(rows)
    groups = OLD.verify_literal_moves(rows, front, names, loose)
    return {tuple(sorted(ports)) for group in groups if len(group) == 3
            for ports in product(*(loose[names[i]] for i in group))}


def literal_complement(state, rows, high, parents, outputs, other):
    front, sites, loose = J.literal_snapshot(rows)
    assert front == state.frontier
    selected = {i: min(loose[sites[i]]) for i in parents}
    first = tuple(sorted(selected.values()))
    second = tuple(sorted(min(bit for bit in loose[sites[i]] if bit != selected.get(i)) for i in other))
    supports = dict(enumerate(rows))
    assert RULE.legal_local_move(supports, first, OLD.FRESH_FOR_PARENT_TEST)
    assert RULE.legal_local_move(supports, second, OLD.FRESH_FOR_PARENT_TEST)
    current_width = 1 + max(chain.from_iterable(rows))
    fresh = tuple(range(current_width, current_width + outputs))
    first_extension = (*rows, (*first, *fresh))
    second_extension = (*rows, (*second, *fresh))
    boundary = set()
    for row in rows:
        boundary.symmetric_difference_update(row)
    assert set(first).isdisjoint(second) and set(first) | set(second) == boundary
    assert set(first_extension[-1]) ^ set(second_extension[-1]) == boundary
    assert set(first_extension[-1]) != set(second_extension[-1])
    return {
        "state": state.description(), "prefix": encode(rows, high),
        "source_parents": tuple(sites[i] for i in parents), "rival_parents": tuple(sites[i] for i in other),
        "number_of_literal_source_choices_with_a_complement": prod(len(loose[sites[i]]) for i in parents),
        "same_parent_group": parents == other, "source_inputs": first, "rival_inputs": second,
        "source_final_support": first_extension[-1], "rival_final_support": second_extension[-1],
        "source_triples_after": tuple(sorted(actual_triples(first_extension))),
        "rival_triples_after": tuple(sorted(actual_triples(second_extension))),
        "sum_of_prefix_equations": tuple(sorted(boundary)),
        "identical_state_spaces_by_appended_difference_equal_to_prefix_sum": True,
    }


def examine_complements(projected, arcs, allowed):
    counts = defaultdict(Counter)
    opposing = []
    for state, links in sorted(arcs.items()):
        for parents, outputs, _ in links:
            if state.prior_shrinks == NOT_YET and outputs != 3:
                continue
            key = ("exceptional_birth" if outputs == 3 else "after_exception",
                   state.prior_shrinks, state.loose, len(parents), outputs)
            counts[key]["tested_moves"] += 1
            literal_count = prod(state.frontier.loose[i] for i in parents)
            counts[key]["tested_named_input_choices_on_one_representative_per_frontier"] += literal_count
            other = complement(state.frontier, parents, allowed[state])
            if other is None:
                continue
            counts[key]["moves_with_a_complement"] += 1
            counts[key]["named_input_choices_with_a_complement"] += literal_count
            rows, high = projected[state]
            opposing.append(literal_complement(state, rows, high, parents, outputs, other))
    assert all(item["source_triples_after"] == item["rival_triples_after"] == () for item in opposing)
    distribution = [
        {"stage": stage, "shrinks_before_exception": None if prior == NOT_YET else prior,
         "loose_bits": loose, "source_parent_count": size, "fresh_outputs": outputs,
         "tested_moves": count["tested_moves"], "moves_with_a_complement": count["moves_with_a_complement"],
         "tested_named_input_choices_on_one_representative_per_frontier":
             count["tested_named_input_choices_on_one_representative_per_frontier"],
         "named_input_choices_with_a_complement": count["named_input_choices_with_a_complement"]}
        for (stage, prior, loose, size, outputs), count in sorted(counts.items())
    ]
    return {"by_source_move": distribution, "all_complementary_cases": opposing}


def reachable_from(start, arcs):
    reached = {start}
    active = [start]
    while active:
        state = active.pop()
        for _, _, following in arcs[state]:
            if following not in reached:
                reached.add(following)
                active.append(following)
    return reached


def run():
    starters, reps, arcs, colored_counts, earliest = explore()
    projected, plain_arcs, plain_groups = projected_arcs(reps)
    reached = {tag: reachable_from(state, arcs) for tag, state in starters.items()}
    assert set.union(*reached.values()) == set(arcs)
    plain_counts = defaultdict(Counter)
    for state in plain_arcs:
        group = plain_counts[state.prior_shrinks, state.shrinks]
        triples = sum(len(parents) == 3 for parents in plain_groups[state])
        group.update(states=1, states_with_triples=bool(triples), triple_holder_groups=triples)
    distribution = []
    for (prior, total), counts in sorted(plain_counts.items()):
        distribution.append({
            "prior_shrinks": None if prior == NOT_YET else prior,
            "subsequent_shrinks": None if prior == NOT_YET else total - prior,
            "total_shrinks": total, "loose_bits": 7 - total, "unmarked_frontiers": dict(counts),
            "frontiers_with_high_holder_tracking": dict(colored_counts[prior, total]),
        })
    return {
        "verified_predecessor_files": EXPECTED,
        "all_projected_states": len(plain_arcs), "all_projected_edges": sum(map(len, plain_arcs.values())),
        "all_states_with_high_holder_tracking": len(arcs), "all_edges_with_high_holder_tracking": sum(map(len, arcs.values())),
        "fixed_point_sha256": fixed_point_digest(arcs), "before_exception_control": original_control(plain_arcs),
        "initial_shapes": {tag: {"start": state.description(), "states_reachable": len(reached[tag]),
                                 "projected_states_reachable": len({item.project() for item in reached[tag]})}
                           for tag, state in starters.items()},
        "states_reachable_from_both_initial_shapes": len(set.intersection(*reached.values())),
        "distribution": distribution,
        "minimum_loose_bits": min(state.loose for state in plain_arcs),
        "maximum_total_shrinks": max(state.shrinks for state in plain_arcs),
        "maximum_shrinks_after_exception_by_prior_shrinks": {
            prior: max(state.shrinks - prior for state in plain_arcs if state.prior_shrinks == prior)
            for prior in sorted({state.prior_shrinks for state in plain_arcs} - {NOT_YET})
        },
        "shortest_post_exception_histories": [
            {"prior_shrinks": before, "subsequent_shrinks": total - before, **history}
            for (before, total), history in sorted(earliest.items())
        ],
        "known_two_width_19_prefix_controls": known_prefixes(reps, arcs),
        "last_site_complement_test": examine_complements(projected, plain_arcs, plain_groups),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
