"""Audit the Setting A rosters, the short-knot rule, and the start arity.

The first-roster calculation follows the frozen complete-round definitions
directly and enumerates subsets of at most seven knots. Continuations use
the shared round engine. The comparisons with the archive are written here.
"""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ENGINE = (
    HERE.parents[2] / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
    / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"
)
sys.path.insert(0, str(ENGINE))
import eng


HORIZON = 16
KNOT_BOUND = 20_000
READINGS = ("name", "sig0", "sig1")
WAIT = "CANCEL-WAIT"
ORDINARY = "STALL"


def ring(length, loose):
    return [
        [(u - 1) % length, u, *range(length + u * loose, length + (u + 1) * loose)]
        for u in range(length)
    ]


STARTS = {
    "ring5-bare": ring(5, 2),
    "ring7-bare": ring(7, 2),
    "two-touching": [[0, 1, 2], [0, 3, 4]],
    "chain3": [[0, 1, 2], [1, 3, 4], [3, 5, 6]],
    "ring5-eddy": ring(5, 3),
    "generator7": [
        [0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14],
        [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22],
        [5, 8, 23, 24],
    ],
}


def first_roster(stars):
    """Count due joins by enumerating small subsets, apart from the engine."""
    incidence = Counter(d for knot in stars for d in knot)
    assert all(1 <= n <= 2 for n in incidence.values())
    held = {u: sum(incidence[d] == 1 for d in knot) for u, knot in enumerate(stars)}
    live = [u for u in held if held[u]]
    places = [set(knot) for knot in stars]
    met = [
        {u for u in live if u != common and places[u] & knot}
        for common, knot in enumerate(places)
    ]
    pairs = {pair for group in met for pair in combinations(sorted(group), 2)}
    larger = [
        set(group) for size in range(3, len(live) + 1) for group in combinations(live, size)
        if all(pair in pairs for pair in combinations(group, 2))
    ]
    joins = [
        group for group in larger
        if not any(group < other for other in larger) and not any(group <= meeting for meeting in met)
    ]
    pairs.difference_update(pair for group in joins for pair in combinations(sorted(group), 2))
    groups = sorted(tuple(sorted(group)) for group in joins) + sorted(pairs)
    owe = Counter(u for group in groups for u in group)
    return {
        "places": [len(knot) for knot in stars], "held": list(held.values()),
        "owe": [owe[u] for u in held], "groups": groups,
        "short": [u for u in live if held[u] < owe[u]],
        "below_three_places": [u for u, knot in enumerate(stars) if len(knot) < 3],
    }


def change_start(stars, change, at):
    changed = [knot.copy() for knot in stars]
    if change == "mark":
        changed[at].append(1 + max(d for knot in stars for d in knot))
    else:
        donor, recipient = at
        incidence = Counter(d for knot in stars for d in knot)
        moved = next(d for d in reversed(stars[donor]) if incidence[d] == 1)
        changed[donor].remove(moved)
        changed[recipient].append(moved)
    return changed


def same_first_roster(expected, record):
    assert record["groups"] == expected["groups"]
    assert [record["h"].get(u, 0) for u in range(len(expected["held"]))] == expected["held"]
    assert [record["owe"].get(u, 0) for u in range(len(expected["held"]))] == expected["owe"]
    assert record["short"] == expected["short"]


