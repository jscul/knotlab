"""Repeat the frozen index gates and check the nearest earlier objects."""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = "MADE-COPIER-20261125-001"
COMMAND = [str(ROOT / ".venv/bin/python"), "-B", "scripts/track.py"]
QUERIES = [
    "made pattern meeting another second form leaves two of what it meets copying pattern",
    "first part course differs with what second part is through the meeting taking shared distinction",
    "two descendant parts same form both parents alone leaves two of itself copy census",
]
def query(subject, extra):
    args = ["objects", subject, "--until", "2026-11-25", "--exclude", EPIC, "--json", *extra]
    output = subprocess.check_output(COMMAND + args,cwd=ROOT)
    return [{"id":r["id"],"object":r["object"],"outcome":r["outcome"]} for r in json.loads(output)["index"]]

if __name__ == "__main__":
    t = time.monotonic()
    if "--pilot" in sys.argv:
        print(len(query(QUERIES[0],["--limit","1"])),round(time.monotonic()-t,3),"seconds")
    else:
        gates = {}
        for ticket in ("C","A","B"):
            registration = "research/" + EPIC + ticket + "/preregistration.md"
            cmd = subprocess.run(COMMAND+["objects-gate",registration],cwd=ROOT, text=True, capture_output=True)
            gates[ticket] = {"return_code":cmd.returncode,"message":(cmd.stdout+cmd.stderr).strip()}
        results = {"gates":gates,"searches":{q:query(q,["--limit","7"]) for q in QUERIES}}
        (HERE / "prior_work.json").write_text(json.dumps(results,indent=2)+"\n")
        print(gates)
