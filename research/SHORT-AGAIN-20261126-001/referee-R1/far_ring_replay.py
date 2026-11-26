"""Rebuild the far baselines, ring returns, and a sample of ring changes."""

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import random

import networkx as nx

from far_ring import FEWER, archive, distance_group
from growth import A_ONLY, B_ONLY, Growth, build, distance_from, first_difference, grow, joinable, met_sets


WAIT = "CANCEL-WAIT"
CAP = 3000
HORIZON = 16
SEED = 20261126


@dataclass
class Part:
    members: frozenset
    holdings: dict
    met: tuple
    has_live_meeting: bool

    def fingerprint(self):
        return (Counter(self.holdings.values()), Counter(map(len, self.met)))

    def incidence(self):
        incidence = nx.Graph()
        for member, holding in self.holdings.items():
            incidence.add_node(member, mark=holding)
        for number, group in enumerate(self.met, 1):
            incidence.add_node(-number, mark=(0, 0))
            incidence.add_edges_from((-number, member) for member in group)
        return incidence


def roster(growth):
    current = set(growth.usable)
    maximal, per_member = met_sets(sorted(current), growth.meets.__getitem__)
    joined = joinable(sorted(current), maximal)
    direct = {u: growth.meets[u] & current for u in current}
    linked = {u: joined[u] | direct[u] for u in current}
    receiver_members = [u for u in current if growth.roles[u] == A_ONLY]
    reaches_receiver = frozenset(distance_from(linked, receiver_members))
    unseen = set(current)
    parts = []
    part_by_member = {}
    for member in sorted(current):
        if member not in unseen:
            continue
        others = frozenset(distance_from(joined, (member,)))
        unseen.difference_update(others)
        met = {group for u in others for group in per_member[u]}
        part = Part(
            others,
            {u: (len(growth.usable[u]), growth.barred[u]) for u in others},
            tuple(sorted(met, key=lambda group: tuple(sorted(group)))),
            any(direct[u] for u in others),
        )
        parts.append(part)
        part_by_member.update(dict.fromkeys(others, part))
    return parts, part_by_member, reaches_receiver


def recurrence_scan(growth, snapshots, who):
    found = []
    for earlier, (parts, _, _) in enumerate(snapshots[1:-1], 1):
        first_after = growth.rows[earlier - 1].knots
        for part in parts:
            if len(part.members) < 5 or any(growth.roles[k] != who for k in part.members):
                continue
            children = set(part.members)
            start = first_after
            for later in range(earlier + 1, len(snapshots)):
                end = growth.rows[later - 1].knots
                for knot in range(start, end):
                    if all(p in children for p in growth.parents[knot]):
                        children.add(knot)
                start = end
                hits = [
                    target for target in snapshots[later][0]
                    if target.members != part.members and target.members <= children
                    and len(target.members) == len(part.members)
                    and target.fingerprint() == part.fingerprint()
                    and nx.vf2pp_is_isomorphic(part.incidence(), target.incidence(), node_label="mark")
                ]
                if hits:
                    found.append((earlier, later, part, hits[0]))
                    break
    return found


def start_with_snapshots(setup, law, rounds, requested):
    growth = Growth(setup, law, WAIT)
    snapshots = [roster(growth)]
    forks = {}
    for round_number in range(1, rounds + 1):
        growth.run(round_number, CAP)
        if len(growth.rows) < round_number:
            break
        snapshots.append(roster(growth))
        if round_number in requested:
            forks[round_number] = growth.fork()
    return growth, snapshots, forks


def nearest(growth, who):
    other = (u for u, role in enumerate(growth.roles) if role != who)
    distances = distance_from(growth.meets, other)
    living = [u for u in growth.usable if growth.roles[u] == who]
    return sorted(living, key=lambda u: (distances.get(u, float("inf")), u))[:5]


def fields(growth):
    return {
        "knots": [r.knots for r in growth.rows],
        "short by": [r.short_by for r in growth.rows],
        "births by": [r.births_by for r in growth.rows],
        "own births": [len(r.own_births) for r in growth.rows],
    }


def audit_mark(whole, changed_at, marked_knot, state):
    changed = state.fork()
    changed.mark(marked_knot)
    changed.run(HORIZON, CAP)
    hearing = first_difference(whole, changed, after=changed_at)
    return [changed_at, marked_knot, hearing, min(len(whole.rows), len(changed.rows))], changed


