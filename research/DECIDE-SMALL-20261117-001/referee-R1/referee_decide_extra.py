"""Referee R1 for DECIDE-SMALL-20261117-001, additions (own code).

  ../../../.venv/bin/python -B referee_decide_extra.py > referee_decide_extra.json      (from this directory)
  ../../../.venv/bin/python -B referee_decide_extra.py 6 (or 7)                       (part 6 or 7 alone, into the existing output)

5. The overlap one size past: the 627 against KEEP-REACH's and the census's descriptions at depth 16 as well as 12, and the union of
   the three populations (the note's "1,000 and more").
6. Patterns where nothing joins the ends: by union-find on the knot triples of pattern(key, 10), for each of the 627, whether a
   level-3 address lies in any knot, and for s = 1..4 whether any component holds addresses at both level 3 and level 3 + s. Where
   none does, no bond meets both levels at depth 10 (Lemma J), so the reading there is "none", not a growth by forgetting.
   Every knot spans at most one level (checked), so a component that misses levels 4 to 7 at depth 10 misses them at every depth.
7. T4's combination of carriers (the owner's point (b)), for the 2 patterns T4 decides: at depths 9 and 10 and s = 1..5, the least
   bond within T4's maximum in each kind of piece (two-orbit, orbit-and-block, stem of depth 2), by the referee's SAT tools.
   Whether one kind covers every cell, or only the combination does.
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
from pattern import pattern  # noqa: E402
from referee_decide import sig, DS, KR  # noqa: E402  (the digest of a clause set)


def populations():
    kr = [json.loads(l) for f in ("sample_keep.jsonl", "mutants_keep.jsonl") for l in open(KR / f)]
    kr_keys = [r["key"] for r in kr if r.get("small_orbits") and r.get("alive_every_depth")]
    census = json.load(open(KR / "census_keep.json"))["rows"]
    cen_keys = []
    for line in gzip.open(ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["case"] in census:
            cen_keys.append(r["key"])
    pats = [json.loads(l) for l in open(DS / "patterns.jsonl")]
    return pats, kr_keys, cen_keys


def part5(pats, kr_keys, cen_keys):
    out = {}
    for N in (12, 16):
        mine = {sig(p["key"], N) for p in pats}
        kr = {sig(k, N) for k in kr_keys}
        cen = {sig(k, N) for k in cen_keys}
        out[N] = {"study": len(mine), "keep_reach": len(kr), "census": len(cen), "keep_reach_and_census": len(kr & cen),
                  "study_seen_before": len(mine & (kr | cen)), "study_new": len(mine - kr - cen), "union_of_all_three": len(mine | kr | cen)}
        print("part5", N, json.dumps(out[N]), file=sys.stderr, flush=True)
    return out


def level_of(a):
    n = 0
    while (1 << (n + 1)) - 1 <= a:
        n += 1
    return n


def part6(pats, N=10):
    rows = []
    for p in pats:
        K = pattern(p["key"], N).tolist()
        par = list(range((1 << (N + 1)) - 1))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        touched = set()
        for t in K:
            touched.update(t)
            for x in t[1:]:
                rx, ry = find(t[0]), find(x)
                if rx != ry:
                    par[rx] = ry
        lv3 = range(7, 15)
        top = {find(a) for a in lv3 if a in touched}
        joined = []
        for s in range(1, 5):
            lo = range((1 << (3 + s)) - 1, (1 << (4 + s)) - 1)
            joined.append(any(find(a) in top for a in lo if a in touched))
        span = max((level_of(max(t)) - level_of(min(t)) for t in K), default=None)
        rows.append({"index": p["index"], "verdict": p["verdict"], "knots": len(K), "largest_level_span_of_a_knot": span,
                     "level3_in_a_knot": any(a in touched for a in lv3), "ends_joined_s1_to_4": joined})
    tally = Counter((r["verdict"], "empty" if r["knots"] == 0 else ("level 3 in no knot" if not r["level3_in_a_knot"] else
                     ("ends never joined" if not any(r["ends_joined_s1_to_4"]) else
                      ("ends joined at every s" if all(r["ends_joined_s1_to_4"]) else "ends joined at some s"))))
                    for r in rows)
    return {"depth": N, "tally": {f"{a} | {b}": v for (a, b), v in sorted(tally.items())},
            "largest_level_span_of_a_knot": dict(Counter(str(r["largest_level_span_of_a_knot"]) for r in rows)),
            "span_0_and_not_joined": sum(1 for r in rows if r["largest_level_span_of_a_knot"] == 0 and not any(r["ends_joined_s1_to_4"])),
            "not_joined_at_every_s": [r for r in rows if not all(r["ends_joined_s1_to_4"])]}


def part7(pats):
    from referee_decide import KPattern, C
    out = {}
    for p in pats:
        if p["verdict"] != "bounded (T4)":
            continue
        rows = []
        for N in (9, 10):
            P = KPattern(p["key"], N)
            for s in range(1, min(5, N - 3) + 1):
                cell = {"N": N, "s": s}
                for kind in ("two", "block", "stem"):
                    if kind == "stem" and s <= 2:
                        cell[kind] = "n/a"
                        continue
                    b, _ = C.least_over_pairs(P, s, kind, cap=p["T4_max"], want=0)
                    cell[kind] = b
                rows.append(cell)
                print("part7", p["index"], json.dumps(cell), file=sys.stderr, flush=True)
        ok = lambda c, kinds: any(isinstance(c[k], int) and c[k] <= p["T4_max"] for k in kinds)
        out[p["index"]] = {"T4_max": p["T4_max"], "cells": rows,
                           "every_cell_held": all(ok(c, ("two", "block", "stem")) for c in rows),
                           "held_by_blocks_alone": all(ok(c, ("block",)) for c in rows),
                           "held_by_stems_alone": all(ok(c, ("stem",)) for c in rows),
                           "held_by_two_orbit_alone": all(ok(c, ("two",)) for c in rows)}
    return out


def main():
    if sys.argv[1:] == ["6"]:                       # part 6 alone, into the existing output
        out = json.load(open(HERE / "referee_decide_extra.json"))
        out["6_ends_joined"] = part6([json.loads(l) for l in open(DS / "patterns.jsonl")])
        json.dump(out, open(HERE / "referee_decide_extra.json", "w"), indent=1)
        return
    if sys.argv[1:] == ["7"]:                       # part 7 alone, into the existing output
        out = json.load(open(HERE / "referee_decide_extra.json"))
        out["7_T4_carriers"] = part7([json.loads(l) for l in open(DS / "patterns.jsonl")])
        json.dump(out, open(HERE / "referee_decide_extra.json", "w"), indent=1)
        return
    pats, kr_keys, cen_keys = populations()
    out = {"6_ends_joined": part6(pats)}
    print("part6", json.dumps(out["6_ends_joined"]["tally"]), file=sys.stderr, flush=True)
    out["5_overlap_at_12_and_16"] = part5(pats, kr_keys, cen_keys)
    out["7_T4_carriers"] = part7(pats)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
