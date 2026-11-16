"""Induce a tiny binary NAND library and compose received answer slots.

The library and public probe budget are fitted globally from terminal labels
and physical packet length. At deployment, supplied anonymous slot/program
enumeration proposes a three-slot decoder or immediately sends four. A full
external certificate is deliberately absent from this raw learned proposal.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IO_PATH = HERE / "packet_io.py"
IO_SHA256 = "7f98c96c212c16959f8c17759f929475d31d629db226632ac5aabf1a67d0cdd1"
CODEC_PATH = ROOT / "experiments/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/codec.py"
CODEC_SHA256 = "6985190eae222a30bbeb63ab6f8bbb55210365e31cce97997a0842fa9bf2470b"
PROBE_BUDGETS = (8, 16, 32, 64, 128)
PROBE_ORDER = tuple(sorted(range(512), key=lambda raw: hashlib.sha256(
    f"answer-compose-probes-v1|{raw}".encode()).digest()))


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _load(path, expected, name):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Frozen source changed: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def _io():
    return _load(IO_PATH, IO_SHA256, "answer_compose_shared_packet_io")


@lru_cache(maxsize=1)
def _codec():
    return _load(CODEC_PATH, CODEC_SHA256, "answer_compose_binary_nand_catalogue")


@lru_cache(maxsize=1)
def _binary():
    return tuple(_codec().binary_catalogue()[0])


def _wiring(wiring):
    return _codec()._wiring(wiring)


def _dag_value(dag, packet, lanes=1):
    """Only NAND evaluates a computed received answer; no truth table access."""
    registers = list(packet) + [0, lanes]
    for left, right in dag["gates"]:
        registers.append(lanes ^ (registers[left] & registers[right]))
    return registers[dag["output"]]


def _validate_dag(dag):
    if not isinstance(dag, dict) or set(dag) != {"gates", "output"}:
        raise ValueError("A literal NAND DAG is required")
    for index, gate in enumerate(dag["gates"]):
        if len(gate) != 2 or any(type(address) is not int or not 0 <= address < 5 + index for address in gate):
            raise ValueError("NAND addresses must point to earlier wires")
    if type(dag["output"]) is not int or not 0 <= dag["output"] < 5 + len(dag["gates"]):
        raise ValueError("Invalid NAND output address")


def _compile_calls(library, calls, output, with_work=False):
    gates, references = [], list(range(5))

    def inline(expr, operands):
        if expr[0] == "input":
            return operands[expr[1]]
        if expr[0] == "const":
            return 3 + expr[1]
        left = inline(expr[1], operands)
        right = left if expr[1] == expr[2] else inline(expr[2], operands)
        gates.append((left, right))
        return 4 + len(gates)

    for operator, left, right in calls:
        references.append(inline(library[operator].expr, (references[left], references[right])))
    result = references[output]
    # Dead NAND nodes are omitted; there is no other cross-subexpression CSE.
    live = set()

    def visit(address):
        if address < 5 or address - 5 in live:
            return
        live.add(address - 5)
        for operand in gates[address - 5]:
            visit(operand)

    visit(result)
    mapping = {index: index for index in range(5)}
    compiled = []
    for index in sorted(live):
        mapping[5 + index] = 5 + len(compiled)
        compiled.append(tuple(mapping[operand] for operand in gates[index]))
    dag = {"gates": tuple(compiled), "output": mapping[result]}
    _validate_dag(dag)
    return (dag, len(gates)) if with_work else dag


@dataclass(frozen=True)
class Candidate:
    signature: int
    calls: tuple
    output: int
    gates: tuple
    dag_output: int

    @property
    def dag(self):
        return {"gates": self.gates, "output": self.dag_output}

    @property
    def key(self):
        return len(self.gates), len(self.calls), self.calls, self.output


_FRAGMENT_WORK = {"fragment_groups_compiled": 0, "abstract_programs_generated": 0,
                  "candidate_syntax_NAND_nodes": 0, "signature_packed_NANDs": 0,
                  "signature_scalar_NANDs": 0}


@lru_cache(maxsize=153)
def _fragment_group(required_ids, max_calls):
    """Lazy fragments for only the operators in a chosen library.

    Acquisition shares these fragments across libraries. A fresh endpoint
    compiles only its own singleton/pair groups, not unrelated operators.
    """
    library = _binary()
    best, generated, syntax_nands, signature_nands = {}, 0, 0, 0

    def offer(calls, output):
        nonlocal generated, syntax_nands, signature_nands
        generated += 1
        dag, unpruned = _compile_calls(library, calls, output, with_work=True)
        syntax_nands += unpruned
        signature_nands += len(dag["gates"])
        signature = _dag_value(dag, (0b10101010, 0b11001100, 0b11110000), 255)
        candidate = Candidate(signature, calls, output, dag["gates"], dag["output"])
        if signature not in best or candidate.key < best[signature].key:
            best[signature] = candidate

    if not required_ids:
        for output in range(5):
            offer((), output)
    elif len(required_ids) == 1:
        operator = required_ids[0]
        for left, right in product(range(5), repeat=2):
            first = ((operator, left, right),)
            offer(first, 5)
            if max_calls == 2:
                for a, b in product(range(6), repeat=2):
                    if a == 5 or b == 5:
                        offer(first + ((operator, a, b),), 6)
    elif len(required_ids) == 2 and max_calls == 2:
        for first_id, second_id in (required_ids, required_ids[::-1]):
            for left, right in product(range(5), repeat=2):
                for a, b in product(range(6), repeat=2):
                    if a == 5 or b == 5:
                        offer(((first_id, left, right), (second_id, a, b)), 6)
    else:
        raise ValueError("A fragment uses zero, one or two generic functions")
    candidates = tuple(sorted(best.values(), key=lambda candidate: candidate.key + (candidate.signature,)))
    stats = {"abstract_programs_generated": generated, "candidate_syntax_NAND_nodes": syntax_nands,
             "signature_packed_NANDs": signature_nands, "signature_scalar_NANDs": 8 * signature_nands}
    _FRAGMENT_WORK["fragment_groups_compiled"] += 1
    for key, value in stats.items():
        _FRAGMENT_WORK[key] += value
    return candidates, stats


@lru_cache(maxsize=1392)
def _catalogue(library_ids, max_calls=2):
    if type(max_calls) is not int or max_calls not in (1, 2):
        raise ValueError("Use one or two calls without changing the fitted library")
    groups = [_fragment_group((), 1)]
    groups += [_fragment_group((operator,), max_calls) for operator in library_ids]
    if max_calls == 2:
        groups += [_fragment_group(pair, 2) for pair in combinations(library_ids, 2)]
    best = {}
    stats = {key: 0 for key in ("abstract_programs_generated", "candidate_syntax_NAND_nodes",
                                "signature_packed_NANDs", "signature_scalar_NANDs")}
    for candidates, fragment_stats in groups:
        for key, value in fragment_stats.items():
            stats[key] += value
        for candidate in candidates:
            if candidate.signature not in best or candidate.key < best[candidate.signature].key:
                best[candidate.signature] = candidate
    # Increasing global operator IDs preserve exactly the within-library
    # syntax order. Translate only the retained circuits to local library IDs.
    local = {operator: index for index, operator in enumerate(library_ids)}
    candidates = [Candidate(candidate.signature,
                            tuple((local[operator], left, right) for operator, left, right in candidate.calls),
                            candidate.output, candidate.gates, candidate.dag_output)
                  for candidate in best.values()]
    candidates.sort(key=lambda candidate: candidate.key + (candidate.signature,))
    stats |= {"semantic_candidates": len(candidates), "required_fragment_groups": len(groups),
              "deduplication": "exact eight-row semantics over three physical packet slots",
              "composition_generator_learned": False}
    return tuple(candidates), stats


def compilation_ledger():
    """Actual process-local symbolic work/cache state, separate from cold plans."""
    return _FRAGMENT_WORK.copy() | {"fragment_cache": _fragment_group.cache_info()._asdict(),
                                    "library_cache": _catalogue.cache_info()._asdict(),
                                    "constraint_cache": _constraints.cache_info()._asdict()}


@lru_cache(maxsize=8192)
def _constraints(columns, omitted, lanes):
    ports = tuple(port for port in range(4) if port != omitted)
    known = ones = 0
    consistent = True
    for code in range(8):
        group = lanes
        for bit, port in enumerate(ports):
            group &= columns[port] if (code >> bit) & 1 else lanes ^ columns[port]
        positive, negative = group & columns[omitted], group & (lanes ^ columns[omitted])
        if positive and negative:
            consistent = False
        if group:
            known |= 1 << code
            if positive:
                ones |= 1 << code
    return ports, known, ones, consistent


def _propose(checkpoint, wiring, columns, parser_ledger, max_calls=2):
    library_ids = tuple(checkpoint["library_ids"])
    candidates, catalogue_work = _catalogue(library_ids, max_calls)
    tests, matches, chosen = 0, 0, None
    lanes = (1 << checkpoint["probe_count"]) - 1
    for omitted in range(4):
        ports, known, ones, consistent = _constraints(columns, omitted, lanes)
        if not consistent:
            continue
        for index, candidate in enumerate(candidates):
            tests += 1
            if candidate.signature & known != ones:
                continue
            matches += 1
            rank = (len(candidate.gates), len(candidate.calls), ports, candidate.calls,
                    candidate.output, candidate.signature)
            if chosen is None or rank < chosen[0]:
                chosen = rank, ports, omitted, index, candidate
            break
    public = dict(parser_ledger) | {"three_port_subsets": 4, "public_candidate_tests": tests,
                                    "public_constraint_code_rows": 32,
                                    "public_constraint_bitset_AND": 160,
                                    "public_constraint_bitset_XOR": 80,
                                    "probe_consistent_candidates": matches,
                                    "catalogue_semantic_candidates": len(candidates),
                                    "catalogue_abstract_programs": catalogue_work["abstract_programs_generated"],
                                    "catalogue_fragment_groups_cold": catalogue_work["required_fragment_groups"],
                                    "catalogue_packed_NANDs_cold": catalogue_work["signature_packed_NANDs"],
                                    "catalogue_scalar_NANDs_cold": catalogue_work["signature_scalar_NANDs"],
                                    "composition_generator_learned": 0}
    if chosen is None:
        result = {"ports": [0, 1, 2, 3], "omitted_port": None, "dag": None,
                  "candidate_id": None, "candidate": None,
                  "proposal_reason": "no three-slot circuit matched the public probe rows"}
    else:
        _, ports, omitted, index, candidate = chosen
        result = {"ports": list(ports), "omitted_port": omitted,
                  "dag": {"gates": [list(gate) for gate in candidate.gates], "output": candidate.dag_output},
                  "candidate_id": f"fn-{candidate.signature:02x}/calls-{len(candidate.calls)}/index-{index}",
                  "candidate": {"truth_signature": candidate.signature,
                                "library_calls": [list(call) for call in candidate.calls],
                                "abstract_output": candidate.output, "library_applications": len(candidate.calls),
                                "catalogue_index": index},
                  "proposal_reason": "minimum-work three-slot circuit matching the public probes"}
    result |= {"public_actions": public, "max_calls": max_calls,
               "probe_count": checkpoint["probe_count"], "raw_proposal": True,
               "parameter_updates": 0, "external_certificate_used": False}
    result["proposal_sha256"] = canonical_sha256(result)
    return result


def _validate_checkpoint(checkpoint):
    if (checkpoint["schema_version"] != 1 or checkpoint["packet_io_sha256"] != IO_SHA256
            or checkpoint["codec_sha256"] != CODEC_SHA256 or checkpoint["parser_sha256"] != _io().PARSER_SHA):
        raise ValueError("Unknown or unbound learned packet codec")
    ids = tuple(checkpoint["library_ids"])
    if len(ids) not in (1, 2, 3) or tuple(sorted(set(ids))) != ids or any(type(index) is not int or not 0 <= index < 16 for index in ids):
        raise ValueError("The learned library must contain one, two or three distinct generic functions")
    expected = [_codec()._program_record(_binary()[index], 2) for index in ids]
    if json.loads(json.dumps(expected)) != checkpoint["library"]:
        raise ValueError("The learned library expression changed")
    budget = checkpoint["probe_count"]
    if type(budget) is not int or budget not in PROBE_BUDGETS or checkpoint["probe_masks"] != list(PROBE_ORDER[:budget]):
        raise ValueError("The frozen public probe schedule changed")


@lru_cache(maxsize=4096)
def _cached_plan(serialized, wiring, max_calls):
    checkpoint = json.loads(serialized)
    _validate_checkpoint(checkpoint)
    columns, ledger = _io().public_columns(wiring, checkpoint["probe_masks"])
    return _propose(checkpoint, wiring, columns, ledger, max_calls)


def plan(checkpoint, wiring, max_calls=2):
    """Raw proposal only; caller may separately certify/fallback after freezing."""
    wiring = _wiring(wiring)
    before = canonical_sha256(checkpoint)
    proposed = _cached_plan(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")), wiring, max_calls)
    if canonical_sha256(checkpoint) != before:
        raise ValueError("Public planning updated the frozen parameters")
    return json.loads(json.dumps(proposed))


def trace_send_plan(wiring, raw, physical_plan):
    wiring = _wiring(wiring)
    ports = tuple(physical_plan["ports"])
    if ports not in tuple(combinations(range(4), 3)) + ((0, 1, 2, 3),):
        raise ValueError("The sender sends an anonymous sorted three-port subset or four")
    values = _io().query_values(wiring, raw, ports)
    nand_count = sum(_io().parser_gate_cost(wiring[port]) for port in ports)
    return {"bits": values, "actions": {"NAND": nand_count, "READ_source_occurrences":
                                         sum(sum(map(len, wiring[port])) for port in ports),
                                         "WRITE_packet": len(ports)}}


def send_plan(wiring, raw, physical_plan):
    return trace_send_plan(wiring, raw, physical_plan)["bits"]


def trace_receive_plan(physical_plan, packet, port):
    ports = tuple(physical_plan["ports"])
    packet = tuple(packet)
    _io().validate_channel(packet, len(ports), port)
    if ports not in tuple(combinations(range(4), 3)) + ((0, 1, 2, 3),):
        raise ValueError("Unknown physical port binding")
    if port in ports:
        return {"answer": int(packet[ports.index(port)]), "actions": {"READ": 1, "COPY": 1, "WRITE": 1, "NAND": 0}}
    dag = physical_plan["dag"]
    if len(ports) != 3 or physical_plan["omitted_port"] != port:
        raise ValueError("A NAND decoder is required for the sole omitted port")
    _validate_dag(dag)
    registers = list(map(int, packet)) + [0, 1]
    actions = {"NAND": 0, "READ": 0, "CONST": 0, "COPY": 0, "WRITE": 0}

    def read(address):
        actions["CONST" if address in (3, 4) else "READ"] += 1
        return registers[address]

    for left, right in dag["gates"]:
        a = read(left)
        if left == right:
            b = a
            actions["COPY"] += 1
        else:
            b = read(right)
        registers.append(1 - (a & b))  # Exactly one NAND instruction.
        actions["NAND"] += 1
        actions["WRITE"] += 1
    answer = read(dag["output"])
    actions["WRITE"] += 1
    return {"answer": answer, "actions": actions}


def receive_plan(physical_plan, packet, port):
    return trace_receive_plan(physical_plan, packet, port)["answer"]


def send(checkpoint, wiring, raw, max_calls=2):
    proposed = plan(checkpoint, wiring, max_calls)
    return send_plan(wiring, raw, proposed)


def receive(checkpoint, wiring, packet, port, max_calls=2):
    return receive_plan(plan(checkpoint, wiring, max_calls), packet, port)


def _checkpoint(library_ids, budget):
    result = {"schema_version": 1, "library_ids": list(library_ids),
              "library": [_codec()._program_record(_binary()[index], 2) for index in library_ids],
              "probe_count": budget, "probe_masks": list(PROBE_ORDER[:budget]),
              "probe_order_rule": "SHA256 ascending of answer-compose-probes-v1|raw",
              "max_library_applications": 2, "packet_io_sha256": IO_SHA256,
              "codec_sha256": CODEC_SHA256, "parser_sha256": _io().PARSER_SHA}
    return json.loads(json.dumps(result, sort_keys=True, separators=(",", ":")))


def _examples(cases, raw_masks):
    result = []
    for case in cases:
        if isinstance(case, dict):
            wiring, answers = case["wiring"], case["answers"]
            if len(answers) == 4 and all(type(value) is int for value in answers):
                columns = tuple(answers)
            else:
                rows = [_codec()._literal_bits(row, 4, "Training answer row") for row in answers]
                if len(rows) != len(raw_masks):
                    raise ValueError("Training rows must align with raw_masks")
                columns = tuple(sum(row[port] << lane for lane, row in enumerate(rows)) for port in range(4))
        else:
            wiring, answers = case
            rows = [_codec()._literal_bits(row, 4, "Training answer row") for row in answers]
            if len(rows) != len(raw_masks):
                raise ValueError("Training rows must align with raw_masks")
            columns = tuple(sum(row[port] << lane for lane, row in enumerate(rows)) for port in range(4))
        result.append((_wiring(wiring), columns))
    if not result:
        raise ValueError("At least one anonymous training menu is required")
    return result


def _predicted_columns(proposed, sender_columns, lanes):
    if proposed["dag"] is None:
        return sender_columns
    result = list(sender_columns)
    packet = tuple(sender_columns[port] for port in proposed["ports"])
    result[proposed["omitted_port"]] = _dag_value(proposed["dag"], packet, lanes)
    return tuple(result)


def fit(cases, raw_masks):
    started = time.perf_counter()
    compilation_before = _FRAGMENT_WORK.copy()
    raw_masks = tuple(raw_masks)
    if not raw_masks or any(type(raw) is not int or not 0 <= raw < 512 for raw in raw_masks):
        raise ValueError("Nine-bit integer training raw masks are required")
    cases, lane_mask = _examples(cases, raw_masks), (1 << len(raw_masks)) - 1
    cache, fit_ledger = [], {"public_rows": 0, "public_parser_calls": 0,
                           "public_scalar_nands": 0, "public_packed_nands": 0}
    for wiring, targets in cases:
        probes, probe_ledger = _io().public_columns(wiring, PROBE_ORDER[:max(PROBE_BUDGETS)])
        sender_columns, sender_ledger = _io().public_columns(wiring, raw_masks)
        for ledger in (probe_ledger, sender_ledger):
            for key, value in ledger.items():
                fit_ledger[key] += value
        cache.append((wiring, targets, probes, sender_columns))
    libraries = [(index,) for index in range(16)] + list(combinations(range(16), 2)) + list(combinations(range(16), 3))
    best, best_rank, initial_loss, improvements, models = None, None, None, [], []
    diagnostic, diagnostic_rank, diagnostic_loss = None, None, None
    catalogue_work = {"libraries": 0, "abstract_programs_generated": 0,
                      "candidate_syntax_NAND_nodes": 0, "semantic_candidates": 0,
                      "signature_packed_NANDs": 0, "signature_scalar_NANDs": 0}
    proposals_by_best = None
    model_index = 0
    for library_ids in libraries:
        _, syntax_work = _catalogue(library_ids, 2)
        catalogue_work["libraries"] += 1
        for field in ("abstract_programs_generated", "candidate_syntax_NAND_nodes", "semantic_candidates",
                      "signature_packed_NANDs", "signature_scalar_NANDs"):
            catalogue_work[field] += syntax_work[field]
        code_size = sum(_binary()[index].gates for index in library_ids)
        for budget in PROBE_BUDGETS:
            model_index += 1
            checkpoint = _checkpoint(library_ids, budget)
            wrong = sent = work = decoder_nands = sender_nands = public_nands = tests = 0
            proposed_rows = []
            for wiring, targets, probe_columns, sender_columns in cache:
                columns = tuple(value & ((1 << budget) - 1) for value in probe_columns)
                gates = sum(_io().parser_gate_cost(question) for question in wiring)
                ledger = {"public_rows": budget, "public_parser_calls": 4 * budget,
                          "public_scalar_nands": gates * budget, "public_packed_nands": gates}
                proposed = _propose(checkpoint, wiring, columns, ledger)
                predicted = _predicted_columns(proposed, sender_columns, lane_mask)
                wrong += sum((prediction ^ target).bit_count() for prediction, target in zip(predicted, targets, strict=True))
                sent += len(proposed["ports"]) * len(raw_masks)
                decoder = 0 if proposed["dag"] is None else len(proposed["dag"]["gates"]) * len(raw_masks)
                sender = sum(_io().parser_gate_cost(wiring[port]) for port in proposed["ports"]) * len(raw_masks)
                decoder_nands += decoder
                sender_nands += sender
                public_nands += ledger["public_scalar_nands"]
                tests += proposed["public_actions"]["public_candidate_tests"]
                work += decoder + sender + ledger["public_scalar_nands"] + proposed["public_actions"]["public_candidate_tests"]
                proposed_rows.append(proposed)
            syntax = tuple(_binary()[index].expr for index in library_ids)
            rank = (wrong, sent, work, code_size, len(library_ids), syntax, budget)
            loss = {"wrong_answer_bits": wrong, "transmitted_bits": sent, "work_units": work,
                    "public_scalar_nands": public_nands, "public_candidate_tests": tests,
                    "sender_scalar_nands": sender_nands, "decoder_scalar_nands": decoder_nands,
                    "library_NAND_size": code_size}
            models.append({"model": model_index, "library_ids": library_ids, "probe_count": budget, **loss})
            if initial_loss is None:
                initial_loss = loss
            if len(library_ids) <= 2 and (diagnostic_rank is None or rank < diagnostic_rank):
                diagnostic, diagnostic_rank, diagnostic_loss = checkpoint, rank, loss
            if best_rank is None or rank < best_rank:
                best_rank, best, proposals_by_best = rank, checkpoint, proposed_rows
                improvements.append({"model": model_index, "library_ids": library_ids,
                                     "library_truth_masks": [_binary()[index].mask for index in library_ids],
                                     "probe_count": budget, **loss})
    frozen = canonical_sha256(best)
    # Check the selected physical DAG/packet path on training data only.
    actual_wrong = actual_bits = 0
    for (wiring, targets), proposed in zip(cases, proposals_by_best, strict=True):
        direct = plan(best, wiring)
        if direct != proposed:
            raise ValueError("Independent public planning changed the fitted raw proposal")
        for lane, raw in enumerate(raw_masks):
            packet = send_plan(wiring, raw, proposed)
            actual_bits += len(packet)
            for port in range(4):
                actual_wrong += receive_plan(proposed, packet, port) != ((targets[port] >> lane) & 1)
    if (actual_wrong, actual_bits) != best_rank[:2] or canonical_sha256(best) != frozen:
        raise ValueError("Physical NAND decoder disagreed with terminal training selection")
    history = {"checkpoint_sha256": frozen, "libraries": len(libraries), "model_candidates": model_index,
               "binary_function_catalogue_size": len(_binary()), "probe_budgets": PROBE_BUDGETS,
               "initial_loss": initial_loss, "final_loss": next(row for row in models if row["model"] == improvements[-1]["model"]),
               "improvement_trace": improvements, "model_scores": models,
               "raw_training_proposals": proposals_by_best,
               "training_actual_wrong_bits": int(actual_wrong), "training_actual_transmitted_bits": actual_bits,
               "fit_actual_parser_ledger": fit_ledger,
               "fit_cold_catalogue_work": catalogue_work,
               "fit_actual_shared_compilation": {key: value - compilation_before[key]
                                                   for key, value in _FRAGMENT_WORK.items()},
               "compilation_cache_after_fit": compilation_ledger(),
               "catalogue_sharing": "lazy per required operator/pair group; acquisition reuses groups across libraries",
               "fresh_endpoint_compilation": "only groups used by its frozen library and application cap",
               "fit_terminal_bit_count_calls": model_index * len(cases) * 4,
               "fit_terminal_answer_events": model_index * len(cases) * len(raw_masks) * 4,
               "fit_selected_physical_replay": {"sender_scalar_nands": improvements[-1]["sender_scalar_nands"],
                                                 "decoder_scalar_nands": improvements[-1]["decoder_scalar_nands"],
                                                 "packet_bits": actual_bits,
                                                 "terminal_answer_bits": len(cases) * len(raw_masks) * 4},
               "best_cap_two_diagnostic": {"checkpoint": diagnostic,
                                           "checkpoint_sha256": canonical_sha256(diagnostic),
                                           "training_rank": diagnostic_rank, "training_loss": diagnostic_loss,
                                           "diagnostic_only": True, "separately_fitted": False},
               "fit_cache": "one128-probe and one training-input column evaluation per menu; smaller probe prefixes are views",
               "provided": ["generic16-function NAND catalogue", "library sizes1/2/3", "anonymous three-port subsets",
                            "COPY/constants", "one/two-call expression generator", "fixed hypothetical probe order",
                            "public program matching", "four-port raw fallback"],
               "learned": ["binary NAND library subset", "public probe budget"],
               "basis_names_or_target_formulas_supplied": False,
               "selection": "terminal errors, packet bits, public+sender+decoder work, library NAND size, stable syntax",
               "work_unit": "one scalar NAND or one candidate-match test",
               "external_certification_used_in_fitting": False,
               "runtime_seconds": time.perf_counter() - started,
               "learner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "packet_io_sha256": IO_SHA256, "codec_sha256": CODEC_SHA256}
    return best, history


def smoke():
    # Only a generic primitive library and unrelated repeated synthetic question.
    nand_id = next(index for index, node in enumerate(_binary()) if node.mask == 7)
    checkpoint = _checkpoint((nand_id,), 8)
    candidates, stats = _catalogue((nand_id,), 2)
    checks = 0
    for candidate in candidates:
        proposed = {"ports": [0, 1, 2], "omitted_port": 3, "dag": candidate.dag}
        for code in range(8):
            packet = tuple((code >> bit) & 1 for bit in range(3))
            if receive_plan(proposed, packet, 3) != ((candidate.signature >> code) & 1):
                raise ValueError("Scalar physical NAND DAG changed its catalogue semantics")
            checks += 1
    question = ((1, -4, 7), (2, -2), (-3, 5), (6, -8))
    wiring = (question,) * 4
    before = canonical_sha256(checkpoint)
    for max_calls in (1, 2):
        proposed = plan(checkpoint, wiring, max_calls=max_calls)
        for raw in (0, 173, 511):
            packet = send_plan(wiring, raw, proposed)
            wanted = _io().query_values(wiring, raw, (0, 1, 2, 3))
            if tuple(receive_plan(proposed, packet, port) for port in range(4)) != wanted:
                raise ValueError("Synthetic physical packet path disagreed with frozen parser")
    if canonical_sha256(checkpoint) != before:
        raise ValueError("No-update planning modified the frozen library")
    return {"synthetic_only": True, "NAND_DAG_truth_rows_checked": checks,
            "catalogue": stats, "one_call_ablation_same_parameters": True,
            "learner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "packet_io_sha256": IO_SHA256}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.parse_args()
    print(json.dumps(smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
