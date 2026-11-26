"""Replay the renumberings and retest the unfinished knot-test job."""

import argparse
from collections import Counter
from itertools import product
import json
import random
import sys

from replication_counts import (
    ROOT, build_start, control_schedule, load_runs, read_controls, seed_maps,
)


def growth_engine():
    directory = next((ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B").glob(
        "*_link_through_a_made_knot"
    ))
    sys.path.insert(0, str(directory))
    import eng
    return eng


def grow(engine, job, start):
    take = "MET-SOLE" if job.take == "sole" else None
    law = engine.Law(ration=job.ration, treatment=job.treatment, take=take, knot_law=job.knot_law)
    return engine.Run(law, stars=start, rounds=9, knot_bound=3000)


def renumbered(start, first_count, rng):
    distinctions = sorted({d for places in start for d in places})
    replacements = distinctions[:]
    rng.shuffle(replacements)
    mapping = dict(zip(distinctions, replacements, strict=True))
    knots = []
    for index, places in enumerate(start):
        replacement = [mapping[d] for d in places]
        rng.shuffle(replacement)
        knots.append((replacement, index < first_count))
    rng.shuffle(knots)
    return [places for places, _ in knots], [1 if first else 2 for _, first in knots]


def reading(run, descent):
    own_rounds, wider_rounds, second_only = [], [], []
    for round_record in run.recs:
        own, wide = Counter(), Counter()
        n_second = 0
        for birth in round_record["births"]:
            inherited = 0
            for parent in birth["parents"]:
                inherited |= descent[parent]
            assert birth["id"] == len(descent) and inherited
            descent.append(inherited)
            if inherited == 2:
                n_second += 1
                continue
            kind = {"join": "j", "offshoot": "o"}[birth["kind"]]
            places = len(birth["inputs"]) + len(birth["fresh"])
            entry = (kind, len(birth["parents"]), places, len(birth["fresh"]), len(birth["takes"]))
            if inherited == 1:
                own[entry] += 1
            wide[(*entry, int(inherited == 1))] += 1
        own_rounds.append([[*entry, count] for entry, count in sorted(own.items())])
        wider_rounds.append([[*entry, count] for entry, count in sorted(wide.items())])
        second_only.append(n_second)
    return {"make": own_rounds, "wider": wider_rounds, "sec_only": second_only,
            "knots": run.S.n_knots, "rounds_read": run.rounds_read, "stop": run.stop}


def replay_renumbering(engine, first, forms, jobs, smoke):
    archive, _, _ = read_controls()
    mismatches = {}
    grouped = Counter()
    for variant, seed in enumerate((3, 4, 5)):
        rng = random.Random(seed)
        for index, job in enumerate(jobs):
            start = build_start(first[job.first], forms[job.family].get(job.second))
            renamed, descent = renumbered(start, len(first[job.first]["knots"]), rng)
            if smoke and index % 10:
                continue
            k = variant * len(jobs) + index
            record = archive[k]
            assert record["key"] == job.archive_key()
            result = reading(grow(engine, job, renamed), descent)
            differing = [field for field, value in result.items() if value != record[field]]
            if differing:
                mismatches[str(k)] = differing
            grouped[f"{job.knot_law}, {job.take}"] += 1
    return {"archive_replays_by_law": grouped, "differences": mismatches}


def clauses(places):
    for p in places:
        yield tuple(d + 1 for d in p)
        yield tuple(-d - 1 for d in p)


def assignments_up_to_complement(distinctions):
    """Each constraint is unchanged by flipping every distinction in the system."""
    assert distinctions
    for rest in product((False, True), repeat=len(distinctions) - 1):
        values = (True, *rest)
        assumptions = [d + 1 if value else -d - 1 for d, value in zip(distinctions, values, strict=True)]
        yield values, assumptions


def check_private_fresh(run):
    for before, after, round_record in zip(run.snaps[:-1], run.snaps[1:], run.recs, strict=True):
        assert before.places == after.places[:before.n_knots]
        for birth in round_record["births"]:
            assert all(after.holders[d] == [birth["id"]] for d in birth["fresh"])
            assert all(d < before.n_distinctions for d in birth["inputs"])


