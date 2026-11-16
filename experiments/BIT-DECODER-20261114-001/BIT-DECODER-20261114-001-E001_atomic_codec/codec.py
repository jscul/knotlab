"""Staged induction of one NAND sender/receiver from terminal training labels.

Truth-mask operations accelerate fitting only. Runtime data computations use
the selected explicit NAND expressions, constants, reads, copies and writes.
Codec instances cache public wiring plans and never retain raw data or packets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


FEATURE_NAMES = (
    "is_query", "first_structural_query_representative",
    "source_positive_pair_nonempty", "source_negative_pair_nonempty",
    "source_positive_triple_nonempty", "source_negative_triple_nonempty",
    "source_equal_identity_pair_nonempty", "source_equal_identity_triple_nonempty",
    "menu_has_query_duplicates", "distinct_query_count_bit0",
    "distinct_query_count_bit1", "distinct_query_count_bit2",
)
PARSER_RETAIN_CAP = 64
EMISSION_GATE_CAP = 3


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _tuple_expr(expr):
    if not isinstance(expr, (tuple, list)) or not expr:
        raise ValueError("A NAND expression is required")
    if expr[0] in ("input", "const") and len(expr) == 2:
        return expr[0], int(expr[1])
    if expr[0] == "NAND" and len(expr) == 3:
        return "NAND", _tuple_expr(expr[1]), _tuple_expr(expr[2])
    raise ValueError("Only NAND, input and const nodes are allowed")


def nand_gate_count(expr):
    if expr[0] in ("input", "const"):
        return 0
    return 1 + nand_gate_count(expr[1]) + (0 if expr[1] == expr[2] else nand_gate_count(expr[2]))


def _nand_eval(expr, inputs, actions=None):
    kind = expr[0]
    if kind == "input":
        if actions is not None:
            actions["READ"] += 1
        return int(inputs[expr[1]])
    if kind == "const":
        if actions is not None:
            actions["CONST"] += 1
        return int(expr[1])
    left = _nand_eval(expr[1], inputs, actions)
    if expr[1] == expr[2]:
        right = left
        if actions is not None:
            actions["COPY"] += 1
    else:
        right = _nand_eval(expr[2], inputs, actions)
    if actions is not None:
        actions["NAND"] += 1
    return 1 - (left & right)  # The one primitive NAND, not an inferred gate macro.


def _truth_mask(expr, arity):
    return sum(_nand_eval(expr, tuple((address >> bit) & 1 for bit in range(arity))) << address
               for address in range(1 << arity))


@dataclass(frozen=True)
class Node:
    mask: int
    gates: int
    expr: tuple


def _node_key(node):
    return node.gates, node.expr


def nand_catalogue(columns, universe, maximum_gates):
    """Enumerate NAND programs; no AND/OR/function identities are supplied."""
    best = {}
    leaves = [(0, ("const", 0)), (universe, ("const", 1))]
    leaves += [(mask, ("input", index)) for index, mask in enumerate(columns)]
    for mask, expr in leaves:
        if mask not in best or expr < best[mask].expr:
            best[mask] = Node(mask, 0, expr)
    levels = [sorted(best.values(), key=_node_key)]
    for cost in range(1, maximum_gates + 1):
        current = {}

        def offer(mask, expr):
            if mask in best:
                return
            if mask not in current or expr < current[mask].expr:
                current[mask] = Node(mask, cost, expr)

        for left_cost in range(cost):
            right_cost = cost - left_cost - 1
            for left in levels[left_cost]:
                for right in levels[right_cost]:
                    if left.expr <= right.expr:
                        offer(universe ^ (left.mask & right.mask), ("NAND", left.expr, right.expr))
        for child in levels[cost - 1]:
            offer(universe ^ child.mask, ("NAND", child.expr, child.expr))
        levels.append(sorted(current.values(), key=_node_key))
        best.update(current)
    nodes = sorted(best.values(), key=_node_key)
    return nodes, {"maximum_NAND_gates": maximum_gates, "functions": len(nodes),
                   "by_minimum_gates": {str(cost): len(level) for cost, level in enumerate(levels)},
                   "same_child_reuse": "evaluate once, COPY to both NAND operands",
                   "syntax_order": "recursive tuple order after commutative child ordering"}


def binary_catalogue():
    nodes, stats = nand_catalogue((0b1010, 0b1100), 0b1111, 5)
    if len(nodes) != 16 or {node.mask for node in nodes} != set(range(16)):
        raise ValueError("The NAND grammar did not supply every binary Boolean function")
    return nodes, stats


def _program_record(node, arity):
    return {"inputs": arity, "expr": node.expr, "nand_gates": node.gates,
            "truth_mask": _truth_mask(node.expr, arity)}


def _compile_program(record, arity, maximum):
    expr = _tuple_expr(record["expr"])

    def validate(node):
        if node[0] == "const":
            if node[1] not in (0, 1):
                raise ValueError("Constants must be bits")
        elif node[0] == "input":
            if not 0 <= node[1] < arity:
                raise ValueError("Input index exceeds the declared program arity")
        else:
            validate(node[1])
            validate(node[2])

    validate(expr)
    cost = nand_gate_count(expr)
    if int(record["inputs"]) != arity or int(record["nand_gates"]) != cost or cost > maximum:
        raise ValueError("Program NAND count or input arity is invalid")
    # Full emitter semantics are metadata; inference never indexes that table.
    if arity == 2 and _truth_mask(expr, 2) != int(record["truth_mask"]):
        raise ValueError("Binary program truth mask disagreed with its atomic expression")
    return expr


def _wiring(wiring):
    result = tuple(tuple(tuple(int(literal) for literal in clause) for clause in question) for question in wiring)
    if len(result) != 4:
        raise ValueError("Four public question ports are required")
    for question in result:
        if len(question) != 4 or sorted(map(len, question)) != [2, 2, 2, 3]:
            raise ValueError("Each question needs one three-pin row and three two-pin rows")
        if any(not 1 <= abs(literal) <= 9 for clause in question for literal in clause):
            raise ValueError("Signed occurrences must name source1 through source9")
    return result


def _question_identity(question):
    # Public structural identity only: preserve signs and multiplicities.
    return tuple(sorted(tuple(sorted(clause)) for clause in question))


def public_features(wiring):
    wiring = _wiring(wiring)
    identities = tuple(_question_identity(question) for question in wiring)
    first = {identity: identities.index(identity) for identity in identities}
    distinct = len(first)
    common = (int(distinct < 4), distinct & 1, (distinct >> 1) & 1, (distinct >> 2) & 1)
    counts = [[0, 0, 0, 0] for _ in range(9)]
    equal_identity = [[0, 0] for _ in range(9)]
    literal_reads = 0
    for question in wiring:
        for clause in question:
            same_identity = len({abs(literal) for literal in clause}) == 1
            for literal in clause:
                literal_reads += 1
                source = abs(literal) - 1
                counts[source][(2 if len(clause) == 3 else 0) + int(literal < 0)] += 1
                if same_identity:
                    equal_identity[source][int(len(clause) == 3)] += 1
    rows = [(0, 0, *(int(value > 0) for value in counts[source]),
             *(int(value > 0) for value in equal_identity[source]), *common) for source in range(9)]
    rows += [(1, int(first[identities[port]] == port), 0, 0, 0, 0, 0, 0, *common) for port in range(4)]
    return tuple(rows), identities, {"PUBLIC_LITERAL_READ": literal_reads,
                                     "PUBLIC_QUESTION_IDENTITIES": 4, "PUBLIC_DISTINCT_COUNT": 1}


@dataclass(frozen=True)
class Plan:
    slots: tuple
    source_slots: tuple
    query_slots: tuple
    features: tuple
    cold_actions: tuple


def _plan_from_flags(wiring, flags, feature_rows, actions=()):
    identities = tuple(_question_identity(question) for question in wiring)
    slots = tuple(("source", index) if index < 9 else ("query", index - 9)
                  for index in range(13) if (flags >> index) & 1)
    source_slots = tuple(next((slot for slot, descriptor in enumerate(slots) if descriptor == ("source", source)), None)
                         for source in range(9))
    query_slots = tuple(next((slot for slot, (kind, index) in enumerate(slots)
                             if kind == "query" and identities[index] == identities[port]), None) for port in range(4))
    return Plan(slots, source_slots, query_slots, feature_rows, tuple(actions))


def _plan_record(plan):
    return {"width": len(plan.slots), "slots": [{"kind": kind, "index": index} for kind, index in plan.slots],
            "source_slots": list(plan.source_slots), "query_slots": list(plan.query_slots),
            "feature_rows": plan.features, "cold_public_actions": dict(plan.cold_actions)}


def _scan_question(parser, question, read_source, actions):
    state = parser["question_initial"]
    actions["CONST"] += 1
    actions["WRITE"] += 1
    for clause in question:
        clause_state = parser["clause_initial"]
        actions["CONST"] += 1
        actions["WRITE"] += 1
        for literal in clause:
            actions["PUBLIC_READ"] += 2  # Supplied occurrence address and sign bit.
            value = read_source(abs(literal) - 1)
            signed = _nand_eval(parser["literal"], (value, int(literal < 0)), actions)
            clause_state = _nand_eval(parser["clause"], (clause_state, signed), actions)
            actions["WRITE"] += 1
        state = _nand_eval(parser["question"], (state, clause_state), actions)
        actions["WRITE"] += 1
    return state


def _literal_bits(values, expected_length, description):
    try:
        values = tuple(values)
    except TypeError as error:
        raise ValueError(f"{description} must be an iterable of literal bits") from error
    if len(values) != expected_length or any(type(value) not in (int, bool) or value not in (0, 1) for value in values):
        raise ValueError(f"{description} must contain exactly {expected_length} literal int/bool bits")
    return tuple(int(value) for value in values)


class Codec:
    """A frozen agent instance with a PUBLIC-ONLY cache and no data history."""

    def __init__(self, checkpoint):
        frozen = json.loads(json.dumps(checkpoint))
        if frozen["schema_version"] != 1 or tuple(frozen["sender"]["feature_names"]) != FEATURE_NAMES:
            raise ValueError("Unknown codec grammar")
        self._parser = {role: _compile_program(frozen["parser"][role], 2, 5)
                        for role in ("literal", "clause", "question")}
        for initial in ("clause_initial", "question_initial"):
            value = int(frozen["parser"][initial])
            if value not in (0, 1):
                raise ValueError("Scan initializers must be bits")
            self._parser[initial] = value
        self._emit = _compile_program(frozen["sender"]["emit"], len(FEATURE_NAMES), EMISSION_GATE_CAP)
        self._missing = int(frozen["missing_source"])
        if self._missing not in (0, 1):
            raise ValueError("The common missing-source constant must be a bit")
        self._public_cache = {}  # Wiring -> immutable plan; never values/packets.

    def _get_plan(self, wiring):
        wiring = _wiring(wiring)
        if wiring in self._public_cache:
            return wiring, self._public_cache[wiring], Counter(), True
        rows, _, public_work = public_features(wiring)
        actions = Counter(public_work)
        flags = 0
        for index, features in enumerate(rows):
            emit = _nand_eval(self._emit, features, actions)
            actions["WRITE"] += 1
            flags += emit << index
        plan = _plan_from_flags(wiring, flags, rows, tuple(sorted(actions.items())))
        self._public_cache[wiring] = plan
        return wiring, plan, actions, False

    def packet_plan(self, wiring):
        _, plan, _, hit = self._get_plan(wiring)
        return _plan_record(plan) | {"public_cache_hit": hit}

    def trace_send(self, wiring, raw):
        wiring, plan, public, hit = self._get_plan(wiring)  # Commit width before reading raw.
        if type(raw) in (int, bool):
            if not 0 <= raw < 512:
                raise ValueError("Raw masks have nine bits")
            values = tuple((raw >> source) & 1 for source in range(9))
        else:
            values = _literal_bits(raw, 9, "Raw source data")
        actions = Counter()

        def read(source):
            actions["READ"] += 1
            return values[source]

        payload = []
        for kind, index in plan.slots:
            value = read(index) if kind == "source" else _scan_question(self._parser, wiring[index], read, actions)
            payload.append(value)
            actions["WRITE"] += 1
        return {"bits": tuple(payload), "width": len(payload), "data_actions": dict(actions),
                "public_actions": dict(public), "actions": dict(actions + public), "public_cache_hit": hit}

    def send(self, wiring, raw):
        return self.trace_send(wiring, raw)["bits"]

    def trace_receive(self, wiring, bits, delayed_port):
        wiring, plan, public, hit = self._get_plan(wiring)
        bits = _literal_bits(bits, len(plan.slots), "Physical packet")
        if type(delayed_port) is not int or delayed_port not in range(4):
            raise ValueError("A literal packet of public width and one delayed port are required")
        actions = Counter()
        query_slot = plan.query_slots[delayed_port]
        if query_slot is not None:
            answer = bits[query_slot]
            actions.update({"READ": 1, "COPY": 1, "WRITE": 1})
            route = {"kind": "query_copy", "slot": query_slot}
        else:
            def read(source):
                slot = plan.source_slots[source]
                if slot is None:
                    actions["CONST"] += 1
                    return self._missing
                actions["READ"] += 1
                return bits[slot]

            answer = _scan_question(self._parser, wiring[delayed_port], read, actions)
            actions["WRITE"] += 1
            route = {"kind": "source_readout"}
        return {"answer": answer, "width": len(bits), "data_actions": dict(actions),
                "public_actions": dict(public), "actions": dict(actions + public),
                "public_cache_hit": hit, "route": route}

    def receive(self, wiring, bits, delayed_port):
        return self.trace_receive(wiring, bits, delayed_port)["answer"]


def packet_plan(checkpoint, wiring):
    return Codec(checkpoint).packet_plan(wiring)


def send(checkpoint, wiring, raw):
    return Codec(checkpoint).send(wiring, raw)


def receive(checkpoint, wiring, bits, delayed_port):
    return Codec(checkpoint).receive(wiring, bits, delayed_port)


def trace_send(checkpoint, wiring, raw):
    return Codec(checkpoint).trace_send(wiring, raw)


def trace_receive(checkpoint, wiring, bits, delayed_port):
    return Codec(checkpoint).trace_receive(wiring, bits, delayed_port)


def _lut(mask, first, second, universe):
    """Fit-only evaluation of an enumerated NAND expression's four truth rows."""
    output = 0
    if mask & 1:
        output |= (universe ^ first) & (universe ^ second)
    if mask & 2:
        output |= first & (universe ^ second)
    if mask & 4:
        output |= (universe ^ first) & second
    if mask & 8:
        output |= first & second
    return output


