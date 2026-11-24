"""Test (b), also row G: the seven recorded sources of REVIEW-LEADS-20261123-001A ticket A, to its horizons (16 rounds or
20,000 knots), under R (conventions O and N) and under ordinary growth (the recorded driver lib.grow).

One run per source, law and rule.  Each run writes one JSON file: knots per stage, births and payments per round,
outcome, largest number of holders, first failing step of the operator test, growth kind, the elimination test against
the shortcut, and a SHA-256 digest of the full holdings (every knot's distinctions, in birth order).  summarize.py
compares the digests.

Run from the repo root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --source NAME --law L --rule ref|R [--conv O|N]
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402

HORIZON, CAP = 16, 20000


def digest(stars):
    return hashlib.sha256(json.dumps([list(s) for s in stars], separators=(",", ":")).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--law", required=True, choices=rlaw.LAWS)
    ap.add_argument("--rule", required=True, choices=("ref", "R"))
    ap.add_argument("--conv", default="O", choices=("O", "N"))
    args = ap.parse_args()
    t0 = time.time()
    stars = rlaw.lib.recorded_sources()[args.source]
    if args.rule == "ref":
        h = rlaw.ordinary_reference(stars, args.law, HORIZON, CAP)
        row = {"n_at": h["n_at"], "outcome": h["outcome"], "births": [len(s) for s in h["births"]],
               "stars_sha256": digest(h["stars"]), "growth_kind": rlaw.lib.growth_kind(h),
               "first_failing_step": rlaw.lib.first_failing_stage(h["stars"], h["n_at"])}
        holders = {}
        for s in h["stars"]:
            for d in s:
                holders[d] = holders.get(d, 0) + 1
        row["max_holders"] = max(holders.values())
    else:
        g = rlaw.Growth(stars, args.law, "R", args.conv, check=True, bound_next=False).run(HORIZON, CAP)
        row = {"n_at": g.n_at, "outcome": g.outcome, "births": g.births_per_round(),
               "payments": [r["payments"] for r in g.rounds], "paid_births": [r["paid_births"] for r in g.rounds],
               "short_knots": [r["short_knots"] for r in g.rounds], "implied": [r["implied"] for r in g.rounds],
               "elim_vs_shortcut": [r["elim_vs_shortcut"] for r in g.rounds],
               "stars_sha256": digest(g.stars), "growth_kind": rlaw.recorded_growth_kind(g),
               "growth_kind_births": rlaw.growth_kind_births(g.births_per_round()),
               "first_failing_step": rlaw.first_failing_step(g), "max_holders": g.max_holders(),
               "check_log": dict(g.check_log)}
    row.update({"source": args.source, "law": args.law, "rule": args.rule,
                "conv": args.conv if args.rule == "R" else None, "seconds": round(time.time() - t0, 1)})
    name = f"b_{args.source}_{args.law}_{args.rule}{args.conv if args.rule == 'R' else ''}.json"
    rlaw.OUT.mkdir(parents=True, exist_ok=True)
    (rlaw.OUT / name).write_text(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in ("source", "law", "rule", "conv", "outcome", "n_at", "seconds")}))


if __name__ == "__main__":
    main()
