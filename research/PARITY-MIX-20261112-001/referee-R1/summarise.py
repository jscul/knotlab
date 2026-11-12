#!/usr/bin/env python3
"""Referee PARITY-MIX-R1: summaries of result_p3.jsonl / result_p4.jsonl (every placement), against the census's weighted rows.

    python3 -B summarise.py p3|p4"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parents[2] / "proofs" / "PARITY-MIX-20261112-001A" / "PARITY-MIX-20261112-001A-P001_parity_among_copies"


def read_lines(path):
    """the rows, from the plain file or its gzip copy (result_p4.jsonl is kept compressed)"""
    if path.exists():
        return path.read_text().splitlines()
    with gzip.open(str(path) + ".gz", "rt") as fh:
        return fh.read().splitlines()


def mine(part):
    rows = [json.loads(l) for l in read_lines(HERE / f"result_{part}.jsonl")]
    n = rows[0]["n"]
    nm = n * n
    tot = Counter()
    src = Counter()
    by_k = {}
    per_h = {}
    for res in rows:
        ph = Counter()
        for r in res["rows"]:
            k = r["k"]
            band = "k = 0" if k == 0 else ("k = nm" if k == nm else "1 <= k < nm")
            tot[band, "placements"] += 1
            if r["state"]:
                tot[band, "with a state"] += 1
                tot[band, "fixed but unreached"] += r["fixed but unreached"] > 0
                tot[band, "full fixing"] += r["full fixing"]
                if band == "1 <= k < nm":
                    ph["survivors"] += 1
                    ph["fixed but unreached"] += r["fixed but unreached"] > 0
                    b = by_k.setdefault(k, Counter())
                    b["survivors"] += 1
                    b["fixed but unreached"] += r["fixed but unreached"] > 0
                    b["full fixing"] += r["full fixing"]
                    for s in r.get("sources", []):
                        src[s] += 1
                    if r.get("sources"):
                        src["placements, deepest source: " + max(r["sources"], key=["B1 parity algebra", "B2 parity and states", "BN stitches alone", "only the whole"].index)] += 1
                if band == "k = 0":
                    for s in r.get("sources", []):
                        src["k = 0: " + s] += 1
            if band == "1 <= k < nm":
                b = by_k.setdefault(k, Counter())
                b["placements"] += 1
        per_h[res["harmony"]] = dict(ph)
    return {"totals": {f"{a}: {b}": v for (a, b), v in sorted(tot.items())}, "fixed-but-unreached counts by source (1 <= k < nm)": dict(src),
            "by k": {k: dict(v) for k, v in sorted(by_k.items())}, "per harmony": per_h}


def theirs(part):
    res = json.loads((CENSUS / f"result_{part}.json").read_text())["checks"]["result"]["rows"]
    n = 3 if part == "p3" else 4
    nm = n * n
    tot = Counter()
    for h in res:
        for r in h["rows"]:
            k, w = r["k"], r["weight"]
            band = "k = 0" if k == 0 else ("k = nm" if k == nm else "1 <= k < nm")
            tot[band, "placements"] += w
            if r["state"]:
                tot[band, "with a state"] += w
                tot[band, "fixed but unreached"] += w * (r["fixed but unreached counts"] > 0)
                tot[band, "full fixing"] += w * bool(r["full fixing"])
    return {f"{a}: {b}": v for (a, b), v in sorted(tot.items())}


if __name__ == "__main__":
    part = sys.argv[1]
    out = {"referee (every placement)": mine(part), "census (classes weighted by size)": theirs(part)}
    (HERE / f"summary_{part}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
