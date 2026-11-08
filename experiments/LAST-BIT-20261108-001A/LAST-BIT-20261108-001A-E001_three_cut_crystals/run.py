"""LAST-BIT-20261108-001A-E001: crystals legal only after three cuts against the last one-bit decoration (exploratory; contract.json).

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py
Writes artifacts/LAST-BIT-20261108-001A/LAST-BIT-20261108-001A-E001_three_cut_crystals/run/{filter.json, rows.jsonl, result.json}."""
from __future__ import annotations

import importlib.util
import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/LAST-BIT-20261108-001A/LAST-BIT-20261108-001A-E001_three_cut_crystals/run"
spec = importlib.util.spec_from_file_location("one_bit_b_run", ROOT / "experiments/ONE-BIT-20261108-001B/ONE-BIT-20261108-001B-E001_escaping_crystals/run.py")
OB = importlib.util.module_from_spec(spec)
sys.modules["one_bit_b_run"] = OB
spec.loader.exec_module(OB)
D, A, AB = OB.D, OB.A, OB.AB
SIG = ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0))
CONTROL = ((1, 0, 0, 0, 1), (0, 1, 1, 0, 0))
W = OB.W


def class_of(typ):
    """1 in L1; 2 if all children's collars are in L1; 3 if all are of class 1 or 2; else 0"""
    h, tiles = typ
    if frozenset(tiles) in W["L1"]:
        return 1
    try:
        kids = [t for t, _ in D.images(h, list(tiles))]
    except Exception:
        return 0
    cls = []
    for t in kids:
        if frozenset(t[1]) in W["L1"]:
            cls.append(1)
            continue
        try:
            grand = [g for g, _ in D.images(t[0], list(t[1]))]
        except Exception:
            return 0
        cls.append(2 if all(frozenset(g[1]) in W["L1"] for g in grand) else 0)
    if 0 in cls:
        return 0
    return 2 if all(c == 1 for c in cls) else 3


def label_job(job):
    pi, sig, ks = job
    spec_, j, P = W["planes"][pi]
    allowed = D.law(W["sk"], sig)
    tori = [L for m in (1, 2) for L in D.sublattices(m)]
    for k in ks:
        for L in tori:
            ok, _ = D.periodic(P, allowed, k, L, want_model=True)
            if ok:
                return {"plane": [spec_[0], spec_[1], [list(d) for d in spec_[2]], list(spec_[3])], "first legal cut": j,
                        "sig": [list(sig[0]), list(sig[1])], "admitted at": [k, list(L)]}
    return {"plane": [spec_[0], spec_[1], [list(d) for d in spec_[2]], list(spec_[3])], "first legal cut": j,
            "sig": [list(sig[0]), list(sig[1])], "admitted at": None}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    OB.init()
    specs = [(m, n, tuple(map(tuple, doms)), tuple(diags)) for m, n in OB.TORI for doms in AB.torus_dominoes(m, n)
             for diags in itertools.product((0, 1), repeat=len(doms))]
    with mp.Pool(16, initializer=OB.init) as pool:
        results = pool.map(OB.filter_job, specs, chunksize=64)
    types = sorted({t for _, cols in results for t in cols}, key=lambda t: (t[0], t[1]))
    with mp.Pool(16, initializer=OB.init) as pool:
        cls = dict(zip(types, pool.map(class_of, types, chunksize=8)))
    counts = defaultdict(int)
    kept, seen2 = {}, set()
    for spec_, cols in results:
        c = [cls[t] for t in cols]
        if 0 in c:
            continue
        j = max(c)
        counts[(spec_[0], spec_[1], j)] += 1
        sig = tuple(sorted(cols))
        if j <= 2:
            seen2.add(sig)
        elif sig not in kept:
            kept[sig] = (spec_, j)
    kept = {s: v for s, v in kept.items() if s not in seen2}
    filt = {"planes": len(specs), "collar types": len(types),
            "types by class": {str(k): sum(1 for v in cls.values() if v == k) for k in (0, 1, 2, 3)},
            "legal planes by torus and first legal cut": {f"{m}x{n} j={j}": v for (m, n, j), v in sorted(counts.items())},
            "distinct planes legal only after three cuts": len(kept), "seconds": round(time.time() - t0, 1)}
    (OUT / "filter.json").write_text(json.dumps(filt, indent=1) + "\n")
    print(json.dumps(filt), flush=True)
    by_j = defaultdict(int)
    for (m, n, j), v in counts.items():
        by_j[j] += v
    ctl = {"classes 1 and 2 reproduce ONE-BIT-20261108-001B's 32 and 176 planes": by_j[1] == 32 and by_j[2] == 176,
           "the plain rectangle lattice gets class 0": any(0 in [cls[t] for t in cols] for s2, cols in results
                                                           if s2 == (2, 2, (("h", 0, 0), ("h", 0, 1)), (0, 0)))}
    sk = D.Skeleton()
    W["sk"] = sk
    planes = []
    for sig_, (spec_, j) in kept.items():
        m, n, doms, diags = spec_
        cell = []
        for (kind, i, jj), d in zip(doms, diags):
            cell += AB.rect_h(i, jj, d) if kind == "h" else AB.rect_v(i, jj, d)
        planes.append((spec_, j, D.Plane(sk, cell, ((m, 0), (0, n)))))
    # the positive control: ONE-BIT-20261108-001B's mixed plane, which admits 10001 / 01100 after two cuts
    mixed = (4, 4, (("h", 0, 0), ("v", 2, 0), ("v", 3, 3), ("h", 3, 1), ("v", 1, 1), ("v", 0, 2), ("h", 2, 2), ("h", 1, 3)),
             (0, 1, 1, 0, 1, 1, 0, 0))
    cell = []
    for (kind, i, jj), d in zip(mixed[2], mixed[3]):
        cell += AB.rect_h(i, jj, d) if kind == "h" else AB.rect_v(i, jj, d)
    planes.append((mixed, 2, D.Plane(sk, cell, ((4, 0), (0, 4)))))
    W["planes"] = planes
    for _, j, P in planes:
        for k in range(6):
            for sp in P.descendants(k):
                P.tile(*sp)
    jobs = [(pi, SIG, (3, 4, 5)) for pi in range(len(planes) - 1)] + [(len(planes) - 1, CONTROL, (2, 3))]
    rows = []
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(16) as pool:
        for row in pool.imap_unordered(label_job, jobs):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    ctrl_row = [r for r in rows if r["sig"] == [list(CONTROL[0]), list(CONTROL[1])]]
    ctl["the control decoration is admitted by the mixed plane"] = bool(ctrl_row and ctrl_row[0]["admitted at"])
    admitted = [r for r in rows if r["sig"] == [list(SIG[0]), list(SIG[1])] and r["admitted at"]]
    res = {"experiment": "LAST-BIT-20261108-001A-E001", "filter": filt, "controls": ctl,
           "planes tested with the decoration": len(planes) - 1, "admitted": admitted, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
