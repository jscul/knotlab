"""Rebuild the four-knot far end and its two marked growths, one at a time.

Each ordinary birth shares one previously loose distinction with each of its
parents and meets no other existing knot. Usable counts and the set of knots
each knot meets therefore suffice from the listed start distinctions onward.
"""

import argparse
import gzip
import hashlib
import json
from collections import Counter, deque
from itertools import combinations
from pathlib import Path

import networkx as nx


FAR_END = "n4:g16:1112@1"
HERE = Path(__file__).resolve().parent


def materialize_start(stub):
    stars = []
    roles = []
    fresh = 0

    def put(role, size=1):
        first = len(stars)
        stars.extend([] for _ in range(size))
        roles.extend([role] * size)
        return first

    def distinction(*holders):
        nonlocal fresh
        for i in holders:
            stars[i].append(fresh)
        fresh += 1

    def pattern(role, pairs, loose):
        first = put(role, len(loose))
        for u, v in pairs:
            distinction(first + u, first + v)
        for local, count in enumerate(loose):
            for _ in range(count):
                distinction(first + local)
        return first

    def meeting(left, right):
        spent = put("spent")
        distinction(left, spent)
        distinction(right, spent)
        distinction(right, spent)
        distinction(left)
        distinction(right)

    a = pattern("A", [(0, 1), (0, 2), (1, 2)], [1, 2, 2])
    if not stub:
        b = pattern("B", [(0, 1), (0, 3), (1, 2), (2, 3)], [1, 1, 1, 2])
    left = a
    for _ in range(2):
        right = put("link")
        meeting(left, right)
        left = right
    right = put("B") if stub else b + 1
    meeting(left, right)
    assert all(len(row) >= 3 for row in stars)
    return stars, roles


def joins(met, live):
    # A pair can join exactly when both occur among the members one knot
    # meets. A larger maximal clique qualifies iff no knot meets them all.
    joinable = nx.Graph()
    joinable.add_nodes_from(live)
    for neighbours in met:
        joinable.add_edges_from(combinations(neighbours & live, 2))
    large = []
    pairs = {tuple(sorted(pair)) for pair in joinable.edges}
    for clique in nx.find_cliques(joinable):
        if len(clique) >= 3 and not set.intersection(*(met[p] for p in clique)):
            group = tuple(sorted(clique))
            large.append(group)
            pairs.difference_update(combinations(group, 2))
    return sorted(large) + sorted(pairs), joinable


class Making:
    """Intern exact birth descriptions across separate growths for comparison."""

    def __init__(self):
        self.identities = {}
        self.names = []

    def intern(self, description, published_name):
        if description not in self.identities:
            self.identities[description] = len(self.names)
            self.names.append(published_name)
        identity = self.identities[description]
        assert self.names[identity] == published_name
        return identity

    def child(self, kind, parents, ordinal):
        description = (kind, tuple(sorted(parents)), ordinal)
        parent_names = tuple(sorted(self.names[p] for p in parents))
        composed = repr((kind, parent_names, ordinal)).encode()
        return self.intern(description, hashlib.sha1(composed).hexdigest()[:16])


class Growth:
    def __init__(self, stub, making):
        self.making = making
        stars, roles = materialize_start(stub)
        self.initial_stars = stars
        self.initial_roles = roles
        by_distinction = {}
        for u, places in enumerate(stars):
            for d in places:
                by_distinction.setdefault(d, []).append(u)
        self.met = [set() for _ in stars]
        self.loose = Counter()
        for holders in by_distinction.values():
            if len(holders) == 1:
                self.loose[holders[0]] += 1
            else:
                u, v = holders
                self.met[u].add(v)
                self.met[v].add(u)
        self.role = [frozenset([role]) for role in roles]
        self.identity = []
        self.parents = [() for _ in roles]
        role_number = Counter()
        for role in roles:
            name = f"{role}{role_number[role]}"
            self.identity.append(making.intern(("start", name), name))
            role_number[role] += 1

    def grow(self):
        live = set(self.loose)
        groups, _ = joins(self.met, live)
        owed = Counter(p for group in groups for p in group)
        wait = {u for u in live if self.loose[u] < owed[u]}
        births = [group for group in groups if wait.isdisjoint(group)]
        paid = Counter(p for group in births for p in group)
        for p in sorted(live - wait):
            births.extend([(p,)] * (self.loose[p] - paid[p]))

        first = len(self.met)
        seen = Counter()
        for parents in births:
            index = len(self.met)
            self.met.append(set(parents))
            self.parents.append(parents)
            for p in parents:
                self.met[p].add(index)
            self.role.append(frozenset.union(*(self.role[p] for p in parents)))
            kind = "offshoot" if len(parents) == 1 else "join"
            parent_names = tuple(sorted(self.identity[p] for p in parents))
            key = (kind, parent_names)
            self.identity.append(self.making.child(kind, parent_names, seen[key]))
            seen[key] += 1

        made = range(first, len(self.met))
        next_groups, _ = joins(self.met, wait | set(made))
        demand = Counter(u for group in next_groups for u in group)
        self.loose = {w: self.loose[w] for w in wait}
        own = {}
        for k in made:
            p = len(self.parents[k])
            f = min(3, max(1, 3 - p, demand[k]))
            self.loose[k] = f
            if self.role[k] == {"A"}:
                own[self.identity[k]] = (f, p + f)
        return own

    def inspect_third_round(self):
        own_a = {u for u, role in enumerate(self.role) if role == {"A"}}
        own_b = {u for u in self.loose if self.role[u] == {"B"}}
        steps = {u: 0 for u in own_a}
        pending = deque(own_a)
        while pending:
            previous = pending.popleft()
            for other in self.met[previous] - steps.keys():
                steps[other] = steps[previous] + 1
                pending.append(other)
        live = set(self.loose)
        _, joined = joins(self.met, live)
        parts = list(nx.connected_components(joined))
        for u in live:
            joined.add_edges_from((u, v) for v in self.met[u] & live)
        classes = list(nx.connected_components(joined))
        rows = []
        for rank, u in enumerate(sorted(own_b, key=lambda x: (steps[x], x)), 1):
            in_part = next(p for p in parts if u in p)
            in_class = next(c for c in classes if u in c)
            rows.append({"rank": rank, "member": u, "sharings": steps[u],
                         "usable": self.loose[u], "parents": self.parents[u],
                         "name by making": self.making.names[self.identity[u]],
                         "receiver-own member in same part": bool(in_part & own_a),
                         "receiver-own member in same class": bool(in_class & own_a)})
        return rows


