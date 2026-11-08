#!/usr/bin/env python3
"""Independent checks of the families that compose at recurring lags with every contact persistent at every size
(RECUR-PATH-20261108-001A-E002), and what they look like. 16 worker processes, several minutes.

    .venv/bin/python3 -B research/RECUR-PATH-20261108-001/verify_recurring.py   writes verify_recurring.json
- Row sequences, independently: path_lib.analyze (NATIVE-PATH-20261108-001A, uncapped) for persistence of every contact, and the
  last contact's own row orbit for composition at some phase of its cycle, at every size of each family's schedule.
- Full state spaces: every family at the two smallest sizes of its schedule (paths of 13 and 17 bits), by E002's full-state-space
  reading (PL.mixed_state_map and PROCESS-CHAIN-20261108-001A's blockwise decisiveness test); and eight families at the third size
  (21 bits).
- What they are: rules, laws, the share of the last contact's cycle at which it composes, and its period, by size."""
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E2 = ROOT / "experiments/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed"
FAMS = ROOT / "artifacts/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed/run/families.json"
sys.path.insert(0, str(E2))
spec = importlib.util.spec_from_file_location("recur_run", E2 / "run.py")
RUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUN)
R, G, PL = RUN.R, RUN.G, RUN.PL
W = PL.W


def decisive(rows):
    """families whose every size after the first meets "recurring, persistent", the first size included via E002's result"""
    out = []
    for p in rows:
        schedule, rules, laws, v, by = p
        sizes = list(G.SIZES[schedule])
        if all(str(s) in by and by[str(s)][1] is True for s in sizes):
            out.append(p)
    return out


def independent(p):
    schedule, rules, laws, v, by = p
    res = {}
    for s in G.SIZES[schedule]:
        r, sz, ks, lw = G.path(schedule, s, tuple(rules), tuple(tuple(l) for l in laws), tuple(v))
        a = PL.analyze(r, sz, ks, lw)
        rows, N, blocks = PL.linear_matrix(r, sz, ks, lw)
        m = [PL.mask(blocks, f"R{i}") for i in range(len(sz))]
        seq, T1, per = W.row_orbit(rows, 1 << (len(sz) - 2))
        cyc = seq[T1 - 1:T1 + per - 1]
        share = sum(1 for x in cyc if x & m[0] and x & m[-1]) / per
        res[s] = {"persist": a["all persist"], "share": share, "period": per, "recurring, persistent": a["all persist"] and share > 0}
    return res


def full(args):
    p, s = args
    schedule, rules, laws, v, by = p
    path = G.path(schedule, s, tuple(rules), tuple(tuple(l) for l in laws), tuple(v))
    return RUN.brute(*path)


def main():
    t0 = time.time()
    rows = json.loads(FAMS.read_text())["rows"]
    result = json.loads((FAMS.parent / "result.json").read_text())
    dec = [p for p in rows if p[0] in ("two apart", "longer")]
    # the first size of a schedule is stored in E002's profiles too (run.py adds it before writing)
    dec = decisive(dec)
    with Pool(16) as pool:
        ind = pool.map(independent, dec, chunksize=2)
        small = [(p, s) for p in dec for s in list(G.SIZES[p[0]])[:2]]
        fs = pool.map(full, small, chunksize=1)
        third = [(p, list(G.SIZES[p[0]])[2]) for p in (dec[:4] + [x for x in dec if x[0] == "longer"][:4])]
        ft = pool.map(full, third, chunksize=1)
    agree_ind = sum(1 for d in ind if all(v["recurring, persistent"] for v in d.values()))
    agree_full = sum(1 for b in fs if b is not None and b[1] is True)
    undecided_full = sum(1 for b in fs if b is None)
    shares, periods = defaultdict(list), defaultdict(list)
    for p, d in zip(dec, ind):
        for s, v in d.items():
            shares[(p[0], s)].append(v["share"])
            periods[(p[0], s)].append(v["period"])
    out = {
        "decisive families (recurring, persistent at every size)": {k: sum(1 for p in dec if p[0] == k) for k in ("two apart", "longer")},
        "independent row sequences agree at every size": agree_ind,
        "full state spaces at the two smallest sizes: agree / paths / undecided": [agree_full, len(fs), undecided_full],
        "full state spaces at the third size (eight families): readings": [[p[0], p[1], s, b] for (p, s), b in zip(third, ft)],
        "rules (schedule, rules: families)": [[k[0], list(k[1]), v] for k, v in Counter((p[0], tuple(p[1])) for p in dec).most_common()],
        "laws (schedule, laws: families)": [[k[0], [list(l) for l in k[1]], v] for k, v in Counter((p[0], tuple(tuple(l) for l in p[2])) for p in dec).most_common(12)],
        "share of the last contact's cycle at which it composes (schedule size: min, mean, max)": {
            f"{k[0]} {k[1]}": [round(min(v), 4), round(sum(v) / len(v), 4), round(max(v), 4)] for k, v in sorted(shares.items())},
        "the last contact's period (schedule size: min, max)": {f"{k[0]} {k[1]}": [min(v), max(v)] for k, v in sorted(periods.items())},
        "E002 control passes": result.get("control passes"),
        "seconds": round(time.time() - t0, 1)}
    (HERE / "verify_recurring.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
