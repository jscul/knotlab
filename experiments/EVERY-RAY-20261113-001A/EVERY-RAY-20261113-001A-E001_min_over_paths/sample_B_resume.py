"""EVERY-RAY-20261113-001A, the thread's resume of stratum B after the crash at 25 of 100 (same frozen selection, Codex's runner,
one worker, with the patched timeout handler, into a fresh B_resume.jsonl since the runner keeps rows of one code version)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "codex"))
from pathlib import Path
import paths_dp as P
import run_paths as RP
out = Path(HERE) / "codex" / "sample"
sel = json.loads((out / "selection.json").read_text())
done = {json.loads(x)["key"] for x in open(out / "B.jsonl")}
rest = [k for k in sel["B"] if k not in done]
print(len(done), len(rest), flush=True)
RP.run_tasks(rest, out / "B_resume.jsonl", 1, census_records=P.load_census_records())
