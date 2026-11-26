"""Press the repeated-change claim using matched histories of receiver-own births.

Run from the repository root with the repository's interpreter and -B. --pilot
times one complete comparison at each requested horizon. --search records a
bounded search for two distinct receptions. --witness reruns named cases with
the full 32-round, 10,000-knot bounds and independently checks own parentage.
"""

import argparse
import gzip
import json
import random
import resource
import time
from collections import Counter
from pathlib import Path

from growth import (build_pair, edit_state, far_members, first_own_difference,
                    grow, link_status, perturb, roster, sharing_counts)


HERE = Path(__file__).resolve().parent
FAR = frozenset({"B"})
RECEIVER = frozenset({"A"})
BOUND = 10000
CYCLIC = "n4:g16:1112@1"
SWITCH = "tri:122@0"
CASES = [
    (SWITCH, CYCLIC, 3),
    ("n4:g15:3222@1", "g6:122@0", 3),
    (SWITCH, "n3:g7:112@0", 3),
    (SWITCH, "n4:g17:0102@1", 3),
    (SWITCH, "n4:g18:0001@3", 3),
    (SWITCH, "n3:g6:122@0", 3),
    ("tri:222@0", CYCLIC, 4),
]


def elapsed(start):
    return round(time.monotonic() - start, 3)


def endpoint(growth):
    return {"round": len(growth.rows), "knots": len(growth.states[-1].knots),
            "stop": growth.stop}


def own_counts(growth):
    return [len(row.own_births) for row in growth.rows]


def number_changes(control, treatment):
    return [i for i, (c, t) in enumerate(zip(own_counts(control), own_counts(treatment)), 1)
            if c != t]


def starting_ancestors(state, knot):
    roots = set()
    pending = [knot]
    seen = set()
    while pending:
        u = pending.pop()
        if u in seen:
            continue
        seen.add(u)
        node = state.knots[u]
        if node.parents:
            pending.extend(node.parents)
        else:
            roots.add(u)
    return sorted(roots)


def setting(state, knot, distance, linked):
    node = state.knots[knot]
    return {"knot": knot, "roles": sorted(node.roles), "born": node.born,
            "parents": node.parents, "start ancestors": starting_ancestors(state, knot),
            "birth name": node.label, "holder steps": distance, "in receiver class": linked,
            "live before": knot in state.members, "acted before": node.spent,
            "usable before": len(state.usable(knot))}


def second_trial(w, g, first_round, t, u, sign, horizon, h1):
    both = perturb(g, t, u, sign, rounds=horizon, bound=BOUND)
    if both is None:
        return {"sign": sign, "applied": False}
    h2, common = first_own_difference(g, both, t)
    initial_in_double, common_with_base = first_own_difference(w, both, first_round)
    preserved = (h1 is not None and h1 <= common and
                 both.rows[h1 - 1].own_births == g.rows[h1 - 1].own_births)
    twice = bool(preserved and initial_in_double == h1 and h2 is not None and h2 > h1)
    effective = both.edits[t]
    return {"sign": sign, "applied": True, "live immediately after": u in effective.members,
            "usable immediately after": len(effective.usable(u)), "first-only vs both": h2,
            "no-change vs both": initial_in_double, "common with first only": common,
            "common with no change": common_with_base, "first hearing preserved": preserved,
            "distinct successive hearings": twice,
            "birth counts at conditional difference": None if h2 is None else
            [len(z.rows[h2 - 1].own_births) for z in (g, both)]}


