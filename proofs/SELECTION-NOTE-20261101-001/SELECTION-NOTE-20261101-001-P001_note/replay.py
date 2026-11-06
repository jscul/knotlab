"""Replay driver for the note 'Native selection on regular systems'.

Copies every proof the note cites, every proof directory they import from or bind by hash, and every research file they read or bind,
into a temporary directory with the same relative layout. Reruns each cited check there with --write, in dependency order, and compares
each fresh result.json with the frozen one, ignoring timing fields. After each comparison the frozen result.json is put back, so that
later checks, which bind earlier results by hash, see the frozen files. The repository is never written, except replay_result.json here
with --write.

Run with the Python that has the checks' packages (the workspace .venv):
    .venv/bin/python -B replay.py [--write]"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# (ticket, what the note uses it for), in dependency order
CITED = [
    ("KNOT-COUPLING-20261031-001A", "the atom and the dimer law (Section 2)"),
    ("KNOT-COUPLING-20261031-001B", "hardness away from the knot's law (Theorem 1)"),
    ("KNOT-COUPLING-20261031-001C", "the complex couplings (Theorem 1)"),
    ("PINNING-20261031-001A", "five classes, the pinning theorem (Theorems 2, 3)"),
    ("PINNING-20261031-001B", "x or (y != z) NP-complete, the 25-line failure (Section 3)"),
    ("PINNING-20261031-001C", "uniqueness, the 1,380,864 signings (Theorem 4)"),
    ("PARITY-CORRECTION-20261031-001A", "parity's family, the theta substitution (Theorem 5, the remark)"),
    ("PARITY-CORRECTION-20261031-001B", "parity's failing class (Theorem 6)"),
    ("FOUR-PLACE-20261031-001A", "the value-free four-place knots (Theorem 8)"),
    ("FOUR-PLACE-20261031-001B", "signed not-all-equal never fails for k >= 4 (Theorem 7)"),
    ("FOUR-PLACE-20261031-001C", "value-free links, 160 instances (Theorem 9)"),
    ("FOUR-PLACE-20261031-001D", "no value-free four-place selection (Section 5)"),
    ("FOUR-PREFER-20261101-001A", "742 knots in 20 classes, the clause (Theorem 8)"),
    ("FOUR-PREFER-20261101-001B", "value-preferring links, 240 instances (Theorem 9)"),
    ("FOUR-PREFER-20261101-001D", "four-place selection table (Corollary 10)"),
    ("KNOT-COMPOSE-20261101-001A", "complementarity and hubs (Lemma 11, Theorem 12)"),
]
IGNORED_KEYS = {"seconds"}
TICKET = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{8}-\d{3}[A-Z]?")
RESEARCH = re.compile(r"research/[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+\.(?:json|md|py)")


def proof_dir(ticket):
    hits = sorted((ROOT / "proofs" / ticket).glob(f"{ticket}-P001_*"))
    assert len(hits) == 1, (ticket, hits)
    return hits[0]


def needed():
    """cited proof directories, every proof directory named in their files or bindings, and every research file they read or bind"""
    dirs, files = set(t for t, _ in CITED), set()
    frontier = list(dirs)
    while frontier:
        t = frontier.pop()
        d = proof_dir(t)
        text = "".join(p.read_text(errors="ignore") for p in d.glob("*.py"))
        binds = json.loads((d / "manifest.json").read_text()).get("parent_bindings", {})
        text += " " + " ".join(binds)
        for u in TICKET.findall(text):
            if (ROOT / "proofs" / u).is_dir() and u not in dirs:
                dirs.add(u)
                frontier.append(u)
        files |= {f for f in RESEARCH.findall(text) if (ROOT / f).is_file()}
        files |= {f for f in binds if (ROOT / f).is_file()}              # every bound file, exactly
    return sorted(dirs), sorted(files)


def diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k in IGNORED_KEYS:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present in only one")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths {len(a)} and {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def main():
    t0 = time.time()
    rows = []
    dirs, files = needed()
    with tempfile.TemporaryDirectory(prefix="selection_note_replay_") as tmp:
        tmp = Path(tmp)
        for t in dirs:
            src = proof_dir(t)
            shutil.copytree(src, tmp / src.relative_to(ROOT), ignore=shutil.ignore_patterns("__pycache__"))
        for f in files:
            (tmp / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / f, tmp / f)
        for ticket, use in CITED:
            src = proof_dir(ticket)
            dst = tmp / src.relative_to(ROOT)
            t1 = time.time()
            run = subprocess.run([sys.executable, "-B", "check.py", "--write"], cwd=dst, capture_output=True, text=True, timeout=10800)
            fresh = json.loads((dst / "result.json").read_text()) if (dst / "result.json").exists() else None
            frozen = json.loads((src / "result.json").read_text())
            differences = diff(fresh, frozen) if fresh is not None else ["no fresh result.json"]
            shutil.copy(src / "result.json", dst / "result.json")         # later checks bind the frozen result by hash
            row = {"ticket": ticket, "used_for": use, "exit_code": run.returncode,
                   "last_line": (run.stdout.strip().splitlines() or [""])[-1],
                   "fresh_status": fresh.get("status") if fresh else None,
                   "matches_frozen_result": not differences, "differences": differences[:20],
                   "seconds": round(time.time() - t1, 1)}
            rows.append(row)
            flag = "ok " if run.returncode == 0 and not differences and row["fresh_status"] in ("passed", "Proved") else "BAD"
            print(f"{flag} {ticket:34s} {row['seconds']:8.1f} s  {row['last_line'][:80]}", flush=True)
            if run.returncode != 0:
                print(run.stderr[-2000:])
    ok = all(r["exit_code"] == 0 and r["matches_frozen_result"] and r["fresh_status"] in ("passed", "Proved") for r in rows)
    summary = {"schema_version": 1, "artifact_id": "SELECTION-NOTE-20261101-001-P001",
               "replay": "every cited check rerun in a temporary copy and compared with its frozen result, timing ignored",
               "copied_directories": dirs, "copied_research_files": files, "ok": ok, "seconds": round(time.time() - t0, 1), "rows": rows}
    if "--write" in sys.argv:
        (HERE / "replay_result.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print("ALL OK" if ok else "FAILURES", summary["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
