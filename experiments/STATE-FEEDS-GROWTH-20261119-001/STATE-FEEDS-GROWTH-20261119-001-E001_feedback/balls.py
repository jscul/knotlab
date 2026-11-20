"""Exact finite-radius balls on the literal parity stages produced by feedback."""

import argparse
import gzip
import hashlib
import io
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from fractions import Fraction
from pathlib import Path
from tempfile import NamedTemporaryFile
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREVIOUS = "EDDY-WORLD-20261119-001"
PREVIOUS_FAMILY = PREVIOUS + "-E001_world"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / PREVIOUS_FAMILY))
import world_bonds as prior
from measure_growth import load_growth


RADII = (1, 2, 3, 4, 5)
QUERY_CAP = 120_000
SHORT_BANK_LINKS = 180
SHORT_BANK_HALVES = 250_000
INFINITY = 10**12
METRICS = ("distinctions", "knots", "original_path_distinctions", "original_path_knots")


def bounds(value):
    if isinstance(value, int):
        return value, value
    if value == prior.UNKNOWN:
        return 1, INFINITY
    if value == prior.INFINITY:
        return INFINITY, INFINITY
    if value.startswith(">"):
        return int(value[1:]) + 1, INFINITY
    raise ValueError(f"unexpected bond reading {value!r}")


def encoded_interval(lo, hi):
    if lo == hi:
        return lo if lo < INFINITY else prior.INFINITY
    return {"lower": lo, "upper": hi if hi < INFINITY else None}


def budgeted_anchored(reader, query):
    """Check the predecessor's path branches in increasing added weight."""
    cutoff = max(RADII) + 1
    best = [cutoff + 1] * len(reader.edges)
    source, target, weight = reader.edges[query]
    pending = [deque() for _ in range(cutoff + 1)]
    if weight <= cutoff:
        pending[weight].append((1 << query, 0, (query,)))
    states = 0
    for cost in range(1, cutoff + 1):
        while pending[cost]:
            if states == QUERY_CAP:
                return best, max(0, cost - 2), states
            removed, fixed, chosen = pending[cost].popleft()
            states += 1
            path, shore = reader.path_or_component(source, target, removed)
            if path is None:
                _, complement = reader.path_or_component(target, source, removed)
                if (len(shore) + len(complement) == reader.vertex_count
                        and all((reader.edges[e][0] in shore) != (reader.edges[e][1] in shore) for e in chosen)):
                    for e in chosen:
                        best[e] = min(best[e], cost)
                continue
            for e in path:
                flag = 1 << e
                new_cost = cost + reader.edges[e][2]
                if not fixed & flag and new_cost <= cutoff:
                    pending[new_cost].append((removed | flag, fixed, (*chosen, e)))
                    fixed |= flag
    return best, max(RADII), states


def bond_rows(stage, origins, allow_bank=True):
    by_block = defaultdict(set)
    for name in origins:
        bundle = stage.bundle_of[name]
        by_block[stage.block_of[bundle]].add(bundle)
    rows = {}
    query_receipts = []
    for ordinal, needed in sorted(by_block.items()):
        block = stage.blocks[ordinal]
        vertices, edges = stage.local_edges(block)
        local = {bundle: j for j, bundle in enumerate(block)}
        short = None
        if (allow_bank and len(edges) <= SHORT_BANK_LINKS
                and prior.bounded_half_count(edges, 6) <= SHORT_BANK_HALVES):
            graph = SimpleNamespace(vertices=vertices, links=[(u, v) for u, v, _ in edges],
                                    bags=[range(weight) for _, _, weight in edges])
            short, _ = prior.short_table(graph, 6, half_limit=SHORT_BANK_HALVES)
        cut_reader = prior.AnchoredCuts(vertices, edges)
        for bundle in sorted(needed):
            if short is not None:
                answer = prior.distance_values(short[local[bundle]], cutoff=6)
                certified_radius = 5
                states = 0
            else:
                cut_costs, certified_radius, states = budgeted_anchored(cut_reader, local[bundle])
                answer = prior.distance_values(cut_costs, cutoff=certified_radius + 1)
            row = [prior.INFINITY] * len(stage.links)
            for target, value in zip(block, answer, strict=True):
                row[target] = value
            rows[bundle] = row
            query_receipts.append({"bundle": bundle, "block": ordinal, "certified_radius": certified_radius,
                                   "method": "short_bond_bank" if short is not None else "anchored_cuts",
                                   "states": states})
    return rows, query_receipts


