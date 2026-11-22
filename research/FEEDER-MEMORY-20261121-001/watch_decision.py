"""Render the recorded paired feeder histories and keeper interventions."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw


PRIOR = Path(__file__).resolve().parents[1] / "KNOT-RATION-GAME-20261121-001" / "spectator.py"
SPEC = importlib.util.spec_from_file_location("ration_media", PRIOR)
MEDIA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MEDIA)

WIDTH, HEIGHT = MEDIA.WIDTH, MEDIA.HEIGHT
BG, PANEL, INSET, STROKE = MEDIA.BG, MEDIA.PANEL, MEDIA.INSET, MEDIA.STROKE
INK, SECONDARY = MEDIA.INK, MEDIA.SECONDARY
MOVE, RATION, GROWTH, DEATH = MEDIA.MOVE, MEDIA.RATION, MEDIA.GROWTH, MEDIA.DEATH
font = MEDIA.font

LAWS = {"parity": "Parity", "nae": "Not-all-equal"}
SIDES = {"empty": "History A", "full": "History B"}
ARMS = {"original": "Original", "sham": "Sham", "swapped": "Reciprocal exchange"}
MEMORY = {"110": "ready", "101": "one port", "011": "multiple ports"}
PREVIOUS = {0: "Start", 1: "Eat", 2: "Move", 3: "Refused"}
LEFT, RIGHT = 36, 609
PANEL_WIDTH = 555


def action_name(bit):
    return {None: "No bit emitted", 0: "PASS", 1: "EAT"}[bit]


def options(slots):
    return slots if isinstance(slots, int) else len(slots)


def public_view(current):
    if isinstance(current, dict):
        feeder, energy, previous, slots = (current[key] for key in ("feeder", "energy", "previous", "slots"))
    else:
        feeder, energy, previous, slots = current
    previous = PREVIOUS.get(previous, str(previous).title())
    return feeder, energy, previous, slots


def paid_meals(prefix):
    return [event for event in prefix if event["consumed"]]


def spectator_result(event):
    """Describe the applied game event independently of the keeper receipt."""
    if event is None:
        return "—", "No game event recorded", SECONDARY
    if event["action"] == "eat":
        if event["consumed"]:
            return "EAT", f"Ration consumed at K{event['holder_before']}", RATION
        detail = "Ration already spent" if event.get("feeder", True) else "No feeder here"
        return "EAT", detail, DEATH
    start, end = event["holder_before"], event["holder_after"]
    if event["action"] == "move" and start != end:
        return "PASS", f"K{start} → K{end} via d{event['distinction']}", MOVE
    return action_name(event["bit"]), "Action refused", DEATH


def recorded_route(case):
    """Lay out the simple recorded chain when it fits both prefix panels."""
    events = [event for side in SIDES for event in case["branches"][side]["prefix"]]
    holders = list(dict.fromkeys(event[key] for event in events
                                 for key in ("holder_before", "holder_after")))
    if not 2 <= len(holders) <= 5:
        return None
    indices = {holder: index for index, holder in enumerate(holders)}
    links = {}
    for event in events:
        if event["action"] != "move":
            continue
        origin, destination = (indices[event[key]] for key in ("holder_before", "holder_after"))
        pair = min(origin, destination), max(origin, destination)
        name = event["distinction"]
        if pair[1] - pair[0] != 1 or links.get(pair, name) != name:
            return None
        links[pair] = name
    return {holder: 86 + round(index * 382 / (len(holders) - 1)) for holder, index in indices.items()}


class Frame:
    def __init__(self, laws, case, stage, index, count):
        self.case = case
        self.pair = case["pair"]
        self.image = Image.new("RGB", (WIDTH, HEIGHT), BG)
        self.draw = ImageDraw.Draw(self.image)
        self.box((36, 32, 44, 99), GROWTH, radius=4)
        self.label(60, 30, "Feeder memory", 44, bold=True)
        self.label(62, 86, "Prepared histories and keeper exchange", 18, SECONDARY)
        law_label = "Parity · Not-all-equal" if len(laws) == 2 else LAWS[laws[0]]
        self.label(1164, 37, law_label, 27, bold=True, anchor="rt")
        scope = f"Seed {self.pair['seed']}  ·  tape {self.pair['tape']}  ·  {self.pair['variant']}"
        self.label(1164, 79, scope, 16, SECONDARY, anchor="rt")
        self.label(37, 632, stage, 19, bold=True)
        self.box((326, 642, 1164, 649), STROKE, radius=4)
        x = 326 + round(838 * index / max(1, count - 1))
        if x > 326:
            self.box((326, 642, x, 649), GROWTH, radius=4)
        self.draw.ellipse((x - 5, 641, x + 5, 651), fill=GROWTH)

    def label(self, x, y, text, size, color=INK, bold=False, anchor="lt"):
        self.draw.text((x, y), str(text), font=font(size, bold), fill=color, anchor=anchor)

    def box(self, bounds, color, outline=None, radius=16):
        self.draw.rounded_rectangle(bounds, radius=radius, fill=color, outline=outline)

    def rule(self, x, y, width):
        self.draw.line((x, y, x + width, y), fill=STROKE)

    def side_panel(self, x, y, side, title=None):
        self.box((x, y, x + PANEL_WIDTH, 608), PANEL)
        self.label(x + 23, y + 21, SIDES[side], 24, bold=True)
        if title:
            self.label(x + PANEL_WIDTH - 23, y + 27, title, 16, SECONDARY, anchor="rt")

    def memory_word(self, x, y, word, emphasized=False):
        fill = "#315243" if emphasized else INSET
        color = GROWTH if emphasized else INK
        self.box((x, y, x + 63, y + 35), fill, radius=6)
        self.label(x + 31, y + 8, word, 22, color, bold=True, anchor="mt")

    def prefix(self, step, route):
        for x, side in ((LEFT, "empty"), (RIGHT, "full")):
            prefix = self.case["branches"][side]["prefix"]
            reached = prefix[:step]
            self.prefix_branch(x, side, prefix, reached, route)

    def prefix_branch(self, x, side, prefix, reached, route):
        side_turn = reached[-1]["turn"] if reached else 0
        self.side_panel(x, 123, side, f"{side_turn} turns played")
        if route and prefix:
            self.label(x + 23, 183, "SPECTATOR ROUTE", 14, SECONDARY, bold=True)
            self.draw_route(x, route, prefix[0]["holder_before"], reached)
        else:
            self.label(x + 23, 183, "RECORDED ACTION", 14, SECONDARY, bold=True)
        if reached:
            event = reached[-1]
            action, detail, color = spectator_result(event)
            count = options(event["slots"])
            port_word = "port" if count == 1 else "ports"
            cue = "on" if event["feeder"] else "off"
            if route:
                heading = f"{action}  ·  {detail}"
                if event["slot"] is not None:
                    heading += f"  ·  port {event['slot']}"
                self.label(x + 532, 183, f"Cue {cue}  ·  {count} {port_word}",
                           15, SECONDARY, anchor="rt")
                self.label(x + 23, 254, heading, 18, color, bold=True)
            else:
                self.label(x + 23, 214, f"{action}  ·  {detail}", 26, color, bold=True)
                self.label(x + 24, 256, f"Feeder cue {cue}  ·  {count} anonymous {port_word}",
                           16, SECONDARY)
            energy = f"{event['energy_before']} → {event['energy_after']}"
            before, after = event["memory_before"], event["memory_after"]
        elif prefix:
            event = prefix[0]
            if route:
                self.label(x + 23, 254, f"Start at K{event['holder_before']}", 18, MOVE, bold=True)
            else:
                self.label(x + 23, 214, f"Start at K{event['holder_before']}", 32, MOVE, bold=True)
            energy, before, after = str(event["energy_before"]), event["memory_before"], None
        else:
            frozen = self.case["branches"][side]["frozen"]
            self.label(x + 23, 214, f"Start at K{frozen['holder']}", 32, MOVE, bold=True)
            energy, before, after = str(frozen["energy"]), self.case["branches"][side]["memory"], None
        self.rule(x + 23, 287, 509)
        self.label(x + 23, 308, "Energy", 16, SECONDARY)
        self.label(x + 23, 334, energy, 28, INK, bold=True)
        self.label(x + 260, 308, "Keeper memory", 16, SECONDARY)
        self.memory_word(x + 260, 330, before)
        if after is not None:
            self.label(x + 333, 338, "→", 21, SECONDARY)
            self.memory_word(x + 361, 330, after, emphasized=before != after)

        self.rule(x + 23, 380, 509)
        self.label(x + 24, 396, "Recent turns", 16, bold=True)
        for idx, item in enumerate(reached[-4:]):
            y = 424 + idx * 29
            action, detail, color = spectator_result(item)
            self.label(x + 24, y, str(item["turn"]), 16, SECONDARY)
            label = detail if action == "PASS" else f"{action}  ·  {detail}"
            self.label(x + 62, y, label, 17, color)
            energy = f"{item['energy_before']} → {item['energy_after']}"
            self.label(x + 531, y, energy, 16, SECONDARY, anchor="rt")
        self.rule(x + 23, 549, 509)
        self.label(x + 24, 568, self.meal_detail(reached), 16, RATION if paid_meals(reached) else SECONDARY)

    def draw_route(self, x, columns, start, reached):
        y = 221
        seen = {start}
        shown = set()
        last = reached[-1] if reached else None
        active = last["distinction"] if last else None
        current = last["holder_after"] if last else start
        spent = {event["holder_before"] for event in paid_meals(reached)}
        for event in reached:
            first, second, name = (event[key] for key in ("holder_before", "holder_after", "distinction"))
            seen.update((first, second))
            if name is None or name in shown:
                continue
            shown.add(name)
            ax, bx = x + columns[first], x + columns[second]
            color = MOVE if name == active else STROKE
            self.draw.line((ax, y, bx, y), fill=color, width=3 if name == active else 2)
            mid = (ax + bx) // 2
            self.box((mid - 20, y - 11, mid + 20, y + 11), PANEL, radius=5)
            self.label(mid, y - 7, f"d{name}", 15, color if name == active else SECONDARY, anchor="mt")
        for holder in seen:
            at = x + columns[holder]
            color = RATION if holder in spent else MOVE if holder == current else STROKE
            self.draw.ellipse((at - 22, y - 22, at + 22, y + 22), fill=INSET, outline=color, width=3)
            self.label(at, y, f"K{holder}", 16, INK, bold=True, anchor="mm")
            if holder == current and holder in spent:
                self.draw.ellipse((at - 25, y - 25, at + 25, y + 25), outline=MOVE, width=2)

    @staticmethod
    def meal_detail(prefix):
        paid = paid_meals(prefix)
        if not paid:
            return "No ration eaten yet"
        event = paid[-1]
        count = options(event["slots"])
        port_word = "port" if count == 1 else "ports"
        return f"Last meal at K{event['holder_before']}  ·  turn {event['turn']}  ·  {count} {port_word}"

    def public_strip(self):
        feeder, energy, previous, slots = public_view(self.pair["current"])
        self.box((36, 123, 1164, 257), PANEL)
        self.label(58, 143, "Same public observation", 25, bold=True)
        self.label(1141, 148, f"Decision on turn {self.pair['turn']}", 17, SECONDARY, anchor="rt")
        port_count = options(slots)
        port_menu = f"{port_count}  ·  " + ", ".join(map(str, slots)) if not isinstance(slots, int) else port_count
        values = ((59, "Feeder cue", "ON" if feeder else "OFF"),
                  (295, "Energy", energy),
                  (495, "Anonymous move ports", port_menu),
                  (821, "Previous action", previous))
        for x, title, value in values:
            self.label(x, 185, title, 15, SECONDARY, bold=True)
            self.label(x, 211, value, 27, INK, bold=True)

    def stock_label(self, side):
        frozen = self.case["branches"][side]["frozen"]
        return "Ration available" if frozen["holder"] in frozen["available"] else "Ration depleted"

    def decision(self):
        self.public_strip()
        self.label(36, 278, "Spectator view  ·  cue remains on after a ration is spent", 17, SECONDARY)
        for x, side in ((LEFT, "empty"), (RIGHT, "full")):
            branch = self.case["branches"][side]
            frozen = branch["frozen"]
            self.side_panel(x, 305, side, f"At feeder K{frozen['holder']}")
            self.label(x + 23, 367, self.stock_label(side), 29, RATION, bold=True)
            self.label(x + 24, 411, self.meal_detail(branch["prefix"]), 17, SECONDARY)
            self.rule(x + 23, 446, 509)
            ready = self.case["arms"]["original"][side]["before"]["a"]
            self.label(x + 24, 464, "Keeper memory", 16, SECONDARY)
            self.memory_word(x + 24, 492, branch["memory"], emphasized=True)
            if branch["memory"] in MEMORY:
                self.label(x + 98, 500, MEMORY[branch["memory"]], 16, SECONDARY)
            self.label(x + 280, 464, "Same prepared action", 16, SECONDARY)
            self.memory_word(x + 280, 492, ready)

    def intervention(self, arm, phase):
        self.public_strip()
        self.label(36, 272, ARMS[arm], 22, bold=True)
        phase_label = {"prepare": "Games paused  ·  ready to read",
                       "read": "Games paused  ·  action bit recorded",
                       "advance": "Both games advanced from their saved states"}[phase]
        self.label(1164, 278, phase_label, 17, GROWTH if phase == "read" else SECONDARY, anchor="rt")
        for x, side in ((LEFT, "empty"), (RIGHT, "full")):
            self.intervention_branch(x, arm, side, phase)

    def intervention_branch(self, x, arm, side, phase):
        record = self.case["arms"][arm][side]
        self.side_panel(x, 305, side, self.stock_label(side))
        before, intervention, read = (record[key] for key in ("before", "after_intervention", "after_read"))
        self.label(x + 23, 363, "Keeper memory", 16, SECONDARY)
        self.memory_word(x + 23, 391, before["m"])
        self.label(x + 96, 398, "→", 22, SECONDARY)
        self.memory_word(x + 124, 391, intervention["m"], emphasized=before["m"] != intervention["m"])
        if phase != "prepare" and read["m"] != intervention["m"]:
            self.label(x + 196, 398, "→", 22, SECONDARY)
            self.memory_word(x + 224, 391, read["m"], emphasized=True)

        self.label(x + 23, 439, "Prepared action", 16, SECONDARY)
        self.label(x + 23, 466, intervention["a"], 25, INK, bold=True)
        if phase != "prepare":
            bit = record["bit"]
            emitted = action_name(bit) if bit is None else f"Bit {bit}  ·  {action_name(bit)}"
            self.label(x + 166, 439, "Actuator after read", 16, SECONDARY)
            self.label(x + 108, 466, "→", 25, SECONDARY)
            self.label(x + 166, 466, read["a"], 25, INK, bold=True)
            self.label(x + 342, 439, "Keeper output", 16, SECONDARY)
            self.label(x + 342, 465, emitted, 25, RATION if bit == 1 else MOVE, bold=True)

        self.rule(x + 23, 510, 509)
        if phase == "advance":
            event = record["event"]
            action, detail, color = spectator_result(event)
            self.label(x + 23, 529, "Actual game result", 15, SECONDARY, bold=True)
            self.label(x + 23, 557, f"{action}  ·  {detail}", 20, color, bold=True)
            if event is not None:
                energy = f"{event['energy_before']} → {event['energy_after']}"
                self.label(x + 532, 559, energy, 19, SECONDARY, anchor="rt")
                if event["terminal"]:
                    self.label(x + 532, 583, "Died", 15, DEATH, bold=True, anchor="rt")

    def summary(self):
        self.public_strip()
        self.box((36, 279, 1164, 608), PANEL)
        self.label(59, 300, "What happened after advancing", 26, bold=True)
        self.label(424, 346, "History A  ·  empty at decision", 18, SECONDARY, bold=True)
        self.label(788, 346, "History B  ·  full at decision", 18, SECONDARY, bold=True)
        for idx, (arm, label) in enumerate(ARMS.items()):
            y = 376 + idx * 66
            self.rule(59, y, 1083)
            self.label(59, y + 16, label, 20, INK, bold=True)
            for x, side in ((424, "empty"), (788, "full")):
                event = self.case["arms"][arm][side]["event"]
                action, detail, color = spectator_result(event)
                self.label(x, y + 10, action, 22, color, bold=True)
                if event is not None and event["terminal"]:
                    detail += "  ·  died"
                self.label(x, y + 39, detail, 17, SECONDARY)


def display_signature(case):
    """Use both laws' saved display records before combining any views."""
    pair = {key: case["pair"][key] for key in ("seed", "tape", "variant", "turn", "current")}
    branches = {side: {"prefix": branch["prefix"], "holder": branch["frozen"]["holder"],
                       "available": branch["frozen"]["available"], "memory": branch["memory"]}
                for side, branch in case["branches"].items()}
    arms = {}
    for arm in ARMS:
        arms[arm] = {}
        for side in SIDES:
            raw = case["arms"][arm][side]
            registers = [(raw[stage]["m"], raw[stage]["a"])
                         for stage in ("before", "after_intervention", "after_read")]
            arms[arm][side] = (registers, raw["bit"], raw["event"])
    return pair, branches, arms


