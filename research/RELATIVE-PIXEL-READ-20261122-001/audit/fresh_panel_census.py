#!/usr/bin/env python3
"""Verify bitmap identity, rotations, split and ancestry without sensing features."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import sys

from tree_oracle import digest, equivalent, loads, read_jsonl, require


PRIOR_AUDIT = Path(__file__).resolve().parents[2] / "VARIED-LETTER-DRAWINGS-20261122-001/audit"
sys.path.insert(0, str(PRIOR_AUDIT))
from panel_audit import connected, dimensions, orbit, origin, support, turning
sys.path.pop(0)


STYLE_NAMES = tuple(f"{base}-relative-{i}" for base, i in product("EF", range(1, 5)))
QUOTA = {"E": ((1, "horizontal"), (1, "horizontal"), (2, "horizontal"), (3, "horizontal")),
         "F": ((2, "vertical"), (2, "horizontal"), (2, "compound"), (2, "compound"))}
SALT = "relative-pixel-read-20261122-v1-"
OLD_BANKS = {
    "PIXEL-LETTERS-20261122-001": ("letters", "train", "queries"),
    "LEARNED-PATCH-GROUPS-20261122-001": ("groups", "train", "queries"),
    "VARIED-LETTER-DRAWINGS-20261122-001": ("drawings", "train_narrow", "train_varied", "queries"),
}


def render(strokes, row, col, q):
    occupied = {tuple(cell) for path in ("stem", "bar") for cell in strokes[path]}
    transformed = turning(tuple(occupied), q)
    slots = {8 * (row + r) + col + c for r, c in transformed}
    require(all(0 <= row + r < 8 and 0 <= col + c < 8 for r, c in transformed), "A rotated drawing clips the bitmap")
    return "".join("1" if i in slots else "0" for i in range(64))


def paths(width, height, attachment, letter, first, second):
    bar = tuple((sum(first[:step]), step) for step in range(width))
    if letter == "L":
        join = bar[0]
        stem = tuple((step - height + 1, -sum(second[step:])) for step in range(height))
    else:
        join = bar[attachment]
        stem = tuple((join[0] + step, join[1] + sum(second[:step])) for step in range(height))
        if not 0 < stem[1][1] < width - 1:
            return None
    occupied = tuple(set(stem) | set(bar))
    if (set(stem) & set(bar) != {join} or len(occupied) != width + height - 1
            or dimensions(occupied) != (height, width) or len({turning(occupied, q) for q in range(4)}) != 4):
        return None
    r, c = origin(occupied)
    shift = lambda point: (point[0] - r, point[1] - c)
    result = {"stem": tuple(map(shift, stem)), "bar": tuple(map(shift, bar)), "junction": shift(join)}
    return result, orbit(occupied, mirror=True)


def design_search(denied):
    pools = {}
    tallies = {}
    raw_slots = []
    for base, quotas in QUOTA.items():
        width, height = (5, 2) if base == "E" else (4, 4)
        alternatives = list(product(product(range(-1, 2), repeat=width-1), product(range(-1, 2), repeat=height-1)))
        for stem_column in sorted({stem for stem, bend in quotas}):
            def key(profile):
                scale = json.dumps((base, stem_column, *profile), separators=(",", ":"))
                return digest((SALT + "design:" + scale).encode("ascii")), profile

            pool = {name: {} for name in ("vertical", "horizontal", "compound")}
            for first, second in sorted(alternatives, key=key):
                if not any(first) and not any(second):
                    continue
                bend = "compound" if any(first) and any(second) else "horizontal" if any(first) else "vertical"
                left, right = (paths(width, height, stem_column, letter, first, second) for letter in "LT")
                if left is None or right is None or left[1] == right[1] or denied.intersection((left[1], right[1])):
                    continue
                candidate = {"base_style": base, "width_height": (width, height), "T_stem_col": stem_column,
                             "bend": bend, "bar_steps": first, "stem_steps": second,
                             "diagonal_bar_steps": sum(bool(n) for n in first), "diagonal_stem_steps": sum(bool(n) for n in second),
                             "normalized_upright_paths": {"L": left[0], "T": right[0]}}
                pool[bend].setdefault((left[1], right[1]), candidate)
            tallies[f"{base}:{stem_column}"] = {bend: len(values) for bend, values in pool.items()}
            pools[base, stem_column] = pool
        raw_slots.extend((f"{base}-relative-{i}", base, attachment, bend)
                         for i, (attachment, bend) in enumerate(quotas, 1))

    def assignments(pos, occupied):
        if pos == len(raw_slots):
            yield ()
            return
        name, base, stem, bend = raw_slots[pos]
        for relation, design in pools[base, stem][bend].items():
            if not occupied.intersection(relation):
                for tail in assignments(pos + 1, occupied.union(relation)):
                    yield ((name, design), *tail)

    chosen = next(assignments(0, set()), None)
    require(chosen is not None, "Independent geometric allocation could not fill quotas")
    return dict(chosen), tallies


def loaded_views(panel, name):
    raw = read_jsonl(panel / f"{name}.jsonl")
    ids = {}
    for row in raw:
        require(set(row) == {"id", "pixels"}, f"Undeclared {name} public field")
        identity, bitmap = row["id"], row["pixels"]
        occupied = support(bitmap)
        require(identity == digest(bitmap.encode("ascii")) and identity not in ids, f"Invalid or duplicate {name} ID")
        require(connected(occupied), f"Disconnected support in {name}")
        ids[identity] = bitmap
    return raw, ids


def older_panels(experiments):
    exclusion = set()
    banks = {}
    for ticket, (suffix, *streams) in OLD_BANKS.items():
        family = experiments / ticket / f"{ticket}-E001_{suffix}" / "panel"
        preceding = set()
        for name in streams:
            _, ids = loaded_views(family, name)
            preceding.update(orbit(support(raw), mirror=True) for raw in ids.values())
        exclusion |= preceding
        banks[ticket] = {"panel": family, "dihedral_orbits": len(preceding)}
    return exclusion, banks


def verify_training(panel, old):
    for new, past in (("train", "train_varied"), ("training_key", "training_key_varied")):
        require((panel / f"{new}.jsonl").read_bytes() == (old / f"{past}.jsonl").read_bytes(), f"Changed archived {new} input")
    views, by_id = loaded_views(panel, "train")
    key = read_jsonl(panel / "training_key.jsonl")
    require(len(views) == len(key) == 64, "Wrong training size")
    require([row["id"] for row in views] == [row["id"] for row in key] and [row["slot"] for row in key] == list(range(64)),
            "Wrong training identity or slot order")
    require(Counter((row["label"], row["q"]) for row in key) == {(label, q): 16 for label, q in product("LT", (0, 1))},
            "Wrong training labels or allowed turn counts")
    return by_id


def verify_pair(panel, old):
    _, pair = loaded_views(panel, "diagnostic")
    key = read_jsonl(panel / "diagnostic_key.jsonl")
    prior = {row["id"]: row for row in read_jsonl(old / "scorer_key.jsonl")}
    _, prior_pixels = loaded_views(old, "queries")
    require(len(pair) == len(key) == 2 and set(pair) == {row["id"] for row in key}, "Wrong public pair roster")
    seen = set()
    for witness in key:
        identity = witness["id"]
        past = prior[identity]
        require(all(witness.get(field) == past[field] for field in ("style", "q", "label", "row", "col")),
                "Wrong held-turn public-pair provenance")
        require(pair[identity] == prior_pixels[identity] and (past["row"], past["col"]) == (1, 1), "Wrong raw public-pair bitmap")
        seen.add((past["style"], past["label"], past["q"]))
    require(seen == {("F-blind-1", "T", 2), ("F-blind-2", "L", 3)}, "Wrong predecessor collision pair")
    expected = tuple(row["id"] for row in sorted(key, key=lambda row: row["label"]))
    for new, previous in (("diagnostic", "queries"), ("diagnostic_key", "scorer_key")):
        old_lines = {loads(raw)["id"]: raw for raw in (old / f"{previous}.jsonl").read_bytes().splitlines(keepends=True)}
        require((panel / f"{new}.jsonl").read_bytes() == b"".join(old_lines[identity] for identity in expected),
                "Public pair is not the exact original bytes in registered order")
    return pair


def verify_queries(panel, manifest, denied):
    views, by_id = loaded_views(panel, "queries")
    key_rows = read_jsonl(panel / "scorer_key.jsonl")
    keys = {row["id"]: row for row in key_rows}
    require(len(views) == len(keys) == len(key_rows) == 1024 and set(keys) == set(by_id), "Wrong test roster or duplicate scorer key")
    require(list(keys) == sorted(keys), "Key must be ordered by raw bitmap digest")
    shape_count = Counter()
    units = defaultdict(set)
    orbit_names = defaultdict(set)
    designs, candidates = design_search(denied)
    require(equivalent(designs, manifest["designs"]), "Geometry-only candidate selection differs from manifest")
    require(candidates == manifest["geometry"]["admissible_pair_counts_by_base_and_stem"], "Wrong geometry admissibility census")
    for identity, row in keys.items():
        design, letter, q, row_, col = (row[name] for name in ("style", "label", "q", "row", "col"))
        require(design in STYLE_NAMES and letter in ("L", "T") and q in range(4) and row_ in range(4) and col in range(4),
                "Unexpected fresh drawing or pose")
        require(row["base_style"] == design[0] and row["style_stratum"] == "blind", "Incorrect design ancestry metadata")
        held_anchor = (row_ + col) % 2 == 0
        expected = (("familiar", "position"), ("orientation", "combined"))[q in (2, 3)][held_anchor]
        require(row["condition"] == expected, "Pose does not match split condition")
        raw = by_id[identity]
        require(raw == render(designs[design]["normalized_upright_paths"][letter], row_, col, q), "Wrong independently rendered test bitmap")
        occupied = support(raw)
        require(origin(occupied) == (row_, col), "The public bitmap does not use its declared anchor")
        require(len(occupied) == (6 if design.startswith("E") else 7), "Ink does not match the declared base")
        shape_count[design, letter, q, expected] += 1
        upright = turning(occupied, (-q) % 4)
        dims = (2, 5) if design.startswith("E") else (4, 4)
        require(dimensions(upright) == dims, "Unexpected relative drawing extent")
        units[design, letter].add(upright)
        orbit_names[orbit(occupied, mirror=True)].add((design, letter))
    require(len(shape_count) == 128 and set(shape_count.values()) == {8}, "Wrong count per independent pose stratum")
    require(len(units) == 16 and all(len(r) == 1 for r in units.values()), "Drawing does not match its full turn orbit")
    require(len(orbit_names) == 16 and all(len(r) == 1 for r in orbit_names.values()) and not denied.intersection(orbit_names),
            "Fresh drawings overlap each other or a prior support orbit")
    query_order = sorted(views, key=lambda row: (digest((SALT + "query:" + row["pixels"]).encode("ascii")), row["id"]))
    require(views == query_order, "Unexpected blind input order")
    return {"unique_fresh_bitmaps": 1024, "fresh_drawing_orbits": len(orbit_names), "per_letter_turn_position_design": 8,
            "all_drawing_letter_turn_units": 64, "held_drawing_letter_turn_units": 32,
            "prior_orbit_overlap": 0, "fresh_occupancy_pairs_checked": False, "candidate_pairs_by_stem": candidates}


def census(panel, experiments):
    manifest = loads((panel / "manifest.json").read_bytes())
    require(digest((panel.parent / "panel.py").read_bytes()) == manifest["generator"]["sha256"], "Wrong producer digest")
    old_orbits, banks = older_panels(experiments)
    most_recent = banks["VARIED-LETTER-DRAWINGS-20261122-001"]["panel"]
    training = verify_training(panel, most_recent)
    pair = verify_pair(panel, most_recent)
    blind = verify_queries(panel, manifest, old_orbits)
    _, fresh = loaded_views(panel, "queries")
    require(not (set(training) & set(pair) or set(training) & set(fresh) or set(pair) & set(fresh)), "Stage cohorts overlap")
    receipts = {}
    for filename, metadata in manifest["files"].items():
        path = panel / filename
        actual = {"rows": len(read_jsonl(path)), "sha256": digest(path.read_bytes())}
        require(equivalent(metadata, actual), f"Inconsistent manifest digest or counts for {filename}")
        receipts[filename] = actual
    return {"training_bitmaps": len(training), "pair_ids": sorted(pair), "blind": blind, "verified_files": receipts,
            "excluded_predecessor_orbits": len(old_orbits), "fresh_sensors_computed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("experiments", type=Path)
    args = parser.parse_args()
    print(json.dumps(census(args.panel, args.experiments), indent=2, sort_keys=True))