def freeze_marks(spec, source):
    roles = spec["roles"]
    path = roles["background"]
    anchors = roles["anchors"]
    seams = roles["seams"]
    assert not path or len(path) == len(anchors) + 1
    for i, mark in enumerate(anchors):
        assert set(source.owner[mark]) == set(path[i:i + 2])
    rings = []
    for i, (knots, marks) in enumerate(zip(roles["rings"], roles["ring_edges"], strict=True)):
        assert len(knots) == len(marks) == 5
        for j, mark in enumerate(marks):
            assert set(source.owner[mark]) == {knots[j], knots[(j + 1) % len(knots)]}
        rings.append({"ring": i, "knots": knots, "marks": marks, "is_ring": True})
    if "cut_appendage" in roles:
        knots = roles["cut_appendage"]
        group = set(knots)
        marks = [name for name, owners in source.owner.items() if len(owners) == 2 and set(owners) <= group]
        assert len(marks) == 4
        rings.append({"ring": None, "knots": knots, "marks": marks, "is_ring": False})
    positions = {knot: i for i, knot in enumerate(path)}
    offsets = [[min(abs(i - positions[s]), abs(i + 1 - positions[s])) for s in seams]
               for i in range(len(anchors))]
    return path, anchors, rings, seams, offsets


def physical_steps(stage, origins):
    adj = [set() for _ in stage.stars]
    for ends in stage.owner.values():
        if len(ends) == 2:
            u, v = ends
            adj[u].add(v)
            adj[v].add(u)
    out = {}
    for origin in origins:
        distances = {origin: 0}
        pending = deque([origin])
        while pending:
            u = pending.popleft()
            for v in adj[u]:
                if v not in distances:
                    distances[v] = distances[u] + 1
                    pending.append(v)
        out[origin] = distances
    return out


def minimum_intervals(lists):
    return [(min(lo for lo, _ in values), min(hi for _, hi in values))
            for values in zip(*lists, strict=True)]


def read_names(stage, rows, origin):
    return [bounds(prior.value_at(stage, rows, origin, name)) for name in stage.names]


def ball_counts(stage, intervals, original_path, original_marks):
    """Count exact/possible distinctions and the union of their actual knot holders."""
    knot_lo = [INFINITY] * len(stage.stars)
    knot_hi = [INFINITY] * len(stage.stars)
    for name, (lo, hi) in zip(stage.names, intervals, strict=True):
        for knot in stage.owner[name]:
            knot_lo[knot] = min(knot_lo[knot], lo)
            knot_hi[knot] = min(knot_hi[knot], hi)
    path_intervals = [pair for name, pair in zip(stage.names, intervals, strict=True) if name in original_marks]
    path_knots = [(knot_lo[v], knot_hi[v]) for v in original_path]
    categories = (intervals, list(zip(knot_lo, knot_hi, strict=True)), path_intervals, path_knots)
    return {key: [[sum(hi <= radius for _, hi in group), sum(lo <= radius for lo, _ in group)]
                  for radius in RADII] for key, group in zip(METRICS, categories, strict=True)}


