"""Independent scalar replay of the frozen anonymous-clause bit codec.

This module imports no producer, fitter, grader, or assessment helper.  Gold
answers use literal satisfaction; learned answers execute their stored NAND
syntax.  Truth masks are checked as metadata and never used for execution.
The public roster below is reconstructed from the frozen input specification.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random


TICKET = "BIT-DECODER-20261114-001"
FAMILY = TICKET + "-E001_atomic_codec"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
CONDITIONS = ("any_only", "varied")
FEATURE_NAMES = (
    "is_query", "first_structural_query_representative",
    "source_positive_pair_nonempty", "source_negative_pair_nonempty",
    "source_positive_triple_nonempty", "source_negative_triple_nonempty",
    "source_equal_identity_pair_nonempty", "source_equal_identity_triple_nonempty",
    "menu_has_query_duplicates", "distinct_query_count_bit0",
    "distinct_query_count_bit1", "distinct_query_count_bit2",
)


class AuditError(ValueError):
    """An artifact or claimed result disagrees with the independent replay."""


def require(condition, explanation):
    if not condition:
        raise AuditError(explanation)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit(value, label="bit"):
    require(type(value) is int and value in (0, 1), f"Invalid {label}: {value!r}")
    return value


def eval_expr(expr, values, actions=None):
    """Execute only NAND, input copies and constants, with no lookup shortcut."""
    require(isinstance(expr, list) and expr, "An expression must be a nonempty JSON list")
    tag = expr[0]
    if tag == "const":
        require(len(expr) == 2, "Malformed constant")
        if actions is not None:
            actions["CONST"] += 1
        return bit(expr[1], "constant")
    if tag == "input":
        require(len(expr) == 2 and type(expr[1]) is int, "Malformed input copy")
        require(0 <= expr[1] < len(values), "Input copy outside its declared inputs")
        if actions is not None:
            actions["READ"] += 1
        return bit(values[expr[1]], "input")
    require(tag == "NAND" and len(expr) == 3, f"Forbidden or malformed action: {tag!r}")
    left = eval_expr(expr[1], values, actions)
    # Identical operands are computed once and copied within this NAND node.
    if expr[1] == expr[2]:
        right = left
        if actions is not None:
            actions["COPY"] += 1
    else:
        right = eval_expr(expr[2], values, actions)
    if actions is not None:
        actions["NAND"] += 1
    return 1 - left * right


def nand_cost(expr):
    """Tree cost, except a node may COPY an identical operand it just computed."""
    tag = expr[0]
    if tag in ("const", "input"):
        return 0
    require(tag == "NAND" and len(expr) == 3, "Malformed NAND expression")
    return 1 + nand_cost(expr[1]) + (0 if expr[1] == expr[2] else nand_cost(expr[2]))


def validate_program(program, inputs):
    require(isinstance(program, dict), "Program must be a JSON object")
    require(set(program) == {"inputs", "expr", "nand_gates", "truth_mask"},
            "Unexpected learned-program fields")
    require(program["inputs"] == inputs, "Program input arity differs from its role")
    computed = 0
    for address in range(1 << inputs):
        values = tuple((address >> i) & 1 for i in range(inputs))
        computed |= eval_expr(program["expr"], values) << address
    cost = nand_cost(program["expr"])
    require(type(program["truth_mask"]) is int and program["truth_mask"] == computed,
            "Stored truth mask disagrees with raw NAND execution")
    require(type(program["nand_gates"]) is int and program["nand_gates"] == cost,
            "Stored NAND count disagrees with admitted COPY convention")
    return {"inputs": inputs, "truth_mask": computed, "nand_gates": cost}


def validate_wiring(wiring):
    require(len(wiring) == 4, "There must be four anonymous question ports")
    for question in wiring:
        require(sorted(map(len, question)) == [2, 2, 2, 3], "Unexpected anonymous clause shape")
        for row in question:
            for pin in row:
                require(type(pin) is int and 1 <= abs(pin) <= 9, "Invalid signed raw occurrence")


def raw_answers(wiring, raw):
    """Independent CNF satisfaction on the nine raw source cells."""
    require(type(raw) is int and 0 <= raw < 512, "Expected a raw nine-bit table")
    answers = []
    for question in wiring:
        answer = 1
        for row in question:
            met = False
            for literal in row:
                value = (raw >> (abs(literal) - 1)) & 1
                if (value == 1) == (literal > 0):
                    met = True
                    break
            if not met:
                answer = 0
                break
        answers.append(answer)
    return tuple(answers)


def question_key(question):
    """Public syntactic equality ignores only pin and clause ordering."""
    return tuple(sorted(tuple(sorted(row)) for row in question))


class FrozenCodec:
    """Independent policy executor: public plans, scalar NAND, literal tuples.

    The sole cache is indexed by public signed clauses and contains public
    addresses/flags only.  `receive` has no raw-source or oracle argument.
    """

    def __init__(self, checkpoint):
        self.checkpoint = json.loads(json.dumps(checkpoint))
        require(set(self.checkpoint) <= {"schema_version", "parser", "sender", "missing_source", "routing"},
                "Unexpected checkpoint data may be a forbidden side channel")
        require(self.checkpoint.get("schema_version") == 1, "Unsupported checkpoint schema")
        parser = self.checkpoint["parser"]
        require(set(parser) == {"literal", "clause", "question", "clause_initial", "question_initial"},
                "Unexpected parser fields")
        self.program_checks = {}
        for role in ("literal", "clause", "question"):
            self.program_checks[role] = validate_program(parser[role], 2)
            require(self.program_checks[role]["nand_gates"] <= 5, "Binary parser exceeded the five-NAND grammar")
        for field in ("clause_initial", "question_initial"):
            bit(parser[field], field)
        sender = self.checkpoint["sender"]
        require(set(sender) == {"feature_names", "emit"}, "Unexpected sender fields")
        require(tuple(sender["feature_names"]) == FEATURE_NAMES, "The public feature order differs")
        self.program_checks["emit"] = validate_program(sender["emit"], 12)
        require(self.program_checks["emit"]["nand_gates"] <= 3, "Sender exceeded the three-NAND grammar")
        bit(self.checkpoint["missing_source"], "missing-source default")
        self._public_plans = {}

    def plan(self, wiring):
        validate_wiring(wiring)
        wiring = tuple(tuple(tuple(row) for row in question) for question in wiring)
        if wiring in self._public_plans:
            return self._public_plans[wiring]
        keys = tuple(question_key(question) for question in wiring)
        distinct = len(set(keys))
        common = (int(distinct < 4), distinct & 1, distinct >> 1 & 1, distinct >> 2 & 1)
        rows = []
        for source in range(1, 10):
            pos_pair = neg_pair = pos_three = neg_three = equal_pair = equal_three = False
            for question in wiring:
                for clause in question:
                    if source in clause:
                        if len(clause) == 2:
                            pos_pair = True
                        else:
                            pos_three = True
                    if -source in clause:
                        if len(clause) == 2:
                            neg_pair = True
                        else:
                            neg_three = True
                    if all(abs(pin) == source for pin in clause):
                        if len(clause) == 2:
                            equal_pair = True
                        else:
                            equal_three = True
            rows.append((0, 0, *map(int, (pos_pair, neg_pair, pos_three, neg_three, equal_pair, equal_three)), *common))
        for port in range(4):
            rows.append((1, int(keys.index(keys[port]) == port), 0, 0, 0, 0, 0, 0, *common))
        actions = Counter({"PUBLIC_LITERAL_READ": sum(len(row) for q in wiring for row in q),
                           "PUBLIC_QUESTION_IDENTITIES": 4, "PUBLIC_DISTINCT_COUNT": 1})
        slots = []
        for index, features in enumerate(rows):
            emit = eval_expr(self.checkpoint["sender"]["emit"]["expr"], features, actions)
            actions["WRITE"] += 1
            if emit:
                slots.append(("source", index) if index < 9 else ("query", index - 9))
        source_slots = [slots.index(("source", source)) if ("source", source) in slots else None
                        for source in range(9)]
        query_slots = []
        for port in range(4):
            candidates = [slot for slot, (kind, index) in enumerate(slots)
                          if kind == "query" and keys[index] == keys[port]]
            query_slots.append(candidates[0] if candidates else None)
        plan = {"width": len(slots), "slots": [{"kind": kind, "index": index} for kind, index in slots],
                "source_slots": source_slots, "query_slots": query_slots, "feature_rows": tuple(rows),
                "cold_public_actions": dict(sorted(actions.items())), "public_cache_hit": False}
        self._public_plans[wiring] = plan
        return plan

    def _question(self, question, read, actions=None):
        parser = self.checkpoint["parser"]
        state = parser["question_initial"]
        if actions is not None:
            actions.update({"CONST": 1, "WRITE": 1})
        for clause in question:
            row_state = parser["clause_initial"]
            if actions is not None:
                actions.update({"CONST": 1, "WRITE": 1})
            for literal in clause:
                if actions is not None:
                    actions["PUBLIC_READ"] += 2
                value = read(abs(literal) - 1)
                signed = eval_expr(parser["literal"]["expr"], (value, int(literal < 0)), actions)
                row_state = eval_expr(parser["clause"]["expr"], (row_state, signed), actions)
                if actions is not None:
                    actions["WRITE"] += 1
            state = eval_expr(parser["question"]["expr"], (state, row_state), actions)
            if actions is not None:
                actions["WRITE"] += 1
        return state

    def send(self, wiring, raw, actions=None):
        plan = self.plan(wiring)  # Public commitment before accessing the data.
        require(type(raw) is int and 0 <= raw < 512, "Expected nine raw bits")

        def read(source):
            if actions is not None:
                actions["READ"] += 1
            return raw >> source & 1

        payload = []
        for slot in plan["slots"]:
            value = read(slot["index"]) if slot["kind"] == "source" else self._question(wiring[slot["index"]], read, actions)
            payload.append(value)
            if actions is not None:
                actions["WRITE"] += 1
        return tuple(payload)

    def receive(self, wiring, payload, port, actions=None):
        plan = self.plan(wiring)
        require(type(payload) is tuple and len(payload) == plan["width"], "Packet is truncated or over-wide")
        for value in payload:
            bit(value, "physical packet bit")
        require(type(port) is int and 0 <= port < 4, "Invalid delayed port")
        query_slot = plan["query_slots"][port]
        if query_slot is not None:
            if actions is not None:
                actions.update({"READ": 1, "COPY": 1, "WRITE": 1})
            return payload[query_slot]

        def read(source):
            slot = plan["source_slots"][source]
            if slot is None:
                if actions is not None:
                    actions["CONST"] += 1
                return self.checkpoint["missing_source"]
            if actions is not None:
                actions["READ"] += 1
            return payload[slot]

        answer = self._question(wiring[port], read, actions)
        if actions is not None:
            actions["WRITE"] += 1
        return answer


def codebook(wiring):
    answers = tuple(raw_answers(wiring, raw) for raw in range(512))
    patterns = set(answers)
    omissions = [j for j in range(4)
                 if len({answer[:j] + answer[j + 1:] for answer in patterns}) == len(patterns)]
    functions = {tuple(answer[j] for answer in answers) for j in range(4)}
    nonconstant = {function for function in functions if len(set(function)) == 2}
    return {"answers": answers, "patterns": patterns, "copy_only_width": len(nonconstant),
            "minimum": (len(patterns) - 1).bit_length(), "recoverable_omissions": omissions,
            "essential_sources": [j for j in range(9)
                                  if any(answers[n] != answers[n ^ (1 << j)] for n in range(512))]}


def omitted_source_witness(wiring, omitted):
    """Pin every other raw source, then expose a distinction lost by omission."""
    require(type(omitted) is int and 0 <= omitted < 9, "Invalid omitted source")
    for raw in range(512):
        if raw & (1 << omitted):
            continue
        other = raw | (1 << omitted)
        first, second = raw_answers(wiring, raw), raw_answers(wiring, other)
        if first != second:
            return {"source": omitted, "raw_masks": [raw, other],
                    "same_other_eight_bits": True, "answers": [first, second]}
    return None


def measure_channel(wiring, send, receive):
    """Enumerate physical messages; `receive` accepts only (packet, port).

    Wrong answers and over-wide messages are outcomes.  Nonbit messages and a
    source-dependent physical width violate the channel contract and reject.
    """
    book = codebook(wiring)
    packets, decoded, widths = [], {}, Counter()
    packet_truths, answer_packets = defaultdict(set), defaultdict(set)
    prefix_examples = {}
    first_error = prefix_collision = None
    right = [0] * 4
    right_odd = exact = 0
    transcript = bytearray()
    for raw, truth in enumerate(book["answers"]):
        payload = send(raw)
        require(type(payload) is tuple, "The physical payload must be a tuple")
        for value in payload:
            bit(value, "physical payload bit")
        widths[len(payload)] += 1
        packets.append(payload)
        transcript.extend([len(payload), *payload])
        if payload not in decoded:
            result = tuple(receive(payload, port) for port in range(4))
            for value in result:
                bit(value, "receiver answer")
            decoded[payload] = result
        result = decoded[payload]
        packet_truths[payload].add(truth)
        answer_packets[truth].add(payload)
        prefix = payload[:3]
        previous = prefix_examples.setdefault(prefix, (raw, truth))
        if prefix_collision is None and previous[1] != truth:
            prefix_collision = {"raw_masks": [previous[0], raw], "prefix": prefix,
                                "answers": [previous[1], truth]}
        for port in range(4):
            hit = result[port] == truth[port]
            right[port] += hit
            right_odd += hit and raw.bit_count() % 2 == 1
        exact += result == truth
        if first_error is None and result != truth:
            first_error = {"raw_mask": raw, "packet": payload, "target": truth, "decoded": result}
    require(len(widths) == 1, f"Source-dependent physical width: {dict(widths)}")
    width = next(iter(widths))
    return {
        "minimum": book["minimum"], "width": width, "answer_patterns": len(book["patterns"]),
        "distinct_packets": len(decoded), "correct_by_port": right, "correct_bits": sum(right),
        "correct_vectors": exact, "correct_odd_bits": right_odd,
        "packet_collisions": sum(len(values) > 1 for values in packet_truths.values()),
        "answer_groups_with_multiple_packets": sum(len(values) > 1 for values in answer_packets.values()),
        "physical_messages_sha256": hashlib.sha256(transcript).hexdigest(),
        "optimal_and_exact": exact == 512 and width == book["minimum"],
        "first_error": first_error, "recoverable_answer_port_omissions": book["recoverable_omissions"],
        "first_collision_after_three_bits": prefix_collision,
        "essential_sources": book["essential_sources"],
        "copy_only_distinct_nonconstant_query_bits": book["copy_only_width"],
        "pinned_source_witnesses": [w for j in book["essential_sources"]
                                    if (w := omitted_source_witness(wiring, j)) is not None],
    }


def summarize(rows):
    result = {}
    for family in sorted({row["family"] for row in rows} | {"all"}):
        subset = [row for row in rows if family == "all" or row["family"] == family]
        result[family] = {
            "wirings": len(subset), "raw_inputs": 512 * len(subset), "queries": 2048 * len(subset),
            "correct_bits": sum(row["correct_bits"] for row in subset),
            "correct_vectors": sum(row["correct_vectors"] for row in subset),
            "odd_correct_bits": sum(row["correct_odd_bits"] for row in subset), "odd_queries": 1024 * len(subset),
            "exact_wirings": sum(row["correct_vectors"] == 512 for row in subset),
            "exact_minimum_wirings": sum(row["optimal_and_exact"] for row in subset),
            "widths": dict(sorted(Counter(row["width"] for row in subset).items())),
            "lower_bounds": dict(sorted(Counter(row["minimum"] for row in subset).items())),
        }
    return result


def paired_channels(items, sender, receiver):
    """Rewire only the public menu, preserving all nine source values."""
    lookup = {identity: wiring for identity, wiring, _ in items}
    pairs = (("any", "exactly_one"), ("matched_negative", "exactly_one"),
             ("alias", "independent"), ("xor_known", "xor_new"),
             ("stress_repeat_exactly_one", "stress_cross_exactly_one"))
    result = {}
    for old, new in pairs:
        counts, witness = Counter(), None
        for _, first, meta in items:
            if meta["family"] != old or new not in meta["partners"]:
                continue
            second = lookup[meta["partners"][new]]
            port = meta["varied_port"]
            require(all(first[j] == second[j] for j in range(4) if j != port),
                    "A matched counterfactual changed an additional question")
            if old == "matched_negative":
                require(Counter(p for row in first[port] for p in row) ==
                        Counter(p for row in second[port] for p in row),
                        "Signed-degree-matched rewire changed a signed occurrence count")
            counts["paired_wirings"] += 1
            for raw in range(512):
                y, z = raw_answers(first, raw)[port], raw_answers(second, raw)[port]
                if y == z:
                    continue
                counts["changed_true_answers"] += 1
                before, after = sender(first, raw), sender(second, raw)
                changed_answer = receiver(second, after, port)
                counts["new_answer_correct"] += changed_answer == z
                if before != after:
                    continue
                counts["same_physical_packet"] += 1
                stale = receiver(first, before, port)
                counts["same_packet_both_answers_correct"] += stale == y and changed_answer == z
                counts["stale_receiver_correct_on_same_packet"] += stale == z
                if witness is None and stale == y and changed_answer == z:
                    witness = {"raw": raw, "source_cells": meta["source_cells"], "port": port,
                               "packet": before, "old": stale, "new": changed_answer}
        result[old + "__" + new] = {"counts": dict(counts), "first_same_packet_change": witness}
    return result


def _shuffle(question, seed):
    rng = random.Random(seed)
    result = []
    for row in question:
        row = list(row)
        rng.shuffle(row)
        result.append(tuple(row))
    rng.shuffle(result)
    return tuple(result)


def _unit(source, decoys, style):
    if style == "expanded_units":
        first, second = decoys[:2]
        return [(source, first, second), (source, -first),
                (source, -second), (first, -first)]
    pads = [source] * 3 if style == "local_padding" else decoys
    return [(source,) * 3] + [(pin, -pin) for pin in pads]


def _ports(family, cells, style, variant):
    a, b, c, d = [cell + 1 for cell in cells]
    decoys = [j for j in range(1, 10) if j not in (a, b, c, d)][:3]
    singles = [_unit(j, decoys, style) for j in (a, b, c)]
    pads = [a, b, c] if style == "local_padding" else decoys
    some = [(a, b, c)] + [(j, -j) for j in pads]
    exclusions = [(-a, -b), (-a, -c), (-b, -c)]
    k = variant % 3
    if family == "repeat_any":
        return [some] * 4
    if family == "any":
        fourth = some
    elif family == "one_exclusion":
        fourth = [(a, b, c)] + [exclusions[k]] * 3
    elif family == "two_exclusions":
        fourth = [(a, b, c), exclusions[k]] + [exclusions[(k + 1) % 3]] * 2
    elif family == "exactly_one":
        fourth = [(a, b, c)] + exclusions
    elif family == "matched_negative":
        fourth = [(a, b, c), (-a, -a), (-b, -c), (-b, -c)]
    elif family in ("independent", "alias"):
        fourth = _unit(d if family == "independent" else c, decoys, style)
    elif family in ("xor_known", "xor_new"):
        operand = b if family == "xor_known" else d
        pads = [a, operand] if style == "local_padding" else decoys[:2]
        fourth = [(a, operand, operand), (-a, -operand)] + [(j, -j) for j in pads]
    else:
        raise AuditError("Unknown roster family")
    return singles + [fourth]


def _group(split, layout, cells, order, style, variant, families):
    result = []
    for family in families:
        ports = [_shuffle(q, 1301 + 43 * variant + i)
                 for i, q in enumerate(_ports(family, cells, style, variant))]
        wiring = tuple(ports[i] for i in order)
        identity = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
        metadata = {"split": split, "family": family, "layout": layout, "padding": style,
                    "source_cells": cells, "port_order": order, "varied_port": order.index(3),
                    "pair_variant": variant % 3}
        result.append((identity, wiring, metadata))
    partners = {meta["family"]: key for key, _, meta in result}
    for key, _, meta in result:
        meta["partners"] = {family: identity for family, identity in partners.items() if identity != key}
    return result


def _order(index):
    base = (2, 0, 3, 1)
    index %= 4
    return base[index:] + base[:index]


def roster():
    """Reconstruct only the public inputs; no producer functions are imported."""
    train = ("any", "one_exclusion", "two_exclusions", "independent", "alias", "repeat_any")
    core = ("any", "exactly_one", "independent", "matched_negative")
    extra = core + ("alias", "repeat_any", "xor_known", "xor_new")
    result = {"train": [], "held": [], "stress": []}
    for i in range(6):
        cells = tuple((j + i) % 9 for j in (0, 2, 6, 8))
        style = ("local_padding", "tautological_decoys")[i % 2]
        result["train"].extend(_group("train", f"training-{i}", cells, _order(i), style, i, train))
    for i, order in enumerate(permutations(range(4))):
        result["held"].extend(_group("held", f"port-permutation-{i}", (0, 1, 4, 7),
                                     order, "local_padding", 9, core))
    for i in range(9):
        cells = tuple((j + i) % 9 for j in (0, 2, 4, 8))
        style = ("local_padding", "tautological_decoys", "expanded_units")[i % 3]
        result["held"].extend(_group("held", f"source-placement-{i}", cells, _order(i),
                                     style, 12 + i, extra))
    cells, order = (7, 2, 5, 0, 8, 4, 6, 1, 3), (2, 3, 0, 1)
    a, b, c, d, e, f, g, h, i = [j + 1 for j in cells]
    for family, last in (("stress_repeat_exactly_one", (a, c, b)),
                         ("stress_cross_exactly_one", (a, d, g))):
        questions = []
        for slot, (x, y, z) in enumerate(((a, b, c), (d, e, f), (g, h, i), last)):
            questions.append(_shuffle([(x, y, z), (-x, -y), (-x, -z), (-y, -z)], 3413 + slot))
        wiring = tuple(questions[j] for j in order)
        key = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
        result["stress"].append((key, wiring, {
            "split": "stress", "family": family, "layout": "four-composed-questions", "padding": "composed",
            "source_cells": cells, "port_order": order, "varied_port": order.index(3), "pair_variant": 0}))
    for key, _, meta in result["stress"]:
        meta["partners"] = {ref["family"]: identity for identity, _, ref in result["stress"] if identity != key}
    return result


def intended_answers(meta, raw):
    """Closed-form check of the generated inputs, independent of clause folds."""
    values = tuple(raw >> source & 1 for source in meta["source_cells"])
    family = meta["family"]
    if meta["split"] == "stress":
        a, b, c, d, e, f, g, h, i = values
        last = a + b + c == 1 if family == "stress_repeat_exactly_one" else a + d + g == 1
        logical = (a + b + c == 1, d + e + f == 1, g + h + i == 1, last)
    else:
        a, b, c, d = values
        if family == "repeat_any":
            return (int(bool(a or b or c)),) * 4
        k = meta["pair_variant"]
        sums = (a + b, a + c, b + c)
        some = bool(a or b or c)
        fourth = {
            "any": some, "one_exclusion": some and sums[k] < 2,
            "two_exclusions": some and sums[k] < 2 and sums[(k + 1) % 3] < 2,
            "exactly_one": a + b + c == 1, "matched_negative": not a and b + c == 1,
            "independent": d, "alias": c, "xor_known": a ^ b, "xor_new": a ^ d,
        }[family]
        logical = (a, b, c, fourth)
    return tuple(int(logical[port]) for port in meta["port_order"])


def validate_roster(panels):
    require({name: len(rows) for name, rows in panels.items()} == {"train": 36, "held": 168, "stress": 2},
            "Declared wiring panel cardinalities changed")
    identities, raw_wirings = set(), set()
    checked = 0
    for items in panels.values():
        for identity, wiring, meta in items:
            validate_wiring(wiring)
            require(identity not in identities and wiring not in raw_wirings, "Repeated raw wiring or identity")
            identities.add(identity)
            raw_wirings.add(wiring)
            for raw in range(512):
                require(raw_answers(wiring, raw) == intended_answers(meta, raw),
                        f"Raw clauses disagree with the stated test at {identity}, input {raw}")
                checked += 1
    return {"cardinalities": {name: len(rows) for name, rows in panels.items()},
            "raw_literal_vs_closed_form_cases": checked,
            "unique_raw_wirings": len(raw_wirings)}


def evaluate_menu(sender, receiver, item):
    identity, wiring, meta = item
    row = measure_channel(wiring, lambda raw: sender.send(wiring, raw),
                          lambda payload, port: receiver.receive(wiring, payload, port))
    row.update({"id": identity, "family": meta["family"], "padding": meta["padding"], "layout": meta["layout"],
                "source_cells": meta["source_cells"], "varied_port": meta["varied_port"], "ports": meta["port_order"],
                "public_plan": sender.plan(wiring)})
    # Data-dependent NAND branching is forbidden.  These counts are invariant
    # across raw values; sample two opposite raw tables as an executable guard.
    send_actions, receive_actions = Counter(), []
    payload = sender.send(wiring, 0, send_actions)
    for port in range(4):
        actions = Counter()
        receiver.receive(wiring, payload, port, actions)
        receive_actions.append(dict(actions))
    second = Counter()
    payload2 = sender.send(wiring, 511, second)
    require(second == send_actions, "Source data changed the sender's primitive execution count")
    for port, expected in enumerate(receive_actions):
        actions = Counter()
        receiver.receive(wiring, payload2, port, actions)
        require(dict(actions) == expected, "Packet values changed primitive execution count")
    row["data_actions_per_send"] = dict(send_actions)
    row["data_actions_per_delayed_port"] = receive_actions
    return row


def assert_equal(actual, expected, label):
    require(canonical(actual) == canonical(expected), f"Independent disagreement: {label}")


def mechanism_checks(name, checkpoint, panels, rows):
    """Cheap channel falsifiers and a post-hoc exact simpler-policy account."""
    sender, receiver = FrozenCodec(checkpoint), FrozenCodec(checkpoint)
    emit = checkpoint["sender"]["emit"]["expr"]
    for address in range(4096):
        flags = tuple(address >> j & 1 for j in range(12))
        # This account is read from the frozen syntax, not used to fit/rank it.
        simple = flags[4] if name == "any_only" else (flags[1] * flags[8] or flags[4] * flags[11])
        require(eval_expr(emit, flags) == int(simple), "Post-hoc sender account is not exactly equivalent")
    report = {"post_hoc_sender_rule":
              "positive triple occurrence" if name == "any_only" else
              "first structural query representative AND menu duplicate; OR positive triple occurrence AND four distinct questions",
              "equivalent_on_all_4096_flag_vectors": True}
    core = [row for row in rows if row["family"] in ("any", "exactly_one", "independent", "matched_negative")]
    require(all(all(slot["kind"] == "source" for slot in row["public_plan"]["slots"]) for row in core),
            "A core result was explained by sending its computed target answer")
    report["held_core_menus_sending_only_raw_sources"] = len(core)
    report["held_core_menus"] = len(core)
    _, wiring, meta = next(item for item in panels["held"]
                           if item[2]["family"] == "independent" and item[2]["layout"] == "port-permutation-0")
    source = meta["source_cells"][3]
    first, second = sender.send(wiring, 0), sender.send(wiring, 1 << source)
    answers = [tuple(receiver.receive(wiring, payload, j) for j in range(4)) for payload in (first, second)]
    require(sum(a != b for a, b in zip(first, second, strict=True)) == 1, "Independent fourth source was not a physical bit")
    require(answers[0] != answers[1], "The receiver ignored the physical independent distinction")
    report["pinned_independent_source"] = {"raw_masks": [0, 1 << source], "source": source,
                                            "packets": [first, second], "answers": answers}
    rejected = []
    for label, payload in (("truncated", first[:-1]), ("extra", first + (0,)),
                           ("nonbit", (2,) + first[1:]), ("scalar_instead_of_tuple", 0)):
        try:
            receiver.receive(wiring, payload, 0)
        except AuditError:
            rejected.append(label)
        else:
            raise AuditError("Malformed physical packet accepted: " + label)
    for role in ("literal", "clause", "question", "emit"):
        damaged = json.loads(json.dumps(checkpoint))
        record = damaged["sender"][role] if role == "emit" else damaged["parser"][role]
        record["truth_mask"] ^= 1
        try:
            FrozenCodec(damaged)
        except AuditError:
            rejected.append("corrupt_" + role + "_truth")
        else:
            raise AuditError("Corrupted learned-program metadata accepted")
    damaged = json.loads(json.dumps(checkpoint))
    damaged["parser"]["question"] = {"inputs": 2, "expr": ["const", 0], "nand_gates": 0, "truth_mask": 0}
    wrong_sender, wrong_receiver = FrozenCodec(damaged), FrozenCodec(damaged)
    wrong = measure_channel(wiring, lambda raw: wrong_sender.send(wiring, raw),
                            lambda packet, port: wrong_receiver.receive(wiring, packet, port))
    require(wrong["correct_vectors"] < 512, "A semantically wrong but well-formed gate escaped answer grading")
    report["mutations_rejected"] = rejected
    report["valid_zero_question_gate_correct_vectors"] = wrong["correct_vectors"]
    return report


def check_bindings(out):
    receipt_path = out / "checkpoint_bindings.json"
    binding = json.loads(receipt_path.read_bytes())
    require(set(binding) == {"sources_frozen", "training_output", "checkpoints", "assessment_requires_both"},
            "Unexpected checkpoint binding schema")
    require(binding["assessment_requires_both"] is True, "Both fits must be frozen before assessment")
    require(binding["training_output"] == file_digest(out / "results.jsonl"), "Training output changed after freeze")
    require(binding["sources_frozen"] == file_digest(out / "freeze.json"), "Source freeze receipt changed")
    freeze = json.loads((out / "freeze.json").read_bytes())
    require(freeze["before_fits"] is True and tuple(freeze["conditions"]) == CONDITIONS, "Invalid pre-fit freeze declaration")
    for relative, expected in freeze["files_sha256"].items():
        path = ROOT / relative
        require(path.resolve().is_relative_to(ROOT) and file_digest(path) == expected,
                f"Source differs from the pre-fit freeze: {relative}")
    require(set(binding["checkpoints"]) == set(CONDITIONS), "Missing or additional fitted condition")
    records = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines() if line.strip()]
    require(len(records) == 2 and all(row.get("status") == "ok" for row in records),
            "The two successful training rows are not complete")
    by_name = {}
    for row in records:
        name = row["case"]
        require(name in CONDITIONS and name not in by_name and row["result"]["condition"] == name,
                "Training condition identity mismatch")
        result = row["result"]
        require(datetime.fromisoformat(row["finished_at"]) >= datetime.fromisoformat(freeze["utc"]),
                "A training row predates the declared pre-fit freeze")
        job = "experiments/" + TICKET + "/" + FAMILY + "/job.py"
        source = "experiments/" + TICKET + "/" + FAMILY + "/codec.py"
        require(row["job_sha"] == freeze["files_sha256"][job] and
                result["fit"]["codec_sha256"] == freeze["files_sha256"][source],
                "Training reports different producer code from the pre-fit freeze")
        path = out / (name + "_checkpoint.json")
        require(file_digest(path) == binding["checkpoints"][name] == result["checkpoint_sha256"],
                "Frozen checkpoint bytes differ from training record")
        checkpoint = json.loads(path.read_bytes())
        assert_equal(checkpoint, result["checkpoint"], name + " checkpoint")
        require(path.read_bytes() == canonical(checkpoint), "Checkpoint is not the frozen canonical serialization")
        by_name[name] = result
    return binding, by_name


def audit(out):
    """Replay both frozen policies without invoking their producer or trainer."""
    out = Path(out)
    binding, training = check_bindings(out)
    recorded = json.loads((out / "result.json").read_bytes())
    assert_equal(recorded["checkpoint_bindings"], binding, "assessment checkpoint bindings")
    panels = roster()
    freeze = json.loads((out / "freeze.json").read_bytes())
    assert_equal({name: digest(items) for name, items in panels.items()}, freeze["public_panels_sha256"],
                 "independently reconstructed public panels")
    panel_check = validate_roster(panels)
    conditions, compared_menu_rows = {}, 0
    for name in CONDITIONS:
        checkpoint = training[name]["checkpoint"]
        sender, receiver = FrozenCodec(checkpoint), FrozenCodec(checkpoint)
        trained = [item for item in panels["train"] if name == "varied" or item[2]["family"] == "any"]
        train_masks = tuple(raw for raw in range(512) if raw.bit_count() % 2 == 0)
        examples = []
        for _, wiring, _ in trained:
            gold = tuple(raw_answers(wiring, raw) for raw in train_masks)
            examples.append({"wiring": wiring, "answers": tuple(sum(answer[j] << lane for lane, answer in enumerate(gold))
                                                                for j in range(4))})
        assert_equal(training[name]["training_wirings"], [item[0] for item in trained], name + " training roster")
        require(training[name]["training_inputs"] == 256, "Training input parity split changed")
        require(training[name]["training_examples_sha256"] == digest(examples), "Training labels or ordering changed")
        part = {"programs": sender.program_checks}
        for split, items in panels.items():
            rows = [evaluate_menu(sender, receiver, item) for item in items]
            expected_rows = recorded["conditions"][name][split]["menus"]
            require(len(expected_rows) == len(rows), "Assessment menu count differs")
            for row, expected in zip(rows, expected_rows, strict=True):
                for key in expected:
                    require(key in row, f"Unrecognized assessment output field: {key}")
                    assert_equal(row[key], expected[key], f"{name}/{split}/{row['id']}/{key}")
                compared_menu_rows += 1
            summary = summarize(rows)
            assert_equal(summary, recorded["conditions"][name][split]["families"], name + "/" + split + " totals")
            part[split] = {"families": summary, "menus": rows}
        part["matched"] = paired_channels(panels["held"] + panels["stress"], sender.send, receiver.receive)
        assert_equal(part["matched"], recorded["conditions"][name]["matched"], name + " matched rewiring")
        trained_ids = {item[0] for item in trained}
        fit_rows = [row for row in part["train"]["menus"] if row["id"] in trained_ids]
        wrong = sum(1024 - (row["correct_bits"] - row["correct_odd_bits"]) for row in fit_rows)
        transmitted = 256 * sum(row["width"] for row in fit_rows)
        fit = training[name]["fit"]
        assert_equal({"wrong_answer_bits": wrong, "transmitted_payload_bits": transmitted},
                     {key: fit["training_loss"][key] for key in ("wrong_answer_bits", "transmitted_payload_bits")},
                     name + " scalar terminal training objective")
        require(fit["checkpoint_sha256"] == binding["checkpoints"][name], "Fit diagnostics bind a different checkpoint")
        part["training_objective_replay"] = {"wrong_answer_bits": wrong, "transmitted_payload_bits": transmitted}
        part["mechanism_checks"] = mechanism_checks(name, checkpoint, panels, part["held"]["menus"])
        conditions[name] = part
    # Recheck immutable files after all decoding; this audit never writes them.
    assert_equal(check_bindings(out)[0], binding, "post-replay frozen bindings")
    return {"ticket": TICKET, "artifact_id": TICKET + "-E001", "schema_version": 1,
            "status": "pass", "independence": "separate scalar raw NAND interpreter; no producer imports or training",
            "checkpoint_bindings": binding, "audit_source_sha256": file_digest(__file__),
            "assessment_sha256": file_digest(out / "result.json"), "public_roster": panel_check,
            "compared_menu_rows": compared_menu_rows, "conditions": conditions,
            "limits": ["Finite public signed-clause grammar and declared wiring panel only.",
                       "No claim of a learning advantage over a supplied task-aware CNF evaluator.",
                       "Emitter search merges programs with identical outputs on training feature rows.",
                       "Sender and decoder routing, iteration, constants and copies are supplied architecture."]}


def self_test():
    """Small synthetic fixtures only; this does not fit or assess a policy."""
    inv = ["NAND", ["input", 0], ["input", 0]]
    conjunction = ["NAND", inv, inv]
    require(nand_cost(conjunction) == 2, "Identical-operand COPY cost is wrong")
    program = {"inputs": 1, "expr": inv, "nand_gates": 1, "truth_mask": 1}
    require(validate_program(program, 1)["truth_mask"] == 1, "NOT fixture failed")
    corrupted = dict(program, truth_mask=2)
    try:
        validate_program(corrupted, 1)
    except AuditError:
        pass
    else:
        raise AuditError("Corrupted NAND truth metadata was accepted")
    for malformed in (["OR", ["const", 0], ["const", 1]], ["input", 3]):
        try:
            eval_expr(malformed, (0,))
        except AuditError:
            pass
        else:
            raise AuditError("Malformed/forbidden instruction was accepted")
    # Primitive three/independent-four read controls; each question keeps the admitted shape.
    units = tuple(tuple(_unit(j, [5, 6, 7], "local_padding")) for j in (1, 2, 3, 4))
    dependent = units[:3] + (((1, 2, 3), (1, -1), (2, -2), (3, -3)),)
    for wiring, expected in ((units, 4), (dependent, 3)):
        validate_wiring(wiring)
        require(codebook(wiring)["minimum"] == expected, "Raw codebook lower bound failed")
    require(omitted_source_witness(units, 3)["raw_masks"] == [0, 8], "Pinned missing-source fixture failed")
    send_four = lambda raw: tuple(raw >> j & 1 for j in range(4))
    copy = lambda payload, port: payload[port]
    exact = measure_channel(units, send_four, copy)
    require(exact["optimal_and_exact"] and exact["correct_vectors"] == 512, "Exact physical channel failed")
    send_three = lambda raw: tuple(raw >> j & 1 for j in range(3))
    incomplete = measure_channel(units, send_three, lambda payload, port: payload[port] if port < 3 else 0)
    require(incomplete["packet_collisions"] == 8 and incomplete["correct_vectors"] == 256,
            "Three-bit independent-four collision was not preserved")
    for send in (lambda raw: (2,), lambda raw: (0,) * (1 + (raw & 1))):
        try:
            measure_channel(units, send, lambda payload, port: 0)
        except AuditError:
            pass
        else:
            raise AuditError("Malformed or source-dependent physical channel was accepted")
    return {"status": "pass", "NAND_interpreter": True, "malformed_and_corrupt_rejected": True,
            "synthetic_three_four_bit_lower_bounds": True, "pinned_missing_source": True,
            "physical_channel_and_forced_three_bit_collision": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="Write only audit.json in the supplied artifact directory")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
    else:
        result = audit(args.out)
        if args.write:
            target = args.out / "audit.json"
            target.write_bytes(canonical(result) + b"\n")
        print(json.dumps({"status": result["status"], "compared_menu_rows": result["compared_menu_rows"],
                          "held": {name: row["held"]["families"]["all"]
                                   for name, row in result["conditions"].items()}}, indent=2))
