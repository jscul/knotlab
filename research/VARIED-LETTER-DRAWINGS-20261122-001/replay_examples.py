"""Read a released blind bitmap through both physical fits and draw matched examples."""

import argparse
import json
from pathlib import Path
import sys

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parents[1]
TICKET = RECORD.name
FAMILY = TICKET + "-E001_drawings"
DATA = ROOT / "artifacts" / TICKET / FAMILY
PANEL = ROOT / "experiments" / TICKET / FAMILY / "panel"
PREVIOUS = ROOT / "experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups"
sys.path.insert(0, str(PREVIOUS))
from learner import KnotLearner


def read_rows(file):
    return [json.loads(line) for line in file.read_text().splitlines()]


def keyed(file):
    return {row["id"]: row for row in read_rows(file)}


def checkpoint(arm, law, convention):
    return json.loads((DATA / "fit" / f"{arm}-{law}-{convention}.json").read_text())


def one(bitmap, key, locked, law):
    pixels = tuple(map(int, bitmap["pixels"]))
    arms = {}
    for arm in ("narrow", "varied"):
        memory = checkpoint(arm, law, "ordinary")
        device = KnotLearner.from_memory(memory)
        result = device.explain(pixels, detail=True)
        groups = device.selection()
        actual = {"ordinary": result["guess"]}
        device.restore_memory(checkpoint(arm, law, "opposite"))
        actual["swapped-ordinary"] = device.predict(pixels)
        device.clear_memory()
        actual["clear-ordinary"] = device.predict(pixels)
        device.restore_memory(memory)
        actual["restored-ordinary"] = device.predict(pixels)
        assert all(locked["actions"][f"{arm}-{law}-{kind}"] == value for kind, value in actual.items())
        arms[arm] = {"actions": {name: "LT"[value] for name, value in actual.items()},
                     "votes_L_T": result["votes"], "abstentions": result["abstentions"],
                     "rule_votes_in_mask_order": result["rule_votes"], "masks": groups["masks"],
                     "class_counts": groups["class_counts"], "per_class_bin_totals": groups["class_totals"]}
    return {**key, "pixels": bitmap["pixels"], "observed_counts": result["counts"], "readers": arms}


def select_examples(keys):
    rows = keys.values()
    return [min(row["id"] for row in rows if row["q"] == turn and row["label"] == letter
                and (row["row"] + row["col"]) % 2 == 0) for turn in (2, 3) for letter in "LT"]


def training_pair():
    # The 0-degree deformed L with the smallest digest defines the whole matched pair.
    varied = list(keyed(PANEL / "training_key_varied.jsonl").values())
    narrow = {row["slot"]: row for row in read_rows(PANEL / "training_key_narrow.jsonl")}
    selected = min((row for row in varied if row["label"] == "L" and row["q"] == 0 and
                    row["id"] != narrow[row["slot"]]["id"]), key=lambda row: row["id"])
    rows = sorted((row for row in varied if (row["row"], row["col"], row["q"], row["style"]) ==
                   (selected["row"], selected["col"], selected["q"], selected["style"])),
                  key=lambda row: row["label"])
    assert [r["label"] for r in rows] == ["L", "T"]
    examples = []
    for row in rows:
        for arm, key in (("narrow", narrow[row["slot"]]), ("varied", row)):
            view = keyed(PANEL / f"train_{arm}.jsonl")[key["id"]]
            examples.append((view["pixels"], arm.capitalize() + " " + key["label"]))
    return examples


def draw(cases, path):
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (792, 445), "white")
    pen = ImageDraw.Draw(canvas)
    bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 17)
    regular = ImageFont.truetype("DejaVuSans.ttf", 15)

    def bitmap(pixels, x, y):
        image = Image.new("L", (8, 8))
        image.putdata([255 * int(bit) for bit in pixels])
        canvas.paste(image.resize((112, 112), Image.Resampling.NEAREST), (x - 56, y))
        pen.rectangle((x - 57, y - 1, x + 56, y + 112), outline="#60737d")

    pen.text((396, 9), "Matched training drawings at 0°", font=bold, fill="#182b35", anchor="mt")
    for i, (pixels, label) in enumerate(training_pair()):
        x = 99 + 198 * i
        bitmap(pixels, x, 42)
        pen.text((x, 163), label, font=regular, fill="#253d49", anchor="mt")
    pen.line((24, 194, 768, 194), fill="#c5cdd0")
    pen.text((396, 209), "Blind drawings at new positions", font=bold, fill="#182b35", anchor="mt")
    for i, result in enumerate(cases):
        x = 99 + 198 * i
        bitmap(result["pixels"], x, 243)
        pen.text((x, 365), f"True {result['label']} at {90 * result['q']}°", font=bold, fill="#182b35", anchor="mt")
        readers = result["readers"]
        for line, arm in enumerate(("narrow", "varied")):
            text = f"{arm.capitalize()} guessed {readers[arm]['actions']['ordinary']}"
            pen.text((x, 393 + 22 * line), text, font=regular, fill="#253d49", anchor="mt")
    canvas.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Unique prefix of a blind image digest")
    parser.add_argument("--law", choices=("parity", "nae"), default="parity")
    parser.add_argument("--figure", type=Path, help="Draw the default four examples")
    args = parser.parse_args()
    if args.figure and args.id:
        parser.error("--figure uses the default four examples")
    if not (DATA / "scored/release.json").is_file():
        parser.error("This interpretation requires the released score")
    keys = keyed(PANEL / "scorer_key.jsonl")
    views = keyed(PANEL / "queries.jsonl")
    locked = keyed(DATA / "blind/predictions.jsonl")
    if args.id:
        ids = [ident for ident in keys if ident.startswith(args.id)]
        if len(ids) != 1:
            parser.error("Give a unique digest prefix")
    else:
        ids = select_examples(keys)
    cases = [one(views[ident], keys[ident], locked[ident], args.law) for ident in ids]
    if args.figure:
        draw(cases, args.figure)
    print(json.dumps(cases, indent=2))


if __name__ == "__main__":
    main()
