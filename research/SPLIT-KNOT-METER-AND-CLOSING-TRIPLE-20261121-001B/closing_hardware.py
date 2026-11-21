"""Replay the two physical closing-knot receivers and their ordinary messages."""

import argparse
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / "research/TWO-READERS-ONE-SURVIVING-SIGN-20261121-001A/instrument_hardware.py"
LAWS = ("parity", "nae")
LABS = ("A", "B")
SLOTS = ("X", "Z")
Q = 9
LOCAL = (0, 1)
REMOTE = (2, 3)
LOCAL_OK = (4, 5)
REMOTE_OK = (6, 7)
SIGN = (8, 10, 11)
COMPLETE = 12
CARRIER_BIT, CARRIER_PRESENT = 0, 1
STAGES = tuple(product((False, True), repeat=2))
BITS = tuple(product((0, 1), repeat=4))
READY_KEEPER = ("110", 1)
KEEPER = (("101", 0), ("011", 1))


@cache
def _earlier():
    spec = spec_from_file_location("b295_one_sign_hardware", PRIOR)
    inherited = module_from_spec(spec)
    sys.modules[spec.name] = inherited
    spec.loader.exec_module(inherited)
    return inherited, inherited._prior(), inherited._prior()._routes()


def _bank(lab):
    return lab + "_receiver"


def _mate(lab):
    return "B" if lab == "A" else "A"


def _channel(lab):
    return lab + "_to_" + _mate(lab)


@cache
def _ready(reverse):
    return _earlier()[2].encode(0, reverse=reverse)


@cache
def _failures(word, reverse):
    routes = _earlier()[2]
    return tuple(tuple(routes._failed_physical(word, law, reverse)) for law in LAWS)


@cache
def _holding_H_mask(reverse):
    routes = _earlier()[2]
    return routes.mask(routes._holding("H", reverse))


@cache
def _port_record(value, reverse):
    old = _earlier()[1]
    label = None if value is None else "ab"[value] if value in (0, 1) else value
    row = old._bench_port_word(label, reverse)
    final = row["final"]["bench_port"]
    assert old._routes().decode(final, reverse=reverse)["keeper"] == "110"
    return final, row


def _port_roles():
    old = _earlier()[1]
    return old.ADDRESS_RECORD[0], old.ADDRESS_RECORD[1], old.MEASURED_RECEIPT


def _port_guard(name, bit=None):
    admitted, answer, receipt = _port_roles()
    common = ((name, admitted, 1), (name, receipt, 0))
    return common if bit is None else (*common, (name, answer, bit))


def _code_controls(bit):
    routes = _earlier()[2]
    return ((routes.A, 1 - bit), (routes.C, 1), (routes.Z, bit))


def _other_word(initial, reverse, *, positions=(), keeper=None, z=None):
    routes = _earlier()[2]
    values = [routes._register(initial, i, reverse) for i in range(13)]
    prior_decode = routes.decode(initial, reverse=reverse)
    for i, bit in positions:
        values[i] = bit
    f = {"keeper": keeper if keeper is not None else prior_decode["keeper"],
         "z": z if z is not None else prior_decode["z"], "h": prior_decode["h"], "reverse": reverse}
    return routes.encode(sum(values[i] << i for i in range(9)),
                         **dict(zip(("q", "t", "l", "s"), values[9:], strict=True)), **f)


class Circuit:
    def __init__(self, words, encodings):
        self.initial = dict(words)
        self.words = dict(words)
        self.reverse = dict(encodings)
        self.actions = []
        self.history = []

    def read(self, bank, register):
        return _earlier()[2]._register(self.words[bank], register, self.reverse[bank])

    def keeper(self, bank):
        decoded = _earlier()[2].decode(self.words[bank], reverse=self.reverse[bank])
        return decoded["keeper"], decoded["z"]

    def visible_ready_keeper(self, bank):
        routes = _earlier()[2]
        word, rev = self.words[bank], self.reverse[bank]
        marks = ((routes.A, 1), (routes.C, 0), (routes.Z, 1))
        return all(routes.bit(word, routes._transport(mark, rev)) == value for mark, value in marks)

    def ready(self, bank):
        return self.read(bank, Q) == 0 and self.visible_ready_keeper(bank)

    def has_port(self, name):
        return all(self.read(src, reg) == value for src, reg, value in _port_guard(name))

    def port(self, name):
        return self.read(name, _port_roles()[1]) if self.has_port(name) else None

    def exchange(self, bank, register, label, *, local=(), raw=(), external=(), offered=True, classical=False):
        self._apply(("exchange", label, bank, register, tuple(local), tuple(raw), tuple(external), bool(offered), classical))

    def writer(self, bank, stage, offered=True):
        self._apply(("writer", f"keeper stage {stage}", bank, stage, (), (), (), bool(offered), False))

    def write(self, bank, stages, *, reverse_order=False):
        order = (2, 1) if reverse_order else (1, 2)
        for stage in order:
            self.writer(bank, stage, stages[stage - 1])

    def _apply(self, spec, *, invert=False, forced_disconnect=False):
        routes = _earlier()[2]
        kind, label, bank, target, local, raw, external, offered, classical = spec
        rev, before = self.reverse[bank], self.words[bank]
        offered = offered and not forced_disconnect
        local_marks = tuple(routes._guard(i, rev, want) for i, want in local)
        local_marks += tuple((routes._transport(mark, rev), want) for mark, want in raw)
        checks = [(bank, mark, want, routes.bit(before, mark)) for mark, want in local_marks]
        transported = []
        for source, register, want in external:
            mark, _ = routes._guard(register, self.reverse[source], want)
            assert mark in routes._holding("H", self.reverse[source])
            same_lab = source[:1] == bank[:1] and "_to_" not in source + bank
            assert same_lab or classical, (bank, source, label)
            transported.append((source, mark, want, self.read(source, register)))
        connected = offered and all(got == want for _, _, want, got in transported)
        if kind == "exchange":
            pair = routes._places(routes.REGISTERS[target][:2], rev)
            assert routes._exchange_supported(pair, local_marks, "H", rev)
            after, enabled, _ = routes.exchange(before, pair, guard=local_marks, connected=connected, reverse=rev)
            action_marks = pair
        elif target == 1:
            pair = routes._places((routes.A, routes.C), rev)
            q_guard = (routes._guard(Q, rev),)
            after, enabled, _ = routes.exchange(before, pair, guard=q_guard, connected=connected, reverse=rev)
            action_marks = pair
            checks += [(bank, mark, want, routes.bit(before, mark)) for mark, want in q_guard]
        else:
            line = routes._concerted_trace(before, connected=connected, reverse=rev)
            after, enabled = line["after"], line["enabled"]
            action_marks = tuple(line["toggled"])
        assert _failures(before, rev) == _failures(after, rev)
        self.words[bank] = after
        assert all(routes.bit(self.words[src], mark) == got for src, mark, _, got in (*checks, *transported))
        if not offered:
            assert not enabled and before == after
        self.actions.append((*spec[:7], offered, classical))
        self.history.append([("reverse " if invert else "") + label, bank, offered, enabled, before, after,
                             action_marks, checks, transported, classical])

    def undo(self, actions, *, disconnect_at=None, stop_on_disconnect=False):
        for i, action in enumerate(reversed(tuple(actions))):
            self._apply(action, invert=True, forced_disconnect=i == disconnect_at)
            if i == disconnect_at and stop_on_disconnect:
                break

    def output(self):
        return {"initial": self.initial, "encodings": self.reverse, "final": dict(self.words),
                "offers": list(self.history), "offer_count": len(self.history),
                "fired_count": sum(step[4] != step[5] for step in self.history)}


