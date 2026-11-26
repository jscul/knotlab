"""Independent recount and replay for the second change and the peeling prediction."""

import argparse
from collections import Counter, defaultdict, deque
import gzip
from itertools import combinations
import json
from pathlib import Path
import random

from growth import A_ONLY, B_ONLY, Growth, build, changes, first_difference, groups_for, grow


STUDY = Path(__file__).resolve().parent.parent
SEED = 726591


def read_lines(name):
    with gzip.open(STUDY / name, "rt") as source:
        yield from map(json.loads, source)


def case_key(row):
    return row["A"], row["B"], row["d"], tuple(row["law"])


def selected_first_changes():
    out = {}
    for row in read_lines("jam_d3_meeting.jsonl.gz"):
        if row.get("law", [None, None])[1] != "CANCEL-WAIT":
            continue
        first = next(
            (c for c in row["changes"] if c["heard"] is not None and c["distance"] >= 3),
            None,
        )
        if first is not None:
            key = case_key(row)
            assert key not in out
            out[key] = row, first
    return out


def span(values):
    values = list(values)
    return [min(values), max(values)] if values else None


def waiting_codes(trials):
    return Counter(
        "".join("1" if w else "0" for w in t["waiting"])
        for t in trials
        if t["heard"] is not None
    )


def count_stage(rows, index):
    tried = [r for r in rows if len(r["again"]) > index and r["again"][index]]
    trials = [t for r in tried for t in r["again"][index]]
    heard = [t for t in trials if t["heard"] is not None]
    hits = {(r["A"], r["B"]) for r in tried if any(t["heard"] is not None for t in r["again"][index])}
    seven_steps = [t for t in trials if t["sharings from A"] == 7]
    return {
        "pairs with at least one placement": len(tried),
        "pairs by number of placements": dict(Counter(len(r["again"][index]) for r in tried)),
        "pairs that heard": len(hits),
        "distinct receivers and senders among hearing pairs": [len(set(a for a, _ in hits)), len(set(b for _, b in hits))],
        "receivers by number of senders that heard": dict(Counter(a for a, _ in hits)),
        "placements": len(trials),
        "placements that heard": len(heard),
        "placements at seven holder steps (total, heard)": [len(seven_steps), sum(t["heard"] is not None for t in seven_steps)],
        "placed after round": dict(Counter(t["set after round"] for t in trials)),
        "number of common comparison rounds after placement": dict(Counter(t["rounds"] - t["set after round"] for t in trials)),
        "common comparison rounds for placements not heard": dict(Counter(t["rounds"] - t["set after round"] for t in trials if t["heard"] is None)),
        "placements heard by round": dict(Counter(t["heard"] for t in heard)),
        "hearings by rounds elapsed after placement": dict(Counter(t["heard"] - t["set after round"] for t in heard)),
        "heard placements by holder steps": dict(Counter(t["sharings from A"] for t in heard)),
        "range of finite holder steps for all placements": span(t["sharings from A"] for t in trials if t["sharings from A"] is not None),
        "placements with no finite holder steps": sum(t["sharings from A"] is None for t in trials),
        "waiting at hearing (unmarked then marked branch, 1=yes)": dict(waiting_codes(trials)),
    }


def hearing_pairs(rows):
    return {(r["A"], r["B"]) for r in rows if r["again"] and any(t["heard"] is not None for t in r["again"][0])}


