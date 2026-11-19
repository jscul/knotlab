"""Continue the fixed wide panel without recomputing or dropping completed seeds."""

from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from prefix_targets import HERE, ORDER_SEED, POPULATION, REPLICATES, WORK, digest, write_at


WIDE = "start-14-age08"


def complete_lines(path):
    return [json.loads(line) for line in path.read_bytes().splitlines(keepends=True) if line.endswith(b"\n")]


def run_range(binary, directory, output, seed, begin, end, workers):
    settings = json.loads((directory / "settings.json").read_text())
    inside = settings["ranker"]["largest_block"]
    args = [binary, directory / "quotient.txt", directory / "bank.txt", output,
            str(ORDER_SEED), str(seed), str(POPULATION), str(begin), str(end), str(workers), str(inside)]
    subprocess.run(args, check=True)


def prepare():
    engine = WORK / "engine" / "32"
    code = (engine / "anneal.cpp").read_text()
    signature = "int main(int argc, char** argv)"
    assert code.count(signature) == 1
    adapter = engine / "anneal_entry_adapter.cpp"
    adapter.write_text(code.replace(signature, "int archived_serial_panel_main(int argc, char** argv)"))
    wrapper = engine / "prefix_targets_parallel.cpp"
    wrapper.write_bytes((HERE / wrapper.name).read_bytes())
    binary = engine / "parallel"
    pending = binary.with_suffix(".pending")
    subprocess.run(["c++", "-O3", "-march=native", "-std=c++20", "-Wno-return-type", str(wrapper),
                    "-o", str(pending)], check=True)
    pending.replace(binary)
    case = WORK / "start-02-age09"
    header, *serial = complete_lines(case / "raw.jsonl")
    seed = serial[0]["seed"]
    with TemporaryDirectory(prefix="prespatial-parallel-check-") as scratch:
        output = Path(scratch)
        run_range(binary, case, output, seed, 4, 9, 3)
        assert all(complete_lines(output / f"seed-{seed+i}.jsonl") == [serial[i]] for i in range(4, 9))
    result = {"verified_actual_control": "start-02-age09", "identical_complete_rows": 5,
              "first_control_offset": 4, "serial_engine16_matches_shared_engine32": True,
              "wrapper_sha256": digest(wrapper), "serial_source_sha256": digest(engine / "anneal.cpp"),
              "binary_sha256": digest(binary),
              "intervention": "Original bank and fixed seeds. Share one immutable graph. Each child checks the exact two-block maximality condition on its unchanged bank slice at the stored byte offset."}
    write_at(WORK / "parallel_check.json", lambda f: json.dump(result, f, indent=2, sort_keys=True))
    return result


def freeze_remaining():
    directory = WORK / WIDE
    metadata = json.loads((directory / "settings.json").read_text())
    assert metadata["integer_id_width"] == 32 and metadata["population"] == POPULATION
    assert digest(directory / "bank.txt") == metadata["bank_sha256"]
    assert digest(directory / "quotient.txt") == metadata["quotient"]["roster_sha256"]
    header, *finished = complete_lines(directory / "raw.jsonl")
    base = metadata["seed"]
    assert [v["seed"] for v in finished] == list(range(base, base + len(finished)))
    check = json.loads((WORK / "parallel_check.json").read_text())
    assert check["identical_complete_rows"] == 5
    location = directory / "continuation.json"
    inherited = []
    if location.is_file():
        previous = json.loads(location.read_text())
        assert previous["metadata"] == metadata and previous["serial_observations"] == finished
        inherited = previous.get("earlier_parallel_batches", [])
        if previous["check"] != check:
            seen = {row["seed"] for batch in inherited for row in batch["accepted_receipts"]}
            accepted = []
            for seed in range(base + len(finished), base + REPLICATES):
                receipt = directory / "continuation" / f"seed-{seed}.jsonl"
                if seed not in seen and receipt.is_file():
                    assert [row["seed"] for row in complete_lines(receipt)] == [seed]
                    accepted.append({"seed": seed, "sha256": digest(receipt)})
            inherited.append({"check": previous["check"], "accepted_receipts": accepted})
    result = {"metadata": metadata, "header": header, "serial_observations": finished,
              "start_offset": len(finished), "submit_end_offset": REPLICATES, "parallel_processes": 4,
              "check": check, "serial_sha256": digest(directory / "raw.jsonl"),
              "earlier_parallel_batches": inherited}
    write_at(location, lambda f: json.dump(result, f, indent=2, sort_keys=True))
    return {"serial_retained": len(finished), "first_remaining_seed": base + len(finished),
            "last_remaining_seed": base + REPLICATES - 1,
            "parallel_already_retained": sum(len(batch["accepted_receipts"]) for batch in inherited)}


