"""Rooted structural comparisons on the dimension-one, two and three tree starts."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import reduce
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from operator import or_
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "backgrounds.json"
FEEDBACK = ROOT / "experiments/STATE-FEEDS-GROWTH-20261119-001/STATE-FEEDS-GROWTH-20261119-001-E001_feedback"
WORLD = ROOT / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world"
sys.path.insert(0, str(FEEDBACK))
import growth


ARM_LENGTHS = (4, 5, 7)
RINGS = {"zero": (), "one_c2": (2,), "one_c1": (1,), "two_c2_c3": (2, 3)}
CAPS = {"junctions": 2048, "distinctions": 8192}
MAX_AGE = 6
ISO_WORK = 2_000_000
RECODE_SEED = 20261119059


def digest(obj):
    return sha256(json.dumps(obj, separators=(",", ":")).encode()).hexdigest()


def cluster_model():
    spec = spec_from_file_location("pace_cluster_count", WORLD / "fate_series.py")
    model = module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def source(dimension, ring=None):
    meetings, arms, arm_marks = [], [], []
    next_knot = 1
    for length in ARM_LENGTHS:
        arm = [0, *range(next_knot, next_knot + length)]
        next_knot += length
        arms.append(arm)
        arm_marks.append(list(range(len(meetings), len(meetings) + length)))
        meetings.extend(zip(arm, arm[1:]))
    surplus = Counter()
    if dimension == 1:
        surplus[arms[2][-1]] = 1
    elif dimension == 3:
        surplus[arms[0][-2]] = 1
    cycle, ring_marks = [], []
    if ring is not None:
        cycle = [0, *range(next_knot, next_knot + 4)]
        surplus.update(cycle[i] for i in RINGS[ring])
        ring_marks = list(range(len(meetings), len(meetings) + 5))
        meetings.extend((cycle[i], cycle[(i + 1) % 5]) for i in range(5))
        next_knot += 4
    near = [set() for _ in range(next_knot)]
    for a, b in meetings:
        near[a].add(b)
        near[b].add(a)
    degree = [len(row) for row in near]
    demand = [sum(degree[w] - 1 for w in row) for row in near]
    openings = [max(3 - d, demand[v]) + surplus[v] for v, d in enumerate(degree)]
    sizes = [a + b for a, b in zip(degree, openings, strict=True)]
    return {"dimension_of_unattached_background": dimension, "ring_style": ring,
            "meetings": meetings, "sizes": sizes, "arms": arms, "arm_marks": arm_marks,
            "cycle": cycle, "ring_marks": ring_marks, "input_surplus": dict(surplus),
            "initial_demand": demand, "initial_openings": openings}


def candidates(stars):
    plan = growth.plan_round(stars, (), ("P", "V"))
    assert plan.status == "extend", plan.status
    return {tuple(rec["parents"]) for rec in plan.details["candidate_groups"]}


def qualified(spec, model):
    mathematical = model.Source(spec)
    assert list(mathematical.demand) == spec["initial_demand"]
    assert mathematical.opens == spec["initial_openings"]
    stars = growth.predecessor().source_stars(spec)
    expected = {pair for group in mathematical.blocks for pair in combinations(group, 2)}
    assert candidates(stars) == expected
    # Any old star is a minimal cut because all other knots each have an
    # opening to the exterior. Even parity is then its exact projection.
    assert min(mathematical.opens) >= 1
    assert all(growth.predecessor().canonical_projection((0,) * len(row)) for row in stars)
    return stars, mathematical


def traced(stars, occupied, through):
    frame = growth.grow(stars, occupied, ("P", "V"), rounds=0)["stages"]["0"]
    frames = {0: frame}
    for age in range(1, through + 1):
        following = growth.step(frame["stars"], frame["occupied"], ("P", "V"), caps=CAPS)
        if following["status"] != "extend":
            keys = ("status", "planned_total_knots", "planned_total_distinctions",
                    "planned_total_distinctions_lower", "shortages")
            return frames, {"last_age": age - 1, **{k: following[k] for k in keys if k in following}}
        assert not following["new_occupied"] and sorted(following["occupied"]) == sorted(occupied)
        frame = frames[age] = following
    return frames, {"status": "age_limit", "last_age": through}


def bare_certificate(dimension, model, through):
    spec = source(dimension)
    stars, mathematical = qualified(spec, model)
    assert len(spec["meetings"]) == len(stars) - 1  # source connected, hence a tree
    pieces = mathematical.pieces()
    assert len(pieces) == 2 and all(row["rank"] == 0 and row["rays"] > 0 for row in pieces)
    assert [row["rays"] for row in pieces] == {1: [1, 1], 2: [1, 2], 3: [1, 3]}[dimension]
    for row in pieces:
        row["ray_hosts"] = {v: mathematical.spares[v] * max(0, 3 - mathematical.opens[v])
                            for v in row["point_ids"]
                            if mathematical.spares[v] and mathematical.opens[v] < 3}
    frames, stop = traced(stars, (), through)
    exact_births = mathematical.count(mathematical.nodes, n=through + 1)
    assert [len(f["born"]) for f in frames.values()] == exact_births[:len(frames)]
    return {"source": spec, "pieces": pieces, "projected_source_knots": len(stars),
            "max_source_arity": max(map(len, stars)),
            "source_K1_K3_kernel_checks": sum(len(row) <= 7 for row in stars),
            "cluster_counts_and_literal_births": exact_births[:len(frames)], "termination": stop}


def ball_distances(adjacency, starts):
    depth = {v: 0 for v in starts}
    waiting = list(starts)
    for v in waiting:
        for u in adjacency[v]:
            if u not in depth:
                waiting.append(u)
                depth[u] = depth[v] + 1
    return depth


def incidence(stars):
    full = defaultdict(list)
    for v, star in enumerate(stars):
        for bit in star:
            knot, distinction = 2 * v, 2 * bit + 1
            full[knot].append(distinction)
            full[distinction].append(knot)
    return {v: tuple(sorted(row)) for v, row in sorted(full.items())}


def induced(adjacency, chosen):
    return {v: tuple(u for u in adjacency[v] if u in chosen) for v in sorted(chosen)}


def peel_profiles(frames, source_size):
    """Rebuild age and old ancestry from each literal growing end."""
    actual_age = [0] * source_size
    actual_origin = [1 << v for v in range(source_size)]
    result = {}
    for age, stage in frames.items():
        if age:
            for v in stage["born"]:
                assert v == len(actual_age)
                actual_age.append(age)
                actual_origin.append(reduce(or_, (actual_origin[p] for p in stage["parent_sets"][v]), 0))
        adjacent = incidence(stage["stars"])
        open_counts = {v: sum(len(adjacent[d]) == 1 for d in row) for v, row in adjacent.items() if v % 2 == 0}
        active = tuple(v for v, n in open_counts.items() if n)
        distance = ball_distances(adjacent, active)
        current_age = distance[0] // 2
        assert current_age == age
        ages = {v: current_age - distance[v] // 2 for v in open_counts}
        assert [ages[2 * v] for v in range(len(actual_age))] == actual_age
        origins = {}
        for v in sorted(open_counts, key=lambda w: (ages[w], w)):
            if ages[v] == 0:
                origins[v] = 1 << (v // 2)
                continue
            old = {w for d in adjacent[v] for w in adjacent[d] if ages[w] == ages[v] - 1}
            origins[v] = reduce(or_, (origins[w] for w in old), 0)
        assert [origins[2 * v] for v in range(len(actual_origin))] == actual_origin
        nearest = {}
        for v in range(source_size):
            steps = ball_distances(adjacent, (2 * v,))
            cutoff = min(steps[u] for u in active)
            nearest[v] = (cutoff // 2, {u: open_counts[u] for u in active if steps[u] == cutoff})
            assert cutoff % 2 == 0 and cutoff // 2 == age
        result[age] = {"adjacent": adjacent, "open_counts": open_counts, "origins": origins,
                       "nearest": nearest, "seam_distance": ball_distances(adjacent, (0,))}
    return result


class IsomorphismLimit(Exception):
    pass


def same_view(a, b, roots):
    """Return True with a checked map, False by a complete test, or None at cap."""
    if a == b:
        return True
    if len(a) != len(b):
        return False
    assert set(roots) <= a.keys() and set(roots) <= b.keys()
    roots = frozenset(roots)
    steps = 0
    effort = len(a) + len(b) + sum(map(len, a.values())) + sum(map(len, b.values()))

    def mark(adjacency):
        distances = ball_distances(adjacency, sorted(roots))
        return {v: (v % 2, v in roots, distances.get(v, -1), len(row)) for v, row in adjacency.items()}

    def integerize(left, right):
        names = {}
        return tuple({v: names.setdefault(c, len(names)) for v, c in data.items()} for data in (left, right))

    def compare(left, right):
        nonlocal steps
        while True:
            steps += effort
            if steps > ISO_WORK:
                raise IsomorphismLimit
            count = Counter(left.values())
            if count != Counter(right.values()):
                return False
            old_classes = len(count)
            labels = [{v: (colors[v], tuple(sorted(colors[w] for w in row))) for v, row in view.items()}
                      for view, colors in ((a, left), (b, right))]
            left, right = integerize(*labels)
            count = Counter(left.values())
            if count != Counter(right.values()):
                return False
            if len(count) == old_classes:
                break
        groups = [{c: [] for c in count} for _ in range(2)]
        for colors, classes in zip((left, right), groups, strict=True):
            for v, c in colors.items():
                classes[c].append(v)
        mapping = {v: w for c in count for v, w in zip(groups[0][c], groups[1][c], strict=True)}
        if all({mapping[u] for u in row} == set(b[mapping[v]]) for v, row in a.items()):
            return True
        cell = min((c for c, n in count.items() if n > 1), key=lambda c: (count[c], c), default=None)
        if cell is None:
            return False
        vertex = groups[0][cell][0]
        next_color = len(count)
        return any(compare({**left, vertex: next_color}, {**right, mate: next_color})
                   for mate in groups[1][cell])

    try:
        return compare(*integerize(mark(a), mark(b)))
    except (IsomorphismLimit, RecursionError):
        return None


def scrambled(*views):
    nodes = set().union(*views)
    rng = Random(RECODE_SEED)
    naming = {}
    for kind in (0, 1):
        group = sorted(v for v in nodes if v % 2 == kind)
        replacements = group.copy()
        rng.shuffle(replacements)
        naming.update(zip(group, replacements, strict=True))
    return naming, [
        dict(sorted((naming[v], tuple(sorted(naming[u] for u in row))) for v, row in view.items()))
        for view in views
    ]


def isomorphism_control():
    def rings(close):
        # Each of six ordinary knots meets the same hub, whose sole open
        # distinction is the root. Their own meetings are regular.
        stars = [[0] + list(range(1, 7))] + [[v] for v in range(1, 7)]
        for bit, (a, b) in enumerate(close, start=7):
            stars[a].append(bit)
            stars[b].append(bit)
        return incidence(stars)

    a = rings(((1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)))
    b = rings(((1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)))
    assert Counter(map(len, a.values())) == Counter(map(len, b.values()))
    assert Counter(ball_distances(a, (1,)).values()) == Counter(ball_distances(b, (1,)).values())
    assert same_view(a, b, (1,)) is False
    # Renaming that fixes the root enables a nontrivial equal test directly.
    naming = {v: v for v in a}
    naming[2], naming[6] = 6, 2
    copy = dict(sorted((naming[v], tuple(sorted(naming[u] for u in row))) for v, row in a.items()))
    assert a != copy and same_view(a, copy, (1,)) is True
    return {"equal_shells_different_incidence": True, "same_incidence_recoded": True}


def recode_literal(q, l, rows):
    a, b = (data["adjacent"] for data in (q, l))
    names, relabelled = scrambled(a, b)
    answer = []
    for row in rows:
        if row["offset"] != 2:
            continue
        exact = row["ordinary"]["earliest_structure_radius"]["exact"]
        assert exact is not None and exact > 0
        marks = tuple(names[2 * bit + 1] for bit in row["marks"])
        depth = [ball_distances(g, marks) for g in relabelled]
        verdicts = []
        for radius in (exact - 1, exact):
            views = [induced(g, {v for v, d in ds.items() if d <= radius})
                     for g, ds in zip(relabelled, depth, strict=True)]
            verdicts.append(same_view(*views, marks))
        assert verdicts == [True, False]
        answer.append({"arm_steps": row["arm_steps"], "marks": row["marks"],
                       "radii": [exact - 1, exact], "isomorphic": verdicts})
    return {"random_seed": RECODE_SEED, "cases": answer}


def old_ring_and_side(nodes, ring, origins, tail_mask):
    knots = {v for v in nodes if v % 2 == 0}
    return {"old_ring_knots": sorted(v // 2 for v in knots if v // 2 in ring),
            "off_arm_knots": sorted(v // 2 for v in knots if origins[v] & ~tail_mask)}


def ball_comparison(quiet, loaded, roots, path, ring, offset):
    arms = (quiet, loaded)
    depth = [ball_distances(data["adjacent"], roots) for data in arms]
    caps = [min(d[2 * v] for v in ring) for d in depth]
    assert caps == [2 * offset + 1] * 2
    last = max(max(d.values()) for d in depth)
    profiles, first_count = [], []
    for kind in (0, 1):
        counts = []
        for d in depth:
            shells = Counter(h for v, h in d.items() if v % 2 == kind)
            counts.append([sum(shells[r] for r in range(i + 1)) for i in range(last + 1)])
        profiles.append(counts)
        first_count.append(next((r for r, pair in enumerate(zip(*counts, strict=True)) if pair[0] != pair[1]), None))
    largest_equal = -1
    earliest_difference = None
    ambiguous = []
    for radius in range(last + 1):
        # A rooted isomorphism restricts to every smaller induced ball.
        sample = [induced(data["adjacent"], {v for v, k in d.items() if k <= radius})
                  for data, d in zip(arms, depth, strict=True)]
        verdict = same_view(*sample, roots)
        if verdict is True:
            largest_equal = radius
        elif verdict is False:
            earliest_difference = radius
            break
        else:
            ambiguous.append(radius)
    lower_radius = largest_equal + 1
    exact_radius = earliest_difference if earliest_difference == lower_radius else None
    first = {"lower": lower_radius if largest_equal < last else None, "upper": earliest_difference,
             "exact": exact_radius, "unresolved_radii": [r for r in ambiguous if r > largest_equal]}
    strict_radius = caps[0] - 1
    full = "different" if earliest_difference is not None else "equal" if largest_equal == last else "unresolved"
    strict = ("different" if earliest_difference is not None and earliest_difference <= strict_radius else
              "equal" if largest_equal >= strict_radius else "unresolved")
    witnesses = {}
    arm_mask = sum(1 << v for v in path[1:])  # original seam excluded for the A117 grading
    for key, radius in (("first_structure", earliest_difference), ("first_count", first_count[0])):
        if radius is None:
            continue
        witnesses[key] = [old_ring_and_side({v for v, k in d.items() if k <= radius}, ring, data["origins"], arm_mask)
                          for data, d in zip(arms, depth, strict=True)]
    return {"earliest_structure_radius": first, "full": full, "strict": strict,
            "strict_through": strict_radius, "first_knot_count_radius": first_count[0],
            "first_distinction_count_radius": first_count[1],
            "knot_counts": profiles[0], "distinction_counts": profiles[1], "where_compared": witnesses}


def other_readings(quiet, loaded, roots, path, holder_set, offset):
    arms = (quiet, loaded)
    possible = [{v for v, r in data["seam_distance"].items() if r >= 2 * offset} for data in arms]
    retained = [induced(data["adjacent"], region) for data, region in zip(arms, possible, strict=True)]
    components = [induced(g, ball_distances(g, roots).keys()) for g in retained]
    tail = sum(1 << v for v in path[offset:])
    ancestral = {}
    for family in ("some", "every"):
        reads = []
        for data in arms:
            knots = {v for v, o in data["origins"].items()
                     if (bool(o & tail) if family == "some" else not o & ~tail)}
            ports = {u for v in knots for u in data["adjacent"][v]}
            reads.append(induced(data["adjacent"], knots | ports))
        ancestral[family] = same_view(*reads, roots)
    nearest = []
    for data in arms:
        visible = {}
        by_holder = []
        for holder in holder_set:
            steps, nodes = data["nearest"][holder]
            visible.update(nodes)
            by_holder.append({"steps": steps, "loose_histogram": sorted(Counter(nodes.values()).items())})
        nearest.append({"by_holder": by_holder, "union": sorted(Counter(visible.values()).items())})

    def sizes(views):
        return [[sum(v % 2 == 0 for v in g), sum(v % 2 == 1 for v in g)] for g in views]

    return {"separation_component_isomorphic": same_view(*components, roots),
            "separation_all_isomorphic": same_view(*retained, roots),
            "separation_component_sizes": sizes(components), "separation_all_sizes": sizes(retained),
            "ancestral_regions_isomorphic": ancestral, "nearest_growing_end_histograms": nearest}


def marksets(spec):
    for arm, row in enumerate(spec["arm_marks"]):
        for offset, bit in enumerate(row):
            yield arm, offset, (bit,)
            if offset + 1 < len(row):
                yield arm, offset, (bit, row[offset + 1])


def compare_all(spec, arms, model, through):
    stars, _ = qualified(spec, model)
    arm_data, profiles = {}, {}
    for name, occupied in zip(("quiet", "loaded"), arms, strict=True):
        frames, stop = traced(stars, occupied, through)
        profiles[name] = peel_profiles(frames, len(stars))
        arm_data[name] = {"termination": stop, "frames": {age: {
            "knots": len(f["stars"]), "distinctions": f["distinction_count"], "born": len(f["born"]),
            "stars_sha256": digest(f["stars"]), "old_occupied": sorted(f["occupied"])}
            for age, f in frames.items()}}
    shared = sorted(set(profiles["quiet"]) & set(profiles["loaded"]))
    comparisons = {}
    recoding = None
    for age in shared:
        q, l = profiles["quiet"][age], profiles["loaded"][age]
        rows = []
        for arm, offset, marks in marksets(spec):
            path = spec["arms"][arm]
            roots = tuple(2 * d + 1 for d in marks)
            holders = path[offset:offset + len(marks) + 1]
            ordinary = ball_comparison(q, l, roots, path, spec["cycle"], offset)
            alternatives = other_readings(q, l, roots, path, holders, offset)
            rows.append({"arm_steps": ARM_LENGTHS[arm], "offset": offset, "marks": marks,
                         "old_holders_outward": holders, "ordinary": ordinary, **alternatives})
        comparisons[age] = rows
        if age == 1 and spec["dimension_of_unattached_background"] == 2 and spec["ring_style"] == "one_c2":
            recoding = recode_literal(q, l, rows)
    return {"source": spec, "arms": arm_data, "comparisons": comparisons, "recoding_control": recoding}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, choices=range(MAX_AGE + 1), default=MAX_AGE)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    model = cluster_model()
    frozen = (HERE / "inputs.json").read_bytes()
    config = json.loads(frozen)
    assert config["dimension_sources"]["arms"] == list(ARM_LENGTHS)
    assert config["branch_caps"] == [CAPS["junctions"], CAPS["distinctions"]]
    result = {"arm_steps": ARM_LENGTHS, "declared_age_cap": args.through, "physical_caps": CAPS,
              "inputs_sha256": sha256(frozen).hexdigest(), "isomorphism_work_cap": ISO_WORK,
              "controls": isomorphism_control(), "bare": {}, "joined": {}}
    for dimension in (1, 2, 3):
        result["bare"][dimension] = bare_certificate(dimension, model, args.through)
        for style in RINGS:
            spec = source(dimension, style)
            cell = compare_all(spec, ((), spec["ring_marks"]), model, args.through)
            result["joined"][f"{dimension}_{style}"] = cell
            print(dimension, style, [(name, t["termination"]) for name, t in cell["arms"].items()], flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