def ring_run(row, rng, mark_count):
    d, law, join = (row[key] for key in ("d", "law", "join"))
    sampled = rng.sample(row["marks"], min(mark_count, len(row["marks"])))
    heard = [m for m in row["marks"] if m[2] is not None]
    sampled.extend(m for m in heard if m not in sampled)
    requested = {m[0] for m in row["marks"]}
    whole, snapshots, forks = start_with_snapshots(build("source", "ring", d, join), law, HORIZON, requested)
    stub = grow(build("source", "stub", d, join), law, WAIT, HORIZON, CAP)
    assert fields(whole) == row["whole"], (d, law, join, "ring")
    assert fields(stub) == row["stub"], (d, law, join, "stub")
    assert [a.round for a, b in zip(whole.rows, stub.rows) if a.own_births != b.own_births] == row[
        "own births differ from with a stub, rounds"
    ], (d, law, join, "unshifted receiver births")

    returns = recurrence_scan(whole, snapshots, B_ONLY)
    assert [[earlier, later, len(source.members)] for earlier, later, source, _ in returns] == row["ring returns"], (
        d, law, join, "returns"
    )
    selected = {}
    for _, later, _, target in returns:
        if later < len(whole.rows):
            selected.setdefault(later, sorted(target.members))
    if selected:
        expected = [(after, u) for after in sorted(selected)[:6] for u in selected[after]]
    else:
        expected = [(after, u) for after in sorted(requested) for u in nearest(forks[after], B_ONLY)]
    assert expected == [tuple(mark[:2]) for mark in row["marks"]], (d, law, join, "change locations")

    isolation = Counter()
    connected_followup = Counter()
    for after, marked_knot, response, horizon in row["marks"]:
        _, member_to_part, reaches_receiver = snapshots[after]
        assert marked_knot in member_to_part
        if not reaches_receiver:
            how = "no_own_receiver_member"
        elif marked_knot not in reaches_receiver:
            how = "wholly_apart_from_receiver"
        else:
            how = "same_part_after_including_direct_live_meetings"
            connected_followup[horizon - after] += 1
        assert how == "same_part_after_including_direct_live_meetings" or response is None, (d, law, join, after, marked_knot)
        isolation[how] += 1

    again_count = 0
    for mark in sampled:
        after, marked_knot = mark[:2]
        replay, changed = audit_mark(whole, after, marked_knot, forks[after])
        assert replay == mark, (d, law, join, replay, mark)
        if replay[2] is not None:
            again_ahead = replay[2] + 1
            first_marked = forks[after].fork()
            first_marked.mark(marked_knot)
            first_marked.run(again_ahead, CAP)
            again_replay = [audit_mark(changed, again_ahead, u, first_marked)[0] for u in nearest(first_marked, B_ONLY)]
            assert again_replay == row["again"], (d, law, join, "second mark")
            again_count += len(again_replay)

    identical_tail = None
    if d >= 2 and join == "meeting" and law in FEWER:
        stub_start = d + 2
        ring_start = stub_start + (1 if law == "JOIN-FEWER" else 2)
        pairs = list(zip(whole.rows[ring_start - 1:], stub.rows[stub_start - 1:]))
        identical_tail = all(a.own_births == b.own_births for a, b in pairs)

    return {
        "steps": d,
        "law": law,
        "join": join,
        "ring_rounds": len(whole.rows),
        "stub_rounds": len(stub.rows),
        "returns": len(returns),
        "returns_with_live_meeting_in_source_part": sum(part.has_live_meeting for _, _, part, _ in returns),
        "returns_with_live_meeting_elsewhere_in_roster": sum(
            any(p.has_live_meeting for p in snapshots[s][0]) for s, _, _, _ in returns
        ),
        "mark_isolation": isolation,
        "followup_rounds_where_receiver_may_be_reached": connected_followup,
        "first_replayed": sampled,
        "second_replayed": again_count,
        "restart_own_birth_records_equal_over_overlap": identical_tail,
    }


def far_baseline(row):
    law, treatment = row["law"]
    baseline = grow(build("source", "source", row["d"]), law, treatment, HORIZON, CAP)
    assert len(baseline.rows) == row["rounds"]
    assert baseline.rows[-1].knots == row["knots"]
    assert (baseline.stop or "rounds") == row["ended"]
    assert [sum(r.short_by.values()) for r in baseline.rows] == row["short"]
    assert [r.a_kept for r in baseline.rows] == row["kept"]
    assert [len(r.own_births) for r in baseline.rows] == row["own births"]
    assert [len(r.joint_births) for r in baseline.rows] == row["joint births"]
    return baseline


def far_clearance(d, laws, far_rows):
    results = []
    for law in laws:
        row = next(r for r in far_rows if r["d"] == d and r["law"] == [law, WAIT])
        baseline = far_baseline(row)
        tested = []
        for name, observation in row["changes"].items():
            if name in ("two", "less"):
                change = ("B", 0, 2 if name == "two" else -1)
            else:
                change = ("link" if name[0] == "L" else "B", int(name[1:]), 1)
            result = grow(build("source", "source", d, change=change, remove=name == "less"), law, WAIT, HORIZON, CAP)
            replay = {
                "own": first_difference(baseline, result),
                "joint": first_difference(baseline, result, "joint_births"),
                "groups": first_difference(baseline, result, "a_cancelled"),
                "rounds": min(len(baseline.rows), len(result.rows)),
            }
            assert replay == observation, (d, law, name, replay, observation)
            tested.append({"mark": name, "heard": replay["own"], "stop": result.stop, "knots": [r.knots for r in result.rows]})
        results.append({"steps": d, "law": law, "marks": tested})
    return results


