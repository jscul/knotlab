"""Independent finite communication and search-control audit for GROUP-SENDER.

No fitting, producer import, or old-policy replay occurs here.  Actual frozen
checkpoint replay is deliberately separate from the public combinatorial
controls.  Source support and informational width are different quantities.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime
from functools import lru_cache, reduce
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import random
import importlib.util


TICKET = "GROUP-SENDER-20261115-001"
FAMILY = TICKET + "-E001_atomic_switch"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
WORK_KEYS = ("NAND", "READ", "COPY", "WRITE", "CONST", "IDENTITY_COMPARE", "WIDTH_COMPARE",
             "MASK_TRIAL", "SUPPORT_READ", "SLOT_WRITE", "PUBLIC_OR", "GROUP_READ")
PARSER_DIGEST = "b328cd2bcd4aa95976fad2513252ad1c23e0e21fa337323b84919a8ea93db0cd"
CODEC_DIGEST = "6985190eae222a30bbeb63ab6f8bbb55210365e31cce97997a0842fa9bf2470b"
DIRECT_FEATURES = ("question_sources", "sources_outside_single_source_questions", "sources_exclusive_to_question",
                   "largest_overlap_with_another_question", "distinct_sources_in_menu",
                   "sources_outside_smaller_questions", "other_questions_with_equal_source_set")
PUBLIC_TRACE_CACHE = {}  # Checker factoring of functions of PUBLIC inputs only.


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit(value):
    require(type(value) is int and value in (0, 1), "A physical bit must be integer zero or one")
    return value


def nand(expr, values, actions=None):
    require(isinstance(expr, (list, tuple)) and expr, "Malformed NAND expression")
    if expr[0] == "input":
        require(len(expr) == 2 and type(expr[1]) is int and 0 <= expr[1] < len(values), "Invalid input copy")
        if actions is not None:
            actions["READ"] += 1
        return bit(values[expr[1]])
    if expr[0] == "const":
        require(len(expr) == 2, "Malformed constant")
        if actions is not None:
            actions["CONST"] += 1
        return bit(expr[1])
    require(expr[0] == "NAND" and len(expr) == 3, "The learned action is outside NAND/COPY/constants")
    left = nand(expr[1], values, actions)
    if expr[1] == expr[2]:
        right = left
        if actions is not None:
            actions["COPY"] += 1
    else:
        right = nand(expr[2], values, actions)
    if actions is not None:
        actions["NAND"] += 1
    return 1 - left * right


def nand_cost(expr):
    if expr[0] in ("input", "const"):
        return 0
    return 1 + nand_cost(expr[1]) + (0 if expr[1] == expr[2] else nand_cost(expr[2]))


def program(record):
    require(set(record) == {"inputs", "expr", "nand_gates", "truth_mask"} and record["inputs"] == 2,
            "Expected a binary learned NAND program")
    result = sum(nand(record["expr"], (address & 1, address >> 1 & 1)) << address for address in range(4))
    require(record["truth_mask"] == result, "NAND syntax differs from its truth metadata")
    require(record["nand_gates"] == nand_cost(record["expr"]), "NAND definition size differs")
    return record["expr"]


def tuple_tree(value):
    return tuple(tuple_tree(child) for child in value) if isinstance(value, list) else value


class FrozenParser:
    """Execute the predecessor's frozen parser solely as a new decoder component."""

    def __init__(self, record):
        require(set(record) == {"literal", "clause", "question", "clause_initial", "question_initial"},
                "Unexpected parser fields")
        self.exprs = {role: tuple_tree(program(record[role])) for role in ("literal", "clause", "question")}
        self.clause_initial = bit(record["clause_initial"])
        self.question_initial = bit(record["question_initial"])

    def scan(self, question, read, actions=None):
        state = self.question_initial
        if actions is not None:
            actions.update({"CONST": 1, "WRITE": 1})
        for clause in question:
            row = self.clause_initial
            if actions is not None:
                actions.update({"CONST": 1, "WRITE": 1})
            for pin in clause:
                if actions is not None:
                    actions["PUBLIC_READ"] += 2
                value = nand(self.exprs["literal"], (read(abs(pin) - 1), int(pin < 0)), actions)
                row = nand(self.exprs["clause"], (row, value), actions)
                if actions is not None:
                    actions["WRITE"] += 1
            state = nand(self.exprs["question"], (state, row), actions)
            if actions is not None:
                actions["WRITE"] += 1
        return state

    def answer(self, question, raw, actions=None):
        def read(source):
            if actions is not None:
                actions["READ"] += 1
            return raw >> source & 1
        return self.scan(question, read, actions)

    @lru_cache(None)
    def table(self, question):
        # Checker-only factoring; this is not a deployment cache or charge.
        return tuple(self.answer(question, raw) for raw in range(512))


@lru_cache(None)
def xor_expr():
    """Independent canonical binary NAND compiler, used only for work replay."""
    best = {0: ("const", 0), 15: ("const", 1), 10: ("input", 0), 12: ("input", 1)}
    levels = [dict(best)]
    for cost in range(1, 6):
        current = {}
        def offer(mask, expr):
            if mask not in best and (mask not in current or expr < current[mask]):
                current[mask] = expr
        for left_cost in range(cost):
            for left_mask, left in levels[left_cost].items():
                for right_mask, right in levels[cost - left_cost - 1].items():
                    if left <= right:
                        offer(15 ^ (left_mask & right_mask), ("NAND", left, right))
        for mask, child in levels[cost - 1].items():
            offer(15 ^ mask, ("NAND", child, child))
        levels.append(current)
        best.update(current)
    require(len(best) == 16 and nand_cost(best[6]) == 5, "Binary NAND compiler is incomplete")
    return best[6]


