"""Replay a held bitmap through the trained, exchanged, cleared and restored state."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

RECORD = Path(__file__).resolve().parent
TICKET = RECORD.name
FAMILY = TICKET + "-E001_groups"
ROOT = RECORD.parents[1]
CODE = ROOT / "experiments" / TICKET / FAMILY
DATA = ROOT / "artifacts" / TICKET / FAMILY
sys.path.insert(0, str(CODE))
from learner import KnotLearner


def read(p):
    return json.loads(p.read_text())


def rows(p):
    return [json.loads(s) for s in p.read_text().splitlines()]


def replay(ident, law):
    q = next(r for r in rows(CODE / "panel/queries.jsonl") if r["id"] == ident)
    pixels = tuple(map(int, q["pixels"]))
    ordinary = read(DATA / f"fit/{law}-ordinary.json")
    opposite = read(DATA / f"fit/{law}-opposite.json")
    dev = KnotLearner.from_memory(ordinary)
    observed = dev.explain(pixels, detail=True)
    learned = dev.selection()
    actions = [observed["guess"]]
    dev.restore_memory(opposite)
    actions.append(dev.predict(pixels))
    dev.clear_memory()
    actions.append(dev.predict(pixels))
    dev.restore_memory(ordinary)
    actions.append(dev.predict(pixels))
    locked = next(r for r in rows(DATA / "blind/predictions.jsonl") if r["id"] == ident)
    labels = ("ordinary","swapped-ordinary","clear-ordinary","restored-ordinary")
    assert actions == [locked["actions"][f"{law}-{key}"] for key in labels]
    assert observed["counts"] == locked["counts"] and observed["votes"] == locked["votes"]
    answer = next(k for k in rows(CODE / "panel/scorer_key.jsonl") if k["id"] == ident)
    explain_rules = []
    for mask, voted in zip(learned["masks"], observed["rule_votes"], strict=True):
        group = [i for i in range(16) if mask & (1 << i)]
        # Show the shorter, equivalent side when it fits the human explanation better.
        if len(group) > 8:
            group = [i for i in range(16) if i not in group]
        means = [str(Fraction(sum(row[i] for i in group), n)) for row,n in
                 zip(learned["class_totals"], learned["class_counts"], strict=True)]
        explain_rules.append({"categories": [format(i,"04b") for i in group],
                              "L_and_T_means":means, "observed_sum":sum(observed["counts"][i] for i in group),
                              "vote":None if voted is None else "LT"[voted]})
    return {**answer,"pixels":[q["pixels"][i:i+8] for i in range(0,64,8)],
            "learned_rules":explain_rules, "issued":dict(zip(labels,["LT"[b] for b in actions])),
            "former_approach":"LT"[locked["actions"][f"previous-{law}"]]}


def draw(choices, path):
    from PIL import Image, ImageDraw, ImageFont
    canvas = Image.new("RGB",(224 * len(choices),239),"white")
    pen = ImageDraw.Draw(canvas)
    plain = ImageFont.truetype("DejaVuSans.ttf",16)
    bold = ImageFont.truetype("DejaVuSans-Bold.ttf",18)
    for i, case in enumerate(choices):
        x = i * 224 + 112
        pen.text((x,10),f"Held turn {90*case['q']}°",font=plain,fill="#28343a",anchor="mt")
        raw = Image.new("L",(8,8))
        raw.putdata([255*int(b) for line in case["pixels"] for b in line])
        canvas.paste(raw.resize((144,144),Image.Resampling.NEAREST),(x-72,39))
        pen.rectangle((x-73,38,x+72,183),outline="#66727a")
        pen.text((x,193),f"True {case['label']}    Guess {case['issued']['ordinary']}",
                 font=bold,fill="#142029",anchor="mt")
        pen.text((x,218),f"Previous guess {case['former_approach']}",font=plain,fill="#505961",anchor="mt")
    canvas.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id",help="Unique prefix of a blind test image ID")
    parser.add_argument("--law",choices=("parity","nae"),default="parity")
    parser.add_argument("--figure",type=Path)
    args = parser.parse_args()
    if args.id:
        ids = [q["id"] for q in rows(CODE/"panel/queries.jsonl") if q["id"].startswith(args.id)]
        if len(ids) != 1:
            parser.error("Supply one unique bitmap prefix")
    else:
        choices = read(DATA/"scored/scores.json")["representatives"]
        ids = [min(row["id"] for key,row in choices.items() if key.startswith(f"blind/combined/q{q}/{letter}/"))
               for q in (2,3) for letter in "LT"]
    result = [replay(i,args.law) for i in ids]
    print(json.dumps(result,indent=2))
    if args.figure:
        draw(result,args.figure)

