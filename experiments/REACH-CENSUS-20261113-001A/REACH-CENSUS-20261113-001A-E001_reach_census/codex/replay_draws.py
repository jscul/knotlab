"""G0: exact, single-process replay of the registered LIMIT-ONLY draws.

Run from the repository root with .venv/bin/python -B and no arguments. Existing
outputs are reused only after checking every input hash and the output hash.
This entry point never computes a family's fate, limit, ray, or DP.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import random
import resource
import sys
import time


THREAD_VARIABLES = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS",
)
for _variable in THREAD_VARIABLES:
    os.environ[_variable] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LANGUAGE = ROOT / (
    "experiments/SHORT-DESC-20261112-001A/"
    "SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
)
SOURCE_CENSUS = ROOT / (
    "experiments/LIMIT-ONLY-20261112-001A/"
    "LIMIT-ONLY-20261112-001A-E001_limit_only/census.py"
)
STORED = ROOT / (
    "artifacts/LIMIT-ONLY-20261112-001A/"
    "LIMIT-ONLY-20261112-001A-E001_limit_only"
)
DRAW_PATH = HERE / "draws.jsonl.gz"
GATE_PATH = HERE / "replay_gate.json"
WORKERS = tuple(range(8))
TRIES = 150_000
EXPECTED_DRAWS = 223_261
TOLERANCE = 1e-9


def compact(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source_hashes():
    sources = [
        Path(__file__).resolve(), LANGUAGE, SOURCE_CENSUS,
        ROOT / "research/REACH-CENSUS-20261113-001/codex_spec.md",
        HERE.parent / "contract.json",
    ]
    sources.extend(STORED / f"sample_{worker}.jsonl.gz" for worker in WORKERS)
    return {str(path.relative_to(ROOT)): digest(path) for path in sources}


def stored_rows(worker, mismatches, stats):
    """Yield data rows, checking that the sole done row is final."""
    done = False
    path = STORED / f"sample_{worker}.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except (ValueError, TypeError) as error:
                mismatches.append(dict(
                    kind="invalid_stored_json", worker=worker,
                    line_number=line_number, error=str(error), line=line,
                ))
                continue
            if done:
                mismatches.append(dict(
                    kind="row_after_done", worker=worker,
                    line_number=line_number, stored=row,
                ))
            if row.get("kind") == "done":
                done = True
                stats["done_rows"] += 1
                if row.get("tries") != TRIES:
                    mismatches.append(dict(
                        kind="stored_tries", worker=worker,
                        line_number=line_number, expected=TRIES, stored=row,
                    ))
                continue
            stats["stored_rows"] += 1
            yield line_number, row
    if stats["done_rows"] != 1:
        mismatches.append(dict(
            kind="done_row_count", worker=worker,
            expected=1, actual=stats["done_rows"],
        ))


def reuse(hashes):
    if not (GATE_PATH.exists() and DRAW_PATH.exists()):
        raise RuntimeError("Partial existing output: refusing to overwrite it")
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    if gate.get("source_hashes") != hashes:
        raise RuntimeError("Existing replay source hashes do not match current inputs")
    if gate.get("draws_sha256") != digest(DRAW_PATH):
        raise RuntimeError("Existing draws hash does not match the recorded replay")
    if gate.get("gate") != "G0" or gate.get("finished") is not True:
        raise RuntimeError("Existing gate is not a finished G0 replay")
    print(compact(dict(
        reused=True, gate="G0", passed=gate["passed"],
        total_draws=gate["total_draws"],
        distinct_families=gate["distinct_families"],
        mismatch_count=gate["mismatch_count"],
        seconds=gate["seconds"], peak_rss_bytes=gate["peak_rss_bytes"],
    )), flush=True)
    return 0 if gate["passed"] else 1


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    started = time.perf_counter()
    initial_hashes = source_hashes()
    if GATE_PATH.exists() or DRAW_PATH.exists():
        return reuse(initial_hashes)

    specification = importlib.util.spec_from_file_location("reach_replay_language", LANGUAGE)
    language = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(language)

    mismatches = []
    workers = []
    distinct_keys = set()
    fate_limit = Counter()
    total_draws = 0
    bits_checked = 0
    defs_checked = 0
    # Exclusive creation protects pre-existing files. A failed interrupted run
    # leaves its partial output for explicit inspection instead of overwriting it.
    with DRAW_PATH.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="\n") as output:
                for worker in WORKERS:
                    worker_started = time.perf_counter()
                    stats = dict(
                        worker=worker, tries=TRIES, replayed_draws=0,
                        stored_rows=0, done_rows=0, paired_draws=0,
                        bits_checked=0, defs_checked=0,
                    )
                    rng = random.Random(int(hashlib.sha256(
                        f"LO:{worker}".encode()
                    ).hexdigest()[:16], 16))
                    rows = iter(stored_rows(worker, mismatches, stats))
                    for try_index in range(TRIES):
                        draw = language.sample(rng, **language.VARIANTS["main"])
                        if "defs" not in draw or draw.get("t") is None:
                            continue
                        stats["replayed_draws"] += 1
                        pair = next(rows, None)
                        key = compact(draw["defs"])
                        distinct_keys.add(key)
                        total_draws += 1
                        if pair is None:
                            mismatches.append(dict(
                                kind="missing_stored_row", worker=worker,
                                try_index=try_index, key=key,
                            ))
                            row = {}
                            line_number = None
                        else:
                            line_number, row = pair
                            stats["paired_draws"] += 1
                        expected_bits = draw["bits"] - draw["tbits"]
                        stored_bits = row.get("bits")
                        stats["bits_checked"] += 1
                        bits_checked += 1
                        if (
                            not isinstance(stored_bits, (int, float))
                            or not math.isfinite(stored_bits)
                            or abs(stored_bits - expected_bits) > TOLERANCE
                        ):
                            mismatches.append(dict(
                                kind="bits", worker=worker, try_index=try_index,
                                stored_line=line_number, expected=expected_bits,
                                stored=stored_bits, key=key,
                            ))
                        if "defs" in row:
                            stats["defs_checked"] += 1
                            defs_checked += 1
                            if row["defs"] != json.loads(key):
                                mismatches.append(dict(
                                    kind="defs", worker=worker,
                                    try_index=try_index, stored_line=line_number,
                                    expected=json.loads(key), stored=row["defs"],
                                ))
                        for field in ("fate", "limit_alive", "bits"):
                            if field not in row:
                                mismatches.append(dict(
                                    kind="missing_stored_field", worker=worker,
                                    try_index=try_index, stored_line=line_number,
                                    field=field,
                                ))
                        fate_limit[(row.get("fate"), row.get("limit_alive"))] += 1
                        output.write(compact(dict(
                            worker=worker, try_index=try_index, key=key,
                            fate=row.get("fate"),
                            limit_alive=row.get("limit_alive"), bits=stored_bits,
                        )) + "\n")
                    for line_number, row in rows:
                        mismatches.append(dict(
                            kind="extra_stored_row", worker=worker,
                            stored_line=line_number, stored=row,
                        ))
                    if stats["replayed_draws"] != stats["stored_rows"]:
                        mismatches.append(dict(
                            kind="worker_count", worker=worker,
                            replayed=stats["replayed_draws"],
                            stored=stats["stored_rows"],
                        ))
                    stats["seconds"] = time.perf_counter() - worker_started
                    workers.append(stats)
                    print(compact(dict(
                        event="worker_done", **stats,
                        cumulative_mismatches=len(mismatches),
                    )), flush=True)

    if total_draws != EXPECTED_DRAWS:
        mismatches.append(dict(
            kind="total_draw_count", expected=EXPECTED_DRAWS, actual=total_draws,
        ))
    final_hashes = source_hashes()
    if final_hashes != initial_hashes:
        for path in sorted(set(final_hashes) | set(initial_hashes)):
            if final_hashes.get(path) != initial_hashes.get(path):
                mismatches.append(dict(
                    kind="input_changed_during_replay", path=path,
                    before=initial_hashes.get(path), after=final_hashes.get(path),
                ))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_rss_bytes = rss if sys.platform == "darwin" else rss * 1024
    gate = dict(
        schema_version=1, gate="G0", finished=True, passed=not mismatches,
        method="exact seeded draw replay; stored fate and limit_alive copied without recomputation",
        workers=workers, tries_per_worker=TRIES,
        total_sample_calls=len(WORKERS) * TRIES,
        try_index_base=0, seed="int(sha256(f'LO:{worker}').hexdigest()[:16],16)",
        variant=language.VARIANTS["main"], bits_absolute_tolerance=TOLERANCE,
        expected_draws=EXPECTED_DRAWS, total_draws=total_draws,
        distinct_families=len(distinct_keys), bits_checked=bits_checked,
        defs_checked=defs_checked,
        fate_limit_counts=[dict(fate=fate, limit_alive=limit_alive, count=count)
                           for (fate, limit_alive), count in sorted(fate_limit.items())],
        mismatch_count=len(mismatches), mismatches=mismatches,
        source_hashes=initial_hashes, source_hashes_after=final_hashes,
        draws_sha256=digest(DRAW_PATH), draws_bytes=DRAW_PATH.stat().st_size,
        command=f".venv/bin/python -B {Path(__file__).resolve().relative_to(ROOT)}",
        cwd=str(ROOT), python=sys.version, numpy_version=language.np.__version__,
        platform=dict(system=os.uname().sysname, release=os.uname().release,
                      machine=os.uname().machine),
        thread_limits={key: os.environ[key] for key in THREAD_VARIABLES},
        processes=1, child_processes=0,
        seconds=time.perf_counter() - started, peak_rss_bytes=peak_rss_bytes,
    )
    with GATE_PATH.open("x", encoding="utf-8") as output:
        json.dump(gate, output, indent=2, sort_keys=True)
        output.write("\n")
    print(compact(dict(
        event="gate_finished", passed=gate["passed"],
        total_draws=total_draws, distinct_families=len(distinct_keys),
        mismatch_count=len(mismatches), seconds=gate["seconds"],
        peak_rss_bytes=peak_rss_bytes, draws_bytes=gate["draws_bytes"],
    )), flush=True)
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
