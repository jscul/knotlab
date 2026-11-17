"""Frozen run for STATE-RULES-20261117-001B-E001: what uniform rules that read only the states grow, and whether they decide.

Parts (see the contract and the pre-registration):
- E1, exact distributions over classes from one knot B(0, 1, 2): F1, F2, F3, F3c to n = 9, U1 to n = 7, U3 and U3c to n = 6
  (c: each class of outcome counted once);
- E2, conservation: F1 from the line, the 2 x 2 pattern and the 3-leaf star, 20 runs each to n = 14;
- E3, F3 and F3c from one knot, 40 runs each to n = 16 (classes at n = 8 and 16; whether each step's top options are one class);
- E4, uniform: U1, 50 runs to n = 12; U3, 50 runs to n = 10;
- E5, softmax over the three-knot extensions, beta 0.5, 1 and 2, 40 runs each to n = 10;
- E6, the referee's sharp form: every extension with up to three knots of a line of 6, 7 and 8;
- E7, Codex's check: continuations invariant under every symmetry of the 3-line and of the square, over all relations and over
  knot extensions, for the signed group and for permutations with the global flip;
- E8, the knot arm: KF3 (fewest states over knot-local moves), KS3 (strict: the whole move inside one existing knot), KC3
  (closure-local, a function of the states: the control) and KU3 (uniform over knot-local moves), exact from one knot to n = 7
  (KF3, KS3) and 30 runs each from one knot, the fan of six and the non-fan of six to n = 12 (KU3 to n = 10); and the
  states-only F3 and U3 from both six-starts with the same seeds (identical by construction).
With --stress: E3b, F3 from one knot, 5 runs to n = 32 (a stress test, written to stress.json)."""
import collections
import json
import math
import os
import sys
import time

import rules as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "STATE-RULES-20261117-001B", "STATE-RULES-20261117-001B-E001_rules")


def kinds_of(rows):
    out = collections.Counter()
    for _, p, m in rows:
        out[m["kind"]] += p
    return {k: round(v, 12) for k, v in sorted(out.items())}


def two_way(rows):
    return round(sum(p for _, p, m in rows if m["two_way"]), 12)


def e1():
    res = {}
    for name, rule, K, nmax, count in (("F1", "fewest", 1, 9, "extensions"), ("F2", "fewest", 2, 9, "extensions"),
                                       ("F3", "fewest", 3, 9, "extensions"), ("F3c", "fewest", 3, 9, "classes"),
                                       ("U1", "uniform", 1, 7, "extensions"), ("U3", "uniform", 3, 6, "extensions"),
                                       ("U3c", "uniform", 3, 6, "classes")):
        t = time.time()
        levels, canon = R.exact(rule, K, "line", nmax, count=count)
        res[name] = [{"n": L["n"], "classes": L["classes"], "kinds": kinds_of(L["dist"]), "two_way": two_way(L["dist"]),
                      "lam": {str(l): round(sum(p for _, p, m in L["dist"] if m["lam"] == l), 12)
                              for l in sorted({m["lam"] for _, _, m in L["dist"]})},
                      "k3_or_more": round(sum(p for _, p, m in L["dist"] if m["k"] not in ("1", "2")), 12),
                      "determined_next": L.get("determined_next"),
                      "class_list": [{"p": round(p, 12), **{x: m[x] for x in ("kind", "N", "splits", "k", "lam")}}
                                     for _, p, m in sorted(L["dist"], key=lambda r: -r[1])][:40]}
                     for L in levels]
        print(f"E1 {name}: {time.time() - t:.0f}s", {L['n']: L['kinds'] for L in res[name]}, flush=True)
    return res