def series(making, rounds, target=None, stub=False):
    state = Growth(stub, making)
    records, size, ranks = [], [], []
    for t in range(1, rounds + 1):
        records.append(state.grow())
        size.append(len(state.met))
        if t == 3 and not stub:
            ranks = state.inspect_third_round()
            if target is not None:
                assert any(r["member"] == target and r["rank"] <= 5 for r in ranks)
                state.loose[target] += 1
        if size[-1] > 6000:
            break
    return records, size, ranks


def summary(records, making):
    rows = []
    for r in records:
        published = sorted((making.names[i], *values) for i, values in r.items())
        rows.append({"count": len(r), "digest by making":
                     hashlib.sha1(repr(published).encode()).hexdigest()[:12]})
    return rows


def compare(before, after, making):
    first = next((i for i, (x, y) in enumerate(zip(before, after)) if x != y), None)
    first_count = next((i + 1 for i, (x, y) in enumerate(zip(before, after))
                        if len(x) != len(y)), None)
    result = {"rounds compared": min(len(before), len(after)),
              "first difference in exact births": None if first is None else first + 1,
              "first difference in count": first_count}
    if first is None:
        return result
    x, y = before[first], after[first]
    common = x.keys() & y.keys()
    differing = []
    for i in sorted(x.keys() | y.keys(), key=making.names.__getitem__):
        if x.get(i) != y.get(i):
            differing.append({"name by making": making.names[i], "before": x.get(i),
                              "after": y.get(i)})
    result.update({"counts at first difference": [len(x), len(y)],
                   "births at first difference in earlier only": len(x.keys() - y.keys()),
                   "births at first difference in later only": len(y.keys() - x.keys()),
                   "same births with different fresh count or places": sum(x[i] != y[i] for i in common),
                   "differing births at first difference (fresh, places)": differing})
    return result


def check(rounds):
    making = Making()
    baseline, knots, ranks = series(making, rounds)
    stub, stub_knots, _ = series(making, rounds, stub=True)
    with gzip.open(HERE.parent / "recede_runs.jsonl.gz", "rt") as rows:
        candidates = [r for line in rows if (r := json.loads(line))["B"] == FAR_END]
    assert len(candidates) == 1
    archive = candidates[0]
    common = min(len(baseline), len(archive["own births"]))
    assert [len(r) for r in baseline[:common]] == archive["own births"][:common]
    assert ranks[0]["sharings"] == archive["nearest far member"][2]
    stars, roles = materialize_start(False)
    report = {
        "far end": FAR_END,
        "far end before joining": {"pairs": [[0, 1], [0, 3], [1, 2], [2, 3]],
                                   "loose counts": [1, 1, 1, 2], "site": 1},
        "receiver before joining": {"pairs": [[0, 1], [0, 2], [1, 2]],
                                    "loose counts": [1, 2, 2], "site": 0},
        "start with both patterns": {"knots in order": stars, "roles": roles},
        "law": "cap of three, waiting and release, no takes, not-all-equal, two link knots",
        "intervention": "add one usable loose distinction at the indicated member after round 3",
        "round limit": rounds, "knot stopping threshold": 6000,
        "baseline rounds matching archived own counts": common,
        "far-own members ranked after round 3": ranks,
        "unmarked": {"total knots": knots, "receiver-own": summary(baseline, making)},
        "stub": {"total knots": stub_knots, "receiver-own": summary(stub, making)},
        "unmarked compared with stub": compare(stub, baseline, making),
        "added distinction": {},
    }
    for target in (41, 46):
        changed, total, again = series(making, rounds, target)
        assert again == ranks
        report["added distinction"][str(target)] = {
            "total knots": total, "receiver-own": summary(changed, making),
            "compared with unmarked": compare(baseline, changed, making),
            "compared with stub": compare(stub, changed, making),
        }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=24, choices=range(3, 25))
    args = parser.parse_args()
    print(json.dumps(check(args.rounds), indent=2))