def profile(stars, marks):
    path, anchors, rings, seams, offsets = marks
    stage = prior.WiredStage(stars)
    names = {name: i for i, name in enumerate(stage.names)}
    selected = sorted(set(anchors).union(*(ring["marks"] for ring in rings)))
    rows, effort = bond_rows(stage, selected)
    individual = {mark: read_names(stage, rows, mark) for mark in selected}
    original_marks = set(anchors)
    physical = physical_steps(stage, set(seams).union(*(ring["knots"] for ring in rings)))

    def balls(distances):
        return ball_counts(stage, distances, path, original_marks)

    def bond_to_ring(intervals, ring):
        chosen = [intervals[names[n]] for n in ring["marks"]]
        return encoded_interval(min(lo for lo, _ in chosen), min(hi for _, hi in chosen))

    def knot_step_counts(origins):
        nearest = [min(physical[v].get(k, INFINITY) for v in origins) for k in range(len(stage.stars))]
        return {"knots": [sum(d <= r for d in nearest) for r in RADII],
                "original_path_knots": [sum(nearest[v] <= r for v in path) for r in RADII]}

    path_profiles = []
    for i, mark in enumerate(anchors):
        knot_steps = [min(physical[s].get(v, INFINITY) for v in stage.owner[mark]) for s in seams]
        intervals = individual[mark]
        path_profiles.append({
            "mark": mark, "source_position": i, "source_offsets": offsets[i],
            "original_seam_knot_steps_to_nearest_holder": [
                value if value < INFINITY else prior.INFINITY for value in knot_steps
            ],
            "minimum_bond_steps_to_each_original_ring": [bond_to_ring(intervals, ring) for ring in rings],
            "balls": balls(intervals),
        })
    ring_profiles = []
    for ring in rings:
        roots = ring["marks"]
        union = minimum_intervals([individual[mark] for mark in roots])
        ring_profiles.append({
            **ring, "union": balls(union),
            "minimum_bond_steps_to_each_original_ring": [bond_to_ring(union, target) for target in rings],
            "individual": [{"mark": mark, "balls": balls(individual[mark])} for mark in roots],
            "ordinary_knot_step_balls": knot_step_counts(ring["knots"]),
        })
    return {"knots": len(stage.stars), "distinctions": len(stage.names), "queries": effort,
            "path": path_profiles, "rings": ring_profiles,
            "ordinary_seam_knot_step_balls": [knot_step_counts((s,)) for s in seams]}


def direct_controls():
    stages = (
        [[0, 1, 2], [0, 3, 4]],
        [[0, 1, 2, 3], [0, 1, 4, 5], [2, 4, 6], [3, 5, 6]],
    )
    for stars in stages:
        stage = prior.WiredStage(stars)
        truth, _, _ = prior.literal_states_distances(stars)
        rows, queried = bond_rows(stage, stage.names)
        anchored, _ = bond_rows(stage, stage.names, allow_bank=False)
        assert rows == anchored
        assert all(q["certified_radius"] == max(RADII) for q in queried)
        for roots in [(i,) for i in range(len(stage.names))] + [(0, 1)]:
            distances = minimum_intervals([read_names(stage, rows, stage.names[i]) for i in roots])
            ball = ball_counts(stage, distances, (0,), {0, 1})
            for r, radius in enumerate(RADII):
                members = {d for i in roots for d, value in zip(stage.names, truth[i], strict=True)
                           if isinstance(value, int) and value <= radius}
                holders = {v for v, support in enumerate(stars) if set(support) & members}
                truth_counts = len(members), len(holders), len(members & {0, 1}), len(holders & {0})
                assert all(ball[key][r] == [target, target]
                           for key, target in zip(METRICS, truth_counts, strict=True))
    return {"literal_allowed_state_controls": len(stages), "all_four_counts_verified": True,
            "multi_root_union_verified": True}


def profile_job(job):
    key, shape, marks = job
    return key, profile(shape, marks)


def focused_late_run(run):
    table = tuple(run["table"])
    return table in (("P", "P"), ("P", "V")) or (run["base_case"] == "J1" and table[1] == "V")


