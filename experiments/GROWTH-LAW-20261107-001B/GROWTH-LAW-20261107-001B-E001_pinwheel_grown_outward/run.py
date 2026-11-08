"""GROWTH-LAW-20261107-001B-E001: the pinwheel grown outward by its own collar law (exploratory; see contract.json).

    python3 -B run.py            run every declared job with 20 workers
Writes artifacts/GROWTH-LAW-20261107-001B/GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward/run/rows.jsonl (one row per job,
as each finishes) and result.json (the summary)."""
from __future__ import annotations

import json
import multiprocessing as mp
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import growth_engine as E  # noqa: E402
import legality as L  # noqa: E402

OUT = ROOT / "artifacts" / "GROWTH-LAW-20261107-001B" / "GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward" / "run"
SIZE = 500
W = {}


def init():
    keys, complete, by_h = E.law()
    W["keys"], W["by_h"] = keys, by_h
    W["climber"] = L.Climber(keys)


def legality(P):
    tiles = list(P.tiles)
    tested, bad = L.atlas_check(tiles)
    if P.is_complete(0):
        found, level, tried = W["climber"].embed(tiles, (P.handed(0), P.collar(0)))
    else:
        found, level, tried = None, None, None
    return {"atlas_darts": tested, "atlas_bad": bad, "embeds": found, "embed_level": level, "chains_tried": tried}


def job(spec):
    t0 = time.time()
    kind, order, seed = spec
    rng = random.Random(seed)
    if kind == "replay":
        if "genuine" not in W:
            W["genuine"] = E.Genuine(7)
        G = W["genuine"]
        try:
            P, rec = E.grow(W["by_h"], order, rng, SIZE, replay=G.replay, check_cache=(order == "bfs"))
        except AssertionError as e:
            return {"kind": kind, "order": order, "seed": seed, "outcome": "left the genuine patch", "error": str(e),
                    "seconds": round(time.time() - t0, 1)}
    else:
        P, rec = E.grow(W["by_h"], order, rng, SIZE)
    row = {"kind": kind, "seed": seed, **{k: v for k, v in rec.items() if k != "options"},
           "options": dict(sorted(Counter(rec["options"]).items()))}
    row.update(legality(P))
    row["seconds"] = round(time.time() - t0, 1)
    return row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("grow", "forced", s) for s in range(1, 11)]
    jobs += [("replay", o, 0) for o in ("bfs", "random", "finger")]
    jobs += [("grow", o, s) for o in ("bfs", "random", "finger") for s in range(1, 21)]
    t0 = time.time()
    rows = []
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(20, initializer=init) as pool:
        for row in pool.imap_unordered(job, jobs):
            rows.append(row)
            fh.write(json.dumps(row, default=str) + "\n")
            fh.flush()
            print(json.dumps({k: row.get(k) for k in ("kind", "order", "seed", "outcome", "tiles", "moves", "forced", "choices",
                                                      "complete_radius", "atlas_bad", "embeds", "seconds")}), flush=True)
    summary = {}
    for kind in ("replay", "grow"):
        for order in ("bfs", "random", "finger", "forced"):
            rs = [r for r in rows if r["kind"] == kind and r["order"] == order]
            if not rs:
                continue
            summary[f"{kind} {order}"] = {
                "runs": len(rs),
                "outcomes": dict(Counter(r["outcome"] for r in rs)),
                "dead-end sizes": sorted(r["tiles"] for r in rs if r["outcome"] == "dead end"),
                "moves": sum(r.get("moves", 0) for r in rs),
                "forced": sum(r.get("forced", 0) for r in rs),
                "choices": sum(r.get("choices", 0) for r in rs),
                "complete radius": sorted(r.get("complete_radius") for r in rs if r.get("complete_radius") is not None),
                "atlas bad darts": sorted(r.get("atlas_bad") for r in rs if r.get("atlas_bad") is not None),
                "embeds": dict(Counter(str(r.get("embeds")) for r in rs)),
            }
    res = {"experiment": "GROWTH-LAW-20261107-001B-E001", "size": SIZE, "summary": summary, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
