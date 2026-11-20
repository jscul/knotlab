"""Read literal parity bond distances and finite-stage ball profiles."""

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings"
STAGES = ROOT / "artifacts" / HERE.parent.name / HERE.name / "stages.json"
sys.path.insert(0, str(PRIOR))
from order_reader import prepare_native
from short_bonds import short_table

INFINITY = "infinite"
UNKNOWN = "unresolved"
VERTEX_LIMIT = 128
BUNDLE_LIMIT = 2000
NATIVE_SECONDS = 60
HALF_LIMIT = 1_500_000
MATCH_LIMIT = 16_000_000
PATH_STATES = 50_000
RADII = (1, 2, 3, 4, 5)


class WiredStage:
    def __init__(self, stars):
        self.stars = [tuple(star) for star in stars]
        owner = defaultdict(list)
        for v, star in enumerate(self.stars):
            if not star or len(set(star)) != len(star):
                raise ValueError("every literal support must be nonempty with distinct names")
            for distinction in star:
                owner[distinction].append(v)
        if not owner or any(len(holders) not in (1, 2) for holders in owner.values()):
            raise ValueError("literal parity wiring requires one or two ordinary holders per name")
        self.names = sorted(owner)
        self.owner = dict(owner)
        self.outside = len(self.stars) if any(len(pair) == 1 for pair in owner.values()) else None
        bundles = defaultdict(list)
        for name in self.names:
            pair = owner[name]
            endpoints = tuple(pair) if len(pair) == 2 else (pair[0], self.outside)
            bundles[endpoints].append(name)
        self.links = sorted(bundles)
        self.bundles = [bundles[link] for link in self.links]
        self.bundle_of = {name: i for i, bundle in enumerate(self.bundles) for name in bundle}
        index = {link: i for i, link in enumerate(self.links)}
        graph = nx.Graph()
        graph.add_edges_from(self.links)
        self.blocks = sorted(
            tuple(sorted(index[tuple(sorted(edge))] for edge in block))
            for block in nx.biconnected_component_edges(graph)
        )
        if sorted(i for block in self.blocks for i in block) != list(range(len(self.links))):
            raise AssertionError("every weighted holder pair must belong to one edge block")
        self.block_of = {edge: j for j, block in enumerate(self.blocks) for edge in block}

    def local_edges(self, block):
        vertices = sorted({v for index in block for v in self.links[index]})
        position = {v: i for i, v in enumerate(vertices)}
        edges = []
        for e in block:
            u, v = self.links[e]
            edges.append((position[u], position[v], len(self.bundles[e])))
        return len(vertices), edges

    def co_support_steps(self, start, targets):
        """Length of a chain of names sharing an ordinary literal support."""
        target = set(targets)
        distance = {start: 0}
        queue = deque([start])
        expanded = set()
        while queue:
            name = queue.popleft()
            target.discard(name)
            if not target:
                break
            for holder in self.owner[name]:
                if holder in expanded:
                    continue
                expanded.add(holder)
                for nxt in self.stars[holder]:
                    if nxt not in distance:
                        distance[nxt] = distance[name] + 1
                        queue.append(nxt)
        return {name: distance.get(name, INFINITY) for name in targets}


def native_table(binary, vertices, edges, queries):
    fields = [vertices, len(edges), len(queries)]
    fields.extend(x for link in edges for x in link)
    fields.extend(queries)
    result = subprocess.run([str(binary), "pairs"], input=" ".join(map(str, fields)), text=True,
                            capture_output=True, timeout=NATIVE_SECONDS, check=True)
    values = [int(token) for token in result.stdout.split()]
    width = len(edges)
    if len(values) != width * len(queries):
        raise ValueError("archive pair solver returned an incomplete table")
    return {q: values[i * width:(i + 1) * width] for i, q in enumerate(queries)}


