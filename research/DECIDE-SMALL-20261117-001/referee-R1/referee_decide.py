"""Referee R1 for DECIDE-SMALL-20261117-001 (own code; decide.py is not imported; its outputs are only compared).

  ../../../.venv/bin/python -B referee_decide.py > referee_decide.json      (from this directory)
  ../../../.venv/bin/python -B referee_decide.py 4                          (part 4 alone, into the existing output)

1. Counting on distinct patterns: the 627 against KEEP-REACH's 2,380 small-orbit descriptions and the census's 786, all as clause
   sets of pattern(key, 12): how many of the 627 are new.
2. The dedup one size past: every kept draw against its group's first draw at depth 16 (the study rechecked at 14).
3. Early exit, by the referee's SAT tools (KEEP-REACH-R1, CARRIER-R1), on a seeded sample:
   - 40 patterns that T1 says grow: every two-orbit bond found at N = 8, s = 1..5, has at least 1 + ceil(s / r) members (Theorem
     F's bound), so no two-orbit bond contradicts the verdict; and their joints r levels apart are products;
   - 40 patterns that T2 says are bounded: a two-orbit bond exists at N = 8 for every s = 1..5.
4. The 33 undecided ground-truth cells: for each with a lower bound, whether a bond of two members meets levels 3 and 3 + s at depth
   9 (none, when each pair's joint is full: then L_9 >= 3); for the bounded ones, a bond within the upper bound at depth 9 (in a
   two-orbit, stem or orbit-and-block piece).
"""
import hashlib
import itertools
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CARRIER-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KEEP-REACH-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
import referee_carrier as C  # noqa: E402  (the referee's own SAT tools)
from pattern import pattern  # noqa: E402
from pysat.solvers import Cadical195  # noqa: E402
from referee_two_orbit_sat import check_b, check_forget  # noqa: E402  (the referee's KEEP-REACH-R1 SAT checks)

DS = ROOT / "research/DECIDE-SMALL-20261117-001"
KR = ROOT / "research/KEEP-REACH-20261117-001"


def sig(key, N):
    """The pattern's clause set at depth N, as a digest of its sorted, row-sorted knot triples (equal digests = equal clause sets)."""
    K = np.sort(np.asarray(pattern(key, N), dtype=np.int64), axis=1)
    K = np.unique(K, axis=0) if len(K) else K.reshape(0, 3)
    return hashlib.sha256(K.tobytes()).hexdigest()