def _unary_rows(mask, value, sign, universe):
    low, high = (mask >> (2 * sign)) & 1, (mask >> (2 * sign + 1)) & 1
    if low == high:
        return universe if low else 0
    return value if high else universe ^ value


@dataclass(frozen=True)
class Parser:
    literal: Node
    clause: Node
    question: Node
    clause_initial: int
    question_initial: int

    @property
    def gates(self):
        return self.literal.gates + self.clause.gates + self.question.gates

    @property
    def syntax(self):
        return (self.literal.expr, self.clause.expr, self.question.expr,
                self.clause_initial, self.question_initial)


def _parser_record(parser):
    return {role: _program_record(getattr(parser, role), 2) for role in ("literal", "clause", "question")} | {
        "clause_initial": parser.clause_initial, "question_initial": parser.question_initial}


def _parse_packed(parser, question, columns, universe):
    state = universe if parser.question_initial else 0
    for clause in question:
        clause_state = universe if parser.clause_initial else 0
        for literal in clause:
            value = _unary_rows(parser.literal.mask, columns[abs(literal) - 1], int(literal < 0), universe)
            clause_state = _lut(parser.clause.mask, clause_state, value, universe)
        state = _lut(parser.question.mask, state, clause_state, universe)
    return state


def _fit_parsers(nodes, cases, columns, universe):
    questions = []
    question_ids = {}
    targets = []
    for case in cases:
        for question, answer in zip(case["wiring"], case["answers"], strict=True):
            if question not in question_ids:
                question_ids[question] = len(questions)
                questions.append(question)
                targets.append([])
            targets[question_ids[question]].append(answer)
    clauses = list(dict.fromkeys(clause for question in questions for clause in question))
    clause_ids = {clause: index for index, clause in enumerate(clauses)}
    question_clause_ids = [tuple(clause_ids[clause] for clause in question) for question in questions]
    minimum, count, retained, best_simple, preview, scored = None, 0, [], None, [], 0
    trace = []
    for literal in nodes:
        signed = {value: _unary_rows(literal.mask, columns[abs(value) - 1], int(value < 0), universe)
                  for value in (*range(-9, 0), *range(1, 10))}
        for clause in nodes:
            for clause_initial in (0, 1):
                clause_values = []
                for pins in clauses:
                    state = universe if clause_initial else 0
                    for pin in pins:
                        state = _lut(clause.mask, state, signed[pin], universe)
                    clause_values.append(state)
                for question in nodes:
                    for question_initial in (0, 1):
                        parser = Parser(literal, clause, question, clause_initial, question_initial)
                        outputs, wrong = [], 0
                        for ids, labels in zip(question_clause_ids, targets, strict=True):
                            state = universe if question_initial else 0
                            for index in ids:
                                state = _lut(question.mask, state, clause_values[index], universe)
                            outputs.append(state)
                            wrong += sum((state ^ answer).bit_count() for answer in labels)
                        scored += 1
                        if minimum is None or wrong < minimum:
                            minimum, count, retained, best_simple, preview = wrong, 0, [], None, []
                            trace.append({"candidate": scored, "wrong_answer_bits": wrong})
                        if wrong == minimum:
                            count += 1
                            item = (parser, tuple(outputs))
                            if best_simple is None or (parser.gates, parser.syntax) < (best_simple[0].gates, best_simple[0].syntax):
                                best_simple = item
                            if count <= PARSER_RETAIN_CAP:
                                retained.append(item)
                            preview.append(item)
                            preview.sort(key=lambda row: (row[0].gates, row[0].syntax))
                            del preview[8:]
    restricted = count > PARSER_RETAIN_CAP
    retained = [best_simple] if restricted else retained
    retained.sort(key=lambda row: (row[0].gates, row[0].syntax))
    return retained, questions, question_ids, {
        "candidates_scored": scored, "minimum_wrong_answer_bits": minimum,
        "minimum_error_parsers": count, "retention_cap": PARSER_RETAIN_CAP,
        "parsers_retained_for_compression": len(retained),
        "fixed_minimum_NAND_tie_selected_first": restricted,
        "initial_payload_bits_per_input_wiring": 4,
        "initial_sender": "copy all four query values computed by the candidate parser",
        "minimum_error_parser_preview": [{"parser": _parser_record(row[0]), "NAND_size": row[0].gates} for row in preview],
        "improvement_trace": trace, "unique_questions": len(questions), "unique_clauses": len(clauses),
    }