def work(actions):
    return sum(actions.get(key, 0) for key in WORK_KEYS)


class NewCodec:
    """New frozen sender/receiver; all routing is regenerated from public input."""

    def __init__(self, checkpoint, head=None, parser=None):
        self.cp = json.loads(json.dumps(checkpoint))
        require(self.cp["schema_version"] == 1 and self.cp["parser_source_sha256"] == CODEC_DIGEST and
                self.cp["parser_checkpoint_sha256"] == PARSER_DIGEST, "Parser provenance differs")
        require(self.cp["variant"] in ("singleton", "joint"), "Invalid controller variant")
        self.parser = parser or FrozenParser(self.cp["parser"])
        self.trace_expr = tuple_tree(program(self.cp["trace"]["program"]))
        self.accept = tuple_tree(program(self.cp["controller"]["accept"]))
        bit(self.cp["trace"]["initial"])
        bit(self.cp["missing_source"])
        require(self.cp["controller"]["initial_computed_mask"] == 0 and
                self.cp["controller"]["horizon"] in range(1, 5), "Invalid public controller start or horizon")
        require(self.cp["controller"]["acceptance_inputs"] ==
                ["trial_width_less_than_incumbent", "trial_width_equal_to_incumbent"], "Acceptance input order differs")
        self.head = head
        if head is not None:
            require(tuple(head["features"]) == DIRECT_FEATURES, "Direct-head feature order differs")
        self._traces, self._plans = {}, {}

    def trace(self, wiring):
        wiring = tuple_tree(wiring)
        if wiring in self._traces:
            return self._traces[wiring]
        key = (digest(self.cp["trace"]), wiring)
        if key in PUBLIC_TRACE_CACHE:
            self._traces[wiring] = PUBLIC_TRACE_CACHE[key]
            return self._traces[wiring]
        actions, supports = Counter(), {}
        for question in dict.fromkeys(wiring):
            mode = self.cp["trace"]["mode"]
            if mode == "counterfactual":
                values = self.parser.table(question)
                query_actions = Counter()
                self.parser.answer(question, 0, query_actions)
                actions.update({key: value * 512 for key, value in query_actions.items()})
                actions["hypothetical_parser_evaluations"] += 512
            mask = 0
            for source in range(9):
                stream = []
                if mode == "identity":
                    for clause in question:
                        actions["GROUP_READ"] += 1
                        for pin in clause:
                            actions.update({"READ": 1, "IDENTITY_COMPARE": 1})
                            stream.append(int(abs(pin) - 1 == source))
                elif mode == "counterfactual":
                    for raw in range(512):
                        if raw & (1 << source):
                            continue
                        actions["READ"] += 2
                        stream.append(nand(xor_expr(), (values[raw], values[raw | (1 << source)]), actions))
                        actions["local_difference_tests"] += 1
                else:
                    raise AuditError("Unknown public trace mode")
                state = self.cp["trace"]["initial"]
                actions.update({"CONST": 1, "WRITE": 1})
                for observation in stream:
                    state = nand(self.trace_expr, (state, observation), actions)
                    actions.update({"WRITE": 1, "trace_updates": 1})
                mask |= state << source
            supports[question] = mask
        masks = [supports[question] for question in wiring]
        signature = digest({"parser": PARSER_DIGEST, "trace": self.cp["trace"], "wiring": wiring, "support_masks": masks})
        actions["cold_work_units"] = work(actions)
        result = {"support_masks": masks, "trace_signature": signature, "public_actions": dict(actions)}
        self._traces[wiring] = result
        PUBLIC_TRACE_CACHE[key] = result
        return result

    def plan_mask(self, wiring, mask, traced=None):
        require(type(mask) is int and 0 <= mask < 16, "Invalid public mask")
        traced = self.trace(wiring) if traced is None else traced
        identities = [question_identity(q) for q in wiring]
        selected = [p for p in range(4) if mask >> p & 1]
        reps, actions = [], Counter()
        for port in range(4):
            representative = None
            for candidate in selected:
                actions["IDENTITY_COMPARE"] += 1
                if identities[candidate] == identities[port]:
                    representative = candidate
                    break
            reps.append(representative)
        source_mask = 0
        for port, representative in enumerate(reps):
            if representative is None:
                source_mask |= traced["support_masks"][port]
                actions.update({"SUPPORT_READ": 9, "PUBLIC_OR": 1})
        raw_slots = [("source", source) for source in range(9) if source_mask >> source & 1]
        query_slots = [("query", rep) for rep in sorted(set(rep for rep in reps if rep is not None))]
        slots = raw_slots + query_slots
        source_slots = [slots.index(("source", source)) if ("source", source) in slots else None for source in range(9)]
        query_indices = [None if rep is None else slots.index(("query", rep)) for rep in reps]
        actions["SLOT_WRITE"] += len(slots)
        actions["cold_work_units"] = work(actions)
        return {"computed_mask": mask, "width": len(slots),
                "slots": [{"kind": kind, "index": index} for kind, index in slots],
                "source_mask": source_mask, "source_slots": source_slots, "query_slots": query_indices,
                "query_representatives": reps, "support_masks": traced["support_masks"],
                "trace_signature": traced["trace_signature"], "routing_actions": dict(actions),
                "public_actions": dict(Counter(traced["public_actions"]) + actions)}

    def direct_mask(self, supports):
        union = lambda sets: reduce(int.__or__, sets, 0)
        singletons = union(s for s in supports if s.bit_count() == 1)
        total = union(supports)
        rows = []
        for port, own in enumerate(supports):
            others = supports[:port] + supports[port + 1:]
            rows.append((own.bit_count(), (own & ~singletons).bit_count(), (own & ~union(others)).bit_count(),
                         max((own & other).bit_count() for other in others), total.bit_count(),
                         (own & ~union(s for s in others if s.bit_count() < own.bit_count())).bit_count(), others.count(own)))
        rule = self.head["rule"]
        op, tests = rule["op"], rule["tests"]
        if op in ("raw", "computed"):
            require(not tests, "Constant head has unused tests")
            return 0 if op == "raw" else 15
        require(op in ("test", "and", "or") and len(tests) == (1 if op == "test" else 2), "Invalid direct rule")
        mask = 0
        for port, row in enumerate(rows):
            values = []
            for column, threshold in tests:
                require(type(column) is int and 0 <= column < 7 and type(threshold) is int and 1 <= threshold <= 9,
                        "Direct-head test outside grammar")
                values.append(row[column] >= threshold)
            mask |= int(any(values) if op == "or" else all(values)) << port
        return mask

    def plan(self, wiring):
        wiring = tuple_tree(wiring)
        if wiring in self._plans:
            return self._plans[wiring]
        traced = self.trace(wiring)
        if self.head is not None:
            result = self.plan_mask(wiring, self.direct_mask(traced["support_masks"]), traced)
        else:
            actions = Counter(traced["public_actions"])
            actions.pop("cold_work_units", None)
            current, trials, plans = 0, [], {0: self.plan_mask(wiring, 0, traced)}
            toggles = (1, 2, 4, 8) if self.cp["variant"] == "singleton" else range(1, 16)
            for round_index in range(self.cp["controller"]["horizon"]):
                anchor, incumbent = current, current
                for toggle in toggles:
                    candidate = anchor ^ toggle
                    actions["MASK_TRIAL"] += 1
                    if candidate not in plans:
                        plans[candidate] = self.plan_mask(wiring, candidate, traced)
                    width, best_width = plans[candidate]["width"], plans[incumbent]["width"]
                    singleton = self.cp["variant"] == "singleton"
                    actions["WIDTH_COMPARE"] += int(singleton)
                    accepted = False
                    if not singleton or width < plans[anchor]["width"]:
                        actions["WIDTH_COMPARE"] += 2
                        accepted = bool(nand(self.accept, (int(width < best_width), int(width == best_width)), actions))
                        actions["acceptance_evaluations"] += 1
                    if accepted:
                        incumbent = candidate
                    trials.append({"round": round_index, "anchor": anchor, "toggle": toggle,
                                   "candidate": candidate, "width": width, "accepted": accepted})
                current = incumbent
                actions["rounds"] += 1
                if current == anchor:
                    break
                actions["mask_updates"] += 1
            for physical in plans.values():
                actions.update({key: value for key, value in physical["routing_actions"].items() if key != "cold_work_units"})
            actions["mask_trials"], actions["unique_masks"] = actions["MASK_TRIAL"], len(plans)
            actions["cold_work_units"] = work(actions)
            result = plans[current] | {"public_actions": dict(actions), "trials": trials}
        self._plans[wiring] = result
        return result

    def send(self, wiring, raw, physical=None):
        physical = self.plan(wiring) if physical is None else physical
        require(type(raw) is int and 0 <= raw < 512, "Invalid raw data")
        return tuple(raw >> slot["index"] & 1 if slot["kind"] == "source" else
                     self.parser.table(tuple_tree(wiring[slot["index"]]))[raw] for slot in physical["slots"])

    def receive(self, wiring, packet, port, physical=None):
        physical = self.plan(wiring) if physical is None else physical
        require(type(packet) is tuple and len(packet) == physical["width"], "Truncated, extra, or non-tuple packet")
        require(type(port) is int and 0 <= port < 4, "Invalid delayed reader")
        for value in packet:
            bit(value)
        slot = physical["query_slots"][port]
        if slot is not None:
            return packet[slot]
        def read(source):
            index = physical["source_slots"][source]
            return self.cp["missing_source"] if index is None else packet[index]
        return self.parser.scan(wiring[port], read)


