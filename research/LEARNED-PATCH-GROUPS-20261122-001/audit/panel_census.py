"""Verify the frozen bitmap panels without importing the producer or fitting."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


STYLES = {
    "A": (3, 4, 1), "B": (4, 3, 2), "C": (3, 5, 1),
    "D": (5, 3, 2), "E": (5, 2, 1), "F": (4, 4, 1),
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(data):
    return sha256(data).hexdigest()


def unique_fields(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "Repeated JSON field")
    return result


def loads(data):
    return json.loads(data, object_pairs_hook=unique_fields)


def read_jsonl(path):
    return [loads(line) for line in path.read_bytes().splitlines()]


def equivalent(actual, expected):
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def bitmap(style, label, q, top, left):
    width, height, stem = STYLES[style]
    horizontal = height - 1 if label == "L" else 0
    vertical = 0 if label == "L" else stem
    glyph = {(horizontal, col) for col in range(width)} | {(row, vertical) for row in range(height)}
    transforms = (
        lambda r, c: (r, c), lambda r, c: (c, height - 1 - r),
        lambda r, c: (height - 1 - r, width - 1 - c), lambda r, c: (width - 1 - c, r),
    )
    image = ["0"] * 64
    for row, col in glyph:
        r, c = transforms[q](row, col)
        require(0 <= top + r < 8 and 0 <= left + c < 8, "Clipped or out-of-bounds glyph")
        image[8 * (top + r) + left + c] = "1"
    require(image.count("1") == width + height - 1, "Incorrect lit pixel count")
    return "".join(image)


def partition(style, q, row, col):
    held = not (row ^ col) & 1
    if q >= 2:
        return "combined" if held else "orientation"
    if held:
        return "position"
    schedule = {"A": not (row ^ q) & 1, "B": (row ^ q) & 1,
                "C": not ((row >> 1) ^ q) & 1, "D": ((row >> 1) ^ q) & 1}
    return "train" if schedule.get(style, False) else "familiar"


def enumerate_panel():
    outputs = {}
    for style, label, q, row, col in product(STYLES, "LT", range(4), range(4), range(4)):
        pixels = bitmap(style, label, q, row, col)
        identity = digest(pixels.encode("ascii"))
        require(identity not in outputs, "Duplicate bitmap or digest")
        outputs[identity] = {
            "id": identity, "pixels": pixels, "style": style, "label": label, "q": q,
            "row": row, "col": col, "style_stratum": "blind" if style in "EF" else "seen",
            "condition": partition(style, q, row, col),
        }
    return outputs


def expected_files(panel):
    files = {}
    for mode, keyname in (("train", "training_key"), ("query", "scorer_key")):
        subset = [case for case in panel.values() if (case["condition"] == "train") == (mode == "train")]
        salt = f"learned-patch-groups-20261122-v1-{mode}:"
        input_name = "train" if mode == "train" else "queries"
        ordered = sorted(subset, key=lambda case: (digest((salt + case["pixels"]).encode("ascii")), case["id"]))
        files[input_name + ".jsonl"] = [{key: case[key] for key in ("id", "pixels")} for case in ordered]
        files[keyname + ".jsonl"] = [
            {field: value for field, value in case.items() if field != "pixels"}
            for case in sorted(subset, key=lambda case: case["id"])
        ]
    return files


def support(pixels):
    return tuple(divmod(index, 8) for index, bit in enumerate(pixels) if bit == "1")


def normalized(support_):
    row, col = map(min, zip(*support_, strict=True))
    return tuple(sorted((r - row, c - col) for r, c in support_))


def orbit(support_, reflections=False):
    transforms = (
        lambda r, c: (r, c), lambda r, c: (c, -r), lambda r, c: (-r, -c), lambda r, c: (-c, r),
    )
    signs = (1, -1) if reflections else (1,)
    return min(normalized(tuple(change(r, sign * c) for r, c in support_)) for change, sign in product(transforms, signs))


def verify_panel(panel_dir, earlier):
    panel = enumerate_panel()
    inputs = expected_files(panel)
    manifest = loads((panel_dir / "manifest.json").read_bytes())
    require(digest((panel_dir.parent / "panel.py").read_bytes()) == manifest["generator"]["sha256"], "Wrong generator digest")
    for name, expected in inputs.items():
        path = panel_dir / name
        require(equivalent(read_jsonl(path), expected), f"Independent rows differ in {name}")
        require(manifest["files"][name] == {"rows": len(expected), "sha256": digest(path.read_bytes())}, f"Wrong manifest: {name}")

    cell_counts = Counter((case["style_stratum"], case["condition"], case["label"]) for case in panel.values())
    expected_per_letter = {
        "seen": {"train": 32, "familiar": 32, "position": 64, "orientation": 64, "combined": 64},
        "blind": {"familiar": 32, "position": 32, "orientation": 32, "combined": 32},
    }
    wanted_cells = {stratum: {cell: {label: count for label in "LT"} for cell, count in cells.items()}
                    for stratum, cells in expected_per_letter.items()}
    require(cell_counts == Counter({(s, c, label): n for s, cells in wanted_cells.items() for c, counts in cells.items()
                                    for label, n in counts.items()}), "Wrong per-class condition counts")
    require(manifest["counts"] == wanted_cells, "Condition totals disagree with manifest")
    training = [case for case in panel.values() if case["condition"] == "train"]
    require({case["q"] for case in training} == {0, 1}, "Held turn in training")
    learning_strata = Counter((case["style"], case["q"], case["label"]) for case in training)
    require(set(learning_strata.values()) == {4} and len(learning_strata) == 16, "Unbalanced admitted calibrations")
    primary = [case for case in panel.values() if case["style_stratum"] == "blind"]
    primary_cells = Counter((case["style"], case["q"], case["condition"], case["label"]) for case in primary)
    require(len(primary_cells) == 32 and set(primary_cells.values()) == {8}, "Wrong primary conditional groups")

    new_bitmaps = {case["pixels"] for case in panel.values()}
    new_shapes = {normalized(support(pixels)) for pixels in new_bitmaps}
    new_orbits = {orbit(shape) for shape in new_shapes}
    require((len(new_bitmaps), len(new_shapes), len(new_orbits)) == (768, 48, 12), "Unexpected image/shape/orbit census")
    for reflections in (False, True):
        trained_orbits = {orbit(support(case["pixels"]), reflections) for case in training}
        blind_orbits = {orbit(support(case["pixels"]), reflections) for case in primary}
        require(len(blind_orbits) == 4 and not trained_orbits & blind_orbits, "A held style has fitting ancestry")

    previous = {case["pixels"] for path in (earlier / "train.jsonl", earlier / "queries.jsonl") for case in read_jsonl(path)}
    previous_shapes = {normalized(support(pixels)) for pixels in previous}
    previous_orbits = {orbit(shape) for shape in previous_shapes}
    overlaps = {
        "bitmap": len(new_bitmaps & previous), "normalized_support": len(new_shapes & previous_shapes),
        "rotation_orbit": len(new_orbits & previous_orbits),
    }
    require(len(previous) == 400 and set(overlaps.values()) == {0}, "The predecessor panel has shared ancestry")
    return {
        "bitmaps": len(new_bitmaps), "normalized_supports": len(new_shapes), "rotation_orbits": len(new_orbits),
        "counts": wanted_cells, "train_per_style_turn_letter": 4, "primary_per_cell_style_turn_letter": 8,
        "primary_orbits": 4, "primary_vs_train_rigid_orbit_overlap": 0, "primary_vs_train_reflected_orbit_overlap": 0,
        "predecessor_overlaps": overlaps,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("earlier", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_panel(args.panel, args.earlier), indent=2, sort_keys=True))
