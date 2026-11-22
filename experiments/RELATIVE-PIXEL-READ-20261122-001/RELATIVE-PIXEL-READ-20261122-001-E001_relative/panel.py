"""Freeze byte-identical training, the public diagnostic pair, and fresh blind drawings."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import accumulate, product
import json
from pathlib import Path
from tempfile import TemporaryDirectory


FAMILY = Path(__file__).resolve().parent
BITMAP_SIZE = 8
ANCHORS = tuple(product(range(4), repeat=2))
FIT_TURNS = (0, 1)
LABELS = ("L", "T")
DIMENSIONS = {"E": (5, 2), "F": (4, 4)}
QUOTAS = {
    "E": ((1, "horizontal"), (1, "horizontal"), (2, "horizontal"), (3, "horizontal")),
    "F": ((2, "vertical"), (2, "horizontal"), (2, "compound"), (2, "compound")),
}
DESIGN_SALT = "relative-pixel-read-20261122-v1-design:"
QUERY_SALT = "relative-pixel-read-20261122-v1-query:"
VARIED = "VARIED-LETTER-DRAWINGS-20261122-001"
PREDECESSORS = {
    "PIXEL-LETTERS-20261122-001": ("letters", {
        "train.jsonl": "68ee66a52191de03bcdf4782c3d99a77aa8094417b1c69a4abc5cd6b123ffe65",
        "queries.jsonl": "52594f1b1ffcbbb94c13c605a46988689d320e2a777ef73a54b1626933f6bcd9",
    }),
    "LEARNED-PATCH-GROUPS-20261122-001": ("groups", {
        "train.jsonl": "de105f38fbd599d53ae8a69993dc8ad712b80c844be13054805553ba52946d34",
        "queries.jsonl": "db76bc20bec41935e65c51ccfc02e00db4b608f5170e3ce463d8a94f8f9bbd70",
    }),
    VARIED: ("drawings", {
        "train_narrow.jsonl": "de105f38fbd599d53ae8a69993dc8ad712b80c844be13054805553ba52946d34",
        "train_varied.jsonl": "93e18b6c560952fe54aa1aa240c7db9b9deb25710d5cfadaf5c69ee40daa1be1",
        "queries.jsonl": "5bbf9a27867f9bb479a02b2e069758c4da2c4839576fffd26953c0c5caa1bc58",
    }),
}
VARIED_KEYS = {
    "training_key_varied.jsonl": "5a09eae8dd63aa8a24c27a2a750a0998c6a2aa55df7be65ddd9062a0b85a9dba",
    "scorer_key.jsonl": "d0328fcf97df0e39c584002ee8331307f3bbbc8d69bec22b8d861876dca543a7",
}
DIAGNOSTIC = (
    ("L", 3, "F-blind-2", "01700eb7fdd499a0e99d7c194ba9f63f89d71562ed5b72ad498ad3923c329652"),
    ("T", 2, "F-blind-1", "8a9f6e8f4d9c94429d9d49cef4a1949bd206bb1b0c3603c78c675209e6e3d53f"),
)

Point = tuple[int, int]
Support = tuple[Point, ...]


@dataclass(frozen=True)
class Drawing:
    stem: Support
    bar: Support
    junction: Point

    @property
    def cells(self) -> set[Point]:
        return set(self.stem) | set(self.bar)


@dataclass(frozen=True)
class Design:
    base: str
    stem_col: int
    bar_steps: tuple[int, ...]
    stem_steps: tuple[int, ...]
    bend: str
    drawings: dict[str, Drawing]
    orbits: tuple[Support, ...]


def normalize(points: Iterable[Point]) -> Support:
    cells = tuple(points)
    top = min(row for row, _ in cells)
    left = min(col for _, col in cells)
    return tuple(sorted((row - top, col - left) for row, col in cells))


def turns(points: Iterable[Point]) -> tuple[Support, ...]:
    support = normalize(points)
    return (
        support,
        normalize((col, -row) for row, col in support),
        normalize((-row, -col) for row, col in support),
        normalize((-col, row) for row, col in support),
    )


def dihedral(points: Iterable[Point]) -> Support:
    rotations = turns(points)
    reflections = tuple(normalize((row, -col) for row, col in support) for support in rotations)
    return min(rotations + reflections)


def bitmap_support(pixels: str) -> Support:
    return tuple(divmod(index, BITMAP_SIZE) for index, pixel in enumerate(pixels) if pixel == "1")


def bitmap(points: Iterable[Point], row: int, col: int, q: int) -> str:
    pixels = ["0"] * BITMAP_SIZE**2
    for r, c in turns(points)[q]:
        if row + r >= BITMAP_SIZE or col + c >= BITMAP_SIZE:
            raise ValueError(f"Glyph placement exceeds the bitmap at {(row, col)} and turn {q}")
        pixels[(row + r) * BITMAP_SIZE + col + c] = "1"
    return "".join(pixels)


def make_drawing(
    width: int, height: int, stem_col: int, label: str, bar_steps: tuple[int, ...], stem_steps: tuple[int, ...]
) -> Drawing | None:
    bar = tuple((r, c) for c, r in enumerate(accumulate(bar_steps, initial=0)))
    offsets = tuple(accumulate(stem_steps, initial=0))
    if label == "L":
        junction = bar[0]
        stem_top = junction[0] - height + 1
        stem_left = junction[1] - offsets[-1]
    else:
        junction = bar[stem_col]
        stem_top, stem_left = junction
    stem = tuple((stem_top + r, stem_left + c) for r, c in enumerate(offsets))
    if (set(stem) & set(bar)) != {junction}:
        return None
    if label == "T" and not bar[0][1] < stem[1][1] < bar[-1][1]:
        return None

    cells = normalize(set(stem) | set(bar))
    if len(cells) != width + height - 1:
        return None
    if (max(c for _, c in cells) + 1, max(r for r, _ in cells) + 1) != (width, height):
        return None
    if len(set(turns(cells))) != 4:
        return None
    top = min(r for r, _ in stem + bar)
    left = min(c for _, c in stem + bar)
    return Drawing(
        tuple((r - top, c - left) for r, c in stem),
        tuple((r - top, c - left) for r, c in bar),
        (junction[0] - top, junction[1] - left),
    )


def geometry_order(value: object) -> str:
    descriptor = json.dumps(value, separators=(",", ":"))
    return sha256((DESIGN_SALT + descriptor).encode("ascii")).hexdigest()


def catalogue(base: str, stem_col: int, excluded: set[Support]) -> dict[str, dict[tuple[Support, ...], Design]]:
    width, height = DIMENSIONS[base]
    if not 0 < stem_col < width - 1:
        raise ValueError(f"T junction must be strictly interior for {base}")
    steps = sorted(
        product(product((-1, 0, 1), repeat=width - 1), product((-1, 0, 1), repeat=height - 1)),
        key=lambda profile: (geometry_order((base, stem_col, *profile)), profile),
    )
    pools: dict[str, dict[tuple[Support, ...], Design]] = defaultdict(dict)
    for bar_steps, stem_steps in steps:
        bends = (any(bar_steps), any(stem_steps))
        if not any(bends):
            continue
        bend = {(True, False): "horizontal", (False, True): "vertical", (True, True): "compound"}[bends]
        l_drawing = make_drawing(width, height, stem_col, "L", bar_steps, stem_steps)
        t_drawing = make_drawing(width, height, stem_col, "T", bar_steps, stem_steps)
        if l_drawing is None or t_drawing is None:
            continue
        orbits = dihedral(l_drawing.cells), dihedral(t_drawing.cells)
        if orbits[0] == orbits[1] or excluded.intersection(orbits):
            continue
        pools[bend].setdefault(
            orbits, Design(base, stem_col, bar_steps, stem_steps, bend, {"L": l_drawing, "T": t_drawing}, orbits)
        )
    return dict(pools)


def choose_designs(old_orbits: set[Support]) -> tuple[dict[str, Design], dict[str, dict[str, int]]]:
    slots = []
    pools = {}
    counts = {}
    for base, quotas in QUOTAS.items():
        for col in sorted({col for col, _ in quotas}):
            allowed = catalogue(base, col, old_orbits)
            counts[f"{base}:{col}"] = {bend: len(allowed.get(bend, {})) for bend in ("vertical", "horizontal", "compound")}
            pools[base, col] = allowed
        slots.extend((f"{base}-relative-{number}", base, col, bend)
                     for number, (col, bend) in enumerate(quotas, 1))

    def assign(index: int, occupied: set[Support]) -> list[tuple[str, Design]] | None:
        if index == len(slots):
            return []
        style, base, col, bend = slots[index]
        for design in pools[base, col].get(bend, {}).values():
            if occupied.intersection(design.orbits):
                continue
            rest = assign(index + 1, occupied.union(design.orbits))
            if rest is not None:
                return [(style, design), *rest]
        return None

    selection = assign(0, set())
    if selection is None:
        raise ValueError("The fixed shape quotas have no disjoint assignment")
    return dict(selection), counts


def checked_bytes(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Predecessor hash mismatch for {path}")
    return data


def parse(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.splitlines()]


def previous_panel(ticket: str, slug: str) -> Path:
    return FAMILY.parents[1] / ticket / f"{ticket}-E001_{slug}" / "panel"


def prior_data() -> tuple[dict[str, bytes], set[str], dict[str, object]]:
    inputs = {}
    old_bitmaps = set()
    provenance = {}
    for ticket, (slug, hashes) in PREDECESSORS.items():
        path = previous_panel(ticket, slug)
        data = {name: checked_bytes(path / name, digest) for name, digest in hashes.items()}
        bitmaps = {row["pixels"] for content in data.values() for row in parse(content)}
        old_bitmaps.update(bitmaps)
        provenance[ticket] = {"unique_bitmaps": len(bitmaps), "file_sha256": hashes}
        if ticket == VARIED:
            inputs = data | {name: checked_bytes(path / name, digest) for name, digest in VARIED_KEYS.items()}
    return inputs, old_bitmaps, provenance


def diagnostic_records(data: bytes) -> bytes:
    wanted = {row[3] for row in DIAGNOSTIC}
    indexed = {}
    for line in data.splitlines(keepends=True):
        row = json.loads(line)
        if row["id"] in wanted:
            indexed[row["id"]] = line
    if set(indexed) != wanted:
        raise ValueError("The public diagnostic records are absent from the predecessor")
    return b"".join(indexed[row[3]] for row in DIAGNOSTIC)


def condition(row: int, col: int, q: int) -> str:
    held_anchor = (row + col) % 2 == 0
    if held_anchor:
        return "position" if q in FIT_TURNS else "combined"
    return "familiar" if q in FIT_TURNS else "orientation"


def query_rows(designs: Mapping[str, Design]) -> tuple[list[dict[str, str]], list[dict[str, str | int]]]:
    public = []
    keys = []
    for (style, design), label, (row, col), q in product(designs.items(), LABELS, ANCHORS, range(4)):
        pixels = bitmap(design.drawings[label].cells, row, col, q)
        example_id = sha256(pixels.encode("ascii")).hexdigest()
        public.append({"id": example_id, "pixels": pixels})
        keys.append({
            "id": example_id, "label": label, "condition": condition(row, col, q), "style": style,
            "base_style": design.base, "style_stratum": "blind", "row": row, "col": col, "q": q,
        })
    public.sort(key=lambda row: (sha256((QUERY_SALT + row["pixels"]).encode("ascii")).hexdigest(), row["id"]))
    keys.sort(key=lambda row: row["id"])
    return public, keys


def json_lines(rows: Iterable[Mapping[str, str | int]]) -> bytes:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")


def audit_panel(files: dict[str, bytes], old_bitmaps: set[str], old_orbits: set[Support]) -> dict[str, object]:
    train = parse(files["train.jsonl"])
    train_keys = parse(files["training_key.jsonl"])
    diagnostic = parse(files["diagnostic.jsonl"])
    diagnostic_keys = parse(files["diagnostic_key.jsonl"])
    queries = parse(files["queries.jsonl"])
    query_keys = parse(files["scorer_key.jsonl"])
    if (len(train), len(train_keys), len(diagnostic), len(diagnostic_keys), len(queries), len(query_keys)) != (64, 64, 2, 2, 1024, 1024):
        raise ValueError("Unexpected view or key row counts")
    if [key["slot"] for key in train_keys] != list(range(64)):
        raise ValueError("Training key must retain all predecessor presentation slots in order")
    if Counter((key["label"], key["q"]) for key in train_keys) != {(label, q): 16 for label, q in product(LABELS, FIT_TURNS)}:
        raise ValueError("Training labels and familiar turns must have equal counts")

    for view, keys in ((train, train_keys), (diagnostic, diagnostic_keys), (queries, query_keys)):
        view_ids = {row["id"] for row in view}
        if len(view_ids) != len(view) or view_ids != {key["id"] for key in keys}:
            raise ValueError("Views require a unique exact key join")
        if not all(set(row) == {"id", "pixels"} for row in view):
            raise ValueError("Public data must contain only IDs and bitmaps")
        for row in view:
            pixels = row["pixels"]
            if len(pixels) != BITMAP_SIZE**2 or set(pixels) != {"0", "1"}:
                raise ValueError("A public bitmap has an invalid raster")
            if sha256(pixels.encode("ascii")).hexdigest() != row["id"]:
                raise ValueError("A public bitmap has the wrong ID")
    if [row["id"] for row in train] != [key["id"] for key in train_keys]:
        raise ValueError("Training keys must use predecessor presentation order")

    for key, (label, q, style, example_id) in zip(diagnostic_keys, DIAGNOSTIC, strict=True):
        if (key["label"], key["q"], key["style"], key["id"], key["row"], key["col"]) != (label, q, style, example_id, 1, 1):
            raise ValueError("Diagnostic key is not the original drawing at anchor (1,1)")

    train_pixels = {row["pixels"] for row in train}
    diagnostic_pixels = {row["pixels"] for row in diagnostic}
    query_pixels = {row["pixels"] for row in queries}
    if (len(train_pixels), len(diagnostic_pixels), len(query_pixels)) != (64, 2, 1024):
        raise ValueError("Within-file bitmaps must be unique")
    if train_pixels & diagnostic_pixels or query_pixels & (old_bitmaps | train_pixels | diagnostic_pixels):
        raise ValueError("Training, diagnostic and fresh blind files have unexpected bitmap overlap")
    if not (train_pixels | diagnostic_pixels) <= old_bitmaps:
        raise ValueError("Training and diagnostic views must come from the earlier panels")
    fit_dimensions = set()
    for image in train:
        rows, cols = zip(*bitmap_support(image["pixels"]))
        fit_dimensions.add(tuple(sorted((max(rows) - min(rows) + 1, max(cols) - min(cols) + 1))))
    if fit_dimensions.intersection(tuple(sorted(box)) for box in DIMENSIONS.values()):
        raise ValueError("Blind bounding dimensions occur in training")
    fresh_orbits = {dihedral(bitmap_support(pixels)) for pixels in query_pixels}
    if len(fresh_orbits) != 16 or fresh_orbits & old_orbits or len(old_orbits) != 54 or len(old_bitmaps) != 2240:
        raise ValueError("Wrong shape counts or orbit overlap with earlier panels")

    keyed = {row["id"]: row for row in queries}
    cells = Counter()
    for key in query_keys:
        pixels = keyed[key["id"]]["pixels"]
        points = bitmap_support(pixels)
        row, col = key["row"], key["col"]
        width, height = DIMENSIONS[key["base_style"]]
        if key["q"] % 2:
            width, height = height, width
        if (min(r for r, _ in points), min(c for _, c in points)) != (row, col):
            raise ValueError("Blind image has the wrong bounding-box origin")
        if (max(r for r, _ in points), max(c for _, c in points)) != (row + height - 1, col + width - 1):
            raise ValueError("Blind image has the wrong box dimensions")
        if len(points) != width + height - 1:
            raise ValueError("Blind image has the wrong ink count")
        if key["condition"] != condition(row, col, key["q"]):
            raise ValueError("Blind image has the wrong condition")
        cells[key["style"], key["label"], key["q"], (row + col) % 2] += 1
    if len(cells) != 128 or set(cells.values()) != {8}:
        raise ValueError("Every style, class, turn and position stratum needs eight distinct translations")
    ink_counts = Counter(pixels.count("1") for pixels in query_pixels)
    if ink_counts != {6: 512, 7: 512}:
        raise ValueError("Fresh blind ink counts must be balanced")
    return {
        "training_bitmaps": len(train_pixels), "diagnostic_bitmaps": len(diagnostic_pixels),
        "blind_bitmaps": len(query_pixels), "blind_d4_orbits": len(fresh_orbits),
        "earlier_bitmaps": len(old_bitmaps), "earlier_d4_orbits": len(old_orbits),
        "blind_bitmap_overlap": 0, "blind_d4_overlap": 0, "translations_per_style_label_turn_position_stratum": 8,
        "blind_ink_counts": dict(ink_counts),
    }


def build_panel() -> dict[str, bytes]:
    """Return the immutable panel contents without writing them."""
    prior, old_bitmaps, provenance = prior_data()
    old_orbits = {dihedral(bitmap_support(pixels)) for pixels in old_bitmaps}
    designs, counts = choose_designs(old_orbits)
    queries, keys = query_rows(designs)
    files = {
        "train.jsonl": prior["train_varied.jsonl"],
        "training_key.jsonl": prior["training_key_varied.jsonl"],
        "queries.jsonl": json_lines(queries),
        "scorer_key.jsonl": json_lines(keys),
        "diagnostic.jsonl": diagnostic_records(prior["queries.jsonl"]),
        "diagnostic_key.jsonl": diagnostic_records(prior["scorer_key.jsonl"]),
    }
    audit = audit_panel(files, old_bitmaps, old_orbits)
    by_condition = Counter((key["condition"], key["label"]) for key in keys)
    manifest = {
        "schema_version": 1,
        "generator": {"path": "../panel.py", "sha256": sha256(Path(__file__).read_bytes()).hexdigest()},
        "bitmap": {"width": 8, "height": 8, "encoding": "row-major ASCII bits", "lit_pixels": [6, 7]},
        "id": "Lowercase hexadecimal SHA-256 of the ASCII bit string",
        "anchor": {
            "definition": "Zero-based top-left position of the normalized rotated bounding box",
            "row_col_indices": list(range(4)), "held_rule": "(row + col) % 2 == 0",
        },
        "turns": {"definition": "q clockwise quarter-turns before translation", "fit_q": [0, 1], "held_q": [2, 3]},
        "conditions": {
            "familiar": "Familiar position and turn", "position": "Held position and familiar turn",
            "orientation": "Familiar position and held turn", "combined": "Held position and turn",
        },
        "ancestry": {
            "E": "Prior held 5-by-2 dimensions with three interior stem columns",
            "F": "Prior held 4-by-4 dimensions with the mirror of the earlier stem offset",
            "training": "Exact previous varied stream and training key, in their original presentation order",
            "diagnostic": "Exact previous public query and key records at (1,1), ordered L at q3 then T at q2",
        },
        "geometry": {
            "candidates": (
                "With fixed width and height, a bar advances one column at each step and a stem advances one row. "
                "Each step adds a perpendicular displacement chosen from -1, 0, +1. Paired L and T use identical step lists."
            ),
            "junctions": (
                "L attaches the last stem point to the first bar point. T attaches the first stem point to the "
                "specified interior bar point. The paths meet in exactly that point. T's next stem column "
                "remains strictly between the two ends of its bar."
            ),
            "connectivity": (
                "A nonzero perpendicular step is diagonal and uses eight-neighbor continuity. The intended "
                "attachments are defined by ordered paths and their shared pixel. Nearby pixels on those paths "
                "can supply additional neighbor pairs in the full bitmap."
            ),
            "gates": (
                "Match exact ink and bounding-box dimensions, require four different normalized turns per drawing, "
                "and exclude earlier and selected drawing identities under all translations, rotations and reflections."
            ),
            "geometry_limits": (
                "The wider common-shear probe at the earlier centered 5-by-2 base left one admissible fresh pair. "
                "Shared ordered stroke steps and three interior stem positions allow four six-ink horizontal-bend pairs."
            ),
            "quota_slots_by_base": QUOTAS,
            "admissible_pair_counts_by_base_and_stem": counts,
            "design_order_salt": DESIGN_SALT,
            "selection": (
                "Rank candidates by SHA-256 of the ASCII salt concatenated with compact JSON "
                "[base, T stem column, bar steps, stem steps], breaking ties lexicographically by step lists. "
                "Within each base, stem column and bend keep the first representative of each ordered pair of "
                "D4 shape orbits. In E then F quota order, take the first complete assignment with disjoint orbits."
            ),
        },
        "designs": {
            name: {
                "base_style": design.base, "width_height": DIMENSIONS[design.base], "T_stem_col": design.stem_col,
                "bend": design.bend, "bar_steps": design.bar_steps, "stem_steps": design.stem_steps,
                "diagonal_bar_steps": sum(bool(step) for step in design.bar_steps),
                "diagonal_stem_steps": sum(bool(step) for step in design.stem_steps),
                "normalized_upright_paths": {
                    label: {"stem": drawing.stem, "bar": drawing.bar, "junction": drawing.junction}
                    for label, drawing in design.drawings.items()
                },
            }
            for name, design in designs.items()
        },
        "ordering": {
            "query_salt": QUERY_SALT,
            "queries": "Ascending SHA-256 of ASCII (salt + bit string), then id for ties",
            "scorer_key": "Ascending id",
            "diagnostic_keys": "Original predecessor records, retaining their original condition and style stratum",
        },
        "predecessors": provenance,
        "predecessor_key_hashes": VARIED_KEYS,
        "blind_counts": {name: {label: by_condition[name, label] for label in LABELS}
                         for name in ("familiar", "position", "orientation", "combined")},
        "audit": audit,
        "files": {name: {"rows": len(data.splitlines()), "sha256": sha256(data).hexdigest()} for name, data in files.items()},
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("ascii")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=FAMILY / "panel")
    parser.add_argument("--check", action="store_true", help="Verify existing files against a fresh build")
    args = parser.parse_args()
    files = build_panel()
    if args.check or args.output.exists():
        mismatches = [name for name, data in files.items()
                      if not (args.output / name).is_file() or (args.output / name).read_bytes() != data]
        if mismatches:
            raise SystemExit(f"Panel files missing or different in {args.output}: {', '.join(mismatches)}")
        print(f"Verified {args.output}")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=f".{args.output.name}-", dir=args.output.parent) as directory:
        staged = Path(directory) / args.output.name
        staged.mkdir()
        for name, data in files.items():
            (staged / name).write_bytes(data)
        staged.rename(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
