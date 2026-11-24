"""Test (c), every allowed choice: on each of the 1,024 draws per law (all have at most 8 knots), every allowed payment
choice at round 1 and, on each resulting structure, every allowed choice at round 2 (deviations.md, A1 and A11).  The
two conventions are run beside it.  Test (a) is checked inline on these histories: every round t to t+1 whose stage t has
at most 22 distinctions, by enumeration of the allowed words of stage t (words.Stage).

One JSON line per draw: the number of allowed choices at round 1 (per short knot and in all), whether every choice
stalls, the numbers of births at round 2 over all choices, residual stalls at round 2, the largest number of holders
after two rounds over all choices, where conventions O and N fall, and the test (a) counts.

Run from the repo root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --law L --arm A [--start S --stop T]
"""
import argparse
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402
import words  # noqa: E402

CAP = 5000
LIMIT_A = 22


class ACount:
    def __init__(self):
        self.c = Counter()

    def check(self, stage, g_before, r, stage_cache):
        """Extension of every allowed word of the stage before round r (if it has at most 22 distinctions)."""
        m = rlaw.distinctions_at(g_before.stars, len(g_before.stars))
        if m > LIMIT_A:
            self.c["rounds_over_22"] += 1
            return
        key = id(g_before)
        if stage is None:
            stage = stage_cache.get(key)
            if stage is None:
                stage = words.Stage(g_before.stars, g_before.law)
                stage_cache[key] = stage
        births = [(row, f) for row, f in zip(r.inputs, r.fresh, strict=True)]
        bad_words, bad_births = stage.extends(births)
        self.c["rounds"] += 1
        self.c["births"] += len(births)
        self.c["births_with_shared"] += sum(1 for prow in r.paid if any(prow))
        self.c["zero_fresh_births"] += sum(1 for f in r.fresh if f == 0)
        self.c["words_checked"] += stage.n_ok
        self.c["words_failing"] += bad_words
        self.c["births_failing"] += bad_births
        if stage.n_ok == 0:
            self.c["stages_with_no_word"] += 1


def choices_of(g, r):
    per = g.allowed_choices(r)
    counts = [len(o) for _, o in per]
    total = math.prod(counts) if per else 1
    return per, counts, total


def all_choices(per):
    keys = [k for k, _ in per]
    for combo in itertools.product(*[o for _, o in per]):
        yield dict(zip(keys, combo))


def convention_rounds(stars, law, conv):
    g = rlaw.Growth(stars, law, "R", conv)
    g.run(2, CAP)
    return {"outcome": g.outcome, "births": g.births_per_round(), "max_holders": g.max_holders()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True, choices=rlaw.LAWS)
    ap.add_argument("--arm", type=int, required=True, choices=(0, 1, 2, 3))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stop", type=int, default=256)
    args = ap.parse_args()
    t_run = time.time()
    rows = []
    acount = ACount()
    for dr in rlaw.lib.p3_draws():
        if dr["arm"] != args.arm or not (args.start <= dr["draw"] < args.stop):
            continue
        t0 = time.time()
        g0 = rlaw.Growth(dr["stars"], args.law, "R", "O")
        r = g0.plan(max_births=CAP - len(g0.stars))
        row = {"arm": dr["arm"], "draw": dr["draw"], "n": dr["n"], "law": args.law, "r1_status": r.status,
               "conv_O": convention_rounds(dr["stars"], args.law, "O"),
               "conv_N": convention_rounds(dr["stars"], args.law, "N")}
        if r.status == "closed":
            row["r1_kind"] = "no live knot"
            rows.append(row)
            continue
        assert r.status in ("extend", "residual_stall"), r.status
        stage0 = words.Stage(g0.stars, args.law) if rlaw.distinctions_at(g0.stars, len(g0.stars)) <= LIMIT_A else None
        if not r.shortages:
            plans1 = [r]
            row.update({"r1_kind": "no short knot", "r1_choices": 1, "r1_choices_per_knot": []})
        else:
            per, counts, total = choices_of(g0, r)
            row.update({"r1_kind": "short", "r1_choices": total, "r1_choices_per_knot": counts,
                        "r1_short": [list(x) for x in r.shortages]})
            plans1 = (g0.plan_with(r, ch) for ch in all_choices(per)) if total else []
        r2_births, r2_status, maxh, r2_choice_counts = Counter(), Counter(), Counter(), Counter()
        r1_births = Counter()
        n1 = 0
        cache = {}
        for p1 in plans1:
            n1 += 1
            if stage0 is not None:
                acount.check(stage0, g0, p1, cache)
            else:
                acount.c["rounds_over_22"] += 1
            r1_births[len(p1.parents)] += 1
            g1 = g0.clone()
            g1.apply(p1)
            if g1.outcome is not None:  # closed after round 1
                r2_status["closed after round 1"] += 1
                maxh[g1.max_holders()] += 1
                continue
            q = g1.plan(max_births=CAP - len(g1.stars))
            if q.status == "residual_stall" or (q.status == "extend" and q.shortages):
                per2, counts2, total2 = choices_of(g1, q)
                r2_choice_counts[total2] += 1
                if total2 == 0:
                    r2_status["residual stall under every choice"] += 1
                    maxh[g1.max_holders()] += 1
                    continue
                plans2 = (g1.plan_with(q, ch) for ch in all_choices(per2))
            elif q.status == "extend":
                plans2 = [q]
            else:
                r2_status[q.status] += 1
                maxh[g1.max_holders()] += 1
                continue
            for p2 in plans2:
                r2_status["extend"] += 1
                r2_births[len(p2.parents)] += 1
                if rlaw.distinctions_at(g1.stars, len(g1.stars)) <= LIMIT_A:
                    acount.check(None, g1, p2, cache)
                else:
                    acount.c["rounds_over_22"] += 1
                g2 = g1.clone()
                g2.apply(p2)
                maxh[g2.max_holders()] += 1
            cache.pop(id(g1), None)
        row.update({"r1_plans_run": n1, "r1_births": dict(r1_births), "r2_births": dict(sorted(r2_births.items())),
                    "r2_status": dict(r2_status), "r2_choice_counts": {str(k): v for k, v in r2_choice_counts.items()},
                    "max_holders_after_two": dict(sorted(maxh.items())), "seconds": round(time.time() - t0, 2)})
        rows.append(row)
    tag = f"{args.law}_arm{args.arm}_{args.start:03d}-{args.stop:03d}"
    rlaw.dump(rlaw.OUT / "enum" / f"c_enum_{tag}.jsonl", rows)
    (rlaw.OUT / "enum" / f"a_enum_{tag}.json").write_text(json.dumps(dict(acount.c)) + "\n")
    print(json.dumps({"run": tag, "draws": len(rows), "seconds": round(time.time() - t_run, 1), "a": dict(acount.c)}))


if __name__ == "__main__":
    main()
