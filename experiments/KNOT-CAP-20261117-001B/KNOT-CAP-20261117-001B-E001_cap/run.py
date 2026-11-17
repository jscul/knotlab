"""Frozen run for KNOT-CAP-20261117-001B-E001.  Each part runs as its own process (--part NAME), then --merge.

- K1, the caps from one knot: exact class distributions to n = 7 for the degree cap c = 3, 4, 5, 6, 9, 12, the pair cap (each
  pair of distinctions in at most 2 knots) and the pair cap with knot-locality; 200 runs each to n = 16 (c = 4, 5, 6, 9, 12 and
  the two pair-cap rules).
- K2, matched starts, exact: the knot-local fewest-states rule (KF3) from the fan and non-fan six-starts, and from two five-starts
  with the line of five's 10 states and three knots each, one with the shared distinction at an end and one with it in the middle
  (every three-knot presentation of that line has a distinction in all three knots), to n = 10.  Distances between the starts' distributions over full classes, classes of states, and coarse
  features; the sorted class probabilities; the classes present in one start only.
- K3, matched starts, sampled: KF3, 1,000 runs per start with identical seed strings, to n = 12, and a floor (a second 1,000 runs
  from each start with other seeds); permutation tests on pooled runs.
- K4, erasure: KF3 to n = 8, then the knots are forgotten and the states-only fewest-states rule continues; exact to n = 11 and
  1,000 runs per start to n = 14, with the floor and permutation tests; the no-erasure control (KF3 kept) exact to n = 10.
- K5, the caps from the matched starts: c = 5 and 6 and the pair cap with knot-locality, 300 runs per start to n = 12.
"""
import collections
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import caplib as C  # noqa: E402

R = C.R
ROOT = C.ROOT
OUT = os.path.join(ROOT, "artifacts", "KNOT-CAP-20261117-001B", "KNOT-CAP-20261117-001B-E001_cap")
INF = 10 ** 9
R.SEEDS["fan5"] = (5, [(0, 1, 2), (0, 2, 3), (0, 3, 4)])          # a line of five; the end distinction 0 in all three knots
R.SEEDS["mid5"] = (5, [(0, 1, 2), (0, 2, 4), (2, 3, 4)])          # the same ten states; the middle distinction 2 in all three
PAIRS = (("fan6", "nonfan6"), ("fan5", "mid5"))
RULES_K1 = {"c3": (3, None, None), "c4": (4, None, None), "c5": (5, None, None), "c6": (6, None, None), "c9": (9, None, None),
            "c12": (12, None, None), "pair2": (INF, None, 2), "pair2-local": (INF, "knot", 2)}


def kinds(rows):
    out = collections.Counter()
    for _, p, m in rows:
        out[m["kind"]] += p
    return {k: round(v, 12) for k, v in sorted(out.items())}


def summary(traces, at):
    out = {}
    for n in at:
        rows = [next((r for r in tr if r.get("n") == n and "kind" in r), None) for tr in traces]
        stopped = sum(1 for tr in traces if any("stopped" in r and r["n"] <= n for r in tr))
        rows = [r for r in rows if r is not None]
        fills = [sum(1 for r in tr if r.get("excess") == 0 and r["n"] <= n) for tr in traces]
        out[str(n)] = {"runs": len(rows), "stalled_by_here": stopped, "kinds": dict(collections.Counter(r["kind"] for r in rows)),
                       "two_way": sum(r["two_way"] for r in rows), "lam": dict(collections.Counter(r["lam"] for r in rows)),
                       "N": dict(collections.Counter(r["N"] for r in rows)),
                       "fills": dict(collections.Counter(fills)),
                       "max_degree": dict(collections.Counter(r.get("max_degree") for r in rows))}
    return out


