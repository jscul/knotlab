"""Matched activity, simultaneous reference shifts, and local two-ring competition."""

from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path
import sys

import growth

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
WORLD = ROOT / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world"
sys.path.insert(0, str(WORLD))
from world_bonds import AnchoredCuts, WiredStage


def activity(stars, state, reference=()):
    difference = frozenset(state) ^ frozenset(reference)
    return frozenset(v for v, row in enumerate(stars) if not difference.isdisjoint(row))


def invariant_plan(plan):
    return tuple((b.parents, b.demand, b.baseline, b.fresh) for b in plan.births)


def replay_action_vector(stars, occupied, table):
    seen = growth.plan_round(stars, occupied, table)
    actions = {tuple(g["parents"]): g["action"] for g in seen.details["candidate_groups"]}
    actions.update({b.parents: b.action for b in seen.births if len(b.parents) == 1})
    replay = growth.plan_round(stars, (), ("P", "P"), recorded_actions=actions)
    assert seen.status == replay.status == "extend"
    assert invariant_plan(seen) == invariant_plan(replay)
    actual = growth.realize_round(seen)
    blank = growth.realize_round(replay)
    assert actual["stars"] == blank["stars"] and not blank["occupied"]
    return actual


def born_near(frame, ring):
    return sum(bool(set(b["parents"]) & ring) for b in frame["births"])


def source_two_rings(gap):
    # The original path and ring funding formula applies at each of these gaps.
    background = list(range(17))
    meetings = list(zip(background, background[1:]))
    rings = [[4, 17, 18, 19, 20], [4+gap, 21, 22, 23, 24]]
    edges = []
    for row in rings:
        start = len(meetings)
        meetings.extend(zip(row, row[1:] + row[:1]))
        edges.append(list(range(start, start+5)))
    adjacent = [set() for _ in range(25)]
    for u, v in meetings:
        adjacent[u].add(v)
        adjacent[v].add(u)
    spares = {0, 1, 15, 16, rings[0][2], rings[1][2]}
    sizes = [len(row) + sum(len(adjacent[u])-1 for u in row) + (v in spares)
             for v, row in enumerate(adjacent)]
    spec = {"id": f"near{gap}", "sizes": sizes, "meetings": meetings,
            "roles": {"background": background, "anchors": list(range(16)), "seams": [4, 4+gap],
                      "rings": rings, "ring_edges": edges, "ring_spares": [[18], [22]],
                      "background_spares": [0, 1, 15, 16]}}
    return spec


def ring_balls(stars, roots):
    """Change of cutoff only. Enumerate every bond of size <=6 through each root."""
    stage = WiredStage(stars)
    needed = {stage.bundle_of[b] for b in roots}
    included = [set(roots) for _ in range(5)]
    for block in stage.blocks:
        local_ids = {g: i for i, g in enumerate(block)}
        query = needed & set(block)
        if not query:
            continue
        count, links = stage.local_edges(block)
        for g in query:
            search = AnchoredCuts(count, links)
            prices = search.through(local_ids[g], 6)
            for i, cost in enumerate(prices):
                for r in range(1, 6):
                    if cost <= r+1:
                        included[r-1].update(stage.bundles[block[i]])
    return {str(i): {"distinctions": len(ball),
                     "knots": len({v for b in ball for v in stage.owner[b]})}
            for i, ball in enumerate(included, 1)}


def source_qualified(stars):
    neighbors = [set() for _ in stars]
    owner = defaultdict(list)
    for v, row in enumerate(stars):
        for bit in row:
            owner[bit].append(v)
    for row in owner.values():
        if len(row) == 2:
            u, v = row
            neighbors[u].add(v)
            neighbors[v].add(u)
    local = Counter()
    for center in neighbors:
        local.update(tuple(sorted(pair)) for pair in combinations(center, 2))
    plan = growth.plan_round(stars)
    assert plan.status == "extend"
    groups = {tuple(g["parents"]) for g in plan.details["candidate_groups"]}
    assert groups == set(local) and all(n == 1 for n in local.values())
    # Every source holder has >=2 loose bits. Its parity projection is exactly the
    # whole row: any values on its meetings extend at its neighbors by a loose.
    assert all(len(row) >= 2 for row in plan.stage.loose.values())
    assert len(plan.stage.loose) == len(stars)
    return groups


def close_pair(gap, archived):
    spec = source_two_rings(gap)
    if gap in (4, 8):
        other = archived["T"+str(gap)]
        assert spec["sizes"] == other["sizes"] and list(map(list, spec["meetings"])) == other["meetings"]
    stars = growth.predecessor().source_stars(spec)
    groups = source_qualified(stars)
    roots = [set(row) for row in spec["roles"]["ring_edges"]]
    donors, receivers = [set(v) for v in spec["roles"]["rings"]]
    common = sorted(p for p in groups if donors.intersection(p) and receivers.intersection(p))
    rows = {}
    for a, b in product((0, 1), repeat=2):
        occupied = (roots[0] if a else set()) ^ (roots[1] if b else set())
        present = activity(stars, occupied)
        for table in ("PP", "PV"):
            frame = replay_action_vector(stars, occupied, table)
            expected = sum(len(p)-1 for p in groups if present.intersection(p))
            if table == "PV":
                assert frame["vetoed_multi"] == expected
            key = f"{table}/{a}{b}"
            rows[key] = {"new_knots": len(frame["births"]), "distinctions": frame["distinction_count"],
                         "receiver_adjacent_births": born_near(frame, receivers),
                         "receiver_balls": ring_balls(frame["stars"], roots[1])}
    def cross(key):
        return rows["PV/11"][key] - rows["PV/01"][key] - rows["PV/10"][key] + rows["PV/00"][key]
    assert cross("new_knots") == -len(common)
    assert bool(common) == (gap <= 2)
    if gap == 2:
        assert len(common) == 1
    return {"gap": gap, "common_proposals": common, "birth_interaction": cross("new_knots"),
            "receiver_adjacent_interaction": cross("receiver_adjacent_births"), "conditions": rows}


