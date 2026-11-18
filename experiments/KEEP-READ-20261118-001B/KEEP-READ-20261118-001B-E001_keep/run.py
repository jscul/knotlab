"""KEEP-READ-20261118-001B-E001: the frozen run.  SEEDK from every bracketing of 5, 6 and 7 and every third of 8 (105 starts),
one seed each, to n = 24; every zero-cost move after the switch is recorded.  Run: python -B run.py [--procs 12]."""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import keeplib as KL  # noqa: E402

M = KL.M
OUT = os.path.join(KL.ROOT, "artifacts", "KEEP-READ-20261118-001B", "KEEP-READ-20261118-001B-E001_keep")
NMAX = 24


def jobs():
    J = []
    for n0 in (5, 6, 7, 8):
        for i, ks in enumerate(M.bracketings(0, n0 - 1)):
            if n0 == 8 and i % 3:
                continue
            J.append((n0, i, ks, 60_000_000 + len(J)))
    return J


RULES = {
    "no_new_filled": lambda m: m["new_filled"] == 0,
    "db2_zero": lambda m: m["db2"] == 0,
    "disconnected": lambda m: m["components"] >= 2,
    "two_middles": lambda m: m["middles"] >= 2,
    "no_new_filled_and_disconnected": lambda m: m["new_filled"] == 0 and m["components"] >= 2,
    "disconnected_or_two_middles": lambda m: m["components"] >= 2 or m["middles"] >= 2,
}


def job(arg):
    """One run: each extension after the switch, with whether it keeps two orders, whether SEED accepts it, the candidate rules
    (some knot set satisfies), and per tier the picture hashes of its knot sets; and the in-run verified mixed pictures."""
    n0, i, ks, seed = arg
    t = time.time()
    rows, verified = KL.moves_after_switch(ks, n0, NMAX, seed)
    ext = {}
    for m in rows:
        key = (m["n"], m["ext"][0], m["ext"][1])
        e = ext.setdefault(key, {"n": m["n"], "keep": m["lam_after"] == 2, "accepted": m["accepted"],
                                 "rules": {k: False for k in RULES}, "h": {t_: set() for t_ in ("0", "1", "2", "c")},
                                 "cov1": [], "cov2": []})
        for k, f in RULES.items():
            e["rules"][k] |= f(m)
        for t_ in ("0", "1", "2", "c"):
            e["h"][t_].add(m[f"h{t_}"])
        e["cov1"].append(m["coverage1"])
        e["cov2"].append(m["coverage2"])
    out = []
    for e in ext.values():
        out.append({"n": e["n"], "keep": e["keep"], "accepted": e["accepted"], "rules": e["rules"],
                    "h": {t_: sorted(v) for t_, v in e["h"].items()},
                    "cov1": round(sum(e["cov1"]) / len(e["cov1"]), 3), "cov2": round(sum(e["cov2"]) / len(e["cov2"]), 3)})
    return {"n0": n0, "index": i, "knots": ks, "seed": seed, "moves": len(rows), "extensions": out,
            "verified": {str(r): v for r, v in verified.items()}, "seconds": round(time.time() - t, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    J = jobs()
    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, J, chunksize=1)):
            res.append(r)
            if (k + 1) % 15 == 0:
                print(k + 1, "of", len(J), round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["n0"], r["index"]))
    json.dump({"jobs": len(res), "seconds": round(time.time() - t0, 1), "results": res}, open(os.path.join(OUT, "results.json"), "w"))
    print("done", len(res), "in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
