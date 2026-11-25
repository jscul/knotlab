"""Grow each case with the recorded engine and count from every member."""

from collections import Counter
import ctypes
import gzip
import hashlib
from itertools import combinations, count
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

# The shared runner provides case-level parallelism. Keep numerical imports single-threaded.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORDED_ENGINE = (
    ROOT / "experiments" / "KNOTS-WITHIN-REACH-20261125-001A"
    / "KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach"
)
sys.path.insert(0, str(RECORDED_ENGINE))
import kwr


KNOT_LAWS = ("nae", "parity")
GROWTH_LAWS = {"L0", "L1", "L6", "L7", "L9", "L11"}
COMPILE_FLAGS = ("-std=c++17", "-O3", "-fPIC", "-shared")
RECORDED_ENGINE_SHA256 = "51c8705d33a8df619b6493c5ba12bbd91a3ab3587ecb7ad2ce67b54bb76fd473"
CENSUS_SHA256 = "bb6c3456a573af80e8657013ab9f8103851694d285145ecefa3911cb3cfa45ed"


def compact_json(value):
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("ascii")


def setup(params):
    global INPUT_CASES, ARTIFACT_DIR, COUNT_REACH, CASES_SHA256, COUNT_SOURCE_SHA256
    if kwr.sha256(RECORDED_ENGINE / "kwr.py") != RECORDED_ENGINE_SHA256:
        raise ValueError("recorded growth engine changed")
    if kwr.sha256(Path(kwr.DATA) / "census_starts.json") != CENSUS_SHA256:
        raise ValueError("recorded census starts changed")
    kwr.census()

    case_path = Path(params.get("cases", HERE.parent / "cases.json"))
    case_bytes = case_path.read_bytes()
    CASES_SHA256 = hashlib.sha256(case_bytes).hexdigest()
    if params.get("cases_sha256", CASES_SHA256) != CASES_SHA256:
        raise ValueError(f"frozen cases changed: {case_path}")
    case_data = json.loads(case_bytes)
    INPUT_CASES = case_data["cases"] if isinstance(case_data, dict) else case_data
    ARTIFACT_DIR = Path(params["artifact_dir"]).resolve()

    source = HERE / "count_reach.cpp"
    COUNT_SOURCE_SHA256 = hashlib.sha256(source.read_bytes()).hexdigest()
    if params.get("count_source_sha256", COUNT_SOURCE_SHA256) != COUNT_SOURCE_SHA256:
        raise ValueError(f"frozen count source changed: {source}")
    with tempfile.TemporaryDirectory(prefix="widening-rosters-count-") as temporary:
        library = Path(temporary) / "count_reach.so"
        subprocess.run(["g++", *COMPILE_FLAGS, str(source), "-o", str(library)], check=True)
        COUNT_REACH = ctypes.CDLL(str(library)).count_reach
    vector = np.ctypeslib.ndpointer(dtype=np.intc, flags=("C_CONTIGUOUS", "ALIGNED"))
    COUNT_REACH.argtypes = [vector, vector, ctypes.c_int, ctypes.c_int, vector]
    COUNT_REACH.restype = ctypes.c_int


def cases():
    for case in INPUT_CASES:
        if case["law"] not in GROWTH_LAWS:
            raise ValueError(f"unknown growth law: {case['law']}")
        rounds = case["rounds"]
        if not rounds or rounds != sorted(set(rounds)) or rounds[0] < 0:
            raise ValueError(f"rounds must be nonnegative and strictly increasing: {rounds}")
        if case["r_max"] < 0 or case["knot_bound"] < 1:
            raise ValueError(f"invalid count or growth bounds for {case['id']}")
        yield case["id"], case


def touching_stars(size):
    """One shared distinction per pair and two loose distinctions per knot."""
    distinctions = count()
    stars = [[] for _ in range(size)]
    for a, b in combinations(range(size), 2):
        distinction = next(distinctions)
        stars[a].append(distinction)
        stars[b].append(distinction)
    for star in stars:
        star.extend((next(distinctions), next(distinctions)))
    return stars


def start_structure(start):
    family, index = start.split(":")
    index = int(index)
    if family == "census" and 0 <= index < len(kwr.census()):
        return kwr.make_start(start)
    if family == "touching" and 3 <= index <= 6:
        return kwr.pm.from_stars(touching_stars(index))
    raise ValueError(f"unknown start: {start}")


def write_rows(kind, rows):
    """Write one immutable, content-addressed gzip JSONL artifact."""
    folder = ARTIFACT_DIR / "raw" / kind
    folder.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with tempfile.NamedTemporaryFile(prefix=".pending-", dir=folder, delete=False) as output:
        pending = Path(output.name)
        try:
            with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0, compresslevel=3) as file:
                for row in rows:
                    line = compact_json(row) + b"\n"
                    digest.update(line)
                    file.write(line)
            output.flush()
            os.fsync(output.fileno())
            sha256 = digest.hexdigest()
            path = folder / f"{sha256}.jsonl.gz"
            try:
                os.link(pending, path)
            except FileExistsError:
                pass
        finally:
            pending.unlink(missing_ok=True)
    return str(path.relative_to(ARTIFACT_DIR)), sha256


