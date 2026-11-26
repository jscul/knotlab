"""Search for at least two whole-held class labels under the frozen parity moves.

Replay the one-round archive before reading extra rounds. Add two seeded
samples of larger connected starts, with publicly specified weightings. Read
each stage under ordinary growth. A stage counts as testable when its class
label rank is at least two. A candidate has at least two dimensions left
after quotienting by the span of labels read on individual listed supports.
Independently tally readings from supports whose allowed-state projections
pass K1–K3. Count over-cap stages as unread. The sample and round bounds
give an exploratory referee check, with no assertion about untested starts.
"""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
from random import Random
import resource
from time import perf_counter

from extended_classes import BinarySpan, bit_sum, incidence, inspect, shortest_change_span
from frozen_recount_core import first_groups, grow


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
HISTORICAL_SIZES = (6, 7, 8)
LARGER_SIZES = (9, 10, 12, 16)
HISTORICAL_SEED = 20261206
DENSITY_SEED = 61261226
FUNDED_SEED = 81261226
ARCHIVE_COUNT = 300
DEFAULT_COUNT = 256
ROUNDS = 4
STAGE_CAP = 1024
STAGE_FIELDS = (
    "knots", "distinctions", "allowed rank", "move rank", "label rank",
    "listed reader rank", "knot reader rank", "old projection kept",
)


def input_rows(specification):
    n, meetings, loose = specification
    rows = [[] for _ in range(n)]
    distinction = 0
    for a, b, multiplicity in meetings:
        for _ in range(multiplicity):
            rows[a].append(distinction)
            rows[b].append(distinction)
            distinction += 1
    for a, amount in enumerate(loose):
        rows[a].extend(range(distinction, distinction + amount))
        distinction += amount
    return tuple(map(tuple, rows))


def connected(n, meetings):
    neighbors = [set() for _ in range(n)]
    for a, b, _ in meetings:
        neighbors[a].add(b)
        neighbors[b].add(a)
    reached = {0}
    pending = [0]
    for knot in pending:
        different = neighbors[knot] - reached
        pending.extend(different)
        reached.update(different)
    return len(reached) == n


def draws(n, count, cohort):
    if cohort == "historical sample":
        rng = Random(HISTORICAL_SEED + n)
        meeting_probability = 1 / 3
        start_cap = 18
    elif cohort == "larger sample":
        rng = Random(DENSITY_SEED + n)
        meeting_probability = 2.75 / (n - 1)
        start_cap = 3 * n
    else:
        assert cohort == "larger funded sample"
        rng = Random(FUNDED_SEED + n)
        meeting_probability = 2.25 / (n - 1)
        start_cap = 8 * n
    pairs = tuple(combinations(range(n), 2))
    accepted = 0
    proposals = 0
    while accepted < count:
        proposals += 1
        present = [pair for pair in pairs if rng.random() < meeting_probability]
        weights = (1, 1, 1, 2) if cohort == "larger funded sample" else (1, 2)
        meetings = tuple((a, b, rng.choice(weights)) for a, b in present)
        if cohort == "larger funded sample":
            if not connected(n, meetings):
                continue
            shared = input_rows((n, meetings, (0,) * n))
            _, _, demand = first_groups(shared, provision_all=True)
            loose = tuple(max(1, 3 - len(row), demand[i]) + (rng.randrange(3) == 0)
                          for i, row in enumerate(shared))
        else:
            loose = tuple(rng.choice((0, 1, 2)) for _ in range(n))
            if not connected(n, meetings):
                continue
        if sum(m for _, _, m in meetings) + sum(loose) > start_cap:
            continue
        rows = input_rows((n, meetings, loose))
        if any(len(row) < 3 for row in rows):
            continue
        accepted += 1
        yield rows, proposals


def archive_rows(file):
    with (STUDY / file).open() as stream:
        return {row['index']: row for line in stream for row in (json.loads(line),)}


def ring_rows(sizes):
    n = sum(sizes)
    meetings = []
    first = 0
    for size in sizes:
        for i in range(size):
            meetings.append((*sorted((first + i, first + (i + 1) % size)), 1))
        first += size
    return input_rows((n, sorted(meetings), (2,) * n))


def check_frozen(index, archived, start, end, stages):
    assert archived["knots"] == len(start), index
    assert archived["grows"] == (len(stages) >= 2), index
    if not archived["grows"]:
        assert archived["end"] == end["status"], (index, archived, end)
        return
    first = stages[1]
    assert archived["classes"] == 1 << first["label rank"], (index, archived, first)
    assert archived["each piece parity a label"] == first["old shared parity is a label"], index
    if archived["classes"] >= 4:
        assert archived["labels read knot by knot"] == (first["label rank"] == first["listed reader rank"]), index