def k1():
    res = {"exact": {}, "runs": {}}
    for name, (c, local, pair) in RULES_K1.items():
        t = time.time()
        levels, _ = C.cap_exact("line", 7, c, local, pair=pair)
        res["exact"][name] = [{"n": L["n"], "classes": L["classes"], "kinds": kinds(L["dist"]),
                               "two_way": round(sum(p for _, p, m in L["dist"] if m["two_way"]), 12),
                               "stalled_before": L["stalled_before"], "determined_next": L.get("determined_next")} for L in levels]
        print("K1 exact", name, f"{time.time() - t:.0f}s", {L["n"]: (L["kinds"], L["stalled_before"]) for L in res["exact"][name]},
              flush=True)
    for name in ("c4", "c5", "c6", "c9", "c12", "pair2", "pair2-local"):
        c, local, pair = RULES_K1[name]
        t = time.time()
        traces = [C.cap_grow("line", 16, f"KC:K1:{name}:{i}", c, local, pair=pair)[3] for i in range(200)]
        res["runs"][name] = summary(traces, [4, 5, 6, 8, 12, 16])
        print("K1 runs", name, f"{time.time() - t:.0f}s", {n: (v["two_way"], v["lam"], v["stalled_by_here"])
                                                            for n, v in res["runs"][name].items()}, flush=True)
    return res


def compare(dists_a, dists_b, sc):
    """dists: {n: {class: p}} over classes of states.  TV of classes and of coarse features; classes in one start only."""
    out = {}
    for n in sorted(set(dists_a) & set(dists_b)):
        a, b = dists_a[n], dists_b[n]
        fa, fb = collections.Counter(), collections.Counter()
        for d, f in ((a, fa), (b, fb)):
            for cl, p in d.items():
                st, nn, _ = sc.reps[cl]
                f[json.dumps(C.feature_key(R.measure(list(st), nn)), sort_keys=True)] += p
        only = []
        for d, other, tag in ((a, b, "first"), (b, a, "second")):
            for cl, p in sorted(d.items(), key=lambda kv: -kv[1]):
                if other.get(cl, 0.0) == 0.0:
                    st, nn, _ = sc.reps[cl]
                    only.append({"in": tag, "p": round(p, 12), **C.feature_key(R.measure(list(st), nn))})
        out[str(n)] = {"tv_states": round(C.tv(a, b), 12), "tv_features": round(C.tv(dict(fa), dict(fb)), 12),
                       "classes": [len(a), len(b)], "shared": len(set(a) & set(b)),
                       "shared_mass": round(sum(min(a.get(k, 0), b.get(k, 0)) for k in set(a) | set(b)), 12),
                       "only_in_one": only[:40], "only_in_one_count": len(only)}
    return out


def k2():
    res = {}
    for fa, fb in PAIRS:
        t = time.time()
        canon, sc = R.Canon(), R.Canon()
        la, _ = C.cap_exact(fa, 10, INF, "knot", canon)
        lb, _ = C.cap_exact(fb, 10, INF, "knot", canon)
        full = {}
        da, db = {}, {}
        for A, B in zip(la, lb):
            n = A["n"]
            pa = {cl: p for cl, p, _ in A["dist"]}
            pb = {cl: p for cl, p, _ in B["dist"]}
            full[str(n)] = {"tv_full": round(C.tv(pa, pb), 12),
                            "sorted_probabilities_equal": sorted(round(p, 9) for p in pa.values()) == sorted(round(p, 9) for p in pb.values()),
                            "two_way": [round(sum(p for _, p, m in A["dist"] if m["two_way"]), 12),
                                        round(sum(p for _, p, m in B["dist"] if m["two_way"]), 12)],
                            "lam": [{str(l): round(sum(p for _, p, m in L["dist"] if m["lam"] == l), 12)
                                     for l in sorted({m["lam"] for _, _, m in L["dist"]})} for L in (A, B)]}
            for L, d in ((A, da), (B, db)):
                mix = collections.Counter()
                for cl, p, _ in L["dist"]:
                    st, nn, kk = canon.reps[cl]
                    mix[sc.cid(list(st), nn)] += p
                d[n] = dict(mix)
        res[f"{fa}|{fb}"] = {"full": full, "states": compare(da, db, sc)}
        print("K2", fa, fb, f"{time.time() - t:.0f}s", {n: (v["tv_states"], v["tv_features"]) for n, v in res[f"{fa}|{fb}"]["states"].items()},
              flush=True)
    return res


