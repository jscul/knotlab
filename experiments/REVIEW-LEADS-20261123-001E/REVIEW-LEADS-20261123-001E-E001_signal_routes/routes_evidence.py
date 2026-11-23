"""Replays that bear on individual routes of the table of routes (run after the five checks).

1. The two detector sides of the concealed-shortage preparation (live descendants of knots A.V and B.V):
   whether they ever meet, per round, for each of the four types and both laws.
2. Whether the four types differ in the numbers of parents and fresh distinctions of any round.
3. A stalled start: the next round is the same stall, with the same shortages, every time.
4. The smallest parity closing (and its edited versions): the births of the round and the allocation
   classes at the funded step, with the R3 comparison.

Run (from the repository root):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""

from collections import Counter, deque
import json
import random

import engine as E
import r1_holdings as R1
import r3_allocations as R3
import starts as S

ARTIFACTS = R1.ARTIFACTS
ROUNDS = 20


def end_graph(frame):
    owners = E.holders_of(frame)
    loose = E.loose_of(frame, owners)
    nbrs = E.neighbours_of(frame, owners)
    live = {k for k, v in loose.items() if v}
    adj = {k: set() for k in live}
    for w in range(len(frame)):
        block = nbrs[w] & live
        for x in block:
            adj[x] |= block - {x}
    return live, adj


def end_distance(adj, sources, targets):
    seen = {s: 0 for s in sources}
    todo = deque(sources)
    while todo:
        v = todo.popleft()
        if v in targets:
            return seen[v]
        for w in adj[v]:
            if w not in seen:
                seen[w] = seen[v] + 1
                todo.append(w)
    return None


def detector_sides(u, v, law):
    rows, _, _ = S.concealed_module().physical(u, v, "primary", u, v)
    names = list(rows)
    a, b = names.index("A.V"), names.index("B.V")
    stars = S.concealed_start(u, v, u, v)
    h = E.grow_history(stars, law, ROUNDS, knot_cap=2000, cross_check=False)
    anc = [{k} for k in range(len(h.frames[0]))]
    per_round, signatures = [], []
    for t, frame in enumerate(h.frames):
        if t:
            for birth in h.births[t - 1]:
                s = {birth.knot}
                for p in birth.parents:
                    s |= anc[p]
                anc.append(s)
            signatures.append(sorted(Counter((len(x.parents), len(x.fresh)) for x in h.births[t - 1]).items()))
        live, adj = end_graph(frame)
        A = {k for k in live if a in anc[k]}
        B = {k for k in live if b in anc[k]}
        per_round.append({"round": t, "live_descendants_of_A.V": len(A), "live_descendants_of_B.V": len(B),
                          "common_live_descendant": bool(A & B),
                          "end_distance_between_the_two_sides": end_distance(adj, A, B) if A and B else None})
    return per_round, signatures


def main():
    out = {"detector_sides": {}, "birth_statistics_equal_across_types": {}, "stall_persistence": {}, "closing": {}}
    for law in E.LAWS:
        sigs = {}
        for u in (0, 1):
            for v in (0, 1):
                rounds, signature = detector_sides(u, v, law)
                out["detector_sides"][f"{law}_type_{u}{v}"] = {
                    "rounds": len(rounds) - 1,
                    "ever_a_common_live_descendant": any(r["common_live_descendant"] for r in rounds),
                    "ever_a_finite_end_distance": any(r["end_distance_between_the_two_sides"] is not None for r in rounds),
                    "per_round": rounds}
                sigs[(u, v)] = signature
        base = sigs[(0, 0)]
        out["birth_statistics_equal_across_types"][law] = all(sigs[k] == base for k in sigs)
    for name in ("stall_00", "stall_01", "stall_10", "concealed_type_00_unedited", "concealed_type_11_unedited"):
        stars = R1.start_for(name)
        for law in E.LAWS:
            plans = [E.plan_round(stars, law) for _ in range(3)]
            h = E.grow_history(stars, law, 5, cross_check=False)
            out["stall_persistence"][f"{name}_{law}"] = {
                "status": [p.status for p in plans], "same_shortages": all(p.shortages == plans[0].shortages for p in plans),
                "shortages": [list(s) for s in plans[0].shortages], "rounds_grown_in_five_attempts": len(h.frames) - 1}
    rng = random.Random(2026112305)
    for name in ("closing_00", "closing_01", "closing_10", "closing_11"):
        stars = R1.start_for(name)
        for law in E.LAWS:
            plan = E.plan_round(stars, law)
            entry = {"status": plan.status, "births": len(plan.parents), "fresh_counts": list(plan.fresh_counts),
                     "implied_sole_birth": plan.implied}
            if plan.status == "extend":
                record, _ = R3.analyse_step(name, stars, law, 4, rng, 0)
                entry["allocation_classes"] = record["allocation_classes"]
                entry["classes_with_changed_round_births"] = record["classes_with_changed_round_births"]
                entry["classes_with_changed_later_births"] = record["classes_with_changed_later_births"]
                entry["grown_allowed_word_counts"] = record["distinct_grown_allowed_word_counts"]
                entry["max_tv_uniform_present"] = record["max_tv_uniform_present_vs_canonical"]
                entry["max_tv_old_word"] = record["max_tv_old_word_vs_canonical"]
            out["closing"][f"{name}_{law}"] = entry
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "routes_evidence.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for key, value in out["detector_sides"].items():
        print(key, "rounds", value["rounds"], "common live descendant ever:", value["ever_a_common_live_descendant"],
              "finite end distance ever:", value["ever_a_finite_end_distance"])
    print("birth statistics equal across the four types:", out["birth_statistics_equal_across_types"])
    for key, value in out["stall_persistence"].items():
        print(key, value)
    for key, value in out["closing"].items():
        print(key, value)


if __name__ == "__main__":
    main()