def replay(start, rounds, cap):
    old_shared = tuple(name for name, owners in incidence(start).items() if len(owners) == 2)
    rows = start
    summaries = [inspect(start)]
    end = {"status": "round limit", "round": rounds}
    witnesses = []
    for next_round in range(1, rounds + 1):
        growth = grow(rows, max_distinctions=cap)
        if growth.status != "funded":
            end = {"status": growth.status, "round": next_round}
            if growth.status == "capped":
                end["at least this many distinctions"] = growth.distinctions
            break
        summaries.append(inspect(growth.stage, old_rows=rows, old_shared=old_shared))
        rows = growth.stage
        current = summaries[-1]
        if (current["label rank"] - current["knot reader rank"] >= 2
                or not current["old projection kept"]):
            witnesses.append({"round": next_round, "supports": rows, "analysis": current})
    return summaries, end, witnesses


def literal_change_control(rows):
    owners = incidence(rows)
    assert sorted(owners) == list(range(len(owners)))
    checks = tuple(map(bit_sum, rows))
    allowed = [word for word in range(1 << len(owners))
               if all((word & check).bit_count() % 2 == 0 for check in checks)]
    literal_moves = BinarySpan()
    for j in owners:
        valid = [word for word in allowed if word & (1 << j)]
        if valid:
            shortest = min(word.bit_count() for word in valid)
            for word in valid:
                if word.bit_count() == shortest:
                    literal_moves.add(word)
    compressed_moves = shortest_change_span([owners[j] for j in sorted(owners)], len(rows),
                                           len(allowed).bit_length() - 1)
    assert len(literal_moves) == len(compressed_moves)
    assert all(not literal_moves.reduce(word) for word in compressed_moves.rows.values())
    return {"distinctions": len(owners), "allowed assignments": len(allowed),
            "move rank": len(literal_moves)}


def run_controls(rounds, cap):
    controls = {}
    # The disjoint pair is a positive control for whole-held rank two. It is
    # outside the connected sampling frames below.
    for sizes, first_rank in (((3,), 0), ((4,), 1), ((5,), 1), ((5, 5), 2)):
        source = ring_rows(sizes)
        stages, end, _ = replay(source, rounds, cap)
        first = stages[1]
        assert first["label rank"] == first_rank and first["listed reader rank"] == 0
        renamed = tuple(tuple(len(incidence(source)) - 1 - name for name in row)
                        for row in reversed(source))
        repeat, _, _ = replay(renamed, rounds, cap)
        assert all(all(left.get(key) == right.get(key) for key in STAGE_FIELDS)
                   for left, right in zip(stages, repeat, strict=True))
        controls[str(sizes)] = {"stages": stages, "end": end, "renaming matched": True}
        if len(sizes) == 1:
            controls[str(sizes)]["literal start"] = literal_change_control(source)
    return controls


def summarize(rows):
    stages = defaultdict(Counter)
    end_statuses = Counter()
    positive_starts = Counter()
    for row in rows:
        end_statuses[f"{row['end']['status']} at {row['end']['round']}"] += 1
        for age, stage in enumerate(row["stages"]):
            _, _, _, _, label_rank, listed_rank, knot_rank, old_projection_kept = stage
            tally = stages[age]
            tally["read"] += 1
            tally[f"class label rank {label_rank}"] += 1
            if label_rank >= 2:
                tally["testable"] += 1
            tally[f"whole-held rank {label_rank - listed_rank}"] += 1
            tally[f"whole-held rank with K1–K3 readers {label_rank - knot_rank}"] += 1
            if old_projection_kept is False:
                tally["old projection narrowed"] += 1
        if any(stage[4] >= 2 for stage in row["stages"]):
            positive_starts["testable within read stages"] += 1
        if any(stage[4] - stage[5] >= 2 for stage in row["stages"]):
            positive_starts["whole-held rank at least two anywhere read"] += 1
        if any(stage[4] - stage[6] >= 2 for stage in row["stages"]):
            positive_starts["K1–K3-filtered whole-held rank at least two anywhere read"] += 1
    return {"starts": len(rows), "stages": dict(stages), "end statuses": end_statuses,
            "start counts": positive_starts,
            "maximum knots read": max(stage[0] for row in rows for stage in row["stages"]),
            "maximum distinctions read": max(stage[1] for row in rows for stage in row["stages"])}


