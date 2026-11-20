"""Exact minimum parity changes and physical reach at one declared stage."""
import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
from statistics import median


HERE = Path(__file__).resolve().parent
ARTIFACTS = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
READINGS = ("additional_flips", "least_distinction_reach_steps", "greatest_distinction_reach_steps",
            "least_holder_reach_steps", "greatest_holder_reach_steps")
MATCH_READINGS = (*READINGS, "minimum_repair_ties", "ties_using_outside")
POLICIES = ("loose_free", "other_loose_distinctions_pinned")


class HolderNetwork:
    def __init__(self, stars):
        self.stars = tuple(tuple(row) for row in stars)
        self.n = len(self.stars)
        self.outside = self.n
        holders = defaultdict(list)
        for j, row in enumerate(self.stars):
            if len(set(row)) != len(row):
                raise ValueError(f"repeated distinction at junction {j}")
            for distinction in row:
                holders[distinction].append(j)
        self.held = dict(holders)
        self.all_steps = [[] for _ in range(self.n + 1)]
        self.physical_steps = [[] for _ in range(self.n + 1)]
        self.loose_at = [[] for _ in range(self.n)]
        self.ends = {}
        for name, endpoints in holders.items():
            if len(endpoints) not in (1, 2):
                raise ValueError(f"distinction {name} has {len(endpoints)} holders")
            u = endpoints[0]
            v = endpoints[1] if len(endpoints) == 2 else self.outside
            self.ends[name] = (u, v)
            self.all_steps[u].append((v, name))
            self.all_steps[v].append((u, name))
            if v != self.outside:
                self.physical_steps[u].append((v, name))
                self.physical_steps[v].append((u, name))
            else:
                self.loose_at[u].append(name)

    @staticmethod
    def search(steps, seeds, deleted=None):
        lengths = [None] * len(steps)
        order = list(dict.fromkeys(seeds))
        for q in order:
            lengths[q] = 0
        for u in order:
            for v, name in steps[u]:
                if name != deleted and lengths[v] is None:
                    lengths[v] = lengths[u] + 1
                    order.append(v)
        return lengths, order

    def physical_distances(self, seeds):
        if not seeds or any(not 0 <= x < self.n for x in seeds):
            raise ValueError("physical distance needs actual junction seeds")
        return self.search(self.physical_steps, seeds)[0]

    def offset(self, distinction, from_anchors):
        values = [from_anchors[v] for v in self.held[distinction] if from_anchors[v] is not None]
        return min(values) if values else None

    def shortest_responses(self, distinction, lengths, pinned=False):
        steps = self.physical_steps if pinned else self.all_steps
        start, end = self.ends[distinction]
        left, order = self.search(steps, (start,), distinction)
        total = left[end]
        if total is None:
            return response(None, 0, 0)
        right, _ = self.search(steps, (end,), distinction)
        size = len(steps)
        count, external = [0] * size, [0] * size
        near = [[None] * size, [None] * size]
        far = [[None] * size, [None] * size]
        near_prev = [[None] * size, [None] * size]
        far_prev = [[None] * size, [None] * size]
        count[start] = 1
        external[start] = int(start == self.outside)
        near[0][start] = near[1][start] = far[0][start] = far[1][start] = 0

        for u in order:
            if not count[u] or right[u] is None or left[u] + right[u] != total:
                continue
            for v, name in steps[u]:
                if name == distinction or left[v] != left[u] + 1 or right[v] is None or left[v] + right[v] != total:
                    continue
                # Outside can participate in the parity equation calculation;
                # it has no position or distance in the physical meeting graph.
                holder_radius = 0 if v == self.outside else lengths[v]
                distinction_radius = 1 + min(lengths[a] for a in (u,v) if a != self.outside)
                count[v] += count[u]
                external[v] += count[u] if v == self.outside else external[u]
                for j, radius in enumerate((holder_radius, distinction_radius)):
                    assert radius is not None
                    next_near, next_far = max(near[j][u], radius), max(far[j][u], radius)
                    if near[j][v] is None or next_near < near[j][v]:
                        near[j][v] = next_near
                        near_prev[j][v] = (u, name)
                    if far[j][v] is None or next_far > far[j][v]:
                        far[j][v] = next_far
                        far_prev[j][v] = (u, name)

        def restore(predecessor):
            at = end
            chosen = []
            while at != start:
                at, name = predecessor[at]
                chosen.append(name)
            chosen.reverse()
            assert len(chosen) == total and self.is_allowed_change([distinction, *chosen])
            return chosen

        return response(total, count[end], external[end],
                        [(near[0][end], far[0][end]), (near[1][end], far[1][end])],
                        [(restore(near_prev[0]), restore(far_prev[0])), (restore(near_prev[1]), restore(far_prev[1]))])

    def loose_response(self, distinction):
        start = self.held[distinction][0]
        colocated = [name for name in self.loose_at[start] if name != distinction]
        if colocated:
            witness = [colocated[0]]
            return response(1, len(colocated), len(colocated), [(0,0), (1,1)], [(witness,witness)]*2)
        pending = deque([start])
        depth, count, parent = {start: 0}, {start: 1}, {}
        nearest = None
        ties = 0
        witness = None
        while pending:
            u = pending.popleft()
            if nearest is not None and depth[u] > nearest:
                break
            if u != start and self.loose_at[u]:
                nearest = depth[u]
                ties += count[u] * len(self.loose_at[u])
                if witness is None:
                    witness = [self.loose_at[u][0]]
                    at = u
                    while at != start:
                        at, name = parent[at]
                        witness.append(name)
                    witness.reverse()
                continue
            if nearest is not None:
                continue
            for v, name in self.physical_steps[u]:
                if v not in depth:
                    depth[v] = depth[u] + 1
                    count[v] = 0
                    parent[v] = (u, name)
                    pending.append(v)
                if depth[v] == depth[u] + 1:
                    count[v] += count[u]
        if nearest is None:
            return response(None, 0, 0)
        assert self.is_allowed_change([distinction, *witness])
        return response(nearest+1, ties, ties, [(nearest,nearest), (nearest+1,nearest+1)], [(witness,witness)]*2)

    def is_allowed_change(self, changed):
        changed = set(changed)
        odd = set()
        for e in changed:
            odd.symmetric_difference_update(self.held[e])
        return not odd

    def profile(self, distinction):
        if len(self.held[distinction]) == 1:
            free, pinned = self.loose_response(distinction), response(None, 0, 0)
        else:
            lengths = self.physical_distances(self.held[distinction])
            free = self.shortest_responses(distinction, lengths)
            pinned = self.shortest_responses(distinction, lengths, pinned=True)
        same = None if free["additional_flips"] is None else pinned["additional_flips"] == free["additional_flips"]
        if same is True:
            assert pinned["minimum_repair_ties"] == free["minimum_repair_ties"] - free["ties_using_outside"]
        elif same is False:
            assert free["ties_using_outside"] == free["minimum_repair_ties"]
        return {"distinction": distinction, "physical_holders": self.held[distinction],
                "holder_count": len(self.held[distinction]),
                "loose_free": free, "other_loose_distinctions_pinned": pinned,
                "same_min_when_other_loose_pinned": same}


