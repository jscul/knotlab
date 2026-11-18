"""COPY-READ-20261118-001B-E001: the read-out.  Written after the freeze and before any result was read: counts, clean-witness
fractions per tier (pooled and held out), confirmed look-alikes, coverage, and predictions P1-P4.  Writes readout.json."""
import gzip
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "COPY-READ-20261118-001B", "COPY-READ-20261118-001B-E001_copy")


def load():
    f = os.path.join(OUT, "results.json")
    return json.load(open(f)) if os.path.exists(f) else json.load(gzip.open(f + ".gz", "rt"))


def main():
    res = load()["results"]
    n_abs_moves = sum(len(r["absorbing"]) for r in res)
    n_ref = sum(r["n_refused"] for r in res)
    out = {"absorbing_moves": n_abs_moves, "refused_moves": n_ref,
           "absorbing_share": n_abs_moves / (n_abs_moves + n_ref) if n_abs_moves + n_ref else None}
    # absorbing extensions: (run, n, ext) -> set of hashes per tier
    def exts(runs):
        E = {}
        for j, r in runs:
            for m in r["absorbing"]:
                e = E.setdefault((j, m["n"], tuple(m["ext"])), {t: set() for t in ("0", "c", "1")})
                for t in ("0", "c", "1"):
                    e[t].add(m["h" + t])
        return E
    allruns = list(enumerate(res))
    E = exts(allruns)
    out["absorbing_extensions"] = len(E)
    out["absorb_n_median"] = statistics.median(k[1] for k in E) if E else None
    tiers = {}
    for t in ("0", "c", "1"):
        dirty = set()
        for r in res:
            dirty |= set(r["refused"][t])
        pooled = sum(1 for e in E.values() if any(h not in dirty for h in e[t])) / len(E) if E else None
        train = [(j, r) for j, r in allruns if r["index"] % 2 == 0]
        test = [(j, r) for j, r in allruns if r["index"] % 2 == 1]
        seen_abs = set()
        dirty_tr = set()
        for j, r in train:
            dirty_tr |= set(r["refused"][t])
            for m in r["absorbing"]:
                seen_abs.add(m["h" + t])
        Et = exts(test)
        seen = sum(1 for e in Et.values() if any(h in seen_abs or h in dirty_tr for h in e[t])) / len(Et) if Et else None
        clean_ho = sum(1 for e in Et.values() if any(h in seen_abs and h not in dirty_tr for h in e[t])) / len(Et) if Et else None
        tiers[t] = {"clean_witness_pooled": pooled, "heldout_seen": seen, "heldout_clean": clean_ho,
                    "confirmed_lookalikes": sum(r["verified"][t]["isomorphic"] for r in res),
                    "test_absorbing_extensions": len(Et)}
    out["tiers"] = tiers
    cov = [m["cov1"] for r in res for m in r["absorbing"]]
    out["coverage1_absorbing_mean"] = statistics.mean(cov) if cov else None
    P = {"P1": out["absorbing_share"] is not None and out["absorbing_share"] < 0.01,
         "P2": tiers["0"]["clean_witness_pooled"] == 0 and tiers["c"]["clean_witness_pooled"] == 0,
         "P3": tiers["1"]["heldout_clean"] is not None and tiers["1"]["heldout_clean"] < 0.5,
         "P4": out["absorb_n_median"] is not None and out["absorb_n_median"] < 15}
    out["predictions"] = P
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1)
    print(json.dumps(P))
    print(json.dumps({k: v for k, v in out.items() if k != "predictions"}, indent=1))


if __name__ == "__main__":
    main()