def _new_circuit(bits, encodings, *, initial=None, direct=None):
    words, coords = {}, {}
    for index, lab in enumerate(LABS):
        reversed_lab = bool(encodings[index])
        for name in (_bank(lab), _channel(lab)):
            words[name] = initial.get(name, _ready(reversed_lab)) if initial else _ready(reversed_lab)
            coords[name] = reversed_lab
        for slot, kind in enumerate(SLOTS):
            name = lab + "_" + kind
            words[name], _ = _port_record(bits[2 * slot + index], reversed_lab)
            coords[name] = reversed_lab
        if direct is not None:
            name = lab + "_third"
            words[name], _ = _port_record(direct[index], reversed_lab)
            coords[name] = reversed_lab
    return Circuit(words, coords)


def _physical_bank_status(circuit, bank):
    value = circuit.words[bank]
    rev = circuit.reverse[bank]
    failures = dict(zip(LAWS, _failures(value, rev), strict=True))
    return {"word": value, "logical_registers": tuple(circuit.read(bank, i) for i in range(13)),
            "keeper_and_z": circuit.keeper(bank), "ordinary_law_failures": failures}


def _visible_code(circuit, bank, *, compensated=True):
    routes = _earlier()[2]
    word, rev = circuit.words[bank], circuit.reverse[bank]
    for bit in (0, 1):
        marks = _code_controls(bit) if compensated else _code_controls(bit)[:2]
        if all(routes.bit(word, routes._transport(mark, rev)) == want for mark, want in marks):
            return bit
    return None


def _archive(circuit, bank, port, slot, *, policy="attested", enabled=True, latch=(True, True)):
    value_reg, flag_reg = LOCAL[slot], LOCAL_OK[slot]
    assert not circuit.read(bank, value_reg) and not circuit.read(bank, flag_reg) or not enabled
    for bit in (0, 1):
        strong = policy == "attested"
        raw = _code_controls(bit) if strong else _code_controls(bit)[:2]
        port_guards = _port_guard(port, bit) if strong else _port_guard(port)
        held_q = ((Q, bit),) if strong else ()
        if bit:
            circuit.exchange(bank, value_reg, "copy visible K value into local archive", local=held_q,
                             raw=raw, external=port_guards, offered=enabled and latch[0])
        circuit.exchange(bank, flag_reg, "set local archive presence after the value check",
                         local=(*held_q, (value_reg, bit)), raw=raw, external=port_guards, offered=enabled and latch[1])


def _capture(circuit, lab, slot, *, write=(True, True), undo=None, uncopy=True,
             latch=(True, True), permitted=True, policy="attested", return_keeper=True):
    bank, port = _bank(lab), lab + "_" + SLOTS[slot]
    q_before = circuit.read(bank, Q)
    raw_port = circuit.port(port)
    known_blank = not circuit.read(bank, LOCAL[slot]) and not circuit.read(bank, LOCAL_OK[slot])
    usable = permitted and circuit.ready(bank) and known_blank and raw_port is not None
    reason = ("offered" if usable else "no resolved admissible port" if raw_port is None else
              "nonready K or Q" if not circuit.ready(bank) else "slot occupied" if not known_blank else "request denied")
    circuit.exchange(bank, Q, "load actually completed local port into Q", external=_port_guard(port, 1), offered=usable)
    writer_start = circuit.words[bank]
    in_audited_writer_orbit = circuit.keeper(bank) == READY_KEEPER and _failures(writer_start, circuit.reverse[bank]) == ((), ())
    forward = len(circuit.actions)
    circuit.write(bank, tuple(p and usable for p in write))
    after_writer = _physical_bank_status(circuit, bank)
    keeper_value = _visible_code(circuit, bank)
    full_matches = raw_port is not None and circuit.keeper(bank) == KEEPER[raw_port]
    if usable:
        assert circuit.read(bank, Q) == raw_port
    if usable and in_audited_writer_orbit:
        assert (keeper_value == raw_port) == full_matches
    _archive(circuit, bank, port, slot, policy=policy, enabled=usable, latch=latch)
    archived = circuit.read(bank, LOCAL[slot]) if circuit.read(bank, LOCAL_OK[slot]) else None
    reset = write if undo is None else undo
    if return_keeper:
        circuit.write(bank, tuple(p and usable for p in reset), reverse_order=True)
        kept_archives = circuit.words[bank]
        restored_before_uncopy = circuit.visible_ready_keeper(bank)
        if usable and in_audited_writer_orbit:
            assert restored_before_uncopy == (circuit.keeper(bank) == READY_KEEPER)
        circuit.exchange(bank, Q, "uncopy Q only after K is physically ready",
                         external=_port_guard(port, 1), offered=usable and restored_before_uncopy and uncopy)
    else:
        kept_archives, restored_before_uncopy = circuit.words[bank], False
    if write == reset and return_keeper and usable:
        routes = _earlier()[2]
        rev = circuit.reverse[bank]
        archive_marks = [mark for i in (LOCAL[slot], LOCAL_OK[slot]) if circuit.read(bank, i)
                         for mark in routes._places(routes.REGISTERS[i][:2], rev)]
        expected = writer_start ^ routes.mask(archive_marks)
        assert kept_archives == expected
        if uncopy:
            assert circuit.read(bank, Q) == q_before
    return {"slot": SLOTS[slot], "launch": reason, "raw_completed_port": raw_port,
            "raw_completed_port_word": circuit.words[port], "writer_connections": write,
            "forward_keeper_receipt": after_writer, "H_visible_keeper_bit": keeper_value,
            "H_visible_keeper_matches_measured_port": raw_port is not None and keeper_value == raw_port,
            "full_word_audit_input_on_documented_both_law_writer_orbit": in_audited_writer_orbit,
            "independent_full_K_agrees_with_measured_port": full_matches,
            "archived_actual_bit_or_absent": archived, "keeper_returned_before_uncopy": restored_before_uncopy,
            "reusable_after_capture": circuit.ready(bank), "initial_Q": q_before,
            "writer_start_word": writer_start, "writer_offer_index": forward, "terminal_bank": _physical_bank_status(circuit, bank)}


def _pack(circuit, source, channel, value, present, *, offered=True, label="archive", present_when=1, additional=()):
    assert circuit.read(channel, CARRIER_BIT) == circuit.read(channel, CARRIER_PRESENT) == 0
    start = len(circuit.actions)
    gate = ((source, present, present_when), *additional)
    circuit.exchange(channel, CARRIER_BIT, f"load {label} value onto directed carrier",
                     external=(*gate, (source, value, 1)), offered=offered, classical=True)
    circuit.exchange(channel, CARRIER_PRESENT, f"mark actual {label} message presence",
                     external=gate, offered=offered, classical=True)
    return tuple(circuit.actions[start:])


def _unpack(circuit, channel, bank, slot, *, offered=True):
    fresh = not circuit.read(bank, REMOTE[slot]) and not circuit.read(bank, REMOTE_OK[slot])
    offered = offered and fresh and circuit.ready(bank)
    gate = ((channel, CARRIER_PRESENT, 1),)
    circuit.exchange(bank, REMOTE[slot], "copy delivered message value to other bank",
                     external=(*gate, (channel, CARRIER_BIT, 1)), offered=offered, classical=True)
    circuit.exchange(bank, REMOTE_OK[slot], "keep independently received message presence",
                     external=gate, offered=offered, classical=True)
    return bool(offered and circuit.read(channel, CARRIER_PRESENT))


def _communicate(circuit, source, slot, connected, *, permitted=True):
    owner, carrier, receiver = _bank(source), _channel(source), _bank(_mate(source))
    ready_word = circuit.words[carrier]
    payload = _pack(circuit, owner, carrier, LOCAL[slot], LOCAL_OK[slot], offered=connected and permitted)
    transmitted = circuit.words[carrier]
    present = bool(circuit.read(carrier, CARRIER_PRESENT))
    accepted = _unpack(circuit, carrier, receiver, slot, offered=connected and permitted)
    message = circuit.read(carrier, CARRIER_BIT) if present else None
    circuit.undo(payload)
    assert circuit.words[carrier] == ready_word
    return {"direction": source + "→" + _mate(source), "slot": SLOTS[slot], "channel_connected": connected,
            "accepted_initial_receiver_words": permitted,
            "carrier_initial": ready_word, "carrier_in_transit": transmitted, "carrier_terminal": circuit.words[carrier],
            "payload_bit": message, "present": present, "accepted": accepted,
            "classical_uses": int(present), "classical_present_and_value_places": (CARRIER_PRESENT, CARRIER_BIT)}


