"""A small addition at a current far member under the ordinary count.

The check covers only starts in which every member can pay throughout both
comparisons. All live members then spend all their holdings under RELEASE.
The first listed knot belongs to the receiver and the second to the sender.
Time a complete comparison on one setting before making the additional swaps.
"""
from collections import Counter, defaultdict, deque
from copy import deepcopy
from itertools import combinations
from time import process_time
import json
import sys

import networkx as nx


def sharing(places):
    holders = defaultdict(set)
    for u, distinctions in enumerate(places):
        for d in distinctions:
            holders[d].add(u)
    meets = [set().union(*(holders[d] for d in row)) - {u} for u, row in enumerate(places)]
    return holders, meets


def groups(members, meets):
    members = set(members)
    met = set(frozenset(ms & members) for ms in meets)
    pairs = set()
    for ms in met:
        pairs.update(combinations(sorted(ms), 2))
    if len(pairs) > 2500:
        raise ValueError("pair bound")
    graph = nx.Graph()
    graph.add_edges_from(pairs)
    larger = []
    for i, clique in enumerate(nx.find_cliques(graph)):
        if i == 2500:
            raise ValueError("clique bound")
        if len(clique) >= 3 and not any(set(clique) <= ms for ms in met):
            larger.append(tuple(sorted(clique)))
    for group in larger:
        pairs.difference_update(combinations(group, 2))
    return sorted(larger) + sorted(pairs)


class Growth:
    def __init__(self, places, owners=None):
        self.places = deepcopy(places)
        self.names = [(0, i) for i in range(len(places))]
        self.roots = [{p} for p in (owners if owners is not None else range(len(places)))]
        self.parents = [() for _ in places]
        self.rows = []

    def mark(self, u):
        self.places[u].append(1 + max(max(row) for row in self.places))

    def step(self, take):
        holders, meets = sharing(self.places)
        available = {u: sorted(d for d in row if len(holders[d]) == 1)
                     for u, row in enumerate(self.places)}
        members = [u for u, loose in available.items() if loose]
        joins = groups(members, meets)
        owed = Counter(u for g in joins for u in g)
        if any(owed[u] > len(available[u]) for u in members):
            raise ValueError("a short member")
        births = joins + [(u,) for u in members for _ in range(len(available[u]) - owed[u])]
        if len(births) > 120:
            raise ValueError("birth bound")
        queues = {u: deque(ds) for u, ds in available.items()}
        born = []
        sibling_counts = Counter()
        next_d = 1 + max(holders)
        for ps in births:
            inputs = [queues[p].popleft() for p in ps]
            if take in ("oldest", "newest", "sole") or (take != "none" and len(ps) == 1):
                if take in ("one-parent-step", "two-parent-steps"):
                    common = set(self.parents[ps[0]])
                    if take == "two-parent-steps":
                        common = set().union(*(self.parents[k] for k in common))
                else:
                    common = set.intersection(*(meets[p] for p in ps)) - set(ps)
                candidates = set().union(*(self.places[k] for k in common))
                candidates = {d for d in candidates if len(holders[d]) >= 2}
                candidates.difference_update(*(self.places[p] for p in ps))
                if candidates and (take in ("oldest", "newest") or len(candidates) == 1):
                    inputs.append(max(candidates) if take == "newest" else min(candidates))
            u = len(self.places)
            born.append(u)
            self.places.append(inputs)
            self.parents.append(ps)
            self.roots.append(set.union(*(self.roots[p] for p in ps)))
            self.names.append((1, tuple(sorted(self.names[p] for p in ps)), sibling_counts[ps]))
            sibling_counts[ps] += 1
        _, after = sharing(self.places)
        demand = Counter(u for g in groups(born, after) for u in g)
        own = []
        for u in born:
            f = max(demand[u], 3 - len(self.places[u]), 1)
            self.places[u].extend(range(next_d, next_d + f))
            next_d += f
            if self.roots[u] == {0}:
                own.append((self.names[u], f, len(self.places[u])))
        self.rows.append(sorted(own))


START = [[0, 3, 4, 7], [1, 2, 5, 6, 8], [0, 1, 2]]


def comparison(take, set_after, steps, places=START, owners=None, nearest_rank=None):
    g = Growth(places, owners)
    for _ in range(set_after):
        g.step(take)
    holders, meets = sharing(g.places)
    active = {u for u, row in enumerate(g.places) if any(len(holders[d]) == 1 for d in row)}
    far = sorted(u for u in active if g.roots[u] == {1})
    receiver = sorted(u for u in active if g.roots[u] == {0})
    if not far or not receiver:
        return {"take": take, "set_after": set_after, "observed": "one end absent"}
    if nearest_rank is not None:
        reached = {u: 0 for u in receiver}
        wave = set(receiver)
        layer = 0
        while wave:
            layer += 1
            later = set.union(*(meets[u] for u in wave)) - reached.keys()
            reached.update({u: layer for u in later})
            wave = later
        far.sort(key=lambda u: (reached.get(u, len(meets) + 1), u))
        if nearest_rank >= len(far):
            return {"take": take, "set_after": set_after, "observed": "far member absent"}
        far[0], far[nearest_rank] = far[nearest_rank], far[0]
    origin = far[0]
    seen = {origin}
    wave = {origin}
    distance = 0
    while wave and not (wave & set(receiver)):
        wave = set.union(*(meets[u] for u in wave)) - seen
        seen |= wave
        distance += 1
    changed = deepcopy(g)
    changed.mark(origin)
    result = {"take": take, "set_after": set_after, "marked": origin,
              "sharings_to_a_current_receiver_member": distance if wave else None,
              "receiver_members": receiver, "sender_members": far, "rounds": []}
    for i in range(1, steps + 1):
        try:
            g.step(take)
            changed.step(take)
        except ValueError as e:
            result["stop"] = str(e)
            break
        own, other = g.rows[-1], changed.rows[-1]
        result["rounds"].append({"round": set_after + i, "same": own == other,
                                 "own_births": [len(own), len(other)],
                                 "own_fresh": [[t[1] for t in x] for x in (own, other)],
                                 "own_places": [[t[2] for t in x] for x in (own, other)]})
        if own != other:
            break
    return result


def main():
    settings = [("oldest", 1, 2), ("none", 1, 2), ("sole", 1, 2),
                ("oldest", 3, 1), ("none", 3, 1), ("sole", 3, 1)]
    if sys.argv[1] == "pilot":
        settings = settings[:1]
    output = []
    for take, when, window in settings:
        begin = process_time()
        try:
            item = comparison(take, when, window)
        except ValueError as e:
            item = {"take": take, "set_after": when, "stop_before_setting": str(e)}
        item["cpu_seconds"] = round(process_time() - begin, 6)
        output.append(item)
    print(json.dumps({"start": START, "first_far_member_by_number": True,
                      "short_members": "any nonzero value stops before reading that round",
                      "comparisons": output}, indent=2))


if __name__ == "__main__":
    main()
