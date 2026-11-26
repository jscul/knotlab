"""Check which class observations are available at holdings passing the knot test."""
import argparse
from collections import Counter
import json
import os
import subprocess
import sys
import time

from census_check import ROOT, archived, basis, grow, input_rows, mask, naelib
from ring_check import minimum_changes

sys.path.insert(0, str(ROOT / "tools"))
from knotlab.knots import check_knot
from knotlab.relations import Relation


def analyse(rows, class_count):
    moves, allowed, _ = minimum_changes(rows)
    assert 1 << (len(allowed) - len(basis(moves))) == class_count
    outcomes = []
    for row in rows:
        support = mask(row)
        projection = basis(word & support for word in allowed)
        local = len(projection) - len(basis(word & support for word in moves))
        passed = len(projection) == len(row) - 1
        outcomes.append((passed, local))
        if local and not passed:
            # Check the actual joint states under the repository's forgetting rule.
            names = [f"d{n}" for n in row]
            words = [0]
            for v in projection:
                words.extend([w ^ v for w in words])
            observed = frozenset(tuple((w >> d) & 1 for d in row) for w in words)
            result = check_knot(Relation(tuple(names), observed), names[:-1], names[-1])
            assert not result.is_knot and not result.loss_on_erasure
    return {"all_pass": all(p for p, _ in outcomes), "best": max(b for _, b in outcomes),
            "best_passing": max((b for p, b in outcomes if p), default=0)}


def run(pilot):
    records = json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())
    archive = archived("census_canonical")
    result = {}
    for age in ["start", "after one round"]:
        stats, examples = Counter(), {}
        cases = [(i, r[age]["loose free"]["classes"]) for i, r in archive.items()
                 if isinstance(r[age], dict) and r[age]["loose free"]["classes"] > 1]
        for i, k in (cases[:12] if pilot else cases):
            rows = input_rows(records[i])
            if age != "start":
                rows, _ = grow(rows, "parity", "ordinary", naelib)
            obs = analyse(rows, k)
            key = str((k, obs["best"], obs["best_passing"], obs["all_pass"]))
            stats[key] += 1
            examples.setdefault(key, i)
        result[age] = {"counts": stats, "example_index": examples}
    return result


def check_witness(pilot):
    # Encode parity by forbidding every odd word, retaining all other holders
    # as witnesses. The visible places come from the physical census entry.
    records = json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())
    rows = input_rows(records[417])
    old = sorted(set().union(*rows))
    clauses = []
    for row in rows:
        for x in range(1 << len(row)):
            if x.bit_count() % 2:
                clauses.append(" ".join(("~" if (x >> j) & 1 else "") + f"d{d}" for j, d in enumerate(row)))
    result = []
    for k in ([1] if pilot else [1, 0]):
        names = [f"d{d}" for d in rows[k]]
        other = [f"d{d}" for d in old if d not in rows[k]]
        cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *names[:-1], "--contact", names[-1], "--witnesses", *other, "--json"]
        report = json.loads(subprocess.check_output(cmd, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}))
        result.append({"index": 417, "holder": k, "places": rows[k], "check": report})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--witness", action="store_true")
    options = parser.parse_args()
    if options.witness:
        print(json.dumps(check_witness(options.pilot)))
        sys.exit(0)
    tic = time.monotonic()
    rows = run(options.pilot)
    print(json.dumps({"key": ["classes", "best bits at any holder", "best bits at a passing holder",
                              "all holders pass"], "results": rows, "seconds": time.monotonic() - tic}))