def _sign_bits(circuit, lab, *, permitted=True):
    bank = _bank(lab)
    offered = circuit.ready(bank) and permitted and all(circuit.read(bank, i) == 0 for i in (*SIGN, COMPLETE))
    for slot in range(2):
        present = ((LOCAL_OK[slot], 1), (REMOTE_OK[slot], 1))
        for src in (LOCAL[slot], REMOTE[slot]):
            circuit.exchange(bank, SIGN[slot], "XOR actually present local and remote bits", local=(*present, (src, 1)), offered=offered)
    all_present = tuple((i, 1) for i in (*LOCAL_OK, *REMOTE_OK))
    circuit.exchange(bank, SIGN[2], "negative product convention: start y at one", local=all_present, offered=offered)
    for sign in SIGN[:2]:
        circuit.exchange(bank, SIGN[2], "complemented XOR for the physical name 30 archive",
                         local=(*all_present, (sign, 1)), offered=offered)
    circuit.exchange(bank, COMPLETE, "write physical complete-triple validity", local=all_present, offered=offered)
    shown = tuple(1 - 2 * circuit.read(bank, SIGN[i]) if offered and circuit.read(bank, LOCAL_OK[i]) and circuit.read(bank, REMOTE_OK[i])
                  else None for i in range(2))
    full = bool(offered and circuit.read(bank, COMPLETE))
    return (*shown, 1 - 2 * circuit.read(bank, SIGN[2]) if full else None)


def _display(circuit, lab, *, hold_last=True, stages=(True, True)):
    bank = _bank(lab)
    rows, held = [], ()
    for i, name in enumerate((28, 29, 30)):
        start = len(circuit.actions)
        ready = circuit.ready(bank) and bool(circuit.read(bank, COMPLETE))
        archive_bit = circuit.read(bank, SIGN[i]) if ready else None
        full_K_ready_on_entry = circuit.keeper(bank) == READY_KEEPER
        circuit.exchange(bank, Q, "load physically archived sign into Q for display",
                         local=((COMPLETE, 1), (SIGN[i], 1)), offered=ready)
        circuit.write(bank, tuple(p and ready for p in stages))
        shown = _physical_bank_status(circuit, bank)
        certified = ready and _visible_code(circuit, bank) == archive_bit
        full_grade = ready and circuit.keeper(bank) == KEEPER[archive_bit]
        if ready and full_K_ready_on_entry:
            assert certified == full_grade
        recipe = tuple(circuit.actions[start:])
        tape_index = len(circuit.history)
        if i == 2 and hold_last and certified:
            held = recipe
        else:
            circuit.undo(recipe)
        rows.append({"physical_name": name, "signed_archive_bit": archive_bit, "ordinary_display": shown,
                     "comparison_with_archive": certified, "observed_after_offer_number": tape_index,
                     "independent_full_K_grade": full_grade,
                     "retained_now": bool(held), "after_return_bank_word": circuit.words[bank]})
    return rows, held


def _primary(circuit, channels, *, faults=None, hold_last=True, no_memory=False, display_stages=None):
    faults = {} if faults is None else faults
    display_stages = {} if display_stages is None else display_stages
    initial_denials, full_initial_grades = {}, {}
    for lab in LABS:
        bank = _bank(lab)
        word = circuit.words[bank]
        reverse = circuit.reverse[bank]
        seed, h = _ready(reverse), _holding_H_mask(reverse)
        initial_denials[lab] = None if word & h == seed & h else "H-visible word differs from supplied fresh receiver"
        full_initial_grades[lab] = word == seed
    captures = {lab: [] for lab in LABS}
    for slot, lab in product(range(2), LABS):
        options = dict(faults.get((lab, slot), {}))
        options["permitted"] = options.get("permitted", True) and initial_denials[lab] is None
        if no_memory:
            options.update(latch=(False, False), return_keeper=False)
            options["permitted"] = options["permitted"] and slot == 0
        captures[lab].append(_capture(circuit, lab, slot, **options))
    messages = [_communicate(circuit, lab, slot, channels[2 * j + slot],
                             permitted=initial_denials[lab] is None and initial_denials[_mate(lab)] is None)
                for j, lab in enumerate(LABS) for slot in range(2)]
    budgets = {lab: tuple(circuit.read(_bank(lab), i) for i in range(13)) for lab in LABS}
    reported, displays, held = {}, {}, {}
    for lab in LABS:
        bank = _bank(lab)
        reported[lab] = _sign_bits(circuit, lab, permitted=initial_denials[lab] is None and not no_memory)
        if initial_denials[lab] is None and not no_memory:
            displays[lab], held[lab] = _display(circuit, lab, hold_last=hold_last, stages=display_stages.get(lab, (True, True)))
        else:
            displays[lab], held[lab] = [], ()
        assert all(circuit.read(bank, i) == budgets[lab][i] for i in (*LOCAL, *REMOTE, *LOCAL_OK, *REMOTE_OK))
    coverage = tuple(sum(reported[lab][i] is not None for lab in LABS) for i in range(3))
    complete = tuple(lab for lab in LABS if all(x is not None for x in reported[lab]))
    if len(complete) == 2:
        assert reported["A"] == reported["B"]
    states = {}
    for lab in LABS:
        bank = _bank(lab)
        states[lab] = {**_physical_bank_status(circuit, bank), "reported_signs": reported[lab],
                       "sequential_display_observations": displays[lab], "initial_receiving_bank_denial": initial_denials[lab],
                       "initial_full_word_matches_supplied_ready_preparation_audit_only": full_initial_grades[lab],
                       "archived_records_full_K_audit": tuple(
                           c["independent_full_K_agrees_with_measured_port"] if c["archived_actual_bit_or_absent"] is not None else None
                           for c in captures[lab])}
    joint = tuple(tuple(captures[lab][slot]["archived_actual_bit_or_absent"] for lab in LABS)
                  for slot in range(2))
    if all(bit is not None for pair in joint for bit in pair):
        x, z = (1 - 2 * (left ^ right) for left, right in joint)
        joint_audit = x, z, -x * z
    else:
        joint_audit = None
    record = {"bank_status": states, "local_captures": captures, "classical_messages": messages,
              "signed_names_28_29_30_available_in_how_many_banks": coverage, "readers_with_the_complete_triple": complete,
              "simultaneous_actual_keeper_words_A_B": tuple(circuit.keeper(_bank(lab))[0] for lab in LABS),
              "ordinary_message_attempts": len(messages), "physical_classical_messages_sent": sum(row["classical_uses"] for row in messages),
              "distributed_archived_bits_by_slot": joint, "joint_audit_can_reconstruct_triple": joint_audit}
    return record, held


def push_fine_record(bits, *, encodings=(False, False), channels=(True, True, True, True), faults=None,
                     hold_last=True, initial=None, no_memory=False, display_stages=None):
    """Replay one record (A_X,B_X,A_Z,B_Z), with channel order A→B X,Z then B→A X,Z.

    Faults are keyed by (lab, slot), with the options accepted by `_capture`.
    The value None means an absent port. Words c,d are explicit out-of-code controls.
    """
    if len(bits) != 4 or len(encodings) != 2 or len(channels) != 4:
        raise ValueError("four local port values, two encodings and four channels are required")
    circuit = _new_circuit(bits, encodings, initial=initial)
    row, _ = _primary(circuit, channels, faults=faults, hold_last=hold_last, no_memory=no_memory, display_stages=display_stages)
    return {"fine_records_A_X_B_X_A_Z_B_Z": tuple(bits), "enabled_channels": tuple(channels),
            **row, "complete_physical_history": circuit.output()}


