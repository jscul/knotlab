"""Inspect the physical read and fixed-recipient interventions for actual queries."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
TICKET = HERE.name
FAMILY = f"{TICKET}-E001_letters"
CODE = HERE.parents[1] / "experiments" / TICKET / FAMILY
ARTIFACTS = HERE.parents[1] / "artifacts" / TICKET / FAMILY
sys.path.insert(0, str(CODE))
from learner import KnotLearner

SELECTION = ("familiar/L/correct", "position/T/correct",
             "orientation/L/error", "orientation/T/error")


def load(path):
    return json.loads(path.read_text())


def lines(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def replay(ident, law):
    public = next(q for q in lines(CODE / "panel/queries.jsonl") if q["id"] == ident)
    locked = next(b for b in lines(ARTIFACTS / "blind/predictions.jsonl") if b["id"] == ident)
    # Construct a fresh receiver with only the law, fixed capacity and fitted marks.
    pixels = tuple(map(int, public["pixels"]))
    receiver = KnotLearner(law, training_limit=64)
    ordinary = load(ARTIFACTS / f"fit/{law}-ordinary.json")
    opposite = load(ARTIFACTS / f"fit/{law}-opposite.json")
    receiver.restore_memory(ordinary)
    own = receiver.explain(pixels)
    receiver.restore_memory(opposite)
    swap = receiver.predict(pixels)
    receiver.clear_memory()
    clear = receiver.predict(pixels)
    receiver.restore_memory(ordinary)
    back = receiver.predict(pixels)
    observed = [own["guess"], swap, clear, back]
    arm_names = ["ordinary", "donor-into-ordinary", "clear-ordinary", "restore-ordinary"]
    assert observed == [locked["actions"][f"{law}-{name}"] for name in arm_names]
    assert own == locked["reading"]
    # Attach the scorer's answer only after all four decisions are out.
    key = next(k for k in lines(CODE / "panel/scorer_key.jsonl") if k["id"] == ident)
    costs = [str(Fraction(a["distance_numerator"], a["distance_denominator"])) for a in own["actions"]]
    return {**key, "pixels": [public["pixels"][n:n + 8] for n in range(0, 64, 8)],
            "patch_counts_0000_through_1111": own["counts"],
            "squared_error_to_L_and_T_means": costs,
            "fixed_recipient_guesses": {name: "LT"[a] for name, a in zip(arm_names, observed)},
            "raw_nearest_guess": "LT"[locked["actions"]["nearest-ordinary"]]}


def figure(cases, path):
    from PIL import Image, ImageDraw, ImageFont
    width = 212
    canvas = Image.new("RGB", (width * len(cases), 240), "white")
    draw = ImageDraw.Draw(canvas)
    regular = ImageFont.truetype("DejaVuSans.ttf", 16)
    bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    labels = {"familiar": "Familiar pose", "position": "New position",
              "orientation": "New orientation", "combined": "New position + turn"}
    for index, case in enumerate(cases):
        x = index * width + width // 2
        draw.text((x, 12), labels[case["condition"]], font=regular, fill="#25333c", anchor="mt")
        block = Image.new("L", (8, 8))
        block.putdata([255 * int(bit) for row in case["pixels"] for bit in row])
        canvas.paste(block.resize((144, 144), Image.Resampling.NEAREST), (x - 72, 41))
        caption = f"True {case['label']}   Guess {case['fixed_recipient_guesses']['ordinary']}"
        draw.text((x, 194), caption, font=bold, fill="#142029", anchor="mt")
        style = {"S": "Compact", "W": "Wide"}[case["style"]]
        draw.text((x, 218), f"{style} · {90 * case['q']}°", font=regular, fill="#505961", anchor="mt")
    canvas.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Unique prefix of a frozen test bitmap ID")
    parser.add_argument("--law", choices=("parity", "nae"), default="parity")
    parser.add_argument("--figure", type=Path, help="Write a PNG of the replayed bitmaps")
    args = parser.parse_args()
    if args.id:
        ids = [r["id"] for r in lines(CODE / "panel/queries.jsonl") if r["id"].startswith(args.id)]
        if len(ids) != 1:
            parser.error("Supply a prefix that identifies one test row")
    else:
        reps = load(ARTIFACTS / "scored/scores.json")["representatives"]
        ids = [reps[condition]["id"] for condition in SELECTION]
    cases = [replay(ident, args.law) for ident in ids]
    print(json.dumps(cases, indent=2))
    if args.figure:
        figure(cases, args.figure)