def bounded_half_count(edges, cutoff):
    ways = [[0 for _ in range(cutoff + 1)] for _ in range(4)]
    ways[0][0] = 1
    for _, _, weight in edges:
        if weight > cutoff:
            continue
        for size in range(3, 0, -1):
            for cost in range(weight, cutoff + 1):
                ways[size][cost] += ways[size - 1][cost - weight]
    return sum(map(sum, ways))


class SearchLimit(Exception):
    pass


class AnchoredCuts:
    """Exact bounded enumeration of bonds through a given holder pair."""

    def __init__(self, vertices, edges):
        self.edges = edges
        self.vertex_count = vertices
        self.adjacency = [[] for _ in range(vertices)]
        for i, (u, v, weight) in enumerate(edges):
            self.adjacency[u].append((v, i))
            self.adjacency[v].append((u, i))
        self.states = 0

    def path_or_component(self, start, target, removed):
        previous = [None] * self.vertex_count
        previous[start] = (-1, -1)
        pending = deque([start])
        while pending:
            u = pending.popleft()
            if u == target:
                route = []
                while u != start:
                    u, edge = previous[u]
                    route.append(edge)
                return route, None
            for v, edge in self.adjacency[u]:
                if previous[v] is None and not (removed >> edge) & 1:
                    previous[v] = (u, edge)
                    pending.append(v)
        return None, {v for v, source in enumerate(previous) if source is not None}

    def through(self, query, cutoff):
        source, target, weight = self.edges[query]
        best = [cutoff + 1] * len(self.edges)
        if weight > cutoff:
            return best

        def complete(removed, fixed, chosen, cost):
            self.states += 1
            if self.states > PATH_STATES:
                raise SearchLimit
            path, shore = self.path_or_component(source, target, removed)
            if path is None:
                _, complement = self.path_or_component(target, source, removed)
                if len(shore) + len(complement) != self.vertex_count:
                    return
                if any((self.edges[e][0] in shore) == (self.edges[e][1] in shore) for e in chosen):
                    return
                for e in chosen:
                    best[e] = min(best[e], cost)
                return
            for e in path:
                flag = 1 << e
                added = self.edges[e][2]
                if not fixed & flag and cost + added <= cutoff:
                    complete(removed | flag, fixed, (*chosen, e), cost + added)
                    fixed |= flag

        complete(1 << query, 0, (query,), weight)
        return best


def distance_values(costs, cutoff=None):
    if cutoff is None:
        return [INFINITY if cost < 0 else cost - 1 for cost in costs]
    return [f">{cutoff - 1}" if cost > cutoff else cost - 1 for cost in costs]


def block_table(stage, block, needed, binary, prefer_full):
    vertices, edges = stage.local_edges(block)
    index = {global_id: j for j, global_id in enumerate(block)}
    queries = sorted(index[e] for e in needed)
    limits = []
    if prefer_full and vertices <= VERTEX_LIMIT and len(edges) <= BUNDLE_LIMIT:
        try:
            values = native_table(binary, vertices, edges, queries)
        except subprocess.TimeoutExpired:
            limits.append("native timeout")
        else:
            return {block[q]: distance_values(row) for q, row in values.items()}, {
                "method": "exact pinned connected cuts", "vertices": vertices, "bundles": len(edges),
                "queries": len(queries), "limits": limits,
            }
    elif prefer_full:
        limits.append("native size limit")

    cutoff = max(RADII) + 1
    if len(edges) <= BUNDLE_LIMIT and bounded_half_count(edges, cutoff) <= HALF_LIMIT:
        adapter = SimpleNamespace(vertices=vertices, links=[(u, v) for u, v, _ in edges],
                                  bags=[range(weight) for _, _, weight in edges])
        table, features = short_table(adapter, cutoff, half_limit=HALF_LIMIT, match_limit=MATCH_LIMIT)
        if table is not None:
            return {block[q]: distance_values(table[q], cutoff) for q in queries}, {
                "method": "exhaustive short bonds", "vertices": vertices, "bundles": len(edges),
                "queries": len(queries), "cutoff": cutoff, "limits": limits, "short_stats": features,
            }
        limits.append(features["limit_hit"])
    else:
        limits.append("short-bond bank size limit")

    reader = AnchoredCuts(vertices, edges)
    found = {block[q]: [UNKNOWN] * len(edges) for q in queries}
    attained = {}
    try:
        for cap in range(min(RADII) + 1, cutoff + 1):
            for q in queries:
                values = reader.through(q, cap)
                found[block[q]] = distance_values(values, cap)
                attained[block[q]] = cap - 1
    except SearchLimit:
        limits.append("anchored path state cap")
    return found, {
        "method": "bounded anchored path branching", "vertices": vertices, "bundles": len(edges),
        "queries": len(queries), "limits": sorted(set(limits)), "path_states": min(reader.states, PATH_STATES),
        "exact_radii_through_bundle": attained,
    }


