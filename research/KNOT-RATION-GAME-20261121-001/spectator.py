"""Render a saved Knot Ration episode without running its policy or growth law."""

from __future__ import annotations

import argparse
from collections import defaultdict
from functools import lru_cache
from itertools import combinations
import json
from math import hypot, sqrt
from pathlib import Path
from random import Random
import shutil
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1200, 680
BG = "#111721"
PANEL = "#192331"
INSET = "#222f41"
STROKE = "#3d5067"
INK = "#f4f7fa"
SECONDARY = "#b4c4d7"
MOVE = "#86def7"
GROWTH = "#b9eca2"
RATION = "#ffd08c"
DEATH = "#ffb1ad"
LINK = "#617891"
MAX_DRAWN_KNOTS = 24


@lru_cache(maxsize=None)
def font(size: int, bold: bool = False):
    names = ("Inter-Bold.otf", "DejaVuSans-Bold.ttf") if bold else (
        "Inter-Regular.otf", "DejaVuSans.ttf"
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def identities(names, prefix: str) -> str:
    """Display the exact IDs, abbreviating runs of consecutive integers."""
    values = sorted(set(names))
    if not values:
        return "—"
    runs = [[values[0]]]
    for value in values[1:]:
        if value == runs[-1][-1] + 1:
            runs[-1].append(value)
        else:
            runs.append([value])
    labels = []
    for run in runs:
        if len(run) < 3:
            labels.extend(f"{prefix}{value}" for value in run)
        else:
            labels.append(f"{prefix}{run[0]}–{prefix}{run[-1]}")
    return ", ".join(labels)


def shared_links(owners):
    return [(name, *holders) for name, holders in sorted(owners.items()) if len(holders) == 2]


def spread_knots(holders, pairs, links, seed):
    """Compute drawing positions using repulsion and pull between linked holders."""
    rng = Random(seed)
    left, top, right, bottom = 81, 229, 688, 448
    spacing = 0.9 * sqrt((right - left) * (bottom - top) / len(holders))
    positions = {h: (rng.uniform(left, right), rng.uniform(top, bottom)) for h in holders}
    for iteration in range(130):
        force = {h: [0.0, 0.0] for h in holders}
        for a, b in pairs:
            dx, dy = (positions[a][axis] - positions[b][axis] for axis in (0, 1))
            scale = (spacing / max(1, hypot(dx, dy))) ** 2
            force[a][0] += dx * scale
            force[a][1] += dy * scale
            force[b][0] -= dx * scale
            force[b][1] -= dy * scale
        for _, a, b in links:
            dx, dy = (positions[a][axis] - positions[b][axis] for axis in (0, 1))
            scale = hypot(dx, dy) / spacing
            force[a][0] -= dx * scale
            force[a][1] -= dy * scale
            force[b][0] += dx * scale
            force[b][1] += dy * scale
        step = 18 * (1 - iteration / 131)
        for holder, (x, y) in positions.items():
            dx, dy = force[holder]
            scale = min(1, step / max(0.01, hypot(dx, dy)))
            positions[holder] = (max(left, min(right, x + dx * scale)),
                                 max(top, min(bottom, y + dy * scale)))
    return positions


def layout_penalty(positions, pairs, links):
    """Prefer clear nodes and few visual crossings in the spectator drawing."""
    def cross(a, b, c):
        x, y = positions[a]
        bx, by = positions[b]
        cx, cy = positions[c]
        return (bx - x) * (cy - y) - (by - y) * (cx - x)

    penalty = 0
    for (_, a, b), (_, c, d) in combinations(links, 2):
        if len({a, b, c, d}) == 4 and cross(a, b, c) * cross(a, b, d) < 0 and cross(c, d, a) * cross(c, d, b) < 0:
            penalty += 20
    for _, a, b in links:
        x, y = positions[a]
        bx, by = positions[b]
        dx, dy = bx - x, by - y
        length = max(1, hypot(dx, dy))
        for holder, (hx, hy) in positions.items():
            along = ((hx - x) * dx + (hy - y) * dy) / length ** 2
            if 0.04 < along < 0.96:
                penalty += 3 * max(0, 29 - abs(cross(a, b, holder)) / length)
    for a, b in pairs:
        dx, dy = (positions[a][axis] - positions[b][axis] for axis in (0, 1))
        penalty += 5 * max(0, 50 - hypot(dx, dy))
    return penalty


def distinction_labels(positions, links):
    """Place distinguishable IDs near their own drawn connections."""
    labels = {}
    occupied = []
    for name, left, right in links:
        ax, ay = positions[left]
        bx, by = positions[right]
        dx, dy = bx - ax, by - ay
        length = max(1, hypot(dx, dy))
        normal_x, normal_y = -dy / length, dx / length
        half_width = 3.7 * len(f"d{name}") + 3
        for fraction, side in ((0.5, -1), (0.5, 1), (0.35, -1), (0.65, 1),
                               (0.65, -1), (0.35, 1), (0.44, 1), (0.56, -1)):
            x = ax + fraction * dx + side * 11 * normal_x
            y = ay + fraction * dy + side * 11 * normal_y
            if not (65 + half_width < x < 709 - half_width and 211 < y < 463):
                continue
            if any(hypot(max(0, abs(x - hx) - half_width), max(0, abs(y - hy) - 8)) < 24
                   for hx, hy in positions.values()):
                continue
            if any(abs(x - cx) < half_width + width + 3 and abs(y - cy) < 17
                   for cx, cy, width in occupied):
                continue
            labels[name] = x, y, half_width
            occupied.append((x, y, half_width))
            break
    return labels


def world_layout(replay):
    """Fix one spectator layout for all the holdings reached in the episode."""
    final = dict(enumerate(replay["initial_holdings"]))
    for event in replay["events"]:
        if event["growth"]:
            for birth in event["growth"]["births"]:
                final[birth["holder"]] = birth["holdings"]
    if not 1 <= len(final) <= MAX_DRAWN_KNOTS:
        return None
    owners = defaultdict(list)
    for holder, names in final.items():
        for name in names:
            owners[name].append(holder)
    if any(len(holders) > 2 for holders in owners.values()):
        return None
    links = shared_links(owners)
    pairs = list(combinations(final, 2))
    positions = min((spread_knots(final, pairs, links, seed) for seed in range(10)),
                    key=lambda chart: layout_penalty(chart, pairs, links))
    return positions, distinction_labels(positions, links)


class ReplayFrame:
    def __init__(self, replay, event):
        self.replay = replay
        self.event = event
        self.image = Image.new("RGB", (WIDTH, HEIGHT), BG)
        self.draw = ImageDraw.Draw(self.image)

    def label(self, x, y, value, size, color=INK, bold=False, anchor="lt"):
        self.draw.text((x, y), str(value), font=font(size, bold), fill=color, anchor=anchor)

    def box(self, bounds, fill, outline=None, radius=14, width=1):
        self.draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)

    def wrapped(self, x, y, text, width, size, color=INK, lines=2):
        face = font(size)
        wrapped = [""]
        for word in text.split():
            candidate = f"{wrapped[-1]} {word}".strip()
            if wrapped[-1] and self.draw.textlength(candidate, font=face) > width:
                wrapped.append(word)
            else:
                wrapped[-1] = candidate
        if len(wrapped) > lines:
            visible = wrapped[lines - 1].rstrip(",")
            while self.draw.textlength(f"{visible} …", font=face) > width:
                visible = visible.rsplit(" ", 1)[0] if " " in visible else visible[:-1]
            wrapped = [*wrapped[:lines - 1], f"{visible} …"]
        for i, line in enumerate(wrapped):
            self.label(x, y + i * (size + 7), line, size, color)

    def heading(self):
        self.box((36, 34, 44, 96), MOVE, radius=4)
        self.label(61, 32, "Knot Ration", 45, bold=True)
        self.label(63, 86, "Spectator replay", 19, SECONDARY)
        law = {"parity": "Parity", "nae": "Not-all-equal"}[self.replay["law"]]
        policy = self.replay["policy"].replace("_", " ").replace("-", " ")
        self.label(1164, 39, law, 28, bold=True, anchor="rt")
        self.label(1164, 81, f"{policy}  ·  seed {self.replay['seed']}  ·  tape {self.replay['tape']}",
                   17, SECONDARY, anchor="rt")

    def knot(self, x, holder, holding, phase, ration, current=False):
        color = MOVE if current else STROKE
        self.box((x, 214, x + 182, 349), INSET, color, width=2)
        self.label(x + 16, 229, phase, 15, SECONDARY, bold=True)
        self.label(x + 15, 254, f"K{holder}", 44, bold=True)
        self.wrapped(x + 16, 309, identities(holding, "d"), 149, 14, SECONDARY)
        ration_text, ration_color = ration
        self.label(x + 91, 361, ration_text, 16, ration_color, anchor="mt")

    def incidence(self, holdings, owners, available, depleted, layout):
        self.box((36, 123, 735, 607), PANEL)
        self.label(59, 145, "Knot incidence", 25, bold=True)
        subtitle = "Spectator drawing" if layout else "Local spectator drawing"
        self.label(60, 179, subtitle, 16, SECONDARY)
        self.label(711, 150, f"{len(holdings)} knots  ·  {len(available)} rations",
                   18, SECONDARY, anchor="rt")

        start = self.replay["start_holder"]
        before = self.event["holder_before"] if self.event else start
        after = self.event["holder_after"] if self.event else start
        if layout:
            self.world_incidence(holdings, owners, available, depleted, layout, before, after)
        else:
            self.local_incidence(holdings, owners, available, depleted, before, after)
        self.draw.line((59, 493, 710, 493), fill=STROKE)
        self.growth(holdings)

    def ring(self, x, y, radius, color, fill=None, width=2):
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                          fill=fill, outline=color, width=width)

    def diamond(self, x, y, filled, radius=5):
        bounds = ((x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y))
        self.draw.polygon(bounds, fill=RATION if filled else PANEL, outline=RATION)

    def world_incidence(self, holdings, owners, available, depleted, layout, before, after):
        positions, mark_labels = layout
        growth = self.event["growth"] if self.event else None
        newborn = {birth["holder"] for birth in growth["births"]} if growth else set()
        used = self.event["distinction"] if before != after else None
        heading = f"K{before} → K{after} via d{used}" if used is not None else f"Bot at K{after}"
        self.label(710, 176, heading, 19, MOVE, bold=True, anchor="rt")

        links = shared_links(owners)
        for name, a, b in links:
            color = "#82a180" if a in newborn or b in newborn else LINK
            self.draw.line((positions[a], positions[b]), fill=color, width=2)
        if used is not None:
            self.move_arrow(positions[before], positions[after])

        for name, _, _ in links:
            if name not in mark_labels:
                continue
            x, y, half_width = mark_labels[name]
            active = name == used
            self.box((x - half_width, y - 8, x + half_width, y + 8), MOVE if active else PANEL,
                     radius=4)
            self.label(x, y, f"d{name}", 13, BG if active else SECONDARY, bold=active, anchor="mm")

        for holder in holdings:
            x, y = positions[holder]
            if holder == after:
                self.ring(x, y, 25, MOVE, width=3)
            rim = GROWTH if holder in newborn else LINK
            self.ring(x, y, 20, rim, fill=INSET, width=3 if holder in newborn else 2)
            self.label(x, y, f"K{holder}", 16, INK, bold=True, anchor="mm")
            if holder in available or holder in depleted:
                self.diamond(x + 17, y - 13, holder in available, radius=6)

        self.ring(66, 478, 6, MOVE)
        self.label(78, 471, "Bot", 15, SECONDARY)
        self.ring(151, 478, 6, GROWTH)
        self.label(163, 471, "New knot", 15, SECONDARY)
        self.diamond(280, 478, True)
        self.label(292, 471, "Ration", 15, SECONDARY)
        self.diamond(383, 478, False)
        self.label(395, 471, "Depleted ration", 15, SECONDARY)

    def move_arrow(self, origin, target):
        self.draw.line((origin, target), fill=PANEL, width=8)
        self.draw.line((origin, target), fill=MOVE, width=4)
        dx, dy = target[0] - origin[0], target[1] - origin[1]
        distance = max(1, hypot(dx, dy))
        tx, ty = dx / distance, dy / distance
        tip = target[0] - 26 * tx, target[1] - 26 * ty
        x, y = tip[0] - 9 * tx, tip[1] - 9 * ty
        self.draw.polygon((tip, (x - 5 * ty, y + 5 * tx), (x + 5 * ty, y - 5 * tx)), fill=MOVE)

    def local_incidence(self, holdings, owners, available, depleted, before, after):
        def ration_at(holder):
            if holder in available:
                return "Ration available", RATION
            if holder in depleted:
                return "Ration depleted", RATION
            return "No ration", SECONDARY

        if before == after:
            self.knot(294, after, holdings[after], "CURRENT KNOT", ration_at(after), current=True)
        else:
            self.knot(64, before, holdings[before], "BEFORE MOVE", ration_at(before))
            self.knot(522, after, holdings[after], "AFTER MOVE", ration_at(after), current=True)
            self.draw.line((246, 279, 519, 279), fill=MOVE, width=3)
            self.draw.polygon(((505, 271), (520, 279), (505, 287)), fill=MOVE)
            used = self.event["distinction"]
            self.box((306, 251, 465, 306), BG, MOVE, radius=10)
            self.label(385, 265, f"d{used}", 27, MOVE, bold=True, anchor="mt")
            self.label(385, 316, "Shared distinction", 16, MOVE, anchor="mt")

        local = []
        for name in sorted(holdings[after]):
            other_holders = set(owners[name]) - {after}
            if other_holders:
                local.append(f"d{name} with {identities(other_holders, 'K')}")
        self.draw.line((59, 394, 710, 394), fill=STROKE)
        self.label(60, 409, f"Shared with K{after}", 17, bold=True)
        self.wrapped(60, 437, "  /  ".join(local) if local else "No shared distinctions",
                     645, 17, SECONDARY, lines=2)

    def growth(self, holdings):
        self.label(60, 510, "Growth", 17, bold=True)
        growth = self.event["growth"] if self.event else None
        if not self.event:
            self.label(60, 541, f"Founders  {identities(holdings, 'K')}", 24, SECONDARY)
            return
        if growth is None:
            self.label(60, 541, "No attempt this turn", 22, SECONDARY)
            return

        self.label(709, 511, f"Formation {growth['formation']}", 17, SECONDARY, anchor="rt")
        births = [birth["holder"] for birth in growth["births"]]
        if not births:
            text = "Growth stalled" if growth["status"] == "stall" else "Growth closed"
            self.label(60, 537, f"{text}  ·  no knots formed", 22, SECONDARY)
            shortages = growth.get("shortages", [])
            if shortages:
                text = ", ".join(f"K{holder} needs {unpaid} more" for holder, unpaid in shortages)
                self.wrapped(60, 570, text, 642, 17, SECONDARY, lines=1)
            return

        name = "knot" if len(births) == 1 else "knots"
        ration_word = "ration" if len(births) == 1 else "rations"
        self.label(60, 537, f"+{len(births)} {name} formed  ·  {len(births)} {ration_word} added",
                   22, GROWTH, bold=True)
        self.wrapped(60, 570, identities(births, "K"), 642, 18, INK, lines=1)

    def player(self):
        self.box((751, 123, 1164, 607), PANEL)
        self.label(775, 149, "Player observation", 24, bold=True)
        sensor = self.event["food_sensor"] if self.event else None
        if not self.event:
            observation, subtitle = "Ready", "First observation comes on turn 1"
        elif sensor is None:
            observation, subtitle = "Blind to rations", "Ration reading unavailable"
        elif sensor:
            observation, subtitle = "Ration sensed", "Reading before the action"
        else:
            observation, subtitle = "No ration sensed", "Reading before the action"
        slots = self.event.get("available_slots") if self.event else None
        if slots is not None:
            port_word = "port" if slots == 1 else "ports"
            subtitle = f"Before the action  ·  {slots} anonymous {port_word}"
        self.label(775, 190, observation, 28, RATION if sensor else INK, bold=True)
        self.label(776, 228, subtitle, 17, SECONDARY)

        self.draw.line((775, 257, 1140, 257), fill=STROKE)
        self.label(775, 274, "Chosen action", 18, bold=True)
        if not self.event:
            action = "—"
        elif self.event["action"] == "eat":
            action = f"Eat at K{self.event['holder_before']}"
        else:
            action = f"Move via port {self.event['slot']}"
        self.label(775, 307, action, 27, MOVE, bold=True)

        self.draw.line((775, 346, 1140, 346), fill=STROKE)
        self.label(775, 363, "Energy", 18, bold=True)
        self.energy()

        self.draw.line((775, 480, 1140, 480), fill=STROKE)
        self.result()

    def energy(self):
        before = self.event["energy_before"] if self.event else self.replay["initial_energy"]
        after = self.event["energy_after"] if self.event else before
        maximum = self.replay["max_energy"]
        displayed = f"{before}  →  {after}" if self.event else str(before)
        color = DEATH if after <= 0 else RATION if after > before else MOVE
        self.label(775, 393, displayed, 42, color, bold=True)
        self.label(1139, 410, f"Maximum {maximum}", 17, SECONDARY, anchor="rt")
        self.box((775, 452, 1140, 461), STROKE, radius=4)
        if after > 0:
            self.box((775, 452, 775 + round(365 * after / maximum), 461), color, radius=4)
        prior = 775 + min(365, round(365 * before / maximum))
        if self.event:
            self.draw.line((prior, 448, prior, 466), fill=INK, width=2)

    def result(self):
        self.label(775, 496, "Ration", 18, bold=True)
        if not self.event:
            ration = "Each new knot is given a ration"
        elif self.event["consumed"]:
            ration = f"Depleted at K{self.event['holder_after']}  ·  +{self.replay['ration_gain']} energy"
        elif self.event["action"] == "eat":
            ration = "No ration available"
        else:
            ration = "No ration collected"
        gained = self.event and self.event["consumed"]
        self.label(775, 524, ration, 19, RATION if gained else SECONDARY)
        if gained:
            cost = "Turn cost −1"
            capped = self.event.get("wasted", 0)
            if capped:
                cost += f"  ·  Cap −{capped}"
            self.label(775, 554, cost, 16, SECONDARY)
        if self.event and self.event["terminal"]:
            reason = self.replay["reason"]
            label = {"death": "Died", "horizon": "Survived to the horizon"}.get(reason, reason)
            self.label(775, 566, f"{label}  ·  turn {self.event['turn']}",
                       23, DEATH if reason == "death" else GROWTH, bold=True)

    def timeline(self, history):
        turn = self.event["turn"] if self.event else 0
        total = self.replay["turns"]
        self.label(37, 632, f"Game turn {turn} / {total}", 21, bold=True)
        left, right = 257, 1155
        self.box((left, 642, right, 649), STROKE, radius=4)
        progress = left + round((right - left) * turn / max(total, 1))
        if progress > left:
            self.box((left, 642, progress, 649), MOVE, radius=4)
        for prior in history:
            growth = prior["growth"]
            if not (prior["consumed"] or (growth and growth["births"])):
                continue
            x = left + round((right - left) * prior["turn"] / max(total, 1))
            color = RATION if prior["consumed"] else GROWTH
            self.draw.line((x, 637, x, 654), fill=color, width=3)
        color = DEATH if self.event and self.event["terminal"] and self.replay["reason"] == "death" else INK
        self.draw.ellipse((progress - 5, 640, progress + 5, 650), fill=color)

    def draw_frame(self, holdings, owners, available, depleted, history, layout):
        self.heading()
        self.incidence(holdings, owners, available, depleted, layout)
        self.player()
        self.timeline(history)
        return self.image


