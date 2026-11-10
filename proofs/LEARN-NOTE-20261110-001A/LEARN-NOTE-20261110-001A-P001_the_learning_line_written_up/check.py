#!/usr/bin/env python3
"""Checks for LEARN-NOTE-20261110-001A: every number in research/LEARN-NOTE-20261110-001/learning_line.md against the record it cites.

    python3 -B check.py [--write]
Reads the committed result files of the fifteen epics; no computation is rerun."""
import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def res(pattern):
    return json.loads(Path(glob.glob(str(ROOT / pattern))[0]).read_text())


def info(r, prefix):
    return next(v["info"] for k, v in r["checks"].items() if k.startswith(prefix))


def main():
    c = {}
    lh = res("proofs/LEARN-HANDLES-20261109-001A/*/result.json")
    c["1 walks 96,732"] = info(lh, "3")["totals"]["walks"] == 96732
    c["1 tori 59"] = info(lh, "1")["tori"] == 59
    c["1 local rule 9,608 of 9,608"] = info(lh, "5")["no_reversal resolved"] == 9608 == info(lh, "5")["of"]
    gh = res("proofs/GROW-HANDLE-20261110-001A/*/result.json")
    stress = json.loads((ROOT / "research/GROW-HANDLE-20261110-001/stress_test.json").read_text())
    c["3 grown tori 540"] = info(gh, "2")["of"] + stress["grown tori"] == 540
    cr = res("artifacts/CHOOSE-RES-20261110-001A/*/run/result.json")
    hits = sum(r[d]["C7 hit"] for r in cr["rows"] for d in ("01", "10", "11") if d in r)
    tot = sum(1 for r in cr["rows"] for d in ("01", "10", "11") if d in r)
    c["4 targets 3,173 of 3,186"] = (hits, tot) == (3173, 3186)
    ms = res("artifacts/MOVING-STATE-20261110-001A/*/run/result.json")
    g1 = sum(r["M"]["final W"].get("0.0", 0) for r in ms["rows"] if r["atoms"] == "away (d = 2)")
    g2 = sum(r["M"]["final W"].get("1.0", 0) for r in ms["rows"] if r["atoms"] == "away (d = 2 and 3)")
    c["7 freed 23 and 28 of 50"] = (g1, g2) == (23, 28)
    lw = res("proofs/LAW-HOLDS-20261110-001A/*/result.json")
    c["9 spaces 15"] = len(lw["rows"]) == 15
    ad = res("proofs/ADDRESS-20261110-001A/*/result.json")
    c["11 pairs 9 of 9, fresh 6 of 6"] = (info(ad, "2")["reached"], info(ad, "1")["reached"]) == (9, 6)
    ra = res("proofs/READ-ADDRESS-20261110-001A/*/result.json")
    c["12 K_4 15 of 15, read 23 of 24"] = (info(ra, "1")["written"], info(ra, "2")["hold"], info(ra, "2")["of"]) == (15, 23, 24)
    sa = res("proofs/ADDRESS-STEER-20261110-001A/*/result.json")
    c["13 classes 1,280, spaces 11"] = (info(sa, "1")["classes"], info(sa, "1")["spaces"]) == (1280, 11)
    sb = res("proofs/ADDRESS-STEER-20261110-001B/*/result.json")
    c["13 four atoms 12 of 12"] = info(sb, "1")["reached"] == 12
    seqb = res("proofs/ADDRESS-SEQ-20261110-001B/*/result.json")["checks"]["1 B (computed)"]["info"]
    ob = seqb["outcomes by k"]
    kept23 = ob["2: kept"] + ob["3: kept"]
    c["13 one flip 240 of 240, two or three 463 of 480"] = ob["1: kept"] == 240 and kept23 == 463
    c["5 erasures 7, stuck 10"] = (seqb["changed at the floor"], seqb["above the floor"]) == (7, 10)
    sq = res("proofs/ADDRESS-SEQ-20261110-001A/*/result.json")
    c["14 writes 90, spaces 14"] = info(sq, "1")["written"] == 90 and len(info(sq, "1")["rows"]) == 14
    ar = res("proofs/ATOM-RULE-20261110-001A/*/result.json")
    c["15 splices 2,700, types 4, none new beyond K_3"] = (info(ar, "1")["splices"] == 2700 and info(ar, "2")["types"] == 4
                                                         and max(info(ar, "2")["first appearance"].values()) == 3)
    out = {"status": "passed" if all(c.values()) else "failed", "checks": c}
    print(json.dumps(out, indent=1))
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1) + "\n")
    sys.exit(0 if all(c.values()) else 1)


if __name__ == "__main__":
    main()
