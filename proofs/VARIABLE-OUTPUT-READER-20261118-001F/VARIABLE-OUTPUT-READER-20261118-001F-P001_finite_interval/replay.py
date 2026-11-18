"""Recompute the six finite triple decisions and check the recorded certificates."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory


FAMILY = Path(__file__).resolve().parent


def receipt(path):
    return json.loads(path.read_text())


def digest(path):
    value = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def replay(scratch, threads):
    reference = receipt(FAMILY / "comparisons.json")
    audit = receipt(FAMILY / "audit.json")
    for name, flags in (("population", []), ("compare", ["-pthread"]), ("histories", ["-fopenmp"])):
        run(["g++", "-std=c++20", "-O3", *flags, FAMILY / f"{name}.cpp", "-o", scratch / name], check=True)
    run([scratch / "population", "3", "26", scratch], check=True)
    run([scratch / "compare", "--self-test"], check=True)
    residuals = []
    for width in range(18, 27):
        raw = scratch / f"width{width}.txt"
        assert digest(raw) == audit["populations"][str(width)]["population_sha256"]
        if width >= 21:
            expected = reference["run_by_increasing_width"][str(width)]["replayed_summary"]
        else:
            expected = reference["controls"]["complete_older_widths"][str(width)]
        cases = scratch / f"cases{width}.jsonl"
        measured = run([scratch / "compare", raw, "--expected-width", str(width),
                        "--threads", str(threads), "--residuals", cases],
                       check=True, capture_output=True, text=True)
        got = json.loads(measured.stdout)
        assert got == {**expected, "input": str(raw), "threads": threads}, width
        if width >= 21:
            residuals.extend(json.loads(row) for row in cases.read_text().splitlines())
        print(f"Checked all {got['measured']:,} tables at width {width}.", flush=True)

    roster = scratch / "cases.jsonl"
    roster.write_text("".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
                              for item in sorted(residuals, key=lambda case: (case["width"], case["line"]))))
    assert roster.read_bytes() == (FAMILY / "residual_cases.jsonl").read_bytes()
    counts = run([scratch / "histories", *(scratch / f"width{w}.txt" for w in range(3, 27))],
                 env={**os.environ, "OMP_NUM_THREADS": str(threads)}, check=True, capture_output=True)
    run([sys.executable, "-B", FAMILY / "check_histories.py", "--compare", FAMILY / "histories.json"],
        input=counts.stdout, check=True)
    audit_run = run([sys.executable, "-B", FAMILY / "audit.py", "--replay", FAMILY / "audit.json",
                     "--population-dir", scratch, "--residuals", roster, "--grader", scratch / "compare"],
                    check=True, capture_output=True)
    assert audit_run.stdout == (FAMILY / "audit.json").read_bytes()
    print("All six widths, the older controls, the history balances and the independent marked checks agree.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int, choices=range(1, 9), default=4)
    options = parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with Python assertions enabled.")
    with TemporaryDirectory(prefix="prespatial-triple-interval-") as tmp:
        replay(Path(tmp), options.threads)