def recount_again(limit=None):
    agreed = selected_first_changes()
    rows = list(read_lines("again_runs.jsonl.gz"))
    assert len({case_key(r) for r in rows}) == len(rows)
    assert {case_key(r) for r in rows} == agreed.keys()
    by_law = defaultdict(list)
    errors = []
    nearest_start = Counter()
    for row in rows[:limit]:
        key = case_key(row)
        original, selected = agreed[key]
        nearest_start[initial_nearest(key, selected["at"])] += 1
        expected = (
            selected["at"],
            selected["heard"],
            [selected["waiting own without"], selected["waiting own with"]],
            [original["rounds"], len(selected["own births with"])],
        )
        actual = row["first"], row["h1"], row["waiting at h1"], row["rounds"]
        if actual != expected:
            errors.append([key, expected, actual])
        by_law[row["law"][0]].append(row)

    results = {}
    for law, cases in sorted(by_law.items()):
        by_rank = Counter()
        chose_later = 0
        no_second = []
        no_third = []
        for row in cases:
            data = row["again"]
            if not data or not data[0]:
                no_second.append({k: row[k] for k in ("A", "B", "first", "h1", "rounds", "again")})
                continue
            placements = data[0]
            assert all(t["set after round"] == row["h1"] for t in placements)
            assert 1 <= len(placements) <= 5
            assert all(t["rounds"] > t["set after round"] for t in placements)
            hit = [(i, t["heard"]) for i, t in enumerate(placements, start=1) if t["heard"] is not None]
            if not hit:
                assert len(data) == 1
                continue
            first_rank, first_round = hit[0]
            by_rank[first_rank] += 1
            chose_later += first_round > min(r for _, r in hit)
            if len(data) < 2 or not data[1]:
                no_third.append(
                    {
                        "A": row["A"],
                        "B": row["B"],
                        "second heard": first_round,
                        "common rounds for chosen second": placements[first_rank - 1]["rounds"],
                        "third stage entered": len(data) > 1,
                    },
                )
                continue
            assert all(t["set after round"] == first_round for t in data[1])
        results[law] = {
            "pairs": len(cases),
            "first hearing by round": dict(Counter(r["h1"] for r in cases)),
            "first change sign": dict(Counter("barred" if r["first"].startswith("b") else "added" for r in cases)),
            "second": count_stage(cases, 0),
            "third": count_stage(cases, 1),
            "second with the stub": count_stage([r for r in cases if r["B"] == "stub"], 0),
            "first hearing placement by rank": dict(by_rank),
            "pairs where first successful placement heard later than another placement": chose_later,
            "pairs with no second placements": no_second,
            "why no third placement after a second hearing": dict(
                Counter(
                    "no eligible member" if r["third stage entered"] else f'hearing at common round {r["second heard"]}'
                    for r in no_third
                )
            ),
        }

    overlap = None
    if "ONE-FEWER" in by_law and "REC-ONE-FEWER" in by_law:
        first_hits = hearing_pairs(by_law["ONE-FEWER"])
        second_hits = hearing_pairs(by_law["REC-ONE-FEWER"])
        overlap = [len(first_hits & second_hits), len(first_hits - second_hits), len(second_hits - first_hits)]
    return {
        "recorded rows": len(rows),
        "recounted rows": sum(map(len, by_law.values())),
        "recorded first-change selection equals all qualifying jam rows": True,
        "first-change field disagreements": errors,
        "initial nearest live sender in holder steps": dict(nearest_start),
        "one-fewer pair hits (common, made only, record only)": overlap,
        "by law": results,
    }


def recount_peeling():
    rows = json.loads((STUDY / "peel.json").read_text())
    tallies = defaultdict(Counter)
    for row in rows:
        counts = tallies[row["law"]]
        late = sum(row["late by"].values())
        assert row["members"] == row["as predicted"] + late
        assert row["shortfalls"] == {"1": row["members"]}
        counts["marks"] += 1
        counts["members summed over marks"] += row["members"]
        counts["acted"] += row["acted"]
        counts["predicted"] += row["as predicted"]
        counts["all predicted marks"] += int(late == 0)
        counts.update({f"late by {k}": v for k, v in row["late by"].items()})
    return {law: dict(counts) for law, counts in tallies.items()}


def shortest_steps(neighbors, starts):
    dist = dict.fromkeys(starts, 0)
    queue = deque(dist)
    while queue:
        here = queue.popleft()
        for there in neighbors[here]:
            if there not in dist:
                dist[there] = dist[here] + 1
                queue.append(there)
    return dist


def initial_nearest(key, label):
    a, b, d, (law, treatment) = key
    change = next(mark for name, _, mark in changes(b, d) if name == label)
    initial = Growth(build(a, b, d, change=change), law, treatment)
    sep = shortest_steps(initial.meets, (u for u in range(len(initial.roles)) if initial.roles[u] == A_ONLY))
    return min(sep[u] for u in initial.usable if initial.roles[u] == B_ONLY)


def sample_again():
    randomizer = random.Random(SEED)
    grouped = defaultdict(list)
    for row in read_lines("again_runs.jsonl.gz"):
        heard = bool(row["again"] and any(t["heard"] is not None for t in row["again"][0]))
        grouped[row["law"][0], heard].append(row)
    sample = []
    for bucket, rows in sorted(grouped.items()):
        empty = [r for r in rows if not r["again"] or not r["again"][0]]
        sample.extend(sorted(empty, key=case_key))
        ordinary = [r for r in rows if r not in empty]
        sample.extend(randomizer.sample(sorted(ordinary, key=case_key), min(4, len(ordinary))))
    return sample


