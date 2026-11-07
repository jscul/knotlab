#!/usr/bin/env python3
"""Checks for SPHERE-SIZE-20261107-001A: islands keep the count hard.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, python-sat). Single process; a few minutes."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import island_lib as I  # noqa: E402

W = I.W
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def audit(K, s, dsep, trials, rng):
    n_cert = n_sum = bad_neg = bad_bound = 0
    same_min, betw_min, ratio, states, nisl = None, None, 0.0, 0, []
    for _ in range(trials):
        isl = I.greedy_packing(K, s, dsep, rng)
        nisl.append(len(isl))
        col = I.island_colours(K, isl, [rng.randrange(6) for _ in isl])
        d_isl = W.bfs(K["adj"], list(col), K["n"])
        free = [p for p in range(K["n"]) if p not in K["corner_pts"] and d_isl[p] >= 2]
        z = rng.choice(free)
        T = I.trivialize_avoiding(K, z, isl)
        if T is None:
            continue
        x = I.random_compatible_state(K, z, T, col, rng)
        if x is None:
            continue
        states += 1
        cs = [cc for cc, _ in isl]
        a_, b_ = min(((u, v) for u in cs for v in cs if u < v), key=lambda ab: W.bfs(K["adj"], [ab[0]], K["n"])[ab[1]] + rng.random())
        da, db = W.bfs(K["adj"], [a_], K["n"]), W.bfs(K["adj"], [b_], K["n"])
        mids = [p for p in range(K["n"]) if abs(da[p] - db[p]) <= 1 and da[p] + db[p] == da[b_] + (da[b_] % 2)]
        c = rng.choice(mids)
        dcen = W.bfs(K["adj"], [c], K["n"])
        r = da[c] + rng.choice((0, 1))
        sp = {p for p in range(K["n"]) if dcen[p] == r and p not in col}
        peb = dict(col)
        peb.update({p: x[p] for p in sp})
        inside = [p for p in free if dcen[p] < r and p not in sp]
        for z2 in rng.sample(inside, min(4, len(inside))):
            T2 = I.trivialize_avoiding(K, z2, isl)
            if T2 is None:
                continue
            cert = W.obstruction(K, T2, peb)
            if cert is None:
                continue
            tot, bneg, smin, bsl, L, rr = I.term_audit(K, T2, isl, col, peb, sp, cert)
            n_cert += 1
            n_sum += tot <= -1
            bad_neg += bneg
            bad_bound += bsl is not None and bsl < 0
            if smin is not None:
                same_min = smin if same_min is None else min(same_min, smin)
            if bsl is not None:
                betw_min = bsl if betw_min is None else min(betw_min, bsl)
            ratio = max(ratio, L / max(rr, 1))
    return dict(packings=trials, islands=nisl, compatible_states=states, certificates=n_cert, sum_le_minus1=n_sum,
                negative_terms_away_from_spoiler=bad_neg, between_bound_violations=bad_bound, min_same_island_term=same_min,
                min_slack_between_island_bound=betw_min, max_length_per_spoiler_pebble=round(ratio, 1))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. without Spoiler pebbles, island restrictions admit a state at every tested free vortex position
    info1, ok1 = {}, True
    rng = random.Random(4)
    for k, s, dsep in ((14, 1, 6), (18, 2, 8), (26, 2, 17)):
        K = W.sphere(k)
        feas = tried = 0
        nisl = []
        for _ in range(6):
            isl = I.greedy_packing(K, s, dsep, rng)
            nisl.append(len(isl))
            col = I.island_colours(K, isl, [rng.randrange(6) for _ in isl])
            d_isl = W.bfs(K["adj"], list(col), K["n"])
            free = [p for p in range(K["n"]) if p not in K["corner_pts"] and d_isl[p] >= 2]
            for z in rng.sample(free, 3):
                T = I.trivialize_avoiding(K, z, isl)
                if T is None:
                    continue
                tried += 1
                feas += W.feasible(K, T, col)[0]
        ok1 &= tried > 0 and feas == tried
        info1["k=%d, s=%d, separation %d" % (k, s, dsep)] = {"islands per packing (greedy, maximal)": nisl,
                                                              "vortex positions feasible": "%d of %d" % (feas, tried)}
    check("1 islands alone never obstruct: for maximal packings of radius-s islands with random constant labels, the window criterion "
          "admits a label state at every tested free vortex position", ok1, info1)

    # 2. certificate audits with Spoiler rings through two islands
    info2, ok2 = {}, True
    rng = random.Random(9)
    for k, s, dsep, trials in ((14, 1, 6, 8), (18, 2, 6, 8), (30, 1, 17, 5)):
        K = W.sphere(k)
        res = audit(K, s, dsep, trials, rng)
        good = res["certificates"] > 0 and res["sum_le_minus1"] == res["certificates"] and res["between_bound_violations"] == 0 \
            and (res["min_same_island_term"] is None or res["min_same_island_term"] >= 0) \
            and (dsep < 17 or res["negative_terms_away_from_spoiler"] == 0)
        ok2 &= good
        info2["k=%d, s=%d, separation %d" % (k, s, dsep)] = res
    check("2 certificates with islands (Spoiler rings through two islands; island-relative arc representatives): every certificate sums "
          "to <= -1, same-island terms are >= 0, terms between different islands obey b >= floor((dist - 11)/6), and at separation 17 no "
          "negative term lies away from a Spoiler pebble", ok2, info2)

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