def alternate_ring_starts():
    results = []
    for law in ("CAP-3", *FEWER):
        for left, right, who in (("ring", None, A_ONLY), ("ring", "stub", A_ONLY), ("stub", "ring", B_ONLY)):
            state, snapshots, _ = start_with_snapshots(build(left, right, 1), law, 12, set())
            returns = recurrence_scan(state, snapshots, who)
            results.append({"law": law, "left": left, "right": right, "rounds": len(state.rows),
                            "returns": [[s, t, len(part.members)] for s, t, part, _ in returns]})
    return results


def mark_link_not_ring():
    results = []
    steps, placed = 4, 2
    for law in ("JOIN-FEWER", "REC-ONE-FEWER"):
        setup = build("source", "ring", steps)
        baseline = grow(setup, law, WAIT, HORIZON, CAP)
        state = grow(setup, law, WAIT, placed, CAP)
        active_links = [u for u in state.usable if state.roles[u] not in (A_ONLY, B_ONLY)]
        distances = distance_from(state.meets, (0,))
        for marked_knot in sorted(active_links, key=lambda u: (distances[u], u)):
            mark = audit_mark(baseline, placed, marked_knot, state)[0]
            barred = state.fork()
            barred.bar(marked_knot)
            barred.run(HORIZON, CAP)
            results.append({"law": law, "steps": steps, "placed_after": placed, "from_receiver_in_sharings": distances[marked_knot],
                            "mark": mark, "hearing_after_barring": first_difference(baseline, barred, after=placed),
                            "barring_rounds": min(len(baseline.rows), len(barred.rows))})
    return results


def recorded_ration_far(distances):
    results = []
    for d in distances:
        law = "REC-ONE-FEWER"
        baseline = grow(build("source", "source", d), law, WAIT, HORIZON, CAP)
        hearings = {}
        for knot in range(7):
            changed = grow(build("source", "source", d, change=("B", knot, 1)), law, WAIT, HORIZON, CAP)
            heard = first_difference(baseline, changed)
            if heard is not None:
                hearings[knot] = heard
        results.append({"steps": d, "unchanged_knots": [r.knots for r in baseline.rows], "heard_additions": hearings})
    return results


def alternate_ring_caps():
    results = []
    for join, d in (("meeting", 1), ("share", 2), ("share", 8)):
        for law in ("CAP-4", "CAP-5"):
            whole, snapshots, _ = start_with_snapshots(build("source", "ring", d, join), law, HORIZON, set())
            results.append({"law": law, "join": join, "steps": d, "rounds": len(whole.rows),
                            "returns": [[s, t, len(part.members)] for s, t, part, _ in recurrence_scan(whole, snapshots, B_ONLY)]})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="run a small subset of the same configurations")
    args = parser.parse_args()
    far = archive("far.jsonl.gz", None)
    ring = archive("ring_line_runs.jsonl.gz", None)
    selected_far = [r for r in far if r["law"][1] == WAIT and r["law"][0] in ("JOIN-FEWER", "ONE-FEWER", "BUSY-FEWER")]
    if args.pilot:
        selected_far = [r for r in selected_far if r["d"] == 4]
        pilot_ring = {(1, "CAP-3", "meeting"), (3, "ORD", "share"), (1, "ONE-FEWER", "share"), (8, "JOIN-FEWER", "meeting")}
        ring = [r for r in ring if (r["d"], r["law"], r["join"]) in pilot_ring]
    frozen = []
    for row in selected_far:
        g = far_baseline(row)
        frozen.append({"steps": row["d"], "law": row["law"][0], "knots": [r.knots for r in g.rows]})
    rng = random.Random(SEED)
    ring_replays = [ring_run(row, rng, 2) for row in ring]
    isolation = {}
    for result in ring_replays:
        key = "/".join((distance_group(result["steps"]), result["law"], result["join"]))
        isolation.setdefault(key, Counter()).update(result["mark_isolation"])
    print(json.dumps({
        "seed": SEED,
        "far_baselines": frozen,
        "far_four_step_marks": far_clearance(4, ("JOIN-FEWER", "ONE-FEWER"), far),
        "ring_replays": ring_replays,
        "ring_isolation": isolation,
        "same_far_starts_with_recorded_one_fewer": recorded_ration_far([4] if args.pilot else range(1, 9)),
        "bare_ring_and_stub_controls": alternate_ring_starts(),
        "alternate_caps": alternate_ring_caps(),
        "four_step_link_controls": mark_link_not_ring(),
    }, indent=2))


if __name__ == "__main__":
    main()
