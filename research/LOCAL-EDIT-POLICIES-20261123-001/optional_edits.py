"""Check ordinary funding on the frozen starts with zero, one or two local additions.

Run with the workspace .venv.  The stored 2026-11-20 starts and their premarked
holders are inputs.  None of the previously scored four settings is a lookup
for the new nine-setting replay.
"""
from collections import Counter
import gzip
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = "WHOLE-STAGE-SETTINGS-20261120-001B"
EDITS = ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_ordinary_edits")
ARCHIVE = ROOT / "artifacts" / PREVIOUS / EDITS.name / "exact_tables.json.gz"

sys.path.insert(0, str(EDITS))
spec = importlib.util.spec_from_file_location("registered_ordinary_replay", EDITS / "run.py")
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)


def replay(start):
    supports = tuple(tuple(row) for row in start["base"])
    readers, marks = start["readers"], start["marks"]
    floor = max(d for row in supports for d in row) + 1
    extras = ((floor, floor + 1), (floor + 2, floor + 3))
    rosters = set()
    response = {}
    for law in ("parity", "nae"):
        cells = {}
        for k, ell in product(range(3), repeat=2):
            changed = list(supports)
            for index, n in enumerate((k, ell)):
                holder = readers[index]
                changed[holder] += extras[index][:n]
            final, receipt = engine.proposal_receipt(tuple(changed), law, floor + 4,
                                                     engine.source.canonical, engine.compact)
            groups = tuple(sorted(tuple(g) for g in receipt["groups"]))
            rosters.add(groups)
            demand = Counter(h for g in groups for h in g)
            fresh = engine.private_marks(changed)
            funded = receipt["status"] == "extend"
            assert funded == all(demand[h] <= len(names) for h, names in fresh.items())
            # If funded every loose mark is consumed either by a group or a unary birth.
            holders = engine.holders(final)
            assert all((len(holders[mark]) == 2) == funded for mark in marks)
            cells[k, ell] = int(funded)
        assert all(cells[k, ell] <= cells[j, m]
                   for (k, ell), (j, m) in product(cells, repeat=2) if k <= j and ell <= m)
        response[law] = [cells[k, ell] for k, ell in product(range(3), repeat=2)]
    assert len(rosters) == 1 and response["parity"] == response["nae"]
    return dict(name=start["name"], group=start.get("group", "dedicated"), funded=response["parity"])


def compute():
    with gzip.open(ARCHIVE, "rt") as handle:
        old = json.load(handle)
    controls = [replay(row) for row in old["built"] if row["name"] in ("S_cycle_five", "S_no_written_meeting")]
    sampled = [replay(row) for row in old["robustness"] if row.get("readers")]
    groups = Counter(row["group"] for row in old["robustness"])
    return dict(choices=[list(p) for p in product(range(3), repeat=2)], laws=["parity", "nae"],
                population=dict(groups), dedicated=controls, panel=sampled)


if __name__ == "__main__":
    result = compute()
    target = HERE / "optional_edits.json"
    if sys.argv[1:] == ["--write"]:
        target.write_text(json.dumps(result, indent=2) + "\n")
    else:
        assert json.loads(target.read_text()) == result
    print("Eligible:", len(result["panel"]), "of", sum(result["population"].values()))
    print("Funded in the panel, per law:", sum(sum(r["funded"]) for r in result["panel"]))
    print("Two separately built shortage controls:", [r["funded"] for r in result["dedicated"]])