def pilot():
    out = []
    for cap, horizon, t1 in ((3, 18, 3), (3, 32, 3), (5, 15, 1), (6, 15, 1)):
        start = time.monotonic()
        pair = build_pair(f"tri:{cap - 2}22@0", CYCLIC)
        w = grow(pair, cap=cap, rounds=horizon, bound=BOUND)
        first = far_members(w.states[t1], True)[0][0]
        g = perturb(w, t1, first)
        h1, _ = first_own_difference(w, g, t1)
        second = far_members(g.states[t1 + 1], True)[0][0]
        outcome = second_trial(w, g, t1, t1 + 1, second, "add", horizon, h1)
        out.append({"cap": cap, "horizon": horizon, "first round": t1,
                    "first": first, "second": second, "h1": h1,
                    "conditional difference": outcome["first-only vs both"],
                    "seconds": elapsed(start),
                    "maximum RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    return out


def search_case(case, horizon=18, first_rounds=(3, 1, 2)):
    """All linked far targets at these settings, with an early stop for a positive."""
    receiver, far, cap = case
    w = grow(build_pair(receiver, far), cap, horizon, BOUND)
    initial_trials = []
    positive = None
    for t1 in first_rounds:
        for first, distance1 in far_members(w.states[t1], True):
            for sign1 in ("add", "bar"):
                g = perturb(w, t1, first, sign1)
                h1, n1 = first_own_difference(w, g, t1)
                trial = {"t1": t1, "first": first, "sign": sign1, "holder steps": distance1,
                         "first hearing": h1, "common rounds": n1, "settings": []}
                initial_trials.append(trial)
                if h1 is None:
                    continue
                times = set(range(t1 + 1, t1 + 7)) | {h1, h1 + 1}
                for t2 in sorted(t for t in times if t < len(g.rows)):
                    state = g.states[t2]
                    sites = far_members(state, True)
                    at = {"t2": t2, "linked strict far members": len(sites), "sites": []}
                    trial["settings"].append(at)
                    for second, distance2 in sites:
                        place = {"knot": second, "holder steps": distance2, "signs": []}
                        at["sites"].append(place)
                        for sign2 in ("add", "bar"):
                            row = second_trial(w, g, t1, t2, second, sign2, horizon, h1)
                            place["signs"].append(row)
                            if row["distinct successive hearings"]:
                                positive = (t1, first, sign1, t2, second, sign2)
                                return initial_trials, positive
    return initial_trials, positive


def run_search(cases, horizon=18, first_rounds=(3, 1, 2)):
    results = []
    for case in cases:
        t = time.monotonic()
        trials, positive = search_case(case, horizon, first_rounds)
        n = sum(len(site["signs"]) for first in trials for at in first["settings"]
                for site in at["sites"])
        result = {"receiver": case[0], "far": case[1], "cap": case[2], "rounds": horizon,
                  "first trials": trials, "second changes placed": n,
                  "distinct successive hearings": positive, "seconds": elapsed(t)}
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if k != "first trials"}), flush=True)
        if positive:
            break
    return results