def replay_cases(data, law):
    if data["schema_version"] != 1:
        raise ValueError(f"Unsupported feeder replay schema {data['schema_version']}")
    available = data["by_law"]
    chosen = LAWS if law == "both" else (law,)
    cases = [(key, available[key]) for key in chosen if available.get(key, {}).get("pair")]
    if not cases:
        raise ValueError("No decisive replay for the requested law")
    if len(cases) == 2 and display_signature(cases[0][1]) == display_signature(cases[1][1]):
        return [(tuple(key for key, _ in cases), cases[0][1])]
    return [((key,), case) for key, case in cases]


def replay_frames(data, law):
    for laws, case in replay_cases(data, law):
        steps = max(len(branch["prefix"]) for branch in case["branches"].values())
        count = steps + 12
        route = recorded_route(case)
        index = 0
        for step in range(steps + 1):
            title = "Prepared histories" if not step else f"Prefix playback  ·  step {step}"
            frame = Frame(laws, case, title, index, count)
            frame.prefix(step, route)
            paid = any(len(branch["prefix"]) >= step and branch["prefix"][step - 1]["consumed"]
                       for branch in case["branches"].values()) if step else False
            yield frame.image, 1500 if paid or step == steps else 850
            index += 1

        frame = Frame(laws, case, "Decision checkpoint", index, count)
        frame.decision()
        yield frame.image, 2550
        index += 1
        for arm in ARMS:
            for phase, duration in (("prepare", 1550), ("read", 1700)):
                frame = Frame(laws, case, ARMS[arm], index, count)
                frame.intervention(arm, phase)
                yield frame.image, duration
                index += 1
        for arm in ARMS:
            frame = Frame(laws, case, ARMS[arm], index, count)
            frame.intervention(arm, "advance")
            yield frame.image, 2000
            index += 1
        frame = Frame(laws, case, "Recorded actions", index, count)
        frame.summary()
        yield frame.image, 3000