class Replay:
    def __init__(self, stars, knot_law):
        self.state = eng.from_stars(stars)
        self.knot_law = knot_law
        self.guard = eng.Guard(100)
        self.signatures = [("start", 0, 0, len(knot)) for knot in stars]
        self.identities = list(range(len(stars)))
        self.names = {}
        self.stop = None

    def fork(self):
        other = object.__new__(Replay)
        other.state = self.state.copy()
        other.knot_law = self.knot_law
        other.guard = eng.Guard(100)
        other.signatures = self.signatures.copy()
        other.identities = self.identities.copy()
        other.names = self.names
        other.stop = self.stop
        return other

    def mark(self, knot):
        state = self.state
        distinction = state.n_distinctions
        state.holders.append([knot])
        state.barred.append(False)
        state.maker.append(knot)
        state.places[knot].append(distinction)
        if self.knot_law == "parity":
            state.basis.clear()
            for places in state.places:
                eng.basis_insert(state.basis, eng.row_of(places))
        self.signatures[knot] = (*self.signatures[knot][:3], len(state.places[knot]))
        return distinction

    def strike(self, added):
        barred = [
            d for u in self.state.holders[added] if self.state.made[u] == self.state.round
            for d in self.state.usable(u)
        ]
        for d in barred:
            self.state.barred[d] = True
        return len(barred)

    def step(self, treatment=WAIT):
        try:
            record = eng.play_round(
                self.state, eng.Law("ORD", treatment, None, self.knot_law), self.guard,
            )
        except eng.GuardStop:
            self.stop = "guard"
            return None, None
        readings = {reading: Counter() for reading in READINGS}
        seen = Counter()
        for birth in record["births"]:
            u = birth["id"]
            assert u == len(self.identities)
            assert birth["implied"] or birth["f"] >= birth["D"]
            kind, parents = birth["kind"], birth["parents"]
            family = kind, tuple(sorted(self.identities[k] for k in parents))
            key = family, seen[family]
            seen[family] += 1
            identity = self.names.setdefault(key, self.state.n_start + len(self.names))
            signature = kind, len(parents), birth["f"], len(self.state.places[u])
            readings["name"][identity, *signature[2:]] += 1
            readings["sig0"][signature] += 1
            parent_signatures = tuple(sorted(self.signatures[k] for k in parents))
            readings["sig1"][(*signature, parent_signatures)] += 1
            self.identities.append(identity)
            self.signatures.append(signature)
        if record["closing"]:
            # With at most two holders and one connected start, an implied
            # parity birth takes all loose distinctions, so there is no next roster.
            assert len(record["births"]) == 1 and not eng.live_members(self.state)
        if not record["births"]:
            self.stop = "closed"
        elif self.state.n_knots > KNOT_BOUND:
            self.stop = "knots"
        return record, readings


def load_archive():
    with gzip.open(HERE.parent / "runs.jsonl.gz", "rt") as source:
        return [row for line in source if (row := json.loads(line)).get("start") in STARTS]


def difference(base, changed):
    return [sum((changed - base).values()), sum((base - changed).values())]


def validate_comparison(expected, base, changed):
    assert expected["n"] == sum(base["sig0"].values())
    assert expected["n'"] == sum(changed["sig0"].values())
    for reading in READINGS:
        assert expected[reading] == difference(base[reading], changed[reading])


def shortlist(record):
    return [
        [u, record["h"][u], record["owe"][u]] for u in record["short"]
    ]


def trace_short(record):
    cancelled = Counter(u for group in record["cancelled"] for u in group)
    kept = [group for group in record["groups"] if group not in record["cancelled"]]
    released = {u: n for u, n in sorted(cancelled.items()) if u not in record["short"]}
    assert all(record["act"][u] == "wait" for u in record["short"])
    assert set(record["short"]) <= {u for u, _, _ in record["persisting"]}
    return {
        "round": record["round"], "short_by_knot_held_owed": shortlist(record),
        "cancelled_joins": record["cancelled"], "kept_join_count": len(kept),
        "extra_offshoots_by_release": released, "birth_count": len(record["births"]),
    }


def mark_and_replay(replay, base, rounds, expected=None, roster=None, strike_after=None):
    """Read active shortness explicitly through the first fully paid round after edits."""
    events, compared = [], 0
    while replay.stop is None and replay.state.round < HORIZON:
        record, reading = replay.step()
        if record is None:
            break
        round_number = record["round"]
        if roster is not None and round_number == 1:
            same_first_roster(roster, record)
        if round_number in rounds:
            validate_comparison(rounds[round_number], base[round_number], reading)
            compared += 1
        if record["short"]:
            events.append(trace_short(record))
        if strike_after is not None and strike_after[0] == round_number:
            assert replay.strike(strike_after[1]) == expected["struck"]
        elif not record["short"]:
            # All old usable distinctions have been spent. The next roster
            # is the demand roster, with h >= demand for every new member.
            # Until a further edit, no later round can introduce a short member.
            assert not record["persisting"]
            assert strike_after is None or strike_after[0] < round_number
            return events, compared, round_number, True
    return events, compared, replay.state.round, replay.stop != "guard"


