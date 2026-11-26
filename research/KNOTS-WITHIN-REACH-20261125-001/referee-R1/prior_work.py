"""Run the frozen search gate and its seven actual queries, then search for the earlier family."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = HERE.parent.name
TICKET = ROOT / "research" / (EPIC + "A")
CLI = [sys.executable, "-B", "scripts/track.py"]
QUERIES = ["within reach", "growth of balls", "knots within r steps", "ball growth grown structure",
           "bond distance", "state distance loose distinctions", "arrival delay",
           "mutually sharing knots first knot fewest fresh distinctions", "down-closed sets chains offshoots"]


def run(*args):
    return subprocess.run(CLI + list(args), cwd=ROOT, text=True, capture_output=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    output = {}
    if not args.pilot:
        output["gate"] = run("objects-gate", str(TICKET / "preregistration.md")).strip()
    results = {}
    for words in QUERIES[:1] if args.pilot else QUERIES:
        records = json.loads(run("objects", words, "--until", "2026-11-25", "--exclude", EPIC, "--limit", "3", "--json"))
        results[words] = [r["id"] for r in records["index"]]
    output["top indexed matches"] = results
    record = (TICKET / "preregistration.md").read_text()
    prior = record.split("## Prior work in the program")[1].split("\n##")[0]
    output["literal queries in code spans"] = re.findall(r'track\.py objects "([^"]+)"', prior)
    contract = json.loads(next((ROOT/"experiments"/(EPIC+"A")).glob("*/contract.json")).read_text())
    hashes = {}
    for key, value in contract.items():
        if key.endswith("_sha256") and isinstance(value,str):
            path = contract.get(key[:-7])
            if isinstance(path,str) and (ROOT/path).is_file():
                hashes[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == value
    for path, digest in contract["data_files"].items():
        hashes[path] = hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
    output["matched contract hashes"] = hashes
    if not args.pilot:
        (HERE/"prior_work.json").write_text(json.dumps(output, indent=2)+"\n")


if __name__ == "__main__":
    main()
