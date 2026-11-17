"""Read-out for WEAVE-LAWS-20261117-001B-E001 (frozen before running).

R1 census: for each law, every relation its knots allow on n = 4 and 5 labelled distinctions (n = 6 where the closure stays
under two million relations), and the number of distinct (N, single counts, pair counts) keys.
R2 the weave: for each law, the row transfer spectrum at widths 3 to 12 (dense eigenvalues to 9, sparse Arnoldi at 10 to 12):
lambda_0, its multiplicity, the gap log_3(lambda_0/|lambda_1|), gap x width, and lambda_0^(1/width) (states per site); and the
connected correlation along the transfer axis at width 12, r = 1..14, with its decay rate from r = 6 to 12 (log base 3 per row).

    .venv/bin/python -B run.py      (writes artifacts/.../results.json)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import lawlib as W  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "WEAVE-LAWS-20261117-001B", "WEAVE-LAWS-20261117-001B-E001_gaps")
CENSUS = {"NAE": False, "OR": False, "not-exactly-two": False, "parity": False, "distance-two, any order": True}


def census():
    out = {}
    for name, all_orders in CENSUS.items():
        excl = W.LAWS["distance-two, place 1 odd"][0] if name.startswith("distance-two") else W.LAWS[name][0]
        out[name] = {}
        for n in (4, 5, 6):
            t = time.time()
            rels = W.relations(n, W.law_knots(n, excl, all_orders), cap=2_000_000)
            if rels is None:
                out[name][n] = "over two million relations; skipped"
                continue
            keys = {}
            for r in rels:
                keys.setdefault(W.pair_key(n, r), []).append(r)
            coll = [v for v in keys.values() if len(v) > 1]
            ex = None
            if coll:
                small = min(coll, key=lambda v: max(bin(r).count("1") for r in v))[:2]
                ex = [[s for s in range(1 << n) if r >> s & 1] for r in small]
            out[name][n] = {"relations": len(rels), "keys": len(keys), "colliding_groups": len(coll),
                            "example": ex, "seconds": round(time.time() - t, 1)}
    return out


def weave():
    out = {}
    for name, law in W.LAWS.items():
        out[name] = [W.spectrum(w, law) for w in range(3, 13)]
    return out


def correlations():
    out = {}
    for name, law in W.LAWS.items():
        if name == "parity":
            continue
        try:
            c = W.axis_correlation(12, law, rmax=14)
        except Exception as exc:          # degenerate spectra (frozen laws) are recorded, not fatal
            out[name] = {"error": repr(exc)}
            continue
        cor = c["correlation"]
        rate = None
        if cor[5] and cor[11] and abs(cor[5]) > 0 and abs(cor[11]) > 0:
            import math
            rate = math.log(abs(cor[5]) / abs(cor[11]), 3) / 6
        out[name] = {"mean": c["mean"], "correlation": cor, "rate_6_to_12": rate}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["weave"] = weave()
    res["axis_correlation_width_12"] = correlations()
    res["census"] = census()
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), res["started"], res["finished"])


if __name__ == "__main__":
    main()