def read_rows(stage, origins, binary, prefer_full):
    by_block = defaultdict(set)
    for name in origins:
        edge = stage.bundle_of[name]
        by_block[stage.block_of[edge]].add(edge)
    rows = {}
    methods = []
    for ordinal, needed in sorted(by_block.items()):
        block = stage.blocks[ordinal]
        rows_here, receipt = block_table(stage, block, needed, binary, prefer_full)
        methods.append({"wired_block": ordinal, **receipt})
        for edge, distances in rows_here.items():
            row = [INFINITY] * len(stage.links)
            for target, distance in zip(block, distances, strict=True):
                row[target] = distance
            rows[edge] = row
    return rows, methods


def value_at(stage, rows, first, second):
    if first == second:
        return 0
    return rows[stage.bundle_of[first]][stage.bundle_of[second]]


def in_ball(distance, radius):
    if isinstance(distance, int):
        return distance <= radius
    if distance == INFINITY or (distance.startswith(">") and int(distance[1:]) >= radius):
        return False
    return None


def balls(stage, rows, origin, names):
    distances = [value_at(stage, rows, origin, target) for target in names]
    out = {}
    for radius in RADII:
        status = [in_ball(distance, radius) for distance in distances]
        count = status.count(True)
        unresolved = status.count(None)
        out[str(radius)] = {"count": count, "exact": not unresolved,
                            "unresolved": unresolved, "saturated": count == len(names)}
    return out


def minimum(values):
    if not values or all(v == INFINITY for v in values):
        return INFINITY if values else UNKNOWN
    upper = min((value for value in values if isinstance(value, int)), default=None)
    lower = min((value if isinstance(value, int) else
                 int(value[1:]) + 1 if value.startswith(">") else 1
                 for value in values if value != INFINITY), default=None)
    if lower == upper:
        return upper
    return {"lower": lower, "upper": upper}


def source_marks(case):
    roles = case["input"]["roles"]
    source = WiredStage(case["stages"]["0"]["stars"])
    path = roles["anchors"]
    positions = roles["background"]
    if path and len(positions) != 1 + len(path):
        raise ValueError("path marks must correspond to successive source junctions")
    for i, name in enumerate(path):
        if set(source.owner[name]) != set(positions[i:i + 2]):
            raise AssertionError("incorrect literal shared path mark")
    seams = roles["seams"]
    ring_marks = []
    for vertices, edges in zip(roles["rings"], roles["ring_edges"], strict=True):
        for i, name in enumerate(edges):
            if set(source.owner[name]) != {vertices[i], vertices[(i + 1) % len(vertices)]}:
                raise AssertionError("incorrect literal shared ring mark")
        exclusive = set(vertices) - set(seams)
        ring_marks.append({
            "shared": edges,
            "selected": [edges[1], edges[3]],
            "exclusive": [name for name, owners in source.owner.items() if set(owners) <= exclusive],
            "exclusive_shared": [name for name in edges if set(source.owner[name]) <= exclusive],
        })
    offsets = []
    for name in path:
        offsets.append(min(abs(positions.index(u) - positions.index(v)) for u in source.owner[name] for v in seams)
                       if seams else None)
    return path, ring_marks, offsets


