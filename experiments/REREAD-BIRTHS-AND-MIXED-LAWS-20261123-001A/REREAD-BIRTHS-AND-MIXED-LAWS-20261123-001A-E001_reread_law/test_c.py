"""Test (c): the 1,024 sparse draws per law of REVIEW-LEADS-20261123-001A ticket A (seed 2026112301), under R with one
convention, 12 rounds or 5,000 knots, beside ordinary growth (the recorded driver).  Also part of row G: every round small
enough is compared with the recorded code (groups, lookahead; and, with no short knot, the whole round).

One JSON line per draw: the ordinary history (outcome, births per round, first failing step of the operator test) and
the R history (outcome, residual stall and where, knots per stage, births, payments and paid births per round, short
knots, implied births, the largest number of holders after each round, first failing step, growth kind both ways).
The stages needed by test (a) (up to the stage after the last one of at most 22 distinctions) go to a separate file.

Run from the repo root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --law L --conv O|N --arm A
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402

HORIZON, CAP = 12, 5000


def history_row(g):
    maxh = []
    return {"outcome": g.outcome, "rounds": len(g.rounds), "n_at": g.n_at, "births": g.births_per_round(),
            "payments": [r["payments"] for r in g.rounds], "paid_births": [r["paid_births"] for r in g.rounds],
            "short_knots": [r["short_knots"] for r in g.rounds], "implied": [r["implied"] for r in g.rounds],
            "fresh_lower_bound": [r["fresh_lower_bound"] for r in g.rounds],
            "max_holders": g.max_holders(), "first_failing_step": rlaw.first_failing_step(g),
            "growth_kind": rlaw.recorded_growth_kind(g), "growth_kind_births": rlaw.growth_kind_births(g.births_per_round()),
            "residual": (list(map(list, g.last.residual)) if g.outcome == "residual_stall" else None),
            "residual_short": (list(map(list, g.last.shortages)) if g.outcome == "residual_stall" else None),
            "elim_vs_shortcut": sum(r["elim_vs_shortcut"] or 0 for r in g.rounds),
            "check_log": dict(g.check_log)}


def run_with_holders(stars, law, conv):
    """R, recording the largest number of holders after each round."""
    g = rlaw.Growth(stars, law, "R", conv, check=True)
    holders_by_round = [g.max_holders()]
    while g.outcome is None and len(g.rounds) < HORIZON:
        r = g.plan(max_births=max(0, CAP - len(g.stars)))
        g.last = r
        if r.status == "extend":
            g.apply(r)
            holders_by_round.append(g.max_holders())
            if g.outcome == "cap" and len(g.rounds) == HORIZON:
                g.outcome = None
        else:
            g.outcome = r.status
    if g.outcome is None:
        g.outcome = "horizon"
    return g, holders_by_round


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, choices=rlaw.LAWS)
    ap.add_argument("--conv", required=True, choices=("O", "N"))
    ap.add_argument("--arm", type=int, required=True, choices=(0, 1, 2, 3))
    args = ap.parse_args()
    t_run = time.time()
    rows, prefixes = [], []
    for dr in rlaw.lib.p3_draws():
        if dr["arm"] != args.arm:
            continue
        t0 = time.time()
        ref = rlaw.ordinary_reference(dr["stars"], args.law, HORIZON, CAP)
        g, hb = run_with_holders(dr["stars"], args.law, args.conv)
        row = {"arm": dr["arm"], "draw": dr["draw"], "n": dr["n"], "law": args.law, "conv": args.conv,
               "ord_outcome": ref["outcome"], "ord_rounds": ref["steps"], "ord_births": [len(s) for s in ref["births"]],
               "ord_first_failing_step": rlaw.lib.first_failing_stage(ref["stars"], ref["n_at"]),
               "ord_growth_kind": rlaw.lib.growth_kind(ref), "ord_n_at": ref["n_at"]}
        row.update(history_row(g))
        row["max_holders_by_round"] = hb
        row["seconds"] = round(time.time() - t0, 2)
        rows.append(row)
        pre = rlaw.small_prefix(g.stars, g.n_at, args.law)
        if pre is not None and not any(g.rounds[t]["fresh_lower_bound"] for t in range(len(pre["n_at"]) - 1)):
            pre.update({"test": "c", "arm": dr["arm"], "draw": dr["draw"], "conv": args.conv,
                        "paid_births": [g.rounds[t]["paid_births"] for t in range(len(pre["n_at"]) - 1)]})
            prefixes.append(pre)
    tag = f"{args.law}_{args.conv}_arm{args.arm}"
    rlaw.dump(rlaw.OUT / f"c_{tag}.jsonl", rows)
    rlaw.dump(rlaw.OUT / "prefixes" / f"c_{tag}.jsonl.gz", prefixes)
    print(json.dumps({"run": tag, "draws": len(rows), "seconds": round(time.time() - t_run, 1),
                      "slowest": max(r["seconds"] for r in rows)}))


if __name__ == "__main__":
    main()
