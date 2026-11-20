"""Check the examples and the all-age identities on the frozen stage records."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys


TICKET = "EDDY-WORLD-20261119-001"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILY = TICKET + "-E001_world"
sys.path.insert(0, str(ROOT / "experiments" / TICKET / FAMILY))
from world_flip import HolderNetwork


def physical(n, margins, loose):
    stars = [[] for _ in range(n)]
    shared = {}
    name = 0
    for a, b, k in margins:
        shared[a, b] = name
        for x in range(name, name + k):
            stars[a].append(x)
            stars[b].append(x)
        name += k
    tips = {}
    for a, k in loose.items():
        tips[a] = list(range(name, name + k))
        stars[a].extend(tips[a])
        name += k
    return stars, shared, tips


def required(blocks, live):
    # Small-control enumerator. All tested current ends here have at most four holders.
    pair = {frozenset(ab) for row in blocks for ab in combinations(row, 2)}
    valid = []
    for size in range(3, len(live) + 1):
        for group in combinations(live, size):
            g = frozenset(group)
            if all(frozenset(ab) in pair for ab in combinations(g, 2)) and not any(g <= b for b in blocks):
                valid.append(g)
    large = [g for g in valid if not any(g < h for h in valid)]
    return large + [p for p in pair if not any(p <= g for g in large)]


def advance(stars):
    network = HolderNetwork(stars)
    live = {i for i, row in enumerate(network.loose_at) if row}
    blocks = [{w for w, x in row if w in live} for row in network.physical_steps]
    groups = sorted(required(blocks, live), key=lambda g: sorted(g))
    tips = {i: list(network.loose_at[i]) for i in live}
    inputs = [[tips[i].pop(0) for i in sorted(g)] for g in groups]
    parent_lists = [set(g) for g in groups]
    for i in sorted(tips):
        for x in tips[i]:
            inputs.append([x])
            parent_lists.append({i})
    assert len(inputs) >= 2
    child_blocks = [{c for c, row in enumerate(parent_lists) if i in row} for i in live]
    next_groups = required(child_blocks, set(range(len(inputs))))
    demand = Counter(c for g in next_groups for c in g)
    next_id = max(network.held) + 1
    new_stars = [row.copy() for row in stars]
    for c, row in enumerate(inputs):
        count = max(1, 3 - len(row), demand[c])
        new_stars.append(row + list(range(next_id, next_id + count)))
        next_id += count
    return new_stars


def minimum_bond(stars, first, second):
    net = HolderNetwork(stars)
    whole = set(range(net.n + 1))

    def connected(shore):
        start = next(iter(shore))
        reached = {start}
        work = [start]
        for u in work:
            for v, _ in net.all_steps[u]:
                if v in shore and v not in reached:
                    work.append(v)
                    reached.add(v)
        return reached == shore

    best, witnesses = None, []
    for mask in range(1, 1 << net.n):
        inside = {i for i in range(net.n) if mask & (1 << i)}
        crossing = sorted(x for x, (u, v) in net.ends.items() if (u in inside) != (v in inside))
        if first not in crossing or second not in crossing or (best is not None and len(crossing) > best):
            continue
        if connected(inside) and connected(whole - inside):
            if best != len(crossing):
                best, witnesses = len(crossing), []
            witnesses.append(crossing)
    return dict(size=best, witnesses=witnesses)


def free_profile(stars, e):
    profile = HolderNetwork(stars).profile(e)["loose_free"]
    return [profile[key] for key in ("additional_flips", "least_distinction_reach_steps",
                                     "greatest_distinction_reach_steps")]


def source_projections(stars):
    graph = HolderNetwork(stars)
    assert all(len(star) >= 3 for star in stars)
    for omit in range(graph.n + 1):
        seed = next(v for v in range(graph.n + 1) if v != omit)
        reached, run = {seed}, [seed]
        for v in run:
            for w, _ in graph.all_steps[v]:
                if w != omit and w not in reached:
                    reached.add(w)
                    run.append(w)
        assert len(reached) == graph.n


def strict_bond_control():
    margins = [(0, 1, 1), (1, 2, 1), (0, 2, 2), (1, 3, 2), (3, 4, 2), (4, 5, 2)]
    old, _, tips = physical(6, margins, {0: 1, 1: 1, 2: 1, 5: 2})
    source_projections(old)
    new = advance(old)
    e, f = tips[0][0], tips[1][0]
    readings = [minimum_bond(s, e, f) for s in (old, new)]
    assert [r["size"] for r in readings] == [5, 4]
    changes = [free_profile(s, e) for s in (old, new)]
    assert changes == [[2, 2, 2], [2, 1, 1]]
    return dict(old_stars=old, new_stars=new, marks=[e, f], min_bonds=readings, one_mark_changes=changes)


def falling_ties(q):
    length = 2 * q + 5
    stem = 2 * q
    u, v, w = 0, length, length + stem
    margins = [(u, v, 1)] + [(i, i + 1, 2) for i in range(length)]
    chain = [u] + list(range(length + 1, w + 1))
    margins.extend((a, b, 2) for a, b in zip(chain, chain[1:]))
    stars, shared, _ = physical(w + 1, margins, {v: 2, w: 2})
    source_projections(stars)
    mark = shared[u, v]
    profiles = []
    for age in (0, 1, 2):
        profiles.append(free_profile(stars, mark))
        if age < 2:
            stars = advance(stars)
    assert profiles[1] == [2 * q + 4, 2 * q + 2, 2 * q + 2]
    assert profiles[2] == [2 * q + 5, q + 3, q + 3]
    return dict(q=q, age_zero_one_two=profiles, one_round_drop=q - 1)


def frozen_cases():
    folder = ROOT / "artifacts" / TICKET / FAMILY
    cases = json.loads((folder / "stages.json").read_text())["cases"]
    radius_counts = Counter()
    for name, case in cases.items():
        birth_age = {}
        for age_key, stage in case["stages"].items():
            age = int(age_key)
            birth_age.update({v: age for v in stage["born"]})
            assert len(birth_age) == len(stage["stars"])
            network = HolderNetwork(stage["stars"])
            if age == 0:
                assert len(stage["live"]) == network.n
            distances = network.physical_distances(stage["live"])
            assert all(distances[v] == age - birth_age[v] for v in birth_age)
        radius_counts[name] = len(case["stages"])
    profiles = json.loads((folder / "flip_results.json").read_text())
    checks = Counter()
    for row in profiles["results"]:
        for probe in row["probes"]:
            if probe["holder_count"] != 2:
                continue
            age = row["age"]
            modes = ["loose_free", "other_loose_distinctions_pinned"] if age else ["loose_free"]
            for mode in modes:
                answer = probe[mode]
                assert answer["additional_flips"] == (3 if age else 2)
                assert answer["least_distinction_reach_steps"] == answer["greatest_distinction_reach_steps"] == (2 if age else 1)
            checks["positive_age_shared_marks" if age else "source_shared_marks"] += 1
    return dict(all_live_source_and_age_layer_checks=dict(radius_counts), flip_observations=dict(checks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result = dict(strict_bond=strict_bond_control(), falling_shortest_reach=[falling_ties(q) for q in (2, 4, 8, 16)],
                  frozen_cases=frozen_cases())
    out = HERE / "world_theory_controls.json"
    if args.verify:
        assert json.loads(out.read_text()) == result
        print("Verified the strict bond control, four reach drops, all physical ages and all shared flip rows.")
    else:
        out.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
