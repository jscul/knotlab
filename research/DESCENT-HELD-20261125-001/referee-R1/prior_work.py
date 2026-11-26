"""Re-run the frozen searches and two independent searches against the current index."""
import argparse
import json
from pathlib import Path
import re
import resource
import shlex
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCOPE = HERE.parent.name
PR = Path("research") / (SCOPE + "A") / "preregistration.md"


def tracker(*arguments):
    return subprocess.run([sys.executable, "-B", "scripts/track.py", *arguments], cwd=ROOT,
                          capture_output=True, text=True, check=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1_400_000_000,1_400_000_000))
    t = perf_counter()
    frozen = [shlex.split(line) for line in re.findall(r'`python3 -B scripts/track.py objects ("[^\n]+?)`',
                                                       (ROOT / PR).read_text())]
    assert len(frozen) == 6
    independent = [[query, "--until", "2026-11-25", "--exclude", SCOPE] for query in (
        "restart parent places same structure parent direction stamp counted in threes",
        "fresh count inherits parent ration independent choice number of places offshoots")]
    results = []
    searches = frozen + independent
    for search in searches[:1] if args.pilot else searches:
        response = tracker("objects", *search, "--limit", "3", "--json")
        response.check_returncode()
        rows = json.loads(response.stdout)["index"]
        results.append({"query": search[0], "leading_indexed_objects": [r["id"] for r in rows]})
    if not args.pilot:
        gate = tracker("objects-gate", str(PR))
        output = {"gate_exit_code":gate.returncode, "gate_output":gate.stdout.splitlines(),
                  "frozen_searches":results[:6], "independent_searches":results[6:]}
        (HERE/"prior_counts.json").write_text(json.dumps(output, indent=2)+"\n")
    print("searches",len(results),"seconds",round(perf_counter()-t,3))

if __name__ == "__main__":
    main()