def _direct(circuit, primary, primary_held, channels, *, retain=True, clear_primary=True, invert_display=False):
    old = _earlier()[1]
    raw = (circuit.port("A_third"), circuit.port("B_third"))
    before = {lab: tuple(circuit.read(_bank(lab), i) for i in range(13) if i != Q) for lab in LABS}
    for lab in LABS:
        if clear_primary:
            circuit.undo(primary_held[lab])
    ready_after_attempt = {lab: circuit.ready(_bank(lab)) for lab in LABS}
    messages, payloads = {}, {}
    for i, lab in enumerate(LABS):
        carrier, spent = _channel(lab), lab + "_third"
        original = circuit.words[carrier]
        payloads[lab] = _pack(circuit, spent, carrier, old.ADDRESS_RECORD[1], old.MEASURED_RECEIPT,
                              offered=channels[i], label="direct third", present_when=0,
                              additional=((spent, old.ADDRESS_RECORD[0], 1),))
        messages[lab] = {"direction": lab + "→" + _mate(lab), "connected": channels[i],
                         "initial": original, "in_transit": circuit.words[carrier],
                         "present": bool(circuit.read(carrier, CARRIER_PRESENT)),
                         "value": circuit.read(carrier, CARRIER_BIT) if circuit.read(carrier, CARRIER_PRESENT) else None}
    results, tails = {}, {}
    for i, lab in enumerate(LABS):
        bank, port, incoming = _bank(lab), lab + "_third", _channel(_mate(lab))
        admitted_bank = primary["bank_status"][lab]["initial_receiving_bank_denial"] is None
        applicable = admitted_bank and ready_after_attempt[lab] and raw[i] is not None and circuit.read(incoming, CARRIER_PRESENT) == 1
        stored = (1 - 2 * circuit.read(bank, SIGN[2])) if admitted_bank and circuit.read(bank, COMPLETE) else None
        assert stored == primary["bank_status"][lab]["reported_signs"][2]
        slot_gate = (*_port_guard(port), (incoming, CARRIER_PRESENT, 1))

        def offered_recipe(comparison):
            available = bool(applicable and (stored is not None or not comparison))
            full_K_ready_on_entry = circuit.keeper(bank) == READY_KEEPER
            start = len(circuit.actions)
            circuit.exchange(bank, Q, "XOR own actually completed third meter bit",
                             external=(*slot_gate, (port, old.ADDRESS_RECORD[1], 1)), offered=available, classical=True)
            circuit.exchange(bank, Q, "XOR directly delivered third meter bit",
                             external=(*slot_gate, (incoming, CARRIER_BIT, 1)), offered=available, classical=True)
            circuit.exchange(bank, Q, "deliberately invert only the display calibration",
                             external=slot_gate, offered=available and invert_display, classical=True)
            if comparison:
                circuit.exchange(bank, Q, "compare against the archived physical name-30 sign",
                                 local=((SIGN[2], 1), (COMPLETE, 1)), external=slot_gate, offered=available, classical=True)
            circuit.write(bank, (available, available))
            bit = circuit.read(bank, Q) if available else None
            full_grade = available and circuit.keeper(bank) == KEEPER[bit]
            visible_grade = available and _visible_code(circuit, bank) == bit
            if available:
                expected = raw[0] ^ raw[1] ^ int(invert_display)
                if comparison:
                    expected ^= int(stored == -1)
                assert bit == expected
                if full_K_ready_on_entry:
                    assert full_grade and visible_grade
            row = {"answer_bit_or_no_new_answer": bit, "displayed_word": circuit.words[bank],
                   "keeper_and_z": circuit.keeper(bank), "observed_after_offer_number": len(circuit.history),
                   "was_an_actual_new_keeper_report": visible_grade,
                   "independent_full_K_grade": full_grade}
            return row, tuple(circuit.actions[start:]), visible_grade

        start_direct_word = circuit.words[bank]
        direct, undo_direct, shown = offered_recipe(False)
        circuit.undo(undo_direct)
        if shown:
            assert circuit.ready(bank) and circuit.words[bank] == start_direct_word
        comparison, undo_comparison, compared = offered_recipe(True)
        if not retain or not compared:
            circuit.undo(undo_comparison)
        else:
            tails[lab] = undo_comparison
        assert before[lab] == tuple(circuit.read(bank, j) for j in range(13) if j != Q)
        results[lab] = {"primary_third_as_previously_archived": stored, "ready_before_direct": ready_after_attempt[lab],
                        "temporary_direct_sign_display": direct, "disagreement_display": comparison,
                        "comparison_retained_in_this_bank": bool(retain and compared),
                        "terminal_bank": _physical_bank_status(circuit, bank)}
    if not tails:
        for lab in reversed(LABS):
            circuit.undo(payloads[lab])
    for lab in LABS:
        messages[lab]["terminal"] = circuit.words[_channel(lab)]
    return {"third_raw_bits": raw, "third_raw_meter_words": tuple(circuit.words[lab + "_third"] for lab in LABS),
            "third_messages": messages, "results": results, "display_convention_inverted": invert_display,
            "a_cleared_comparison_has_no_new_terminal_receipt": not tails, "all_twelve_non_Q_archive_fields_unchanged": True,
            "carrier_retained_while_its_actual_controls_are_needed": bool(tails)}


def _replay_laws_of_damage():
    routes = _earlier()[2]
    all_rows = {}
    for reverse in (False, True):
        bank, port = _bank("A"), "A_X"
        source, _ = _port_record(1, reverse)
        word = _other_word(_ready(reverse), reverse, positions=((Q, 1),), keeper="011", z=1)
        hidden_fault = word ^ (1 << routes._transport(routes.B, reverse))
        h = _holding_H_mask(reverse)
        assert word & h == hidden_fault & h
        assert _failures(word, reverse) == ((), ()) and _failures(hidden_fault, reverse) == (("K",), ())
        cases = {}
        for label, initial in (("complete_011", word), ("private_B_fault_001", hidden_fault)):
            c = Circuit({bank: initial, port: source}, {bank: reverse, port: reverse})
            visible = _visible_code(c, bank)
            assert visible == c.read(bank, Q) == c.port(port) == 1
            _archive(c, bank, port, 0)
            assert c.read(bank, LOCAL[0]) == c.read(bank, LOCAL_OK[0]) == 1
            cases[label] = {"indistinguishable_H_word": initial & h, "full_K_read_audit_only": c.keeper(bank),
                            "physically_archive_visible_bit": c.read(bank, LOCAL[0]), "H_only_credit": bool(c.read(bank, LOCAL_OK[0])),
                            "full_K_matches_port": c.keeper(bank) == KEEPER[1], "source_port_word": source,
                            "law_failures_initial_and_final": dict(zip(LAWS, _failures(c.words[bank], reverse), strict=True)),
                            "history": c.output()}
        deltas = tuple(s[4] ^ s[5] for s in cases["complete_011"]["history"]["offers"])
        assert deltas == tuple(s[4] ^ s[5] for s in cases["private_B_fault_001"]["history"]["offers"])
        fresh = _ready(reverse)
        dirty_ready = fresh ^ (1 << routes._transport(routes.B, reverse))
        assert fresh & h == dirty_ready & h and _failures(dirty_ready, reverse) == (("K",), ())
        c = _new_circuit((1, 0, 1, 0), (reverse, reverse), initial={bank: dirty_ready}, direct=(0, 0))
        primary, held = _primary(c, (True, True, True, True))
        observed = primary["bank_status"]["A"]
        assert not observed["initial_receiving_bank_denial"] and not observed["initial_full_word_matches_supplied_ready_preparation_audit_only"]
        assert primary["local_captures"]["A"][0]["forward_keeper_receipt"]["keeper_and_z"] == ("001", 1)
        assert observed["archived_records_full_K_audit"] == (False, False)
        third = _direct(c, primary, held, (True, True))
        a = third["results"]["A"]["disagreement_display"]
        assert a["was_an_actual_new_keeper_report"] and not a["independent_full_K_grade"] and a["keeper_and_z"] == ("001", 1)
        c.undo(c.actions)
        assert c.words[bank] == dirty_ready and c.visible_ready_keeper(bank) and c.keeper(bank) == ("100", 1)
        all_rows[str(int(reverse))] = {**cases, "private_B_present_even_an_inadmissible_initial_or_return_word": {
            "known_correct_initial_word": fresh, "adversarial_lawful_under_NAE_initial_word": dirty_ready,
            "primary": primary, "direct_and_agreement": third, "H_visible_ready_on_return": c.visible_ready_keeper(bank),
            "actual_full_K_on_return": c.keeper(bank), "actual_complete_history_including_return": c.output()}}
    return all_rows