def literal_answers(wiring, raw):
    """Gold Boolean questions by raw signed-clause satisfaction only."""
    require(type(raw) is int and 0 <= raw < 512, "Expected nine raw bits")
    answers = []
    for question in wiring:
        answer = True
        for clause in question:
            satisfied = False
            for pin in clause:
                require(type(pin) is int and 1 <= abs(pin) <= 9, "Invalid signed raw source")
                if (raw >> (abs(pin) - 1) & 1) == int(pin > 0):
                    satisfied = True
                    break
            answer &= satisfied
        answers.append(int(answer))
    return tuple(answers)


def question_identity(question):
    return tuple(sorted(tuple(sorted(clause)) for clause in question))


def question_classes(wiring):
    identities = [question_identity(question) for question in wiring]
    representatives = []
    classes = []
    for identity in identities:
        if identity not in representatives:
            representatives.append(identity)
        classes.append(representatives.index(identity))
    return tuple(classes)


def semantic_support(answer_rows):
    """Exact influence, comparing each raw distinction with others pinned."""
    require(len(answer_rows) == 512 and all(len(row) == 4 for row in answer_rows), "Expected 512 four-answer rows")
    return tuple(frozenset(source for source in range(9)
                           if any(answer_rows[raw][port] != answer_rows[raw | (1 << source)][port]
                                  for raw in range(512) if not raw & (1 << source)))
                 for port in range(4))


