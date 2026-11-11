#!/usr/bin/env python3
"""Finite checks for OVERLAP-READ-20261111-001B-P001: what not-all-equal forces (proof.md).

  C1. L1 on every labeled knot pattern on 3 to 6 distinctions (6 by its distinct state sets) and 5,000 random ones on 7 to 9, those
      with a state: nothing frozen, every tie an equality or an inequality, every triple with free pairs (knots included) missing
      nothing or exactly one complementary pair of patterns.
  C2. L2: the Pasch and the octahedron have the same 18 states, every pair of the six free, each complementary triple missing 000 and
      111 under the Pasch alone.
  C3. L3: the book with k pages is read faithfully, k = 1 to 12.
  C4. L4: the weighted cut equals 2(|E| - m) for 2,000 random bases with 5 random colourings each; no state on the complete triple
      systems on 5 to 8 points, the Fano plane, the affine plane of order 3 and a 2-(6, 3, 2) design.
  C5. Mutation: the one-in-three law (exactly one 1) in place of NAE breaks C1 (so C1 can fail); it is not symmetric under
      complement, which is what L1 uses.
  C6. Mutation: the parity law (an odd number of 1s) breaks the triple part of C1 alone (its triples miss four patterns).
  C7. L5: knot patterns with the same number of knots on every pair have the same states: the Pasch and its complementary four, and
      1,000 random pairs of patterns related by a Pasch trade.

Usage: check.py [--write]   (the workspace .venv)
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "KNOTS-ALONE-20261111-001A" / "KNOTS-ALONE-20261111-001A-E001_knots_alone_census"))
import knots_alone as ka  # noqa: E402

NAE = ka.LAWS["NAE"]
ONE_IN_THREE = (1,)
PARITY = (1, 3)


def states(V, T, W=NAE):
    return ka.all_states(V, T, W)


def patterns(st, S):
    code = np.zeros(len(st), dtype=np.int64)
    for i, v in enumerate(S):
        code |= ((st >> v) & 1) << i
    return set(np.unique(code).tolist())


def l1_violations(V, T, W=NAE, st=None, triples_only=False):
    st = states(V, T, W) if st is None else st
    if len(st) == 0:
        return 0
    bad = 0
    full = lambda S: len(patterns(st, S)) == 1 << len(S)
    frozen = [v for v in range(V) if not full((v,))]
    free = {p for p in itertools.combinations(range(V), 2) if full(p)}
    if not triples_only:
        bad += len(frozen)
        for p in itertools.combinations(range(V), 2):
            if p in free or p[0] in frozen or p[1] in frozen:
                continue
            if patterns(st, p) not in ({0b00, 0b11}, {0b01, 0b10}):
                bad += 1
    for t in itertools.combinations(range(V), 3):
        if not all(q in free for q in itertools.combinations(t, 2)):
            continue
        A = patterns(st, t)
        if len(A) == 8:
            continue
        missing = sorted(set(range(8)) - A)
        if not (len(missing) == 2 and missing[0] ^ missing[1] == 7):
            bad += 1
    return bad


def state_sets(n, W):
    """Every distinct state set of a labeled knot pattern on n distinctions under W, by the one-pass trick."""
    trip = list(itertools.combinations(range(n), 3))
    X = np.arange(1 << n)
    ok_w = np.zeros(4, dtype=bool)
    ok_w[list(W)] = True
    bad = np.zeros(1 << n, dtype=np.int64)
    for k, t in enumerate(trip):
        s = ((X >> t[0]) & 1) + ((X >> t[1]) & 1) + ((X >> t[2]) & 1)
        bad |= (~ok_w[s]).astype(np.int64) << k
    Ts = np.arange(1, 1 << len(trip), dtype=np.int64)
    S = np.zeros(len(Ts), dtype=np.uint64)
    for x in range(1 << n):
        S |= (((bad[x] & Ts) == 0).astype(np.uint64) << np.uint64(x))
    return [np.array([x for x in range(1 << n) if (int(u) >> x) & 1], dtype=np.int64) for u in np.unique(S)]


def c1(mutate=None):
    W = {None: NAE, "one-in-three": ONE_IN_THREE, "parity": PARITY}[mutate]
    triples_only = mutate == "parity"
    tested = bad = 0
    for n in range(3, 7):
        for st in state_sets(n, W):
            if len(st) == 0:
                continue
            tested += 1
            bad += l1_violations(n, [], W, st=st, triples_only=triples_only) > 0
    rng = random.Random(7)
    for _ in range(5000):
        n = rng.randint(7, 9)
        trip = list(itertools.combinations(range(n), 3))
        T = sorted(rng.sample(trip, rng.randint(2, len(trip) // 3)))
        st = states(n, T, W)
        if len(st) == 0:
            continue
        tested += 1
        bad += l1_violations(n, T, W, st=st, triples_only=triples_only) > 0
    return {"state sets and patterns with a state": tested, "with a violation": bad}


def c2():
    a, x, b, y, c, z = range(6)
    P = [(a, b, c), (a, y, z), (x, b, z), (x, y, c)]
    comp = [(x, y, z), (x, b, c), (a, y, c), (a, b, z)]
    O = P + comp
    sp, so = set(states(6, [tuple(sorted(t)) for t in P]).tolist()), set(states(6, [tuple(sorted(t)) for t in O]).tolist())
    st = np.array(sorted(sp), dtype=np.int64)
    pairs_free = all(len(patterns(st, p)) == 4 for p in itertools.combinations(range(6), 2))
    comp_nae = all(patterns(st, tuple(sorted(t))) == set(range(8)) - {0, 7} for t in comp)
    return {"Pasch states": len(sp), "octahedron states": len(so), "equal": sp == so, "every pair free": pairs_free,
            "complementary triples NAE": comp_nae, "states": sorted(sp)}


def c3():
    out = {}
    for k in range(1, 13):
        T = [(0, 1, i) for i in range(2, k + 2)]
        out[k] = bool(ka.read_law_brute(k + 2, T, NAE)["faithful"])
    return out


def designs():
    out = {}
    for v in range(5, 9):
        out[f"complete on {v}"] = [tuple(t) for t in itertools.combinations(range(v), 3)]
    out["Fano plane"] = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
    pts = [(i, j) for i in range(3) for j in range(3)]
    idx = {p: k for k, p in enumerate(pts)}
    lines = set()
    for p, q in itertools.combinations(pts, 2):
        d = ((q[0] - p[0]) % 3, (q[1] - p[1]) % 3)
        line = tuple(sorted(idx[((p[0] + t * d[0]) % 3, (p[1] + t * d[1]) % 3)] for t in range(3)))
        lines.add(line)
    out["affine plane of order 3"] = sorted(lines)
    # a 2-(6,3,2) design: the 10 triples of the unique one (two copies of each pair)
    out["2-(6,3,2)"] = [(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 5), (0, 4, 5), (1, 2, 5), (1, 3, 4), (1, 4, 5), (2, 3, 4), (2, 3, 5)]
    return out


def c4():
    rng = random.Random(8)
    mism = 0
    for _ in range(2000):
        n = rng.randint(4, 12)
        trip = list(itertools.combinations(range(n), 3))
        T = rng.sample(trip, rng.randint(1, min(len(trip), 40)))
        c = {}
        for t in T:
            for p in itertools.combinations(t, 2):
                c[p] = c.get(p, 0) + 1
        for _ in range(5):
            s = [rng.randint(0, 1) for _ in range(n)]
            cut = sum(w for p, w in c.items() if s[p[0]] != s[p[1]])
            m = sum(1 for t in T if s[t[0]] == s[t[1]] == s[t[2]])
            mism += cut != 2 * (len(T) - m)
    des = {}
    for name, T in designs().items():
        V = 1 + max(v for t in T for v in t)
        cnt = {}
        for t in T:
            for p in itertools.combinations(t, 2):
                cnt[p] = cnt.get(p, 0) + 1
        is_design = len(cnt) == V * (V - 1) // 2 and len(set(cnt.values())) == 1
        des[name] = {"design": is_design, "lambda": next(iter(set(cnt.values()))), "states": int(len(states(V, T)))}
    return {"identity mismatches": mism, "designs": des}


def c7():
    a, x, b, y, c, z = range(6)
    P = [(a, b, c), (a, y, z), (x, b, z), (x, y, c)]
    Q = [(x, y, z), (x, b, c), (a, y, c), (a, b, z)]
    same = set(states(6, [tuple(sorted(t)) for t in P]).tolist()) == set(states(6, [tuple(sorted(t)) for t in Q]).tolist())
    rng = random.Random(9)
    trades = differ = 0
    for _ in range(1000):
        n = rng.randint(6, 10)
        six = rng.sample(range(n), 6)
        a, x, b, y, c, z = six
        P = [tuple(sorted(t)) for t in ((a, b, c), (a, y, z), (x, b, z), (x, y, c))]
        Q = [tuple(sorted(t)) for t in ((x, y, z), (x, b, c), (a, y, c), (a, b, z))]
        trip = [t for t in itertools.combinations(range(n), 3) if t not in P and t not in Q]
        R = rng.sample(trip, rng.randint(0, min(12, len(trip))))
        trades += 1
        differ += set(states(n, R + P).tolist()) != set(states(n, R + Q).tolist())
    return {"Pasch and complement same states": same, "random trades": trades, "with different states": differ}


def main():
    out = {"C1": c1(), "C2": c2(), "C3": c3(), "C4": c4(), "C5": c1(mutate="one-in-three"), "C6": c1(mutate="parity"), "C7": c7()}
    ok = {"C1": out["C1"]["with a violation"] == 0,
          "C2": out["C2"]["equal"] and out["C2"]["Pasch states"] == 18 and out["C2"]["every pair free"] and out["C2"]["complementary triples NAE"],
          "C3": all(out["C3"].values()),
          "C4": out["C4"]["identity mismatches"] == 0 and all(d["design"] and d["states"] == 0 for d in out["C4"]["designs"].values()),
          "C5": out["C5"]["with a violation"] > 0,
          "C6": out["C6"]["with a violation"] > 0,
          "C7": out["C7"]["Pasch and complement same states"] and out["C7"]["with different states"] == 0}
    out["pass"] = ok
    out["failures"] = [k for k, v in ok.items() if not v]
    print(json.dumps({k: v for k, v in out.items() if k != "C2"} | {"C2": {k: v for k, v in out["C2"].items() if k != "states"}}, indent=1))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not out["failures"] else "failed", "claim": manifest["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