def response(total, ties, outside, reaches=None, witnesses=None):
    result = {"additional_flips": total, "minimum_repair_ties": ties, "ties_using_outside": outside}
    if reaches is None:
        reaches = [(None,None)] * 2
        witnesses = [(None,None)] * 2
    assert outside <= ties and (total is None) == (ties == 0)
    for how, (low,high), (low_witness,high_witness) in zip(("holder", "distinction"), reaches, witnesses):
        assert low is None or low <= high
        result[f"least_{how}_reach_steps"] = low
        result[f"greatest_{how}_reach_steps"] = high
        result[f"least_{how}_reach_witness"] = low_witness
        result[f"greatest_{how}_reach_witness"] = high_witness
    return result


def star_rows(n, shared, loose=()):
    """Literal test controls with one separately named distinction per occurrence."""
    rows = [[] for _ in range(n)]
    for e, ends in enumerate([*shared, *((u,) for u in loose)]):
        for u in ends:
            rows[u].append(e)
    return rows


def literal_profile(stars, target, pinned=False):
    """Independent finite oracle by allowed assignments and physical Floyd distances."""
    memberships = defaultdict(list)
    for j, star in enumerate(stars):
        for e in star:
            memberships[e].append(j)
    roots = memberships[target]
    n = len(stars)
    limit = n + 1
    distance = [[limit] * n for _ in stars]
    for u in range(n):
        distance[u][u] = 0
    for ends in memberships.values():
        if len(ends) == 2:
            u, v = ends
            distance[u][v] = distance[v][u] = 1
    for q in range(n):
        for u in range(n):
            for v in range(n):
                distance[u][v] = min(distance[u][v], distance[u][q] + distance[q][v])
    pairs = {e: set() for e in memberships}
    for star in stars:
        for first,second in combinations(star,2):
            pairs[first].add(second)
            pairs[second].add(first)
    distinction_distance = {target: 0}
    queue = [target]
    for e in queue:
        for other in pairs[e] - distinction_distance.keys():
            distinction_distance[other] = distinction_distance[e] + 1
            queue.append(other)
    free = [e for e, ends in memberships.items() if e != target and (not pinned or len(ends) == 2)]
    for n_extra in range(len(free) + 1):
        holder_reaches, distinction_reaches, uses_outside = [], [], 0
        for extra in combinations(free, n_extra):
            marked = {target, *extra}
            if any(sum(e in marked for e in row) % 2 for row in stars):
                continue
            reached = {u for e in marked for u in memberships[e]}
            radius = max(min(distance[root][u] for root in roots) for u in reached)
            assert radius < limit
            holder_reaches.append(radius)
            distinction_reaches.append(max(distinction_distance[e] for e in extra))
            uses_outside += any(len(memberships[e]) == 1 for e in marked)
        if holder_reaches:
            return (n_extra, len(holder_reaches), min(holder_reaches), max(holder_reaches),
                    min(distinction_reaches), max(distinction_reaches), uses_outside)
    return None, 0, None, None, None, None, 0