def information_bound(answer_rows):
    patterns = Counter(tuple(row) for row in answer_rows)
    return {"answer_patterns": len(patterns), "minimum_bits": (len(patterns) - 1).bit_length(),
            "multiplicities": {"".join(map(str, pattern)): count for pattern, count in sorted(patterns.items())}}


def mixed_costs(supports, classes):
    """All sixteen public masks in the raw+computed-query receiver grammar.

    Selecting any member of a structural class supplies one computed bit for
    that class.  Every other class must be reconstructed from raw sources.
    Supports passed here must come from a separately specified evaluator.
    """
    require(len(supports) == len(classes) == 4, "Exactly four questions are required")
    records = []
    for mask in range(16):
        computed = {classes[port] for port in range(4) if mask >> port & 1}
        raw = set()
        for port in range(4):
            if classes[port] not in computed:
                raw.update(supports[port])
        records.append({"mask": mask, "width": len(computed) + len(raw),
                        "computed_classes": sorted(computed), "raw_sources": sorted(raw)})
    return records


def strict_batch_search(costs, maximum_toggles):
    """Task-aware baseline with an explicit charged neighborhood traversal."""
    require(1 <= maximum_toggles <= 4 and len(costs) == 16, "Invalid bounded mask-search domain")
    widths = [entry["width"] for entry in costs]
    mask = 0
    path = [mask]
    probes = [mask]
    while True:
        candidates = []
        for count in range(1, maximum_toggles + 1):
            for positions in combinations(range(4), count):
                flip = sum(1 << port for port in positions)
                candidate = mask ^ flip
                probes.append(candidate)
                candidates.append(candidate)
        next_mask = min(candidates, key=lambda candidate: (widths[candidate], candidate))
        if widths[next_mask] >= widths[mask]:
            break
        mask = next_mask
        path.append(mask)
    return {"mask": mask, "width": widths[mask], "path": path,
            "width_probes": len(probes), "distinct_masks_probed": len(set(probes)),
            "maximum_toggles": maximum_toggles}


def nonworsening_singleton_reachability(costs):
    """Strong neutral-move control; searches every reachable non-worsening path."""
    widths = [entry["width"] for entry in costs]
    reached, pending, probes = {0}, [0], 1
    while pending:
        mask = pending.pop(0)
        for port in range(4):
            candidate = mask ^ (1 << port)
            probes += 1
            if widths[candidate] <= widths[mask] and candidate not in reached:
                reached.add(candidate)
                pending.append(candidate)
    best = min(reached, key=lambda mask: (widths[mask], mask))
    return {"mask": best, "width": widths[best], "reachable_masks": sorted(reached), "width_probes": probes}


def task_aware_controls(wiring, answer_rows):
    supports = semantic_support(answer_rows)
    classes = question_classes(wiring)
    for left in range(4):
        for right in range(left):
            if classes[left] == classes[right]:
                require(all(row[left] == row[right] for row in answer_rows),
                        "Structural binding merges unequal answer functions")
    costs = mixed_costs(supports, classes)
    minimum = min(row["width"] for row in costs)
    syntax = sorted({abs(pin) - 1 for question in wiring for clause in question for pin in clause})
    distinct_functions = {tuple(row[port] for row in answer_rows) for port in range(4)}
    bound = information_bound(answer_rows)
    return {
        "information": bound, "semantic_support_by_port": [sorted(support) for support in supports],
        "naive_all_literal_raw_width": len(syntax), "semantic_raw_width": costs[0]["width"],
        "all_computed_structural_width": costs[15]["width"],
        "all_computed_semantic_functions": len(distinct_functions),
        "exact_mixed_grammar_width": minimum, "optimal_masks": [row["mask"] for row in costs if row["width"] == minimum],
        "information_bound_attainable_in_mixed_grammar": minimum == bound["minimum_bits"],
        "sixteen_mask_scheduler": {"width": minimum, "width_probes": 16},
        "greedy_singleton": strict_batch_search(costs, 1),
        "nonworsening_singleton": nonworsening_singleton_reachability(costs),
        "strict_batch_two": strict_batch_search(costs, 2),
        "strict_batch_three": strict_batch_search(costs, 3),
        "strict_batch_four": strict_batch_search(costs, 4), "masks": costs,
        "support_derivation": {"function_evaluations": 512 * 4,
                               "possible_pinned_pair_comparisons": 9 * 256 * 4,
                               "counts_are_not_free_deployment_work": True},
    }


