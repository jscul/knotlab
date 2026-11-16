"""Audit local cursor moves with the frozen WIRED-FOLD checkpoint."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
TICKET = "STRAND-RETURN-20261114-001"
WIRED = "WIRED-FOLD-20261114-001"
POLICY_DIR = ROOT / "artifacts" / WIRED / (WIRED + "-E001_frozen_policy")
LENGTHS = (2, 3, 4, 6, 8)
NAMES = "ABCD"
MENUS = tuple(product((1, 2, 3), repeat=2))
SCHEDULES = {"serial_one": (1, False), "alternating_one": (1, True),
             "alternating_two": (2, True)}


def encode_set(values):
    return sum(1 << value for value in set(values))


def assigned_values(signs, unary):
    """Full-assignment oracle on the original cyclic constraints."""
    length = len(signs)
    midpoint = length // 2
    possible = set()
    for assignment in product((0, 1), repeat=length):
        if not unary & (1 << assignment[midpoint]):
            continue
        if all((assignment[i] ^ assignment[(i + 1) % length]) == sign
               for i, sign in enumerate(signs)):
            possible.add(assignment[0])
    return encode_set(possible)


class Cursor:
    def __init__(self, strand):
        self.signs, self.unary = strand
        self.position = 0
        self.possible = {(0, 0), (1, 1)}
        self.work = Counter(moves=0, link_reads=0, unary_reads=0)

    def advance(self, span, blind=False):
        start = self.position
        stop = min(start + span, len(self.signs))
        if stop == start:
            raise ValueError("completed cursor")
        self.work["moves"] += 1
        for index in range(start, stop):
            if blind and stop - start == 2 and index == start:
                sign = 0
            else:
                sign = self.signs[index]
                self.work["link_reads"] += 1
            self.possible = {(h, current ^ sign) for h, current in self.possible}
            if index + 1 == len(self.signs) // 2:
                self.work["unary_reads"] += 1
                self.possible = {(h, current) for h, current in self.possible
                                 if self.unary & (1 << current)}
        self.position = stop

    @property
    def done(self):
        return self.position == len(self.signs)

    def allowed(self):
        if not self.done:
            raise ValueError("finish the return before reading")
        return encode_set(h for h, current in self.possible if h == current)


def schedule(strands, names, span, alternate, blind=False):
    cursors = {name: Cursor(strands[name]) for name in names}
    order = []
    while any(not cursor.done for cursor in cursors.values()):
        for name, cursor in cursors.items():
            while not cursor.done:
                cursor.advance(span, blind)
                order.append(name)
                if alternate:
                    break
    work = Counter()
    for cursor in cursors.values():
        work.update(cursor.work)
    return {name: cursor.allowed() for name, cursor in cursors.items()}, work, order


def single_strands():
    by_length = {}
    blind_witness = None
    for length in LENGTHS:
        cells = Counter()
        costs = {}
        for signs in product((0, 1), repeat=length):
            for unary in range(4):
                expected = assigned_values(signs, unary)
                strand = {"a": (signs, unary)}
                cells["cases"] += 1
                for label, span, blind in (("one", 1, False), ("two", 2, False),
                                            ("blind", 2, True)):
                    actual, work, _ = schedule(strand, ["a"], span, False, blind)
                    cells[label + "_correct"] += actual["a"] == expected
                    costs[label] = dict(work)
                if blind_witness is None and signs[0] and expected != actual["a"] and unary == 3:
                    paired = (0,) + signs[1:]
                    other = assigned_values(paired, unary)
                    other_blind, _, _ = schedule({"a": (paired, unary)}, ["a"], 2, False, True)
                    if other != expected and other_blind == actual:
                        blind_witness = {"sign_words": [list(paired), list(signs)], "unary": unary,
                                         "oracle_masks": [other, expected],
                                         "blind_masks": [other_blind["a"], actual["a"]]}
        by_length[str(length)] = {"tally": cells, "per_loop_work": costs}
    return {"lengths": by_length, "blind_witness": blind_witness}


def word_representatives():
    """Generate four explicit eight-link fixtures; the agent receives raw strands."""
    words = [(1, 0, 0, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0, 0, 1),
             (0, 0, 0, 0, 0, 0, 0, 0), (1, 0, 0, 0, 1, 0, 0, 0)]
    return list(zip(words, (3, 2, 2, 3)))


def gate(checkpoint, name, *inputs):
    address = sum(int(bit) << index for index, bit in enumerate(inputs))
    return (checkpoint[name]["truth_mask"] >> address) & 1


def demands(checkpoint, inlets):
    """Test data dependence of the learned gate at these two name comparisons."""
    needed = []
    for name in NAMES:
        flags = (name == inlets[0], name == inlets[1])
        if any(gate(checkpoint, "T", state, 0, *flags)
               != gate(checkpoint, "T", state, 1, *flags) for state in (0, 1)):
            needed.append(name)
    return needed


def sender_state(checkpoint, memberships, inlets):
    states = [checkpoint["initial_bit"]] * 2
    for name in NAMES:
        mask = memberships.get(name, 0)
        match = (name == inlets[0], name == inlets[1])
        states = [gate(checkpoint, "T", old, (mask >> h) & 1, *match)
                  for h, old in enumerate(states)]
    return tuple(states)


def packet_width(checkpoint, menu):
    first, second = menu
    return 1 + gate(checkpoint, "W", first & 1, first >> 1, second & 1, second >> 1)


def make_packet(checkpoint, states, menu, width):
    if width == 2:
        return states
    first = menu[0]
    return (gate(checkpoint, "F", *states, first & 1, first >> 1),)


def decode(checkpoint, packet, mask):
    table = checkpoint["decoders"]["one" if len(packet) == 1 else "two"][str(mask)]
    code = sum(bit << index for index, bit in enumerate(packet))
    return table[code]


def steering(checkpoint):
    representatives = word_representatives()
    oracle = [assigned_values(*strand) for strand in representatives]
    if oracle != list(range(4)):
        raise ValueError("fixture coverage failed")
    inlets_panel = tuple(permutations(NAMES, 2))
    widths = {menu: packet_width(checkpoint, menu) for menu in MENUS}
    needed = {inlets: demands(checkpoint, inlets) for inlets in inlets_panel}
    summary = {label: Counter() for label in SCHEDULES}
    first_rewire = None
    for world in product(range(4), repeat=len(NAMES)):
        masks = dict(zip(NAMES, world))
        strands = {name: representatives[mask] for name, mask in masks.items()}
        by_inlets = {}
        for inlets in inlets_panel:
            direct = sender_state(checkpoint, masks, inlets)
            true_common = masks[inlets[0]] & masks[inlets[1]]
            for label, (span, alternate) in SCHEDULES.items():
                visited, work, visit_order = schedule(strands, needed[inlets], span, alternate)
                totals = summary[label]
                totals.update(work)
                totals["world_wirings"] += 1
                totals["cursors_opened"] += len(visited)
                totals["exactly_wired_names"] += set(visited) == set(inlets)
                via_cursors = sender_state(checkpoint, visited, inlets)
                totals["same_state_as_direct"] += via_cursors == direct
                for menu in MENUS:
                    packet = make_packet(checkpoint, via_cursors, menu, widths[menu])
                    totals["packets_of_" + str(len(packet)) + "_bit"] += 1
                    totals["payload_bits"] += len(packet)
                    for mask in menu:
                        answer = decode(checkpoint, packet, mask)
                        totals["queries"] += 1
                        totals["correct"] += answer == bool(true_common & mask)
                    if first_rewire is None and label == "alternating_one" and menu == (1, 1):
                        by_inlets[inlets] = {"inlets": "".join(inlets), "cursors": list(visited),
                                             "actions": "".join(visit_order), "packet": packet,
                                             "answer": decode(checkpoint, packet, 1),
                                             "oracle": int(bool(true_common & 1))}
        if first_rewire is None:
            for a, b in permutations(by_inlets, 2):
                left, right = by_inlets[a], by_inlets[b]
                if (left["oracle"] != right["oracle"] and left["answer"] == left["oracle"]
                        and right["answer"] == right["oracle"] and set(a).isdisjoint(b)):
                    first_rewire = {"source_masks": masks, "menu": [1, 1], "sockets": [left, right]}
                    break
    return {"per_schedule": summary, "first_changed_answer_disjoint_rewire": first_rewire,
            "sources_demanded": {"".join(key): value for key, value in needed.items()},
            "length": 8, "source_masks_verified_by_assignments": oracle,
            "representatives": representatives}


def run(case_id, payload):
    raw = json.loads((POLICY_DIR / "checkpoint.json").read_text())
    digest = sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    listed = json.loads((POLICY_DIR / "result.json").read_text())["checkpoint_sha256"]
    if digest != listed:
        raise ValueError("frozen dependency checkpoint changed")
    junctions = runpy.run_path(str(ROOT / "research" / TICKET / "junctions.py"))
    return {"checkpoint_sha256": digest, "single_strands": single_strands(),
            "steering": steering(raw), "junctions": junctions["verify"]()}


def cases():
    yield "closed-strands", {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(run("closed-strands", {}), indent=2, sort_keys=True))