def own_waiting(growth, index):
    return {growth.names[u] for u in growth.rows[index].short if growth.roles[u] == A_ONLY}


def inclusive_births(branch, index):
    return tuple(sorted(
        (branch.names[b.id], b.fresh, b.places)
        for b in branch.rows[index].birth_records
        if 'A' in branch.roles[b.id]
    ))


def compare_mark(snap, whole, mark, *, bar=False):
    after = len(snap.rows)
    changed = snap.fork()
    if bar:
        changed.bar(mark)
    else:
        changed.mark(mark)
    changed.run(12, 1500)
    common = min(len(whole.rows), len(changed.rows))
    hearing = first_difference(whole, changed, after=after)
    inclusive = next(
        (i + 1 for i in range(after, common) if inclusive_births(whole, i) != inclusive_births(changed, i)),
        None,
    )
    reading = {
        "heard": hearing,
        "rounds": common,
        "waiting": None if hearing is None else [bool(whole.rows[hearing - 1].a_short), bool(changed.rows[hearing - 1].a_short)],
    }
    more = {
        "first difference including all A descent": inclusive,
        "first difference in own birth counts": next((
            i + 1 for i in range(after, common) if len(whole.rows[i].own_births) != len(changed.rows[i].own_births)
        ), None),
        "last knots": [len(whole.places), len(changed.places)],
        "post-mark rounds": [
            [
                r.round, r.knots, r.births, r.a_members, r.a_short, len(r.own_births),
            ]
            for r in changed.rows[after:]
        ],
    }
    if hearing is not None:
        waiting_before = own_waiting(whole, hearing - 1)
        waiting_after = own_waiting(changed, hearing - 1)
        acting_before = {
            whole.names[u] for u in whole.rows[hearing - 1].available
            if whole.roles[u] == A_ONLY and u not in whole.rows[hearing - 1].short
        }
        acting_after = {
            changed.names[u] for u in changed.rows[hearing - 1].available
            if changed.roles[u] == A_ONLY and u not in changed.rows[hearing - 1].short
        }
        more["own names shifting from wait to act"] = sorted(waiting_before & acting_after)
        more["own names shifting from act to wait"] = sorted(acting_before & waiting_after)
    return reading, more, changed


