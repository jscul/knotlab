"""Compare every saved six-reading and deletion row to a different solver."""

import argparse
import hashlib
import json
import resource
import time
from functools import partial

import step_readings as readings


def canonical(row):
    return (json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n").encode()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", action="store_true")
    cli.add_argument("--backend", required=True)
    args = cli.parse_args()
    suffix = "_pilot" if args.pilot else ""
    start = time.perf_counter()
    readings.Solver = partial(readings.Solver, name=args.backend)
    official = readings.open_rows(readings.HERE / f"step_reading_rows{suffix}.jsonl.gz")
    before = hashlib.sha256()
    after = hashlib.sha256()
    size = 0
    for stage in readings.open_rows(readings.HERE / f"step_stages{suffix}.jsonl.gz"):
        checker = readings.StageCheck(stage["supports"])
        try:
            for i, chain in enumerate(stage["chains"]):
                row = checker.check(chain)
                row.update(stage=stage["id"], chain_index=i)
                current = canonical(next(official))
                previous = canonical(row)
                assert current == previous, (stage["id"], i)
                before.update(previous)
                after.update(current)
                size += 1
        finally:
            checker.close()
    assert next(official, None) is None
    result = {"rows_compared": size, "recomputed_sha256": before.hexdigest(), "stored_sha256": after.hexdigest(),
              "wall_seconds": time.perf_counter() - start, "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (readings.HERE / f"step_backend_comparison{suffix}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
