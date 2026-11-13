"""Deterministic populations and a resumable, bounded address census.

The coordinator is worker zero: --workers 4 starts only THREE child processes.
No full census is started merely by importing this module.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
import math
import multiprocessing as mp
from pathlib import Path
import random
import resource
import signal
import time

import addr

HERE = Path(__file__).resolve().parent
POPULATION_SEED = 20261113


def gamma(rng):
    """Independent reimplementation of the permitted dlang.gamma algorithm."""
    z = 0
    while rng.random() < 0.5:
        z += 1
    n = 1
    for _ in range(z):
        n = 2 * n + (rng.random() < 0.5)
    return int(n), 2 * z + 1


@lru_cache(maxsize=5)
def placement_choices(s):
    return tuple(itertools.combinations(range(1 + s + s * s), 3))


def _placements(rng, s, r):
    choices = placement_choices(s)
    return [choices[rng.randrange(len(choices))] for _ in range(r)]


def _with_key(row, s, sw, d0, d1, placements):
    key = addr.normalize_key((s, sw, d0, d1, placements))
    row.update(key=addr.key_json(key), key_id=addr.key_id(key),
               placements=[list(p) for p in placements])
    return row


def sample_w(i, seed=POPULATION_SEED):
    rng = random.Random(f"{seed}-{i}")
    s, bits = gamma(rng)
    row = {"population": "W", "index": i, "s": s, "bits": bits, "r_capped": False}
    if s > 5:
        row["rejected"] = "s"
        return row
    sw, d0, d1 = [], [], []
    for _ in range(s):
        sw.append(rng.randrange(2))
        d0.append(rng.randrange(s))
        d1.append(rng.randrange(s))
        bits += 1 + 2 * math.log2(s)
    r, rbits = gamma(rng)
    bits += rbits
    row.update(r=r, bits=bits)
    if r > 8:
        row["rejected"] = "r"
        return row
    placements = _placements(rng, s, r)
    row["bits"] = bits + r * math.log2(len(placement_choices(s)))
    return _with_key(row, s, sw, d0, d1, placements)


def automata(s):
    for sw in itertools.product((0, 1), repeat=s):
        for d0 in itertools.product(range(s), repeat=s):
            for d1 in itertools.product(range(s), repeat=s):
                yield sw, d0, d1


def sample_e(s, a, j, aut):
    rng = random.Random(f"20261114-{s}-{a}-{j}")
    g, gbits = gamma(rng)
    r = min(1 + g, 9)
    placements = _placements(rng, s, r)
    # "bits as in the weighting" does not specify which code to charge to
    # E's shifted, capped gamma draw. Preserve both candidates, choose neither.
    abits = (2 * (s.bit_length() - 1) + 1) + s * (1 + 2 * math.log2(s))
    pbits = r * math.log2(len(placement_choices(s)))
    row = {"population": "E", "s": s, "a": a, "j": j,
           "r": r, "r_capped": 1 + g > 9, "bits": None,
           "gamma_value": g, "gamma_draw_bits": gbits,
           "automaton_code_bits": abits, "placement_bits": pbits,
           "reference_bit_candidates": {
               "fixed_automaton_plus_sampled_gamma_plus_placements": abits + gbits + pbits,
               "W_code_of_capped_description": abits + 2 * (r.bit_length() - 1) + 1 + pbits},
           "bits_ambiguity": "E shifted/capped gamma versus W reference code"}
    return _with_key(row, s, *aut, placements)


def build_draws():
    draws = [sample_w(i) for i in range(40000)]
    for s, copies in ((3, 3), (2, 30)):
        for a, aut in enumerate(automata(s)):
            for j in range(copies):
                draws.append(sample_e(s, a, j, aut))
    keys = {}
    for row in draws:
        if "key" in row:
            keys[row["key_id"]] = addr.normalize_key(row["key"])
    return draws, keys


def _inside(path):
    result = Path(path).resolve()
    if result != HERE and HERE not in result.parents:
        raise ValueError(f"Output must be inside {HERE}")
    return result


def _atomic_json(path, value):
    path = _inside(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def write_draws(path, draws):
    path = _inside(path)
    if path.exists():
        with gzip.open(path, "rt") as f:
            old = [json.loads(line) for line in f]
        if old != draws:
            raise ValueError("Existing draws disagree with the deterministic populations")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            for row in draws:
                compressed.write((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode())
    temporary.replace(path)


def read_finished(out, repair=False):
    """Only an unterminated, unparseable final write can be removed on restart."""
    records = {}
    for path in sorted((Path(out) / "keys").glob("worker-*.jsonl")):
        with path.open("rb") as f:
            lines = f.readlines()
        valid_bytes = 0
        for i, line in enumerate(lines):
            try:
                row = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                if i != len(lines) - 1 or line.endswith(b"\n"):
                    raise ValueError(f"Malformed completed record: {path}:{i + 1}")
                if repair:
                    with path.open("r+b") as f:
                        f.truncate(valid_bytes)
                break
            valid_bytes += len(line)
            kid = row["key_id"]
            if kid in records:
                raise ValueError(f"Duplicate completed key {kid}")
            records[kid] = row
        if repair and lines and not lines[-1].endswith(b"\n") and valid_bytes == sum(map(len, lines)):
            # A final object can be complete although its delimiter was lost.
            # Preserve that completed key and delimit the next append safely.
            with path.open("ab") as f:
                f.write(b"\n")
    return records


def select_smoke(draws, keys):
    """Disjoint key strata; original list r (before key deduplication)."""
    rng = random.Random(20261116)
    pools = {
        "E_s3_r_ge4": sorted({d["key_id"] for d in draws
                              if d["population"] == "E" and d["s"] == 3 and d["r"] >= 4}),
        "E_uniform": sorted({d["key_id"] for d in draws if d["population"] == "E"}),
        "W_s_ge2": sorted({d["key_id"] for d in draws
                           if d["population"] == "W" and "key_id" in d and d["s"] >= 2})}
    selected = []
    seen = set()
    strata = {}
    for label, pool in pools.items():
        eligible = [kid for kid in pool if kid not in seen]
        chosen = rng.sample(eligible, 100)
        strata[label] = chosen
        selected.extend(chosen)
        seen.update(chosen)
    return {"seed": 20261116, "sampling_unit": "distinct key",
            "r_filter": "original E placement-list r; existence of an eligible draw",
            "overlap_rule": "sample without replacement, excluding prior strata",
            "strata": strata, "keys": [addr.key_json(keys[kid]) for kid in selected]}


def _worker(k, jobs, out, completed, stop_after, group_id):
    # Address-space ceiling is stricter than the requested resident-memory cap.
    cap = 1400 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    out = Path(out)
    path = out / "keys" / f"worker-{k}.jsonl"
    with path.open("a", buffering=1) as f:
        for key in jobs:
            record = addr.evaluate_key(key)
            record["worker"] = k
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            with completed.get_lock():
                f.write(encoded)
                f.flush()
                completed.value += 1
                done = completed.value
                if stop_after and done >= stop_after:
                    # Dedicated group contains only this run's parent and its
                    # own worker children. This is an actual interrupted run.
                    os.killpg(group_id, signal.SIGTERM)
            if done % 25 == 0:
                print(f"finished {done} keys", flush=True)


def run(out, workers, keys_file=None, stop_after=None):
    if workers < 1:
        raise ValueError("workers must be positive")
    out = _inside(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "keys").mkdir(exist_ok=True)
    started = time.perf_counter()
    draws, all_keys = build_draws()
    write_draws(out / "draws.jsonl.gz", draws)
    if keys_file:
        data = json.loads(Path(keys_file).read_text())
        selected = data["keys"] if isinstance(data, dict) else data
        keys = {addr.key_id(key): addr.normalize_key(key) for key in selected}
        if not set(keys) <= set(all_keys):
            raise ValueError("Key subset contains keys outside the two populations")
    else:
        keys = all_keys
    finished = read_finished(out, repair=True)
    if not set(finished) <= set(keys):
        raise ValueError("Output already contains keys outside this run")
    ordered = sorted(keys)
    random.Random(20261116).shuffle(ordered)
    jobs = [[] for _ in range(workers)]
    for index, kid in enumerate(ordered):
        if kid not in finished:
            jobs[index % workers].append(keys[kid])
    meta = {"schema": 1, "workers": workers, "worker_zero_is_coordinator": True,
            "child_processes": workers - 1,
            "per_worker_address_space_cap_mb": 1400,
            "draw_counts": dict(Counter(d["population"] for d in draws)),
            "rejections_W": dict(Counter(d["rejected"] for d in draws if "rejected" in d)),
            "population_distinct_keys": len(all_keys), "selected_keys": len(keys),
            "already_finished": len(finished), "key_subset": str(keys_file) if keys_file else None,
            "sampling": "random.Random named seeds; rng.randrange for uniform choices",
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (HERE / "addr.py", Path(__file__).resolve())},
            "E_bits_status": "ambiguous; raw components and both reference candidates retained"}
    old_meta = out / "run_info.json"
    prior = None
    if old_meta.exists():
        prior = json.loads(old_meta.read_text())
        if prior["source_sha256"] != meta["source_sha256"]:
            raise ValueError("Source changed since this run began; use a fresh output directory")
    if not any(jobs):
        if prior and prior.get("status") == "complete":
            print(f"already complete: {len(finished)} keys", flush=True)
            return prior
        meta.update(finished=len(finished), elapsed_seconds=time.perf_counter() - started,
                    status="complete")
        _atomic_json(old_meta, meta)
        print(f"already complete: {len(finished)} keys", flush=True)
        return meta
    _atomic_json(old_meta, meta)
    if stop_after:
        os.setpgrp()
    group_id = os.getpgrp()
    ctx = mp.get_context("fork")
    completed = ctx.Value("i", len(finished))
    children = []
    try:
        for k in range(1, workers):
            p = ctx.Process(target=_worker,
                            args=(k, jobs[k], out, completed, stop_after, group_id))
            p.start()
            children.append(p)
        _worker(0, jobs[0], out, completed, stop_after, group_id)
        for p in children:
            p.join()
        failures = [p.exitcode for p in children if p.exitcode != 0]
        if failures:
            raise RuntimeError(f"Worker failures: {failures}; restart retains completed keys")
    except BaseException:
        for p in children:
            if p.is_alive():
                p.terminate()
        for p in children:
            p.join()
        raise
    records = read_finished(out)
    meta.update(finished=len(records), elapsed_seconds=time.perf_counter() - started,
                status="complete" if len(records) == len(keys) else "incomplete")
    _atomic_json(out / "run_info.json", meta)
    print(json.dumps({k: meta[k] for k in ("finished", "elapsed_seconds", "status")}), flush=True)
    return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--keys-file", type=Path, help="Validation/smoke subset; omit for full census")
    parser.add_argument("--stop-after", type=int, help="Validation only: kill the run at this completed count")
    parser.add_argument("--prepare-smoke", action="store_true", help="Write populations and subset, without solving")
    args = parser.parse_args()
    if args.prepare_smoke:
        out = _inside(args.out)
        out.mkdir(parents=True, exist_ok=True)
        draws, keys = build_draws()
        write_draws(out / "draws.jsonl.gz", draws)
        _atomic_json(out / "smoke_keys.json", select_smoke(draws, keys))
        print(json.dumps({"draws": len(draws), "distinct_keys": len(keys), "smoke_keys": 300}))
    else:
        run(args.out, args.workers, args.keys_file, args.stop_after)


if __name__ == "__main__":
    main()
