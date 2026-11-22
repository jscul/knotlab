"""Build and replay matched narrow and varied training panels and one blind panel."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from tempfile import TemporaryDirectory


FAMILY = Path(__file__).resolve().parent
BITMAP_SIZE = 8
ANCHORS = tuple(product(range(4), repeat=2))
FAMILIAR_TURNS = (0, 1)
LABELS = ("L", "T")
FIT_BASES = {"A": (3, 4, 1), "B": (4, 3, 2), "C": (3, 5, 1), "D": (5, 3, 2)}
BLIND_BASES = {"E": (5, 2, 2), "F": (4, 4, 1)}
BASES = FIT_BASES | BLIND_BASES
BENDS = ("vertical", "horizontal", "compound")
QUOTAS = {
    "A": ("vertical", "horizontal", "compound"),
    "B": ("horizontal", "compound", "compound"),
    "C": ("vertical", "horizontal", "compound"),
    "D": ("vertical", "horizontal", "compound"),
    "E": ("horizontal", "horizontal", "horizontal", "compound"),
    "F": ("vertical", "horizontal", "compound", "compound"),
}
DESIGN_SALT = "varied-letter-drawings-20261122-v1-design:"
ANCHOR_SALT = "varied-letter-drawings-20261122-v1-anchor:"
QUERY_SALT = "varied-letter-drawings-20261122-v1-query:"
PREDECESSORS = {
    "PIXEL-LETTERS-20261122-001": (
        "letters", 400,
        "68ee66a52191de03bcdf4782c3d99a77aa8094417b1c69a4abc5cd6b123ffe65",
        "52594f1b1ffcbbb94c13c605a46988689d320e2a777ef73a54b1626933f6bcd9",
    ),
    "LEARNED-PATCH-GROUPS-20261122-001": (
        "groups", 768,
        "de105f38fbd599d53ae8a69993dc8ad712b80c844be13054805553ba52946d34",
        "db76bc20bec41935e65c51ccfc02e00db4b608f5170e3ce463d8a94f8f9bbd70",
    ),
}
NARROW_SOURCE = "LEARNED-PATCH-GROUPS-20261122-001"

Point = tuple[int, int]
Support = tuple[Point, ...]
Move = tuple[str, int, int, int]


@dataclass(frozen=True)
class Drawing:
    vertical: Support
    bar: Support
    junction: Point

    @property
    def cells(self) -> set[Point]:
        return set(self.vertical) | set(self.bar)


@dataclass(frozen=True)
class Design:
    base: str
    moves: tuple[Move, ...]
    bend: str
    drawings: dict[str, Drawing]
    orbits: tuple[Support, ...]


@dataclass(frozen=True)
class Example:
    pixels: str
    label: str
    condition: str
    style: str
    base_style: str
    style_stratum: str
    row: int
    col: int
    q: int

    @property
    def id(self) -> str:
        return sha256(self.pixels.encode("ascii")).hexdigest()

    def view(self) -> dict[str, str]:
        return {"id": self.id, "pixels": self.pixels}

    def key(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "label": self.label,
            "condition": self.condition,
            "style": self.style,
            "base_style": self.base_style,
            "style_stratum": self.style_stratum,
            "row": self.row,
            "col": self.col,
            "q": self.q,
        }


def top_left(cells: Support | set[Point]) -> Point:
    return min(row for row, _ in cells), min(col for _, col in cells)


def normalize(cells: Iterable[Point]) -> Support:
    points = tuple(cells)
    top, left = top_left(points)
    return tuple(sorted((row - top, col - left) for row, col in points))


def rotate(support: Support) -> Support:
    return normalize((col, -row) for row, col in support)


def normalized_turns(cells: Iterable[Point]) -> list[Support]:
    turns = [normalize(cells)]
    for _ in range(3):
        turns.append(rotate(turns[-1]))
    return turns


def normalize_dihedral(cells: Iterable[Point]) -> Support:
    turns = normalized_turns(cells)
    reflections = [normalize((row, -col) for row, col in support) for support in turns]
    return min(turns + reflections)


def bitmap_support(pixels: str) -> Support:
    return tuple(divmod(index, BITMAP_SIZE) for index, value in enumerate(pixels) if value == "1")


def bitmap(support: Iterable[Point], top: int, left: int, q: int) -> str:
    turned = normalize(support)
    for _ in range(q):
        turned = rotate(turned)
    bits = ["0"] * BITMAP_SIZE**2
    for row, col in turned:
        if top + row >= BITMAP_SIZE or left + col >= BITMAP_SIZE:
            raise ValueError(f"Glyph exceeds the bitmap at {(top, left)} and turn {q}")
        bits[(top + row) * BITMAP_SIZE + left + col] = "1"
    return "".join(bits)


def displace(path: Support, moves: tuple[Move, ...]) -> Support:
    for axis, start, stop, amount in moves:
        if axis == "row":
            path = tuple((row, col + amount) if start <= row < stop else (row, col) for row, col in path)
        else:
            path = tuple((row + amount, col) if start <= col < stop else (row, col) for row, col in path)
    return path


def continuous(path: Support, main_axis: int) -> bool:
    return all(
        end[main_axis] - start[main_axis] == 1 and abs(end[1 - main_axis] - start[1 - main_axis]) <= 1
        for start, end in zip(path, path[1:])
    )


def make_drawing(base: tuple[int, int, int], label: str, moves: tuple[Move, ...]) -> Drawing | None:
    width, height, stem_col = base
    bar_row = height - 1 if label == "L" else 0
    stem_col = 0 if label == "L" else stem_col
    vertical = displace(tuple((row, stem_col) for row in range(height)), moves)
    bar = displace(tuple((bar_row, col) for col in range(width)), moves)
    junction = vertical[-1] if label == "L" else vertical[0]
    cells = set(vertical) | set(bar)
    if not continuous(vertical, 0) or not continuous(bar, 1):
        return None
    if junction != bar[stem_col] or (set(vertical) & set(bar)) != {junction}:
        return None
    if label == "T" and not bar[0][1] < vertical[1][1] < bar[-1][1]:
        return None

    top, left = top_left(cells)
    if (
        len(cells) != width + height - 1
        or max(row for row, _ in cells) - top + 1 != height
        or max(col for _, col in cells) - left + 1 != width
    ):
        return None
    return Drawing(
        tuple((row - top, col - left) for row, col in vertical),
        tuple((row - top, col - left) for row, col in bar),
        (junction[0] - top, junction[1] - left),
    )


def bend_type(drawing: Drawing) -> str:
    vertical_bends = len({col for _, col in drawing.vertical}) > 1
    bar_bends = len({row for row, _ in drawing.bar}) > 1
    return {
        (False, False): "straight",
        (True, False): "vertical",
        (False, True): "horizontal",
        (True, True): "compound",
    }[vertical_bends, bar_bends]


def make_design(base: str, moves: tuple[Move, ...]) -> Design | None:
    drawings = {}
    for label in LABELS:
        drawing = make_drawing(BASES[base], label, moves)
        if drawing is None or len(set(normalized_turns(drawing.cells))) != 4:
            return None
        drawings[label] = drawing
    bends = {bend_type(drawing) for drawing in drawings.values()}
    orbits = tuple(normalize_dihedral(drawing.cells) for drawing in drawings.values())
    if len(bends) != 1 or len(set(orbits)) != len(LABELS):
        return None
    return Design(base, moves, bends.pop(), drawings, orbits)


def move_options(axis: str, size: int) -> tuple[Move, ...]:
    return tuple(
        (axis, start, stop, sign)
        for start in range(size)
        for stop in range(start + 1, size + 1)
        if stop - start < size
        for sign in (-1, 1)
    )


def possible_moves(base: str) -> Iterable[tuple[Move, ...]]:
    width, height, _ = BASES[base]
    rows = move_options("row", height)
    columns = move_options("col", width)
    yield from ((step,) for step in rows + columns)
    yield from product(rows, columns)
    yield from product(columns, rows)


def compact_json(value: object) -> str:
    return json.dumps(value, separators=(",", ":"))


def order_hash(salt: str, value: str) -> str:
    return sha256((salt + value).encode("ascii")).hexdigest()


def choose_designs(
    bases: Mapping[str, tuple[int, int, int]], stratum: str, forbidden: set[Support]
) -> tuple[dict[str, Design], dict[str, dict[str, int]]]:
    catalogue = {}
    slots_by_dimensions = defaultdict(list)
    for base, (width, height, _) in bases.items():
        distinct = {bend: {} for bend in BENDS}
        moves = sorted(
            possible_moves(base), key=lambda moves: (order_hash(DESIGN_SALT, compact_json((base, moves))), moves)
        )
        for steps in moves:
            design = make_design(base, steps)
            if design is None or design.bend == "straight" or forbidden.intersection(design.orbits):
                continue
            distinct[design.bend].setdefault(design.orbits, design)
        catalogue[base] = distinct
        slots_by_dimensions[tuple(sorted((width, height)))].extend(
            (f"{base}-{stratum}-{index}", base, bend) for index, bend in enumerate(QUOTAS[base], 1)
        )

    def assign(
        slots: list[tuple[str, str, str]], index: int, occupied: set[Support]
    ) -> list[tuple[str, Design]] | None:
        if index == len(slots):
            return []
        name, base, bend = slots[index]
        for design in catalogue[base][bend].values():
            if occupied.intersection(design.orbits):
                continue
            rest = assign(slots, index + 1, occupied.union(design.orbits))
            if rest is not None:
                return [(name, design), *rest]
        return None

    # A reflection or quarter-turn preserves the unordered bounding dimensions.
    selection = {}
    for dimensions, slots in slots_by_dimensions.items():
        block = assign(slots, 0, set())
        if block is None:
            raise ValueError(f"No disjoint assignment for {stratum} geometric quotas at dimensions {dimensions}")
        selection.update(block)
    counts = {base: {bend: len(pool) for bend, pool in pools.items()} for base, pools in catalogue.items()}
    return selection, counts


def load_predecessors() -> tuple[bytes, set[str], dict[str, object]]:
    narrow_source = b""
    bitmaps = set()
    provenance = {}
    for ticket, (slug, count, train_hash, query_hash) in PREDECESSORS.items():
        panel = FAMILY.parents[1] / ticket / f"{ticket}-E001_{slug}" / "panel"
        panel_bitmaps = set()
        files = {"train.jsonl": train_hash, "queries.jsonl": query_hash}
        for name, expected in files.items():
            data = (panel / name).read_bytes()
            if sha256(data).hexdigest() != expected:
                raise ValueError(f"Predecessor hash mismatch for {panel / name}")
            panel_bitmaps.update(json.loads(line)["pixels"] for line in data.splitlines())
            if ticket == NARROW_SOURCE and name == "train.jsonl":
                narrow_source = data
        if len(panel_bitmaps) != count or bitmaps & panel_bitmaps:
            raise ValueError(f"Unexpected predecessor bitmap count or overlap for {ticket}")
        bitmaps.update(panel_bitmaps)
        provenance[ticket] = {"bitmaps": len(panel_bitmaps), "file_sha256": files}
    return narrow_source, bitmaps, provenance


def held_anchor(row: int, col: int) -> bool:
    return (row + col) % 2 == 0


def query_condition(row: int, col: int, q: int) -> str:
    if held_anchor(row, col):
        return "position" if q in FAMILIAR_TURNS else "combined"
    return "familiar" if q in FAMILIAR_TURNS else "orientation"


def example(design: Design, style: str, label: str, row: int, col: int, q: int, stratum: str) -> Example:
    condition = query_condition(row, col, q) if stratum == "blind" else "train"
    pixels = bitmap(design.drawings[label].cells, row, col, q)
    return Example(pixels, label, condition, style, design.base, stratum, row, col, q)


def make_training(
    narrow_source: bytes, straight: dict[str, Design], selected: dict[str, Design]
) -> tuple[list[Example], list[Example]]:
    by_id = {}
    anchors = defaultdict(list)
    for (row, col), q in product(ANCHORS, FAMILIAR_TURNS):
        if held_anchor(row, col):
            continue
        for base in ("AB"[(row + q) % 2], "CD"[(row // 2 + q) % 2]):
            anchors[base, q].append((row, col))
            for label in LABELS:
                prior = example(straight[base], base, label, row, col, q, "straight")
                by_id[prior.id] = prior
    narrow = [by_id[json.loads(line)["id"]] for line in narrow_source.splitlines()]
    variant_lookup = {}
    for (base, q), poses in anchors.items():
        styles = [base, *(name for name, design in selected.items() if design.base == base)]
        ordered = sorted(
            poses, key=lambda pose: (order_hash(ANCHOR_SALT, compact_json((base, q, *pose))), pose)
        )
        for (row, col), style in zip(ordered, styles, strict=True):
            variant_lookup[base, q, row, col] = style

    varied = []
    for prior in narrow:
        base, q, row, col = prior.base_style, prior.q, prior.row, prior.col
        style = variant_lookup[base, q, row, col]
        if style == base:
            varied.append(prior)
        else:
            varied.append(example(selected[style], style, prior.label, row, col, q, "varied"))
    return narrow, varied


def make_queries(selected: dict[str, Design]) -> list[Example]:
    queries = [
        example(design, style, label, row, col, q, "blind")
        for (style, design), (row, col), q, label in product(selected.items(), ANCHORS, range(4), LABELS)
    ]
    return sorted(queries, key=lambda row: (order_hash(QUERY_SALT, row.pixels), row.id))


def json_lines(rows: Iterable[Mapping[str, str | int]]) -> bytes:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")


def audit_panel(
    narrow: list[Example], varied: list[Example], queries: list[Example], old_bitmaps: set[str], old_orbits: set[Support]
) -> dict[str, object]:
    narrow_bits, varied_bits, query_bits = ({row.pixels for row in rows} for rows in (narrow, varied, queries))
    if (len(narrow_bits), len(varied_bits), len(query_bits)) != (64, 64, 1024):
        raise ValueError("Unexpected unique bitmap count")
    if (len(narrow), len(varied), len(queries)) != (64, 64, 1024):
        raise ValueError("Unexpected number of rows")
    if len(narrow_bits & varied_bits) != 16 or sum(a.pixels == b.pixels for a, b in zip(narrow, varied)) != 16:
        raise ValueError("Expected 16 shared bitmaps in exactly the same slots")
    if not narrow_bits <= old_bitmaps or len(varied_bits & old_bitmaps) != 16:
        raise ValueError("Only the specified old drawings should be reused")
    if query_bits & (old_bitmaps | narrow_bits | varied_bits):
        raise ValueError("A blind bitmap occurs in an earlier panel or in training")

    for a, b in zip(narrow, varied, strict=True):
        if (a.base_style, a.label, a.q, a.row, a.col) != (b.base_style, b.label, b.q, b.row, b.col):
            raise ValueError(f"Training slots are unmatched for {a.id} and {b.id}")
        if a.pixels.count("1") != b.pixels.count("1"):
            raise ValueError(f"Training slot ink is unmatched for {a.id} and {b.id}")
    signatures = {
        name: {normalize_dihedral(bitmap_support(row.pixels)) for row in rows}
        for name, rows in (("narrow", narrow), ("varied", varied), ("blind", queries))
    }
    if {name: len(orbits) for name, orbits in signatures.items()} != {"narrow": 6, "varied": 30, "blind": 16}:
        raise ValueError("Unexpected number of drawing orbits")
    if (signatures["varied"] & old_orbits) != signatures["narrow"]:
        raise ValueError("Only straight training styles may reuse earlier drawing orbits")
    if signatures["blind"] & (old_orbits | signatures["varied"]):
        raise ValueError("Blind drawing orbits must be fresh relative to both earlier panels and training")

    for rows in (narrow, varied, queries):
        for row in rows:
            points = bitmap_support(row.pixels)
            width, height, _ = BASES[row.base_style]
            if row.q % 2:
                width, height = height, width
            top, left = top_left(points)
            if (top, left) != (row.row, row.col) or len(points) != width + height - 1:
                raise ValueError(f"Wrong anchor or ink in {row.id}")
            if (max(r for r, _ in points) - top + 1, max(c for _, c in points) - left + 1) != (height, width):
                raise ValueError(f"Wrong bounding box in {row.id}")

    for rows, designs, count in ((narrow, 4, 4), (varied, 16, 1)):
        replication = Counter((row.style, row.q, row.label) for row in rows)
        if len(replication) != designs * 4 or set(replication.values()) != {count}:
            raise ValueError("Each training design must replicate equally across labels and familiar turns")
        if any(row.q not in FAMILIAR_TURNS or held_anchor(row.row, row.col) for row in rows):
            raise ValueError("Held-out training turn or anchor")
    blind_replication = Counter((row.style, row.q, row.label, held_anchor(row.row, row.col)) for row in queries)
    if len(blind_replication) != 128 or set(blind_replication.values()) != {8}:
        raise ValueError("Each blind design must have eight translations per label, turn and position stratum")
    return {
        "bitmap_counts": {"narrow": len(narrow_bits), "varied": len(varied_bits), "blind": len(query_bits),
                          "union": len(narrow_bits | varied_bits | query_bits)},
        "straight_bitmaps_shared_in_same_training_slots": 16,
        "dihedral_orbit_counts": {name: len(orbits) for name, orbits in signatures.items()},
        "previous_unique_bitmaps": len(old_bitmaps),
        "previous_dihedral_orbit_count": len(old_orbits),
        "blind_bitmap_overlap_previous_or_training": 0,
        "blind_dihedral_overlap_previous_or_training": 0,
        "varied_bitmap_overlap_previous": len(varied_bits & old_bitmaps),
        "varied_dihedral_overlap_previous": len(signatures["varied"] & old_orbits),
    }


def build_panel() -> dict[str, bytes]:
    """Return exact artifacts without writing to disk."""
    narrow_source, old_bitmaps, provenance = load_predecessors()
    old_orbits = {normalize_dihedral(bitmap_support(pixels)) for pixels in old_bitmaps}
    straight = {}
    for base in FIT_BASES:
        design = make_design(base, ())
        if design is None:
            raise ValueError(f"Straight training design is invalid for {base}")
        straight[base] = design
    fitted_styles, fitted_counts = choose_designs(FIT_BASES, "varied", old_orbits)
    narrow, varied = make_training(narrow_source, straight, fitted_styles)
    training_orbits = set().union(*(design.orbits for design in fitted_styles.values()))
    blind_styles, blind_counts = choose_designs(BLIND_BASES, "blind", old_orbits | training_orbits)
    queries = make_queries(blind_styles)
    audit = audit_panel(narrow, varied, queries, old_bitmaps, old_orbits)
    rows_by_file = {
        "train_narrow.jsonl": [row.view() for row in narrow],
        "train_varied.jsonl": [row.view() for row in varied],
        "queries.jsonl": [row.view() for row in queries],
        "training_key_narrow.jsonl": [row.key() | {"slot": slot} for slot, row in enumerate(narrow)],
        "training_key_varied.jsonl": [row.key() | {"slot": slot} for slot, row in enumerate(varied)],
        "scorer_key.jsonl": [row.key() for row in sorted(queries, key=lambda row: row.id)],
    }
    files = {name: json_lines(rows) for name, rows in rows_by_file.items()}
    if files["train_narrow.jsonl"] != narrow_source:
        raise ValueError("Narrow training stream must match the predecessor byte for byte")
    query_counts = Counter((row.condition, row.label) for row in queries)
    manifest = {
        "schema_version": 1,
        "generator": {"path": "../panel.py", "sha256": sha256(Path(__file__).read_bytes()).hexdigest()},
        "bitmap": {"rows": 8, "cols": 8, "encoding": "row-major ASCII bits", "lit_pixels": [6, 7]},
        "id": "Lowercase hexadecimal SHA-256 of the ASCII bit string",
        "anchors": {
            "coordinates": "Zero-based top-left index of the normalized rotated bounding box",
            "indices": list(range(4)),
            "held_out_rule": "(row + col) % 2 == 0",
        },
        "rotation": {
            "definition": "q clockwise quarter-turns, normalized before translation to the anchor",
            "fit_q": FAMILIAR_TURNS,
            "held_out_q": (2, 3),
        },
        "base_dimensions_and_t_stem_col": BASES,
        "base_ancestry": {
            "fit": "A through D are the predecessor's straight training bases",
            "blind_E": "Predecessor E width, height and L skeleton, with a centered T stem",
            "blind_F": "Predecessor F width, height and skeletons",
        },
        "geometry": {
            "moves": "Each [axis,start,stop,amount] shifts the other coordinate by amount in [start,stop) measured in current coordinates",
            "candidates": "Every nonempty proper contiguous row or column interval with amount -1 or +1, singly or one of each in either order",
            "strokes": "Matched ink and dimensions, one-step progress along each stroke's main axis and cross-step at most one",
            "junctions": "The exact end intersection of L or the interior bar intersection of T survives, and T's next stem column remains strictly within the bar span",
            "bend_quota_basis": "The transformed vertical path, bar or both actually bend in both letters",
            "distinct_turns": "Require all four normalized turns of each individual drawing to be different",
            "orbit_exclusion": "All previous and selected deformed drawings under translation, quarter-turn and reflection",
            "quota_slots_by_base": QUOTAS,
            "admissible_distinct_pairs_by_base_and_bend": fitted_counts | blind_counts,
            "geometry_limits": {
                "B": "Zero admissible vertical-only pairs",
                "E": (
                    "Zero admissible vertical-only pairs. Two admissible compound pairs share a dihedral orbit "
                    "across labels, so the proposed two horizontal and two compound pairs became three "
                    "horizontal and one compound before fitting."
                ),
            },
            "selection": (
                "For each base and bend, salt-sort compact JSON [base,moves], then moves for hash ties. "
                "Keep the first representative of each ordered pair of dihedral support orbits. "
                "Fill the quotas of A through D against earlier panels and fix their training slots. "
                "Then fill E and F against earlier panels and the fixed training designs. "
                "Each pass takes the first complete disjoint assignment in base and quota order. "
                "Different unordered bounding dimensions are solved independently since their orbits cannot coincide."
            ),
            "selection_salt": DESIGN_SALT,
        },
        "style_designs": {
            name: {
                "base_style": design.base, "moves": design.moves, "bend": design.bend,
                "upright_strokes": {
                    label: {"vertical": drawing.vertical, "bar": drawing.bar, "junction": drawing.junction}
                    for label, drawing in design.drawings.items()
                },
            }
            for name, design in (straight | fitted_styles | blind_styles).items()
        },
        "ordering": {
            "narrow_training": "Exact presentation order from the predecessor training file",
            "varied_training": "Reuse narrow slots. For each base and q, order the four narrow anchors by salted compact JSON [base,q,row,col], then by anchor for ties. Assign straight then the three variants in style-number order, preserving both letters in each paired allocation.",
            "varied_anchor_salt": ANCHOR_SALT,
            "queries": "Ascending salted bitmap SHA-256, then id for ties",
            "query_salt": QUERY_SALT,
            "training_keys": "Same order as public training rows, slots 0 through 63",
            "scorer_key": "Ascending id",
        },
        "blind_conditions": {
            "familiar": "Seen anchor and familiar q",
            "position": "Held-out anchor and familiar q",
            "orientation": "Seen anchor and held-out q",
            "combined": "Held-out anchor and q",
        },
        "blind_counts": {
            condition: {label: query_counts[condition, label] for label in LABELS}
            for condition in ("familiar", "position", "orientation", "combined")
        },
        "predecessors": provenance,
        "audit": audit,
        "files": {name: {"rows": len(rows_by_file[name]), "sha256": sha256(data).hexdigest()} for name, data in files.items()},
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
        mismatches = [
            name for name, data in files.items()
            if not (args.output / name).is_file() or (args.output / name).read_bytes() != data
        ]
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
