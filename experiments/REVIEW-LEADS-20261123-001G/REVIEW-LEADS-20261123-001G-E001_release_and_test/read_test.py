"""Read ticket A's test along each start's growth (Q1 and Q2), under both laws.

Per start and law (pre-registration, "Per start"): growth kind (ticket A `growth_kind`), first failing step (ticket A
`first_failing_stage`), knots at the first failing stage, and the birth whose addition first makes the stage fail: from the
last passing stage, the next step's births are added one at a time in the engine's order (`lib.grow` keeps that order in
`stars`) and the test is read after each; that birth's number of parents and of fresh distinctions are reported.  For Q1, also
whether the forbidden sub-pattern of the first failing stage uses only knots that the unedited source also has at that step
(knots identified by parentage, see `genealogy_ids`), with the unedited source grown under the same law and horizon.

Both laws: the engine (end_operator.step) differs between the laws only in `implied = (law == parity and exactly one birth)`.
Q1: both laws are grown separately for every start; the not-all-equal row records whether its history (knots, births,
outcome) equals the parity history (`history_shared_with_parity`).  Q2 (where a growth can take minutes): when the parity
history has no step with exactly one birth and did not close, the clause cannot act and the not-all-equal history is the
parity history (`history_shared_with_parity: true`); its first CHECK_STEPS steps are grown directly and compared
(`nae_short_check`).  Otherwise the not-all-equal law is grown separately.

Run from the repo root (each run stops starting new starts after --deadline seconds and prints the next index):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --pop Q1 --start 0 --stop 53 --tag a
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

A = C.A
CHECK_STEPS = 3     # Q2: steps of the not-all-equal law grown directly to check the shared history
LINEAR_LIMIT = 300  # births in the breaking step up to which the one-at-a-time scan is literal; above it, bisection (same answer)


def grow(stars, law):
    return A.grow([tuple(s) for s in stars], law, C.HORIZON, C.CAP, time_limit=C.GROW_SECONDS)


def has_single_birth_step(history):
    return any(len(step) == 1 for step in history["births"])


def genealogy_ids(history, n_source, registry):
    """Identity by parentage: founder k is ('f', k); a birth at parent step s is ('b', s, sorted parent ids, occurrence), the
    occurrence counting earlier births of that step with the same parents in the engine's order.  A birth's parents are the
    knots that held its input distinctions (the first `p` distinctions of its star, p = its number of parents)."""
    stars = history["stars"]
    owner, ids = {}, []
    for k in range(n_source):
        ids.append(registry.setdefault(("f", k), len(registry)))
        for d in stars[k]:
            owner.setdefault(d, k)
    idx = n_source
    for s, step in enumerate(history["births"], start=1):
        seen = Counter()
        for p, _fresh in step:
            star = stars[idx]
            parents = [owner[d] for d in star[:p]]
            assert len(set(parents)) == p and all(q < idx for q in parents)
            pk = tuple(sorted(ids[q] for q in parents))
            ids.append(registry.setdefault(("b", s, pk, seen[pk]), len(registry)))
            seen[pk] += 1
            for d in star:
                owner.setdefault(d, idx)
            idx += 1
    assert idx == len(stars)
    return ids


def stage_passes(stars, n):
    return A.passes(A.incidence_graph(stars, n))


def breaking_birth(history, ff):
    """First prefix of step ff's births (engine order) whose stage fails; stage ff-1 passes by the choice of ff."""
    stars, n_at = history["stars"], history["n_at"]
    lo, hi = n_at[ff - 1], n_at[ff]
    count = hi - lo
    if count <= LINEAR_LIMIT:
        method = "one at a time"
        m = next(m for m in range(lo + 1, hi + 1) if not stage_passes(stars, m))
    else:
        method = "bisection (failing is monotone in the prefix)"
        a, b = lo, hi
        while b - a > 1:
            mid = (a + b) // 2
            if stage_passes(stars, mid):
                a = mid
            else:
                b = mid
        m = b
    assert not stage_passes(stars, m) and (m - 1 == lo or stage_passes(stars, m - 1))
    j = m - lo
    p, fresh = history["births"][ff - 1][j - 1]
    held_before = Counter(d for k in range(m - 1) for d in stars[k])
    shared_with_earlier = sum(1 for d in stars[m - 1] if held_before[d])
    assert shared_with_earlier == p, (shared_with_earlier, p)
    return {"index_in_step": j, "births_in_step": count, "parents": p, "fresh": fresh, "knots_at_breaking_prefix": m,
            "method": method}


