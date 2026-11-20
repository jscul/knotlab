"""Union of full parity-bond balls about fixed original same-side marks."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from functools import reduce
from hashlib import sha256
import json
from operator import or_
from pathlib import Path
from random import Random
import sys
from tempfile import NamedTemporaryFile

from side_sources import AGES, CAPS, HERE, ROOT, cases, generate, growth, loads, marksets, offset


FEEDBACK = "STATE-FEEDS-GROWTH-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / FEEDBACK / f"{FEEDBACK}-E001_feedback"))
import balls as previous


prior = previous.prior
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "side_balls.json"
OFFSETS_OUT = OUT.with_name("side_balls_offsets.json")
RADII = tuple(range(8))
EARLY_AGE = 1
LATE_PANEL_AGE = 6
FOLLOWUP_OFFSETS = (4, 6, 8, 10, 12, 16)
FOLLOWUP_SHAPES = ((0, 1), (0, 4))


def bits(values):
    return reduce(or_, (1 << v for v in values), 0)


def indices(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def physical_mask(stage, names):
    return bits(v for d in names for v in stage.owner[d])


def update_larger(stage, by_bundle, rows, high_marks):
    """Use the older exact search again at a higher cutoff, with its own budget."""
    stats = {}
    for bundle in sorted({stage.bundle_of[d] for d in high_marks}):
        block = stage.blocks[stage.block_of[bundle]]
        nv, edges = stage.local_edges(block)
        q = block.index(bundle)
        previous_cert = by_bundle[bundle]
        attempts = []
        for radius in (7, 6):
            if radius <= previous_cert:
                break
            reader = prior.AnchoredCuts(nv, edges)
            try:
                costs = reader.through(q, radius + 1)
            except prior.SearchLimit:
                attempts.append([radius, prior.PATH_STATES, False])
                continue
            attempts.append([radius, reader.states, True])
            exact = prior.distance_values(costs, radius + 1)
            for k, v in zip(block, exact, strict=True):
                old = rows[bundle][k]
                if isinstance(old, int):
                    assert old == v
                rows[bundle][k] = v
            by_bundle[bundle] = radius
            break
        stats[bundle] = attempts
    return stats


def rooted_masks(stage, intervals):
    lower_dist = [0] * len(RADII)
    upper_dist = [0] * len(RADII)
    lower_knot = [0] * len(RADII)
    upper_knot = [0] * len(RADII)
    for i, (d, (lo, hi)) in enumerate(zip(stage.names, intervals, strict=True)):
        knot = bits(stage.owner[d])
        for radius in range(lo, len(RADII)):
            upper_dist[radius] |= 1 << i
            upper_knot[radius] |= knot
        for radius in range(hi, len(RADII)):
            lower_dist[radius] |= 1 << i
            lower_knot[radius] |= knot
    return list(zip(lower_dist, upper_dist, lower_knot, upper_knot, strict=True))


def incidence_sha256(stars):
    return sha256(json.dumps(stars, separators=(",", ":")).encode()).hexdigest()


def read_profile(job, bank=True):
    stars, origins, high = job
    stage = prior.WiredStage(stars)
    rows, effort = previous.bond_rows(stage, origins, allow_bank=bank)
    by_bundle = {r["bundle"]: r["certified_radius"] for r in effort}
    high_attempts = update_larger(stage, by_bundle, rows, high)
    return {"names": stage.names, "knot_count": len(stage.stars), "distinction_count": len(stage.names),
            "incidence_sha256": incidence_sha256(stars),
            "root_masks": {d: rooted_masks(stage, previous.read_names(stage, rows, d)) for d in origins},
            "cutoff": {d: by_bundle[stage.bundle_of[d]] for d in origins},
            "lower_search": effort, "higher_search": high_attempts}


def union_ball(profile, roots, radius):
    return tuple(reduce(or_, column, 0) for column in zip(
        *(profile["root_masks"][d][radius] for d in roots), strict=True))


def plain_representation(spec):
    return tuple(map(tuple, growth.predecessor().source_stars(spec)))


def grades(spec):
    path = spec["roles"]["background"]
    seams = spec["roles"]["seams"] or [4]
    rings = spec["roles"]["rings"] or [[]]
    neighbors = [set() for _ in spec["sizes"]]
    for u, v in spec["meetings"]:
        neighbors[u].add(v)
        neighbors[v].add(u)
    result = []
    for s, ring in zip(seams, rings, strict=True):
        side = [bits(growth.predecessor().reached(neighbors, p, s)) for p in (path[s - 1], path[s + 1])]
        assert not (side[0] & side[1]) and not (bits(ring) & (side[0] | side[1]))
        result.append({"seam": s, "source_components": side, "old_ring_knots": bits(ring)})
    return result


def stage_side_masks(ancestors, marks):
    return [[bits(v for v, ancestry in enumerate(ancestors) if not ancestry & ~component)
             for component in m["source_components"]] for m in marks]


def mark_panel(spec, age, followup):
    tag = spec["id"]
    if followup:
        n = len(spec["roles"]["anchors"])
        s, = spec["roles"]["seams"]
        translated = {ms for d in FOLLOWUP_OFFSETS for shape in FOLLOWUP_SHAPES for ms in
                      (tuple(s + d + a for a in shape), tuple(sorted(s - 1 - d - a for a in shape)))
                      if 0 <= ms[0] < ms[-1] < n}
        return tuple(sorted(translated))
    if tag == "J1":
        return tuple(marksets(spec, full=True))
    translated = tuple(marksets(spec))
    if age > EARLY_AGE and tag in {"P4", "P8", "P16"}:
        s, = spec["roles"]["seams"]
        return ((s + 4, s + 8),)
    return translated


def prepare(selected, through, followup):
    jobs = []
    job_ids = {}
    datasets = {}
    for tag, spec in selected.items():
        score = grades(spec)
        stage_bound = min(AGES[tag], through, EARLY_AGE if "additional_ring_edges" in spec["roles"] else through)
        source = plain_representation(spec)
        by_hot = defaultdict(list)
        for key, lit in loads(spec).items():
            active = tuple(v for v, support in enumerate(source) if not lit.isdisjoint(support))
            by_hot[active].append((key, lit))
        panels = {age: mark_panel(spec, age, followup) for age in range(3 if followup else 0, stage_bound + 1)}
        anchors = spec["roles"]["anchors"]
        traces = {}
        for active, equal in by_hot.items():
            representative, lit = equal[0]
            trace = {"physical_loadings": [{"arm": arm, "occupied": sorted(state), "dose": len(state)}
                                           for arm, state in equal],
                     "active_original_holders": active, "frames": {}}
            ancestors = [1 << v for v in range(len(source))]
            stages = generate(spec, lit, stage_bound, CAPS)
            while True:
                try:
                    age, frame = next(stages)
                except StopIteration as stop:
                    trace["termination"] = stop.value
                    break
                if age:
                    for v in frame["born"]:
                        assert v == len(ancestors)
                        ancestors.append(reduce(or_, (ancestors[p] for p in frame["parent_sets"][v]), 0))
                    assert not frame["new_occupied"] and not frame["spent_occupied"]
                if age not in panels:
                    continue
                roots = sorted({anchors[p] for ms in panels[age] for p in ms})
                if followup or age <= EARLY_AGE:
                    higher = roots
                else:
                    s = score[0]["seam"]
                    higher = [anchors[p] for p in (s + 4, s + 8) if p < len(anchors) and anchors[p] in roots]
                signature = (tuple(map(tuple, frame["stars"])), tuple(roots), tuple(higher))
                job = job_ids.setdefault(signature, len(jobs))
                if job == len(jobs):
                    jobs.append(signature)
                trace["frames"][age] = {"profile": job, "pure_side_holder_masks": stage_side_masks(ancestors, score)}
            traces[representative] = trace
        datasets[tag] = {"input": spec, "target_age": stage_bound, "marks": score, "marksets": panels, "traces": traces}
    return jobs, datasets


def exact_ball(profile, physical_roots, radius):
    dlo, dhi, klo, khi = union_ball(profile, physical_roots, radius)
    return (dlo, klo) if dlo == dhi and klo == khi else None


def describe(profile, ball, frame, data, marks, radius, donor, side):
    distances, holders = ball
    path = data["input"]["roles"]["background"]
    d = [profile["names"][i] for i in indices(distances)]
    return {"profile": frame["profile"], "distinctions": d, "knots": list(indices(holders)),
            "original_path_knots": list(indices(holders & bits(path))),
            "holders_with_ancestry_outside_the_marked_side": list(indices(holders & ~frame["pure_side_holder_masks"][donor][side])),
            "first_certified_radius_reaching_a_ring_holder": next((r for r in RADII if
                union_ball(profile, marks, r)[2] & data["marks"][donor]["old_ring_knots"]), None),
            "individual_root_knot_counts": [union_ball(profile, (p,), radius)[2].bit_count() for p in marks]}


def scan_pair(data, profiles, quiet, loaded, donor=0):
    """Grade exact result sets, separately for each seam, without choosing centers."""
    stats = defaultdict(Counter)
    examples = {}
    offsets = defaultdict(Counter)
    by_age = defaultdict(Counter)
    by_size = defaultdict(lambda: defaultdict(Counter))
    anchors = data["input"]["roles"]["anchors"]
    common = sorted(quiet["frames"].keys() & loaded["frames"].keys())
    legacy = []
    for age in common:
        a, b = (trace["frames"][age] for trace in (quiet, loaded))
        pa, pb = (profiles[f["profile"]] for f in (a, b))
        for marks in data["marksets"][age]:
            roots = tuple(anchors[p] for p in marks)
            for radius in RADII:
                rows = [union_ball(p, roots, radius) for p in (pa, pb)]
                goal = stats[radius]
                goal["asked"] += 1
                size = by_size[len(marks)][radius]
                size["asked"] += 1
                has_literal_balls = all(dl == dh and kl == kh for dl, dh, kl, kh in rows)
                [(_, _, a_lo, a_hi), (_, _, b_lo, b_hi)] = rows
                a_count = (a_lo.bit_count(), a_hi.bit_count())
                b_count = (b_lo.bit_count(), b_hi.bit_count())
                goal["exact_knot_counts"] += a_count[0] == a_count[1] and b_count[0] == b_count[1]
                if min(b_count) > max(a_count) or max(b_count) < min(a_count):
                    goal["separated_by_bounds"] += 1
                if marks == (data["marks"][0]["seam"] + 4, data["marks"][0]["seam"] + 8):
                    legacy.append({"age": age, "radius": radius, "marks": marks, "quiet": a_count, "loaded": b_count})
                if not has_literal_balls:
                    continue
                (_, _, ak, _), (_, _, bk, _) = rows
                delta = bk.bit_count() - ak.bit_count()
                goal["exact"] += 1
                size["exact"] += 1
                by_age[age]["exact"] += 1
                goal["changed"] += delta != 0
                size["changed"] += delta != 0
                by_age[age]["changed"] += delta != 0
                if not delta:
                    continue
                goal["positive"] += delta > 0
                score = data["marks"][donor]
                side = int(marks[0] >= score["seam"])
                quiet_pure = not ak & ~a["pure_side_holder_masks"][donor][side]
                loaded_pure = not bk & ~b["pure_side_holder_masks"][donor][side]
                pure = quiet_pure and loaded_pure
                before = not (score["old_ring_knots"] & (ak | bk))
                off = offset(marks, score["seam"])
                offsets[off]["changed"] += 1
                offsets[off]["both_wholly_one_side"] += pure
                offsets[off]["loaded_wholly_one_side"] += loaded_pure
                offsets[off]["before_any_ring_holder"] += before
                offsets[off]["positive_and_wholly_one_side"] += pure and delta > 0
                tests = ["different", f"different_{len(marks)}_marks"]
                if pure:
                    tests += ["wholly_one_side", "positive_wholly_one_side"] if delta > 0 else ["wholly_one_side"]
                if loaded_pure:
                    tests.append("loaded_wholly_one_side")
                if before:
                    tests += ["before_any_ring_holder", "positive_before_any_ring_holder"] if delta > 0 else ["before_any_ring_holder"]
                for test in tests:
                    order = (radius, age, -off, len(marks), marks)
                    if test in examples and order >= examples[test]["order"]:
                        continue
                    examples[test] = {"order": order, "age": age, "radius": radius, "indices": marks,
                                      "donor_seam": score["seam"], "offset": off, "knot_delta": delta,
                                      "both_wholly_one_side": pure, "before_any_ring_holder": before,
                                      "quiet": describe(pa, (rows[0][0], ak), a, data, roots, radius, donor, side),
                                      "loaded": describe(pb, (rows[1][0], bk), b, data, roots, radius, donor, side)}
    return {"common_ages": common, "radius_counts": dict(stats), "age_counts": dict(by_age),
            "witnesses": examples, "changed_by_offset_from_toggled_donor": dict(offsets), "translated_legacy_pair": legacy,
            "size_by_radius": {n: dict(per_radius) for n, per_radius in by_size.items()}}


def factorial(data, profiles, arms):
    common = sorted(set.intersection(*(set(arms[a]["frames"]) for a in ("0", "1", "2", "3"))))
    anchors = data["input"]["roles"]["anchors"]
    results = defaultdict(Counter)
    first = None
    first_strict = None
    for age in common:
        frames = [arms[a]["frames"][age] for a in ("0", "1", "2", "3")]
        for marks in data["marksets"][age]:
            roots = tuple(anchors[p] for p in marks)
            for r in RADII:
                found = [exact_ball(profiles[f["profile"]], roots, r) for f in frames]
                if any(v is None for v in found):
                    continue
                counts = [k.bit_count() for _, k in found]
                delta = counts[3] - counts[2] - counts[1] + counts[0]
                results[age]["exact"] += 1
                results[age]["nonzero_interactions"] += delta != 0
                if not delta:
                    continue
                choice = (age, r, len(marks), marks)
                strict = []
                before_ring = []
                for j, g in enumerate(data["marks"]):
                    side = int(marks[0] >= g["seam"])
                    if all(not (k & ~f["pure_side_holder_masks"][j][side]) for (_, k), f in zip(found, frames, strict=True)):
                        strict.append(g["seam"])
                    if all(not (k & g["old_ring_knots"]) for _, k in found):
                        before_ring.append(g["seam"])
                results[age]["nonzero_wholly_one_side_of_a_seam"] += bool(strict)
                results[age]["nonzero_before_any_holder_on_one_ring"] += bool(before_ring)
                note = {"order": choice, "age": age, "radius": r, "marks": marks,
                        "knots_00_10_01_11": counts, "difference_of_differences": delta,
                        "wholly_one_side_of_seams": strict, "without_old_ring_holders_of_seams": before_ring}
                if first is None or choice < first["order"]:
                    first = note
                if strict and (first_strict is None or choice < first_strict["order"]):
                    first_strict = note
    return {"age_counts": dict(results), "first_nonzero": first, "first_nonzero_wholly_one_side": first_strict}


def dose_panel(data, profiles):
    weighted = [(arm["arm"], arm["dose"], t) for t in data["traces"].values() for arm in t["physical_loadings"]]
    quiet = next(t for a, amount, t in weighted if amount == 0)
    anchors = data["input"]["roles"]["anchors"]
    totals = {key: Counter() for key in sorted({n for _, n, _ in weighted})}
    changed = Counter()
    varied_same_dose = Counter()
    strict_changed = Counter()
    first = None
    extremes = {}
    for age, f0 in quiet["frames"].items():
        for marks in data["marksets"][age]:
            roots = tuple(anchors[p] for p in marks)
            for r in RADII:
                base = exact_ball(profiles[f0["profile"]], roots, r)
                if base is None:
                    continue
                current = defaultdict(list)
                for arm, amount, t in weighted:
                    if age not in t["frames"]:
                        continue
                    f = t["frames"][age]
                    got = exact_ball(profiles[f["profile"]], roots, r)
                    if got is None:
                        continue
                    delta = got[1].bit_count() - base[1].bit_count()
                    totals[amount]["exact_arm_observations"] += 1
                    totals[amount]["sum_deltas"] += delta
                    changed[amount] += delta != 0
                    current[amount].append((delta, arm))
                    extrema = extremes.setdefault(amount, [delta, delta])
                    extrema[:] = (min(extrema[0], delta), max(extrema[1], delta))
                    if delta:
                        side = int(marks[0] >= data["marks"][0]["seam"])
                        strict_changed[amount] += not (base[1] & ~f0["pure_side_holder_masks"][0][side]
                                                      or got[1] & ~f["pure_side_holder_masks"][0][side])
                for amount, entries in current.items():
                    lo, hi = min(entries), max(entries)
                    if lo[0] == hi[0]:
                        continue
                    varied_same_dose[amount] += 1
                    choice = (age, r, len(marks), marks, amount)
                    if first is None or choice < first["order"]:
                        first = {"order": choice, "age": age, "radius": r, "marks": marks,
                                 "dose": amount, "changed_counts_and_arms": [lo, hi],
                                 "quiet_count": base[1].bit_count()}
    return {"weight_by_amount": dict(Counter(n for _, n, _ in weighted)), "geometries_by_activity_mask": len(data["traces"]),
            "changed": dict(changed), "within_dose_unequal_cells": dict(varied_same_dose),
            "strictly_one_side_changes": dict(strict_changed),
            "observations_by_dose": {amount: {**r, "range_of_deltas": extremes[amount],
                "mean_delta": str(Fraction(r["sum_deltas"], r["exact_arm_observations"]))}
                                     for amount, r in totals.items() if r["exact_arm_observations"]},
            "first_within_dose_difference": first}


def check_control():
    """Independently enumerate allowed rows and compare with a permuted cut reading."""
    stars = ((0, 1, 2), (2, 3, 4), (0, 4, 5), (1, 3, 6))
    roots = (0, 2, 3, 6)
    actual = read_profile((stars, roots, roots))
    all_bonds, _, _ = prior.literal_states_distances(stars)
    rename = [11 + 7 * d for d in range(7)]
    Random(163).shuffle(rename)
    changed = tuple(tuple(rename[d] for d in row) for row in reversed(stars))
    trial = read_profile((changed, tuple(rename[r] for r in roots), tuple(rename[r] for r in roots)), bank=False)
    assert trial["cutoff"] == {rename[r]: 7 for r in roots}
    n = 0
    for ms in ((0, 6), (0, 2, 3), roots):
        for radius in RADII:
            expected = {d for d in range(7) if any(
                (value := all_bonds[r][d]) != prior.INFINITY and value <= radius for r in ms)}
            expected_holders = {v for v, row in enumerate(stars) if not expected.isdisjoint(row)}
            assert exact_ball(actual, ms, radius) == (bits(expected), bits(expected_holders))
            moved, holders = exact_ball(trial, tuple(rename[r] for r in ms), radius)
            assert {trial["names"][i] for i in indices(moved)} == {rename[d] for d in expected}
            assert set(indices(holders)) == {len(stars) - 1 - v for v in expected_holders}
            n += 1
    return n


def pack_profile(record):
    return {**record, "root_masks": {d: [[hex(x) for x in row] for row in rr] for d, rr in record["root_masks"].items()}}


def unpack_profile(record):
    return {**record,
            "root_masks": {int(d): [tuple(int(x, 16) for x in row) for row in rr] for d, rr in record["root_masks"].items()},
            "cutoff": {int(d): r for d, r in record["cutoff"].items()}, "reused_roots": record.get("reused_roots", [])}


def read_saved(path):
    saved = json.loads(path.read_text())
    for record in saved["cases"].values():
        record["marksets"] = {int(k): tuple(map(tuple, v)) for k, v in record["marksets"].items()}
        for m in record["marks"]:
            m["source_components"] = [int(x, 16) for x in m["source_components"]]
            m["old_ring_knots"] = int(m["old_ring_knots"], 16)
        for t in record["traces"].values():
            t["frames"] = {int(age): f for age, f in t["frames"].items()}
            for f in t["frames"].values():
                f["pure_side_holder_masks"] = [[int(side, 16) for side in pair] for pair in f["pure_side_holder_masks"]]
    return saved["cases"], [unpack_profile(p) for p in saved["profiles"]], saved["scope"]


def measure(jobs, workers, cache):
    work, roster = [], []
    cache = {p["incidence_sha256"]: p for p in cache}
    for stars, origins, high in jobs:
        previous_profile = cache.get(incidence_sha256(stars))
        old = [] if previous_profile is None else [d for d in origins
              if previous_profile["cutoff"].get(d, -1) >= (7 if d in high else 5)]
        needed = tuple(d for d in origins if d not in old)
        roster.append((previous_profile, old, bool(needed)))
        if needed:
            work.append((stars, needed, tuple(d for d in high if d in needed)))
    print(f"{len(jobs)} distinct physical profiles, {len(work)} with new cut queries", file=sys.stderr, flush=True)
    if workers == 1:
        computed = list(map(read_profile, work))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            computed = list(pool.map(read_profile, work, chunksize=1))
    cursor = iter(computed)
    merged = []
    for old_profile, reused, newly_measured in roster:
        if newly_measured:
            profile = next(cursor)
        else:
            profile = {**old_profile, "root_masks": {}, "cutoff": {}, "lower_search": [], "higher_search": {}}
        if reused:
            assert profile["names"] == old_profile["names"]
            for field in ("root_masks", "cutoff"):
                profile[field].update((d, old_profile[field][d]) for d in reused)
        profile["reused_roots"] = reused
        merged.append(profile)
    assert next(cursor, None) is None
    return merged


def fixed_radius_cells(data, profiles, arms):
    s = data["marks"][0]["seam"]
    a, b = arms["0"]["frames"], arms["1"]["frames"]
    rows = []
    for age in sorted(a.keys() & b.keys()):
        for ms in data["marksets"][age]:
            roots = tuple(data["input"]["roles"]["anchors"][m] for m in ms)
            for radius in (5, 6, 7):
                masks = [union_ball(profiles[fr["profile"]], roots, radius) for fr in (a[age], b[age])]
                quiet, loaded = [tuple(k.bit_count() for k in row[2:]) for row in masks]
                rows.append({"age": age, "offset": offset(ms, s), "side": "right" if ms[0] >= s else "left",
                             "gap": ms[1] - ms[0], "marks": ms, "radius": radius, "quiet": quiet, "loaded": loaded,
                             "delta": [loaded[0] - quiet[1], loaded[1] - quiet[0]]})
    return rows


def actual_recoding(data, profiles):
    if "J1" not in data or not all(3 in r["frames"] for r in data["J1"]["traces"].values()):
        return []
    source = data["J1"]
    controls = []
    for arm, state in loads(source["input"]).items():
        for age, stage in generate(source["input"], state, 3, CAPS):
            if age not in (2, 3):
                continue
            marks, r = ((0, 1), 4) if age == 2 else ((8, 12), 7)
            original = profiles[source["traces"][arm]["frames"][age]["profile"]]
            rng = Random(2079)
            renamed = [9 * i + 70 for i in range(original["distinction_count"])]
            rng.shuffle(renamed)
            names = dict(zip(original["names"], renamed, strict=True))
            stars = tuple(tuple(names[d] for d in row) for row in reversed(stage["stars"]))
            roots = tuple(names[d] for d in marks)
            trial = read_profile((stars, roots, roots if r > 5 else ()), bank=False)
            recoded = exact_ball(trial, roots, r)
            assert recoded is not None
            d, k = exact_ball(original, marks, r)
            assert {names[original["names"][i]] for i in indices(d)} == {trial["names"][i] for i in indices(recoded[0])}
            assert {len(stars) - 1 - i for i in indices(k)} == set(indices(recoded[1]))
            controls.append({"arm": arm, "age": age, "radius": r, "marks": marks, "knots": k.bit_count()})
    return controls


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--through", type=int)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--followup", action="store_true")
    parser.add_argument("--reuse", type=Path, help="recompute only contrasts from an existing exact mask receipt")
    config = cases()
    args = parser.parse_args()
    target = args.out or (OFFSETS_OUT if args.followup else OUT)
    controls = check_control()
    if args.reuse:
        data, profiles, scope = read_saved(args.reuse)
    else:
        tags = args.cases or (("P8", "P16") if args.followup else tuple(config))
        selected = {tag: config[tag] for tag in tags}
        through = args.through or (8 if args.followup else LATE_PANEL_AGE)
        jobs, data = prepare(selected, through, args.followup)
        saved = read_saved(OUT)[1] if args.followup and OUT.exists() else []
        profiles = measure(jobs, args.workers, saved)
        scope = {"early_full_higher_radii_through": EARLY_AGE, "default_max_age": through,
                 "growth_caps": CAPS, "base_path_cap_per_query": previous.QUERY_CAP,
                 "higher_path_cap_per_trial": prior.PATH_STATES}
        if args.followup:
            scope["fixed_radius_followup_offsets"] = FOLLOWUP_OFFSETS
            scope["fixed_radius_followup_shapes"] = FOLLOWUP_SHAPES
    reruns = actual_recoding(data, profiles)
    result = {}
    for tag, record in data.items():
        arms = {row["arm"]: t for t in record["traces"].values() for row in t["physical_loadings"]}
        if "w00" in arms:
            result[tag] = {"dose": dose_panel(record, profiles)}
        elif len(arms) == 4:
            result[tag] = {"contrasts": {f"{a}/{b}": scan_pair(record, profiles, arms[a], arms[b],
                                                              donor=(int(a) ^ int(b)).bit_length() - 1)
                                         for a, b in (("0", "1"), ("0", "2"), ("1", "3"), ("2", "3"))},
                           "factorial": factorial(record, profiles, arms)}
        else:
            result[tag] = {"contrasts": {"0/1": scan_pair(record, profiles, arms["0"], arms["1"])} if "1" in arms else {}}
            if "fixed_radius_followup_offsets" in scope:
                result[tag]["fixed_radius_cells"] = fixed_radius_cells(record, profiles, arms)
    for record in data.values():
        for m in record["marks"]:
            m["source_components"] = [hex(x) for x in m["source_components"]]
            m["old_ring_knots"] = hex(m["old_ring_knots"])
        for t in record["traces"].values():
            for f in t["frames"].values():
                f["pure_side_holder_masks"] = [[hex(side) for side in pair] for pair in f["pure_side_holder_masks"]]
    receipt = {"radii": RADII, "scope": scope, "literal_and_recoding_controls": controls, "actual_witness_recodings": reruns,
               "cases": data, "profiles": [pack_profile(row) for row in profiles], "comparisons": result}
    target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=target.parent, delete=False) as out:
        temp = Path(out.name)
        json.dump(receipt, out, separators=(",", ":"))
        out.write("\n")
    temp.replace(target)


if __name__ == "__main__":
    main()
