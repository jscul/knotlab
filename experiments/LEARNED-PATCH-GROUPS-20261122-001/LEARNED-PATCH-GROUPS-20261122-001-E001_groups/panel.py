"""Build and replay the letter panel with a blind stroke-style holdout."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from tempfile import TemporaryDirectory


BITMAP_SIZE = 8
ANCHORS = tuple(product(range(4), repeat=2))
FAMILIAR_QUARTER_TURNS = (0, 1)
LABELS = ("L", "T")
QUERY_CONDITIONS = ("familiar", "position", "orientation", "combined")
TRAIN_ORDER_SALT = "learned-patch-groups-20261122-v1-train:"
QUERY_ORDER_SALT = "learned-patch-groups-20261122-v1-query:"
FAMILY = Path(__file__).resolve().parent
PREDECESSOR = (
    Path("PIXEL-LETTERS-20261122-001") / "PIXEL-LETTERS-20261122-001-E001_letters" / "panel"
)
PREDECESSOR_HASHES = {
    "train.jsonl": "68ee66a52191de03bcdf4782c3d99a77aa8094417b1c69a4abc5cd6b123ffe65",
    "queries.jsonl": "52594f1b1ffcbbb94c13c605a46988689d320e2a777ef73a54b1626933f6bcd9",
}


@dataclass(frozen=True)
class Style:
    width: int
    height: int
    stem_col: int
    stratum: str


STYLES = {
    "A": Style(3, 4, 1, "seen"),
    "B": Style(4, 3, 2, "seen"),
    "C": Style(3, 5, 1, "seen"),
    "D": Style(5, 3, 2, "seen"),
    "E": Style(5, 2, 1, "blind"),
    "F": Style(4, 4, 1, "blind"),
}


@dataclass(frozen=True)
class Example:
    id: str
    pixels: str
    label: str
    condition: str
    style: str
    row: int
    col: int
    q: int

    @property
    def style_stratum(self) -> str:
        return STYLES[self.style].stratum

    def view(self) -> dict[str, str]:
        return {"id": self.id, "pixels": self.pixels}

    def key(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "label": self.label,
            "condition": self.condition,
            "style": self.style,
            "style_stratum": self.style_stratum,
            "row": self.row,
            "col": self.col,
            "q": self.q,
        }


def held_anchor(row: int, col: int) -> bool:
    return (row + col) % 2 == 0


def condition_for(style: str, row: int, col: int, q: int) -> str:
    if held_anchor(row, col):
        return "position" if q in FAMILIAR_QUARTER_TURNS else "combined"
    if q not in FAMILIAR_QUARTER_TURNS:
        return "orientation"
    training_styles = ("AB"[(row + q) % 2], "CD"[(row // 2 + q) % 2])
    return "train" if style in training_styles else "familiar"


def upright_glyph(style: Style, label: str) -> tuple[str, ...]:
    bar = "1" * style.width
    if label == "L":
        stem = "1" + "0" * (style.width - 1)
        return (stem,) * (style.height - 1) + (bar,)
    stem = "0" * style.stem_col + "1" + "0" * (style.width - style.stem_col - 1)
    return (bar,) + (stem,) * (style.height - 1)


def bitmap(glyph: tuple[str, ...], top: int, left: int, q: int) -> str:
    for _ in range(q):
        glyph = tuple("".join(column) for column in zip(*reversed(glyph)))
    height, width = len(glyph), len(glyph[0])
    if top + height > BITMAP_SIZE or left + width > BITMAP_SIZE:
        raise ValueError(f"Glyph exceeds the bitmap at {(top, left)} and rotation {q}")
    rows = ["0" * BITMAP_SIZE] * BITMAP_SIZE
    for row, stroke in enumerate(glyph, start=top):
        rows[row] = "0" * left + stroke + "0" * (BITMAP_SIZE - left - width)
    return "".join(rows)


def make_examples() -> list[Example]:
    examples = []
    for style_name, style in STYLES.items():
        if not 0 < style.stem_col < style.width - 1:
            raise ValueError(f"Style {style_name} requires a strictly interior T stem")
        for label in LABELS:
            glyph = upright_glyph(style, label)
            for (row, col), q in product(ANCHORS, range(4)):
                pixels = bitmap(glyph, row, col, q)
                examples.append(Example(
                    id=sha256(pixels.encode("ascii")).hexdigest(),
                    pixels=pixels,
                    label=label,
                    condition=condition_for(style_name, row, col, q),
                    style=style_name,
                    row=row,
                    col=col,
                    q=q,
                ))
    return examples


Support = tuple[tuple[int, int], ...]


def normalize(positions: Iterable[tuple[int, int]]) -> Support:
    positions = tuple(positions)
    top = min(row for row, _ in positions)
    left = min(col for _, col in positions)
    return tuple(sorted((row - top, col - left) for row, col in positions))


def normalized_support(pixels: str) -> Support:
    return normalize(divmod(index, BITMAP_SIZE) for index, pixel in enumerate(pixels) if pixel == "1")


def canonical_support(support: Support) -> Support:
    turns = [support]
    for _ in range(3):
        turns.append(normalize((col, -row) for row, col in turns[-1]))
    return min(turns)


def audit_support(examples: list[Example]) -> dict:
    bitmaps = {example.pixels for example in examples}
    if len(examples) != 768 or len(bitmaps) != 768 or len({row.id for row in examples}) != 768:
        raise ValueError("The panel must contain 768 unique bitmaps and IDs")

    normalized = set()
    orbit_owners = defaultdict(set)
    for example in examples:
        support = normalized_support(example.pixels)
        style = STYLES[example.style]
        if len(support) != style.width + style.height - 1 or len(support) <= 5:
            raise ValueError(f"Wrong ink count for {example.id}")
        normalized.add(support)
        orbit_owners[canonical_support(support)].add((example.style, example.label))
    if len(normalized) != 48 or len(orbit_owners) != 12 or any(len(owners) != 1 for owners in orbit_owners.values()):
        raise ValueError("Each style and label must have its own four normalized turns")

    previous_bitmaps = set()
    for name, expected_hash in PREDECESSOR_HASHES.items():
        path = FAMILY.parents[1] / PREDECESSOR / name
        data = path.read_bytes()
        if sha256(data).hexdigest() != expected_hash:
            raise ValueError(f"Predecessor hash mismatch for {path}")
        previous_bitmaps.update(json.loads(line)["pixels"] for line in data.splitlines())
    if len(previous_bitmaps) != 400:
        raise ValueError("Expected 400 unique predecessor bitmaps")
    previous_normalized = {normalized_support(pixels) for pixels in previous_bitmaps}
    previous_orbits = {canonical_support(support) for support in previous_normalized}
    overlaps = {
        "bitmaps": len(bitmaps & previous_bitmaps),
        "normalized_supports": len(normalized & previous_normalized),
        "rotation_orbits": len(set(orbit_owners) & previous_orbits),
    }
    if any(overlaps.values()):
        raise ValueError(f"Predecessor and successor panels overlap {overlaps}")
    return {
        "unique_bitmaps": len(bitmaps),
        "normalized_supports": len(normalized),
        "rotation_orbits": len(orbit_owners),
        "blind_seen_rotation_orbit_overlap": 0,
        "predecessor": {
            "path_from_experiments": PREDECESSOR.as_posix(),
            "file_sha256": PREDECESSOR_HASHES,
            "unique_bitmaps": len(previous_bitmaps),
            "normalized_supports": len(previous_normalized),
            "rotation_orbits": len(previous_orbits),
            "overlap": overlaps,
        },
    }


def order_key(salt: str, example: Example) -> tuple[str, str]:
    return sha256((salt + example.pixels).encode("ascii")).hexdigest(), example.id


def json_lines(rows: Iterable[Mapping[str, str | int]]) -> bytes:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")


def build_panel() -> dict[str, bytes]:
    """Return the panel files and manifest without writing to disk."""
    examples = make_examples()
    support_audit = audit_support(examples)
    training = sorted(
        (example for example in examples if example.condition == "train"),
        key=lambda example: order_key(TRAIN_ORDER_SALT, example),
    )
    queries = sorted(
        (example for example in examples if example.condition != "train"),
        key=lambda example: order_key(QUERY_ORDER_SALT, example),
    )
    rows_by_file = {
        "train.jsonl": [example.view() for example in training],
        "queries.jsonl": [example.view() for example in queries],
        "training_key.jsonl": [example.key() for example in sorted(training, key=lambda row: row.id)],
        "scorer_key.jsonl": [example.key() for example in sorted(queries, key=lambda row: row.id)],
    }
    files = {name: json_lines(rows) for name, rows in rows_by_file.items()}
    counts = Counter((row.style_stratum, row.condition, row.label) for row in examples)
    manifest = {
        "schema_version": 1,
        "generator": {"path": "../panel.py", "sha256": sha256(Path(__file__).read_bytes()).hexdigest()},
        "bitmap": {
            "rows": BITMAP_SIZE,
            "cols": BITMAP_SIZE,
            "encoding": "row-major ASCII bits",
            "values": [0, 1],
            "lit_pixels": [6, 7],
        },
        "id": "Lowercase hexadecimal SHA-256 of the ASCII bit string",
        "styles": {
            name: {
                "width": style.width,
                "height": style.height,
                "T_stem_col": style.stem_col,
                "style_stratum": style.stratum,
                "lit_pixels": style.width + style.height - 1,
                "upright": {label: upright_glyph(style, label) for label in LABELS},
            }
            for name, style in STYLES.items()
        },
        "anchors": {
            "coordinates": "Zero-based (row, col) of the top-left of the rotated bounding box",
            "indices": list(range(4)),
            "held_out_rule": "(row + col) % 2 == 0",
            "held_out": [(row, col) for row, col in ANCHORS if held_anchor(row, col)],
            "seen": [(row, col) for row, col in ANCHORS if not held_anchor(row, col)],
        },
        "orientation": {
            "rotation": "q clockwise quarter-turns within the bounding box, then place at the anchor without clipping",
            "seen_q": FAMILIAR_QUARTER_TURNS,
            "held_out_q": (2, 3),
        },
        "conditions": {
            "train": "Seen anchor and q with style 'AB'[(row + q) % 2] or 'CD'[(row // 2 + q) % 2]",
            "familiar": "Seen anchor and q with the remaining two seen styles and both blind styles",
            "position": "Held-out anchor and seen q with all styles",
            "orientation": "Seen anchor and held-out q with all styles",
            "combined": "Held-out anchor and q with all styles",
        },
        "ordering": {
            "input_sort": "Ascending SHA-256 of ASCII (salt + bit string), then ascending id for ties",
            "train_salt": TRAIN_ORDER_SALT,
            "query_salt": QUERY_ORDER_SALT,
            "key_sort": "Ascending id within each key file",
        },
        "counts": {
            stratum: {
                condition: {label: counts[stratum, condition, label] for label in LABELS}
                for condition in conditions
            }
            for stratum, conditions in (("seen", ("train",) + QUERY_CONDITIONS), ("blind", QUERY_CONDITIONS))
        },
        "support_audit": support_audit,
        "files": {
            name: {"rows": len(rows_by_file[name]), "sha256": sha256(data).hexdigest()}
            for name, data in files.items()
        },
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
