"""Check the difference between a direct link and a class of linked parts.

Each listed pair shares its own distinction. Under the recorded no-take law
a birth meets only its parents. The pair list and the usable loose counts
therefore retain everything needed for this small complete-round replay.
"""

import argparse
import json
from collections import Counter
from itertools import combinations, product

import networkx as nx


def fixture(kind):
    # a and b are the two members followed throughout. They meet c and d.
    # Witnesses x, y and h meet the members of three separate sets.
    pairs = [
        ("a", "c"), ("b", "d"), ("p", "q"), ("r", "s"),
        ("x", "a"), ("x", "p"), ("x", "q"),
        ("y", "b"), ("y", "r"), ("y", "s"),
        ("h", "c"), ("h", "d"), ("h", "z"),
    ]
    loose = dict.fromkeys(("a", "b", "c", "d", "p", "q", "r", "s"), 1)
    if kind == "twelve":
        # z initially belongs to the same part as both a and b, then acts.
        pairs += [("z", "x"), ("z", "y")]
        loose["z"] = 8
    else:
        # w links a and b at the start. z lets c and d act one round later.
        pairs += [("a", "u"), ("u", "w"), ("u", "v"), ("v", "w"), ("v", "b")]
        loose.update(w=2, z=2)
    meeting = nx.Graph(pairs)
    return meeting, loose


def members_and_parts(meeting, members):
    members = set(members)
    met_sets = {frozenset(meeting[w]) & members for w in meeting}
    joinable = nx.Graph()
    joinable.add_nodes_from(members)
    for met in met_sets:
        joinable.add_edges_from(combinations(sorted(met), 2))
    return met_sets, joinable


def birth_groups(meeting, members):
    met_sets, joinable = members_and_parts(meeting, members)
    larger = []
    for clique in nx.find_cliques(joinable):
        clique = frozenset(clique)
        if len(clique) >= 3 and not any(clique <= met for met in met_sets):
            larger.append(clique)
    smaller = [frozenset((p, q)) for p, q in joinable.edges
               if not any(p in large and q in large for large in larger)]
    return sorted(tuple(sorted(group)) for group in larger + smaller)


def read_parts(meeting, members):
    _, joinable = members_and_parts(meeting, members)
    part_a = nx.node_connected_component(joinable, "a")
    part_b = nx.node_connected_component(joinable, "b")
    same_part = part_a == part_b
    direct_link = any(v in part_b for u in part_a for v in meeting[u])
    classes = joinable.copy()
    classes.add_edges_from(meeting.subgraph(members).edges)
    return {
        "part of a": sorted(part_a), "part of b": sorted(part_b),
        "same part": same_part,
        "one part or directly linked parts": same_part or direct_link,
        "same class": nx.has_path(classes, "a", "b"),
    }


def play_round(meeting, loose, round_number, cap):
    groups = birth_groups(meeting, loose)
    owes = Counter(p for group in groups for p in group)
    waits = {p for p in loose if owes[p] > loose[p]}
    births = [group for group in groups if waits.isdisjoint(group)]
    paid = Counter(p for group in births for p in group)
    for p in sorted(loose.keys() - waits):
        births.extend([(p,)] * (loose[p] - paid[p]))
    next_meeting = meeting.copy()
    next_loose = {p: loose[p] for p in sorted(waits)}
    made = {}
    for i, parents in enumerate(births):
        name = f"k{round_number}.{i}"
        next_meeting.add_edges_from((p, name) for p in parents)
        made[name] = parents
    provisional = set(made) | set(next_loose)
    demand = Counter(p for g in birth_groups(next_meeting, provisional) for p in g)
    for k, parents in made.items():
        next_loose[k] = min(cap, max(3 - len(parents), demand[k], 1))
    return next_meeting, next_loose, made, dict(sorted(owes.items())), sorted(waits)


def local_rules(meeting, loose):
    # Each private distinction and each shared pair has its own identity.
    by_knot = {u: [] for u in meeting}
    for index, (p, q) in enumerate(sorted(tuple(sorted(p)) for p in meeting.edges)):
        by_knot[p].append(index)
        by_knot[q].append(index)
    first_loose = meeting.number_of_edges()
    for p in sorted(loose):
        by_knot[p].extend(range(first_loose, first_loose + loose[p]))
        first_loose += loose[p]
    return by_knot


def extends_nae(rules, assigned):
    """Try an unset distinction in a knot that is still monochromatic."""
    first_choice = None
    for rule in rules:
        fixed = {assigned[d] for d in rule if d in assigned}
        if len(fixed) == 2:
            continue
        free = [d for d in rule if d not in assigned]
        if not free:
            return False
        if len(fixed) == 1 and len(free) == 1:
            return extends_nae(rules, assigned | {free[0]: 1 - next(iter(fixed))})
        if first_choice is None:
            first_choice = free[0]
    if first_choice is None:
        return True
    return any(extends_nae(rules, assigned | {first_choice: bit}) for bit in (0, 1))


def initial_relation(meeting, loose):
    rules = local_rules(meeting, loose)
    counts = {}
    for k, rule in sorted(rules.items()):
        assert len(rule) >= 3
        # Complementation preserves all the rules. Test one representative
        # of each complementary pair; constant assignments violate this knot.
        allowed = 0
        for tail in product((0, 1), repeat=len(rule) - 1):
            if any(tail) and extends_nae(rules.values(), dict(zip(rule, (0,) + tail))):
                allowed += 2
        assert allowed == 2 ** len(rule) - 2
        counts[k] = {"places": len(rule), "allowed assignments on its places": allowed}
    return counts


def check(kind, cap=3):
    meeting, loose = fixture(kind)
    record = {
        "cap on a birth": cap,
        "each pair holds one shared distinction": sorted(sorted(p) for p in meeting.edges),
        "usable loose distinctions at start": dict(sorted(loose.items())),
        "not-all-equal projections in the whole start": initial_relation(meeting, loose),
        "after round": [read_parts(meeting, loose)],
        "growth": [],
    }
    for t in (1, 2):
        meeting, loose, made, owing, waits = play_round(meeting, loose, t, cap)
        record["after round"].append(read_parts(meeting, loose))
        record["growth"].append({"owing": owing, "waiting": waits, "parents by birth": made})
    rows = record["after round"]
    assert [r["same part"] for r in rows] == [True, False, True]
    assert [r["one part or directly linked parts"] for r in rows] == [True, False, True]
    assert all(r["same class"] for r in rows)
    assert "a" in record["growth"][1]["waiting"] and "b" in record["growth"][1]["waiting"]
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", choices=("twelve", "fifteen", "both"), default="both")
    args = parser.parse_args()
    choices = ["twelve", "fifteen"] if args.fixture == "both" else [args.fixture]
    print(json.dumps({choice: check(choice) for choice in choices}, indent=2))