def forbidden_subpattern(stars, n):
    g = nx.Graph(nx.k_core(A.incidence_graph(stars, n), 2))
    res, why = C.with_alarm(C.CERT_SECONDS, nx.check_planarity, g, counterexample=True)
    if res is None:
        return None, why
    ok, cert = res
    assert not ok
    deg = Counter(dict(cert.degree()).values())
    kind = "K5" if deg.get(4, 0) == 5 and not any(d > 4 for d in deg) else (
        "K3,3" if deg.get(3, 0) == 6 and not any(d > 3 for d in deg) else f"degrees {dict(deg)}")
    return {"knots": sorted(x[1] for x in cert.nodes if x[0] == "k"),
            "distinctions": sorted(x[1] for x in cert.nodes if x[0] == "d"), "kind": kind}, "ok"


def read(history, law, n_source, shared, unedited=None, edit_distinction=None):
    stars, n_at = history["stars"], history["n_at"]
    t0 = time.time()
    ff = A.first_failing_stage(stars, n_at)
    one, total = A.one_parent_share(history)
    row = {"law": law, "outcome": history["outcome"], "steps": history["steps"], "n_at": n_at,
           "births_per_step": [len(s) for s in history["births"]], "growth_kind": A.growth_kind(history),
           "one_parent_births": one, "births": total, "has_single_birth_step": has_single_birth_step(history),
           "history_shared_with_parity": shared, "first_failing_step": ff,
           "fails_within_horizon": ff is not None, "knots_at_first_failure": None if ff is None else n_at[ff],
           "breaking_birth": None}
    if ff is not None and ff > 0:
        row["breaking_birth"] = breaking_birth(history, ff)
    if unedited is not None and ff is not None:
        registry = {}
        u_ids = genealogy_ids(unedited, n_source, registry)
        ids = genealogy_ids(history, n_source, registry)
        inh = {"unedited_steps": unedited["steps"], "unedited_first_failing_step": unedited["first_failing_step"]}
        if ff < len(unedited["n_at"]):
            U = set(u_ids[:unedited["n_at"][ff]])
            inherited = [k for k in range(n_at[ff]) if ids[k] in U]
            inh["knots_inherited_at_stage"] = len(inherited)
            inh["knots_at_stage"] = n_at[ff]
            sub = [stars[k] for k in inherited]
            inh["inherited_knots_alone_fail"] = not A.passes(A.incidence_graph(sub)) if sub else False
            cert, why = forbidden_subpattern(stars, n_at[ff])
            inh["subpattern_note"] = why
            if cert is not None:
                inh["subpattern_kind"] = cert["kind"]
                inh["subpattern_knots"] = len(cert["knots"])
                inh["subpattern_knots_inherited"] = sum(ids[k] in U for k in cert["knots"])
                inh["subpattern_uses_only_inherited_knots"] = all(ids[k] in U for k in cert["knots"])
                inh["subpattern_uses_edit_distinction"] = (edit_distinction in cert["distinctions"]
                                                           if edit_distinction is not None else None)
                inh["subpattern_knot_list"] = cert["knots"]
        else:
            inh["note"] = "the unedited source has no stage at this step within the horizon"
        row["inheritance"] = inh
    row["read_seconds"] = round(time.time() - t0, 2)
    return row