class TraceIndex:
    """Store repeated complete primitive offers once, retaining every history."""

    def __init__(self):
        self.rows = []
        self.lookup = {}

    def add(self, history):
        indices = []
        for offer in history["offers"]:
            key = (*offer[:7], tuple(offer[7]), tuple(offer[8]), offer[9])
            if key not in self.lookup:
                self.lookup[key] = len(self.rows)
                self.rows.append(offer)
            indices.append(self.lookup[key])
        return {**{k: v for k, v in history.items() if k != "offers"}, "offers": indices}

    def record(self, row):
        return {**row, "complete_physical_history": self.add(row["complete_physical_history"])}


def _key(values):
    return "".join("-" if x is None else str(int(x)) if isinstance(x, bool) else str(x) for x in values)


def _fine_lookup(index):
    intact, disconnections, literal, cleared = {}, {}, {}, {}
    for orientations, bits, channels in product(STAGES, BITS, BITS):
        rv, b, m = _key(orientations), _key(bits), _key(channels)
        row = push_fine_record(bits, encodings=orientations, channels=channels)
        first, second = 1 - 2 * (bits[0] ^ bits[1]), 1 - 2 * (bits[2] ^ bits[3])
        for i, lab in enumerate(LABS):
            incoming = channels[2 * (1 - i):2 * (1 - i) + 2]
            desired = (first if incoming[0] else None, second if incoming[1] else None,
                       -first * second if all(incoming) else None)
            assert row["bank_status"][lab]["reported_signs"] == desired
        assert row["joint_audit_can_reconstruct_triple"] == (first, second, -first * second)
        assert row["physical_classical_messages_sent"] == sum(channels)
        for message in row["classical_messages"]:
            assert message["carrier_initial"] == message["carrier_terminal"]
        if all(channels):
            intact[f"{rv}/{b}"] = index.record(row)
            clear_row = push_fine_record(bits, encodings=orientations, hold_last=False)
            assert clear_row["simultaneous_actual_keeper_words_A_B"] == ("110", "110")
            cleared[f"{rv}/{b}"] = index.record(clear_row)
            literal_row = push_fine_record(bits, encodings=orientations, no_memory=True)
            for i, lab in enumerate(LABS):
                assert literal_row["bank_status"][lab]["keeper_and_z"] == KEEPER[bits[i]]
                assert literal_row["bank_status"][lab]["reported_signs"] == (None, None, None)
            literal_row["only_obtainable_joint_sign_from_the_two_simultaneous_keeper_words"] = first
            literal_row["both_other_joint_signs_left_open_by_the_two_keepers"] = (29, 30)
            literal[f"{rv}/{b}"] = index.record(literal_row)
        else:
            disconnections[f"{rv}/{b}/{m}"] = index.record(row)
    return intact, disconnections, literal, cleared


def _fault_lookup(index):
    solitary, joined, display = {}, {}, {}
    for reverse, bit, slot, write, back, uncopy, latch, policy in product(
            (False, True), (0, 1), range(2), STAGES, STAGES, (False, True), STAGES, ("attested", "code_only")):
        bits = (bit, None, None, None) if slot == 0 else (None, None, bit, None)
        circuit = _new_circuit(bits, (reverse, reverse))
        start = _physical_bank_status(circuit, _bank("A"))
        row = _capture(circuit, "A", slot, write=write, undo=back, uncopy=uncopy, latch=latch, policy=policy)
        if policy == "attested" and row["archived_actual_bit_or_absent"] is not None:
            assert row["independent_full_K_agrees_with_measured_port"] and row["archived_actual_bit_or_absent"] == bit
        key = f"{int(reverse)}/{bit}/{slot}/{_key(write)}/{_key(back)}/{int(uncopy)}/{_key(latch)}/{policy}"
        solitary[key] = {"initial_receiver": start, **row, "complete_physical_history": index.add(circuit.output())}
    routes = _earlier()[2]
    for orientations, site in product(STAGES, LABS):
        rev, ii = orientations[LABS.index(site)], LABS.index(site)
        seed = _ready(rev)
        corrupt = {
            "stale_binary_bit": _other_word(seed, rev, positions=((LOCAL[0], 1),)),
            "stale_completed_if_reused": _other_word(seed, rev, positions=((COMPLETE, 1), *((i, 1) for i in (*LOCAL_OK, *REMOTE_OK)))),
            "already_occupied_keeper": _other_word(seed, rev, keeper="101", z=0),
            "old_Q_occupied": _other_word(seed, rev, positions=((Q, 1),)),
            "empty_keeper_000": _other_word(seed, rev, keeper="000"),
            "invalid_keeper_111": _other_word(seed, rev, keeper="111"),
            "damaged_complementary_pair": seed ^ (1 << routes._guard(Q, rev)[0]),
        }
        for label, word in corrupt.items():
            replay = push_fine_record((1, 1, 0, 0), encodings=orientations, initial={_bank(site): word})
            stale = replay["bank_status"][site]
            assert stale["initial_receiving_bank_denial"] and stale["word"] == word
            joined[f"{_key(orientations)}/{site}/{label}"] = index.record(replay)
        for b, slot, mode in product((0, 1), range(2), ("slot_missing", "c", "d", "request_denied", "partial_writer", "return_disconnected", "uncopy_disconnected", "code_only_wrong_word")):
            bits = list((b, 1, b, 0))
            mark = 2 * slot + ii
            bits[mark] = None if mode == "slot_missing" else mode if mode in ("c", "d") else b
            fault = {"request_denied": {"permitted": False}, "partial_writer": {"write": (False, True)},
                     "return_disconnected": {"undo": (False, False)}, "uncopy_disconnected": {"uncopy": False},
                     "code_only_wrong_word": {"write": (False, True), "policy": "code_only"}}.get(mode, {})
            row = push_fine_record(bits, encodings=orientations, faults={(site, slot): fault})
            joined[f"{_key(orientations)}/{site}/{slot}/{b}/{mode}"] = index.record(row)
    for enc, first, second, left, right in product(STAGES, (False, True), (False, True), STAGES, STAGES):
        row = push_fine_record((0, int(first), 0, int(second)), encodings=enc, display_stages={"A": left, "B": right})
        for lab in LABS:
            assert all(sign is not None for sign in row["bank_status"][lab]["reported_signs"])
        display[f"{_key(enc)}/{int(first)}{int(second)}/{_key(left)}/{_key(right)}"] = index.record(row)
    return {"all_single_slot_combinations": solitary, "failed_slots_before_and_after_a_success_plus_stale_banks": joined,
            "disconnected_final_display_with_archive_still_intact": display}