def controls():
    key_fields = ("additional_flips", "minimum_repair_ties", "least_holder_reach_steps", "greatest_holder_reach_steps",
                  "least_distinction_reach_steps", "greatest_distinction_reach_steps", "ties_using_outside")
    checked = 0

    def check(stars):
        nonlocal checked
        network = HolderNetwork(stars)
        for distinction in network.held:
            measured = network.profile(distinction)
            for pinned, key in ((False, "loose_free"), (True, "other_loose_distinctions_pinned")):
                expected = literal_profile(stars, distinction, pinned)
                assert tuple(measured[key][k] for k in key_fields) == expected, (stars, distinction, key)
                for middle in ("least_holder_reach_witness", "greatest_holder_reach_witness",
                               "least_distinction_reach_witness", "greatest_distinction_reach_witness"):
                    witness = measured[key][middle]
                    if witness is not None:
                        assert len(set(witness)) == len(witness) and distinction not in witness
                        assert network.is_allowed_change([distinction, *witness])
                checked += 1
        return network.profile(0)

    parallel = check(star_rows(2, [(0, 1), (0, 1), (0, 1)]))
    assert tuple(parallel["loose_free"][k] for k in key_fields) == (1, 2, 0, 0, 1, 1, 0)
    bridge = check(star_rows(2, [(0, 1)]))
    assert bridge["loose_free"]["additional_flips"] is None
    two_tied_reaches = check(star_rows(3, [(0, 1), (0, 2), (1, 2)], [0, 1]))
    assert tuple(two_tied_reaches["loose_free"][k] for k in key_fields) == (2, 2, 0, 1, 1, 1, 1)
    assert tuple(two_tied_reaches["other_loose_distinctions_pinned"][k] for k in key_fields) == (2, 1, 1, 1, 1, 1, 0)
    five_cycle_with_branch = [(0,1), (1,2), (2,3), (3,4), (4,0), (0,5), (5,6)]
    tied_distinction_reaches = check(star_rows(7, five_cycle_with_branch, [1,6]))
    assert tuple(tied_distinction_reaches["loose_free"][k] for k in key_fields) == (4, 2, 2, 2, 2, 3, 1)
    rim = [(u, (u + 1) % 6) for u in range(6)]
    boundary_shortcut = check(star_rows(6, rim, [0, 1]))
    assert boundary_shortcut["loose_free"]["additional_flips"] == 2
    assert boundary_shortcut["other_loose_distinctions_pinned"]["additional_flips"] == 5
    separate = check(star_rows(7, [(0, 1), (0, 2), (2, 3), (5, 6)], [1, 3, 4, 5, 6]))
    assert separate["loose_free"]["greatest_distinction_reach_steps"] == 3
    renaming_stars = star_rows(7, five_cycle_with_branch, [1,6])
    renaming = {e: e*11+17 for e in range(9)}
    transported = HolderNetwork([[renaming[e] for e in reversed(star)] for star in renaming_stars[::-1]]).profile(renaming[0])
    for policy in POLICIES:
        assert all(transported[policy][key] == tied_distinction_reaches[policy][key] for key in key_fields)

    rng = Random(202611190317)
    for n in range(2, 7):
        possible = list(combinations(range(n), 2))
        for _ in range(40):
            shared = [rng.choice(possible) for _ in range(rng.randrange(1, 7))]
            loose = [rng.randrange(n) for _ in range(rng.randrange(4))]
            check(star_rows(n, shared, loose))
    return {"literal_probe_policy_checks": checked, "seeded_tiny_patterns": 200,
            "parallel": parallel, "bridge": bridge, "holder_tie_control": two_tied_reaches,
            "distinction_tie_control": tied_distinction_reaches,
            "boundary_shortcut": boundary_shortcut, "separate_component": separate, "literal_renaming_check": True}