def supports_by_round(growth):
    prior_knots = 0
    for stage, knots in enumerate(growth.n_knots):
        yield {
            "round": stage,
            "knots": knots,
            "distinctions": growth.n_dist[stage],
            "supports": [sorted(support) for support in growth.S.places[prior_knots:knots]],
        }
        prior_knots = knots


def count_from_all_members(members, pairs, maximum_steps):
    member_index = {member: i for i, member in enumerate(members)}
    neighbors = [[] for _ in members]
    for first, second in pairs:
        a, b = member_index[first], member_index[second]
        neighbors[a].append(b)
        neighbors[b].append(a)

    degrees = [len(row) for row in neighbors]
    offsets = np.empty(len(members) + 1, dtype=np.intc)
    offsets[0] = 0
    np.cumsum(degrees, out=offsets[1:])
    adjacent = np.fromiter(
        (member for row in neighbors for member in row), dtype=np.intc, count=2 * len(pairs)
    )
    counts = np.empty((len(members), maximum_steps + 1), dtype=np.intc)
    if COUNT_REACH(offsets, adjacent, len(members), maximum_steps, counts):
        raise MemoryError("member count could not allocate its queues")
    histogram = {str(degree): frequency for degree, frequency in sorted(Counter(degrees).items())}
    return counts.tolist(), histogram


def read_stage(growth, case, knot_law, stage):
    members = growth.members[stage]
    knots = growth.n_knots[stage]
    met = kwr.met_sets(growth.S, members, upto=knots)
    parts = kwr.parts_of(growth.S, members, upto=knots, ms=met)
    pairs = sorted({pair for met_members in met.values() for pair in combinations(sorted(met_members), 2)})
    counts, degrees = count_from_all_members(members, pairs, case["r_max"])
    greatest = [max(column) for column in zip(*counts)] if counts else [0] * (case["r_max"] + 1)
    detail = {
        "round": stage,
        "member_ids": members,
        "witnessed_pairs": pairs,
        "part_members": parts,
        "counts_by_member": counts,
    }
    summary = {
        "case": case["id"],
        "kl": knot_law,
        "round": stage,
        "knots": knots,
        "members": len(members),
        "pairs": len(pairs),
        "part_sizes": sorted(map(len, parts), reverse=True),
        "degree_histogram": degrees,
        "greatest_counts": greatest,
        "reach_sha256": hashlib.sha256(compact_json(sorted(counts))).hexdigest(),
    }
    return summary, detail


def run_law(case, knot_law):
    closing_rounds = []

    def record_closing(_growth, round_record):
        if round_record.get("closing"):
            closing_rounds.append(round_record["round"])

    started = time.monotonic()
    growth = kwr.Grown(
        case["start"], kwr.make_law(case["law"], knot_law),
        rounds=case["rounds"][-1], knot_bound=case["knot_bound"],
        S=start_structure(case["start"]), parts_every_round=False, on_round=record_closing,
    )
    grow_seconds = time.monotonic() - started
    artifact_started = time.monotonic()
    support_file, support_sha256 = write_rows("supports", supports_by_round(growth))
    support_write_seconds = time.monotonic() - artifact_started
    summaries = []
    stage_read_seconds = {}

    def stage_rows():
        for stage in case["rounds"]:
            if growth.reached(stage):
                read_started = time.monotonic()
                summary, detail = read_stage(growth, case, knot_law, stage)
                stage_read_seconds[str(stage)] = round(time.monotonic() - read_started, 6)
                summaries.append(summary)
                yield detail

    artifact_started = time.monotonic()
    stages_file, stages_sha256 = write_rows("stages", stage_rows())
    stages_seconds = time.monotonic() - artifact_started
    return {
        "kl": knot_law,
        "rounds_done": growth.rounds_done,
        "stop": growth.stop or "rounds",
        "guard": growth.guard,
        "ended": growth.ended,
        "missing_rounds": [stage for stage in case["rounds"] if not growth.reached(stage)],
        "knots": growth.S.n_knots,
        "distinctions": growth.S.n_distinctions,
        "parity_closing_rounds": closing_rounds,
        "grow_seconds": round(grow_seconds, 6),
        "support_write_seconds": round(support_write_seconds, 6),
        "stages_seconds": round(stages_seconds, 6),
        "stage_read_seconds": stage_read_seconds,
        "support_file": support_file,
        "support_sha256": support_sha256,
        "stages_file": stages_file,
        "stages_sha256": stages_sha256,
        "stages": summaries,
    }


def run(case_id, case):
    if case_id != case["id"]:
        raise ValueError("case identifiers disagree")
    return {
        "case": case_id,
        "start": case["start"],
        "law": case["law"],
        "rounds": case["rounds"],
        "r_max": case["r_max"],
        "knot_bound": case["knot_bound"],
        "cases_sha256": CASES_SHA256,
        "count_source_sha256": COUNT_SOURCE_SHA256,
        "laws": [run_law(case, knot_law) for knot_law in KNOT_LAWS],
    }