def frames(replay, turn=None):
    """Draw the initial state and every event, in recorded game order."""
    if replay["schema_version"] != 1:
        raise ValueError(f"Unsupported replay schema {replay['schema_version']}")
    if len(replay["events"]) != replay["turns"]:
        raise ValueError("A complete render requires one recorded event per game turn")
    layout = world_layout(replay)
    holdings = dict(enumerate(replay["initial_holdings"]))
    owners = defaultdict(list)
    for holder, names in holdings.items():
        for name in names:
            owners[name].append(holder)
    available, depleted = set(), set()
    history = []
    if turn in (None, 0):
        yield ReplayFrame(replay, None).draw_frame(holdings, owners, available, depleted, history, layout), 1200
    ordinary_ms = min(860, max(220, 15_000 // max(replay["turns"], 1)))
    for event in replay["events"]:
        growth = event["growth"]
        if growth:
            for birth in growth["births"]:
                holder = birth["holder"]
                holdings[holder] = birth["holdings"]
                available.add(holder)
                for name in birth["holdings"]:
                    owners[name].append(holder)
        if event["consumed"]:
            holder = event["holder_after"]
            available.remove(holder)
            depleted.add(holder)
        history.append(event)
        if turn not in (None, event["turn"]):
            continue
        hold_ms = max(ordinary_ms, 1200) if growth or event["consumed"] else ordinary_ms
        if event["terminal"]:
            hold_ms = 2450
        yield ReplayFrame(replay, event).draw_frame(holdings, owners, available, depleted, history, layout), hold_ms


def make_video(frame_source, ffmpeg, scratch, output):
    manifest = ["ffconcat version 1.0"]
    total_ms = 0
    for index, (image, duration) in enumerate(frame_source):
        name = f"frame-{index:05d}.png"
        image.save(scratch / name)
        manifest.extend((f"file {name}", f"duration {duration / 1000:.3f}"))
        total_ms += duration
    manifest.append(f"file {name}")  # Give the final still its declared duration.
    (scratch / "frames.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "concat", "-i", "frames.txt",
         "-vf", "fps=10", "-an", "-c:v", "libx264", "-threads", "2", "-crf", "18",
         "-pix_fmt", "yuv420p", "-g", "10", "-t", f"{total_ms / 1000:.3f}",
         "-movflags", "+faststart", str(output)],
        cwd=scratch, check=True,
    )


def render_replay(replay, output_path, *, turn=None) -> Path:
    """Save the complete GIF or MP4, or one PNG (the final turn by default)."""
    output = Path(output_path).expanduser().resolve()
    extension = output.suffix.lower()
    if extension not in {".png", ".gif", ".mp4"}:
        raise ValueError("Replay output must end in .png, .gif, or .mp4")
    if turn is not None and (extension != ".png" or not 0 <= turn <= replay["turns"]):
        raise ValueError("A single turn is available for PNG output and must be within the replay")
    ffmpeg = shutil.which("ffmpeg") if extension == ".mp4" else None
    if extension == ".mp4" and ffmpeg is None:
        raise ValueError("MP4 replay output requires ffmpeg with libx264")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".replay-", dir=output.parent) as directory:
        scratch = Path(directory)
        staged = scratch / f"replay{extension}"
        if extension == ".png":
            selected = replay["turns"] if turn is None else turn
            image, _ = next(frames(replay, selected))
            image.save(staged)
        elif extension == ".mp4":
            make_video(frames(replay), ffmpeg, scratch, staged)
        else:
            images, durations = [], []
            for image, duration in frames(replay):
                images.append(image.quantize(colors=128))
                durations.append(duration)
            images[0].save(staged, save_all=True, append_images=images[1:],
                           duration=durations, loop=0, optimize=True)
        staged.replace(output)
    return output


def main():
    parser = argparse.ArgumentParser(description="Draw an already recorded Knot Ration game.")
    parser.add_argument("replay", type=Path, help="path to the game’s replay JSON")
    parser.add_argument("output", type=Path, help=".gif, .mp4, or .png output path")
    parser.add_argument("--turn", type=int, help="turn to show in a PNG, with 0 for the start")
    args = parser.parse_args()
    try:
        replay = json.loads(args.replay.read_text(encoding="utf-8"))
        print(render_replay(replay, args.output, turn=args.turn))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