def run(count, rounds, cap, pilot_limit):
    started = perf_counter()
    controls = run_controls(rounds, cap)
    prior = archive_rows("frozen_heldout.jsonl")
    census = archive_rows("frozen_census.jsonl")
    starts = json.loads((STUDY.parent / 'FORBID-EDITS-20261126-001' / 'starts.json').read_text())
    replayed = Counter()
    summaries = {}
    rows = []
    witnesses = []

    def record(cohort, n, index, source, archived=None):
        stages, end, new_witnesses = replay(source, rounds, cap)
        if archived is not None:
            check_frozen(index, archived, source, end, stages)
            replayed[cohort] += 1
        rows.append({"cohort": cohort, "size": n, "sample index": index,
                     "stages": [[stage.get(key) for key in STAGE_FIELDS] for stage in stages], "end": end})
        if new_witnesses:
            witnesses.append({"cohort": cohort, "size": n, "sample index": index,
                              "start supports": source, "stages": new_witnesses})

    offset = len(rows)
    tic = perf_counter()
    for index, archived in census.items():
        if archived.get("classes", 1) >= 4:
            record("testable census rounds", archived["knots"], index, input_rows(starts[index]), archived)
    summaries["testable census rounds"] = summarize(rows[offset:]) | {"seconds": perf_counter() - tic}

    for cohort, sizes, target in (("historical sample", HISTORICAL_SIZES, ARCHIVE_COUNT),
                                  ("larger sample", LARGER_SIZES, count),
                                  ("larger funded sample", LARGER_SIZES, count)):
        summaries[cohort] = {}
        for n in sizes:
            offset = len(rows)
            tic = perf_counter()
            planned = min(target, pilot_limit) if pilot_limit else target
            for i, (source, proposals) in enumerate(draws(n, planned, cohort)):
                index = f"{n}-{i}"
                archived = prior[index] if cohort == "historical sample" else None
                record(cohort, n, index, source, archived)
            summaries[cohort][n] = summarize(rows[offset:]) | {
                "seconds": perf_counter() - tic, "proposals for accepted starts": proposals,
            }
    return {
        "protocol": {
            "round rules": "Even parity, ordinary fresh count, loose distinctions free, every shortest change through each distinction.",
            "sampling": "Labelled connected starts with replacement. Accept only if every listed support has at least three distinctions and the start is within its cohort cap.",
            "historical sample": "Meeting probability 1/3 independently per pair, one or two shared distinctions and zero, one or two loose distinctions chosen uniformly, cap 18. Seed 20261206 plus number of knots.",
            "larger sample": "Meeting probability 2.75/(n-1) independently per pair, one or two shared distinctions and zero, one or two loose distinctions chosen uniformly, cap 3*n. Seed 61261226 plus number of knots.",
            "larger funded sample": "Meeting probability 2.25/(n-1) independently per pair, double with probability 1/4. Each knot gets the maximum of its round-one demand with all knots live, one, and the count needed for three distinctions. Add one loose distinction independently with probability 1/3. Cap 8*n. Seed 81261226 plus number of knots.",
            "scheduled larger starts per size per sample": count,
            "round cap": rounds,
            "distinction cap per stage": cap,
            "pilot prefix per sampled size": pilot_limit,
            "stage fields": STAGE_FIELDS,
            "testable stage": "At least four classes (label rank at least two).",
            "candidate": "Label rank minus rank of the span of readings on individual listed supports is at least two.",
            "K1–K3 readers": "Restrict that span to supports with at least three distinctions whose allowed-state projection passes K1–K3.",
            "limits": "Larger sizes and longer runs outside the displayed frame were not tested. Stages beyond the distinction cap were not read.",
        },
        "timing": {"seconds": perf_counter() - started, "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
        "frozen rows matched": replayed,
        "controls": controls,
        "summaries": summaries,
        "witnesses": witnesses,
        "sample rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--rounds", type=int, default=ROUNDS)
    parser.add_argument("--cap", type=int, default=STAGE_CAP)
    parser.add_argument("--pilot-limit", type=int)
    args = parser.parse_args()
    assert args.count > 0 and args.rounds >= 1 and args.cap >= 256
    assert args.pilot_limit is None or args.pilot_limit > 0
    print(json.dumps(run(args.count, args.rounds, args.cap, args.pilot_limit), separators=(",", ":")))
