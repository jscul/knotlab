"""Re-score all returned atomic programs without importing the fitting engine."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import enumerate_programs
import independent
from lesson_inputs import world_weights


TICKET = "ATOMIC-FOLD-20261114-001"
ROOT = Path(__file__).resolve().parents[2]
FAMILY = TICKET + "-E001_atomic_actions"
FOLLOW_UP = TICKET + "-E002_program_mutation"


def delayed_pair():
    # The decoder will learn the pair and the specific branch after encoding.
    views = [tuple(independent.oracle(w, c, q) for q in (1, 2) for c in ("c0", "c2", "c4"))
             for w in range(64)]
    signatures = set(views)
    return {"patterns_per_branch": [len({v[a:a + 3] for v in signatures}) for a in (0, 3)],
            "joint_patterns": len(signatures), "minimum_bits": (len(signatures) - 1).bit_length()}


def inspect_winner(cue, queries, item, weights):
    program = item["program"]
    gates = [(g["op"].upper(), g["left"], g["right"]) for g in program["gates"]]
    taps = program["outputs"]
    width = len(taps)
    dec = {q: item["decoder"][str(q)] for q in queries}
    code = [tuple(independent.execute(w, gates, taps)) for w in range(64)]
    codes = [sum(b << i for i, b in enumerate(row)) for row in code]
    wanted = [tuple(int(independent.oracle(w, cue, q)) for q in queries) for w in range(64)]
    seen = [tuple(dec[q][word] for q in queries) for word in codes]
    if codes != item["evaluation"]["codes_by_world"]:
        raise ValueError("Independent evaluator disagrees on the emitted bits")
    for i, q in enumerate(queries):
        pred_mask = sum(s[i] << w for w, s in enumerate(seen))
        truth_mask = sum(s[i] << w for w, s in enumerate(wanted))
        saved = item["evaluation"]["queries"][str(q)]
        if (pred_mask, truth_mask) != (int(saved["prediction_mask_hex"], 16), int(saved["truth_mask_hex"], 16)):
            raise ValueError("Held-out truth or predictions differed")
    # An evaluator can read the answers. Only this offline re-fit uses labels here.
    even = [w for w in range(64) if w.bit_count() % 2 == 0]
    odd = sorted(set(range(64)) - set(even))
    for word in range(1 << width):
        group = [w for w in even if codes[w] == word]
        for i, q in enumerate(queries):
            majority = int(2 * sum(wanted[w][i] for w in group) > len(group))
            if dec[q][word] != majority:
                raise ValueError("Decoder differs from a training-only majority lookup")
    signatures = set(wanted)
    sufficient = all(len({wanted[w] for w in range(64) if codes[w] == c}) == 1 for c in set(codes))
    minimal = sufficient and len(set(codes)) == len(signatures)
    correct = [sum(bit == label for bit, label in zip(s, t)) for s, t in zip(seen, wanted)]
    board = {}
    for key, worlds in (("train", even), ("held_out", odd), ("all", range(64))):
        board[key] = [sum(correct[w] for w in worlds), len(worlds) * len(queries)]
        if board[key] != [item["evaluation"][key]["correct"], item["evaluation"][key]["total"]]:
            raise ValueError(f"Producer and checker disagree for {key}")

    def support(values):
        return [i for i in range(6) if any(values[w] != values[w ^ (1 << i)] for w in range(64))]

    composition = None
    if 1 in queries and 2 in queries:
        # Offer the decoded allowed h to two more arbitrary unary rules.
        passes = 0
        first_bad = None
        for w in range(64):
            decoded = seen[w][queries.index(1)] | (seen[w][queries.index(2)] << 1)
            actual = wanted[w][queries.index(1)] | (wanted[w][queries.index(2)] << 1)
            for tail1 in range(4):
                for tail2 in range(4):
                    a = bool(decoded & tail1 & tail2)
                    b = bool(actual & tail1 & tail2)
                    passes += a == b
                    if a != b and first_bad is None:
                        first_bad = [w, tail1, tail2]
        composition = {"correct": passes, "total": 1024, "first_mismatch": first_bad}
    return {
        "width": width, "live_gates": program["live_gates"], "gates": gates, "taps": taps, "decoder": dec,
        **board, "sufficient": sufficient, "minimal_partition": minimal,
        "minimum_possible_width": (len(signatures) - 1).bit_length(), "realized_codes": len(set(codes)),
        "code_input_support": support(codes), "answer_input_support": support(seen),
        "target_input_support": support(wanted),
        "lesson_correct": sum(weights[w]*correct[w] for w in range(64)),
        "lesson_total": sum(weights.values())*len(queries), "composition": composition,
        "first_wrong_world": next((w for w in range(64) if seen[w] != wanted[w]), None),
        "first_exact_training_sample": item["search"]["first_exact_sample"],
    }


def run(family=FAMILY):
    raw = ROOT / "artifacts" / TICKET / family / "results.jsonl"
    producer = ROOT / "experiments" / TICKET / family / "job.py"
    producer_sha = hashlib.sha256(producer.read_bytes()).hexdigest()
    state = json.loads((raw.parent / "state.json").read_text())
    if not state["complete"] or state["counts"]["ok"] != 3 or state["job_sha"] != producer_sha:
        raise ValueError("Incomplete run or changed producer")
    method_pair = ("cem", "blind") if family == FAMILY else ("guided", "neutral")
    records = sorted((json.loads(line) for line in raw.read_bytes().splitlines()), key=lambda r: r["case"])
    if ([r["case"] for r in records] != ["seed-17", "seed-31", "seed-53"] or
            any(r["status"] != "ok" for r in records)):
        raise ValueError("The frozen three-seed run is incomplete")
    weights, source = world_weights()
    panels, metrics, evaluations = [], {}, 0
    for rec in records:
        seed = rec["result"]["seed"]
        for ctx in rec["result"]["contexts"]:
            cue, queries = ctx["context_id"], ctx["query_ids"]
            methods = ctx["methods"]
            for w in ("1", "2"):
                guided = methods[method_pair[0]]["widths"][w]["search"]
                blind = methods[method_pair[1]]["widths"][w]["search"]
                if guided["initial_population_sha256"] != blind["initial_population_sha256"]:
                    raise ValueError("Different initial samples in matched methods")
                if guided["evaluations"] != 12288 or blind["evaluations"] != 12288:
                    raise ValueError("Unmatched candidate-evaluation budgets")
                evaluations += 24576
            for name, info in methods.items():
                candidates = {str(w): inspect_winner(cue, queries, v, weights) for w, v in info["widths"].items()}
                chosen = str(info["chosen_width"])
                if chosen != min(candidates, key=lambda w: (-candidates[w]["train"][0], int(w), candidates[w]["live_gates"])):
                    raise ValueError("Candidate width was not chosen from training alone")
                item = candidates[chosen]
                exact = item["all"][0] == item["all"][1]
                kind = "broad" if len(queries) == 1 else "selective"
                count = metrics.setdefault(name, {}).setdefault(kind, Counter())
                count.update({"fits": 1, "exact": int(exact), "minimal_partitions": int(item["minimal_partition"]),
                              "minimum_width_exact": int(exact and item["width"] == item["minimum_possible_width"]),
                              "width_one": int(item["width"] == 1), "held_out_correct": item["held_out"][0],
                              "held_out_total": item["held_out"][1]})
                panel = {"seed": seed, "context": cue, "use": kind, "method": name,
                         "chosen_width": int(chosen), "widths": candidates}
                if family == FOLLOW_UP and kind == "selective":
                    decoder = {}
                    for q in queries:
                        for value, prediction in enumerate(item["decoder"][q]):
                            code = tuple(value >> j & 1 for j in range(item["width"]))
                            decoder[code, q] = prediction
                    panel["further_composition"] = independent.composition_check(
                        cue, item["gates"], item["taps"], decoder)
                panels.append(panel)
    return {"ticket": TICKET, "evidence_stage": "exploratory", "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
            "producer_sha256": producer_sha, "program_evaluations": evaluations,
            "counts": metrics, "primary": panels, "known_input_sources": source, "delayed_pair": delayed_pair(),
            "size_ordered_reference": enumerate_programs.run(), "independent_controls": independent.self_check()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--follow-up", action="store_true")
    opts = parser.parse_args()
    report = run(FOLLOW_UP if opts.follow_up else FAMILY)
    print(json.dumps(report if opts.json else report["counts"], sort_keys=True, indent=2))
