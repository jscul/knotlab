"""Replay driver for the note 'Counting homomorphisms from knot groups to solvable groups can be #P-hard'.

Copies every proof the note cites (and the libraries they import) into a temporary directory with the same
relative layout, reruns each check there with --write, and compares each fresh result.json with the frozen one,
ignoring timing fields. The frozen artifacts in the repository are never written.

Standard library only. Run from anywhere:  python3 -B replay.py [--write]
With --write, the summary is saved as replay_result.json next to this file.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# (ticket, what the note uses it for)
CITED = [
    ("BOUNDED-H1-20261025-001A", "bicycle law, Potts(12,1/2), knot gadgets; T(K) #P-hard"),
    ("BOUNDED-H1-20261025-001B", "abelian-by-nilpotent targets polynomial on knot groups"),
    ("CLOSED-H1-20261025-001B", "Livingston's equal counts, re-proved"),
    ("SL23-BOUNDED-20261025-001B", "H_K(S4) = 4 + R + 2T; double covers"),
    ("CORRECTIONS-20261026-001A", "count as a twisted triple-product kernel (F4)"),
    ("CORRECTIONS-20261026-001C", "Borromean steering (F4)"),
    ("CORRECTIONS-20261026-001D", "UT3(F4) x| C3 hardness; knot groups (+63)"),
    ("COPRIME-CLASS2-20261026-001B", "count, steering and pure leaves (odd p)"),
    ("COPRIME-CLASS2-20261026-001C", "no hard pair: polynomial"),
    ("COPRIME-CLASS2-20261026-001D", "hard pair: gadgets, construction, knot groups"),
]
# Imported read-only by the cited checks.
LIBRARIES = ["TRIPLE-PRODUCT-20261026-001A"]
IGNORED_KEYS = {"seconds"}


def proof_dir(ticket):
    hits = sorted((ROOT / "proofs" / ticket).glob(f"{ticket}-P001_*"))
    assert len(hits) == 1, (ticket, hits)
    return hits[0]


def diff(a, b, path=""):
    """List the paths where two JSON values differ, ignoring timing keys."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
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
    with tempfile.TemporaryDirectory(prefix="rowell_replay_") as tmp:
        tmp = Path(tmp)
        for ticket in [t for t, _ in CITED] + LIBRARIES:
            src = proof_dir(ticket)
            dst = tmp / src.relative_to(ROOT)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            if ticket not in LIBRARIES:
                (dst / "result.json").unlink()
        for ticket, use in CITED:
            src = proof_dir(ticket)
            dst = tmp / src.relative_to(ROOT)
            t1 = time.time()
            run = subprocess.run([sys.executable, "-B", "check.py", "--write"], cwd=dst,
                                 capture_output=True, text=True, timeout=3600)
            fresh_path = dst / "result.json"
            fresh = json.loads(fresh_path.read_text()) if fresh_path.exists() else None
            frozen = json.loads((src / "result.json").read_text())
            differences = diff(fresh, frozen) if fresh is not None else ["no fresh result.json"]
            row = {
                "ticket": ticket,
                "used_for": use,
                "exit_code": run.returncode,
                "last_line": (run.stdout.strip().splitlines() or [""])[-1],
                "fresh_status": fresh.get("status") if fresh else None,
                "matches_frozen_result": not differences,
                "differences": differences[:20],
                "seconds": round(time.time() - t1, 1),
            }
            if fresh is not None:
                row["fresh_checks"] = fresh.get("checks")
            rows.append(row)
            flag = "ok " if run.returncode == 0 and not differences and row["fresh_status"] == "Proved" else "BAD"
            print(f"{flag} {ticket:32s} {row['seconds']:7.1f} s  {row['last_line']}")
            if run.returncode != 0:
                print(run.stderr[-2000:])
    ok = all(r["exit_code"] == 0 and r["matches_frozen_result"] and r["fresh_status"] == "Proved" for r in rows)
    summary = {
        "schema_version": 1,
        "artifact_id": "ROWELL-NOTE-20261026-001-P001",
        "replay": "every cited check rerun in a temporary copy and compared with its frozen result",
        "ok": ok,
        "seconds": round(time.time() - t0, 1),
        "rows": rows,
    }
    if "--write" in sys.argv:
        (HERE / "replay_result.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print("ALL OK" if ok else "FAILURES", summary["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
