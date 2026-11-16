"""Cross the two frozen tracing programs and switch controllers without fitting."""

import argparse
import hashlib
import json
from datetime import datetime, timezone

import assess
import panels


STRATEGIES = {"joint_counterfactual":"joint", "singleton_occurrence":"singleton", "direct_counterfactual":"direct"}


def derived(out):
    originals = {k:assess.load(out / (k + ".json")) for k in ("singleton", "joint")}
    joint = originals["joint"] | {"trace":originals["singleton"]["trace"]}
    singleton = originals["singleton"] | {"trace":originals["joint"]["trace"]}
    return {"joint_counterfactual":joint, "singleton_occurrence":singleton, "direct_counterfactual":joint}


def freeze(out):
    path = out / "crossover_freeze.json"
    stamp = assess.load(path)["utc"] if path.exists() else datetime.now(timezone.utc).isoformat()
    checkpoint_hashes = {k:hashlib.sha256(assess.canonical(v)).hexdigest() for k,v in derived(out).items()}
    record = {
        "utc":stamp, "kind":"post-training mechanism control",
        "reason":"The trained one-switch and joint-switch policies selected different source traces. Compare both controllers and the same direct head with both traces.",
        "timing":"Specified after inspecting training settings and before inspecting any target scores. No further fitting.",
        "script_sha256":assess.file_hash(assess.RESEARCH/"crossover.py"),
        "original_bindings":assess.file_hash(out/"checkpoints.json"),
        "direct_head_binding":assess.file_hash(out/"direct.json"),
        "crossed_policy_sha256":checkpoint_hashes,
    }
    assess.bind(path, record)
    return record


def run(out):
    if not (out/"crossover_freeze.json").exists():
        raise ValueError("The crossed policy definitions must already be bound")
    freeze(out)
    conditions = {k:{} for k in STRATEGIES}
    schedules = assess.rosters()
    sender_policies, receiver_policies = derived(out), derived(out)
    head = assess.load(out/"direct.json")["head"]
    for split in ("historical","held"):
        for name in STRATEGIES:
            conditions[name][split] = []
        for ident, wiring, meta in schedules[split]:
            answers = [tuple(panels.truth(wiring, raw)) for raw in range(512)]
            semantic = assess.grammar(wiring, answers)
            for name, strategy in STRATEGIES.items():
                row = assess.measure(strategy, sender_policies[name], receiver_policies[name], head,
                                     wiring, meta, ident, answers, semantic)
                conditions[name][split].append(row)
    report = {"freeze_sha256":assess.file_hash(out/"crossover_freeze.json"),
              "conditions":conditions, "summary":{name:{s:assess.summarize(rows) for s,rows in data.items()}
                                                  for name,data in conditions.items()}}
    assess.bind(out/"crossover.json", report)
    return report["summary"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze","assess"))
    parser.add_argument("--out", type=assess.Path, default=assess.DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps((freeze if args.action == "freeze" else run)(args.out), indent=2))
