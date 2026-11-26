"""Recount the two parity archives and regrow selected records under both marks."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from time import process_time

from growth import Growth
from starts import SENDERS, build_pair, census_pairs


STUDY = Path(__file__).resolve().parents[2] / "TWO-RECEPTIONS-20261126-001"
ARCHIVES = {"stale": "parity_runs.jsonl.gz", "renewed": "parity2_runs.jsonl.gz"}
NO_TAKE = ("ORD", None, None)
CROSS_PART = ("ORD", "J-EACH-PART", None)
SETTINGS = (
    NO_TAKE, ("ORD", "MET", "OLDEST"), ("ORD", "MET", "NEWEST"), ("ORD", "MET-SOLE", None),
    ("ORD", "STEPS1-SOLE", None), ("ORD", "STEPS2-SOLE", None), CROSS_PART,
)
DIAGNOSTIC = ("n4:g17:0232@0", "g7:122@0", CROSS_PART)
EDIT_AFTER, ROUNDS, KNOT_BOUND = 3, 12, 1500
SEED = 2026112604


def read_archive(lines, mode):
    records, jobs = {}, {}
    expected_mark = "equations renewed" if mode == "renewed" else None
    for line in lines:
        row = json.loads(line)
        if "not run" in row:
            job = tuple(row["job"])
            if job in jobs:
                raise ValueError(f"Repeated {mode} job {job}")
            jobs[job] = row
            continue
        key = (row["A"], row["B"], tuple(row["law"]))
        if key in records:
            raise ValueError(f"Repeated {mode} record {key}")
        if row["knot law"] != "parity" or row.get("mark") != expected_mark:
            raise ValueError(f"Unexpected law or mark in {mode} {key}")
        records[key] = row
    return records, jobs


def load(mode):
    with gzip.open(STUDY / ARCHIVES[mode], "rt", encoding="utf-8") as f:
        return read_archive(f, mode)


def placements(case):
    """Identify archived placements by their metadata and occurrence within that metadata."""
    out = {}
    occurrences = Counter()
    for row in case["changes"]:
        linked, sharings = signature = (row["linked"], row["sharings"])
        occurrences[signature] += 1
        endpoint, hearing = row["rounds"], row["heard"]
        if not EDIT_AFTER <= endpoint <= case["rounds"] or (
            hearing is not None and not EDIT_AFTER < hearing <= endpoint
        ):
            raise ValueError(f"Inconsistent placement endpoint or hearing {row!r}")
        out[linked, sharings, occurrences[signature]] = row
    counts = Counter(row["linked"] for row in case["changes"])
    if counts[True] > 5 or counts[False] > 2:
        raise ValueError(f"Placement count exceeds the selection limit in {case!r}")
    return out


def compare_records(key, stale, renewed):
    for field in ("rounds", "ended", "made short", "linked"):
        if stale[field] != renewed[field]:
            raise ValueError(f"Unchanged growth {field!r} differs at {key!r}")
    old, new = placements(stale), placements(renewed)
    if tuple(old) != tuple(new):
        raise ValueError(f"Placement sequence differs at {key!r}")
    for signature, row in old.items():
        if row["rounds"] != new[signature]["rounds"]:
            raise ValueError(f"Common endpoint differs at {key!r} placement {signature!r}")
    return [(signature, row, new[signature]) for signature, row in old.items()]


def coverage(records):
    changes = [row for record in records.values() for row in placements(record).values()]
    positives = [(key, row) for key, record in records.items() for row in record["changes"]
                 if row["heard"] is not None]
    by_setting = Counter()
    for key, record in records.items():
        by_setting[" ".join(v for v in key[2] if v)] += len(record["changes"])
    return {
        "records": len(records),
        "pairs": len({key[:2] for key in records}),
        "records with placements": sum(bool(record["changes"]) for record in records.values()),
        "records with a hearing": len({key for key, _ in positives}),
        "placements": len(changes),
        "placements by setting": dict(sorted(by_setting.items())),
        "linked placements": sum(row["linked"] for row in changes),
        "unlinked placements": sum(not row["linked"] for row in changes),
        "reached round 7": sum(row["rounds"] >= 7 for row in changes),
        "stopped before round 7": sum(row["rounds"] < 7 for row in changes),
        "endpoints": dict(sorted(Counter(row["rounds"] for row in changes).items())),
        "first hearings by round": dict(sorted(Counter(row["heard"] for _, row in positives).items())),
        "first hearings by setting": dict(Counter(" ".join(v for v in key[2] if v) for key, _ in positives)),
        "unlinked first hearings": sum(not row["linked"] for _, row in positives),
    }


def stopped_job_coverage(planned, records, jobs):
    records_per_receiver = len(SETTINGS) * len(SENDERS)
    missing = set()
    for (first, stop), job in jobs.items():
        batch = planned[first * records_per_receiver:stop * records_per_receiver]
        done = tuple(key for key in batch if key in records)
        read = job["lines read"]
        if not 0 <= read < len(batch) or done != batch[:read]:
            raise ValueError(f"Stopped job {(first, stop)} does not have the reported prefix")
        missing.update(batch[read:])
    return {
        "stops by reported result": dict(Counter(row["not run"] for row in jobs.values())),
        "missing records in stopped jobs": len(missing),
        "missing records outside stopped jobs": len(set(planned) - records.keys() - missing),
    }


def recount(stale, renewed, stale_jobs, renewed_jobs):
    ordered = tuple((*pair, setting) for pair in census_pairs(include_controls=False) for setting in SETTINGS)
    planned = set(ordered)
    old_keys, new_keys = set(stale), set(renewed)
    if (old_keys | new_keys) - planned:
        raise ValueError("Archive contains pair and setting keys outside the planned frame")
    common = old_keys & new_keys
    differences = []
    compared = 0
    for key in sorted(common, key=repr):
        changes = compare_records(key, stale[key], renewed[key])
        compared += len(changes)
        for placement, old, new in changes:
            if old["heard"] != new["heard"]:
                differences.append([key, placement, old["heard"], new["heard"]])
    within = lambda records, keys: coverage({key: records[key] for key in keys})
    return {
        "planned records": len(planned),
        "stale archive": coverage(stale),
        "renewed archive": coverage(renewed),
        "stale missing records": len(planned - old_keys),
        "renewed missing records": len(planned - new_keys),
        "missing from both": len(planned - (old_keys | new_keys)),
        "stale stopped jobs": stopped_job_coverage(ordered, stale, stale_jobs),
        "renewed stopped jobs": stopped_job_coverage(ordered, renewed, renewed_jobs),
        "stale only": within(stale, old_keys - new_keys),
        "renewed only": within(renewed, new_keys - old_keys),
        "common": within(renewed, common),
        "comparisons": compared,
        "different first hearings": differences,
        "placement identity in archives": "Metadata and occurrence in stored order. Knot identities are absent.",
    }


def equation(holdings):
    return sum(1 << d for d in holdings)


def low_pivot_basis(vectors):
    """Use least-distinction pivots to check the equation stores independently."""
    basis = {}
    for vector in vectors:
        while vector:
            pivot = vector & -vector
            if pivot not in basis:
                basis[pivot] = vector
                break
            vector ^= basis[pivot]
    return basis


def in_span(vector, basis):
    while vector:
        pivot = vector & -vector
        if pivot not in basis:
            return False
        vector ^= basis[pivot]
    return True


def mark_check(before, stale, renewed, knot):
    loose = next(d for d in before.places[knot] if before.holders[d] == (knot,))
    fresh = len(before.holders)
    assert stale.places == renewed.places and stale.holders == renewed.holders
    assert renewed.holders[loose] == renewed.holders[fresh] == (knot,)
    old_row, new_row = equation(before.places[knot]), equation(renewed.places[knot])
    assert old_row ^ new_row == 1 << fresh

    projections = {}
    for mode, state in (("stale", stale), ("renewed", renewed)):
        vectors = state.parity_basis.values()
        basis = low_pivot_basis(vectors)
        projected = {f"{(vector >> loose) & 1}{(vector >> fresh) & 1}" for vector in vectors} | {"00"}
        assert projected == ({"00", "10"} if mode == "stale" else {"00", "11"})
        expected = before.places if mode == "stale" else state.places
        actual_basis = low_pivot_basis(map(equation, expected))
        assert len(basis) == len(actual_basis)
        assert all(in_span(vector, basis) for vector in actual_basis.values())
        projections[mode] = sorted(projected)
        assert (in_span(old_row, basis), in_span(new_row, basis)) == (mode == "stale", mode == "renewed")
    return {"old loose distinction": loose, "new loose distinction": fresh, "equation projections": projections}


def observations(baseline, changed, mark, linked):
    endpoint = min(len(baseline.rounds), len(changed.rounds))
    differences = [i + 1 for i in range(EDIT_AFTER, endpoint)
                   if baseline.rounds[i].receiver_signature != changed.rounds[i].receiver_signature]
    return {"linked": linked, "sharings": mark.sharings,
            "heard": differences[0] if differences else None, "rounds": endpoint}, differences


def first_funding_discrepancy(baseline, stale, renewed):
    for i in range(EDIT_AFTER, min(len(stale.rounds), len(renewed.rounds))):
        old, new = stale.rounds[i].births, renewed.rounds[i].births
        if old == new:
            continue
        if tuple((b.descent, b.kind, b.parents, b.p, b.D) for b in old) != tuple(
            (b.descent, b.kind, b.parents, b.p, b.D) for b in new
        ):
            raise ValueError(f"First discrepancy in round {i + 1} did not preserve the proposed births")
        details = []
        for a, b in zip(old, new, strict=True):
            if a.f == b.f:
                continue
            inputs = stale._snapshots[i + 1].places[a.knot][:a.p]
            assert inputs == renewed._snapshots[i + 1].places[b.knot][:b.p]
            stale_basis = low_pivot_basis(stale._snapshots[i].parity_basis.values())
            current_basis = low_pivot_basis(map(equation, renewed._snapshots[i].places))
            memberships = [in_span(equation(inputs), basis) for basis in (stale_basis, current_basis)]
            assert memberships == [a.f == 0, b.f == 0]
            base = next((k for k in baseline.rounds[i].births if k.descent == a.descent), None)
            details.append({"kind": a.kind, "knot": a.knot, "owner": a.owner, "demand": a.D,
                            "implied under stale and actual equations": memberships,
                            "fresh under stale and renewed": [a.f, b.f],
                            "places under baseline, stale, renewed": [
                                None if base is None else base.p + base.f, a.p + a.f, b.p + b.f]})
        return {"round": i + 1, "births": details}
    return None


def replay(key, old_archive, new_archive):
    started = process_time()
    receiver, far, setting = key
    if setting not in (NO_TAKE, CROSS_PART):
        raise ValueError(f"Unsupported replay setting {setting}")
    baseline = Growth(*build_pair(receiver, far), law="ORD", knot_law="parity", take=setting[1])
    baseline.run(ROUNDS, KNOT_BOUND)
    rebuilt = {"rounds": len(baseline.rounds), "ended": baseline.stop,
               "made short": [r.made_short for r in baseline.rounds],
               "linked": [baseline.linked(t) for t in range(1, len(baseline.rounds) + 1)]}
    slots = []
    if len(baseline.rounds) > EDIT_AFTER and baseline.linked(EDIT_AFTER) is not None:
        slots = [(linked, mark) for linked, limit in ((True, 5), (False, 2))
                 for mark in baseline.mark_candidates(EDIT_AFTER, linked)[:limit]]

    details = []
    readings = {"stale": [], "renewed": []}
    for linked, mark in slots:
        stale = baseline.fork(EDIT_AFTER).mark(mark.knot, renew=False)
        renewed = baseline.fork(EDIT_AFTER).mark(mark.knot, renew=True)
        check = mark_check(baseline._snapshots[EDIT_AFTER], stale._snapshots[-1], renewed._snapshots[-1], mark.knot)
        stale.run(ROUNDS, KNOT_BOUND)
        renewed.run(ROUNDS, KNOT_BOUND)
        record = {"knot": mark.knot, "descent": mark.descent, "mark check": check}
        for mode, growth in (("stale", stale), ("renewed", renewed)):
            observation, differences = observations(baseline, growth, mark, linked)
            readings[mode].append(observation)
            record[mode] = {**observation, "own differences": differences, "changed stop": growth.stop,
                            "changed endpoint": len(growth.rounds)}
        record["first funding discrepancy"] = first_funding_discrepancy(baseline, stale, renewed)
        details.append(record)

    differences = {}
    for mode, archived in (("stale", old_archive), ("renewed", new_archive)):
        observed = {**rebuilt, "changes": readings[mode]}
        differences[mode] = {field: {"replay": value, "archive": archived[field]}
                             for field, value in observed.items() if archived[field] != value}
    return {"key": key, "baseline": rebuilt, "placements": details, "archive differences": differences,
            "CPU seconds": round(process_time() - started, 4), "peak KiB": getrusage(RUSAGE_SELF).ru_maxrss}


def select(stale, renewed):
    common = sorted(set(stale) & set(renewed), key=repr)
    groups = {
        "no-take": [key for key in common if key[2] == NO_TAKE and stale[key]["changes"]
                    and all(row["heard"] is None for row in stale[key]["changes"])],
        "round-four": [key for key in common if key[2] == CROSS_PART
                       and any(row["heard"] == 4 for row in stale[key]["changes"])],
        "round-five": [key for key in common if key[2] == CROSS_PART and key != DIAGNOSTIC
                       and any(row["heard"] == 5 for row in stale[key]["changes"])],
    }
    rng = Random(SEED)
    sizes = {"no-take": 4, "round-four": 2, "round-five": 2}
    return {group: (len(keys), rng.sample(keys, sizes[group])) for group, keys in groups.items()}


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("mode", choices=("archive", "no-take", "round-four", "round-five", "diagnostic", "sample"))
    arg.add_argument("--limit", type=int)
    opts = arg.parse_args()
    stale, stale_jobs = load("stale")
    renewed, renewed_jobs = load("renewed")
    if opts.mode == "archive":
        result = recount(stale, renewed, stale_jobs, renewed_jobs)
    else:
        started = process_time()
        groups = select(stale, renewed)
        if opts.mode == "diagnostic":
            selected = [DIAGNOSTIC]
        elif opts.mode == "sample":
            selected = list(dict.fromkeys(key for _, keys in groups.values() for key in keys))
        else:
            selected = groups[opts.mode][1]
        if opts.limit is not None:
            selected = selected[:opts.limit]
        result = {"seed": SEED, "uniform within each group": groups, "selected": selected,
                  "edit after": EDIT_AFTER, "round limit": ROUNDS, "knot bound": KNOT_BOUND,
                  "results": [replay(key, stale[key], renewed[key]) for key in selected]}
        result["CPU seconds"] = round(process_time() - started, 4)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