def sampled_dists(traces, sc, at):
    d = {n: collections.Counter() for n in at}
    for st_tr in traces:
        for n, st in st_tr:
            if n in d:
                d[n][sc.cid(st, n)] += 1.0 / len(traces)
    return {n: dict(v) for n, v in d.items()}


def run_states(start, nmax, tag, count, erase_at=None):
    """count runs of KF3 (knot-local fewest), erasing the knots at erase_at if given; records the states at each n."""
    out, measures = [], []
    for i in range(count):
        rng = random.Random(f"KC:{tag}:{i}")
        n, knots = R.SEEDS[start][0], list(R.SEEDS[start][1])
        states = R.base_from_knots(n, knots)
        rec = [(n, states)]
        ms = {n: R.measure(states, n)}
        while n < nmax:
            if erase_at is not None and n >= erase_at:
                new, ks, _ = R.step(states, n, "fewest", 3, rng)
                if new is None:
                    break
                states, n = new, n + 1
            else:
                new, nk, ks, _ = C.cap_step(states, n, knots, INF, rng, "knot")
                if new is None:
                    break
                states, knots, n = new, nk, n + 1
            rec.append((n, states))
            ms[n] = R.measure(states, n)
        out.append(rec)
        measures.append(ms)
    return out, measures


def permutation_p(labels_a, labels_b, observed, perms, seed):
    """Permutation test for the TV between two samples of class labels (one label per run)."""
    rng = random.Random(seed)
    pool = labels_a + labels_b
    na = len(labels_a)
    hits = 0
    for _ in range(perms):
        rng.shuffle(pool)
        a, b = collections.Counter(pool[:na]), collections.Counter(pool[na:])
        t = 0.5 * sum(abs(a[k] / na - b[k] / (len(pool) - na)) for k in set(a) | set(b))
        hits += t >= observed - 1e-12
    return (hits + 1) / (perms + 1)


def sampled_compare(start_a, start_b, nmax, count, tag, erase_at=None, at=None):
    sc = R.Canon()
    ta, ma = run_states(start_a, nmax, tag, count, erase_at)            # identical seed strings for both starts
    tb, mb = run_states(start_b, nmax, tag, count, erase_at)
    fa, _ = run_states(start_a, nmax, tag + ":floor", count, erase_at)  # the floor: the same start, other seeds
    fb, _ = run_states(start_b, nmax, tag + ":floor", count, erase_at)
    out = {}
    for n in at:
        la = [sc.cid(st, nn) for tr in ta for nn, st in tr if nn == n]
        lb = [sc.cid(st, nn) for tr in tb for nn, st in tr if nn == n]
        lfa = [sc.cid(st, nn) for tr in fa for nn, st in tr if nn == n]
        lfb = [sc.cid(st, nn) for tr in fb for nn, st in tr if nn == n]
        dist = lambda xs: {k: v / len(xs) for k, v in collections.Counter(xs).items()}
        obs = C.tv(dist(la), dist(lb))
        two = [sum(1 for m in ma if n in m and m[n]["two_way"]), sum(1 for m in mb if n in m and m[n]["two_way"])]
        lam = [dict(collections.Counter(m[n]["lam"] for m in ms if n in m)) for ms in (ma, mb)]
        out[str(n)] = {"runs": [len(la), len(lb)], "classes_seen": [len(set(la)), len(set(lb))], "tv_states": round(obs, 6),
                       "floor": [round(C.tv(dist(la), dist(lfa)), 6), round(C.tv(dist(lb), dist(lfb)), 6)],
                       "permutation_p": permutation_p(la, lb, obs, 200, f"perm:{tag}:{n}"), "two_way": two, "lam": lam}
    return out


