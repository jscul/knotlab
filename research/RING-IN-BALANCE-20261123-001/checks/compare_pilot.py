"""The thread's part of ticket A's gate: ticket A's trace of run A1 against the pilot's two programs (pilot_traces.json,
made by pilot_traces.py).  Compared per round: members, parts, sorted usable loose counts, sorted sizes of the
inclusion-maximal met sets, births.  Run from the repository root with .venv/bin/python -B."""
import json, pathlib, re
here = pathlib.Path(__file__).parent
root = here.parents[2]
art = root / "artifacts/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring"
mine = json.loads((art / "a1_trace.json").read_text())["runs"]
pilot = json.loads((here / "pilot_traces.json").read_text())
name = {"ordinary": "ordinary", "two added rules": "two", "three added rules": "three", "two": "two", "three": "three"}
ok = bad = 0; notes = []
for key, run in sorted(mine.items()):
    n = int(re.search(r"Ring\((\d+)", run["start"]).group(1))
    law = next(v for k, v in name.items() if k in run["law_name"])
    p = pilot[f"ring({n},3)|{law}"]
    rows = [{"members": r["members"], "parts": r["parts"], "h": sorted(r["h"]), "met": sorted(r["metset_sizes"]), "births": r["births"]} for r in run["rows"]]
    for prog in ("roster.py", "own_check.py"):
        ref = [r for r in p[prog] if r and "members" in r]
        m = min(len(rows), len(ref))
        diff = [i for i in range(m) if rows[i] != ref[i]]
        tail = len(rows) != len(ref)
        if diff:
            bad += 1; notes.append(f"{run['start']} {law} vs {prog}: first difference at round {diff[0]}: engine {rows[diff[0]]['members']}/{rows[diff[0]]['parts']} births {rows[diff[0]]['births']}, pilot {ref[diff[0]]['members']}/{ref[diff[0]]['parts']} births {ref[diff[0]]['births']}")
        else:
            ok += 1
            if tail: notes.append(f"{run['start']} {law} vs {prog}: equal on the {m} rounds both have (engine {len(rows)}, pilot {len(ref)})")
print(f"{ok} comparisons equal on every common round, {bad} with a difference")
print("\n".join(notes))
