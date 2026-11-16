"""Fit public tracing and anonymous packet switches; reuse a frozen NAND reader.

The parser, probe loops, trial-mask generator, width comparisons and physical
slot convention are supplied. The trace mode/accumulator/initial bit, binary
acceptance program and bounded horizon are selected by terminal training loss.
Public plans never inspect the actual raw input or a grading answer.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CODEC_PATH = ROOT / "experiments/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/codec.py"
CODEC_SHA256 = "6985190eae222a30bbeb63ab6f8bbb55210365e31cce97997a0842fa9bf2470b"
PARSER_PATH = ROOT / "artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/varied_checkpoint.json"
PARSER_SHA256 = "b328cd2bcd4aa95976fad2513252ad1c23e0e21fa337323b84919a8ea93db0cd"
WORK_KEYS = ("NAND", "READ", "COPY", "WRITE", "CONST", "IDENTITY_COMPARE",
             "WIDTH_COMPARE", "MASK_TRIAL", "SUPPORT_READ", "SLOT_WRITE", "PUBLIC_OR", "GROUP_READ")


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def _codec():
    if hashlib.sha256(CODEC_PATH.read_bytes()).hexdigest() != CODEC_SHA256:
        raise ValueError("The frozen NAND codec source changed")
    name = "frozen_nand_codec_for_group_sender"
    spec = importlib.util.spec_from_file_location(name, CODEC_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def _frozen():
    raw = PARSER_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PARSER_SHA256:
        raise ValueError("The frozen varied parser checkpoint changed")
    return json.loads(raw)


@lru_cache(maxsize=1)
def _compiled_parser():
    codec, frozen = _codec(), _frozen()
    parser = {role: codec._compile_program(frozen["parser"][role], 2, 5)
              for role in ("literal", "clause", "question")}
    parser |= {key: frozen["parser"][key] for key in ("clause_initial", "question_initial")}
    return parser


@lru_cache(maxsize=1)
def _binary():
    return tuple(_codec().binary_catalogue()[0])


def _question(question):
    return _codec()._wiring((question,) * 4)[0]


def _raw_values(raw):
    if type(raw) in (int, bool):
        if not 0 <= raw < 512:
            raise ValueError("Nine-bit raw mask required")
        return tuple((raw >> source) & 1 for source in range(9))
    return _codec()._literal_bits(raw, 9, "Raw source data")


def _question_scalar(question, raw, actions):
    values = _raw_values(raw)

    def read(source):
        actions["READ"] += 1
        return values[source]

    return _codec()._scan_question(_compiled_parser(), question, read, actions)


def question_value(checkpoint, question, raw_mask):
    _validate_parser(checkpoint)
    return _question_scalar(_question(question), raw_mask, Counter())


def _validate_parser(checkpoint):
    if (checkpoint["parser"] != _frozen()["parser"]
            or int(checkpoint["missing_source"]) != int(_frozen()["missing_source"])):
        raise ValueError("The previous varied parser must remain unchanged")


def _work(actions):
    return sum(int(actions.get(key, 0)) for key in WORK_KEYS)


def _scaled(actions, scale):
    return {key: int(value) * scale for key, value in actions.items()}


@lru_cache(maxsize=2048)
def _probe_question(question):
    actions = Counter()
    values = tuple(_question_scalar(question, raw, actions) for raw in range(512))
    return values, dict(actions)


def answer_table(checkpoint, question, raw_masks=None):
    """Public hypothetical parser evaluations, not grading-oracle answers."""
    _validate_parser(checkpoint)
    question = _question(question)
    if raw_masks is None:
        return _probe_question(question)[0]
    return tuple(_question_scalar(question, raw, Counter()) for raw in raw_masks)


@lru_cache(maxsize=2048)
def _observations(wiring, mode):
    """Public probe streams and cold-work profile, reused between fit candidates."""
    codec = _codec()
    streams, actions = {}, Counter()
    for question in dict.fromkeys(wiring):
        source_streams = []
        if mode == "identity":
            for source in range(9):
                row = []
                for clause in question:
                    actions["GROUP_READ"] += 1
                    for literal in clause:
                        actions["READ"] += 1
                        actions["IDENTITY_COMPARE"] += 1
                        row.append(int(abs(literal) - 1 == source))
                source_streams.append(tuple(row))
        elif mode == "counterfactual":
            values, probe_actions = _probe_question(question)
            actions.update(probe_actions)
            actions["hypothetical_parser_evaluations"] += 512
            difference = next(node for node in _binary() if node.mask == 6)
            for source in range(9):
                row = []
                for raw in range(512):
                    if (raw >> source) & 1:
                        continue
                    actions["READ"] += 2
                    row.append(codec._nand_eval(difference.expr, (values[raw], values[raw | (1 << source)]), actions))
                    actions["local_difference_tests"] += 1
                source_streams.append(tuple(row))
        else:
            raise ValueError("Trace mode must be identity or counterfactual")
        streams[question] = tuple(source_streams)
    return streams, dict(actions)


def _trace_for(checkpoint, wiring):
    codec = _codec()
    wiring = codec._wiring(wiring)
    expr = codec._compile_program(checkpoint["trace"]["program"], 2, 5)
    initial = int(checkpoint["trace"]["initial"])
    if initial not in (0, 1):
        raise ValueError("Trace initial state must be a bit")
    streams, base_actions = _observations(wiring, checkpoint["trace"]["mode"])
    actions, supports = Counter(base_actions), {}
    for question, source_streams in streams.items():
        mask = 0
        for source, values in enumerate(source_streams):
            state = initial
            actions["CONST"] += 1
            actions["WRITE"] += 1
            for value in values:
                state = codec._nand_eval(expr, (state, value), actions)
                actions["WRITE"] += 1
                actions["trace_updates"] += 1
            mask += state << source
        supports[question] = mask
    masks = tuple(supports[question] for question in wiring)
    signature = canonical_sha256({"parser": PARSER_SHA256, "trace": checkpoint["trace"],
                                  "wiring": wiring, "support_masks": masks})
    actions["cold_work_units"] = _work(actions)
    return {"wiring": wiring, "support_masks": masks, "trace_signature": signature,
            "public_actions": dict(actions),
            "accounting": "cold logical public-work profile; cached public probe streams may amortize compilation"}


def _plan_from_trace(wiring, computed_mask, traced):
    if type(computed_mask) is not int or not 0 <= computed_mask < 16:
        raise ValueError("A four-port computed flag mask is required")
    codec = _codec()
    identities = tuple(codec._question_identity(question) for question in wiring)
    computed = tuple(port for port in range(4) if (computed_mask >> port) & 1)
    routing = Counter()
    representatives = []
    for reader in range(4):
        representative = None
        for port in computed:
            routing["IDENTITY_COMPARE"] += 1
            if identities[port] == identities[reader]:
                representative = port
                break
        representatives.append(representative)
    representatives = tuple(representatives)
    chosen_queries = tuple(sorted(set(port for port in representatives if port is not None)))
    source_mask = 0
    for port, representative in enumerate(representatives):
        if representative is None:
            routing["SUPPORT_READ"] += 9
            source_mask |= int(traced["support_masks"][port])
            routing["PUBLIC_OR"] += 1
    slots = tuple(("source", source) for source in range(9) if (source_mask >> source) & 1)
    slots += tuple(("query", port) for port in chosen_queries)
    source_slots = tuple(next((slot for slot, descriptor in enumerate(slots) if descriptor == ("source", source)), None)
                         for source in range(9))
    query_slots = tuple(None if representative is None else slots.index(("query", representative))
                        for representative in representatives)
    routing["SLOT_WRITE"] += len(slots)
    routing["cold_work_units"] = _work(routing)
    return {"computed_mask": computed_mask, "width": len(slots),
            "slots": [{"kind": kind, "index": index} for kind, index in slots],
            "source_mask": source_mask, "source_slots": list(source_slots),
            "query_slots": list(query_slots), "query_representatives": list(representatives),
            "support_masks": list(traced["support_masks"]), "trace_signature": traced["trace_signature"],
            "routing_actions": dict(routing),
            "public_actions": dict(Counter(traced["public_actions"]) + routing)}


def _choose(widths, variant, accept_mask, horizon, accept_work):
    """Fit-only scalar accelerator of the same anonymous runtime scan."""
    current, trials, acceptances, rounds, changed = 0, 0, 0, 0, 0
    seen = 1
    toggles = (1, 2, 4, 8) if variant == "singleton" else tuple(range(1, 16))
    for _ in range(horizon):
        anchor, incumbent = current, current
        rounds += 1
        for toggle in toggles:
            candidate = anchor ^ toggle
            trials += 1
            seen |= 1 << candidate
            if variant == "singleton" and widths[candidate] >= widths[anchor]:
                continue
            acceptances += 1
            address = int(widths[candidate] < widths[incumbent]) + 2 * int(widths[candidate] == widths[incumbent])
            if (accept_mask >> address) & 1:
                incumbent = candidate
        current = incumbent
        if current == anchor:
            break
        changed += 1
    work = trials * (1 + int(variant == "singleton")) + acceptances * (2 + accept_work)
    return current, {"mask_trials": trials, "unique_mask_bits": seen, "acceptance_evaluations": acceptances,
                     "rounds": rounds, "mask_updates": changed, "controller_work_units": work}


class Runtime:
    """Frozen parameters and public-only caches; no raw/packet history."""

    def __init__(self, checkpoint):
        checkpoint = json.loads(json.dumps(checkpoint))
        _validate_parser(checkpoint)
        self.checkpoint = checkpoint
        self._trace_cache, self._plan_cache = {}, {}

    def trace_public(self, wiring):
        wiring = _codec()._wiring(wiring)
        if wiring not in self._trace_cache:
            self._trace_cache[wiring] = _trace_for(self.checkpoint, wiring)
        return self._trace_cache[wiring]

    def plan_from_mask(self, wiring, computed_mask, traced=None):
        wiring = _codec()._wiring(wiring)
        traced = self.trace_public(wiring) if traced is None else traced
        if _codec()._wiring(traced["wiring"]) != wiring:
            raise ValueError("The supplied public trace belongs to another wiring")
        return _plan_from_trace(wiring, computed_mask, traced)

    def plan(self, wiring):
        wiring = _codec()._wiring(wiring)
        if wiring in self._plan_cache:
            return self._plan_cache[wiring]
        variant = self.checkpoint["variant"]
        if variant not in ("singleton", "joint"):
            raise ValueError("A fitted singleton or joint controller is required")
        controller = self.checkpoint["controller"]
        accept = _codec()._compile_program(controller["accept"], 2, 5)
        traced = self.trace_public(wiring)
        plans = {0: self.plan_from_mask(wiring, 0, traced)}
        actions = Counter(traced["public_actions"])
        actions.pop("cold_work_units", None)
        current, history, seen = 0, [], {0}
        toggles = (1, 2, 4, 8) if variant == "singleton" else tuple(range(1, 16))
        for round_index in range(int(controller["horizon"])):
            anchor, incumbent = current, current
            for toggle in toggles:
                candidate = anchor ^ toggle
                actions["MASK_TRIAL"] += 1
                if candidate not in plans:
                    plans[candidate] = self.plan_from_mask(wiring, candidate, traced)
                seen.add(candidate)
                trial, old = plans[candidate]["width"], plans[incumbent]["width"]
                allowed = variant != "singleton" or trial < plans[anchor]["width"]
                actions["WIDTH_COMPARE"] += int(variant == "singleton")
                accepted = False
                if allowed:
                    actions["WIDTH_COMPARE"] += 2
                    accepted = bool(_codec()._nand_eval(accept, (int(trial < old), int(trial == old)), actions))
                    actions["acceptance_evaluations"] += 1
                if accepted:
                    incumbent = candidate
                history.append({"round": round_index, "anchor": anchor, "toggle": toggle,
                                "candidate": candidate, "width": trial, "accepted": accepted})
            current = incumbent
            actions["rounds"] += 1
            if current == anchor:
                break
            actions["mask_updates"] += 1
            if variant == "singleton" and ((current ^ anchor).bit_count() != 1
                    or plans[current]["width"] >= plans[anchor]["width"]):
                raise ValueError("A singleton update was not one strictly improving physical switch")
        for candidate in seen:
            routing = Counter(plans[candidate]["routing_actions"])
            routing.pop("cold_work_units", None)
            actions.update(routing)
        actions["mask_trials"] = actions["MASK_TRIAL"]
        actions["unique_masks"] = len(seen)
        actions["cold_work_units"] = _work(actions)
        result = plans[current] | {"public_actions": dict(actions), "trials": history,
                                   "subset_generation": "supplied one-flag neighbors" if variant == "singleton"
                                   else "supplied enumeration of all15 nonempty flag subsets"}
        self._plan_cache[wiring] = result
        return result


@lru_cache(maxsize=128)
def _runtime(serialized):
    return Runtime(json.loads(serialized))


def _agent(checkpoint):
    return _runtime(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")))


def trace_public(checkpoint, wiring):
    return json.loads(json.dumps(_agent(checkpoint).trace_public(wiring)))


def support_masks(checkpoint, wiring):
    return tuple(trace_public(checkpoint, wiring)["support_masks"])


def plan_from_mask(checkpoint, wiring, computed_mask, traced=None):
    return _agent(checkpoint).plan_from_mask(wiring, computed_mask, traced)


def plan(checkpoint, wiring):
    return json.loads(json.dumps(_agent(checkpoint).plan(wiring)))


def trace_send_plan(checkpoint, wiring, raw, physical_plan):
    _validate_parser(checkpoint)
    wiring, values, actions = _codec()._wiring(wiring), _raw_values(raw), Counter()
    payload = []
    for descriptor in physical_plan["slots"]:
        index = descriptor["index"]
        if descriptor["kind"] == "source":
            actions["READ"] += 1
            value = values[index]
        elif descriptor["kind"] == "query":
            value = _question_scalar(wiring[index], values, actions)
        else:
            raise ValueError("Unknown physical slot type")
        payload.append(value)
        actions["WRITE"] += 1
    return {"bits": tuple(payload), "actions": dict(actions), "width": len(payload)}


def send_plan(checkpoint, wiring, raw, physical_plan):
    return trace_send_plan(checkpoint, wiring, raw, physical_plan)["bits"]


def trace_receive_plan(checkpoint, wiring, bits, delayed_port, physical_plan):
    _validate_parser(checkpoint)
    wiring = _codec()._wiring(wiring)
    bits = _codec()._literal_bits(bits, physical_plan["width"], "Physical packet")
    if type(delayed_port) is not int or not 0 <= delayed_port < 4:
        raise ValueError("The delayed port must be an integer0..3")
    actions, slot = Counter(), physical_plan["query_slots"][delayed_port]
    if slot is not None:
        answer = bits[slot]
        actions.update({"READ": 1, "COPY": 1, "WRITE": 1})
    else:
        def read(source):
            slot = physical_plan["source_slots"][source]
            if slot is None:
                actions["CONST"] += 1
                return checkpoint["missing_source"]
            actions["READ"] += 1
            return bits[slot]

        answer = _codec()._scan_question(_compiled_parser(), wiring[delayed_port], read, actions)
        actions["WRITE"] += 1
    return {"answer": answer, "actions": dict(actions), "width": len(bits)}


def receive_plan(checkpoint, wiring, bits, delayed_port, physical_plan):
    return trace_receive_plan(checkpoint, wiring, bits, delayed_port, physical_plan)["answer"]


def send(checkpoint, wiring, raw):
    public_plan = plan(checkpoint, wiring)  # Width is chosen before raw is read.
    return send_plan(checkpoint, wiring, raw, public_plan)


def receive(checkpoint, wiring, bits, delayed_port):
    return receive_plan(checkpoint, wiring, bits, delayed_port, plan(checkpoint, wiring))


def plan_answer_columns(checkpoint, wiring, physical_plan, raw_masks):
    """Fit-only exact parser accelerator; normal receivers execute NAND ASTs."""
    _validate_parser(checkpoint)
    wiring = _codec()._wiring(wiring)
    raw_masks = tuple(raw_masks)
    source_mask, default = physical_plan["source_mask"], checkpoint["missing_source"]
    columns = []
    for port, representative in enumerate(physical_plan["query_representatives"]):
        question = wiring[port if representative is None else representative]
        table = _probe_question(question)[0]
        values = raw_masks if representative is not None else tuple(
            (raw & source_mask) | ((511 ^ source_mask) if default else 0) for raw in raw_masks)
        columns.append(sum(table[raw] << lane for lane, raw in enumerate(values)))
    return tuple(columns)


def _checkpoint(variant, mode, trace_node, initial, accept_node, horizon):
    codec, frozen = _codec(), _frozen()
    result = {"schema_version": 1, "parser": frozen["parser"], "missing_source": frozen["missing_source"],
              "parser_source_sha256": CODEC_SHA256, "parser_checkpoint_sha256": PARSER_SHA256,
              "variant": variant,
              "trace": {"mode": mode, "program": codec._program_record(trace_node, 2), "initial": initial},
              "controller": {"accept": codec._program_record(accept_node, 2), "horizon": horizon,
                             "initial_computed_mask": 0,
                             "acceptance_inputs": ["trial_width_less_than_incumbent", "trial_width_equal_to_incumbent"]}}
    return json.loads(json.dumps(result, sort_keys=True, separators=(",", ":")))


def _examples(examples, raw_masks):
    result = []
    for example in examples:
        if isinstance(example, dict):
            wiring, answers = example["wiring"], example["answers"]
            if len(answers) == 4 and all(type(value) is int for value in answers):
                columns = tuple(answers)
            else:
                rows = [_codec()._literal_bits(row, 4, "Training answer row") for row in answers]
                if len(rows) != len(raw_masks):
                    raise ValueError("Training answer rows must align with raw_masks")
                columns = tuple(sum(row[port] << lane for lane, row in enumerate(rows)) for port in range(4))
        else:
            wiring, answers = example
            rows = [_codec()._literal_bits(row, 4, "Training answer row") for row in answers]
            if len(rows) != len(raw_masks):
                raise ValueError("Training answer rows must align with raw_masks")
            columns = tuple(sum(row[port] << lane for lane, row in enumerate(rows)) for port in range(4))
        result.append((_codec()._wiring(wiring), columns))
    if not result:
        raise ValueError("At least one anonymous training menu is required")
    return result


def fit(examples, raw_masks, variant="joint"):
    if variant not in ("singleton", "joint"):
        raise ValueError("Fit variant is singleton or joint")
    started = time.perf_counter()
    raw_masks = tuple(raw_masks)
    if not raw_masks or any(type(raw) is not int or not 0 <= raw < 512 for raw in raw_masks):
        raise ValueError("Training raw masks must be nine-bit integers")
    examples = _examples(examples, raw_masks)
    nodes, best, best_rank, improvements = _binary(), None, None, []
    plan_loss_cache, candidate_count, cache_hits = {}, 0, 0
    trace_profiles = []
    for mode in ("identity", "counterfactual"):
        for trace_node in nodes:
            for initial in (0, 1):
                template = _checkpoint(variant, mode, trace_node, initial, nodes[0], 1)
                runtime = Runtime(template)
                case_data = []
                for case_index, (wiring, targets) in enumerate(examples):
                    traced = runtime.trace_public(wiring)
                    all_plans = tuple(runtime.plan_from_mask(wiring, mask, traced) for mask in range(16))
                    errors = []
                    for physical in all_plans:
                        key = (case_index, physical["source_mask"], tuple(physical["query_representatives"]))
                        if key not in plan_loss_cache:
                            predicted = plan_answer_columns(template, wiring, physical, raw_masks)
                            plan_loss_cache[key] = sum((a ^ b).bit_count() for a, b in zip(predicted, targets, strict=True))
                        else:
                            cache_hits += 1
                        errors.append(plan_loss_cache[key])
                    case_data.append((traced, all_plans, tuple(errors)))
                trace_profiles.append({"mode": mode, "truth_mask": trace_node.mask, "initial": initial,
                                       "distinct_training_supports": len({tuple(row[0]["support_masks"]) for row in case_data})})
                for accept_node in nodes:
                    accept_actions = Counter()
                    _codec()._nand_eval(accept_node.expr, (0, 0), accept_actions)
                    accept_work = _work(accept_actions)
                    for horizon in (1, 2, 3, 4):
                        candidate_count += 1
                        wrong = width = work = 0
                        chosen_masks = []
                        for traced, all_plans, errors in case_data:
                            widths = tuple(physical["width"] for physical in all_plans)
                            mask, counts = _choose(widths, variant, accept_node.mask, horizon, accept_work)
                            chosen_masks.append(mask)
                            wrong += errors[mask]
                            width += widths[mask] * len(raw_masks)
                            work += traced["public_actions"]["cold_work_units"] + counts["controller_work_units"]
                            work += sum(all_plans[mask]["routing_actions"]["cold_work_units"] for mask in range(16)
                                        if (counts["unique_mask_bits"] >> mask) & 1)
                        size = trace_node.gates + accept_node.gates
                        rank = (wrong, width, work, size, mode, trace_node.expr, initial, accept_node.expr, horizon)
                        if best_rank is None or rank < best_rank:
                            best_rank = rank
                            best = _checkpoint(variant, mode, trace_node, initial, accept_node, horizon)
                            improvements.append({"candidate": candidate_count, "wrong_answer_bits": wrong,
                                                 "transmitted_bits": width, "public_cold_work_units": work,
                                                 "NAND_parameter_gates": size, "chosen_masks": chosen_masks})
    frozen = canonical_sha256(best)
    # Validate the selected anonymous controller through NAND acceptance, not
    # the fit-only scalar accelerator, before any external assessment.
    runtime = Runtime(best)
    wrong = width = work = 0
    for wiring, targets in examples:
        physical = runtime.plan(wiring)
        predicted = plan_answer_columns(best, wiring, physical, raw_masks)
        wrong += sum((a ^ b).bit_count() for a, b in zip(predicted, targets, strict=True))
        width += physical["width"] * len(raw_masks)
        work += physical["public_actions"]["cold_work_units"]
    if (wrong, width, work) != best_rank[:3] or canonical_sha256(best) != frozen:
        raise ValueError("Selected NAND runtime disagreed with training controller selection")
    history = {"variant": variant, "checkpoint_sha256": frozen, "candidates_scored": candidate_count,
               "training_menus": len(examples), "training_raw_masks": len(raw_masks),
               "terminal_answer_bits": 4 * len(examples) * len(raw_masks),
               "loss": {"wrong_answer_bits": wrong, "transmitted_bits": width,
                        "public_cold_work_units": work, "NAND_parameter_gates": best_rank[3]},
               "improvement_trace": improvements, "trace_profiles": trace_profiles,
               "distinct_physical_training_losses": len(plan_loss_cache), "plan_loss_cache_hits": cache_hits,
               "provided": ["frozen varied NAND parser", "identity or counterfactual probe loops",
                            "NAND difference measurement", "anonymous trial masks", "width comparisons",
                            "all-raw start", "physical source/query slot routing"],
               "learned": ["trace mode", "trace accumulator and initial bit", "acceptance NAND program", "horizon"],
               "subset_generation_learned": False,
               "runtime_subset_enumeration": "4 singleton or15 joint trials per round, horizon1..4",
               "trace_soundness_gate": False,
               "public_work_units": {key: 1 for key in WORK_KEYS},
               "work_accounting": "cold logical public primitives; public compiler caches amortize repeated evaluations",
               "fit_seconds": time.perf_counter() - started,
               "sender_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return best, history


def smoke():
    nodes = _binary()
    by_mask = {node.mask: node for node in nodes}
    # Primitive synthetic wiring/inputs only. No panel or external grading data.
    question = ((1, -4, 7), (2, -2), (-3, 5), (6, -8))
    wiring = (question,) * 4
    checkpoint = _checkpoint("joint", "identity", by_mask[10], 1, by_mask[0], 1)
    traced = trace_public(checkpoint, wiring)
    if tuple(traced["support_masks"]) != (511,) * 4:
        raise ValueError("Synthetic trace accumulator failed raw public traversal")
    comparisons = 0
    for mask in range(16):
        physical = plan_from_mask(checkpoint, wiring, mask, traced)
        columns = plan_answer_columns(checkpoint, wiring, physical, (0, 173, 511))
        for lane, raw in enumerate((0, 173, 511)):
            payload = send_plan(checkpoint, wiring, raw, physical)
            for port in range(4):
                actual = receive_plan(checkpoint, wiring, payload, port, physical)
                if actual != ((columns[port] >> lane) & 1):
                    raise ValueError("Packed physical-plan accelerator disagreed with NAND execution")
                comparisons += 1
    for variant in ("singleton", "joint"):
        checkpoint = _checkpoint(variant, "identity", by_mask[10], 1, by_mask[10], 2)
        runtime = Runtime(checkpoint)
        actual = runtime.plan(wiring)
        trace = runtime.trace_public(wiring)
        widths = [runtime.plan_from_mask(wiring, mask, trace)["width"] for mask in range(16)]
        actions = Counter()
        _codec()._nand_eval(by_mask[10].expr, (0, 0), actions)
        selected, _ = _choose(widths, variant, 10, 2, _work(actions))
        if selected != actual["computed_mask"]:
            raise ValueError("Anonymous trial-loop scalar accelerator disagreed")
    return {"synthetic_only": True, "physical_packet_answer_checks": comparisons,
            "singleton_joint_controller_replay": True,
            "parser_checkpoint_sha256": PARSER_SHA256, "parser_source_sha256": CODEC_SHA256,
            "sender_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.parse_args()
    print(json.dumps(smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
