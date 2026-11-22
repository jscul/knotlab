"""Draw actual issued bitmaps and calls from the sealed public and blind releases."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from custody import ARCHIVE, RECORD


def indexed(path):
    return {r["id"]: r for line in path.read_bytes().splitlines() if (r := json.loads(line))}


def figure():
    if not (ARCHIVE / "scored/release.json").is_file():
        raise ValueError("This illustration requires the released blind score")
    panel = RECORD.parents[1] / "experiments" / RECORD.name / ARCHIVE.name / "panel"
    letters = "LT"
    banks = []
    for stage, kind, key in (("pair", "diagnostic", "diagnostic_key"), ("blind", "queries", "scorer_key")):
        keys, images = indexed(panel / (key + ".jsonl")), indexed(panel / (kind + ".jsonl"))
        rows = []
        for identity, pred in sorted(indexed(ARCHIVE / stage / "predictions.jsonl").items()):
            q = keys[identity]
            guess = letters[pred["actions"]["position-parity-ordinary"]]
            rows.append((q["label"], guess, q["q"] * 90, images[identity]["pixels"], q["style"]))
        banks.append(rows)
    canvas = Image.new("RGB", (816, 386), "#ffffff")
    draw = ImageDraw.Draw(canvas)
    fonts = Path("/usr/share/fonts/truetype/dejavu")
    title = ImageFont.truetype(str(fonts / "DejaVuSans-Bold.ttf"), 15)
    normal = ImageFont.truetype(str(fonts / "DejaVuSans.ttf"), 14)
    small = ImageFont.truetype(str(fonts / "DejaVuSans.ttf"), 11)
    for col, header in enumerate(("Public diagnostic", "Fresh · correct guess", "Fresh · wrong guess")):
        x = 15 + col * 269
        draw.text((x, 8), header, font=title, fill="#162f44")
        for row, label in enumerate(letters):
            y = 40 + row * 173
            options = [s for s in banks[int(col > 0)] if s[0] == label and
                       (col == 0 or (s[2] >= 180 and (s[0] == s[1]) == (col == 1)))]
            if not options:
                draw.text((x, y + 50), f"No held {label} in this cell", font=normal, fill="#555555")
                continue
            truth, guess, angle, bits, style = options[0]
            for pos, bit in enumerate(bits):
                rr, cc = divmod(pos, 8)
                a, b = x + cc * 14, y + rr * 14
                draw.rectangle((a, b, a + 14, b + 14), fill="#192d3a" if bit == "1" else "#ffffff",
                               outline="#cfd9df", width=1)
            draw.text((x, y + 116), f"{truth} at {angle}°  →  guessed {guess}", font=normal,
                      fill="#086b53" if truth == guess else "#922b28")
            draw.text((x, y + 136), style, font=small, fill="#516572")
    canvas.save(RECORD / "drawings.png", optimize=True)


if __name__ == "__main__":
    figure()