def public_constants(path):
    """Read public panel literals without executing producer code."""
    allowed = {"TRAIN", "HELD", "EIGHT", "ALL_PAIRS", "DOUBLE_PAIRS"}
    values = {}
    def read(node):
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.Tuple, ast.List)):
            return tuple(read(child) for child in node.elts)
        if isinstance(node, ast.Dict):
            return {read(k): read(v) for k, v in zip(node.keys, node.values, strict=True)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -read(node.operand)
        raise AuditError("Nonliteral panel input")
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in allowed:
                values[name] = read(node.value)
    require(set(values) == allowed, "Missing public panel constants")
    return values


def clauses(op, pins):
    a = pins[0]
    taut = (a, -a)
    if op == "unit":
        return [(a, a, a), taut, taut, taut]
    b = pins[1]
    if op == "xor":
        return [(a, b, b), (-a, -b), taut, (b, -b)]
    if op == "or2":
        return [(a, b, b), taut, (b, -b), taut]
    c = pins[2]
    return {"e": [(a, b, c), (-a, -b), (-a, -c), (-b, -c)],
            "o": [(a, b, c), taut, (b, -b), (c, -c)],
            "a": [(a, a, a), (b, b), (c, c), taut],
            "m": [(a, b, c), (a, b), (b, c), (c, a)],
            "s": [(a, -a, b), (-a, b), (a, c), (c, -c)],
            "g": [(a, a, -b), (-a, b), (b, -c), (-b, c)],
            "p": [(a, b, c), (-a, -b), (b, -b), (c, -c)],
            "padded_unit": [(a, b, c), (a, -b), (a, -c), (b, -b)]}[op]


def panel_row(spec, seed, order, split, family, template, layout):
    rng = random.Random(seed)
    rename = rng.sample(range(1, 10), 9)
    questions = []
    for op, pins in spec:
        mapped = [rename[abs(pin) - 1] * (1 if pin > 0 else -1) for pin in pins]
        rows = []
        for row in clauses(op, mapped):
            row = list(row)
            rng.shuffle(row)
            rows.append(tuple(row))
        rng.shuffle(rows)
        questions.append(tuple(rows))
    wiring = tuple(questions[port] for port in order)
    identity = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
    return identity, wiring, {"split": split, "family": family, "template": template, "layout": layout,
                              "port_order": list(order), "cell_order": [name - 1 for name in rename]}


def rosters():
    constants = public_constants(ROOT / "research" / TICKET / "panels.py")
    orders = tuple(permutations(range(4)))
    train = [panel_row(spec, 20341 + 13*i, orders[7*i % 24], "train", name, name, f"train-{i}")
             for i in range(4) for name, spec in constants["TRAIN"].items()]
    def eight(i):
        name, links, ops, signs = constants["EIGHT"][i]
        return name, tuple((op, tuple(-source if sign >> j & 1 else source for j, source in enumerate(sources)))
                           for op, sources, sign in zip(ops, links, signs, strict=True))
    held = []
    for i in range(8):
        name, spec = eight(i)
        held.append(panel_row(spec, 41987 + 23*i, orders[(5*i+3) % 24], "held", "plateau_eight", name, f"eight-{i}"))
    name, spec = eight(0)
    for i, order in enumerate(orders):
        row = panel_row(spec, 51361 + 17*i, order, "held", "plateau_relabel", name, f"relabel-{i}")
        row[2]["relabel_of"] = held[0][0]
        held.append(row)
    for i in range(4):
        group = [panel_row(spec, 62533 + 19*i, orders[(5*i+9) % 24], "held", name, name, f"controlled-{i}")
                 for name, spec in constants["HELD"].items()]
        ids = {meta["family"]: identity for identity, _, meta in group}
        partners = {"majority_repeat": "majority_cross", "xor_closed": "xor_open", "raw_three": "raw_four"}
        partners.update({value: key for key, value in partners.items()})
        for _, _, meta in group:
            if meta["family"] in partners:
                meta["partner"] = ids[partners[meta["family"]]]
        held.extend(group)
    # Only reuse the previous independent public-input construction. No old
    # sender/decoder is called, and baseline outcomes come from saved JSON.
    prior_file = ROOT / "research/BIT-DECODER-20261114-001/audit.py"
    require(file_digest(prior_file) == "2a9287069d47e34c64b242785ab84eede80700290272d709aa7b2a8d38cd39ee",
            "Independent archived input reconstruction changed")
    spec = importlib.util.spec_from_file_location("independent_archived_inputs", prior_file)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    old = prior.roster()
    lookup = {identity: (wiring, meta) for split in ("held", "stress") for identity, wiring, meta in old[split]}
    archived = json.loads((ROOT / "artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/result.json").read_bytes())
    historical = []
    for section in ("held", "stress"):
        for row in archived["conditions"]["varied"][section]["menus"]:
            if section == "held" and row["width"] == row["minimum"]:
                continue
            wiring, meta = lookup[row["id"]]
            historical.append((row["id"], wiring, dict(meta, split="historical", template=row["family"],
                               original_section=section, earlier_width=row["width"], earlier_minimum=row["minimum"],
                               earlier_correct_bits=row["correct_bits"])))
    return {"train": train, "held": held, "historical": historical}


def equality(actual, expected, label):
    require(canonical(actual) == canonical(expected), "Independent mismatch: " + label)


def measure(codec, receiver, wiring, meta, identity, controls):
    physical, incoming = codec.plan(wiring), receiver.plan(wiring)
    equality(physical, incoming, "independent public routing")
    gold = [literal_answers(wiring, raw) for raw in range(512)]
    counts, correct, odd, vectors, first = [0] * 4, 0, 0, 0, None
    h, decoded, packets = hashlib.sha256(), {}, {}
    for raw, wanted in enumerate(gold):
        payload = codec.send(wiring, raw, physical)
        require(type(payload) is tuple and len(payload) == physical["width"], "Data-dependent packet width")
        for value in payload:
            bit(value)
        h.update(bytes((len(payload), *payload)))
        if payload not in decoded:
            decoded[payload] = tuple(receiver.receive(wiring, payload, port, incoming) for port in range(4))
        got = decoded[payload]
        matches = [a == b for a, b in zip(wanted, got, strict=True)]
        correct += sum(matches)
        odd += (raw.bit_count() % 2) * sum(matches)
        vectors += all(matches)
        counts = [a + b for a, b in zip(counts, matches, strict=True)]
        if first is None and not all(matches):
            first = {"raw": raw, "wanted": wanted, "got": got, "packet": payload}
        packets.setdefault(payload, set()).add(wanted)
    masks = [sum(1 << source for source in support) for support in controls["semantic_support_by_port"]]
    return {"id": identity, "metadata": meta, "input_count": 512, "correct_vectors": vectors,
            "correct_bits": correct, "odd_correct_bits": odd, "correct_by_port": counts, "first_error": first,
            "width": physical["width"], "answer_patterns": controls["information"]["answer_patterns"],
            "minimum": controls["information"]["minimum_bits"], "grammar_minimum": controls["exact_mixed_grammar_width"],
            "mask_widths_by_true_support": [entry["width"] for entry in controls["masks"]],
            "physical_sha256": h.hexdigest(), "computed_mask": physical["computed_mask"], "slots": physical["slots"],
            "support_masks": physical["support_masks"], "semantic_support_masks": masks,
            "public_actions": physical["public_actions"]}, {
                "distinct_packets": len(packets), "ambiguous_packets": sum(len(values) > 1 for values in packets.values()),
                "trials": physical.get("trials", []), "trace_mode": codec.cp["trace"]["mode"]}


def summary(rows):
    return {"wirings": len(rows), "questions": 2048 * len(rows), "correct_bits": sum(r["correct_bits"] for r in rows),
            "odd_correct_bits": sum(r["odd_correct_bits"] for r in rows),
            "all_correct_wirings": sum(r["correct_bits"] == 2048 for r in rows),
            "exact_and_minimum": sum(r["correct_bits"] == 2048 and r["width"] == r["minimum"] for r in rows),
            "exact_and_grammar_minimum": sum(r["correct_bits"] == 2048 and r["width"] == r["grammar_minimum"] for r in rows),
            "widths": dict(sorted(Counter(r["width"] for r in rows).items()))}


def bindings(out):
    binding = json.loads((out / "checkpoints.json").read_bytes())
    require(binding["training_output"] == file_digest(out / "results.jsonl") and
            binding["source_freeze"] == file_digest(out / "freeze.json"), "Training/freeze binding changed")
    freeze = json.loads((out / "freeze.json").read_bytes())
    require(freeze["before_fits"] is True, "Sources were not declared frozen before fitting")
    for relative, expected in freeze["files_sha256"].items():
        require(file_digest(ROOT / relative) == expected, "Frozen source/dependency changed: " + relative)
    require(set(binding["checkpoints"]) == {"singleton", "joint", "direct"}, "Unexpected checkpoint roster")
    values = {}
    for name, expected in binding["checkpoints"].items():
        path = out / (name + ".json")
        require(file_digest(path) == expected, "Checkpoint file changed: " + name)
        value = json.loads(path.read_bytes())
        require(path.read_bytes() == canonical(value), "Checkpoint is not canonical frozen bytes")
        values[name] = value
    require(values["direct"]["trace_checkpoint_sha256"] == binding["checkpoints"]["joint"], "Direct trace binding differs")
    prior = json.loads((ROOT / "artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/varied_checkpoint.json").read_bytes())
    raw = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    require(len(raw) == 2 and {row["case"] for row in raw} == {"joint", "singleton"}, "Training cases incomplete")
    for row in raw:
        name, fitted = row["case"], row["result"]
        require(row["status"] == "ok" and fitted["strategy"] == name, "Failed or mismatched training case")
        job_path = "experiments/" + TICKET + "/" + FAMILY + "/job.py"
        sender_path = "experiments/" + TICKET + "/" + FAMILY + "/sender.py"
        require(row["job_sha"] == freeze["files_sha256"][job_path] and
                fitted["history"]["sender_sha256"] == freeze["files_sha256"][sender_path], "Fit source identity differs")
        require(datetime.fromisoformat(row["finished_at"]) >= datetime.fromisoformat(freeze["utc"]), "Fit predates source freeze")
        equality(fitted["checkpoint"], values[name], "serialized training checkpoint")
        require(fitted["checkpoint_sha256"] == binding["checkpoints"][name], "Checkpoint not bound to fit")
        equality(values[name]["parser"], prior["parser"], "unchanged frozen parser")
        require(values[name]["missing_source"] == prior["missing_source"], "Missing-source convention changed")
        if name == "joint":
            equality(fitted["direct"]["head"], values["direct"]["head"], "direct head frozen from training")
    return binding, freeze, values, {row["case"]: row["result"] for row in raw}


def incidence(supports):
    sources = set().union(*map(set, supports))
    return min(tuple(sorted(sum(int(source in supports[port]) << bit for bit, port in enumerate(order))
                            for source in sources)) for order in permutations(range(4)))


def audit(out):
    out = Path(out)
    bound, freeze, values, training = bindings(out)
    panels = rosters()
    equality({name: len(rows) for name, rows in panels.items()}, freeze["roster_sizes"], "public panel sizes")
    equality({name: digest(rows) for name, rows in panels.items()}, freeze["rosters_sha256"], "independent panel reconstruction")
    all_w = [w for rows in panels.values() for _, w, _ in rows]
    require(len(set(all_w)) == len(all_w), "Exact wiring duplicated across splits")
    official = json.loads((out / "result.json").read_bytes())
    equality(official["bindings"], bound, "assessment provenance")
    policies = {"singleton": (values["singleton"], None), "joint": (values["joint"], None),
                "direct": (values["joint"], values["direct"]["head"])}
    reports = {name: official for name in policies}
    crossover = json.loads((out / "crossover.json").read_bytes())
    crossed = json.loads((out / "crossover_freeze.json").read_bytes())
    require(crossover["freeze_sha256"] == file_digest(out / "crossover_freeze.json") and
            crossed["original_bindings"] == file_digest(out / "checkpoints.json") and
            crossed["direct_head_binding"] == file_digest(out / "direct.json") and
            crossed["script_sha256"] == file_digest(ROOT / "research" / TICKET / "crossover.py"), "Crossover binding changed")
    joint_cf = values["joint"] | {"trace": values["singleton"]["trace"]}
    singleton_id = values["singleton"] | {"trace": values["joint"]["trace"]}
    policies.update({"joint_counterfactual": (joint_cf, None), "singleton_occurrence": (singleton_id, None),
                     "direct_counterfactual": (joint_cf, values["direct"]["head"])})
    for name in ("joint_counterfactual", "singleton_occurrence", "direct_counterfactual"):
        require(digest(policies[name][0]) == crossed["crossed_policy_sha256"][name], "Crossed policy differs")
        reports[name] = crossover
    parser = FrozenParser(values["joint"]["parser"])
    evaluators = {name: (NewCodec(cp, head, parser), NewCodec(cp, head, parser)) for name, (cp, head) in policies.items()}
    controls, outcome, compared = {}, {name: {} for name in policies}, 0
    train_incidence = {incidence(semantic_support([literal_answers(w, raw) for raw in range(512)]))
                       for _, w, _ in panels["train"]}
    for split in ("historical", "held"):
        by_name = {name: [] for name in policies}
        extra = {name: [] for name in policies}
        for index, (identity, wiring, meta) in enumerate(panels[split]):
            gold = [literal_answers(wiring, raw) for raw in range(512)]
            for port, question in enumerate(wiring):
                equality(parser.table(question), [row[port] for row in gold], "new receiver NAND semantics")
            control = task_aware_controls(wiring, gold)
            require(control["exact_mixed_grammar_width"] >= control["information"]["minimum_bits"], "Grammar violates counting bound")
            controls[identity] = {"metadata": meta, **control}
            for name, (sender, receiver) in evaluators.items():
                row, details = measure(sender, receiver, wiring, meta, identity, control)
                expected = reports[name]["conditions"][name][split][index]
                equality(row, expected, name + "/" + split + "/" + identity)
                compared += 1
                traced = sender.trace(wiring)
                options = [sender.plan_mask(wiring, mask, traced) for mask in range(16)]
                semantic_masks = row["semantic_support_masks"]
                require(all((semantic_masks[port] & ~traced["support_masks"][port]) == 0 for port in range(4)),
                        "A fitted public trace omitted an essential source")
                # Every offered mask is therefore correct without consulting
                # gold at selection time. This scheduler uses public widths.
                best = min(option["width"] for option in options)
                details["recovered_support_scheduler"] = {
                    "width": best, "width_probes": 16,
                    "optimal_masks": [option["computed_mask"] for option in options if option["width"] == best],
                    "learned_width_equals_scheduler": row["width"] == best,
                    "trace_exact_by_port": [a == b for a, b in zip(semantic_masks, traced["support_masks"], strict=True)],
                }
                by_name[name].append(row)
                extra[name].append({"id": identity, **details})
        for name, rows in by_name.items():
            totals = summary(rows)
            equality(totals, reports[name]["summary"][name][split], name + "/" + split + " summary")
            outcome[name][split] = {"summary": totals, "menus": rows, "channel_checks": extra[name]}
    # Replay training labels and the selected programs' objectives. No fitting.
    mask_even = [raw for raw in range(512) if raw.bit_count() % 2 == 0]
    examples, identities = [], []
    for identity, wiring, _ in panels["train"]:
        identities.append(identity)
        examples.append((wiring, [literal_answers(wiring, raw) for raw in mask_even]))
    for name in ("singleton", "joint"):
        fitted = training[name]
        equality(fitted["training_ids"], identities, name + " training IDs")
        require(fitted["examples_sha256"] == digest(examples) and fitted["raw_masks"] == 256, "Training examples differ")
        sender, receiver = evaluators[name]
        wrong = width = public = 0
        for _, wiring, _ in panels["train"]:
            physical = sender.plan(wiring)
            width += 256 * physical["width"]
            public += physical["public_actions"]["cold_work_units"]
            for raw in mask_even:
                payload = sender.send(wiring, raw, physical)
                wanted = literal_answers(wiring, raw)
                wrong += sum(receiver.receive(wiring, payload, port) != wanted[port] for port in range(4))
        loss = fitted["history"]["loss"]
        equality((wrong, width, public), (loss["wrong_answer_bits"], loss["transmitted_bits"], loss["public_cold_work_units"]),
                 name + " selected training objective")
        require(fitted["history"]["candidates_scored"] == 4096, "Different training grammar count")
        outcome[name]["training_replay"] = {"wrong_bits": wrong, "transmitted_bits": width, "public_cold_work_units": public}
    require(training["joint"]["direct"]["history"]["programs_offered"] == 3971, "Direct grammar count differs")
    direct, direct_receiver = evaluators["direct"]
    direct_wrong = direct_width = 0
    for _, wiring, _ in panels["train"]:
        physical = direct.plan(wiring)
        direct_width += physical["width"]
        cached = {}
        for raw in mask_even:
            payload = direct.send(wiring, raw, physical)
            if payload not in cached:
                cached[payload] = tuple(direct_receiver.receive(wiring, payload, port) for port in range(4))
            direct_wrong += sum(a != b for a, b in zip(cached[payload], literal_answers(wiring, raw), strict=True))
    head_history = training["joint"]["direct"]["history"]
    equality((direct_wrong, direct_width), (head_history["training_wrong_answer_bits"], head_history["training_total_width"]),
             "direct selected training objective")
    outcome["direct"]["training_replay"] = {"wrong_bits": direct_wrong, "total_width_per_training_menu": direct_width}
    # Physical channel failures are schema failures; actual wrong answers and
    # above-minimum widths remain reportable scientific outcomes.
    first_wire = panels["held"][0][1]
    sender, receiver = evaluators["joint"]
    packet = sender.send(first_wire, 0)
    rejections = []
    for label, bad in (("truncated", packet[:-1]), ("extra", packet + (0,)),
                       ("nonbit", (2,) + packet[1:]), ("integer_payload", 0)):
        try:
            receiver.receive(first_wire, bad, 0)
        except AuditError:
            rejections.append(label)
        else:
            raise AuditError("Forbidden physical channel accepted: " + label)
    equality(bindings(out)[0], bound, "bindings after independent replay")
    eight = [controls[identity] for identity, _, meta in panels["held"] if meta["family"] == "plateau_eight"]
    require(len(eight) == 8, "Expected eight primary coordinated menus")
    for control in eight:
        widths = [entry["width"] for entry in control["masks"]]
        require(widths[0] == 6 and all(widths[1 << p] == 7 for p in range(4)) and
                min(widths[1:15]) >= 6 and widths[15] == control["information"]["minimum_bits"] == 4,
                "A coordinated menu did not require all four switches for strict improvement")
        require(incidence(control["semantic_support_by_port"]) not in train_incidence,
                "Coordinated held incidence was present in training")
    identity, xor_wiring, _ = next(item for item in panels["held"] if item[2]["family"] == "xor_closed")
    xor_rows = [literal_answers(xor_wiring, raw) for raw in range(512)]
    require(len({row[:3] for row in xor_rows}) == 8 and all(row[3] == (row[0] ^ row[1] ^ row[2]) for row in xor_rows),
            "Three-bit XOR-cycle identifying code failed")
    require(controls[identity]["exact_mixed_grammar_width"] == 4, "Restricted receiver limit failed")
    forced = {"width": 3, "query_slots": [0, 1, 2, None], "source_slots": [None] * 9}
    wrong_forced = sum(evaluators["joint"][1].receive(xor_wiring, row[:3], 3, forced) != row[3] for row in xor_rows)
    require(wrong_forced == 256, "Forced three-query decoder control failed")
    return {"ticket": TICKET, "schema_version": 1, "status": "pass", "bindings": bound,
            "audit_source_sha256": file_digest(__file__), "result_sha256": file_digest(out / "result.json"),
            "crossover_sha256": file_digest(out / "crossover.json"), "compared_menu_rows": compared,
            "no_old_sender_refit_or_replay": True, "physical_mutations_rejected": rejections,
            "coordinated_eight": {"all_have_raw_width": 6, "all_singletons_width": 7,
                                  "required_strict_improvement_toggles": 4, "minimum_width": 4,
                                  "novel_support_incidence_vs_training": True},
            "restricted_receiver_limit": {"id": identity, "answer_patterns": 8, "unrestricted_minimum": 3,
                                          "raw_or_copy_query_minimum": 4, "first_three_answers_identify_all_four": True,
                                          "forced_three_query_wrong_fourth_answers": wrong_forced},
            "conditions": outcome, "task_aware_controls": controls,
            "limits": ["All15 joint subsets are supplied and enumerated; subset generation is not learned.",
                       "Counterfactual tracing enumerates512 hypothetical parser inputs per unique question at cold deployment.",
                       "Direct head uses supplied source-count/overlap features and integer threshold tests.",
                       "Direct feature extraction is absent from public_actions:60 integer bit_count calls plus overlap/union work and4 threshold comparisons per menu.",
                       "Cold logical work excludes PUBLIC_READ and general Python/cache/ranking overhead.",
                       "Independent function-table/public-trace caching factors the checker, not the deployed policy.",
                       "Information bound need not be attainable by the raw-or-copy-query receiver."]}


def self_test():
    # Abstract dependency sets exercise search bookkeeping without constructing
    # or evaluating any new experiment panel or learned checkpoint.
    supports = ({0, 1, 2}, {0, 1, 2}, {3}, {3})
    costs = mixed_costs(supports, (0, 1, 2, 3))
    require(costs[0]["width"] == 4 and costs[1]["width"] == costs[2]["width"] == 5,
            "Uphill-singleton fixture is wrong")
    require(costs[3]["width"] == 3 and costs[15]["width"] == 4, "Mixed packet fixture is wrong")
    require(strict_batch_search(costs, 1)["width"] == 4, "Greedy singleton crossed an uphill step")
    require(nonworsening_singleton_reachability(costs)["width"] == 4, "Neutral control crossed an uphill step")
    require(strict_batch_search(costs, 2)["width"] == 3, "Two-toggle task-aware control failed")
    cycle = mixed_costs(({0, 1}, {1, 2}, {2, 3}, {3, 0}), (0, 1, 2, 3))
    require(min(row["width"] for row in cycle) == 4, "Restricted-grammar fixture is wrong")
    duplicate = mixed_costs(({0, 1}, {0, 1}, {2}, {2}), (0, 0, 1, 2))
    require(duplicate[1] == dict(duplicate[2], mask=1), "Structural duplicate cost depends on selected alias")
    require(nand_cost(xor_expr()) == 5 and all(nand(xor_expr(), (a, b)) == a ^ b for a in range(2) for b in range(2)),
            "Independent NAND comparator failed")
    return {"status": "pass", "abstract_singleton_batch_controls": True,
            "raw_query_grammar_limit": True, "duplicate_class_binding": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
    else:
        result = audit(args.out)
        if args.write:
            (args.out / "audit.json").write_bytes(canonical(result) + b"\n")
        print(json.dumps({"status": result["status"], "compared_menu_rows": result["compared_menu_rows"],
                          "summary": {name: {split: part["summary"] for split, part in value.items() if "summary" in part}
                                      for name, value in result["conditions"].items()}}, indent=2))