def trace_agreement(start, pop, law, history):
    """Agreement of lib.grow's births per step with the study's recorded rosters (sanity check, not a gate)."""
    b = [len(s) for s in history["births"]]
    pairs = []
    if pop == "Q1":
        for age, _live, planned in start["recorded_trace"][law]:
            if planned is not None and age < len(b):
                pairs.append((planned, b[age]))
    else:
        if start["recorded_parts"][law] == 1:
            for age, width in start["recorded_widths"][law]:
                if 1 <= age <= len(b):
                    pairs.append((width, b[age - 1]))
    return {"compared": len(pairs), "equal": sum(x == y for x, y in pairs)}


def unedited_histories(pops):
    stars = pops["Q1"]["original_supports"]
    out = {}
    for law in C.LAWS:
        h = grow(stars, law)
        h["first_failing_step"] = A.first_failing_stage(h["stars"], h["n_at"])
        out[law] = h
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", required=True, choices=("Q1", "Q2"))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stop", type=int, default=10**6)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--deadline", type=float, default=250.0)
    args = ap.parse_args()
    t_run = time.time()
    pops = C.load_populations()
    starts = pops[args.pop]["starts"]
    unedited = unedited_histories(pops) if args.pop == "Q1" else None
    lines, nxt = [], None
    for i in range(args.start, min(args.stop, len(starts))):
        if time.time() - t_run > args.deadline:
            nxt = i
            break
        s = starts[i]
        n_source = len(s["stars"])
        edit_d = s["edit"]["distinction"] if args.pop == "Q1" and s["edit"]["operation"].startswith("add") else None
        t0 = time.time()
        parity = grow(s["stars"], "parity")
        g_par = time.time() - t0
        law_check = None
        if args.pop == "Q1" or has_single_birth_step(parity) or parity["outcome"] == "closed":
            nae = grow(s["stars"], "nae")
            shared = (nae["stars"] == parity["stars"] and nae["births"] == parity["births"]
                      and nae["outcome"] == parity["outcome"])
        else:
            # Q2: the engine's only law clause cannot act (no parity step has exactly one birth), so the not-all-equal
            # history is the parity history; checked directly on the first CHECK_STEPS steps.
            nae, shared = parity, True
            short = A.grow([tuple(x) for x in s["stars"]], "nae", CHECK_STEPS, C.CAP, time_limit=C.GROW_SECONDS)
            k = short["steps"]
            law_check = {"steps": k, "equal": short["births"] == parity["births"][:k]
                         and short["stars"] == parity["stars"][:parity["n_at"][k]]}
        for law, h, is_shared in (("parity", parity, False), ("nae", nae, shared)):
            row = read(h, law, n_source, is_shared, unedited=None if unedited is None else unedited[law],
                       edit_distinction=edit_d)
            row.update({"population": args.pop, "id": s["id"], "index": i, "verdict": s["verdict"][law],
                        "trace_agreement": trace_agreement(s, args.pop, law, h),
                        "nae_short_check": law_check if law == "nae" else None})
            if args.pop == "Q1":
                row.update({"name": s["name"], "legal": s["legal"], "funded": s["funded"], "reason": s["reason"][law]})
            else:
                row.update({"extra": s["extra"], "draw": s["draw"], "n": s["n"]})
            lines.append(row)
        print(json.dumps({"id": s["id"], "grow_parity_s": round(g_par, 1), "total_s": round(time.time() - t0, 1),
                          "shared": shared, "outcome": parity["outcome"], "n_at": parity["n_at"],
                          "ff": [l["first_failing_step"] for l in lines[-2:]]}), flush=True)
    name = f"read_{args.pop}_{args.tag}.jsonl"
    C.dump(C.OUT / name, lines)
    if unedited is not None:
        C.dump(C.OUT / f"unedited_{args.tag}.jsonl",
               [{"law": law, "outcome": h["outcome"], "steps": h["steps"], "n_at": h["n_at"],
                 "births_per_step": [len(s) for s in h["births"]], "growth_kind": A.growth_kind(h),
                 "first_failing_step": h["first_failing_step"]} for law, h in unedited.items()])
    print(json.dumps({"file": name, "seconds": round(time.time() - t_run, 1), "rows": len(lines), "next_index": nxt}))


if __name__ == "__main__":
    main()