def init_baselines(archive):
    expected_by_start = {}
    for row in archive:
        key = row["start"], row["knot law"]
        expected = row["base counts"], row["base_stop"]
        assert expected_by_start.setdefault(key, expected) == expected
    result = {}
    for (start, knot_law), (expected, stop) in expected_by_start.items():
        replay = Replay(STARTS[start], knot_law)
        readings, snapshots = {}, {}
        while replay.stop is None and replay.state.round < HORIZON:
            record, metrics = replay.step()
            if record is None:
                break
            round_number = record["round"]
            assert not record["short"]
            if round_number == 1:
                same_first_roster(first_roster(STARTS[start]), record)
            if round_number in (2, 4):
                snapshots[round_number] = replay.fork()
            readings[round_number] = metrics
        assert [sum(round_["sig0"].values()) for round_ in readings.values()] == expected
        assert replay.stop == stop
        result[start, knot_law] = (readings, snapshots, replay.names)
    return result


def audit_case(job, case, baselines):
    start, change, knot_law = job["start"], job["change"], job["knot law"]
    base, snapshots, names = baselines[start, knot_law]
    first = None
    strike_after = None
    if change in {"mark", "move"}:
        what = job["at"]
        stars = change_start(STARTS[start], change, what)
        first = first_roster(stars)
        replay = Replay(stars, knot_law)
        replay.names = names
        rows = job["rows"]
    else:
        made_round = job["round"]
        replay = snapshots[made_round].fork()
        if change == "pair":
            what = case["knots"]
            assert all(replay.state.made[k] == made_round for k in what)
            for k in what:
                replay.mark(k)
            rows = []
        else:
            what = case["knot"]
            assert replay.state.made[what] == made_round
            added = replay.mark(what)
            if change == "pulse":
                strike_after = (made_round + 1, added)
            rows = case["rows"]
    events, compared, checked_through, funded_test_complete = mark_and_replay(
        replay, base, {row["round"]: row for row in rows}, expected=case, roster=first,
        strike_after=strike_after,
    )
    identity = {"start": start, "knot_law": knot_law, "change": change, "at": what}
    if "round" in job:
        identity["made_round"] = job["round"]
    counts = {
        "cases": 1, "initially_short": bool(first and first["short"]),
        "below_three_places": bool(first and first["below_three_places"]),
        "short_after_first_round": any(event["round"] > 1 for event in events),
        "short_at_any_round": bool(events),
        "keeps_waiting_through_checked_rounds": bool(events and events[-1]["round"] == checked_through),
        "funding_check_complete": funded_test_complete,
        "strict_ordinary_eligible": (
            funded_test_complete and not events and not (first and first["below_three_places"])
        ),
        "has_eight_comparable_rounds": len(rows) >= 8,
        "verdict_applies": change != "pair",
        "archive_rows_checked": compared,
    }
    if rows and len(rows) < 8:
        identity["recorded_stop"] = case["stop"]
        identity["comparable_rounds"] = len(rows)
    if first and first["below_three_places"]:
        identity["below_three_places"] = first["below_three_places"]
    if events:
        identity["short_rounds"] = events
        identity["ordinary_stalls_round"] = events[0]["round"]
    return identity, counts, case.get("verdicts")


