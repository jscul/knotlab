"""Check the freeze, the deviation record and the dated prior-work index."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.relative_to(ROOT)
FREEZE = "de892a09d6"
RESULT = "815b1964d7"
SEARCHES = (
    "witnessed neighborhoods inclusive descendants funded cuts fresh counts ancestry reach",
    "how many parent steps earliest change receiver guard implied closure shortage",
    "local round asynchronous parent records schedule admissions",
    "reduction maximal blocks start loose counts group three common holder",
    "local reader predicted births parents kinds census starts",
    "one step of the map a round parity preparations change",
)


def command(args, input_bytes=None):
    p = subprocess.run(args, cwd=ROOT, input=input_bytes, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def git(*args):
    status, out, err = command(["git", *map(str, args)])
    if status:
        raise RuntimeError(err.decode())
    return out


def tracker(*args, input_bytes=None):
    return command([str(ROOT / ".venv/bin/python"), "-B", "scripts/track.py", *args],
                   input_bytes=input_bytes)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def freeze_text(ref):
    return git("show", f"{ref}:{STUDY}/README.md")


def prior_gate(path, content=None):
    status, out, err = tracker("objects-gate", str(path), input_bytes=content)
    return {"status": status, "output": (out + err).decode().strip()}


def search(query):
    args = ["objects", query, "--until", "2026-11-26", "--exclude", STUDY.name,
            "--limit", "6", "--json"]
    status, data, err = tracker(*args)
    if status:
        raise RuntimeError(err.decode())
    rows = json.loads(data)
    return {"arguments": args, "index": [r["id"] for r in rows["index"]],
            "unindexed": [r["id"] for r in rows["other_epics"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (600 << 20, 600 << 20))
    start = time.monotonic()
    frozen = freeze_text(FREEZE)
    result_text = freeze_text(RESULT)
    freeze_manifest = git("ls-tree", "--name-only", "-r", FREEZE, STUDY).decode().splitlines()
    # Store only the relevant logic and data paths. File digests bind the original files.
    sources = ["README.md", "handtest.json", "handtest.py", "explore.py",
               "ondemand.py", "run.py", "score.py", "score.json",
               "results_census6.jsonl", "results_tree40.jsonl",
               "results_treeplus25.jsonl", "results_treeplus25_first_run.jsonl"]
    versions = {}
    for name in sources:
        path = STUDY / name
        versions[name] = {
            "freeze": digest(git("show", f"{FREEZE}:{path}")) if str(path) in freeze_manifest else None,
            "results": digest(git("show", f"{RESULT}:{path}")),
            "working": digest((ROOT / path).read_bytes()),
        }
    source_file = STUDY / "ondemand.py"
    def routines(commit):
        tree = ast.parse(git("show", f"{commit}:{source_file}").decode())
        return {node.name: ast.dump(node) for node in tree.body if isinstance(node, ast.FunctionDef)}
    a, b = routines(FREEZE), routines(RESULT)
    queries = SEARCHES[:1] if args.pilot else SEARCHES
    result = {
        "freeze": git("rev-parse", FREEZE).decode().strip(),
        "closure": git("rev-parse", RESULT).decode().strip(),
        "closure_starts_with_frozen_note": result_text.startswith(frozen.rstrip()),
        "results_note_extra_headings": [s for s in result_text[len(frozen.rstrip()):].decode().splitlines()
                                        if s.startswith(("**Deviation", "## What was found"))][:2],
        "readme_commits_freeze_through_results": git("log", "--format=%H", f"{FREEZE}^..{RESULT}",
                                                      "--", STUDY / "README.md").decode().splitlines(),
        "unchanged_roster_routines": sorted(k for k in a if a[k] == b.get(k)),
        "changed_roster_routines": sorted(k for k in a if a[k] != b.get(k)),
        "sha256": versions,
        "gate_exact_freeze_bytes": prior_gate("/dev/stdin", frozen),
        "gate_current_note": prior_gate(STUDY / "README.md"),
        "searches": [search(q) for q in queries],
        "elapsed_seconds": round(time.monotonic() - start, 4),
    }
    output = HERE / ("provenance_pilot.json" if args.pilot else "provenance.json")
    output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
