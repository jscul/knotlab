"""Build and replay the finite 8-by-8 pixel-letter panel."""

import argparse
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from tempfile import TemporaryDirectory


BITMAP_SIZE = 8
ANCHORS = tuple(product(range(5), repeat=2))
FAMILIAR_QUARTER_TURNS = (0, 1)
STYLES = ("S", "W")
LABELS = ("L", "T")
CONDITIONS = ("train", "familiar", "position", "orientation", "combined")
GLYPHS = {
    "S": {
        "L": ("100", "100", "111"),
        "T": ("111", "010", "010"),
    },
    "W": {
        "L": ("1000", "1111"),
        "T": ("1111", "0100"),
    },
}
TRAIN_ORDER_SALT = "pixel-letters-20261122-v1-train:"
QUERY_ORDER_SALT = "pixel-letters-20261122-v1-query:"


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

    def view(self) -> dict[str, str]:
        return {"id": self.id, "pixels": self.pixels}

    def scorer_key(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "label": self.label,
            "condition": self.condition,
            "style": self.style,
            "row": self.row,
            "col": self.col,
            "q": self.q,
        }


def held_anchor(row: int, col: int) -> bool:
    return (row + 2 * col) % 3 == 0


def condition_for(style: str, row: int, col: int, q: int) -> str:
    if held_anchor(row, col):
        return "position" if q in FAMILIAR_QUARTER_TURNS else "combined"
    if q not in FAMILIAR_QUARTER_TURNS:
        return "orientation"
    return "train" if style == STYLES[(row + col + q) % 2] else "familiar"


def bitmap(rows: tuple[str, ...], top: int, left: int, q: int) -> str:
    height, width = len(rows), len(rows[0])
    lit = {
        (row, col)
        for row, glyph_row in enumerate(rows)
        for col, pixel in enumerate(glyph_row)
        if pixel == "1"
    }
    for _ in range(q):
        lit = {(col, height - 1 - row) for row, col in lit}
        height, width = width, height

    if top + height > BITMAP_SIZE or left + width > BITMAP_SIZE:
        raise ValueError(f"Glyph exceeds the bitmap at {(top, left)} and rotation {q}")
    return "".join(
        "1" if (row - top, col - left) in lit else "0"
        for row, col in product(range(BITMAP_SIZE), repeat=2)
    )


def make_examples() -> list[Example]:
    examples = []
    for (row, col), q, style, label in product(ANCHORS, range(4), STYLES, LABELS):
        pixels = bitmap(GLYPHS[style][label], row, col, q)
        examples.append(Example(
            id=sha256(pixels.encode("ascii")).hexdigest(),
            pixels=pixels,
            label=label,
            condition=condition_for(style, row, col, q),
            style=style,
            row=row,
            col=col,
            q=q,
        ))
    if any(example.pixels.count("1") != 5 for example in examples):
        raise ValueError("Every bitmap must have five lit pixels")
    if len({example.id for example in examples}) != len(examples):
        raise ValueError("Every bitmap and hash ID must occur exactly once")
    return examples


def order_hash(salt: str, example: Example) -> str:
    return sha256((salt + example.pixels).encode("ascii")).hexdigest()


def json_lines(rows: Iterable[Mapping[str, str | int]]) -> bytes:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")


def build_panel() -> dict[str, bytes]:
    """Return the panel files and manifest without writing to disk."""
    examples = make_examples()
    training = sorted(
        (example for example in examples if example.condition == "train"),
        key=lambda example: (order_hash(TRAIN_ORDER_SALT, example), example.id),
    )
    queries = sorted(
        (example for example in examples if example.condition != "train"),
        key=lambda example: (order_hash(QUERY_ORDER_SALT, example), example.id),
    )
    rows_by_file = {
        "train.jsonl": [example.view() for example in training],
        "queries.jsonl": [example.view() for example in queries],
        "training_key.jsonl": [
            example.scorer_key() for example in sorted(training, key=lambda example: example.id)
        ],
        "scorer_key.jsonl": [
            example.scorer_key() for example in sorted(queries, key=lambda example: example.id)
        ],
    }
    files = {name: json_lines(rows) for name, rows in rows_by_file.items()}
    counts = Counter((example.condition, example.label) for example in examples)
    manifest = {
        "schema_version": 1,
        "generator": {
            "path": "../panel.py",
            "sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "bitmap": {
            "rows": BITMAP_SIZE,
            "cols": BITMAP_SIZE,
            "encoding": "row-major ASCII bits",
            "lit_pixels": 5,
        },
        "id": "Lowercase hexadecimal SHA-256 of the ASCII bit string",
        "upright_glyphs": GLYPHS,
        "anchors": {
            "coordinates": "Zero-based (row, col) of the top-left of the rotated bounding box",
            "indices": list(range(5)),
            "held_out_rule": "(row + 2 * col) % 3 == 0",
            "held_out": [(row, col) for row, col in ANCHORS if held_anchor(row, col)],
            "seen": [(row, col) for row, col in ANCHORS if not held_anchor(row, col)],
        },
        "orientation": {
            "rotation": "q clockwise quarter-turns within the bounding box, then place at the anchor without clipping",
            "seen_q": FAMILIAR_QUARTER_TURNS,
            "held_out_q": (2, 3),
        },
        "conditions": {
            "train": "Seen anchor and q, style S for even (row + col + q) and W for odd",
            "familiar": "Seen anchor and q, the other style at that pose",
            "position": "Held-out anchor and seen q, both styles",
            "orientation": "Seen anchor and held-out q, both styles",
            "combined": "Held-out anchor and q, both styles",
        },
        "ordering": {
            "input_sort": "Ascending SHA-256 of ASCII (salt + bit string), then ascending id for ties",
            "train_salt": TRAIN_ORDER_SALT,
            "query_salt": QUERY_ORDER_SALT,
            "key_sort": "Ascending id within each key file",
        },
        "counts": {
            condition: {label: counts[condition, label] for label in LABELS}
            for condition in CONDITIONS
        },
        "files": {
            name: {"rows": len(rows_by_file[name]), "sha256": sha256(data).hexdigest()}
            for name, data in files.items()
        },
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("ascii")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().with_name("panel"))
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
