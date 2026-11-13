"""G4: check the usual limit of every distinct stored-forever draw family.

This single-process check uses exactly LS.usual and L's relation iteration. It
does not build a ray or run the DP. Existing results require verified source
hashes and a verified canonical-payload checksum before they can be reused.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
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
LIMIT_STATE = ROOT / (
    "experiments/LIMIT-STATE-20261112-001A/"
    "LIMIT-STATE-20261112-001A-E001_limit_states/census.py"
)
DRAW_PATH = HERE / "draws.jsonl.gz"
REPLAY_GATE = HERE / "replay_gate.json"
GATE_PATH = HERE / "compactness_gate.json"


def compact(value):
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source_hashes():
    paths = [
        Path(__file__).resolve(), LANGUAGE, LIMIT_STATE, DRAW_PATH, REPLAY_GATE,
        ROOT / "research/REACH-CENSUS-20261113-001/codex_spec.md",
        HERE.parent / "contract.json",
    ]
    return {str(path.relative_to(ROOT)): digest(path) for path in paths}


def payload_digest(gate):
    payload = {key: value for key, value in gate.items() if key != "payload_sha256"}
    return hashlib.sha256(compact(payload).encode("utf-8")).hexdigest()


def summary(gate, reused):
    return dict(
        event="gate_finished", gate="G4", reused=reused, passed=gate["passed"],
        forever_draws=gate["forever_draws"],
        forever_families=gate["forever_families"],
        families_checked=gate["families_checked"],
        failure_families=gate["failure_families"],
        failure_draws=gate["failure_draws"],
        error_families=gate["error_families"],
        seconds=gate["seconds"], peak_rss_bytes=gate["peak_rss_bytes"],
    )


def reuse(hashes):
    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    if gate.get("source_hashes") != hashes:
        raise RuntimeError("Existing G4 source hashes do not match current inputs")
    if gate.get("payload_sha256") != payload_digest(gate):
        raise RuntimeError("Existing G4 canonical-payload checksum does not match")
    if gate.get("gate") != "G4" or gate.get("finished") is not True:
        raise RuntimeError("Existing output is not a finished G4 check")
    print(compact(summary(gate, reused=True)), flush=True)
    return 0 if gate["passed"] else 1


def normalize(key):
    return [(k, l, [(callee, tuple(args)) for callee, args in calls])
            for k, l, calls in json.loads(key)]


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    started = time.perf_counter()
    initial_hashes = source_hashes()
    if GATE_PATH.exists():
        return reuse(initial_hashes)

    replay = json.loads(REPLAY_GATE.read_text(encoding="utf-8"))
    if replay.get("gate") != "G0" or replay.get("passed") is not True:
        raise RuntimeError("G4 requires a passed G0 replay")
    if replay.get("draws_sha256") != initial_hashes[str(DRAW_PATH.relative_to(ROOT))]:
        raise RuntimeError("The draws do not match G0's recorded output hash")
    if replay["source_hashes"][str(LANGUAGE.relative_to(ROOT))] != initial_hashes[str(LANGUAGE.relative_to(ROOT))]:
        raise RuntimeError("L no longer matches the source used by G0")

    spec = importlib.util.spec_from_file_location("reach_g4_limit_state", LIMIT_STATE)
    limit_state = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(limit_state)
    language = limit_state.L
    if Path(language.__file__).resolve() != LANGUAGE:
        raise RuntimeError("LS imported an unexpected dlang module")

    forever = Counter()
    total_draws = 0
    with gzip.open(DRAW_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            total_draws += 1
            if row["fate"] == "forever":
                forever[row["key"]] += 1
    if total_draws != replay["total_draws"]:
        raise RuntimeError("The decoded draw count disagrees with G0")

    failures = []
    errors = []
    checked = 0
    usual_pass_families = 0
    usual_pass_draws = 0
    computation_started = time.perf_counter()
    for key in sorted(forever):
        try:
            defs = normalize(key)
            usual, passes = limit_state.usual(defs)
            greatest = language.depth_sequence(usual, language.TOP)[2]
            main_relation = language.relations(usual, greatest)[-1]
            usual_alive = bool(main_relation.any())
            checked += 1
            usual_pass_families += int(passes)
            usual_pass_draws += int(passes) * forever[key]
            if not usual_alive:
                failure = dict(
                    key=key, draw_count=forever[key], draw_references=[],
                    usual_pass_through=bool(passes),
                    main_allowed_states=[int(i) for i in language.np.flatnonzero(main_relation)],
                    usual_self_allowed_states={
                        str(i): [int(s) for s in language.np.flatnonzero(rel)]
                        for i, rel in greatest.items()
                    },
                )
                failures.append(failure)
                print(compact(dict(
                    event="G4_failure", key=key, draw_count=forever[key],
                    failure_families=len(failures),
                )), flush=True)
        except Exception as error:
            errors.append(dict(
                key=key, draw_count=forever[key], draw_references=[],
                exception_type=type(error).__name__, error=str(error),
            ))
            print(compact(dict(
                event="G4_error", key=key,
                exception_type=type(error).__name__, error=str(error),
            )), flush=True)
        processed = checked + len(errors)
        if processed % 5000 == 0 or processed == len(forever):
            print(compact(dict(
                event="progress", families_processed=processed,
                forever_families=len(forever), families_checked=checked,
                failure_families=len(failures), error_families=len(errors),
                seconds=time.perf_counter() - started,
            )), flush=True)
    computation_seconds = time.perf_counter() - computation_started

    # Keep references only for failures/errors, avoiding a per-draw reference
    # table for families that pass. Every retained reference is 0-based.
    retained = {row["key"]: row for row in failures + errors}
    if retained:
        with gzip.open(DRAW_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["fate"] == "forever" and row["key"] in retained:
                    retained[row["key"]]["draw_references"].append(dict(
                        worker=row["worker"], try_index=row["try_index"],
                    ))
        for row in retained.values():
            if len(row["draw_references"]) != row["draw_count"]:
                raise RuntimeError("Retained failure references disagree with draw counts")

    final_hashes = source_hashes()
    input_changes = [dict(
        path=path, before=initial_hashes.get(path), after=final_hashes.get(path),
    ) for path in sorted(set(initial_hashes) | set(final_hashes))
        if initial_hashes.get(path) != final_hashes.get(path)]
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_rss_bytes = rss if sys.platform == "darwin" else rss * 1024
    gate = dict(
        schema_version=1, gate="G4", finished=True,
        passed=not failures and not errors and not input_changes,
        question="No stored-forever draw has a dead usual limit",
        calculation="u=LS.usual(defs)[0]; G=L.depth_sequence(u,L.TOP)[2]; bool(L.relations(u,G)[-1].any())",
        total_draws=total_draws, forever_draws=sum(forever.values()),
        forever_families=len(forever), families_checked=checked,
        failure_families=len(failures),
        failure_draws=sum(row["draw_count"] for row in failures), failures=failures,
        error_families=len(errors), errors=errors,
        usual_pass_through_families=usual_pass_families,
        usual_pass_through_draws=usual_pass_draws,
        input_changes=input_changes,
        source_hashes=initial_hashes, source_hashes_after=final_hashes,
        computation_seconds=computation_seconds,
        seconds=time.perf_counter() - started, peak_rss_bytes=peak_rss_bytes,
        command=f".venv/bin/python -B {Path(__file__).resolve().relative_to(ROOT)}",
        cwd=str(ROOT), python=sys.version, numpy_version=language.np.__version__,
        platform=dict(system=os.uname().sysname, release=os.uname().release,
                      machine=os.uname().machine),
        thread_limits={name: os.environ[name] for name in THREAD_VARIABLES},
        processes=1, child_processes=0, try_index_base=0,
        integrity_scope="SHA-256 of canonical compact sorted-key JSON excluding payload_sha256",
    )
    gate["payload_sha256"] = payload_digest(gate)
    with GATE_PATH.open("x", encoding="utf-8") as output:
        json.dump(gate, output, indent=2, sort_keys=True)
        output.write("\n")
    print(compact(summary(gate, reused=False)), flush=True)
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