def stage_read(name, case, age, binary):
    start = time.monotonic()
    stage_data = case["stages"][str(age)]
    stage = WiredStage(stage_data["stars"])
    path, rings, offsets = source_marks(case)
    selected = list(path)
    for ring in rings:
        selected.extend(ring["selected"])
    origins = set(selected)
    if len(rings) == 2:
        origins.update(rings[0]["exclusive"])
    rows, methods = read_rows(stage, sorted(origins), binary,
                              prefer_full=age <= 1 or len(stage.stars) <= 18)
    out = {
        "case": name, "age": age, "cluster_size": age + 1,
        "junctions": len(stage.stars), "distinctions": len(stage.names), "bundles": len(stage.links),
        "outside_used_for_loose_incidence": stage.outside is not None, "methods": methods,
        "path": [], "rings": [],
    }
    for i, mark in enumerate(path):
        out["path"].append({
            "e": i, "name": mark, "h": offsets[i],
            "balls_full": balls(stage, rows, mark, stage.names),
            "balls_restricted": balls(stage, rows, mark, path),
            "path_bond_distances": [value_at(stage, rows, mark, other) for other in path],
        })
    for ring in rings:
        ring_rows = []
        for label, mark in zip(("c1-c2", "c3-c4"), ring["selected"], strict=True):
            ring_rows.append({
                "mark": label, "name": mark,
                "balls_full": balls(stage, rows, mark, stage.names),
                "balls_original_ring_shared": balls(stage, rows, mark, ring["shared"]),
                "ring_shared_bond_distances": [value_at(stage, rows, mark, dest) for dest in ring["shared"]],
                "co_support_steps": list(stage.co_support_steps(mark, ring["shared"]).values()),
            })
        out["rings"].append(ring | {"readings": ring_rows})
    if len(rings) == 2:
        for tag in ("exclusive", "exclusive_shared"):
            across = []
            for u in rings[0][tag]:
                steps = stage.co_support_steps(u, rings[1][tag])
                across.extend({"first": u, "second": v, "bond_distance": value_at(stage, rows, u, v),
                               "co_support_steps": steps[v]} for v in rings[1][tag])
            out[f"between_rings_{tag}"] = {
                "minimum_bond_distance": minimum([pair["bond_distance"] for pair in across]),
                "minimum_co_support_steps": minimum([pair["co_support_steps"] for pair in across]),
                "pairs": across,
            }
    if age <= 1:
        out["marked_rows"] = {
            "holder_bundles": stage.bundles,
            "origins": [{"literal_name": mark, "own_bundle": stage.bundle_of[mark],
                         "bond_distance_to_distinct_name_in_bundle": rows[stage.bundle_of[mark]]}
                        for mark in sorted(origins)],
        }
    out["seconds"] = time.monotonic() - start
    return out


COMPARISONS = tuple((variant, "B") for variant in ("J0", "J1", "J2", "T4", "T8", "C1")) + (
    ("J1", "J0"), ("J2", "J0"), ("J2", "J1"), ("J1", "C1"),
)


def average_record(values, planned):
    return {
        "exact": len(values), "planned": planned,
        "mean_signed_delta": str(Fraction(sum(values), len(values))) if values else None,
        "mean_absolute_delta": str(Fraction(sum(map(abs, values)), len(values))) if values else None,
        "delta_histogram": dict(sorted(Counter(values).items())),
    }


def ball_comparison(first, second, key):
    out = {}
    for radius in RADII:
        grouped = defaultdict(list)
        for a, b in zip(first, second, strict=True):
            bucket = a["h"] if a["h"] is not None else b["h"]
            row_a, row_b = a[key][str(radius)], b[key][str(radius)]
            value = row_a["count"] - row_b["count"] if row_a["exact"] and row_b["exact"] else None
            grouped[bucket].append(value)
        todo = {
            str(h): average_record([v for v in values if v is not None], len(values))
            for h, values in sorted(grouped.items())
        }
        for label, keep in (("near", lambda h: h == 0), ("far", lambda h: h >= 3)):
            selected = [v for h, values in grouped.items() if keep(h) for v in values]
            todo[label] = average_record([v for v in selected if v is not None], len(selected))
        out[str(radius)] = todo
    return out