def check_not_all_equal(run, smoke):
    from pysat.solvers import Solver

    start = run.snaps[0].places
    checks = []
    with Solver(bootstrap_with=list(clauses(start))) as solver:
        for knot, places in enumerate(start):
            for values, assumptions in assignments_up_to_complement(places):
                assert solver.solve(assumptions=assumptions) == (not all(values)), (knot, values)
        for before, after, round_record in zip(run.snaps[:-1], run.snaps[1:], run.recs, strict=True):
            births = round_record["births"]
            assert all(birth["fresh"] for birth in births)
            covered = births[::10] if smoke else births
            distinct_inputs = {tuple(sorted(birth["inputs"])) for birth in covered}
            calls = 0
            for inputs in sorted(distinct_inputs):
                for _, assumptions in assignments_up_to_complement(inputs):
                    assert solver.solve(assumptions=assumptions), (after.round, assumptions)
                    calls += 1
            checks.append({"round": after.round, "births": len(births), "checked_births": len(covered),
                           "solver_calls": calls})
            for clause in clauses(after.places[before.n_knots:]):
                solver.add_clause(clause)
    return checks


def insert_row(echelon, row):
    """Insert a binary row by its largest index, or recognize a consequence."""
    while row:
        pivot = row.bit_length() - 1
        if pivot not in echelon:
            echelon[pivot] = row
            break
        row ^= echelon[pivot]


def mask(names):
    return sum(1 << d for d in names)


def known_remainder(row, remainder):
    reduced = 0
    while row:
        low = row & -row
        reduced ^= remainder[low.bit_length() - 1]
        row ^= low
    return reduced


def check_parity(run):
    start = run.snaps[0]
    echelon = {}
    for places in start.places:
        insert_row(echelon, mask(places))
    remainder = {}
    for d in range(start.n_distinctions):
        unit = 1 << d
        remainder[d] = known_remainder(echelon[d] ^ unit, remainder) if d in echelon else unit

    def projection_rank(places):
        projected = {}
        for d in places:
            insert_row(projected, remainder[d])
        return len(projected)

    for places in start.places:
        assert projection_rank(places) == len(places) - 1
    checks = []
    for round_record in run.recs:
        implied = 0
        for birth in round_record["births"]:
            inputs, fresh = birth["inputs"], birth["fresh"]
            assert inputs
            if fresh:
                assert projection_rank(inputs) == len(inputs), (round_record["round"], inputs)
                pivot = max(fresh)
                remainder.update({d: 1 << d for d in fresh if d != pivot})
                other_places = mask(inputs) | mask([d for d in fresh if d != pivot])
                remainder[pivot] = known_remainder(other_places, remainder)
            else:
                assert known_remainder(mask(inputs), remainder) == 0
                assert projection_rank(inputs) == len(inputs) - 1, (round_record["round"], inputs)
                implied += 1
        checks.append({"round": round_record["round"], "births": len(round_record["births"]),
                       "implied": implied})
    return checks


def retest_control(engine, first, forms, job, baseline, smoke):
    start = build_start(first[job.first], forms[job.family].get(job.second))
    run = grow(engine, job, start)
    first_count = len(first[job.first]["knots"])
    result = reading(run, [1] * first_count + [2] * (len(start) - first_count))
    assert all(result[field] == baseline[field] for field in result), job
    check_private_fresh(run)
    checks = check_not_all_equal(run, smoke) if job.knot_law == "nae" else check_parity(run)
    return {"job": job.archive_key(), "start_knot_relations_checked": len(start),
            "snapshot_knot_occurrences": sum(snapshot.n_knots for snapshot in run.snaps),
            "minimum_places": min(map(len, run.S.places)), "record_agrees": True, "rounds": checks}


def missing_controls(engine, first, forms, jobs, smoke):
    archive, _, _ = read_controls()
    missing = [(index, job) for index, job in enumerate(jobs, 900) if index not in archive and index != 941]
    if smoke:
        one_per_law = {}
        for index, job in missing:
            one_per_law.setdefault((job.knot_law, job.take), (index, job))
        missing = list(one_per_law.values())
    cases = {}
    for runset in ("R2", "R4"):
        archived_runs = load_runs(runset, forms)
        for index, job in missing:
            if job.runset == runset:
                cases[str(index)] = retest_control(engine, first, forms, job, archived_runs[job], smoke)
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", choices=("renumber", "unfinished", "omitted"))
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    engine = growth_engine()
    first, forms = seed_maps()
    renumber_jobs, knot_jobs = control_schedule(forms)
    if args.control == "renumber":
        result = replay_renumbering(engine, first, forms, renumber_jobs, args.smoke)
    elif args.control == "unfinished":
        job = knot_jobs[41]
        result = retest_control(engine, first, forms, job, load_runs("R2", forms)[job], args.smoke)
    else:
        result = missing_controls(engine, first, forms, knot_jobs, args.smoke)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
