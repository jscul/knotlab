#!/usr/bin/env python3
"""Independent check of the census and conformal test; imports no producer code.

Parses the raw rows and the frozen contract, recomputes every estimate and decision from the raw counts and the frozen
Pinson limits, and compares them with result.json. It replays two tori with its own construction, sampler and tests:
'x or (h != h')' on the 9 x 18 torus by breadth-first two-colouring of the disequality edges, and not-all-equal on the
9 x 9 torus by forced-value propagation (checked first against brute force on the 3 x 3 torus). Each replayed fraction
must lie within five standard errors of the recorded one. A deliberately tightened tolerance must change the verdict.
"""

from __future__ import annotations

import json
import math
import random
from collections import deque
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ARTIFACT = ROOT / "artifacts/CONTACT-CENSUS-20261022-001B/CONTACT-CENSUS-20261022-001B-E001_census_and_conformal_test"


def wmean(rows):
    ws = [1 / r["se_E"] ** 2 for r in rows]
    return sum(w * r["E"] for w, r in zip(ws, rows)) / sum(ws), math.sqrt(1 / sum(ws))


def edges_of(a, b):
    out = []
    for i in range(a):
        for j in range(b):
            out.append((i * b + j, ((i + 1) % a) * b + j))
    for i in range(a):
        for j in range(b):
            out.append((i * b + j, i * b + (j + 1) % b))
    return out


def two_colourable(nv, edges):
    adj = [[] for _ in range(nv)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    col = [-1] * nv
    for s in range(nv):
        if col[s] >= 0:
            continue
        col[s] = 0
        dq = deque([s])
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if col[w] < 0:
                    col[w] = 1 - col[u]
                    dq.append(w)
                elif col[w] == col[u]:
                    return False
    return True


def nae_extends(nv, edges, x):
    adj = [[] for _ in range(nv)]
    for (u, v), xe in zip(edges, x):
        adj[u].append((v, xe))
        adj[v].append((u, xe))
    val = {}
    for s in range(nv):
        if s in val:
            continue
        for start in (0, 1):
            trial = {s: start}
            stack = [s]
            ok = True
            while stack and ok:
                u = stack.pop()
                for w, xe in adj[u]:
                    if trial[u] == xe:
                        need = 1 - xe
                        have = trial.get(w, val.get(w))
                        if have is None:
                            trial[w] = need
                            stack.append(w)
                        elif have != need:
                            ok = False
                            break
            if ok:
                val.update(trial)
                break
        else:
            return False
    return all(not (val[u] == val[v] == xe) for (u, v), xe in zip(edges, x))


def decide(rows, contract, allowance=0.01):
    fam = {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r)
    pred = contract["predictions"]["pinson_limits_bits"]
    ok = True
    devs = {}
    for shape, limit in pred.items():
        m, se = wmean(fam[f"C2_{shape}"][-2:])
        devs[shape] = m - limit
        ok &= abs(m - limit) <= 3 * se + allowance
    rm, rse = wmean(fam["C2_rotated_square"])
    devs["rotated_square"] = rm - pred["square_both_odd"]
    ok &= abs(rm - pred["square_both_odd"]) <= 3 * rse + allowance
    return ok, devs


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    assert len(rows) == result["rows"] and result["controls_ok"] is True and result["control_failures"] == []
    for r in rows:
        p = r["consistent"] / r["samples"]
        assert abs(p - r["P"]) < 1e-12
        if r["consistent"] == 0:
            assert r["E"] is None and abs(r["E_lower_bound"] - math.log2(r["samples"])) < 1e-12
        else:
            assert abs(-math.log2(p) - r["E"]) < 1e-12
            assert abs(math.sqrt(p * (1 - p) / r["samples"]) / (p * math.log(2)) - r["se_E"]) < 1e-12
        if r["family"] == "control_bipartite" or r["family"].startswith("C1_vacuum"):
            assert r["consistent"] == r["samples"], r["label"]
        if r.get("tests_agree") is not None:
            assert r["tests_agree"] == r["doubly_judged"], r["label"]
    ok, devs = decide(rows, contract)
    assert ok == result["primary"]["H_conformal"]
    for shape, d in devs.items():
        assert abs(d - result["C2_conformal"][shape]["deviation"]) < 1e-12, shape

    # replays with independent code
    nv, edges = 9, edges_of(3, 3)
    rng = random.Random("check-brute")
    for _ in range(300):
        x = [rng.randrange(2) for _ in edges]
        brute = any(all(not (h[u] == h[v] == xe) for (u, v), xe in zip(edges, x)) for h in product((0, 1), repeat=nv))
        assert nae_extends(nv, edges, x) == brute
    replay = {}
    rec = next(r for r in rows if r["family"] == "C2_rows_odd_columns_double" and r["label"] == "9x18")
    edges = edges_of(9, 18)
    rng = random.Random("check-or-neq")
    n = 4000
    good = sum(two_colourable(162, [e for e in edges if rng.randrange(2) == 0]) for _ in range(n))
    p = good / n
    se = math.sqrt(rec["P"] * (1 - rec["P"]) * (1 / n + 1 / rec["samples"]))
    replay["or_neq 9x18"] = (round(p, 4), round(rec["P"], 4))
    assert abs(p - rec["P"]) <= 5 * se
    rec = next(r for r in rows if r["family"] == "C1_not_all_equal" and r["label"] == "9x9")
    edges = edges_of(9, 9)
    rng = random.Random("check-nae")
    n = 3000
    good = sum(nae_extends(81, edges, [rng.randrange(2) for _ in edges]) for _ in range(n))
    p = good / n
    se = math.sqrt(rec["P"] * (1 - rec["P"]) * (1 / n + 1 / rec["samples"]))
    replay["not-all-equal 9x9"] = (round(p, 4), round(rec["P"], 4))
    assert abs(p - rec["P"]) <= 5 * se

    tight, _ = decide(rows, contract, allowance=-1.0)
    assert tight is False
    print(f"checked: {len(rows)} rows, verdict {result['verdict']}, primary {result['primary']}, deviations "
          f"{ {k: round(v, 4) for k, v in devs.items()} }, replay {replay}; tightened tolerance rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