def summarize(rows):
    out = {}
    for policy in POLICIES:
        present = [row[policy] for row in rows if row[policy]["additional_flips"] is not None]
        metrics = {}
        for key in ("additional_flips", "least_holder_reach_steps", "greatest_holder_reach_steps",
                    "least_distinction_reach_steps", "greatest_distinction_reach_steps", "minimum_repair_ties"):
            values = [row[key] for row in present]
            if values:
                metrics[key] = {"min": min(values), "median": median(values), "max": max(values),
                                "histogram": dict(sorted(Counter(values).items()))}
        out[policy] = {"probes": len(rows), "feasible": len(present), "impossible": len(rows) - len(present),
                       "some_shortest_response_uses_outside": sum(row["ties_using_outside"] > 0 for row in present),
                       "every_shortest_response_uses_outside": sum(row["ties_using_outside"] == row["minimum_repair_ties"] for row in present),
                       "distinction_reach_differs_across_ties": sum(row["least_distinction_reach_steps"] != row["greatest_distinction_reach_steps"] for row in present),
                       "holder_reach_differs_across_ties": sum(row["least_holder_reach_steps"] != row["greatest_holder_reach_steps"] for row in present),
                       "metrics": metrics}
    out["same_min_when_other_loose_pinned"] = sum(row["same_min_when_other_loose_pinned"] is True for row in rows)
    return out


