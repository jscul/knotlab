"""Shared-runner job for the referee's check of SCALE-THEOREM-20261119-001 (own classification, own reading of the relayed complex,
own growth and relayed model; SCALE-SHARE's samples regenerated with its own sampler, scale.chain, run read-only only to regenerate
the study's data; SCALE-SHARE's and SCALE-THEOREM's per-sample records read from runs/scale-share and runs/scale-theorem as data;
no study reader imported or run).

For each of the 64 chains (n = 5, 6, 7, 8, 10, 12, 16, 20; seeds 0-7, 4-7 from a dense ring), every one of the 1,000 samples:
- integrity: the regenerated sample's shared count m and open places per knot against SCALE-SHARE's recorded features;
- the referee's class (DOUBLE-IDENT-R1's classify: stall, out (S3), out (S4), none, one loose, in) and, in the class (in, one
  loose, none, as dims.py and scalelib read it), its growth class from the referee's X+ (DOUBLE-IDENT-R1's build and predict) and
  the dimension-two mechanism (relay: a finished piece among two or more; two chains: a tree core with two rays);
- compared with SCALE-THEOREM's recorded theorem class and prediction, and with SCALE-SHARE's recorded cluster-rule class;
- regrowth (the referee's own sample, all chains): every in-class grower with crc32(n-seed-i) % 8 == 0, every exponential and
  every grower of dimension three or more: the referee's growth (FIRST-KNOT-R1 engine, the program's rule) against its relayed
  model (RELAY-IDENT-R1's relayed_keys), keys (parents, fresh, the parents' keys) per round to 6; every one-loose and loose-free
  start in the class: whether the growth closes at round 1; every exponential: counts to round 12.

  .venv/bin/python -B scripts/longrun.py launch research/SCALE-THEOREM-20261119-001/referee-R1/job_scale.py \\
      --out runs/referee-scale-theorem --unit referee-scale-theorem --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import importlib.util
import itertools
import json
import sys
import zlib
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/DOUBLE-IDENT-20261119-001/referee-R1", "research/RELAY-IDENT-20261119-001/referee-R1",
          "research/CHAIN-IDENT-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
SAMPLER = ROOT / "experiments/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/scale.py"
SIZES = (5, 6, 7, 8, 10, 12, 16, 20)
T = 6


def sampler():
    spec = importlib.util.spec_from_file_location("ss_scale_data", SAMPLER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.chain           # used only to regenerate the study's samples


def records(run, case):
    for line in open(ROOT / run / "results.jsonl"):
        r = json.loads(line)
        if r["case"] == case:
            return r["result"]["samples"]
    raise KeyError(case)


def mechanism(X):
    pieces = [c for c in X["comps"].values() if c["knots"]]
    kinds = set()
    for c in pieces:
        pts = c["points"] | c["knots"]
        cyc = c["inc"] - (len(pts) + c["blocks"]) + 1
        if cyc == 0 and c["rays"] == 0 and len(pieces) >= 2:
            kinds.add("relay")
        if cyc == 0 and c["rays"] == 2:
            kinds.add("two chains")
    return " and ".join(sorted(kinds))


PARAMS = {}


def setup(params):
    PARAMS.update(params)


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    for n in SIZES:
        for seed in range(8):
            cid = f"S-n{n:02d}-c{seed}"
            if only is None or cid in only:
                yield cid, {"n": n, "seed": seed}


def run(case_id, p):
    import job_double as JD
    import job_relay as RL
    n, seed = p["n"], p["seed"]
    samp = sampler()(n, 1000, seed, dense=seed >= 4)
    ss = records("runs/scale-share", case_id)
    st = records("runs/scale-theorem", case_id)
    rows, regrown, closing, expo = [], [], [], []
    for i, (sizes, M) in enumerate(samp):
        flat = [M[a][b] for a, b in itertools.combinations(range(n), 2)]
        m = sum(flat)
        opk = (sum(sizes) - 2 * m) / n
        integ = m == ss[i]["m"] and abs(opk - ss[i]["open_per_knot"]) < 1e-9
        c = JD.classify(sizes, flat)
        D, mech = None, None
        if c in ("in", "one loose", "none"):
            X = JD.build(sizes, flat, 2)
            D = JD.predict(X)
            if D == 2:
                mech = mechanism(X)
        rows.append([i, c, None if D is None else str(D), mech, st[i]["theorem"], st[i].get("predicted"), st[i].get("why"),
                     ss[i]["class"], integ, ss[i]["weight"], opk])
        if c in ("one loose", "none"):
            a, counts = RL.grow_keys(n, JD.data(sizes, flat)[1], list(sizes), 2)
            closing.append([i, c, counts])
            continue
        if D is None or D == 0:
            continue
        pick = zlib.crc32(f"{n}-{seed}-{i}".encode()) % 8 == 0 or D == "exp" or (isinstance(D, int) and D >= 3)
        if pick:
            X = JD.build(sizes, flat, T + 3)
            a, counts = RL.grow_keys(n, X["edges"], list(sizes), T)
            b = RL.relayed_keys(n, X, T + 1)
            bad = [t for t in range(T + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} !=
                   {k: v for k, v in b.get(t, {}).items() if v}]
            regrown.append([i, str(D), not bad, bad, counts])
        if D == "exp":
            a, counts = RL.grow_keys(n, JD.data(sizes, flat)[1], list(sizes), 12, maxj=200000)
            expo.append([i, counts, sizes, flat])
    return {"rows": rows, "regrown": regrown, "one loose or none": closing, "exponential": expo}