def pair_comparison(first, second):
    finite = []
    censored = 0
    exact_infinite = 0
    finite_from_infinite = 0
    infinite_from_finite = 0
    for i, (a, b) in enumerate(zip(first, second, strict=True)):
        for observed, reference in zip(a["path_bond_distances"][i + 1:], b["path_bond_distances"][i + 1:], strict=True):
            if isinstance(observed, int) and isinstance(reference, int):
                finite.append(observed - reference)
            elif observed == reference == INFINITY:
                exact_infinite += 1
            elif isinstance(observed, int) and reference == INFINITY:
                finite_from_infinite += 1
            elif observed == INFINITY and isinstance(reference, int):
                infinite_from_finite += 1
            else:
                censored += 1
    return {"delta_histogram": dict(sorted(Counter(finite).items())), "finite_comparisons": len(finite),
            "exact_equal_infinite": exact_infinite, "finite_from_infinite": finite_from_infinite,
            "infinite_from_finite": infinite_from_finite, "censored": censored}


def contrasts(records):
    by = {(row["case"], row["age"]): row for row in records}
    out = []
    for name, reference in COMPARISONS:
        for case, age in sorted(by):
            if case != name or (reference, age) not in by:
                continue
            first, second = by[case, age]["path"], by[reference, age]["path"]
            out.append({"case": case, "reference": reference, "age": age,
                        "matched_path_pairs": pair_comparison(first, second),
                        "full_balls": ball_comparison(first, second, "balls_full"),
                        "restricted_balls": ball_comparison(first, second, "balls_restricted")})
    return out


GLOBAL = {}


def setup(params):
    path = Path(params.get("stages", STAGES))
    raw = path.read_bytes()
    GLOBAL["study"] = json.loads(raw)
    GLOBAL["panel"] = params.get("panel", "all")
    if "binary" in params:
        GLOBAL["binary"] = Path(params["binary"])
    else:
        GLOBAL["scratch"] = tempfile.TemporaryDirectory(prefix="eddy-bound-cuts-")
        GLOBAL["binary"] = prepare_native(GLOBAL["scratch"].name)


def cases():
    data = GLOBAL["study"]["cases"]
    ages = sorted({int(age) for case in data.values() for age in case["stages"]})
    panel = GLOBAL["panel"]
    for age in ages:
        if (panel == "first" and age > 1) or (panel == "later" and age < 2):
            continue
        for key, value in data.items():
            if panel == "smoke" and (key != "B" or age > 1):
                continue
            if str(age) in value["stages"]:
                yield f"{key}-{age:02}", (key, age)


def run(case_id, payload):
    key, age = payload
    return stage_read(key, GLOBAL["study"]["cases"][key], age, GLOBAL["binary"])


def literal_states_distances(stars):
    names = sorted({name for star in stars for name in star})
    index = {name: i for i, name in enumerate(names)}
    masks = [sum(1 << index[name] for name in star) for star in stars]
    total = 1 << len(names)
    states = [x for x in range(total) if all((x & mask).bit_count() % 2 == 0 for mask in masks)]
    free = [len({x & mask for x in states}) == 1 << mask.bit_count() for mask in range(total)]
    bonds = []
    table = [[INFINITY] * len(names) for _ in names]
    for i, row in enumerate(table):
        row[i] = 0
    for mask in range(1, total):
        if free[mask]:
            continue
        selected = [i for i in range(len(names)) if mask & (1 << i)]
        if not all(free[mask ^ (1 << i)] for i in selected):
            continue
        bonds.append([names[i] for i in selected])
        for a, b in itertools.combinations(selected, 2):
            d = len(selected) - 1
            if table[a][b] == INFINITY or d < table[a][b]:
                table[a][b] = table[b][a] = d
    return table, len(states), bonds