def read_export(path, max_age, workers, progress, full_through, late_knot_limit):
    stamp = path.stat()
    export = load_growth(path)
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    ending = path.stat()
    if (stamp.st_ino, stamp.st_size, stamp.st_mtime_ns) != (ending.st_ino, ending.st_size, ending.st_mtime_ns):
        raise ValueError("the growth export changed while being read; use the completed saved version")
    profiles = {}
    cache = {}
    cases = {}
    prepared = {}
    jobs = defaultdict(list)
    for name, run in export["cases"].items():
        meta = {key: value for key, value in run.items() if key not in ("input", "stages")}
        cases[name] = meta | {"ages": {}, "completed_ages_without_bond_measurement": []}
        original = min(run["stages"], key=int)
        shape = tuple(tuple(row) for row in run["stages"][original]["stars"])
        mark_key = (run["base_case"], shape)
        if mark_key not in prepared:
            prepared[mark_key] = freeze_marks(run["input"], prior.WiredStage(shape))
    stages = sorted({int(age) for run in export["cases"].values() for age in run["stages"]
                     if int(age) <= max_age})
    for age in stages:
        for name, run in export["cases"].items():
            row = run["stages"].get(str(age))
            if row is None:
                continue
            if age > full_through:
                if not focused_late_run(run):
                    cases[name]["completed_ages_without_bond_measurement"].append(
                        {"age": age, "reason": "later_table_scope"})
                    continue
                if len(row["stars"]) > late_knot_limit:
                    cases[name]["completed_ages_without_bond_measurement"].append(
                        {"age": age, "reason": "later_measurement_knot_limit"})
                    continue
            shape = tuple(tuple(star) for star in row["stars"])
            key = (run["base_case"], shape)
            if key not in cache:
                original = min(run["stages"], key=int)
                source = tuple(tuple(star) for star in run["stages"][original]["stars"])
                prior_marks = prepared[run["base_case"], source]
                number = str(len(cache))
                cache[key] = number
                jobs[age].append((number, shape, prior_marks))
            cases[name]["ages"][str(age)] = cache[key]
    growth_age_limit, growth_caps = export["age_limit"], export["caps"]
    del export, cache, prepared
    executor = ProcessPoolExecutor(max_workers=workers) if workers > 1 else nullcontext()
    with executor as pool:
        evaluate = pool.map if pool else map
        for age, scheduled in jobs.items():
            if progress:
                print(f"Age {age}: {len(scheduled)} different literal stages", file=sys.stderr, flush=True)
            for key, result in evaluate(profile_job, scheduled):
                profiles[key] = result
            if progress:
                print(f"Age {age}: {len(profiles)} profiles finished overall", file=sys.stderr, flush=True)
    return {"growth_sha256": digest, "run_index": cases, "profiles": profiles,
            "growth_export_age_limit": growth_age_limit, "growth_caps": growth_caps,
            "max_age": max_age, "all_tables_through": full_through, "radii": RADII, "query_cap": QUERY_CAP,
            "later_measurement_knot_limit": late_knot_limit,
            "counts_meaning": ("each entry is an inclusive [lower, upper] bound; a knot is counted once if it "
                               "holds at least one distinction in the ball; original path knots restrict "
                               "this same set of holders"),
            "controls": direct_controls()}


def deltas(first, second):
    if first is second:
        return {key: [[0, 0] for _ in RADII] for key in METRICS}
    return {key: [[lv - ur, uv - lr] for (lv, uv), (lr, ur) in zip(first[key], second[key], strict=True)]
            for key in METRICS}


def average(values):
    exact = [lo for lo, hi in values if lo == hi]
    if not values:
        return {}
    return {
        "anchors": len(values), "exact": len(exact),
        "signed_mean_over_all": [str(Fraction(sum(row[i] for row in values), len(values))) for i in (0, 1)],
        "support_range": [min(lo for lo, _ in values), max(hi for _, hi in values)],
        "exact_delta_histogram": dict(sorted(Counter(exact).items())),
    }


def profile_difference(first, second):
    path = []
    offsets = defaultdict(list)
    by_seam = defaultdict(list)
    for a, b in zip(first["path"], second["path"], strict=True):
        value = deltas(a["balls"], b["balls"])
        heads = a["source_offsets"] or b["source_offsets"]
        path.append({"source_position": a["source_position"], "offsets": heads, "deltas": value})
        if heads:
            offsets[min(heads)].append(value)
        for seam, h in enumerate(heads):
            by_seam[seam, h].append(value)

    def summarize(values):
        return {key: [average([row[key][i] for row in values]) for i in range(len(RADII))] for key in METRICS}

    ring_changes = [
        {"ring": a["ring"], "union": deltas(a["union"], b["union"]),
         "individual": [deltas(u["balls"], v["balls"])
                        for u, v in zip(a["individual"], b["individual"], strict=True)]}
        for a, b in zip(first["rings"], second["rings"]) if a["is_ring"] == b["is_ring"]
    ]
    return {"path": path, "by_offset": {h: summarize(v) for h, v in sorted(offsets.items())},
            "by_each_seam_offset": {f"{seam}:{h}": summarize(v) for (seam, h), v in sorted(by_seam.items())}
            if len({seam for seam, _ in by_seam}) > 1 else {},
            "rings": ring_changes}


