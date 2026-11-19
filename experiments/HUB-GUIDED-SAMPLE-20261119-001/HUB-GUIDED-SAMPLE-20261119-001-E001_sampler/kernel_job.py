"""Fixed auxiliary sampler jobs and reports for the shared runner."""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from decimal import Decimal, localcontext
from pathlib import Path


STAGES = {
    "start-01-age10": 21516, "start-02-age09": 102871, "start-03-age08": 28065,
    "start-05-age09": 102871, "start-06-age07": 12004, "start-07-age07": 31735,
    "start-08-age09": 102871, "start-09-age06": 4652, "start-10-age07": 4157,
    "start-11-age07": 3493, "start-12-age07": 36394, "start-13-age07": 35408,
    "start-14-age08": 162336, "start-15-age08": 38001,
}

settings = {}


def sha256(file):
    with file.open("rb") as readable:
        return hashlib.file_digest(readable, "sha256").hexdigest()


def setup(params):
    settings.update(params)
    settings["kernel"] = Path(params["kernel"]).resolve()
    settings["inputs"] = Path(params["inputs"]).resolve()
    settings["kernel_digest"] = sha256(settings["kernel"])
    if settings["kernel_digest"] != params["digest"]:
        raise ValueError("the sampler changed after design lock")


def case(stage, seed, width, pool, cache, cap, policy="partner", order="coverage"):
    key = f"{stage}:{seed}"
    return key, {
        "stage": stage,
        "seed": seed,
        "width": width,
        "policy": policy,
        "order": order,
        "pool": pool,
        "local": 22,
        "factor": 1024,
        "cache": cache,
        "cap": cap,
    }


def cases():
    panel = settings["panel"]
    if panel == "smoke":
        for offset in range(4):
            yield case("start-03-age07", 202611197750 + offset, 64, 32, 160, 150000)
    elif panel == "primary":
        for offset in range(24):
            yield case("start-03-age08", 202611205000 + offset, 32, 32, 160, 150000)
    elif panel == "applications":
        for stage, n in STAGES.items():
            if stage == "start-03-age08":
                continue
            if n > 120000:
                width, pool, cache, cap = 2, 8, 768, 40000
            elif n > 40000:
                width, pool, cache, cap = 8, 16, 384, 60000
            else:
                width, pool, cache, cap = 16, 16, 192, 100000
            seed = 202611206000 + 100 * int(stage[6:8])
            for offset in range(8):
                yield case(stage, seed + offset, width, pool, cache, cap)
    elif panel == "fallback":
        for stage in settings["stages"].split(","):
            n = STAGES[stage]
            seed = 202611206050 + 100 * int(stage[6:8])
            for offset in range(4):
                yield case(stage, seed + offset, 1 if n > 120000 else 2, 8, 768 if n > 120000 else 384, 40000)
    else:
        raise ValueError(f"unknown panel: {panel}")


def run(case_id, payload):
    stage = payload["stage"]
    input_path = settings["inputs"] / f"{stage}.txt"
    digest = sha256(input_path)
    arg = (
        settings["kernel"], input_path, 1, payload["seed"], payload["width"], payload["policy"],
        payload["order"], payload["pool"], payload["local"], payload["factor"], payload["cache"],
        1, payload["cap"],
    )
    process = subprocess.run(tuple(map(str, arg)), capture_output=True, text=True, check=True)
    header, result = map(json.loads, process.stdout.splitlines())
    expected_n = 386 if stage == "start-03-age07" else STAGES[stage]
    if header["n"] != expected_n or result["seed"] != payload["seed"]:
        raise ValueError(f"wrong input or seed for {case_id}")
    if not result.get("status") and not result["weight"].isdecimal():
        raise ValueError(f"invalid count for {case_id}")
    return {
        "input_sha256": digest,
        "config": header,
        "result": result,
    }


def quantile(ordered, fraction):
    index = Decimal(len(ordered) - 1) * fraction
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (index - low) * (ordered[high] - ordered[low])


def summarize(rows, scheduled):
    complete = [row for row in rows if ((row.get("result") or {}).get("result") or {}).get("weight") is not None]
    values = sorted(Decimal(row["result"]["result"]["weight"]) for row in complete)
    out = {"completed": len(complete), "recorded": len(rows), "scheduled": scheduled, "runs": rows}
    if not values:
        return out
    with localcontext() as context:
        context.prec = 50
        mean = sum(values) / len(values)
        lower = quantile(values, Decimal(".025"))
        upper = quantile(values, Decimal(".975"))
        out.update({
            "averaging_scope": ("all scheduled runs" if len(complete) == scheduled
                                else "completed runs only, censored descriptive subset"),
            "mean": str(mean),
            "minimum": str(values[0]),
            "maximum": str(values[-1]),
            "central95_empirical": [str(lower), str(upper)],
            "central95_ratio": str(upper / lower) if lower else None,
            "largest_replicate_share": str(values[-1] / sum(values)) if values[-1] else None,
            "zero_draws": sum(value == 0 for value in values),
            "exact_runs_no_merges": sum(row["result"]["result"]["merges"] == 0 for row in complete),
        })
        if len(values) > 1:
            out["standard_deviation"] = str((sum((value - mean) ** 2 for value in values) / (len(values) - 1)).sqrt())
    return out


def report():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("scheduled", type=int, help="number of draws prescheduled per stage")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root / "scripts"))
    from longrun import load_results

    per_stage = defaultdict(list)
    records = load_results(str(args.runs))
    for name, result in sorted(records.items()):
        per_stage[name.split(":", 1)[0]].append(result)
    if not per_stage:
        raise ValueError("runner wrote no result records")
    with args.output.open("x") as output:
        json.dump({stage: summarize(rows, args.scheduled) for stage, rows in per_stage.items()}, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    report()