def wired_control_stars(links):
    stars = [[] for _ in range(1 + max(max(a, b) for a, b, _ in links))]
    name = 0
    for a, b, weight in links:
        for _ in range(weight):
            stars[a].append(name)
            stars[b].append(name)
            name += 1
    return stars


def controls(binary):
    host = [(0, 1, 1), (2, 3, 1), (0, 3, 1), (1, 2, 1), (1, 3, 5)]
    cases = {
        "host": wired_control_stars(host),
        "single_attachment": wired_control_stars(host + [(0, 4, 3)]),
        "two_terminal_attachment": wired_control_stars(host + [(0, 4, 1), (2, 4, 1)]),
        "loose_outside": [[0, 1, 2], [0, 3, 4]],
        "size_two_ties": wired_control_stars([(0, 1, 1), (1, 2, 1), (0, 2, 1)]),
        "independent_parts": wired_control_stars([(0, 1, 3), (2, 3, 3)]),
    }
    receipts = {}
    for tag, stars in cases.items():
        stage = WiredStage(stars)
        truth, states, bonds = literal_states_distances(stars)
        exact, _ = read_rows(stage, stage.names, binary, prefer_full=True)
        bounded, _ = read_rows(stage, stage.names, binary, prefer_full=False)
        for i, a in enumerate(stage.names):
            for j, b in enumerate(stage.names):
                value = value_at(stage, exact, a, b)
                if value != truth[i][j]:
                    raise AssertionError((tag, a, b, value, truth[i][j]))
                clipped = value_at(stage, bounded, a, b)
                if any(in_ball(clipped, r) != in_ball(value, r) for r in RADII):
                    raise AssertionError((tag, a, b, value, clipped))
        for block in stage.blocks:
            vertices, edges = stage.local_edges(block)
            local = AnchoredCuts(vertices, edges)
            for query, a in enumerate(block):
                row = distance_values(local.through(query, 6), cutoff=6)
                full = exact[a]
                for j, b in enumerate(block):
                    if any(in_ball(row[j], r) != in_ball(full[b], r) for r in RADII):
                        raise AssertionError(("anchored", tag, a, b, row[j], full[b]))
        receipts[tag] = {"distinctions": len(stage.names), "allowed_states": states,
                         "minimal_nonfree_sets": bonds, "marked_pair_0_1": truth[0][1],
                         "all_values_replayed": True, "all_five_balls_replayed": True}
    if [receipts[k]["marked_pair_0_1"] for k in ("host", "single_attachment", "two_terminal_attachment")] != [6, 6, 3]:
        raise AssertionError("attachment control lost the connected-cut obstruction")
    return receipts


def collect(run_dirs):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    all_rows = []
    omitted = []
    for folder in run_dirs:
        for case_id, record in sorted(load_results(str(folder)).items()):
            if record["status"] == "ok":
                all_rows.append(record["result"])
            else:
                omitted.append({"case_id": case_id, "reason": record["status"]})
    if len({(row["case"], row["age"]) for row in all_rows}) != len(all_rows):
        raise ValueError("run groups overlap")
    return {"records": all_rows, "comparisons": contrasts(all_rows), "omitted": omitted}


