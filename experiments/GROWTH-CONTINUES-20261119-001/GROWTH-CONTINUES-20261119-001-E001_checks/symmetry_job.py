"""Shared-runner wrapper for the fixed archive symmetry screen."""

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from symmetry_check import archive_cases, run_stage


params = {}


def setup(options):
    params.update(options)


def cases():
    for name, payload in archive_cases(*(Path(params[k]) for k in
                                         ("archive", "controls", "stage_index", "control_index"))):
        if params.get("panel") != "smoke" or name in {"partner-3-age00", "start-00-age22", "start-03-age08"}:
            yield name, payload


def run(case_id, payload):
    return run_stage(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    plan = json.loads((args.runs / "job.json").read_text())
    setup(plan["params"])
    expected = {key for key, _ in cases()}
    actual = load_results(str(args.runs))
    if expected != set(actual):
        raise ValueError(f"archive case records missing: {sorted(expected - set(actual))}")
    results = []
    for case, record in sorted(actual.items()):
        if record["status"] == "ok":
            results.append(record["result"])
        else:
            results.append({"verdict": "partial", "reason": record["status"], "case_id": case,
                            "runner_record": record})
    with args.output.open("x") as output:
        json.dump(results, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    main()