def other_starts(limit=12, seed=26112613):
    """An equal-weight draw within strata outside the original repeated-change pairs."""
    groups = {"switch; apart or missing by round 3": [], "switch; linked at 3 only": [],
              "other receivers; apart or missing by round 3": [],
              "other receivers; linked at 3 only": []}
    with gzip.open(HERE.parent / "linked_runs.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("law") != "CAP-3":
                continue
            readings = row["linked"]
            if len(readings) < 16 or readings[0] is not True or readings[15] is True:
                continue
            population = "switch" if row["A"] == SWITCH else "other receivers"
            prefix = "linked at 3 only" if readings[2] is True else "apart or missing by round 3"
            groups[population + "; " + prefix].append((row["A"], row["B"], 3))
    rng = random.Random(seed)
    entries = []
    for group, pairs in groups.items():
        for case in rng.sample(sorted(pairs), min(limit, len(pairs))):
            entries.append((group, case))
    return entries


def broader(limit):
    results = []
    for group, case in other_starts(limit):
        trials, positive = search_case(case, 16, (1, 2))
        changed = [row for row in trials if row["first hearing"] is not None]
        count = sum(len(site["signs"]) for x in changed for a in x["settings"] for site in a["sites"])
        results.append({"stratum": group, "receiver": case[0], "far": case[1],
                        "first changes": len(trials), "first changes heard": len(changed),
                        "second changes placed": count, "first trials giving hearings": changed,
                        "distinct successive hearings": positive})
        if positive:
            break
    print("broader", len(results), sum(x["first changes"] for x in results),
          sum(x["second changes placed"] for x in results),
          results[-1]["distinct successive hearings"] if results else None, flush=True)
    return results


def canonical_first(quiet_limit, seed=26112671):
    """Keep the initial nearest addition, including when that change is inaudible."""
    with gzip.open(HERE.parent / "again_linked_runs_receivers.jsonl.gz", "rt") as stream:
        pairs = list(map(json.loads, stream))
    quiet = sorted((p["A"], p["B"]) for p in pairs if p["changes"][0]["heard"] is None)
    heard = sorted((p["A"], p["B"]) for p in pairs if p["changes"][0]["heard"] is not None)
    selected = random.Random(seed).sample(quiet, min(quiet_limit, len(quiet))) + heard
    out = []
    for a, b in selected:
        w = grow(build_pair(a, b), 3, 18, BOUND)
        first = far_members(w.states[3], True)[0][0]
        g = perturb(w, 3, first)
        h1, _ = first_own_difference(w, g, 3)
        x = {"receiver": a, "far": b, "first": first, "h1": h1,
             "second placements": 0, "second changes affecting own births": []}
        for t in (4, 5, 6):
            for u, d in far_members(g.states[t], True):
                for sign in ("add", "bar"):
                    row = second_trial(w, g, 3, t, u, sign, 18, h1)
                    x["second placements"] += 1
                    if row["first-only vs both"] is not None:
                        x["second changes affecting own births"].append(
                            {"after round": t, "knot": u, "holder steps": d, **row})
        out.append(x)
    return {"seed": seed, "all census pairs with first hearing": len(heard),
            "quiet pairs eligible": len(quiet), "quiet pairs drawn with equal weighting": min(quiet_limit, len(quiet)),
            "setting rounds": [4, 5, 6], "round cap": 18, "knot bound": BOUND,
            "all linked strict far targets and both signs": True,
            "placed": sum(row["second placements"] for row in out),
            "conditional effects": sum(len(row["second changes affecting own births"]) for row in out),
            "comparisons": out}


def exact_making(history, codes):
    """Intern parent descriptions across histories, never using the birth name's digest."""
    def intern(description):
        return codes.setdefault(description, len(codes))

    ids = [intern(("start", k.label)) for k in history.pair.start.knots]
    signatures = []
    for i, row in enumerate(history.rows, 1):
        state = history.states[i]
        occurrence = Counter()
        own = []
        for u in row.births:
            knot = state.knots[u]
            parents = tuple(sorted(ids[p] for p in knot.parents))
            key = (knot.kind, parents)
            label = intern((key, occurrence[key]))
            occurrence[key] += 1
            assert len(ids) == u
            ids.append(label)
            if knot.roles == RECEIVER:
                own.append((label, knot.fresh, len(knot.places)))
        signatures.append(sorted(own))
    return signatures, ids


def difference(control, treatment, after):
    return next((i + 1 for i in range(after, min(len(control), len(treatment)))
                 if control[i] != treatment[i]), None)


def detailed_witness(case, moves):
    receiver, far, cap = case
    t1, first, first_sign, t2, second, second_sign = moves
    pair = build_pair(receiver, far)
    w = grow(pair, cap, 32, BOUND)
    g = perturb(w, t1, first, first_sign)
    both = perturb(g, t2, second, second_sign)
    assert g is not None and both is not None
    histories = {"no change": w, "first only": g, "both": both}
    codes = {}
    readings = {key: exact_making(history, codes) for key, history in histories.items()}
    second_code = readings["first only"][1][second]
    twins = [u for u in w.states[t2].members if readings["no change"][1][u] == second_code]
    if len(twins) == 1:
        second_only = perturb(w, t2, twins[0], second_sign)
        if second_only is not None:
            histories["second only at its matched live counterpart"] = second_only
            readings["second only at its matched live counterpart"] = exact_making(second_only, codes)
    contrasts = {}
    comparisons = [("no change", "first only", t1), ("first only", "both", t2),
                   ("no change", "both", t1)]
    second_key = "second only at its matched live counterpart"
    if second_key in histories:
        comparisons += [("no change", second_key, t2), (second_key, "both", t1)]
    for c, h, after in comparisons:
        t = difference(readings[c][0], readings[h][0], after)
        archive_t, common = first_own_difference(histories[c], histories[h], after)
        assert t == archive_t
        contrasts[c + " vs " + h] = {
            "first exact-parentage difference": t,
            "rounds with different own birth counts": number_changes(histories[c], histories[h]),
            "common rounds": common,
            "own counts at difference": None if t is None else
            [len(readings[key][0][t - 1]) for key in (c, h)],
        }
    sites = []
    for before, after, t, u, sign in [(w, g, t1, first, first_sign),
                                       (g, both, t2, second, second_sign)]:
        st = before.states[t]
        rr = roster(st)
        near = {rr.class_of[v] for v in rr.members if st.knots[v].roles == RECEIVER}
        ctx = setting(st, u, sharing_counts(st).get(u), rr.class_of.get(u) in near)
        ctx.update({"after round": t, "sign": sign, "effective usable": len(after.edits[t].usable(u)),
                    "just barred": sorted(after.edits[t].barred - st.barred),
                    "before and after knot counts": [len(st.knots), len(after.edits[t].knots)],
                    "rank among linked strict far members": next((i for i, (v, _) in
                        enumerate(far_members(st, True), 1) if v == u), None)})
        sites.append(ctx)
    return {"receiver": receiver, "far": far, "cap": cap,
            "original far site": pair.far_site, "sites": sites, "comparisons": contrasts,
            "second target matching live members without first": twins,
            "identical recorded history through second setting": (
                g.rows[:t2] == both.rows[:t2] and g.states[:t2 + 1] == both.states[:t2 + 1]),
            "endpoint by history": {k: endpoint(v) for k, v in histories.items()},
            "own births by round": {k: own_counts(v) for k, v in histories.items()},
            "link at settings and first hearing": {
                key: {str(t): link_status(v.states[t]) for t in sorted({t1, t2, 13, 15})
                      if t < len(v.states)} for key, v in histories.items()}}


def diagnostics():
    """Place changes after the first reception. Source and eligibility are recorded separately."""
    pair = build_pair(SWITCH, CYCLIC)
    w = grow(pair, 3, 32, BOUND)
    t1 = 3
    first = far_members(w.states[t1], True)[0][0]
    g = perturb(w, t1, first)
    h1, _ = first_own_difference(w, g, t1)
    result = {"pair": [SWITCH, CYCLIC], "first change": [t1, first, "add"],
              "first hearing": h1, "settings": []}
    for t in (4, 7, h1, h1 + 1):
        state = g.states[t]
        rr = roster(state)
        d = sharing_counts(state)
        near = {rr.class_of[u] for u in rr.members if state.knots[u].roles == RECEIVER}
        sites = {"original far site": pair.far_site}
        far = far_members(state)
        if far:
            sites["nearest current strict far member"] = far[0][0]
        for family in ({'A', 'link'}, {'B', 'link'}, {'A', 'B', 'link'}, {'A'}):
            eligible = [u for u in rr.members if state.knots[u].roles == family
                        and rr.class_of[u] in near]
            if eligible:
                u = min(eligible, key=lambda v: (d[v], v))
                sites["nearest current " + "+".join(sorted(family)) + " in receiver class"] = u
        at = {"after round": t, "linked strict far candidates": len(far_members(state, True)),
              "placements": []}
        for description, u in sites.items():
            out = setting(state, u, d[u], rr.class_of.get(u) in near)
            out.update({"selection": description, "signs": []})
            for sign in ("add", "bar"):
                row = second_trial(w, g, t1, t, u, sign, 32, h1)
                out["signs"].append(row)
            at["placements"].append(out)
        result["settings"].append(at)
    waiters = []
    with_one = []
    for t in range(1, min(17, len(g.rows))):
        if t in g.edits:
            continue
        st = g.states[t]
        for u in sorted(g.rows[t].short):
            assert u in g.states[t + 1].members
            if len(st.usable(u)) == 1:
                with_one.append((st.knots[u].roles != FAR, t, u))
            else:
                waiters.append((st.knots[u].roles != FAR, t, u))
    for kind, candidates in (("one usable distinction", with_one),
                             ("several usable distinctions", waiters)):
        if not candidates:
            result["waiter with " + kind] = None
            continue
        _, t, u = min(candidates)
        st = g.states[t]
        original = st.usable(u)
        barred = edit_state(st, u, "bar")
        after = perturb(g, t, u, "bar", rounds=t + 1)
        assert barred is not None and after is not None
        assert barred.knots == st.knots and barred.holders == st.holders
        assert original[-1] in barred.barred and (u in barred.members) == (len(original) > 1)
        result["waiter with " + kind] = {
            "after round": t, "knot": u, "roles": sorted(st.knots[u].roles),
            "usable before": original, "demand without intervention": g.rows[t].owe[u],
            "waits without intervention": u in g.rows[t].short,
            "remains member after an unmarked round": u in g.states[t + 1].members,
            "barred distinction": original[-1], "usable after bar": barred.usable(u),
            "immediately remains a member": u in barred.members,
            "waits in next round with bar": u in after.rows[t].short,
            "all knots and holders identical immediately after the bar": True}
    waiter_far = "n4:g15:2110@3"
    waiting_pair = build_pair(SWITCH, waiter_far)
    waiting_run = grow(waiting_pair, 3, 4, BOUND)
    t = 1
    u = waiting_pair.far_site
    before = waiting_run.states[t]
    after_bar = perturb(waiting_run, t, u, "bar", rounds=t + 1)
    immediate = after_bar.edits[t]
    assert len(before.usable(u)) == 1 and u in waiting_run.rows[t].short
    assert before.knots == immediate.knots and before.holders == immediate.holders
    assert u not in immediate.members and u not in after_bar.states[t + 1].members
    result["separate one-usable waiter control"] = {
        "receiver": SWITCH, "far": waiter_far, "selection": "The given site of the four-knot far end",
        "cap": 3, "after round": t, "knot": u, "roles": sorted(before.knots[u].roles),
        "usable before": before.usable(u), "owed without intervention": waiting_run.rows[t].owe[u],
        "otherwise waits next round": u in waiting_run.rows[t].short,
        "next-round member without bar": u in waiting_run.states[t + 1].members,
        "usable immediately after bar": immediate.usable(u),
        "member immediately after bar": u in immediate.members,
        "member next round with bar": u in after_bar.states[t + 1].members,
        "all knots and holders identical immediately after bar": True}
    return result


def initial_data():
    return {"question": "Can a second change alter receiver-own births? Does a first hearing survive at a distinct, earlier round?",
            "bound": BOUND,
            "reading": "Compare the same history with and without its next single change. Strict own means ancestry from that end alone. Distinct receptions retain the first-only response at its first difference from the unmarked growth, and differ from first-only at a later round.",
            "censoring": "A missing difference is only through the last common round. The setting round plus the holder-step count plus one is a comparison benchmark.",
            "pilot": pilot()}


def summarize(rows):
    counts = Counter()
    for case in rows:
        trs = case.get("first trials", case.get("first trials giving hearings", []))
        counts["pairs"] += 1
        counts["first changes"] += case.get("first changes", len(trs))
        for x in trs:
            if x["first hearing"] is None:
                continue
            h1 = x["first hearing"]
            counts["first changes heard"] += 1
            for at in x["settings"]:
                t2 = at["t2"]
                for site in at["sites"]:
                    for mark in site["signs"]:
                        if not mark["applied"]:
                            continue
                        counts["second marks applied"] += 1
                        counts["set after first hearing"] += int(t2 >= h1)
                        counts["common round at least setting plus holder steps plus one"] += int(
                            t2 + site["holder steps"] + 1 <= mark["common with first only"])
                        h2 = mark["first-only vs both"]
                        counts["second alters own births versus first only"] += int(h2 is not None)
                        if h2 is not None:
                            counts["first-only difference suppressed through common with no change"] += int(
                                mark["no-change vs both"] is None and
                                h1 <= min(mark["common with first only"], mark["common with no change"]))
                            counts["distinct successive receptions"] += int(mark["distinct successive hearings"])
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--broader", type=int, metavar="CASES_PER_STRATUM")
    parser.add_argument("--witness", action="store_true")
    parser.add_argument("--canonical-first", metavar="QUIET_PAIRS", type=int)
    parser.add_argument("--refresh-witness", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--horizon", choices=(18, 32), type=int, default=18)
    parser.add_argument("--first-rounds", type=int, nargs="+", default=[3, 1, 2])
    parser.add_argument("--cases", type=int, nargs="+", default=list(range(len(CASES))))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = (json.loads(args.refresh_witness.read_text()) if args.refresh_witness else initial_data())
    if args.all:
        out["design"] = {
            "targeted": "Seven named cases. Change each linked strict far member with each sign after rounds 3, 1, 2. When heard, try both signs at each linked strict far member in the next six setting rounds and immediately after the first hearing and one round later, where the comparison reaches the setting. Read to round 18 or 10,000 knots.",
            "longer check": "For the four-knot far end with loose counts 1,1,1,2 and the other four-knot receiver with loose counts 3,2,2,2, the same tests from a first change after round 3 were read to round 32 or 10,000 knots.",
            "broader": "Equal weighting within each of four strata, seed 26112613. Up to 20 label pairs per stratum with an initial link, no link at round 16 and a baseline that completed round 16. Two strata use the switch as receiver, two use census receivers. Each is split by link present versus absent or missing at round 3. First changes after rounds 1 and 2, through round 16 or 10,000 knots.",
            "higher caps": "The matched switch receiver under caps five and six with the cyclic four-knot far end. First change after round 1, allowing an earlier arrival. Read to round 15 or 10,000 knots.",
            "selection": "The first two named starts have recorded first hearings. The panel includes shorter and longer surviving links, a far end whose own members are lost, an alternative receiving start, and the cap of four. Stop an exploratory panel on its first two separate strict-far receptions. The close-to-receiver, spent-site and waiting checks are controls."}
        out["search"] = run_search(CASES)
        out["longer check"] = run_search(CASES[:2], 32, (3,))
        out["higher caps"] = run_search([(f"tri:{cap - 2}22@0", CYCLIC, cap) for cap in (5, 6)],
                                         15, (1,))
        out["broader"] = broader(20)
    elif args.search:
        out["search"] = run_search([CASES[i] for i in args.cases], args.horizon, args.first_rounds)
    elif args.broader:
        out["broader"] = broader(args.broader)
    elif args.canonical_first:
        out["canonical first, earlier second settings"] = canonical_first(args.canonical_first)
    elif not (args.pilot or args.witness or args.refresh_witness):
        parser.error("give --pilot, --search, --broader, --witness or --all")
    if args.all or args.witness or args.refresh_witness:
        out["four-knot cancellation"] = {
            sign: detailed_witness(CASES[0], (3, 46, "add", 4, 60, sign))
            for sign in ("add", "bar")}
        out["near, original-site and waiting controls"] = diagnostics()
    if args.all or args.refresh_witness:
        out["canonical first, earlier second settings"] = canonical_first(1)
        for panel in ("search", "longer check", "higher caps", "broader"):
            out.setdefault("summary", {})[panel] = summarize(out[panel])
        out["maximum RSS KiB"] = max(out.get("maximum RSS KiB", 0),
                                     resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if args.refresh_witness:
            args.out = args.refresh_witness
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")
    else:
        print(json.dumps(out["pilot"]))


if __name__ == "__main__":
    main()