def part1():
    pats = [json.loads(l) for l in open(DS / "patterns.jsonl")]
    mine = {sig(p["key"], 12) for p in pats}
    kr = [json.loads(l) for f in ("sample_keep.jsonl", "mutants_keep.jsonl") for l in open(KR / f)]
    kr_sigs = {sig(r["key"], 12) for r in kr if r.get("small_orbits") and r.get("alive_every_depth")}
    import gzip
    census = json.load(open(KR / "census_keep.json"))["rows"]
    keys = {}
    for line in gzip.open(ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["case"] in census:
            keys[r["case"]] = r["key"]
    cen_sigs = {sig(k, 12) for k in keys.values()}
    return {"study_patterns": len(pats), "distinct_at_12": len(mine), "keep_reach_distinct": len(kr_sigs),
            "census_distinct": len(cen_sigs), "in_keep_reach": len(mine & kr_sigs), "in_census": len(mine & cen_sigs),
            "in_either": len(mine & (kr_sigs | cen_sigs)), "new": len(mine - kr_sigs - cen_sigs)}


def part2(N=16):
    draws = [json.loads(l) for l in open(DS / "draws.jsonl")]
    kept = [d for d in draws if d.get("kept") == "small, alive"]
    first = {}
    for d in kept:
        if d.get("first"):
            first[d["pattern"]] = d
    rep_sig = {p: sig(d["key"], N) for p, d in first.items()}
    split = sum(1 for d in kept if not d.get("first") and sig(d["key"], N) != rep_sig[d["pattern"]])
    distinct_reps = len(set(rep_sig.values()))
    return {"kept_draws": len(kept), "groups": len(first), "merged_draws_rechecked_at_16": sum(1 for d in kept if not d.get("first")),
            "split_at_16": split, "group_representatives_distinct_at_16": distinct_reps}


def part3(sample=40):
    pats = [json.loads(l) for l in open(DS / "patterns.jsonl")]
    rng = random.Random(11)
    t1 = [p for p in pats if p["verdict"] == "grows (T1)"]
    t2 = [p for p in pats if p["verdict"] == "bounded (T2)"]
    out = {"T1": [], "T2": []}
    for p in rng.sample(t1, sample):
        r = p["T1_r"]
        b = check_b(p["key"], 8)
        bad = [s for s, v in (b.get("b") or {}).items() if v is not None and v < 1 + math.ceil(int(s) / r)]
        f = check_forget(p["key"], 8, r)
        out["T1"].append({"index": p["index"], "r": r, "b8": b.get("b"), "two_orbit_bonds_below_F_bound": bad,
                          "non_product_joints_at_r": f.get("non_product_count")})
        print("T1", p["index"], r, b.get("b"), bad, f.get("non_product_count"), file=sys.stderr, flush=True)
    for p in rng.sample(t2, sample):
        b = check_b(p["key"], 8)
        out["T2"].append({"index": p["index"], "b8": b.get("b"), "bond_at_every_s": all(v is not None for v in b["b"].values())})
        print("T2", p["index"], b.get("b"), file=sys.stderr, flush=True)
    out["summary"] = {"T1_contradictions": sum(1 for x in out["T1"] if x["two_orbit_bonds_below_F_bound"]),
                      "T1_non_product_joints": sum(x["non_product_joints_at_r"] or 0 for x in out["T1"]),
                      "T2_missing_bonds": sum(1 for x in out["T2"] if not x["bond_at_every_s"])}
    return out


class KPattern(C.Pattern):
    def __init__(self, key, N):
        self.idx, self.N, self.key = None, N, key
        K = pattern(key, N)
        self.cl = []
        for a, b, c in K.tolist():
            self.cl.append([a + 1, b + 1, c + 1])
            self.cl.append([-(a + 1), -(b + 1), -(c + 1)])
        self.orb = {n: C.orbits(key, n) for n in range(0, N + 1)}
        self.where = {n: {y: i for i, o in enumerate(self.orb[n]) for y in o} for n in self.orb}


def part4():
    gt = json.load(open(DS / "ground_truth.json"))
    pats = {p["index"]: p for p in (json.loads(l) for l in open(DS / "patterns.jsonl"))}
    out = []
    for row in gt["rows"]:
        for cell in row["cells"]:
            if cell["L9"] != "undecided":
                continue
            key = pats[row["index"]]["key"]
            s = cell["s"]
            P = KPattern(key, 9)
            res = {"index": row["index"], "verdict": row["verdict"], "s": s, "lower": cell["lower"], "upper": cell["upper"]}
            if cell["lower"] is not None:
                # no bond of two members across levels 3 and 3 + s: every pair's joint is full
                pairs_constrained = 0
                with Cadical195(bootstrap_with=P.cl) as S:
                    for v in range((1 << (P.N + 1)) - 1):            # register every address, even one no knot mentions
                        S.add_clause([v + 1, -(v + 1)])
                    for u in range(8):
                        for v in range(1 << (3 + s)):
                            a, b = C.vid(3, u), C.vid(3 + s, v)
                            if not all(S.solve(assumptions=[(a + 1) if x else -(a + 1), (b + 1) if y else -(b + 1)])
                                       for x in (0, 1) for y in (0, 1)):
                                pairs_constrained += 1
                res["two_member_bonds"] = pairs_constrained
                res["L9_at_least_3"] = pairs_constrained == 0
                # fits when the lower bound is 2 (every bond has two members), or 3 with no bond of two members
                res["fits"] = True if cell["lower"] <= 2 or (cell["lower"] <= 3 and pairs_constrained == 0) else "not shown"
            if cell["upper"] is not None:
                best = None
                for kind in ("two", "stem", "block"):
                    if kind == "stem" and s <= 2:
                        continue
                    b, arg = C.least_over_pairs(P, s, kind, cap=cell["upper"], want=cell["upper"])
                    if b is not None and (best is None or b < best):
                        best = b
                    if best is not None and best <= cell["upper"]:
                        break
                res["bond_within_upper_found"] = best
                res["fits"] = best is not None and best <= cell["upper"]
            out.append(res)
            print("gt", json.dumps(res), file=sys.stderr, flush=True)
    return out


def main():
    if sys.argv[1:] == ["4"]:                       # rerun part 4 alone into the existing output
        out = json.load(open(HERE / "referee_decide.json"))
        out["4_undecided_ground_truth"] = part4()
        out["4_summary"] = Counter(str(r.get("fits")) for r in out["4_undecided_ground_truth"])
        json.dump(out, open(HERE / "referee_decide.json", "w"), indent=1, default=str)
        return
    out = {"1_counts": part1()}
    print("part 1", json.dumps(out), file=sys.stderr, flush=True)
    out["2_dedup_at_16"] = part2()
    print("part 2", json.dumps(out["2_dedup_at_16"]), file=sys.stderr, flush=True)
    out["4_undecided_ground_truth"] = part4()
    out["4_summary"] = Counter(str(r.get("fits")) for r in out["4_undecided_ground_truth"])
    out["3_early_exit_sample"] = part3()
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
