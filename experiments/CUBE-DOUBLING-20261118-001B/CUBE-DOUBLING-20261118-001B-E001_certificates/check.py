"""Frozen check for CUBE-DOUBLING-20261118-001B-E001.

D1. For s = 1 to 7, both classes of cheapest step from the cube Q_s (a subdivision, a pendant): every certificate of the proof's L5
    gives a zero-cost admitted fill that is not a copy; the fills are distinct; their number equals the unoccupied orientations,
    2^(s+1) - 2^s - 1.
D2. For s = 2 to 4: every admitted extension of Q_s with up to three knots (STATE-RULES's rules.extensions): none costs nothing,
    and exactly s 2^(s-1) + 2^s cost N + 2 (L4).
D3. The exact distribution of the cheapest rule (fewest states, three knots) from one knot to n = 20: the states at every n and the
    kinds at n = 4, 8, 16.
It builds on STATE-RULES-20261117-001B-E001's rules.py (closed; sha256 pinned in the contract).

    .venv/bin/python -B check.py      (writes artifacts/.../results.json)
"""
import collections
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "STATE-RULES-20261117-001B", "STATE-RULES-20261117-001B-E001_rules"))
import rules as R  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "CUBE-DOUBLING-20261118-001B", "CUBE-DOUBLING-20261118-001B-E001_certificates")


def cube(s):
    """The cut system of Q_s: point i has coordinates the bits of i."""
    n = 1 << s
    full = (1 << n) - 1
    states = {0, full}
    for j in range(s):
        m = sum(1 << i for i in range(n) if (i >> j) & 1)
        states |= {m, full ^ m}
    return n, sorted(states)


def admitted_zero_cost_fill(states, n, knots):
    new = R.extend_brute(states, n, knots)
    if {x & ((1 << n) - 1) for x in new} != set(states):
        return None, "an old state dies"
    if len(new) != len(states):
        return None, f"costs {len(new) - len(states)}"
    for u in range(n):
        if all(((x >> u) & 1) == ((x >> n) & 1) for x in new):
            return None, f"a copy of {u}"
    return tuple(new), "ok"


def point(s, bit0, w):
    return bit0 | (w << 1)


def d1(s):
    n, st = cube(s)
    out = {}
    # subdivision of the edge between (0, w0) and (1, w0); p = n
    w0 = 0
    p = n
    sub = R.extend_brute(st, n, [(point(s, 0, w0), p, point(s, 1, w0))])
    fills, fails = set(), []
    for w in range(1 << (s - 1)):
        cert = []
        if w != w0:
            cert.append([(point(s, 0, w), n + 1, point(s, 1, w)), (point(s, 0, w0), p, n + 1), (point(s, 1, w0), p, n + 1)])
        cert.append([(point(s, 0, w), n + 1, point(s, 1, w)), (p, point(s, 0, w), n + 1), (p, point(s, 1, w), n + 1)])
        for ks in cert:
            r, why = admitted_zero_cost_fill(sub, n + 1, ks)
            (fills.add(r) if r else fails.append((ks, why)))
    out["subdivision"] = {"fills": len(fills), "unoccupied": 2 ** (s + 1) - 2 ** s - 1, "failures": [str(f) for f in fails],
                          "states_after_step": len(sub)}
    # pendant at c = 0: p copies point 0, plus the trivial split {p}
    c = 0
    cbar = n - 1
    pen = R.extend_brute(st, n, [(cbar, c, p)])
    fills, fails = set(), []
    for x in range(n):
        if x == c:
            continue
        ks = [(p, n + 1, x), (c, p, n + 1), (c, x, n + 1)]
        r, why = admitted_zero_cost_fill(pen, n + 1, ks)
        (fills.add(r) if r else fails.append((ks, why)))
    out["pendant"] = {"fills": len(fills), "unoccupied": 2 ** (s + 1) - 2 ** s - 1, "failures": [str(f) for f in fails],
                      "states_after_step": len(pen)}
    return out


def d2(s):
    n, st = cube(s)
    ext = R.extensions(st, n, 3)
    costs = collections.Counter(R.pc(a0) + R.pc(a1) - len(st) for a0, a1 in ext)
    return {"N": len(st), "zero_cost": costs.get(0, 0), "at_N_plus_2": costs.get(2, 0), "predicted": s * 2 ** (s - 1) + 2 ** s,
            "least_cost": min(costs)}


def d3(nmax=20):
    levels, canon = R.exact("fewest", 3, "line", nmax)
    out = {}
    for L in levels:
        out[str(L["n"])] = {"classes": L["classes"], "states": sorted({m["N"] for _, _, m in L["dist"]}),
                            "kinds": {k: round(sum(p for _, p, m in L["dist"] if m["kind"] == k), 12) for k in {m["kind"] for _, _, m in L["dist"]}},
                            "predicted_states": 2 * math.ceil(math.log2(L["n"])) + 2 if L["n"] >= 4 else None}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["D1"] = {str(s): d1(s) for s in range(1, 8)}
    print("D1", {s: (v["subdivision"]["fills"], v["pendant"]["fills"], v["subdivision"]["unoccupied"], len(v["subdivision"]["failures"]) + len(v["pendant"]["failures"])) for s, v in res["D1"].items()}, flush=True)
    res["D2"] = {}
    for s in (2, 3, 4):
        t = time.time()
        res["D2"][str(s)] = d2(s)
        print("D2", s, res["D2"][str(s)], f"{time.time() - t:.0f}s", flush=True)
    t = time.time()
    res["D3"] = d3()
    print("D3", f"{time.time() - t:.0f}s", {n: (v["states"], v["predicted_states"]) for n, v in res["D3"].items()}, flush=True)
    res["seconds"] = round(time.time() - t0)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print("done", res["seconds"], "s")


if __name__ == "__main__":
    main()