def replay_again(row, jam_entry, *, controls=False):
    a, b, d, (law, treatment) = case_key(row)
    jam, first_entry = jam_entry
    change = next(mark for label, _, mark in changes(b, d) if label == row["first"])
    setup = build(a, b, d, change=change)
    w = grow(build(a, b, d), law, treatment, rounds=12, bound=1500, trace=True)
    first_at = grow(setup, law, treatment, rounds=row["h1"], bound=1500, trace=True)
    first = first_at.fork().run(12, 1500)
    observed_h1 = first_difference(w, first)
    assert row["rounds"] == [len(w.rows), len(first.rows)], (a, b, law, row["rounds"], len(w.rows), len(first.rows))
    assert observed_h1 == row["h1"], (a, b, law, observed_h1, row["h1"])
    assert [bool(w.rows[observed_h1 - 1].a_short), bool(first.rows[observed_h1 - 1].a_short)] == row["waiting at h1"]
    for recorded, measured in [
        (jam["births"], [r.births for r in w.rows]),
        (jam["A members"], [r.a_members for r in w.rows]),
        (jam["A short"], [r.a_short for r in w.rows]),
        (jam["own births"], [len(r.own_births) for r in w.rows]),
        (jam["A shortfall"], [r.a_shortfall for r in w.rows]),
        (jam["shortfall"], [r.shortfall for r in w.rows]),
        (first_entry["own births with"], [len(r.own_births) for r in first.rows]),
        (first_entry["A short with"], [r.a_short for r in first.rows]),
    ]:
        assert recorded == measured, (a, b, law, recorded, measured)
    out = {
        "case": case_key(row),
        "first": row["first"],
        "first heard": observed_h1,
        "initial nearest live sender in holder steps": initial_nearest(case_key(row), row["first"]),
        "unchanged and first-change rounds compared": [len(w.rows), len(first.rows)],
        "stage details": [],
    }
    snap, current = first_at, first
    matched_paths = []
    for recorded_trials in row["again"]:
        after = len(snap.rows)
        assert after < len(current.rows)
        distances = shortest_steps(snap.meets, (u for u in range(len(snap.roles)) if snap.roles[u] == A_ONLY))
        own_live = [u for u in snap.usable if snap.roles[u] == B_ONLY]
        chosen = sorted(own_live, key=lambda u: (distances.get(u, float("inf")), u))[:5]
        assert chosen == [r["knot"] for r in recorded_trials], (a, b, law, chosen, recorded_trials)
        successful = None
        audit_trials = []
        for u, recorded in zip(chosen, recorded_trials):
            metrics, more, grown = compare_mark(snap, current, u)
            observed = {"set after round": after, "knot": u, "sharings from A": distances.get(u), **metrics}
            assert observed == recorded, (a, b, law, observed, recorded)
            audit_trials.append({**observed, **more})
            if successful is None and observed["heard"] is not None:
                successful = u, observed["heard"], grown
        out["stage details"].append(audit_trials)
        if successful is None:
            break
        u, heard, grown = successful
        matched_paths.append((snap, current, u, heard))
        snap = snap.fork()
        snap.mark(u)
        snap.run(heard, 1500)
        current = grown
    if controls:
        swapped = grow(build(a, b, d, join="share"), law, treatment, rounds=12, bound=1500, trace=True)
        try:
            swapped_setup = build(a, b, d, join="share", change=change)
        except ValueError:
            out["first-change join swap (shared distinction)"] = "change has no usable distinction to bar"
        else:
            swapped_first = grow(swapped_setup, law, treatment, rounds=12, bound=1500, trace=True)
            read = first_difference(swapped, swapped_first)
            details = {"first heard": read, "common rounds": min(len(swapped.rows), len(swapped_first.rows))}
            if read is not None and read < len(swapped_first.rows):
                switched = grow(swapped_setup, law, treatment, rounds=read, bound=1500, trace=True)
                dist = shortest_steps(switched.meets, (u for u in range(len(switched.roles)) if switched.roles[u] == A_ONLY))
                live_b = [u for u in switched.usable if switched.roles[u] == B_ONLY]
                candidates = sorted(live_b, key=lambda u: (dist.get(u, float("inf")), u))[:5]
                details["second change"] = [
                    {"knot": u, "sharings from A": dist.get(u), **compare_mark(switched, swapped_first, u)[0]}
                    for u in candidates
                ]
            out["first-change join swap (shared distinction)"] = details
        if matched_paths:
            mark_state, whole, mark, _ = matched_paths[0]
            bar_metrics, _, _ = compare_mark(mark_state, whole, mark, bar=True)
            out["bar instead of adding at first successful second placement"] = bar_metrics
    return out


def neighbors_by_groups(groups, members):
    neighbors = {u: set() for u in members}
    for group in groups:
        for a, b in combinations(group, 2):
            neighbors[a].add(b)
            neighbors[b].add(a)
    return neighbors


def peel_on_restricted_roster(initial, mark, rounds):
    """Recompute groups after each removal, with the round-one knots as the only common knots."""
    h = {u: len(places) + (u == mark) for u, places in initial.usable.items()}
    acted = {}
    for cycle in range(2, rounds + 1):
        owe = Counter(u for group in groups_for(h, initial.meets.__getitem__) for u in group)
        ready = {u for u, usable in h.items() if owe[u] <= usable}
        if not ready:
            break
        acted.update(dict.fromkeys(ready, cycle))
        for u in ready:
            del h[u]
    return acted


def real_actions(initial, mark, rounds, *, bar=False, bound=None):
    roster = set(initial.usable)
    grown = initial.fork()
    if mark is not None:
        if bar:
            grown.bar(mark)
        else:
            grown.mark(mark)
    acted = {}
    while len(grown.rows) < rounds and len(acted) < len(roster):
        if not grown.step():
            break
        read = grown.rows[-1]
        for u in set(read.available) - read.short:
            if u in roster and u not in acted:
                acted[u] = read.round
        if bound is not None and len(grown.places) > bound:
            break
    return grown, acted