def _emission_catalogue(cases):
    rows = [row for case in cases for row in public_features(case["wiring"])[0]]
    columns = tuple(sum(features[index] << bit for bit, features in enumerate(rows)) for index in range(len(FEATURE_NAMES)))
    universe = (1 << len(rows)) - 1
    nodes, stats = nand_catalogue(columns, universe, EMISSION_GATE_CAP)
    available = {node.mask for node in nodes}
    baselines = {"none": 0, "all_candidates": universe, "all_query_candidates": columns[0],
                 "all_source_candidates": universe ^ columns[0]}
    if any(mask not in available for mask in baselines.values()):
        raise ValueError("The emitter language lost a declared baseline alternative")
    stats |= {"feature_names": FEATURE_NAMES, "training_descriptor_rows": len(rows),
              "semantic_collapse_domain": "public candidate-feature rows from training wiring only",
              "baseline_alternatives_present": list(baselines)}
    return nodes, stats


def _plans_for_node(node, cases):
    return tuple(_plan_from_flags(case["wiring"], (node.mask >> (13 * index)) & ((1 << 13) - 1), ())
                 for index, case in enumerate(cases))


def _checkpoint(parser, emitter, missing):
    checkpoint = {"schema_version": 1, "parser": _parser_record(parser),
                  "sender": {"feature_names": FEATURE_NAMES, "emit": _program_record(emitter, len(FEATURE_NAMES))},
                  "missing_source": missing,
                  "routing": "public signed-literal/clause multiset identity; first emitted equivalent query, else source scan"}
    return json.loads(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")))


def _verify_training(checkpoint, cases, raw_masks):
    sender, receiver = Codec(checkpoint), Codec(checkpoint)  # Independent caches; no raw/packet state shared.
    wrong, bits = 0, 0
    for case in cases:
        wiring = case["wiring"]
        for lane, raw in enumerate(raw_masks):
            payload = sender.send(wiring, raw)
            bits += len(payload)
            for port in range(4):
                answer = receiver.receive(wiring, payload, port)
                wrong += answer != ((case["answers"][port] >> lane) & 1)
    return {"wrong_answer_bits": int(wrong), "transmitted_payload_bits": bits,
            "terminal_answer_bits": len(cases) * len(raw_masks) * 4,
            "independent_sender_receiver_instances": True}


def fit(cases, raw_masks):
    started = time.perf_counter()
    raw_masks = tuple(map(int, raw_masks))
    if not raw_masks or len(set(raw_masks)) != len(raw_masks) or any(not 0 <= value < 512 for value in raw_masks):
        raise ValueError("Unique nine-bit training raw masks are required")
    universe = (1 << len(raw_masks)) - 1
    cases = tuple({"wiring": _wiring(case["wiring"]), "answers": tuple(map(int, case["answers"]))} for case in cases)
    if not cases or any(len(case["answers"]) != 4 or any(not 0 <= answer <= universe for answer in case["answers"]) for case in cases):
        raise ValueError("Each training wiring needs four aligned packed terminal-answer columns")
    columns = tuple(sum(((raw >> source) & 1) << lane for lane, raw in enumerate(raw_masks)) for source in range(9))
    binary, binary_stats = binary_catalogue()
    parser_started = time.perf_counter()
    retained, questions, question_ids, parser_stats = _fit_parsers(binary, cases, columns, universe)
    parser_seconds = time.perf_counter() - parser_started
    emitter_started = time.perf_counter()
    emitters, emitter_stats = _emission_catalogue(cases)
    plans = [_plans_for_node(node, cases) for node in emitters]
    payload_costs = [sum(len(plan.slots) for plan in group) * len(raw_masks) for group in plans]
    emitter_seconds = time.perf_counter() - emitter_started
    best, best_rank, trace = None, None, []
    evaluated = pruned = cached_readouts = 0
    selection_started = time.perf_counter()
    for parser, full_outputs in retained:
        cache = {}
        for missing in (0, 1):
            for emitter, group, payload_bits in zip(emitters, plans, payload_costs, strict=True):
                size = parser.gates + emitter.gates
                if best_rank is not None and best_rank[0] == 0 and (payload_bits > best_rank[1]
                        or (payload_bits == best_rank[1] and size > best_rank[2])):
                    pruned += 1
                    continue
                wrong = 0
                for case, plan in zip(cases, group, strict=True):
                    source_mask = sum(1 << index for index, slot in enumerate(plan.source_slots) if slot is not None)
                    for port, target in enumerate(case["answers"]):
                        query_slot = plan.query_slots[port]
                        if query_slot is not None:
                            query_index = plan.slots[query_slot][1]
                            prediction = full_outputs[question_ids[case["wiring"][query_index]]]
                        else:
                            question_id = question_ids[case["wiring"][port]]
                            key = (question_id, source_mask, missing)
                            if key not in cache:
                                substituted = tuple(value if (source_mask >> index) & 1 else universe if missing else 0
                                                    for index, value in enumerate(columns))
                                cache[key] = _parse_packed(parser, questions[question_id], substituted, universe)
                                cached_readouts += 1
                            prediction = cache[key]
                        wrong += (prediction ^ target).bit_count()
                evaluated += 1
                rank = (wrong, payload_bits, size, parser.syntax, emitter.expr, missing)
                if best_rank is None or rank < best_rank:
                    best_rank, best = rank, (parser, emitter, missing)
                    trace.append({"combination": evaluated, "wrong_answer_bits": wrong,
                                  "transmitted_payload_bits": payload_bits, "NAND_code_size": size,
                                  "missing_source": missing})
    checkpoint = _checkpoint(*best)
    frozen = canonical_sha256(checkpoint)
    selection_seconds = time.perf_counter() - selection_started
    verification_started = time.perf_counter()
    verified = _verify_training(checkpoint, cases, raw_masks)
    if (verified["wrong_answer_bits"], verified["transmitted_payload_bits"]) != best_rank[:2]:
        raise ValueError("Actual NAND sender/receiver disagreed with packed training selection")
    if canonical_sha256(checkpoint) != frozen:
        raise ValueError("Training replay changed the frozen checkpoint")
    stats = {"checkpoint_sha256": frozen, "binary_NAND_catalogue": binary_stats,
             "parser_search": parser_stats, "emitter_search": emitter_stats,
             "compression_combinations_evaluated": evaluated,
             "nonnegative_loss_bound_pruned": pruned, "packed_readouts_computed": cached_readouts,
             "training_loss": {"wrong_answer_bits": best_rank[0], "transmitted_payload_bits": best_rank[1],
                               "NAND_code_size": best_rank[2]},
             "training_verification": verified, "improvement_trace": trace,
             "selection": "terminal wrong bits, actual packet bits, NAND definition size, canonical parser/emitter/default ties",
             "payload_unit": "one committed packet per raw input/wiring, assessed at all four delayed ports",
             "staged_search": True, "jointly_exhaustive_over_all_parsers": False,
             "runtime_seconds": {"parser": parser_seconds, "public_emission_grammar": emitter_seconds,
                                 "compression_selection": selection_seconds,
                                 "actual_training_replay": time.perf_counter() - verification_started,
                                 "total": time.perf_counter() - started},
             "codec_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return checkpoint, stats


def smoke():
    binary, stats = binary_catalogue()
    for node in binary:
        if _truth_mask(node.expr, 2) != node.mask or nand_gate_count(node.expr) != node.gates:
            raise ValueError("A binary function failed atomic NAND replay")
    # Unrelated synthetic scan programs, not a supplied conjunction/disjunction parser.
    by_mask = {node.mask: node for node in binary}
    parser = Parser(by_mask[7], by_mask[10], by_mask[7], 0, 1)
    emitter = Node(0, 0, ("input", 0))  # Public query-candidate bank, four physical slots.
    checkpoint = _checkpoint(parser, emitter, 0)
    question = ((1, -4, 7), (2, -2), (-3, 5), (6, -8))
    wiring = (question, question[::-1], question, question[::-1])
    sender, receiver = Codec(checkpoint), Codec(checkpoint)
    columns = tuple(sum(((raw >> source) & 1) << lane for lane, raw in enumerate((0, 173, 511))) for source in range(9))
    predictions = [_parse_packed(parser, query, columns, 7) for query in wiring]
    for lane, raw in enumerate((0, 173, 511)):
        payload = sender.send(wiring, raw)
        if len(payload) != 4:
            raise ValueError("A synthetic packet changed public width")
        for port in range(4):
            # Public structural reuse routes to the first emitted matching question.
            representative = 0
            if receiver.receive(wiring, payload, port) != ((predictions[representative] >> lane) & 1):
                raise ValueError("Independent synthetic sender/receiver copies disagreed")
    if any(not isinstance(key, tuple) for key in sender._public_cache) or set(sender.__dict__) != {
            "_parser", "_emit", "_missing", "_public_cache"}:
        raise ValueError("The agent retained an unexpected state channel")
    # Verify every baseline controller belongs to the same NAND search grammar.
    _, emit_stats = _emission_catalogue(({"wiring": wiring},))
    return {"synthetic_only": True, "binary_functions_verified": len(binary),
            "binary_catalogue": stats, "baseline_alternatives": emit_stats["baseline_alternatives_present"],
            "independent_sender_receiver": True,
            "packet_to_answer_actions": receiver.trace_receive(wiring, sender.send(wiring, 173), 0)["actions"],
            "codec_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.parse_args()
    print(json.dumps(smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
