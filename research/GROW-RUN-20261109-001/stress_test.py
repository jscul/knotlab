#!/usr/bin/env python3
"""Stress test for GROW-RUN-20261109-001, one size past each check of ticket A:
- Theorem 1 (rings not reached and band rings keep every binding; checked on 3 x 8, 4 x 6, 3 x 5) on 5 x 6 at g = 2 and 4 x 5 at g = 3,
  insertion lags 0 to 39, four splits;
- the census of every insertion lag (13 tubes to 6 x 3) on 4 x 5 and 5 x 4 at g = 2 and 3 x 3 at g = 5;
- the spread (3 x 8) on 3 x 10 at g = 2 and 3 x 8 at g = 3;
- repeated growth (four bands) with six bands, P = 6 and 10.
Writes stress_test.json beside this file."""
import collections
import copy
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/GROW-RUN-20261109-001A/GROW-RUN-20261109-001A-P001_a_band_inserted_while_running_keeps_only_the_knots_it_has_not_reached"))
import check as C  # noqa: E402

GR = C.GR
T0 = time.time()
out = {}

cnt = collections.Counter()
for n, m, g in ((5, 6, 2), (4, 5, 3)):
    for split in C.SPLITS:
        run = GR.Run(GR.Tube(n, list(range(m)), g))
        for t0 in range(40):
            r2 = copy.deepcopy(run)
            r2.insert_band(0, 0.5, split)
            st = GR.Run(GR.Tube(n, r2.tube.rows, g))
            for _ in range(t0):
                st.step()
            tb = r2.tube
            un = {R: GR.footprint(r2, R) == GR.footprint(st, R) for R in run.tube.rings}
            for k in C.contacts(r2):
                ff, T1, p = GR.binds_forever(r2, k)
                ra, pa, rb, pb, law = tb.contacts[tb.pos[k]]
                for j, R in enumerate((tb.rings[ra], tb.rings[rb])):
                    key = "band ring" if R not in un else ("not reached" if un[R] else "reached")
                    cnt[key + " / " + ("fails" if ff[j] is not None else "binds")] += 1
            run.step()
    print("theorem", dict(cnt), round(time.time() - T0), "s", flush=True)
out["Theorem 1 on 5 x 6 (g = 2) and 4 x 5 (g = 3)"] = dict(cnt)

C.CENSUS = ((4, 5, 2), (5, 4, 2), (3, 3, 5))
cen = C.census()
out["census"] = {k: {s: len(c) for s, c in v["clean insertion lags"].items()} | {"cycle": v["state preperiod"] + v["state period"],
                 "lower": v["clean insertion lags"]["lower"]} for k, v in cen.items()}
print("census", out["census"], round(time.time() - T0), "s", flush=True)


def spread(n, m, g, horizon):
    run = GR.Run(GR.Tube(n, list(range(m)), g))
    first = {}
    for t0 in range(horizon):
        r2 = copy.deepcopy(run)
        r2.insert_band(m // 2 - 1, m // 2 - 0.5, "lower")
        for k in C.contacts(r2):
            if GR.binds_forever(r2, k)[0] != [None, None]:
                first.setdefault(k[3], t0)
        run.step()
    return {str(k): v for k, v in sorted(first.items())}


out["spread 3 x 10, g = 2"] = spread(3, 10, 2, 30)
out["spread 3 x 8, g = 3"] = spread(3, 8, 3, 36)
print("spread", out["spread 3 x 10, g = 2"], out["spread 3 x 8, g = 3"], round(time.time() - T0), "s", flush=True)

rep = {}
for P in (6, 10):
    run = GR.Run(GR.Tube(3, [0, 1, 2], 2))
    born = {R: 0 for R in run.tube.rings}
    k = 0
    for t in range(1, 7 * P + 1):
        run.step()
        if t % P == 0 and t < 7 * P:
            k += 1
            run.insert_band(0, 0.5 ** k, "lower")
            for R in run.tube.rings:
                born.setdefault(R, t)
    kept = collections.defaultdict(lambda: [0, 0])
    for key in C.contacts(run):
        ff, T1, p = GR.binds_forever(run, key)
        ra, pa, rb, pb, law = run.tube.contacts[run.tube.pos[key]]
        for j, R in enumerate((run.tube.rings[ra], run.tube.rings[rb])):
            kept[born[R]][0] += ff[j] is None
            kept[born[R]][1] += 1
    rep["P = %d" % P] = {str(b): v for b, v in sorted(kept.items())}
out["six bands"] = rep
print("repeated", rep, round(time.time() - T0), "s", flush=True)

rows_ok = all(sorted(v for r, v in s.items() if float(r) < m / 2) for s, m in ((out["spread 3 x 10, g = 2"], 10), (out["spread 3 x 8, g = 3"], 8)))
out["pass"] = (out["Theorem 1 on 5 x 6 (g = 2) and 4 x 5 (g = 3)"].get("not reached / fails", 0) == 0
               and out["Theorem 1 on 5 x 6 (g = 2) and 4 x 5 (g = 3)"].get("band ring / fails", 0) == 0
               and all(v["lower"] and v["lower"][0] == 0 for v in out["census"].values())
               and all(v[str(6 * int(k.split()[-1]))] == [12, 12] for k, v in rep.items()))
out["seconds"] = round(time.time() - T0)
(HERE / "stress_test.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
print("PASS" if out["pass"] else "FAIL")
