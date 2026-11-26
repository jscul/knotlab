"""Read the ancestry, age and fate of the classes linking the two patterns."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import random
import resource
from time import perf_counter

from growth import FAR, RECEIVER, build_pair, far_members, first_own_difference, grow, perturb, roster


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SEED = 26112603
CHECK_ROUNDS = (4, 8, 12, 16)
TRACE_PAIR = ("tri:122@0", "n3:g6:122@0", 3)
SPLIT_PAIR = ("tri:122@0", "n3:g7:112@0", 3)


def cases():
    strata = defaultdict(list)
    archived = {}
    for path in sorted(STUDY.glob("again_linked_runs_*.jsonl.gz")):
        with gzip.open(path, "rt") as stream:
            for line in stream:
                entry = json.loads(line)
                a, b, cap = entry["A"], entry["B"], int(entry["law"].removeprefix("CAP-"))
                label = f"switch at cap {cap}" if a.startswith("tri:") else f"census receiver with {b}"
                strata[label].append((a, b, cap))
                change = entry["changes"][0]
                first = next(c for c, status in enumerate(change["linked after it"], 1)
                             if c > 3 and status is not True)
                assert (a, b, cap) not in archived
                archived[a, b, cap] = (change["knot"], change["sharings"], first)
    assert sum(map(len, strata.values())) == 293 and len(strata) == 6
    return strata, archived


def classes(state):
    """Group the live members by their linked class and identify both strict ancestries."""
    r = roster(state)
    members = defaultdict(list)
    receiver, far = set(), set()
    for u in r.members:
        cls = r.class_of[u]
        members[cls].append(u)
        if state.knots[u].roles == RECEIVER:
            receiver.add(cls)
        elif state.knots[u].roles == FAR:
            far.add(cls)
    return r, members, receiver, far


def descend(previous, state, current):
    """For each previous class, find all classes containing its next live descendants."""
    successors = defaultdict(set)
    for u in current.members:
        knot = state.knots[u]
        parents = knot.parents if knot.born == state.round else (u,)
        for p in parents:
            successors[previous.class_of[p]].add(current.class_of[u])
    return successors


def inside(row, state, members):
    return {
        "size": len(members),
        "receiver_only": sum(state.knots[u].roles == RECEIVER for u in members),
        "far_only": sum(state.knots[u].roles == FAR for u in members),
        "both_patterns_in_ancestry": sum({"A", "B"} <= state.knots[u].roles for u in members),
        "older": sum(state.knots[u].born < state.round for u in members),
        "short_next": None if row is None else len(row.short.intersection(members)),
    }


def baseline_counts(g):
    profile, common = [], []
    for c, state in enumerate(g.states[1:], 1):
        r, by_class, a, b = classes(state)
        shared = a & b
        if not shared:
            raise AssertionError(f"Expected a common class after round {c}")
        members = [u for cls in shared for u in by_class[cls]]
        # Read the next round's waiting separately from having already waited.
        # The endpoint has no next step in this 16-round check.
        next_row = g.rows[c] if c < len(g.rows) else None
        count = inside(next_row, state, members)
        count["classes"] = len(shared)
        count["parts"] = len({r.part_of[u] for u in members})
        profile.append(count)
        if c in CHECK_ROUNDS:
            common.append(len(members))
    assert len(profile) == 16
    return {
        "sizes_at_4_8_12_16": common,
        "member_rounds": sum(v["size"] for v in profile),
        "member_rounds_with_known_next_step": sum(v["size"] for v in profile[:-1]),
        "older_member_rounds": sum(v["older"] for v in profile),
        "rounds_with_older_member": [c for c, v in enumerate(profile, 1) if v["older"]],
        "next_round_waits_after_1_to_15": sum(v["short_next"] for v in profile[:-1]),
        "rounds_with_next_round_wait": [c for c, v in enumerate(profile[:-1], 1) if v["short_next"]],
        "rounds_with_multiple_classes": [c for c, v in enumerate(profile, 1) if v["classes"] > 1],
        "rounds_with_multiple_parts": [c for c, v in enumerate(profile, 1) if v["parts"] > 1],
        "joint_ancestry_at_4_8_12_16": [v["both_patterns_in_ancestry"] for c, v in enumerate(profile, 1)
                                           if c in CHECK_ROUNDS],
        "rounds_with_no_member_of_joint_ancestry": [c for c, v in enumerate(profile, 1)
                                                     if not v["both_patterns_in_ancestry"]],
    }


def first_loss(g, t0):
    previous, previous_members, a, b = classes(g.edits[t0])
    shared = a & b
    had_split = False
    waiting = []
    for c in range(t0 + 1, len(g.states)):
        state = g.states[c]
        current, members, a, b = classes(state)
        row = g.rows[c - 1]
        old_members = [u for k in shared for u in previous_members[k]]
        if row.short.intersection(old_members):
            waiting.append(c)
        successors = descend(previous, state, current)
        new_shared = a & b
        splits = any(len(successors[k]) >= 2 for k in shared)
        if not new_shared:
            counts = []
            for cls in sorted(shared):
                counts.append([
                    inside(None, state, members[d])
                    for d in sorted(successors[cls])
                ])
            return {
                "round": c,
                "far_still_present": bool(b),
                "receiver_still_present": bool(a),
                "common_class_split_at_loss": splits,
                "common_class_split_after_mark_before_loss": had_split,
                "short_in_common_class_in_transition_to_rounds": waiting,
                "descendant_classes_of_previously_common_classes": counts,
            }
        had_split |= splits
        previous, previous_members, shared = current, members, new_shared
    raise AssertionError(f"Still linked after round {g.states[-1].round}")


def read_case(case, expected):
    a, b, cap = case
    g = grow(build_pair(a, b), cap, 16, 10000)
    marked, sharings = far_members(g.states[3], True)[0]
    h = perturb(g, 3, marked, rounds=10, bound=10000)
    loss = first_loss(h, 3)
    assert (marked, sharings, loss["round"]) == expected, case
    return {
        "A": a, "B": b, "cap": cap, "changed_far_member": marked, "holder_steps": sharings,
        "baseline": baseline_counts(g), "first_addition": loss,
    }


def detailed_trace(rounds=13):
    a, b, cap = TRACE_PAIR
    g = grow(build_pair(a, b), cap, rounds, 10000)
    target, sharings = far_members(g.states[3], True)[0]
    h = perturb(g, 3, target)
    trace = {}
    for name, branch in (("unchanged", g), ("addition", h)):
        history, work = [], []
        previous = None
        for c in range(min(rounds, 7) + 1):
            state = branch.edits.get(c, branch.states[c])
            r, by_class, near, far = classes(state)
            next_row = branch.rows[c] if c < len(branch.rows) else None
            successor = descend(previous, state, r) if previous else {}
            records = []
            for cls, group in sorted(by_class.items()):
                records.append(dict(
                    cls=cls,
                    parts=len({r.part_of[u] for u in group}),
                    previous_classes=[k for k, v in successor.items() if cls in v],
                    **inside(next_row, state, group),
                ))
            history.append({"round": c, "classes": records})
            previous = r
            if c < 3 or c > 5 or next_row is None:
                continue
            after = branch.states[c + 1]
            local = []
            for cls in sorted(near & far):
                for u in by_class[cls]:
                    if state.knots[u].roles != FAR:
                        continue
                    births = []
                    for v in next_row.births:
                        k = after.knots[v]
                        if u in k.parents:
                            births.append({"id": v, "parents": list(k.parents), "ancestry": sorted(k.roles),
                                           "fresh": k.fresh, "next_demand": next_row.demand.get(v, 0)})
                    local.append({"far_member": u, "parents": list(state.knots[u].parents),
                                  "usable": len(state.usable(u)), "owed": next_row.owe.get(u, 0),
                                  "groups": [list(q) for q in next_row.groups if u in q],
                                  "births_using_member": births})
            work.append({"growth_round": c + 1, "short_anywhere": sorted(next_row.short),
                         "cancelled_groups": sum(not next_row.short.isdisjoint(q) for q in next_row.groups),
                         "strict_far_members_in_common_class": local})
        trace[name] = {"classes_after_each_round": history, "local_growth": work,
                       "receiver_own_birth_counts": [len(r.own_births) for r in branch.rows]}
    first, last = first_own_difference(g, h, 3)
    trace.update({"A": a, "B": b, "cap": cap, "far_member": target, "holder_steps": sharings,
                  "description": "Three mutually sharing receiver knots, site with one loose distinction and the others two. "
                                 "The far three knots form a path, joined at the middle knot with one loose distinction, "
                                 "the ends with two each before the meeting.",
                  "first_receiver_difference": first, "last_round_read": last})
    return trace


def split_and_rescue():
    """Follow the additional partner and change supply at the one short knot."""
    a, b, cap = SPLIT_PAIR
    original = grow(build_pair(a, b), cap, 8, 10000)
    target, steps = far_members(original.states[3], True)[0]
    marked = perturb(original, 3, target)
    state = marked.states[7]
    row = marked.rows[7]
    short, = row.short
    short_label = state.knots[short].label
    earlier = original.states[7]
    counterpart, = [u for u in earlier.members if earlier.knots[u].label == short_label]
    partners = sorted({u for g in row.groups if short in g for u in g if u != short})
    original_names = {k.label for k in earlier.knots}
    added_partner, = [u for u in partners if state.knots[u].label not in original_names]
    new_chain = []
    u = added_partner
    while u is not None:
        knot = state.knots[u]
        new_chain.append({"id": u, "round": knot.born, "parents": list(knot.parents), "kind": knot.kind})
        unmatched = [p for p in knot.parents if state.knots[p].label not in original_names]
        assert len(unmatched) <= 1
        u = unmatched[0] if unmatched else None
    new_chain.reverse()
    assert new_chain[0]["parents"] == [target] and len(new_chain) == 4
    assert sorted(set(state.knots[short].parents).intersection(state.knots[added_partner].parents))
    partner_control = min(partners)
    restored = perturb(marked, 7, short)
    control = perturb(marked, 7, partner_control)
    paths = {}
    for label, branch, local in (("unchanged", original, counterpart), ("first_addition", marked, short),
                                 ("supply_short_knot", restored, short), ("supply_one_of_its_partners", control, short)):
        before = branch.edits.get(7, branch.states[7])
        r8 = branch.rows[7]
        after = branch.states[8]
        pre = classes(before)
        _, members, near, far = classes(after)
        paths[label] = {
            "classes_sizes_after_7": sorted(map(len, pre[1].values())),
            "knot_whose_supply_is_read": local,
            "usable": len(before.usable(local)), "owed": r8.owe[local],
            "groups_of_this_knot": [list(g) for g in r8.groups if local in g],
            "all_short_members_in_round_8": sorted(r8.short),
            "all_cancelled_groups": [list(g) for g in r8.groups if not r8.short.isdisjoint(g)],
            "classes_after_8": [inside(None, after, v) for v in members.values()],
            "births_in_round_8": len(r8.births), "knots_after_8": len(after.knots),
            "linked_after_8": bool(near & far),
        }
    assert [v["linked_after_8"] for v in paths.values()] == [True, False, True, False]
    return {
        "A": a, "B": b, "cap": cap, "holder_steps": steps, "first_addition_at_member": target,
        "description": "Both starts have three mutually sharing knots. The receiver has loose counts 1,2,2 and "
                       "the far end has 1,1,2. Both meet at the first one-loose knot.",
        "local_comparison": "With the extra offshoot after round 3, follow the unmatched child at each of the next "
                            "three rounds. The round-7 child and the eventual short knot have a parent in common. "
                            "This gives a fourth distinct partner to a knot with the same parent-derived name "
                            "as a three-partner knot in the unchanged growth. The cap supplied three in both.",
        "new_chain_to_fourth_partner": new_chain,
        "common_parent_of_new_partner_and_short_knot": sorted(
            set(state.knots[short].parents) & set(state.knots[added_partner].parents)),
        "partner_control_id": partner_control, "short_knot_id": short, "paths": paths,
        "scope": "The two extra supplies after round 7 are controls for the immediate loss of the link. "
                 "They are placed at knots with mixed ancestry. The check ends in round 8.",
    }


def totals(records):
    result = {}
    for label, values in records.items():
        profiles = [v["baseline"] for v in values]
        losses = [v["first_addition"] for v in values]
        result[label] = {
            "pairs": len(values),
            "sizes_at_4_8_12_16": dict(sorted(Counter(
                ",".join(map(str, p["sizes_at_4_8_12_16"])) for p in profiles).items())),
            "member_rounds": sum(p["member_rounds"] for p in profiles),
            "member_rounds_with_known_next_step": sum(p["member_rounds_with_known_next_step"] for p in profiles),
            "older_member_rounds": sum(p["older_member_rounds"] for p in profiles),
            "pairs_with_older_members": sum(bool(p["older_member_rounds"]) for p in profiles),
            "pairs_with_older_member_by_round": dict(sorted(Counter(
                c for p in profiles for c in p["rounds_with_older_member"]).items())),
            "next_round_waits_after_1_to_15": sum(p["next_round_waits_after_1_to_15"] for p in profiles),
            "pairs_with_wait_in_following_transition_by_round": dict(sorted(Counter(
                c for p in profiles for c in p["rounds_with_next_round_wait"]).items())),
            "pairs_with_no_joint_ancestry_member_by_round": dict(sorted(Counter(
                c for p in profiles for c in p["rounds_with_no_member_of_joint_ancestry"]).items())),
            "pairs_ever_in_multiple_common_classes": sum(bool(p["rounds_with_multiple_classes"]) for p in profiles),
            "pairs_ever_in_multiple_common_parts": sum(bool(p["rounds_with_multiple_parts"]) for p in profiles),
            "pairs_with_a_class_split_at_loss": sum(l["common_class_split_at_loss"] for l in losses),
            "pairs_with_a_prior_common_class_split_since_mark": sum(
                l["common_class_split_after_mark_before_loss"] for l in losses),
            "pairs_with_shortness_in_common_class_between_mark_and_loss": sum(
                bool(l["short_in_common_class_in_transition_to_rounds"]) for l in losses),
            "loss_rounds": dict(sorted(Counter(l["round"] for l in losses).items())),
            "far_absent_at_loss": sum(not l["far_still_present"] for l in losses),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Time one complete pair in each stratum.")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2400000 * 1024, 2400000 * 1024))
    start = perf_counter()
    rng = random.Random(SEED)
    strata, archived = cases()
    records = defaultdict(list)
    calibration = {}
    for label, pairs in sorted(strata.items()):
        rng.shuffle(pairs)
        begin = perf_counter()
        records[label].append(read_case(pairs[0], archived[pairs[0]]))
        calibration[label] = {"pair": pairs[0], "seconds": round(perf_counter() - begin, 4)}
    begin = perf_counter()
    detailed_trace(6)
    trace_pilot = perf_counter() - begin
    begin = perf_counter()
    a, b, cap = SPLIT_PAIR
    split_prefix = grow(build_pair(a, b), cap, 6, 10000)
    target, _ = far_members(split_prefix.states[3], True)[0]
    perturb(split_prefix, 3, target)
    split_pilot = perf_counter() - begin
    if args.pilot:
        print(json.dumps({"round_6_trace_seconds": trace_pilot, "round_6_split_seconds": split_pilot,
                          "strata": calibration}, indent=2))
        return
    for label, pairs in sorted(strata.items()):
        records[label].extend(read_case(case, archived[case]) for case in pairs[1:])
    trace = detailed_trace()
    assert trace["first_receiver_difference"] == 13
    output = {
        "reading": "One entry per selected pair. For unchanged growth after rounds 1 through 16, a member is older if "
                   "it was born before the snapshot. Waiting in the next transition is read separately after rounds "
                   "1 through 15. A common class contains at least one strictly own live member of each end. "
                   "At loss, its successors are classified by actual parentage, with an unchanged member its own successor. "
                   "The class number is local to its snapshot. The census file does not supply class ages or sizes.",
        "extent": "All 293 archived second-pass selections under caps three to six; each baseline through round 16, "
                  "its first addition through the first loss of a common class (at most round 10). "
                  "The detailed control and first-addition pair are read through round 13. A complementary class split "
                  "and its two one-knot controls are read through round 8.",
        "pilot_seed": SEED,
        "pilot_exact_pair_seconds": calibration,
        "pilot_first_six_trace_rounds_seconds": round(trace_pilot, 4),
        "pilot_first_six_split_rounds_seconds": round(split_pilot, 4),
        "detailed_trace": trace,
        "split_and_rescue": split_and_rescue(),
        "agreement_with_archive": "All 293 selected first additions match setting member, holder steps and first "
                                  "round where the linked reading ceases to be true.",
        "by_selection": totals(records),
        "all": totals({"pairs": sum(records.values(), [])})["pairs"],
        "cases": {label: sorted(values, key=lambda v: (v["A"], v["B"])) for label, values in records.items()},
        "elapsed_seconds": round(perf_counter() - start, 3),
        "maximum_resident_kibibytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (HERE / "trace.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["all"], indent=2))


if __name__ == "__main__":
    main()