def audit_cases(archive, baselines, pilot):
    table = defaultdict(Counter)
    exceptional, weakens, short_events_by_round = [], [], Counter()
    for job in archive:
        change = job["change"]
        if change in {"mark", "move"}:
            cases = [job]
        else:
            cases = job["pairs" if change == "pair" else "marks"]
            _, snapshots, _ = baselines[job["start"], job["knot law"]]
            state = snapshots[job["round"]].state
            made = [k for k in range(state.n_start, state.n_knots) if state.made[k] == job["round"]]
            assert job["made"] == len(made)
            if change == "pair":
                assert [tuple(case["knots"]) for case in cases] == list(combinations(made, 2))
            else:
                assert [case["knot"] for case in cases] == made[:40]
        if pilot:
            if change in {"mark", "move"} and job["at"] not in (0, 1, [0, 1], [0, 2], [4, 0]):
                continue
            cases = cases[:1]
        for case in cases:
            identity, counts, verdicts = audit_case(job, case, baselines)
            key = job["knot law"], job["start"], change
            table[key].update(counts)
            if counts["short_at_any_round"] or counts["below_three_places"] or "recorded_stop" in identity:
                exceptional.append(identity)
            for event in identity.get("short_rounds", []):
                short_events_by_round[job["knot law"], change, event["round"]] += 1
            if verdicts and any(verdicts[reading] == "weakens" for reading in ("sig0", "sig1")):
                weakens.append({
                    **identity, "initially_short": counts["initially_short"],
                    "short_after_first_round": counts["short_after_first_round"],
                    "strict_ordinary_eligible": counts["strict_ordinary_eligible"],
                })
    totals = defaultdict(Counter)
    for (knot_law, _, change), counts in table.items():
        totals[knot_law, change].update(counts)
    return {
        "by_start": [
            {"knot_law": law, "start": start, "change": change, **counts}
            for (law, start, change), counts in sorted(table.items())
        ],
        "by_intervention": [
            {"knot_law": law, "change": change, **counts}
            for (law, change), counts in sorted(totals.items())
        ],
        "short_round_frequency": [
            {"knot_law": law, "change": change, "round": round_number, "cases": count}
            for (law, change, round_number), count in sorted(short_events_by_round.items())
        ],
        "exceptional_cases": exceptional,
        "weakens_cases": weakens,
    }


def verdict(damage, combined):
    if len(damage) < 8:
        return "too few rounds"
    mid = len(damage) // 2
    if not any(damage[mid:]):
        return "dies out"
    if all(100 * d >= 95 * n > 0 for d, n in zip(damage[-4:], combined[-4:])):
        return "takes over"
    if combined[-1] <= combined[mid]:
        return "bounded" if damage[-1] <= damage[mid] else "grows"
    if 2 * combined[-1] >= 3 * combined[mid] and damage[-1] <= damage[mid]:
        return "weakens"
    return "holds"


