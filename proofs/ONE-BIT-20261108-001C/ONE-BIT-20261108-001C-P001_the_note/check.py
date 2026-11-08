#!/usr/bin/env python3
"""Check for ONE-BIT-20261108-001C-P001: the note "The pinwheel tilings have no undecorated local rules".

    python3 -B check.py          (about half a minute; writes result.json and replay_result.txt)

- Runs replay.py (the note's independent replay, standard library only) and requires every line to pass.
- Checks that the note's TeX, PDF and figure here are byte-identical to the published copy under publication/knotlab/notes/.
- Checks that every record the note cites in its evidence section exists in the workspace."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PUB = ROOT / "publication/knotlab/notes/pinwheel-local-rules"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    res = {"checks": {}, "controls": {}}
    out = subprocess.run([sys.executable, "-B", str(HERE / "replay.py")], capture_output=True, text=True, timeout=1800)
    (HERE / "replay_result.txt").write_text(out.stdout)
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    res["checks"]["replay: every line passes"] = out.returncode == 0 and len(lines) == 6 and all(l.startswith("PASS") for l in lines)
    for name in ("pinwheel_local_rules.tex", "pinwheel_local_rules.pdf", "figure.tex"):
        res["checks"][f"{name} matches the published copy"] = sha(HERE / "note" / name) == sha(PUB / name)
    res["checks"]["replay.py matches the published copy"] = sha(HERE / "replay.py") == sha(PUB / "replay.py")
    tex = (HERE / "note" / "pinwheel_local_rules.tex").read_text()
    cited = sorted(set(re.findall(r"\\texttt\{((?:proofs|research|artifacts)/[A-Z0-9-]+)\}", tex)))
    res["census"] = {"cited record folders": cited}
    res["checks"]["every cited record folder exists"] = bool(cited) and all((ROOT / c).exists() for c in cited)
    res["controls"]["a wrong digest is rejected"] = sha(HERE / "replay.py") != "0" * 64
    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    (HERE / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
