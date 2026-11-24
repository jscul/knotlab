"""Row G, first part: the code checks on the sparse draws (the seven recorded sources are run by test_b.py).

G-a  On the 280 funded draws per law (seed 2026112301), R under both conventions and the ordinary mode of rlaw reproduce
     the recorded driver lib.grow exactly (stars, knots per stage, outcome), with no short knot and no payment, 12 rounds
     or 5,000 knots; every round small enough is also compared with the recorded end_operator on the same end (groups,
     witnessed sets, lookahead demand, the whole round).
G-b  The elimination test agrees with the ordinary shortcut (implied exactly when the birth is the round's only birth) on
     every parity birth of every ordinary history of the 1,024 draws, closings included; the closings met are counted.
G-c  The elimination test against enumeration: on every stage of at most 20 distinctions met in round 1 or 2 of R
     (convention O) on the 744 draws that stall under ordinary growth, and on every such stage of the funded draws, a
     parity birth is implied by elimination exactly when the parity of what it takes is the same on every allowed word.
G-d  The two closings of test (d) (C_binary, C_ternary at setting 00, ordinary growth): implied by elimination.
G-e  On the 744 stalled draws, R under both conventions: every round with no short knot and small enough is compared
     with the recorded operator on the same end; every round's groups and lookahead are compared with the recorded code.
     (The same checks run inside every test_c.py run, whose check logs summarize.py adds up.)
G-f  The C search against the Python search on ends and lookaheads too large for the recorded code, and the next-round
     cap shortcut against full computation.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --part a|b|c|d|e|f [--law L] [--arm A]
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402
import words  # noqa: E402

HORIZON, CAP = 12, 5000


def same_as_recorded(g, ref):
    return ([tuple(s) for s in ref["stars"]] == g.stars and ref["n_at"] == g.n_at
            and ref["outcome"] == ("stall" if g.outcome == "residual_stall" else g.outcome))


def part_a(law):
    out = Counter()
    bad = []
    for dr in rlaw.lib.p3_draws():
        ref = rlaw.ordinary_reference(dr["stars"], law, HORIZON, CAP)
        if ref["outcome"] == "stall" or not ref["births"]:
            continue
        out["funded"] += 1
        g_ord = rlaw.Growth(dr["stars"], law, "ordinary", check=True).run(HORIZON, CAP)
        ok = same_as_recorded(g_ord, ref)
        out["ordinary_mode_equal"] += ok
        if not ok:
            bad.append(("ordinary", dr["arm"], dr["draw"]))
        for conv in ("O", "N"):
            g = rlaw.Growth(dr["stars"], law, "R", conv, check=True).run(HORIZON, CAP)
            ok = same_as_recorded(g, ref)
            pays = sum(r["payments"] for r in g.rounds)
            shorts = sum(r["short_knots"] for r in g.rounds)
            out[f"R_{conv}_equal"] += ok
            out[f"R_{conv}_payments"] += pays
            out[f"R_{conv}_short_knots"] += shorts
            for k, v in g.check_log.items():
                out[f"R_{conv}_check_{k}"] += v
            if not ok:
                bad.append((conv, dr["arm"], dr["draw"]))
        for k, v in g_ord.check_log.items():
            out[f"ordinary_check_{k}"] += v
    return {"counts": dict(out), "mismatches": bad}


def part_b():
    out = Counter()
    closings = []
    for dr in rlaw.lib.p3_draws():
        g = rlaw.Growth(dr["stars"], "parity", "ordinary", elim_always=True).run(HORIZON, CAP)
        ref = rlaw.ordinary_reference(dr["stars"], "parity", HORIZON, CAP)
        assert same_as_recorded(g, ref)
        for t, r in enumerate(g.rounds):
            out["births"] += r["births"]
            out["disagreements"] += r["elim_vs_shortcut"]
            if r["births"] == 1:
                closings.append((dr["arm"], dr["draw"], t + 1))
        out["histories"] += 1
    out["closings"] = len(closings)
    return {"counts": dict(out), "closings": closings}


def _implied_by_enumeration(stars, taken):
    names = sorted({d for s in stars for d in s})
    planes, valid = words.planes_for(names)
    ok = words.allowed(stars, "parity", planes, valid)
    par = valid.copy() & 0
    for d in taken:
        par = par ^ planes[d]
    odd = ok & par
    even = ok & ~par
    n_odd, n_even = words.popcount(odd), words.popcount(even)
    return n_odd == 0 or n_even == 0, n_odd + n_even


def part_c():
    out = Counter()
    examples = []
    for dr in rlaw.lib.p3_draws():
        g = rlaw.Growth(dr["stars"], "parity", "R", "O")
        for t in range(2):
            if g.outcome is not None:
                break
            if rlaw.distinctions_at(g.stars, len(g.stars)) > 20:
                break
            r = g.plan(max_births=CAP - len(g.stars))
            if r.status != "extend":
                break
            for row, e in zip(r.inputs, r.elim, strict=True):
                enum, n_words = _implied_by_enumeration(g.stars, row)
                out["births_tested"] += 1
                out["implied_by_elimination"] += bool(e)
                out["agree"] += (bool(e) == enum)
                if bool(e) != enum:
                    examples.append((dr["arm"], dr["draw"], t + 1, row))
                if n_words == 0:
                    out["stage_with_no_allowed_word"] += 1
            out["stages_tested"] += 1
            g.apply(r)
    return {"counts": dict(out), "disagreements": examples}


def part_d():
    sys.path.insert(0, str(rlaw.ROOT / "experiments/WHOLE-STAGE-SETTINGS-20261120-001B/"
                                       "WHOLE-STAGE-SETTINGS-20261120-001B-E001_ordinary_edits"))
    import edits  # noqa: E402
    res = {}
    for prep in edits.built_cases():
        if prep.name not in ("C_binary", "C_ternary"):
            continue
        stars = prep.edited((0, 0))
        g = rlaw.Growth(stars, "parity", "ordinary", elim_always=True)
        r = g.plan()
        res[prep.name] = {"births": len(r.parents), "fresh": list(r.fresh), "shortcut_implied": list(r.implied),
                          "elimination_implied": list(r.elim),
                          "enumeration_implied": [_implied_by_enumeration(list(stars), row)[0] for row in r.inputs]}
    return res


def part_e(law):
    out = Counter()
    for dr in rlaw.lib.p3_draws():
        ref = rlaw.ordinary_reference(dr["stars"], law, 1, CAP)
        if ref["outcome"] != "stall":
            continue
        for conv in ("O", "N"):
            g = rlaw.Growth(dr["stars"], law, "R", conv, check=True).run(HORIZON, CAP)
            for k, v in g.check_log.items():
                out[f"{conv}_{k}"] += v
            out[f"{conv}_histories"] += 1
    return {"counts": dict(out)}


def part_f(law, arm, start=0, stop=256):
    """The C search against the Python search (same algorithm) on every end and lookahead of R (convention O) on the
    draws of one arm with at most 400 candidate classes; and the next-round cap shortcut against full computation on
    every history it ended whose last round has at most 1,200 births (full lookahead stopped, unverified, beyond
    200,000 maximal groups)."""
    out = Counter()
    unverified = []

    def both(nodes, blocks):
        rlaw.USE_C, rlaw.C_MIN = True, 0
        a = rlaw.Groups(nodes, blocks)
        rlaw.USE_C = False
        ncand = sum(1 for k in a.keys if len(k) >= 2)
        if ncand <= 400:
            b = rlaw.Groups(nodes, blocks)
            out["searches_compared"] += 1
            out["searches_equal"] += (sorted(map(tuple, a.big)) == sorted(map(tuple, b.big)) and a.total == b.total)
        rlaw.USE_C, rlaw.C_MIN = True, 64

    for dr in rlaw.lib.p3_draws():
        if dr["arm"] != arm or not (start <= dr["draw"] < stop):
            continue
        g = rlaw.Growth(dr["stars"], law, "R", "O")
        while g.outcome is None and len(g.rounds) < HORIZON:
            opens, raw = g.present_end()
            both(list(opens), rlaw.maximal_blocks(raw))
            r = g.plan(max_births=CAP - len(g.stars))
            if r.status != "extend":
                g.outcome = r.status
                break
            if not r.next_capped and len(r.parents) <= 2000:
                both(range(len(r.parents)), rlaw.maximal_blocks(g.lookahead_blocks(r.inputs)))
            g.apply(r)
        if g.outcome == "cap" and g.rounds and g.rounds[-1]["fresh_lower_bound"]:
            out["shortcut_histories"] += 1
            # Replay to the last round, plan it with the shortcut (same parents and payments), then compute its
            # lookahead in full up to 200,000 maximal groups; if that finishes, give the round its exact fresh counts,
            # build the next end from the holdings and confirm the recorded cap rule does not take the next round.
            full = rlaw.Growth(dr["stars"], law, "R", "O")
            for _ in range(len(g.rounds) - 1):
                full.apply(full.plan(max_births=CAP - len(full.stars)))
            r = full.plan(max_births=CAP - len(full.stars))
            assert r.next_capped
            gr = rlaw.Groups(range(len(r.parents)), rlaw.maximal_blocks(full.lookahead_blocks(r.inputs)), limit=200000)
            if gr.exceeded:
                unverified.append((dr["draw"], "lookahead has more than 200,000 maximal groups"))
                continue
            cnt = gr.counts()
            r.fresh = tuple(0 if imp else max(cnt[i], 3 - len(ps), 1)
                            for i, (ps, imp) in enumerate(zip(r.parents, r.implied, strict=True)))
            r.next_capped = False
            full.apply(r)
            nxt = full.plan(max_births=CAP - len(full.stars))
            out["shortcut_verified"] += 1
            out["shortcut_agrees"] += (nxt.status == "cap" and full.n_at == g.n_at)
    return {"counts": dict(out), "unverified": unverified}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=list("abcdef"))
    ap.add_argument("--law", choices=rlaw.LAWS)
    ap.add_argument("--arm", type=int)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stop", type=int, default=256)
    args = ap.parse_args()
    t0 = time.time()
    if args.part == "a":
        res = part_a(args.law)
    elif args.part == "b":
        res = part_b()
    elif args.part == "c":
        res = part_c()
    elif args.part == "d":
        res = part_d()
    elif args.part == "e":
        res = part_e(args.law)
    else:
        res = part_f(args.law, args.arm, args.start, args.stop)
    res["seconds"] = round(time.time() - t0, 1)
    name = f"gate_{args.part}" + (f"_{args.law}" if args.law else "") + (f"_arm{args.arm}" if args.arm is not None else "") + (
        f"_{args.start:03d}-{args.stop:03d}" if (args.start, args.stop) != (0, 256) else "") + ".json"
    rlaw.OUT.mkdir(parents=True, exist_ok=True)
    (rlaw.OUT / name).write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "closings"}, default=str)[:3000])


if __name__ == "__main__":
    main()
