"""Census of population P3: fresh draws, seed 2026112301, with the rewired comparison.

Sizes four to eight with equal weight, a uniform labelled tree at each size, each knot filled to three places and given one more
loose distinction with chance 1/4, in four arms with 0, 1, 2 and 3 uniform extra meetings, 256 draws per arm per law, grown 12
parent steps or to 5,000 knots; stalls kept in every denominator.  For every start the ordinary history is replayed eight times
with the births rewired (lib.rewire; seeds 2026112310 to 2026112317, one per replica, re-seeded for every start).

One JSON line per stage of each start, one per closed parity part met, one per start (history and rewiring summary).

Run from the repo root (a chunk of draws per run keeps each run under ten minutes):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --law parity --arm 1 [--start 0 --stop 256]
"""
import argparse
import json
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

HORIZON, CAP = 12, 5000
GROW_SECONDS = 25
BOUND_SECONDS = 20


class Slow(Exception):
    pass


def _alarm(signum, frame):
    raise Slow()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, choices=lib.LAWS)
    ap.add_argument("--arm", type=int, required=True, choices=(0, 1, 2, 3))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stop", type=int, default=256)
    args = ap.parse_args()
    t_run = time.time()
    lines = []
    signal.signal(signal.SIGALRM, _alarm)
    for dr in lib.p3_draws():
        if dr["arm"] != args.arm or not (args.start <= dr["draw"] < args.stop):
            continue
        key = {"population": "P3", "law": args.law, "arm": dr["arm"], "draw": dr["draw"], "n": dr["n"]}
        history = lib.grow(dr["stars"], args.law, HORIZON, CAP, time_limit=GROW_SECONDS)
        stars, n_at = history["stars"], history["n_at"]
        first_fail, rows = None, []
        for t, n in enumerate(n_at):
            row = lib.stage_row(stars, n)
            rows.append(row)
            births = history["births"][t - 1] if t else []
            row.update(key)
            row.update({"kind": "stage", "t": t, "births": len(births),
                        "one_parent_births": sum(1 for p, _ in births if p == 1)})
            lines.append(row)
            if row["T"] == "fail" and first_fail is None:
                first_fail = t
            if row["loose"] == 0 and args.law == "parity":
                parts, holders = lib.closed_parts(stars, n)
                for part in parts:
                    verdict, why = lib.operator_reading(part, holders)
                    sub = [stars[k] for k in part]
                    g = lib.incidence_graph(sub)
                    part_dist = {d for s in sub for d in s}
                    lines.append({**key, "kind": "closed_part", "t": t, "knots": len(part), "distinctions": len(part_dist),
                                  "loop_rank": lib.loop_rank(g), "T": "pass" if lib.passes(g) else "fail",
                                  "admits": verdict, "admits_note": why,
                                  "stars": [list(s) for s in sub] if len(part_dist) <= 40 else None})
        one, total = lib.one_parent_share(history)
        summary = {**key, "kind": "history", "outcome": history["outcome"], "steps": history["steps"], "n_at": n_at,
                   "births_per_step": [len(s) for s in history["births"]], "growth_kind": lib.growth_kind(history),
                   "one_parent_births": one, "births": total, "one_parent_share": (one / total if total else None),
                   "first_failing_step": first_fail, "meetings": dr["meetings"], "opens": dr["opens"],
                   "extra_meetings": dr["extra_meetings"]}
        summary["monotone_violation"] = any(a["T"] == "fail" and b["T"] == "pass" for a, b in zip(rows, rows[1:]))
        if first_fail is not None:
            signal.alarm(BOUND_SECONDS)
            try:
                ub, why = lib.upper_removal_bound(stars, n_at[first_fail])
            except Slow:
                ub, why = None, f"not finished in {BOUND_SECONDS} s"
            finally:
                signal.alarm(0)
            summary["upper_bound_at_first_failing_stage"] = ub
            summary["upper_bound_note"] = why
            summary["lower_bound_at_first_failing_stage"] = rows[first_fail]["lower_bound"]
        # the rewired comparison
        rewired = []
        if history["steps"] >= 1:
            for seed in lib.REWIRE_SEEDS:
                rstars, shortfall, short_births = lib.rewire(dr["stars"], history["births"], seed)
                rewired.append({"seed": seed, "first_failing_step": lib.first_failing_stage(rstars, n_at),
                                "shortfall": shortfall, "births_with_shortfall": short_births})
        else:
            rewired = [{"seed": seed, "first_failing_step": first_fail, "shortfall": 0, "births_with_shortfall": 0}
                       for seed in lib.REWIRE_SEEDS]
        summary["rewired"] = rewired
        lines.append(summary)
    name = f"p3_{args.law}_arm{args.arm}_{args.start:03d}-{args.stop:03d}.jsonl"
    lib.dump(lib.OUT / name, lines)
    print(json.dumps({"file": name, "seconds": round(time.time() - t_run, 1),
                      "starts": sum(1 for l in lines if l["kind"] == "history")}))


if __name__ == "__main__":
    main()