def k3():
    res = {}
    for fa, fb in PAIRS:
        t = time.time()
        res[f"{fa}|{fb}"] = sampled_compare(fa, fb, 12, 1000, "K3", None, list(range(R.SEEDS[fa][0], 13)))
        print("K3", fa, fb, f"{time.time() - t:.0f}s", {n: (v["tv_states"], v["floor"], v["permutation_p"]) for n, v in res[f"{fa}|{fb}"].items()},
              flush=True)
    return res


def k4():
    res = {"exact": {}, "sampled": {}}
    for fa, fb in PAIRS:
        t = time.time()
        canon, sc = R.Canon(), R.Canon()
        mixes = {}
        for s in (fa, fb):
            levels, _ = C.cap_exact(s, 8, INF, "knot", canon)
            mixes[s] = C.states_exact_from(C.states_mixture(levels, canon, sc), sc, 11)
        ea = {n: d for n, d in mixes[fa]}
        eb = {n: d for n, d in mixes[fb]}
        kept = {}                                            # the no-erasure control: KF3 with the knots kept, exact to n = 10
        for s in (fa, fb):
            levels, _ = C.cap_exact(s, 10, INF, "knot", canon)
            kept[s] = {}
            for L in levels:
                mix = collections.Counter()
                for cl, p, _ in L["dist"]:
                    st, nn, kk = canon.reps[cl]
                    mix[sc.cid(list(st), nn)] += p
                kept[s][L["n"]] = dict(mix)
        res["exact"][f"{fa}|{fb}"] = {"erased": compare(ea, eb, sc),
                                      "kept": {str(n): round(C.tv(kept[fa][n], kept[fb][n]), 12) for n in kept[fa] if n >= 8}}
        print("K4 exact", fa, fb, f"{time.time() - t:.0f}s", {n: v["tv_states"] for n, v in res["exact"][f"{fa}|{fb}"]["erased"].items()},
              res["exact"][f"{fa}|{fb}"]["kept"], flush=True)
        t = time.time()
        res["sampled"][f"{fa}|{fb}"] = sampled_compare(fa, fb, 14, 1000, "K4", 8, list(range(8, 15)))
        print("K4 sampled", fa, fb, f"{time.time() - t:.0f}s", {n: (v["tv_states"], v["floor"], v["permutation_p"])
                                                                 for n, v in res["sampled"][f"{fa}|{fb}"].items()}, flush=True)
    return res


def k5():
    res = {}
    for name in ("c5", "c6", "pair2-local"):
        c, local, pair = RULES_K1[name]
        for fa, fb in PAIRS:
            t = time.time()
            ta = [C.cap_grow(fa, 12, f"KC:K5:{name}:{i}", c, local, pair=pair)[3] for i in range(300)]
            tb = [C.cap_grow(fb, 12, f"KC:K5:{name}:{i}", c, local, pair=pair)[3] for i in range(300)]
            at = list(range(R.SEEDS[fa][0], 13))
            res[f"{name}:{fa}|{fb}"] = {"first": summary(ta, at), "second": summary(tb, at)}
            print("K5", name, fa, fb, f"{time.time() - t:.0f}s",
                  {n: (res[f"{name}:{fa}|{fb}"]["first"][n]["two_way"], res[f"{name}:{fa}|{fb}"]["second"][n]["two_way"],
                       res[f"{name}:{fa}|{fb}"]["first"][n]["stalled_by_here"], res[f"{name}:{fa}|{fb}"]["second"][n]["stalled_by_here"])
                   for n in ("8", "12")}, flush=True)
    return res


PARTS = {"K1": k1, "K2": k2, "K3": k3, "K4": k4, "K5": k5}


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
        print("merged", len(PARTS), "parts")
        return
    raise SystemExit("use --part NAME (one of " + ", ".join(PARTS) + ") or --merge")


if __name__ == "__main__":
    main()
