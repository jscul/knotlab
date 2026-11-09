"""RING-RUN-20261109-001A-E001: what survives a ring inserted while the twist tube runs (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/RING-RUN-20261109-001A/RING-RUN-20261109-001A-E001_running_insertion/run/result.json

For each twist tube (N rings, g), the run's state from lag 0 is eventually periodic; inserting a ring at lag t0 depends only on the state
at t0, so reading every t0 below the state's preperiod plus its period reads every insertion lag. After the insertion the network is the
next stage, fixed, and a contact's binding of each of its rings at every later lag is read exactly through the orbit of its row
(growrun_lib.binds_forever). An old ring is not reached when its footprint at t0 equals its footprint in the next stage run from lag 0
(GROW-RUN-20261109-001A)."""
import collections
import copy
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import twist_lib as TL  # noqa: E402

GR = TL.GR
OUT = ROOT / "artifacts" / "RING-RUN-20261109-001A" / "RING-RUN-20261109-001A-E001_running_insertion" / "run"
ROSTER = [(N, 2) for N in range(4, 13)] + [(N, g) for g in (3, 4) for N in range(4, 9)]
SPLITS = ("keep", "fresh")
LAG_CAP = 64   # amended before launch (contract.json, "amendment")


def contacts(run):
    return [k for k in run.tube.keys if k[0] == 'c']


def state_cycle(N, g):
    run = TL.Run(TL.TwistTube(list(range(N)), g))
    seen, T = {}, 0
    while True:
        key = tuple(run.state)
        if key in seen:
            return seen[key], T - seen[key]
        seen[key] = T
        run.step()
        T += 1


def tube_task(args):
    N, g = args
    pre, per = state_cycle(N, g)
    out = {"N": N, "g": g, "state preperiod": pre, "state period": per, "splits": {}}
    lags = min(pre + per, LAG_CAP)
    out["lags read"] = lags
    out["every lag read"] = lags == pre + per
    for split in SPLITS:
        run = TL.Run(TL.TwistTube(list(range(N)), g))
        st = None
        clean, cnt = [], collections.Counter()
        for t0 in range(lags):
            r2 = copy.deepcopy(run)
            r2.insert_ring(0, 0.5, split)
            if st is None:
                st = TL.Run(TL.TwistTube(r2.tube.labels, g))   # the next stage, run from lag 0 alongside
            tb = r2.tube
            reached = {R: GR.footprint(r2, R) != GR.footprint(st, R) for R in run.tube.rings}
            every = True
            for k in contacts(r2):
                ff, T1, p = GR.binds_forever(r2, k)
                ra, pa, rb, pb, law = tb.contacts[tb.pos[k]]
                for j, R in enumerate((tb.rings[ra], tb.rings[rb])):
                    kind = "new ring" if R not in reached else ("reached" if reached[R] else "not reached")
                    fails = ff[j] is not None
                    cnt[(kind, "fails" if fails else "binds")] += 1
                    every &= not fails
            if every:
                clean.append(t0)
            run.step()
            st.step()
        out["splits"][split] = {"clean insertion lags": clean, "bindings": {" / ".join(k): v for k, v in sorted(cnt.items())}}
    return out


def main():
    t0 = time.time()
    with Pool(16) as pool:
        rows = pool.map(tube_task, ROSTER, chunksize=1)
    tot = {s: collections.Counter() for s in SPLITS}
    for r in rows:
        for s in SPLITS:
            tot[s].update(r["splits"][s]["bindings"])
    summary = {}
    for s in SPLITS:
        c = tot[s]
        reached = c.get("reached / fails", 0) + c.get("reached / binds", 0)
        summary[s] = {
            "H1 lag 0 clean on every tube": all(0 in r["splits"][s]["clean insertion lags"] for r in rows),
            "H2 failures of rings not reached or of the new ring": c.get("not reached / fails", 0) + c.get("new ring / fails", 0),
            "H3 share of reached bindings that fail": round(c.get("reached / fails", 0) / reached, 4) if reached else None,
            "clean lags": sum(len(r["splits"][s]["clean insertion lags"]) for r in rows),
            "lags read": sum(r["lags read"] for r in rows),
            "tubes with every lag read": sum(1 for r in rows if r["every lag read"]),
            "bindings": dict(c)}
    res = {"experiment": "RING-RUN-20261109-001A-E001", "rows": rows, "summary": summary, "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
