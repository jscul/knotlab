#!/usr/bin/env python3
"""Independent public bitmap census and structural split audit."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path

from reference import digest, equivalent, load, read_jsonl, require


BASES = {"A": (3, 4, 1), "B": (4, 3, 2), "C": (3, 5, 1), "D": (5, 3, 2), "E": (5, 2, 2), "F": (4, 4, 1)}
QUOTAS = {
    "A": ("vertical", "horizontal", "compound"), "B": ("horizontal", "compound", "compound"),
    "C": ("vertical", "horizontal", "compound"), "D": ("vertical", "horizontal", "compound"),
    "E": ("horizontal", "horizontal", "horizontal", "compound"),
    "F": ("vertical", "horizontal", "compound", "compound"),
}
SALT_PREFIX = "varied-letter-drawings-20261122-v1-"


def order_hash(mode, value):
    serial = json.dumps(value, separators=(",", ":")) if type(value) is not str else value
    return digest((SALT_PREFIX + mode + ":" + serial).encode("ascii"))


def support(pixels):
    require(type(pixels) is str and len(pixels) == 64 and set(pixels) <= {"0", "1"}, "Malformed bitmap")
    occupied = tuple(divmod(i, 8) for i, bit in enumerate(pixels) if bit == "1")
    require(bool(occupied), "The glyph is empty")
    return occupied


def origin(occupied):
    return tuple(map(min, zip(*occupied, strict=True)))


def normalize(occupied):
    top, left = origin(occupied)
    return tuple(sorted((row - top, col - left) for row, col in occupied))


def dimensions(occupied):
    normalized = normalize(occupied)
    return tuple(1 + max(lengths) for lengths in zip(*normalized, strict=True))


def connected(occupied):
    frontier = [occupied[0]]
    left = set(occupied[1:])
    while frontier:
        row, col = frontier.pop()
        neighbors = {(row + dr, col + dc) for dr, dc in product((-1, 0, 1), repeat=2)} & left
        left -= neighbors
        frontier.extend(neighbors)
    return not left


def turning(positions, q):
    motions = (
        lambda r, c: (r, c), lambda r, c: (c, -r), lambda r, c: (-r, -c), lambda r, c: (-c, r),
    )
    return normalize(tuple(motions[q](r, c) for r, c in positions))


def orbit(positions, mirror=False):
    reflected = tuple((r, -c) for r, c in positions)
    alternatives = (positions, reflected) if mirror else (positions,)
    return min(turning(configuration, q) for configuration, q in product(alternatives, range(4)))


def changed(point, moves):
    r, c = point
    for axis, start, stop, step in moves:
        if axis == "row" and start <= r < stop:
            c += step
        if axis == "col" and start <= c < stop:
            r += step
    return r, c


def monotone(path, axis):
    differences = tuple(tuple(y - x for x, y in zip(u, v, strict=True)) for u, v in zip(path[:-1], path[1:], strict=True))
    return all(pair[axis] == 1 and abs(pair[1 - axis]) <= 1 for pair in differences)


def draw(base, label, moves):
    width, height, stem = BASES[base]
    upright = label == "L"
    bar_row, stem_col = (height - 1, 0) if upright else (0, stem)
    stem_path = tuple(changed((r, stem_col), moves) for r in range(height))
    bar_path = tuple(changed((bar_row, c), moves) for c in range(width))
    join = stem_path[-1] if upright else stem_path[0]
    points = set(stem_path) | set(bar_path)
    if (not monotone(stem_path, 0) or not monotone(bar_path, 1) or not len(points) == height + width - 1
            or set(stem_path) & set(bar_path) != {join} or bar_path[stem_col] != join
            or dimensions(points) != (height, width)):
        return None
    if not upright and not 0 < stem_path[1][1] - bar_path[0][1] < width - 1:
        return None
    if len({turning(tuple(points), q) for q in range(4)}) != 4:
        return None
    r, c = origin(points)
    local = lambda point: (point[0] - r, point[1] - c)
    shifted = {"vertical": tuple(map(local, stem_path)), "bar": tuple(map(local, bar_path)), "junction": local(join)}
    bent = (any(a[1] != b[1] for a, b in zip(stem_path, stem_path[1:])),
            any(a[0] != b[0] for a, b in zip(bar_path, bar_path[1:])))
    bend = {(False, False): "straight", (True, False): "vertical", (False, True): "horizontal", (True, True): "compound"}[bent]
    return shifted, bend, orbit(tuple(points), mirror=True)


def build_pair(base, moves):
    left, right = (draw(base, label, moves) for label in "LT")
    if left is None or right is None or left[1] != right[1] or left[2] == right[2]:
        return None
    return {"base_style": base, "moves": moves, "bend": left[1], "upright_strokes": {"L": left[0], "T": right[0]}}, (left[2], right[2])


def moves_for(base):
    limits = {"col": BASES[base][0], "row": BASES[base][1]}
    alternatives = {}
    for axis, boundary in limits.items():
        alternatives[axis] = [(axis, low, high, direction) for low, high in combinations(range(boundary + 1), 2)
                              if (low, high) != (0, boundary) for direction in (-1, 1)]
    single = [(one,) for axis in alternatives.values() for one in axis]
    return single + [pair for choice in (("row", "col"), ("col", "row"))
                     for pair in product(*[alternatives[axis] for axis in choice])]


def select_phase(bases, stratum, excluded):
    possible = {}
    for base in bases:
        groups = {bend: {} for bend in ("horizontal", "vertical", "compound")}
        allowed = sorted(moves_for(base), key=lambda choice: (order_hash("design", (base, choice)), choice))
        for moves in allowed:
            alternative = build_pair(base, moves)
            if alternative is None:
                continue
            design, orbits = alternative
            if design["bend"] in groups and not excluded.intersection(orbits):
                groups[design["bend"]].setdefault(orbits, design)
        possible[base] = groups

    slots = [(f"{base}-{stratum}-{i}", base, bend) for base in bases for i, bend in enumerate(QUOTAS[base], 1)]

    def assignments(index, used):
        if index == len(slots):
            yield ()
            return
        style, base, bend = slots[index]
        for pair, design in possible[base][bend].items():
            if not used.intersection(pair):
                for tail in assignments(index + 1, used.union(pair)):
                    yield ((style, design, pair), *tail)

    choice = next(assignments(0, set()), None)
    require(choice is not None, "Independent geometry search could not fill fixed quotas")
    census = {base: {bend: len(members) for bend, members in groups.items()} for base, groups in possible.items()}
    return {style: design for style, design, _ in choice}, {one for _, _, pair in choice for one in pair}, census


def independent_designs(older_orbits):
    straight = {base: build_pair(base, ())[0] for base in "ABCD"}
    training, fitted_shapes, train_counts = select_phase("ABCD", "varied", older_orbits)
    blind, _, blind_counts = select_phase("EF", "blind", older_orbits | fitted_shapes)
    return straight | training | blind, train_counts | blind_counts


def render(strokes, row, col, q):
    positions = turning(tuple(set(strokes["vertical"]) | set(strokes["bar"])), q)
    image = ["0"] * 64
    for r, c in positions:
        require(row + r < 8 and col + c < 8, "Independent rendering clips a design")
        image[(row + r) * 8 + col + c] = "1"
    return "".join(image)


def check_views(views, keys, name):
    retained = {}
    for row in views:
        require(set(row) == {"id", "pixels"}, f"{name}: undeclared public field")
        pixels = row["pixels"]
        occupied = support(pixels)
        require(connected(occupied), f"{name}: a glyph is disconnected")
        identity = row["id"]
        require(digest(pixels.encode("ascii")) == identity and identity not in retained,
                f"{name}: wrong or duplicated bitmap identity")
        retained[identity] = occupied
    require(set(retained) == set(keys), f"{name}: key/view identity mismatch")
    for identity, occupied in retained.items():
        metadata = keys[identity]
        require(metadata["label"] in ("L", "T") and type(metadata["q"]) is int and 0 <= metadata["q"] < 4,
                f"{name}: undeclared label or turn")
        require((metadata["row"], metadata["col"]) == origin(occupied), f"{name}: wrong visual anchor")
        require(all(type(metadata[name]) is int and 0 <= metadata[name] <= 3 for name in ("row", "col")),
                f"{name}: undeclared anchor")
    return retained


def verify_machine_keys(stream, old, arm):
    for new, old_key in zip(stream, old, strict=True):
        require(all(new[name] == old_key[name] for name in ("label", "q", "row", "col")),
                f"{arm} training slot broke the label, turn or anchor match")
        require(new["base_style"] == old_key["style"], f"{arm} training slot changed the matched base")
        require(new["q"] in (0, 1) and (new["row"] + new["col"]) % 2 == 1 and new["condition"] == "train",
                f"{arm}: held pose or other condition in fitting")


def census(panel_dir, predecessor_dir, initial_dir):
    previous = read_jsonl(predecessor_dir / "train.jsonl")
    previous_by_id = {row["id"]: row for row in read_jsonl(predecessor_dir / "training_key.jsonl")}
    previous_order = [previous_by_id[row["id"]] for row in previous]
    manifest = load(panel_dir / "manifest.json")
    require(digest((panel_dir.parent / "panel.py").read_bytes()) == manifest["generator"]["sha256"], "Generator hash mismatches")
    required_streams = ("train_narrow", "train_varied", "training_key_narrow", "training_key_varied", "queries", "scorer_key")
    for stream in required_streams:
        filename = stream + ".jsonl"
        path = panel_dir / filename
        known = manifest["files"][filename]
        require(known["sha256"] == digest(path.read_bytes()) and known["rows"] == len(read_jsonl(path)),
                f"Manifest commitment differs in {filename}")

    arm_views = {arm: read_jsonl(panel_dir / f"train_{arm}.jsonl") for arm in ("narrow", "varied")}
    require((panel_dir / "train_narrow.jsonl").read_bytes() == (predecessor_dir / "train.jsonl").read_bytes()
            and len(previous) == 64, "Narrow arm changed predecessor exposure")
    logical_training, supports_training, paired = {}, {}, {}
    for arm, views in arm_views.items():
        key_rows = read_jsonl(panel_dir / f"training_key_{arm}.jsonl")
        arm_keys = {row["id"]: row for row in key_rows}
        require(len(key_rows) == len(arm_keys) == 64, "Incomplete or duplicate fitting keys")
        current = [arm_keys[row["id"]] for row in views]
        supports_training[arm] = check_views(views, arm_keys, arm)
        logical_training[arm] = current
        verify_machine_keys(current, previous_order, arm)
        slots = [key["slot"] for key in current]
        require(slots == list(range(64)) and key_rows == current, f"{arm}: schedule and declared slot disagree")
        turn_balance = Counter((key["label"], key["q"]) for key in current)
        require(turn_balance == {(label, q): 16 for label, q in product("LT", (0, 1))}, "Incorrect training target balance")
        exposure = Counter((key["style"], key["label"], key["q"]) for key in current)
        require(len(exposure) == (16 if arm == "narrow" else 64) and set(exposure.values()) == ({4} if arm == "narrow" else {1}),
                f"{arm}: wrong exposure to underlying training styles")
        canonical = defaultdict(set)
        for key in current:
            canonical[key["style"], key["label"]].add(turning(supports_training[arm][key["id"]], (-key["q"]) % 4))
        require(all(len(equivalents) == 1 for equivalents in canonical.values()), f"{arm}: a style changes support across turn")
        paired[arm] = {
            "unique_bitmaps": len(supports_training[arm]),
            "style_labels": len({(key["style"], key["label"]) for key in current}),
            "rigid_orbits": len({orbit(occupied) for occupied in supports_training[arm].values()}),
            "dihedral_orbits": len({orbit(occupied, mirror=True) for occupied in supports_training[arm].values()}),
        }

    for narrow, varied in zip(logical_training["narrow"], logical_training["varied"], strict=True):
        require(narrow["slot"] == varied["slot"], "Slots differ across arms")
        before = supports_training["narrow"][narrow["id"]]
        after = supports_training["varied"][varied["id"]]
        require(len(before) == len(after) and dimensions(before) == dimensions(after),
                "Acquisition replacement changed ink or bounding dimensions")

    queries = read_jsonl(panel_dir / "queries.jsonl")
    scorer = read_jsonl(panel_dir / "scorer_key.jsonl")
    scorer_key = {row["id"]: row for row in scorer}
    require(len(scorer) == len(scorer_key) and list(scorer_key) == sorted(scorer_key), "Wrong scorer roster or ordering")
    held_shapes = check_views(queries, scorer_key, "blind")
    expected_holdout_key = {"id", "label", "condition", "style", "base_style", "style_stratum", "row", "col", "q"}
    counts = Counter()
    drawings = defaultdict(set)
    for item in scorer_key.values():
        require(set(item) == expected_holdout_key and item["style_stratum"] == "blind", "Wrong scorer metadata")
        held_position = (item["row"] + item["col"]) % 2 == 0
        want_condition = (("familiar", "position"), ("orientation", "combined"))[item["q"] >= 2][held_position]
        require(item["condition"] == want_condition, "Wrong query condition")
        counts[item["style"], item["q"], item["label"], want_condition] += 1
        upright = turning(held_shapes[item["id"]], (-item["q"]) % 4)
        drawings[item["style"], item["label"]].add(upright)
    require(set(counts.values()) == {8}, "Unbalanced query drawings within pose and label")
    require(len(counts) == 128 and len(drawings) == 16, "Missing some held style/label/pose groups")
    require(all(len(shapes) == 1 for shapes in drawings.values()), "Held style does not identify a rotational drawing")

    prior_occupied = [support(row["pixels"]) for source in (predecessor_dir, initial_dir)
                      for name in ("train.jsonl", "queries.jsonl") for row in read_jsonl(source / name)]
    fitted_occupied = [occupied for arm in supports_training.values() for occupied in arm.values()]
    designs, admitted = independent_designs({orbit(shape, mirror=True) for shape in prior_occupied})
    require(equivalent(manifest["style_designs"], designs), "Selected designs differ from independent geometry-only choice")
    require(manifest["geometry"]["admissible_distinct_pairs_by_base_and_bend"] == admitted, "Wrong geometry candidate census")
    fitting_anchor_roster = {}
    for base, q in product("ABCD", (0, 1)):
        relevant = {(key["row"], key["col"]) for key in previous_order if key["style"] == base and key["q"] == q}
        ordered = sorted(relevant, key=lambda anchor: (order_hash("anchor", (base, q, *anchor)), anchor))
        fitting_anchor_roster[base, q] = dict(zip(ordered, (base, *(f"{base}-varied-{i}" for i in range(1, 4))), strict=True))
    for arm, rows in arm_views.items():
        for raw, metadata in zip(rows, logical_training[arm], strict=True):
            base, q, row, col, style, label = (metadata[k] for k in ("base_style", "q", "row", "col", "style", "label"))
            wanted = base if arm == "narrow" else fitting_anchor_roster[base, q][row, col]
            require(style == wanted and raw["pixels"] == render(designs[style]["upright_strokes"][label], row, col, q),
                    "A matched training view differs from the independent geometry and schedule")
    blind_inputs = []
    for style, label, q, row, col in product((name for name in designs if "-blind-" in name), "LT", range(4), range(4), range(4)):
        raw = render(designs[style]["upright_strokes"][label], row, col, q)
        identity = digest(raw.encode("ascii"))
        supplied = scorer_key[identity]
        require((supplied["style"], supplied["label"], supplied["q"], supplied["row"], supplied["col"]) ==
                (style, label, q, row, col), "A blind key row changes the independently rendered drawing")
        blind_inputs.append({"id": identity, "pixels": raw})
    blind_inputs.sort(key=lambda row: (order_hash("query", row["pixels"]), row["id"]))
    require(equivalent(queries, blind_inputs), "Blind payload differs from independent bitmap rendering and order")

    unseen = {}
    for mirror in (False, True):
        blind_orbits = {orbit(occupied, mirror) for occupied in held_shapes.values()}
        train_orbits = {orbit(occupied, mirror) for occupied in fitted_occupied}
        older_orbits = {orbit(occupied, mirror) for occupied in prior_occupied}
        unseen[str(mirror).lower()] = {
            "blind_orbits": len(blind_orbits), "overlap_with_fit": len(blind_orbits & train_orbits),
            "overlap_with_predecessors": len(blind_orbits & older_orbits),
        }
    require(all(measures == {"blind_orbits": 16, "overlap_with_fit": 0, "overlap_with_predecessors": 0}
                for measures in unseen.values()), "Blind supports overlap a fitted or prior orbit")

    return {"training": paired, "training_slots": 64, "matched": ["action", "turn", "row", "col", "base", "ink", "dimensions", "slot"],
            "training_overlap": len(set(supports_training["narrow"]) & set(supports_training["varied"])),
            "blind_bitmaps": len(queries), "blind_style_letter_drawings": len(drawings),
            "each_held_style_letter_turn_position_count": 8, "support_novelty_allowing_reflections": unseen,
            "independent_geometry_variants": len(designs), "geometry_admitted_pairs": admitted,
            "artifact_stream_digests": {name: digest((panel_dir / (name + ".jsonl")).read_bytes()) for name in required_streams}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("first_panel", type=Path)
    config = parser.parse_args()
    print(json.dumps(census(config.panel, config.predecessor, config.first_panel), indent=2, sort_keys=True))