def replay_peel(d, law, *, join="meeting", treatment="CANCEL-WAIT", control=False, b="source"):
    initial = grow(build("source", b, d, join=join), law, treatment, rounds=1, bound=1_000_000, trace=True)
    original = initial.usable
    offer = groups_for(sorted(original), initial.meets.__getitem__)
    owe = Counter(u for group in offer for u in group)
    shortfall = {u: owe[u] - len(places) for u, places in original.items()}
    neighbors = neighbors_by_groups(offer, original)
    seed = [u for u in original if initial.roles[u] == B_ONLY]

    if control:
        unmodified = initial.fork().run(16, 5000)
        out = {
            "d": d, "law": law, "join": join, "treatment": treatment, "B": b,
            "initial shortages": dict(Counter(shortfall.values())),
            "unchanged births by round": [r.births for r in unmodified.rows],
            "marks": [],
        }
        link_seeds = [u for u in original if initial.roles[u] == frozenset({"link"})]
        for m in (*seed, *link_seeds):
            for bar in (False, True):
                grown, acted = real_actions(initial, m, 16, bar=bar, bound=5000)
                if len(grown.places) <= 5000:
                    grown.run(16, 5000)
                hearing = first_difference(unmodified, grown, after=1)
                out["marks"].append({
                    "id": m, "sign": "-" if bar else "+", "marked descent": sorted(initial.roles[m]),
                    "mark shortfall before": shortfall[m],
                    "number of initial members that acted": len(acted),
                    "own knot acts among initial members": span(t for u, t in acted.items() if initial.roles[u] == A_ONLY),
                    "first difference from no mark in own births": hearing,
                    "common rounds": min(len(unmodified.rows), len(grown.rows)),
                })
        return out

    assert all(gap == 1 for gap in shortfall.values())
    assert not any(initial.meets[u].intersection(original) for u in original)
    replay = []
    for m in seed:
        grown, acted = real_actions(initial, m, 16)
        dist = shortest_steps(neighbors, (m,))
        restricted = peel_on_restricted_roster(initial, m, 16)
        recompute = {}
        original_rounds = []
        for current in grown.rows[1:]:
            old_live = tuple(u for u in current.available if u in original)
            if old_live not in recompute:
                recompute[old_live] = groups_for(old_live, initial.meets.__getitem__)
            full = tuple(g for g in current.groups if any(u in original for u in g))
            original_rounds.append({
                "round": current.round, "remaining original members": old_live,
                "full groups involving a remaining original member": full,
                "restricted groups": recompute[old_live],
            })
        per_knot = []
        for u in sorted(original):
            predicted = 2 + dist[u]
            actual = acted[u]
            first_partner = min(acted[v] for v in neighbors[u]) if neighbors[u] else None
            k = {
                "knot": u, "strict own A": initial.roles[u] == A_ONLY, "predicted": predicted, "acted": actual,
                "earliest acted original group partner": first_partner, "restricted roster prediction": restricted.get(u),
            }
            if u != m and first_partner is not None and actual > first_partner + 1:
                start_of_round = grown.rows[first_partner]
                prior_groups = [g for g in grown.rows[first_partner - 1].groups if u in g]
                remaining = original_rounds[first_partner - 1]["restricted groups"]
                trimmed = [g for g in remaining if u in g and any(set(g) < set(p) for p in prior_groups)]
                k["round after first original partner acts"] = {
                    "held": start_of_round.available[u], "owed": start_of_round.owed[u],
                    "groups in previous round": prior_groups,
                    "groups in full round": [g for g in start_of_round.groups if u in g],
                    "groups after recomputing on just the initial members still live": [g for g in remaining if u in g],
                    "new groups that are proper subsets of old groups": trimmed,
                }
            per_knot.append(k)
        matches = sum(k["predicted"] == k["acted"] for k in per_knot)
        misses = sorted([k["knot"], k["strict own A"], k["predicted"], k["acted"]] for k in per_knot if k["predicted"] != k["acted"])
        serialized = {
            "d": d, "law": law, "marked": m, "members": len(original), "shortfalls": {"1": len(original)},
            "acted": len(acted), "as predicted": matches, "late by": dict(Counter(str(k[3] - k[2]) for k in misses)),
            "misses": misses[:6],
        }
        differing_group_rounds = [
            r for r in original_rounds
            if r["full groups involving a remaining original member"] != r["restricted groups"]
        ]
        replay.append({
            "summary": serialized, "members": per_knot, "last round needed": len(grown.rows),
            "last knots": len(grown.places), "differing group rounds": differing_group_rounds,
        })
    return {
        "initial groups": offer,
        "distinct original members sharing a distinction": 0,
        "original members by round made": dict(Counter(initial.born[u] for u in original)),
        "marks": replay,
    }


