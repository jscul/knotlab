"""Render two distinct held letters with the same complete count signature at one new position."""

import argparse
import json
from pathlib import Path

from replay_examples import DATA, PANEL, keyed


def witness():
    diagnostics = json.loads((DATA / "group_diagnostics.json").read_bytes())
    collision = diagnostics["signature_collision_bounds"]["full_sensor"]["held_turns"]["witness"]
    keys = keyed(PANEL / "scorer_key.jsonl")
    views = keyed(PANEL / "queries.jsonl")
    decisions = keyed(DATA / "blind/predictions.jsonl")
    examples = []
    for letter in "LT":
        seed = keys[collision["example_ids"][letter]]
        key, = (row for row in keys.values() if row["label"] == letter and row["style"] == seed["style"]
                and row["q"] == seed["q"] and (row["row"], row["col"]) == (1, 1))
        pred = decisions[key["id"]]
        assert pred["details"]["varied"]["counts"] == collision["signature"]
        examples.append({**key, "pixels": views[key["id"]]["pixels"],
                         "narrow_guess": "LT"[pred["actions"]["narrow-parity-ordinary"]],
                         "varied_guess": "LT"[pred["actions"]["varied-parity-ordinary"]]})
    assert examples[0]["pixels"] != examples[1]["pixels"]
    return {"examples": examples, "common_counts": collision["signature"]}


def draw(result, path):
    from PIL import Image, ImageDraw, ImageFont
    canvas = Image.new("RGB", (510, 278), "white")
    pen = ImageDraw.Draw(canvas)
    header = ImageFont.truetype("DejaVuSans-Bold.ttf", 19)
    body = ImageFont.truetype("DejaVuSans.ttf", 15)
    pen.text((255, 10), "Different letters, identical sensor counts", font=header, fill="#182b35", anchor="mt")
    for x, case in zip((130, 380), result["examples"], strict=True):
        tile = Image.new("L", (8, 8))
        tile.putdata([255 * int(b) for b in case["pixels"]])
        canvas.paste(tile.resize((120, 120), Image.Resampling.NEAREST), (x - 60, 46))
        pen.rectangle((x - 61, 45, x + 60, 166), outline="#60737d")
        pen.text((x, 177), f"True {case['label']} at {90 * case['q']}°", font=header, fill="#182b35", anchor="mt")
        pen.text((x, 204), f"Narrow {case['narrow_guess']}    Varied {case['varied_guess']}",
                 font=body, fill="#29434e", anchor="mt")
    pen.text((255, 244), "Counts    " + "  ".join(map(str, result["common_counts"])),
             font=body, fill="#29434e", anchor="mt")
    canvas.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", type=Path)
    args = parser.parse_args()
    result = witness()
    if args.figure:
        draw(result, args.figure)
    print(json.dumps(result, indent=2))