def cases():
    yield WIDE, WIDE


def run(case, payload):
    assert case == payload == WIDE
    directory = WORK / WIDE
    plan = json.loads((directory / "continuation.json").read_text())
    field = plan["metadata"]
    assert digest(directory / "raw.jsonl") == plan["serial_sha256"]
    assert digest(directory / "bank.txt") == field["bank_sha256"]
    assert digest(directory / "quotient.txt") == field["quotient"]["roster_sha256"]
    binary = WORK / "engine" / "32" / "parallel"
    assert digest(binary) == plan["check"]["binary_sha256"]
    seed = field["seed"]
    first, past = plan["start_offset"], plan["submit_end_offset"]
    output = directory / "continuation"
    missing = [i for i in range(first, past) if not (output / f"seed-{seed+i}.jsonl").is_file()]
    while missing:
        left, right = missing[0], missing[0] + 1
        while right in missing:
            right += 1
        run_range(binary, directory, output, seed, left, right, plan["parallel_processes"])
        missing = [i for i in missing if i >= right]
    observed = [complete_lines(output / f"seed-{seed+i}.jsonl")[0] for i in range(first, past)]
    assert [r["seed"] for r in observed] == list(range(seed + first, seed + past))
    return {"serial_retained": first, "parallel_completed": len(observed), "total": first + len(observed)}


def verify_retained():
    """Compare the complete rows from prior executables with the current reader."""
    directory = WORK / WIDE
    plan = json.loads((directory / "continuation.json").read_text())
    binary = WORK / "engine" / "32" / "parallel"
    assert digest(binary) == plan["check"]["binary_sha256"]
    assert digest(directory / "raw.jsonl") == plan["serial_sha256"]
    assert digest(directory / "bank.txt") == plan["metadata"]["bank_sha256"]
    expected = {row["seed"]: row for row in plan["serial_observations"]}
    for batch in plan["earlier_parallel_batches"]:
        for row in batch["accepted_receipts"]:
            seed = row["seed"]
            receipt = directory / "continuation" / f"seed-{seed}.jsonl"
            assert digest(receipt) == row["sha256"]
            expected[seed], = complete_lines(receipt)
    base = plan["metadata"]["seed"]
    with TemporaryDirectory(prefix="prespatial-retained-check-") as scratch:
        output = Path(scratch)
        run_range(binary, directory, output, base, min(expected) - base, max(expected) - base + 1,
                  plan["parallel_processes"])
        for seed, original in expected.items():
            assert complete_lines(output / f"seed-{seed}.jsonl") == [original]
    result = {"binary_sha256": digest(binary), "exactly_reproduced_retained_seeds": sorted(expected)}
    write_at(directory / "retained_replay.json", lambda f: json.dump(result, f, indent=2, sort_keys=True))
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    actions = {"prepare": prepare, "freeze-remaining": freeze_remaining, "verify-retained": verify_retained}
    parser.add_argument("action", choices=actions)
    args = parser.parse_args()
    print(json.dumps(actions[args.action](), sort_keys=True))


if __name__ == "__main__":
    main()