def peel_results(pilot):
    original = json.loads((STUDY / "peel.json").read_text())
    canonical = {(r["law"], r["d"], r["marked"]): r for r in original}
    matches = []
    for law in ("JOIN-FEWER", "ONE-FEWER"):
        for d in ((1, 8) if pilot else range(1, 9)):
            batch = replay_peel(d, law)
            for replay in batch["marks"]:
                seen = replay["summary"]
                wanted = canonical[law, d, seen["marked"]]
                assert seen == wanted, (seen, wanted)
            matches.append({"law": law, "d": d, **batch})
    controls = [
        replay_peel(d, law, join=join, treatment=treatment, control=True, b=b)
        for d in ((3,) if pilot else (1, 3))
        for law, join, treatment, b in (
            ("FLOOR1", "meeting", "CANCEL-WAIT", "source"),
            ("ONE-FEWER", "share", "CANCEL-WAIT", "source"),
            ("ONE-FEWER", "meeting", "CANCEL-WAIT", "source"),
            ("ONE-FEWER", "meeting", "CANCEL-RETIRE", "source"),
            ("REC-ONE-FEWER", "meeting", "CANCEL-WAIT", "source"),
            ("CAP-5", "meeting", "CANCEL-WAIT", "source"),
            ("ONE-FEWER", "meeting", "CANCEL-WAIT", "stub"),
        )
    ]
    cases = [m for batch in matches for m in batch["marks"]]
    all_outcomes = [k for m in cases for k in m["members"]]
    constant = Counter(k["acted"] for k in all_outcomes).most_common(1)[0]
    first_partner_results = Counter(
        k["acted"] - k["earliest acted original group partner"] - 1
        for m in cases
        for k in m["members"]
        if k["knot"] != m["summary"]["marked"]
    )
    skips = [k for k in all_outcomes if "round after first original partner acts" in k]
    model_counts = Counter()
    for k in skips:
        groups = k["round after first original partner acts"]
        model_counts["blocked in full, able on restricted roster"] += len(groups["groups after recomputing on just the initial members still live"]) <= groups["held"]
        model_counts["blocked even on restricted roster"] += len(groups["groups after recomputing on just the initial members still live"]) > groups["held"]
        model_counts["some group shrank to a smaller group preserving an obligation"] += bool(groups["new groups that are proper subsets of old groups"])
    return {
        "replayed branches": len(cases),
        "members": len(all_outcomes),
        "fixed peel correct": sum(k["predicted"] == k["acted"] for k in all_outcomes),
        "fixed peel correct excluding marked knots": sum(k["predicted"] == k["acted"] for k in all_outcomes) - len(cases),
        "strict own A members": sum(k["strict own A"] for k in all_outcomes),
        "fixed peel correct for strict own A": sum(k["strict own A"] and k["predicted"] == k["acted"] for k in all_outcomes),
        "restricted roster prediction correct": sum(k["restricted roster prediction"] == k["acted"] for k in all_outcomes),
        "rounds compared for groups involving surviving original members": sum(m["last round needed"] - 1 for m in cases),
        "rounds with different groups involving surviving original members": sum(len(m["differing group rounds"]) for m in cases),
        "best constant round (round, correct)": constant,
        "extra delay after earliest actual original group partner, excluding marked knot": dict(first_partner_results),
        "why actual partners are insufficient": dict(model_counts),
        "largest marked run in knots": max(m["last knots"] for m in cases),
        "branch results": matches,
        "scaffold controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--mode", choices=("recount", "peel", "again"), default="recount")
    args = parser.parse_args()
    if args.mode == "recount":
        output = {
            "second-change recount": recount_again(24 if args.pilot else None),
            "peeling recount": recount_peeling(),
        }
    elif args.mode == "peel":
        output = peel_results(args.pilot)
    else:
        entries = selected_first_changes()
        sample = sample_again()
        if args.pilot:
            # Include a success, failure and empty sample in the pilot.
            sample = [sample[i] for i in (0, 8, 11)]
        output = {
            "seed": SEED,
            "sampling": "Four per ration and hearing outcome, or all if fewer, plus all unmarkable cases.",
            "replayed": [
                replay_again(r, entries[case_key(r)], controls=bool(r["again"] and any(t["heard"] is not None for t in r["again"][0])))
                for r in sample
            ],
        }
    rendered = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered)


if __name__ == "__main__":
    main()
