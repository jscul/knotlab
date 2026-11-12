#!/usr/bin/env python3
"""Referee STEER-LEARN-R1: the harness's arithmetic and the marks, with the referee's own code.

    .venv/bin/python3 -B ref_steer.py      (writes result_referee.json)

- The maps of the laws at rest are taken as data from the frozen harness (`check.py`'s rest_maps, which reads them by SAT); the
  referee does not rebuild the engines F and GE or the rest sets (that census is the earlier epics', V1 here).
- From those maps, with the referee's own code: each target's share of the interface's own flips (every input flip and the output
  flip), the chance per blind draw, the swap target by the frozen closest-chance rule, and the exact blind median of a geometric
  count of draws.
- From runs.jsonl, with the referee's own tallies: for every (setting, rule, target) the found count, the median charged and world
  probes (unfound runs count as never), the share found within the blind median, the frozen mark, and the same mark on world probes
  alone; the charging identity (charged = world + candidate checks; none for B and P).
- Claim 3: in the swap-target runs of F, how often the walk's law computed the count at some probe before the stop, against what
  blind draws would give over the same number of probes."""
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPIC = HERE.parent
sys.path.insert(0, str(EPIC))

XOR, NXOR = "01101001", "10010110"


def variants(m):
    pats = list(itertools.product((0, 1), repeat=3))
    pos = {x: i for i, x in enumerate(pats)}
    out = []
    for f in itertools.product((0, 1), repeat=3):
        for o in (0, 1):
            w = ""
            for x in pats:
                c = m[pos[tuple(a ^ b for a, b in zip(x, f))]]
                w += {"0": "1", "1": "0"}.get(c, c) if o else c
            out.append(w)
    return out


def median_draws(p):
    """smallest m with 1 - (1 - p)^m >= 1/2"""
    m = 1
    while 1 - (1 - p) ** m < 0.5:
        m += 1
    return m


def main():
    import check as C           # the frozen harness, used only as the source of the maps at rest
    out = {"harness": {}, "marks": {}, "claim 3": {}}
    for setting in ("F", "GE"):
        maps = [m for _, m in C.rest_maps(setting)]
        share = {}
        for m in maps:
            for v in variants(m):
                share[v] = share.get(v, 0) + 1 / (16 * len(maps))
        p_xor = share.get(XOR, 0)
        cands = sorted(t for t in share if t not in (XOR, NXOR) and "x" not in t)
        g = min(cands, key=lambda t: (abs(share[t] - p_xor), t))
        out["harness"][setting] = {"laws at rest": len(maps), "distinct maps": sorted(set(maps)), "p(count)": p_xor,
                                   "blind median (count)": median_draws(p_xor), "g": g, "p(g)": share[g],
                                   "blind median (g)": median_draws(share[g]), "1/p": [1 / p_xor, 1 / share[g]]}
    rows = [json.loads(l) for l in open(EPIC / "runs.jsonl")]
    out["runs"] = len(rows)
    out["dropped at the time cap"] = sum(1 for r in rows if r.get("dropped (time cap)"))
    out["charging identity holds"] = all(r["charged probes"] == r["world probes"] + r["candidate checks"] for r in rows if "charged probes" in r)
    out["no candidate checks for B and P"] = all(r["candidate checks"] == 0 for r in rows if r["rule"] in "BP" and "candidate checks" in r)
    INF = math.inf
    for setting in ("F", "GE"):
        h = out["harness"][setting]
        for target, bm in ((XOR, h["blind median (count)"]), (h["g"], h["blind median (g)"])):
            for rule in "BPMA":
                rs = [r for r in rows if r["setting"] == setting and r["target"] == target and r["rule"] == rule]
                ch = [r["charged probes"] if r["found"] else INF for r in rs]
                wp = [r["world probes"] if r["found"] else INF for r in rs]
                mc, mw = statistics.median(ch), statistics.median(wp)
                wc = sum(c <= bm for c in ch) / len(rs)
                ww = sum(c <= bm for c in wp) / len(rs)
                out["marks"][f"{setting} {target} {rule}"] = {
                    "runs": len(rs), "found": sum(r["found"] for r in rs), "dropped": sum(1 for r in rs if r.get("dropped (time cap)")),
                    "median charged": mc if mc < INF else "never", "median world": mw if mw < INF else "never",
                    "within blind (charged)": wc, "within blind (world)": ww,
                    "passes (frozen, charged)": mc <= bm / 2 and wc >= 0.75, "would pass on world probes": mw <= bm / 2 and ww >= 0.75}
    # claim 3: the count's laws met during the swap-target runs of F, against blind draws over the same probes
    for setting in ("F", "GE"):
        g = out["harness"][setting]["g"]
        p = out["harness"][setting]["p(count)"]
        for rule in "BPMA":
            rs = [r for r in rows if r["setting"] == setting and r["target"] == g and r["rule"] == rule and not r.get("dropped (time cap)")]
            seen = sum(1 for r in rs if r["xor seen at probe"] is not None)
            # blind: P(at least one count draw among the probes before the stop) = 1 - (1 - p)^(probes - 1), averaged
            exp = sum(1 - (1 - p) ** max(0, r["world probes"] - 1) for r in rs) / len(rs) if rs else None
            out["claim 3"][f"{setting} {rule}"] = {"runs (not dropped)": len(rs), "count met before the stop": seen,
                                                  "share": seen / len(rs) if rs else None, "blind draws would give": exp}
    (HERE / "result_referee.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out["harness"], indent=1))


if __name__ == "__main__":
    main()
