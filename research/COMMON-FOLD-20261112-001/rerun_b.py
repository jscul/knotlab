"""Ticket B's frozen census, rerun with each run written as it finishes and a cap per run (a disclosed deviation).

The registered run of COMMON-FOLD-20261112-001B-E001 (unit cf-b-1794467859) finished the tree control, U(100) and U(200) in under
5 minutes, then ran its 20 U(400) runs for 2 hours without finishing one (each forced set at the last base needs hundreds of SAT
calls on a base at the edge of contradiction, where single calls are slow); it writes only at the end, so it was stopped and nothing
was kept. This rerun imports the frozen census.py unchanged (same seeds, sets, readings) and runs each (process, n, run) in its own
process, writing it to rows.jsonl when done; a run still going after CAP seconds is stopped and recorded as dropped. The summary is
computed as the frozen code does, over the runs kept, leaving out the per-distance profile, which the frozen summary would
have tried to add up as a number (a bug that would have stopped it after its runs).

    .venv/bin/python -B research/COMMON-FOLD-20261112-001/rerun_b.py [--workers 6] [--cap 1800] [--summary-only]
Output: artifacts/COMMON-FOLD-20261112-001B/COMMON-FOLD-20261112-001B-E001_finite_influence/rerun/{rows.jsonl,summary.json,log.txt}
"""
from __future__ import annotations

import importlib.util
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
spec = importlib.util.spec_from_file_location("census", os.path.join(
    ROOT, "experiments/COMMON-FOLD-20261112-001B/COMMON-FOLD-20261112-001B-E001_finite_influence/census.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
OUT = os.path.join(C.OUT, "rerun")


def run_one(item, q):
    q.put(C.job(item))


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 1800
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    items = [("T", 0, r) for r in range(C.RUNS)] + [("U", n, r) for n in C.NS for r in range(C.RUNS)]
    pending, live, rows, dropped = list(items), [], [], []
    if "--summary-only" in sys.argv:
        # the summary of a finished rerun from rows.jsonl (the unit's time limit stopped the first one before it was written)
        rows = [json.loads(line) for line in open(os.path.join(OUT, "rows.jsonl"))]
        kept = {(r["process"], r["n"], r["run"]) for r in rows}
        dropped = [list(i) for i in items if i not in kept]
        pending = []
    else:
        with open(os.path.join(OUT, "rows.jsonl"), "w"):
            pass
    while pending or live:
        while pending and len(live) < workers:
            item = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=run_one, args=(item, q))
            p.start()
            live.append((item, p, q, time.time()))
        time.sleep(1)
        for entry in list(live):
            item, p, q, start = entry
            if not q.empty():
                row = q.get()
                p.join()
                rows.append(row)
                with open(os.path.join(OUT, "rows.jsonl"), "a") as f:
                    f.write(json.dumps(row) + "\n")
                live.remove(entry)
                log("done", item, round(time.time() - start, 1), "s")
            elif time.time() - start > cap:
                p.terminate()
                p.join()
                dropped.append(list(item))
                live.remove(entry)
                log("dropped at the cap", item)
    summ = {"cap seconds": cap, "dropped": dropped, "kept": len(rows)}
    for proc, n in [("T", 0)] + [("U", n) for n in C.NS]:
        rr = [r for r in rows if r["process"] == proc and r["n"] == n]
        if not rr:
            continue
        for st in (("half", "horizon") if proc == "T" else ("half", "three quarters", "last base")):
            for lab in ("pair", "knot"):
                vals = [r[st][lab] for r in rr]
                summ[f"{proc}{n or ''} {st} {lab}"] = {"runs": len(vals), **{q: round(sum(v[q] for v in vals) / len(vals), 4) for q in vals[0]
                                                                   if q.endswith("mean") and q != "profile mean"}}
    tr = [r for r in rows if r["process"] == "T"]
    summ["checks"] = {"T: a knot's pattern forces nothing (largest forced fraction)": max(r[st]["knot"]["forced max"] for r in tr for st in ("half", "horizon")),
                      "T: largest pair reach": max(r[st]["pair"]["reach max"] for r in tr for st in ("half", "horizon"))}
    json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    log("summary", json.dumps(summ)[:4000])
    log("finished", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
