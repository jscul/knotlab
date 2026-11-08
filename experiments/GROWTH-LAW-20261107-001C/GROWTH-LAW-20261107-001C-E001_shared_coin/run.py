"""GROWTH-LAW-20261107-001C-E001: the pinwheel's growth needs a shared coin (exploratory; see contract.json).

    python3 -B run.py            run every declared job with 20 workers
Writes artifacts/GROWTH-LAW-20261107-001C/GROWTH-LAW-20261107-001C-E001_shared_coin/run/rows.jsonl (one row per job, as each
finishes) and result.json (the summary)."""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import shared_coin as S  # noqa: E402

E, L = S.E, S.L
OUT = ROOT / "artifacts" / "GROWTH-LAW-20261107-001C" / "GROWTH-LAW-20261107-001C-E001_shared_coin" / "run"
B_ROWS = ROOT / "artifacts" / "GROWTH-LAW-20261107-001B" / "GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward" / "run" / "rows.jsonl"
W = {}


def init():
    keys, complete, by_h = E.law()
    W["by_h"] = by_h
    W["climber"] = L.Climber(keys)


def job(spec):
    t0 = time.time()
    kind, order, seed, size = spec
    if kind == "trace":
        row = S.trace_run(W["by_h"], order, seed, size, W["climber"])
    elif kind == "strong":
        row = S.strong_run(W["by_h"], order, seed, size, W["climber"])
    elif kind == "strong replay":
        row = S.strong_replay(W["by_h"], size)
    else:
        row = S.oracle_run(W["by_h"], order, seed, size, W["climber"])
    row["kind"] = kind
    row["seconds"] = round(time.time() - t0, 1)
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    b_rows = [json.loads(line) for line in B_ROWS.read_text().splitlines()]
    b_coin = {(r["order"], r["seed"]): r for r in b_rows if r["kind"] == "grow"}
    jobs = [("strong replay", "bfs", 0, 500)]
    jobs += [("oracle", "bfs", s, 1000) for s in range(1, 11)]
    jobs += [("oracle", "random", s, 1000) for s in range(1, 6)]
    jobs += [("strong", o, s, 500) for o in ("bfs", "random") for s in range(1, 21)]
    jobs += [("trace", o, s, 500) for (o, s) in sorted(b_coin)]
    t0 = time.time()
    rows = []
    if "--summarize" in sys.argv:            # rebuild the summary from the rows already written, running no job
        rows = [json.loads(line) for line in (OUT / "rows.jsonl").read_text().splitlines()]
        return summarize(rows, b_coin, t0)
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(20, initializer=init) as pool:
        for row in pool.imap_unordered(job, jobs):
            rows.append(row)
            fh.write(json.dumps(row, default=str) + "\n")
            fh.flush()
            print(json.dumps({k: row.get(k) for k in ("kind", "order", "seed", "outcome", "tiles", "moves", "choices",
                                                      "first_illegal_move", "first_illegal_forced", "first_illegal_option_legality",
                                                      "bits_all_options", "bits_legal_options", "final_legal", "seconds")},
                             default=str), flush=True)
    return summarize(rows, b_coin, t0)


def summarize(rows, b_coin, t0):
    traces = [r for r in rows if r["kind"] == "trace"]
    reproduced = sum(1 for r in traces if (b := b_coin[(r["order"], r["seed"])]) and
                     (b["outcome"], b["tiles"], b["moves"]) == (r["outcome"], r["tiles"], r["moves"]))
    first = [r for r in traces if "first_illegal_move" in r]
    opts = [r["first_illegal_option_legality"] for r in first if "first_illegal_option_legality" in r]
    oracles = [r for r in rows if r["kind"] == "oracle"]
    strong = [r for r in rows if r["kind"] == "strong"]
    summary = {
        "traces": len(traces),
        "traces reproducing ticket B's run": reproduced,
        "traces with a first illegal move": len(first),
        "first illegal move was a forced move": sum(1 for r in first if r["first_illegal_forced"]),
        "first illegal move index (moves)": sorted(r["first_illegal_move"] for r in first),
        "moves from the first illegal move to the end": sorted(r["moves_from_first_illegal_to_end"] for r in first),
        "tile distance from the first illegal move to the dead tile": sorted(r["distance_to_dead_tile"] for r in first
                                                                            if r.get("distance_to_dead_tile") is not None),
        "options at the first illegal move (legal/all)": dict(Counter(f"{sum(o)}/{len(o)}" for o in opts)),
        "stronger-law replay control": [r for r in rows if r["kind"] == "strong replay"],
        "stronger law runs": len(strong),
        "stronger law outcomes by order": {o: dict(Counter(r["outcome"] for r in strong if r["order"] == o)) for o in ("bfs", "random")},
        "stronger law dead-end sizes": sorted(r["tiles"] for r in strong if r["outcome"] == "dead end"),
        "stronger law final patches legal": dict(Counter(str(r["final_legal"]) for r in strong)),
        "oracle runs": len(oracles),
        "oracle outcomes": dict(Counter(r["outcome"] for r in oracles)),
        "oracle final patches legal": dict(Counter(str(r["final_legal"]) for r in oracles)),
        "oracle choices: legal/all options": dict(Counter(f"{g}/{a}" for r in oracles for _, a, g in r["choices_log"])),
        "oracle bits [order, seed, tiles, choices, bits of all options, bits of legal options]":
            [[r["order"], r["seed"], r["tiles"], r["choices"], r["bits_all_options"], r["bits_legal_options"]] for r in oracles],
    }
    res = {"experiment": "GROWTH-LAW-20261107-001C-E001", "summary": summary, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