def render_replay(data, output, law="both", frame_number=None):
    output = Path(output).expanduser().resolve()
    extension = output.suffix.lower()
    if extension not in {".gif", ".mp4", ".png"}:
        raise ValueError("Output must end in .gif, .mp4, or .png")
    if frame_number is not None and (extension != ".png" or frame_number < 0):
        raise ValueError("A nonnegative --frame applies to PNG output")
    ffmpeg = shutil.which("ffmpeg") if extension == ".mp4" else None
    if extension == ".mp4" and ffmpeg is None:
        raise ValueError("MP4 output requires ffmpeg with libx264")
    output.parent.mkdir(parents=True, exist_ok=True)
    source = replay_frames(data, law)
    with TemporaryDirectory(prefix=".feeder-replay-", dir=output.parent) as work:
        scratch = Path(work)
        staged = scratch / f"replay{extension}"
        if extension == ".mp4":
            MEDIA.make_video(source, ffmpeg, scratch, staged)
        elif extension == ".gif":
            images, durations = [], []
            for image, duration in source:
                images.append(image.quantize(colors=128))
                durations.append(duration)
            images[0].save(staged, save_all=True, append_images=images[1:],
                           duration=durations, loop=0, optimize=True)
        else:
            for index, (image, _) in enumerate(source):
                if index == frame_number:
                    break
            else:
                if frame_number is not None:
                    raise ValueError("Requested frame is outside the replay")
            image.save(staged)
        staged.replace(output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Saved decisive replay JSON")
    parser.add_argument("output", type=Path, help="Replay output as GIF, MP4 or PNG")
    parser.add_argument("--law", choices=("both", *LAWS), default="both")
    parser.add_argument("--frame", type=int, help="Zero-based frame to export as PNG")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
        print(render_replay(data, args.output, law=args.law, frame_number=args.frame))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
