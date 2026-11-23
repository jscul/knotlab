"""Census of population P2: recorded sources under both laws, 16 parent steps or 20,000 knots.

Sources (all built by lib.py from the recorded code named there): seven_knot, nine_knot_drawn, knots21_two_clocks,
five_founder_clock, archive_start-00, archive_start-04, archive_start-13 (the three archived explosive starts of the six-rule
study, FOUR-READINGS-20261120-001A growth.ordinary).  One JSON line per stage and one per history.

The two laws differ in the engine only in the clause `implied = (law == parity and exactly one birth in the step)`.  When the
parity history has no step with exactly one birth, the not-all-equal history is the same history; it is then not recomputed and
its lines carry `history_shared_with_parity: true`.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --source NAME
"""
import argparse
import json
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

HORIZON, CAP = 16, 20000
GROW_SECONDS = 330
BOUND_SECONDS = 40


class Slow(Exception):
    pass


def _alarm(signum, frame):
    raise Slow()


def history_lines(population, name, law, history, shared, extra=None):
    """Stage lines, closed-part lines and the one history line of a grown history."""
    stars, n_at = history["stars"], history["n_at"]
    lines, first_fail, closed = [], None, []
    for t, n in enumerate(n_at):
        row = lib.stage_row(stars, n)
        births = history["births"][t - 1] if t else []
        row.update({"kind": "stage", "population": population, "source": name, "law": law, "t": t,
                    "births": len(births), "one_parent_births": sum(1 for p, _ in births if p == 1),
                    "history_shared_with_parity": shared})
        lines.append(row)
        if row["T"] == "fail" and first_fail is None:
            first_fail = t
        if row["loose"] == 0 and law == "parity":
            parts, holders = lib.closed_parts(stars, n)
            for part in parts:
                verdict, why = lib.operator_reading(part, holders)
                part_set = set(part)
                part_links = sum(1 for d, hs in holders.items() for k in hs if k in part_set)
                part_dist = [d for d, hs in holders.items() if hs[0] in part_set]
                g = lib.incidence_graph([stars[k] for k in part])
                fails = not lib.passes(g)
                closed.append({"kind": "closed_part", "population": population, "source": name, "law": law, "t": t,
                               "knots": len(part), "distinctions": len(part_dist), "links": part_links,
                               "loop_rank": lib.loop_rank(g), "T": "fail" if fails else "pass",
                               "admits": verdict, "admits_note": why,
                               "stars": [list(stars[k]) for k in part] if len(part_dist) <= 40 else None})
    one, total = lib.one_parent_share(history)
    summary = {"kind": "history", "population": population, "source": name, "law": law, "outcome": history["outcome"],
               "steps": history["steps"], "n_at": n_at, "births_per_step": [len(s) for s in history["births"]],
               "growth_kind": lib.growth_kind(history), "one_parent_births": one, "births": total,
               "one_parent_share": (one / total if total else None), "first_failing_step": first_fail,
               "history_shared_with_parity": shared}
    if first_fail is not None:
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(BOUND_SECONDS)
        try:
            ub, why = lib.upper_removal_bound(stars, n_at[first_fail], max_links=600, max_removals=300)
        except Slow:
            ub, why = None, f"not finished in {BOUND_SECONDS} s"
        finally:
            signal.alarm(0)
        summary["upper_bound_at_first_failing_stage"] = ub
        summary["upper_bound_note"] = why
        summary["lower_bound_at_first_failing_stage"] = lines[first_fail]["lower_bound"]
    return lines, closed, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    args = ap.parse_args()
    started = time.time()
    stars = lib.recorded_sources()[args.source]
    out_lines = []
    parity = lib.grow(stars, "parity", HORIZON, CAP, time_limit=GROW_SECONDS)
    took_parity = time.time() - started
    shared = all(len(step) != 1 for step in parity["births"]) and parity["outcome"] != "closed"
    nae = parity
    if not shared:
        nae = lib.grow(stars, "nae", HORIZON, CAP, time_limit=max(30, 560 - (time.time() - started)))
    for law, hist, is_shared in (("parity", parity, False), ("nae", nae, shared)):
        lines, closed, summary = history_lines("P2", args.source, law, hist, is_shared)
        out_lines += lines + closed + [summary]
    lib.dump(lib.OUT / f"p2_{args.source}.jsonl", out_lines)
    print(json.dumps({"source": args.source, "seconds": round(time.time() - started, 1), "parity_growth_seconds": round(took_parity, 1),
                      "shared": shared, "outcomes": {l["law"]: [l["outcome"], l["n_at"], l["growth_kind"], l["first_failing_step"]]
                                                        for l in out_lines if l["kind"] == "history"}}, default=str))


if __name__ == "__main__":
    main()