def comparison_panel(result):
    runs = result["run_index"]
    profiles = result["profiles"]
    pairs = []
    exact_pairs = {}
    pairs_cache = {}

    def add(first, second, kind):
        a, b = runs[first]["ages"], runs[second]["ages"]
        common = sorted(a.keys() & b.keys(), key=int)
        grades = {}
        for age in common:
            mark = (a[age], b[age])
            if mark not in pairs_cache:
                key = str(len(pairs_cache))
                pairs_cache[mark] = key
                exact_pairs[key] = profile_difference(profiles[mark[0]], profiles[mark[1]])
            grades[age] = pairs_cache[mark]
        pairs.append({"first": first, "second": second, "kind": kind, "matched_ages": grades,
                      "first_only_ages": sorted(a.keys() - b.keys(), key=int),
                      "second_only_ages": sorted(b.keys() - a.keys(), key=int)})

    sources = {}
    passive = {}
    for name, run in runs.items():
        geom, table = run["base_case"], tuple(run["table"])
        if run["family"] == "source":
            sources[geom, table, run["load_mask"]] = name
        key = geom, run["family"], run["arm"], run["load_mask"]
        if table == ("P", "P"):
            if key in passive:
                raise ValueError(f"ambiguous passive comparison {key}")
            passive[key] = name
    for name, run in runs.items():
        typ = run["family"]
        geom, table, load = run["base_case"], tuple(run["table"]), run["load_mask"]
        quiet = run.get("matched_quiet")
        if quiet in runs and quiet != name:
            add(name, quiet, "preparation_vs_matched_quiet")
        inactive = passive.get((geom, typ, run["arm"], load))
        if inactive and inactive != name:
            add(name, inactive, "same_preparation_passive_table")
        if typ == "source":
            controls = [("J1", "J0"), ("J2", "J1"), ("J2", "J0"), ("J1", "C1"), ("T8", "T4")]
            if geom in ("J0", "J1", "J2", "T4", "T8", "C1"):
                controls.append((geom, "B"))
            for field, other in controls:
                other_load = 0 if other in ("B", "C1") else load
                match = sources.get((other, table, other_load)) if field == geom else None
                if match and (other != "C1" or not load):
                    add(name, match, "matched_geometry_comparator")
            if geom in ("T4", "T8") and not (load & 2):
                single = sources.get(("J1", table, load))
                if single:
                    add(name, single, "additional_quiet_ring")

    receiver_rows = []
    for (geom, table, mask), quiet in sources.items():
        if geom not in ("T4", "T8") or mask:
            continue
        cases = {mask: sources[(geom, table, mask)] for mask in range(4)}
        ages = {mask: runs[key]["ages"] for mask, key in cases.items()}
        all_ages = sorted(set.union(*(set(row) for row in ages.values())), key=int)
        for age in all_ages:
            found = {mask: profiles[row[age]] for mask, row in ages.items() if age in row}
            outcomes = []
            for receiver, own_load in itertools.product(range(2), range(2)):
                without = own_load << receiver
                with_donor = without | (1 << (1 - receiver))
                change = None
                if without in found and with_donor in found:
                    a = found[with_donor]["rings"][receiver]
                    b = found[without]["rings"][receiver]
                    change = {"union": deltas(a["union"], b["union"]),
                              "individual": [deltas(u["balls"], v["balls"])
                                             for u, v in zip(a["individual"], b["individual"], strict=True)],
                              "ordinary_knot_step_balls": {
                                  k: [u - v for u, v in zip(row, b["ordinary_knot_step_balls"][k], strict=True)]
                                  for k, row in a["ordinary_knot_step_balls"].items()
                              }}
                outcomes.append({"receiver": receiver, "receiver_loaded": bool(own_load),
                                 "first_mask": with_donor, "second_mask": without, "changes": change})
            interaction = None
            if len(found) == 4:
                interaction = []
                for receiver in range(2):
                    cold, hot = (effect["changes"]["union"] for effect in outcomes if effect["receiver"] == receiver)
                    interaction.append(deltas(hot, cold))
            receiver_rows.append({"base_case": geom, "table": table, "age": int(age), "runs": cases,
                                  "available_load_masks": sorted(found), "own_state_fixed": outcomes,
                                  "interaction_by_receiver": interaction})
    return {"pair_index": pairs, "pair_profiles": exact_pairs, "receiver_contrasts": receiver_rows}


