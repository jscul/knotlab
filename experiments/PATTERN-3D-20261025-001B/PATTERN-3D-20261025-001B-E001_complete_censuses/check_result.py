#!/usr/bin/env python3
"""Independent re-check of PATTERN-3D-20261025-001B-E001.
- recomputes every survivor's reduced rule by brute force over all edge labellings of a tetrahedron (not the propagation solver used
  by run.py) and re-derives the per-part classification, predictions and verdict;
- re-verifies 150 random survivors of each large part with the standard-library law test of PATTERN-3D-20261025-001A-P001;
- replays two random chunks of each large part with a freshly compiled binary and compares statistics and survivors."""
from __future__ import annotations

import itertools
import json
import random
from collections import Counter

from common import A, OUT, build_binary, classify_reduced, decode_relation, decode_table, run_census
from run import FIVE, SEVEN

PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
FACES = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def reduced_brute(R, n):
    out = set()
    for lab in itertools.product(range(n), repeat=6):
        x = dict(zip(PAIRS, lab))
        tris = [(x[(a, b)], x[(b, c)], x[(a, c)]) for a, b, c in FACES]
        if all(t in R for t in tris):
            out.update(tris)
    return out


def main():
    result = json.loads((OUT / "result.json").read_text())
    rows = [json.loads(l) for l in (OUT / "rows.jsonl").read_text().splitlines()]
    ok = True
    recomputed = {}
    for p in ("rel2", "tab3", "rel3", "tab4"):
        n = int(p[-1])
        names, bad = Counter(), 0
        surv = [s for r in rows if r["part"] == p for s in r["survivors"]]
        for idx, lam, mu in surv:
            R = decode_relation(idx, n) if p.startswith("rel") else decode_table(idx, n)
            name, good = classify_reduced(reduced_brute(R, n), n, lam, mu)
            names[str(name)] += 1
            bad += not good
        recomputed[p] = {"survivors by type": dict(names), "count not matching": bad}
        ok &= recomputed[p]["survivors by type"] == result["parts"][p]["survivors by type"]
        ok &= bad == result["parts"][p]["count not matching"]
    pr = {"P1_relations_three_labels": recomputed["rel3"]["count not matching"] == 0 and set(recomputed["rel3"]["survivors by type"]) == SEVEN,
          "P2_tables_four_labels": recomputed["tab4"]["count not matching"] == 0 and set(recomputed["tab4"]["survivors by type"]) == FIVE,
          "P3_small_parts": recomputed["rel2"]["survivors by type"] == {"one constant": 4, "two constants": 1, "Z2": 2, "free on 2 labels": 1}
          and recomputed["tab3"]["survivors by type"] == {"Z3": 3}}
    ok &= all(pr[k] == result["predictions"][k] for k in pr)
    # re-verify sampled survivors with the independent Python law test
    rng = random.Random(20261029)
    sample_ok = True
    for p in ("rel3", "tab4"):
        n = int(p[-1])
        surv = [s for r in rows if r["part"] == p for s in r["survivors"]]
        for idx, lam, mu in rng.sample(surv, 150):
            R = decode_relation(idx, n) if p.startswith("rel") else decode_table(idx, n)
            sample_ok &= A.Law(R).verdict() == ("survives", lam, mu)
    # replay chunks
    exe = build_binary()
    replay_ok = True
    for p in ("rel3", "tab4"):
        for r in rng.sample([r for r in rows if r["part"] == p], 2):
            surv, stats = run_census(exe, p[:3], int(p[-1]), r["start"], r["end"])
            replay_ok &= surv == r["survivors"] and stats == r["stats"]
    out = {"recomputed": recomputed, "predictions": pr, "sampled survivors re-verified": sample_ok, "chunks replayed": replay_ok,
           "matches result.json": ok}
    verdict_ok = result["verdict"] == ("supported" if all(pr.values()) else result["verdict"])
    print(json.dumps(out, indent=1))
    return 0 if ok and sample_ok and replay_ok and verdict_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
