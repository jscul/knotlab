"""Replay this proof family's numerical evidence from the shared repository root."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKS = (
    ("check_reader.py", "reader_checks.json"),
    ("check_horizon.py", "horizon.json"),
    ("check_binary.py", "binary_exception.json"),
    ("check_advisor.py", "advisor_blocks.json"),
    ("prefix_check.py", "prefix_check.json"),
    ("cross_search.py", "cross_results.json"),
)


def compare(command, receipt):
    actual = subprocess.check_output(command, cwd=ROOT, text=True)
    expected = json.loads((HERE / receipt).read_text())
    if json.loads(actual) != expected:
        raise AssertionError(f"Replay differs from {receipt}")
    return receipt


def replay_check(pair):
    script, receipt = pair
    return compare([sys.executable, "-B", str(HERE / script)], receipt)


def main():
    with tempfile.TemporaryDirectory(prefix="large-parity-joins-") as temporary:
        executable = Path(temporary) / "orbit_search"
        subprocess.run(["c++", "-std=c++20", "-O3", "-march=native", "-pthread",
                        str(HERE / "orbit_search.cpp"), "-o", str(executable)], cwd=ROOT, check=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            jobs = [pool.submit(replay_check, pair) for pair in CHECKS]
            jobs.append(pool.submit(compare, [str(executable)], "orbit_search.json"))
            for job in jobs:
                print(f"Reproduced {job.result()}", flush=True)


if __name__ == "__main__":
    main()
