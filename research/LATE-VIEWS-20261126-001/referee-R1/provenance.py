"""Check the recorded freeze, scoring inputs and prior-work searches without running the study."""
import argparse
import ast
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
S = STUDY.relative_to(ROOT)
FREEZE = "f97fd78ae5"
RESULT = "3ceb22a8ec"
HANDOFF = "28e85b7dea"
QUERIES = (
    "local reader birth types parents fresh distinctions views settling round",
    "clusters relays groups of three every round cheapest growth unrolled map",
    "down-closure maximal blocks hub realization live neighbours",
    "polynomial count finite core endless chains clusters rays",
    "growth outside proved class filled map first round groups sharing",
)


def run(args, check=True):
    return subprocess.run(args, cwd=ROOT, capture_output=True, check=check)


def git(*args):
    return run(["git", *map(str, args)]).stdout


def digest(data):
    return hashlib.sha256(data).hexdigest()


def gates():
    tracker = [sys.executable, "-B", "scripts/track.py", "objects-gate"]
    # Pass the actual frozen note as a file descriptor, without copying it to disk.
    fd = os.memfd_create("frozen-note")
    try:
        os.write(fd, git("show", f"{FREEZE}:{S}/README.md"))
        os.lseek(fd, 0, os.SEEK_SET)
        frozen = subprocess.run([*tracker, f"/proc/self/fd/{fd}"], cwd=ROOT,
                                pass_fds=(fd,), capture_output=True)
    finally:
        os.close(fd)
    current = run([*tracker, str(S / "README.md")], check=False)
    return {label: {"exit": p.returncode, "message": (p.stdout + p.stderr).decode().strip()}
            for label, p in [("at_freeze", frozen), ("as_published", current)]}


def search(query):
    result = json.loads(run([sys.executable, "-B", "scripts/track.py", "objects", query,
                             "--until", "2026-11-26", "--exclude", STUDY.name, "--json"]).stdout)
    return {"query": query, "top_index_rows": [
        {"id": r["id"], "record": r["record"]} for r in result["index"][:5]]}


def audit(limit):
    note = git("show", f"{FREEZE}:{S}/README.md")
    stated = re.search(rb'`([a-f0-9]{64})`', note)[1].decode()
    hashes = {}
    filename = "predictions.jsonl.gz"
    for rev in [FREEZE, RESULT, HANDOFF, "working copy"]:
        data = ((STUDY / filename).read_bytes() if rev == "working copy"
                else git("show", f"{rev}:{S}/{filename}"))
        with gzip.open(io.BytesIO(data), "rb") as f:
            h = hashlib.sha256()
            n = 0
            for _ in range(limit or sys.maxsize):
                line = f.readline()
                if not line:
                    break
                h.update(line)
                n += 1
        hashes[rev] = {"compressed_sha256": digest(data), "uncompressed_sha256": h.hexdigest(),
                       "lines_read": n}
        if not limit:
            assert h.hexdigest() == stated
    orig = git("ls-tree", "-r", "--name-only", FREEZE, S).decode().splitlines()
    changed = git("diff", "--name-status", FREEZE, RESULT, "--", S).decode().splitlines()
    frozen_script = ast.parse(git("show", f"{FREEZE}:{S}/late.py"))
    current_script = ast.parse(git("show", f"{RESULT}:{S}/late.py"))
    pred_function = next(n for n in current_script.body if isinstance(n, ast.FunctionDef) and n.name == "predict")
    # Substitute the default value explicitly, then compare parsed executable code.
    class FrozenBranch(ast.NodeTransformer):
        def visit_IfExp(self, node):
            if isinstance(node.test, ast.Name) and node.test.id == "general":
                assert isinstance(node.body, ast.Name) and node.body.id == "GeneralPiece"
                assert isinstance(node.orelse, ast.Name) and node.orelse.id == "Piece"
                return node.orelse
            return self.generic_visit(node)

    FrozenBranch().visit(pred_function)
    pred_function.args.args.pop()
    pred_function.args.defaults.pop()
    current_script.body[:] = [n for n in current_script.body if getattr(n, "name", None) != "GeneralPiece"]
    assert ast.dump(frozen_script) == ast.dump(current_script)
    inputs = ["LOOK-ALIKE-20261126-001/alike.py", "LOOK-ALIKE-20261126-001/phase2.py",
              "SETTLE-BOUND-20261126-001/bound.py"]
    upstream = [str(Path("research") / name) for name in inputs]
    upstream.extend(str(p.relative_to(ROOT)) for pattern in [
        "experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/*/eng.py",
        "experiments/COPYING-PARTS-20261123-001A/*/cpcensus.py",
        "experiments/WEIGHTINGS-20261119-001B/*/weightlib.py",
        "proofs/DOUBLE-IDENT-20261119-001A/*/machine_check.py"] for p in ROOT.glob(pattern))
    return {"stated_uncompressed_sha256": stated, "digests": hashes, "freeze_files": orig,
            "freeze_to_result_changes": changed,
            "default_prediction_code_identical_after_removing_optional_revision": True,
            "frozen_note_is_prefix_of_result_note": git("show", f"{RESULT}:{S}/README.md").startswith(note),
            "upstream_files": upstream, "upstream_diff": git("diff", "--name-only", FREEZE, RESULT, "--", *upstream).decode().splitlines(),
            "scorer_joins": ["set", "knot law", "index"],
            "gates": gates(), "object_index": [search(q) for q in QUERIES[:1 if limit else None]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    t = time.monotonic()
    result = audit(32 if args.pilot else None)
    result["elapsed_seconds"] = round(time.monotonic() - t, 3)
    name = "provenance_pilot.json" if args.pilot else "provenance.json"
    (HERE / name).write_text(json.dumps(result, indent=2) + "\n")
    print(name, result["elapsed_seconds"], result["gates"])
