"""Frozen run for LOCAL-ROOM-20261118-001B-E001.  Parts as separate processes (--part NAME), then --merge.

- L1, the reach limit: exact class distributions of LF3(r) (the cheapest rule, every knot's old pair within r splits), r = 1, 2, 3,
  from one knot and from the 2 x 2 pattern, to n = 14; and 100 runs each to n = 20.
- L2, the class law (one remembered bit per split; knots only across splits of different classes; no pendants), from the 2 x 2
  pattern with its two splits in two classes: 200 runs to n = 30.
"""
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locallib as L  # noqa: E402

R = L.R
OUT = os.path.join(L.ROOT, "artifacts", "LOCAL-ROOM-20261118-001B", "LOCAL-ROOM-20261118-001B-E001_local")


def summary(traces, at):
    out = {}
    for n in at:
        rows = [next((x for x in tr if x.get("n") == n and "kind" in x), None) for tr in traces]
        rows = [x for x in rows if x is not None]
        out[str(n)] = {"runs": len(rows), "stalled": sum(1 for tr in traces if any("stopped" in x and x["n"] <= n for x in tr)),
                       "kinds": dict(collections.Counter(x["kind"] for x in rows)), "lam": dict(collections.Counter(x["lam"] for x in rows)),
                       "N": dict(collections.Counter(x["N"] for x in rows)),
                       "full_grid": sum(1 for x in rows if x.get("full_grid"))}
    return out


def l1():
    res = {"exact": {}, "runs": {}}
    for r in (1, 2, 3):
        for start in ("line", "2x2"):
            t = time.time()
            levels, _ = L.exact(start, 14, 3, r)
            res["exact"][f"r{r}:{start}"] = [{"n": Lv["n"], "classes": Lv["classes"], "stalled_before": Lv["stalled_before"],
                                               "kinds": {k: round(sum(p for _, p, m in Lv["dist"] if m["kind"] == k), 12)
                                                         for k in {m["kind"] for _, _, m in Lv["dist"]}},
                                               "lam": {str(l): round(sum(p for _, p, m in Lv["dist"] if m["lam"] == l), 12)
                                                       for l in {m["lam"] for _, _, m in Lv["dist"]}},
                                               "states": sorted({m["N"] for _, _, m in Lv["dist"]})} for Lv in levels]
            print("L1 exact", r, start, f"{time.time() - t:.0f}s", {Lv["n"]: (Lv["kinds"], Lv["stalled_before"]) for Lv in res["exact"][f"r{r}:{start}"]}, flush=True)
            traces = [L.grow(start, 20, f"LR:L1:{r}:{start}:{i}", 3, r)[2] for i in range(100)]
            res["runs"][f"r{r}:{start}"] = summary(traces, [8, 12, 16, 20])
            print("L1 runs", r, start, {n: (v["kinds"], v["stalled"]) for n, v in res["runs"][f"r{r}:{start}"].items()}, flush=True)
    return res


def l2():
    t = time.time()
    traces = [L.class_grow(30, f"LR:L2:{i}")[2] for i in range(200)]
    at = [4, 6, 9, 12, 16, 20, 25, 30]
    out = summary(traces, at)
    fills_at_full = collections.Counter()
    for tr in traces:
        for x in tr:
            if x.get("full_grid"):
                fills_at_full[x["n"]] += 1
    res = {"summary": out, "full_grid_counts_by_n": dict(sorted(fills_at_full.items())),
           "class_splits_at_30": dict(collections.Counter(tuple(tr[-1].get("class_splits", [])) for tr in traces)),
           "every_run_lam2_k2": all(x["lam"] == 2 and x["k"] == "2" for tr in traces for x in tr if "lam" in x and x["n"] >= 4)}
    print("L2", f"{time.time() - t:.0f}s", {n: (v["kinds"], v["full_grid"], v["stalled"]) for n, v in out.items()}, res["every_run_lam2_k2"], flush=True)
    return res


PARTS = {"L1": l1, "L2": l2}


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--part" in sys.argv:
        name = sys.argv[sys.argv.index("--part") + 1]
        t0 = time.time()
        res = {"part": name, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "result": PARTS[name]()}
        res["seconds"] = round(time.time() - t0)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        json.dump(res, open(os.path.join(OUT, f"part_{name}.json"), "w"), indent=1, default=str)
        print("done", name, res["seconds"], "s")
        return
    if "--merge" in sys.argv:
        res = {}
        for name in PARTS:
            part = json.load(open(os.path.join(OUT, f"part_{name}.json")))
            res[name] = part["result"]
            res.setdefault("parts", {})[name] = {k: part[k] for k in ("started", "finished", "seconds")}
        json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
        print("merged")
        return
    raise SystemExit("use --part L1|L2 or --merge")


if __name__ == "__main__":
    main()
