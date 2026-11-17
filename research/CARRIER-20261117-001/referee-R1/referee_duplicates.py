"""Referee R1 for CARRIER-20261117-001: how many distinct patterns the descriptions are.  Two descriptions are the same pattern when
the census's `pattern(key, N)` gives the same set of knot triples.

  ../../../.venv/bin/python -B referee_duplicates.py > referee_duplicates.json      (from this directory)

- the 25 open descriptions of KEEP-REACH (CARRIER's 12 and 13) at N = 8, 9 and 12, with the groups;
- KEEP-REACH's third class (39) and its 2,380 sampled and mutated small-orbit descriptions, and the census's 786, at N = 9;
- whether word 0 and word 2 of 8db5da810c00-73's automaton act identically on every level to 12 (the mutated pair of -73 and -79).
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
from pattern import addr, pattern  # noqa: E402

KR = ROOT / "research/KEEP-REACH-20261117-001"
THIRD = json.load(open(KR / "third_class.json"))["third"]


def sig(key, N):
    return frozenset(tuple(sorted(t)) for t in pattern(key, N).tolist())


def groups(named, N):
    g = {}
    for name, key in named:
        g.setdefault(sig(key, N), []).append(name)
    return list(g.values())


def main():
    out = {}
    twelve = ["bace53f8f952-147", "bace53f8f952-111", "bace53f8f952-58"] + [f"ca1efb37ad88-{i}" for i in
                                                                             (361, 364, 367, 375, 378, 386, 389, 418, 835)]
    thirteen = [f"8db5da810c00-{i}" for i in (73, 76, 79, 81, 84, 86, 89, 92, 94, 97, 100, 103, 106)]
    for N in (8, 9, 12):
        out[f"25_at_N{N}"] = {"twelve": groups([(n, THIRD[n]["key"]) for n in twelve], N),
                              "thirteen": groups([(n, THIRD[n]["key"]) for n in thirteen], N)}
    g = groups([(n, v["key"]) for n, v in THIRD.items()], 9)
    kinds = {n: v["kind"] for n, v in THIRD.items()}
    out["third_class_39_at_N9"] = {"descriptions": len(THIRD), "distinct": len(g),
                                   "distinct_by_kind": dict(Counter(kinds[x[0]] for x in g)),
                                   "descriptions_by_kind": dict(Counter(kinds.values()))}
    rows = [json.loads(l) for f in ("sample_keep.jsonl", "mutants_keep.jsonl") for l in open(KR / f)]
    alive = [r for r in rows if r.get("small_orbits") and r.get("alive_every_depth")]
    ga = groups([(r["index"], r["key"]) for r in alive], 9)
    forget = {r["index"] for r in alive if r.get("r_all") is not None}
    out["sample_and_mutants_2380_at_N9"] = {"descriptions": len(alive), "distinct": len(ga),
                                            "distinct_that_forget": sum(1 for x in ga if x[0] in forget)}
    census = json.load(open(KR / "census_keep.json"))["rows"]
    keys = {}
    for line in gzip.open(ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["case"] in census:
            keys[r["case"]] = r["key"]
    gc = groups(list(keys.items()), 9)
    out["census_786_at_N9"] = {"descriptions": len(keys), "distinct": len(gc)}
    s, sw, d0, d1, pls = THIRD["8db5da810c00-73"]["key"]
    W = addr.words(s)
    aut = tuple(tuple(r) for r in (sw, d0, d1))
    out["words_0_and_2_act_identically_to_level_12"] = all(np.array_equal(addr.action(aut, W[0], n), addr.action(aut, W[2], n))
                                                           for n in range(1, 13))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
