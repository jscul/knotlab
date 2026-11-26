"""Recheck every registered not-all-equal birth test from fresh complete rounds.

At a birth the inputs are old distinctions. Every new rule has at least one
fresh distinction of its own, so every old allowed state extends over all
other births of this round and over future rounds. All assignments to these
inputs extend exactly when forgetting one fresh distinction can leave the
rest free. In that case the local projection is the full not-all-equal
relation. Start knots use forgetting directly. Complementation halves each
enumeration of signs while preserving existence.
"""

import argparse
import gzip
import itertools
import json
import resource
import time
from collections import Counter
from pathlib import Path

from pysat.solvers import Solver

from end_recount import FAMILY, ROOT, TICKET, LAWS
from regrow_engine import Growth


def admit(solver, places):
    ids = [d+1 for d in places]
    solver.add_clause(ids)
    solver.add_clause([-v for v in ids])


def jointly_free(solver, places, counts):
    if not places:
        return solver.solve()
    fixed = places[0] + 1
    others = [(d+1, -d-1) for d in places[1:]]
    for choices in itertools.product(*others):
        counts["extension_queries"] += 1
        if not solver.solve(assumptions=(fixed, *choices)):
            return False
    return True


def start_verdicts(stars, totals):
    with Solver() as solver:
        for places in stars:
            admit(solver, places)
        assert solver.solve()
        return [all(jointly_free(solver, places[:i]+places[i+1:], totals)
                    for i in range(len(places))) for places in stars]


def check(run, stars, verdicts, totals):
    last = max((s["round"] for s in run["stages"] if s["status"] == "computed"), default=0)
    totals["catalogue_start_law_runs"] += 1
    totals["all_start_knot_occurrences"] += len(stars)
    if not last:
        assert "knot_test" not in run
        totals["runs_without_recorded_stage_test"] += 1
        totals["start_knots_without_recorded_stage_test"] += len(stars)
        return
    totals["runs_with_recorded_stage_test"] += 1
    growth = Growth(stars, run["law"])
    tests = list(verdicts)
    with Solver() as solver:
        for places in stars:
            admit(solver, places)
        for t in range(1, last+1):
            knots_before, distinctions_before = len(growth.places), len(growth.holders)
            assert growth.step() == run["births"][t-1]
            for places in growth.places[knots_before:]:
                old = [d for d in places if d < distinctions_before]
                assert len(old) < len(places)
                tests.append(jointly_free(solver, old, totals))
            for places in growth.places[knots_before:]:
                admit(solver, places)
    saved = run["knot_test"]
    failed = [k for k, ok in enumerate(tests) if not ok]
    direct = sum(len(places) <= 12 for places in growth.places)
    assert failed == [r["knot"] for r in saved["fails"]]
    assert len(tests) == saved["tested"] and direct == saved["direct_compared"]
    totals["start_knots_in_stage_test"] += len(stars)
    totals["births_in_stage_test"] += len(tests)-len(stars)
    totals["tested_once_per_knot_per_run"] += len(tests)
    totals["failures"] += len(failed)
    totals["direct_comparisons_in_original"] += direct
    totals["missing_original_direct_checks_above_12"] += len(tests)-direct


def main(limit):
    nodes = json.loads((ROOT/"research"/TICKET/"census_starts.json").read_text())
    first = Counter()
    initial = {}
    groups = {}
    for law in LAWS:
        tally = Counter()
        with gzip.open(FAMILY/f"run5_{law}.jsonl.gz","rt") as f:
            for raw in itertools.islice(f, limit):
                run = json.loads(raw)
                idx = run["index"]
                stars = nodes[idx]["stars"]
                if idx not in initial:
                    verdicts = start_verdicts(stars,first)
                    initial[idx] = verdicts
                    first["catalogue_starts"] += 1
                    first["knots_tested_once_per_start"] += len(verdicts)
                    first["failures"] += verdicts.count(False)
                check(run,stars,initial[idx],tally)
        groups[law] = tally
    return {"round_zero_ignoring_law": first, "through_last_computed_stage_by_law": groups}


if __name__ == "__main__":
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--limit", type=int)
    argp.add_argument("--output", required=True, type=Path)
    args = argp.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(2_300_000_000,2_300_000_000))
    tic = time.monotonic()
    result = main(args.limit)
    result.update(limit_per_law=args.limit, seconds=time.monotonic()-tic,
                  peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