def validate_panel(stage_path, profile_path, independent_path):
    raw = stage_path.read_bytes()
    study = json.loads(raw)["cases"]
    profiles = json.loads(profile_path.read_text())
    rows = {(row["case"], row["age"]): row for row in profiles["records"]}
    expected = {(name, int(age)) for name, case in study.items() for age in case["stages"]}
    if set(rows) != expected or len(rows) != len(profiles["records"]) or profiles["omitted"]:
        raise AssertionError("bond profiles must cover the entire supplied stage roster")
    extensions = 0
    exact_balls = Counter()
    censored_balls = Counter()
    methods = Counter()
    for name, case in study.items():
        old_stars = []
        old_labels = set()
        for age in sorted(map(int, case["stages"])):
            stars = case["stages"][str(age)]["stars"]
            if age:
                if stars[:len(old_stars)] != old_stars:
                    raise AssertionError((name, age, "earlier supports must remain as equations"))
                new_stars = stars[len(old_stars):]
                new_counts = Counter(label for star in new_stars for label in star)
                if not all(any(label not in old_labels and new_counts[label] == 1 for label in star)
                           for star in new_stars):
                    raise AssertionError((name, age, "each new equation needs a distinct fresh distinction"))
                extensions += 1
            old_stars = stars
            old_labels = {label for star in stars for label in star}
            record = rows[name, age]
            if (record["junctions"], record["distinctions"]) != (len(stars), len(old_labels)):
                raise AssertionError((name, age, "literal roster size does not match profile"))
            methods.update(m["method"] for m in record["methods"])
            ring_marks = [mark for ring in record["rings"] for mark in ring["readings"]]
            for mark in record["path"] + ring_marks:
                for ball_type, by_radius in mark.items():
                    if ball_type.startswith("balls_"):
                        for value in by_radius.values():
                            (exact_balls if value["exact"] else censored_balls)[ball_type] += 1
            for rec in record["path"]:
                for radius, value in rec["balls_restricted"].items():
                    direct = [in_ball(dist, int(radius)) for dist in rec["path_bond_distances"]]
                    if (value["count"], value["unresolved"]) != (direct.count(True), direct.count(None)):
                        raise AssertionError((name, age, rec["e"], radius, "restricted ball mismatch"))

    source_pair_checks = 0
    independent = json.loads(independent_path.read_text())
    for name, matrix in independent["matrices"].items():
        actual = [mark["path_bond_distances"] for mark in rows[name, 0]["path"]]
        if actual != matrix:
            raise AssertionError((name, "independent source pair table mismatch"))
        source_pair_checks += len(actual) * (len(actual) - 1) // 2
    if source_pair_checks != independent["verified_pairs"]:
        raise AssertionError("independent receipt and replay count disagree")
    return {"stage_sha256": hashlib.sha256(raw).hexdigest(), "stages": len(rows),
            "fresh_witness_extensions": extensions, "exact_balls": exact_balls,
            "censored_balls": censored_balls, "block_methods": methods,
            "independent_source_pair_checks": source_pair_checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    compile_cmd = commands.add_parser("compile")
    compile_cmd.add_argument("directory", type=Path)
    control_cmd = commands.add_parser("controls")
    control_cmd.add_argument("binary", type=Path)
    single_cmd = commands.add_parser("single")
    single_cmd.add_argument("case")
    single_cmd.add_argument("age", type=int)
    single_cmd.add_argument("binary", type=Path)
    single_cmd.add_argument("--stages", type=Path, default=STAGES)
    collect_cmd = commands.add_parser("collect")
    collect_cmd.add_argument("run_dirs", type=Path, nargs="+")
    validate_cmd = commands.add_parser("validate")
    validate_cmd.add_argument("profile", type=Path)
    validate_cmd.add_argument("--stages", type=Path, default=STAGES)
    validate_cmd.add_argument("--independent-source", type=Path, default=STAGES.with_name("source_bonds.json"))
    args = parser.parse_args()
    if args.action == "compile":
        print(prepare_native(args.directory))
    elif args.action == "controls":
        print(json.dumps(controls(args.binary), indent=2))
    elif args.action == "single":
        study = json.loads(args.stages.read_text())
        print(json.dumps(stage_read(args.case, study["cases"][args.case], args.age, args.binary)))
    elif args.action == "validate":
        print(json.dumps(validate_panel(args.stages, args.profile, args.independent_source), indent=2))
    else:
        print(json.dumps(collect(args.run_dirs), indent=2))


if __name__ == "__main__":
    main()