def passive_replay(result):
    raw = prior.STAGES.with_name("bond_profiles.json").read_bytes()
    previous = {(row["case"], str(row["age"])): row for row in json.loads(raw)["records"]}
    checks = Counter()
    for run in result["run_index"].values():
        if run["table"] != ["P", "P"] or run["family"] != "source" or run["load_mask"]:
            continue
        for age, profile_id in run["ages"].items():
            expected = previous.get((run["base_case"], age))
            if not expected:
                continue
            today = result["profiles"][profile_id]
            for observed, original in zip(today["path"], expected["path"], strict=True):
                for field, reference in (("distinctions", "balls_full"),
                                         ("original_path_distinctions", "balls_restricted")):
                    for i, radius in enumerate(RADII):
                        count = original[reference][str(radius)]["count"]
                        lo, hi = observed["balls"][field][i]
                        assert original[reference][str(radius)]["exact"] and lo <= count <= hi
                        checks["exact" if lo == hi else "bounded"] += 1
    return {"prior_profiles_sha256": hashlib.sha256(raw).hexdigest(), "compared_marked_counts": checks}


def load_balls(path=DATA / "balls.json"):
    path = Path(path)
    document = json.loads(path.read_text())
    if "gzip_payload" not in document:
        return document
    payload = path.with_name(document["gzip_payload"])
    with payload.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != document["payload_sha256"]:
        raise ValueError("the compressed bond panel differs from its manifest")
    with gzip.open(payload, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def write_balls(result, target):
    target = Path(target)
    payload = target.with_suffix(".json.gz")
    with NamedTemporaryFile("w+b", dir=target.parent, delete=False) as tmp:
        staging = Path(tmp.name)
        with gzip.GzipFile(filename="", fileobj=tmp, mode="wb", mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as writer:
                json.dump(result, writer, separators=(",", ":"))
        tmp.seek(0)
        digest = hashlib.file_digest(tmp, "sha256").hexdigest()
    staging.replace(payload)
    profiles = result["profiles"]
    runs = result["run_index"]
    certification = Counter(q["certified_radius"] for p in profiles.values() for q in p["queries"])
    manifest = {
        "schema": 2, "gzip_payload": payload.name, "payload_sha256": digest,
        "growth_sha256": result["growth_sha256"], "growth_export_age_limit": result.get("growth_export_age_limit"),
        "max_age": result["max_age"], "radii": result["radii"], "query_cap": result["query_cap"],
        "all_tables_through": result.get("all_tables_through", result["max_age"]),
        "later_measurement_knot_limit": result.get("later_measurement_knot_limit"),
        "traces": len(runs), "completed_frame_references": sum(len(run["ages"]) for run in runs.values()),
        "literal_profiles": len(profiles), "queries_by_certified_radius": certification,
        "paired_comparison_references": len(result["comparisons"]["pair_index"]),
    }
    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
        staging = Path(tmp.name)
        json.dump(manifest, tmp, indent=2)
        tmp.write("\n")
    staging.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--growth", type=Path, default=DATA / "growth.json")
    parser.add_argument("--max-age", type=int, default=6)
    parser.add_argument("--full-through", type=int, default=4, help="all tables through this age, then focused arms")
    parser.add_argument("--late-knot-limit", type=int, default=3000,
                        help="knot limit for only the focused later measurements")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--controls", action="store_true")
    parser.add_argument("--out", type=Path, help="write a manifest and deterministic gzip payload")
    parser.add_argument("--pack-existing", type=Path, help="pack an already completed raw panel to --out")
    args = parser.parse_args()
    if args.pack_existing:
        if not args.out or args.controls:
            parser.error("--pack-existing requires --out and a completed raw panel")
        write_balls(load_balls(args.pack_existing), args.out)
        return
    if args.controls:
        result = direct_controls()
    else:
        if args.workers < 1:
            parser.error("--workers must be positive")
        result = read_export(args.growth, args.max_age, args.workers, args.progress, args.full_through,
                             args.late_knot_limit)
        result["comparisons"] = comparison_panel(result)
        result["passive_replay"] = passive_replay(result)
    if args.out:
        if args.controls:
            parser.error("a control-only replay has no stage manifest")
        write_balls(result, args.out)
    else:
        print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