def matched_activity(spec):
    stars = growth.predecessor().source_stars(spec)
    rim = set(spec["roles"]["ring_edges"][0])
    ring_knots = set(spec["roles"]["rings"][0])
    base = growth.plan_round(stars)
    pairs = {d for v in ring_knots for d in base.stage.loose[v][:2]}
    assert len(pairs) == 10 and not pairs & rim
    assert activity(stars, rim) == activity(stars, pairs) == ring_knots
    reports = {}
    for table in product(growth.ACTIONS, repeat=2):
        regular = replay_action_vector(stars, rim, table)
        outside = replay_action_vector(stars, pairs, table)
        assert regular["stars"] == outside["stars"]
        for x in (rim, pairs, set()):
            for translation in (rim, pairs, rim ^ pairs):
                assert activity(stars, x) == activity(stars, x ^ translation, translation)
                translated_difference = (x ^ translation) ^ translation
                assert invariant_plan(growth.plan_round(stars, x, table)) == invariant_plan(
                    growth.plan_round(stars, translated_difference, table))
        reports["".join(table)] = {"new_knots": len(regular["births"]), "width": regular["distinction_count"],
                                   "geometry_matches": True, "new_occupied_raw_ring": len(regular["new_occupied"]),
                                   "new_occupied_local_pairs": len(outside["new_occupied"])}
    cases = {}
    for name, state in (("rim", rim), ("loose_pairs", pairs)):
        result = growth.grow(stars, state, ("P", "V"), rounds=5,
                             caps={"junctions":6000, "distinctions":32000})
        levels = []
        for j, frame in result["stages"].items():
            loose = {d for seq in frame["loose"].values() for d in seq}
            count = len(loose.intersection(frame["occupied"]))
            assert count == (10 if name == "loose_pairs" else 0)
            levels.append([int(j), frame["junction_count"], frame["distinction_count"], count])
        cases[name] = {"levels_age_knots_distinctions_active_loose": levels,
                       "termination": result["termination"]["status"]}
    return {"first_round_by_table": reports, "later_under_PV": cases, "tested_joint_reference_shifts": 144}


def physical_motion_vs_growth(spec):
    sys.path.insert(0, str(ROOT/"experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion"))
    from nearness import ReturnRule, co_knotted_pairs
    source = growth.predecessor().source_stars(spec)
    stars = growth.step(source)["stars"]
    recovered = ReturnRule(co_knotted_pairs(stars))
    lookup = {frozenset(row):i for i,row in enumerate(recovered.stars)}
    thru = [lookup[frozenset(source[i])] for i in (0, 1, 2)]
    pulse = recovered.packet(thru)
    plan = growth.plan_round(stars, pulse)
    assert len(pulse) == 4 and len(plan.details["hot_live_parents"]) == 1
    results = {}
    for table in product(growth.ACTIONS, repeat=2):
        quiet = growth.step(stars, (), table)
        loaded = growth.step(stars, pulse, table)
        assert loaded["status"] == quiet["status"] == "extend"
        # Postponing the flip to the same four old shared distinctions remains allowed.
        assert all(len(pulse.intersection(row)) % 2 == 0 for row in quiet["stars"])
        changed = (quiet["junction_count"], quiet["distinction_count"]) != (loaded["junction_count"], loaded["distinction_count"])
        assert changed == (table[0] != table[1])
        result = {"blank": [quiet["junction_count"], quiet["distinction_count"]],
                  "pulse": [loaded["junction_count"], loaded["distinction_count"]], "structure_changed": changed}
        if table == ("P", "-"):
            steps = [growth.step(f["stars"], f["occupied"], table) for f in (quiet, loaded)]
            result["following_status"] = [f["status"] for f in steps]
            assert result["following_status"] == ["extend", "stall"]
        results["".join(table)] = result
    return {"pulse": sorted(pulse), "tables": results}


def main():
    source = json.loads((WORLD/"inputs.json").read_text())
    cases = {s["id"]:s for s in source["cases"]}
    result = {"separation": [close_pair(gap, cases) for gap in (1, 2, 3, 4, 8)],
              "same_active_holders": matched_activity(cases["J1"]),
              "one_allowed_four_change": physical_motion_vs_growth(cases["R0"])}
    (DATA/"specificity.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print("First-round interaction by separation:", [(row["gap"], row["birth_interaction"])
                                                     for row in result["separation"]])
    print("Minimum change control:", result["one_allowed_four_change"]["tables"]["P-"])


if __name__ == "__main__":
    main()
