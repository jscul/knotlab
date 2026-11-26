"""A funded 25-knot start of the tree-plus weighting. Direct enumeration of one round."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
import os
from pathlib import Path
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def groups(members, holders):
    """Enumerate candidate subsets around each member; require all pairs and maximality."""
    sets = [set(h) & members for h in holders]
    pairs = {frozenset(p) for h in sets for p in combinations(h, 2)}
    neighbours = {v: set() for v in members}
    for a, b in pairs:
        neighbours[a].add(b)
        neighbours[b].add(a)
    large = set()
    for v in members:
        more = sorted(w for w in neighbours[v] if w > v)
        for size in range(2, len(more) + 1):
            for others in combinations(more, size):
                if any(frozenset(p) not in pairs for p in combinations(others, 2)):
                    continue
                s = frozenset((v, *others))
                if any(s <= h for h in sets):
                    continue
                if set.intersection(*(neighbours[w] for w in s)):
                    continue
                large.add(s)
    return sorted((large | {p for p in pairs if not any(p <= q for q in large)}),
                  key=lambda s: tuple(sorted(s)))


def count_round(members, loose, places, holders, reader):
    joins = groups(members, holders)
    demand = Counter(v for g in joins for v in g)
    short = {v: [loose[v], demand[v]] for v in sorted(members) if loose[v] < demand[v]}
    rows = [] if short else joins + [frozenset([v]) for v in sorted(members)
                                      for _ in range(loose[v] - demand[v])]
    children = defaultdict(set)
    for j, parents in enumerate(rows):
        for parent in parents:
            children[parent].add(j)
    next_demand = Counter(j for g in groups(set(range(len(rows))), children.values()) for j in g)
    view = []
    for j, g in enumerate(rows):
        if reader in g:
            p = len(g)
            fresh = max(1, 3 - p, next_demand[j])
            view.append([sorted(g), p, fresh, p + fresh, sorted(places[v] for v in g)])
    return {"short_loose_and_owed": short, "groups": [sorted(g) for g in joins],
            "births": len(rows), "view_parents_count_fresh_places_parent_places": view}


def build():
    # Each entry gives the actual shared distinctions of one of five starting knots.
    holding = {"U": "RV", "W": "VABC", "I": "AX", "J": "BX", "K": "CX"}
    pairs = [(holder, v) for holder, word in holding.items() for v in word]
    chain = ["X"] + [f"s{i}" for i in range(1, 15)]
    pairs.extend(zip(chain, chain[1:]))
    names = sorted(set(v for p in pairs for v in p))
    neighbours = {v: set() for v in names}
    for a, b in pairs:
        neighbours[a].add(b)
        neighbours[b].add(a)
    demand = Counter(v for g in groups(set(names), neighbours.values()) for v in g)
    places = {v: max(3, len(neighbours[v]) + demand[v]) for v in names}
    loose = {v: places[v] - len(neighbours[v]) for v in names}
    assert min(loose.values()) >= 1
    return pairs, names, neighbours, places, loose


def reach(reader, steps, neighbours):
    seen = {reader}
    for _ in range(steps):
        seen.update(set().union(*(neighbours[w] for v in tuple(seen) for w in neighbours[v])))
    return seen


def project(pairs, names, loose, selected, law):
    """Exhibit a joint assignment for each allowed pin of every selected knot."""
    shared = {v: [j for j, pair in enumerate(pairs) if v in pair] for v in names}
    bits = len(pairs)
    private = {}
    stars = {}
    for v in names:
        private[v] = list(range(bits, bits + loose[v]))
        stars[v] = shared[v] + private[v]
        bits += loose[v]
    def legal(values):
        return len(set(values)) == 2 if law == "nae" else sum(values) % 2 == 0

    projected = {}
    arities = set()
    for v in selected:
        size = len(stars[v])
        allowed = 0
        for pin in product((0, 1), repeat=size):
            if not legal(pin):
                continue
            joint = [0] * bits
            for bit, value in zip(stars[v], pin):
                joint[bit] = value
            for w in names:
                if w != v:
                    bit = private[w][0]
                    joint[bit] = (1 - joint[shared[w][0]] if law == "nae"
                                  else sum(joint[b] for b in stars[w] if b != bit) % 2)
            assert all(legal([joint[b] for b in star]) for star in stars.values())
            assert tuple(joint[b] for b in stars[v]) == pin
            allowed += 1
        projected[v] = {"places": size, "extendible": allowed, "forbidden_by_own_rule": 2**size - allowed}
        arities.add(size)
    canonical = {}
    for size in sorted(arities):
        fields = [f"z{i}" for i in range(size)]
        forbidden = [pin for pin in product((0, 1), repeat=size) if not legal(pin)]
        cnf = "; ".join(" ".join(("~" if bit else "") + field for bit, field in zip(pin, fields))
                        for pin in forbidden)
        q = [str(ROOT / ".venv/bin/python"), "-B", "-m", "knotlab", "check", "--json",
             "--cnf", cnf, "--loops", *fields[:-1], "--contact", fields[-1]]
        result = json.loads(subprocess.check_output(q, cwd=ROOT, env=dict(os.environ, PYTHONPATH="tools")))
        assert result["is_knot"] and len(result["allowed"]) == 2**size - len(forbidden)
        canonical[size] = {k: result[k] for k in ("binding", "invisible_in_parts", "coexistence", "is_knot")}
    return {"projections": projected, "canonical_check_by_number_of_places": canonical}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="one starting knot's full projection")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (700 << 20, 700 << 20))
    stamp = time.monotonic()
    pairs, names, neighbours, places, loose = build()
    whole = set(names)
    within_two = reach("R", 2, neighbours)
    assert within_two == set("RVABC")
    # Removing these two shared distinctions leaves a tree in the weighting's input.
    added = {("J", "X"), ("K", "X")}
    base = [p for p in pairs if p not in added]
    connected = {names[0]}
    for _ in names:
        connected |= {b for p in base if connected.intersection(p) for b in p}
    assert len(base) == len(connected) - 1 and connected == whole

    cases = {}
    def read(key, members, reader):
        cases[key] = {"reader": reader, "region": sorted(members),
                      **count_round(members, loose, places, neighbours.values(), reader)}
        return cases[key]["view_parents_count_fresh_places_parent_places"]

    full_r = read("R whole", whole, "R")
    assert full_r and not read("R within two steps", within_two, "R")
    assert read("R within two steps plus X", within_two | {"X"}, "R") == full_r
    full_u = read("U whole", whole, "U")
    base_u = reach("U", 2, neighbours)
    assert full_u and read("U within two steps", base_u, "U") == full_u
    first = base_u | set("VABC")
    second = base_u | {"X"}
    assert not read("U adds V A B C before X", first, "U")
    assert read("U adds X before V A B C", second, "U") == full_u
    assert read("U after both additions", first | second, "U") == full_u

    # Cross-check the hand computation with the separate complete-round implementation.
    from growth import Roster, grow
    numbers = {v: i for i, v in enumerate(names)}
    roster = Roster.from_graph([places[v] for v in names], [(numbers[a], numbers[b]) for a, b in pairs])
    assert roster.within(numbers["R"], 2) == {numbers[v] for v in within_two}
    for case in cases.values():
        reader = numbers[case["reader"]]
        region = roster.restrict({numbers[v] for v in case["region"]})
        expected = Counter()
        for _, parents, fresh, places_held, parent_places in case["view_parents_count_fresh_places_parent_places"]:
            desc = ("join" if parents > 1 else "offshoot", parents, fresh, places_held)
            expected[(desc, tuple(("start", 0, 0, h) for h in parent_places))] += 1
        for law in ("nae", "parity"):
            run = grow(region, 1, law, cap=3000)
            assert (run.end == "stall") == bool(case["short_loose_and_owed"])
            assert sum(map(len, run.rows)) == case["births"]
            assert run.views(reader, 1)[0][1] == expected
    selected = [max(places, key=places.get)] if args.pilot else names
    data = {"second_implementation_matches_per_law": len(cases), "shared_distinctions": pairs, "additional_to_the_tree": sorted(added),
            "places": places, "loose": loose, "round_one": cases,
            "admission": {law: project(pairs, names, loose, selected, law) for law in ("nae", "parity")}}
    data["elapsed_seconds"] = round(time.monotonic() - stamp, 4)
    target = HERE / ("weighted_example_pilot.json" if args.pilot else "weighted_example.json")
    target.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