def _direct_lookup(index):
    trials = {}
    for orientations, raw_bits, third, channels in product(STAGES, BITS, STAGES, STAGES):
        triple_bit = 1 ^ raw_bits[0] ^ raw_bits[1] ^ raw_bits[2] ^ raw_bits[3]
        for mode in ("intact", "reversed_physical_coupling", "inverted_display_convention", "both_cleared", "primary_K_not_cleared",
                     "direct_source_missing", "A_port_missing", "B_port_missing", "primary_archive_missing"):
            if mode != "intact" and not (all(channels) and raw_bits in ((0, 0, 0, 0), (0, 0, 0, 1))):
                continue
            if mode == "reversed_physical_coupling" and (third[0] ^ third[1]) != triple_bit:
                continue
            local_ports = list(third)
            primary_raw = raw_bits
            if mode == "reversed_physical_coupling":
                local_ports[1] ^= 1
            elif mode == "direct_source_missing":
                local_ports = [None, None]
            elif mode == "A_port_missing":
                local_ports[0] = None
            elif mode == "B_port_missing":
                local_ports[1] = None
            elif mode == "primary_archive_missing":
                primary_raw = (None, raw_bits[1], *raw_bits[2:])
            circuit = _new_circuit(primary_raw, orientations, direct=local_ports)
            primary, held = _primary(circuit, (True, True, True, True))
            row = _direct(circuit, primary, held, channels, retain=mode != "both_cleared",
                          clear_primary=mode != "primary_K_not_cleared", invert_display=mode == "inverted_display_convention")
            key = f"{_key(orientations)}/{_key(raw_bits)}/{_key(third)}/{_key(channels)}/{mode}"
            if mode == "reversed_physical_coupling":
                assert row["third_raw_bits"] != tuple(third)
                assert all(row["results"][lab]["disagreement_display"]["answer_bit_or_no_new_answer"] == 1 for lab in LABS)
            for i, lab in enumerate(LABS):
                result = row["results"][lab]
                exists = None not in local_ports and channels[1 - i] and mode != "primary_K_not_cleared"
                assert result["temporary_direct_sign_display"]["was_an_actual_new_keeper_report"] == exists
                assert result["disagreement_display"]["was_an_actual_new_keeper_report"] == (exists and mode != "primary_archive_missing")
                if mode == "both_cleared":
                    assert result["terminal_bank"]["keeper_and_z"] == READY_KEEPER
            trials[key] = {"primary_record_before_direct": primary, **row, "uncrossed_third_ports": third,
                           "scope_of_setting_change": {"reversed_physical_coupling": "old signed coupling can reverse one meter's result",
                                                       "inverted_display_convention": "raw gates, source and port words unchanged; Q convention flipped"}.get(mode),
                           "complete_physical_history": index.add(circuit.output())}
    return trials


