"""Stress test for RESCUE-MAP-20261109-001, one size past the checks of RESCUE-MAP-20261109-001A: the census of every lattice to index
100 (square), 140 (triangular) and 80 (honeycomb), against the checked 50, 93 and 48: no on-time torus outside the families and the
listed ones, and every family torus on time; and the tube certificates on a window of 300 positions (checked on 160).
Output: stress_test.json beside this script."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/RESCUE-MAP-20261109-001A/RESCUE-MAP-20261109-001A-P001_short_loops_rescue"))
import check as K  # noqa: E402

R, C = K.R, K.C
PAST = {"square": (51, 100), "triangular": (94, 140), "honeycomb": (49, 80)}


def main():
    t0 = time.time()
    out = {}
    with Pool(20) as pool:
        for kind, (lo, hi) in PAST.items():
            jobs = [(kind, B) for N in range(lo, hi + 1) for B in K.hnf_lattices(N)]
            res = pool.map(K.on_time, jobs, chunksize=8)
            fam = lambda B: any(K.contains(B, v) for v in K.FAMILY[kind])
            out[kind] = {"indices": [lo, hi], "lattices": len(jobs),
                         "on time outside the families": [list(map(list, r[1])) for r in res if r[2] and not fam(r[1])],
                         "family tori late": [list(map(list, r[1])) for r in res if r[2] is False and fam(r[1])],
                         "family tori on time": sum(1 for r in res if r[2] and fam(r[1]))}
    certs = {}
    for kind, v in K.TUBES:
        for t0_ in range(R.TYPES[kind]):
            c = C.certificate(kind, v, t0_, W=300, radius=1300)
            q = C.quotient_conditions(c)
            certs["%s %s target %d" % (kind, v, t0_)] = not c["bad"] and c["agree"] and q["Q2"] and q["Q3"] and q["grow right"] and q["grow left"]
    out["tube certificates, window 300"] = certs
    out["pass"] = all(not x["on time outside the families"] and not x["family tori late"] for k, x in out.items() if k in PAST) and all(certs.values())
    out["elapsed_seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: (v if not isinstance(v, dict) or "lattices" not in v else {a: b for a, b in v.items() if a != "x"}) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