def alternatives(baselines, archive):
    targets = [("ring5-bare", [0, 1]), ("ring5-bare", [0, 2]), ("ring7-bare", [0, 1])]
    result = []
    for start, at in targets:
        base, _, names = baselines[start, "nae"]
        stars = change_start(STARTS[start], "move", at)
        first = first_roster(stars)
        assert first["short"] == [at[0]]
        original = next(
            row for row in archive
            if row["start"] == start and row["knot law"] == "nae"
            and row["change"] == "move" and row["at"] == at
        )
        entries = [{
            "treatment": ORDINARY, "stop": "stalled before first birth",
            "verdicts": dict.fromkeys(READINGS, "too few rounds"), "compared_rounds": 0,
        }]
        for treatment in (WAIT, "CANCEL-OFFSHOOT", "CANCEL-RETIRE"):
            replay = Replay(stars, "nae")
            replay.names = names
            values, damage = [], {reading: [] for reading in READINGS}
            short_rounds, first_donor_births = [], None
            while replay.stop is None and replay.state.round < HORIZON:
                record, changed = replay.step(treatment)
                if record is None:
                    break
                round_number = record["round"]
                if round_number == 1:
                    same_first_roster(first, record)
                    details = {
                        "short_by_knot_held_owed": shortlist(record),
                        "cancelled": record["cancelled"],
                        "births_by_kind_and_parents": [[b["kind"], list(b["parents"])] for b in record["births"]],
                        "donor_action": record["act"][at[0]],
                    }
                if record["short"]:
                    short_rounds.append([round_number, shortlist(record)])
                if first_donor_births is None:
                    born = [[b["kind"], list(b["parents"])] for b in record["births"] if at[0] in b["parents"]]
                    if born:
                        first_donor_births = {"round": round_number, "births_by_kind_and_parents": born}
                if round_number not in base:
                    break
                before = sum(base[round_number]["sig0"].values())
                after = sum(changed["sig0"].values())
                values.append([before, after])
                for reading in READINGS:
                    damage[reading].append(sum(difference(base[round_number][reading], changed[reading])))
                if treatment == WAIT:
                    validate_comparison(original["rows"][round_number - 1], base[round_number], changed)
            combined = [sum(pair) for pair in values]
            verdicts = {reading: verdict(damage[reading], combined) for reading in READINGS}
            if treatment == WAIT:
                assert verdicts == original["verdicts"] and replay.stop == original["stop"]
            entries.append({
                "treatment": treatment, "stop": replay.stop, "first_round": details,
                "short_rounds": short_rounds, "first_donor_births": first_donor_births,
                "compared_rounds": len(values), "base_and_changed_birth_counts": values,
                "damage": damage, "verdicts": verdicts,
            })
        result.append({"start": start, "move": at, "knot_law": "nae", "treatments": entries})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Replay only selected interventions with the same bounds.")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    archive = load_archive()
    expected_start_changes = set()
    for start, stars in STARTS.items():
        held = first_roster(stars)["held"]
        for law in ("nae", "parity"):
            expected_start_changes.update((start, law, "mark", (u,)) for u in range(len(stars)))
            expected_start_changes.update(
                (start, law, "move", (u, v))
                for u, count in enumerate(held) if count for v in range(len(stars)) if u != v
            )
    start_changes = [
        (row["start"], row["knot law"], row["change"],
         (row["at"],) if row["change"] == "mark" else tuple(row["at"]))
        for row in archive if row["change"] in {"mark", "move"}
    ]
    assert len(start_changes) == len(expected_start_changes) and set(start_changes) == expected_start_changes
    late_panels = [
        (row["start"], row["knot law"], row["change"], row["round"])
        for row in archive if row["change"] not in {"mark", "move"}
    ]
    expected_late_panels = {
        (start, "nae", change, round_number)
        for start in STARTS for change in ("made", "pulse") for round_number in (2, 4)
    }
    expected_late_panels.update((start, "parity", "made", 2) for start in STARTS)
    expected_late_panels.update((start, "nae", "pair", 2) for start in ("two-touching", "chain3"))
    assert len(late_panels) == len(expected_late_panels) and set(late_panels) == expected_late_panels
    baselines = init_baselines(archive)
    audited = audit_cases(archive, baselines, args.pilot)
    result = {
        "setting": "A",
        "frozen_ordinary_growth": "Ordinary count, stall if any member is short, nothing taken extra.",
        "recorded_growth": "Ordinary count, cancel joins of short knots, those knots wait, other knots release, nothing taken extra.",
        "frozen_start": "Every start knot holds at least three distinct places.",
        "coverage": (
            ("The pilot uses a subset of the changed runs. " if args.pilot else "")
            + "Each tested first roster was enumerated directly. Each archive baseline was replayed to its full horizon. "
            "Each changed run was replayed through the first round with no short member after its last edit, "
            "or through its stop. After a fully paid round, every old member spends all its usable distinctions "
            "and every new member holds at least its demand in that next roster. An implied parity birth ends "
            "the run. Thus no later unaudited round can first introduce a short member without another edit. "
            "Three selected short moves were compared through the full horizon under alternative treatments."
        ),
        "archive_jobs": dict(Counter((row["knot law"] for row in archive))),
        "baseline_first_rosters": {start: first_roster(stars) for start, stars in STARTS.items()},
        "baseline_birth_counts": {
            law: {
                start: [sum(metrics["sig0"].values()) for metrics in baselines[start, law][0].values()]
                for start in STARTS
            } for law in ("nae", "parity")
        },
        **audited,
        "alternative_short_treatments": alternatives(baselines, archive),
    }
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["by_intervention"], indent=2))


if __name__ == "__main__":
    main()