def summarise_runs(traces, at):
    out = {}
    for n in at:
        rows = [next((r for r in tr if r.get("n") == n and "kind" in r), None) for tr in traces]
        rows = [r for r in rows if r is not None]
        out[str(n)] = {"runs": len(rows), "kinds": dict(collections.Counter(r["kind"] for r in rows)),
                       "two_way": sum(r["two_way"] for r in rows), "lam": dict(collections.Counter(r["lam"] for r in rows)),
                       "k": dict(collections.Counter(r["k"] for r in rows)),
                       "N_median": sorted(r["N"] for r in rows)[len(rows) // 2] if rows else None}
    return out


def runs(rule, K, start, nmax, count, tag, beta=None, canon=None):
    traces = []
    for i in range(count):
        _, _, tr = R.grow(rule, K, start, nmax, f"SR:{tag}:{i}", beta, canon)
        traces.append(tr)
    return traces


def top_one_class(traces):
    c = collections.Counter((r["n"], r["top_classes"] == 1) for tr in traces for r in tr if "top_classes" in r)
    return {str(n): {"yes": c[(n, True)], "no": c[(n, False)]} for n in sorted({n for n, _ in c})}


def e2():
    res = {}
    for start in ("line", "2x2", "star"):
        traces = runs("fewest", 1, start, 14, 20, f"E2:{start}", canon=R.Canon())
        kl = collections.Counter((r["k"], r["lam"]) for tr in traces for r in tr if "lam" in r)
        res[start] = {"k_lam_pairs_over_all_steps": {f"k={a}, lam={b}": c for (a, b), c in kl.items()},
                      "top_one_class": top_one_class(traces),
                      "summary": summarise_runs(traces, [n for n in range(R.SEEDS[start][0], 15)]),
                      "exact_line_every_step": all(r["line"] for tr in traces for r in tr if "line" in r) if start == "line" else None}
        print("E2", start, res[start]["k_lam_pairs_over_all_steps"], flush=True)
    return res


def e3(nmax=16, count=40, tag="E3", how="extensions"):
    import random
    canon = R.Canon()
    traces, cls, determined = [], collections.defaultdict(list), collections.Counter()
    for i in range(count):
        rng = random.Random(f"SR:{tag}:{i}")
        n, st = R.seed("line")
        tr = [{"n": n, **R.measure(st, n)}]
        while n < nmax:
            new, ks, rec = R.step(st, n, "fewest", 3, rng, None, canon, how)
            st, n = new, n + 1
            tr.append({"n": n, "knots": len(ks), **rec, **R.measure(st, n)})
            determined[(n, rec["top_classes"] == 1)] += 1
            if n in (8, 16, 32):
                cls[n].append(canon.cid(st, n))
        traces.append(tr)
        print(f"{tag} run {i}: " + " ".join(f"{r['n']}:{r['lam']}/{r['k']}" for r in tr), flush=True)
    return {"summary": summarise_runs(traces, list(range(3, nmax + 1))),
            "classes_at": {str(n): dict(collections.Counter(v)) for n, v in cls.items()},
            "cube_at_8": sum(1 for tr in traces for r in tr if r["n"] == 8 and r["cube"]),
            "cube_at_16": sum(1 for tr in traces for r in tr if r["n"] == 16 and r["cube"]),
            "cube_at_32": sum(1 for tr in traces for r in tr if r["n"] == 32 and r["cube"]),
            "top_one_class": {str(n): {"yes": determined[(n, True)], "no": determined[(n, False)]}
                              for n in range(4, nmax + 1)},
            "top_options_median": {str(n): sorted(r["top_options"] for tr in traces for r in tr if r["n"] == n)[count // 2]
                                   for n in range(4, nmax + 1)},
            "states": {str(n): sorted({r["N"] for tr in traces for r in tr if r["n"] == n}) for n in range(3, nmax + 1)}}


def e4():
    res = {}
    for name, K, nmax, count in (("U1", 1, 12, 50), ("U3", 3, 10, 50)):
        traces = runs("uniform", K, "line", nmax, count, f"E4:{name}")
        res[name] = summarise_runs(traces, list(range(3, nmax + 1)))
        print("E4", name, {n: (v["two_way"], v["lam"]) for n, v in res[name].items()}, flush=True)
    return res


def e5():
    res = {}
    for beta in (0.5, 1.0, 2.0):
        traces = runs("softmax", 3, "line", 10, 40, f"E5:{beta}", beta=beta)
        res[str(beta)] = summarise_runs(traces, list(range(3, 11)))
        print("E5", beta, {n: (v["two_way"], v["lam"]) for n, v in res[str(beta)].items()}, flush=True)
    return res


def e6():
    res = {}
    canon = R.Canon()
    for n in (6, 7, 8):
        knots = [(i, j, l) for i in range(n) for j in range(i + 1, n) for l in range(j + 1, n)]
        st = R.base_from_knots(n, knots)
        ext = R.extensions(st, n, 3)
        N = len(st)
        rows = []
        for (a0, a1), ks in ext.items():
            new = R.apply(st, n, a0, a1)
            m = R.measure(new, n + 1)
            rows.append((len(new) - N, m, ks, canon.cid(new, n + 1)))
        zero = [r for r in rows if r[0] == 0]
        res[str(n)] = {
            "states": N, "extensions": len(rows),
            "kinds": dict(collections.Counter(r[1]["kind"] for r in rows)),
            "excess": dict(sorted(collections.Counter(r[0] for r in rows).items())),
            "max_lam": max(r[1]["lam"] for r in rows), "max_k": max(r[1]["k"] for r in rows),
            "keep_line": sum(r[1]["line"] for r in rows),
            "keep_line_excess": sorted({r[0] for r in rows if r[1]["line"]}),
            "zero_cost": len(zero), "zero_cost_kinds": dict(collections.Counter(r[1]["kind"] for r in zero)),
            "zero_cost_classes": len({r[3] for r in zero}),
            "zero_cost_knot_counts": dict(collections.Counter(len(r[2]) for r in zero)),
            "uniform_fraction_two_way": sum(r[1]["two_way"] for r in rows) / len(rows),
            "binomial_n_3": math.comb(n, 3)}
        print("E6", n, res[str(n)], flush=True)
    return res


def e7():
    res = {}
    for name in ("line", "2x2"):
        n, st = R.seed(name)
        for group in ("signed", "complement"):
            inv = R.invariant_continuations(st, n, group)
            res[f"{name}:{group}"] = {"symmetries": len([1 for p, f in R.signed_symmetries(st, n)
                                                          if group == "signed" or f in (0, (1 << n) - 1)]),
                                      "all_relations": dict(collections.Counter(k for _, k in inv)),
                                      "open_states": sorted(sum(2 if c == 2 else 1 for c in ch) for ch, k in inv if k == "open"),
                                      "knot_extensions_invariant_states": sorted(R.invariant_knot_extensions(st, n, 3, group))}
        print("E7", name, {k: v for k, v in res.items() if k.startswith(name)}, flush=True)
    return res


def knot_runs(rule, start, nmax, count, tag, local):
    canon = R.Canon()
    traces = []
    for i in range(count):
        _, _, _, tr = R.knot_grow(rule, 3, start, nmax, f"SR:{tag}:{i}", canon, local)
        traces.append(tr)
    return traces


def e8():
    res = {"exact": {}, "runs": {}, "states_only_controls": {}}
    for name, local in (("KF3", "knot"), ("KS3", "strict")):
        t = time.time()
        levels, _ = R.knot_exact("fewest", 3, "line", 7, local)
        res["exact"][name] = [{"n": L["n"], "classes": L["classes"], "kinds": kinds_of(L["dist"]), "two_way": two_way(L["dist"]),
                               "determined_next": L.get("determined_next")} for L in levels]
        print(f"E8 exact {name}: {time.time() - t:.0f}s", {L['n']: L['kinds'] for L in res['exact'][name]}, flush=True)
    for name, rule, local, nmax in (("KF3", "fewest", "knot", 12), ("KS3", "fewest", "strict", 12),
                                    ("KC3", "fewest", "closure", 12), ("KU3", "uniform", "knot", 10)):
        for start in ("line", "fan6", "nonfan6"):
            t = time.time()
            traces = knot_runs(rule, start, nmax, 30, f"E8:{name}:{start}", local)
            first2 = collections.Counter(next((r["n"] for r in tr if r.get("two_way")), None) for tr in traces)
            first3 = collections.Counter(next((r["n"] for r in tr if r.get("lam", 0) >= 3), None) for tr in traces)
            res["runs"][f"{name}:{start}"] = {"summary": summarise_runs(traces, list(range(SEED_N[start], nmax + 1))),
                                             "first_two_way": {str(k): v for k, v in first2.items()},
                                             "first_three_orders": {str(k): v for k, v in first3.items()},
                                             "stopped": sum(1 for tr in traces if any("stopped" in r for r in tr)),
                                             "top_one_class": top_one_class(traces)}
            print(f"E8 {name} {start}: {time.time() - t:.0f}s",
                  {n: (v["two_way"], v["lam"]) for n, v in res["runs"][f"{name}:{start}"]["summary"].items()}, flush=True)
    for name, rule in (("F3", "fewest"), ("U3", "uniform")):
        out = {}
        for start in ("fan6", "nonfan6"):
            traces = runs(rule, 3, start, 10, 20, f"E8:{name}:six")      # the same seeds for both starts
            out[start] = [[(r["n"], r.get("N"), r.get("kind")) for r in tr] for tr in traces]
        res["states_only_controls"][name] = {"identical": out["fan6"] == out["nonfan6"],
                                             "summary_fan6": summarise_runs([[{"n": a, "N": b, "kind": c, "two_way": c == "two orders",
                                                                               "lam": 0, "k": ""} for a, b, c in tr] for tr in out["fan6"]], [10])}
        print("E8 states-only control", name, res["states_only_controls"][name]["identical"], flush=True)
    return res


SEED_N = {"line": 3, "fan6": 6, "nonfan6": 6}


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--stress" in sys.argv:
        t = time.time()
        out = e3(nmax=32, count=5, tag="E3b")
        out["seconds"] = round(time.time() - t)
        json.dump(out, open(os.path.join(OUT, "stress.json"), "w"), indent=1)
        return
    t0 = time.time()
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["E6"] = e6()
    res["E1"] = e1()
    res["E2"] = e2()
    res["E3"] = e3()
    res["E4"] = e4()
    res["E5"] = e5()
    res["E3c"] = e3(tag="E3c", how="classes")
    res["E7"] = e7()
    res["E8"] = e8()
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print("done", res["seconds"], "s")


if __name__ == "__main__":
    main()
