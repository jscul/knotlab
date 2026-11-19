"""Exact finite closure for the unary third three-fresh birth."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib import util
from itertools import chain, product
import json
from math import prod
from pathlib import Path
import sys


PROOFS = Path(__file__).resolve().parents[2]
L_PATH = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001L" / "VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third"
EXPECTED = {
    "frontier.py": "235f74069d2d19f61706f0db48777a0ee45349c980be4b6757d21558bb4c59c1",
    "rival.json": "5c41b2fcf2873887b51e41d45ed3e30730fd445c1c8357c9cca64a6e452cbf45",
}


def verified(name):
    data = (L_PATH / name).read_bytes()
    assert sha256(data).hexdigest() == EXPECTED[name], name
    return data


verified("frontier.py")
spec = util.spec_from_file_location("third_unary_binary_predecessor", L_PATH / "frontier.py")
L = util.module_from_spec(spec)
sys.modules[spec.name] = L
spec.loader.exec_module(L)
J, OLD, RULE = L.J, L.OLD, L.RULE
NOT_YET = -1


@dataclass(frozen=True, order=True)
class State:
    prior: int
    front: OLD.Frontier

    @property
    def used(self):
        return self.prior != NOT_YET

    @property
    def loose(self):
        return sum(self.front.loose)

    @property
    def shrinks(self):
        return (9 if self.used else 7) - self.loose

    def record(self):
        return (self.front.loose, self.front.adjacent, self.front.retired)


@cache
def groups(front):
    return tuple(OLD.possible_parents(front))


def choices(state):
    for parents in groups(state.front):
        if len(parents) >= 2:
            yield parents, 2
        elif not state.used:
            yield parents, 3


def fixed_point():
    roots = {State(NOT_YET, J.literal_snapshot(rows)[0]): rows for rows in J.initial_histories()}
    queue = deque(roots)
    parents_at_birth = dict.fromkeys(roots)
    depth = dict.fromkeys(roots, 3)
    edges = {}
    while queue:
        state = queue.popleft()
        assert 2 <= state.loose <= 9
        links = []
        for group, h in choices(state):
            prior = state.shrinks if h == 3 else state.prior
            following = State(prior, J.step(state.front, group, h))
            if following not in depth:
                parents_at_birth[following] = state, group, h
                depth[following] = depth[state] + 1
                queue.append(following)
            links.append((group, h, following))
        edges[state] = tuple(links)
    return roots, parents_at_birth, depth, edges


def named_menu(front, sites, loose):
    return tuple(sorted(tuple(sorted(bits)) for group in groups(front) if len(group) == 3
                        for bits in product(*(loose[sites[i]] for i in group))))


def replay(state, roots, ancestry, depth):
    cursor = state
    path = []
    while ancestry[cursor] is not None:
        previous, group, h = ancestry[cursor]
        path.append((previous, group, h, cursor))
        cursor = previous
    rows = roots[cursor]
    special = None
    for previous, group, h, following in reversed(path):
        front, sites, loose = J.literal_snapshot(rows)
        assert front == previous.front
        assert group in OLD.verify_literal_moves(rows, front, sites, loose)
        if h == 3:
            assert special is None and len(group) == 1
            special = len(rows)
        rows = J.advance(rows, tuple(sites[i] for i in group), h)
        assert J.literal_snapshot(rows)[0] == following.front
    form, sites, loose = J.literal_snapshot(rows)
    assert set(groups(form)) == OLD.verify_literal_moves(rows, form, sites, loose)
    assert form == state.front
    assert state.shrinks == sum(len(row) == 5 for row in rows) and state.used == (special is not None)
    assert len(rows) == depth[state]
    width = 1 + max(chain.from_iterable(rows))
    assert width == 2 * len(rows) + 3 + state.used
    return {
        "width": width, "junction_supports": rows, "special_unary_site": special,
        "live_holders_and_loose_bits": tuple((site, tuple(sorted(loose[site]))) for site in sites),
        "legal_triples": named_menu(form, sites, loose),
    }


def digest(edges):
    order = sorted(edges)
    index = {state: i for i, state in enumerate(order)}
    check = sha256()
    for state in order:
        row = (state.prior, state.record(), [(group, h, index[nxt]) for group, h, nxt in edges[state]])
        check.update(json.dumps(row, separators=(",", ":")).encode() + b"\n")
    return check.hexdigest()


def bounded_control(edges, depth):
    archive = json.loads(verified("rival.json"))
    limit = archive["bounded_ordinary_site_limit"]
    within = tuple(state for state in edges if depth[state] <= limit)
    counts = defaultdict(Counter)
    for state in within:
        counts[state.prior, state.shrinks].update(
            states=1, positive=int(any(len(p) == 3 for p in groups(state.front)))
        )
    named_counts = [
        {"shrinks_before_unary_third": None if p == NOT_YET else p, "total_shrinks": t, **c}
        for (p, t), c in sorted(counts.items())
    ]
    arcs = sum(len(edges[state]) for state in within if depth[state] < limit)
    assert named_counts == archive["distribution"]
    assert arcs == archive["bounded_transitions"] and len(within) == archive["bounded_states"]
    return {"site_limit": limit, "records": len(within), "transitions": arcs, "same_distribution_as_L": True}


def distribution(edges, replay_of):
    hist = defaultdict(Counter)
    first = {}
    first_positive = {}
    for state, links in edges.items():
        tag = (state.prior, state.shrinks)
        first.setdefault(tag, state)
        triples = tuple(group for group in groups(state.front) if len(group) == 3)
        entry = hist[tag]
        entry.update(states=1, transitions=len(links), positive=int(bool(triples)),
                     legal_holder_triples=len(triples),
                     named_triples_on_representatives=sum(prod(state.front.loose[i] for i in t) for t in triples))
        if triples:
            first_positive.setdefault(tag, state)
    return [
        {"shrinks_before_special": None if prior == NOT_YET else prior,
         "shrinks": total, "loose_bits": (7 if prior == NOT_YET else 9) - total, **counts,
         "earliest": replay_of(first[(prior, total)]),
         "earliest_positive": replay_of(first_positive[(prior, total)]) if (prior, total) in first_positive else None}
        for (prior, total), counts in sorted(hist.items())
    ], first_positive


def binary_graph(edges, depth, slots):
    scope = tuple(sorted(state for state in edges if state.used and state.loose == slots))
    numbered = {state: i for i, state in enumerate(scope)}
    reverse = defaultdict(list)
    internal = []
    for state in scope:
        for group, h, following in edges[state]:
            if len(group) != 2 or h != 2:
                continue
            assert following in numbered
            reverse[following].append(state)
            internal.append((numbered[state], group, numbered[following]))
    positive = tuple(state for state in scope if any(len(g) == 3 for g in groups(state.front)))
    distance = dict.fromkeys(positive, 0)
    queue = list(positive)
    for state in queue:
        for ancestor in sorted(reverse[state]):
            if ancestor not in distance:
                distance[ancestor] = distance[state] + 1
                queue.append(ancestor)
    pattern = defaultdict(Counter)
    records = []
    for state in scope:
        triples = tuple(group for group in groups(state.front) if len(group) == 3)
        row = {"prior_shrinks": state.prior, "frontier": state.record(),
               "minimum_width": 2 * depth[state] + 4, "triple_holder_groups": triples,
               "binary_arcs_entering": len(reverse[state]), "binary_steps_to_some_positive": distance.get(state)}
        records.append(row)
        if state in distance:
            pattern[state.prior].update(
                states_reaching_a_positive=1, already_positive=int(bool(triples)),
                already_positive_with_an_incoming_binary_arc=int(bool(triples and reverse[state])),
            )
    return {
        "states": records, "binary_transitions": internal,
        "reverse_binary_trim": {prior: dict(val) for prior, val in sorted(pattern.items())},
    }


def complement(front, group):
    remaining = tuple(n - (i in group) for i, n in enumerate(front.loose))
    if any(n not in (0, 1) for n in remaining):
        return None
    other = tuple(i for i, n in enumerate(remaining) if n)
    return other if other in groups(front) else None


def complementary_moves(edges, replay_of):
    stats = defaultdict(Counter)
    first = {}
    for state, links in edges.items():
        for group, h, _ in links:
            if not state.used and h != 3:
                continue
            tag = state.prior, state.loose, len(group), h
            stats[tag]["moves"] += 1
            other = complement(state.front, group)
            if other is None:
                continue
            stats[tag]["moves_with_complement"] += 1
            stats[tag]["complement_choices_on_the_same_holders"] += group == other
            stats[tag]["named_choices_with_complement"] += prod(state.front.loose[i] for i in group)
            if tag in first:
                continue
            item = replay_of(state)
            loose = [tuple(bits) for _, bits in item["live_holders_and_loose_bits"]]
            choice = {i: min(loose[i]) for i in group}
            p = tuple(sorted(choice.values()))
            q = tuple(sorted(min(bit for bit in loose[i] if bit != choice.get(i)) for i in other))
            support = dict(enumerate(item["junction_supports"]))
            assert RULE.legal_local_move(support, p, OLD.FRESH_FOR_PARENT_TEST)
            assert RULE.legal_local_move(support, q, OLD.FRESH_FOR_PARENT_TEST)
            assert not set(p) & set(q) and set(p) | set(q) == set(chain.from_iterable(loose))
            first[tag] = {"witness": item, "source_inputs": p, "other_inputs": q}
    return [
        {"prior_shrinks": None if prior == NOT_YET else prior, "loose_bits": loose,
         "source_parents": size, "source_outputs": h,
         **{name: tags[name] for name in ("moves", "moves_with_complement",
                                         "complement_choices_on_the_same_holders", "named_choices_with_complement")},
         "first_example": first.get((prior, loose, size, h))}
        for (prior, loose, size, h), tags in sorted(stats.items())
    ]


def run():
    roots, ancestry, depth, edges = fixed_point()

    @cache
    def replay_of(state):
        return replay(state, roots, ancestry, depth)

    low_records = [state for state in edges if state.used and state.loose <= 6]
    for state in low_records:
        replay_of(state)
    counts, first_positive = distribution(edges, replay_of)
    positive_late = replay_of(first_positive[2, 2])
    proper = L.five_cut(positive_late["junction_supports"], set(range(positive_late["special_unary_site"])))
    assert proper["incoming"] == []
    return {
        "dependency_sha256": EXPECTED,
        "fixed_point_states": len(edges), "fixed_point_transitions": sum(map(len, edges.values())),
        "fixed_point_digest_sha256": digest(edges), "literal_low_records_replayed": len(low_records),
        "maximum_number_of_shrinks": max(state.shrinks for state in edges if state.used),
        "minimum_loose_bits": min(state.loose for state in edges if state.used),
        "bounded_control": bounded_control(edges, depth), "distribution": counts,
        "binary_graph_at_five_loose": binary_graph(edges, depth, 5),
        "binary_graph_at_six_loose": binary_graph(edges, depth, 6),
        "complementary_moves": complementary_moves(edges, replay_of),
        "proper_five_bond_at_first_positive_with_two_prior_shrinks": {"source": positive_late, "cut": proper},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