def run(archive, plan):
    output = []
    history = {}
    stage_key = None
    for row in sorted(plan, key=lambda row: (row["case"], row["age"], row["cohort"])):
        case = archive["cases"][row["case"]]
        stage = case["stages"][str(row["age"])]
        key = (row["case"], row["age"])
        if key != stage_key:
            graph = HolderNetwork(stage["stars"])
            cache = {}
            stage_key = key
            assert graph.n == stage["junction_count"] and len(graph.ends) == stage["distinction_count"]
        if row.get("anchors"):
            physical_offsets = graph.physical_distances(row["anchors"])
        else:
            physical_offsets = None
        loose_control = row.get("distinctions") == "all_growing_end_loose"
        if loose_control:
            selected = sorted({e for names in stage["loose"].values() for e in names})
            assert set(selected) == {e for e, v in graph.held.items() if len(v) == 1}
        else:
            selected = row["distinctions"]
        descriptor = row.get("probe_metadata", {})
        profiles = []
        for probe in selected:
            if loose_control:
                resolved = graph.profile(probe)
            else:
                if probe not in cache:
                    cache[probe] = graph.profile(probe)
                resolved = dict(cache[probe])
                resolved.update(descriptor.get(str(probe), {}))
            if physical_offsets is not None:
                resolved["offset_steps"] = graph.offset(probe, physical_offsets)
            profiles.append(resolved)
            if loose_control:
                continue
            key = (row["case"], row["cohort"], probe)
            old = history.get(key)
            if old is not None:
                older_age, older_stars, older_profile = old
                if older_age != row["age"]:
                    assert graph.stars[:len(older_stars)] == older_stars
                    value = resolved["loose_free"]["additional_flips"]
                    older_value = older_profile["loose_free"]["additional_flips"]
                    assert value is None or (older_value is not None and value >= older_value)
                    transition = {"previous_age": older_age}
                    for policy in POLICIES:
                        changes = {}
                        for field in READINGS:
                            before, after = older_profile[policy][field], resolved[policy][field]
                            changes[field] = after - before if before is not None and after is not None else None
                        changes["feasible_before"] = older_profile[policy]["additional_flips"] is not None
                        changes["feasible_after"] = resolved[policy]["additional_flips"] is not None
                        transition[policy] = changes
                    resolved["fixed_distinction_transition"] = transition
            history[key] = (row["age"], graph.stars, resolved)
        by_depth = defaultdict(list)
        for p in profiles:
            if "source_offset" in p:
                by_depth[p["source_offset"]].append(p)
        detail = profiles
        digest = None
        if loose_control:
            digest = sha256(json.dumps(profiles, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            possible = [p for p in profiles if p["loose_free"]["additional_flips"] is not None]
            detail = profiles[:3]
            if possible:
                farthest = max(possible, key=lambda p: p["loose_free"]["greatest_distinction_reach_steps"])
                if farthest not in detail:
                    detail.append(farthest)
        output.append({"case": row["case"], "age": row["age"], "cohort": row["cohort"],
                       "junction_count": graph.n, "distinction_count": len(graph.ends),
                       "size_label": row.get("size_label"), "anchors": row.get("anchors", []),
                       "description": row.get("description"), "probes": detail, "summary": summarize(profiles),
                       "all_probe_profiles_sha256": digest,
                       "summary_by_source_offset": {str(h): summarize(p) for h,p in sorted(by_depth.items())}})
    return output


def frozen_plan(archive):
    plan = []

    def cohort(tag, age, label, distinctions, anchors, offsets=None):
        item = {"case": tag, "age": age, "cohort": label, "size_label": age+1,
                "distinctions": distinctions, "anchors": anchors}
        if offsets is not None:
            item["probe_metadata"] = {str(e): {"coordinate_index": i, "source_offset": offsets[i]}
                                      for i,e in enumerate(distinctions)}
        plan.append(item)

    for tag, case in archive["cases"].items():
        initial = HolderNetwork(case["stages"]["0"]["stars"])
        roles = case["input"]["roles"]
        path = roles["background"]
        anchors = roles["anchors"]
        seam = roles["seams"]
        rings, ring_edges = roles["rings"], roles["ring_edges"]
        assert len(rings) == len(ring_edges)
        if path:
            assert len(path) == 17 and len(anchors) == 16
            path_seams = seam or [path[4]]
            positions = [path.index(j) for j in path_seams]
            offsets = [min(abs(i-s) for i in (k,k+1) for s in positions) for k in range(16)]
            assert all(set(initial.held[e]) == set(pair) for e,pair in zip(anchors,zip(path,path[1:])))
        for copy, names in zip(rings, ring_edges):
            assert len(copy) == len(names) == 5
            assert all(set(initial.held[e]) == set(pair) for e,pair in zip(names,zip(copy,copy[1:]+copy[:1])))

        for key in case["stages"]:
            age = int(key)
            if path:
                cohort(tag, age, "original_path", anchors, path_seams, offsets)
            for i, (copy, names) in enumerate(zip(rings, ring_edges)):
                ring_offsets = [min(e, (e+1)%5, 5-e, 5-((e+1)%5)) for e in range(5)]
                cohort(tag, age, f"original_ring_{i}", names, [copy[0]], ring_offsets)
            cohort(tag, age, "growing_end_loose", "all_growing_end_loose", [])
    return plan


def matched_comparisons(rows):
    indexed = {(r["case"], r["age"], r["cohort"]): r["probes"] for r in rows}
    pairs = [(tag,"original_path","B","original_path") for tag in ("J0","J1","J2","T4","T8","C1")]
    pairs.append(("J1","original_path","C1","original_path"))
    pairs.extend((f"J{k}","original_ring_0",f"R{k}","original_ring_0") for k in range(3))
    pairs.extend((tag,f"original_ring_{copy}",ref,"original_ring_0")
                 for tag in ("T4","T8") for copy in range(2) for ref in ("R1","J1"))
    comparisons = []
    for a, cohort_a, b, cohort_b in pairs:
        for tag, age, source_cohort in indexed:
            if (tag, source_cohort) != (a, cohort_a) or (b, age, cohort_b) not in indexed:
                continue
            left, right = indexed[(a, age, cohort_a)], indexed[(b, age, cohort_b)]
            columns = defaultdict(lambda: defaultdict(Counter))
            for first, second in zip(left, right, strict=True):
                assert first["coordinate_index"] == second["coordinate_index"]
                h = first["source_offset"]
                context = "near" if h == 0 else "far" if h >= 3 else "intermediate"
                for policy in POLICIES:
                    values = [(field, first[policy][field], second[policy][field]) for field in MATCH_READINGS]
                    for field, x, y in values:
                        step = x-y if x is not None and y is not None else "both_infeasible" if x is y else "one_infeasible"
                        for label in ("all", context, f"h={h}"):
                            columns[label][policy][(field,step)] += 1
            comparisons.append({"case": a, "baseline": b, "age": age, "size": age+1,
                                "cohort": cohort_a, "baseline_cohort": cohort_b,
                                "matched_probes": len(left),
                                "deltas_by_source_offset": {
                                    label: {policy: [{"reading": field,"delta": delta,"count": count}
                                                     for (field,delta),count in measures.items()]
                                            for policy,measures in policies.items()}
                                    for label, policies in columns.items()}})
    return comparisons


def original_mark_certificate(archive, rows):
    checked = {}
    for tag, case in archive["cases"].items():
        source = HolderNetwork(case["stages"]["0"]["stars"])
        initial_neighborhoods = [{v for v,e in row} for row in source.physical_steps[:source.n]]
        assert all(len(initial_neighborhoods[u]) == len(source.physical_steps[u]) for u in range(source.n))
        assert all(source.loose_at)
        original_wedges = Counter(tuple(sorted(pair)) for row in initial_neighborhoods for pair in combinations(row,2))
        # No source 3- or 4-cycle, so every two-step meeting gives one actual child.
        assert all(count == 1 and v not in initial_neighborhoods[u] for (u,v),count in original_wedges.items())
        first = case["stages"]["1"]
        first_pairs = Counter(tuple(sorted(parents)) for parents in first["parent_sets"].values() if len(parents) >= 2)
        assert first_pairs == original_wedges
        first_incidence = HolderNetwork(first["stars"])
        assert all(len(first_incidence.held[e]) == 2 for labels in source.loose_at for e in labels)
        confirmed = 0
        for row in rows:
            if row["case"] != tag or not row["cohort"].startswith("original"):
                continue
            for probe in row["probes"]:
                u,v = source.held[probe["distinction"]]
                observed = probe["loose_free"]
                assert probe["source_offset"] == probe["offset_steps"]
                if row["age"] == 0:
                    count = len(source.loose_at[u])*len(source.loose_at[v])
                    assert (observed["additional_flips"], observed["minimum_repair_ties"], observed["ties_using_outside"]) == (2,count,count)
                    pinned = probe[POLICIES[1]]
                    assert pinned["additional_flips"] == (4 if row["cohort"].startswith("original_ring") else None)
                    assert (observed["least_distinction_reach_steps"], observed["greatest_distinction_reach_steps"]) == (1,1)
                    assert (observed["least_holder_reach_steps"], observed["greatest_holder_reach_steps"]) == (0,0)
                else:
                    count = len(initial_neighborhoods[u])+len(initial_neighborhoods[v])-2
                    assert (observed["additional_flips"], observed["minimum_repair_ties"], observed["ties_using_outside"]) == (3,count,0)
                    assert probe["same_min_when_other_loose_pinned"]
                    assert (observed["least_distinction_reach_steps"], observed["greatest_distinction_reach_steps"]) == (2,2)
                    assert (observed["least_holder_reach_steps"], observed["greatest_holder_reach_steps"]) == (1,1)
                confirmed += 1
        checked[tag] = {"original_marks_at_all_ages_checked": confirmed, "original_two_step_meetings": len(original_wedges),
                        "sole_child_per_original_two_step_meeting": True, "source_triangle_and_four_cycle_free": True,
                        "all_source_loose_distinctions_consumed_at_first_round": True}
    return checked


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stages", type=Path, default=ARTIFACTS / "stages.json")
    p.add_argument("--plan", type=Path)
    p.add_argument("--control-only", action="store_true")
    args = p.parse_args()
    check = controls()
    if args.control_only:
        print(check["literal_probe_policy_checks"], "literal probe and policy comparisons")
        return
    source = args.stages.read_bytes()
    archive = json.loads(source)
    if args.plan is not None:
        plan_bytes = args.plan.read_bytes()
        plan = json.loads(plan_bytes)["measurements"]
    else:
        plan = frozen_plan(archive)
        plan_bytes = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    results = run(archive, plan)
    comparisons = matched_comparisons(results) if args.plan is None else None
    certificate = original_mark_certificate(archive, results) if args.plan is None else None
    payload = {"source_sha256": sha256(source).hexdigest(), "probe_plan_sha256": sha256(plan_bytes).hexdigest(),
               "program_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "controls": check, "results": results, "matched_comparisons": comparisons,
               "original_mark_formula_checks": certificate}
    (ARTIFACTS / "flip_results.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    print(len(results), sum(row["summary"]["loose_free"]["probes"] for row in results), "cohorts and exact probes")


if __name__ == "__main__":
    main()