def _source_checks(index):
    earlier, _, _ = _earlier()
    source = earlier._bench_binary_source()
    corrected_source = source["complete_binary_source_through_both_physical_heralds"]
    policies = ("both_corrected", "plus_only", "uncorrected")
    attempts, repetitions, denials, sources = {}, {}, {}, {}
    for rev in (False, True):
        for policy in policies:
            calibration = corrected_source[f"{int(rev)}/{policy}"]
            rows = calibration["all_final_ports"]
            sources[f"{int(rev)}/{policy}"] = {
                port: {**rows[port], "physical_correction_path": tuple(
                    source["preparation_and_port_branch_supports"][term["ordinary_prep_and_raw_recombiner_key"]]["physical_phase_correction_column"]
                    for term in rows[port]["signed_terms"])} for port in "ab"
            }
            for count in (1, 2, 3):
                for heralds in product(("a", "b", None), repeat=count):
                    accepted = tuple(port is not None and rows[port]["physically_selected_delivery"] for port in heralds)
                    ports = tuple(_port_record(port, rev)[0] for port in heralds)
                    attempts[f"{int(rev)}/{policy}/{_key(heralds)}"] = {
                        "source_heralds": heralds, "full_bench_herald_words": ports, "source_attempt_count": len(heralds),
                        "delivered_pair_flags": accepted, "all_sources_available": all(accepted),
                        "consumed_pairs_if_all_available": sum(accepted), "source_quantum_weights_supply": "in the independent probability ledger"}
    configurations = tuple(product(("a", "b", None), repeat=2))
    for bench_rev, first_policy, second_policy, first, second in product((False, True), policies[:2], policies[:2], configurations, configurations):
        key1 = f"{int(bench_rev)}/{first_policy}/{_key(first)}"
        key2 = f"{int(bench_rev)}/{second_policy}/{_key(second)}"
        repetitions[key1 + "/" + key2] = (attempts[key1]["delivered_pair_flags"], attempts[key2]["delivered_pair_flags"])
    for enc, bits, available in product(STAGES, BITS, STAGES):
        raw = tuple(b if available[i // 2] else None for i, b in enumerate(bits))
        row = push_fine_record(raw, encodings=enc)
        for lab in LABS:
            assert (row["bank_status"][lab]["reported_signs"][2] is not None) == all(available)
        denials[f"{_key(enc)}/{_key(bits)}/{_key(available)}"] = index.record(row)
    gate_keys = {g for modes in sources.values() for port in modes.values() for g in port["physical_correction_path"]}
    return {"ancestral_source_through_both_actual_binary_heralds": sources,
            "physical_H_CX_H_source_calibrations": {key: source["binary_z_gate_on_each_basis_and_herald"][key] for key in sorted(gate_keys)},
            "all_fresh_source_policies_and_plus_minus_absent_attempts": attempts, "first_source_x_second_source_lookup": repetitions,
            "primary_physical_word_by_which_pair_source_failed": denials,
            "old_hidden_and_uncomputed_source_tag_controls": source["physical_which_arm_captures"]}


@cache
def _gate_column(gate, data, control, dr, mr, connected, record="clean"):
    earlier, old, _ = _earlier()
    words = {"A_data": old._basis(data, dr), "A_meter": old._basis(control, mr)}
    return earlier._exact_gate(words, {"A_data": dr, "A_meter": mr}, earlier.GATES[gate], drive=connected, tag=record)


def _local_gate_checks():
    old = _earlier()[1]
    rows, tagged, references = {}, {}, {}
    for data, mx, mz, dr, xr, zr, orientation, connected in product(
            "abcd", "abcd", "abcd", (False, True), (False, True), (False, True), ("XZ", "ZX"), STAGES):
        out, phase, orders = data, 1, []
        for gate in orientation:
            ctrl, rev, offer = (mx, xr, connected[0]) if gate == "X" else (mz, zr, connected[1])
            name = "C" + gate
            column, paths = _gate_column(name, out, ctrl, dr, rev, offer)
            [(actual, amp)] = column.items()
            data_word, meter_word = actual
            assert amp[0] in (-1, 1) and amp[1] == 0 and meter_word == old._basis(ctrl, rev)
            ref = f"{name}/{int(dr)}{int(rev)}/{out}{ctrl}/{int(offer)}"
            if ref not in references:
                references[ref] = {"signed_output": (data_word, meter_word, int(amp[0])),
                                   "all_physical_supports_before_amplitudes_are_combined": paths}
            orders.append(ref)
            out, phase = old._address(data_word, dr), phase * int(amp[0])
        active = data in "ab"
        flipped_when_x = active and mx == "b" and connected[0]
        seen_by_Z = {"a": "b", "b": "a"}[data] if flipped_when_x and orientation == "XZ" else data
        expected = -1 if active and mz == "b" and connected[1] and seen_by_Z == "b" else 1
        assert phase == expected and out == ({"a": "b", "b": "a"}[data] if flipped_when_x else data)
        key = f"{int(dr)}{int(xr)}{int(zr)}/{data}{mx}{mz}/{orientation}/{_key(connected)}"
        rows[key] = {"ending_full_words_data_X_Z": (old._basis(out, dr), old._basis(mx, xr), old._basis(mz, zr)),
                     "direct_signed_amplitude": phase, "actual_separate_meter_offers": orders}
    for gate, data, ctrl, rev, mode in product(("CX", "CZ", "CJ", "C_minus_J"), "abcd", "ab", (False, True),
                                                ("audit", "control_kept", "control_hidden", "control_returned", "fully_read", "firing_kept")):
        column, paths = _gate_column(gate, data, ctrl, rev, rev, True, mode)
        clean, _ = _gate_column(gate, data, ctrl, rev, rev, True)
        if mode in ("audit", "control_returned"):
            assert clean == column
        tagged[f"{gate}/{int(rev)}/{data}{ctrl}/{mode}"] = {
            "terms_after_combination": [(*w, tuple(map(str, a))) for w, a in sorted(column.items())],
            "physical_supports_before_combination": paths,
            "retained_physical_controls_are_part_of_complete_words": mode in ("control_kept", "control_hidden", "firing_kept", "fully_read")}
    direct = {}
    for gate, data, control, target_rev, meter_rev in product(("CJ", "C_minus_J"), "abcd", "abcd", (False, True), (False, True)):
        terms, paths = _gate_column(gate, data, control, target_rev, meter_rev, True)
        for (dw, mw), amp in terms.items():
            assert mw == old._basis(control, meter_rev) and amp[1] == 0
            direct[f"{gate}/{int(target_rev)}{int(meter_rev)}/{data}{control}"] = {
                "full_words_and_amplitude": (dw, mw, int(amp[0])), "ordinary_branch_offers": paths}
    return {"complete_local_X_then_Z_or_Z_then_X_basis_columns": rows, "gate_support_lookup": references,
            "direct_third_inherited_signed_gate_columns": direct, "physical_route_tags_vs_logs": tagged,
            "signed_lifts_are_supplied_by_the_calibrated_protocol": True,
            "other_laboratory_is_a_disjoint_copy_and_never_a_gate_guard": True}


def _one_pair_ordinary_control(index):
    old = _earlier()[1]
    cases = {}
    for encodings, bits in product(STAGES, BITS):
        circuit = _new_circuit((*bits[:2], None, None), encodings)
        extra_words = {}
        for i, lab in enumerate(LABS):
            data, port = lab + "_post_X_data", lab + "_Z"
            reverse = encodings[i]
            extra_words[data] = old._basis("ab"[bits[2 + i]], reverse)
            circuit.initial[data] = circuit.words[data] = extra_words[data]
            circuit.reverse[data] = reverse
            assert circuit.read(data, old.Q) == 1
            for target, source in ((old.Q, old.Q), (old.S, old.S),
                                   (old.ADDRESS_RECORD[0], old.Q), (old.ADDRESS_RECORD[1], old.S)):
                circuit.exchange(port, target, "copy the actually projectively read data word to an explicit ordinary latch",
                                 external=((data, source, 1),))
            circuit.exchange(port, old.MEASURED_RECEIPT, "mark the copied ordinary read complete")
            assert circuit.words[port] == _port_record(bits[2 + i], reverse)[0]
        proof, _ = _primary(circuit, (True, True, True, True))
        assert all(circuit.words[k] == v for k, v in extra_words.items())
        cases[f"{_key(encodings)}/{_key(bits)}"] = {
            "additional_ordinary_Z_latches": tuple(lab + "_Z" for lab in LABS),
            "measured_data_words_remain_in_their_original_banks": extra_words,
            "explicit_extra_second_coherent_pair_count": 0, "primary_record": proof,
            "complete_physical_history": index.add(circuit.output())}
    return cases


def _keeper_repeats(index):
    clear, second, interruptions = {}, {}, {}
    complete = (True, True, True, True)
    for enc, bits, sources, with_verification in product(STAGES, BITS, STAGES, (False, True)):
        raw = tuple(b if sources[i // 2] else None for i, b in enumerate(bits))
        direct = (0, 1 ^ bits[0] ^ bits[1] ^ bits[2] ^ bits[3])
        c = _new_circuit(raw, enc, direct=direct if with_verification else None)
        first, held = _primary(c, complete)
        if with_verification:
            verification = _direct(c, first, held, (True, True))
        else:
            verification = None
        forward = tuple(c.actions)
        reverse_started = len(forward)
        retained_raw = {k: word for k, word in c.words.items() if "_receiver" not in k and "_to_" not in k}
        before_reverse = dict(c.words)
        c.undo(forward)
        assert c.words == c.initial and all(c.words[k] == w for k, w in retained_raw.items())
        key = f"{_key(enc)}/{_key(bits)}/{_key(sources)}/{int(with_verification)}"
        clear[key] = {"first_raw_carrier_words_still_held": retained_raw, "word_state_before_actual_full_inverse": before_reverse,
                      "actual_same_receivers_and_message_carriers_back_at_ready": True, "begins_inverse_at_offer": reverse_started,
                      "direct_comparison_was_present_at_first_cut": bool(verification and verification["carrier_retained_while_its_actual_controls_are_needed"]),
                      "complete_physical_history": index.add(c.output())}
        if all(sources):
            for second_bits in BITS:
                second[key + "/" + _key(second_bits)] = {
                    "first_inverse_key": key, "fresh_second_primary_record_key": f"{_key(enc)}/{_key(second_bits)}",
                    "same_two_receivers_with_actual_blank_check": True, "fresh_distinct_carriers_request": 2,
                    "first_four_spent_halves_stay_physically_held": tuple(retained_raw[k] for k in ("A_X", "B_X", "A_Z", "B_Z")),
                    "first_report_no_longer_printed_in_either_receiver": True}
        if not all(sources) or bits not in ((0, 0, 0, 0), (1, 0, 0, 0)):
            continue
        for mode in ("failed_reverse", "reread", "already_occupied_but_second_data_acts", "reuse_spent_quantum_carriers"):
            c = _new_circuit(raw, enc, direct=direct if with_verification else None)
            primary, held = _primary(c, complete)
            if with_verification:
                _direct(c, primary, held, (True, True))
            original_final = dict(c.words)
            if mode == "failed_reverse":
                stop = next(i for i, offer in enumerate(reversed(c.history)) if offer[4] != offer[5])
                c.undo(c.actions, disconnect_at=stop, stop_on_disconnect=True)
                assert c.words != c.initial
                info = {"second_deposition": "stopped with residual marks", "second_data_offer": False,
                        "first_reverse_disconnected_at": stop, "second_asked_for_fresh_pairs": 2}
            elif mode == "reread":
                info = {"direct_read_of_the_actually_held_K_A_B": tuple(c.keeper(_bank(lab)) for lab in LABS),
                        "new_quantum_pair_count": 0, "second_deposition": "read the old display", "second_data_offer": False}
                assert c.words == original_final
            elif mode == "already_occupied_but_second_data_acts":
                # The separate meter acts; only deposition at the exact same old receivers is refused.
                fresh_words = {k: original_final[k] for k in (_bank("A"), _bank("B"))}
                new = push_fine_record((1, 0, 1, 0), encodings=enc, initial=fresh_words)
                assert all(new["bank_status"][lab]["initial_receiving_bank_denial"] for lab in LABS)
                assert all(new["bank_status"][lab]["word"] == original_final[_bank(lab)] for lab in LABS)
                info = {"second_deposition": "both occupied old receiver words refused", "second_data_offer": True,
                        "new_quantum_pair_count": 2, "separate_actual_second_carrier_and_refused_deposition_history": index.record(new)}
            else:
                c.undo(c.actions)
                assert c.words == c.initial
                for name in ("A_X", "B_X", "A_Z", "B_Z"):
                    assert c.read(name, _port_roles()[2]) == 0
                info = {"second_deposition": "spent original carriers refused before new data gates", "second_data_offer": False,
                        "new_quantum_pair_count": 0, "actual_spent_carrier_words": retained_raw}
            interruptions[key + "/" + mode] = {**info, "first_raw_records_preserved": all(c.words[k] == w for k, w in retained_raw.items()),
                                                  "complete_physical_history": index.add(c.output())}
    return {"exact_first_inverse_on_the_same_two_banks": clear, "second_fresh_request_lookup": second,
            "measured_again_vs_reread_stale_or_failed_return_controls": interruptions,
            "fresh_second_requests_after_any_checked_first_inverse": (
                "Compose exact_first_inverse_on_the_same_two_banks with primary_physical_word_by_which_pair_source_failed "
                "using the same encoding. The first inverse restores the same complete receiving and message words for every first source mask. "
                "The second program holds the whole first four spent words aside and never uses them as controls."),
            "request_boundary": "A second source has distinct fresh quantum carrier identities. Its port lookup has exactly the verified blank initial receiving banks; the first raw ports remain on the four disjoint spent carriers."}


def _recover_closing_slot_names():
    earlier = _earlier()[0]
    archived = earlier._target()
    routes = archived["independent_four_by_four_routes"]
    i, x, z = ((1, 0), (0, 1)), ((0, 1), (1, 0)), ((1, 0), (0, -1))
    j = earlier._multiply(x, z)
    claimed = (earlier._tensor(x, x), earlier._tensor(z, z), earlier._negative(earlier._tensor(j, j)))
    roster = []
    for name, old_holder, expected in zip((28, 29, 30), (14, 15, 16), claimed, strict=True):
        selected = [r for r in routes if name in r["physical_names"]]
        [route] = selected
        assert route["ordered_holders"] == (old_holder, 17) and route["physical_names"] == [name]
        assert route["two_word_slots_matrix"] == expected
        roster.append({"physical_name": name, **route})
    assert earlier._multiply(earlier._multiply(*claimed[:2]), claimed[2]) == earlier._negative(earlier._tensor(i, i))
    assert archived["old_even_words"] == 16384 and archived["original_forbidden_odd_words"] == 0
    return {"three_verified_physical_names": roster, "other_six_basis_measurement_assignments": [r for r in routes if r["column_holder"] != 17],
            "physical_signed_closing_product": -1, "ordinary_port_bits_only_enter_through_measured_carriers": True,
            "previous_certificate_all_holders": archived}


def _apparatus():
    routes = _earlier()[2]
    ready = {}
    for rev in (False, True):
        word = _ready(rev)
        assert _failures(word, rev) == ((), ())
        decoded = routes.decode(word, reverse=rev)
        assert decoded == {"data": 0, "q": 0, "t": 0, "l": 0, "s": 0, "keeper": "110", "z": 1, "h": 1}
        ready[str(int(rev))] = {"complete_initial_word": word, "decoded": decoded,
                                "each_local_holding_and_its_count": {name: (routes._holding(name, rev),
                                    sum(routes.bit(word, mark) for mark in routes._holding(name, rev))) for name in routes.SUBSTRATE},
                                "a_b_c_z_named_physical_marks": routes._places((routes.A, routes.B, routes.C, routes.Z), rev)}
    return {"exactly_two_receiving_banks": LABS, "physical_marks_per_bank": 44, "both_ready_encodings": ready,
            "receiver_layout": {"local_values": LOCAL, "remote_values": REMOTE, "local_presence": LOCAL_OK, "remote_presence": REMOTE_OK,
                                "separately_stored_sign_bits_names_28_29_30": SIGN, "writer_Q": Q, "complete_triple_valid": COMPLETE},
            "two_ordinary_reusable_carriers": tuple(_channel(lab) for lab in LABS),
            "each_message_uses_actual_presence_and_value_registers": (CARRIER_PRESENT, CARRIER_BIT),
            "one_recipient_per_carrier_direction": True, "any_ordinary_Z_latches_are_listed_separately": True,
            "the_ordinary_growth_law_does_not_initiate_these_offers": True}


def hardware_checks():
    """Return the complete exact hardware record with integers indexing shared offers.

    The standard join is intact_fine_records["revArevB/iXkXiZkZ"].
    Channel-mask records append /abcd with A→B X,Z followed by B→A X,Z.
    Use push_fine_record for an unfactored record with specific slot faults.
    """
    index = TraceIndex()
    intact, disconnected, literal, cleared = _fine_lookup(index)
    earlier, old, _ = _earlier()
    inputs = (Path(__file__).resolve(), HERE / "preregistration.md", PRIOR, earlier.HARDWARE, earlier.ERASURE,
              earlier.CLOSURE, earlier.ASSIGNMENT, old.KEEPER_PATH)
    out = {"apparatus": _apparatus(), "recovered_named_target": _recover_closing_slot_names(), "intact_fine_records": intact,
           "all_other_primary_channel_masks": disconnected, "literal_two_write_only_keepers": literal,
           "serial_reads_without_a_terminal_display": cleared, "fault_and_archive_tables": _fault_lookup(index),
           "same_H_visible_word_with_private_K_damage": _replay_laws_of_damage(),
           "direct_third_and_physical_agreement_overlay": _direct_lookup(index), "same_two_receivers_on_repeat": _keeper_repeats(index),
           "all_sources_and_refusals": _source_checks(index), "physical_gates": _local_gate_checks(),
           "one_pair_plus_actual_ordinary_data_word_control": _one_pair_ordinary_control(index),
           "raw_completed_port_recipe_by_encoding": {f"{int(reverse)}/{_key((bit,))}": _port_record(bit, reverse)[1]
                                                       for reverse, bit in product((False, True), (0, 1, None, "c", "d"))},
           "inputs_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs},
           "offer_columns": ("label", "target_bank", "offered", "enabled", "word_before", "word_after",
                             "physical_target_marks", "unchanged_H_guards", "separately_held_guards", "classical_message_authority"),
           "shared_ordinary_offer_rows": index.rows,
           "record_access": {"intact_lookup": "encode reversals as two 0/1 digits, followed by / and the slot-major four port bits",
                             "offer_grammar": "An indexed history lists integer indices into shared_ordinary_offer_rows. These are successive complete physical word permutations.",
                             "verified_laws": LAWS, "completed_meter_receipt_zero": "the original measured mark is physically changed to zero",
                             "private_K_only_audit": "B is private to K. Audit columns containing a full word do not provide B to archive guards."}}
    return out


def _smoke():
    baseline = push_fine_record((1, 0, 1, 0), encodings=(False, True))
    assert all(baseline["bank_status"][lab]["reported_signs"] == (-1, -1, -1) for lab in LABS)
    assert baseline["simultaneous_actual_keeper_words_A_B"] == ("011", "011")
    failed = push_fine_record((1, 0, 1, 0), faults={("A", 0): {"write": (False, True)}})
    assert failed["local_captures"]["A"][0]["archived_actual_bit_or_absent"] is None
    leakage_control = _replay_laws_of_damage()["0"]["private_B_fault_001"]
    assert leakage_control["H_only_credit"] and not leakage_control["full_K_matches_port"]
    c = _new_circuit((0, 0, 0, 0), (False, True), direct=(0, 1))
    base, held = _primary(c, (True, True, True, True))
    extra = _direct(c, base, held, (True, True))
    assert all(extra["results"][lab]["terminal_bank"]["keeper_and_z"] == KEEPER[0] for lab in LABS)
    c.undo(c.actions)
    assert c.words == c.initial
    return {"intact_and_faulty_keeper_ports": True, "private_B_visibility_test": True,
            "actual_direct_agreement_and_same_bank_inverse": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    option = parser.parse_args()
    if option.smoke:
        print(json.dumps(_smoke(), sort_keys=True))
    else:
        data = json.dumps(hardware_checks(), sort_keys=True, separators=(",", ":")).encode()
        print(f"hardware_checks {sha256(data).hexdigest()} over {len(data)} canonical JSON bytes")


if __name__ == "__main__":
    main()
